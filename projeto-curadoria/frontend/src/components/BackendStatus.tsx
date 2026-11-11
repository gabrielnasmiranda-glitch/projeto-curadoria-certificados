"use client";

import { useBackendHealth } from "@/hooks/useBackendHealth";

export default function BackendStatus() {
  const state = useBackendHealth();

  const styles = {
    loading: "bg-zinc-500",
    online: "bg-emerald-400",
    offline: "bg-red-400",
  } as const;

  return (
    <div
      className="inline-flex items-center gap-3 rounded-lg border border-white/10 bg-white/[0.03] px-4 py-3 text-sm"
      role="status"
      aria-live="polite"
    >
      <span className={`h-2.5 w-2.5 rounded-full ${styles[state.status]}`} aria-hidden />
      {state.status === "loading" && <span>Verificando conexão com a API…</span>}
      {state.status === "online" && (
        <span>
          API online · ambiente <strong>{state.data.environment}</strong>
        </span>
      )}
      {state.status === "offline" && <span>API indisponível: {state.message}</span>}
    </div>
  );
}
