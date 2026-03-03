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

interface CandlestickChartProps {
  symbol: string;
  interval?: string;
  height?: number;
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
      time: d.time.split("T")[0] as string,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    const volumeData: HistogramData[] = history.map((d) => ({
      time: d.time.split("T")[0] as string,
      value: d.volume,
      color:
        d.close >= d.open
          ? chartColors.upColor + "80"
          : chartColors.downColor + "80",
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);
    chartRef.current?.timeScale().fitContent();
  }, [history, chartColors]);

  // ── Gerçek zamanlı güncelleme ──
  useEffect(() => {
    if (!quote || !candleSeriesRef.current) return;

    const today = new Date().toISOString().split("T")[0];
    candleSeriesRef.current.update({
      time: today as string,
      open: quote.open,
      high: quote.high,
      low: quote.low,
      close: quote.price,
    });
  }, [quote]);

  if (isLoading) {
    return <Skeleton className="w-full" style={{ height }} />;
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
