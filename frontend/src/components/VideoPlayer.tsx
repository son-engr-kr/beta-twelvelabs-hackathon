import { useRef, useEffect, useCallback } from 'react';

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

declare global {
  interface Window {
    YT: typeof YT;
    onYouTubeIframeAPIReady: (() => void) | undefined;
  }
}

let apiLoaded = false;
let apiReady = false;
const apiReadyCallbacks: (() => void)[] = [];

function ensureYTApi(cb: () => void) {
  if (apiReady) {
    cb();
    return;
  }
  apiReadyCallbacks.push(cb);
  if (!apiLoaded) {
    apiLoaded = true;
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    document.head.appendChild(tag);
    window.onYouTubeIframeAPIReady = () => {
      apiReady = true;
      apiReadyCallbacks.forEach((fn) => fn());
      apiReadyCallbacks.length = 0;
    };
  }
}

export default function VideoPlayer({ url, seekTo, onProgress, onDuration }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<YT.Player | null>(null);
  const intervalRef = useRef<number | null>(null);
  const currentUrlRef = useRef<string>('');

  const startProgressPolling = useCallback(() => {
    if (intervalRef.current) return;
    intervalRef.current = window.setInterval(() => {
      const p = playerRef.current;
      if (p && typeof p.getCurrentTime === 'function') {
        onProgress(p.getCurrentTime());
      }
    }, 500);
  }, [onProgress]);

  const stopProgressPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Create / replace player when URL changes
  useEffect(() => {
    const videoId = extractYouTubeId(url);
    if (!videoId || url === currentUrlRef.current) return;
    currentUrlRef.current = url;

    ensureYTApi(() => {
      // Destroy previous player
      if (playerRef.current) {
        stopProgressPolling();
        playerRef.current.destroy();
        playerRef.current = null;
      }

      if (!containerRef.current) return;
      // YT.Player replaces the target element, so create a fresh div
      const el = document.createElement('div');
      containerRef.current.innerHTML = '';
      containerRef.current.appendChild(el);

      playerRef.current = new window.YT.Player(el, {
        videoId,
        width: '100%',
        height: '100%',
        playerVars: {
          autoplay: 0,
          controls: 1,
          rel: 0,
          modestbranding: 1,
        },
        events: {
          onReady: (e: YT.PlayerEvent) => {
            onDuration(e.target.getDuration());
          },
          onStateChange: (e: YT.OnStateChangeEvent) => {
            if (e.data === window.YT.PlayerState.PLAYING) {
              startProgressPolling();
            } else {
              stopProgressPolling();
            }
          },
        },
      });
    });

    return () => {
      stopProgressPolling();
    };
  }, [url, onDuration, startProgressPolling, stopProgressPolling]);

  // Handle seekTo
  useEffect(() => {
    if (seekTo !== null && playerRef.current && typeof playerRef.current.seekTo === 'function') {
      playerRef.current.seekTo(seekTo, true);
      playerRef.current.playVideo();
    }
  }, [seekTo]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopProgressPolling();
      if (playerRef.current) {
        playerRef.current.destroy();
        playerRef.current = null;
      }
    };
  }, [stopProgressPolling]);

  return (
    <div className="aspect-video bg-black rounded-lg overflow-hidden">
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
}
