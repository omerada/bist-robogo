"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Clock,
  Target,
  Activity,
  Percent,
  Award,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { BacktestEquityCurve } from "@/components/charts/backtest-equity-curve";
import { BacktestPageSkeleton } from "@/components/shared/loading-skeleton";
import { useBacktestDetail, useEquityCurve } from "@/hooks/use-backtest";

export default function BacktestDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { data: backtest, isLoading } = useBacktestDetail(id);
  const { data: equityCurve } = useEquityCurve(id);

  if (isLoading) return <BacktestPageSkeleton />;
  if (!backtest) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        Backtest bulunamadı
      </div>
    );
  }

  const metrics = [
    {
      label: "Toplam Getiri",
      value: `${Number(backtest.total_return) >= 0 ? "+" : ""}${Number(backtest.total_return).toFixed(2)}%`,
      icon: TrendingUp,
      positive: Number(backtest.total_return) >= 0,
    },
    {
      label: "CAGR",
      value: `${Number(backtest.cagr).toFixed(2)}%`,
      icon: Activity,
      positive: Number(backtest.cagr) >= 0,
    },
    {
      label: "Sharpe Ratio",
      value: Number(backtest.sharpe_ratio).toFixed(3),
      icon: Award,
      positive: Number(backtest.sharpe_ratio) > 1,
    },
    {
      label: "Sortino Ratio",
      value: Number(backtest.sortino_ratio).toFixed(3),
      icon: Target,
      positive: Number(backtest.sortino_ratio) > 1,
    },
    {
      label: "Max Drawdown",
      value: `${Number(backtest.max_drawdown).toFixed(2)}%`,
      icon: TrendingDown,
      positive: Number(backtest.max_drawdown) > -10,
    },
    {
      label: "Win Rate",
      value: `${(Number(backtest.win_rate) * 100).toFixed(1)}%`,
      icon: Percent,
      positive: Number(backtest.win_rate) > 0.5,
    },
    {
      label: "Profit Factor",
      value: Number(backtest.profit_factor).toFixed(2),
      icon: BarChart3,
      positive: Number(backtest.profit_factor) > 1,
    },
    {
      label: "Ort. Holding",
      value: `${Number(backtest.avg_holding_days).toFixed(0)} gün`,
      icon: Clock,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Başlık */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/backtest")}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">
              {backtest.name || "Backtest Detay"}
            </h1>
            <StatusBadge status={backtest.status} />
          </div>
          <div className="flex gap-3 text-sm text-muted-foreground mt-1">
            <span>{backtest.symbols?.join(", ")}</span>
            <span>|</span>
            <span>
              {backtest.start_date} → {backtest.end_date}
            </span>
            <span>|</span>
            <span>
              Sermaye: ₺
              {Number(backtest.initial_capital).toLocaleString("tr-TR")}
            </span>
            <span>|</span>
            <span>İşlem: {backtest.total_trades ?? 0}</span>
          </div>
        </div>
      </div>

      {/* Metrik Kartları */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {metrics.map((m) => (
          <Card key={m.label}>
            <CardContent className="p-4 flex items-center gap-3">
              <div
                className={`p-2 rounded-lg ${m.positive === undefined ? "bg-muted" : m.positive ? "bg-emerald-500/10" : "bg-red-500/10"}`}
              >
                <m.icon
                  className={`h-4 w-4 ${m.positive === undefined ? "text-muted-foreground" : m.positive ? "text-emerald-500" : "text-red-500"}`}
                />
              </div>
              <div>
                <p className="text-[11px] text-muted-foreground">{m.label}</p>
                <p
                  className={`text-base font-bold ${m.positive === undefined ? "" : m.positive ? "text-emerald-500" : "text-red-500"}`}
                >
                  {m.value}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Equity Curve */}
      {equityCurve && (
        <BacktestEquityCurve
          data={equityCurve}
          initialCapital={Number(backtest.initial_capital)}
        />
      )}

      {/* Hata mesajı */}
      {backtest.error_message && (
        <Card className="border-destructive">
          <CardContent className="p-4 text-destructive text-sm">
            <strong>Hata:</strong> {backtest.error_message}
          </CardContent>
        </Card>
      )}

      {/* Trade Listesi */}
      {backtest.trades && backtest.trades.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>İşlem Geçmişi</span>
              <Badge variant="secondary">{backtest.trades.length} İşlem</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Sembol</TableHead>
                    <TableHead>Yön</TableHead>
                    <TableHead>Giriş Tarihi</TableHead>
                    <TableHead className="text-right">Giriş Fiyatı</TableHead>
                    <TableHead>Çıkış Tarihi</TableHead>
                    <TableHead className="text-right">Çıkış Fiyatı</TableHead>
                    <TableHead className="text-right">Adet</TableHead>
                    <TableHead className="text-right">K/Z</TableHead>
                    <TableHead className="text-right">K/Z %</TableHead>
                    <TableHead className="text-right">Süre</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {backtest.trades.map((trade) => (
                    <TableRow key={trade.id}>
                      <TableCell className="font-medium">
                        {trade.symbol}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            trade.side === "long" ? "default" : "destructive"
                          }
                        >
                          {trade.side === "long" ? "ALIŞ" : "SATIŞ"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs">
                        {trade.entry_date}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs">
                        ₺{Number(trade.entry_price).toFixed(2)}
                      </TableCell>
                      <TableCell className="text-xs">
                        {trade.exit_date ?? "—"}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs">
                        {trade.exit_price
                          ? `₺${Number(trade.exit_price).toFixed(2)}`
                          : "—"}
                      </TableCell>
                      <TableCell className="text-right">
                        {trade.quantity}
                      </TableCell>
                      <TableCell
                        className={`text-right font-mono text-xs ${Number(trade.pnl) >= 0 ? "text-emerald-500" : "text-red-500"}`}
                      >
                        {trade.pnl !== null
                          ? `₺${Number(trade.pnl).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`
                          : "—"}
                      </TableCell>
                      <TableCell
                        className={`text-right font-mono text-xs ${Number(trade.pnl_pct) >= 0 ? "text-emerald-500" : "text-red-500"}`}
                      >
                        {trade.pnl_pct !== null
                          ? `${Number(trade.pnl_pct) >= 0 ? "+" : ""}${Number(trade.pnl_pct).toFixed(2)}%`
                          : "—"}
                      </TableCell>
                      <TableCell className="text-right text-xs">
                        {trade.holding_days !== null
                          ? `${trade.holding_days}g`
                          : "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Parametreler */}
      <Card>
        <CardHeader>
          <CardTitle>Parametreler</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="bg-muted p-4 rounded-lg text-xs overflow-x-auto">
            {JSON.stringify(backtest.parameters, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<
    string,
    {
      variant: "default" | "secondary" | "destructive" | "outline";
      label: string;
    }
  > = {
    pending: { variant: "outline", label: "Bekliyor" },
    running: { variant: "secondary", label: "Çalışıyor" },
    completed: { variant: "default", label: "Tamamlandı" },
    failed: { variant: "destructive", label: "Hatalı" },
  };
  const cfg = map[status] || { variant: "outline" as const, label: status };
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>;
}
