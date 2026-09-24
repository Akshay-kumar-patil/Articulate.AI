from groq import Groq
from backend.config import Config


client = Groq(api_key=Config.GROQ_API_KEY)


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file using Groq's Whisper API.
    Returns the transcribed text.
    Raises an exception if the API call fails.
    """
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )
    return transcription.text

# NOTE: pyttsx3 / speak_question removed — it requires the 'espeak' system
# package which is not available on Render free-tier Linux containers.
# Text-to-speech is handled entirely in the browser (Web UI) or via
# gTTS in the Streamlit frontend, so no server-side TTS is needed.

