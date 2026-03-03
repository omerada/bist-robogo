/**
 * Model karşılaştırma kartı — iki modelin performansını yan yana gösterir.
 * Doc 10 §Faz 3 Sprint 3.3
 */

import { Trophy, Clock, Target, BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AccuracyBadge } from "./accuracy-badge";
import type { AIModelComparison } from "@/types/ai";

interface ModelComparisonCardProps {
  comparison: AIModelComparison;
}

function ModelStat({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <Icon className="h-4 w-4 text-muted-foreground" />
      <span className="text-muted-foreground">{label}:</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

export function ModelComparisonCard({ comparison }: ModelComparisonCardProps) {
  const { model_a, model_b, winner, comparison_notes } = comparison;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Model Karşılaştırması
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Model A */}
          <div
            className={`rounded-lg border p-4 space-y-3 ${winner === model_a.model_id ? "border-green-500 bg-green-50/50 dark:bg-green-950/20" : ""}`}
          >
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm">
                {model_a.model_id.split("/").pop()}
              </h4>
              {winner === model_a.model_id && (
                <Badge className="bg-green-600 text-white">
                  <Trophy className="h-3 w-3 mr-1" />
                  Kazanan
                </Badge>
              )}
            </div>
            <AccuracyBadge
              rate={model_a.accuracy.accuracy_rate}
              label="Doğruluk"
            />
            <div className="space-y-1">
              <ModelStat
                label="Analiz"
                value={String(model_a.total_analyses)}
                icon={Target}
              />
              <ModelStat
                label="Ort. Gecikme"
                value={`${Number(model_a.avg_latency_ms).toFixed(0)}ms`}
                icon={Clock}
              />
              <ModelStat
                label="Ort. Skor"
                value={`${(Number(model_a.avg_score) * 100).toFixed(1)}%`}
                icon={BarChart3}
              />
            </div>
          </div>

          {/* Model B */}
          <div
            className={`rounded-lg border p-4 space-y-3 ${winner === model_b.model_id ? "border-green-500 bg-green-50/50 dark:bg-green-950/20" : ""}`}
          >
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm">
                {model_b.model_id.split("/").pop()}
              </h4>
              {winner === model_b.model_id && (
                <Badge className="bg-green-600 text-white">
                  <Trophy className="h-3 w-3 mr-1" />
                  Kazanan
                </Badge>
              )}
            </div>
            <AccuracyBadge
              rate={model_b.accuracy.accuracy_rate}
              label="Doğruluk"
            />
            <div className="space-y-1">
              <ModelStat
                label="Analiz"
                value={String(model_b.total_analyses)}
                icon={Target}
              />
              <ModelStat
                label="Ort. Gecikme"
                value={`${Number(model_b.avg_latency_ms).toFixed(0)}ms`}
                icon={Clock}
              />
              <ModelStat
                label="Ort. Skor"
                value={`${(Number(model_b.avg_score) * 100).toFixed(1)}%`}
                icon={BarChart3}
              />
            </div>
          </div>
        </div>

        {/* Notlar */}
        {comparison_notes.length > 0 && (
          <div className="mt-4 space-y-1">
            {comparison_notes.map((note, i) => (
              <p key={i} className="text-xs text-muted-foreground">
                • {note}
              </p>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
