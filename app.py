import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests

# =========================
# IMPORT CUSTOM MODULES
# =========================

from builder.form_handler import handle_resume_form
from reviewer.resume_parser import extract_text_from_pdf
from reviewer.ats_scoring import calculate_ats_score
from reviewer.ai_suggestions import (
    get_ai_suggestions,
    get_general_ai_feedback
)

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Resume Forge",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# LOAD CSS
# =========================

def load_custom_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("Custom CSS file not found.")

load_custom_css()

# =========================
# SESSION STATE
# =========================

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}

# =========================
# HERO SECTION
# =========================

st.markdown("""
<div class="hero-container">

<div class="hero-title">
🚀 Resume Forge
</div>

<div class="hero-subtitle">
Build stunning resumes, optimize ATS scores, and get AI-powered career insights instantly.
</div>

</div>
""", unsafe_allow_html=True)




# =========================
# NAVBAR
# =========================

st.markdown('<div class="navbar">', unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Build Resume", "ATS Review", "Suggestions"],
    icons=["pencil-square", "graph-up-arrow", "lightbulb"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "background-color": "transparent",
        },
        "nav-link": {
            "font-size": "16px",
            "font-weight": "600",
            "color": "#CBD5E1",
            "padding": "12px",
            "border-radius": "12px",
            "--hover-color": "#1E293B",
        },
        "nav-link-selected": {
            "background": "linear-gradient(90deg,#7C4DFF,#00D4FF)",
            "color": "white",
        },
    }
)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# BUILD RESUME SECTION
# ============================================================

if selected == "Build Resume":

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.header("📝 Resume Builder")

    st.write(
        "Fill out your details below and generate a professional ATS-friendly resume."
    )

    st.markdown("---")

    handle_resume_form()

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ATS REVIEW SECTION
# ============================================================

if selected == "ATS Review":

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.header("📊 ATS & Resume Review")

    st.write(
        "Upload your resume and analyze it against ATS systems or get general AI feedback."
    )

    uploaded_resume = st.file_uploader(
        "📄 Upload Resume (PDF)",
        type=["pdf"]
    )

    review_mode = st.checkbox(
        "Review against a specific Job Description",
        value=True
    )

    if review_mode:

        st.session_state.job_description = st.text_area(
            "📝 Paste Job Description Here",
            value=st.session_state.job_description,
            height=220
        )

    if st.button("🔍 Analyze Resume", use_container_width=True):

        if uploaded_resume:

            with st.spinner("AI is analyzing your resume... ⏳"):

                st.session_state.resume_text = extract_text_from_pdf(
                    uploaded_resume
                )

                # ATS Review Mode
                if review_mode:

                    if st.session_state.job_description:

                        st.session_state.analysis_results = calculate_ats_score(
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )

                        st.session_state.analysis_done = True

                    else:
                        st.warning(
                            "⚠️ Please paste a job description."
                        )

                        st.session_state.analysis_done = False

                # General Review Mode
                else:

                    st.session_state.analysis_results = (
                        get_general_ai_feedback(
                            st.session_state.resume_text
                        )
                    )

                    st.session_state.analysis_done = True

                if st.session_state.analysis_done:
                    st.success("Analysis Complete 🎉")

        else:
            st.warning("⚠️ Please upload a resume.")

    # =========================
    # SHOW RESULTS
    # =========================

    if st.session_state.analysis_done:

        results = st.session_state.analysis_results

        score_value = results.get("score", 0)

        feedback_text = results.get("feedback", "")

        st.markdown("---")

        # =========================
        # METRIC CARDS
        # =========================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>ATS Score</h3>
                <h1>{score_value}%</h1>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Matched Skills</h3>
                <h1>{len(results.get('matched_skills', []))}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Missing Skills</h3>
                <h1>{len(results.get('missing_skills', []))}</h1>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # =========================
        # GAUGE CHART
        # =========================

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_value,

            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#7C4DFF"},

                'steps': [
                    {'range': [0, 50], 'color': "#EF4444"},
                    {'range': [50, 75], 'color': "#F59E0B"},
                    {'range': [75, 100], 'color': "#10B981"},
                ],
            }
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={
                'color': "#F8FAFC",
                'family': "Poppins"
            },
            height=320
        )

        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # FEEDBACK SECTION
        # =========================

        st.subheader("💡 AI Feedback")

        with st.container(border=True):
            st.markdown(feedback_text)

        # =========================
        # SKILL ANALYSIS
        # =========================

        if review_mode:

            st.write("")

            st.subheader("🛠 Skill Analysis")

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### ✅ Matched Skills")

                matched_skills = results.get("matched_skills", [])

                if matched_skills:
                    for skill in matched_skills:
                        st.success(skill)
                else:
                    st.info("No matched skills found.")

            with col2:

                st.markdown("### ❌ Missing Skills")

                missing_skills = results.get("missing_skills", [])

                if missing_skills:
                    for skill in missing_skills:
                        st.error(skill)
                else:
                    st.success("No missing skills 🎉")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SUGGESTIONS SECTION
# ============================================================

if selected == "Suggestions":

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.header("🧠 AI Career Coach")

    st.write(
        "Get intelligent resume improvement suggestions powered by AI."
    )

    if not st.session_state.analysis_done:

        st.info(
            "💡 Please analyze a resume first in the ATS Review section."
        )

    else:

        with st.spinner("AI Coach is reviewing your resume..."):

            missing_skills = st.session_state.analysis_results.get(
                "missing_skills",
                []
            )

            suggestions = get_ai_suggestions(
                st.session_state.resume_text,
                st.session_state.job_description,
                missing_skills
            )

            st.markdown(suggestions)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("""
<hr>

<center>
Built with ❤️ using AI • Resume Forge © 2026
</center>
""", unsafe_allow_html=True)    