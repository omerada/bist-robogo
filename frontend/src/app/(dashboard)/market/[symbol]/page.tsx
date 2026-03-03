"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Star, Share2, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { CandlestickChart } from "@/components/charts/candlestick-chart";
import { QuoteTicker } from "@/components/market/quote-ticker";
import { SymbolDetailSkeleton } from "@/components/shared/loading-skeleton";
import { useQuote } from "@/hooks/use-market-data";
import { useMarketStore } from "@/stores/market-store";
import { useWebSocket } from "@/hooks/use-websocket";
import { cn } from "@/lib/utils";

const INTERVALS = [
  { value: "1m", label: "1D" },
  { value: "5m", label: "5D" },
  { value: "1h", label: "1S" },
  { value: "1d", label: "1A" },
  { value: "1w", label: "1H" },
  { value: "1M", label: "Tümü" },
];

export default function SymbolDetailPage() {
  const params = useParams<{ symbol: string }>();
  const router = useRouter();
  const symbol = params.symbol?.toUpperCase() ?? "";
  const [interval, setInterval] = useState("1d");

  const { data: quote, isLoading } = useQuote(symbol);
  const wsQuote = useMarketStore((s) => s.quotes[symbol]);

  // WebSocket canlı fiyat aboneliği
  useWebSocket({
    channels: [`quote:${symbol}`],
    autoConnect: !!symbol,
  });

  // WebSocket verisi varsa onu, yoksa API verisini kullan
  const displayQuote = wsQuote ?? quote;

  if (isLoading && !displayQuote) {
    return <SymbolDetailSkeleton />;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Üst bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{symbol}</h1>
              <Badge variant="outline" className="text-xs">
                BIST
              </Badge>
            </div>
            {displayQuote && (
              <p className="text-sm text-muted-foreground">
                {displayQuote.name}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <Star className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Bell className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Share2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Fiyat bilgisi */}
      {displayQuote && (
        <QuoteTicker
          price={Number(displayQuote.price) || 0}
          change={Number(displayQuote.change) || 0}
          changePct={Number(displayQuote.change_pct) || 0}
        />
      )}

      {/* Grafik interval seçici */}
      <Tabs value={interval} onValueChange={setInterval}>
        <TabsList>
          {INTERVALS.map((iv) => (
            <TabsTrigger key={iv.value} value={iv.value}>
              {iv.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Candlestick grafik */}
      <CandlestickChart symbol={symbol} interval={interval} height={450} />

      {/* Detay kartları */}
      {displayQuote && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <DetailCard
            label="Açılış"
            value={`₺${Number(displayQuote.open).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`}
          />
          <DetailCard
            label="Yüksek"
            value={`₺${Number(displayQuote.high).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`}
            valueClassName="text-green-500"
          />
          <DetailCard
            label="Düşük"
            value={`₺${Number(displayQuote.low).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`}
            valueClassName="text-red-500"
          />
          <DetailCard
            label="Önceki Kapanış"
            value={`₺${Number(displayQuote.close_prev).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`}
          />
          <DetailCard
            label="Hacim"
            value={Number(displayQuote.volume).toLocaleString("tr-TR")}
          />
          <DetailCard
            label="Alış"
            value={`₺${Number(displayQuote.bid).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`}
          />
          <DetailCard
            label="Satış"
            value={`₺${Number(displayQuote.ask).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`}
          />
          <DetailCard
            label="Son Güncelleme"
            value={new Date(displayQuote.updated_at).toLocaleTimeString(
              "tr-TR",
            )}
          />
        </div>
      )}
    </div>
  );
}

function DetailCard({
  label,
  value,
  valueClassName,
}: {
  label: string;
  value: string;
  valueClassName?: string;
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="text-xs text-muted-foreground mb-1">{label}</div>
        <div
          className={cn("text-sm font-semibold tabular-nums", valueClassName)}
        >
          {value}
        </div>
      </CardContent>
    </Card>
  );
}
