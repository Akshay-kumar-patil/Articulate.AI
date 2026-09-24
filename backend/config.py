import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Groq API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "openai/gpt-oss-120b"

    # Secret key for security-related features (kept for JWT compatibility if needed later)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")