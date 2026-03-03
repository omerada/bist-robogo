/**
 * Trend Analiz sayfası — dip adayları ve kırılım adayları.
 * Doc 04 §2.4 wireframe'ine göre: filtreler + iki sütun layout.
 */
"use client";

import { useState } from "react";
import {
  TrendingDown,
  TrendingUp,
  RefreshCw,
  BarChart3,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTrendAnalysis } from "@/hooks/use-trends";
import { DipCandidateCard } from "@/components/trends/dip-candidate-card";
import { BreakoutCandidateCard } from "@/components/trends/breakout-candidate-card";

export default function TrendsPage() {
  const [period, setPeriod] = useState<"daily" | "weekly" | "monthly">("daily");
  const [index, setIndex] = useState("XU030");
  const [type, setType] = useState<"all" | "dip" | "breakout">("all");

  const { data, isLoading, isError, refetch, isFetching } = useTrendAnalysis({
    period,
    index,
    type,
    min_score: 20,
    limit: 20,
  });

  const analysis = data?.data;
  const meta = data?.meta;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="h-6 w-6" />
            Trend Analiz
          </h1>
          <p className="text-muted-foreground text-sm">
            AI destekli dip ve kırılım adayı tespiti
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${isFetching ? "animate-spin" : ""}`}
          />
          Yenile
        </Button>
      </div>

      {/* Filtreler */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Periyot */}
        <Select
          value={period}
          onValueChange={(v) => setPeriod(v as "daily" | "weekly" | "monthly")}
        >
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Periyot" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="daily">Günlük</SelectItem>
            <SelectItem value="weekly">Haftalık</SelectItem>
            <SelectItem value="monthly">Aylık</SelectItem>
          </SelectContent>
        </Select>

        {/* Endeks */}
        <Select value={index} onValueChange={setIndex}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Endeks" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="XU030">BIST 30</SelectItem>
            <SelectItem value="XU100">BIST 100</SelectItem>
            <SelectItem value="XKTUM">Tüm Piyasa</SelectItem>
          </SelectContent>
        </Select>

        {/* Tip */}
        <Select
          value={type}
          onValueChange={(v) => setType(v as "all" | "dip" | "breakout")}
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Tür" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tümü</SelectItem>
            <SelectItem value="dip">Dip Adayları</SelectItem>
            <SelectItem value="breakout">Kırılım Adayları</SelectItem>
          </SelectContent>
        </Select>

        {/* Meta bilgi */}
        {meta && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground ml-auto">
            <Badge variant="outline" className="text-[10px]">
              📉 {meta.total_dip_candidates} dip
            </Badge>
            <Badge variant="outline" className="text-[10px]">
              📈 {meta.total_breakout_candidates} kırılım
            </Badge>
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[0, 1].map((col) => (
            <div key={col} className="space-y-4">
              <Skeleton className="h-6 w-48" />
              {Array.from({ length: 4 }).map((_, i) => (
                <Card key={i}>
                  <CardHeader className="pb-2">
                    <Skeleton className="h-5 w-32" />
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Skeleton className="h-6 w-24" />
                    <Skeleton className="h-2 w-full" />
                    <div className="grid grid-cols-2 gap-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {isError && (
        <Card className="border-red-200 bg-red-50 dark:bg-red-950/20">
          <CardContent className="flex items-center gap-3 py-6">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <div>
              <p className="font-medium text-red-800 dark:text-red-200">
                Trend verisi yüklenemedi
              </p>
              <p className="text-sm text-red-600 dark:text-red-400">
                Lütfen daha sonra tekrar deneyin.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="ml-auto"
              onClick={() => refetch()}
            >
              Tekrar Dene
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Data */}
      {analysis && !isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Dip Adayları */}
          {(type === "all" || type === "dip") && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-red-500" />
                Dip Adayları
                <Badge variant="secondary" className="text-xs">
                  {analysis.dip_candidates.length}
                </Badge>
              </h2>

              {analysis.dip_candidates.length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center text-muted-foreground">
                    Bu kriterlere uygun dip adayı bulunamadı.
                  </CardContent>
                </Card>
              ) : (
                analysis.dip_candidates.map((c) => (
                  <DipCandidateCard key={c.symbol} candidate={c} />
                ))
              )}
            </div>
          )}

          {/* Kırılım Adayları */}
          {(type === "all" || type === "breakout") && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                Kırılım Adayları
                <Badge variant="secondary" className="text-xs">
                  {analysis.breakout_candidates.length}
                </Badge>
              </h2>

              {analysis.breakout_candidates.length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center text-muted-foreground">
                    Bu kriterlere uygun kırılım adayı bulunamadı.
                  </CardContent>
                </Card>
              ) : (
                analysis.breakout_candidates.map((c) => (
                  <BreakoutCandidateCard key={c.symbol} candidate={c} />
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
