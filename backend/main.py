from backend.routes.auth import router as auth_router
from backend.routes.resume import router  as resume_router
from backend.routes.interview import router  as question_router
from backend.routes.analytics import router as analytics_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Articulate.AI API",
    version="1.0.0"
)

# Allow browser-based clients (Netlify, local dev, Streamlit, etc.) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins — safe since auth is ID-based, not cookie-based
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)