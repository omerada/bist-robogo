// Broker bağlantı yönetimi tipleri

export type BrokerType = "paper" | "is_yatirim" | "gedik" | "deniz" | "garanti";
export type BrokerStatus = "connected" | "disconnected" | "error" | "pending";

export interface BrokerConnection {
  id: string;
  broker_name: string;
  is_active: boolean;
  is_paper_trading: boolean;
  label: string;
  status: BrokerStatus;
  last_connected_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BrokerConnectionCreate {
  broker_name: BrokerType;
  credentials: Record<string, string>;
  is_paper_trading?: boolean;
  label?: string;
}

export interface BrokerConnectionUpdate {
  credentials?: Record<string, string>;
  is_paper_trading?: boolean;
  is_active?: boolean;
  label?: string;
}

export interface BrokerConnectionListResponse {
  items: BrokerConnection[];
  total: number;
}

export interface BrokerTestResult {
  success: boolean;
  broker_name: string;
  message: string;
  latency_ms: number | null;
}

export interface BrokerQuoteResponse {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  volume: number;
  source: string;
}

export interface BrokerInfo {
  name: BrokerType;
  display_name: string;
  description: string;
  requires_credentials: boolean;
  credential_fields: string[];
  is_available: boolean;
}

export interface BrokerListInfo {
  brokers: BrokerInfo[];
}
