import streamlit as st
import google.generativeai as genai
import json
import PyPDF2
import urllib.request
import urllib.parse
import re

# Set Streamlit page configuration
st.set_page_config(
    page_title="AI Candidate Evaluator", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INJECT CUSTOM VIOLET THEME STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #130821 0%, #261042 45%, #3d1a68 100%);
        color: #f3e8ff;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .header-banner {
        background-color: #6b21a8;
        padding: 1.8rem 2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.35);
        margin-bottom: 2rem;
        border: 1px solid rgba(216, 180, 254, 0.2);
    }
    .header-title {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .header-subtitle {
        color: #e9d5ff;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        font-weight: 400;
    }
    h2, h3 { color: #f3e8ff !important; font-weight: 600 !important; }
    .stTextArea textarea {
        background-color: rgba(19, 8, 33, 0.6) !important;
        color: #f3e8ff !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #7e22ce 0%, #9333ea 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
    }
    .skill-badge-matched {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(74, 222, 128, 0.3);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    .skill-badge-missing {
        display: inline-block;
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.3);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    hr { border-color: rgba(168, 85, 247, 0.2) !important; }
    </style>
""", unsafe_allow_html=True)

# Fetch API Key securely from Streamlit Cloud Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Authentication Error: GEMINI_API_KEY is missing from Streamlit Secrets. Please check your app settings.")
    st.stop()

# --- HEADER BANNER ---
st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">AI Candidate Evaluator</h1>
        <p class="header-subtitle">Automated Skill Gap Analysis & Qualification Assessment</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Input Data")
    
    input_method = st.radio("Choose Resume Input Method:", ["Paste Text", "Upload File (.pdf, .txt)"])
    
    resume_text = ""
    if input_method == "Paste Text":
        resume_text = st.text_area("Candidate Resume", height=200, placeholder="Paste complete resume text here...")
    else:
        uploaded_file = st.file_uploader("Upload Candidate Resume", type=["pdf", "txt"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    extracted_page = page.extract_text()
                    if extracted_page:
                        resume_text += extracted_page + "\n"
            else:
                resume_text = uploaded_file.read().decode("utf-8")
            st.success("Resume text extracted successfully.")

    st.markdown("---")
    jd_text = st.text_area("Job Description (JD)", height=200, placeholder="Paste target Job Description text here...")
    
    evaluate_button = st.button("Evaluate Candidate", use_container_width=True)

with col2:
    st.subheader("Evaluation Results")
    
    if evaluate_button:
        if not resume_text.strip() or not jd_text.strip():
            st.warning("Please provide both the Resume and the Job Description.")
        else:
            with st.spinner("Analyzing profile alignment and extracting skills..."):
                try:
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
                    
                    # --- Assignment 2: Verdict & Reasoning ---
                    verdict = result.get("verdict", "Not Yet")
                    if verdict == "Qualified": st.success(f"Verdict: {verdict}")
                    elif verdict == "Almost There": st.warning(f"Verdict: {verdict}")
                    else: st.error(f"Verdict: {verdict}")
                    
                    st.markdown("**Assessment Breakdown:**")
                    for reason in result.get("reasons", []):
                        st.markdown(f"• {reason}")
                        
                    st.markdown("---")
                    
                    # --- Assignment 1: Skill Gap Breakdown ---
                    match_percentage = result.get("match_percentage", 0)
                    st.markdown(f"### Skill Match: **{match_percentage}%**")
                    st.progress(match_percentage / 100)
                    
                    m_col1, m_col2 = st.columns(2)
                    
                    with m_col1:
                        st.markdown("**Matched Skills**")
                        matched_skills = result.get("matched_skills", [])
                        if matched_skills:
                            html_badges = "".join([f'<span class="skill-badge-matched">{s}</span>' for s in matched_skills])
                            st.markdown(html_badges, unsafe_allow_html=True)
                        else:
                            st.write("None identified")
                            
                    with m_col2:
                        st.markdown("**Missing Skills**")
                        missing_skills = result.get("missing_skills", [])
                        if missing_skills:
                            html_badges = "".join([f'<span class="skill-badge-missing">{s}</span>' for s in missing_skills])
                            st.markdown(html_badges, unsafe_allow_html=True)
                            
                            # --- BONUS FEATURE: YouTube Direct Link Generator ---
                            with st.expander("View Learning Resources"):
                                st.markdown("Bridge your skill gap with these top tutorials:")
                                for skill in missing_skills:
                                    try:
                                        # Programmatically search YouTube and scrape the first video ID
                                        query = urllib.parse.urlencode({"search_query": f"learn {skill} crash course"})
                                        html = urllib.request.urlopen(f"https://www.youtube.com/results?{query}").read().decode()
                                        video_ids = re.findall(r'"videoId":"(.{11})"', html)
                                        
                                        if video_ids:
                                            direct_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                                            st.markdown(f"- [📺 **{skill}** - Top Crash Course]({direct_url})")
                                        else:
                                            # Fallback if scraping fails
                                            search_url = f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}+tutorial"
                                            st.markdown(f"- [📺 Learn **{skill}**]({search_url})")
                                    except Exception:
                                        search_url = f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}+tutorial"
                                        st.markdown(f"- [📺 Learn **{skill}**]({search_url})")
                        else:
                            st.write("None identified")
                        
                except Exception as e:
                    st.error(f"An error occurred during evaluation: {str(e)}")
    else:
        st.info("Input profile data on the left panel and click 'Evaluate Candidate' to view analytics.")
