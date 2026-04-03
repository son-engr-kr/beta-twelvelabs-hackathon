import { useState, useEffect, useCallback, useRef } from 'react';
import type { VideoMeta, Chapter, Segment } from './types';
import { listVideos, ingestVideo, getChapters, recommend } from './api/client';
import SearchBar from './components/SearchBar';
import VideoGrid from './components/VideoGrid';
import VideoPlayer from './components/VideoPlayer';
import ChapterTimeline from './components/ChapterTimeline';
import RecommendationList from './components/RecommendationList';
import SegmentCards from './components/SegmentCards';

export default function App() {
  const [videos, setVideos] = useState<VideoMeta[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<VideoMeta | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [activeChapterIdx, setActiveChapterIdx] = useState<number | null>(null);
  const [searchResults, setSearchResults] = useState<Segment[]>([]);
  const [autoRecs, setAutoRecs] = useState<Segment[]>([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [seekTo, setSeekTo] = useState<number | null>(null);
  const [ingestUrl, setIngestUrl] = useState('');
  const [loading, setLoading] = useState({ ingest: false, chapters: false, search: false, autoRec: false });
  const [error, setError] = useState<string | null>(null);
  const [showIndexedOnly, setShowIndexedOnly] = useState(true);
  const lastAutoRecChapter = useRef<number | null>(null);

  const filteredVideos = showIndexedOnly
    ? videos.filter((v) => v.tl_video_id)
    : videos;

  // Load video list on mount + poll for new videos during seeding
  useEffect(() => {
    listVideos().then(setVideos).catch((e) => setError(e.message));
    const interval = setInterval(() => {
      listVideos().then(setVideos).catch(() => {});
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Load chapters when video selected
  useEffect(() => {
    if (!selectedVideo) return;
    setChapters([]);
    setActiveChapterIdx(null);
    setAutoRecs([]);
    setError(null);
    lastAutoRecChapter.current = null;
    setLoading((l) => ({ ...l, chapters: true }));
    getChapters(selectedVideo.video_id)
      .then(setChapters)
      .catch((e) => setError(e.message))
      .finally(() => setLoading((l) => ({ ...l, chapters: false })));
  }, [selectedVideo]);

  // Auto-recommend when chapters load (use first chapter's title as query)
  useEffect(() => {
    if (chapters.length === 0 || !selectedVideo) return;
    setLoading((l) => ({ ...l, autoRec: true }));
    recommend(selectedVideo.title, selectedVideo.video_id, 8)
      .then(setAutoRecs)
      .catch(() => {})
      .finally(() => setLoading((l) => ({ ...l, autoRec: false })));
  }, [chapters, selectedVideo]);

  // Auto-update recommendations when playback enters a new chapter
  useEffect(() => {
    if (chapters.length === 0 || !selectedVideo) return;
    const idx = chapters.findIndex((ch) => currentTime >= ch.start && currentTime < ch.end);
    if (idx === -1 || idx === lastAutoRecChapter.current) return;
    lastAutoRecChapter.current = idx;
    setActiveChapterIdx(idx);
    setLoading((l) => ({ ...l, autoRec: true }));
    recommend(chapters[idx].title, selectedVideo.video_id, 8)
      .then(setAutoRecs)
      .catch(() => {})
      .finally(() => setLoading((l) => ({ ...l, autoRec: false })));
  }, [currentTime, chapters, selectedVideo]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestUrl.trim()) return;
    setLoading((l) => ({ ...l, ingest: true }));
    setError(null);
    ingestVideo(ingestUrl.trim())
      .then((video) => {
        setVideos((prev) => [...prev, video]);
        setIngestUrl('');
        setSelectedVideo(video);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading((l) => ({ ...l, ingest: false })));
  };

  const handleChapterSelect = useCallback(
    (chapter: Chapter, index: number) => {
      setActiveChapterIdx(index);
      setSeekTo(chapter.start);
      lastAutoRecChapter.current = index;
      setError(null);
      setLoading((l) => ({ ...l, autoRec: true }));
      recommend(chapter.title, selectedVideo?.video_id, 8)
        .then(setAutoRecs)
        .catch((e) => setError(e.message))
        .finally(() => setLoading((l) => ({ ...l, autoRec: false })));
    },
    [selectedVideo]
  );

  const handleSearch = useCallback(
    (query: string) => {
      setError(null);
      setLoading((l) => ({ ...l, search: true }));
      recommend(query, selectedVideo?.video_id)
        .then(setSearchResults)
        .catch((e) => setError(e.message))
        .finally(() => setLoading((l) => ({ ...l, search: false })));
    },
    [selectedVideo]
  );

  const handleSegmentSelect = useCallback(
    (seg: Segment) => {
      const target = videos.find((v) => v.video_id === seg.video_id);
      if (target && target.video_id !== selectedVideo?.video_id) {
        setSelectedVideo(target);
      }
      setSeekTo(seg.start);
    },
    [videos, selectedVideo]
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">SegRec</h1>
            <p className="text-sm text-gray-400">Segment-Level Video Recommendations</p>
          </div>
          <div className="w-96">
            <SearchBar onSearch={handleSearch} loading={loading.search} />
          </div>
        </div>
      </header>

      {error && (
        <div className="max-w-7xl mx-auto px-6 pt-4">
          <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-2 rounded-lg text-sm">
            {error}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left sidebar - Video list + Ingest */}
          <div className="col-span-3 space-y-4 relative z-10">
            <form onSubmit={handleIngest} className="flex gap-2 sticky top-0 bg-gray-950 py-2">
              <input
                type="text"
                value={ingestUrl}
                onChange={(e) => setIngestUrl(e.target.value)}
                placeholder="YouTube URL"
                className="flex-1 min-w-0 px-3 py-2 text-sm rounded-lg border border-gray-700 bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={loading.ingest}
                className="px-3 py-2 text-sm bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 flex-shrink-0"
              >
                {loading.ingest ? '...' : '+'}
              </button>
            </form>
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span>{filteredVideos.length} / {videos.length} videos</span>
              <button
                onClick={() => setShowIndexedOnly((v) => !v)}
                className={`px-2 py-1 rounded text-xs ${
                  showIndexedOnly
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'bg-gray-800 text-gray-400'
                }`}
              >
                {showIndexedOnly ? 'Indexed only' : 'Show all'}
              </button>
            </div>
            <div className="max-h-[calc(100vh-240px)] overflow-y-auto">
            <VideoGrid
              videos={filteredVideos}
              onSelect={setSelectedVideo}
              selectedId={selectedVideo?.video_id ?? null}
            />
            </div>
          </div>

          {/* Center + Right area */}
          <div className="col-span-9 space-y-4">
            {selectedVideo ? (
              <>
                <div className="grid grid-cols-3 gap-6">
                  {/* Player + Chapters */}
                  <div className="col-span-2 space-y-4">
                    <VideoPlayer
                      url={selectedVideo.url || ''}
                      seekTo={seekTo}
                      onProgress={setCurrentTime}
                      onDuration={setDuration}
                    />
                    <h2 className="text-lg font-semibold">{selectedVideo.title}</h2>
                    {loading.chapters ? (
                      <div className="text-gray-400 animate-pulse">Generating chapters...</div>
                    ) : (
                      <ChapterTimeline
                        chapters={chapters}
                        duration={duration}
                        currentTime={currentTime}
                        onSelect={handleChapterSelect}
                        activeIndex={activeChapterIdx}
                      />
                    )}
                  </div>

                  {/* Search results sidebar */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
                      Search Results
                    </h3>
                    <RecommendationList
                      segments={searchResults}
                      onSelect={handleSegmentSelect}
                      loading={loading.search}
                    />
                  </div>
                </div>

                {/* Recommended segments below player - YouTube style */}
                <SegmentCards
                  segments={autoRecs}
                  onSelect={handleSegmentSelect}
                  loading={loading.autoRec}
                  title={
                    activeChapterIdx !== null && chapters[activeChapterIdx]
                      ? `Similar to "${chapters[activeChapterIdx].title}"`
                      : 'Recommended Segments'
                  }
                />
              </>
            ) : (
              <div className="flex items-center justify-center h-96 bg-gray-900 rounded-lg">
                <p className="text-gray-500">Select a video to start</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
