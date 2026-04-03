"""Auto-seed videos on server startup if none exist."""

import threading
import logging
import time

from backend.services import cache, video_service, twelvelabs_service

logger = logging.getLogger(__name__)

SEED_URLS = [
    # Cooking
    "https://www.youtube.com/watch?v=ZJy1ajvMU1k",  # Gordon Ramsay - 5 Basic Cooking Skills
    "https://www.youtube.com/watch?v=1AxLzMJIgxM",  # Babish - Essential Kitchen Tools
    # Fitness / Sports
    "https://www.youtube.com/watch?v=IODxDxX7oi4",  # The Perfect Push Up
    "https://www.youtube.com/watch?v=gC_L9qAHVJ8",  # 30 min fat burning workout
    "https://www.youtube.com/watch?v=brFHyOtTwH4",  # Running Form Tips
    # Science / Education
    "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown - Neural networks
    "https://www.youtube.com/watch?v=HEfHFsfGXjs",  # Veritasium - Counting puzzle
    "https://www.youtube.com/watch?v=p7nGcY73epw",  # Computerphile - Abstraction
    # Nature / Travel
    "https://www.youtube.com/watch?v=LXb3EKWsInQ",  # Costa Rica 4K
    # Music
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",  # Ed Sheeran - Shape of You
    "https://www.youtube.com/watch?v=RgKAFK5djSk",  # See You Again
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
    "https://www.youtube.com/watch?v=CevxZvSJLk8",  # Katy Perry - Roar
    "https://www.youtube.com/watch?v=YQHsXMglC9A",  # Adele - Hello
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
    # Other
    "https://www.youtube.com/watch?v=4vTJHUDB5ak",  # Yoga for neck/shoulders
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (first YT video)
]


def _recover_from_index(index_id: str):
    """Recover cache from existing Twelve Labs assets."""
    client = twelvelabs_service._get_client()
    assets = list(client.assets.list())
    if not assets:
        return

    # Build filename -> tl_video_id map
    tl_map = {}
    for asset in assets:
        if asset.filename and asset.status == "ready":
            local_id = asset.filename.replace(".mp4", "")
            tl_map[local_id] = asset.id

    if not tl_map:
        return

    logger.info(f"Found {len(tl_map)} indexed assets in Twelve Labs. Recovering cache...")

    # For each seed URL, check if its video_id matches a TL asset
    for url in SEED_URLS:
        video_id = video_service._video_id_from_url(url)
        existing = cache.load_video_meta(video_id)

        if existing and existing.get("tl_video_id"):
            continue  # Already have full data

        if video_id in tl_map:
            try:
                meta = video_service.extract_metadata(url)
                meta["tl_index_id"] = index_id
                meta["tl_video_id"] = tl_map[video_id]
                cache.save_video_meta(video_id, meta)
                logger.info(f"Recovered: {meta['title']} -> {tl_map[video_id]}")
            except Exception as e:
                logger.warning(f"Failed to recover {url}: {e}")


def _ingest_one(url: str, index_id: str) -> bool:
    """Ingest a video. Returns True if fully indexed, False if metadata-only."""
    meta = video_service.extract_metadata(url)
    meta["tl_index_id"] = index_id

    try:
        tl_video_id = twelvelabs_service.index_video(index_id, url)
        meta["tl_video_id"] = tl_video_id
        cache.save_video_meta(meta["video_id"], meta)
        logger.info(f"Seeded + indexed: {meta['title']}")
        return True
    except Exception as e:
        if "429" in str(e) or "too_many_requests" in str(e):
            cache.save_video_meta(meta["video_id"], meta)
            logger.warning(f"Rate limited. Saved metadata only: {meta['title']}")
            return False
        raise


def _seed_worker():
    index_id = twelvelabs_service.get_or_create_index()

    # Step 1: Recover existing TL assets into cache
    _recover_from_index(index_id)

    # Step 2: Seed missing videos
    existing = cache.list_videos()
    existing_urls = {v.get("url") for v in existing}
    urls_to_seed = [u for u in SEED_URLS if u not in existing_urls]

    if not urls_to_seed:
        logger.info(f"All {len(SEED_URLS)} seed videos present.")
        return

    logger.info(f"Have {len(existing)} videos. Seeding {len(urls_to_seed)} more...")

    rate_limited = False
    for i, url in enumerate(urls_to_seed):
        logger.info(f"[{i+1}/{len(urls_to_seed)}] {url}")

        if rate_limited:
            try:
                meta = video_service.extract_metadata(url)
                meta["tl_index_id"] = index_id
                cache.save_video_meta(meta["video_id"], meta)
                logger.info(f"Saved metadata: {meta['title']}")
            except Exception as e:
                logger.warning(f"Failed metadata for {url}: {e}")
            continue

        try:
            indexed = _ingest_one(url, index_id)
            if not indexed:
                rate_limited = True
        except Exception as e:
            logger.warning(f"Failed to seed {url}: {e}")

    # Step 3: Retry unindexed in background
    unindexed = [v for v in cache.list_videos() if not v.get("tl_video_id")]
    if unindexed:
        logger.info(f"{len(unindexed)} videos need indexing. Retrying in background...")
        _retry_indexing(index_id, unindexed)

    logger.info("Seeding complete.")


def _retry_indexing(index_id: str, videos: list[dict]):
    """Retry indexing for metadata-only videos."""
    while videos:
        logger.info(f"Waiting 60s before retrying {len(videos)} videos...")
        time.sleep(60)
        remaining = []
        for v in videos:
            url = v.get("url")
            if not url:
                continue
            try:
                tl_video_id = twelvelabs_service.index_video(index_id, url)
                v["tl_video_id"] = tl_video_id
                cache.save_video_meta(v["video_id"], v)
                logger.info(f"Indexed: {v['title']}")
            except Exception as e:
                if "429" in str(e) or "too_many_requests" in str(e):
                    remaining = videos[videos.index(v):]
                    logger.warning(f"Still rate limited. {len(remaining)} remaining.")
                    break
                logger.warning(f"Failed to index {url}: {e}")
        videos = remaining


def seed_if_empty():
    """Run seed in a background thread so server starts immediately."""
    t = threading.Thread(target=_seed_worker, daemon=True)
    t.start()
