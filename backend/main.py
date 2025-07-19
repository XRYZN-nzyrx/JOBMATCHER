from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
load_dotenv()


from backend.match import router as match_router

app = FastAPI()
origins = [
    "https://jobmatcher-k9uh.onrender.com",
    "http://localhost:3000",  # Optional for dev
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match_router)

# Updated paths to match your actual folder structure
app.mount("/static", StaticFiles(directory="jobmatcher-frontend/build/static"), name="static")

@app.get("/")
def serve_react():
    return FileResponse("jobmatcher-frontend/build/index.html")

# Catch-all route to serve React app for client-side routing
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    # Don't serve React for API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        return {"error": "Not found"}
    return FileResponse("jobmatcher-frontend/build/index.html")