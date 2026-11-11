"use client";

import { useEffect, useState } from "react";

import {
  getFeedCategories,
  getFeedPreview,
  getYoutubeFeed,
  getYoutubeTopics,
} from "@/services/api";
import type { FeedCategories, FeedPreviewResponse } from "@/types/api";

export type FeedSource = "youtube" | "arxiv";

export type FeedState =
  | { status: "loading" }
  | { status: "ready"; data: FeedPreviewResponse }
  | { status: "error"; message: string };

export function useFeedOptions(source: FeedSource): FeedCategories | null {
  const [result, setResult] = useState<{ source: FeedSource; options: FeedCategories } | null>(
    null,
  );

  useEffect(() => {
    let cancelled = false;
    const load = source === "youtube" ? getYoutubeTopics : getFeedCategories;
    load()
      .then((options) => {
        if (!cancelled) setResult({ source, options });
      })
      .catch(() => {
        // Sem a lista, o seletor usa apenas o valor padrão.
      });
    return () => {
      cancelled = true;
    };
  }, [source]);

  return result && result.source === source ? result.options : null;
}

export function useFeed(source: FeedSource, option: string): FeedState {
  const key = `${source}:${option}`;
  const [result, setResult] = useState<{ key: string; state: FeedState } | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data =
          source === "youtube" ? await getYoutubeFeed(option) : await getFeedPreview(option);
        if (!cancelled) setResult({ key, state: { status: "ready", data } });
      } catch (error) {
        const message = error instanceof Error ? error.message : "Erro desconhecido";
        if (!cancelled) setResult({ key, state: { status: "error", message } });
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [source, option, key]);

  if (!result || result.key !== key) return { status: "loading" };
  return result.state;
}
