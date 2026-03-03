import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ayarlar",
};

export default function SettingsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Ayarlar</h1>
      <p className="text-muted-foreground">
        Kullanıcı profili, bildirim tercihleri ve broker bağlantı ayarları
        burada yönetilecek.
      </p>
    </div>
  );
}
