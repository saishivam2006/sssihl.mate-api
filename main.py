
import os
from urllib.parse import urlparse, parse_qs

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="Downly API")

# Set FRONTEND_ORIGIN on Render to your actual published
# Lovable website URL. Comma-separated origins are supported.
origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class MetadataRequest(BaseModel):
    url: HttpUrl


@app.get("/")
def root():
    return {"message": "Downly API is running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/metadata")
def metadata(request: MetadataRequest):
    parsed = urlparse(str(request.url))
    host = (parsed.hostname or "").lower()

    if host not in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtube-nocookie.com",
    }:
        raise HTTPException(
            status_code=400,
            detail="Enter a supported YouTube URL."
        )

    video_id = None

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [None])[0]
    elif parsed.path.startswith("/shorts/"):
        parts = parsed.path.split("/")
        if len(parts) > 2:
            video_id = parts[2]

    if not video_id or not all(
        c.isalnum() or c in "_-" for c in video_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Could not identify the video."
        )

    return {
        "status": "ok",
        "video_id": video_id,
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "message": "URL validated. Metadata provider not connected yet."
    }
