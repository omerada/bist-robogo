"use client";

import { Wallet, TrendingUp, TrendingDown, Layers, Zap } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";

export function DashboardStats() {
  // TODO: usePortfolioSummary() hook'undan veri çekilecek
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      <StatCard
        title="Portföy Değeri"
        value="₺0"
        change="+0%"
        changeType="neutral"
        icon={Wallet}
      />
      <StatCard
        title="Günlük PnL"
        value="₺0"
        change="0%"
        changeType="neutral"
        icon={TrendingUp}
      />
      <StatCard
        title="Toplam PnL"
        value="₺0"
        change="0%"
        changeType="neutral"
        icon={TrendingDown}
      />
      <StatCard
        title="Açık Pozisyon"
        value="0"
        subtitle="/ 10 maks"
        icon={Layers}
      />
      <StatCard
        title="Aktif Strateji"
        value="0"
        subtitle="paper trading"
        icon={Zap}
      />
    </div>
  );
}
