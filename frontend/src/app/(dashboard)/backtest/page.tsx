import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Backtest",
};

export default function BacktestPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Backtest</h1>
      <p className="text-muted-foreground">
        Strateji backtesting ve sonuçları burada gösterilecek.
      </p>
    </div>
  );
}
