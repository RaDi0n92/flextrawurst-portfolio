#!/usr/bin/env python3
"""
Wesen-Einzug-Vault-Agent — reine Plattenoperationen fuer einen eigenen,
sauberen Vault zur Einzug-Erinnerungsfrage ("Erinnerung behalten oder neu
anfangen"), getrennt vom bestehenden `wesen_vaults/`.

Entstanden 2026-09-16 auf Daniels Auftrag ("bau mal. aber das post im flarum
uebernehme ich und erst dann geht die frage live", danach "wie beim alten
vault"). Funktionsumfang bewusst 1:1 an obsidian_vault_agent.py's Phase-3-
Funktionen angelehnt (liste_ordner/baum/lese_datei_info/
schreibe_datei_mechanisch/loeschen/neuer_ordner/umbenennen/verschieben,
_sicherer_vault_pfad) -- komplett eigenstaendig kopiert statt importiert,
damit das laufende Vault-System (Grundgesetz 7) unberuehrt bleibt.

Ein Unterschied bewusst NICHT uebernommen: obsidian_vault_agent._vault_event_
schreiben() schreibt "vault."-praefigierte Events in dieselbe geteilte
events-Tabelle, die wesenvaultsystem_api.py's /api/live (Port 8097) live an
jeden ausliefert, der die Seite offen hat. Waere dieses Modul daran
angeschlossen, koennten die anderen Wesen live mitverfolgen, wer gerade zur
Einzug-Frage schreibt -- genau der Anker-Effekt, den die Kombination aus
Flarum-Debatte + stiller Einzelentscheidung vermeiden soll (Gespraech mit
Daniel, 2026-09-16). Dieses Modul schreibt deshalb keine Events in die
geteilte Tabelle. Falls spaeter eine Live-Ansicht gewuenscht wird, braucht sie
einen eigenen, nicht-oeffentlichen Kanal -- eigene Entscheidung, noch offen.

`oeffne_datei_und_schreibe()` (Anhaengen, fuer ein Wesen das selbst ueber
sein LLM schreibt -- Pendant zu obsidian_vault_agent.py, aufgerufen aus
browser_agent.py bei `obsidian_schreiben:`) ist hier vorbereitet, aber NOCH
NICHT an browser_agent.py angebunden. Grund: die Anbindung hiesse, den
Wesen ueber ihr eigenes System-Prompt eine neue Aktion beizubringen -- das
waere selbst schon ein Stueck "live gehen", bevor Daniels Flarum-Post steht.
Siehe _ZUSTAND.md im Vault-Wurzelordner.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path("/root/werkraum/wesen_einzug_entscheidung")

# Gleiche sieben Namen wie obsidian_vault_agent.py::CONTAINER_NAMES, hier
# unabhaengig gefuehrt statt importiert (siehe Moduldoku oben).
WESEN = (
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
    "dak+gord-system",
)


def _pruefe_wesen(wesen: str) -> None:
    if wesen not in WESEN:
        raise ValueError(f"Unbekanntes Wesen: {wesen!r}")


def vault_pfad(wesen: str) -> Path:
    _pruefe_wesen(wesen)
    return VAULT_ROOT / wesen


def _sicherer_vault_pfad(wesen: str, pfad: str) -> Path:
    """Loest pfad gegen den Vault des Wesens auf, wirft ValueError bei Ausbruchsversuch."""
    basis = vault_pfad(wesen).resolve()
    ziel = (basis / pfad.strip().lstrip("/")).resolve()
    ziel.relative_to(basis)
    return ziel


def liste_ordner(wesen: str, pfad: str = "") -> list[dict]:
    pfad = pfad.strip().lstrip("/")
    basis = vault_pfad(wesen).resolve()
    ziel = (basis / pfad).resolve()
    ziel.relative_to(basis)
    if not ziel.is_dir():
        raise NotADirectoryError(f"{pfad!r} ist kein Ordner in {wesen}s Vault")
    eintraege = []
    for kind in sorted(ziel.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if kind.name.startswith("."):
            continue
        eintraege.append({
            "name": kind.name,
            "typ": "ordner" if kind.is_dir() else "datei",
            "groesse": kind.stat().st_size if kind.is_file() else None,
            "geaendert": kind.stat().st_mtime if kind.is_file() else None,
        })
    return eintraege


def baum(wesen: str, pfad: str = "") -> list[dict]:
    eintraege = liste_ordner(wesen, pfad)
    for e in eintraege:
        if e["typ"] == "ordner":
            unterpfad = f"{pfad}/{e['name']}" if pfad else e["name"]
            e["kinder"] = baum(wesen, unterpfad)
    return eintraege


def lese_datei_info(wesen: str, pfad: str) -> dict:
    ziel = _sicherer_vault_pfad(wesen, pfad)
    if not ziel.is_file():
        raise FileNotFoundError(f"{pfad!r} existiert nicht in {wesen}s Vault")
    stat = ziel.stat()
    return {
        "pfad": str(ziel.relative_to(vault_pfad(wesen))),
        "inhalt": ziel.read_text(encoding="utf-8", errors="replace"),
        "geaendert": stat.st_mtime,
        "groesse": stat.st_size,
    }


def lese_datei(wesen: str, dateiname: str) -> str:
    """Wesen-freundlicher Lesezugriff -- haengt .md automatisch an, wie
    obsidian_vault_agent.oeffne_datei_und_lese() es fuer den normalen Vault tut.
    lese_datei_info() bleibt strikt (exakter Pfad), fuer den Web-Editor, der Namen
    immer schon mit Endung aus dem Dateibaum kennt."""
    if not dateiname.endswith(".md"):
        dateiname += ".md"
    return lese_datei_info(wesen, dateiname)["inhalt"]


def schreibe_datei_mechanisch(wesen: str, pfad: str, inhalt: str) -> Path:
    """Ueberschreibt komplett (kein Anhaengen) -- fuer den Web-Editor."""
    ziel = _sicherer_vault_pfad(wesen, pfad)
    if not ziel.name.endswith(".md"):
        ziel = ziel.with_name(ziel.name + ".md")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(inhalt, encoding="utf-8")
    return ziel


# Rueckwaertskompatibler Alias -- erste Fassung dieses Moduls hiess die
# Funktion schreibe_datei(), noch in Gebrauch falls woanders schon aufgerufen.
schreibe_datei = schreibe_datei_mechanisch


def oeffne_datei_und_schreibe(wesen: str, dateiname: str, text: str,
                                titel: str | None = None) -> Path:
    """Haengt text ans Ende einer Datei an (legt sie mit titel an falls sie noch
    nicht existiert).

    2026-09-17, Daniels Auftrag: echtes, vom System erzeugtes Datum/Uhrzeit vor
    jeden Eintrag setzen -- nicht dem Wesen ueberlassen. Grund: mehrere Eintraege
    in diesem Vault trugen erfundene/falsche Datumsangaben als Text
    ("2026-10-24", "2026-11-14" -- weit in der Zukunft, offenbar geraten statt
    gewusst). `datetime.now()` (Servertimezone Europe/Berlin, dieselbe Zeit wie
    in dieser Session sonst auch angesagt) ist die einzige verlaessliche Quelle,
    keine Annahme vom Wesen noetig. Bei mehreren Eintraegen in derselben Datei
    bekommt jeder einzelne seinen eigenen Zeitstempel, nicht nur der erste."""
    if not dateiname.endswith(".md"):
        dateiname += ".md"
    ziel = _sicherer_vault_pfad(wesen, dateiname)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if not ziel.exists():
        kopf = f"{titel}\n\n" if titel else ""
        ziel.write_text(kopf, encoding="utf-8")
    zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M Uhr")
    with ziel.open("a", encoding="utf-8") as f:
        f.write(f"\n---\n{zeitstempel}\n---\n\n")
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")
    return ziel


def loeschen(wesen: str, pfad: str) -> Path:
    """Verschiebt in einen wesen-eigenen _papierkorb-Ordner, kein echtes unlink()
    -- konsistent mit Grundgesetz 4 (nichts wird geloescht, nur unsichtbar gemacht)."""
    quelle = _sicherer_vault_pfad(wesen, pfad)
    if not quelle.is_file():
        raise FileNotFoundError(f"{pfad!r} existiert nicht in {wesen}s Vault")
    papierkorb = vault_pfad(wesen) / "_papierkorb"
    papierkorb.mkdir(parents=True, exist_ok=True)
    zeitstempel = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ziel = papierkorb / f"{zeitstempel}_{quelle.name}"
    quelle.rename(ziel)
    return ziel


def neuer_ordner(wesen: str, pfad: str) -> Path:
    ziel = _sicherer_vault_pfad(wesen, pfad)
    ziel.mkdir(parents=True, exist_ok=True)
    return ziel


def umbenennen(wesen: str, alter_pfad: str, neuer_name: str) -> Path:
    quelle = _sicherer_vault_pfad(wesen, alter_pfad)
    if not quelle.is_file():
        raise FileNotFoundError(f"{alter_pfad!r} existiert nicht in {wesen}s Vault")
    neuer_name = neuer_name.strip().lstrip("/")
    if not neuer_name.endswith(".md"):
        neuer_name += ".md"
    if "/" in neuer_name:
        raise ValueError("neuer_name darf keinen Ordner enthalten -- dafuer verschieben() nutzen")
    ziel = quelle.parent / neuer_name
    if ziel.exists():
        raise FileExistsError(f"{neuer_name!r} existiert in diesem Ordner bereits")
    quelle.rename(ziel)
    return ziel


def verschieben(wesen: str, quell_pfad: str, ziel_ordner: str) -> Path:
    quelle = _sicherer_vault_pfad(wesen, quell_pfad)
    if not quelle.is_file():
        raise FileNotFoundError(f"{quell_pfad!r} existiert nicht in {wesen}s Vault")
    ziel_verzeichnis = _sicherer_vault_pfad(wesen, ziel_ordner)
    ziel_verzeichnis.mkdir(parents=True, exist_ok=True)
    ziel = ziel_verzeichnis / quelle.name
    if ziel.exists():
        raise FileExistsError(f"{quelle.name!r} existiert im Zielordner bereits")
    quelle.rename(ziel)
    return ziel
