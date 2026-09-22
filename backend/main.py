from backend.routes.auth import router as auth_router
from backend.routes.resume import router as resume_router
from backend.routes.interview import router as question_router
from backend.routes.analytics import router as analytics_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Articulate.AI API",
    version="2.0.0",
    description="Session-based AI interview coach — no database, no login required."
)

# Allow browser-based clients (Netlify, local dev, Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session management (replaces auth — just a name + session_id)
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Session"]
)

app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)

app.include_router(
    question_router,
    prefix="/question",
    tags=["Interview"]
)

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)