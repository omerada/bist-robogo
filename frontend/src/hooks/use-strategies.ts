/**
 * Strateji Yönetimi TanStack Query hooks.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getStrategies,
  createStrategy,
  getStrategy,
  updateStrategy,
  deleteStrategy,
  activateStrategy,
  deactivateStrategy,
  getStrategySignals,
  getStrategyPerformance,
  type StrategiesParams,
  type SignalsParams,
} from "@/lib/api/strategies";
import type {
  StrategyCreateRequest,
  StrategyUpdateRequest,
} from "@/types/strategy";

// ── Queries ──

export function useStrategies(params?: StrategiesParams) {
  return useQuery({
    queryKey: ["strategies", params],
    queryFn: () => getStrategies(params),
    staleTime: 30_000,
  });
}

export function useStrategy(strategyId: string) {
  return useQuery({
    queryKey: ["strategies", strategyId],
    queryFn: () => getStrategy(strategyId),
    staleTime: 30_000,
    enabled: !!strategyId,
  });
}

export function useStrategySignals(strategyId: string, params?: SignalsParams) {
  return useQuery({
    queryKey: ["strategies", strategyId, "signals", params],
    queryFn: () => getStrategySignals(strategyId, params),
    staleTime: 15_000,
    enabled: !!strategyId,
  });
}

export function useStrategyPerformance(strategyId: string) {
  return useQuery({
    queryKey: ["strategies", strategyId, "performance"],
    queryFn: () => getStrategyPerformance(strategyId),
    staleTime: 60_000,
    enabled: !!strategyId,
  });
}

// ── Mutations ──

export function useCreateStrategy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: StrategyCreateRequest) => createStrategy(req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategies"] });
    },
  });
}

export function useUpdateStrategy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: StrategyUpdateRequest }) =>
      updateStrategy(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["strategies"] });
      queryClient.invalidateQueries({
        queryKey: ["strategies", variables.id],
      });
    },
  });
}

export function useDeleteStrategy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteStrategy(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategies"] });
    },
  });
}

export function useActivateStrategy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => activateStrategy(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["strategies"] });
      queryClient.invalidateQueries({ queryKey: ["strategies", id] });
    },
  });
}

export function useDeactivateStrategy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deactivateStrategy(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["strategies"] });
      queryClient.invalidateQueries({ queryKey: ["strategies", id] });
    },
  });
}
