/**
 * Sembol tablosu — fiyat, değişim, hacim sütunları ile.
 * Canlı fiyat verisi livePrices prop'u ile sağlanır.
 */

"use client";

import Link from "next/link";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { SymbolInfo } from "@/types/market";
import type { LivePriceData } from "@/lib/api/dashboard";
import { cn } from "@/lib/utils";

interface SymbolTableProps {
  symbols: SymbolInfo[];
  isLoading?: boolean;
  livePrices?: Record<string, LivePriceData>;
}

function formatVolume(vol: number | string): string {
  const v = Number(vol) || 0;
  if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`;
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  return v.toString();
}

function formatPrice(price: number | string): string {
  return Number(price).toLocaleString("tr-TR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function ChangeIndicator({
  changePct: rawPct,
}: {
  changePct: number | string;
}) {
  const changePct = Number(rawPct) || 0;
  if (changePct > 0) {
    return (
      <span className="flex items-center gap-1 text-emerald-600 font-medium text-sm tabular-nums">
        <ArrowUpRight className="h-3.5 w-3.5" />+{changePct.toFixed(2)}%
      </span>
    );
  }
  if (changePct < 0) {
    return (
      <span className="flex items-center gap-1 text-red-600 font-medium text-sm tabular-nums">
        <ArrowDownRight className="h-3.5 w-3.5" />
        {changePct.toFixed(2)}%
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-muted-foreground text-sm tabular-nums">
      <Minus className="h-3.5 w-3.5" />
      0.00%
    </span>
  );
}

function SymbolTableSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 10 }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  );
}

export function SymbolTable({
  symbols,
  isLoading,
  livePrices = {},
}: SymbolTableProps) {
  if (isLoading) return <SymbolTableSkeleton />;

  if (symbols.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Sembol bulunamadı.
      </div>
    );
  }

  const hasLivePrices = Object.keys(livePrices).length > 0;

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Sembol</TableHead>
            <TableHead>Şirket</TableHead>
            {hasLivePrices && (
              <>
                <TableHead className="text-right">Fiyat</TableHead>
                <TableHead className="text-right">Değişim</TableHead>
                <TableHead className="text-right">Hacim</TableHead>
              </>
            )}
            <TableHead className="text-right">Sektör</TableHead>
            <TableHead className="text-right w-[80px]">Durum</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {symbols.map((symbol) => {
            const live = livePrices[symbol.ticker];
            return (
              <TableRow
                key={symbol.id}
                className="cursor-pointer hover:bg-muted/50"
              >
                <TableCell className="font-bold">
                  <Link
                    href={`/market/${symbol.ticker}`}
                    className="hover:text-primary transition-colors"
                  >
                    {symbol.ticker}
                  </Link>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {symbol.name}
                </TableCell>
                {hasLivePrices && (
                  <>
                    <TableCell className="text-right font-medium tabular-nums">
                      {live ? `₺${formatPrice(live.price)}` : "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      {live ? (
                        <ChangeIndicator changePct={live.change_pct} />
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right text-sm text-muted-foreground tabular-nums">
                      {live ? formatVolume(live.volume) : "—"}
                    </TableCell>
                  </>
                )}
                <TableCell className="text-right text-sm text-muted-foreground">
                  {symbol.sector || "—"}
                </TableCell>
                <TableCell className="text-right">
                  {symbol.is_active ? (
                    <Badge
                      variant="outline"
                      className="text-green-500 border-green-500/30"
                    >
                      Aktif
                    </Badge>
                  ) : (
                    <Badge
                      variant="outline"
                      className="text-red-500 border-red-500/30"
                    >
                      Pasif
                    </Badge>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
