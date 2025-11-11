import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# =========================
# FIREBASE INITIALIZATION
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # replace with your key file
    firebase_admin.initialize_app(cred)
db = firestore.client()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="MCQ Quiz App", layout="centered")
st.title("🧠 Online Quiz (Firebase Enabled)")

# =========================
# USER DETAILS
# =========================
name = st.text_input("Enter your full name")
email = st.text_input("Enter your email ID")

# =========================
# LOAD QUESTIONS
# =========================
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")
    # Drop the Sl No column if present
    if "Sl No" in df.columns:
        df = df.drop(columns=["Sl No"])
    return df

questions_df = load_questions()

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

        st.success(f"🎯 {name}, you scored **{score}/{total_questions}**!")

        # Save to Firestore (prevent multiple submissions)
        doc_ref = db.collection("quiz_scores").where("email", "==", email).get()
        if len(doc_ref) == 0:
            db.collection("quiz_scores").add({
                "name": name,
                "email": email,
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
        st.table(df.sort_values(by="Score", ascending=False).reset_index(drop=True))
