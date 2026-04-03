import hashlib
from pathlib import Path

import yt_dlp

VIDEOS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "videos"


def _video_id_from_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def download_video(url: str) -> dict:
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    video_id = _video_id_from_url(url)
    output_path = VIDEOS_DIR / f"{video_id}.%(ext)s"

    ydl_opts = {
        "format": "mp4[height<=720]/best[height<=720]/mp4/best",
        "outtmpl": str(output_path),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Find the actual downloaded file
    downloaded = list(VIDEOS_DIR.glob(f"{video_id}.*"))
    assert downloaded, f"Download failed: no file found for {video_id}"
    filepath = str(downloaded[0])

    return {
        "video_id": video_id,
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration"),
        "thumbnail_url": info.get("thumbnail"),
        "filepath": filepath,
        "url": url,
    }
