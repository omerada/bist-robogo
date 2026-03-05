import { describe, it, expect, beforeEach, vi } from "vitest";
import { useAuthStore } from "@/stores/auth-store";

// Mock api client
vi.mock("@/lib/api/client", () => ({
  setAccessToken: vi.fn(),
  default: {
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

// Her testte store'u sıfırla
beforeEach(() => {
  useAuthStore.setState({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isLoading: true,
  });
  // Cookie temizle
  document.cookie = "auth-storage=; path=/; max-age=0; SameSite=Lax";
});

const mockUser = {
  id: "user-1",
  email: "test@example.com",
  full_name: "Test Kullanıcı",
  role: "user",
};

describe("useAuthStore", () => {
  describe("initial state", () => {
    it("başlangıçta authenticated değil", () => {
      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
      expect(state.accessToken).toBeNull();
    });

    it("başlangıçta isLoading true", () => {
      expect(useAuthStore.getState().isLoading).toBe(true);
    });
  });

  describe("setUser", () => {
    it("kullanıcı ve token set eder", () => {
      useAuthStore.getState().setUser(mockUser, "jwt-token-123");
      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.accessToken).toBe("jwt-token-123");
      expect(state.isAuthenticated).toBe(true);
      expect(state.isLoading).toBe(false);
    });

    it("cookie'ye auth state yazar", () => {
      useAuthStore.getState().setUser(mockUser, "jwt-token-123");
      expect(document.cookie).toContain("auth-storage=");
    });
  });

  describe("logout", () => {
    it("tüm state'i sıfırlar", () => {
      // Önce giriş yap
      useAuthStore.getState().setUser(mockUser, "jwt-token-123");
      // Sonra çıkış yap
      useAuthStore.getState().logout();
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.accessToken).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });

    it("cookie'yi temizler", () => {
      useAuthStore.getState().setUser(mockUser, "jwt-token-123");
      useAuthStore.getState().logout();
      // max-age=0 ile temizlenir
      expect(document.cookie).not.toContain("jwt-token-123");
    });
  });

  describe("setLoading", () => {
    it("loading durumunu değiştirir", () => {
      useAuthStore.getState().setLoading(false);
      expect(useAuthStore.getState().isLoading).toBe(false);

      useAuthStore.getState().setLoading(true);
      expect(useAuthStore.getState().isLoading).toBe(true);
    });
  });
});
