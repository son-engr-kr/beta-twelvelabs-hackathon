import hashlib

import yt_dlp


def _video_id_from_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def extract_metadata(url: str) -> dict:
    """Extract video metadata without downloading."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    video_id = _video_id_from_url(url)

    return {
        "video_id": video_id,
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration"),
        "thumbnail_url": info.get("thumbnail"),
        "url": url,
    }
