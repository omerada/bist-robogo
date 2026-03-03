/**
 * Dip adayı kartı — trend sayfasında dip fırsatı gösteren semboller.
 */
"use client";

import {
  ArrowDown,
  Target,
  BarChart3,
  Activity,
  TrendingDown,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { DipCandidate } from "@/types/strategy";
import { cn } from "@/lib/utils";

interface DipCandidateCardProps {
  candidate: DipCandidate;
}

function formatCurrency(v: number) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    minimumFractionDigits: 2,
  }).format(v);
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-emerald-500";
  if (score >= 40) return "text-yellow-500";
  return "text-orange-500";
}

function progressColor(score: number): string {
  if (score >= 80) return "[&>div]:bg-green-600";
  if (score >= 60) return "[&>div]:bg-emerald-500";
  if (score >= 40) return "[&>div]:bg-yellow-500";
  return "[&>div]:bg-orange-500";
}

export function DipCandidateCard({ candidate }: DipCandidateCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <TrendingDown className="h-4 w-4 text-red-500" />
          <CardTitle className="text-base font-bold">
            {candidate.symbol}
          </CardTitle>
          {candidate.name && (
            <span className="text-xs text-muted-foreground truncate max-w-[120px]">
              {candidate.name}
            </span>
          )}
        </div>
        <Badge variant="secondary" className="text-xs">
          {candidate.trend_status}
        </Badge>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Fiyat ve Değişim */}
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold">
            {formatCurrency(candidate.price)}
          </span>
          <span
            className={cn(
              "text-sm font-semibold",
              candidate.change_pct < 0 ? "text-red-600" : "text-green-600",
            )}
          >
            <ArrowDown className="inline h-3 w-3 mr-0.5" />
            {candidate.change_pct.toFixed(2)}%
          </span>
        </div>

        {/* Dip Skoru */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Dip Skoru</span>
            <span className={cn("font-bold", scoreColor(candidate.dip_score))}>
              {candidate.dip_score.toFixed(0)}/100
            </span>
          </div>
          <Progress
            value={candidate.dip_score}
            className={cn("h-2", progressColor(candidate.dip_score))}
          />
        </div>

        {/* Göstergeler */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          {candidate.rsi !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <Activity className="h-3 w-3" />
                RSI
              </span>
              <span
                className={cn(
                  "font-medium",
                  candidate.rsi < 30
                    ? "text-green-600"
                    : candidate.rsi > 70
                      ? "text-red-600"
                      : "",
                )}
              >
                {candidate.rsi.toFixed(1)}
              </span>
            </div>
          )}

          {candidate.volume_ratio !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <BarChart3 className="h-3 w-3" />
                Hacim
              </span>
              <span className="font-medium">
                {candidate.volume_ratio.toFixed(2)}x
              </span>
            </div>
          )}

          {candidate.support_level !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <Target className="h-3 w-3" />
                Destek
              </span>
              <span className="font-medium text-green-600">
                {formatCurrency(candidate.support_level)}
              </span>
            </div>
          )}

          {candidate.resistance_level !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <Target className="h-3 w-3" />
                Direnç
              </span>
              <span className="font-medium text-red-600">
                {formatCurrency(candidate.resistance_level)}
              </span>
            </div>
          )}
        </div>

        {/* MACD Sinyal */}
        <div className="flex items-center justify-between text-xs border-t pt-2">
          <span className="text-muted-foreground">MACD Sinyal</span>
          <Badge
            variant={
              candidate.macd_signal === "bullish_crossover"
                ? "default"
                : candidate.macd_signal === "bearish_crossover"
                  ? "destructive"
                  : "secondary"
            }
            className="text-[10px] px-1.5 py-0"
          >
            {candidate.macd_signal === "bullish_crossover"
              ? "Yükseliş"
              : candidate.macd_signal === "bearish_crossover"
                ? "Düşüş"
                : "Nötr"}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}
