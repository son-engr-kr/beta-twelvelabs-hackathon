from fastapi import APIRouter

from backend.models import RecommendRequest, Segment
from backend.services import cache, twelvelabs_service

router = APIRouter(prefix="/api", tags=["recommend"])


def _resolve_video_title(tl_video_id: str) -> str | None:
    """Look up the local title for a Twelve Labs video ID."""
    for v in cache.list_videos():
        if v.get("tl_video_id") == tl_video_id:
            return v.get("title")
    return None


@router.post("/recommend")
def recommend(req: RecommendRequest) -> list[Segment]:
    index_id = twelvelabs_service.get_or_create_index()

    segments = twelvelabs_service.search_segments(
        index_id=index_id,
        query=req.query,
        top_k=req.top_k,
    )

    # Enrich with local video info
    result = []
    for seg in segments:
        # Find local video_id from tl_video_id
        local_id = None
        for v in cache.list_videos():
            if v.get("tl_video_id") == seg["tl_video_id"]:
                local_id = v["video_id"]
                break

        result.append(Segment(
            video_id=local_id or "unknown",
            tl_video_id=seg["tl_video_id"],
            start=seg["start"],
            end=seg["end"],
            score=seg["score"],
            thumbnail_url=seg.get("thumbnail_url"),
            video_title=_resolve_video_title(seg["tl_video_id"]),
        ))

    return result
