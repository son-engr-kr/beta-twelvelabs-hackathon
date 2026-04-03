export interface VideoMeta {
  video_id: string;
  title: string;
  duration: number | null;
  thumbnail_url: string | null;
  url: string | null;
  tl_video_id: string | null;
  tl_index_id: string | null;
}

export interface Chapter {
  start: number;
  end: number;
  title: string;
  summary: string;
}

export interface Segment {
  video_id: string;
  tl_video_id: string;
  start: number;
  end: number;
  score: number;
  thumbnail_url: string | null;
  video_title: string | null;
  chapter_title: string | null;
}
