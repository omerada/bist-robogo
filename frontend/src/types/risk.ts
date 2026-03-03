/**
 * Risk ve Bildirim TypeScript tipleri.
 * // Source: Doc 03 §3.7 + §3.9
 */

// ── Risk ──

export type RiskLevel = "low" | "moderate" | "high" | "critical";

export interface RiskStatus {
  overall_risk: RiskLevel;
  daily_loss: number;
  daily_loss_limit: number;
  open_positions: number;
  max_positions: number;
  rules_active: number;
  recent_events: RiskEventSummary[];
}

export interface RiskEventSummary {
  type: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface RiskRule {
  id: string;
  rule_type: string;
  value: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RiskRuleUpdate {
  value?: Record<string, unknown>;
  is_active?: boolean;
}

export interface RiskEvent {
  id: string;
  user_id: string;
  event_type: string;
  rule_id: string | null;
  details: Record<string, unknown>;
  created_at: string;
}

// ── Notification ──

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  body: string;
  channel: string;
  is_read: boolean;
  metadata_: Record<string, unknown>;
  sent_at: string;
  read_at: string | null;
}
