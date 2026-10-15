"""Spiegelt jedes neue Ereignis des Starters und jede Ledger-Zeile der Praxisläufe sofort in den Ereignisspeicher — in einem eigenen Faden, damit das Aufzeichnen nie wartet.

Fällt die Datenbank aus, versucht der Faden es mit wachsendem Abstand erneut; Ereignisse bleiben in der Warteschlange (bis `MAX_WARTEND`).
Was darüber hinaus verworfen wird, steht in `verworfen` und bleibt in `ereignisse.jsonl`: `speicher einlesen` holt es nach (wiederholbar, nichts doppelt).
Ohne `BRIDGE_DB_URL` startet kein Spiegel.
"""

from __future__ import annotations

import queue
import threading
import time

from ..ereignisprotokoll import Ereignis, Ereignisprotokoll
from .ereignisspeicher import Ereignisspeicher, adresse

MAX_WARTEND = 20_000
WARTE_MIN_S, WARTE_MAX_S = 1.0, 30.0


class Spiegel:
    def __init__(self, protokoll: Ereignisprotokoll, dsn: str | None = None, speicher_fabrik=None):
        self._fabrik = speicher_fabrik or (lambda: Ereignisspeicher(dsn or adresse()))
        self._warteschlange: queue.Queue = queue.Queue(maxsize=MAX_WARTEND)
        self.verworfen = 0
        self.geschrieben = 0
        self.fehler = ""
        self._ende = threading.Event()
        self._faden = threading.Thread(target=self._lauf, name="ereignisspeicher-spiegel", daemon=True)
        protokoll.abonnieren(self._an)
        self._faden.start()

    def _an(self, e: Ereignis) -> None:
        try:
            self._warteschlange.put_nowait(e)
        except queue.Full:
            self.verworfen += 1

    def ledger(self, zeile: dict) -> None:
        """Eine Zeile des Praxis-Ledgers; derselbe Weg und dieselben Garantien wie bei Ereignissen."""
        try:
            self._warteschlange.put_nowait(zeile)
        except queue.Full:
            self.verworfen += 1

    def _schreiben(self, speicher: Ereignisspeicher, e) -> None:
        if isinstance(e, dict):
            speicher.schreibe_ledgerzeile(e)
        else:
            speicher.schreiben("protokoll", e.art, agent=e.agent, text=e.text, grund=str(e.daten.get("reason", "")), zeit_ms=e.zeit_ms,
                               daten={**e.daten, "ziel": e.ziel}, extern_id=f"{e.id}@{e.zeit_ms}")

    def _lauf(self) -> None:
        speicher, warte = None, WARTE_MIN_S
        while not self._ende.is_set():
            try:
                e = self._warteschlange.get(timeout=0.5)
            except queue.Empty:
                continue
            while not self._ende.is_set():
                try:
                    if speicher is None:
                        speicher = self._fabrik()
                    self._schreiben(speicher, e)
                    self.geschrieben += 1
                    self.fehler, warte = "", WARTE_MIN_S
                    break
                except Exception as f:
                    self.fehler = f"{type(f).__name__}: {f}"[:200]
                    speicher = None
                    self._ende.wait(warte)
                    warte = min(WARTE_MAX_S, warte * 2)

    def beenden(self) -> None:
        self._ende.set()
