"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

interface AllocationChartProps {
  cashBalance: number;
  investedValue: number;
}

const COLORS = ["hsl(var(--primary))", "hsl(var(--muted-foreground))"];

export function AllocationChart({
  cashBalance,
  investedValue,
}: AllocationChartProps) {
  const total = cashBalance + investedValue;
  const investedPct =
    total > 0 ? ((investedValue / total) * 100).toFixed(1) : "0";
  const cashPct = total > 0 ? ((cashBalance / total) * 100).toFixed(1) : "100";

  const data = [
    { name: `Yatırım (${investedPct}%)`, value: investedValue },
    { name: `Nakit (${cashPct}%)`, value: cashBalance },
  ];

  if (total === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">
            Pozisyon Dağılımı
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-56 items-center justify-center text-muted-foreground">
            Henüz yatırım yapılmamış.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">
          Pozisyon Dağılımı
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={224}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={80}
              dataKey="value"
              label={false}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => [
                `₺${value.toLocaleString("tr-TR")}`,
              ]}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              wrapperStyle={{ fontSize: "12px" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
