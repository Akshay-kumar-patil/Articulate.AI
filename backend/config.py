import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


class Config:
    # Groq API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "openai/gpt-oss-120b"

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = "Articulate"

    # Secret key for security-related features
    SECRET_KEY = os.getenv("SECRET_KEY")


# connectTimeoutMS / serverSelectionTimeoutMS — don't block at import time.
# PyMongo will only actually connect when the first real DB operation happens.
client = MongoClient(
    Config.MONGO_URI,
    serverSelectionTimeoutMS=10000,   # 10s to select a server
    connectTimeoutMS=10000,           # 10s to establish TCP connection
    socketTimeoutMS=20000,            # 20s for any single socket operation
    tls=True,
    tlsAllowInvalidCertificates=False,
)

db = client[Config.DB_NAME]