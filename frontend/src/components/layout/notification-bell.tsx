// Source: Doc 09 ikon kılavuzu — Notification bell bileşeni
"use client";

import { Bell, Check, CheckCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  useNotifications,
  useUnreadCount,
  useMarkNotificationRead,
  useMarkAllRead,
} from "@/hooks/use-notifications";

export function NotificationBell() {
  const { data: unreadCount = 0 } = useUnreadCount();
  const { data: notifData } = useNotifications({ per_page: 10 });
  const markReadMutation = useMarkNotificationRead();
  const markAllMutation = useMarkAllRead();

  const notifications = notifData?.data || [];

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative h-9 w-9">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
          <span className="sr-only">Bildirimler</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="flex items-center justify-between px-4 py-3">
          <h4 className="text-sm font-semibold">Bildirimler</h4>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs gap-1"
              onClick={() => markAllMutation.mutate()}
            >
              <CheckCheck className="h-3 w-3" />
              Tümünü oku
            </Button>
          )}
        </div>
        <Separator />
        <ScrollArea className="h-64">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Bell className="mb-2 h-8 w-8 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">
                Henüz bildirim yok
              </p>
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent cursor-pointer ${
                    !notification.is_read ? "bg-accent/50" : ""
                  }`}
                  onClick={() => {
                    if (!notification.is_read) {
                      markReadMutation.mutate(notification.id);
                    }
                  }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium">{notification.title}</p>
                    {!notification.is_read && (
                      <span className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {notification.body}
                  </p>
                  <p className="text-[10px] text-muted-foreground/60 mt-1">
                    {new Date(notification.sent_at).toLocaleString("tr-TR")}
                  </p>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
