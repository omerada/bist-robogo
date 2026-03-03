# bist-robogo — Frontend Implementasyon Kılavuzu

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Amaç:** AI Agent'ın frontend'i component component, sayfa sayfa sıfır hata ile geliştirebilmesi.

---

## 1. Proje Kurulumu

### 1.1 Başlatma Komutları

```bash
# Next.js 15 projesi oluştur
pnpm create next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd frontend

# shadcn/ui kur
pnpm dlx shadcn@latest init

# Temel bağımlılıkları ekle
pnpm add @tanstack/react-query@^5.62 zustand@^5.0 socket.io-client@^4.8
pnpm add lightweight-charts@^4.2 recharts@^2.15 @tremor/react@^3.18
pnpm add axios@^1.7 zod@^3.24 react-hook-form@^7.54 @hookform/resolvers@^3.9
pnpm add date-fns@^4.1 clsx@^2.1 tailwind-merge@^2.6 class-variance-authority@^0.7
pnpm add lucide-react@^0.468 next-themes@^0.4
pnpm add nuqs@^2.0  # URL state management

# Dev bağımlılıklar
pnpm add -D vitest@^2.1 @testing-library/react@^16.1 @testing-library/jest-dom@^6.6
pnpm add -D playwright@^1.49 prettier@^3.4 prettier-plugin-tailwindcss@^0.6
```

### 1.2 shadcn/ui Component Kurulumu

```bash
# Gerekli shadcn/ui bileşenlerini ekle (tümü)
pnpm dlx shadcn@latest add button card input label select textarea
pnpm dlx shadcn@latest add dialog sheet dropdown-menu popover tooltip
pnpm dlx shadcn@latest add table tabs badge separator
pnpm dlx shadcn@latest add progress slider switch checkbox
pnpm dlx shadcn@latest add alert toast sonner
pnpm dlx shadcn@latest add avatar skeleton scroll-area
pnpm dlx shadcn@latest add command form navigation-menu
pnpm dlx shadcn@latest add collapsible accordion
```

---

## 2. Yapılandırma Dosyaları

### 2.1 next.config.ts

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Strict mode
  reactStrictMode: true,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.bist-robogo.com",
      },
    ],
  },

  // Environment variables (client-side erişim)
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000",
  },

  // Experimental features
  experimental: {
    optimizePackageImports: [
      "lucide-react",
      "recharts",
      "@tremor/react",
      "date-fns",
    ],
  },

  // Headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
```

### 2.2 tailwind.config.ts

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/**/*.{ts,tsx}",
    "./node_modules/@tremor/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // ── Renkler (CSS variable referansları) ──
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Finans özel renkleri
        profit: "hsl(var(--profit))",
        loss: "hsl(var(--loss))",
        warning: "hsl(var(--warning))",
        // Grafik renkleri
        chart: {
          1: "hsl(var(--chart-1))",
          2: "hsl(var(--chart-2))",
          3: "hsl(var(--chart-3))",
          4: "hsl(var(--chart-4))",
          5: "hsl(var(--chart-5))",
        },
      },
      // ── Tipografi ──
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }], // 10px
      },
      // ── Border Radius ──
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      // ── Animasyonlar ──
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        "price-flash-up": {
          "0%": { backgroundColor: "hsl(var(--profit) / 0.3)" },
          "100%": { backgroundColor: "transparent" },
        },
        "price-flash-down": {
          "0%": { backgroundColor: "hsl(var(--loss) / 0.3)" },
          "100%": { backgroundColor: "transparent" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
        "price-flash-up": "price-flash-up 0.8s ease-out",
        "price-flash-down": "price-flash-down 0.8s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

### 2.3 src/app/globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* ── Light Tema ── */
  :root {
    --background: 0 0% 100%;
    --foreground: 224 71% 4%;
    --card: 0 0% 100%;
    --card-foreground: 224 71% 4%;
    --popover: 0 0% 100%;
    --popover-foreground: 224 71% 4%;
    --primary: 220 70% 50%;
    --primary-foreground: 210 40% 98%;
    --secondary: 220 14% 96%;
    --secondary-foreground: 220 9% 46%;
    --muted: 220 14% 96%;
    --muted-foreground: 220 9% 46%;
    --accent: 220 14% 96%;
    --accent-foreground: 220 9% 15%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 210 40% 98%;
    --border: 220 13% 91%;
    --input: 220 13% 91%;
    --ring: 220 70% 50%;
    --radius: 0.625rem;

    /* Finans renkleri — Light */
    --profit: 142 72% 40%;
    --loss: 0 84% 55%;
    --warning: 38 92% 50%;

    /* Grafik renkleri */
    --chart-1: 220 70% 50%;
    --chart-2: 160 60% 45%;
    --chart-3: 30 80% 55%;
    --chart-4: 280 65% 60%;
    --chart-5: 340 75% 55%;
  }

  /* ── Dark Tema (Varsayılan) ── */
  .dark {
    --background: 224 71% 4%;
    --foreground: 210 20% 98%;
    --card: 224 71% 6%;
    --card-foreground: 210 20% 98%;
    --popover: 224 71% 6%;
    --popover-foreground: 210 20% 98%;
    --primary: 217 91% 60%;
    --primary-foreground: 222 47% 11%;
    --secondary: 217 33% 17%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 65%;
    --accent: 217 33% 17%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 63% 55%;
    --destructive-foreground: 210 40% 98%;
    --border: 217 33% 17%;
    --input: 217 33% 17%;
    --ring: 224 76% 48%;
    --radius: 0.625rem;

    /* Finans renkleri — Dark */
    --profit: 142 72% 45%;
    --loss: 0 84% 60%;
    --warning: 38 92% 55%;

    /* Grafik renkleri */
    --chart-1: 220 70% 60%;
    --chart-2: 160 60% 50%;
    --chart-3: 30 80% 60%;
    --chart-4: 280 65% 65%;
    --chart-5: 340 75% 60%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground antialiased;
    font-feature-settings:
      "rlig" 1,
      "calt" 1;
  }

  /* Tabular nums — finansal verilerde hizalama */
  .tabular-nums {
    font-variant-numeric: tabular-nums;
    font-feature-settings: "tnum";
  }
}

@layer utilities {
  /* Scrollbar stilleri — minimal ve şık */
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: hsl(var(--muted)) transparent;
  }
  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  .scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
  }
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background-color: hsl(var(--muted));
    border-radius: 3px;
  }
}
```

---

## 3. API Client

### 3.1 src/lib/api/client.ts

```typescript
/**
 * Axios API client — interceptor'lar ile merkezi HTTP istemci.
 *
 * Özellikler:
 * - Base URL yapılandırması
 * - Token ekleme (Authorization header)
 * - 401'de otomatik token refresh
 * - Standart hata dönüştürme
 * - Request/response loglama (development)
 */

import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── API Error tipi ──
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: ApiError;
  meta?: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

// ── Token yönetimi ──
let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

// ── Axios Instance ──
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // httpOnly cookie'ler için
});

// ── Request Interceptor: Token ekle ──
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response Interceptor: Hata dönüştürme + Token refresh ──
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ error?: ApiError }>) => {
    const originalRequest = error.config;

    // 401 → Token refresh dene
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return apiClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await axios.post(
          `${API_URL}/api/v1/auth/refresh`,
          {},
          { withCredentials: true },
        );
        const newToken = response.data.data.access_token;
        setAccessToken(newToken);
        processQueue(null, newToken);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        setAccessToken(null);
        // Login sayfasına yönlendir
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Standart hata dönüştürme
    const apiError: ApiError = error.response?.data?.error || {
      code: "NETWORK_ERROR",
      message: error.message || "Bağlantı hatası",
    };

    return Promise.reject(apiError);
  },
);

// AxiosRequestConfig tip genişletmesi
declare module "axios" {
  export interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

export default apiClient;
```

### 3.2 src/lib/api/market.ts

```typescript
/**
 * Piyasa verisi API fonksiyonları.
 */

import apiClient, { type ApiResponse } from "./client";
import type { Quote, OHLCV, SymbolInfo } from "@/types/market";

export async function getSymbols(index?: string): Promise<SymbolInfo[]> {
  const params = index ? { index } : {};
  const { data } = await apiClient.get<ApiResponse<SymbolInfo[]>>(
    "/market/symbols",
    { params },
  );
  return data.data;
}

export async function getQuote(symbol: string): Promise<Quote> {
  const { data } = await apiClient.get<ApiResponse<Quote>>(
    `/market/symbols/${symbol}/quote`,
  );
  return data.data;
}

export async function getHistory(
  symbol: string,
  interval: string = "1d",
  start?: string,
  end?: string,
  limit?: number,
): Promise<OHLCV[]> {
  const { data } = await apiClient.get<ApiResponse<OHLCV[]>>(
    `/market/symbols/${symbol}/history`,
    { params: { interval, start, end, limit } },
  );
  return data.data;
}

export async function getIndices() {
  const { data } =
    await apiClient.get<ApiResponse<Array<{ code: string; name: string }>>>(
      "/market/indices",
    );
  return data.data;
}
```

### 3.3 src/lib/api/orders.ts

```typescript
/**
 * Emir API fonksiyonları.
 */

import apiClient, { type ApiResponse } from "./client";
import type { OrderCreateRequest, Order } from "@/types/order";

export async function createOrder(order: OrderCreateRequest): Promise<Order> {
  const { data } = await apiClient.post<ApiResponse<Order>>("/orders", order);
  return data.data;
}

export async function getOrders(params?: {
  status?: string;
  symbol?: string;
  page?: number;
  per_page?: number;
}): Promise<{ orders: Order[]; total: number }> {
  const { data } = await apiClient.get<ApiResponse<Order[]>>("/orders", {
    params,
  });
  return { orders: data.data, total: data.meta?.total || 0 };
}

export async function cancelOrder(orderId: string): Promise<void> {
  await apiClient.delete(`/orders/${orderId}`);
}
```

---

## 4. TypeScript Tip Tanımları

### 4.1 src/types/market.ts

```typescript
export interface SymbolInfo {
  id: string;
  ticker: string;
  name: string;
  sector: string;
  industry?: string;
  is_active: boolean;
}

export interface Quote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
  open: number;
  high: number;
  low: number;
  close_prev: number;
  volume: number;
  bid: number;
  ask: number;
  bid_size: number;
  ask_size: number;
  market_cap?: number;
  pe_ratio?: number;
  updated_at: string;
}

export interface OHLCV {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OrderBookEntry {
  price: number;
  quantity: number;
}

export interface OrderBook {
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
  timestamp: string;
}
```

### 4.2 src/types/order.ts

```typescript
export type OrderSide = "buy" | "sell";
export type OrderType =
  | "market"
  | "limit"
  | "stop_loss"
  | "take_profit"
  | "trailing_stop";
export type OrderStatus =
  | "pending"
  | "submitted"
  | "partial_fill"
  | "filled"
  | "cancelled"
  | "rejected"
  | "expired";
export type TimeInForce = "day" | "gtc" | "ioc" | "fok";

export interface OrderCreateRequest {
  symbol: string;
  side: OrderSide;
  order_type: OrderType;
  quantity: number;
  price?: number;
  stop_loss?: number;
  take_profit?: number;
  time_in_force?: TimeInForce;
  strategy_id?: string;
}

export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  order_type: OrderType;
  quantity: number;
  price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  status: OrderStatus;
  filled_quantity: number;
  filled_price: number | null;
  commission: number;
  is_paper: boolean;
  created_at: string;
  updated_at: string;
}
```

### 4.3 src/types/portfolio.ts

```typescript
export interface PortfolioSummary {
  total_value: number;
  cash_balance: number;
  invested_value: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
  winning_positions: number;
  losing_positions: number;
}

export interface Position {
  id: string;
  symbol: string;
  side: "long" | "short";
  quantity: number;
  avg_entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  realized_pnl: number;
  stop_loss: number | null;
  take_profit: number | null;
  strategy_id: string | null;
  opened_at: string;
}
```

### 4.4 src/types/strategy.ts

```typescript
export interface Strategy {
  id: string;
  name: string;
  description: string | null;
  strategy_type: string;
  parameters: Record<string, unknown>;
  symbols: string[];
  index_filter: string | null;
  timeframe: string;
  is_active: boolean;
  is_paper: boolean;
  created_at: string;
  updated_at: string;
}

export interface Signal {
  id: string;
  strategy_id: string;
  symbol: string;
  signal_type: "buy" | "sell" | "hold";
  confidence: number;
  price: number;
  stop_loss: number | null;
  take_profit: number | null;
  indicators: Record<string, number>;
  created_at: string;
}

export interface TrendCandidate {
  symbol: string;
  name: string;
  price: number;
  score: number;
  trend_status: string;
  rsi: number | null;
  volume_ratio: number | null;
  support_level?: number;
  resistance_level?: number;
  breakout_level?: number;
  target_price?: number;
  macd_signal?: string;
  indicators: Record<string, number>;
}
```

---

## 5. Zustand Stores

### 5.1 src/stores/auth-store.ts

```typescript
/**
 * Auth store — kullanıcı oturumu yönetimi.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { setAccessToken } from "@/lib/api/client";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User, token: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,

      setUser: (user, token) => {
        setAccessToken(token);
        set({ user, isAuthenticated: true, isLoading: false });
      },

      logout: () => {
        setAccessToken(null);
        set({ user: null, isAuthenticated: false, isLoading: false });
      },

      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
```

### 5.2 src/stores/market-store.ts

```typescript
/**
 * Market store — gerçek zamanlı piyasa verisi.
 */

import { create } from "zustand";
import type { Quote } from "@/types/market";

interface MarketState {
  // symbol → Quote map
  quotes: Record<string, Quote>;
  // Seçili sembol
  selectedSymbol: string | null;
  // Seçili endeks filtresi
  selectedIndex: string;

  // Actions
  updateQuote: (symbol: string, quote: Partial<Quote>) => void;
  setSelectedSymbol: (symbol: string | null) => void;
  setSelectedIndex: (index: string) => void;
  setBulkQuotes: (quotes: Record<string, Quote>) => void;
}

export const useMarketStore = create<MarketState>()((set) => ({
  quotes: {},
  selectedSymbol: null,
  selectedIndex: "XU030",

  updateQuote: (symbol, quoteUpdate) =>
    set((state) => ({
      quotes: {
        ...state.quotes,
        [symbol]: { ...state.quotes[symbol], ...quoteUpdate } as Quote,
      },
    })),

  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setSelectedIndex: (index) => set({ selectedIndex: index }),

  setBulkQuotes: (quotes) =>
    set((state) => ({
      quotes: { ...state.quotes, ...quotes },
    })),
}));
```

### 5.3 src/stores/ui-store.ts

```typescript
/**
 * UI store — sidebar, modal, genel UI durumu.
 */

import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebarCollapse: () => void;
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarOpen: true,
  sidebarCollapsed: false,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebarCollapse: () =>
    set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
}));
```

---

## 6. Custom Hooks

### 6.1 src/hooks/use-websocket.ts

```typescript
/**
 * WebSocket hook — piyasa verisi ve bildirim akışı.
 *
 * Özellikler:
 * - Otomatik bağlanma / reconnect
 * - Heartbeat (ping/pong)
 * - Channel subscribe/unsubscribe
 * - Connection state yönetimi
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
```

### 6.2 src/hooks/use-market-data.ts

```typescript
/**
 * Piyasa verisi hook'ları — TanStack Query ile.
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import { getSymbols, getQuote, getHistory, getIndices } from "@/lib/api/market";

export function useSymbols(index?: string) {
  return useQuery({
    queryKey: ["symbols", index],
    queryFn: () => getSymbols(index),
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
```

### 6.3 src/hooks/use-portfolio.ts

```typescript
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
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
```

---

## 7. Layout Bileşenleri

### 7.1 src/app/layout.tsx — Root Layout

```tsx
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "bist-robogo — AI Trading Platform",
    template: "%s | bist-robogo",
  },
  description: "BIST İçin AI Destekli Otomatik Ticaret Platformu",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>
            {children}
            <Toaster richColors position="top-right" />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### 7.2 src/components/providers/theme-provider.tsx

```tsx
"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ThemeProviderProps } from "next-themes";

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

### 7.3 src/components/providers/query-provider.tsx

```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000, // 30 sn
            gcTime: 5 * 60_000, // 5 dk (eski cacheTime)
            retry: 2,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 1,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
```

### 7.4 src/app/(dashboard)/layout.tsx — Dashboard Layout

```tsx
/**
 * Dashboard layout — sidebar + header + content alanı.
 * Tüm dashboard sayfaları bu layout'u paylaşır.
 */

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { AuthGuard } from "@/components/auth/auth-guard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-6 scrollbar-thin">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
```

### 7.5 src/components/layout/sidebar.tsx

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  LineChart,
  TrendingUp,
  Layers,
  FlaskConical,
  Briefcase,
  ClipboardList,
  Settings,
  ChevronLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/market", label: "Piyasa", icon: LineChart },
  { href: "/trends", label: "Trend Analiz", icon: TrendingUp },
  { href: "/strategies", label: "Stratejiler", icon: Layers },
  { href: "/backtest", label: "Backtest", icon: FlaskConical },
  { href: "/portfolio", label: "Portföy", icon: Briefcase },
  { href: "/orders", label: "Emirler", icon: ClipboardList },
  { href: "/settings", label: "Ayarlar", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebarCollapse } = useUIStore();

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "relative flex h-full flex-col border-r border-border bg-card transition-all duration-300",
          sidebarCollapsed ? "w-16" : "w-60",
        )}
      >
        {/* Logo */}
        <div className="flex h-14 items-center gap-2 border-b border-border px-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            B
          </div>
          {!sidebarCollapsed && (
            <span className="text-lg font-semibold tracking-tight">
              bist-robogo
            </span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            const link = (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </Link>
            );

            if (sidebarCollapsed) {
              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>{link}</TooltipTrigger>
                  <TooltipContent side="right">{item.label}</TooltipContent>
                </Tooltip>
              );
            }

            return link;
          })}
        </nav>

        {/* Collapse button */}
        <div className="border-t border-border p-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebarCollapse}
            className="w-full justify-center"
          >
            <ChevronLeft
              className={cn(
                "h-4 w-4 transition-transform",
                sidebarCollapsed && "rotate-180",
              )}
            />
          </Button>
        </div>
      </aside>
    </TooltipProvider>
  );
}
```

### 7.6 src/components/layout/header.tsx

```tsx
"use client";

import { Bell, Moon, Sun, Search, Menu } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/stores/auth-store";
import { useUIStore } from "@/stores/ui-store";

export function Header() {
  const { theme, setTheme } = useTheme();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const { toggleSidebar } = useUIStore();

  const initials =
    user?.full_name
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2) || "??";

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4">
      {/* Sol: Hamburger + Arama */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={toggleSidebar}
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div className="relative hidden md:block">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Sembol ara... (ör: THYAO)"
            className="w-64 pl-8 bg-secondary/50"
          />
        </div>
      </div>

      {/* Sağ: Tema + Bildirim + Profil */}
      <div className="flex items-center gap-2">
        {/* Tema değiştir */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Tema değiştir</span>
        </Button>

        {/* Bildirimler */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] text-white">
            3
          </span>
        </Button>

        {/* Profil */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Avatar className="h-8 w-8 cursor-pointer">
              <AvatarFallback className="bg-primary/10 text-primary text-xs font-medium">
                {initials}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem
              className="text-xs text-muted-foreground"
              disabled
            >
              {user?.email}
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <a href="/settings">Ayarlar</a>
            </DropdownMenuItem>
            <DropdownMenuItem className="text-destructive" onClick={logout}>
              Çıkış Yap
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
```

---

## 8. Dashboard Bileşenleri

### 8.1 src/components/dashboard/stat-card.tsx

```tsx
/**
 * Dashboard üst kısımda gösterilen istatistik kartı.
 * Portföy değeri, günlük PnL, toplam PnL, açık pozisyon, aktif strateji gösterir.
 */

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  subtitle?: string;
  icon?: LucideIcon;
}

export function StatCard({
  title,
  value,
  change,
  changeType = "neutral",
  subtitle,
  icon: Icon,
}: StatCardProps) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {title}
          </p>
          {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
        </div>
        <div className="mt-2">
          <p className="text-2xl font-bold tabular-nums">{value}</p>
          <div className="mt-1 flex items-center gap-2">
            {change && (
              <span
                className={cn(
                  "text-xs font-medium tabular-nums",
                  changeType === "positive" && "text-profit",
                  changeType === "negative" && "text-loss",
                  changeType === "neutral" && "text-muted-foreground",
                )}
              >
                {change}
              </span>
            )}
            {subtitle && (
              <span className="text-xs text-muted-foreground">{subtitle}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 8.2 src/app/(dashboard)/dashboard/page.tsx — Dashboard Sayfası

```tsx
/**
 * Dashboard sayfası — tüm kritik bilgilerin tek bakışta görüldüğü ana ekran.
 *
 * Bölümler:
 * 1. Üst: 5 istatistik kartı (portföy, günlük PnL, toplam PnL, pozisyonlar, stratejiler)
 * 2. Orta sol: Portföy equity curve grafiği
 * 3. Orta sağ: Pozisyon dağılımı (pie chart)
 * 4. Alt sol: Son sinyaller tablosu
 * 5. Alt sağ: Risk durumu gauge
 * 6. En alt: Son emirler tablosu
 */

import type { Metadata } from "next";
import { Suspense } from "react";
import { DashboardStats } from "./_components/dashboard-stats";
import { EquityCurve } from "./_components/equity-curve";
import { AllocationChart } from "./_components/allocation-chart";
import { RecentSignals } from "./_components/recent-signals";
import { RiskStatus } from "./_components/risk-status";
import { RecentOrders } from "./_components/recent-orders";
import { Skeleton } from "@/components/ui/skeleton";

export const metadata: Metadata = {
  title: "Dashboard",
};

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Üst: İstatistik Kartları */}
      <Suspense fallback={<StatsLoading />}>
        <DashboardStats />
      </Suspense>

      {/* Orta: Equity Curve + Allocation */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Suspense fallback={<ChartLoading />}>
            <EquityCurve />
          </Suspense>
        </div>
        <div>
          <Suspense fallback={<ChartLoading />}>
            <AllocationChart />
          </Suspense>
        </div>
      </div>

      {/* Alt: Sinyaller + Risk */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Suspense fallback={<TableLoading />}>
            <RecentSignals />
          </Suspense>
        </div>
        <div>
          <Suspense fallback={<ChartLoading />}>
            <RiskStatus />
          </Suspense>
        </div>
      </div>

      {/* En Alt: Son Emirler */}
      <Suspense fallback={<TableLoading />}>
        <RecentOrders />
      </Suspense>
    </div>
  );
}

// ── Loading Skeleton'ları ──
function StatsLoading() {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-24 rounded-lg" />
      ))}
    </div>
  );
}

function ChartLoading() {
  return <Skeleton className="h-72 rounded-lg" />;
}

function TableLoading() {
  return <Skeleton className="h-48 rounded-lg" />;
}
```

---

## 9. TradingView Chart Entegrasyonu

### 9.1 src/components/charts/candlestick-chart.tsx

```tsx
/**
 * TradingView Lightweight Charts entegrasyonu — mum grafiği.
 *
 * Props:
 * - symbol: Gösterilecek sembol
 * - interval: Zaman dilimi (1d, 1h, vb.)
 * - height: Chart yüksekliği (px)
 *
 * Özellikler:
 * - Responsive
 * - Dark/Light tema uyumlu
 * - WebSocket ile gerçek zamanlı güncelleme
 * - Volume alt chart
 */

"use client";

import { useEffect, useRef, useMemo } from "react";
import { useTheme } from "next-themes";
import {
  createChart,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type HistogramData,
  ColorType,
} from "lightweight-charts";
import { useHistory } from "@/hooks/use-market-data";
import { useMarketStore } from "@/stores/market-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface CandlestickChartProps {
  symbol: string;
  interval?: string;
  height?: number;
}

export function CandlestickChart({
  symbol,
  interval = "1d",
  height = 400,
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { data: history, isLoading } = useHistory(symbol, interval);
  const quote = useMarketStore((s) => s.quotes[symbol]);

  // ── Tema renkleri ──
  const chartColors = useMemo(
    () => ({
      backgroundColor: isDark ? "hsl(224, 71%, 4%)" : "hsl(0, 0%, 100%)",
      textColor: isDark ? "hsl(215, 20%, 65%)" : "hsl(220, 9%, 46%)",
      gridColor: isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.04)",
      upColor: isDark ? "#22c55e" : "#16a34a",
      downColor: isDark ? "#ef4444" : "#dc2626",
      borderUpColor: isDark ? "#22c55e" : "#16a34a",
      borderDownColor: isDark ? "#ef4444" : "#dc2626",
      wickUpColor: isDark ? "#22c55e" : "#16a34a",
      wickDownColor: isDark ? "#ef4444" : "#dc2626",
    }),
    [isDark],
  );

  // ── Chart oluştur ──
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: {
          type: ColorType.Solid,
          color: chartColors.backgroundColor,
        },
        textColor: chartColors.textColor,
        fontFamily: "Inter, system-ui, sans-serif",
      },
      grid: {
        vertLines: { color: chartColors.gridColor },
        horzLines: { color: chartColors.gridColor },
      },
      width: chartContainerRef.current.clientWidth,
      height,
      crosshair: {
        mode: 0, // Normal
      },
      rightPriceScale: {
        borderColor: chartColors.gridColor,
      },
      timeScale: {
        borderColor: chartColors.gridColor,
        timeVisible: true,
      },
    });

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: chartColors.upColor,
      downColor: chartColors.downColor,
      borderUpColor: chartColors.borderUpColor,
      borderDownColor: chartColors.borderDownColor,
      wickUpColor: chartColors.wickUpColor,
      wickDownColor: chartColors.wickDownColor,
    });

    // Volume series (alt grafik)
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    // Responsive
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        chart.applyOptions({ width: entry.contentRect.width });
      }
    });
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [chartColors, height]);

  // ── Veri yükle ──
  useEffect(() => {
    if (!history || !candleSeriesRef.current || !volumeSeriesRef.current)
      return;

    const candleData: CandlestickData[] = history.map((d) => ({
      time: d.time.split("T")[0] as string,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    const volumeData: HistogramData[] = history.map((d) => ({
      time: d.time.split("T")[0] as string,
      value: d.volume,
      color:
        d.close >= d.open
          ? chartColors.upColor + "80"
          : chartColors.downColor + "80",
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);
    chartRef.current?.timeScale().fitContent();
  }, [history, chartColors]);

  // ── Gerçek zamanlı güncelleme ──
  useEffect(() => {
    if (!quote || !candleSeriesRef.current) return;

    const today = new Date().toISOString().split("T")[0];
    candleSeriesRef.current.update({
      time: today as string,
      open: quote.open,
      high: quote.high,
      low: quote.low,
      close: quote.price,
    });
  }, [quote]);

  if (isLoading) {
    return <Skeleton className="w-full" style={{ height }} />;
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">
          {symbol} — {interval} Grafik
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div ref={chartContainerRef} />
      </CardContent>
    </Card>
  );
}
```

---

## 10. Yardımcı Fonksiyonlar

### 10.1 src/lib/utils.ts

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 10.2 src/lib/utils/formatters.ts

```typescript
/**
 * Para, sayı, tarih formatlama — tutarlı ve yerelleştirilmiş.
 */

const currencyFormatter = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const compactFormatter = new Intl.NumberFormat("tr-TR", {
  notation: "compact",
  compactDisplay: "short",
  maximumFractionDigits: 1,
});

const percentFormatter = new Intl.NumberFormat("tr-TR", {
  style: "percent",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  signDisplay: "always",
});

const dateFormatter = new Intl.DateTimeFormat("tr-TR", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

/** ₺1.250.000,00 */
export function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

/** 45,2M veya 1,2B */
export function formatCompact(value: number): string {
  return compactFormatter.format(value);
}

/** +2,50% veya -1,30% */
export function formatPercent(value: number): string {
  return percentFormatter.format(value / 100);
}

/** 03.03.2026 15:30 */
export function formatDate(dateStr: string): string {
  return dateFormatter.format(new Date(dateStr));
}

/** Kısa tarih: 03.03 15:30 */
export function formatShortDateTime(dateStr: string): string {
  const d = new Date(dateStr);
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  return `${day}.${month} ${hours}:${minutes}`;
}

/** PnL renk sınıfı: text-profit veya text-loss */
export function pnlColorClass(value: number): string {
  if (value > 0) return "text-profit";
  if (value < 0) return "text-loss";
  return "text-muted-foreground";
}

/** PnL prefix: +12.500 veya -3.200 */
export function formatPnl(value: number): string {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${currencyFormatter.format(value)}`;
}
```

---

## 11. Auth Guard

### 11.1 src/components/auth/auth-guard.tsx

```tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { Skeleton } from "@/components/ui/skeleton";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="space-y-4 text-center">
          <Skeleton className="mx-auto h-12 w-12 rounded-full" />
          <Skeleton className="mx-auto h-4 w-32" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return <>{children}</>;
}
```

---

## 12. Geliştirme Sırası (Frontend)

AI Agent frontend'i aşağıdaki sırada geliştirmelidir:

### Faz 0 — Proje İskeleti:

1. `pnpm create next-app` → Proje oluştur
2. `pnpm dlx shadcn@latest init` → shadcn/ui kur
3. `globals.css` → CSS tokens (dark/light)
4. `tailwind.config.ts` → Custom theme
5. `next.config.ts` → Yapılandırma
6. shadcn/ui bileşenlerini ekle (button, card, input, table, vb.)
7. `src/lib/utils.ts` → cn yardımcı
8. `src/lib/utils/formatters.ts` → Para/tarih formatlama

### Faz 0 — Providers & Layout:

9. `src/components/providers/theme-provider.tsx`
10. `src/components/providers/query-provider.tsx`
11. `src/app/layout.tsx` → Root layout
12. `src/stores/auth-store.ts` → Auth store
13. `src/stores/ui-store.ts` → UI store
14. `src/stores/market-store.ts` → Market store

### Faz 0 — API & Auth:

15. `src/lib/api/client.ts` → Axios client + interceptors
16. `src/types/` → Tüm TypeScript tipleri
17. `src/components/auth/auth-guard.tsx`
18. `src/app/(auth)/login/page.tsx` → Login sayfası
19. `src/app/(auth)/register/page.tsx` → Kayıt sayfası

### Faz 1 — Dashboard Layout:

20. `src/components/layout/sidebar.tsx`
21. `src/components/layout/header.tsx`
22. `src/app/(dashboard)/layout.tsx`

### Faz 1 — Dashboard Sayfası:

23. `src/hooks/use-portfolio.ts`
24. `src/components/dashboard/stat-card.tsx`
25. `src/app/(dashboard)/dashboard/page.tsx` + alt bileşenler

### Faz 1 — Piyasa Sayfası:

26. `src/lib/api/market.ts` → Market API
27. `src/hooks/use-market-data.ts`
28. `src/hooks/use-websocket.ts`
29. `src/components/charts/candlestick-chart.tsx` → TradingView
30. `src/components/market/symbol-table.tsx`
31. `src/app/(dashboard)/market/page.tsx`
32. `src/app/(dashboard)/market/[symbol]/page.tsx`

### Faz 1 — Paper Trading:

33. `src/lib/api/orders.ts`
34. `src/components/market/order-form.tsx`
35. `src/app/(dashboard)/orders/page.tsx`
36. `src/app/(dashboard)/portfolio/page.tsx`

### Faz 2 — Trend Analiz:

37. `src/components/trends/` → Trend bileşenleri
38. `src/app/(dashboard)/trends/page.tsx`

### Faz 2 — Strateji & Backtest:

39. `src/app/(dashboard)/strategies/page.tsx`
40. `src/app/(dashboard)/backtest/page.tsx`
41. `src/app/(dashboard)/settings/page.tsx`

---

_Bu doküman, bist-robogo projesinin frontend geliştirme sürecinde AI Agent'ın takip edeceği tam referans kılavuzdur._
