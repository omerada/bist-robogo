/**
 * Dashboard hooks — TanStack Query ile veri yönetimi.
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import {
  getDashboardSummary,
  getLivePrices,
  getLiveIndices,
  type DashboardSummary,
  type LivePriceData,
  type LiveIndexData,
} from "@/lib/api/dashboard";

export const dashboardKeys = {
  all: ["dashboard"] as const,
  summary: () => [...dashboardKeys.all, "summary"] as const,
  livePrices: (symbols?: string[]) =>
    [...dashboardKeys.all, "live-prices", symbols] as const,
  liveIndices: () => [...dashboardKeys.all, "live-indices"] as const,
};

export function useDashboardSummary() {
  return useQuery<DashboardSummary>({
    queryKey: dashboardKeys.summary(),
    queryFn: getDashboardSummary,
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useLivePrices(symbols?: string[]) {
  return useQuery<LivePriceData[]>({
    queryKey: dashboardKeys.livePrices(symbols),
    queryFn: () => getLivePrices(symbols),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

export function useLiveIndices() {
  return useQuery<LiveIndexData[]>({
    queryKey: dashboardKeys.liveIndices(),
    queryFn: getLiveIndices,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}
