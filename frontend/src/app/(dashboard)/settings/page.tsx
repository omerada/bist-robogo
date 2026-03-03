"use client";

import { useState } from "react";
import {
  Shield,
  Bell,
  User,
  Save,
  ToggleLeft,
  ToggleRight,
  Loader2,
  AlertTriangle,
  Sparkles,
  Link2,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useRiskRules,
  useUpdateRiskRule,
  useRiskStatus,
} from "@/hooks/use-risk";
import {
  useAISettings,
  useUpdateAISettings,
  useAIModels,
} from "@/hooks/use-ai";
import {
  useBrokerConnections,
  useTestBrokerConnection,
  useUpdateBrokerConnection,
  useDeleteBrokerConnection,
} from "@/hooks/use-brokers";
import { BrokerConnectionCard } from "@/components/broker/broker-connection-card";
import { AddBrokerDialog } from "@/components/broker/add-broker-dialog";
import type { RiskRule } from "@/types/risk";

// ── Kural Türü İsim Eşleme ──
const RULE_LABELS: Record<
  string,
  { label: string; description: string; unit: string }
> = {
  max_position_count: {
    label: "Maks Pozisyon Sayısı",
    description: "Aynı anda açılabilir maksimum pozisyon",
    unit: "adet",
  },
  max_position_size_pct: {
    label: "Maks Pozisyon Büyüklüğü",
    description: "Tek pozisyonun portföy oranı limiti",
    unit: "%",
  },
  daily_loss_limit_pct: {
    label: "Günlük Kayıp Limiti",
    description: "Günlük maksimum kayıp yüzdesi",
    unit: "%",
  },
  max_order_value: {
    label: "Maks Emir Değeri",
    description: "Tek emir için maksimum değer",
    unit: "₺",
  },
  stop_loss_required: {
    label: "Stop Loss Zorunlu",
    description: "Her pozisyon için stop loss gerekli mi",
    unit: "",
  },
  max_sector_exposure_pct: {
    label: "Maks Sektör Ağırlığı",
    description: "Tek sektörde maksimum portföy yüzdesi",
    unit: "%",
  },
  min_cash_reserve_pct: {
    label: "Min Nakit Rezerv",
    description: "Her zaman elde tutulacak minimum nakit yüzdesi",
    unit: "%",
  },
  max_daily_trades: {
    label: "Maks Günlük İşlem",
    description: "Günlük maksimum işlem sayısı",
    unit: "adet",
  },
  max_leverage: {
    label: "Maks Kaldıraç",
    description: "İzin verilen maksimum kaldıraç oranı",
    unit: "x",
  },
};

function RiskLevelBadge({ level }: { level: string }) {
  const colors = {
    low: "bg-green-500/10 text-green-500",
    moderate: "bg-yellow-500/10 text-yellow-500",
    high: "bg-orange-500/10 text-orange-500",
    critical: "bg-red-500/10 text-red-500",
  };
  const labels = {
    low: "Düşük",
    moderate: "Orta",
    high: "Yüksek",
    critical: "Kritik",
  };
  return (
    <Badge className={colors[level as keyof typeof colors] || colors.low}>
      {labels[level as keyof typeof labels] || level}
    </Badge>
  );
}

function RuleCard({ rule }: { rule: RiskRule }) {
  const updateMutation = useUpdateRiskRule();
  const meta = RULE_LABELS[rule.rule_type] || {
    label: rule.rule_type,
    description: "",
    unit: "",
  };
  const limitValue =
    rule.value?.limit ?? rule.value?.default_pct ?? rule.value?.enabled ?? "";
  const [editValue, setEditValue] = useState(String(limitValue));

  const handleToggle = () => {
    updateMutation.mutate(
      { ruleId: rule.id, data: { is_active: !rule.is_active } },
      {
        onSuccess: () =>
          toast.success(`Kural ${!rule.is_active ? "aktif" : "pasif"} edildi`),
        onError: () => toast.error("Güncelleme başarısız"),
      },
    );
  };

  const handleSave = () => {
    const numVal = Number(editValue);
    if (isNaN(numVal)) {
      toast.error("Geçerli bir değer girin");
      return;
    }
    updateMutation.mutate(
      { ruleId: rule.id, data: { value: { limit: numVal } } },
      {
        onSuccess: () => toast.success("Kural güncellendi"),
        onError: () => toast.error("Güncelleme başarısız"),
      },
    );
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1">
            <div className="flex items-center gap-2">
              <span className="font-medium">{meta.label}</span>
              <Badge variant={rule.is_active ? "default" : "secondary"}>
                {rule.is_active ? "Aktif" : "Pasif"}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{meta.description}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleToggle}
            disabled={updateMutation.isPending}
          >
            {rule.is_active ? (
              <ToggleRight className="h-5 w-5 text-green-500" />
            ) : (
              <ToggleLeft className="h-5 w-5 text-muted-foreground" />
            )}
          </Button>
        </div>
        {rule.rule_type !== "stop_loss_required" && (
          <div className="flex items-center gap-2 mt-4">
            <Input
              type="number"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="w-32"
            />
            <span className="text-sm text-muted-foreground">{meta.unit}</span>
            <Button
              size="sm"
              variant="outline"
              onClick={handleSave}
              disabled={
                updateMutation.isPending || editValue === String(limitValue)
              }
            >
              {updateMutation.isPending ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <Save className="h-3 w-3" />
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── AI Ayarları Tab Bileşeni ──

function AISettingsTab() {
  const { data: settings, isLoading } = useAISettings();
  const { data: modelsData } = useAIModels();
  const updateMutation = useUpdateAISettings();
  const [model, setModel] = useState("");
  const [temperature, setTemperature] = useState("");
  const [maxTokens, setMaxTokens] = useState("");

  // İlk yükleme
  useState(() => {
    if (settings) {
      setModel(settings.model);
      setTemperature(String(settings.temperature));
      setMaxTokens(String(settings.max_tokens));
    }
  });

  const handleSave = () => {
    const payload: Record<string, unknown> = {};
    if (model && model !== settings?.model) payload.model = model;
    if (temperature && Number(temperature) !== settings?.temperature)
      payload.temperature = Number(temperature);
    if (maxTokens && Number(maxTokens) !== settings?.max_tokens)
      payload.max_tokens = Number(maxTokens);

    if (Object.keys(payload).length === 0) {
      toast.info("Değişiklik yok");
      return;
    }

    updateMutation.mutate(
      payload as { model?: string; temperature?: number; max_tokens?: number },
      {
        onSuccess: () => toast.success("AI ayarları güncellendi"),
        onError: () => toast.error("Güncelleme başarısız"),
      },
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6 space-y-3">
          <div className="h-4 w-32 bg-muted animate-pulse rounded" />
          <div className="h-10 w-full bg-muted animate-pulse rounded" />
          <div className="h-10 w-full bg-muted animate-pulse rounded" />
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            OpenRouter Yapılandırması
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">API Bağlantı Durumu</p>
              <p className="text-xs text-muted-foreground">
                {settings?.base_url}
              </p>
            </div>
            <Badge
              className={
                settings?.api_key_set
                  ? "bg-green-500/10 text-green-500"
                  : "bg-red-500/10 text-red-500"
              }
            >
              {settings?.api_key_set ? "API Key Ayarlı" : "API Key Eksik"}
            </Badge>
          </div>

          <div className="space-y-2">
            <Label>Model</Label>
            <Input
              value={model || settings?.model || ""}
              onChange={(e) => setModel(e.target.value)}
              placeholder="google/gemini-2.5-flash"
            />
            <p className="text-xs text-muted-foreground">
              OpenRouter model ID (ör: google/gemini-2.5-flash,
              anthropic/claude-sonnet-4)
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Sıcaklık (Temperature)</Label>
              <Input
                type="number"
                step="0.1"
                min="0"
                max="2"
                value={temperature || String(settings?.temperature ?? 0.3)}
                onChange={(e) => setTemperature(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Maks Token</Label>
              <Input
                type="number"
                step="100"
                min="100"
                max="16384"
                value={maxTokens || String(settings?.max_tokens ?? 4096)}
                onChange={(e) => setMaxTokens(e.target.value)}
              />
            </div>
          </div>

          <Button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="w-full"
          >
            {updateMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Kaydet
          </Button>
        </CardContent>
      </Card>

      {modelsData && modelsData.models.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Kullanılabilir Modeller ({modelsData.models.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {modelsData.models.slice(0, 20).map((m) => (
                <div
                  key={m.id}
                  className="flex items-center justify-between text-sm border-b pb-2 last:border-0 cursor-pointer hover:bg-muted/50 rounded p-1"
                  onClick={() => setModel(m.id)}
                >
                  <div>
                    <p className="font-medium">{m.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">
                      {m.id}
                    </p>
                  </div>
                  {m.context_length && (
                    <Badge variant="outline" className="text-xs">
                      {(m.context_length / 1000).toFixed(0)}K ctx
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
}

// ── Broker Yönetimi Tab Bileşeni ──

function BrokerTab() {
  const { data: connectionsData, isLoading } = useBrokerConnections();
  const testMutation = useTestBrokerConnection();
  const updateMutation = useUpdateBrokerConnection();
  const deleteMutation = useDeleteBrokerConnection();

  const connections = connectionsData?.items ?? [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  return (
    <>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Broker Bağlantıları</h3>
          <p className="text-sm text-muted-foreground">
            Paper trading veya gerçek broker bağlantılarınızı yönetin
          </p>
        </div>
        <AddBrokerDialog />
      </div>

      {connections.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Link2 className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold">Henüz bağlantı yok</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Paper Trading veya gerçek broker bağlantısı ekleyerek başlayın
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {connections.map((conn) => (
            <BrokerConnectionCard
              key={conn.id}
              connection={conn}
              onTest={(id) => testMutation.mutate(id)}
              onToggle={(id, active) =>
                updateMutation.mutate({ id, data: { is_active: active } })
              }
              onDelete={(id) => deleteMutation.mutate(id)}
              isTestLoading={testMutation.isPending}
              isToggleLoading={updateMutation.isPending}
            />
          ))}
        </div>
      )}
    </>
  );
}

export default function SettingsPage() {
  const { data: rules, isLoading: rulesLoading } = useRiskRules();
  const { data: riskStatus } = useRiskStatus();

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Ayarlar</h1>
        {riskStatus && <RiskLevelBadge level={riskStatus.overall_risk} />}
      </div>

      <Tabs defaultValue="risk" className="space-y-4">
        <TabsList>
          <TabsTrigger value="risk" className="gap-2">
            <Shield className="h-4 w-4" />
            Risk Kuralları
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="h-4 w-4" />
            Bildirimler
          </TabsTrigger>
          <TabsTrigger value="profile" className="gap-2">
            <User className="h-4 w-4" />
            Profil
          </TabsTrigger>
          <TabsTrigger value="ai" className="gap-2">
            <Sparkles className="h-4 w-4" />
            AI Ayarları
          </TabsTrigger>
          <TabsTrigger value="broker" className="gap-2">
            <Link2 className="h-4 w-4" />
            Broker
          </TabsTrigger>
        </TabsList>

        {/* ── Risk Kuralları ── */}
        <TabsContent value="risk" className="space-y-4">
          {riskStatus && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Risk Seviyesi
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <RiskLevelBadge level={riskStatus.overall_risk} />
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Günlük Kayıp
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-bold">
                    ₺{Number(riskStatus.daily_loss).toLocaleString("tr-TR")} / ₺
                    {Number(riskStatus.daily_loss_limit).toLocaleString(
                      "tr-TR",
                    )}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Açık Pozisyon
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-bold">
                    {riskStatus.open_positions} / {riskStatus.max_positions}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Aktif Kural
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-bold">{riskStatus.rules_active}</p>
                </CardContent>
              </Card>
            </div>
          )}

          {rulesLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {rules?.map((rule) => (
                <RuleCard key={rule.id} rule={rule} />
              ))}
            </div>
          )}

          {riskStatus && riskStatus.recent_events.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-500" />
                  Son Risk Olayları
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {riskStatus.recent_events.map((event, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between text-sm border-b pb-2 last:border-0"
                    >
                      <span>
                        {(event.details as Record<string, string>)?.reason ||
                          event.type}
                      </span>
                      <span className="text-muted-foreground text-xs">
                        {new Date(event.created_at).toLocaleString("tr-TR")}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* ── Bildirim Ayarları ── */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Bildirim Kanalları</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">
                    Uygulama İçi Bildirimler
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Tüm bildirimler uygulama içinde gösterilir
                  </p>
                </div>
                <Badge>Her zaman aktif</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Email Bildirimleri</Label>
                  <p className="text-sm text-muted-foreground">
                    Önemli bildirimler email ile gönderilir
                  </p>
                </div>
                <Badge variant="secondary">Yapılandırma gerekli</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Telegram Bildirimleri</Label>
                  <p className="text-sm text-muted-foreground">
                    Anlık bildirimler Telegram bot ile gönderilir
                  </p>
                </div>
                <Badge variant="secondary">Yapılandırma gerekli</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Bildirim Türleri</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                {
                  type: "risk_report",
                  label: "Günlük Risk Raporu",
                  desc: "Her gün saat 18:45",
                },
                {
                  type: "order_filled",
                  label: "Emir Gerçekleşme",
                  desc: "Emir doldurulduğunda",
                },
                {
                  type: "signal",
                  label: "Sinyal Uyarısı",
                  desc: "Strateji sinyal ürettiğinde",
                },
                {
                  type: "risk_violation",
                  label: "Risk İhlali",
                  desc: "Risk kuralı ihlal edildiğinde",
                },
              ].map((item) => (
                <div
                  key={item.type}
                  className="flex items-center justify-between border-b pb-3 last:border-0"
                >
                  <div>
                    <p className="font-medium text-sm">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.desc}</p>
                  </div>
                  <Badge variant="outline">Aktif</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Profil ── */}
        <TabsContent value="profile" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Profil Bilgileri</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Ad Soyad</Label>
                  <Input placeholder="Ad Soyad" disabled />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input placeholder="email@ornek.com" disabled />
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Profil bilgileri şu an için salt okunurdur. İleride
                güncellenebilecektir.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Broker Bağlantısı</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Paper Trading</p>
                  <p className="text-sm text-muted-foreground">
                    Simülasyon modunda işlem yapın
                  </p>
                </div>
                <Badge className="bg-green-500/10 text-green-500">Aktif</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── AI Ayarları ── */}
        <TabsContent value="ai" className="space-y-4">
          <AISettingsTab />
        </TabsContent>

        {/* ── Broker Yönetimi ── */}
        <TabsContent value="broker" className="space-y-4">
          <BrokerTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
