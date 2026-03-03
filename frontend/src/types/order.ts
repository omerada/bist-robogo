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
