/**
 * Deney sonuçları — her model × sembol kombinasyonunun sonucunu gösterir.
 * Doc 10 §Faz 3 Sprint 3.3
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { AIExperimentResponse } from "@/types/ai";

interface ExperimentResultsProps {
  experiment: AIExperimentResponse;
}

function actionIcon(action: string) {
  switch (action) {
    case "buy":
      return <TrendingUp className="h-3 w-3 text-green-600" />;
    case "sell":
      return <TrendingDown className="h-3 w-3 text-red-600" />;
    default:
      return <Minus className="h-3 w-3" />;
  }
}

export function ExperimentResults({ experiment }: ExperimentResultsProps) {
  if (experiment.results.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-muted-foreground">
          Deney henüz çalıştırılmadı veya sonuç yok.
        </CardContent>
      </Card>
    );
  }

  // Sonuçları sembol → model bazında grupla
  const bySymbol = new Map<
    string,
    {
      model_a: (typeof experiment.results)[0] | null;
      model_b: (typeof experiment.results)[0] | null;
    }
  >();

  for (const r of experiment.results) {
    if (!bySymbol.has(r.symbol)) {
      bySymbol.set(r.symbol, { model_a: null, model_b: null });
    }
    const entry = bySymbol.get(r.symbol)!;
    if (r.model_id === experiment.model_a) {
      entry.model_a = r;
    } else {
      entry.model_b = r;
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Deney Sonuçları</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-3">Sembol</th>
                <th className="text-center py-2 px-3">
                  {experiment.model_a.split("/").pop()}
                </th>
                <th className="text-center py-2 px-3">
                  {experiment.model_b.split("/").pop()}
                </th>
              </tr>
            </thead>
            <tbody>
              {Array.from(bySymbol.entries()).map(
                ([symbol, { model_a, model_b }]) => (
                  <tr key={symbol} className="border-b last:border-0">
                    <td className="py-2 px-3 font-semibold">{symbol}</td>
                    <td className="py-2 px-3 text-center">
                      {model_a ? (
                        <div className="flex items-center justify-center gap-1">
                          {actionIcon(model_a.action)}
                          <span className="font-mono text-xs">
                            {(model_a.score * 100).toFixed(0)}%
                          </span>
                          <Badge variant="outline" className="text-xs ml-1">
                            {model_a.latency_ms}ms
                          </Badge>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="py-2 px-3 text-center">
                      {model_b ? (
                        <div className="flex items-center justify-center gap-1">
                          {actionIcon(model_b.action)}
                          <span className="font-mono text-xs">
                            {(model_b.score * 100).toFixed(0)}%
                          </span>
                          <Badge variant="outline" className="text-xs ml-1">
                            {model_b.latency_ms}ms
                          </Badge>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
