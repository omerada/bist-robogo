import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Stratejiler",
};

export default function StrategiesPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Stratejiler</h1>
      <p className="text-muted-foreground">
        Ticaret stratejileri yönetimi burada gösterilecek.
      </p>
    </div>
  );
}
