"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ShieldCheck, ShieldAlert, Shield } from "lucide-react";

interface RiskStatusProps {
  totalValue: number;
  investedValue: number;
  openPositions: number;
}

export function RiskStatus({
  totalValue,
  investedValue,
  openPositions,
}: RiskStatusProps) {
  // Basit risk seviyesi hesaplama
  const exposureRatio = totalValue > 0 ? (investedValue / totalValue) * 100 : 0;
  const positionRisk = Math.min(openPositions * 10, 100);
  const overallRisk = Math.round(exposureRatio * 0.6 + positionRisk * 0.4);

  let riskLevel: "low" | "medium" | "high";
  let riskLabel: string;
  let RiskIcon: typeof ShieldCheck;

  if (overallRisk < 30) {
    riskLevel = "low";
    riskLabel = "Düşük Risk";
    RiskIcon = ShieldCheck;
  } else if (overallRisk < 65) {
    riskLevel = "medium";
    riskLabel = "Orta Risk";
    RiskIcon = Shield;
  } else {
    riskLevel = "high";
    riskLabel = "Yüksek Risk";
    RiskIcon = ShieldAlert;
  }

  const colorMap = {
    low: "text-emerald-500",
    medium: "text-amber-500",
    high: "text-red-500",
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Risk Durumu</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <RiskIcon className={`h-8 w-8 ${colorMap[riskLevel]}`} />
          <div>
            <p className={`text-lg font-bold ${colorMap[riskLevel]}`}>
              {riskLabel}
            </p>
            <p className="text-xs text-muted-foreground">
              Risk skoru: {overallRisk}/100
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Yatırım Oranı</span>
            <span className="font-medium tabular-nums">
              %{exposureRatio.toFixed(1)}
            </span>
          </div>
          <Progress value={exposureRatio} className="h-2" />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Pozisyon Riski</span>
            <span className="font-medium tabular-nums">{openPositions}/10</span>
          </div>
          <Progress value={positionRisk} className="h-2" />
        </div>
      </CardContent>
    </Card>
  );
}
