/**
 * AI performans grafiği — model performans metriklerini bar chart ile gösterir.
 * Doc 10 §Faz 3 Sprint 3.3
 */
"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AIModelPerformance } from "@/types/ai";

interface PerformanceChartProps {
  models: AIModelPerformance[];
}

export function PerformanceChart({ models }: PerformanceChartProps) {
  if (models.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground">
          Henüz performans verisi yok.
        </CardContent>
      </Card>
    );
  }

  const chartData = models.map((m) => ({
    model: m.model_id.split("/").pop() || m.model_id,
    "Doğruluk (%)": +(m.accuracy.accuracy_rate * 100).toFixed(1),
    "Ort. Skor": +(m.avg_score * 100).toFixed(1),
    "Ort. Gecikme (ms)": +m.avg_latency_ms.toFixed(0),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">
          Model Performans Karşılaştırması
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="model" className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip />
            <Legend />
            <Bar
              dataKey="Doğruluk (%)"
              fill="hsl(var(--chart-1))"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="Ort. Skor"
              fill="hsl(var(--chart-2))"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
