import streamlit as st
import asyncio
import os
import sys

# Make sure we can import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from resume.resume_generator import generate_resume  # your async function

st.set_page_config(page_title="SnapSkill - Resume Builder", layout="wide")
st.markdown("""
    <style>
    /* SnapSkill Light Theme - Final Fix */

    html, body, .main, .block-container {
        background: linear-gradient(135deg, #f0f8ff, #e0f7fa);
        color: #2c2c2c;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Inputs */
    textarea, input, select {
        background-color: white !important;
        color: #2c2c2c !important;
        border: 1px solid #d0e8f2 !important;
        border-radius: 8px !important;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(to right, #1e90ff, #00b894);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-size: 16px;
        transition: background 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(to right, #0f78d1, #009b7d);
    }

    .stDownloadButton > button {
        background-color: #1e90ff !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f8ff !important;
    }

    /* Header (remove dark strip) */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    header[data-testid="stHeader"]::before {
        content: none;
    }

    /* Footer */
    footer {
        background: transparent;
        color: transparent;
    }
    footer:after {
        content: "";
        display: block;
        height: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 🚀 UI
st.title("📄 Build Your Resume with SnapSkill")
st.markdown("Generate your resume in minutes using AI. Just share your experience and choose a template!")




# 🔤 Prompt input
prompt = st.text_area("🧠 Enter your experience, job goals, or paste an old resume:", height=200)

# 🎨 Template selection
templates = ["modern.html", "professional.html", "minimalist.html", "classic.html", "creative.html", "bluish.html"]
st.markdown("### 🎨 Choose Your Template")
template_choice = st.selectbox("Choose a template", templates, label_visibility="collapsed")


# 🚀 Generate Resume Button
if st.button("Generate Resume"):
    if not prompt.strip():
        st.error("⚠️ Please enter a prompt to generate your resume.")
    else:
        with st.spinner("Generating your resume..."):
            try:
                # Async call to backend logic
                pdf_path = asyncio.run(generate_resume(prompt, template_choice))
                st.success("✅ Your resume is ready!")

                # 🧾 PDF download
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name="SnapSkill_Resume.pdf")
            except Exception as e:
                st.error(f"❌ Error: {e}")

