/**
 * Trading & Portfolio TanStack Query hooks.
 */
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getPortfolioSummary,
  getPositions,
  getPortfolioHistory,
  getOrders,
  createOrder,
  cancelOrder,
  type OrdersParams,
} from "@/lib/api/trading";
import type { OrderCreateRequest } from "@/types/order";

// ── Portfolio ──

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ["portfolio", "summary"],
    queryFn: getPortfolioSummary,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

export function usePositions() {
  return useQuery({
    queryKey: ["portfolio", "positions"],
    queryFn: getPositions,
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function usePortfolioHistory(limit: number = 30) {
  return useQuery({
    queryKey: ["portfolio", "history", limit],
    queryFn: () => getPortfolioHistory(limit),
    staleTime: 5 * 60_000,
  });
}

// ── Orders ──

export function useOrders(params?: OrdersParams) {
  return useQuery({
    queryKey: ["orders", params],
    queryFn: () => getOrders(params),
    staleTime: 10_000,
  });
}

// ── Mutations ──

export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (req: OrderCreateRequest) => createOrder(req),
    onSuccess: () => {
      // Emirler ve portföy verilerini invalide et
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
    },
  });
}

export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => cancelOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
    },
  });
}
