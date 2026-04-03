"""Local embedding using sentence-transformers. No API dependency."""

import json
import math
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

EMBED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cache" / "embeddings"
MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, fast, good quality

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded.")
    return _model


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


def embed_text(text: str, cache_key: str) -> list[float]:
    """Get embedding for text, using cache if available."""
    cached = _load_cached(cache_key)
    if cached is not None:
        return cached

    model = _get_model()
    vec = model.encode(text).tolist()
    _save_cached(cache_key, vec)
    return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
