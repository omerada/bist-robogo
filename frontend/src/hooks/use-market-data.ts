/**
 * Piyasa verisi hook'ları — TanStack Query ile.
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import {
  getSymbols,
  getQuote,
  getHistory,
  getIndices,
  getSectors,
  type SymbolsParams,
} from "@/lib/api/market";

export function useSymbols(params?: SymbolsParams) {
  return useQuery({
    queryKey: ["symbols", params],
    queryFn: () => getSymbols(params),
    staleTime: 5 * 60 * 1000, // 5 dk
  });
}

export function useQuote(symbol: string) {
  return useQuery({
    queryKey: ["quote", symbol],
    queryFn: () => getQuote(symbol),
    enabled: !!symbol,
    staleTime: 10 * 1000, // 10 sn (WebSocket ile de güncellenir)
    refetchInterval: 30 * 1000, // 30 sn'de bir yenile (fallback)
  });
}

export function useHistory(symbol: string, interval: string = "1d") {
  return useQuery({
    queryKey: ["history", symbol, interval],
    queryFn: () => getHistory(symbol, interval),
    enabled: !!symbol,
    staleTime: 60 * 1000, // 1 dk
  });
}

export function useIndices() {
  return useQuery({
    queryKey: ["indices"],
    queryFn: getIndices,
    staleTime: 60 * 60 * 1000, // 1 saat
  });
}

export function useSectors() {
  return useQuery({
    queryKey: ["sectors"],
    queryFn: getSectors,
    staleTime: 60 * 60 * 1000, // 1 saat
  });
}
