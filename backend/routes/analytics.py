from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from backend.db.models import interviews_collection, save_interview, users_collection


router = APIRouter()
 
 
class SaveInterviewRequest(BaseModel):
    user_id: str
    difficulty: str
    answers: list
 
@router.post("/save-interview")
def save_interview_route(req: SaveInterviewRequest):
    interview_id = save_interview(req.user_id, req.answers, req.difficulty)
    return {"message": "Interview saved", "interview_id": interview_id}
 

 
@router.get("/get-report/{user_id}")
def get_report(user_id: str):
    interviews = list(interviews_collection.find({"user_id": user_id}))
    for interview in interviews:
        interview["_id"] = str(interview["_id"])
    return {"interviews": interviews}
 
 

@router.delete("/delete-session/{interview_id}")
def delete_session(interview_id: str):
    result = interviews_collection.delete_one({"_id": ObjectId(interview_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {"message": "Interview deleted permanently"}
 

@router.delete("/delete-user/{user_id}")
def delete_user(user_id:str):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    interviews_collection.delete_many({"user_id": user_id})
    return {"message": "User Deleted permanently"}

