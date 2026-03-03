/**
 * Risk TanStack Query hooks.
 * // Source: Doc 08 §6 — React hooks pattern
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getRiskStatus,
  listRiskEvents,
  listRiskRules,
  updateRiskRule,
  type RiskEventListParams,
} from "@/lib/api/risk";
import type { RiskRuleUpdate } from "@/types/risk";

// ── Risk Durumu ──

export function useRiskStatus() {
  return useQuery({
    queryKey: ["risk", "status"],
    queryFn: getRiskStatus,
    refetchInterval: 60_000, // 1 dk
  });
}

// ── Risk Kuralları ──

export function useRiskRules() {
  return useQuery({
    queryKey: ["risk", "rules"],
    queryFn: listRiskRules,
  });
}

export function useUpdateRiskRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ruleId, data }: { ruleId: string; data: RiskRuleUpdate }) =>
      updateRiskRule(ruleId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risk"] });
    },
  });
}

// ── Risk Olayları ──

export function useRiskEvents(params?: RiskEventListParams) {
  return useQuery({
    queryKey: ["risk", "events", params],
    queryFn: () => listRiskEvents(params),
  });
}
