import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# =========================
# FIREBASE INITIALIZATION
# =========================
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# PAGE CONFIG
# =========================
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
# DOWNLOAD SECTION
# =========================
if not df.empty:
    st.markdown("### 💾 Download Results")

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,
        file_name="quiz_results.csv",
        mime="text/csv"
    )

    # Excel version
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    st.download_button(
        label="📘 Download as Excel",
        data=buffer.getvalue(),
        file_name="quiz_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =========================
# VISUALIZATION
# =========================
if not df.empty:
    st.subheader("📈 Score Distribution")
    fig, ax = plt.subplots(figsize=(6, 4))  # smaller plot size
    ax.hist(df["score"], bins=10, edgecolor='black')
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Students")
    ax.set_title("Score Distribution Histogram")
    st.pyplot(fig)

    st.subheader("🏆 Top Performers")
    top_df = df.sort_values(by="score", ascending=False).head(5)
    st.table(top_df.reset_index(drop=True))
