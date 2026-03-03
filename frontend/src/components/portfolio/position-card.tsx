/**
 * Pozisyon kartı — portföy sayfasında açık pozisyonları gösterir.
 */
"use client";

import { ArrowDown, ArrowUp, TrendingDown, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Position } from "@/types/portfolio";
import { cn } from "@/lib/utils";

interface PositionCardProps {
  position: Position;
}

function formatCurrency(v: number | string) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    minimumFractionDigits: 2,
  }).format(Number(v) || 0);
}

export function PositionCard({ position }: PositionCardProps) {
  const unrealizedPnl = Number(position.unrealized_pnl) || 0;
  const unrealizedPnlPct = Number(position.unrealized_pnl_pct) || 0;
  const isProfit = unrealizedPnl >= 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <CardTitle className="text-lg font-bold">{position.symbol}</CardTitle>
          <Badge variant={position.side === "long" ? "default" : "destructive"}>
            {position.side === "long" ? (
              <ArrowUp className="mr-1 h-3 w-3" />
            ) : (
              <ArrowDown className="mr-1 h-3 w-3" />
            )}
            {position.side.toUpperCase()}
          </Badge>
        </div>
        <div
          className={cn(
            "flex items-center gap-1 text-sm font-semibold",
            isProfit ? "text-green-600" : "text-red-600",
          )}
        >
          {isProfit ? (
            <TrendingUp className="h-4 w-4" />
          ) : (
            <TrendingDown className="h-4 w-4" />
          )}
          {unrealizedPnlPct >= 0 ? "+" : ""}
          {unrealizedPnlPct.toFixed(2)}%
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Miktar</span>
            <span className="font-medium">{position.quantity} lot</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Ort. Giriş</span>
            <span className="font-medium">
              {formatCurrency(position.avg_entry_price)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Güncel</span>
            <span className="font-medium">
              {position.current_price
                ? formatCurrency(position.current_price)
                : "—"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">G/Z (Açık)</span>
            <span
              className={cn(
                "font-medium",
                isProfit ? "text-green-600" : "text-red-600",
              )}
            >
              {formatCurrency(position.unrealized_pnl)}
            </span>
          </div>
          {position.stop_loss && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Stop Loss</span>
              <span className="font-medium text-red-500">
                {formatCurrency(position.stop_loss)}
              </span>
            </div>
          )}
          {position.take_profit && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Take Profit</span>
              <span className="font-medium text-green-500">
                {formatCurrency(position.take_profit)}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
