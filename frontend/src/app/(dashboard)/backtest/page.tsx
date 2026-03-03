"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Play,
  Trash2,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Clock,
  BarChart3,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { BacktestPageSkeleton } from "@/components/shared/loading-skeleton";
import {
  useBacktestList,
  useRunBacktest,
  useDeleteBacktest,
} from "@/hooks/use-backtest";
import { useStrategies } from "@/hooks/use-strategies";
import type { BacktestResult } from "@/types/backtest";

const backtestSchema = z.object({
  strategy_id: z.string().min(1, "Strateji seçiniz"),
  name: z.string().optional(),
  symbols: z.string().min(1, "En az bir sembol giriniz"),
  start_date: z.string().min(1, "Başlangıç tarihi gerekli"),
  end_date: z.string().min(1, "Bitiş tarihi gerekli"),
  initial_capital: z.coerce.number().min(1000, "Minimum ₺1.000"),
  commission_rate: z.coerce.number().min(0).max(0.1),
  slippage_rate: z.coerce.number().min(0).max(0.1),
});

type BacktestFormData = z.infer<typeof backtestSchema>;

export default function BacktestPage() {
  const router = useRouter();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const { data: backtestData, isLoading } = useBacktestList({
    status: statusFilter,
  });
  const { data: strategiesData } = useStrategies();
  const runMutation = useRunBacktest();
  const deleteMutation = useDeleteBacktest();

  const form = useForm<BacktestFormData>({
    resolver: zodResolver(backtestSchema),
    defaultValues: {
      initial_capital: 1000000,
      commission_rate: 0.001,
      slippage_rate: 0.0005,
      start_date: getDefaultStartDate(),
      end_date: getDefaultEndDate(),
    },
  });

  const onSubmit = async (values: BacktestFormData) => {
    try {
      await runMutation.mutateAsync({
        strategy_id: values.strategy_id,
        name: values.name || undefined,
        symbols: values.symbols
          .split(",")
          .map((s) => s.trim().toUpperCase())
          .filter(Boolean),
        start_date: values.start_date,
        end_date: values.end_date,
        initial_capital: values.initial_capital,
        commission_rate: values.commission_rate,
        slippage_rate: values.slippage_rate,
      });
      toast.success("Backtest başarıyla tamamlandı");
      setDialogOpen(false);
      form.reset();
    } catch {
      toast.error("Backtest başlatılamadı");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id);
      toast.success("Backtest silindi");
    } catch {
      toast.error("Backtest silinemedi");
    }
  };

  if (isLoading) return <BacktestPageSkeleton />;

  const backtests = backtestData?.data ?? [];
  const stats = computeStats(backtests);
  const strategies = strategiesData?.strategies ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Başlık */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Backtest</h1>
          <p className="text-muted-foreground text-sm">
            Stratejilerinizi geçmiş veriler üzerinde test edin
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Play className="mr-2 h-4 w-4" />
              Yeni Backtest
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Backtest Çalıştır</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-4 pt-2"
            >
              {/* Strateji */}
              <div className="space-y-2">
                <Label>Strateji</Label>
                <Select
                  onValueChange={(v) => form.setValue("strategy_id", v)}
                  defaultValue=""
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Strateji seçin" />
                  </SelectTrigger>
                  <SelectContent>
                    {strategies.map((s) => (
                      <SelectItem key={s.id} value={s.id}>
                        {s.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {form.formState.errors.strategy_id && (
                  <p className="text-destructive text-xs">
                    {form.formState.errors.strategy_id.message}
                  </p>
                )}
              </div>

              {/* Ad */}
              <div className="space-y-2">
                <Label>Backtest Adı (opsiyonel)</Label>
                <Input
                  placeholder="Ör: BIST30 MA Crossover 2024"
                  {...form.register("name")}
                />
              </div>

              {/* Semboller */}
              <div className="space-y-2">
                <Label>Semboller (virgülle ayırın)</Label>
                <Input
                  placeholder="THYAO, GARAN, ASELS"
                  {...form.register("symbols")}
                />
                {form.formState.errors.symbols && (
                  <p className="text-destructive text-xs">
                    {form.formState.errors.symbols.message}
                  </p>
                )}
              </div>

              {/* Tarihler */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Başlangıç</Label>
                  <Input type="date" {...form.register("start_date")} />
                </div>
                <div className="space-y-2">
                  <Label>Bitiş</Label>
                  <Input type="date" {...form.register("end_date")} />
                </div>
              </div>

              {/* Sermaye */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Sermaye (₺)</Label>
                  <Input
                    type="number"
                    step="1000"
                    {...form.register("initial_capital")}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Komisyon</Label>
                  <Input
                    type="number"
                    step="0.0001"
                    {...form.register("commission_rate")}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Slippage</Label>
                  <Input
                    type="number"
                    step="0.0001"
                    {...form.register("slippage_rate")}
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={runMutation.isPending}
              >
                {runMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Çalıştırılıyor...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Backtest Başlat
                  </>
                )}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* İstatistik Kartları */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Toplam Backtest"
          value={stats.total.toString()}
          icon={BarChart3}
        />
        <StatCard
          title="Ort. Getiri"
          value={`${stats.avgReturn >= 0 ? "+" : ""}${stats.avgReturn.toFixed(1)}%`}
          icon={TrendingUp}
          positive={stats.avgReturn >= 0}
        />
        <StatCard
          title="En İyi"
          value={`${stats.bestReturn >= 0 ? "+" : ""}${stats.bestReturn.toFixed(1)}%`}
          icon={TrendingUp}
          positive={stats.bestReturn >= 0}
        />
        <StatCard
          title="En Kötü"
          value={`${stats.worstReturn >= 0 ? "+" : ""}${stats.worstReturn.toFixed(1)}%`}
          icon={TrendingDown}
          positive={stats.worstReturn >= 0}
        />
      </div>

      {/* Filtre */}
      <div className="flex gap-2">
        {["all", "completed", "pending", "running", "failed"].map((s) => (
          <Button
            key={s}
            variant={
              (s === "all" && !statusFilter) || statusFilter === s
                ? "default"
                : "outline"
            }
            size="sm"
            onClick={() => setStatusFilter(s === "all" ? undefined : s)}
          >
            {statusLabels[s] || s}
          </Button>
        ))}
      </div>

      {/* Backtest Listesi */}
      {backtests.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <BarChart3 className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p className="font-medium">Henüz backtest bulunmuyor</p>
            <p className="text-sm mt-1">
              Yeni bir backtest başlatmak için &quot;Yeni Backtest&quot;
              butonuna tıklayın
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {backtests.map((bt) => (
            <BacktestRow
              key={bt.id}
              backtest={bt}
              onDelete={handleDelete}
              onNavigate={() => router.push(`/backtest/${bt.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ── Yardımcı Bileşenler ──

function StatCard({
  title,
  value,
  icon: Icon,
  positive,
}: {
  title: string;
  value: string;
  icon: React.ElementType;
  positive?: boolean;
}) {
  return (
    <Card>
      <CardContent className="p-4 flex items-center gap-3">
        <div
          className={`p-2 rounded-lg ${positive === undefined ? "bg-muted" : positive ? "bg-emerald-500/10" : "bg-red-500/10"}`}
        >
          <Icon
            className={`h-4 w-4 ${positive === undefined ? "text-muted-foreground" : positive ? "text-emerald-500" : "text-red-500"}`}
          />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{title}</p>
          <p className="text-lg font-bold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function BacktestRow({
  backtest,
  onDelete,
  onNavigate,
}: {
  backtest: BacktestResult;
  onDelete: (id: string) => void;
  onNavigate: () => void;
}) {
  return (
    <Card className="hover:bg-accent/50 transition-colors">
      <CardContent className="p-4 flex items-center justify-between">
        <div
          className="flex-1 cursor-pointer flex items-center gap-4"
          onClick={onNavigate}
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <p className="font-medium">
                {backtest.name || "İsimsiz Backtest"}
              </p>
              <StatusBadge status={backtest.status} />
            </div>
            <div className="flex gap-3 text-xs text-muted-foreground">
              <span>{backtest.symbols?.join(", ") || "—"}</span>
              <span>
                {backtest.start_date} → {backtest.end_date}
              </span>
              <span>
                ₺{Number(backtest.initial_capital).toLocaleString("tr-TR")}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {backtest.status === "completed" && (
            <div className="flex gap-4 text-sm">
              <MetricChip
                label="Getiri"
                value={`${Number(backtest.total_return) >= 0 ? "+" : ""}${Number(backtest.total_return).toFixed(2)}%`}
                positive={Number(backtest.total_return) >= 0}
              />
              <MetricChip
                label="Sharpe"
                value={Number(backtest.sharpe_ratio).toFixed(2)}
              />
              <MetricChip
                label="İşlem"
                value={String(backtest.total_trades ?? 0)}
              />
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(backtest.id);
            }}
          >
            <Trash2 className="h-4 w-4 text-muted-foreground" />
          </Button>
          <ChevronRight
            className="h-4 w-4 text-muted-foreground cursor-pointer"
            onClick={onNavigate}
          />
        </div>
      </CardContent>
    </Card>
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

function MetricChip({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive?: boolean;
}) {
  return (
    <div className="text-center">
      <p className="text-[10px] text-muted-foreground">{label}</p>
      <p
        className={`font-semibold text-xs ${positive === undefined ? "" : positive ? "text-emerald-500" : "text-red-500"}`}
      >
        {value}
      </p>
    </div>
  );
}

// ── Utility ──

const statusLabels: Record<string, string> = {
  all: "Tümü",
  completed: "Tamamlanan",
  pending: "Bekleyen",
  running: "Çalışan",
  failed: "Hatalı",
};

function computeStats(backtests: BacktestResult[]) {
  const completed = backtests.filter((b) => b.status === "completed");
  const returns = completed
    .map((b) => Number(b.total_return ?? 0))
    .filter((r) => !isNaN(r));

  return {
    total: backtests.length,
    avgReturn: returns.length
      ? returns.reduce((a, b) => a + b, 0) / returns.length
      : 0,
    bestReturn: returns.length ? Math.max(...returns) : 0,
    worstReturn: returns.length ? Math.min(...returns) : 0,
  };
}

function getDefaultStartDate(): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 1);
  return d.toISOString().split("T")[0];
}

function getDefaultEndDate(): string {
  return new Date().toISOString().split("T")[0];
}
