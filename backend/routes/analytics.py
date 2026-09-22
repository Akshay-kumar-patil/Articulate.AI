import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from backend.db.models import sessions, interviews

router = APIRouter()


class SaveInterviewRequest(BaseModel):
    session_id: str
    difficulty: str
    answers: list  # list of {question, answer, scores}


@router.post("/save-interview")
def save_interview_route(req: SaveInterviewRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    interview_doc = {
        "interview_id": str(uuid.uuid4()),
        "difficulty": req.difficulty,
        "answers": req.answers,
        "created_at": datetime.utcnow().isoformat(),
    }

    interviews.setdefault(req.session_id, []).append(interview_doc)

    return {
        "message": "Interview saved",
        "interview_id": interview_doc["interview_id"],
    }


@router.get("/get-report/{session_id}")
def get_report(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return {"interviews": interviews.get(session_id, [])}


@router.delete("/delete-interview/{session_id}/{interview_id}")
def delete_interview(session_id: str, interview_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    session_interviews = interviews.get(session_id, [])
    new_list = [i for i in session_interviews if i["interview_id"] != interview_id]

    if len(new_list) == len(session_interviews):
        raise HTTPException(status_code=404, detail="Interview not found")

    interviews[session_id] = new_list
    return {"message": "Interview deleted"}


@router.delete("/clear-session/{session_id}")
def clear_session_data(session_id: str):
    """Wipe all interview data for this session (keeps session alive)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    interviews[session_id] = []
    return {"message": "All session data cleared"}
