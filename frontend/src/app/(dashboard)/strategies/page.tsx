/**
 * Strateji Yönetimi sayfası — strateji listesi, oluşturma, kontrol.
 * Doc 04 §2.5 wireframe'ine göre: header + yeni strateji butonu + kart listesi.
 */
"use client";

import { useState } from "react";
import { Activity, AlertTriangle, RefreshCw, Layers } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
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
import {
  useStrategies,
  useCreateStrategy,
  useActivateStrategy,
  useDeactivateStrategy,
  useDeleteStrategy,
} from "@/hooks/use-strategies";
import { StrategyCard } from "@/components/strategies/strategy-card";
import { CreateStrategyDialog } from "@/components/strategies/create-strategy-dialog";
import { toast } from "sonner";

export default function StrategiesPage() {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [activeFilter, setActiveFilter] = useState<string>("all");

  const params = {
    ...(typeFilter !== "all" && { strategy_type: typeFilter }),
    ...(activeFilter !== "all" && { is_active: activeFilter === "active" }),
    per_page: 50,
  };

  const { data, isLoading, isError, refetch, isFetching } =
    useStrategies(params);
  const createMutation = useCreateStrategy();
  const activateMutation = useActivateStrategy();
  const deactivateMutation = useDeactivateStrategy();
  const deleteMutation = useDeleteStrategy();

  const strategies = data?.strategies ?? [];

  const activeCount = strategies.filter((s) => s.is_active).length;

  function handleActivate(id: string) {
    activateMutation.mutate(id, {
      onSuccess: () => toast.success("Strateji aktifleştirildi"),
      onError: () => toast.error("Strateji aktifleştirilemedi"),
    });
  }

  function handleDeactivate(id: string) {
    deactivateMutation.mutate(id, {
      onSuccess: () => toast.success("Strateji durduruldu"),
      onError: () => toast.error("Strateji durdurulamadı"),
    });
  }

  function handleDelete(id: string) {
    if (!window.confirm("Bu stratejiyi silmek istediğinize emin misiniz?")) {
      return;
    }
    deleteMutation.mutate(id, {
      onSuccess: () => toast.success("Strateji silindi"),
      onError: () => toast.error("Strateji silinemedi"),
    });
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Layers className="h-6 w-6" />
            Strateji Yönetimi
          </h1>
          <p className="text-muted-foreground text-sm">
            Otomatik ticaret stratejileri oluşturun ve yönetin
          </p>
        </div>

        <div className="flex items-center gap-2">
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
          <CreateStrategyDialog
            onSubmit={(req) =>
              createMutation.mutate(req, {
                onSuccess: () => toast.success("Strateji oluşturuldu"),
                onError: () => toast.error("Strateji oluşturulamadı"),
              })
            }
            isPending={createMutation.isPending}
          />
        </div>
      </div>

      {/* Filtreler + Özet */}
      <div className="flex flex-wrap items-center gap-3">
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Tip" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tüm Tipler</SelectItem>
            <SelectItem value="ma_crossover">MA Çapraz</SelectItem>
            <SelectItem value="rsi_reversal">RSI Dönüş</SelectItem>
          </SelectContent>
        </Select>

        <Select value={activeFilter} onValueChange={setActiveFilter}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Durum" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tüm Durumlar</SelectItem>
            <SelectItem value="active">Aktif</SelectItem>
            <SelectItem value="inactive">Pasif</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2 text-xs text-muted-foreground ml-auto">
          <Badge variant="outline" className="text-[10px]">
            <Activity className="h-3 w-3 mr-1" />
            {activeCount} aktif
          </Badge>
          <Badge variant="outline" className="text-[10px]">
            {strategies.length} toplam
          </Badge>
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-5 w-12" />
                </div>
                <Skeleton className="h-4 w-full" />
                <div className="grid grid-cols-2 gap-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                </div>
                <Skeleton className="h-3 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Error */}
      {isError && (
        <Card className="border-red-200 bg-red-50 dark:bg-red-950/20">
          <CardContent className="flex items-center gap-3 py-6">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <div>
              <p className="font-medium text-red-800 dark:text-red-200">
                Stratejiler yüklenemedi
              </p>
              <p className="text-sm text-red-600 dark:text-red-400">
                Lütfen giriş yaptığınızdan emin olun.
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

      {/* Strategy Cards */}
      {!isLoading && !isError && (
        <>
          {strategies.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Layers className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  Henüz strateji yok
                </h3>
                <p className="text-muted-foreground mb-4">
                  İlk stratejinizi oluşturarak otomatik sinyal üretmeye
                  başlayın.
                </p>
                <CreateStrategyDialog
                  onSubmit={(req) =>
                    createMutation.mutate(req, {
                      onSuccess: () => toast.success("Strateji oluşturuldu"),
                      onError: () => toast.error("Strateji oluşturulamadı"),
                    })
                  }
                  isPending={createMutation.isPending}
                />
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {strategies.map((strategy) => (
                <StrategyCard
                  key={strategy.id}
                  strategy={strategy}
                  onActivate={handleActivate}
                  onDeactivate={handleDeactivate}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
