/**
 * AI TypeScript tipleri.
 * // Source: Doc 10 §Faz 3 Sprint 3.1 — AI types
 */

// ── Enum'lar ──

export type AISignalAction = "buy" | "sell" | "hold";
export type AIConfidence = "low" | "medium" | "high";
export type ChatRole = "system" | "user" | "assistant";

// ── Gösterge Özeti ──

export interface AIIndicatorSummary {
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  macd_crossover: string | null;
  stoch_k: number | null;
  stoch_d: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  sma_20: number | null;
  sma_50: number | null;
  ema_12: number | null;
  adx: number | null;
  volume_ratio: number | null;
  support_level: number | null;
  resistance_level: number | null;
  obv_trend: string | null;
}

// ── Analiz ──

export interface AIAnalysisRequest {
  symbol: string;
  period?: string;
  include_indicators?: boolean;
}

export interface AIAnalysisResponse {
  symbol: string;
  action: AISignalAction;
  confidence: AIConfidence;
  summary: string;
  reasoning: string;
  key_factors: string[];
  target_price: number | null;
  stop_loss: number | null;
  risk_level: string;
  indicators: AIIndicatorSummary | null;
  model_used: string;
  analyzed_at: string;
}

// ── Sohbet ──

export interface AIChatMessage {
  role: ChatRole;
  content: string;
}

export interface AIChatRequest {
  messages: AIChatMessage[];
  symbol?: string;
}

export interface AIChatResponse {
  reply: string;
  model_used: string;
  usage: Record<string, unknown>;
}

// ── Sinyal ──

export interface AISignalResponse {
  symbol: string;
  action: AISignalAction;
  confidence: AIConfidence;
  reason: string;
  score: number;
}

export interface AISignalListResponse {
  signals: AISignalResponse[];
  model_used: string;
  generated_at: string;
}

// ── Model ──

export interface AIModelInfo {
  id: string;
  name: string;
  context_length: number | null;
  pricing: Record<string, string>;
}

export interface AIModelListResponse {
  models: AIModelInfo[];
}

// ── Ayarlar ──

export interface AISettingsRequest {
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface AISettingsResponse {
  model: string;
  temperature: number;
  max_tokens: number;
  base_url: string;
  api_key_set: boolean;
}
