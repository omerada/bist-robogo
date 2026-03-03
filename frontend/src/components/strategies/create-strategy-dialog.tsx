/**
 * Yeni strateji oluşturma dialog'u.
 */
"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { StrategyCreateRequest } from "@/types/strategy";

interface CreateStrategyDialogProps {
  onSubmit: (req: StrategyCreateRequest) => void;
  isPending?: boolean;
}

const STRATEGY_TYPES = [
  {
    value: "ma_crossover",
    label: "MA Çapraz (Golden/Death Cross)",
    description: "Hareketli ortalama kesişimlerini takip eder",
  },
  {
    value: "rsi_reversal",
    label: "RSI Dönüş (Mean Reversion)",
    description: "Aşırı alım/satım bölgelerinde dönüş sinyali",
  },
];

const INDEX_OPTIONS = [
  { value: "XU030", label: "BIST 30" },
  { value: "XU100", label: "BIST 100" },
  { value: "XKTUM", label: "Tüm Piyasa" },
];

export function CreateStrategyDialog({
  onSubmit,
  isPending,
}: CreateStrategyDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [strategyType, setStrategyType] = useState("ma_crossover");
  const [indexFilter, setIndexFilter] = useState("XU030");
  const [timeframe, setTimeframe] = useState("daily");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;

    onSubmit({
      name: name.trim(),
      description: description.trim() || undefined,
      strategy_type: strategyType,
      index_filter: indexFilter,
      timeframe,
    });

    // Reset form
    setName("");
    setDescription("");
    setStrategyType("ma_crossover");
    setIndexFilter("XU030");
    setTimeframe("daily");
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Yeni Strateji
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[480px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Yeni Strateji Oluştur</DialogTitle>
            <DialogDescription>
              Otomatik sinyal üreten bir ticaret stratejisi tanımlayın.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* İsim */}
            <div className="space-y-2">
              <Label htmlFor="strategy-name">Strateji Adı</Label>
              <Input
                id="strategy-name"
                placeholder="ör. BIST30 Altın Çapraz"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            {/* Açıklama */}
            <div className="space-y-2">
              <Label htmlFor="strategy-desc">Açıklama (opsiyonel)</Label>
              <Input
                id="strategy-desc"
                placeholder="Strateji hakkında kısa not"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Tip */}
            <div className="space-y-2">
              <Label>Strateji Tipi</Label>
              <Select value={strategyType} onValueChange={setStrategyType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {STRATEGY_TYPES.map((st) => (
                    <SelectItem key={st.value} value={st.value}>
                      <div>
                        <div className="font-medium">{st.label}</div>
                        <div className="text-xs text-muted-foreground">
                          {st.description}
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Endeks */}
            <div className="space-y-2">
              <Label>Endeks Filtresi</Label>
              <Select value={indexFilter} onValueChange={setIndexFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {INDEX_OPTIONS.map((idx) => (
                    <SelectItem key={idx.value} value={idx.value}>
                      {idx.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Zaman Dilimi */}
            <div className="space-y-2">
              <Label>Zaman Dilimi</Label>
              <Select value={timeframe} onValueChange={setTimeframe}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Günlük</SelectItem>
                  <SelectItem value="weekly">Haftalık</SelectItem>
                  <SelectItem value="monthly">Aylık</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              İptal
            </Button>
            <Button type="submit" disabled={!name.trim() || isPending}>
              {isPending ? "Oluşturuluyor..." : "Oluştur"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
