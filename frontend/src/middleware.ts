import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Next.js Middleware — sunucu tarafında auth koruması.
 *
 * Çalışma mantığı:
 * 1. Public route'lara (login, register, health) erişime izin ver
 * 2. Dashboard route'larında auth-storage cookie/localStorage kontrolü yap
 * 3. Token yoksa /login'e redirect et
 *
 * NOT: Next.js middleware edge runtime'da çalıştığı için
 * localStorage'a erişemez. Cookie tabanlı kontrol yapıyoruz.
 * Client-side AuthGuard ek bir güvenlik katmanı sağlar.
 */

// ── Public route'lar (auth gerektirmeyen) ──
const PUBLIC_ROUTES = ["/login", "/register"];
const PUBLIC_PREFIXES = ["/api", "/_next", "/favicon.ico", "/manifest.json"];

function isPublicRoute(pathname: string): boolean {
  // Tam eşleşen public route'lar
  if (PUBLIC_ROUTES.includes(pathname)) return true;

  // Root sayfası (redirect to dashboard olacak)
  if (pathname === "/") return true;

  // Statik dosya ve API prefix'leri
  if (PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix)))
    return true;

  return false;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public route ise devam et
  if (isPublicRoute(pathname)) {
    return NextResponse.next();
  }

  // Auth kontrolü — auth-storage cookie'sinde token var mı?
  // Zustand persist middleware localStorage kullanır, cookie'ye de yazar
  // Alternatif: Cookie-based token kontrolü
  const authStorage = request.cookies.get("auth-storage")?.value;

  if (authStorage) {
    try {
      const parsed = JSON.parse(authStorage);
      const state = parsed?.state;
      if (state?.accessToken && state?.isAuthenticated) {
        return NextResponse.next();
      }
    } catch {
      // Parse hatası — login'e yönlendir
    }
  }

  // Token yok ama Authorization header varsa izin ver (API çağrıları)
  const authHeader = request.headers.get("authorization");
  if (authHeader?.startsWith("Bearer ")) {
    return NextResponse.next();
  }

  // Kimlik doğrulanmamış — login'e yönlendir
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("redirect", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  /*
   * Matcher: Tüm sayfa route'larını eşle, statik dosyaları hariç tut.
   * https://nextjs.org/docs/app/building-your-application/routing/middleware#matcher
   */
  matcher: ["/((?!_next/static|_next/image|favicon.ico|manifest.json|api).*)"],
};
