"""Embeddings using Twelve Labs Marengo. Falls back to sentence-transformers if unavailable."""

import json
import math
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

EMBED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cache" / "embeddings"
TL_EMBED_MODEL = "Marengo-retrieval-2.7"

_tl_client = None
_st_model = None


def _get_tl_client():
    global _tl_client
    if _tl_client is None:
        from twelvelabs import TwelveLabs
        _tl_client = TwelveLabs(api_key=os.environ["TWELVELABS_API_KEY"])
    return _tl_client


def _get_st_model():
    global _st_model
    if _st_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading fallback sentence-transformers model")
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _st_model


def _cache_path(key: str) -> Path:
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    return EMBED_DIR / f"{key}.json"


def _load_cached(key: str) -> list[float] | None:
    path = _cache_path(key)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _save_cached(key: str, vec: list[float]):
    path = _cache_path(key)
    path.write_text(json.dumps(vec), encoding="utf-8")


def _tl_embed(text: str) -> list[float]:
    """Call Twelve Labs Marengo text embedding API."""
    client = _get_tl_client()
    res = client.embed.create(model_name=TL_EMBED_MODEL, text=text)
    te = res.text_embedding
    # Handle different SDK versions
    if hasattr(te, "float") and te.float:
        return te.float
    if hasattr(te, "segments") and te.segments:
        seg = te.segments[0]
        vec = getattr(seg, "embeddings_float", None) or getattr(seg, "float", None)
        if vec:
            return vec
    raise ValueError("Unexpected TL embed response structure")


def embed_text(text: str, cache_key: str) -> list[float]:
    """Get embedding via Twelve Labs Marengo; falls back to sentence-transformers."""
    cached = _load_cached(cache_key)
    if cached is not None:
        return cached

    try:
        vec = _tl_embed(text)
        _save_cached(cache_key, vec)
        logger.debug(f"TL embed: {cache_key} ({len(vec)}d)")
        return vec
    except Exception as e:
        logger.warning(f"TL embed failed ({e}), using sentence-transformers")

    model = _get_st_model()
    vec = model.encode(text).tolist()
    _save_cached(cache_key, vec)
    return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
