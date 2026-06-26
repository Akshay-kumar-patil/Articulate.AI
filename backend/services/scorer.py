import json
from groq import Groq
import re
from backend.config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

def score_answer(question: str, answer: str, is_intro_question: bool = False) -> dict:
    extra_field = ""
    if is_intro_question:
        extra_field = '"confidence_score": 0,'

    prompt = f"""
You are a strict technical interviewer evaluating one answer.
Question: {question}
Candidate's answer: {answer}

Judge ONLY based on what the candidate actually said. Do not assume anything extra.

Return ONLY valid JSON in this exact format, nothing else:
{{
  "verdict": "correct" or "partial" or "wrong",
  "reason": "one short sentence",
  {extra_field}
}}
"""

    response = client.chat.completions.create(
        model=Config.GROQ_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )
    raw = response.choices[0].message.content
    raw = re.sub(r"```json|```", "", raw).strip()
    raw = re.sub(r",\s*}", "}", raw)
    print("GROQ RAW RESPONSE:", repr(raw))
    return json.loads(raw)
