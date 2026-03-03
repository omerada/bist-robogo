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
        set({
          user,
          accessToken: token,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () => {
        setAccessToken(null);
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
          state.setLoading(false);
        }
      },
    },
  ),
);
