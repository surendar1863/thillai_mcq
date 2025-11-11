import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# FIREBASE INITIALIZATION
# =========================
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Quiz Dashboard", layout="wide")
st.title("📊 Faculty Dashboard – Quiz Results")

# =========================
# FETCH DATA
# =========================
def load_data():
    docs = db.collection("quiz_scores").stream()
    data = [d.to_dict() for d in docs]
    if not data:
        st.warning("No quiz results found yet.")
        return pd.DataFrame(columns=["name", "score"])
    return pd.DataFrame(data)

df = load_data()

# =========================
# DISPLAY TABLE
# =========================
st.subheader("📋 Participant Scores")
st.dataframe(df.sort_values(by="score", ascending=False).reset_index(drop=True))

# =========================
# VISUALIZATION
# =========================
if not df.empty:
    st.subheader("📈 Score Distribution")
    fig, ax = plt.subplots()
    ax.hist(df["score"], bins=10, edgecolor='black')
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Students")
    ax.set_title("Score Distribution Histogram")
    st.pyplot(fig)

    st.subheader("🏆 Top Performers")
    top_df = df.sort_values(by="score", ascending=False).head(5)
    st.table(top_df.reset_index(drop=True))
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# FIREBASE INITIALIZATION
# =========================
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Quiz Dashboard", layout="wide")
st.title("📊 Faculty Dashboard – Quiz Results")

# =========================
# FETCH DATA
# =========================
def load_data():
    docs = db.collection("quiz_scores").stream()
    data = [d.to_dict() for d in docs]
    if not data:
        st.warning("No quiz results found yet.")
        return pd.DataFrame(columns=["name", "score"])
    return pd.DataFrame(data)

df = load_data()

# =========================
# DISPLAY TABLE
# =========================
st.subheader("📋 Participant Scores")
st.dataframe(df.sort_values(by="score", ascending=False).reset_index(drop=True))

# =========================
# VISUALIZATION
# =========================
if not df.empty:
    st.subheader("📈 Score Distribution")
    fig, ax = plt.subplots()
    ax.hist(df["score"], bins=10, edgecolor='black')
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Students")
    ax.set_title("Score Distribution Histogram")
    st.pyplot(fig)

    st.subheader("🏆 Top Performers")
    top_df = df.sort_values(by="score", ascending=False).head(5)
    st.table(top_df.reset_index(drop=True))
