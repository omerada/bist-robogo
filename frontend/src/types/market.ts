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
