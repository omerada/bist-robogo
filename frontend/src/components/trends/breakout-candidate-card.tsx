/**
 * Kırılım adayı kartı — trend sayfasında breakout fırsatı gösteren semboller.
 */
"use client";

import { ArrowUp, Target, BarChart3, Zap, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { BreakoutCandidate } from "@/types/strategy";
import { cn } from "@/lib/utils";

interface BreakoutCandidateCardProps {
  candidate: BreakoutCandidate;
}

function formatCurrency(v: number | string) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    minimumFractionDigits: 2,
  }).format(Number(v) || 0);
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

export function BreakoutCandidateCard({
  candidate,
}: BreakoutCandidateCardProps) {
  const potentialGain =
    candidate.target_price && candidate.price
      ? ((Number(candidate.target_price) - Number(candidate.price)) /
          Number(candidate.price)) *
        100
      : null;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-green-500" />
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
              candidate.change_pct > 0 ? "text-green-600" : "text-red-600",
            )}
          >
            <ArrowUp className="inline h-3 w-3 mr-0.5" />+
            {candidate.change_pct.toFixed(2)}%
          </span>
        </div>

        {/* Kırılım Skoru */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Kırılım Skoru</span>
            <span
              className={cn("font-bold", scoreColor(candidate.breakout_score))}
            >
              {candidate.breakout_score.toFixed(0)}/100
            </span>
          </div>
          <Progress
            value={candidate.breakout_score}
            className={cn("h-2", progressColor(candidate.breakout_score))}
          />
        </div>

        {/* Göstergeler */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          {candidate.breakout_level !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <Zap className="h-3 w-3" />
                Kırılım
              </span>
              <span className="font-medium text-blue-600">
                {formatCurrency(candidate.breakout_level)}
              </span>
            </div>
          )}

          {candidate.target_price !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <Target className="h-3 w-3" />
                Hedef
              </span>
              <span className="font-medium text-green-600">
                {formatCurrency(candidate.target_price)}
              </span>
            </div>
          )}

          {candidate.volume_surge !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <BarChart3 className="h-3 w-3" />
                Hacim Artış
              </span>
              <span
                className={cn(
                  "font-medium",
                  candidate.volume_surge > 1.5
                    ? "text-green-600"
                    : "text-muted-foreground",
                )}
              >
                {candidate.volume_surge.toFixed(2)}x
              </span>
            </div>
          )}

          {potentialGain !== null && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                Potansiyel
              </span>
              <span className="font-bold text-green-600">
                +{potentialGain.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
