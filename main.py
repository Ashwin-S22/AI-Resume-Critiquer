import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from openai._exceptions import RateLimitError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Page configuration
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")

st.title("📃 AI Resume Critiquer")
st.markdown("Upload your resume and get **AI-powered feedback** tailored to your career goals!")

# Load API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# File uploader and input
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")

analyze = st.button("🔍 Analyze Resume")

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# Extract text based on file type
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

# Handle resume analysis
if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("The uploaded file does not contain any readable content.")
            st.stop()

        # Prepare prompt
        prompt = f"""Please analyze this resume and provide constructive feedback. 
Focus on the following aspects:
1. Content clarity and impact
2. Skills presentation
3. Experience descriptions
4. Specific improvements for {job_role if job_role else 'general job applications'}

Resume content:
{file_content}

Please provide your analysis in a clear, structured format with specific recommendations."""

        # OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume reviewer with years of experience in HR and recruitment."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Output analysis
        st.markdown("### 📊 Analysis Results")
        st.markdown(response.choices[0].message.content)

    except RateLimitError:
        st.error("🚫 You have exceeded your OpenAI API quota. Please check your usage or billing details.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")