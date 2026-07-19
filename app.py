import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import PyPDF2

load_dotenv() 

st.set_page_config(page_title="AI Candidate Evaluator", layout="wide")

st.title("📄 AI Candidate Evaluator")
st.caption("Fulfills Assignment 1 & 2 using Google Gemini (Free Tier).")


col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 Input Data")
    
    input_method = st.radio("Choose Resume Input Method:", ["Paste Text", "Upload File (.pdf, .txt)"])
    
    resume_text = ""
    if input_method == "Paste Text":
        resume_text = st.text_area("Paste Full Candidate Resume Here", height=200, placeholder="Paste entire resume text...")
    else:
        uploaded_file = st.file_uploader("Upload Resume File", type=["pdf", "txt"])
        if uploaded_file is not None:
            # Handle PDF extraction
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    extracted_page = page.extract_text()
                    if extracted_page:
                        resume_text += extracted_page + "\n"
            # Handle TXT extraction
            else:
                resume_text = uploaded_file.read().decode("utf-8")
            st.success("Resume loaded successfully from file!")

    st.markdown("---")
    jd_text = st.text_area("Paste Job Description (JD) Here", height=200, placeholder="Paste entire Job Description text...")
    
    evaluate_button = st.button("Evaluate Candidate", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Evaluation Results")
    
    if evaluate_button:
        if not resume_text.strip() or not jd_text.strip():
            st.warning("Please provide both the Resume and the Job Description.")
        else:
            with st.spinner("AI is extracting skills and calculating fit..."):
                try:
                    # Configure Gemini API
                    genai.configure(api_key = os.getenv("GEM_API_KEY"))
                    
                    # Force the model to return a JSON object
                    model = genai.GenerativeModel(
                        "gemini-2.5-flash",
                        generation_config={"response_mime_type": "application/json"}
                    )
                    
                    prompt = f"""
                    You are an expert HR Technical Recruiter. Extract skills from the Resume and Job Description.
                    Return EXACTLY a JSON object with the following structure and no other text:
                    {{
                        "matched_skills": ["Skill 1", "Skill 2"],
                        "missing_skills": ["Skill 3", "Skill 4"],
                        "match_percentage": 75,
                        "verdict": "Almost There", 
                        "reasons": ["Reason 1", "Reason 2", "Reason 3"]
                    }}
                    
                    Rules:
                    - 'verdict' MUST be exactly one of: 'Qualified', 'Almost There', or 'Not Yet'.
                    - 'match_percentage' MUST be an integer between 0 and 100.
                    - 'reasons' MUST contain exactly 3 strings.

                    Candidate Resume:
                    {resume_text}

                    Job Description:
                    {jd_text}
                    """

                    response = model.generate_content(prompt)
                    result = json.loads(response.text)
                    
                    # --- Render Assignment 2 ---
                    verdict = result.get("verdict", "Not Yet")
                    if verdict == "Qualified": st.success(f"### Verdict: {verdict}")
                    elif verdict == "Almost There": st.warning(f"### Verdict: {verdict}")
                    else: st.error(f"### Verdict: {verdict}")
                    
                    for reason in result.get("reasons", []):
                        st.markdown(f"- {reason}")
                        
                    st.markdown("---")
                    
                    # --- Render Assignment 1 ---
                    match_percentage = result.get("match_percentage", 0)
                    st.markdown(f"### Match Percentage: **{match_percentage}%**")
                    st.progress(match_percentage / 100)
                    
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.markdown("**Extracted Matched Skills**")
                        for skill in result.get("matched_skills", []): st.markdown(f"🍏 `{skill}`")
                    with m_col2:
                        st.markdown("**Extracted Missing Skills**")
                        for skill in result.get("missing_skills", []): st.markdown(f"🍎 `{skill}`")

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Provide inputs on the left and click 'Evaluate Candidate'.")