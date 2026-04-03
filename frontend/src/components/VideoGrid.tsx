import type { VideoMeta } from '../types';

interface Props {
  videos: VideoMeta[];
  onSelect: (video: VideoMeta) => void;
  selectedId: string | null;
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return '--:--';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function VideoGrid({ videos, onSelect, selectedId }: Props) {
  if (videos.length === 0) {
    return (
      <div className="text-gray-400 text-center py-8">
        No videos yet. Ingest a YouTube URL to get started.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3">
      {videos.map((v) => (
        <button
          key={v.video_id}
          onClick={() => onSelect(v)}
          className={`flex gap-3 p-3 rounded-lg text-left transition-colors ${
            selectedId === v.video_id
              ? 'bg-blue-900/50 border border-blue-500'
              : 'bg-gray-800 hover:bg-gray-700 border border-transparent'
          }`}
        >
          {v.thumbnail_url && (
            <img
              src={v.thumbnail_url}
              alt={v.title}
              className="w-24 h-16 object-cover rounded flex-shrink-0"
            />
          )}
          <div className="min-w-0">
            <div className="text-sm font-medium text-white truncate">{v.title}</div>
            <div className="text-xs text-gray-400 mt-1">{formatDuration(v.duration)}</div>
          </div>
        </button>
      ))}
    </div>
  );
}
