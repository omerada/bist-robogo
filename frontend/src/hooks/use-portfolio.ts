"use client";

import { useQuery } from "@tanstack/react-query";
import apiClient, { type ApiResponse } from "@/lib/api/client";
import type { PortfolioSummary, Position } from "@/types/portfolio";

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ["portfolio", "summary"],
    queryFn: async () => {
      const { data } =
        await apiClient.get<ApiResponse<PortfolioSummary>>(
          "/portfolio/summary",
        );
      return data.data;
    },
    staleTime: 10_000,
    refetchInterval: 30_000,
  });
}

export function usePositions() {
  return useQuery({
    queryKey: ["portfolio", "positions"],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<Position[]>>(
        "/portfolio/positions",
      );
      return data.data;
    },
    staleTime: 10_000,
    refetchInterval: 30_000,
  });
}
