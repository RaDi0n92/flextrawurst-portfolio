"""Folge-Dienst: schreibt neue Zeilen aus `ereignisse.jsonl` und den Praxis-Ledgern laufend in den Ereignisspeicher.

Unabhängig vom Relay: liest nur Dateien, die ohnehin entstehen. Beim Start wird alles Bisherige nachgeholt (wiederholbar, nichts doppelt), danach
folgt er jeder Datei ab dem gelesenen Stand. Eine kleinere Datei als zuletzt (Rotation) wird von vorn gelesen. Eine kaputte Zeile bleibt liegen,
ohne den Dienst anzuhalten. Fällt die Datenbank aus, versucht er es mit wachsendem Abstand erneut und liest erst danach weiter, es geht nichts verloren.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .ereignisspeicher import Ereignisspeicher

TAKT_S = 1.0
EINBETTEN_ALLE_S = 30.0
WARTE_MAX_S = 30.0


class Folger:
    def __init__(self, speicher: Ereignisspeicher, wurzel: Path):
        self.speicher, self.wurzel = speicher, Path(wurzel)
        self.stand: dict[Path, int] = {}
        self.geschrieben = 0
        self.fehler = ""

    def dateien(self) -> list[Path]:
        return sorted(self.wurzel.glob("g13/protokoll/ereignisse.jsonl")) + sorted(self.wurzel.glob("praxis/*.jsonl"))

    def runde(self) -> int:
        """Liest neue Zeilen aller Dateien; gibt die Anzahl neu geschriebener Ereignisse zurück."""
        neu = 0
        for datei in self.dateien():
            try:
                groesse = datei.stat().st_size
            except OSError:
                continue
            ab = self.stand.get(datei, 0)
            if groesse < ab:
                ab = 0  # Rotation: die Datei ist kleiner als beim letzten Lesen
            if groesse == ab:
                continue
            with open(datei, "rb") as f:
                f.seek(ab)
                daten = f.read(groesse - ab)
            ende = daten.rfind(b"\n") + 1  # nur vollständige Zeilen; ein halb geschriebenes Ende wartet auf die nächste Runde
            if ende == 0:
                continue
            for zeile in daten[:ende].decode("utf-8", "replace").splitlines():
                neu += self._zeile(datei, zeile)
            self.stand[datei] = ab + ende
        self.geschrieben += neu
        return neu

    def _zeile(self, datei: Path, zeile: str) -> int:
        try:
            e = json.loads(zeile)
            if "protokoll" in datei.parts:
                d = e.get("daten") or {}
                i = self.speicher.schreiben("protokoll", str(e["art"]), agent=str(e.get("agent", "")), text=str(e.get("text", "")),
                                            grund=str(d.get("reason", "") or d.get("grund", "")), daten={**d, "ziel": e.get("ziel", "")},
                                            zeit_ms=int(e["zeit_ms"]), extern_id=f"{e['id']}@{e['zeit_ms']}")
            else:
                i = self.speicher.schreibe_ledgerzeile(e)
        except (ValueError, KeyError, TypeError):
            return 0
        return 1 if i else 0


def lauf(wurzel: Path, ende=lambda: False, protokoll=print) -> None:
    from . import rag

    warte, speicher, folger, einbetter, zuletzt_eingebettet = 1.0, None, None, None, 0.0
    while not ende():
        try:
            if speicher is None:
                speicher = Ereignisspeicher()
                speicher.schema_anlegen()
                folger = Folger(speicher, wurzel)
                protokoll(f"verbunden, hole nach: {folger.runde()} neue Ereignisse")
            neu = folger.runde()
            if neu:
                protokoll(f"{time.strftime('%H:%M:%S')} +{neu}")
            if time.monotonic() - zuletzt_eingebettet > EINBETTEN_ALLE_S:
                einbetter = einbetter or rag.Einbetter()
                n = rag.einbetten_neue(speicher, einbetter, grenze=2000)
                zuletzt_eingebettet = time.monotonic()
                if n:
                    protokoll(f"{time.strftime('%H:%M:%S')} {n} eingebettet")
            warte = 1.0
            time.sleep(TAKT_S)
        except Exception as f:
            protokoll(f"{time.strftime('%H:%M:%S')} Fehler: {type(f).__name__}: {str(f)[:160]}; neuer Versuch in {warte:.0f} s")
            speicher = folger = None
            time.sleep(warte)
            warte = min(WARTE_MAX_S, warte * 2)
