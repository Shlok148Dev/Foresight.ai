/**
 * Foresight — useWebSocket Hook
 * ================================
 * Phase 2D: Real-time connection to /ws/signals or /ws/trends.
 * Auto-reconnects on disconnect, surfaces incoming messages via callback.
 */

"use client";

import { useEffect, useRef, useCallback } from "react";

const WS_BASE =
  process.env.NEXT_PUBLIC_WS_URL?.replace(/\/$/, "") ?? "ws://localhost:8000";

type WSStatus = "connecting" | "connected" | "disconnected" | "error";

interface UseWebSocketOptions {
  /** Called with every incoming JSON message */
  onMessage: (data: unknown) => void;
  /** Called when connection status changes */
  onStatusChange?: (status: WSStatus) => void;
  /** Auto-reconnect delay in ms (default 3000) */
  reconnectDelay?: number;
  /** Set false to disable the hook entirely */
  enabled?: boolean;
}

export function useWebSocket(
  channel: "signals" | "trends",
  { onMessage, onStatusChange, reconnectDelay = 3000, enabled = true }: UseWebSocketOptions
) {
  const wsRef = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!enabled || typeof window === "undefined") return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    onStatusChange?.("connecting");
    const ws = new WebSocket(`${WS_BASE}/ws/${channel}`);
    wsRef.current = ws;

    ws.onopen = () => {
      onStatusChange?.("connected");
      // Start keep-alive ping every 25 s
      timerRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) ws.send("ping");
      }, 25_000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data !== "pong") onMessage(data);
      } catch {
        // ignore non-JSON frames
      }
    };

    ws.onerror = () => onStatusChange?.("error");

    ws.onclose = () => {
      onStatusChange?.("disconnected");
      if (timerRef.current) clearInterval(timerRef.current);
      if (mountedRef.current && enabled) {
        setTimeout(connect, reconnectDelay);
      }
    };
  }, [channel, enabled, onMessage, onStatusChange, reconnectDelay]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (timerRef.current) clearInterval(timerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
}
