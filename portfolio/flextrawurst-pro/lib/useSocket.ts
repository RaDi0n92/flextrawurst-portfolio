"use client";

import { useEffect, useRef, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useWeltStore } from "@/store/useWeltStore";
import type { WeltstromEvent } from "@/lib/api";

let globalSocket: Socket | null = null;

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const { addWeltstromEvent, setSocketConnected } = useWeltStore();

  const connect = useCallback(() => {
    if (globalSocket?.connected) {
      socketRef.current = globalSocket;
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL ?? "";
    const socket = io(wsUrl || undefined!, {
      path: "/api/ws/socket.io",
      transports: ["websocket", "polling"],
      reconnectionAttempts: 5,
      reconnectionDelay: 2000,
    });

    socket.on("connect", () => {
      setSocketConnected(true);
      socket.emit("subscribe", { channel: "weltstrom" });
      socket.emit("subscribe", { channel: "denkstream" });
    });

    socket.on("disconnect", () => {
      setSocketConnected(false);
    });

    function toEvent(data: Record<string, unknown>, type?: string): WeltstromEvent {
      return {
        id: (data.id as string) ?? `evt-${Date.now()}`,
        event_type: (data.event_type as string) ?? type ?? "unknown",
        entity_id: data.entity_id as string | undefined,
        entity_name: (data.entity_name ?? data.actor_name) as string | undefined,
        entity_farbe: (data.entity_farbe ?? data.actor_farbe) as string | undefined,
        inhalt: (data.inhalt ?? data.text) as string | undefined,
        data: data.data as Record<string, unknown> | undefined,
        payload: data.payload as Record<string, unknown> | undefined,
        created_at: (data.created_at ?? data.ts ?? new Date().toISOString()) as string,
      };
    }

    socket.on("weltstrom_event", (data: Record<string, unknown>) => {
      addWeltstromEvent(toEvent(data, "weltstrom_event"));
    });

    socket.on("welt_event", (data: Record<string, unknown>) => {
      addWeltstromEvent(toEvent(data, "welt_event"));
    });

    socket.on("post_created", (data: Record<string, unknown>) => {
      addWeltstromEvent(toEvent(data, "post_created"));
    });

    socket.on("wesen_event", (data: Record<string, unknown>) => {
      addWeltstromEvent(toEvent(data, "wesen_event"));
    });

    socket.on("denkstream_entry", (data: Record<string, unknown>) => {
      addWeltstromEvent(toEvent(data, "denkstream"));
    });

    globalSocket = socket;
    socketRef.current = socket;
  }, [addWeltstromEvent, setSocketConnected]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      globalSocket = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      // Socket bleibt global – kein Disconnect beim Unmount
    };
  }, []);

  return { connect, disconnect, socket: socketRef.current };
}
