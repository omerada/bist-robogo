"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  LineChart,
  TrendingUp,
  Layers,
  FlaskConical,
  Briefcase,
  ClipboardList,
  Settings,
  ChevronLeft,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/market", label: "Piyasa", icon: LineChart },
  { href: "/trends", label: "Trend Analiz", icon: TrendingUp },
  { href: "/strategies", label: "Stratejiler", icon: Layers },
  { href: "/backtest", label: "Backtest", icon: FlaskConical },
  { href: "/portfolio", label: "Portföy", icon: Briefcase },
  { href: "/orders", label: "Emirler", icon: ClipboardList },
  { href: "/ai", label: "AI Analiz", icon: Sparkles },
  { href: "/settings", label: "Ayarlar", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebarCollapse } = useUIStore();

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "relative flex h-full flex-col border-r border-border bg-card transition-all duration-300",
          sidebarCollapsed ? "w-16" : "w-60",
        )}
      >
        {/* Logo */}
        <div className="flex h-14 items-center gap-2 border-b border-border px-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            B
          </div>
          {!sidebarCollapsed && (
            <span className="text-lg font-semibold tracking-tight">
              bist-robogo
            </span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            const link = (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </Link>
            );

            if (sidebarCollapsed) {
              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>{link}</TooltipTrigger>
                  <TooltipContent side="right">{item.label}</TooltipContent>
                </Tooltip>
              );
            }

            return link;
          })}
        </nav>

        {/* Collapse button */}
        <div className="border-t border-border p-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebarCollapse}
            className="w-full justify-center"
          >
            <ChevronLeft
              className={cn(
                "h-4 w-4 transition-transform",
                sidebarCollapsed && "rotate-180",
              )}
            />
          </Button>
        </div>
      </aside>
    </TooltipProvider>
  );
}
