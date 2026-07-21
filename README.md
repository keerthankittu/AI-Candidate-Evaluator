# AI Candidate Evaluator (Assignment 1 & 2)

A fast, single-file Streamlit application that automates technical candidate profile parsing, skill gap analysis, and qualification verdicts using Google Gemini's NLP capabilities.

## Features
- **Assignment 1 (Skill Gap Checker):** Extracts matching and missing technical skills dynamically and computes a clean percentage match score.
- **Assignment 2 (Fit Verdict):** Evaluates overall candidate alignment into standard HR tiers (`Qualified`, `Almost There`, `Not Yet`) alongside exactly three sharp, actionable supporting reasons.
- **Native PDF Parsing:** Uses `PyPDF2` to read unstructured data straight from resume uploads, mimicking standard Applicant Tracking System (ATS) intake pipelines.
- **Bonus Feature (YouTube Resource Scraper):** Dynamically generates direct links to top YouTube crash courses for any missing skills. It utilizes Python's `urllib` and Regex to scrape real video IDs, completely bypassing LLM hallucination risks without needing an extra API key.
- **Custom UI/UX:** Features a polished, modern violet gradient theme built with custom CSS injection for an enterprise feel.
- **Unified Query Architecture:** Executes both assignments within a single, optimized prompt context window to cut latency in half and lower API token overhead.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your system. 

### 2. Install Dependencies
Open your terminal in the project directory and install the required modules:

pip install streamlit google-generativeai PyPDF2

### 3. Run the Application
Launch the web interface locally by running:
streamlit run app.py
Note: If Windows does not recognize the command due to user path restrictions, use:
python -m streamlit run app.py

### 4. Usage
Open the local address in your browser (defaults to http://localhost:8501).

Generate a free API Key from Google AI Studio (aistudio.google.com) and paste it into the sidebar configuration.

Upload a candidate resume (.pdf or .txt) or paste the raw text.

Input the Target Job Description text.

Click Evaluate Candidate to view the live, processed results.

## Architectural Assumptions & Trade-offs
1. Framework Selection (Streamlit vs. Full-Stack Boilerplate)
Decision: Built using Streamlit rather than a split React frontend / FastAPI backend.

Trade-off: While a separate full-stack architecture offers granular UI customization, it introduces high state management and deployment overhead. Streamlit allowed a 100% focus on robust prompt engineering, structured parsing, and error safety under a tight deadline, producing an easily testable MVP for code review.

2. LLM Engine Pivot & Single-Call Architecture
Decision: Both assignments are parsed in a single text context window using gemini-2.5-flash.

Trade-off: By combining the prompt to return a strict, unified JSON schema, latency and token costs are cut in half, guaranteeing consistency between the skill-gap details and the overarching fit verdict.

3. YouTube Scraper vs. LLM Generation
Decision: Used native Python HTTP requests (urllib) and Regex to fetch YouTube links.

Trade-off: LLMs are notorious for hallucinating broken URLs. By programmatically scraping YouTube's search results for exact video IDs, the application guarantees 100% accurate, working links without adding the overhead of the official YouTube Data API.
Trade-off: This method easily handles text-based digital PDFs (standard resume format). Complex images or scanned document types require heavier OCR pipelines (like Tesseract), which were intentionally out-of-scope to keep the local installation dependencies incredibly clean and lightweight.
