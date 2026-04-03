import { useState, useEffect, useRef } from 'react';

interface Props {
  url: string;
  seekTo: number | null;
  onProgress: (seconds: number) => void;
  onDuration: (duration: number) => void;
}

function extractYouTubeId(url: string): string | null {
  const m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s]+)/);
  return m ? m[1] : null;
}

export default function VideoPlayer({ url, seekTo, onProgress, onDuration }: Props) {
  const videoId = extractYouTubeId(url);
  const [startSeconds, setStartSeconds] = useState(0);
  const iframeKey = useRef(0);

  // When seekTo changes, update start time and force iframe reload
  useEffect(() => {
    if (seekTo !== null) {
      setStartSeconds(Math.floor(seekTo));
      iframeKey.current += 1;
    }
  }, [seekTo]);

  if (!videoId) {
    return (
      <div className="aspect-video bg-black rounded-lg flex items-center justify-center text-gray-500">
        Select a video
      </div>
    );
  }

  const embedUrl = `https://www.youtube.com/embed/${videoId}?start=${startSeconds}&autoplay=${seekTo !== null ? 1 : 0}&rel=0&modestbranding=1`;

  return (
    <div className="aspect-video bg-black rounded-lg overflow-hidden">
      <iframe
        key={`${videoId}-${iframeKey.current}`}
        src={embedUrl}
        width="100%"
        height="100%"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        style={{ border: 'none' }}
        title="Video player"
      />
    </div>
  );
}
