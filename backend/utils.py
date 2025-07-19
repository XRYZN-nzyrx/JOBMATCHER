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

if not GOOGLE_GENAI_API_KEY:
    raise EnvironmentError(" GOOGLE_API_KEY is not set in environment variables.")

# Configure Gemini
genai.configure(api_key=GOOGLE_GENAI_API_KEY)

def extract_text_from_file(path):
    ext = os.path.splitext(path)[1].lower()
    try:
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
    except Exception as e:
        return f" Error while extracting text from {ext} file: {str(e)}"

def analyze_profile_with_gemini(profile_text):
    prompt = f"""
You are an expert career analyst and job readiness evaluator. As per the latest trends in 2025 and beyond, analyze the following user profile to identify skills, gaps, and career recommendations.

\"\"\"{profile_text}\"\"\"

Return a valid JSON object with the following fields:
1. "current_skills"
2. "missing_skills"
3. "recommended_certifications"
4. "effort_level"
5. "summary_advice"
6. "job_roles_you_can_apply_for"
7. "job_roles_you_desire"
8. "percentage_match"
9. "cv_strong_points"
10. "cv_weak_points"
11. "cv_improvement_suggestions"
12. "market_trend_advice"
13. "recommended_courses" (format: [{{"missing_skill": ..., "courses": [...]}}])
Return only JSON. No markdown, no explanation, no example.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw_response = response.text.strip()

        # Sanitize any unwanted formatting (e.g., ```json ... ```)
        cleaned = re.sub(r"^```json|```$", "", raw_response, flags=re.IGNORECASE).strip()

        parsed = json.loads(cleaned)

        # Fallback-safe JSON response
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
            "error": " Gemini returned invalid JSON format.",
            "raw_response": raw_response
        }

    except Exception as e:
        return {"error": f" Gemini processing error: {str(e)}"}
