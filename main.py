import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# =========================
# FIREBASE INITIALIZATION  (for Streamlit Cloud)
# =========================
if not firebase_admin._apps:
    try:
        # Load from Streamlit Secrets (preferred on Streamlit Cloud)
        firebase_config = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error("❌ Firebase initialization failed. Check your Streamlit Secrets.")
        st.stop()

db = firestore.client()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="MCQ Quiz App", layout="centered")
st.title("🧠 Online Quiz (Firebase Enabled)")

# =========================
# USER DETAILS
# =========================
st.markdown("### 👤 Participant Details")
name = st.text_input("Enter your full name")
email = st.text_input("Enter your email ID")

# =========================
# LOAD QUESTIONS
# =========================
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")
    if "Sl No" in df.columns:      # drop serial column if exists
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
    opts = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
    answers[i] = st.radio(f"**Q{i+1}. {q}**", opts, key=f"q{i}")

# =========================
# SUBMIT & SCORE
# =========================
if st.button("Submit Quiz"):
    if not name or not email:
        st.warning("Please enter your name and email before submitting.")
    else:
        total_questions = len(questions_df)
        score = 0
        for i, row in questions_df.iterrows():
            correct = str(row["Answer"]).strip()
            selected = str(answers[i]).strip()
            if selected == correct:
                score += 1

        # Display score popup
        st.success(f"🎯 {name}, you scored **{score}/{total_questions}**!")

        # Check if this email already submitted
        existing = db.collection("quiz_scores").where("email", "==", email).get()
        if len(existing) == 0:
            db.collection("quiz_scores").add({
                "name": name,
                "email": email,
                "score": score
            })
            st.info("✅ Your response has been recorded successfully!")
        else:
            st.warning("⚠️ You have already submitted the quiz. Only one attempt is allowed.")

        # =========================
        # DISPLAY LEADERBOARD
        # =========================
        st.subheader("🏅 Leaderboard (Live)")
        docs = db.collection("quiz_scores").stream()
        data = [{"Name": d.to_dict()["name"], "Score": d.to_dict()["score"]} for d in docs]
        df = pd.DataFrame(data)
        if len(df) > 0:
            st.table(df.sort_values(by="Score", ascending=False).reset_index(drop=True))
        else:
            st.info("No submissions yet.")
