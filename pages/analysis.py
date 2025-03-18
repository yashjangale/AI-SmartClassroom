import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# ✅ Set Streamlit Page Config at the Top
st.set_page_config(page_title="Student Performance Analysis", layout="wide")

# Load environment variables
load_dotenv()

# MongoDB Connection
client = MongoClient(os.environ.get('MONGO_DB_URI'))

# Retrieve student ID and quiz ID from session
student_id = st.session_state.get("student_id")
quiz_id = st.session_state.get("quiz_id")  # Quiz student attempted

if not student_id or not quiz_id:
    st.error("❌ Error: Missing student ID or quiz ID.")
    st.stop()

# ✅ Extract Subject Name from quiz_id (e.g., "history" from "history101")
subject_name = "".join(filter(str.isalpha, quiz_id)).lower()

# ✅ Connect to the Correct Database
db = client[subject_name]

# Ensure "test_scores" collection exists
if "test_scores" not in db.list_collection_names():
    st.error(f"❌ Collection 'test_scores' not found in database '{subject_name}'.")
    st.stop()

collection = db["test_scores"]

# ✅ Fetch Student's Test Data
student_data = list(collection.find({"student_id": student_id}))

if not student_data:
    st.warning(f"⚠️ No test data found for Student ID: {student_id}")
    st.stop()

# ✅ Convert to DataFrame
df = pd.DataFrame(student_data)
df.columns = df.columns.str.strip().str.lower()  # Ensure consistency

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# ✅ Streamlit Dashboard
st.title("📊 Student Performance Analysis")

# ✅ Student Overview
st.header(f"Performance Overview: {student_id}")

latest_score = df.iloc[-1]
accuracy = (latest_score["score"] / latest_score["total"]) * 100

col1, col2 = st.columns(2)

with col1:
    st.metric("Latest Score", f"{latest_score['score']} / {latest_score['total']}")
with col2:
    st.progress(accuracy / 100)

# ✅ Score Progression Line Chart
st.subheader("📈 Score Progression Over Time")
line_chart = px.line(
    df,
    x="timestamp",
    y="score",
    title="Score Progression",
    labels={"timestamp": "Time", "score": "Score"},
    markers=True
)
st.plotly_chart(line_chart, use_container_width=True)

# ✅ Quiz Performance Bar Chart
st.subheader("📊 Performance by Quiz")
bar_chart = px.bar(
    df,
    x="quiz_id",
    y="score",
    title="Scores Across Quizzes",
    labels={"quiz_id": "Quiz", "score": "Score"},
    color="score",
    color_continuous_scale="Blues"
)
st.plotly_chart(bar_chart, use_container_width=True)

# ✅ Display Detailed Score Table
st.subheader("📄 Detailed Quiz Results")
st.dataframe(df[["quiz_id", "score", "total", "timestamp"]])

st.markdown("Built with ❤️ using Streamlit")