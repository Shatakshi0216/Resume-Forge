# file: reviewer/ai_suggestions.py

import streamlit as st
import google.generativeai as genai
import json

# Configure the Gemini API key from Streamlit secrets
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    GEMINI_MODEL = genai.GenerativeModel('gemini-flash-latest')
except (KeyError, Exception):
    GEMINI_MODEL = None

def get_ai_suggestions(resume_text: str, job_description: str, missing_skills: list):
    """
    Uses Gemini to generate qualitative feedback and suggestions for a resume.
    """
    if not GEMINI_MODEL:
        st.error("Gemini AI model is not configured. Please add your GOOGLE_API_KEY to the Streamlit secrets.")
        return "AI Suggestions are unavailable."
        
    prompt = f"""
    You are an expert career coach and professional resume reviewer. Your task is to provide
    actionable feedback on a resume based on a specific job description.

    Here is the user's resume text:
    ---
    {resume_text}
    ---

    Here is the target job description:
    ---
    {job_description}
    ---

    Based on my previous analysis, these key skills from the job description appear to be missing from the resume: {', '.join(missing_skills)}.

    Please provide your feedback in Markdown format with the following structure:

    ### **Overall Impression**
    Start with a brief, encouraging summary of the resume's strengths and overall structure.

    ### **Alignment with Job Description**
    Critically analyze how well the resume is tailored to the job description. Point out specific areas where the alignment could be stronger. Use the list of missing skills as a starting point, but also look for gaps in experience or project relevance.

    ### **Action Verb Analysis**
    Review the bullet points in the work experience section. Suggest 3-5 stronger, more impactful action verbs to replace weaker ones (e.g., instead of "Responsible for...", suggest "Orchestrated...", "Engineered...", "Managed...").

    ### **Content & Clarity**
    Provide one or two suggestions to improve the clarity, conciseness, or impact of the professional summary or project descriptions.
    
    Keep your feedback constructive and professional.
    """

    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI suggestions: {e}"
    

# Add this new function to the bottom of reviewer/ai_suggestions.py

def get_general_ai_feedback(resume_text: str):
    """
    Uses Gemini to generate a general quality review of a resume
    when no job description is provided.
    """
    if not GEMINI_MODEL:
        st.error("Gemini AI model is not configured. Please add your GOOGLE_API_KEY to the Streamlit secrets.")
        return {"score": 0, "feedback": "AI Suggestions are unavailable."}
        
    prompt = f"""
    You are an expert career coach. Your task is to provide a general quality review of a resume.
    Do not ask for a job description. Analyze the resume on its own merits.

    Here is the user's resume text:
    ---
    {resume_text}
    ---

    Please perform the following analysis:
    1.  **Assign a "Resume Quality Score"** from 0 to 100 based on clarity, structure, impact, and the use of best practices.
    2.  **Provide a brief summary** of the resume's main strengths.
    3.  **Give 2-3 specific, actionable suggestions** for improvement. Focus on things like strengthening the summary, using more quantifiable achievements, or improving action verbs.

    Return your response as a JSON object with two keys: "score" (an integer) and "feedback" (a string in Markdown format).
    Example: {{"score": 85, "feedback": "### Strengths\\n- Your resume is well-structured...\\n### Areas for Improvement\\n- Consider quantifying achievements..."}}
    """

    try:
        response = GEMINI_MODEL.generate_content(prompt)
        # Clean up the response to extract only the JSON part
        json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    except Exception as e:
        return {"score": 0, "feedback": f"Error generating AI feedback: {e}"}
