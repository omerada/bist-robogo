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
      </Tabs>
    </div>
  );
}
