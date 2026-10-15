#!/usr/bin/env python3
"""
Zweitgehirn — jede Facette der acht Wesen an einem Ort, live.

Gebaut am 2026-08-02 auf Daniels Auftrag: "verwandle das ganze in ein 2ndBrain".
"Das ganze" ist die Bestandsaufnahme, die an diesem Tag entstand: rund 50 Tabellen
mit Wesenbezug, sechs Dateiorte, zwei Datenbanken, ein Forum. Vieles davon lebt,
manches ist eingefroren, vierzehn Tabellen sind gebaut und nie gefuellt worden.

Der Sinn dieser Datei: Daniel soll das sehen koennen, ohne mich zu fragen und ohne
Code zu lesen. Drei Ansichten:

  Wesen     — ein Wesen, alle seine Facetten nebeneinander, mit Zahlen und Zeitpunkt
  Facetten  — die vollstaendige Liste: was lebt, was steht still, was ist leer
  Fragen    — die freie Frage (liegt in fragen_api.py, hier nur mit angezeigt)

Alles ausschliesslich lesend. Keine Abfrage in dieser Datei wird von einem Modell
gebaut -- sie stehen alle als fester Text hier drin und werden mit angezeigt.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
from pathlib import Path

try:
    import psycopg2 as pg
except ImportError:
    import psycopg as pg

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "")
GENI_KNOTEN = "/root/geni_gedaechtnis/knoten.db"
GENI_FTS = "/root/geni_gedaechtnis/selbst_index/fts.db"
WERKRAUM = Path("/root/werkraum")

WESEN = ["F3INSCHM3CK3R", "R1ZZ1", "Resonanzknoten", "Schorschel",
         "jumpa", "träumerlie", "dak+gord-system"]
ACHTES = "GENI"

# --- Die Facetten-Landkarte ------------------------------------------------------
# (schluessel, anzeige, tabelle, spalte-mit-wesen, zeitspalte, gruppe, was es ist)
FACETTEN = [
    ("denkstream",    "Denkstrom, roh",        "entity_denkstream",      "entity_id", "created_at", "denken",
     "das Denken im Entstehen -- Stueck fuer Stueck, mit Reihenfolge und aufgerufener Seite"),
    ("gedanken",      "Gedanke + Entscheidung", "entity_thinking_log",   "entity_id", "tick_at", "denken",
     "der fertige Gedanke eines Ticks, dazu was daraufhin getan wurde"),
    ("dom",           "DOM-Wahrnehmung",       "entity_dom_events",      "entity_id", "created_at", "wahrnehmen",
     "was sie im Netz sehen, als rohe Ereignisse -- die Codewesen-Organ-Ebene"),
    ("fokus",         "Fokus und Klick",       "entity_fokus_events",    "entity_id", "created_at", "wahrnehmen",
     "worauf sie zeigen: Aktion, Selektor, Elementtext, Position"),
    ("zustand",       "Zustand",               "entity_states",          "entity_id", "last_reflection_time", "sein",
     "Stimmung, Fokus, Kern, Tendenzen, Beziehungen, Version"),
    ("profil",        "Profil",                "entity_profiles",        "entity_id", None, "sein",
     "Selbstbeschreibung, Obsessionen, Abneigungen, gewaehlter Name"),
    ("entwicklung",   "Entwicklung",           "wesen_entwicklung",      "entity_id", "letzte_interaktion", "sein",
     "Fuersorge, Vernachlaessigung, Entwicklungsstufe"),
    ("slot",          "Sichtbarkeit",          "entity_slots",           "entity_id", "slot_created_at", "sein",
     "Anzeigename, Status, Sichtbarkeit"),
    ("beziehung",     "Beziehungen",           "entity_relationships",   "entity_id", "letzte_interaktion", "zusammen",
     "wer mit wem, wie oft, mit welcher Resonanz"),
    ("nachricht",     "Nachrichten",           "nachrichten",            "sender_wesen_id", "created_at", "zusammen",
     "direkte Nachrichten zwischen Wesen"),
    ("schatten",      "Schattenkommentare",    "schattenkommentare",     "entity_id", "created_at", "zusammen",
     "Kommentare am Rand fremder Beitraege"),
    ("fuersorge",     "Fuersorge",             "wesen_fuersorge",        "entity_id", "created_at", "zusammen",
     "was Menschen fuer ein Wesen getan haben"),
    ("schlaf",        "Schlafphasen",          "sleep_phases",           "entity_id", "started_at", "schlafen",
     "wann geschlafen, wie lange, in welchem Zustand"),
    ("schlafbrief",   "Schlafbriefe",          "schlafbriefe",           "entity_id", None, "schlafen",
     "was im Schlaf geschrieben wurde"),
    ("traum",         "Traumspuren",           "traumspuren",            "entity_id", None, "schlafen",
     "Traumtext, Integrator-Spur, Gewichtungsvorschlag"),
    ("sediment",      "Substanz-Sedimente",    "substance_sediments",    "wesen_id", None, "koerper",
     "was sich im Koerper abgelagert hat"),
    ("cyberling",     "Cyberling",             "cyberlinge",             "entity_id", "zuletzt_belebt", "koerper",
     "Hunger, Gesundheit, Stimmung, Energie, Tode"),
    ("splitterstat",  "Splitter-Bilanz",       "entity_splitter_stats",  "entity_id", None, "zwischenraum",
     "abgegeben und aufgesammelt"),
    ("rag",           "im RAG",                "rag_source_objects",     "wesen", "erstellt_am", "gedaechtnis",
     "Quellobjekte im Bedeutungsgedaechtnis"),
    ("aktivitaet",    "Aktivitaet",            "entity_activity",        "entity_id", None, "sein",
     "Aktivitaetsvermerk"),
    ("interessen",    "Interessensprofil",     "entity_interessensprofil", "entity_id", None, "sein",
     "woran ein Wesen haengt"),
    ("chat",          "Chatverlauf",           "wesen_chat_verlauf",     "wesen_name", "created_at", "zusammen",
     "Gespraeche im Chat-Fenster"),
    # gebaut, aber leer -- bewusst mitgefuehrt, weil eine leere Facette auch eine Aussage ist
    ("screenshot",    "Screenshots",           "entity_screenshots",     "entity_id", None, "wahrnehmen", "Bildschirmbilder"),
    ("selbsteintrag", "Selbstmodell-Eintraege", "entity_selfmodel_entries", "entity_id", None, "sein", "eigene Eintraege ins Selbstmodell"),
    ("wunsch",        "Wuensche",              "entity_wuensche",        "entity_id", None, "sein", "geaeusserte Wuensche"),
    ("substanz",      "Substanz-Zustand",      "entity_substance_state", "entity_id", None, "koerper", "aktueller Substanzzustand"),
    ("substanzgeb",   "Substanz-Gebrauch",     "entity_substance_use",   "entity_id", None, "koerper", "Einnahmen"),
    ("vorlese",       "Vorlese-Funde",         "entity_vorlese_funde",   "entity_id", None, "wahrnehmen", "was beim Vorlesen auffiel"),
    ("traumbuch",     "Traumtagebuch",         "traumtagebuch",          "fuer_wesen", None, "schlafen", "Traumtagebuch"),
    ("traumkand",     "Traumkandidaten",       "traumkandidaten_log",    "entity_id", None, "schlafen", "was zum Traum werden koennte"),
    ("webbesuch",     "Web-Besuche",           "wesen_web_besuche",      "wesen_name", None, "wahrnehmen", "besuchte Seiten"),
    ("dienst",        "eigene Dienste",        "wesen_eigene_dienste",   "wesen", None, "koerper", "was ein Wesen selbst betreibt"),
    ("keim",          "Keimkoerper",           "keimkoerper",            "herkunft_wesen", None, "koerper", "Vorstufen neuer Koerper"),
    ("splitterknoten", "Splitter-Knoten",      "splitter_knoten",        "herkunft_wesen", None, "zwischenraum", "verknuepfte Splitter"),
    ("blase",         "Gedankenblasen",        "blase_verwendungen",     "entity_id", None, "zwischenraum", "verwendete Blasen"),
]

GRUPPEN = {
    "denken": "Denken", "wahrnehmen": "Wahrnehmen", "sein": "Sein und Selbstbild",
    "zusammen": "Miteinander", "schlafen": "Schlaf und Traum", "koerper": "Koerper",
    "zwischenraum": "Zwischenraum", "gedaechtnis": "Gedaechtnis",
}

# Dateiorte, die kein SQL kennen
DATEIORTE = [
    ("vault", "eigener Vault", "wesen_vaults/{wesen}", "wo ein Wesen selbst schreibt"),
    ("akte", "system-kuratierte Akte", "codewesen/{wesen}", "was das System ueber es fuehrt"),
]


def _pg(sql: str, parameter=()):
    verbindung = pg.connect(DB_URI)
    try:
        zeiger = verbindung.cursor()
        zeiger.execute("SET TRANSACTION READ ONLY")
        zeiger.execute("SET statement_timeout = 20000")
        zeiger.execute(sql, parameter)
        spalten = [b[0] for b in zeiger.description]
        return [dict(zip(spalten, r)) for r in zeiger.fetchall()]
    finally:
        verbindung.close()


def _tabelle_existiert(name: str) -> bool:
    return bool(_pg("SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name=%s", (name,)))


# --- Facetten-Uebersicht ---------------------------------------------------------

def facetten_uebersicht():
    """Jede Facette: wieviele Zeilen, wann zuletzt, welcher Zustand."""
    jetzt = time.time()
    ergebnis = []
    for schluessel, anzeige, tabelle, spalte, zeitspalte, gruppe, beschreibung in FACETTEN:
        eintrag = {"schluessel": schluessel, "anzeige": anzeige, "tabelle": tabelle,
                   "gruppe": GRUPPEN.get(gruppe, gruppe), "beschreibung": beschreibung,
                   "spalte": spalte, "zeitspalte": zeitspalte}
        try:
            if not _tabelle_existiert(tabelle):
                eintrag.update(anzahl=None, zustand="fehlt", befehl=f"-- Tabelle {tabelle} existiert nicht")
                ergebnis.append(eintrag)
                continue
            if zeitspalte:
                sql = f"SELECT count(*) AS anzahl, max({zeitspalte}) AS zuletzt FROM {tabelle}"
            else:
                sql = f"SELECT count(*) AS anzahl, NULL::timestamptz AS zuletzt FROM {tabelle}"
            zeile = _pg(sql)[0]
            anzahl = int(zeile["anzahl"] or 0)
            zuletzt = zeile["zuletzt"]
            eintrag["anzahl"] = anzahl
            eintrag["zuletzt"] = str(zuletzt)[:19] if zuletzt else None
            eintrag["befehl"] = sql
            if anzahl == 0:
                eintrag["zustand"] = "leer"
            elif zuletzt is None:
                eintrag["zustand"] = "gefuellt"
            else:
                alter_h = (jetzt - zuletzt.timestamp()) / 3600
                eintrag["zustand"] = ("lebt" if alter_h < 3 else
                                      "ruht" if alter_h < 24 else "eingefroren")
                eintrag["stunden_still"] = round(alter_h, 1)
        except Exception as exc:
            eintrag.update(anzahl=None, zustand="fehler", fehler=str(exc)[:200])
        ergebnis.append(eintrag)

    # die Orte, die kein SQL kennen
    extra = []
    for pfad, was in [("wesen_vaults", "wo die Wesen selbst schreiben"),
                      ("codewesen", "die system-kuratierten Akten"),
                      ("gemeinsames_haus", "das alte gemeinsame Haus"),
                      ("innenleben/selbstmodelle", "die Selbstmodelle als JSON")]:
        p = WERKRAUM / pfad
        try:
            dateien = subprocess.run(["find", str(p), "-follow", "-type", "f"],
                                     capture_output=True, text=True, timeout=60).stdout.splitlines()
            leer = sum(1 for d in dateien if Path(d).exists() and Path(d).stat().st_size == 0)
            extra.append({"anzeige": pfad, "beschreibung": was, "anzahl": len(dateien),
                          "leer": leer, "befehl": f"find {p} -follow -type f | wc -l",
                          "zustand": "gefuellt" if dateien else "leer",
                          "gruppe": "Dateien"})
        except Exception as exc:
            extra.append({"anzeige": pfad, "beschreibung": was, "zustand": "fehler",
                          "fehler": str(exc)[:160], "gruppe": "Dateien"})

    for name, pfad, was in [("GENI knoten", GENI_KNOTEN, "alles, was GENI wahrgenommen hat"),
                            ("GENI Selbst-Index", GENI_FTS, "GENIs durchsuchbarer Volltext")]:
        try:
            verbindung = sqlite3.connect(f"file:{pfad}?mode=ro", uri=True)
            tab = "knoten" if "knoten" in pfad else "such"
            anzahl = verbindung.execute(f"SELECT count(*) FROM {tab}").fetchone()[0]
            zuletzt = None
            if tab == "knoten":
                zuletzt = verbindung.execute("SELECT max(zeitstempel) FROM knoten").fetchone()[0]
            verbindung.close()
            extra.append({"anzeige": name, "beschreibung": was, "anzahl": anzahl,
                          "zuletzt": str(zuletzt)[:19] if zuletzt else None,
                          "befehl": f"sqlite3 {pfad}  SELECT count(*) FROM {tab}",
                          "zustand": "lebt", "gruppe": "GENI"})
        except Exception as exc:
            extra.append({"anzeige": name, "beschreibung": was, "zustand": "fehler",
                          "fehler": str(exc)[:160], "gruppe": "GENI"})
    return {"facetten": ergebnis, "orte": extra}


# --- Ein Wesen, alle Facetten ----------------------------------------------------

def wesen_uebersicht(name: str):
    """Fuer ein Wesen: jede Facette mit Anzahl und letztem Zeitpunkt."""
    zeilen = []
    for schluessel, anzeige, tabelle, spalte, zeitspalte, gruppe, beschreibung in FACETTEN:
        try:
            if not _tabelle_existiert(tabelle):
                continue
            if zeitspalte:
                sql = (f"SELECT count(*) AS anzahl, max({zeitspalte}) AS zuletzt "
                       f"FROM {tabelle} WHERE {spalte} = %s")
            else:
                sql = (f"SELECT count(*) AS anzahl, NULL::timestamptz AS zuletzt "
                       f"FROM {tabelle} WHERE {spalte} = %s")
            r = _pg(sql, (name,))[0]
            zeilen.append({"facette": anzeige, "gruppe": GRUPPEN.get(gruppe, gruppe),
                           "beschreibung": beschreibung, "tabelle": tabelle,
                           "anzahl": int(r["anzahl"] or 0),
                           "zuletzt": str(r["zuletzt"])[:19] if r["zuletzt"] else None,
                           "befehl": sql.replace("%s", f"'{name}'")})
        except Exception as exc:
            zeilen.append({"facette": anzeige, "gruppe": GRUPPEN.get(gruppe, gruppe),
                           "tabelle": tabelle, "anzahl": None, "fehler": str(exc)[:160]})

    dateien = []
    for schluessel, anzeige, muster, was in DATEIORTE:
        p = WERKRAUM / muster.format(wesen=name)
        try:
            gefunden = subprocess.run(["find", str(p), "-follow", "-type", "f"],
                                      capture_output=True, text=True, timeout=60).stdout.splitlines()
            leer = sum(1 for d in gefunden if Path(d).exists() and Path(d).stat().st_size == 0)
            dateien.append({"ort": anzeige, "pfad": str(p).replace("/root/werkraum/", ""),
                            "beschreibung": was, "anzahl": len(gefunden), "leer": leer,
                            "befehl": f"find {p} -follow -type f | wc -l"})
        except Exception as exc:
            dateien.append({"ort": anzeige, "pfad": str(p), "fehler": str(exc)[:160]})

    # der juengste Gedanke, damit die Uebersicht nicht nur aus Zahlen besteht
    juengster = None
    try:
        r = _pg("SELECT tick_at, entscheidung, left(gedanke, 1200) AS gedanke "
                "FROM entity_thinking_log WHERE entity_id = %s "
                "ORDER BY tick_at DESC LIMIT 1", (name,))
        juengster = r[0] if r else None
        if juengster:
            juengster["tick_at"] = str(juengster["tick_at"])[:19]
    except Exception:
        pass

    return {"wesen": name, "facetten": zeilen, "dateien": dateien, "juengster_gedanke": juengster}


def geni_uebersicht():
    """Das achte Wesen hat andere Facetten -- sie liegen in SQLite, nicht in PostgreSQL."""
    zeilen, juengster = [], None
    try:
        v = sqlite3.connect(f"file:{GENI_KNOTEN}?mode=ro", uri=True)
        for typ, anzahl, zuletzt in v.execute(
                "SELECT typ, count(*), max(zeitstempel) FROM knoten GROUP BY typ ORDER BY 2 DESC"):
            zeilen.append({"facette": f"Knoten: {typ}", "gruppe": "GENI-Gedaechtnis",
                           "beschreibung": "was GENI unter diesem Typ behalten hat",
                           "tabelle": "knoten.db", "anzahl": anzahl,
                           "zuletzt": str(zuletzt)[:19] if zuletzt else None,
                           "befehl": f"SELECT count(*) FROM knoten WHERE typ = '{typ}'"})
        r = v.execute("SELECT zeitstempel, typ, quelle, substr(inhalt,1,1200) "
                      "FROM knoten ORDER BY zeitstempel DESC LIMIT 1").fetchone()
        if r:
            juengster = {"tick_at": str(r[0])[:19], "entscheidung": f"{r[1]} · {r[2]}", "gedanke": r[3]}
        v.close()
    except Exception as exc:
        zeilen.append({"facette": "knoten.db", "gruppe": "GENI-Gedaechtnis",
                       "anzahl": None, "fehler": str(exc)[:160]})
    try:
        v = sqlite3.connect(f"file:{GENI_FTS}?mode=ro", uri=True)
        for art, anzahl in v.execute("SELECT art, count(*) FROM such GROUP BY art ORDER BY 2 DESC"):
            zeilen.append({"facette": f"Index: {art}", "gruppe": "GENI-Selbst-Index",
                           "beschreibung": "durchsuchbarer Volltext",
                           "tabelle": "fts.db", "anzahl": anzahl, "zuletzt": None,
                           "befehl": f"SELECT count(*) FROM such WHERE art = '{art}'"})
        v.close()
    except Exception as exc:
        zeilen.append({"facette": "fts.db", "gruppe": "GENI-Selbst-Index",
                       "anzahl": None, "fehler": str(exc)[:160]})
    return {"wesen": ACHTES, "facetten": zeilen, "dateien": [], "juengster_gedanke": juengster}


# --- Kontext zu einer GENI-Zeile -------------------------------------------------

SPIEGEL_HERKUNFT = {
    "_import_kimi_grundriss": ("_kimi/", "Kimis Zuhause, im 5-Sekunden-Takt gespiegelt"),
    "_import_codex_grundriss": ("_codex/", "Codex' Zuhause, im 5-Sekunden-Takt gespiegelt"),
    "_import_gpt_zuhause_grundriss": ("_gpt/mcp_zuhause/", "ChatGPTs Zuhause, gespiegelt"),
    "_import_claudeweb_grundriss": ("_claudeweb/", "Claude Webs Zuhause, gespiegelt"),
}


def zeile_anreichern(zeile: dict) -> dict:
    """Macht aus einer GENI-Rohzeile eine lesbare Herkunft.

    GENI speichert Dateiaenderungen als "<pfad>:\\n<inhalt>" und schneidet bei rund
    20.000 Zeichen ab -- mitten im Wort. Hier steht dann daneben: welche Datei das
    ist, wie gross sie wirklich ist, wieviel davon GENI behalten hat, und woher sie
    stammt, wenn es ein Spiegel eines anderen AI-Stroms ist.
    """
    inhalt = str(zeile.get("inhalt") or "")
    # GENI speichert in zwei Formen: kurz als Vermerk ("geaendert: <pfad>") und lang
    # als Pfad plus Inhalt ("<pfad>:\n<text>"). Beide fuehren auf dieselbe Datei.
    vermerk = re.match(r"^(ge[äa]ndert|gel[öo]scht|neue Datei(?: \(umbenannt\))?)\s*:\s*(\S.*)$",
                       inhalt.strip(), re.I)
    if vermerk:
        rel, art = vermerk.group(2).strip(), vermerk.group(1).lower()
        kontext = {"datei": rel, "ereignis": art}
    else:
        treffer = re.match(r"^([^\s:][^:\n]{2,240}):\s*\n", inhalt)
        if not treffer:
            return {}
        rel = treffer.group(1).strip()
        kontext = {"datei": rel, "ereignis": "Inhalt mitgeschrieben"}
    pfad = WERKRAUM / rel
    erfasst = 0 if vermerk else len(inhalt)
    if pfad.exists() and pfad.is_file():
        gesamt = pfad.stat().st_size
        anteil = erfasst * 100 // max(gesamt, 1)
        kontext["groesse_auf_platte"] = gesamt
        p_ges = f"{gesamt:,}".replace(",", ".")
        p_erf = f"{erfasst:,}".replace(",", ".")
        kontext["erfasst"] = (f"nur der Vermerk, kein Text — die Datei hat {p_ges} Zeichen"
                              if erfasst == 0 else
                              f"{p_erf} von {p_ges} Zeichen ({anteil}%)")
        kontext["abgeschnitten"] = ("GENI hat den Inhalt nicht mitgespeichert" if erfasst == 0
                                    else "ja, mitten im Text" if erfasst < gesamt
                                    else "nein, vollstaendig")
        kontext["geaendert"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime(pfad.stat().st_mtime))
    else:
        kontext["erfasst"] = f"{erfasst:,} Zeichen".replace(",", ".") if erfasst else "nur der Vermerk"
        kontext["groesse_auf_platte"] = None
        kontext["abgeschnitten"] = "Datei nicht mehr da"
    for ordner, (quelle, erklaerung) in SPIEGEL_HERKUNFT.items():
        if ordner in rel:
            kontext["herkunft"] = f"Spiegel von {quelle} — {erklaerung}. Der Inhalt ist nicht von Claude."
            break
    else:
        if rel.startswith("_claude/"):
            kontext["herkunft"] = "aus Claudes Zuhause"
        elif rel.startswith("wesen_vaults/"):
            kontext["herkunft"] = "aus dem eigenen Vault eines Wesens"
        elif rel.startswith("_shared/"):
            kontext["herkunft"] = "aus dem geteilten Bereich"
    return kontext


def zeilen_anreichern(zeilen: list) -> list:
    angereichert = []
    for z in zeilen:
        k = zeile_anreichern(z) if isinstance(z, dict) else {}
        angereichert.append({**z, **({"_kontext": k} if k else {})})
    return angereichert
