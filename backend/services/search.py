"""Local text-based search across cached chapters."""

import re
from collections import Counter

from backend.services import cache


def _tokenize(text: str) -> list[str]:
    return re.findall(r'[a-z0-9]+', text.lower())


def _tfidf_score(query_tokens: list[str], doc_tokens: list[str]) -> float:
    """Simple TF-based relevance score."""
    if not doc_tokens or not query_tokens:
        return 0.0
    doc_counts = Counter(doc_tokens)
    score = 0.0
    for token in query_tokens:
        if token in doc_counts:
            tf = doc_counts[token] / len(doc_tokens)
            score += tf
    return score / len(query_tokens)


def search_segments(query: str, exclude_video_id: str | None = None, top_k: int = 8) -> list[dict]:
    """Search all cached chapters using text similarity."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    all_videos = cache.list_videos()
    results = []

    for video in all_videos:
        vid = video["video_id"]
        if vid == exclude_video_id:
            continue

        chapters = cache.load_chapters(vid)
        if not chapters:
            continue

        for ch in chapters:
            doc_text = f"{ch.get('title', '')} {ch.get('summary', '')}"
            doc_tokens = _tokenize(doc_text)
            score = _tfidf_score(query_tokens, doc_tokens)

            if score > 0:
                results.append({
                    "video_id": vid,
                    "tl_video_id": video.get("tl_video_id", ""),
                    "start": ch["start"],
                    "end": ch["end"],
                    "score": score,
                    "thumbnail_url": video.get("thumbnail_url"),
                    "video_title": f"{video.get('title', 'Unknown')} — {ch.get('title', '')}",
                })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
