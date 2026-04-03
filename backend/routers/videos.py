import threading

from fastapi import APIRouter
from fastapi.responses import FileResponse

from backend.models import IngestRequest, VideoMeta, Chapter
from backend.services import cache, video_service, twelvelabs_service, thumbnails

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/ingest")
def ingest_video(req: IngestRequest) -> VideoMeta:
    # Extract metadata (no download)
    meta = video_service.extract_metadata(req.url)

    # Create/get Twelve Labs index
    index_id = twelvelabs_service.get_or_create_index()
    meta["tl_index_id"] = index_id

    # Index video by URL (no file upload)
    tl_video_id = twelvelabs_service.index_video(index_id, req.url)
    meta["tl_video_id"] = tl_video_id

    # Cache metadata
    cache.save_video_meta(meta["video_id"], meta)

    return VideoMeta(**meta)


@router.get("")
def list_videos() -> list[VideoMeta]:
    videos = cache.list_videos()
    return [VideoMeta(**v) for v in videos]


@router.get("/{video_id}")
def get_video(video_id: str) -> VideoMeta:
    meta = cache.load_video_meta(video_id)
    assert meta is not None, f"Video not found: {video_id}"
    return VideoMeta(**meta)


@router.get("/{video_id}/chapters")
def get_chapters(video_id: str) -> list[Chapter]:
    meta = cache.load_video_meta(video_id)
    assert meta is not None, f"Video not found: {video_id}"

    # Check cache first
    cached = cache.load_chapters(video_id)
    if cached is not None:
        # Ensure thumbnails exist in background
        _ensure_thumbnails(video_id, meta, cached)
        return [Chapter(**c) for c in cached]

    # Need Twelve Labs to generate chapters
    tl_video_id = meta.get("tl_video_id", "")
    assert tl_video_id and not tl_video_id.startswith("gemini_"), \
        f"Video not indexed with Twelve Labs: {video_id}"

    chapters = twelvelabs_service.generate_chapters(tl_video_id)
    cache.save_chapters(video_id, chapters)
    _ensure_thumbnails(video_id, meta, chapters)

    return [Chapter(**c) for c in chapters]


def _ensure_thumbnails(video_id: str, meta: dict, chapters: list[dict]):
    """Trigger background thumbnail generation if any are missing."""
    url = meta.get("url")
    if not url:
        return
    has_missing = any(not thumbnails.thumb_exists(video_id, i) for i in range(len(chapters)))
    if has_missing:
        threading.Thread(
            target=thumbnails.generate_chapter_thumbnails,
            args=(video_id, url, chapters),
            daemon=True,
        ).start()


@router.get("/{video_id}/chapters/{chapter_idx}/thumbnail")
def get_chapter_thumbnail(video_id: str, chapter_idx: int):
    path = thumbnails.thumb_path(video_id, chapter_idx)
    if path.exists():
        return FileResponse(str(path), media_type="image/jpeg")
    # Fallback to video thumbnail
    meta = cache.load_video_meta(video_id)
    assert meta is not None, f"Video not found: {video_id}"
    from fastapi.responses import RedirectResponse
    if meta.get("thumbnail_url"):
        return RedirectResponse(meta["thumbnail_url"])
    return FileResponse(str(path), media_type="image/jpeg")  # will 404
