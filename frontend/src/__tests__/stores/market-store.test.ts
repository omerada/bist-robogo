import { describe, it, expect, beforeEach } from "vitest";
import { useMarketStore } from "@/stores/market-store";
import type { Quote } from "@/types/market";

// Her testten önce store'u sıfırla
beforeEach(() => {
  useMarketStore.setState({
    quotes: {},
    selectedSymbol: null,
    selectedIndex: "ALL",
  });
});

const mockQuote: Quote = {
  symbol: "THYAO",
  name: "Türk Hava Yolları",
  price: 285.5,
  change: 3.2,
  change_pct: 1.13,
  volume: 45_000_000,
  high: 288.0,
  low: 282.0,
  open: 283.0,
  close_prev: 282.3,
  bid: 285.4,
  ask: 285.6,
  bid_size: 1000,
  ask_size: 800,
  updated_at: "2026-03-05T15:30:00Z",
};

describe("useMarketStore", () => {
  describe("updateQuote", () => {
    it("yeni sembol ekler", () => {
      useMarketStore.getState().updateQuote("THYAO", mockQuote);
      const quotes = useMarketStore.getState().quotes;
      expect(quotes["THYAO"]).toBeDefined();
      expect(quotes["THYAO"].price).toBe(285.5);
    });

    it("mevcut quote'u günceller (merge)", () => {
      useMarketStore.getState().updateQuote("THYAO", mockQuote);
      useMarketStore.getState().updateQuote("THYAO", { price: 290.0 });
      const quote = useMarketStore.getState().quotes["THYAO"];
      expect(quote.price).toBe(290.0);
      expect(quote.volume).toBe(45_000_000); // eski alan korunur
    });

    it("diğer sembolleri etkilemez", () => {
      useMarketStore.getState().updateQuote("THYAO", mockQuote);
      useMarketStore.getState().updateQuote("ASELS", {
        ...mockQuote,
        symbol: "ASELS",
        price: 50.0,
      });
      expect(useMarketStore.getState().quotes["THYAO"].price).toBe(285.5);
      expect(useMarketStore.getState().quotes["ASELS"].price).toBe(50.0);
    });
  });

  describe("setSelectedSymbol", () => {
    it("sembol seçer", () => {
      useMarketStore.getState().setSelectedSymbol("THYAO");
      expect(useMarketStore.getState().selectedSymbol).toBe("THYAO");
    });

    it("null ile seçimi temizler", () => {
      useMarketStore.getState().setSelectedSymbol("THYAO");
      useMarketStore.getState().setSelectedSymbol(null);
      expect(useMarketStore.getState().selectedSymbol).toBeNull();
    });
  });

  describe("setSelectedIndex", () => {
    it("endeks filtresi değiştirir", () => {
      useMarketStore.getState().setSelectedIndex("XU030");
      expect(useMarketStore.getState().selectedIndex).toBe("XU030");
    });

    it("başlangıç değeri ALL olmalı", () => {
      expect(useMarketStore.getState().selectedIndex).toBe("ALL");
    });
  });

  describe("setBulkQuotes", () => {
    it("toplu quote ekler", () => {
      const bulkQuotes: Record<string, Quote> = {
        THYAO: mockQuote,
        ASELS: { ...mockQuote, symbol: "ASELS", price: 50.0 },
      };
      useMarketStore.getState().setBulkQuotes(bulkQuotes);
      const quotes = useMarketStore.getState().quotes;
      expect(Object.keys(quotes)).toHaveLength(2);
      expect(quotes["ASELS"].price).toBe(50.0);
    });

    it("mevcut quote'ları korur ve yenileri ekler", () => {
      useMarketStore
        .getState()
        .updateQuote("SISE", { ...mockQuote, symbol: "SISE", price: 10.0 });
      useMarketStore.getState().setBulkQuotes({
        THYAO: mockQuote,
      });
      const quotes = useMarketStore.getState().quotes;
      expect(quotes["SISE"].price).toBe(10.0);
      expect(quotes["THYAO"].price).toBe(285.5);
    });
  });
});
