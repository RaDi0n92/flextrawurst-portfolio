#
# reibungsknoten existieren -- er heilt/belebt sich in dem Moment, in dem ein Bewertungsprofil
# zum ersten Mal einen Strom zeigt, der ueberwiegend widerspricht statt zustimmt, und das
# stehen bleiben darf, ohne dass irgendwer es als Problem behandelt.
"""
Reibungsgewebe-API: Bewertungsprofil + Lese-Endpunkte fuer das Reibungsgewebe.
Wird von api.py importiert via: from reibungsgewebe_api import reibungsgewebe_router

Owner-Prinzip (siehe _claude/konzepte/2026-08-17_reibungsgewebe_stroeme.md): diese API
ist NUR lesend. Schreiben passiert ausschliesslich ueber reibung_bruecke.py, die den
Briefkasten liest -- kein Strom bekommt hier einen Schreibzugriff auf die DB.

Endpunkte:
  GET /reibungsgewebe/knoten                    — Liste aller Knoten (neueste zuerst)
  GET /reibungsgewebe/knoten/{kurzcode}          — ein Knoten mit allen Events
  GET /reibungsgewebe/profil/{strom}             — Bewertungsprofil eines Stroms
  GET /reibungsgewebe/profile                    — alle Bewertungsprofile auf einmal
"""

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, HTTPException
from db_runtime import DB_URI

reibungsgewebe_router = APIRouter(prefix="/reibungsgewebe", tags=["reibungsgewebe"])


def _conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


@reibungsgewebe_router.get("/knoten")
def liste_knoten(limit: int = 100, strom: str | None = None):
    conn = _conn()
    try:
        cur = conn.cursor()
        if strom:
            cur.execute(
                """
                SELECT meta->>'kurzcode' AS kurzcode, urspruenglicher_text, urspruenglicher_strom,
                       zustand, erstellt
                FROM reibungsknoten WHERE urspruenglicher_strom = %s
                ORDER BY erstellt DESC LIMIT %s
                """,
                (strom, limit),
            )
        else:
            cur.execute(
                """
                SELECT meta->>'kurzcode' AS kurzcode, urspruenglicher_text, urspruenglicher_strom,
                       zustand, erstellt
                FROM reibungsknoten ORDER BY erstellt DESC LIMIT %s
                """,
                (limit,),
            )
        return {"knoten": cur.fetchall()}
    finally:
        conn.close()


@reibungsgewebe_router.get("/knoten/{kurzcode}")
def knoten_details(kurzcode: str):
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, urspruenglicher_text, urspruenglicher_strom, zustand, erstellt
            FROM reibungsknoten WHERE meta->>'kurzcode' = %s
            """,
            (kurzcode,),
        )
        knoten = cur.fetchone()
        if not knoten:
            raise HTTPException(status_code=404, detail="Knoten nicht gefunden")
        cur.execute(
            """
            SELECT strom, art, marker, text, erstellt FROM reibungsevents
            WHERE knoten_id = %s ORDER BY erstellt ASC
            """,
            (knoten["id"],),
        )
        return {"knoten": knoten, "events": cur.fetchall()}
    finally:
        conn.close()


def _bewertungsprofil(cur, strom: str) -> dict:
    """Direkt aus reibungsevents berechnet, keine eigene Tabelle -- damit das Profil
    nie aus dem Takt mit den echten Reaktionen laeuft (siehe Konzept-Datei)."""
    cur.execute(
        "SELECT art, COUNT(*) AS n FROM reibungsevents WHERE strom = %s GROUP BY art",
        (strom,),
    )
    art_verteilung = {row["art"]: row["n"] for row in cur.fetchall()}

    cur.execute(
        """
        SELECT marker, COUNT(*) AS n FROM reibungsevents
        WHERE strom = %s AND marker IS NOT NULL GROUP BY marker
        """,
        (strom,),
    )
    marker_haeufigkeit = {row["marker"]: row["n"] for row in cur.fetchall()}

    cur.execute(
        "SELECT COUNT(*) AS n FROM reibungsevents WHERE strom = %s",
        (strom,),
    )
    gesamt = cur.fetchone()["n"]

    return {
        "strom": strom,
        "gesamt_events": gesamt,
        "art_verteilung": art_verteilung,
        "marker_haeufigkeit": marker_haeufigkeit,
    }


@reibungsgewebe_router.get("/profil/{strom}")
def bewertungsprofil(strom: str):
    conn = _conn()
    try:
        cur = conn.cursor()
        profil = _bewertungsprofil(cur, strom)
        if profil["gesamt_events"] == 0:
            raise HTTPException(status_code=404, detail=f"Kein Strom '{strom}' mit Events gefunden")
        return profil
    finally:
        conn.close()


@reibungsgewebe_router.get("/profile")
def alle_bewertungsprofile():
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT strom FROM reibungsevents ORDER BY strom")
        stroeme = [row["strom"] for row in cur.fetchall()]
        return {"profile": [_bewertungsprofil(cur, s) for s in stroeme]}
    finally:
        conn.close()
