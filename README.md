# SegRec: Segment-Level Video Recommendation Engine

YouTube recommends **whole videos**. SegRec recommends **specific segments**.

Click a chapter in one video, and discover similar moments across your entire library.

## Setup

### 1. Environment

```bash
# Create venv with Python 3.11.9
uv venv --python 3.11.9

# Activate
source .venv/Scripts/activate   # Windows (Git Bash)
source .venv/bin/activate       # macOS/Linux

# Install backend dependencies
uv pip install fastapi "uvicorn[standard]" yt-dlp twelvelabs python-dotenv

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. API Key

Create a `.env` file in the project root:

```
TWELVELABS_API_KEY=your-api-key-here
```

Get your key at https://api.twelvelabs.io

### 3. Run

```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:5173 (proxies `/api` to backend)

### 4. FiftyOne Plugin (optional)

```bash
mkdir -p ~/fiftyone/__plugins__
ln -s "$(pwd)/plugin" ~/fiftyone/__plugins__/video-understanding-plugin
```

## How It Works

1. Paste a YouTube URL to ingest a video (download + Twelve Labs indexing)
2. Auto-generated chapters appear as a clickable timeline
3. Click a chapter to find similar segments across all indexed videos
4. Click a recommendation to jump to that exact moment

## Project Structure

```
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # Pydantic request/response models
│   ├── routers/
│   │   ├── videos.py           # /api/videos endpoints
│   │   └── recommend.py        # /api/recommend endpoint
│   └── services/
│       ├── twelvelabs_service.py  # Twelve Labs API (index, chapters, search)
│       ├── video_service.py       # yt-dlp video download
│       └── cache.py               # JSON file cache
├── frontend/
│   └── src/
│       ├── App.tsx             # Main layout and state management
│       ├── api/client.ts       # Backend API client
│       └── components/
│           ├── VideoPlayer.tsx
│           ├── ChapterTimeline.tsx
│           ├── RecommendationList.tsx
│           ├── SearchBar.tsx
│           └── VideoGrid.tsx
├── plugin/
│   ├── fiftyone.yml            # FiftyOne plugin metadata
│   └── __init__.py             # FindSimilarSegments operator
├── data/
│   ├── cache/                  # JSON cache files
│   └── videos/                 # Downloaded video files
└── .env                        # API keys (not committed)
```

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | FastAPI + Python 3.11 |
| Frontend | Vite + React + TypeScript + Tailwind CSS |
| Video Player | react-player |
| Video Source | YouTube (yt-dlp) |
| Indexing & Search | Twelve Labs API (Marengo + Pegasus) |
| FiftyOne Plugin | FindSimilarSegments operator |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/videos/ingest` | Download YouTube video + index with Twelve Labs |
| `GET` | `/api/videos` | List all indexed videos |
| `GET` | `/api/videos/{id}` | Video details |
| `GET` | `/api/videos/{id}/chapters` | Auto-generated chapters |
| `GET` | `/api/videos/{id}/stream` | Stream video file |
| `POST` | `/api/recommend` | Find similar segments by text query |
| `GET` | `/api/status` | Health check |
