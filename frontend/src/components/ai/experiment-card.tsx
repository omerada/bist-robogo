/**
 * Deney kartı — tek bir A/B test deneyini gösterir.
 * Doc 10 §Faz 3 Sprint 3.3
 */

import {
  Play,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AIExperimentResponse } from "@/types/ai";

interface ExperimentCardProps {
  experiment: AIExperimentResponse;
  onRun?: (id: string) => void;
  onDelete?: (id: string) => void;
  onClick?: (id: string) => void;
  isRunning?: boolean;
}

function statusBadge(status: string) {
  switch (status) {
    case "completed":
      return (
        <Badge className="bg-green-600 text-white">
          <CheckCircle className="h-3 w-3 mr-1" />
          Tamamlandı
        </Badge>
      );
    case "running":
      return (
        <Badge className="bg-blue-600 text-white">
          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          Çalışıyor
        </Badge>
      );
    case "failed":
      return (
        <Badge className="bg-red-600 text-white">
          <XCircle className="h-3 w-3 mr-1" />
          Başarısız
        </Badge>
      );
    default:
      return (
        <Badge variant="secondary">
          <Clock className="h-3 w-3 mr-1" />
          Bekliyor
        </Badge>
      );
  }
}

export function ExperimentCard({
  experiment,
  onRun,
  onDelete,
  onClick,
  isRunning,
}: ExperimentCardProps) {
  return (
    <Card
      className="hover:bg-muted/30 transition-colors cursor-pointer"
      onClick={() => onClick?.(experiment.id)}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h4 className="font-semibold">{experiment.name}</h4>
            {experiment.description && (
              <p className="text-sm text-muted-foreground">
                {experiment.description}
              </p>
            )}
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-mono">
                {experiment.model_a.split("/").pop()}
              </span>
              <span>vs</span>
              <span className="font-mono">
                {experiment.model_b.split("/").pop()}
              </span>
              <span>·</span>
              <span>{experiment.symbols.length} sembol</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {statusBadge(experiment.status)}
            {experiment.status === "pending" && onRun && (
              <Button
                size="sm"
                variant="outline"
                disabled={isRunning}
                onClick={(e) => {
                  e.stopPropagation();
                  onRun(experiment.id);
                }}
              >
                {isRunning ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            )}
            {onDelete && (
              <Button
                size="sm"
                variant="ghost"
                className="text-destructive hover:text-destructive"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(experiment.id);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        {experiment.completed_at && (
          <p className="text-xs text-muted-foreground mt-2">
            Tamamlanma:{" "}
            {new Date(experiment.completed_at).toLocaleString("tr-TR")}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
