/**
 * Backtest TanStack Query hooks.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteBacktest,
  getBacktest,
  getBacktestDetail,
  getBacktestTrades,
  getEquityCurve,
  listBacktests,
  runBacktest,
  type BacktestListParams,
} from "@/lib/api/backtest";
import type { BacktestRunRequest } from "@/types/backtest";

// ── Backtest Listesi ──

export function useBacktestList(params?: BacktestListParams) {
  return useQuery({
    queryKey: ["backtests", params],
    queryFn: () => listBacktests(params),
    staleTime: 30_000,
  });
}

// ── Backtest Detay ──

export function useBacktest(backtestId: string | undefined) {
  return useQuery({
    queryKey: ["backtest", backtestId],
    queryFn: () => getBacktest(backtestId!),
    enabled: !!backtestId,
    staleTime: 60_000,
  });
}

// ── Backtest Detay + Trades ──

export function useBacktestDetail(backtestId: string | undefined) {
  return useQuery({
    queryKey: ["backtest-detail", backtestId],
    queryFn: () => getBacktestDetail(backtestId!),
    enabled: !!backtestId,
    staleTime: 60_000,
  });
}

// ── Backtest Trades ──

export function useBacktestTrades(
  backtestId: string | undefined,
  params?: { page?: number; per_page?: number },
) {
  return useQuery({
    queryKey: ["backtest-trades", backtestId, params],
    queryFn: () => getBacktestTrades(backtestId!, params),
    enabled: !!backtestId,
    staleTime: 60_000,
  });
}

// ── Equity Curve ──

export function useEquityCurve(backtestId: string | undefined) {
  return useQuery({
    queryKey: ["equity-curve", backtestId],
    queryFn: () => getEquityCurve(backtestId!),
    enabled: !!backtestId,
    staleTime: 60_000,
  });
}

// ── Backtest Çalıştır (Mutation) ──

export function useRunBacktest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BacktestRunRequest) => runBacktest(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backtests"] });
    },
  });
}

// ── Backtest Sil (Mutation) ──

export function useDeleteBacktest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (backtestId: string) => deleteBacktest(backtestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backtests"] });
    },
  });
}
