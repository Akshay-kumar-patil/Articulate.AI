import json
from groq import Groq
from backend.config import Config


client=Groq(api_key=Config.GROQ_API_KEY)

FIXED_QUESTIONS=[
    "Tell me about yourself.",
    "Tell me about your projects."
]

def generate_questions(resume_info: dict, difficulty: str, total_questions: int) -> list:
    remaining = total_questions - len(FIXED_QUESTIONS)

    prompt = f"""
You are a real technical interviewer. Based ONLY on this candidate's resume info,
generate {remaining} realistic interview questions at {difficulty} difficulty.

Resume info:
{json.dumps(resume_info)}

Return ONLY a JSON list of strings, nothing else. Example:
["question 1", "question 2"]
"""
    
    response=client.chat.completions.create(

        model=Config.GROQ_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1000
    )

    generated = json.loads(response.choices[0].message.content)
    return FIXED_QUESTIONS + generated