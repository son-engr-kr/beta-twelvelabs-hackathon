import type { Chapter } from '../types';

interface Props {
  chapters: Chapter[];
  duration: number;
  currentTime: number;
  onSelect: (chapter: Chapter, index: number) => void;
  activeIndex: number | null;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function ChapterTimeline({ chapters, duration, currentTime, onSelect, activeIndex }: Props) {
  if (chapters.length === 0) return null;

  return (
    <div className="space-y-2">
      {/* Visual timeline bar */}
      <div className="relative h-8 bg-gray-800 rounded-full overflow-hidden">
        {chapters.map((ch, i) => {
          const left = (ch.start / duration) * 100;
          const width = ((ch.end - ch.start) / duration) * 100;
          const isActive = activeIndex === i;
          const isCurrent = currentTime >= ch.start && currentTime < ch.end;
          return (
            <button
              key={i}
              onClick={() => onSelect(ch, i)}
              className={`absolute top-0 h-full border-r border-gray-900 transition-colors ${
                isActive
                  ? 'bg-blue-500'
                  : isCurrent
                  ? 'bg-blue-700'
                  : 'bg-gray-600 hover:bg-gray-500'
              }`}
              style={{ left: `${left}%`, width: `${width}%` }}
              title={ch.title}
            />
          );
        })}
        {/* Playhead */}
        <div
          className="absolute top-0 h-full w-0.5 bg-red-500 z-10"
          style={{ left: `${(currentTime / duration) * 100}%` }}
        />
      </div>

      {/* Chapter list */}
      <div className="grid grid-cols-1 gap-1 max-h-48 overflow-y-auto">
        {chapters.map((ch, i) => (
          <button
            key={i}
            onClick={() => onSelect(ch, i)}
            className={`flex items-center gap-2 px-3 py-2 rounded text-left text-sm transition-colors ${
              activeIndex === i
                ? 'bg-blue-900/50 text-blue-300'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            <span className="text-xs text-gray-500 w-12 flex-shrink-0">
              {formatTime(ch.start)}
            </span>
            <span className="truncate">{ch.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
