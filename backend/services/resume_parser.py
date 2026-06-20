import json
from groq import Groq
from backend.config import Config

client =Groq(api_key=Config.GROQ_API_KEY)

def extract_resume_info(resume_text: str)->dict:
    prompt = f"""
Extract ONLY information that literally appears in this resume text.
Do NOT guess, assume, or add anything not explicitly written.
If a field is not found, return an empty list.

Return ONLY valid JSON, no extra text, in this exact format:
{{
  "technical_skills": [],
  "projects": [],
  "achievements": [],
  "certificates":[]
}}

Resume text:
{resume_text}
"""
    
    response=client.chat.completions.create(
        model=Config.GROQ_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    raw = response.choices[0].message.content
    return json.loads(raw)