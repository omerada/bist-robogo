/**
 * WebSocket hook — piyasa verisi ve bildirim akışı.
 */

"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { useMarketStore } from "@/stores/market-store";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type ConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting";

interface UseWebSocketOptions {
  channels?: string[];
  onMessage?: (channel: string, data: unknown) => void;
  autoConnect?: boolean;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { channels = [], onMessage, autoConnect = true } = options;
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);
  const [state, setState] = useState<ConnectionState>("disconnected");
  const retriesRef = useRef(0);
  const maxRetries = 10;
  const updateQuote = useMarketStore((s) => s.updateQuote);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setState("connecting");
    const ws = new WebSocket(`${WS_URL}/ws/v1/market/stream`);

    ws.onopen = () => {
      setState("connected");
      retriesRef.current = 0;

      // Kanallara abone ol
      if (channels.length > 0) {
        ws.send(JSON.stringify({ action: "subscribe", channels }));
      }

      // Heartbeat başlat (her 30 sn)
      heartbeatRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ action: "ping" }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const { channel, data } = message;

        // Quote güncellemelerini store'a yaz
        if (channel?.startsWith("quote:")) {
          const symbol = channel.replace("quote:", "");
          updateQuote(symbol, data);
        }

        // Callback'i çağır
        onMessage?.(channel, data);
      } catch {
        // JSON parse hatası — yoksay
      }
    };

    ws.onclose = () => {
      setState("disconnected");
      clearInterval(heartbeatRef.current!);

      // Exponential backoff ile reconnect
      if (retriesRef.current < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, retriesRef.current), 30000);
        setState("reconnecting");
        reconnectTimeoutRef.current = setTimeout(() => {
          retriesRef.current++;
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [channels, onMessage, updateQuote]);

  const disconnect = useCallback(() => {
    clearTimeout(reconnectTimeoutRef.current!);
    clearInterval(heartbeatRef.current!);
    wsRef.current?.close();
    wsRef.current = null;
    setState("disconnected");
  }, []);

  const subscribe = useCallback((newChannels: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({ action: "subscribe", channels: newChannels }),
      );
    }
  }, []);

  const unsubscribe = useCallback((removeChannels: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({ action: "unsubscribe", channels: removeChannels }),
      );
    }
  }, []);

  useEffect(() => {
    if (autoConnect) connect();
    return () => disconnect();
  }, [autoConnect, connect, disconnect]);

  return { state, connect, disconnect, subscribe, unsubscribe };
}
