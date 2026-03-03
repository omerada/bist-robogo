"use client";

import { Wallet, TrendingUp, TrendingDown, Layers, Zap } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";

interface DashboardStatsProps {
  totalValue: number;
  dailyPnl: number;
  dailyPnlPct: number;
  totalPnl: number;
  totalPnlPct: number;
  openPositions: number;
  activeStrategies: number;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function pnlChangeType(value: number): "positive" | "negative" | "neutral" {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}

export function DashboardStats({
  totalValue,
  dailyPnl,
  dailyPnlPct,
  totalPnl,
  totalPnlPct,
  openPositions,
  activeStrategies,
}: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      <StatCard
        title="Portföy Değeri"
        value={formatCurrency(totalValue)}
        icon={Wallet}
      />
      <StatCard
        title="Günlük PnL"
        value={formatCurrency(dailyPnl)}
        change={`${dailyPnlPct >= 0 ? "+" : ""}${dailyPnlPct.toFixed(2)}%`}
        changeType={pnlChangeType(dailyPnl)}
        icon={TrendingUp}
      />
      <StatCard
        title="Toplam PnL"
        value={formatCurrency(totalPnl)}
        change={`${totalPnlPct >= 0 ? "+" : ""}${totalPnlPct.toFixed(2)}%`}
        changeType={pnlChangeType(totalPnl)}
        icon={TrendingDown}
      />
      <StatCard
        title="Açık Pozisyon"
        value={String(openPositions)}
        subtitle="/ 10 maks"
        icon={Layers}
      />
      <StatCard
        title="Aktif Strateji"
        value={String(activeStrategies)}
        subtitle="paper trading"
        icon={Zap}
      />
    </div>
  );
}
