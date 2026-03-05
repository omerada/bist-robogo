import { describe, it, expect, beforeEach } from "vitest";
import { useUIStore } from "@/stores/ui-store";

beforeEach(() => {
  useUIStore.setState({
    sidebarOpen: true,
    sidebarCollapsed: false,
  });
});

describe("useUIStore", () => {
  describe("initial state", () => {
    it("sidebar varsayılan olarak açık", () => {
      expect(useUIStore.getState().sidebarOpen).toBe(true);
    });

    it("sidebar varsayılan olarak genişletilmiş", () => {
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });
  });

  describe("toggleSidebar", () => {
    it("açıkken kapatır", () => {
      useUIStore.getState().toggleSidebar();
      expect(useUIStore.getState().sidebarOpen).toBe(false);
    });

    it("kapalıyken açar", () => {
      useUIStore.getState().toggleSidebar(); // kapat
      useUIStore.getState().toggleSidebar(); // aç
      expect(useUIStore.getState().sidebarOpen).toBe(true);
    });
  });

  describe("setSidebarOpen", () => {
    it("direkt olarak açar/kapatır", () => {
      useUIStore.getState().setSidebarOpen(false);
      expect(useUIStore.getState().sidebarOpen).toBe(false);

      useUIStore.getState().setSidebarOpen(true);
      expect(useUIStore.getState().sidebarOpen).toBe(true);
    });
  });

  describe("toggleSidebarCollapse", () => {
    it("genişletilmişken daraltır", () => {
      useUIStore.getState().toggleSidebarCollapse();
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);
    });

    it("daraltılmışken genişletir", () => {
      useUIStore.getState().toggleSidebarCollapse(); // daralt
      useUIStore.getState().toggleSidebarCollapse(); // genişlet
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });
  });
});
