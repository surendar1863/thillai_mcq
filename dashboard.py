import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
# FETCH DATA FROM FIRESTORE
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
# DISPLAY DATA TABLE
# =========================
st.subheader("📋 Participant Scores")
st.dataframe(df.sort_values(by="score", ascending=False).reset_index(drop=True), use_container_width=True)

# =========================
# DOWNLOAD RESULTS
# =========================
if not df.empty:
    st.markdown("### 💾 Download Results")

    # CSV download
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,
        file_name="quiz_results.csv",
        mime="text/csv"
    )

    # Excel download
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
# VISUALIZATION SECTION
# =========================
if not df.empty:
    st.subheader("📈 Score Distribution")

    # Seaborn style for clean visuals
    sns.set_style("whitegrid")

    # Compact histogram
    fig, ax = plt.subplots(figsize=(4.5, 3))
    sns.histplot(df["score"], bins=10, kde=False, ax=ax, color="#3b8ed0", edgecolor="black")
    ax.set_xlabel("Score", fontsize=10)
    ax.set_ylabel("Number of Students", fontsize=10)
    ax.set_title("Score Distribution", fontsize=12, pad=10)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

    # =========================
    # ANALYTICS SUMMARY
    # =========================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📈 Average", round(df["score"].mean(), 2))
    with col2:
        st.metric("🏆 Highest", df["score"].max())
    with col3:
        st.metric("📉 Lowest", df["score"].min())
    with col4:
        st.metric("👥 Participants", len(df))

    # =========================
    # TOP PERFORMERS
    # =========================
    st.subheader("🏅 Top Performers")
    top_df = df.sort_values(by="score", ascending=False).head(5)
    st.dataframe(top_df.reset_index(drop=True), use_container_width=True)
