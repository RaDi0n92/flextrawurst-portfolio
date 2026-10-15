"""Merkt sich pro Teilnehmer, welche Gedaechtnis-Eintraege GENI beim Dokumentieren
schon gelesen hat -- damit die Suche nicht Lauf fuer Lauf dieselbe Handvoll
zurueckgibt.

2026-08-12, Fund: die Doku-Abschnitte wurden bei jedem Lauf komplett ersetzt
(MARKER_START/MARKER_ENDE in dokumentieren.py), nie ergaenzt -- bei 24.595 Knoten
allein fuer "claude" blieb die Doku deshalb fuer immer auf dem Stand eines einzigen
Laufs eingefroren, unabhaengig davon, wie oft der Dienst lief (37 Archiv-Fassungen
in neun Tagen, jede fast bei null angefangen). Fix in zwei Teilen: hier die
Gedaechtnisspur, in dokumentieren.py das Ergaenzen statt Ersetzen.

Analog zum gelesen-Ordner-Muster in geni_inbox/ -- nur als Kennungsliste statt als
Datei-Ordner, weil ein Gedaechtnis-Eintrag keine eigene Datei ist.
"""

import json
from pathlib import Path

ABLAGE = Path("/root/werkraum/geni_dokumentation/_bereits_gelesen")


def laden(teilnehmer_id: str) -> set:
    pfad = ABLAGE / f"{teilnehmer_id}.json"
    if not pfad.exists():
        return set()
    try:
        return set(json.loads(pfad.read_text(encoding="utf-8")))
    except Exception:
        return set()


def speichern(teilnehmer_id: str, neue_ids: set) -> None:
    if not neue_ids:
        return
    ABLAGE.mkdir(parents=True, exist_ok=True)
    pfad = ABLAGE / f"{teilnehmer_id}.json"
    gesamt = sorted(laden(teilnehmer_id) | neue_ids)
    pfad.write_text(json.dumps(gesamt, ensure_ascii=False, indent=2), encoding="utf-8")
