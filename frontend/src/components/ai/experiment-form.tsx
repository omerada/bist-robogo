/**
 * Deney oluşturma formu.
 * Doc 10 §Faz 3 Sprint 3.3
 */
"use client";

import { useState } from "react";
import { Plus, FlaskConical } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateExperiment } from "@/hooks/use-ai";

interface ExperimentFormProps {
  onCreated?: () => void;
}

const DEFAULT_SYMBOLS = ["THYAO", "ASELS", "KCHOL", "SAHOL", "SISE"];

export function ExperimentForm({ onCreated }: ExperimentFormProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [modelA, setModelA] = useState("google/gemini-2.5-flash");
  const [modelB, setModelB] = useState("openai/gpt-4o-mini");
  const [symbolsText, setSymbolsText] = useState(DEFAULT_SYMBOLS.join(", "));

  const createMutation = useCreateExperiment();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !modelA.trim() || !modelB.trim()) return;

    const symbols = symbolsText
      .split(",")
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);

    createMutation.mutate(
      {
        name,
        description: description || undefined,
        model_a: modelA,
        model_b: modelB,
        symbols,
      },
      {
        onSuccess: () => {
          setName("");
          setDescription("");
          onCreated?.();
        },
      },
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <FlaskConical className="h-5 w-5" />
          Yeni A/B Test Deneyi
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Deney Adı</Label>
              <Input
                id="name"
                placeholder="Ör: Gemini vs GPT-4o"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Açıklama (opsiyonel)</Label>
              <Input
                id="description"
                placeholder="Kısa açıklama"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="modelA">Model A</Label>
              <Input
                id="modelA"
                placeholder="google/gemini-2.5-flash"
                value={modelA}
                onChange={(e) => setModelA(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="modelB">Model B</Label>
              <Input
                id="modelB"
                placeholder="openai/gpt-4o-mini"
                value={modelB}
                onChange={(e) => setModelB(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="symbols">Semboller (virgülle ayırın)</Label>
            <Input
              id="symbols"
              placeholder="THYAO, ASELS, KCHOL..."
              value={symbolsText}
              onChange={(e) => setSymbolsText(e.target.value)}
              required
            />
          </div>

          <Button
            type="submit"
            disabled={createMutation.isPending || !name.trim()}
          >
            <Plus className="h-4 w-4 mr-2" />
            {createMutation.isPending ? "Oluşturuluyor..." : "Deney Oluştur"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
