/**
 * Dashboard üst kısımda gösterilen istatistik kartı.
 */

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  subtitle?: string;
  icon?: LucideIcon;
}

export function StatCard({
  title,
  value,
  change,
  changeType = "neutral",
  subtitle,
  icon: Icon,
}: StatCardProps) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {title}
          </p>
          {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
        </div>
        <div className="mt-2">
          <p className="text-2xl font-bold tabular-nums">{value}</p>
          <div className="mt-1 flex items-center gap-2">
            {change && (
              <span
                className={cn(
                  "text-xs font-medium tabular-nums",
                  changeType === "positive" && "text-profit",
                  changeType === "negative" && "text-loss",
                  changeType === "neutral" && "text-muted-foreground",
                )}
              >
                {change}
              </span>
            )}
            {subtitle && (
              <span className="text-xs text-muted-foreground">{subtitle}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
