/**
 * Dashboard sayfası — tüm kritik bilgilerin tek bakışta görüldüğü ana ekran.
 */

import type { Metadata } from "next";
import { Suspense } from "react";
import { DashboardStats } from "./_components/dashboard-stats";
import { EquityCurve } from "./_components/equity-curve";
import { AllocationChart } from "./_components/allocation-chart";
import { RecentSignals } from "./_components/recent-signals";
import { RiskStatus } from "./_components/risk-status";
import { RecentOrders } from "./_components/recent-orders";
import { Skeleton } from "@/components/ui/skeleton";

export const metadata: Metadata = {
  title: "Dashboard",
};

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Üst: İstatistik Kartları */}
      <Suspense fallback={<StatsLoading />}>
        <DashboardStats />
      </Suspense>

      {/* Orta: Equity Curve + Allocation */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Suspense fallback={<ChartLoading />}>
            <EquityCurve />
          </Suspense>
        </div>
        <div>
          <Suspense fallback={<ChartLoading />}>
            <AllocationChart />
          </Suspense>
        </div>
      </div>

      {/* Alt: Sinyaller + Risk */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Suspense fallback={<TableLoading />}>
            <RecentSignals />
          </Suspense>
        </div>
        <div>
          <Suspense fallback={<ChartLoading />}>
            <RiskStatus />
          </Suspense>
        </div>
      </div>

      {/* En Alt: Son Emirler */}
      <Suspense fallback={<TableLoading />}>
        <RecentOrders />
      </Suspense>
    </div>
  );
}

// ── Loading Skeleton'ları ──
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
