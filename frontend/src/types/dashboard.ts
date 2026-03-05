/**
 * Dashboard TypeScript tipleri.
 * Backend: api/v1/dashboard.py
 */

export interface DashboardPortfolio {
  total_value: number;
  cash_balance: number;
  invested_value: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
}

export interface DashboardSignal {
  id: string;
  symbol: string;
  signal_type: string;
  confidence: number;
  created_at: string | null;
}

export interface DashboardOrder {
  id: string;
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  price: number | null;
  status: string;
  created_at: string | null;
}

export interface EquityHistoryEntry {
  date: string;
  total_value: number;
  cash_balance: number;
  invested_value: number;
  daily_pnl: number;
  positions_count: number;
}

export interface DashboardSummary {
  portfolio: DashboardPortfolio;
  active_strategies: number;
  recent_signals: DashboardSignal[];
  recent_orders: DashboardOrder[];
  equity_history: EquityHistoryEntry[];
}

export interface LivePriceData {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  volume: number;
  change_pct: number;
  name: string;
  source: string;
  updated_at: string;
}

export interface LiveIndexData {
  code: string;
  name: string;
  price: string;
  rate: string;
  source: string;
  updated_at: string;
}
