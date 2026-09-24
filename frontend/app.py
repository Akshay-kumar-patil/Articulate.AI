import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64
import io

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_URL = st.secrets["Backend_URL"].rstrip("/")

# ─────────────────────────────────────────────
# TEXT-TO-SPEECH
# ─────────────────────────────────────────────
def speak(text: str):
    tts = gTTS(text=text, lang="en")
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    audio_base64 = base64.b64encode(audio_buffer.read()).decode()
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for key, default in {
    "session_id": None,
    "username": None,
    "logged_in": False,
    "resume_info": None,
    "questions": None,
    "current_q": 0,
    "answers": [],
    "difficulty": "medium",
    "saved": False,
    "processed_q": -1,
    "spoken_q": -1,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────
st.title("🎤 Articulate.AI")

# ─────────────────────────────────────────────
# AUTH: SESSION START (replaces login/signup)
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("### Welcome! Enter your name to begin.")
    st.info(
        "ℹ️ No account required. Your session and data exist only while this "
        "server is running — they are cleared automatically when the server restarts."
    )

    name = st.text_input("Your name", placeholder="e.g. Akshay", key="input_name")

    if st.button("Start Session"):
        if not name.strip():
            st.error("Please enter your name.")
        else:
            try:
                res = requests.post(
                    f"{API_URL}/auth/start-session",
                    json={"name": name.strip()},
                    timeout=10,
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.username = data["name"]
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error(f"Failed to start session: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Could not connect to backend at `{API_URL}`. "
                    "Make sure the backend is running."
                )

    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.write(f"👤 **{st.session_state.username}**")
st.sidebar.caption(f"Session: `{st.session_state.session_id[:8]}…`")

if st.sidebar.button("🚪 End Session"):
    try:
        requests.delete(
            f"{API_URL}/auth/end-session/{st.session_state.session_id}",
            timeout=5,
        )
    except Exception:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

page = st.sidebar.radio("Navigate", ["Interview", "My Reports"])

# ─────────────────────────────────────────────
# INTERVIEW PAGE
# ─────────────────────────────────────────────
if page == "Interview":

    # ---- RESUME UPLOAD ----
    st.subheader("📄 Upload your resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file and st.button("Process Resume"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        with st.spinner("Parsing resume..."):
            res = requests.post(f"{API_URL}/resume/upload-resume", files=files, timeout=30)
        if res.status_code == 200:
            data = res.json()
            st.session_state.resume_info = data["resume_info"]
            st.success("Resume processed! You can now start the interview.")
        else:
            st.error(f"Failed to process resume: {res.text}")

    if not st.session_state.resume_info:
        st.warning("⚠️ Please upload and process your resume first.")
        st.stop()

    # ---- INTERVIEW SETTINGS ----
    st.subheader("⚙️ Interview settings")
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
    total_questions = st.slider("Number of questions", 5, 15, 5)

    if st.button("Generate Questions"):
        with st.spinner("Generating questions..."):
            res = requests.post(
                f"{API_URL}/question/generate-questions",
                json={
                    "resume_info": st.session_state.resume_info,
                    "difficulty": difficulty,
                    "total_questions": total_questions,
                },
                timeout=30,
            )
        if res.status_code == 200:
            st.session_state.questions = res.json()["questions"]
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.session_state.difficulty = difficulty
            st.session_state.saved = False
            st.session_state.processed_q = -1
            st.session_state.spoken_q = -1
            st.success(f"{len(st.session_state.questions)} questions ready!")
        else:
            st.error(f"Failed to generate questions: {res.text}")

    # ---- INTERVIEW SCREEN ----
    if st.session_state.questions and st.session_state.current_q < len(st.session_state.questions):
        q_index = st.session_state.current_q
        question_text = st.session_state.questions[q_index]

        st.subheader(f"Question {q_index + 1} of {len(st.session_state.questions)}")
        st.info(question_text)

        if st.session_state.spoken_q != q_index:
            st.session_state.spoken_q = q_index
            speak(question_text)

        st.empty()

        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop",
            key=f"rec_{q_index}",
        )

        if audio and st.session_state.processed_q != q_index:
            st.session_state.processed_q = q_index
            audio_bytes = audio["bytes"]
            files = {"file": ("answer.wav", audio_bytes, "audio/wav")}

            with st.spinner("Transcribing your answer..."):
                res = requests.post(
                    f"{API_URL}/question/answer-audio",
                    files=files,
                    timeout=30,
                )

            if res.status_code == 200:
                transcribed_text = res.json()["text"]
                st.write("**Your answer:**", transcribed_text)

                is_intro = q_index < 2

                with st.spinner("Scoring your answer..."):
                    score_res = requests.post(
                        f"{API_URL}/question/score-answer",
                        json={
                            "question": question_text,
                            "answer": transcribed_text,
                            "is_intro_question": is_intro,
                        },
                        timeout=20,
                    )

                if score_res.status_code == 200:
                    score_data = score_res.json()
                    st.session_state.answers.append({
                        "question": question_text,
                        "answer": transcribed_text,
                        **score_data,
                    })

                    verdict = score_data["verdict"]
                    if verdict == "correct":
                        st.success(f"✅ Verdict: {verdict} — {score_data['reason']}")
                    elif verdict == "partial":
                        st.warning(f"⚠️ Verdict: {verdict} — {score_data['reason']}")
                    else:
                        st.error(f"❌ Verdict: {verdict} — {score_data['reason']}")

                    if "confidence_score" in score_data:
                        st.write(f"🎯 Confidence score: {score_data['confidence_score']}/10")
            else:
                st.error(f"Transcription failed: {res.text}")

        if st.session_state.processed_q == q_index:
            if st.button("Next Question ➡️"):
                st.session_state.current_q += 1
                st.rerun()

    # ---- INTERVIEW COMPLETE: AUTO-SAVE ----
    elif st.session_state.questions:
        st.success("🎉 Interview complete!")

        if not st.session_state.get("saved", False):
            with st.spinner("Saving your results..."):
                save_res = requests.post(
                    f"{API_URL}/analytics/save-interview",
                    json={
                        "session_id": st.session_state.session_id,
                        "difficulty": st.session_state.difficulty,
                        "answers": st.session_state.answers,
                    },
                    timeout=10,
                )
            if save_res.status_code == 200:
                st.session_state.saved = True
                st.info("✅ Saved to your report history")
            else:
                st.warning(f"Could not save report: {save_res.text}")

        st.subheader("📋 Quick summary")
        for i, ans in enumerate(st.session_state.answers):
            verdict = ans["verdict"]
            icon = "✅" if verdict == "correct" else "⚠️" if verdict == "partial" else "❌"
            st.write(f"{icon} **Q{i+1}:** {ans['question']}")
            st.write(f"Verdict: {verdict} — {ans['reason']}")
            if "confidence_score" in ans:
                st.write(f"Confidence: {ans['confidence_score']}/10")
            st.divider()

        if st.button("🔄 Start new interview"):
            st.session_state.questions = None
            st.session_state.answers = []
            st.session_state.current_q = 0
            st.session_state.processed_q = -1
            st.session_state.spoken_q = -1
            st.session_state.saved = False
            st.session_state.resume_info = None
            st.rerun()

# ─────────────────────────────────────────────
# MY REPORTS PAGE
# ─────────────────────────────────────────────
elif page == "My Reports":
    st.subheader("📊 My Interview Reports")

    res = requests.get(
        f"{API_URL}/analytics/get-report/{st.session_state.session_id}",
        timeout=10,
    )
    if res.status_code == 200:
        interviews = res.json()["interviews"]

        if not interviews:
            st.write("No interviews yet. Go complete one!")
        else:
            st.write(f"Total interviews: **{len(interviews)}**")

        for interview in interviews:
            total = len(interview["answers"])
            correct = sum(1 for a in interview["answers"] if a["verdict"] == "correct")
            partial = sum(1 for a in interview["answers"] if a["verdict"] == "partial")
            wrong = sum(1 for a in interview["answers"] if a["verdict"] == "wrong")

            with st.expander(
                f"📅 {interview['created_at']} — {interview['difficulty'].upper()} "
                f"— ✅{correct} ⚠️{partial} ❌{wrong}"
            ):
                for i, ans in enumerate(interview["answers"]):
                    verdict = ans["verdict"]
                    icon = "✅" if verdict == "correct" else "⚠️" if verdict == "partial" else "❌"
                    st.write(f"{icon} **Q{i+1}: {ans['question']}**")
                    st.write(f"Answer: {ans['answer']}")
                    st.write(f"Verdict: {verdict} — {ans['reason']}")
                    if "confidence_score" in ans:
                        st.write(f"🎯 Confidence: {ans['confidence_score']}/10")
                    st.divider()

                if st.button(
                    "🗑️ Delete this interview",
                    key=f"del_{interview['interview_id']}",
                ):
                    del_res = requests.delete(
                        f"{API_URL}/analytics/delete-interview"
                        f"/{st.session_state.session_id}/{interview['interview_id']}",
                        timeout=10,
                    )
                    if del_res.status_code == 200:
                        st.success("Deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete")
    else:
        st.error(f"Failed to load reports: {res.text}")