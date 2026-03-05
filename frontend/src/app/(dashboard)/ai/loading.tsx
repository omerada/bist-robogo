import { Skeleton } from "@/components/ui/skeleton";

export default function AILoading() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-36" />

      {/* Tab skeleton */}
      <Skeleton className="h-10 w-80" />

      {/* İçerik */}
      <div className="space-y-4">
        <Skeleton className="h-64 rounded-lg" />
        <Skeleton className="h-48 rounded-lg" />
      </div>
    </div>
  );
}
