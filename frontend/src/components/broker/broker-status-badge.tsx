"use client";

import { Wifi, WifiOff, AlertTriangle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { BrokerStatus } from "@/types/broker";

interface StatusBadgeProps {
  status: BrokerStatus;
}

const STATUS_CONFIG: Record<
  BrokerStatus,
  {
    label: string;
    variant: "default" | "secondary" | "destructive" | "outline";
    icon: React.ReactNode;
  }
> = {
  connected: {
    label: "Bağlı",
    variant: "default",
    icon: <Wifi className="h-3 w-3" />,
  },
  disconnected: {
    label: "Bağlı Değil",
    variant: "secondary",
    icon: <WifiOff className="h-3 w-3" />,
  },
  error: {
    label: "Hata",
    variant: "destructive",
    icon: <AlertTriangle className="h-3 w-3" />,
  },
  pending: {
    label: "Bekliyor",
    variant: "outline",
    icon: <Clock className="h-3 w-3" />,
  },
};

export function BrokerStatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.disconnected;

  return (
    <Badge variant={config.variant} className="gap-1">
      {config.icon}
      {config.label}
    </Badge>
  );
}
