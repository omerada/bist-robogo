"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RecentOrders() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Son Emirler</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-32 items-center justify-center text-muted-foreground">
          Emir tablosu burada gösterilecek
        </div>
      </CardContent>
    </Card>
  );
}
