"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Link from "next/link";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[DashboardError]", error);
  }, [error]);

  return (
    <div className="flex flex-1 items-center justify-center p-6">
      <Card className="mx-auto max-w-lg border-destructive/20">
        <CardContent className="pt-6">
          <div className="space-y-6 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10">
              <AlertTriangle className="h-7 w-7 text-destructive" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-semibold tracking-tight">
                Sayfa Yüklenemedi
              </h2>
              <p className="text-sm text-muted-foreground">
                Bu sayfada bir hata oluştu. Sorunu çözmeye çalışıyoruz.
              </p>
              {error.message && process.env.NODE_ENV === "development" && (
                <pre className="mt-3 max-h-32 overflow-auto rounded-md bg-muted p-3 text-left font-mono text-xs text-muted-foreground">
                  {error.message}
                </pre>
              )}
            </div>
            <div className="flex justify-center gap-3">
              <Button onClick={reset} size="sm">
                <RefreshCw className="mr-2 h-4 w-4" />
                Tekrar Dene
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/dashboard">
                  <Home className="mr-2 h-4 w-4" />
                  Dashboard
                </Link>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
