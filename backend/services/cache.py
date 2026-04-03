import json
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
VIDEOS_FILE = CACHE_DIR / "videos.json"
CHAPTERS_DIR = CACHE_DIR / "chapters"


def _ensure_dirs():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)


def _load_videos_db() -> dict:
    _ensure_dirs()
    if VIDEOS_FILE.exists():
        return json.loads(VIDEOS_FILE.read_text(encoding="utf-8"))
    return {}


def _save_videos_db(db: dict):
    _ensure_dirs()
    VIDEOS_FILE.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")


def save_video_meta(video_id: str, meta: dict):
    db = _load_videos_db()
    db[video_id] = meta
    _save_videos_db(db)


def load_video_meta(video_id: str) -> dict | None:
    db = _load_videos_db()
    return db.get(video_id)


def list_videos() -> list[dict]:
    db = _load_videos_db()
    return list(db.values())


def save_chapters(video_id: str, chapters: list[dict]):
    _ensure_dirs()
    path = CHAPTERS_DIR / f"{video_id}.json"
    path.write_text(json.dumps(chapters, indent=2, ensure_ascii=False), encoding="utf-8")


def load_chapters(video_id: str) -> list[dict] | None:
    _ensure_dirs()
    path = CHAPTERS_DIR / f"{video_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None
