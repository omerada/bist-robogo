"use client";

import { useState, useMemo } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SymbolTable } from "@/components/market/symbol-table";
import { MarketPageSkeleton } from "@/components/shared/loading-skeleton";
import { useSymbols, useIndices } from "@/hooks/use-market-data";
import { useMarketStore } from "@/stores/market-store";

const DEFAULT_INDICES = [
  { code: "ALL", name: "Tümü" },
  { code: "XU030", name: "BIST 30" },
  { code: "XU100", name: "BIST 100" },
  { code: "XKTUM", name: "Katılım" },
];

export default function MarketPage() {
  const [search, setSearch] = useState("");
  const selectedIndex = useMarketStore((s) => s.selectedIndex);
  const setSelectedIndex = useMarketStore((s) => s.setSelectedIndex);

  const { data: indicesData } = useIndices();
  const { data, isLoading } = useSymbols({
    index_code: selectedIndex === "ALL" ? undefined : selectedIndex,
    search: search.length >= 2 ? search : undefined,
    per_page: 100,
  });

  const indices = useMemo(() => {
    if (!indicesData) return DEFAULT_INDICES;
    return [
      { code: "ALL", name: "Tümü" },
      ...indicesData.map((i) => ({ code: i.code, name: i.name })),
    ];
  }, [indicesData]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Başlık */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Piyasa</h1>
          <p className="text-sm text-muted-foreground">
            BIST sembol listesi ve fiyat bilgileri
          </p>
        </div>
        {data && (
          <span className="text-sm text-muted-foreground">
            {data.meta.total} sembol
          </span>
        )}
      </div>

      {/* Endeks filtreleri */}
      <Tabs
        value={selectedIndex}
        onValueChange={(val) => setSelectedIndex(val)}
      >
        <TabsList>
          {indices.map((idx) => (
            <TabsTrigger key={idx.code} value={idx.code}>
              {idx.name}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Arama */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Sembol veya şirket ara..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Tablo */}
      {isLoading ? (
        <MarketPageSkeleton />
      ) : (
        <SymbolTable symbols={data?.symbols ?? []} isLoading={isLoading} />
      )}
    </div>
  );
}
