"""Hybrid search: embedding cosine similarity + text fallback."""

import re
import logging
from collections import Counter

from backend.services import cache, embeddings

logger = logging.getLogger(__name__)


def _chapter_cache_key(video_id: str, idx: int) -> str:
    return f"ch_{video_id}_{idx}"


def embed_all_chapters():
    """Pre-embed all cached chapters. Safe to call multiple times."""
    all_videos = cache.list_videos()
    total = 0
    skipped = 0

    for video in all_videos:
        vid = video["video_id"]
        chapters = cache.load_chapters(vid)
        if not chapters:
            continue

        for i, ch in enumerate(chapters):
            key = _chapter_cache_key(vid, i)
            if embeddings._load_cached(key) is not None:
                skipped += 1
                continue

            text = f"{ch.get('title', '')}. {ch.get('summary', '')}"
            try:
                embeddings.embed_text(text, key)
                total += 1
                logger.info(f"Embedded: {vid} ch{i} — {ch.get('title', '')[:40]}")
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    logger.warning(f"Rate limited during embedding. Stopping.")
                    return
                logger.warning(f"Failed to embed {vid} ch{i}: {e}")
                continue

    logger.info(f"Embedding done. New: {total}, Already cached: {skipped}")


def _tokenize(text: str) -> list[str]:
    return re.findall(r'[a-z0-9]+', text.lower())


def _text_score(query_tokens: list[str], doc_tokens: list[str]) -> float:
    if not doc_tokens or not query_tokens:
        return 0.0
    counts = Counter(doc_tokens)
    matches = sum(1 for t in query_tokens if t in counts)
    return matches / len(query_tokens) * 0.5  # scale to 0-0.5 range


def search_segments(query: str, exclude_video_id: str | None = None, top_k: int = 8) -> list[dict]:
    """Hybrid search across all cached chapters."""
    query_tokens = _tokenize(query)

    # Try to embed the query
    query_key = f"q_{hash(query) & 0xFFFFFFFF:08x}"
    query_vec = None
    try:
        query_vec = embeddings.embed_text(query, query_key)
    except Exception:
        pass

    all_videos = cache.list_videos()
    results = []

    for video in all_videos:
        vid = video["video_id"]
        if vid == exclude_video_id:
            continue

        chapters = cache.load_chapters(vid)
        if not chapters:
            continue

        for i, ch in enumerate(chapters):
            doc_text = f"{ch.get('title', '')} {ch.get('summary', '')}"
            doc_tokens = _tokenize(doc_text)

            # Try embedding similarity first
            score = 0.0
            key = _chapter_cache_key(vid, i)
            ch_vec = embeddings._load_cached(key)

            if query_vec and ch_vec:
                score = embeddings.cosine_similarity(query_vec, ch_vec)
            else:
                # Text fallback
                score = _text_score(query_tokens, doc_tokens)

            if score > 0.05:
                results.append({
                    "video_id": vid,
                    "tl_video_id": video.get("tl_video_id", ""),
                    "start": ch["start"],
                    "end": ch["end"],
                    "score": round(score, 4),
                    "thumbnail_url": f"/api/videos/{vid}/chapters/{i}/thumbnail",
                    "video_title": video.get("title", "Unknown"),
                    "chapter_title": ch.get("title", ""),
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
