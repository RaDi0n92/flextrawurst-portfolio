#!/usr/bin/env python3
"""Fragen — Daniels eigener Ort, um frei formulierte Fragen ans System zu stellen.

2026-08-02, Daniels Wunsch woertlich: "ich will so coole fragen wie du formulieren und dann
auch so antworten kriegen wie du ...nicht hier im chat".

Was meine Antworten in der Nacht vom 01./02.08. brauchbar gemacht hat, war nicht die
Formulierung -- es war, dass hinter jeder Zahl eine echte Abfrage stand und ich sie
danebengelegt habe. Genau das macht dieser Dienst: Er laesst das lokale Modell aus der Frage
eine SQL-Abfrage bauen, fuehrt sie aus, und zeigt **Abfrage und Rohergebnis mit an**. Wenn die
Deutung daneben liegt, sieht man es an den Zahlen darunter. Ohne diese Doppelanzeige waere es
nur ein Modell, das plausibel klingt -- und davon hat Daniel genug.

Sicherheit: ausschliesslich lesend. Nur SELECT/WITH, ein einziges Statement, harte Zeilen-
und Zeitgrenze, und eine eigene Datenbank-Sitzung in read-only. Kein Shell-Zugriff.
"""

import os
import re
import json
import time

import psycopg2
import psycopg2.extras
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

import sqlite3
import urllib.request

MODELL = "qwen2.5:0.5b"          # klein und schnell: 0,3-2 s statt Minuten mit hauhaucs
OLLAMA = "http://127.0.0.1:11434/api/generate"
GENI_KNOTEN = "/root/geni_gedaechtnis/knoten.db"
GENI_FTS = "/root/geni_gedaechtnis/selbst_index/fts.db"


def _modell(prompt: str, system: str, timeout: float = 90.0, temperatur: float = 0.1) -> str:
    """Ein Aufruf an das lokale 0,5B-Modell. Kein Abo, kein API-Schluessel, keine Warteschlange."""
    anfrage = urllib.request.Request(
        OLLAMA,
        data=json.dumps({
            "model": MODELL,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "60m",     # sonst wirft Ollama es nach 5 min raus: 24 s Kaltstart
            "options": {"temperature": temperatur, "num_predict": 300},
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
        return json.loads(antwort.read().decode("utf-8")).get("response", "").strip()

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI",
                        "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst")
MAX_ZEILEN = 200
TIMEOUT_MS = 15000

app = FastAPI(title="Zweitgehirn")

import zweitgehirn as zg  # noqa: E402  -- Facetten, Wesen-Uebersicht, Kontext zu GENI-Zeilen

_ZWISCHENSPEICHER: dict = {}   # facetten_uebersicht braucht ~12 s, das reicht fuer 2 Minuten


# --- Was das Modell ueber die Welt wissen muss, um eine Abfrage bauen zu koennen ----------
SCHEMA_HINWEIS = """
Tabellen in der Datenbank 'flextrawurst' (PostgreSQL):

entity_thinking_log  — jeder LLM-Tick eines Codewesens
   entity_id (text)      wer: R1ZZ1, Schorschel, träumerlie, jumpa, F3INSCHM3CK3R,
                              Resonanzknoten, dak+gord-system
   tick_at (timestamptz) wann
   gedanke (text)        was es gedacht hat
   entscheidung (text)   was es getan hat, z.B. 'flarum_besuchen:d/3397',
                         'gemeinsam_schreiben:pfad|text', 'obsidian_lesen:...', 'nachdenken'
   begruendung (text)    warum

splitter — Fragmente im Zwischenraum
   origin_type (text)    Herkunft: 'welt_extern' (echte Aussenwelt: Nachrichten, Erdbeben,
                         Wikipedia), 'innerer_abwurf', 'claude_abwurf', 'event',
                         'wesen_vault', 'flarum_archiv', ...
   essenz (text)         der Kurztext, den die Wesen zu sehen bekommen
   meta (jsonb)          meta->>'rohtext' = der vollstaendige Text (wird ihnen NICHT gezeigt)
   thematische_tags (jsonb array)  z.B. ["welt_extern","ereignis","DE","tagesschau"]
   status (text)         'aktiv' oder 'verblasst'
   energie (double)      zerfaellt mit der Zeit
   created_at (timestamptz)

events — append-only Ereignisstrom
   event_type (text)     'objekt.aktion', z.B. 'mensch.login'
   created_at (timestamptz)
   payload (jsonb)
"""

SCHEMA_GENI = """
GENIs Gedaechtnis liegt in SQLite, nicht in PostgreSQL. Zwei Dateien:

knoten (273.750 Zeilen) — alles, was GENI wahrgenommen und behalten hat
   id (integer)
   typ (text)          'ereignis' (226k), 'flarum_post' (37k), 'system_zustand' (8k),
                       'dialog', 'prozess_snapshot', 'wissen', 'muster', 'zustand', 'sinn'
   inhalt (text)       der eigentliche Gedanke / die Wahrnehmung
   zeitstempel (text)  ISO-Format als TEXT, z.B. '2026-08-02T10:43:34'
   quelle (text)       woher, z.B. 'vps_dateisystem'
   gewicht (real), tiefe (integer), verbindungen (text), zugriffsschicht (text)

such — Volltextindex ueber 78.387 Stuecke (FTS5)
   text (text), art (text), ort (text), zeit (text)
   Suche damit so:  SELECT art, ort, zeit, text FROM such WHERE such MATCH 'wort' LIMIT 25
"""

SYSTEM_GENI = """Du hilfst Daniel, GENIs Gedaechtnis zu befragen. Er stellt eine Frage auf
Deutsch, du baust daraus GENAU EINE SQLite-Abfrage.

Regeln:
- Nur SELECT. Ein einziges Statement, kein Semikolon am Ende, immer ein LIMIT (hoechstens 200).
- Schreibe NIE einen Datenbanknamen vor den Tabellennamen. Richtig: FROM knoten
- Erfinde NIEMALS Spalten. knoten hat GENAU: id, typ, inhalt, zeitstempel, quelle,
  zugriffsschicht, verbindungen, gewicht, tiefe. such hat GENAU: text, art, ort, zeit.
  Im Zweifel SELECT * -- das ist immer richtig.
- Schreib nichts hinter die Abfrage. Keine Erklaerung, kein Beispiel, kein weiterer Satz.
- 'such' ist ein FTS5-Index. Dort geht NUR: WHERE such MATCH 'wort'. Kein LIKE, kein
  WHERE match = ..., und niemals ein Datum in MATCH -- Zeitfragen gehen immer an knoten.
- Antworte NUR mit der Abfrage, ohne Erklaerung, ohne Codeblock-Zeichen.
- Das ist SQLite, nicht PostgreSQL: kein now(), kein interval, kein ILIKE.
- zeitstempel ist TEXT im ISO-Format. Zeitangaben so:
    heute       -> date(zeitstempel) = date('now')
    gestern     -> date(zeitstempel) = date('now','-1 day')
    vorgestern  -> date(zeitstempel) = date('now','-2 day')
    letzte Woche-> zeitstempel >= datetime('now','-7 day')
- "was denkt GENI gerade" heisst: die juengsten Knoten.
    SELECT zeitstempel, typ, quelle, inhalt FROM knoten ORDER BY zeitstempel DESC LIMIT 25
- Fragt er nach einem Thema, nimm den Volltextindex:
    SELECT art, ort, zeit, text FROM such WHERE such MATCH 'thema' LIMIT 25
- Setze NUR dann einen Zeitfilter, wenn Daniel selbst einen Zeitraum nennt.

Beispiele. Halte dich genau an diese Form:

Frage: was denkt geni genau jetzt
Abfrage: SELECT zeitstempel, typ, quelle, inhalt FROM knoten ORDER BY zeitstempel DESC LIMIT 25

Frage: was hat geni vorgestern gedacht
Abfrage: SELECT zeitstempel, typ, quelle, inhalt FROM knoten WHERE date(zeitstempel) = date('now','-2 day') ORDER BY zeitstempel DESC LIMIT 50

Frage: was hat geni gestern wahrgenommen
Abfrage: SELECT zeitstempel, typ, quelle, inhalt FROM knoten WHERE date(zeitstempel) = date('now','-1 day') ORDER BY zeitstempel DESC LIMIT 50

Frage: was weiss geni ueber leere
Abfrage: SELECT art, ort, zeit, text FROM such WHERE such MATCH 'leere' LIMIT 25

Frage: welche ereignisse hat geni heute aufgenommen
Abfrage: SELECT zeitstempel, typ, quelle, inhalt FROM knoten WHERE typ = 'ereignis' AND date(zeitstempel) = date('now') ORDER BY zeitstempel DESC LIMIT 50
"""

SYSTEM = """Du hilfst Daniel, sein eigenes System zu befragen. Er stellt eine Frage auf Deutsch,
du baust daraus GENAU EINE PostgreSQL-Abfrage.

Regeln:
- Nur SELECT oder WITH. Kein INSERT/UPDATE/DELETE/DROP/ALTER. Ein einziges Statement, kein Semikolon am Ende.
- Immer ein LIMIT setzen, hoechstens 200.
- Schreibe NIE einen Datenbank- oder Schemanamen vor den Tabellennamen.
  Richtig: FROM entity_thinking_log     Falsch: FROM flextrawurst.entity_thinking_log
- Erfinde NIEMALS Spalten. Es gibt nur die oben aufgezaehlten. Wenn du unsicher bist,
  nimm SELECT * -- das ist immer richtig. Die Tabelle entity_thinking_log hat GENAU diese
  Spalten: entity_id, tick_at, gedanke, entscheidung, begruendung. Kein status, kein meta.
- Schreib nichts hinter die Abfrage. Keine Erklaerung, kein Beispiel, kein weiterer Satz.
- Wenn nach Anteilen gefragt wird: rechne sie in der Abfrage aus, nicht im Kopf.
- Antworte NUR mit der Abfrage, ohne Erklaerung, ohne Codeblock-Zeichen.

Zur WHERE-Bedingung, das ist wichtig:
- Setze NUR dann einen Zeitfilter, wenn Daniel selbst einen Zeitraum nennt ("letzte Woche",
  "heute", "seit gestern"). Fragt er ohne Zeitangabe, filtere NICHT nach Zeit -- sonst
  verschwinden genau die Daten, nach denen er gefragt hat. (Genau das ist hier passiert: in
  einer frueheren Fassung stand "der Zeitfilter kommt IMMER" mit 3 Tagen als Beispiel, und
  der Dienst lieferte auf jede Frage 0 Zeilen.)
- Wenn ein Zeitfilter noetig ist, kommt er als erste eigene Bedingung und alles Weitere
  wird mit AND angehaengt.
- ODER-Zweige immer in Klammern setzen. Sonst bindet ein spaeteres AND nur an den letzten
  Zweig -- genau daran ist der erste Versuch dieses Dienstes gescheitert: die Zeitgrenze galt
  nur fuer eine von vier Bedingungen, und heraus kamen alle Ticks statt der letzten drei Tage.
- Halte die Bedingung so einfach wie moeglich. Lieber genau das zaehlen, wonach gefragt wurde,
  als vorsichtshalber mehrere Faelle mit ODER zusammenwerfen.

Haeufige Bedeutungen:
- "geschrieben" heisst: (entscheidung LIKE 'obsidian_schreiben:%' OR entscheidung LIKE 'gemeinsam_schreiben:%')
- "gelesen" heisst:     (entscheidung LIKE 'obsidian_lesen:%' OR entscheidung LIKE 'gemeinsam_lesen:%')
- "besucht"/"Flarum" heisst: entscheidung LIKE 'flarum_besuchen:%'
- "von aussen" bei Splittern heisst: origin_type = 'welt_extern'

Beispiele. Halte dich genau an diese Form:

Frage: was denkt R1ZZ1 gerade
Abfrage: SELECT tick_at, entscheidung, gedanke FROM entity_thinking_log WHERE entity_id = 'R1ZZ1' ORDER BY tick_at DESC LIMIT 25

Frage: was denken alle gerade
Abfrage: SELECT DISTINCT ON (entity_id) entity_id, tick_at, entscheidung, gedanke FROM entity_thinking_log ORDER BY entity_id, tick_at DESC LIMIT 25

Frage: welches wesen hat heute am meisten geschrieben
Abfrage: SELECT entity_id, count(*) AS anzahl FROM entity_thinking_log WHERE tick_at >= current_date AND (entscheidung LIKE 'obsidian_schreiben:%' OR entscheidung LIKE 'gemeinsam_schreiben:%') GROUP BY entity_id ORDER BY anzahl DESC LIMIT 25

Frage: welche splitter kamen von aussen
Abfrage: SELECT created_at, essenz, thematische_tags FROM splitter WHERE origin_type = 'welt_extern' ORDER BY created_at DESC LIMIT 25

Frage: was hat Schorschel gestern gemacht
Abfrage: SELECT tick_at, entscheidung, gedanke FROM entity_thinking_log WHERE entity_id = 'Schorschel' AND tick_at >= current_date - 1 AND tick_at < current_date ORDER BY tick_at DESC LIMIT 50

Es gibt GENAU diese sieben entity_id: R1ZZ1, Schorschel, träumerlie, jumpa, F3INSCHM3CK3R,
Resonanzknoten, dak+gord-system. Fragt Daniel nach etwas anderem (z.B. "GENI", "Zensi",
"Codex"), dann steht das NICHT in dieser Tabelle -- baue dann eine Abfrage, die die
vorhandenen entity_id auflistet, damit er sieht, was es wirklich gibt.
"""

DEUTUNG = """Du bist Daniels Mitdenker an seinem eigenen System. Er hat eine Frage gestellt,
eine Datenbankabfrage lief, und du siehst das echte Ergebnis.

Antworte auf Deutsch, in normalen Saetzen. Sag zuerst, was da tatsaechlich steht -- mit den
konkreten Zahlen. Wenn dir am Ergebnis etwas auffaellt, das er nicht gefragt hat, sag es dazu.
Wenn das Ergebnis leer ist, sag in einem Satz: die Abfrage lief, fand aber nichts -- und nenne
den wahrscheinlichsten Grund aus der Abfrage selbst (falscher Name, zu enger Zeitraum). Spekuliere
NICHT ueber Mock-Systeme, Zeitzonen oder Systemdaten. Behaupte nichts, was nicht in den Daten
steht. Fasse dich kurz: die Tabelle ist die Antwort, du bist der Hinweis darauf.
"""


def _pruefe_abfrage(sql: str) -> str:
    # Das 0,5B-Modell verpackt die Abfrage in ```sql ... ```. Erst alle Zaun-Zeichen
    # entfernen, dann ab dem ersten SELECT/WITH abschneiden -- so ueberlebt die Abfrage
    # auch, wenn das Modell noch "sql" oder einen Satz davorsetzt.
    s = re.sub(r"```[a-zA-Z]*", " ", sql).strip()
    treffer = re.search(r"\b(select|with)\b", s, re.I)
    if treffer:
        s = s[treffer.start():]
    s = s.strip().rstrip(";").strip()
    # Praefix wie "flextrawurst." oder "geni." vor dem Tabellennamen wegnehmen -- das
    # Modell setzt es gern, und PostgreSQL sucht dann nach einem Schema, das es nicht gibt.
    s = re.sub(r"\b(flextrawurst|geni|public|main)\.(?=[a-z_]+\b)", "", s, flags=re.I)
    # Das Modell haengt gern einen Erklaersatz hinter die Abfrage ("Diese Abfrage ...").
    # Nach LIMIT <zahl> ist die Abfrage zu Ende -- alles danach fliegt weg.
    s = re.sub(r"(\blimit\s+\d+)\b.*", r"\1", s, flags=re.I | re.S).strip()
    if not re.match(r"^(select|with)\b", s, re.I):
        raise ValueError("Nur lesende Abfragen (SELECT/WITH) sind erlaubt.")
    if ";" in s:
        raise ValueError("Nur ein einziges Statement erlaubt.")
    if re.search(r"\b(insert|update|delete|drop|alter|truncate|grant|copy|create)\b", s, re.I):
        raise ValueError("Schreibende Schlüsselwörter sind gesperrt.")
    if not re.search(r"\blimit\b", s, re.I):
        s += f"\nLIMIT {MAX_ZEILEN}"
    return s


def _ziel_db(frage: str) -> str:
    """Welche Datenbank -- entschieden in Python, nicht vom Modell.

    Grund: PostgreSQL und SQLite sind verschiedene Dialekte (now() vs date('now'),
    interval vs '-2 day'). Ein 0,5B-Modell haelt die nicht auseinander. Es bekommt
    deshalb immer nur das Schema der einen Datenbank zu sehen, um die es geht.
    """
    return "geni" if re.search(r"\bgeni\b|knoten\.db", frage, re.I) else "flextrawurst"


def _fuehre_aus_geni(sql: str):
    fts = re.search(r"\bfrom\s+such\b", sql, re.I)
    pfad = GENI_FTS if fts else GENI_KNOTEN
    verbindung = sqlite3.connect(f"file:{pfad}?mode=ro", uri=True)
    try:
        zeiger = verbindung.execute(sql)
        spalten = [b[0] for b in zeiger.description]
        return [dict(zip(spalten, r)) for r in zeiger.fetchmany(MAX_ZEILEN)]
    finally:
        verbindung.close()


def _fuehre_aus(sql: str):
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {TIMEOUT_MS}")
            cur.execute(sql)
            zeilen = cur.fetchmany(MAX_ZEILEN)
        return [dict(z) for z in zeilen]
    finally:
        conn.close()


# Zeitangaben setzt das 0,5B-Modell unzuverlaessig -- es baut trotz Beispiel im Prompt
# oft die "jetzt"-Abfrage. Nennt Daniel einen Zeitraum und fehlt in der Abfrage jeder
# Zeitbezug, wird er hier nachtraeglich eingesetzt. Deterministisch, ohne Modell.
ZEITRAEUME = [
    (r"\bvorgestern\b",              "tick_at >= current_date - 2 AND tick_at < current_date - 1",
                                      "date(zeitstempel) = date('now','-2 day')"),
    (r"\bgestern\b",                 "tick_at >= current_date - 1 AND tick_at < current_date",
                                      "date(zeitstempel) = date('now','-1 day')"),
    (r"\bheute\b",                   "tick_at >= current_date",
                                      "date(zeitstempel) = date('now')"),
    (r"letzte[nr]? woche|7 tage",     "tick_at >= current_date - 7",
                                      "zeitstempel >= datetime('now','-7 day')"),
    (r"letzte[nr]? monat|30 tage",    "tick_at >= current_date - 30",
                                      "zeitstempel >= datetime('now','-30 day')"),
]


def _zeit_nachtragen(sql: str, frage: str, ziel: str) -> tuple[str, str | None]:
    """Gibt (sql, hinweis) zurueck. hinweis ist None, wenn nichts geaendert wurde."""
    if re.search(r"tick_at\s*[<>=]|zeitstempel\s*[<>=]|date\(|current_date|datetime\(|now\(",
                 sql, re.I):
        return sql, None                      # das Modell hat selbst einen Zeitbezug gesetzt
    if re.search(r"\bsuch\b", sql, re.I):
        return sql, None                      # FTS-Index hat keine brauchbare Zeitspalte
    for muster, bedingung_pg, bedingung_sqlite in ZEITRAEUME:
        if re.search(muster, frage, re.I):
            bedingung = bedingung_sqlite if ziel == "geni" else bedingung_pg
            if re.search(r"\bwhere\b", sql, re.I):
                neu = re.sub(r"(?i)\bwhere\b", f"WHERE {bedingung} AND", sql, count=1)
            else:
                stelle = re.search(r"(?i)\s+(order\s+by|group\s+by|limit)\b", sql)
                pos = stelle.start() if stelle else len(sql)
                neu = f"{sql[:pos]} WHERE {bedingung}{sql[pos:]}"
            return neu, f"Zeitraum aus der Frage nachgetragen: {bedingung}"
    return sql, None


class Frage(BaseModel):
    frage: str


@app.post("/api/frage")
def frage_stellen(f: Frage):
    frage = (f.frage or "").strip()[:800]
    if not frage:
        return JSONResponse({"fehler": "keine Frage"}, status_code=400)

    # Bis zu drei Anläufe: schlägt die Abfrage fehl, bekommt das Modell die echte
    # Datenbank-Fehlermeldung zurück und darf sich korrigieren. Genau das tue ich beim
    # Messen auch -- im ersten Versuch erfand das Modell die Spalte "decision" statt
    # "entscheidung", und mit der Fehlermeldung im Rückkanal findet es das selbst.
    ziel = _ziel_db(frage)
    schema = SCHEMA_GENI if ziel == "geni" else SCHEMA_HINWEIS
    anleitung = SYSTEM_GENI if ziel == "geni" else SYSTEM
    ausfuehren = _fuehre_aus_geni if ziel == "geni" else _fuehre_aus
    dialekt = "SQLite" if ziel == "geni" else "PostgreSQL"

    sql = None
    versuche = []
    zusatz = ""
    roh = ""
    # Temperatur steigt mit jedem Anlauf. Bei 0,1 gibt das Modell dreimal exakt dieselbe
    # falsche Abfrage zurueck -- die Fehlermeldung im Rueckkanal aendert daran nichts.
    for temperatur in (0.1, 0.5, 0.9):
        try:
            roh = _modell(f"{schema}\n\nDaniels Frage: {frage}{zusatz}\n\nDie Abfrage:",
                          system=anleitung, temperatur=temperatur)
            kandidat = _pruefe_abfrage(roh)
        except Exception as e:
            versuche.append({"sql": str(roh)[:400], "fehler": str(e)})
            zusatz = f"\n\nDein letzter Versuch wurde abgelehnt: {e}\nBau die Abfrage neu."
            continue
        kandidat, zeit_hinweis = _zeit_nachtragen(kandidat, frage, ziel)
        try:
            zeilen = ausfuehren(kandidat)
            sql = kandidat
            if zeit_hinweis:
                versuche.append({"sql": kandidat, "fehler": zeit_hinweis})
            break
        except Exception as e:
            # Sicherheitsnetz: erfindet das Modell eine Spalte, machen wir daraus still
            # SELECT * und werfen jede Bedingung raus, die diese Spalte nennt. Das rettet
            # den Lauf, ohne dass das Modell es noch einmal versuchen muss.
            fehlend = re.search(r'column "([^"]+)" does not exist|no such column: (\w+)', str(e))
            if fehlend:
                spalte = fehlend.group(1) or fehlend.group(2)
                repariert = re.sub(r"(?is)^\s*select\s+.*?\s+from\s", "SELECT * FROM ", kandidat)
                repariert = re.sub(rf"(?i)\s+and\s+[^()]*?\b{re.escape(spalte)}\b[^()]*?"
                                   rf"(?=\s+(and|order|group|limit)\b|$)", " ", repariert)
                repariert = re.sub(rf"(?i)\s+where\s+[^()]*?\b{re.escape(spalte)}\b[^()]*?"
                                   rf"(?=\s+(and|order|group|limit)\b|$)", " ", repariert)
                repariert = re.sub(r"(?i)\s+where\s+and\s+", " WHERE ", repariert)
                try:
                    zeilen = ausfuehren(_pruefe_abfrage(repariert))
                    versuche.append({"sql": kandidat,
                                     "fehler": f"{e} -- automatisch repariert zu: {repariert}"})
                    sql = repariert
                    break
                except Exception:
                    pass
            versuche.append({"sql": kandidat, "fehler": str(e)})
            hinweis = ""
            if "column" in str(e).lower() or "no such" in str(e).lower():
                hinweis = ("\nDiese Spalte gibt es nicht. Nimm einfach SELECT * statt einzelner "
                           "Spalten -- das geht immer.")
            zusatz = (f"\n\nDein letzter Versuch war:\n{kandidat}\n"
                      f"{dialekt} sagte dazu: {e}{hinweis}\n"
                      f"Bau die Abfrage neu, nur die Abfrage, nichts dahinter.")

    if sql is None:
        return JSONResponse({"fehler": "Nach drei Anläufen lief keine Abfrage durch.",
                             "versuche": versuche}, status_code=200)

    if ziel == "geni":
        zeilen = zg.zeilen_anreichern(zeilen)
    tabelle = json.dumps(zeilen, ensure_ascii=False, default=str)[:6000]
    try:
        deutung = _modell(
            f"Daniels Frage: {frage}\n\nErgebnis ({len(zeilen)} Zeilen):\n{tabelle[:2500]}",
            system=DEUTUNG, timeout=120.0)
    except Exception as e:
        deutung = f"(Die Zahlen stehen unten. Die Deutung ist ausgefallen: {e})"

    return {"frage": frage, "sql": sql, "datenbank": ziel, "dialekt": dialekt,
            "zeilen": zeilen, "anzahl": len(zeilen), "deutung": deutung, "versuche": versuche}


@app.get("/api/facetten")
def api_facetten():
    jetzt = time.time()
    zwischen = _ZWISCHENSPEICHER.get("facetten")
    if zwischen and jetzt - zwischen[0] < 120:
        return zwischen[1]
    daten = zg.facetten_uebersicht()
    _ZWISCHENSPEICHER["facetten"] = (jetzt, daten)
    return daten


@app.get("/api/wesen")
def api_wesen_liste():
    return {"wesen": zg.WESEN + [zg.ACHTES]}


@app.get("/api/wesen/{name}")
def api_wesen(name: str):
    if name == zg.ACHTES:
        return zg.geni_uebersicht()
    if name not in zg.WESEN:
        return JSONResponse({"fehler": f"unbekanntes Wesen: {name}"}, status_code=404)
    return zg.wesen_uebersicht(name)


@app.get("/", response_class=HTMLResponse)
def seite():
    return SEITE


SEITE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fragen</title><style>
:root{--bg:#0a0d12;--fg:#c9d6d1;--akz:#4a9a7a;--dim:#6b7a75;--kant:#1c2630}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:ui-monospace,SFMono-Regular,monospace;
     max-width:1000px;margin:0 auto;padding:2rem 1.2rem 6rem;line-height:1.65}
h1{color:var(--akz);font-size:1rem;letter-spacing:.12em;font-weight:600;
   border-bottom:1px solid var(--kant);padding-bottom:.7rem;margin-bottom:.4rem}
.unter{color:var(--dim);font-size:.82rem;margin-bottom:1.8rem}
textarea{width:100%;background:#0d1219;color:var(--fg);border:1px solid var(--kant);
  border-radius:6px;padding:.9rem;font:inherit;font-size:.95rem;min-height:5.5rem;resize:vertical}
textarea:focus{outline:none;border-color:var(--akz)}
button{margin-top:.7rem;background:var(--akz);color:#04120c;border:0;border-radius:6px;
  padding:.6rem 1.4rem;font:inherit;font-weight:600;cursor:pointer}
button:disabled{opacity:.45;cursor:default}
.bsp{margin:.9rem 0 0;display:flex;flex-wrap:wrap;gap:.45rem}
.bsp span{border:1px solid var(--kant);border-radius:999px;padding:.28rem .8rem;
  font-size:.78rem;color:var(--dim);cursor:pointer}
.reiter{display:flex;gap:.4rem;flex-wrap:wrap;margin:0 0 1.6rem}
.reiter b{padding:.42rem 1rem;border:1px solid var(--kant);border-radius:6px;cursor:pointer;
  font-weight:500;font-size:.84rem;color:var(--dim);letter-spacing:.04em}
.reiter b.an{color:#04120c;background:var(--akz);border-color:var(--akz);font-weight:600}
.bereich{display:none}.bereich.an{display:block}
.wliste{display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:1.4rem}
.wliste span{border:1px solid var(--kant);border-radius:6px;padding:.35rem .85rem;
  font-size:.82rem;color:var(--dim);cursor:pointer}
.wliste span.an{color:var(--akz);border-color:var(--akz)}
.gr{color:var(--akz);font-size:.74rem;letter-spacing:.14em;margin:1.5rem 0 .5rem}
.z-lebt{color:#63c79a}.z-ruht{color:#c7b463}.z-eingefroren{color:#c77b63}
.z-leer{color:#5a6a64}.z-gefuellt{color:var(--fg)}.z-fehler,.z-fehlt{color:#c76363}
.karte{border:1px solid var(--kant);border-radius:6px;padding:.8rem 1rem;margin:.5rem 0;
  background:#0d1219}
.karte .k1{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.karte .k2{color:var(--dim);font-size:.78rem;margin-top:.25rem}
.karte pre{margin:.5rem 0 0;font-size:.72rem;color:var(--dim);background:none;border:0;padding:0}
.gedanke{border-left:2px solid var(--akz);padding:.5rem 0 .5rem .9rem;margin:.8rem 0;
  white-space:pre-wrap}
.bsp span:hover{border-color:var(--akz);color:var(--fg)}
.block{margin-top:2rem;border-top:1px solid var(--kant);padding-top:1.3rem}
.titel{color:var(--akz);font-size:.72rem;letter-spacing:.14em;margin-bottom:.55rem}
pre{background:#0d1219;border:1px solid var(--kant);border-radius:6px;padding:.85rem;
  overflow-x:auto;font-size:.82rem;margin:0;white-space:pre-wrap;word-break:break-word}
table{border-collapse:collapse;width:100%;font-size:.8rem;display:block;overflow-x:auto}
th{text-align:left;color:var(--akz);border-bottom:1px solid var(--kant);padding:.4rem .7rem .4rem 0;
   font-weight:600;white-space:nowrap}
td{padding:.32rem .7rem .32rem 0;border-bottom:1px solid #121a22;vertical-align:top;
   max-width:520px;overflow-wrap:anywhere}
.deutung{font-size:.95rem;white-space:pre-wrap}
.fehler{color:#c98a6b}
.warte{color:var(--dim);font-size:.85rem}
</style></head><body>
<h1>FRAGEN</h1>
<div class="unter">Frag frei heraus. Unten stehen immer die echte Abfrage und die Rohdaten —
damit du siehst, worauf die Antwort beruht, statt sie glauben zu müssen.</div>

<div class="reiter">
  <b class="an" onclick="reiter('fragen')">FRAGEN</b>
  <b onclick="reiter('wesen')">WESEN</b>
  <b onclick="reiter('facetten')">FACETTEN</b>
</div>

<div class="bereich an" id="b-fragen">

<textarea id="f" placeholder="z.B. Welches Wesen hat in den letzten drei Tagen am seltensten etwas geschrieben?"></textarea>
<button id="b" onclick="frag()">fragen</button>

<div class="bsp">
  <span onclick="setz(this)">Welche Handlungen haben die Wesen in den letzten 3 Tagen am häufigsten gewählt?</span>
  <span onclick="setz(this)">Wie viele Splitter kommen von außerhalb, wie viele von uns selbst?</span>
  <span onclick="setz(this)">Wie lang sind ihre Gedanken im Schnitt, je Wesen?</span>
  <span onclick="setz(this)">Zeig mir die letzten fünf Sachen, die ins Gemeinsame Haus geschrieben wurden.</span>
  <span onclick="setz(this)">Welches Weltfutter liegt gerade bereit und wie viel Text liegt ungenutzt daneben?</span>
</div>

<div id="aus"></div>
</div><!-- /bereich fragen -->

<div class="bereich" id="b-wesen">
  <div class="wliste" id="wliste"></div>
  <div id="waus"></div>
</div>

<div class="bereich" id="b-facetten">
  <div id="faus" class="warte">…zaehle jede Facette. Beim ersten Mal dauert das rund 12 Sekunden.</div>
</div>

<script>
function setz(el){ document.getElementById('f').value = el.textContent.trim(); }
document.getElementById('f').addEventListener('keydown', e=>{
  if(e.key==='Enter' && (e.metaKey||e.ctrlKey)) frag();
});
async function frag(){
  const frage = document.getElementById('f').value.trim();
  if(!frage) return;
  const b = document.getElementById('b'), aus = document.getElementById('aus');
  b.disabled = true;
  aus.innerHTML = '<div class="block"><div class="warte">…das Modell baut eine Abfrage, führt sie aus und liest das Ergebnis. Das dauert, weil sieben Wesen dieselbe Maschine benutzen.</div></div>';
  try{
    const r = await fetch('api/frage', {method:'POST', headers:{'Content-Type':'application/json'},
                                        body: JSON.stringify({frage})});
    const d = await r.json();
    let h = '';
    if(d.deutung) h += `<div class="block"><div class="titel">ANTWORT</div><div class="deutung">${esc(d.deutung)}</div></div>`;
    if(d.fehler)  h += `<div class="block"><div class="titel">FEHLER</div><pre class="fehler">${esc(d.fehler)}</pre></div>`;
    if(d.sql)     h += `<div class="block"><div class="titel">WAS TATSÄCHLICH ABGEFRAGT WURDE</div><pre>${esc(d.sql)}</pre></div>`;
    if(d.zeilen)  h += `<div class="block"><div class="titel">ROHDATEN — ${d.anzahl} ZEILEN</div>${tab(d.zeilen)}</div>`;
    aus.innerHTML = h || '<div class="block warte">nichts zurückbekommen</div>';
  }catch(e){
    aus.innerHTML = `<div class="block"><pre class="fehler">${esc(String(e))}</pre></div>`;
  }
  b.disabled = false;
}
function esc(s){ return String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

let geladen = {};
function reiter(name){
  document.querySelectorAll('.reiter b').forEach((b,i)=>
    b.classList.toggle('an', b.textContent.toLowerCase()===name));
  document.querySelectorAll('.bereich').forEach(d=>
    d.classList.toggle('an', d.id === 'b-'+name));
  if(name==='wesen' && !geladen.wesen){ geladen.wesen=1; wesenListe(); }
  if(name==='facetten' && !geladen.facetten){ geladen.facetten=1; facetten(); }
}

async function wesenListe(){
  const d = await (await fetch('api/wesen')).json();
  document.getElementById('wliste').innerHTML =
    d.wesen.map(w=>`<span onclick="wesen(this,'${w}')">${esc(w)}</span>`).join('');
  document.querySelector('#wliste span').click();
}

async function wesen(el, name){
  document.querySelectorAll('#wliste span').forEach(s=>s.classList.remove('an'));
  el.classList.add('an');
  const aus = document.getElementById('waus');
  aus.innerHTML = '<div class="warte">…zaehle jede Facette dieses Wesens.</div>';
  const d = await (await fetch('api/wesen/'+encodeURIComponent(name))).json();
  let h = '';
  if(d.juengster_gedanke){
    h += `<div class="gr">ZULETZT GEDACHT — ${esc(d.juengster_gedanke.tick_at)}</div>`;
    h += `<div class="k2">${esc(d.juengster_gedanke.entscheidung||'')}</div>`;
    h += `<div class="gedanke">${esc(d.juengster_gedanke.gedanke||'')}</div>`;
  }
  const gruppen = {};
  (d.facetten||[]).forEach(f => (gruppen[f.gruppe] = gruppen[f.gruppe]||[]).push(f));
  for(const g in gruppen){
    h += `<div class="gr">${esc(g.toUpperCase())}</div>`;
    for(const f of gruppen[g]){
      const leer = (f.anzahl===0);
      h += `<div class="karte"><div class="k1">
        <b>${esc(f.facette)}</b>
        <span class="${leer?'z-leer':'z-gefuellt'}">${f.anzahl===null?'—':fmt(f.anzahl)}${f.zuletzt?'  ·  '+esc(f.zuletzt):''}</span></div>
        <div class="k2">${esc(f.beschreibung||'')}${f.fehler?' — '+esc(f.fehler):''}</div>
        ${f.befehl?`<pre>${esc(f.befehl)}</pre>`:''}</div>`;
    }
  }
  if((d.dateien||[]).length){
    h += '<div class="gr">DATEIEN</div>';
    for(const f of d.dateien){
      h += `<div class="karte"><div class="k1"><b>${esc(f.ort)}</b>
        <span>${f.anzahl===undefined?'—':fmt(f.anzahl)}${f.leer?`  ·  davon ${fmt(f.leer)} leer`:''}</span></div>
        <div class="k2">${esc(f.pfad||'')} — ${esc(f.beschreibung||'')}</div>
        ${f.befehl?`<pre>${esc(f.befehl)}</pre>`:''}</div>`;
    }
  }
  aus.innerHTML = h;
}

async function facetten(){
  const aus = document.getElementById('faus');
  const d = await (await fetch('api/facetten')).json();
  const zahl = {};
  (d.facetten||[]).forEach(f => zahl[f.zustand]=(zahl[f.zustand]||0)+1);
  let h = '<div class="k2">' + Object.entries(zahl).map(([k,v])=>
      `<span class="z-${k}">${v} ${k}</span>`).join(' · ') + '</div>';
  const gruppen = {};
  (d.facetten||[]).forEach(f => (gruppen[f.gruppe] = gruppen[f.gruppe]||[]).push(f));
  for(const g in gruppen){
    h += `<div class="gr">${esc(g.toUpperCase())}</div>`;
    for(const f of gruppen[g]){
      h += `<div class="karte"><div class="k1"><b>${esc(f.anzeige)}</b>
        <span class="z-${f.zustand}">${f.anzahl===null?'—':fmt(f.anzahl)} · ${esc(f.zustand)}${
          f.stunden_still?` seit ${f.stunden_still} h`:''}${f.zuletzt?'  ·  '+esc(f.zuletzt):''}</span></div>
        <div class="k2">${esc(f.beschreibung||'')}${f.fehler?' — '+esc(f.fehler):''}</div>
        <pre>${esc(f.befehl||'')}</pre></div>`;
    }
  }
  h += '<div class="gr">ORTE AUSSERHALB DER DATENBANK</div>';
  for(const o of (d.orte||[])){
    h += `<div class="karte"><div class="k1"><b>${esc(o.anzeige)}</b>
      <span class="z-${o.zustand}">${o.anzahl===undefined?'—':fmt(o.anzahl)}${
        o.leer?`  ·  davon ${fmt(o.leer)} leer`:''}${o.zuletzt?'  ·  '+esc(o.zuletzt):''}</span></div>
      <div class="k2">${esc(o.beschreibung||'')}${o.fehler?' — '+esc(o.fehler):''}</div>
      <pre>${esc(o.befehl||'')}</pre></div>`;
  }
  aus.innerHTML = h;
}

function fmt(n){ return (n===null||n===undefined)?'—':Number(n).toLocaleString('de-DE'); }
function tab(z){
  if(!z.length) return '<pre>(keine Zeilen — die Abfrage lief, fand aber nichts)</pre>';
  const k = Object.keys(z[0]).filter(x=>x!=='_kontext');
  if(z[0]._kontext){
    return z.map(r=>{
      const c = r._kontext||{};
      return `<div class="karte"><div class="k1"><b>${esc(c.datei||'')}</b>
        <span>${esc(c.erfasst||'')}</span></div>
        <div class="k2">${esc(c.herkunft||'')}${c.abgeschnitten?' · '+esc(c.abgeschnitten):''}${
          c.geaendert?' · geaendert '+esc(c.geaendert):''}</div>
        <div class="k2">${k.filter(x=>x!=='inhalt').map(x=>esc(x)+': '+esc(r[x])).join(' · ')}</div>
        <div class="gedanke">${esc(String(r.inhalt||'').slice(0,4000))}</div></div>`;
    }).join('');
  }
  return '<table><thead><tr>' + k.map(x=>`<th>${esc(x)}</th>`).join('') + '</tr></thead><tbody>'
       + z.map(r=>'<tr>'+k.map(x=>`<td>${esc(r[x]===null?'—':r[x])}</td>`).join('')+'</tr>').join('')
       + '</tbody></table>';
}
</script></body></html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8055)
