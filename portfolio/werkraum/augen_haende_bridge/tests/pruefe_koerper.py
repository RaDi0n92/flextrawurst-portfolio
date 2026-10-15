#!/usr/bin/env python3
"""Koerper-Tor: haelt den Windows-Koerper gegen Daniels dokumentierte Vorgaben.

Der uebrige Pruefapparat der Bridge fragt: ist der Code technisch konsistent? Dieses Tor
fragt etwas anderes: steht im Koerper noch etwas, das bereits wortlich beanstandet wurde?
Jede Regel nennt die Stelle, an der sie beanstandet wurde.

Massstab sind die dokumentierten Vorgaben (docs/augen_haende_bridge/ANFORDERUNGEN.md). Die Skizze dient nur der Orientierung.

Es liest nur, baut nichts und aendert nichts.

Exit-Codes: 0 = nichts Beanstandetes im Koerper - 1 = mindestens ein Verstoss -
3 = Datei nicht gefunden, nichts geprueft.

Was dieses Tor NICHT sagt: ob das geoeffnete Fenster den Vorgaben entspricht. Das entscheidet
ein Blick auf den echten Start, nicht ein grep. Es sagt nur: was wurde benannt und steht
trotzdem noch da - und haelt Entferntes davon fern.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Seit PLAN-G02 ist der Koerper das Paket `koerper/` (alle .py-Dateien); der alte Tk-Koerper `overlay_app.py` ist abgeloest.
KOERPER = Path(__file__).resolve().parents[1] / "src" / "augen_haende_bridge" / "koerper"

VERBOTEN = [
    {
        "id": "V01-GEMALTE-AGENTEN",
        "muster": r'AgentNode\(\s*"(codex|gemini|claude|daniel)"',
        "was": "fest gemalte Agenten mit festen Koordinaten",
        "beanstandet": 'Goal G09: "Reale Multi-Agent-Orchestrierung statt vier fest gemalter Namen" '
                       "(Rueckwaertsplan, seit der Zusammenlegung nur noch in Git)",
        "regel": "Rauten erscheinen nur fuer Agenten, die es wirklich gibt und die gebunden sind.",
    },
    {
        "id": "V02-DEKO-PFEILE",
        "muster": r"create_line\([^)]*arrow\s*=",
        "was": "gezeichnete Beziehungspfeile",
        "beanstandet": 'R032 (Daniel U443): "Beschriftungspfeile in der Skizze sind keine dekorativen '
                       'Datenleitungen"',
        "regel": "Die Erklaerungspfeile der Skizze sind Erklaerung, nicht Bauteil.",
    },
    {
        "id": "V03-DECKKRAFT",
        "muster": r'attributes\(\s*"-alpha"\s*,\s*0\.9',
        "was": "Deckkraft 0,94 statt der verlangten 66 % Transparenz",
        "beanstandet": 'Baustartpruefung 2026-09-19: "der bestehende Wert 0,94 erfuellt das nicht"',
        "regel": "66 % transparent heisst 34 % Deckkraft, je Bereich einstellbar. Tk kennt -alpha "
                 "nur fuer das ganze Fenster; die Loesung ist ein natives Layered Window "
                 "(Recherche 2026-09-19), nicht ein anderer Zahlenwert.",
    },
    {
        "id": "V04-MEDIEN-ATTRAPPE",
        "muster": r"agent\.(mic|camera)\b|Mikrofon: |Kamera: ",
        "was": "Mikrofon/Kamera als blosse Zustandsschalter",
        "beanstandet": 'Baustartpruefung 2026-09-19: "lokale Zustandswechsel fuer Mikrofon/Kamera '
                       'statt belegter Aufnahme"',
        "regel": "Ein Schalter, hinter dem keine Aufnahme haengt, ist keine Kamera (START_HIER Regel 3).",
    },
]


def fundstellen(text: str, muster: str) -> list[tuple[str, str]]:
    return [(ort, z.strip()[:96]) for ort, z in _zeilen(text) if re.search(muster, z)]


def _zeilen(text: str) -> list[tuple[str, str]]:
    """(Ort, Zeile): fuer eine Datei die Zeilennummer, fuer ein Paket `datei:zeile`."""
    ergebnis = []
    aktuell, nr = "", 0
    for zeile in text.splitlines():
        if zeile.startswith("\x00DATEI "):
            aktuell, nr = zeile[len("\x00DATEI "):], 0
            continue
        nr += 1
        ergebnis.append((f"{aktuell}:{nr}" if aktuell else str(nr), zeile))
    return ergebnis


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datei", default=str(KOERPER), help="zu pruefender Koerper")
    args = ap.parse_args()

    ziel = Path(args.datei)
    if not ziel.exists():
        print(f"UNBEKANNT - {ziel} existiert nicht. Nichts geprueft.")
        return 3
    if ziel.is_dir():
        dateien = sorted(ziel.glob("*.py"))
        if not dateien:
            print(f"UNBEKANNT - {ziel} enthaelt keine .py-Dateien. Nichts geprueft.")
            return 3
        text = "\n".join(f"\x00DATEI {d.name}\n" + d.read_text(encoding="utf-8", errors="replace") for d in dateien)
    else:
        text = ziel.read_text(encoding="utf-8", errors="replace")

    print(f"Koerper-Tor - {ziel}")
    print(f"{len(_zeilen(text))} Zeilen geprueft; Massstab: die dokumentierten Vorgaben")
    print()
    verstoesse = 0
    for v in VERBOTEN:
        tr = fundstellen(text, v["muster"])
        if tr:
            verstoesse += 1
            zeilen = ", ".join(n for n, _ in tr[:6]) + (f" (+{len(tr) - 6})" if len(tr) > 6 else "")
            print(f"  [{v['id']}]  VERSTOSS  Zeile {zeilen}")
            print(f"      {v['was']}")
            print(f"      beanstandet in: {v['beanstandet']}")
            print(f"      Regel: {v['regel']}")
        else:
            print(f"  [{v['id']}]  sauber    - {v['was']}: nicht gefunden")
        print()
    print(f"Urteil: {verstoesse} von {len(VERBOTEN)} beanstandeten Dingen stehen noch im Koerper.")
    return 1 if verstoesse else 0


if __name__ == "__main__":
    sys.exit(main())
