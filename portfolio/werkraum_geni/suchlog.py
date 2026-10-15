#!/usr/bin/env python3
"""Chronologisches Suchlog -- wer wann wonach gesucht hat, was angeboten wurde, was gewaehlt wurde.

Daniel, 2026-08-03, woertlich:
  "ich will ab sofort chronologisch natürlih wissen und loggen lso dokun´mentiert haben wer wann
   was mit welchen zuständen in einer su´che angefragt hat welche zum lesen alle vorgeschlage
   wurden und welche gewählt wurdenu und wenn es das noch nicht gibt auch optional mit einem grund"

Liegt in einer eigenen PostgreSQL (Datenbank `geni`, Besitzer `geni`), NICHT in der
flextrawurst-Datenbank. Zugangsdaten in /root/werkraum/.agent/geni-db.env.
Schema: migration_001_suchlog.sql.

Grundsatz dieser Datei: **das Log darf die Suche nie kaputtmachen.** Jede Funktion faengt alles ab
und gibt im Fehlerfall None zurueck. Wenn die Datenbank weg ist, sucht GENI trotzdem weiter -- sie
merkt es sich dann eben nicht.
"""

import os
import threading

ENV_PFAD = "/root/werkraum/.agent/geni-db.env"

_lock = threading.Lock()
_conn = None
_tot = False          # nach dem ersten harten Fehlschlag nicht endlos neu verbinden


def _uri() -> str:
    uri = os.environ.get("GENI_DB_URI", "")
    if uri:
        return uri
    try:
        with open(ENV_PFAD, encoding="utf-8") as f:
            for zeile in f:
                if zeile.startswith("GENI_DB_URI="):
                    return zeile.strip().split("=", 1)[1]
    except Exception:
        pass
    return ""


def _verbindung():
    global _conn, _tot
    if _tot:
        return None
    if _conn is not None and getattr(_conn, "closed", 1) == 0:
        return _conn
    uri = _uri()
    if not uri:
        _tot = True
        return None
    try:
        import psycopg2
        _conn = psycopg2.connect(uri)
        _conn.autocommit = True
        return _conn
    except Exception:
        _tot = True
        return None


def suche_beginnen(frage: str, sucher: str = "unbekannt", sucher_art: str = "unbekannt",
                   anlass: str | None = None, zustand: dict | None = None,
                   meta: dict | None = None):
    """Legt die Anfrage an und gibt ihre id zurueck (oder None, wenn das Log nicht erreichbar ist).

    `zustand` ist Daniels "mit welchen zuständen" -- was beim Sucher gerade los war: Takt, Energie,
    Ziel, was auch immer der Aufrufer weiss. Bewusst frei als JSONB, damit spaetere Aufrufer mehr
    hineinlegen koennen, ohne das Schema zu aendern (Grundgesetz 2).
    """
    conn = _verbindung()
    if conn is None:
        return None
    import json
    try:
        with _lock, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO suche (sucher, sucher_art, anlass, frage, zustand, meta) "
                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (sucher, sucher_art, anlass, frage,
                 json.dumps(zustand or {}, ensure_ascii=False),
                 json.dumps(meta or {}, ensure_ascii=False)),
            )
            return cur.fetchone()[0]
    except Exception:
        return None


def treffer_loggen(suche_id, treffer: list) -> None:
    """Schreibt ALLE Vorschlaege mit ihrem Rang -- nicht nur die spaeter gelesenen."""
    if suche_id is None or not treffer:
        return
    conn = _verbindung()
    if conn is None:
        return
    try:
        zeilen = [
            (suche_id, rang, t.get("id"), t.get("quelle"), t.get("art"),
             t.get("ort"), t.get("score"), (t.get("wege") or "").strip("+"))
            for rang, t in enumerate(treffer, start=1)
        ]
        with _lock, conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO suche_treffer (suche_id, rang, eintrag_id, quelle, art, ort, score, wege) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                zeilen,
            )
    except Exception:
        return


def wahl_loggen(suche_id, eintrag_id: str, art: str = "gelesen",
                grund: str | None = None, meta: dict | None = None) -> None:
    """Eigenes Ereignis, kein UPDATE am Treffer -- Grundgesetz 5, append-only.

    Wird bewusst nur dort aufgerufen, wo tatsaechlich eine Wahl stattfindet. Wo ein Aufrufer alle
    Treffer am Stueck bekommt und keiner davon ausgewaehlt wird, bleibt diese Tabelle leer -- eine
    erfundene Wahl waere schlimmer als gar keine.
    """
    if suche_id is None or not eintrag_id:
        return
    conn = _verbindung()
    if conn is None:
        return
    import json
    try:
        with _lock, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO suche_wahl (suche_id, eintrag_id, art, grund, meta) "
                "VALUES (%s,%s,%s,%s,%s)",
                (suche_id, eintrag_id, art, grund,
                 json.dumps(meta or {}, ensure_ascii=False)),
            )
    except Exception:
        return


def nie_erschienen(eintrag_ids: list) -> list:
    """Welche dieser Eintraege kamen in KEINER Suche je als Treffer vor.

    Grundlage fuer den eigenen Takt, der den Wesen genau diese Uebersehenen anbietet.
    Daniel: "aber halt nurdie die sonst nicht in ihren suchen vorkommen ... damit es nicht still ist".

    Gibt im Fehlerfall eine leere Liste zurueck -- lieber nichts anbieten als das Falsche.
    """
    if not eintrag_ids:
        return []
    conn = _verbindung()
    if conn is None:
        return []
    try:
        with _lock, conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT eintrag_id FROM suche_treffer WHERE eintrag_id = ANY(%s)",
                (list(eintrag_ids),),
            )
            gesehen = {r[0] for r in cur.fetchall()}
        return [e for e in eintrag_ids if e not in gesehen]
    except Exception:
        return []
