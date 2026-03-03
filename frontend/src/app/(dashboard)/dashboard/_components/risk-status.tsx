"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RiskStatus() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Risk Durumu</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-32 items-center justify-center text-muted-foreground">
          Risk gauge burada gösterilecek
        </div>
      </CardContent>
    </Card>
  );
}
