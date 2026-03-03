/**
 * Sembol tablosu — fiyat, değişim, hacim sütunları ile.
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
import { cn } from "@/lib/utils";

interface SymbolTableProps {
  symbols: SymbolInfo[];
  isLoading?: boolean;
}

function formatVolume(vol: number): string {
  if (vol >= 1_000_000_000) return `${(vol / 1_000_000_000).toFixed(1)}B`;
  if (vol >= 1_000_000) return `${(vol / 1_000_000).toFixed(1)}M`;
  if (vol >= 1_000) return `${(vol / 1_000).toFixed(1)}K`;
  return vol.toString();
}

function formatPrice(price: number): string {
  return price.toLocaleString("tr-TR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
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

export function SymbolTable({ symbols, isLoading }: SymbolTableProps) {
  if (isLoading) return <SymbolTableSkeleton />;

  if (symbols.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Sembol bulunamadı.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Sembol</TableHead>
            <TableHead>Şirket</TableHead>
            <TableHead className="text-right">Sektör</TableHead>
            <TableHead className="text-right w-[80px]">Durum</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {symbols.map((symbol) => (
            <TableRow key={symbol.id} className="cursor-pointer hover:bg-muted/50">
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
              <TableCell className="text-right text-sm text-muted-foreground">
                {symbol.sector || "—"}
              </TableCell>
              <TableCell className="text-right">
                {symbol.is_active ? (
                  <Badge variant="outline" className="text-green-500 border-green-500/30">
                    Aktif
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-red-500 border-red-500/30">
                    Pasif
                  </Badge>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
