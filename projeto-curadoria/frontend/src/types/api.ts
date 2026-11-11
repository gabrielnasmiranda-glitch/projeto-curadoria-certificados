export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
}

export interface ContentPreview {
  external_id: string;
  source: string;
  title: string;
  summary: string | null;
  authors: string[];
  categories: string[];
  published_at: string | null;
  url: string;
  thumbnail_url: string | null;
  view_count: number | null;
}

export interface FeedPreviewResponse {
  category: string;
  count: number;
  items: ContentPreview[];
  evaluated: boolean;
  note: string;
}

export type FeedCategories = Record<string, string>;
