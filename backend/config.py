import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


class Config:
    # Groq API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = "Articulate"

    # Secret key for security-related features
    SECRET_KEY = os.getenv("SECRET_KEY")



client = MongoClient(Config.MONGO_URI)

db = client[Config.DB_NAME]