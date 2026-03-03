import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Piyasa",
};

export default function MarketPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Piyasa</h1>
      <p className="text-muted-foreground">
        BIST sembol listesi ve fiyat bilgileri burada gösterilecek.
      </p>
    </div>
  );
}
