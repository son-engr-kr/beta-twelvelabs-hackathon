from fastapi import APIRouter

from backend.models import IngestRequest, VideoMeta, Chapter
from backend.services import cache, video_service, twelvelabs_service

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
    # Check cache first
    cached = cache.load_chapters(video_id)
    if cached is not None:
        return [Chapter(**c) for c in cached]

    # Get Twelve Labs video ID
    meta = cache.load_video_meta(video_id)
    assert meta is not None, f"Video not found: {video_id}"
    assert meta.get("tl_video_id"), f"Video not indexed: {video_id}"

    # Generate chapters
    chapters = twelvelabs_service.generate_chapters(meta["tl_video_id"])
    cache.save_chapters(video_id, chapters)

    return [Chapter(**c) for c in chapters]
