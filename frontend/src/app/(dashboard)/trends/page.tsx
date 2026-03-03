import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Trend Analiz",
};

export default function TrendsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Trend Analiz</h1>
      <p className="text-muted-foreground">
        AI destekli trend adayları ve sektörel analiz burada gösterilecek.
      </p>
    </div>
  );
}
