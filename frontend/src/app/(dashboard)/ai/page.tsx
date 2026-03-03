/**
 * AI Analiz sayfası — sembol analizi, sohbet, sinyaller, performans, A/B test.
 * Doc 10 §Faz 3 Sprint 3.1 + 3.3 — AI Dashboard
 */
"use client";

import { useState, useRef, useEffect } from "react";
import {
  Bot,
  Send,
  Sparkles,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Brain,
  MessageSquare,
  Zap,
  Search,
  AlertTriangle,
  BarChart3,
  FlaskConical,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useAIAnalysis,
  useAIChat,
  useAISignals,
  useAIPerformance,
  useExperiments,
  useRunExperiment,
  useDeleteExperiment,
} from "@/hooks/use-ai";
import { PerformanceChart } from "@/components/ai/performance-chart";
import { AccuracyBadge } from "@/components/ai/accuracy-badge";
import { ExperimentCard } from "@/components/ai/experiment-card";
import { ExperimentForm } from "@/components/ai/experiment-form";
import type {
  AIAnalysisResponse,
  AIChatMessage,
  AISignalResponse,
} from "@/types/ai";

// ── Sinyal renk ve ikon eşlemesi ──

function getActionBadge(action: string) {
  switch (action) {
    case "buy":
      return (
        <Badge className="bg-green-600 hover:bg-green-700 text-white">
          <TrendingUp className="w-3 h-3 mr-1" />
          AL
        </Badge>
      );
    case "sell":
      return (
        <Badge className="bg-red-600 hover:bg-red-700 text-white">
          <TrendingDown className="w-3 h-3 mr-1" />
          SAT
        </Badge>
      );
    default:
      return (
        <Badge variant="secondary">
          <Minus className="w-3 h-3 mr-1" />
          TUT
        </Badge>
      );
  }
}

function getConfidenceBadge(confidence: string) {
  switch (confidence) {
    case "high":
      return <Badge className="bg-emerald-500 text-white">Yüksek</Badge>;
    case "medium":
      return <Badge className="bg-amber-500 text-white">Orta</Badge>;
    default:
      return <Badge variant="outline">Düşük</Badge>;
  }
}

// ── Analiz Tab ──

function AnalysisTab() {
  const [symbol, setSymbol] = useState("");
  const [result, setResult] = useState<AIAnalysisResponse | null>(null);
  const analysis = useAIAnalysis();

  const handleAnalyze = () => {
    if (!symbol.trim()) return;
    analysis.mutate(
      { symbol: symbol.toUpperCase(), include_indicators: true },
      {
        onSuccess: (data) => setResult(data),
      },
    );
  };

  return (
    <div className="space-y-4">
      {/* Arama */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Sembol girin (ör: THYAO)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
            className="pl-10"
          />
        </div>
        <Button
          onClick={handleAnalyze}
          disabled={analysis.isPending || !symbol.trim()}
        >
          {analysis.isPending ? (
            <RefreshCw className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <Brain className="h-4 w-4 mr-2" />
          )}
          Analiz Et
        </Button>
      </div>

      {/* Yükleniyor */}
      {analysis.isPending && (
        <Card>
          <CardContent className="p-6 space-y-3">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardContent>
        </Card>
      )}

      {/* Hata */}
      {analysis.isError && (
        <Card className="border-destructive">
          <CardContent className="p-6 flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            <p className="text-destructive">
              Analiz yapılamadı. Lütfen tekrar deneyin.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Sonuç */}
      {result && !analysis.isPending && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                {result.symbol} AI Analizi
              </CardTitle>
              <div className="flex gap-2">
                {getActionBadge(result.action)}
                {getConfidenceBadge(result.confidence)}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Özet */}
            <div>
              <h4 className="font-semibold text-sm text-muted-foreground mb-1">
                Özet
              </h4>
              <p className="text-sm">{result.summary}</p>
            </div>

            {/* Gerekçe */}
            <div>
              <h4 className="font-semibold text-sm text-muted-foreground mb-1">
                Detaylı Gerekçe
              </h4>
              <p className="text-sm whitespace-pre-wrap">{result.reasoning}</p>
            </div>

            {/* Anahtar Faktörler */}
            {result.key_factors.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                  Anahtar Faktörler
                </h4>
                <div className="flex flex-wrap gap-2">
                  {result.key_factors.map((f, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {f}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Fiyat Seviyeleri */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {result.target_price && (
                <div className="bg-muted/50 rounded-lg p-3 text-center">
                  <p className="text-xs text-muted-foreground">Hedef Fiyat</p>
                  <p className="text-lg font-bold text-green-600">
                    ₺{result.target_price.toFixed(2)}
                  </p>
                </div>
              )}
              {result.stop_loss && (
                <div className="bg-muted/50 rounded-lg p-3 text-center">
                  <p className="text-xs text-muted-foreground">Zarar Durdur</p>
                  <p className="text-lg font-bold text-red-600">
                    ₺{result.stop_loss.toFixed(2)}
                  </p>
                </div>
              )}
              <div className="bg-muted/50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">Risk Seviyesi</p>
                <p className="text-lg font-bold capitalize">
                  {result.risk_level === "high"
                    ? "Yüksek"
                    : result.risk_level === "medium"
                      ? "Orta"
                      : "Düşük"}
                </p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">Model</p>
                <p className="text-xs font-mono truncate">
                  {result.model_used}
                </p>
              </div>
            </div>

            {/* Göstergeler */}
            {result.indicators && (
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                  Teknik Göstergeler
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  {result.indicators.rsi !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">RSI:</span>{" "}
                      <span className="font-mono">{result.indicators.rsi}</span>
                    </div>
                  )}
                  {result.indicators.macd !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">MACD:</span>{" "}
                      <span className="font-mono">
                        {result.indicators.macd}
                      </span>
                    </div>
                  )}
                  {result.indicators.adx !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">ADX:</span>{" "}
                      <span className="font-mono">{result.indicators.adx}</span>
                    </div>
                  )}
                  {result.indicators.sma_20 !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">SMA20:</span>{" "}
                      <span className="font-mono">
                        {result.indicators.sma_20}
                      </span>
                    </div>
                  )}
                  {result.indicators.volume_ratio !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">Vol Ratio:</span>{" "}
                      <span className="font-mono">
                        {result.indicators.volume_ratio}
                      </span>
                    </div>
                  )}
                  {result.indicators.support_level !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">Destek:</span>{" "}
                      <span className="font-mono">
                        ₺{result.indicators.support_level}
                      </span>
                    </div>
                  )}
                  {result.indicators.resistance_level !== null && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">Direnç:</span>{" "}
                      <span className="font-mono">
                        ₺{result.indicators.resistance_level}
                      </span>
                    </div>
                  )}
                  {result.indicators.obv_trend && (
                    <div className="bg-muted/30 rounded p-2">
                      <span className="text-muted-foreground">OBV:</span>{" "}
                      <span className="font-mono">
                        {result.indicators.obv_trend}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ── Sohbet Tab ──

function ChatTab() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<AIChatMessage[]>([]);
  const [replies, setReplies] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const chatMutation = useAIChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [replies]);

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return;

    const userMsg: AIChatMessage = { role: "user", content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setReplies((prev) => [...prev, { role: "user", content: input }]);
    setInput("");

    chatMutation.mutate(
      { messages: newMessages },
      {
        onSuccess: (data) => {
          const assistantMsg: AIChatMessage = {
            role: "assistant",
            content: data.reply,
          };
          setMessages((prev) => [...prev, assistantMsg]);
          setReplies((prev) => [
            ...prev,
            { role: "assistant", content: data.reply },
          ]);
        },
        onError: () => {
          setReplies((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Yanıt alınamadı. Lütfen tekrar deneyin.",
            },
          ]);
        },
      },
    );
  };

  return (
    <div className="flex flex-col h-[600px]">
      {/* Mesajlar */}
      <div className="flex-1 overflow-y-auto space-y-3 p-4 bg-muted/20 rounded-t-lg">
        {replies.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <Bot className="h-12 w-12 mb-3 opacity-50" />
            <p className="text-sm">BIST yatırım asistanı ile sohbet edin</p>
            <p className="text-xs mt-1">
              Hisseler, teknik analiz, piyasa durumu hakkında soru
              sorabilirsiniz
            </p>
          </div>
        )}

        {replies.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              {msg.role === "assistant" && (
                <Bot className="h-3 w-3 inline mr-1 opacity-70" />
              )}
              <span className="whitespace-pre-wrap">{msg.content}</span>
            </div>
          </div>
        ))}

        {chatMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-foreground/30 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-foreground/30 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-foreground/30 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2 p-3 border-t bg-background rounded-b-lg">
        <Input
          placeholder="Mesajınızı yazın..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          disabled={chatMutation.isPending}
        />
        <Button
          size="icon"
          onClick={handleSend}
          disabled={chatMutation.isPending || !input.trim()}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

// ── Sinyaller Tab ──

function SignalsTab() {
  const { data, isLoading, isError, refetch, isFetching } = useAISignals(10);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          AI tarafından üretilmiş en güncel alım/satım sinyalleri
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${isFetching ? "animate-spin" : ""}`}
          />
          Yenile
        </Button>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      )}

      {isError && (
        <Card className="border-destructive">
          <CardContent className="p-4 flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            <p className="text-sm text-destructive">
              Sinyaller yüklenemedi. OpenRouter API anahtarınızı kontrol edin.
            </p>
          </CardContent>
        </Card>
      )}

      {data && data.signals.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            <Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Henüz sinyal üretilmedi.</p>
          </CardContent>
        </Card>
      )}

      {data &&
        data.signals.map((signal: AISignalResponse, i: number) => (
          <Card key={i} className="hover:bg-muted/30 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-lg">{signal.symbol}</span>
                  {getActionBadge(signal.action)}
                  {getConfidenceBadge(signal.confidence)}
                </div>
                <div className="text-right">
                  <div className="text-sm font-mono">
                    Skor: {(signal.score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {signal.reason}
              </p>
            </CardContent>
          </Card>
        ))}

      {data && data.model_used && (
        <p className="text-xs text-muted-foreground text-center">
          Model: {data.model_used} ·{" "}
          {new Date(data.generated_at).toLocaleString("tr-TR")}
        </p>
      )}
    </div>
  );
}

// ── Performans Tab ──

function PerformanceTab() {
  const { data, isLoading, isError } = useAIPerformance({ days: 30 });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-[300px] w-full" />
        <div className="grid grid-cols-3 gap-4">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <Card className="border-destructive">
        <CardContent className="p-4 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive">
            Performans verileri yüklenemedi.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.models.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground">
          <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>Henüz performans verisi yok.</p>
          <p className="text-xs mt-1">
            AI analiz kullandıkça performans metrikleri burada görünecek.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Özet Kartlar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">Toplam Analiz</p>
            <p className="text-2xl font-bold">{data.total_analyses}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">Genel Doğruluk</p>
            <AccuracyBadge rate={data.overall_accuracy} />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">Model Sayısı</p>
            <p className="text-2xl font-bold">{data.models.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Grafik */}
      <PerformanceChart models={data.models} />

      {/* Model Detayları */}
      <div className="space-y-3">
        {data.models.map((model) => (
          <Card key={model.model_id}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-sm">
                    {model.model_id.split("/").pop()}
                  </h4>
                  <p className="text-xs text-muted-foreground font-mono">
                    {model.model_id}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <AccuracyBadge
                    rate={model.accuracy.accuracy_rate}
                    label="Doğruluk"
                  />
                  <Badge variant="outline" className="text-xs">
                    {model.total_analyses} analiz
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {model.avg_latency_ms.toFixed(0)}ms
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ── A/B Test Tab ──

function ABTestTab() {
  const { data, isLoading, refetch } = useExperiments();
  const runMutation = useRunExperiment();
  const deleteMutation = useDeleteExperiment();

  return (
    <div className="space-y-4">
      {/* Form */}
      <ExperimentForm onCreated={() => refetch()} />

      {/* Deney Listesi */}
      <div className="space-y-3">
        <h3 className="font-semibold text-sm text-muted-foreground">
          Deneyler
        </h3>

        {isLoading && (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        )}

        {data && data.experiments.length === 0 && (
          <Card>
            <CardContent className="p-8 text-center text-muted-foreground">
              <FlaskConical className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>Henüz deney oluşturulmadı.</p>
            </CardContent>
          </Card>
        )}

        {data?.experiments.map((exp) => (
          <ExperimentCard
            key={exp.id}
            experiment={exp}
            onRun={(id) => runMutation.mutate(id)}
            onDelete={(id) => deleteMutation.mutate(id)}
            isRunning={runMutation.isPending}
          />
        ))}
      </div>
    </div>
  );
}

// ── Ana Sayfa ──

export default function AIPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <Sparkles className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Analiz</h1>
          <p className="text-muted-foreground text-sm">
            Yapay zeka destekli piyasa analizi, sohbet, sinyaller, performans ve
            A/B test
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="analysis" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="analysis" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            <span className="hidden sm:inline">Analiz</span>
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            <span className="hidden sm:inline">Sohbet</span>
          </TabsTrigger>
          <TabsTrigger value="signals" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            <span className="hidden sm:inline">Sinyaller</span>
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">Performans</span>
          </TabsTrigger>
          <TabsTrigger value="abtest" className="flex items-center gap-2">
            <FlaskConical className="h-4 w-4" />
            <span className="hidden sm:inline">A/B Test</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="analysis" className="mt-4">
          <AnalysisTab />
        </TabsContent>

        <TabsContent value="chat" className="mt-4">
          <ChatTab />
        </TabsContent>

        <TabsContent value="signals" className="mt-4">
          <SignalsTab />
        </TabsContent>

        <TabsContent value="performance" className="mt-4">
          <PerformanceTab />
        </TabsContent>

        <TabsContent value="abtest" className="mt-4">
          <ABTestTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
