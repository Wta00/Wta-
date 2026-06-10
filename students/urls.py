from django.urls import path
from . import views

urlpatterns = [

    path("", views.attendance_page),

    path("admin-page/", views.admin_page),

    path("student-page/", views.student_page),

    path("coach-page/", views.coach_page),

    path("students/", views.get_students),

    path("attendance/", views.mark_attendance),

    path("fees/", views.mark_fees),

    path("add-student/", views.add_student),

    path("report/", views.monthly_report),

    path("coach/checkin/", views.coach_checkin),

    path("coach/checkout/", views.coach_checkout),

    path("admin/students/", views.admin_students),

    path("student/<str:id>/", views.student_profile),

    # NEW COACH ATTENDANCE URLS
    path("coach-attendance/", views.coach_attendance),

    path(
        "coach-attendance/<str:name>/",
        views.coach_attendance_details
    ),

]