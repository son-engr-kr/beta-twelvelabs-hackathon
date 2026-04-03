from fastapi import APIRouter

from backend.models import RecommendRequest, Segment
from backend.services import search

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend")
def recommend(req: RecommendRequest) -> list[Segment]:
    segments = search.search_segments(
        query=req.query,
        exclude_video_id=req.video_id,
        top_k=req.top_k,
    )

    return [Segment(**seg) for seg in segments]
