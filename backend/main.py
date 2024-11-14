from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
import yt_dlp
import os
from typing import Optional
import asyncio
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class VideoURL(BaseModel):
    url: HttpUrl
    format: Optional[str] = "best"  # best, audio, 720p, etc.

def clean_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()

def get_video_info(url: str):
    """Get video information using yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/video-info")
async def get_info(video: VideoURL):
    """Get video information without downloading"""
    info = get_video_info(str(video.url))
    return {
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "formats": [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution"),
                "filesize": f.get("filesize"),
                "format_note": f.get("format_note")
            }
            for f in info.get("formats", [])
            if f.get("ext") in ["mp4", "webm", "m4a"]  # Filter common formats
        ]
    }

@app.post("/api/download")
async def download_video(video: VideoURL):
    """Download video and stream it to the client"""
    try:
        info = get_video_info(str(video.url))
        title = clean_filename(info['title'])

        # Configure yt-dlp options
        ydl_opts = {
            'format': video.format,
            'outtmpl': str(DOWNLOAD_DIR / f'{title}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        # Add format-specific options
        if video.format == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([str(video.url)])
            if error_code != 0:
                raise HTTPException(status_code=500, detail="Download failed")

        # Find the downloaded file
        downloaded_file = next(DOWNLOAD_DIR.glob(f'{title}.*'))

        # Stream the file
        def iterfile():
            with open(downloaded_file, 'rb') as f:
                yield from f
            # Clean up after streaming
            os.remove(downloaded_file)

        # Determine content type
        content_type = 'audio/mpeg' if video.format == "audio" else 'video/mp4'

        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{downloaded_file.name}"'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cleanup endpoint to remove old downloads
@app.post("/api/cleanup")
async def cleanup_downloads():
    """Remove all files in the downloads directory"""
    try:
        for file in DOWNLOAD_DIR.glob("*"):
            file.unlink()
        return {"message": "Cleanup successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)