"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[GlobalError]", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <div className="mx-auto max-w-md space-y-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
          <AlertTriangle className="h-8 w-8 text-destructive" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight">
            Beklenmeyen Bir Hata Oluştu
          </h1>
          <p className="text-muted-foreground">
            Bir şeyler yanlış gitti. Lütfen sayfayı yenilemeyi deneyin.
          </p>
          {error.digest && (
            <p className="font-mono text-xs text-muted-foreground">
              Hata Kodu: {error.digest}
            </p>
          )}
        </div>
        <div className="flex justify-center gap-3">
          <Button onClick={reset} variant="default">
            <RefreshCw className="mr-2 h-4 w-4" />
            Tekrar Dene
          </Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = "/dashboard")}
          >
            Ana Sayfaya Dön
          </Button>
        </div>
      </div>
    </div>
  );
}
