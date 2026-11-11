import type { FeedCategories, FeedPreviewResponse, HealthResponse } from "@/types/api";

// URL pública da API. Não é segredo: chaves de API ficam apenas no backend.
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new ApiError(`Não foi possível conectar à API em ${API_URL}`);
  }
  if (!response.ok) {
    throw new ApiError(`A API respondeu com erro ${response.status}`, response.status);
  }
  return (await response.json()) as T;
}

async function fetchWithDetail<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  } catch {
    throw new ApiError(`Não foi possível conectar à API em ${API_URL}`);
  }
  if (!response.ok) {
    let detail = `A API respondeu com erro ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // mantém a mensagem padrão
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health", { cache: "no-store" });
}

export function getFeedCategories(): Promise<FeedCategories> {
  return request<FeedCategories>("/api/feed/categories");
}

export async function getFeedPreview(
  category: string,
  limit = 10,
): Promise<FeedPreviewResponse> {
  const params = new URLSearchParams({ category, limit: String(limit) });
  try {
    return await request<FeedPreviewResponse>(`/api/feed/preview?${params}`, {
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === 502) {
      throw new ApiError("A fonte (arXiv) não respondeu. Tente novamente em instantes.", 502);
    }
    throw error;
  }
}

export function getYoutubeTopics(): Promise<FeedCategories> {
  return request<FeedCategories>("/api/feed/youtube/topics");
}

export async function getYoutubeFeed(topic: string, limit = 10): Promise<FeedPreviewResponse> {
  const params = new URLSearchParams({ topic, limit: String(limit) });
  return fetchWithDetail<FeedPreviewResponse>(`/api/feed/youtube?${params}`);
}
