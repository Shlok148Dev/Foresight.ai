/**
 * Foresight — useSignals Hook
 * ==============================
 * Data fetching hooks for signals and detections.
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { signalsApi, detectionsApi, searchApi } from "@/lib/api";

/* ── Signals ─────────────────────────────────────────────────── */

export function useSignals(params?: {
  limit?: number;
  offset?: number;
  platform?: string;
}) {
  return useQuery({
    queryKey: ["signals", params],
    queryFn: () => signalsApi.list(params).then((r) => r.data),
    staleTime: 60_000, // 1 minute
    refetchInterval: 120_000, // Auto-refresh every 2 min
  });
}

export function useSignal(id: string) {
  return useQuery({
    queryKey: ["signal", id],
    queryFn: () => signalsApi.get(id).then((r) => r.data),
    enabled: !!id,
  });
}

export function useIngestSignal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: signalsApi.ingest,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["signals"] }),
  });
}

/* ── Detections ──────────────────────────────────────────────── */

export function useDetections(params?: {
  limit?: number;
  offset?: number;
  stage?: string;
  min_confidence?: number;
  sort_by?: string;
}) {
  return useQuery({
    queryKey: ["detections", params],
    queryFn: () => detectionsApi.list(params).then((r) => r.data),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

export function useDetection(id: string) {
  return useQuery({
    queryKey: ["detection", id],
    queryFn: () => detectionsApi.get(id).then((r) => r.data),
    enabled: !!id,
  });
}

export function useStagesSummary() {
  return useQuery({
    queryKey: ["detections", "stages-summary"],
    queryFn: () => detectionsApi.stagesSummary().then((r) => r.data),
    staleTime: 30_000,
  });
}

export function useRunPipeline() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (windowHours?: number) =>
      detectionsApi.runPipeline(windowHours).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["detections"] });
      qc.invalidateQueries({ queryKey: ["signals"] });
    },
  });
}

export function useSearch(query: string, limit?: number) {
  return useQuery({
    queryKey: ["search", query, limit],
    queryFn: () => searchApi.search(query, limit).then((r) => r.data),
    enabled: query.trim().length >= 2,
    staleTime: 10_000,
  });
}

