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

interface RecentOrder {
  id: string;
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  price: number | null;
  status: string;
  created_at: string | null;
}

interface RecentOrdersProps {
  orders: RecentOrder[];
}

function statusBadge(status: string) {
  const map: Record<
    string,
    {
      label: string;
      variant: "default" | "destructive" | "secondary" | "outline";
    }
  > = {
    filled: { label: "Gerçekleşti", variant: "default" },
    pending: { label: "Bekliyor", variant: "secondary" },
    cancelled: { label: "İptal", variant: "destructive" },
    rejected: { label: "Reddedildi", variant: "destructive" },
    partial: { label: "Kısmi", variant: "outline" },
  };
  const m = map[status] || { label: status, variant: "outline" as const };
  return <Badge variant={m.variant}>{m.label}</Badge>;
}

export function RecentOrders({ orders }: RecentOrdersProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Son Emirler</CardTitle>
      </CardHeader>
      <CardContent>
        {orders.length === 0 ? (
          <div className="flex h-32 items-center justify-center text-muted-foreground">
            Henüz emir verilmemiş.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sembol</TableHead>
                <TableHead>Yön</TableHead>
                <TableHead>Tip</TableHead>
                <TableHead className="text-right">Adet</TableHead>
                <TableHead className="text-right">Fiyat</TableHead>
                <TableHead>Durum</TableHead>
                <TableHead className="text-right">Tarih</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {orders.map((o) => (
                <TableRow key={o.id}>
                  <TableCell className="font-medium">{o.symbol}</TableCell>
                  <TableCell>
                    <span
                      className={
                        o.side === "buy"
                          ? "text-emerald-600 font-medium"
                          : "text-red-600 font-medium"
                      }
                    >
                      {o.side === "buy" ? "AL" : "SAT"}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs uppercase">
                    {o.order_type}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {Number(o.quantity) || 0}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {o.price
                      ? `₺${Number(o.price).toLocaleString("tr-TR")}`
                      : "-"}
                  </TableCell>
                  <TableCell>{statusBadge(o.status)}</TableCell>
                  <TableCell className="text-right text-xs text-muted-foreground">
                    {o.created_at
                      ? new Date(o.created_at).toLocaleDateString("tr-TR")
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
