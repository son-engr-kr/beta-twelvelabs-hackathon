import json
import os
import urllib.request

import fiftyone.operators as foo
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.environ.get("SEGREG_BACKEND_URL", "http://127.0.0.1:8000")


class FindSimilarSegments(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="find_similar_segments",
            label="Find Similar Segments",
            description="Search for similar video segments using Twelve Labs",
        )

    def resolve_input(self, ctx):
        inputs = foo.types.Object()
        inputs.str(
            "query",
            label="Search Query",
            description="Describe the segment you're looking for",
            required=True,
        )
        inputs.int("top_k", label="Number of Results", default=5)
        return foo.types.Property(inputs)

    def execute(self, ctx):
        query = ctx.params["query"]
        top_k = ctx.params.get("top_k", 5)

        payload = json.dumps({"query": query, "top_k": top_k}).encode()
        req = urllib.request.Request(
            f"{BACKEND_URL}/api/recommend",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req)
        segments = json.loads(resp.read().decode())

        results = []
        for seg in segments:
            results.append({
                "video_id": seg["video_id"],
                "video_title": seg.get("video_title", "Unknown"),
                "start": seg["start"],
                "end": seg["end"],
                "score": f"{seg['score'] * 100:.0f}%",
            })

        return {"segments": results}

    def resolve_output(self, ctx):
        outputs = foo.types.Object()
        outputs.list(
            "segments",
            foo.types.Object(),
            label="Similar Segments",
        )
        return foo.types.Property(outputs)


class IngestVideo(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="ingest_video",
            label="Ingest Video to SegRec",
            description="Add a YouTube video to SegRec — indexes with Twelve Labs and generates chapters",
        )

    def resolve_input(self, ctx):
        inputs = foo.types.Object()
        inputs.str(
            "url",
            label="YouTube URL",
            description="YouTube video URL to ingest",
            required=True,
        )
        return foo.types.Property(inputs)

    def execute(self, ctx):
        url = ctx.params["url"]

        payload = json.dumps({"url": url}).encode()
        req = urllib.request.Request(
            f"{BACKEND_URL}/api/videos/ingest",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            video = json.loads(resp.read().decode())
            return {
                "status": "success",
                "title": video.get("title", "Unknown"),
                "video_id": video.get("video_id", ""),
                "duration": f"{video.get('duration', 0) // 60}m {video.get('duration', 0) % 60}s",
            }
        except Exception as e:
            return {"status": "error", "title": str(e), "video_id": "", "duration": ""}

    def resolve_output(self, ctx):
        outputs = foo.types.Object()
        outputs.str("status", label="Status")
        outputs.str("title", label="Video Title")
        outputs.str("video_id", label="Video ID")
        outputs.str("duration", label="Duration")
        return foo.types.Property(outputs)


def register(plugin):
    plugin.register(FindSimilarSegments)
    plugin.register(IngestVideo)
