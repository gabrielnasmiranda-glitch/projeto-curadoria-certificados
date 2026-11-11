import type { ContentPreview } from "@/types/api";

function formatDate(iso: string | null): string | null {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatViews(count: number | null): string | null {
  if (count === null) return null;
  return `${new Intl.NumberFormat("pt-BR").format(count)} visualizações`;
}

export default function FeedCard({ item }: { item: ContentPreview }) {
  const date = formatDate(item.published_at);
  const views = formatViews(item.view_count);
  const authors =
    item.authors.length > 3
      ? `${item.authors.slice(0, 3).join(", ")} e mais ${item.authors.length - 3}`
      : item.authors.join(", ");

  return (
    <article className="flex flex-col gap-3 overflow-hidden rounded-xl border border-white/10 bg-white/[0.03] transition-colors hover:border-white/20">
      {item.thumbnail_url && (
        // eslint-disable-next-line @next/next/no-img-element -- miniaturas externas da fonte
        <img
          src={item.thumbnail_url}
          alt=""
          loading="lazy"
          className="aspect-video w-full object-cover"
        />
      )}

      <div className="flex flex-col gap-3 p-5 pt-2">
        <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-400">
          <span className="rounded-full bg-sky-400/10 px-2.5 py-1 font-medium text-sky-300">
            {item.source}
          </span>
          {item.categories.slice(0, 3).map((c) => (
            <span key={c} className="rounded-full border border-white/10 px-2.5 py-1">
              {c}
            </span>
          ))}
          {date && <span className="ml-auto">{date}</span>}
        </div>

        <h3 className="text-lg font-semibold leading-snug text-zinc-50">{item.title}</h3>

        {(authors || views) && (
          <p className="text-sm text-zinc-400">{[authors, views].filter(Boolean).join(" · ")}</p>
        )}

        {item.summary && (
          <p className="line-clamp-3 text-sm leading-6 text-zinc-300">{item.summary}</p>
        )}

        <div className="mt-1 flex items-center justify-between gap-3">
          <span className="text-xs text-zinc-500">Sem avaliação de IA ainda</span>
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-zinc-950 transition-colors hover:bg-sky-400"
          >
            Abrir original
          </a>
        </div>
      </div>
    </article>
  );
}
