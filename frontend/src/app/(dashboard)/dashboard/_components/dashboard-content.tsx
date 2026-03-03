/**
 * Dashboard içerik bileşeni — useDashboardSummary ile tüm veriyi çeker.
 */

"use client";

import { Wallet, TrendingUp, TrendingDown, Layers, Zap } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardSummary } from "@/hooks/use-dashboard";
import { DashboardStats } from "./dashboard-stats";
import { EquityCurve } from "./equity-curve";
import { AllocationChart } from "./allocation-chart";
import { RecentSignals } from "./recent-signals";
import { RecentOrders } from "./recent-orders";
import { RiskStatus } from "./risk-status";

function StatsLoading() {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-24 rounded-lg" />
      ))}
    </div>
  );
}

function ChartLoading() {
  return <Skeleton className="h-72 rounded-lg" />;
}

function TableLoading() {
  return <Skeleton className="h-48 rounded-lg" />;
}

export function DashboardContent() {
  const { data, isLoading, isError } = useDashboardSummary();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <StatsLoading />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <ChartLoading />
          </div>
          <ChartLoading />
        </div>
        <TableLoading />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex h-64 items-center justify-center text-muted-foreground">
        Dashboard verisi yüklenemedi. Lütfen sayfayı yenileyin.
      </div>
    );
  }

  const p = data.portfolio;

  // API Decimal alanları string döndürebiliyor — savunmacı Number() dönüşümü
  const totalValue = Number(p.total_value) || 0;
  const cashBalance = Number(p.cash_balance) || 0;
  const investedValue = Number(p.invested_value) || 0;
  const dailyPnl = Number(p.daily_pnl) || 0;
  const dailyPnlPct = Number(p.daily_pnl_pct) || 0;
  const totalPnl = Number(p.total_pnl) || 0;
  const totalPnlPct = Number(p.total_pnl_pct) || 0;
  const openPositions = Number(p.open_positions) || 0;
  const activeStrategies = Number(data.active_strategies) || 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Üst: İstatistik Kartları */}
      <DashboardStats
        totalValue={totalValue}
        dailyPnl={dailyPnl}
        dailyPnlPct={dailyPnlPct}
        totalPnl={totalPnl}
        totalPnlPct={totalPnlPct}
        openPositions={openPositions}
        activeStrategies={activeStrategies}
      />

      {/* Orta: Equity Curve + Allocation */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <EquityCurve history={data.equity_history} />
        </div>
        <div>
          <AllocationChart
            cashBalance={cashBalance}
            investedValue={investedValue}
          />
        </div>
      </div>

      {/* Alt: Sinyaller + Risk */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentSignals signals={data.recent_signals} />
        </div>
        <div>
          <RiskStatus
            totalValue={totalValue}
            investedValue={investedValue}
            openPositions={openPositions}
          />
        </div>
      </div>

      {/* En Alt: Son Emirler */}
      <RecentOrders orders={data.recent_orders} />
    </div>
  );
}
