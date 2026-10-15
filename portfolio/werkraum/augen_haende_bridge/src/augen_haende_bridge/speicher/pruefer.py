"""Die echten Prüfer des Infrastruktur-Graphen: jeder Knoten wird nur aus Ereignissen im Speicher belegt, nie aus einer Behauptung.

Ein Agent ist hier seine Terminal-Id (`t-…`), wie im Ereignisprotokoll. Die Fenster (Sekunden) stehen oben als Konstanten.

* ziel_gebunden: der Bilderstrom des Agenten hat in den letzten `ZIEL_S` ein Bild geliefert (Desktop zählt als Ziel).
* strom_frisch: das letzte Bild ist jünger als `FRISCH_S`.
* lease: die letzte Lease-Anfrage war in den letzten `LEASE_S` erfolgreich; sonst steht ihr Grund da.
* hand: die letzte Hände-Aktion der letzten `HAND_S` war ausgeführt; sonst steht ihr Grund da.
* beleg: nach der letzten ausgeführten Hände-Aktion gibt es ein eigenes `sehen`-Ereignis des Agenten.
* urteil: der Lauf hat nach dem Beleg ein Urteil im Ledger (`ok`, `anders`, `fehler`, `entdeckung` mit eigenem Bild zählt nicht).
"""

from __future__ import annotations

import time

from .ereignisspeicher import Ereignisspeicher
from .infragraph import Pruefer

ZIEL_S, FRISCH_S, LEASE_S, HAND_S = 120, 30, 120, 300
URTEILE = ("ok", "anders", "fehler")


def ereignis_pruefer(speicher: Ereignisspeicher, jetzt_ms=lambda: int(time.time() * 1000)) -> dict[str, Pruefer]:
    def letzte(agent: str, art: str, nur_ok: bool | None = None) -> dict | None:
        bedingung = "" if nur_ok is None else f" AND (daten->>'ok')::boolean IS {'TRUE' if nur_ok else 'NOT TRUE'}"
        z = speicher.abfrage(f"SELECT * FROM ereignis WHERE quelle='protokoll' AND art=%s AND agent=%s{bedingung} ORDER BY zeit_ms DESC, id DESC LIMIT 1", (art, agent))
        return z[0] if z else None

    def alter_s(e: dict | None) -> float:
        return (jetzt_ms() - e["zeit_ms"]) / 1000 if e else float("inf")

    def ziel(lauf: str, agent: str):
        a = alter_s(letzte(agent, "frame"))
        return (True, "") if a <= ZIEL_S else (False, "kein_bild_gebunden" if a == float("inf") else f"kein_bild_seit_{int(a)}_s")

    def strom(lauf: str, agent: str):
        a = alter_s(letzte(agent, "frame"))
        return (True, "") if a <= FRISCH_S else (False, "kein_bild" if a == float("inf") else f"bild_{int(a)}_s_alt")

    def lease(lauf: str, agent: str):
        ok = letzte(agent, "lease", True)
        if ok and alter_s(ok) <= LEASE_S:
            return True, ""
        e = letzte(agent, "lease")
        return False, (e["grund"] or "lease_abgelehnt") if e and alter_s(e) <= LEASE_S else "keine_lease"

    def hand(lauf: str, agent: str):
        ok = letzte(agent, "haende", True)
        if ok and alter_s(ok) <= HAND_S:
            return True, ""
        e = letzte(agent, "haende")
        return False, (e["grund"] or "abgelehnt") if e and alter_s(e) <= HAND_S else "keine_aktion"

    def beleg(lauf: str, agent: str):
        h = letzte(agent, "haende", True)
        s = letzte(agent, "sehen")
        return (True, "") if h and s and s["zeit_ms"] >= h["zeit_ms"] else (False, "kein_eigenes_bild_nach_der_aktion" if h else "keine_aktion")

    def urteil(lauf: str, agent: str):
        h = letzte(agent, "haende", True)
        z = speicher.abfrage("SELECT 1 FROM ereignis WHERE quelle='ledger' AND lauf=%s AND art = ANY(%s) AND zeit_ms >= %s LIMIT 1",
                             (lauf, list(URTEILE), h["zeit_ms"] if h else 0))
        return (True, "") if z else (False, "kein_urteil")

    return {"ziel_gebunden": ziel, "strom_frisch": strom, "lease": lease, "hand": hand, "beleg": beleg, "urteil": urteil}
