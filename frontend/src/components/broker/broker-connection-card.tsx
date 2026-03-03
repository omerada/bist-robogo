"use client";

import {
  Trash2,
  TestTube,
  ToggleLeft,
  ToggleRight,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BrokerStatusBadge } from "./broker-status-badge";
import type { BrokerConnection } from "@/types/broker";

interface BrokerConnectionCardProps {
  connection: BrokerConnection;
  onTest: (id: string) => void;
  onToggle: (id: string, active: boolean) => void;
  onDelete: (id: string) => void;
  isTestLoading?: boolean;
  isToggleLoading?: boolean;
}

export function BrokerConnectionCard({
  connection,
  onTest,
  onToggle,
  onDelete,
  isTestLoading,
  isToggleLoading,
}: BrokerConnectionCardProps) {
  const lastConnected = connection.last_connected_at
    ? new Date(connection.last_connected_at).toLocaleString("tr-TR")
    : "Hiç bağlanılmadı";

  return (
    <Card className={!connection.is_active ? "opacity-60" : ""}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <CardTitle className="text-base font-semibold">
            {connection.label || connection.broker_name}
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            {connection.broker_name.toUpperCase()}
            {connection.is_paper_trading && " • Paper Trading"}
          </p>
        </div>
        <BrokerStatusBadge status={connection.status} />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Son Bağlantı</span>
            <span>{lastConnected}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Oluşturulma</span>
            <span>
              {new Date(connection.created_at).toLocaleDateString("tr-TR")}
            </span>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onTest(connection.id)}
              disabled={isTestLoading || !connection.is_active}
            >
              {isTestLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <TestTube className="h-4 w-4" />
              )}
              <span className="ml-1 hidden sm:inline">Test</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onToggle(connection.id, !connection.is_active)}
              disabled={isToggleLoading}
            >
              {isToggleLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : connection.is_active ? (
                <ToggleRight className="h-4 w-4 text-green-500" />
              ) : (
                <ToggleLeft className="h-4 w-4" />
              )}
              <span className="ml-1 hidden sm:inline">
                {connection.is_active ? "Deaktif" : "Aktif"}
              </span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className="ml-auto text-destructive hover:text-destructive"
              onClick={() => onDelete(connection.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
