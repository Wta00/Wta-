from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["academy"]

students_collection = db["students"]
coach_log_collection = db["coach_logs"]