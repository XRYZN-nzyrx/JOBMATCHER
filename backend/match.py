from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from backend.utils import extract_text_from_file, analyze_profile_with_gemini  # Fixed import
import os
from werkzeug.utils import secure_filename

router = APIRouter()
UPLOAD_DIR = "uploads"

# Ensure upload folder exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/match-jobs")
async def analyze_profile(
    skills: str = Form(""),
    desired_jobs: str = Form(""),
    file: UploadFile = File(None)
):
    text_data = skills.strip()
    file_used = False

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        extracted = extract_text_from_file(file_path)
        os.remove(file_path)
        if extracted.strip():
            text_data += "\n" + extracted
            file_used = True

    if desired_jobs.strip():
        text_data += f"\nDesired Jobs: {desired_jobs.strip()}"

    if not text_data.strip():
        return JSONResponse(content={"error": "No valid input provided."}, status_code=400)

    result = analyze_profile_with_gemini(text_data)

    
    if result and isinstance(result, dict) and "error" not in result:
        result["used_cv"] = file_used
        return JSONResponse(content=result)
    else:
        return JSONResponse(
            content={"error": "Failed to process profile", "details": result},
            status_code=500
        )