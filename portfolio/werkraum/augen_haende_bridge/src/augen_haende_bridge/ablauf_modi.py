"""Modi der Abläufe (G12, R075): `free`, `shadow`, `witness`, `daniel_gate`, `learning`, `delegated_learning` — einzeln wählbar und kombinierbar, Lernen anfangs aus.

* **free**: der Agent arbeitet im eingeschalteten Aufgabenbereich ohne zusätzliche Einzelbestätigung je Aktion. Ist der Bereich nicht eingeschaltet, geschieht nichts.
* **shadow**: Vorschau. Kein handelnder Knoten (`handeln`, `delegieren`) wird ausgeführt; der Lauf geht den Graphen durch und kennzeichnet alles als simuliert. Shadow gewinnt gegen jeden anderen Modus.
* **witness**: jeder Schritt geht als Ereignis an einen Beobachter (Daniel oder ein anderer Agent), ohne den Lauf aufzuhalten.
* **daniel_gate**: vor **jeder** handelnden Aktion fragt der Lauf Daniel und wartet. Keine Antwort in der Frist heißt nein.
* **learning**: Beobachtungen und Ergebnisse jedes Schritts gehen als Erfahrungsaufzeichnung an eine Senke (Grundlage für G13). Nur nach ausdrücklichem Einschalten (`lernen_aktiv`).
* **delegated_learning**: wie `learning`, aber die Auswertung gehört einem anderen Agenten; auch das nur nach ausdrücklichem Einschalten.

Ein `tor`-Knoten im Ablauf ist ein bewusst entworfenes Daniel-Tor und fragt immer (außer unter Shadow, wo nichts geschieht).
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable

MODI = ("free", "shadow", "witness", "daniel_gate", "learning", "delegated_learning")
LERNMODI = frozenset({"learning", "delegated_learning"})


class ModiFehler(ValueError):
    pass


class Genehmigungen:
    """Offene Fragen an Daniel. Thread-sicher; `warte` ist unterbrechbar."""

    def __init__(self, uhr: Callable[[], float] = time.monotonic):
        self._uhr = uhr
        self._offen: dict[str, dict] = {}
        self._sperre = threading.Lock()

    def anfordern(self, lauf_id: str, knoten: str, beschreibung: str) -> str:
        gid = f"g-{uuid.uuid4().hex[:8]}"
        with self._sperre:
            self._offen[gid] = {"id": gid, "lauf": lauf_id, "knoten": knoten, "beschreibung": beschreibung[:300], "entscheidung": None, "event": threading.Event(), "seit": self._uhr()}
        return gid

    def offen(self) -> list[dict]:
        with self._sperre:
            return [{k: v for k, v in g.items() if k != "event"} for g in self._offen.values() if g["entscheidung"] is None]

    def entscheiden(self, gid: str, ja: bool) -> bool:
        with self._sperre:
            g = self._offen.get(gid)
            if g is None or g["entscheidung"] is not None:
                return False
            g["entscheidung"] = "ja" if ja else "nein"
            g["event"].set()
            return True

    def warte(self, gid: str, timeout_s: float, abbruch: Callable[[], bool] = lambda: False) -> str:
        g = self._offen.get(gid)
        if g is None:
            return "unbekannt"
        ende = time.monotonic() + timeout_s
        while time.monotonic() < ende:
            if g["event"].wait(0.05):
                break
            if abbruch():
                with self._sperre:
                    g["entscheidung"] = g["entscheidung"] or "abgebrochen"
                return "abgebrochen"
        with self._sperre:
            if g["entscheidung"] is None:
                g["entscheidung"] = "zeitablauf"
            return g["entscheidung"]


def normalisieren(modi, *, lernen_aktiv: bool = False) -> tuple[str, ...]:
    """Die Modi eines Laufs prüfen: nur bekannte, ohne Doppelte; Lernen nur, wenn es eingeschaltet ist. Ohne Angabe: `free`."""
    if modi is None or modi == ():
        return ("free",)
    if isinstance(modi, str):
        modi = (modi,)
    gesehen = []
    for m in modi:
        if m not in MODI:
            raise ModiFehler(f"modus_unbekannt:{m}")
        if m in LERNMODI and not lernen_aktiv:
            raise ModiFehler("lernen_ist_aus")
        if m not in gesehen:
            gesehen.append(m)
    return tuple(gesehen)


class Modi:
    def __init__(self, genehmigungen: Genehmigungen | None = None, *, aufgabenbereich: Callable[[object], bool] = lambda lauf: True, ereignis: Callable[[dict], None] | None = None,
                 lernen: Callable[[dict], None] | None = None, frist_s: float = 120.0, lernen_aktiv: bool = False):
        self.genehmigungen = genehmigungen or Genehmigungen()
        self._bereich, self._ereignis, self._lernen, self.frist_s = aufgabenbereich, ereignis, lernen, frist_s
        self.lernen_aktiv = lernen_aktiv  # anfangs aus; nur Daniel schaltet es ein

    def normalisieren(self, modi) -> tuple[str, ...]:
        return normalisieren(modi, lernen_aktiv=self.lernen_aktiv)

    def vor_handeln(self, lauf, kid: str, k: dict) -> str:
        """`ausfuehren`, `simulieren` oder `abgelehnt` für einen handelnden Knoten."""
        m = set(lauf.modi)
        if "shadow" in m:
            return "simulieren"
        if not self._bereich(lauf):
            lauf.grund = "aufgabenbereich_aus"
            return "abgelehnt"
        if "daniel_gate" in m:
            gid = self.genehmigungen.anfordern(lauf.id, kid, f"{k.get('art')} {k.get('aktion') or k.get('an') or ''} ({k.get('name', kid)})")
            antwort = self.genehmigungen.warte(gid, self.frist_s, abbruch=lambda: lauf.run.status.value in ("aborted", "paused"))
            if antwort != "ja":
                lauf.grund = f"freigabe_{antwort}"
                return "abgelehnt"
        return "ausfuehren"

    def tor_frei(self, lauf, kid: str, k: dict) -> bool:
        if "shadow" in lauf.modi:
            return True
        gid = self.genehmigungen.anfordern(lauf.id, kid, f"Tor {k.get('name', kid)}")
        return self.genehmigungen.warte(gid, self.frist_s, abbruch=lambda: lauf.run.status.value in ("aborted", "paused")) == "ja"

    def nach_schritt(self, lauf, eintrag) -> None:
        m = set(lauf.modi)
        if "witness" in m and self._ereignis is not None:
            try:
                self._ereignis({"lauf": lauf.id, "ablauf": lauf.ablauf.id, "knoten": eintrag.knoten, "signal": eintrag.signal, "status": eintrag.status, "detail": eintrag.detail, "zeit_ms": eintrag.zeit_ms,
                                "simuliert": eintrag.simuliert})
            except Exception:
                pass  # ein kaputter Beobachter hält den Lauf nicht an
        if m & LERNMODI and self.lernen_aktiv and self._lernen is not None and not eintrag.simuliert:
            try:
                self._lernen({"lauf": lauf.id, "ablauf": f"{lauf.ablauf.id}@{lauf.ablauf.version}", "knoten": eintrag.knoten, "signal": eintrag.signal, "status": eintrag.status,
                              "ergebnis": lauf.ctx.get(lauf.ablauf.knoten[eintrag.knoten].get("speichere", eintrag.knoten)), "delegiert": "delegated_learning" in m,
                              "auswerter": lauf.zustand.get("auswerter") if "delegated_learning" in m else None})
            except Exception:
                pass
