import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64
from streamlit_cookies_manager import EncryptedCookieManager
import io

API_URL = "http://127.0.0.1:8000"

cookies = EncryptedCookieManager(prefix="articulate_", password="your_secret_key")
if not cookies.ready():
    st.stop()

if "spoken_q" not in st.session_state:
    st.session_state.spoken_q = -1

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

# Initialize session state
if "logged_in" not in st.session_state:
    saved_user_id = cookies.get("user_id")
    if saved_user_id:
        try:
            verify = requests.get(f"{API_URL}/auth/verify/{saved_user_id}")
            if verify.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user_id = saved_user_id
            else:
                cookies["user_id"] = ""
                cookies.save()
                st.session_state.logged_in = False
        except:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "resume_info" not in st.session_state:
    st.session_state.resume_info = None
if "processed_q" not in st.session_state:
    st.session_state.processed_q = -1

st.title("🎤 Articulate.AI")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post(f"{API_URL}/auth/login", json={
                "email": email, "password": password
            })
            if res.status_code == 200:
                data = res.json()
                st.session_state.logged_in = True
                st.session_state.user_id = data["user_id"]
                cookies["user_id"] = data["user_id"]
                cookies.save()
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        username = st.text_input("Username", key="signup_user")
        signup_email = st.text_input("Email", key="signup_email")
        signup_pass = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Signup"):
            res = requests.post(f"{API_URL}/auth/signup", json={
                "username": username, "email": signup_email, "password": signup_pass
            })
            if res.status_code == 200:
                st.success("Account created! Please login.")
            else:
                st.error(res.json()["detail"])

else:
    st.sidebar.write(f"👤 User ID: {st.session_state.user_id}")

    # ---- LOGOUT + DELETE ACCOUNT ----
    if st.sidebar.button("🚪 Logout"):
        cookies["user_id"] = ""
        cookies.save()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if st.sidebar.button("🗑️ Delete My Account"):
        del_res = requests.delete(f"{API_URL}/analytics/delete-user/{st.session_state.user_id}")
        if del_res.status_code == 200:
            cookies["user_id"] = ""
            cookies.save()
            st.sidebar.success("Account deleted permanently")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        else:
            st.sidebar.error("Failed to delete account")

    page = st.sidebar.radio("Navigate", ["Interview", "My Reports"])

    # ============ INTERVIEW PAGE ============
    if page == "Interview":

        # ---- RESUME UPLOAD ----
        st.subheader("📄 Upload your resume")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        if uploaded_file and st.button("Process Resume"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            res = requests.post(f"{API_URL}/resume/upload-resume", files=files)
            if res.status_code == 200:
                data = res.json()
                st.session_state.resume_info = data["resume_info"]
                st.success("Resume processed! You can now start the interview.")
            else:
                st.error("Failed to process resume")

        # ---- GUARD: resume must be uploaded before interview ----
        if not st.session_state.resume_info:
            st.warning("⚠️ Please upload and process your resume first to start the interview.")
            st.stop()

        # ---- INTERVIEW SETTINGS ----
        st.subheader("⚙️ Interview settings")
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
        total_questions = st.slider("Number of questions", 5, 15, 5)

        if st.button("Generate Questions"):
            res = requests.post(f"{API_URL}/question/generate-questions", json={
                "resume_info": st.session_state.resume_info,
                "difficulty": difficulty,
                "total_questions": total_questions
            })
            if res.status_code == 200:
                st.session_state.questions = res.json()["questions"]
                st.session_state.current_q = 0
                st.session_state.answers = []
                st.session_state.difficulty = difficulty
                st.session_state.saved = False
                st.session_state.processed_q = -1
                st.success(f"{len(st.session_state.questions)} questions ready!")
            else:
                st.error("Failed to generate questions")

        # ---- INTERVIEW SCREEN ----
        if "questions" in st.session_state and st.session_state.current_q < len(st.session_state.questions):
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
                key=f"rec_{q_index}"
            )

            if audio and st.session_state.processed_q != q_index:
                st.session_state.processed_q = q_index

                audio_bytes = audio["bytes"]
                files = {"file": ("answer.wav", audio_bytes, "audio/wav")}

                with st.spinner("Transcribing your answer..."):
                    res = requests.post(f"{API_URL}/question/answer-audio", files=files)

                if res.status_code == 200:
                    transcribed_text = res.json()["text"]
                    st.write("**Your answer:**", transcribed_text)

                    is_intro = q_index < 2

                    with st.spinner("Scoring your answer..."):
                        score_res = requests.post(f"{API_URL}/question/score-answer", json={
                            "question": question_text,
                            "answer": transcribed_text,
                            "is_intro_question": is_intro
                        })

                    if score_res.status_code == 200:
                        score_data = score_res.json()
                        st.session_state.answers.append({
                            "question": question_text,
                            "answer": transcribed_text,
                            **score_data
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

            # Show Next button only after answer is processed
            if st.session_state.processed_q == q_index:
                if st.button("Next Question ➡️"):
                    st.session_state.current_q += 1
                    st.rerun()

        # ---- INTERVIEW COMPLETE: AUTO-SAVE ----
        elif "questions" in st.session_state:
            st.success("🎉 Interview complete!")

            if not st.session_state.get("saved", False):
                with st.spinner("Saving your results..."):
                    save_res = requests.post(f"{API_URL}/analytics/save-interview", json={
                        "user_id": st.session_state.user_id,
                        "difficulty": st.session_state.difficulty,
                        "answers": st.session_state.answers
                    })
                if save_res.status_code == 200:
                    st.session_state.saved = True
                    st.info("✅ Saved to your report history")

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
                st.session_state.saved = False
                st.session_state.resume_info = None
                st.rerun()

    # ============ MY REPORTS PAGE ============
    elif page == "My Reports":
        st.subheader("📊 My Interview Reports")

        res = requests.get(f"{API_URL}/analytics/get-report/{st.session_state.user_id}")
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

                with st.expander(f"📅 {interview['created_at']} — {interview['difficulty'].upper()} — ✅{correct} ⚠️{partial} ❌{wrong}"):
                    for i, ans in enumerate(interview["answers"]):
                        verdict = ans["verdict"]
                        icon = "✅" if verdict == "correct" else "⚠️" if verdict == "partial" else "❌"
                        st.write(f"{icon} **Q{i+1}: {ans['question']}**")
                        st.write(f"Answer: {ans['answer']}")
                        st.write(f"Verdict: {verdict} — {ans['reason']}")
                        if "confidence_score" in ans:
                            st.write(f"🎯 Confidence: {ans['confidence_score']}/10")
                        st.divider()

                    if st.button("🗑️ Delete this interview", key=f"del_{interview['_id']}"):
                        del_res = requests.delete(f"{API_URL}/analytics/delete-session/{interview['_id']}")
                        if del_res.status_code == 200:
                            st.success("Deleted permanently")
                            st.rerun()
                        else:
                            st.error("Failed to delete")