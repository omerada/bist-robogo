import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Portföy",
};

export default function PortfolioPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Portföy</h1>
      <p className="text-muted-foreground">
        Portföy detayları, pozisyonlar ve performans metrikleri burada
        gösterilecek.
      </p>
    </div>
  );
}
