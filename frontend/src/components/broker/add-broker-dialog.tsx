"use client";

import { useState } from "react";
import { Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
  useAvailableBrokers,
  useCreateBrokerConnection,
} from "@/hooks/use-brokers";
import type { BrokerInfo, BrokerType } from "@/types/broker";

export function AddBrokerDialog() {
  const [open, setOpen] = useState(false);
  const [selectedBroker, setSelectedBroker] = useState<BrokerType | "">("");
  const [label, setLabel] = useState("");
  const [credentials, setCredentials] = useState<Record<string, string>>({});

  const { data: brokersData } = useAvailableBrokers();
  const createMutation = useCreateBrokerConnection();

  const brokers = brokersData?.brokers ?? [];
  const selectedBrokerInfo = brokers.find((b) => b.name === selectedBroker);

  const handleSubmit = async () => {
    if (!selectedBroker) return;

    await createMutation.mutateAsync({
      broker_name: selectedBroker as BrokerType,
      credentials,
      is_paper_trading: selectedBroker === "paper",
      label: label || undefined,
    });

    setOpen(false);
    setSelectedBroker("");
    setLabel("");
    setCredentials({});
  };

  const handleCredentialChange = (field: string, value: string) => {
    setCredentials((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Broker Ekle
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Yeni Broker Bağlantısı</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Broker Seçimi */}
          <div className="space-y-2">
            <Label>Broker</Label>
            <Select
              value={selectedBroker}
              onValueChange={(v) => {
                setSelectedBroker(v as BrokerType);
                setCredentials({});
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Broker seçin..." />
              </SelectTrigger>
              <SelectContent>
                {brokers.map((broker) => (
                  <SelectItem
                    key={broker.name}
                    value={broker.name}
                    disabled={!broker.is_available}
                  >
                    {broker.display_name}
                    {!broker.is_available && " (Yakında)"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedBrokerInfo && (
              <p className="text-xs text-muted-foreground">
                {selectedBrokerInfo.description}
              </p>
            )}
          </div>

          {/* Etiket */}
          <div className="space-y-2">
            <Label>Etiket (opsiyonel)</Label>
            <Input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="Bağlantı etiketi..."
            />
          </div>

          {/* Credential Alanları */}
          {selectedBrokerInfo?.requires_credentials &&
            selectedBrokerInfo.credential_fields.map((field) => (
              <div key={field} className="space-y-2">
                <Label className="capitalize">{field.replace(/_/g, " ")}</Label>
                <Input
                  type={
                    field.includes("password") || field.includes("secret")
                      ? "password"
                      : "text"
                  }
                  value={credentials[field] || ""}
                  onChange={(e) =>
                    handleCredentialChange(field, e.target.value)
                  }
                  placeholder={`${field} girin...`}
                />
              </div>
            ))}

          <Button
            onClick={handleSubmit}
            className="w-full"
            disabled={!selectedBroker || createMutation.isPending}
          >
            {createMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : null}
            Bağlantı Oluştur
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
