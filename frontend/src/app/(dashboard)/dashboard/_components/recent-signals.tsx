"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RecentSignals() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Son Sinyaller</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-32 items-center justify-center text-muted-foreground">
          Sinyal tablosu burada gösterilecek
        </div>
      </CardContent>
    </Card>
  );
}
