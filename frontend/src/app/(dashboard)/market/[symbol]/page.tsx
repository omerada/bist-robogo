import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sembol Detay",
};

export default function SymbolDetailPage({
  params,
}: {
  params: { symbol: string };
}) {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">{params.symbol}</h1>
      <p className="text-muted-foreground">
        Sembol detay sayfası — grafik, order book ve emir formu burada
        gösterilecek.
      </p>
    </div>
  );
}
