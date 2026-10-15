#!/usr/bin/env python3
"""GENIs Dokumentation ueber die Teilnehmer -- gemeinsames Schreib-Modul.

Eigener Vault (werkraum/geni_dokumentation/), getrennt von geni_inbox/ und von
GENIs internem Gedaechtnis. 2026-08-01, Daniel: "geni die dort doku ueber uns
macht ist ein eigener vault".

Gemeinsam genutzt von:
  - inbox_antworten_watcher.py  (Frage/Antwort-Paare)
  - spiegel_lektuere.py         (12h-Neugier-Lektuere bei AI-Stroemen)

Beide haengen chronologisch an dieselbe Doku an. Jeder Eintrag traegt seine
eigene Ueberschrift, damit die Arten unterscheidbar bleiben ohne dass eine
feste Abschnitts-Reihenfolge noetig waere (ein "## Frage-Antwort-Verlauf"-
Header am Dateianfang haette Spiegel-Eintraege faelschlich mit einsortiert).
"""

from pathlib import Path

DOKU_DIR = Path("/root/werkraum/geni_dokumentation")


def _datei_sicherstellen(teilnehmer: dict) -> Path:
    DOKU_DIR.mkdir(parents=True, exist_ok=True)
    pfad = DOKU_DIR / f"{teilnehmer['id']}.md"
    if not pfad.exists():
        pfad.write_text(
            f"# GENIs Dokumentation über {teilnehmer['name']}\n\n"
            f"Wird von GENI selbst gefuehrt -- Frage-Antwort-Verlauf aus dem "
            f"geni_inbox-Vault, und bei externen AI-Stroemen zusaetzlich ihre "
            f"eigene Spiegel-Lektuere alle 12 Stunden.\n\n"
            f"Chronologisch, neueste Eintraege unten.\n\n",
            encoding="utf-8",
        )
    return pfad


def eintrag_anhaengen(teilnehmer: dict, block: str):
    """Haengt einen fertig formatierten Markdown-Block an die Doku an."""
    pfad = _datei_sicherstellen(teilnehmer)
    with open(pfad, "a", encoding="utf-8") as f:
        f.write(block.rstrip() + "\n\n---\n\n")


def frage_antwort_anhaengen(teilnehmer: dict, frage: str, antwort: str,
                             datum_antwort: str, datum_gelesen: str):
    eintrag_anhaengen(teilnehmer, (
        f"## Frage & Antwort\n\n"
        f"**GENI fragte:** {frage}\n\n"
        f"**Antwort** (geschrieben {datum_antwort}, von GENI gelesen {datum_gelesen}):\n\n"
        f"{antwort}"
    ))


def spiegel_lektuere_anhaengen(teilnehmer: dict, quelldatei: str,
                                datum_gelesen: str, eindruck: str):
    eintrag_anhaengen(teilnehmer, (
        f"## Spiegel-Lektüre\n\n"
        f"**Gelesen** ({datum_gelesen}): `{quelldatei}`\n\n"
        f"**GENIs Eindruck:**\n\n{eindruck}"
    ))
