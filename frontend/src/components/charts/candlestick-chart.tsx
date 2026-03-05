/**
 * TradingView Lightweight Charts entegrasyonu — mum grafiği.
 */

"use client";

import { useEffect, useRef, useMemo } from "react";
import { useTheme } from "next-themes";
import {
  createChart,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type HistogramData,
  ColorType,
} from "lightweight-charts";
import { useHistory } from "@/hooks/use-market-data";
import { useMarketStore } from "@/stores/market-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BarChart3 } from "lucide-react";

interface CandlestickChartProps {
  symbol: string;
  interval?: string;
  height?: number;
}

/**
 * OHLCV zaman dizisini Lightweight Charts'ın beklediği formata çevirir.
 *
 * Günlük interval'da: "YYYY-MM-DD" string (business day)
 * İntraday interval'da: Unix timestamp (seconds) — saat bilgisi korunur
 */
function parseChartTime(isoTime: string, interval: string): string | number {
  const isIntraday = ["1m", "5m", "15m", "1h"].includes(interval);
  if (isIntraday) {
    // Unix timestamp (saniye) — intraday veri için saat bilgisi korunur
    return Math.floor(new Date(isoTime).getTime() / 1000);
  }
  // Günlük ve üstü — "YYYY-MM-DD" formatı
  return isoTime.split("T")[0];
}

export function CandlestickChart({
  symbol,
  interval = "1d",
  height = 400,
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { data: history, isLoading } = useHistory(symbol, interval);
  const quote = useMarketStore((s) => s.quotes[symbol]);

  // ── Tema renkleri ──
  const chartColors = useMemo(
    () => ({
      backgroundColor: isDark ? "hsl(224, 71%, 4%)" : "hsl(0, 0%, 100%)",
      textColor: isDark ? "hsl(215, 20%, 65%)" : "hsl(220, 9%, 46%)",
      gridColor: isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.04)",
      upColor: isDark ? "#22c55e" : "#16a34a",
      downColor: isDark ? "#ef4444" : "#dc2626",
      borderUpColor: isDark ? "#22c55e" : "#16a34a",
      borderDownColor: isDark ? "#ef4444" : "#dc2626",
      wickUpColor: isDark ? "#22c55e" : "#16a34a",
      wickDownColor: isDark ? "#ef4444" : "#dc2626",
    }),
    [isDark],
  );

  // ── Chart oluştur ──
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: {
          type: ColorType.Solid,
          color: chartColors.backgroundColor,
        },
        textColor: chartColors.textColor,
        fontFamily: "Inter, system-ui, sans-serif",
      },
      grid: {
        vertLines: { color: chartColors.gridColor },
        horzLines: { color: chartColors.gridColor },
      },
      width: chartContainerRef.current.clientWidth,
      height,
      crosshair: {
        mode: 0, // Normal
      },
      rightPriceScale: {
        borderColor: chartColors.gridColor,
      },
      timeScale: {
        borderColor: chartColors.gridColor,
        timeVisible: true,
      },
    });

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: chartColors.upColor,
      downColor: chartColors.downColor,
      borderUpColor: chartColors.borderUpColor,
      borderDownColor: chartColors.borderDownColor,
      wickUpColor: chartColors.wickUpColor,
      wickDownColor: chartColors.wickDownColor,
    });

    // Volume series (alt grafik)
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    // Responsive
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        chart.applyOptions({ width: entry.contentRect.width });
      }
    });
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [chartColors, height]);

  // ── Veri yükle ──
  useEffect(() => {
    if (!history || !candleSeriesRef.current || !volumeSeriesRef.current)
      return;

    const candleData: CandlestickData[] = history.map((d) => ({
      time: parseChartTime(d.time, interval) as string & number,
      open: Number(d.open),
      high: Number(d.high),
      low: Number(d.low),
      close: Number(d.close),
    }));

    const volumeData: HistogramData[] = history.map((d) => ({
      time: parseChartTime(d.time, interval) as string & number,
      value: Number(d.volume),
      color:
        Number(d.close) >= Number(d.open)
          ? chartColors.upColor + "80"
          : chartColors.downColor + "80",
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);
    chartRef.current?.timeScale().fitContent();
  }, [history, chartColors, interval]);

  // ── Gerçek zamanlı güncelleme (WebSocket quote) ──
  useEffect(() => {
    if (!quote || !candleSeriesRef.current) return;

    const isIntraday = ["1m", "5m", "15m", "1h"].includes(interval);
    const time = isIntraday
      ? Math.floor(Date.now() / 1000)
      : (new Date().toISOString().split("T")[0] as string);

    candleSeriesRef.current.update({
      time: time as string & number,
      open: Number(quote.open) || Number(quote.price),
      high: Number(quote.high) || Number(quote.price),
      low: Number(quote.low) || Number(quote.price),
      close: Number(quote.price),
    });
  }, [quote, interval]);

  if (isLoading) {
    return <Skeleton className="w-full" style={{ height }} />;
  }

  // Veri yoksa bilgilendirme göster
  if (!history || history.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">
            {symbol} — {interval} Grafik
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className="flex flex-col items-center justify-center text-muted-foreground"
            style={{ height }}
          >
            <BarChart3 className="h-12 w-12 mb-3 opacity-30" />
            <p className="text-sm font-medium">Grafik verisi bulunamadı</p>
            <p className="text-xs mt-1">
              Bu sembol için henüz geçmiş veri mevcut değil.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">
          {symbol} — {interval} Grafik
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div ref={chartContainerRef} />
      </CardContent>
    </Card>
  );
}
