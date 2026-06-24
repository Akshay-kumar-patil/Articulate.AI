from backend.config import db
from datetime import datetime

# Users collection
users_collection = db["users"]

# Interviews collection
interviews_collection = db["interviews"]


def save_interview(user_id: str, answers: list, difficulty: str):
    interview_doc = {
        "user_id": user_id,
        "difficulty": difficulty,
        "answers": answers,
        "created_at": datetime.utcnow()
    }
    result = interviews_collection.insert_one(interview_doc)
    return str(result.inserted_id)