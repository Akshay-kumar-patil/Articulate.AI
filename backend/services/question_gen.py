import json
import re
from groq import Groq
from backend.config import Config


client = Groq(api_key=Config.GROQ_API_KEY)

FIXED_QUESTIONS = [
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

    response = client.chat.completions.create(
        model=Config.GROQ_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1000
    )

    raw = response.choices[0].message.content
    # Strip markdown code fences if the model wraps in ```json ... ```
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()

    try:
        generated = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to extract a JSON array from anywhere in the response
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if match:
            generated = json.loads(match.group())
        else:
            # If parsing completely fails, return a safe fallback question
            generated = [f"Can you describe a challenging {difficulty} project you've worked on?"]

    return FIXED_QUESTIONS + generated