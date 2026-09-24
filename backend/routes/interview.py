import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.services.question_gen import generate_questions
from backend.services.speech import transcribe_audio
from backend.services.scorer import score_answer

router = APIRouter()


class QuestionRequest(BaseModel):
    resume_info: dict
    difficulty: str
    total_questions: int


@router.post("/generate-questions")
def get_questions(req: QuestionRequest):
    questions = generate_questions(req.resume_info, req.difficulty, req.total_questions)
    return {"questions": questions}


@router.post("/answer-audio")
def answer_audio(file: UploadFile = File(...)):
    # Write to /tmp — the working directory may be read-only on Render
    suffix = os.path.splitext(file.filename or ".webm")[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    try:
        data = transcribe_audio(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Always clean up, even if transcription raised
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "message": "Audio transcribed successfully",
        "text_length": len(data),
        "preview": data[:300],
        "text": data,
    }


class ScoreRequest(BaseModel):
    question: str
    answer: str
    is_intro_question : bool


@router.post("/score-answer")
def get_score(score:ScoreRequest):
    scores=score_answer(score.question,score.answer,score.is_intro_question)
    return scores