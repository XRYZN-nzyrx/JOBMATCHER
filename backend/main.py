from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.match import router as match_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match_router)

# Serve React build
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/")
def serve_react():
    return FileResponse("frontend/build/index.html")
