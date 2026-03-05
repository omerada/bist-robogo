import { Skeleton } from "@/components/ui/skeleton";

export default function TrendsLoading() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />

      {/* Tab skeleton */}
      <Skeleton className="h-10 w-64" />

      {/* Kartlar */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-48 rounded-lg" />
        ))}
      </div>
    </div>
  );
}
