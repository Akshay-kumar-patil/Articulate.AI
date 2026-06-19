import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
    MONGO_URI = os.environ.get("MONGO_URI")
    DB_NAME = "Articulate.Ai"