from groq import Groq
from backend.config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )
    return transcription.text                                                                           