/**
 * AI TypeScript tipleri.
 * // Source: Doc 10 §Faz 3 Sprint 3.1 + 3.3 — AI types
 */

// ── Enum'lar ──

export type AISignalAction = "buy" | "sell" | "hold";
export type AIConfidence = "low" | "medium" | "high";
export type ChatRole = "system" | "user" | "assistant";
export type AIExperimentStatus = "pending" | "running" | "completed" | "failed";

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

// ── A/B Test Deneyleri ──

export interface AIExperimentCreate {
  name: string;
  description?: string;
  model_a: string;
  model_b: string;
  symbols: string[];
  config?: Record<string, unknown>;
}

export interface AIExperimentResultResponse {
  id: string;
  experiment_id: string;
  symbol: string;
  model_id: string;
  action: AISignalAction;
  confidence: AIConfidence;
  score: number;
  reasoning: string | null;
  latency_ms: number;
  token_usage: Record<string, unknown>;
  created_at: string;
}

export interface AIExperimentResponse {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  model_a: string;
  model_b: string;
  symbols: string[];
  status: AIExperimentStatus;
  config: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string | null;
  results: AIExperimentResultResponse[];
}

export interface AIExperimentListResponse {
  experiments: AIExperimentResponse[];
  total: number;
}

// ── Performans ──

export interface AIAccuracyMetric {
  total_analyses: number;
  correct_predictions: number;
  accuracy_rate: number;
  buy_accuracy: number;
  sell_accuracy: number;
  hold_accuracy: number;
}

export interface AIModelPerformance {
  model_id: string;
  total_analyses: number;
  avg_latency_ms: number;
  avg_score: number;
  avg_confidence_distribution: Record<string, number>;
  total_tokens_used: number;
  accuracy: AIAccuracyMetric;
  period_start: string | null;
  period_end: string | null;
}

export interface AIModelComparison {
  model_a: AIModelPerformance;
  model_b: AIModelPerformance;
  winner: string | null;
  comparison_notes: string[];
}

export interface AIModelComparisonResponse {
  comparison: AIModelComparison;
  generated_at: string;
}

export interface AIPerformanceSummary {
  models: AIModelPerformance[];
  total_analyses: number;
  overall_accuracy: number;
  period_days: number;
  generated_at: string;
}
