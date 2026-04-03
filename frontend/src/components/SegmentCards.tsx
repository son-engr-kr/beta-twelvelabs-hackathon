import type { Segment } from '../types';

interface Props {
  segments: Segment[];
  onSelect: (segment: Segment) => void;
  loading: boolean;
  title: string;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function SegmentCards({ segments, onSelect, loading, title }: Props) {
  if (loading) {
    return (
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-3">{title}</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-800 rounded-lg aspect-video" />
              <div className="mt-2 h-4 bg-gray-800 rounded w-3/4" />
              <div className="mt-1 h-3 bg-gray-800 rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (segments.length === 0) return null;

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {segments.map((seg, i) => (
          <button
            key={`${seg.tl_video_id}-${seg.start}-${i}`}
            onClick={() => onSelect(seg)}
            className="group text-left rounded-lg overflow-hidden transition-transform hover:scale-[1.02]"
          >
            <div className="relative aspect-video bg-gray-800 rounded-lg overflow-hidden">
              {seg.thumbnail_url ? (
                <img
                  src={seg.thumbnail_url}
                  alt=""
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-600">
                  No thumbnail
                </div>
              )}
              <div className="absolute bottom-1 right-1 bg-black/80 text-xs px-1.5 py-0.5 rounded">
                {formatTime(seg.start)} - {formatTime(seg.end)}
              </div>
              <div className="absolute top-1 left-1 bg-blue-600/90 text-xs px-1.5 py-0.5 rounded">
                {Math.round(seg.score * 100) > 100
                  ? `#${seg.score}`
                  : `${Math.round(seg.score * 100)}%`}
              </div>
            </div>
            <div className="mt-2 px-1">
              <div className="text-sm font-medium text-gray-200 line-clamp-2 group-hover:text-white">
                {seg.chapter_title || seg.video_title || 'Related segment'}
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {seg.video_title && seg.chapter_title && (
                  <span className="text-gray-400">{seg.video_title}</span>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {formatTime(seg.start)} - {formatTime(seg.end)}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
