from django.http import JsonResponse
import json
from datetime import date
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime
from django.utils import timezone
from .mongo import students_collection, coach_log_collection
from django.shortcuts import render
def attendance_page(request):

    return render(request, "attendance.html")


def admin_page(request):

    return render(request, "admin.html")


def student_page(request):

    return render(request, "student.html")


def coach_page(request):

    return render(request, "attendanceC.html")


def get_students(request):

    coach = request.GET.get("coach", "").strip().lower()

    coach_branch = {

    "veslin wta": [
        "Kalpakkam",
        "Anupuram",
        "Navy"
    ],

    "dani wta": [
        "S.p koil",
        "Zee School",
        "Deva's program"
    ],

    "sujith wta": [
        "Kalpakkam",
        "Navy",
        "Anupuram"
    ],

    "eso wta": [
        "Kalpakkam"
    ],

    "mathesh wta": [
        "Anupuram"
    ],

    "jesurajan wta": [
        "Kudankulam",
        "Kingschool"
    ],

    "wta": [
        "Kalpakkam",
        "S.p koil",
        "Navy",
        "Anupuram",
        "Kudankulam",
        "Kingschool",
        "Deva's program",
        "Zee School"
    ]
    }

    branches = coach_branch.get(coach, [])

    regex_branches = [
        {
            "branch": {
                "$regex": f"^{b}$",
                "$options": "i"
            }
        }
        for b in branches
    ]
    
    if not regex_branches:
        return JsonResponse([], safe=False)

    students = list(
        students_collection.find({
        "$or": regex_branches
        })
    )
    if coach == "veslin wta":
        students = [
            s for s in students
            if s.get("branch") != "Kalpakkam"
            or s.get("session") in ["Morning", "Morning and Evening"]
        ]

    elif coach == "sujith wta":
        students = [
            s for s in students
            if s.get("branch") != "Kalpakkam"
            or s.get("session") in ["Evening", "Morning and Evening"]
        ]

    elif coach == "eso wta":
        students = [
            s for s in students
            if s.get("branch") == "Kalpakkam"
            and s.get("session") in ["Evening", "Morning and Evening"]
        ]

    for s in students:
        s["_id"] = str(s["_id"])

    return JsonResponse(students, safe=False)

@csrf_exempt
def mark_attendance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            student_id = data.get("studentId")
            present = data.get("present")

            if not student_id:
                return JsonResponse({"error": "Missing studentId"}, status=400)

            today = str(date.today())

            students_collection.update_one(
                {"_id": ObjectId(student_id)},
                {
                    "$set": {
                        f"attendance.{today}": present
                    }
                }
            )

            return JsonResponse({"message": "Attendance saved"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)




@csrf_exempt
def mark_fees(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            student_id = data.get("studentId")
            month = data.get("month")
            proof = data.get("proof")

            if not student_id or not month:
                return JsonResponse({"error": "Missing data"}, status=400)

            students_collection.update_one(
                {"_id": ObjectId(student_id)},
                {
                    "$set": {
                        f"fees.{month}.paid": True,
                        f"fees.{month}.datePaid": str(date.today())
                    },
                    "$push": {
                        f"fees.{month}.proofs": proof  
                    }
                }
            )

            return JsonResponse({"message": "Fees updated (history saved)"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def add_student(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)

            student = {

                "name": data["name"],
                "age": data.get("age", ""),
                "dob": data.get("dob", ""),
                "standard": data.get("standard", ""),
                "school": data.get("school", ""),

                "fatherName": data.get("fatherName", ""),
                "motherName": data.get("motherName", ""),

                "fatherPhone": data.get("fatherPhone", ""),
                "motherPhone": data.get("motherPhone", ""),

                "studentPhone": data.get("studentPhone", ""),

                "joinDate": data.get("joinDate", ""),
                "joinYear": data.get("joinYear", ""),

                "batch": data.get("batch", ""),      
                "court": data.get("court", ""),
                "session": data.get("session", ""),

                "branch": data.get("branch", ""),

                "attendance": {},
                "fees": {}
            }

            students_collection.insert_one(student)

            return JsonResponse({
                "message": "Student added"
            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "error": "Invalid request"
    }, status=400)


def monthly_report(request):
    students = list(students_collection.find())

    report = []

    for s in students:
        attendance = s.get("attendance", {})

        present = 0
        absent = 0

        for day, value in attendance.items():
            if value:
                present += 1
            else:
                absent += 1

        report.append({
            "name": s["name"],
            "present_days": present,
            "absent_days": absent
        })

    return JsonResponse(report, safe=False)




@csrf_exempt
def coach_checkin(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)

            name = data.get("name")
            location = data.get("location").strip().lower()
            start_ball_count = data.get("startBallCount")

            today = str(date.today())
            current_time = timezone.localtime().strftime("%H:%M:%S")

            existing = coach_log_collection.find_one({
                "name": name,
                "logs": {
                    "$elemMatch": {
                        "date": today,
                        "outTime": None
                    }
                }
            })

            if existing:
                return JsonResponse({
                    "error": "Already checked in. Please checkout first."
                }, status=400)

            coach_log_collection.update_one(

                {"name": name},

                {
                    "$push": {
                        "logs": {
                            "date": today,
                            "inTime": current_time,
                            "outTime": None,
                            "location": location,
                            "startBallCount": int(start_ball_count)
                        }
                    }
                },

                upsert=True
            )

            return JsonResponse({
                "message": "Checked in"
            })

        except Exception as e:
            return JsonResponse({
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "error": "Invalid request"
    }, status=400)



@csrf_exempt
def coach_checkout(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)

            name = data.get("name")
            location = data.get("location").strip().lower()
            end_ball_count = data.get("endBallCount")

            result = coach_log_collection.update_one(

                {
                    "name": name,
                    "logs.location": location,
                    "logs.outTime": None
                },

                {
                    "$set": {
                        "logs.$.outTime": timezone.localtime().strftime("%H:%M:%S"),
                        "logs.$.endBallCount": int(end_ball_count)
                    }
                }

            )

            if result.modified_count == 0:

                return JsonResponse({
                    "error": "No active session for this location"
                }, status=400)

            return JsonResponse({
                "message": "Checked out"
            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "error": "Invalid request"
    }, status=400)
    
    
    
def admin_students(request):

    branch = request.GET.get("branch")

    students = list(
        students_collection.find({
            "branch": {
                "$regex": f"^{branch}$",
                "$options": "i"
            }
        })
    )

    for s in students:
        s["_id"] = str(s["_id"])

    return JsonResponse(students, safe=False)


def student_profile(request, id):

    student = students_collection.find_one({
        "_id": ObjectId(id)
    })

    student["_id"] = str(student["_id"])

    return render(
        request,
        "student.html",
        {"student": student}
    )




def coach_attendance(request):

    coaches = list(coach_log_collection.find())

    data = []

    for coach in coaches:

        data.append({
            "_id": str(coach["_id"]),
            "name": coach["name"]
        })

    return JsonResponse(data, safe=False)



def coach_attendance_details(request, name):

    coach = coach_log_collection.find_one({
        "name": name
    })

    if not coach:
        return JsonResponse([], safe=False)

    return JsonResponse(
        coach.get("logs", []),
        safe=False
    )
    

def fee_status(request):

    students = list(students_collection.find())

    branches = {}

    for s in students:

        branch = s.get("branch", "Unknown")

        if branch not in branches:
            branches[branch] = {
                "branch": branch,
                "paid": [],
                "notPaid": []
            }

        current_month = datetime.now().strftime("%Y-%m")

    fees = s.get("fees", {})

    if current_month in fees and fees[current_month].get("paid"):
        branches[branch]["paid"].append(s["name"])
    else:
        branches[branch]["notPaid"].append(s["name"])

    return JsonResponse(
        list(branches.values()),
        safe=False
    )