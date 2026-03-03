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
