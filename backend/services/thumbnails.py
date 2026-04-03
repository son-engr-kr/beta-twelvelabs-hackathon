"""Capture video frames at specific timestamps for chapter thumbnails."""

import logging
import subprocess
from pathlib import Path

import yt_dlp

logger = logging.getLogger(__name__)

THUMB_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cache" / "thumbnails"


def _ensure_dir():
    THUMB_DIR.mkdir(parents=True, exist_ok=True)


def thumb_path(video_id: str, chapter_idx: int) -> Path:
    return THUMB_DIR / f"{video_id}_{chapter_idx}.jpg"


def thumb_exists(video_id: str, chapter_idx: int) -> bool:
    return thumb_path(video_id, chapter_idx).exists()


def get_stream_url(youtube_url: str) -> str | None:
    """Get direct video stream URL from YouTube (no download)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "mp4[height<=480]/best[height<=480]",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info.get("url")


def capture_frame(stream_url: str, timestamp: float, output_path: Path) -> bool:
    """Capture a single frame from a video stream at the given timestamp."""
    cmd = [
        "ffmpeg",
        "-ss", str(timestamp),
        "-i", stream_url,
        "-vframes", "1",
        "-q:v", "5",
        "-y",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=30)
    return result.returncode == 0 and output_path.exists()


def generate_chapter_thumbnails(video_id: str, youtube_url: str, chapters: list[dict]):
    """Generate thumbnails for all chapters of a video. Cached — safe to call repeatedly."""
    _ensure_dir()

    # Check which chapters need thumbnails
    needed = [(i, ch) for i, ch in enumerate(chapters) if not thumb_exists(video_id, i)]
    if not needed:
        return

    logger.info(f"Generating {len(needed)} thumbnails for {video_id}...")

    # Get stream URL once for all chapters
    stream_url = get_stream_url(youtube_url)
    if not stream_url:
        logger.warning(f"Could not get stream URL for {video_id}")
        return

    for i, ch in needed:
        # Capture at 2 seconds into the chapter for a more representative frame
        timestamp = ch["start"] + 2
        out = thumb_path(video_id, i)
        ok = capture_frame(stream_url, timestamp, out)
        if ok:
            logger.info(f"  Thumbnail {video_id}_ch{i} at {timestamp:.0f}s")
        else:
            logger.warning(f"  Failed thumbnail {video_id}_ch{i}")


def generate_all_missing():
    """Generate thumbnails for all cached videos that have chapters. Safe to call on startup."""
    from backend.services import cache

    for video in cache.list_videos():
        vid = video["video_id"]
        url = video.get("url")
        if not url:
            continue
        chapters = cache.load_chapters(vid)
        if not chapters:
            continue
        # generate_chapter_thumbnails already skips existing
        try:
            generate_chapter_thumbnails(vid, url, chapters)
        except Exception as e:
            logger.warning(f"Thumbnail generation failed for {vid}: {e}")
