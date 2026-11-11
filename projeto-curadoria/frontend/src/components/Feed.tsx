"use client";

import { useState } from "react";

import FeedCard from "@/components/FeedCard";
import { useFeed, useFeedOptions, type FeedSource } from "@/hooks/useFeed";

const SOURCES: Record<FeedSource, { label: string; defaultOption: string; title: string; subtitle: string; selectLabel: string }> = {
  youtube: {
    label: "YouTube",
    defaultOption: "ia",
    title: "Vídeos em português",
    subtitle: "Resultados reais da API oficial do YouTube, por tópico.",
    selectLabel: "Tópico",
  },
  arxiv: {
    label: "Artigos científicos (arXiv)",
    defaultOption: "cs.AI",
    title: "Artigos recentes",
    subtitle: "Publicações reais do arXiv, ordenadas por data de envio (em inglês).",
    selectLabel: "Área",
  },
};

export default function Feed() {
  const [source, setSource] = useState<FeedSource>("youtube");
  const [options, setOptions] = useState<Record<FeedSource, string>>({
    youtube: SOURCES.youtube.defaultOption,
    arxiv: SOURCES.arxiv.defaultOption,
  });

  const option = options[source];
  const available = useFeedOptions(source);
  const state = useFeed(source, option);
  const config = SOURCES[source];

  return (
    <section className="flex flex-col gap-5" aria-labelledby="feed-title">
      <div role="tablist" aria-label="Fonte de conteúdo" className="flex gap-2">
        {(Object.keys(SOURCES) as FeedSource[]).map((key) => (
          <button
            key={key}
            role="tab"
            aria-selected={source === key}
            onClick={() => setSource(key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              source === key
                ? "bg-sky-500 text-zinc-950"
                : "border border-white/10 text-zinc-300 hover:border-white/25"
            }`}
          >
            {SOURCES[key].label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 id="feed-title" className="text-xl font-semibold text-zinc-50">
            {config.title}
          </h2>
          <p className="text-sm text-zinc-400">{config.subtitle}</p>
        </div>

        <label className="flex flex-col gap-1 text-xs text-zinc-400">
          {config.selectLabel}
          <select
            value={option}
            onChange={(e) => setOptions((prev) => ({ ...prev, [source]: e.target.value }))}
            className="rounded-lg border border-white/10 bg-zinc-900 px-3 py-2 text-sm text-zinc-100"
          >
            {available ? (
              Object.entries(available).map(([code, label]) => (
                <option key={code} value={code}>
                  {label}
                </option>
              ))
            ) : (
              <option value={option}>{option}</option>
            )}
          </select>
        </label>
      </div>

      {state.status === "loading" && (
        <p className="text-sm text-zinc-400" role="status">
          Buscando conteúdos…
        </p>
      )}

      {state.status === "error" && (
        <p
          className="rounded-lg border border-red-400/30 bg-red-400/5 px-4 py-3 text-sm text-red-300"
          role="alert"
        >
          {state.message}
        </p>
      )}

      {state.status === "ready" && state.data.items.length === 0 && (
        <p className="text-sm text-zinc-400">Nenhum conteúdo encontrado neste tópico.</p>
      )}

      {state.status === "ready" && state.data.items.length > 0 && (
        <>
          <p className="text-xs text-zinc-500">{state.data.note}</p>
          <div className="grid gap-4">
            {state.data.items.map((item) => (
              <FeedCard key={`${item.source}:${item.external_id}`} item={item} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
