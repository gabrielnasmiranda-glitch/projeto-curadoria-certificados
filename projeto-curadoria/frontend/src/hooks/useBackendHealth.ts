"use client";

import { useEffect, useState } from "react";

import { getHealth } from "@/services/api";
import type { HealthResponse } from "@/types/api";

export type BackendHealthState =
  | { status: "loading" }
  | { status: "online"; data: HealthResponse }
  | { status: "offline"; message: string };

export function useBackendHealth(): BackendHealthState {
  const [state, setState] = useState<BackendHealthState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const data = await getHealth();
        if (!cancelled) setState({ status: "online", data });
      } catch (error) {
        const message = error instanceof Error ? error.message : "Erro desconhecido";
        if (!cancelled) setState({ status: "offline", message });
      }
    }

    void check();
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
