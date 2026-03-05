/**
 * Auth store — kullanıcı oturumu yönetimi.
 *
 * persist middleware ile localStorage'a kaydedilir.
 * Hydration tamamlandığında isLoading → false yapılır,
 * böylece AuthGuard skeleton'da takılı kalmaz.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { setAccessToken } from "@/lib/api/client";

/**
 * Auth cookie senkronizasyonu — Next.js middleware için.
 * Middleware (edge runtime) localStorage'a erişemez,
 * bu nedenle auth state'i cookie'ye de yazıyoruz.
 */
function syncAuthCookie(accessToken: string | null, isAuthenticated: boolean) {
  if (typeof document === "undefined") return;
  if (accessToken && isAuthenticated) {
    const value = JSON.stringify({
      state: { accessToken, isAuthenticated },
    });
    document.cookie = `auth-storage=${encodeURIComponent(value)}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
  } else {
    document.cookie = "auth-storage=; path=/; max-age=0; SameSite=Lax";
  }
}

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User, token: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,

      setUser: (user, token) => {
        setAccessToken(token);
        syncAuthCookie(token, true);
        set({
          user,
          accessToken: token,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () => {
        setAccessToken(null);
        syncAuthCookie(null, false);
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Hydration tamamlandığında token'ı axios'a yükle ve loading'i kapat
        if (state) {
          if (state.accessToken) {
            setAccessToken(state.accessToken);
          }
          // Middleware için cookie'ye de yaz
          syncAuthCookie(state.accessToken, state.isAuthenticated);
          state.setLoading(false);
        }
      },
    },
  ),
);
