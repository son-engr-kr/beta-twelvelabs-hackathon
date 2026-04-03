import { useState, useEffect, useCallback } from 'react';
import type { VideoMeta, Chapter, Segment } from './types';
import { listVideos, ingestVideo, getChapters, recommend, videoStreamUrl } from './api/client';
import SearchBar from './components/SearchBar';
import VideoGrid from './components/VideoGrid';
import VideoPlayer from './components/VideoPlayer';
import ChapterTimeline from './components/ChapterTimeline';
import RecommendationList from './components/RecommendationList';

export default function App() {
  const [videos, setVideos] = useState<VideoMeta[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<VideoMeta | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [activeChapterIdx, setActiveChapterIdx] = useState<number | null>(null);
  const [recommendations, setRecommendations] = useState<Segment[]>([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [seekTo, setSeekTo] = useState<number | null>(null);
  const [ingestUrl, setIngestUrl] = useState('');
  const [loading, setLoading] = useState({ ingest: false, chapters: false, recommend: false });

  // Load video list on mount
  useEffect(() => {
    listVideos().then(setVideos);
  }, []);

  // Load chapters when video selected
  useEffect(() => {
    if (!selectedVideo) return;
    setChapters([]);
    setActiveChapterIdx(null);
    setRecommendations([]);
    setLoading((l) => ({ ...l, chapters: true }));
    getChapters(selectedVideo.video_id)
      .then(setChapters)
      .finally(() => setLoading((l) => ({ ...l, chapters: false })));
  }, [selectedVideo]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestUrl.trim()) return;
    setLoading((l) => ({ ...l, ingest: true }));
    const video = await ingestVideo(ingestUrl.trim());
    setVideos((prev) => [...prev, video]);
    setIngestUrl('');
    setSelectedVideo(video);
    setLoading((l) => ({ ...l, ingest: false }));
  };

  const handleChapterSelect = useCallback(
    (chapter: Chapter) => {
      const idx = chapters.indexOf(chapter);
      setActiveChapterIdx(idx);
      setSeekTo(chapter.start);
      // Search for similar segments using chapter title
      setLoading((l) => ({ ...l, recommend: true }));
      recommend(chapter.title, selectedVideo?.video_id)
        .then(setRecommendations)
        .finally(() => setLoading((l) => ({ ...l, recommend: false })));
    },
    [chapters, selectedVideo]
  );

  const handleSearch = useCallback(
    (query: string) => {
      setLoading((l) => ({ ...l, recommend: true }));
      recommend(query, selectedVideo?.video_id)
        .then(setRecommendations)
        .finally(() => setLoading((l) => ({ ...l, recommend: false })));
    },
    [selectedVideo]
  );

  const handleRecommendationSelect = useCallback(
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
            <SearchBar onSearch={handleSearch} loading={loading.recommend} />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left sidebar - Video list + Ingest */}
          <div className="col-span-3 space-y-4">
            <form onSubmit={handleIngest} className="flex gap-2">
              <input
                type="text"
                value={ingestUrl}
                onChange={(e) => setIngestUrl(e.target.value)}
                placeholder="YouTube URL"
                className="flex-1 px-3 py-2 text-sm rounded-lg border border-gray-700 bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={loading.ingest}
                className="px-3 py-2 text-sm bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {loading.ingest ? '...' : '+'}
              </button>
            </form>
            <VideoGrid
              videos={videos}
              onSelect={setSelectedVideo}
              selectedId={selectedVideo?.video_id ?? null}
            />
          </div>

          {/* Center - Player + Chapters */}
          <div className="col-span-6 space-y-4">
            {selectedVideo ? (
              <>
                <VideoPlayer
                  url={videoStreamUrl(selectedVideo.video_id)}
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
              </>
            ) : (
              <div className="flex items-center justify-center h-96 bg-gray-900 rounded-lg">
                <p className="text-gray-500">Select a video to start</p>
              </div>
            )}
          </div>

          {/* Right sidebar - Recommendations */}
          <div className="col-span-3 space-y-3">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
              Similar Segments
            </h3>
            <RecommendationList
              segments={recommendations}
              onSelect={handleRecommendationSelect}
              loading={loading.recommend}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
