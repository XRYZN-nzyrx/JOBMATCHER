import os
import json
import pytesseract
from PIL import Image
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document
from dotenv import load_dotenv
import google.generativeai as genai
import re

# Load environment variables
load_dotenv()
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
print("🧪 [DEBUG] GOOGLE_API_KEY:", GOOGLE_GENAI_API_KEY)

if not GOOGLE_GENAI_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY is not set in environment variables.")
# Configure Gemini
genai.configure(api_key=GOOGLE_GENAI_API_KEY)

def extract_text_from_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    elif ext == ".docx":
        return " ".join(p.text for p in Document(path).paragraphs)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return pytesseract.image_to_string(Image.open(path))
    elif ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return ""

def analyze_profile_with_gemini(profile_text):
    prompt = f"""
You are an expert career analyst and job readiness evaluator.As per the latest trends in 2025 and also the trends that's gonna be in future, analyze the following user profile text to identify skills, gaps, and recommendations for career advancement.Do whatever search you need to do to get the latest trends in 2025 and also the trends that's gonna be in future, and then analyze the profile text.

The following content includes the user's resume or skill set and optionally their desired job roles.

\"\"\"{profile_text}\"\"\"

Analyze the text and return a JSON object with the following fields:

1. "current_skills": list of clearly identified technical or soft skills.
2. "missing_skills": list of skills the user lacks but are important for current market demands in 2025 or for future,or their desired roles.Missing skills should be relevant to the user's current skillset and desired job roles.
3. "recommended_certifications": list of certifications (with name and provider) that would boost the user's profile.
4. "effort_level": categorize effort to become job-ready as one of ["Beginner", "Intermediate", "Advanced"].
5. "summary_advice": short career advice (2-3 sentences).
6. "job_roles_you_can_apply_for": list of roles matched based on the current skills.
7. "job_roles_you_desire": extract roles the user aspires to from their input.
8. "percentage_match": match percentage between user’s current skillset and their desired roles.The intersection of current skills and desired roles should be considered for this percentage, and the formula should be Interserction of Current Skills and Desired Roles / Total Desired Roles * 100.
9. "cv_strong_points": list of strong or well-represented areas in the resume or skills.
10. "cv_weak_points": list of weak areas in the resume or missing structure/content.
11. "cv_improvement_suggestions": suggestions to improve the CV/resume.
12. "market_trend_advice": insights about current job market trends that relate to user's field.
13. "recommended_courses": (list) Each item should be a dictionary with two keys:
    - "missing_skill": string
    - "courses": list of 1-2 course names (include platform in format "Course – Platform")

Example:
[
  {{
    "missing_skill": "Cloud Computing",
    "courses": ["AWS Cloud Practitioner – Coursera", "Azure Fundamentals – edX"]
  }},
  {{
    "missing_skill": "Git",
    "courses": ["Git for Beginners – LinkedIn Learning", "Version Control with Git – Coursera"]
  }}
]

Return only a valid JSON object (no markdown, no notes, no explanation, no triple backticks).
Please note that example is just for reference, do not include it in the response,if not applicable.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw_response = response.text.strip()

        # Remove potential formatting
        cleaned = re.sub(r"^```json|```$", "", raw_response, flags=re.IGNORECASE).strip()

        parsed = json.loads(cleaned)

        # Fill any missing fields with default safe values
        default_result = {
            "current_skills": [],
            "missing_skills": [],
            "recommended_certifications": [],
            "effort_level": "Not specified",
            "summary_advice": "No advice provided.",
            "job_roles_you_can_apply_for": [],
            "job_roles_you_desire": [],
            "percentage_match": 0,
            "cv_strong_points": [],
            "cv_weak_points": [],
            "cv_improvement_suggestions": [],
            "market_trend_advice": "No advice available.",
            "recommended_courses": []
        }

        final_result = {key: parsed.get(key, default) for key, default in default_result.items()}
        return final_result

    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON format returned by Gemini. Please retry.",
            "raw_response": response.text
        }

    except Exception as e:
        return {"error": f"Error from Gemini: {str(e)}"}
