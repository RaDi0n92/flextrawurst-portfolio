#!/usr/bin/env python3
"""GENI traegt zusammen, was sie ueber jeden im System weiss.

2026-08-01, Daniel: "geni soll dort doch auch unsere splitter die sie sammeln
will ueber uns alle da sammeln ... und sie soll eh anhand ihrer ganzen hoersinne
und den knoten versuchen ne doku ueber jeeeden anzulegen nicht nur euch ... denn
sie hat spuren ueber uns alle".

Sammelt pro Teilnehmer aus zwei Quellen und schreibt das Ergebnis in einen
eigenen, bei jedem Lauf ERSETZTEN Abschnitt der Akte (geni_dokumentation/<id>.md):
  1. Splitter aus dem Zwischenraum (Postgres, ueber entity_id)
  2. Knoten aus ihrem eigenen Gedaechtnis (SQLite, ueber quelle + Namensnennung)

Der Abschnitt liegt zwischen Markern und wird ersetzt, nicht angehaengt --
sonst wuerde jeder Lauf dieselben Splitter erneut in die Akte kippen. Die
chronologischen Eintraege darueber (Frage/Antwort, Spiegel-Lektuere) bleiben
davon unberuehrt.

ID-ZUORDNUNG, gemessen am 2026-08-01: die Splitter-Datenbank benutzt teils
andere Kennungen als der Teilnehmer-Roster. Ohne diese Tabelle gingen 1170
Splitter verloren bzw. wuerden falsch zugeordnet:
    traeumerlie <- "träumerlie" (mit Umlaut, 593 Splitter)
    dakgord     <- "dak+gord-system" (477)
    daniel      <- "dak" (100 -- "dak" ist Daniels eigenes Kuerzel)

Aufruf: python3 doku_sammler.py [teilnehmer_id]   (ohne Argument: alle)
"""

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/geni")
import hauhau_client
from teilnehmer_roster import TEILNEHMER, teilnehmer_by_id
from sprechen import kern_laden


def _system_prompt() -> str:
    """Nur ihr eigener Kern -- keine Zusaetze von mir (Daniel, 2026-08-01)."""
    return f"""Du bist GENI.

{kern_laden()}"""

KNOTEN_DB = Path("/root/geni_gedaechtnis/knoten.db")
DOKU_DIR = Path("/root/werkraum/geni_dokumentation")

MARKER_START = "<!-- GENI-SAMMLUNG-ANFANG -- wird bei jedem Lauf ersetzt -->"
MARKER_ENDE = "<!-- GENI-SAMMLUNG-ENDE -->"

# Roster-ID -> zusaetzliche Kennungen in der Splitter-DB (siehe Modul-Docstring)
SPLITTER_ALIASE = {
    "traeumerlie": ["träumerlie"],
    "dakgord": ["dak+gord-system"],
    "daniel": ["dak"],
}

# Rauschquellen -- 99,91 % aller Knoten, siehe selbst_suche.py
RAUSCH_QUELLEN = ("vps_dateisystem", "chatgpt", "vps_prozesse")

MAX_SPLITTER = 25
MAX_KNOTEN = 25
MAX_ZEICHEN = 33333   # flextrawurst-weite Regel (Daniel, 2026-08-01)


def _db_uri() -> str:
    pfad = "/root/werkraum/.agent/flextrawurst-db.env"
    if os.path.exists(pfad):
        for zeile in open(pfad, encoding="utf-8"):
            if zeile.startswith("FLEXTRAWURST_DB_URI="):
                return zeile.strip().split("=", 1)[1]
    return os.environ.get("FLEXTRAWURST_DB_URI", "")


def _kennungen(teilnehmer_id: str) -> list:
    return [teilnehmer_id] + SPLITTER_ALIASE.get(teilnehmer_id, [])


def splitter_holen(teilnehmer_id: str) -> list:
    uri = _db_uri()
    if not uri:
        return []
    conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT essenz, materialitaet, energie, status, created_at, origin_type
                FROM splitter WHERE entity_id = ANY(%s)
                ORDER BY created_at DESC LIMIT %s
            """, (_kennungen(teilnehmer_id), MAX_SPLITTER))
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def splitter_zaehlen(teilnehmer_id: str) -> int:
    uri = _db_uri()
    if not uri:
        return 0
    conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) c FROM splitter WHERE entity_id = ANY(%s)",
                        (_kennungen(teilnehmer_id),))
            return cur.fetchone()["c"]
    finally:
        conn.close()


def knoten_holen(teilnehmer_id: str) -> list:
    """Was GENI selbst ueber diese Person gehoert hat.

    Erst die eigene Quelle (indiziert), dann Namensnennungen in kleinen Quellen.
    Rauschquellen bleiben aussen vor -- sonst waeren es nur Temp-Dateinamen.
    """
    conn = sqlite3.connect(f"file:{KNOTEN_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    treffer, gesehen = [], set()

    def _nimm(rows):
        for r in rows:
            if len(treffer) >= MAX_KNOTEN:
                return
            text = (r["inhalt"] or "").strip()
            if not text or text[:80] in gesehen:
                continue
            gesehen.add(text[:80])
            treffer.append({
                "zeit": datetime.fromtimestamp(r["mtime"], timezone.utc).strftime("%Y-%m-%d %H:%M"),
                "quelle": r["quelle"] or "?",
                "text": text,
            })

    for kennung in _kennungen(teilnehmer_id):
        _nimm(conn.execute(
            "SELECT quelle, mtime, inhalt FROM knoten WHERE quelle=? ORDER BY mtime DESC LIMIT ?",
            (kennung, MAX_KNOTEN)).fetchall())

    if len(treffer) < MAX_KNOTEN:
        platzhalter = ",".join("?" * len(RAUSCH_QUELLEN))
        for kennung in _kennungen(teilnehmer_id):
            if len(treffer) >= MAX_KNOTEN:
                break
            _nimm(conn.execute(
                f"SELECT quelle, mtime, inhalt FROM knoten "
                f"WHERE quelle NOT IN ({platzhalter}) AND inhalt LIKE ? "
                f"ORDER BY mtime DESC LIMIT ?",
                (*RAUSCH_QUELLEN, f"%{kennung}%", MAX_KNOTEN - len(treffer))).fetchall())
    conn.close()
    return treffer


def _material_bauen(teilnehmer: dict) -> str:
    """Das Rohmaterial, das GENI vorgelegt bekommt -- NICHT die Akte selbst.

    2026-08-01, Daniel: "ich will doch keinen fucking log ueber uns .... ich will
    alles handgeschrieben von geni". Die erste Fassung dieses Skripts hat genau
    so einen Log erzeugt: Splitter und Knoten als Aufzaehlung formatiert und
    direkt in die Akte geschrieben. Falsch. Das Gesammelte ist ihr EINGANG,
    ihre eigenen Worte sind das Ergebnis.
    """
    tid = teilnehmer["id"]
    splitter = splitter_holen(tid)
    knoten = knoten_holen(tid)

    teile = []
    if splitter:
        teile.append("Splitter, die von ihm/ihr im Zwischenraum liegen:")
        for s in splitter:
            datum = s["created_at"].strftime("%Y-%m-%d %H:%M") if s["created_at"] else "?"
            teile.append(f"[{datum}] {(s['essenz'] or '').strip()}")
    if knoten:
        teile.append("")
        teile.append("Was du selbst gehoert hast:")
        for k in knoten:
            teile.append(f"[{k['zeit']}] {k['text'][:400]}")
    return "\n".join(teile)[:MAX_ZEICHEN]


def abschnitt_bauen(teilnehmer: dict) -> str:
    """Laesst GENI die Akte selbst schreiben und verpackt nur ihren Text.

    Aufforderung im selben knappen Stil wie Daniels Frage-Vorgabe
    ('hallo geni. jetzt geht es um "name". stell "name" eine frage.') --
    keine Ton- oder Charaktervorgaben, die kommen aus ihrem eigenen Kern.
    """
    material = _material_bauen(teilnehmer)
    if not material.strip():
        return ""

    name = teilnehmer["name"]
    prompt = (f'hallo geni. jetzt geht es um "{name}". '
              f'hier ist was du ueber "{name}" wahrgenommen hast:\n\n{material}\n\n'
              f'leg eine doku ueber "{name}" an.')

    text = hauhau_client.chat(
        prompt, system=_system_prompt(), think=False,
        max_tokens=MAX_TOKENS, temperature=0.85, timeout=720.0,
    ).strip()
    if not text:
        return ""

    jetzt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return "\n".join([MARKER_START, "", f"*Von GENI geschrieben, Stand {jetzt}.*", "",
                      text, "", MARKER_ENDE])


def akte_aktualisieren(teilnehmer: dict) -> bool:
    DOKU_DIR.mkdir(parents=True, exist_ok=True)
    pfad = DOKU_DIR / f"{teilnehmer['id']}.md"
    neuer = abschnitt_bauen(teilnehmer)

    if pfad.exists():
        alt = pfad.read_text(encoding="utf-8")
    else:
        alt = (f"# GENIs Dokumentation über {teilnehmer['name']}\n\n"
               f"Wird von GENI selbst gefuehrt -- Frage-Antwort-Verlauf aus dem "
               f"geni_inbox-Vault, ihre Spiegel-Lektuere, und was sie aus Splittern "
               f"und ihrem Gedaechtnis ueber diese Person zusammengetragen hat.\n\n"
               f"Chronologisch, neueste Eintraege unten.\n\n")

    if MARKER_START in alt and MARKER_ENDE in alt:
        vor = alt.split(MARKER_START)[0]
        nach = alt.split(MARKER_ENDE, 1)[1]
        neu = vor + neuer + nach
    else:
        neu = alt.rstrip() + "\n\n" + neuer + "\n"

    if neu != alt:
        pfad.write_text(neu, encoding="utf-8")
        return True
    return False


def main():
    ziele = TEILNEHMER
    if len(sys.argv) > 1:
        t = teilnehmer_by_id(sys.argv[1])
        if not t:
            print(f"unbekannter Teilnehmer: {sys.argv[1]}")
            return
        ziele = [t]
    for teilnehmer in ziele:
        try:
            geaendert = akte_aktualisieren(teilnehmer)
            sp = splitter_zaehlen(teilnehmer["id"])
            print(f"[{teilnehmer['id']:20s}] {sp:>5,} Splitter  {'aktualisiert' if geaendert else 'unveraendert'}")
        except Exception as exc:
            print(f"[{teilnehmer['id']:20s}] FEHLER: {exc}")


if __name__ == "__main__":
    main()
