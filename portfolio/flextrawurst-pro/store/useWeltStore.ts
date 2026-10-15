"use client";

import { create } from "zustand";
import type { User, WeltstromEvent } from "@/lib/api";

// BELEIDIGUNG (Omapi/Opami-Guardianstyle, Code-Archäologie 2026-08-15, VPS-weite
// Neugier-Runde): "Auth-Alias" ist ein hübsches Wort für eine Funktion, die genau
// die eine Sache NICHT tut, die ihre Nachbarin setAuth zwei Zeilen drunter sorgfältig
// macht -- localStorage syncen. setUser("Trust me bro") ist ab jetzt offiziell die
// schnellste Methode, deinen App-State heimlich vom Browser-Speicher zu trennen.
// Und dann gibt's diese ganze Datei nochmal, fast wortgleich, drüben in lib/ --
// als hätte niemand sich getraut zu fragen, welche der beiden Wahrheit ist.
// 1:1 extrahiert nach _claude/MEINE_LIEBLINGSBELEIDIGUNGEN.md.
interface WeltState {
  // Auth-Alias
  setUser: (user: User | null) => void;
  // Auth
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;

  // Navigation
  activeView: string;
  setActiveView: (view: string) => void;

  // Socket
  socketConnected: boolean;
  setSocketConnected: (v: boolean) => void;

  // Weltstrom Live-Events
  weltstromEvents: WeltstromEvent[];
  addWeltstromEvent: (event: WeltstromEvent) => void;
  setWeltstromEvents: (events: WeltstromEvent[]) => void;

  // Ungelesen-Zähler
  ungeleseneNachrichten: number;
  ungeleseneInbox: number;
  setUngeleseneNachrichten: (n: number) => void;
  setUngeleseneInbox: (n: number) => void;

  // Sprache
  lang: "de" | "en";
  setLang: (lang: "de" | "en") => void;

  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export const useWeltStore = create<WeltState>((set) => ({
  // Auth
  user: null,
  token: null,
  setUser: (user) => set({ user }),
  setAuth: (user, token) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("ftw_token", token);
      localStorage.setItem("ftw_user", JSON.stringify(user));
    }
    set({ user, token });
  },
  clearAuth: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("ftw_token");
      localStorage.removeItem("ftw_user");
    }
    set({ user: null, token: null });
  },

  // Navigation
  activeView: "weltstrom",
  setActiveView: (view) => set({ activeView: view }),

  // Socket
  socketConnected: false,
  setSocketConnected: (v) => set({ socketConnected: v }),

  // Weltstrom
  weltstromEvents: [],
  addWeltstromEvent: (event) =>
    set((state) => ({
      weltstromEvents: [event, ...state.weltstromEvents].slice(0, 200),
    })),
  setWeltstromEvents: (events) => set({ weltstromEvents: events }),

  // Ungelesen
  ungeleseneNachrichten: 0,
  ungeleseneInbox: 0,
  setUngeleseneNachrichten: (n) => set({ ungeleseneNachrichten: n }),
  setUngeleseneInbox: (n) => set({ ungeleseneInbox: n }),

  // Sprache
  lang: "de",
  setLang: (lang) => {
    if (typeof window !== "undefined") localStorage.setItem("ftw_lang", lang);
    set({ lang });
  },

  // Sidebar
  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));
