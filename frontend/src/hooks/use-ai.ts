/**
 * AI TanStack Query hooks.
 * // Source: Doc 10 §Faz 3 Sprint 3.1 + 3.3 — AI hooks
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  analyzeSymbol,
  compareModels,
  createExperiment,
  deleteExperiment,
  getAIPerformance,
  getAISettings,
  getAISignals,
  getExperiment,
  listAIModels,
  listExperiments,
  runExperiment,
  sendChatMessage,
  updateAISettings,
} from "@/lib/api/ai";
import type {
  AIAnalysisRequest,
  AIChatRequest,
  AIExperimentCreate,
  AISettingsRequest,
} from "@/types/ai";

// ── Analiz ──

export function useAIAnalysis() {
  return useMutation({
    mutationFn: (request: AIAnalysisRequest) => analyzeSymbol(request),
  });
}

// ── Sohbet ──

export function useAIChat() {
  return useMutation({
    mutationFn: (request: AIChatRequest) => sendChatMessage(request),
  });
}

// ── Sinyaller ──

export function useAISignals(limit?: number) {
  return useQuery({
    queryKey: ["ai", "signals", limit],
    queryFn: () => getAISignals(limit),
    refetchInterval: 5 * 60_000, // 5 dk
    enabled: true,
  });
}

// ── Modeller ──

export function useAIModels() {
  return useQuery({
    queryKey: ["ai", "models"],
    queryFn: listAIModels,
    staleTime: 30 * 60_000, // 30 dk cache
  });
}

// ── Ayarlar ──

export function useAISettings() {
  return useQuery({
    queryKey: ["ai", "settings"],
    queryFn: getAISettings,
  });
}

export function useUpdateAISettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: AISettingsRequest) => updateAISettings(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "settings"] });
    },
  });
}

// ── A/B Test Deneyleri ──

export function useExperiments(params?: {
  status?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["ai", "experiments", params],
    queryFn: () => listExperiments(params),
  });
}

export function useExperiment(experimentId: string) {
  return useQuery({
    queryKey: ["ai", "experiments", experimentId],
    queryFn: () => getExperiment(experimentId),
    enabled: !!experimentId,
  });
}

export function useCreateExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: AIExperimentCreate) => createExperiment(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "experiments"] });
    },
  });
}

export function useRunExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => runExperiment(experimentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "experiments"] });
    },
  });
}

export function useDeleteExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => deleteExperiment(experimentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "experiments"] });
    },
  });
}

// ── Performans ──

export function useAIPerformance(params?: {
  model_id?: string;
  symbol?: string;
  days?: number;
}) {
  return useQuery({
    queryKey: ["ai", "performance", params],
    queryFn: () => getAIPerformance(params),
    staleTime: 5 * 60_000,
  });
}

export function useModelComparison(
  modelA: string,
  modelB: string,
  days?: number,
) {
  return useQuery({
    queryKey: ["ai", "performance", "compare", modelA, modelB, days],
    queryFn: () => compareModels(modelA, modelB, days),
    enabled: !!modelA && !!modelB,
    staleTime: 5 * 60_000,
  });
}
