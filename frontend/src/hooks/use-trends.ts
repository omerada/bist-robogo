/**
 * Trend Analiz TanStack Query hooks.
 */
"use client";

import { useQuery } from "@tanstack/react-query";
import { getTrendAnalysis, type TrendAnalysisParams } from "@/lib/api/analysis";

export function useTrendAnalysis(params?: TrendAnalysisParams) {
  return useQuery({
    queryKey: ["trends", params],
    queryFn: () => getTrendAnalysis(params),
    staleTime: 2 * 60_000, // 2 dk — OHLCV verisi sık değişmez
    refetchInterval: 5 * 60_000, // 5 dk
  });
}
