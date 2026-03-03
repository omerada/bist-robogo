/**
 * Emir formu — sembol detay sayfasından veya emirler sayfasından kullanılır.
 */
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";

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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCreateOrder } from "@/hooks/use-trading";
import { cn } from "@/lib/utils";

const orderSchema = z.object({
  symbol: z.string().min(1, "Sembol gerekli").max(20),
  quantity: z.coerce.number().int().positive("Miktar 0'dan büyük olmalı"),
  price: z.coerce.number().positive().optional(),
  stop_loss: z.coerce.number().positive().optional(),
  take_profit: z.coerce.number().positive().optional(),
});

type OrderFormValues = z.infer<typeof orderSchema>;

interface OrderFormProps {
  symbol?: string;
  onSuccess?: () => void;
}

export function OrderForm({ symbol, onSuccess }: OrderFormProps) {
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");

  const createOrder = useCreateOrder();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<OrderFormValues>({
    resolver: zodResolver(orderSchema),
    defaultValues: {
      symbol: symbol || "",
      quantity: 1,
    },
  });

  const onSubmit = async (values: OrderFormValues) => {
    try {
      await createOrder.mutateAsync({
        symbol: values.symbol,
        side,
        order_type: orderType,
        quantity: values.quantity,
        price: orderType === "limit" ? values.price : undefined,
        stop_loss: values.stop_loss || undefined,
        take_profit: values.take_profit || undefined,
      });
      reset();
      onSuccess?.();
    } catch {
      // Error handled by mutation
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Emir Oluştur</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Side toggle */}
          <div className="grid grid-cols-2 gap-2">
            <Button
              type="button"
              variant={side === "buy" ? "default" : "outline"}
              className={cn(
                side === "buy" && "bg-green-600 hover:bg-green-700 text-white",
              )}
              onClick={() => setSide("buy")}
            >
              AL (Buy)
            </Button>
            <Button
              type="button"
              variant={side === "sell" ? "default" : "outline"}
              className={cn(
                side === "sell" && "bg-red-600 hover:bg-red-700 text-white",
              )}
              onClick={() => setSide("sell")}
            >
              SAT (Sell)
            </Button>
          </div>

          {/* Symbol */}
          <div className="space-y-1.5">
            <Label htmlFor="symbol">Sembol</Label>
            <Input
              id="symbol"
              placeholder="THYAO"
              {...register("symbol")}
              disabled={!!symbol}
              className="uppercase"
            />
            {errors.symbol && (
              <p className="text-xs text-red-500">{errors.symbol.message}</p>
            )}
          </div>

          {/* Order type */}
          <div className="space-y-1.5">
            <Label>Emir Tipi</Label>
            <Select
              value={orderType}
              onValueChange={(v) => setOrderType(v as "market" | "limit")}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="market">Piyasa (Market)</SelectItem>
                <SelectItem value="limit">Limit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Quantity */}
          <div className="space-y-1.5">
            <Label htmlFor="quantity">Miktar (Lot)</Label>
            <Input
              id="quantity"
              type="number"
              min={1}
              {...register("quantity")}
            />
            {errors.quantity && (
              <p className="text-xs text-red-500">{errors.quantity.message}</p>
            )}
          </div>

          {/* Limit price */}
          {orderType === "limit" && (
            <div className="space-y-1.5">
              <Label htmlFor="price">Limit Fiyat (₺)</Label>
              <Input
                id="price"
                type="number"
                step="0.01"
                {...register("price")}
              />
            </div>
          )}

          {/* Stop Loss & Take Profit */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="stop_loss">Stop Loss (₺)</Label>
              <Input
                id="stop_loss"
                type="number"
                step="0.01"
                placeholder="Opsiyonel"
                {...register("stop_loss")}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="take_profit">Take Profit (₺)</Label>
              <Input
                id="take_profit"
                type="number"
                step="0.01"
                placeholder="Opsiyonel"
                {...register("take_profit")}
              />
            </div>
          </div>

          {/* Error display */}
          {createOrder.isError && (
            <p className="text-sm text-red-500">
              {(createOrder.error as Error)?.message || "Emir oluşturulamadı"}
            </p>
          )}

          {/* Success display */}
          {createOrder.isSuccess && (
            <p className="text-sm text-green-600">Emir başarıyla oluşturuldu!</p>
          )}

          {/* Submit */}
          <Button
            type="submit"
            className={cn(
              "w-full",
              side === "buy"
                ? "bg-green-600 hover:bg-green-700"
                : "bg-red-600 hover:bg-red-700",
            )}
            disabled={createOrder.isPending}
          >
            {createOrder.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            {side === "buy" ? "AL" : "SAT"} — Emir Gönder
          </Button>

          <p className="text-xs text-muted-foreground text-center">
            📝 Paper Trading — Gerçek para kullanılmaz
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
