// Backtest TypeScript type tanımları

export interface BacktestRunRequest {
  strategy_id: string;
  name?: string;
  parameters?: Record<string, unknown>;
  symbols: string[];
  start_date: string; // YYYY-MM-DD
  end_date: string;
  initial_capital?: number;
  commission_rate?: number;
  slippage_rate?: number;
}

export interface BacktestTrade {
  id: string;
  backtest_id: string;
  symbol: string;
  side: string;
  entry_date: string;
  entry_price: number;
  exit_date: string | null;
  exit_price: number | null;
  quantity: number;
  pnl: number | null;
  pnl_pct: number | null;
  holding_days: number | null;
  signal_metadata: Record<string, unknown>;
}

export interface BacktestResult {
  id: string;
  strategy_id: string;
  name: string | null;
  status: "pending" | "running" | "completed" | "failed";
  parameters: Record<string, unknown>;
  symbols: string[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission_rate: number;
  slippage_rate: number;
  total_return: number | null;
  cagr: number | null;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  max_drawdown: number | null;
  win_rate: number | null;
  profit_factor: number | null;
  total_trades: number | null;
  avg_trade_pnl: number | null;
  avg_holding_days: number | null;
  equity_curve: EquityCurveData | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface BacktestDetail extends BacktestResult {
  trades: BacktestTrade[];
}

export interface EquityCurveData {
  dates: string[];
  values: number[];
  benchmark: number[];
}
