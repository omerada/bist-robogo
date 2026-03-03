"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function EquityCurve() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Portföy Eğrisi</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-56 items-center justify-center text-muted-foreground">
          Equity curve grafiği burada gösterilecek
        </div>
      </CardContent>
    </Card>
  );
}
