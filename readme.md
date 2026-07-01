# 🎤 Articulate.AI — Verbal Mock Interview Preparation App

Articulate.AI is an AI-powered mock interview platform that conducts **real verbal interviews** based on your resume. The bot asks questions out loud, you answer by speaking, and it scores your responses using AI.

---

## 🚀 Features

- 📄 **Resume-based questions** — upload your PDF resume and get personalized interview questions generated from your actual skills and projects
- 🎙️ **Voice interaction** — the bot speaks questions aloud (Google TTS) and transcribes your spoken answers (Whisper via Groq)
- 🤖 **AI scoring** — every answer is scored as `correct`, `partial`, or `wrong` with a reason
- 🎯 **Confidence scoring** — first 2 questions ("tell me about yourself" and "tell me about your projects") are also scored for attitude and confidence
- ⚙️ **Difficulty levels** — choose easy, medium, or hard
- 📊 **Analytics report** — full per-question breakdown after each interview
- 🗂️ **Interview history** — past interviews saved to your account, viewable anytime
- 🗑️ **Delete anytime** — permanently delete individual interviews or your entire account

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Speech-to-text | Whisper (via Groq) |
| Text-to-speech | Google TTS (gTTS) |
| Database | MongoDB |
| Password security | bcrypt |

---

## 📁 Project Structure

```
Articulate.AI/
├── frontend/
│   └── app.py                  # Streamlit UI
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # App configuration
│   ├── routes/
│   │   ├── auth.py             # Signup, login, verify
│   │   ├── resume.py           # PDF upload and parsing
│   │   ├── interview.py        # Question generation, audio, scoring
│   │   └── analytics.py        # Save, fetch, delete interviews
│   ├── services/
│   │   ├── resume_parser.py    # Extract skills/projects from resume
│   │   ├── question_gen.py     # AI question generation
│   │   ├── speech.py           # Whisper transcription
│   │   └── scorer.py           # AI answer scoring
│   ├── db/
│   │   └── models.py           # MongoDB collections and schemas
│   └── auth/
│       └── security.py         # Password hashing and verification
├── .env                        # Environment variables (never commit this)
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/Akshay-kumar-patil/Articulate.AI.git
cd Articulate.AI
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file in the root directory
```
GROQ_API_KEY=your_groq_api_key
MONGO_URI=mongodb://localhost:27017
SECRET_KEY=any_random_long_string
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Start the backend
```bash
uvicorn backend.main:app --reload
```

### 6. Start the frontend (in a new terminal)
```bash
streamlit run frontend/app.py
```

---

## 🔄 How It Works

```
1. Sign up / Login
2. Upload your resume PDF
3. Select difficulty (easy / medium / hard) and number of questions (5-15)
4. AI generates personalized questions from your resume
5. Bot asks each question out loud
6. You answer by speaking into your mic
7. Whisper transcribes your answer
8. Groq AI scores your answer (correct / partial / wrong)
9. After all questions — view your full analytics report
10. Save or delete your interview history anytime
```

---

## 📊 Scoring System

| Question | Scoring criteria |
|---|---|
| Q1 — Tell me about yourself | Content + attitude + confidence score (0-10) |
| Q2 — Tell me about your projects | Content + attitude + confidence score (0-10) |
| Q3 onwards | correct / partial / wrong + reason |

---

## 🌐 Deployment

- **Backend** — deployed on [Render](https://articulate-ai.onrender.com/)
- **Frontend** — deployed on [Streamlit Cloud](https://articulateai-akki.streamlit.app/)
- **Database** — MongoDB Atlas (free tier)

---

## ⚠️ Known Limitations

- Whisper transcription accuracy depends on mic quality and background noise — speak clearly and close to the mic for best results
- Render free tier sleeps after 15 minutes of inactivity — first request after idle may take 30-60 seconds to wake up
- gTTS requires an internet connection for text-to-speech

---

