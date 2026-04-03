import json
import os
import time

from twelvelabs import TwelveLabs
from twelvelabs.errors import TooManyRequestsError

INDEX_NAME = "segreg-demo"

_client: TwelveLabs | None = None


def _get_client() -> TwelveLabs:
    global _client
    if _client is None:
        api_key = os.environ["TWELVELABS_API_KEY"]
        _client = TwelveLabs(api_key=api_key)
    return _client


def get_or_create_index() -> str:
    client = _get_client()
    # Check if index already exists
    indexes = client.indexes.list()
    for idx in indexes:
        if idx.index_name == INDEX_NAME:
            return idx.id
    # Create new index
    index = client.indexes.create(
        index_name=INDEX_NAME,
        models=[
            {
                "model_name": "marengo3.0",
                "model_options": ["visual", "audio"],
            },
            {
                "model_name": "pegasus1.2",
                "model_options": ["visual", "audio"],
            },
        ],
        addons=["thumbnail"],
    )
    return index.id


def index_video(index_id: str, video_url: str) -> str:
    """Submit a video URL for indexing and wait until ready."""
    client = _get_client()
    task = client.tasks.create(index_id=index_id, video_url=video_url)
    # Poll until complete
    while True:
        task_status = client.tasks.retrieve(task_id=task.id)
        if task_status.status == "ready":
            return task_status.video_id
        assert task_status.status != "failed", f"Indexing failed: {task_status}"
        time.sleep(5)


CHAPTER_PROMPT = """Analyze this video and break it into distinct chapters/segments.
For each chapter, provide:
- start_time (in seconds)
- end_time (in seconds)
- title (short descriptive title)
- summary (1-2 sentence description)

Return ONLY a JSON array, no other text. Example:
[{"start": 0, "end": 30, "title": "Introduction", "summary": "The video begins with..."}]"""


def generate_chapters(video_id: str) -> list[dict]:
    client = _get_client()
    response = client.analyze(
        video_id=video_id,
        prompt=CHAPTER_PROMPT,
    )
    # Parse JSON from the response text
    text = response.data.strip()
    # Handle markdown code blocks
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    chapters = json.loads(text)
    return [
        {
            "start": ch["start_time"] if "start_time" in ch else ch.get("start", 0),
            "end": ch["end_time"] if "end_time" in ch else ch.get("end", 0),
            "title": ch.get("title", "Untitled"),
            "summary": ch.get("summary", ""),
        }
        for ch in chapters
    ]


def search_segments(index_id: str, query: str, top_k: int = 5) -> list[dict]:
    client = _get_client()
    try:
        results = client.search.query(
            index_id=index_id,
            query_text=query,
            search_options=["visual", "audio"],
            group_by="clip",
            page_limit=top_k,
        )
    except TooManyRequestsError as e:
        raise RuntimeError("Twelve Labs API rate limit exceeded (50 req/day). Try again later.") from e
    segments = []
    for item in results:
        segments.append({
            "tl_video_id": item.video_id,
            "start": item.start,
            "end": item.end,
            "score": 1.0 / max(getattr(item, "rank", 1), 1),
            "thumbnail_url": getattr(item, "thumbnail_url", None),
        })
        if len(segments) >= top_k:
            break
    return segments
