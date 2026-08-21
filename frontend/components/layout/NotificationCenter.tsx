"use client";

import { useEffect, useRef, useState } from "react";

import { fetchWithAuth, getAccessToken, resolveApiBaseUrl } from "@/lib/auth";
import type { NotificationEvent, NotificationItem, NotificationUnreadCount } from "@/lib/catalog";
import { formatRelativeTimestamp } from "@/lib/catalog";

function BellIcon() {
  return (
    <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.86 18a3 3 0 0 1-5.72 0M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9Z" />
    </svg>
  );
}

function buildWebSocketUrl(token: string) {
  const baseUrl = resolveApiBaseUrl();
  const wsBase = baseUrl.startsWith("https://")
    ? baseUrl.replace("https://", "wss://")
    : baseUrl.replace("http://", "ws://");
  const url = new URL("/ws/notifications", wsBase);
  url.searchParams.set("token", token);
  return url.toString();
}

type NotificationCenterProps = {
  authenticated: boolean;
};

export default function NotificationCenter({ authenticated }: NotificationCenterProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const pollingRef = useRef<number | null>(null);

  useEffect(() => {
    if (!authenticated) {
      return;
    }

    let active = true;
    let socket: WebSocket | null = null;

    async function refreshNotifications() {
      setLoading(true);
      try {
        const [items, count] = await Promise.all([
          fetchWithAuth<NotificationItem[]>("/notifications"),
          fetchWithAuth<NotificationUnreadCount>("/notifications/unread-count"),
        ]);
        if (!active) {
          return;
        }
        setNotifications(items);
        setUnreadCount(count.unread_count);
        setError(null);
      } catch (requestError) {
        if (!active) {
          return;
        }
        setError(requestError instanceof Error ? requestError.message : "Unable to load notifications.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    function startPollingFallback() {
      if (pollingRef.current !== null) {
        return;
      }
      pollingRef.current = window.setInterval(() => {
        void refreshNotifications();
      }, 30000);
    }

    function stopPollingFallback() {
      if (pollingRef.current !== null) {
        window.clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }

    function upsertNotification(item: NotificationItem) {
      setNotifications((current) => {
        const existing = current.findIndex((notification) => notification.id === item.id);
        if (existing === -1) {
          return [item, ...current];
        }
        const next = [...current];
        next[existing] = item;
        return next;
      });
    }

    void refreshNotifications();

    const token = getAccessToken();
    if (token) {
      socket = new WebSocket(buildWebSocketUrl(token));
      socket.onopen = () => {
        if (!active) {
          return;
        }
        setWsConnected(true);
        stopPollingFallback();
      };
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data) as NotificationEvent | { event: string; unread_count: number };
        if (!active) {
          return;
        }
        if ("notification" in payload) {
          upsertNotification(payload.notification);
        }
        setUnreadCount(payload.unread_count);
      };
      socket.onerror = () => {
        if (!active) {
          return;
        }
        setWsConnected(false);
        startPollingFallback();
      };
      socket.onclose = () => {
        if (!active) {
          return;
        }
        setWsConnected(false);
        startPollingFallback();
      };
    } else {
      startPollingFallback();
    }

    return () => {
      active = false;
      stopPollingFallback();
      socket?.close();
    };
  }, [authenticated]);

  async function markRead(notificationId: number) {
    const updated = await fetchWithAuth<NotificationItem>(`/notifications/${notificationId}/read`, {
      method: "PUT",
    });
    setNotifications((current) =>
      current.map((notification) => (notification.id === notificationId ? updated : notification)),
    );
    setUnreadCount((current) => Math.max(0, current - 1));
  }

  async function markAllRead() {
    const payload = await fetchWithAuth<NotificationUnreadCount>("/notifications/read-all", {
      method: "PUT",
    });
    setNotifications((current) => current.map((notification) => ({ ...notification, is_read: true })));
    setUnreadCount(payload.unread_count);
  }

  async function deleteNotification(notificationId: number) {
    await fetchWithAuth<void>(`/notifications/${notificationId}`, {
      method: "DELETE",
    });
    setNotifications((current) => current.filter((notification) => notification.id !== notificationId));
  }

  return (
    <div className="relative">
      <button
        type="button"
        aria-label="View notifications"
        onClick={() => setOpen((current) => !current)}
        className="relative rounded-full p-2 transition-colors hover:bg-white/10 hover:text-[#E50914] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
      >
        <BellIcon />
        {unreadCount > 0 ? (
          <span className="absolute -right-1 -top-1 inline-flex min-h-5 min-w-5 items-center justify-center rounded-full bg-[#E50914] px-1.5 text-[10px] font-semibold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <div className="absolute right-0 top-14 w-[22rem] rounded-[1.5rem] border border-white/10 bg-[#111111] p-4 shadow-[0_24px_64px_rgba(0,0,0,0.45)]">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-white">Notifications</p>
              <p className="text-xs text-white/45">{wsConnected ? "Live updates connected" : "REST refresh fallback active"}</p>
            </div>
            <button
              type="button"
              onClick={() => void markAllRead()}
              className="text-xs font-medium text-[#ff8b92] transition hover:text-white disabled:opacity-50"
              disabled={unreadCount === 0}
            >
              Mark all read
            </button>
          </div>

          <div className="mt-4 max-h-[24rem] space-y-3 overflow-y-auto pr-1">
            {loading ? <p className="text-sm text-white/55">Loading notifications...</p> : null}
            {!loading && error ? <p className="text-sm text-[#ff9fa4]">{error}</p> : null}
            {!loading && !error && notifications.length === 0 ? (
              <p className="rounded-2xl border border-dashed border-white/10 px-4 py-6 text-center text-sm text-white/50">
                No notifications yet.
              </p>
            ) : null}
            {!loading && !error
              ? notifications.map((notification) => (
                  <article
                    key={notification.id}
                    className={`rounded-2xl border p-4 ${
                      notification.is_read ? "border-white/8 bg-white/[0.03]" : "border-[#E50914]/25 bg-[#E50914]/8"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-white">{notification.title}</p>
                        <p className="mt-2 text-sm leading-6 text-white/65">{notification.message}</p>
                        <p className="mt-3 text-xs text-white/40">{formatRelativeTimestamp(notification.created_at)}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => void deleteNotification(notification.id)}
                        className="text-xs text-white/35 transition hover:text-white"
                      >
                        Remove
                      </button>
                    </div>
                    {!notification.is_read ? (
                      <button
                        type="button"
                        onClick={() => void markRead(notification.id)}
                        className="mt-3 text-xs font-medium text-[#ff8b92] transition hover:text-white"
                      >
                        Mark as read
                      </button>
                    ) : null}
                  </article>
                ))
              : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
