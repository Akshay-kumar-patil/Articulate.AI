from groq import Groq
from backend.config import Config
import pyttsx3


client = Groq(api_key=Config.GROQ_API_KEY)

def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )
    return transcription.text                                                                           

def speak_question(text:str):
    engine=pyttsx3.init()
    engine.setProperty("rate",150) #speeking speed
    engine.setProperty("volume", 1.0) # volume 0-1
    engine.say(text)
    engine.runAndWait()

