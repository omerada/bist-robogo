/**
 * Sembol kart bileşeni — kompakt fiyat gösterimi.
 */

"use client";

import Link from "next/link";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { Quote } from "@/types/market";

interface SymbolCardProps {
  quote: Quote;
}

export function SymbolCard({ quote }: SymbolCardProps) {
  const change = Number(quote.change) || 0;
  const changePct = Number(quote.change_pct) || 0;
  const price = Number(quote.price) || 0;
  const isUp = change > 0;
  const isDown = change < 0;

  return (
    <Link href={`/market/${quote.symbol}`}>
      <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-sm">{quote.symbol}</span>
            <span
              className={cn(
                "flex items-center text-xs font-medium",
                isUp && "text-green-500",
                isDown && "text-red-500",
                !isUp && !isDown && "text-muted-foreground",
              )}
            >
              {isUp && <ArrowUpRight className="h-3 w-3 mr-0.5" />}
              {isDown && <ArrowDownRight className="h-3 w-3 mr-0.5" />}
              {!isUp && !isDown && <Minus className="h-3 w-3 mr-0.5" />}
              {changePct >= 0 ? "+" : ""}
              {changePct.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-lg font-bold tabular-nums">
                ₺
                {price.toLocaleString("tr-TR", {
                  minimumFractionDigits: 2,
                })}
              </div>
              <div className="text-xs text-muted-foreground truncate max-w-[120px]">
                {quote.name}
              </div>
            </div>
            <div className="text-right text-xs text-muted-foreground">
              <div>H: ₺{quote.volume.toLocaleString("tr-TR")}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
