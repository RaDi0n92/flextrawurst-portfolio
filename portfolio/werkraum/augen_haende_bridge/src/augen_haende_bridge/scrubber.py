"""Der Zeit-Scrubber (G13): durch einen aufgezeichneten Verlauf laufen und an jedem Punkt sehen, was damals war — **nur lesen**.

Die Zeitlinie bekommt Daten (Ereignisse, Terminalstücke, Bilder), nie Handlungsfähigkeiten: beim Scrubben geht **keine** Eingabe hinaus, nichts wird in einer Anwendung zurückgesetzt, und das Ergebnis sagt es (`wirkung_auf_anwendung: False`, `anwendung_zurueckgesetzt: False`).
Ein Neuanfang ab einem alten Punkt ist ein **Zweig** (Abläufe: `zweig_aus_kapsel`) und liest vor jeder Live-Handlung den jetzigen Zustand neu.
"""

from __future__ import annotations

from bisect import bisect_right


class Zeitlinie:
    def __init__(self, ereignisse: list[dict], terminal_stuecke: dict[str, list[tuple[int, str]]] | None = None, frames: dict[str, list[tuple[int, dict]]] | None = None):
        self._ereignisse = sorted(ereignisse, key=lambda e: e["zeit_ms"])
        self._zeiten = [e["zeit_ms"] for e in self._ereignisse]
        self._terminal = {t: sorted(s) for t, s in (terminal_stuecke or {}).items()}
        self._frames = {t: sorted(f, key=lambda x: x[0]) for t, f in (frames or {}).items()}

    @property
    def marken(self) -> list[int]:
        """Alle Zeitpunkte, an denen etwas geschah (Ereignisse, Terminalstücke, Bilder), aufsteigend und ohne Doppelte."""
        t = set(self._zeiten)
        for s in self._terminal.values():
            t.update(z for z, _ in s)
        for f in self._frames.values():
            t.update(z for z, _ in f)
        return sorted(t)

    def schritt(self, ab_ms: int, richtung: int) -> int | None:
        """Die nächste (richtung > 0) oder vorherige Marke; None am Ende."""
        m = self.marken
        if richtung > 0:
            i = bisect_right(m, ab_ms)
            return m[i] if i < len(m) else None
        i = bisect_right(m, ab_ms - 1)
        return m[i - 1] if i > 0 else None

    def zustand_bei(self, t_ms: int, agenten: list[str] | None = None, letzte: int = 8, max_terminal: int = 4000) -> dict:
        n = bisect_right(self._zeiten, t_ms)
        bis = [e for e in self._ereignisse[:n] if not agenten or e.get("agent") in agenten or not e.get("agent")]
        terminal, frame, luecken = {}, {}, []
        for t in (agenten or sorted(set(self._terminal) | set(self._frames))):
            stuecke = [s for z, s in self._terminal.get(t, []) if z <= t_ms]
            if t in self._terminal and not stuecke:
                luecken.append({"agent": t, "grund": "zu diesem Zeitpunkt noch keine Terminalausgabe aufgezeichnet"})
            terminal[t] = "".join(stuecke)[-max_terminal:]
            davor = [(z, m) for z, m in self._frames.get(t, []) if z <= t_ms]
            if davor:
                z, m = davor[-1]
                frame[t] = {"meta": m, "alter_ms": t_ms - z}
            else:
                frame[t] = None
                luecken.append({"agent": t, "grund": "zu diesem Zeitpunkt lag noch kein Bild vor (oder es ist nicht mehr gespeichert)"})
        return {"zeit_ms": t_ms, "ereignisse_bis_hier": len(bis), "letzte": bis[-letzte:], "nachrichten": [e for e in bis if e["art"] in ("nachricht", "auftrag", "regie")][-letzte:], "terminal": terminal,
                "frame": frame, "luecken": luecken, "wirkung_auf_anwendung": False, "anwendung_zurueckgesetzt": False, "hinweis": "nur gelesen: beim Scrubben geht nichts hinaus und nichts wird zurückgesetzt"}
