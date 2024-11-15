import os
import yt_dlp # type: ignore
import uvicorn # type: ignore
from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import StreamingResponse # type: ignore
from pydantic import BaseModel, HttpUrl # type: ignore
from typing import Optional
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class VideoURL(BaseModel):
    url: HttpUrl
    format: Optional[str] = None  # User-selected format_id
    audio_only: Optional[bool] = False  # New flag to indicate audio-only download

def clean_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()

def get_video_info(url: str):
    """Get video information using yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'outtmpl': '%(title)s.%(ext)s',  # Use this to get the full format list
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

def download_video(format_id, url):
    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.post("/api/video-info")
async def get_info(video: VideoURL):
    """Get video information without downloading"""
    info = get_video_info(str(video.url))

    formats = []
    for f in info.get("formats", []):
        formats.append({
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution", "audio only"),
            "filesize": f.get("filesize"),
            "format_note": f.get("format_note", ""),
            "acodec": f.get("acodec"),
            "vcodec": f.get("vcodec")
        })

    # Helper function to extract sorting key
    def resolution_key(resolution: str) -> int:
        if resolution == "audio only":
            return 0
        if 'p' in resolution:
            try:
                return int(resolution.rstrip('p'))
            except ValueError:
                return 0
        if 'x' in resolution:
            try :
                width_height = resolution.split('x')
                return int(width_height[1])  # Use the height value
            except (IndexError, ValueError):
                return 0
        return 0

    # Sort formats by quality
    formats.sort(key=lambda x: resolution_key(x["resolution"]), reverse=True)

    return {
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "formats": formats
    }

@app.post("/api/download")
async def download_video_endpoint(video: VideoURL):
    """Download video and stream it to the client"""
    try:
        info = get_video_info(str(video.url))
        title = clean_filename(info['title'])

        if video.audio_only:
            # For audio-only download
            ydl_opts = {
                'format': 'bestaudio/best',  # Download best available audio
                'outtmpl': str(DOWNLOAD_DIR / f'{title}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',  # Change to desired format
                    'preferredquality': '192',
                }],
            }
        else:
            # Normal video download
            selected_format = next(
                (f for f in info['formats'] if f['format_id'] == video.format), None)

            if not selected_format:
                raise HTTPException(status_code=400, detail="Invalid format selected")

            if selected_format.get('acodec') == 'none':
                format_selector = f"{video.format}+bestaudio/best"
            else:
                format_selector = video.format

            ydl_opts = {
                'format': format_selector,
                'outtmpl': str(DOWNLOAD_DIR / f'{title}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

        # Download the video/audio
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

        # Determine content type based on extension
        extension = downloaded_file.suffix.lower()
        if extension in ['.mp3', '.m4a', '.aac', '.wav', '.ogg']:
            content_type = f'audio/{extension.lstrip(".")}'
        else:
            content_type = 'video/mp4'

        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{downloaded_file.name}"'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)