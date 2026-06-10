from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://christineellise:Bonjour123salut@cluster0.llzsra9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

db = client["academy"]

students_collection = db["students"]
coach_log_collection = db["coach_logs"]