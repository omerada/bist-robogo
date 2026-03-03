/**
 * Portföy sayfası — özet kartları, pozisyon listesi.
 */
"use client";

import {
  ArrowDownRight,
  ArrowUpRight,
  Banknote,
  Briefcase,
  PieChart,
  TrendingUp,
  Wallet,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePortfolioSummary, usePositions } from "@/hooks/use-trading";
import { PositionCard } from "@/components/portfolio/position-card";
import { cn } from "@/lib/utils";

function formatCurrency(v: number | string) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    minimumFractionDigits: 2,
  }).format(Number(v) || 0);
}

function SummaryCard({
  label,
  value,
  Icon,
  variant,
}: {
  label: string;
  value: string;
  Icon: React.ElementType;
  variant?: "positive" | "negative" | "neutral";
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <p
          className={cn(
            "text-2xl font-bold",
            variant === "positive" && "text-green-600",
            variant === "negative" && "text-red-600",
          )}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

export default function PortfolioPage() {
  const { data: summary, isLoading: summaryLoading } = usePortfolioSummary();
  const { data: positions, isLoading: positionsLoading } = usePositions();

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Portföy</h1>
        <p className="text-muted-foreground">
          Portföy özeti ve açık pozisyonlar
        </p>
      </div>

      {/* Summary Cards */}
      {summaryLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : summary ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <SummaryCard
            label="Toplam Değer"
            value={formatCurrency(summary.total_value)}
            Icon={Wallet}
          />
          <SummaryCard
            label="Nakit Bakiye"
            value={formatCurrency(summary.cash_balance)}
            Icon={Banknote}
          />
          <SummaryCard
            label="Yatırım Değeri"
            value={formatCurrency(summary.invested_value)}
            Icon={Briefcase}
          />
          <SummaryCard
            label="Toplam K/Z"
            value={`${Number(summary.total_pnl) >= 0 ? "+" : ""}${formatCurrency(summary.total_pnl)}`}
            Icon={
              Number(summary.total_pnl) >= 0 ? ArrowUpRight : ArrowDownRight
            }
            variant={Number(summary.total_pnl) >= 0 ? "positive" : "negative"}
          />
        </div>
      ) : null}

      {/* Extra metrics row */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-3">
          <SummaryCard
            label="Günlük K/Z"
            value={`${Number(summary.daily_pnl) >= 0 ? "+" : ""}${formatCurrency(summary.daily_pnl)} (${Number(summary.daily_pnl_pct ?? 0) >= 0 ? "+" : ""}${Number(summary.daily_pnl_pct ?? 0).toFixed(2)}%)`}
            Icon={TrendingUp}
            variant={Number(summary.daily_pnl) >= 0 ? "positive" : "negative"}
          />
          <SummaryCard
            label="Açık Pozisyon"
            value={String(summary.open_positions)}
            Icon={PieChart}
          />
          <SummaryCard
            label="Toplam K/Z %"
            value={`${Number(summary.total_pnl_pct ?? 0) >= 0 ? "+" : ""}${Number(summary.total_pnl_pct ?? 0).toFixed(2)}%`}
            Icon={TrendingUp}
            variant={
              Number(summary.total_pnl_pct ?? 0) >= 0 ? "positive" : "negative"
            }
          />
        </div>
      )}

      {/* Positions */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Açık Pozisyonlar</h2>
        {positionsLoading ? (
          <div className="grid gap-4 md:grid-cols-2">
            {Array.from({ length: 2 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-20" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : positions && positions.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {positions.map((pos) => (
              <PositionCard key={pos.id} position={pos} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <PieChart className="h-12 w-12 text-muted-foreground mb-3" />
              <CardDescription>
                Henüz açık pozisyon yok. Piyasa sayfasından emir vererek
                başlayabilirsiniz.
              </CardDescription>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
