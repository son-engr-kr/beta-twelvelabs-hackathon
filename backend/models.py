from pydantic import BaseModel


# --- Request models ---

class IngestRequest(BaseModel):
    url: str


class RecommendRequest(BaseModel):
    query: str
    video_id: str | None = None
    top_k: int = 5


# --- Response models ---

class VideoMeta(BaseModel):
    video_id: str
    title: str
    duration: float | None = None
    thumbnail_url: str | None = None
    url: str | None = None  # YouTube URL for playback
    tl_video_id: str | None = None  # Twelve Labs video ID
    tl_index_id: str | None = None  # Twelve Labs index ID


class Chapter(BaseModel):
    start: float
    end: float
    title: str
    summary: str


class Segment(BaseModel):
    video_id: str
    tl_video_id: str
    start: float
    end: float
    score: float
    thumbnail_url: str | None = None
    video_title: str | None = None
