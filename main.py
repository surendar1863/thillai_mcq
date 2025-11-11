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
        firebase_config = dict(st.secrets["firebase"])  # from Streamlit Secrets
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

        # Show score popup
        st.success(f"🎯 {name}, you scored **{score}/{total_questions}**!")

        # Check if this name already submitted
        existing = db.collection("quiz_scores").where("name", "==", name).get()
        if len(existing) == 0:
            db.collection("quiz_scores").add({
                "name": name,
                "score": score
            })
            st.info("✅ Your response has been recorded successfully!")
        else:
            st.warning("⚠️ You have already submitted the quiz.")

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
