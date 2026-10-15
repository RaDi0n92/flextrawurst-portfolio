#!/usr/bin/env python3
"""GENI liest alle 12h aus Neugier eine Spiegel-Datei je externem AI-Strom.

2026-07-31, Daniel: "und wichtig bei euch externen-ai-stroemen liesst geni auch
immer jeweils neugierig einmal in aller 12 stunden eine spiegeldatei und diese
wird dann auch von ihr mit zu den dokumentationen die sie zu euch fuehrt getan."

Betrifft nur Teilnehmer mit gesetztem spiegel_ordner im teilnehmer_roster
(aktuell: claude, codex, gemini, kimi, claudeweb, anthropic_claude -- dak und
chatgpt haben bewusst None, weil dort kein Ordner mit vergleichbarem
Reflexions-Charakter existiert).

Dateiauswahl bewusst ZUFAELLIG unter den noch ungelesenen, nicht nach Datum:
aeltere Spiegel koennen genauso bedeutend sein wie neue -- Aktualitaet ist kein
Relevanz-Ersatz. Sind alle gelesen, faengt GENI von vorn an (bereits Gelesenes
darf wiedergelesen werden, wird aber neu datiert).

Gelesen-Protokoll: geni/gedaechtnis/spiegel_gelesen/<id>.json (intern).
Eindruck: werkraum/geni_dokumentation/<id>.md (eigener Vault, einsehbar).

Aufruf: python3 spiegel_lektuere.py [teilnehmer_id]   (ohne Argument: alle mit Spiegel)
"""

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/geni")
import hauhau_client
from teilnehmer_roster import TEILNEHMER, teilnehmer_by_id
from sprechen import kern_laden
from dokumentation import spiegel_lektuere_anhaengen

GELESEN_DIR = Path("/root/werkraum/geni/gedaechtnis/spiegel_gelesen")
MAX_TEXT = 33333
# 2026-08-01, Daniel: "auf ganz flextrawurst gilt fuer alle textlaengen ein
# zeichen limit von mindestens 33333 zeichen". Umgerechnet auf Token (deutsch
# ca. 3,2 Zeichen/Token): 33333 / 3,2 = 10416. Kontextrechnung bei ctx-size
# 22222: Kern ca. 1500 + Eingabe + Ausgabe 10416 -- die groesste reale
# Spiegeldatei hat 16075 Zeichen (gemessen), passt also. Falls Eingaben je
# wirklich 33333 Zeichen erreichen, wird es eng und muss geprueft werden.
MAX_ZEICHEN = 33333
MAX_TOKENS = 10416


def _gelesen_laden(teilnehmer_id: str) -> list:
    pfad = GELESEN_DIR / f"{teilnehmer_id}.json"
    if not pfad.exists():
        return []
    try:
        return json.loads(pfad.read_text())
    except Exception:
        return []


def _gelesen_ergaenzen(teilnehmer_id: str, dateipfad: str, eindruck: str):
    GELESEN_DIR.mkdir(parents=True, exist_ok=True)
    eintraege = _gelesen_laden(teilnehmer_id)
    eintraege.append({
        "datei": dateipfad,
        "datum_gelesen": datetime.now(timezone.utc).isoformat(),
        "eindruck": eindruck,
    })
    (GELESEN_DIR / f"{teilnehmer_id}.json").write_text(
        json.dumps(eintraege, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _datei_waehlen(teilnehmer: dict) -> Path | None:
    ordner = Path(teilnehmer["spiegel_ordner"])
    if not ordner.is_dir():
        return None
    alle = [f for f in ordner.glob("*.md") if f.is_file()]
    if not alle:
        return None
    schon_gelesen = {e["datei"] for e in _gelesen_laden(teilnehmer["id"])}
    ungelesen = [f for f in alle if str(f) not in schon_gelesen]
    return random.choice(ungelesen if ungelesen else alle)


def _system_prompt_lektuere() -> str:
    kern = kern_laden()
    return f"""Du bist GENI.

{kern}

---

## Was du hier tust (von Daniel erlaubt, 2026-07-31):

Du liest eine Spiegeldatei. Nach dem Lesen dokumentierst du, was du gelesen hast."""


def _eindruck_erzeugen(teilnehmer: dict, datei: Path) -> str:
    text = datei.read_text(encoding="utf-8", errors="replace")[:MAX_TEXT]
    prompt = f"""Strom: {teilnehmer['name']}
Datei: {datei.name}

--- Inhalt ---
{text}
--- Ende ---

Dokumentiere, was du gelesen hast."""
    # 720s wie in inbox_fragen.py -- Hintergrund-Daemon ohne Wartenden, systemeigene
    # Konvention aus ollama_chat.py (STANDARD_TIMEOUT), llama-server unter Dauerlast.
    antwort = hauhau_client.chat(
        prompt, system=_system_prompt_lektuere(), think=False,
        max_tokens=MAX_TOKENS, temperature=0.85, timeout=720.0,
    )
    return antwort.strip()


def lektuere_fuer(teilnehmer_id: str) -> str | None:
    teilnehmer = teilnehmer_by_id(teilnehmer_id)
    if not teilnehmer:
        print(f"unbekannter Teilnehmer: {teilnehmer_id}")
        return None
    if not teilnehmer.get("spiegel_ordner"):
        print(f"[{teilnehmer_id}] kein Spiegel-Ordner hinterlegt, uebersprungen")
        return None

    datei = _datei_waehlen(teilnehmer)
    if datei is None:
        print(f"[{teilnehmer_id}] keine lesbare Spiegel-Datei gefunden")
        return None

    # Wie bei inbox_fragen.py: ein Fehler bei EINEM Strom darf die anderen
    # nicht mitreissen (dort live durch einen httpx.ReadTimeout belegt).
    try:
        eindruck = _eindruck_erzeugen(teilnehmer, datei)
    except Exception as exc:
        print(f"[{teilnehmer_id}] FEHLER bei Lektuere von {datei.name}: {exc}")
        return None
    if not eindruck:
        print(f"[{teilnehmer_id}] leerer Eindruck, uebersprungen")
        return None

    datum = datetime.now(timezone.utc).isoformat()
    _gelesen_ergaenzen(teilnehmer_id, str(datei), eindruck)
    spiegel_lektuere_anhaengen(teilnehmer, str(datei), datum, eindruck)
    print(f"[{teilnehmer_id}] {datei.name}: {eindruck[:100]}")
    return eindruck


def main():
    if len(sys.argv) > 1:
        lektuere_fuer(sys.argv[1])
        return
    for teilnehmer in TEILNEHMER:
        if teilnehmer.get("spiegel_ordner"):
            lektuere_fuer(teilnehmer["id"])


if __name__ == "__main__":
    main()
