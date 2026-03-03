"use client";

import { useRouter } from "next/navigation";
import { Moon, Sun, Search, Menu } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/stores/auth-store";
import { useUIStore } from "@/stores/ui-store";
import { NotificationBell } from "./notification-bell";

export function Header() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const user = useAuthStore((s) => s.user);
  const logoutStore = useAuthStore((s) => s.logout);
  const { toggleSidebar } = useUIStore();

  const handleLogout = async () => {
    try {
      const { logout: logoutApi } = await import("@/lib/api/auth");
      await logoutApi();
    } catch {
      // API hatası olsa bile store'u temizle
    }
    logoutStore();
    router.push("/login");
  };

  const initials =
    user?.full_name
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2) || "??";

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4">
      {/* Sol: Hamburger + Arama */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={toggleSidebar}
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div className="relative hidden md:block">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Sembol ara... (ör: THYAO)"
            className="w-64 pl-8 bg-secondary/50"
          />
        </div>
      </div>

      {/* Sağ: Tema + Bildirim + Profil */}
      <div className="flex items-center gap-2">
        {/* Tema değiştir */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Tema değiştir</span>
        </Button>

        {/* Bildirimler */}
        <NotificationBell />

        {/* Profil */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Avatar className="h-8 w-8 cursor-pointer">
              <AvatarFallback className="bg-primary/10 text-primary text-xs font-medium">
                {initials}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem
              className="text-xs text-muted-foreground"
              disabled
            >
              {user?.email}
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <a href="/settings">Ayarlar</a>
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive"
              onClick={handleLogout}
            >
              Çıkış Yap
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
