import type { Segment } from '../types';

interface Props {
  segments: Segment[];
  onSelect: (segment: Segment) => void;
  loading: boolean;
  error?: string | null;
  hasSearched?: boolean;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function RecommendationList({ segments, onSelect, loading, error, hasSearched }: Props) {
  if (loading) {
    return (
      <div className="text-gray-400 text-center py-8 animate-pulse">
        Finding similar segments...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center py-6 text-sm">
        <p className="font-medium mb-1">Search failed</p>
        <p className="text-red-500 text-xs">{error}</p>
      </div>
    );
  }

  if (hasSearched && segments.length === 0) {
    return (
      <div className="text-gray-400 text-center py-6 text-sm">
        <p className="font-medium mb-1">No similar segments found</p>
        <p className="text-gray-500 text-xs">
          Only videos with generated chapters can be searched.
          Try a different query or wait for more videos to be indexed.
        </p>
      </div>
    );
  }

  if (segments.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8 text-sm">
        Search or click a chapter to find similar segments.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {segments.map((seg, i) => (
        <button
          key={`${seg.tl_video_id}-${seg.start}-${i}`}
          onClick={() => onSelect(seg)}
          className="w-full flex gap-3 p-3 rounded-lg bg-gray-800 hover:bg-gray-700 text-left transition-colors border border-transparent hover:border-blue-500"
        >
          {seg.thumbnail_url && (
            <img
              src={seg.thumbnail_url}
              alt=""
              className="w-24 h-16 object-cover rounded flex-shrink-0"
            />
          )}
          <div className="min-w-0 flex-1">
            <div className="text-sm font-medium text-white truncate">
              {seg.chapter_title || seg.video_title || seg.video_id}
            </div>
            {seg.video_title && seg.chapter_title && (
              <div className="text-xs text-gray-500 truncate">{seg.video_title}</div>
            )}
            <div className="text-xs text-gray-400 mt-1">
              {formatTime(seg.start)} - {formatTime(seg.end)}
            </div>
            <div className="mt-1">
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-900 text-blue-300">
                {(seg.score * 100).toFixed(0)}% match
              </span>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
