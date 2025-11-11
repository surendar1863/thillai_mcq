import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# =========================
# FIREBASE INITIALIZATION (Streamlit Cloud)
# =========================
if not firebase_admin._apps:
    try:
        firebase_config = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception:
        st.error("❌ Firebase initialization failed. Check your Streamlit Secrets.")
        st.stop()

db = firestore.client()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="MCQ Quiz App", layout="centered")
st.title("🧠 Online Quiz")

# =========================
# USER DETAILS
# =========================
name = st.text_input("Enter your full name")

# =========================
# LOAD QUESTIONS
# =========================
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")
    if "Sl No" in df.columns:
        df = df.drop(columns=["Sl No"])
    return df

questions_df = load_questions()

# =========================
# QUIZ FORM
# =========================
st.markdown("---")
st.markdown("### 📝 Answer the following questions")

answers = {}
for i, row in questions_df.iterrows():
    q = row["Question"]
    opts = ["--Select--", row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
    answers[i] = st.radio(f"**Q{i+1}. {q}**", opts, key=f"q{i}")

# =========================
# SUBMIT & SCORE
# =========================
if st.button("Submit Quiz"):
    if not name.strip():
        st.warning("Please enter your name before submitting.")
    else:
        total_questions = len(questions_df)
        score = 0
        for i, row in questions_df.iterrows():
            correct = str(row["Answer"]).strip()
            selected = str(answers[i]).strip()
            if selected != "--Select--" and selected == correct:
                score += 1

        st.success(f"🎯 {name}, you scored **{score}/{total_questions}**!")

        # Each user’s name as unique document ID
        doc_ref = db.collection("quiz_scores").document(name)
        doc = doc_ref.get()
        if doc.exists:
            st.warning("⚠️ You have already submitted the quiz.")
        else:
            doc_ref.set({"name": name, "score": score})
            st.info("✅ Your response has been recorded successfully!")
