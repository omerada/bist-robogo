/**
 * AI TanStack Query hooks.
 * // Source: Doc 10 §Faz 3 Sprint 3.1 — AI hooks
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  analyzeSymbol,
  getAISettings,
  getAISignals,
  listAIModels,
  sendChatMessage,
  updateAISettings,
} from "@/lib/api/ai";
import type {
  AIAnalysisRequest,
  AIChatRequest,
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
