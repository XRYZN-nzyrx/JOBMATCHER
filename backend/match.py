from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from backend.utils import extract_text_from_file, analyze_profile_with_gemini
import os
from werkzeug.utils import secure_filename

router = APIRouter()
UPLOAD_DIR = "uploads"

# Ensure upload folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/match-jobs")
async def analyze_profile(
    skills: str = Form(""),
    desired_jobs: str = Form(""),
    file: UploadFile = File(None)
):
    extracted = ""
    file_used = False

    # Handle file upload and extraction
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(await file.read())

            extracted = extract_text_from_file(file_path)

        finally:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Warning: Could not delete uploaded file: {e}")

        if extracted.strip():
            file_used = True

    # Validate input before proceeding
    if not skills.strip() and not extracted.strip() and not desired_jobs.strip():
        return JSONResponse(content={"error": "No valid input provided."}, status_code=400)

    # Analyze profile with structured input
    print("🚀 Gemini input:", skills.strip(), desired_jobs.strip(), extracted.strip())
    result = analyze_profile_with_gemini(
        skills.strip(),
        desired_jobs.strip(),
        extracted.strip()
    )

    # Return result or error
    if result and isinstance(result, dict) and "error" not in result:
        result["used_cv"] = file_used
        return JSONResponse(content=result)
    else:
        return JSONResponse(
            content={
                "error": "Failed to process profile.",
                "details": result if isinstance(result, dict) else {"raw": str(result)}
            },
            status_code=500
        )