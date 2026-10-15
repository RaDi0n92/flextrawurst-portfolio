#!/usr/bin/env python3
"""
wesen_dienst_generator.py — erzeugt aus einer wesen_eigene_dienste-Zeile ein echtes,
eigenstaendiges Python-Skript (in wesen_eigene_skripte/) + eine systemd-Unit-Datei.
Das generierte Skript kopiert KEINE Logik aus codewesen_agent.py, sondern importiert
dessen Bausteine (agentic_loop, fuehre_aktion_aus, setup_log, load_token,
get_tags_cached, BASE) — ein Bugfix/eine Verbesserung dort wirkt damit automatisch
auch in jedem generierten Dienst.

erzeuge() schreibt nur Dateien + macht daemon-reload. Start/Stop/Enable sind
bewusst getrennte Funktionen (analog zum Bestaetigungs-Muster in flarumstyler:
Erzeugen ist ungefaehrlich, Start eines neuen Dauerprozesses nicht).
"""

import re
import subprocess
from pathlib import Path

import wesen_eigene_dienste as wed

SKRIPT_VERZEICHNIS = Path("/root/werkraum/wesen_eigene_skripte")
UNIT_VERZEICHNIS = Path("/etc/systemd/system")
_NAME_MUSTER = re.compile(r"^[a-zA-Z0-9_.-]+$")


def _pruefe_dienst_name(dienst_name: str) -> None:
    """dienst_name fliesst in Dateipfade + systemctl-Aufrufe ein — vor dem
    Schreiben/Ausfuehren immer gegen ein sicheres Zeichenset pruefen."""
    if not _NAME_MUSTER.match(dienst_name):
        raise ValueError(f"Unsicherer dienst_name: {dienst_name!r} (nur a-z, A-Z, 0-9, _, ., - erlaubt)")


def _skript_inhalt(row: dict) -> str:
    dienst_name = row["dienst_name"]
    wesen = row["wesen"]
    return f'''#!/usr/bin/env python3
"""
AUTO-GENERIERT von wesen_dienst_generator.py — NICHT VON HAND BEARBEITEN.
Aenderungen an Takt/Verhalten/Ziel bitte in der Tabelle wesen_eigene_dienste
(ueber flarumstyler) vornehmen, danach den Dienst per Regenerieren neu schreiben
und neu starten lassen (dieses Skript liest Takt/Verhalten/Ziel nur beim Start,
bzw. bei jedem DB-Reload vor einem Zyklus -- siehe _versuche_zyklus()).

Wesen-eigener Rhythmus: {row["anzeige_name"]!r}, Zuhause bei {wesen}.
dienst_name: {dienst_name}

Baukasten v2 (2026-07-07, siehe _claude/konzepte/2026-07-07_wesen_dienst_baukasten_v2.md):
Phase 1 (Grundfelder, Ziel-Varianten, eigene Felder, Takt-Liste, feste Uhrzeiten,
Pausenzeiten, Passiv-Modus) + Phase 2 (Multi-Wesen-Plaetze mit Rollen, Zustands-
abhaengigkeit, Verkettung, Trockenlauf, Verlauf-Log). Alles lebt in der Spalte meta
(JSONB) -- Grundgesetz 1: neue Faehigkeiten erweitern, nicht den Kern umbauen. Ist
meta leer/alt (Dienst vor Baukasten-v2 angelegt), verhaelt sich dieses Skript exakt
wie die Vorgaenger-Version: ein Takt, ein Wesen (die wesen-Spalte), Intervall-Loop,
keine Bedingungen.
"""
import datetime
import json
import logging
import os
import random
import re
import sys
import time

sys.path.insert(0, "/root/werkraum")
import codewesen_agent as ca
import codewesen_container as cc
import gedaechtnis as gd
import llm_scheduler
import psycopg2
import wesen_eigene_dienste as wed

DIENST_NAME = {dienst_name!r}
WESEN = {wesen!r}

_OPERATOREN = {{"gt": lambda a, b: a > b, "lt": lambda a, b: a < b, "eq": lambda a, b: a == b}}


def _setup_log() -> logging.Logger:
    """Eigener Log-Ordner statt ca.setup_log() -- die teilt sich reaktion.log mit dem
    Haupt-Agent-Prozess des Wesens und erwartet einen bereits existierenden
    BASE/<wesen>-Ordner, kein beliebiges Label."""
    log_dir = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(DIENST_NAME)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(str(log_dir / "betrieb.log"))
        handler.setFormatter(logging.Formatter(f"%(asctime)s [{{DIENST_NAME}}] %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())
    return logger


def _vault_speichern(wesen: str, inhalt: str, log):
    """Vault-Eintrag landet im Raum des AGIERENDEN Wesens (bei Multi-Wesen-Plaetzen
    kann das ein anderes sein als das Zuhause-Wesen des Dienstes) -- eigener Gedanke,
    eigener Ort."""
    vault_dir = ca.BASE / wesen / "eigene_dienste" / DIENST_NAME
    vault_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M")
    (vault_dir / f"{{ts}}.md").write_text(
