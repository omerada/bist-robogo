import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Giriş Yap",
};

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md space-y-6 rounded-xl border bg-card p-8 shadow-lg">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-bold tracking-tight">BIST Robogo</h1>
          <p className="text-sm text-muted-foreground">
            Hesabınıza giriş yapın
          </p>
        </div>

        {/* Login form will be implemented in Sprint 1 */}
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="email">
              E-posta
            </label>
            <input
              id="email"
              type="email"
              placeholder="ornek@email.com"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="password">
              Şifre
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <button className="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90">
            Giriş Yap
          </button>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          Hesabınız yok mu?{" "}
          <a
            href="/register"
            className="text-primary underline-offset-4 hover:underline"
          >
            Kayıt Olun
          </a>
        </p>
      </div>
    </div>
  );
}
