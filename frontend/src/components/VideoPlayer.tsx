import { useRef, useEffect, useCallback } from 'react';
import ReactPlayer from 'react-player';

interface Props {
  url: string;
  seekTo: number | null;
  onProgress: (seconds: number) => void;
  onDuration: (duration: number) => void;
}

export default function VideoPlayer({ url, seekTo, onProgress, onDuration }: Props) {
  const playerRef = useRef<ReactPlayer>(null);

  useEffect(() => {
    if (seekTo !== null && playerRef.current) {
      playerRef.current.seekTo(seekTo, 'seconds');
    }
  }, [seekTo]);

  const handleProgress = useCallback(
    (state: { playedSeconds: number }) => {
      onProgress(state.playedSeconds);
    },
    [onProgress]
  );

  return (
    <div className="aspect-video bg-black rounded-lg overflow-hidden">
      <ReactPlayer
        ref={playerRef}
        url={url}
        width="100%"
        height="100%"
        controls
        playing
        onProgress={handleProgress}
        onDuration={onDuration}
        progressInterval={500}
      />
    </div>
  );
}
