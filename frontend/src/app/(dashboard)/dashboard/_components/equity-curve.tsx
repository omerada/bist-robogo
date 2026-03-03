"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface EquityPoint {
  date: string;
  total_value: number;
  cash_balance: number;
  invested_value: number;
  daily_pnl: number;
  positions_count: number;
}

interface EquityCurveProps {
  history: EquityPoint[];
}

export function EquityCurve({ history }: EquityCurveProps) {
  if (!history || history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">
            Portföy Eğrisi
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-56 items-center justify-center text-muted-foreground">
            Henüz portföy geçmişi yok. İşlem yaptıkça grafik oluşacak.
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = history.map((h) => ({
    date: new Date(h.date).toLocaleDateString("tr-TR", {
      day: "2-digit",
      month: "short",
    }),
    value: Number(h.total_value) || 0,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Portföy Eğrisi</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={224}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="hsl(var(--primary))"
                  stopOpacity={0.3}
                />
                <stop
                  offset="95%"
                  stopColor="hsl(var(--primary))"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              className="text-xs"
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              className="text-xs"
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `₺${(v / 1000).toFixed(0)}K`}
            />
            <Tooltip
              formatter={(value: number) => [
                `₺${value.toLocaleString("tr-TR")}`,
                "Değer",
              ]}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(var(--primary))"
              fill="url(#equityGrad)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
