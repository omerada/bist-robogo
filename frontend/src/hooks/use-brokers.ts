/**
 * Broker yönetimi TanStack Query hooks.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  createBrokerConnection,
  deleteBrokerConnection,
  getAvailableBrokers,
  getBrokerConnection,
  getBrokerQuote,
  listBrokerConnections,
  testBrokerConnection,
  updateBrokerConnection,
} from "@/lib/api/brokers";
import type {
  BrokerConnectionCreate,
  BrokerConnectionUpdate,
} from "@/types/broker";

// ── Query Keys ──

const brokerKeys = {
  all: ["brokers"] as const,
  info: () => [...brokerKeys.all, "info"] as const,
  connections: () => [...brokerKeys.all, "connections"] as const,
  connection: (id: string) => [...brokerKeys.all, "connection", id] as const,
};

// ── Queries ──

export function useAvailableBrokers() {
  return useQuery({
    queryKey: brokerKeys.info(),
    queryFn: getAvailableBrokers,
    staleTime: 1000 * 60 * 30, // 30 dakika
  });
}

export function useBrokerConnections() {
  return useQuery({
    queryKey: brokerKeys.connections(),
    queryFn: () => listBrokerConnections(),
    staleTime: 1000 * 60 * 2, // 2 dakika
  });
}

export function useBrokerConnection(connectionId: string) {
  return useQuery({
    queryKey: brokerKeys.connection(connectionId),
    queryFn: () => getBrokerConnection(connectionId),
    enabled: !!connectionId,
  });
}

// ── Mutations ──

export function useCreateBrokerConnection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BrokerConnectionCreate) => createBrokerConnection(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: brokerKeys.connections() });
      toast.success("Broker bağlantısı oluşturuldu");
    },
    onError: () => {
      toast.error("Broker bağlantısı oluşturulamadı");
    },
  });
}

export function useUpdateBrokerConnection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BrokerConnectionUpdate }) =>
      updateBrokerConnection(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: brokerKeys.all });
      toast.success("Broker bağlantısı güncellendi");
    },
    onError: () => {
      toast.error("Güncelleme başarısız");
    },
  });
}

export function useDeleteBrokerConnection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteBrokerConnection(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: brokerKeys.connections() });
      toast.success("Broker bağlantısı silindi");
    },
    onError: () => {
      toast.error("Silme başarısız");
    },
  });
}

export function useTestBrokerConnection() {
  return useMutation({
    mutationFn: (id: string) => testBrokerConnection(id),
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Bağlantı başarılı (${data.latency_ms?.toFixed(0)}ms)`);
      } else {
        toast.error(`Bağlantı hatası: ${data.message}`);
      }
    },
    onError: () => {
      toast.error("Bağlantı testi başarısız");
    },
  });
}

export function useBrokerQuote(connectionId: string, symbol: string) {
  return useQuery({
    queryKey: [...brokerKeys.connection(connectionId), "quote", symbol],
    queryFn: () => getBrokerQuote(connectionId, symbol),
    enabled: !!connectionId && !!symbol,
    staleTime: 1000 * 30, // 30 saniye
    refetchInterval: 1000 * 60, // 1 dakika
  });
}
