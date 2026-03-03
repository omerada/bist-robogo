/**
 * Backtest equity curve bileşeni — Recharts ile strateji vs Buy&Hold karşılaştırma.
 * // Source: Doc 09 §15 — Grafik standartları
 */

"use client";

import { useMemo } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { EquityCurveData } from "@/types/backtest";

interface BacktestEquityCurveProps {
  data: EquityCurveData;
  initialCapital: number;
  height?: number;
}

export function BacktestEquityCurve({
  data,
  initialCapital,
  height = 400,
}: BacktestEquityCurveProps) {
  const chartData = useMemo(() => {
    if (!data?.dates?.length) return [];
    return data.dates.map((date, i) => ({
      date: formatDate(date),
      strateji: data.values[i] ?? initialCapital,
      buyHold: data.benchmark[i] ?? initialCapital,
    }));
  }, [data, initialCapital]);

  const { strategyReturn, benchmarkReturn } = useMemo(() => {
    if (!data?.values?.length) {
      return { strategyReturn: 0, benchmarkReturn: 0 };
    }
    const lastStrategy = data.values[data.values.length - 1];
    const lastBenchmark = data.benchmark[data.benchmark.length - 1];
    return {
      strategyReturn: ((lastStrategy - initialCapital) / initialCapital) * 100,
      benchmarkReturn:
        ((lastBenchmark - initialCapital) / initialCapital) * 100,
    };
  }, [data, initialCapital]);

  if (!chartData.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Equity Curve</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Equity curve verisi bulunamadı.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Equity Curve</CardTitle>
        <div className="flex gap-4 text-sm">
          <span className="text-emerald-500">
            Strateji:{" "}
            <strong>
              {strategyReturn >= 0 ? "+" : ""}
              {strategyReturn.toFixed(2)}%
            </strong>
          </span>
          <span className="text-blue-500">
            Buy&Hold:{" "}
            <strong>
              {benchmarkReturn >= 0 ? "+" : ""}
              {benchmarkReturn.toFixed(2)}%
            </strong>
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="strategyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="benchmarkGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis
              dataKey="date"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `₺${(v / 1000).toFixed(0)}K`}
            />
            <Tooltip
              formatter={(value: number) =>
                `₺${value.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`
              }
              labelStyle={{ fontWeight: 600 }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="strateji"
              name="Strateji"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#strategyGrad)"
            />
            <Area
              type="monotone"
              dataKey="buyHold"
              name="Buy & Hold"
              stroke="#3b82f6"
              strokeWidth={1.5}
              fill="url(#benchmarkGrad)"
              strokeDasharray="5 5"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("tr-TR", { month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
}
