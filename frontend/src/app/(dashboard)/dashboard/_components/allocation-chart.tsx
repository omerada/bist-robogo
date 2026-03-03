"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AllocationChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">
          Pozisyon Dağılımı
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-56 items-center justify-center text-muted-foreground">
          Pie chart burada gösterilecek
        </div>
      </CardContent>
    </Card>
  );
}
