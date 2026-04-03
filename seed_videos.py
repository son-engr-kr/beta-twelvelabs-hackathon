"""Seed the app with multiple YouTube videos.
Run while the backend server is up: python seed_videos.py
"""

import json
import urllib.request
import sys
import time

BACKEND = "http://127.0.0.1:8000"

# Diverse set of short YouTube videos (< 10 min each to stay within free tier)
VIDEOS = [
    # Cooking
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # placeholder - replace with real URLs
    "https://www.youtube.com/watch?v=ZJy1ajvMU1k",  # Gordon Ramsay scrambled eggs
    "https://www.youtube.com/watch?v=hLnEC5qhJEk",  # Japanese street food
    # Sports / Fitness
    "https://www.youtube.com/watch?v=IODxDxX7oi4",  # Yoga for beginners
    "https://www.youtube.com/watch?v=ml6cT4AZdqI",  # Basketball highlights
    # Nature / Travel
    "https://www.youtube.com/watch?v=LXb3EKWsInQ",  # Costa Rica 4K
    "https://www.youtube.com/watch?v=n4DPTm9mCak",  # Northern lights
    # Music / Performance
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",  # Ed Sheeran
    # Education / Science
    "https://www.youtube.com/watch?v=rKS6eYGMrtg",  # How batteries work
    "https://www.youtube.com/watch?v=R9OHn5ZF4Uo",  # 3Blue1Brown
    # Tech
    "https://www.youtube.com/watch?v=aircAruvnKk",  # Neural networks
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # placeholder
]


def ingest(url: str) -> dict | None:
    payload = json.dumps({"url": url}).encode()
    req = urllib.request.Request(
        f"{BACKEND}/api/videos/ingest",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=600)
    return json.loads(resp.read().decode())


def main():
    # Remove duplicates while preserving order
    urls = list(dict.fromkeys(VIDEOS))
    total = len(urls)
    print(f"Ingesting {total} videos...\n")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{total}] {url}")
        start = time.time()
        result = ingest(url)
        elapsed = time.time() - start
        print(f"  -> {result['title']} ({elapsed:.0f}s)\n")

    print(f"\nDone! {total} videos ingested.")
    resp = urllib.request.urlopen(f"{BACKEND}/api/videos")
    videos = json.loads(resp.read().decode())
    print(f"Total videos in library: {len(videos)}")


if __name__ == "__main__":
    main()
