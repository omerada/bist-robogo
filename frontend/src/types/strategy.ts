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

export interface StrategyCreateRequest {
  name: string;
  description?: string;
  strategy_type: string;
  parameters?: Record<string, unknown>;
  symbols?: string[];
  index_filter?: string;
  timeframe?: string;
  risk_params?: Record<string, unknown>;
}

export interface StrategyUpdateRequest {
  name?: string;
  description?: string;
  parameters?: Record<string, unknown>;
  symbols?: string[];
  index_filter?: string;
  timeframe?: string;
  risk_params?: Record<string, unknown>;
}

export interface StrategyPerformance {
  strategy_id: string;
  total_signals: number;
  executed_signals: number;
  buy_signals: number;
  sell_signals: number;
  win_rate: number;
  total_pnl: number;
  avg_confidence: number;
  last_signal_at: string | null;
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
  is_executed: boolean;
  created_at: string;
}

export interface TrendIndicators {
  sma_20: number | null;
  sma_50: number | null;
  ema_12: number | null;
  bollinger_lower: number | null;
  bollinger_upper: number | null;
  adx: number | null;
  stochastic_k: number | null;
  macd_histogram: number | null;
  obv_trend: string | null;
}

export interface DipCandidate {
  symbol: string;
  name: string;
  price: number;
  change_pct: number;
  dip_score: number;
  support_level: number | null;
  resistance_level: number | null;
  rsi: number | null;
  macd_signal: string;
  volume_ratio: number | null;
  trend_status: string;
  indicators: TrendIndicators;
}

export interface BreakoutCandidate {
  symbol: string;
  name: string;
  price: number;
  change_pct: number;
  breakout_score: number;
  breakout_level: number | null;
  target_price: number | null;
  volume_surge: number | null;
  trend_status: string;
  indicators: TrendIndicators;
}

export interface TrendAnalysis {
  period: string;
  index: string;
  analysis_date: string;
  dip_candidates: DipCandidate[];
  breakout_candidates: BreakoutCandidate[];
}

export interface TrendAnalysisMeta {
  total_dip_candidates: number;
  total_breakout_candidates: number;
  analysis_timestamp: string;
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
