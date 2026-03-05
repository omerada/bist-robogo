/**
 * Notification TypeScript tipleri.
 * Backend: models/notification.py, schemas/notification.py
 */

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

export type NotificationChannel = "in_app" | "email" | "telegram" | "sms";

export type NotificationType =
  | "order_filled"
  | "order_cancelled"
  | "signal_generated"
  | "risk_alert"
  | "system"
  | "price_alert";

export interface NotificationListParams {
  is_read?: boolean;
  channel?: string;
  page?: number;
  per_page?: number;
}
