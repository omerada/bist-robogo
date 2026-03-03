/**
 * Fiyat ticker — fiyat değişiminde flash animasyonu.
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface QuoteTickerProps {
  price: number;
  change: number;
  changePct: number;
  className?: string;
}

export function QuoteTicker({
  price: rawPrice,
  change: rawChange,
  changePct: rawChangePct,
  className,
}: QuoteTickerProps) {
  const price = Number(rawPrice) || 0;
  const change = Number(rawChange) || 0;
  const changePct = Number(rawChangePct) || 0;
  const prevPriceRef = useRef(price);
  const [flash, setFlash] = useState<"up" | "down" | null>(null);

  useEffect(() => {
    if (price !== prevPriceRef.current) {
      setFlash(price > prevPriceRef.current ? "up" : "down");
      prevPriceRef.current = price;

      const timer = setTimeout(() => setFlash(null), 600);
      return () => clearTimeout(timer);
    }
  }, [price]);

  const isUp = change > 0;
  const isDown = change < 0;

  return (
    <div className={cn("flex items-baseline gap-3", className)}>
      <span
        className={cn(
          "text-3xl font-bold tabular-nums transition-colors duration-300",
          flash === "up" && "text-green-400",
          flash === "down" && "text-red-400",
          !flash && isUp && "text-green-500",
          !flash && isDown && "text-red-500",
          !flash && !isUp && !isDown && "text-foreground",
        )}
      >
        ₺{price.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}
      </span>
      <span
        className={cn(
          "text-lg font-semibold tabular-nums",
          isUp && "text-green-500",
          isDown && "text-red-500",
          !isUp && !isDown && "text-muted-foreground",
        )}
      >
        {change >= 0 ? "+" : ""}
        {change.toFixed(2)} ({changePct >= 0 ? "+" : ""}
        {changePct.toFixed(2)}%)
      </span>
    </div>
  );
}
