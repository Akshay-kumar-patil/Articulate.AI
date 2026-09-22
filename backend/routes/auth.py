import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.db.models import sessions

router = APIRouter()


class StartSessionRequest(BaseModel):
    name: str  # Just a display name — no password, no email


@router.post("/start-session")
def start_session(req: StartSessionRequest):
    """
    Create a new in-memory session.  Returns a session_id the client stores
    locally (localStorage / Python variable).  No database involved.
    """
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "name": req.name.strip(),
    }
    return {
        "message": "Session started",
        "session_id": session_id,
        "name": req.name.strip(),
    }


@router.get("/verify/{session_id}")
def verify_session(session_id: str):
    """Check whether a session_id is still alive in this server process."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return {"message": "Session active", "name": sessions[session_id]["name"]}


@router.delete("/end-session/{session_id}")
def end_session(session_id: str):
    """Explicitly clear a session and all its interview data."""
    from backend.db.models import interviews
    sessions.pop(session_id, None)
    interviews.pop(session_id, None)
    return {"message": "Session ended and data cleared"}