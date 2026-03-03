/**
 * Market store — gerçek zamanlı piyasa verisi.
 */

import { create } from "zustand";
import type { Quote } from "@/types/market";

interface MarketState {
  // symbol → Quote map
  quotes: Record<string, Quote>;
  // Seçili sembol
  selectedSymbol: string | null;
  // Seçili endeks filtresi
  selectedIndex: string;

  // Actions
  updateQuote: (symbol: string, quote: Partial<Quote>) => void;
  setSelectedSymbol: (symbol: string | null) => void;
  setSelectedIndex: (index: string) => void;
  setBulkQuotes: (quotes: Record<string, Quote>) => void;
}

export const useMarketStore = create<MarketState>()((set) => ({
  quotes: {},
  selectedSymbol: null,
  selectedIndex: "XU030",

  updateQuote: (symbol, quoteUpdate) =>
    set((state) => ({
      quotes: {
        ...state.quotes,
        [symbol]: { ...state.quotes[symbol], ...quoteUpdate } as Quote,
      },
    })),

  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setSelectedIndex: (index) => set({ selectedIndex: index }),

  setBulkQuotes: (quotes) =>
    set((state) => ({
      quotes: { ...state.quotes, ...quotes },
    })),
}));
