/**
 * Emirler sayfası — emir listesi, filtreleme, iptal.
 */
"use client";

import { useState } from "react";
import {
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Loader2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useOrders, useCancelOrder } from "@/hooks/use-trading";
import { OrderForm } from "@/components/market/order-form";
import { cn } from "@/lib/utils";
import type { Order, OrderStatus } from "@/types/order";

const STATUS_FILTERS: { label: string; value: string | undefined }[] = [
  { label: "Tümü", value: undefined },
  { label: "Bekleyen", value: "pending" },
  { label: "Dolmuş", value: "filled" },
  { label: "İptal", value: "cancelled" },
  { label: "Reddedilmiş", value: "rejected" },
];

function statusIcon(status: OrderStatus) {
  switch (status) {
    case "filled":
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "cancelled":
      return <XCircle className="h-4 w-4 text-gray-400" />;
    case "rejected":
      return <AlertTriangle className="h-4 w-4 text-red-500" />;
    case "pending":
    case "submitted":
      return <Clock className="h-4 w-4 text-yellow-500" />;
    default:
      return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

function statusBadge(status: OrderStatus) {
  const variantMap: Record<
    string,
    "default" | "secondary" | "destructive" | "outline"
  > = {
    filled: "default",
    cancelled: "secondary",
    rejected: "destructive",
    pending: "outline",
    submitted: "outline",
    partial_fill: "outline",
    expired: "secondary",
  };
  return (
    <Badge variant={variantMap[status] || "outline"} className="gap-1">
      {statusIcon(status)}
      {status}
    </Badge>
  );
}

function formatCurrency(v: number | string | null) {
  if (v === null || v === undefined) return "—";
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    minimumFractionDigits: 2,
  }).format(Number(v) || 0);
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("tr-TR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function OrdersPage() {
  const [statusFilter, setStatusFilter] = useState<string | undefined>(
    undefined,
  );
  const [page, setPage] = useState(1);

  const { data, isLoading } = useOrders({
    status: statusFilter,
    page,
    per_page: 20,
  });
  const cancelOrder = useCancelOrder();

  const orders = data?.orders ?? [];
  const meta = data?.meta;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Emirler</h1>
          <p className="text-muted-foreground">Emir geçmişi ve aktif emirler</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Order list — 2/3 */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filter Tabs */}
          <Tabs
            value={statusFilter ?? "all"}
            onValueChange={(v) => {
              setStatusFilter(v === "all" ? undefined : v);
              setPage(1);
            }}
          >
            <TabsList>
              {STATUS_FILTERS.map((f) => (
                <TabsTrigger key={f.value ?? "all"} value={f.value ?? "all"}>
                  {f.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {/* Table */}
          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-6 space-y-3">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : orders.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16">
                  <FileText className="h-12 w-12 text-muted-foreground mb-3" />
                  <CardDescription>
                    Henüz emir yok. Sağdaki formdan emir oluşturabilirsiniz.
                  </CardDescription>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Sembol</TableHead>
                      <TableHead>Yön</TableHead>
                      <TableHead>Tip</TableHead>
                      <TableHead className="text-right">Miktar</TableHead>
                      <TableHead className="text-right">Fiyat</TableHead>
                      <TableHead>Durum</TableHead>
                      <TableHead>Tarih</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orders.map((order: Order) => (
                      <TableRow key={order.id}>
                        <TableCell className="font-medium">
                          {order.symbol}
                        </TableCell>
                        <TableCell>
                          <span
                            className={cn(
                              "font-semibold",
                              order.side === "buy"
                                ? "text-green-600"
                                : "text-red-600",
                            )}
                          >
                            {order.side === "buy" ? "AL" : "SAT"}
                          </span>
                        </TableCell>
                        <TableCell className="capitalize">
                          {order.order_type}
                        </TableCell>
                        <TableCell className="text-right">
                          {order.filled_quantity}/{order.quantity}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(order.filled_price ?? order.price)}
                        </TableCell>
                        <TableCell>{statusBadge(order.status)}</TableCell>
                        <TableCell className="text-muted-foreground text-xs">
                          {formatDate(order.created_at)}
                        </TableCell>
                        <TableCell>
                          {(order.status === "pending" ||
                            order.status === "submitted") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => cancelOrder.mutate(order.id)}
                              disabled={cancelOrder.isPending}
                            >
                              {cancelOrder.isPending ? (
                                <Loader2 className="h-3 w-3 animate-spin" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-500" />
                              )}
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Pagination */}
          {meta && meta.total_pages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Toplam {meta.total} emir
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Önceki
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= meta.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Sonraki
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Order form — 1/3 */}
        <div>
          <OrderForm />
        </div>
      </div>
    </div>
  );
}
