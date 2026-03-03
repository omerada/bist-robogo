import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Emirler",
};

export default function OrdersPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Emirler</h1>
      <p className="text-muted-foreground">
        Aktif ve geçmiş emirler burada listelenecek.
      </p>
    </div>
  );
}
