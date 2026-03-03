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
