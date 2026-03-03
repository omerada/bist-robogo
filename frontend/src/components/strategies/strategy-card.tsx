/**
 * Strateji kartı — strateji listesinde her stratejiyi gösterir.
 */
"use client";

import {
  Play,
  Pause,
  Trash2,
  Settings,
  TrendingUp,
  Activity,
  Signal,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Strategy } from "@/types/strategy";
import { cn } from "@/lib/utils";

interface StrategyCardProps {
  strategy: Strategy;
  onActivate?: (id: string) => void;
  onDeactivate?: (id: string) => void;
  onDelete?: (id: string) => void;
  onEdit?: (id: string) => void;
}

const STRATEGY_TYPE_LABELS: Record<string, string> = {
  ma_crossover: "MA Çapraz",
  rsi_reversal: "RSI Dönüş",
  ai_trend: "AI Trend",
};

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function StrategyCard({
  strategy,
  onActivate,
  onDeactivate,
  onDelete,
  onEdit,
}: StrategyCardProps) {
  return (
    <Card
      className={cn(
        "hover:shadow-md transition-shadow",
        strategy.is_active && "border-green-300 dark:border-green-800",
      )}
    >
      <CardHeader className="flex flex-row items-start justify-between pb-2">
        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-center gap-2">
            <CardTitle className="text-base font-bold truncate">
              {strategy.name}
            </CardTitle>
            <Badge
              variant={strategy.is_active ? "default" : "secondary"}
              className="text-[10px] shrink-0"
            >
              {strategy.is_active ? (
                <>
                  <Signal className="h-3 w-3 mr-1" />
                  Aktif
                </>
              ) : (
                "Pasif"
              )}
            </Badge>
          </div>
          {strategy.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">
              {strategy.description}
            </p>
          )}
        </div>

        {/* Aksiyon Butonlar */}
        <div className="flex items-center gap-1 ml-2 shrink-0">
          {strategy.is_active ? (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => onDeactivate?.(strategy.id)}
              title="Durdur"
            >
              <Pause className="h-3.5 w-3.5" />
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-green-600"
              onClick={() => onActivate?.(strategy.id)}
              title="Başlat"
            >
              <Play className="h-3.5 w-3.5" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => onEdit?.(strategy.id)}
            title="Düzenle"
          >
            <Settings className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-red-500 hover:text-red-700"
            onClick={() => onDelete?.(strategy.id)}
            title="Sil"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Bilgiler */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center gap-1">
              <Activity className="h-3 w-3" />
              Tip
            </span>
            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
              {STRATEGY_TYPE_LABELS[strategy.strategy_type] ??
                strategy.strategy_type}
            </Badge>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              Zaman Dilimi
            </span>
            <span className="font-medium">{strategy.timeframe}</span>
          </div>

          <div className="flex items-center justify-between col-span-2">
            <span className="text-muted-foreground">Semboller</span>
            <span className="font-medium truncate max-w-[200px]">
              {strategy.symbols.length > 0
                ? strategy.symbols.join(", ")
                : (strategy.index_filter ?? "Tümü")}
            </span>
          </div>
        </div>

        {/* Alt bilgi */}
        <div className="flex items-center justify-between text-[10px] text-muted-foreground border-t pt-2">
          <span>{strategy.is_paper ? "📄 Kağıt" : "💰 Gerçek"} Hesap</span>
          <span>Oluşturulma: {formatDate(strategy.created_at)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
