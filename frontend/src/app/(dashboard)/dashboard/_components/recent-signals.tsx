"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ArrowUpCircle, ArrowDownCircle, MinusCircle } from "lucide-react";

interface Signal {
  id: string;
  symbol: string;
  signal_type: string;
  confidence: number;
  created_at: string | null;
}

interface RecentSignalsProps {
  signals: Signal[];
}

function signalIcon(type: string) {
  if (type === "buy" || type === "strong_buy")
    return <ArrowUpCircle className="h-4 w-4 text-emerald-500" />;
  if (type === "sell" || type === "strong_sell")
    return <ArrowDownCircle className="h-4 w-4 text-red-500" />;
  return <MinusCircle className="h-4 w-4 text-muted-foreground" />;
}

function signalBadge(type: string) {
  const map: Record<
    string,
    {
      label: string;
      variant: "default" | "destructive" | "secondary" | "outline";
    }
  > = {
    buy: { label: "AL", variant: "default" },
    strong_buy: { label: "GÜÇLÜ AL", variant: "default" },
    sell: { label: "SAT", variant: "destructive" },
    strong_sell: { label: "GÜÇLÜ SAT", variant: "destructive" },
    hold: { label: "TUT", variant: "secondary" },
  };
  const m = map[type] || {
    label: type.toUpperCase(),
    variant: "outline" as const,
  };
  return <Badge variant={m.variant}>{m.label}</Badge>;
}

export function RecentSignals({ signals }: RecentSignalsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Son Sinyaller</CardTitle>
      </CardHeader>
      <CardContent>
        {signals.length === 0 ? (
          <div className="flex h-32 items-center justify-center text-muted-foreground">
            Henüz sinyal üretilmemiş.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10"></TableHead>
                <TableHead>Sembol</TableHead>
                <TableHead>Sinyal</TableHead>
                <TableHead className="text-right">Güven</TableHead>
                <TableHead className="text-right">Tarih</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {signals.map((s) => (
                <TableRow key={s.id}>
                  <TableCell>{signalIcon(s.signal_type)}</TableCell>
                  <TableCell className="font-medium">{s.symbol}</TableCell>
                  <TableCell>{signalBadge(s.signal_type)}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    %{(Number(s.confidence) * 100).toFixed(0)}
                  </TableCell>
                  <TableCell className="text-right text-xs text-muted-foreground">
                    {s.created_at
                      ? new Date(s.created_at).toLocaleDateString("tr-TR")
                      : "-"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
