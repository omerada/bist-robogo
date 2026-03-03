/**
 * Doğruluk badge — doğruluk oranını renkli badge olarak gösterir.
 * Doc 10 §Faz 3 Sprint 3.3
 */

import { Badge } from "@/components/ui/badge";

interface AccuracyBadgeProps {
  rate: number;
  label?: string;
}

export function AccuracyBadge({ rate, label }: AccuracyBadgeProps) {
  const pct = (rate * 100).toFixed(1);
  const color =
    rate >= 0.7
      ? "bg-green-600 hover:bg-green-700 text-white"
      : rate >= 0.5
        ? "bg-amber-500 hover:bg-amber-600 text-white"
        : "bg-red-600 hover:bg-red-700 text-white";

  return (
    <Badge className={color}>
      {label ? `${label}: ` : ""}%{pct}
    </Badge>
  );
}
