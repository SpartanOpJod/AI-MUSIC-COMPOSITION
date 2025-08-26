# app.py
import streamlit as st
from mood_analyzer import MoodAnalyzer

st.title("🎶 AI Mood-Based Music Composer")

user_input = st.text_area("How are you feeling today?", "I'm feeling happy and energetic")

if st.button("Analyze Mood"):
    analyzer = MoodAnalyzer()
    result = analyzer.analyze(user_input)

    st.subheader("Mood Analysis Results")
    st.write(result)
