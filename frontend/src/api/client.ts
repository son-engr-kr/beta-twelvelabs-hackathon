import type { VideoMeta, Chapter, Segment } from '../types';

const BASE = '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data as T;
}

export function listVideos(): Promise<VideoMeta[]> {
  return request('/videos');
}

export function getVideo(id: string): Promise<VideoMeta> {
  return request(`/videos/${id}`);
}

export function ingestVideo(url: string): Promise<VideoMeta> {
  return request('/videos/ingest', {
    method: 'POST',
    body: JSON.stringify({ url }),
  });
}

export function getChapters(videoId: string): Promise<Chapter[]> {
  return request(`/videos/${videoId}/chapters`);
}

export function recommend(query: string, videoId?: string, topK = 5): Promise<Segment[]> {
  return request('/recommend', {
    method: 'POST',
    body: JSON.stringify({ query, video_id: videoId, top_k: topK }),
  });
}

export function videoStreamUrl(videoId: string): string {
  return `${BASE}/videos/${videoId}/stream`;
}
