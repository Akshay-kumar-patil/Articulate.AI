from backend.routes.auth import router as auth_router
from backend.routes.resume import router  as resume_router
from backend.routes.interview import router  as question_router
from fastapi import FastAPI

app = FastAPI(
    title="Articulate.AI API",
    version="1.0.0"
)

# Register Authentication Routes
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)


app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)

app.include_router(
    question_router,
    prefix="/question",
    tags=["question"]
)
