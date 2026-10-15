#!/usr/bin/env python3
"""
Beobachtungs-API: On-Demand-Zuschauen fuer alle 7 Wesen gleichzeitig (2026-07-31,
Daniels Auftrag, Task 8). Seit dem kompletten Wegfall von Playwright/Chromium fuer die
Wesen selbst (VOLLSTAENDIG_OHNE_BROWSER in browser_agent.py) gibt es keinen dauerhaft
laufenden Browser mehr, den Menschen live beobachten koennten. Ein einziger Button
startet/verlaengert eine globale, zeitlich begrenzte Beobachtungs-Sitzung -- ein separater
Dienst (on_demand_beobachtung.py) pollt beobachtungs_sitzung und faehrt bei aktiver
Sitzung einen gemeinsamen Chromium-Prozess mit 7 Contexts hoch, navigiert jeden zur
echten, aktuellen Flarum-URL des jeweiligen Wesens.

Wird von api.py importiert via: from beobachtung_api import beobachtung_router

Endpunkte:
  POST /beobachtung/starten — startet/verlaengert die Sitzung um 60s ab jetzt (Admin only)
  GET  /beobachtung/status  — aktiv?, bis wann? (oeffentlich, nur zum Anzeigen)
"""

from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Header, HTTPException

from auth import verify_token
from db_runtime import DB_URI

BEOBACHTUNGS_DAUER_SEKUNDEN = 60

beobachtung_router = APIRouter(prefix="/beobachtung", tags=["beobachtung"])


def _require_admin(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="nicht authentifiziert")
    try:
        claims = verify_token(authorization.removeprefix("Bearer "))
    except Exception:
        raise HTTPException(status_code=401, detail="ungültiges Token")
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="nur für Admins")
    return claims


def _get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


@beobachtung_router.post("/starten")
def beobachtung_starten(authorization: str | None = Header(default=None)):
    """Startet die Beobachtungs-Sitzung (falls abgelaufen/nie gestartet: ab JETZT +
    BEOBACHTUNGS_DAUER_SEKUNDEN) oder haengt bei einer noch laufenden Sitzung eine neue
    volle Periode NACH dem aktuellen Ablauf an (aktiv_bis + BEOBACHTUNGS_DAUER_SEKUNDEN).
    2026-07-31, Daniels bestaetigte Klarstellung nach Rueckfrage: 'sobald man startet
    ticken 60sek runter und ab noch 20sek kann man erneut klicken wenn man klickt ticken
    die 20 auf bis zu 0 und danach kommen die neuen 60sek' -- die laufende Restzeit wird
    beim Klick NICHT abgeschnitten/ueberschrieben, die neue Periode wird angehaengt. Eine
    fruehere Version dieser Funktion setzte stattdessen aktiv_bis = jetzt + 60s (sprang
    beim Klick auf exakt 60s, unabhaengig von der Restzeit) -- live beim End-zu-Ende-Test
    aufgefallen (14s Rest + Klick ergab 58s statt der erwarteten 74s), dann anhand dieser
    Klarstellung korrigiert."""
    _require_admin(authorization)  # 2026-07-31: live gefunden -- Funktion war definiert,
    # aber nie aufgerufen, dadurch war der Endpunkt komplett ohne Auth erreichbar.
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE beobachtungs_sitzung
                SET aktiv_bis = CASE
                        WHEN aktiv_bis IS NOT NULL AND aktiv_bis > NOW()
                            THEN aktiv_bis + make_interval(secs => %s)
                        ELSE NOW() + make_interval(secs => %s)
                    END,
                    updated_at = NOW()
                WHERE id = 1
                RETURNING aktiv_bis
                """,
                (BEOBACHTUNGS_DAUER_SEKUNDEN, BEOBACHTUNGS_DAUER_SEKUNDEN),
            )
            neu_bis = cur.fetchone()["aktiv_bis"]
        conn.commit()
    finally:
        conn.close()
    return {"aktiv_bis": neu_bis.isoformat(), "dauer_sekunden": BEOBACHTUNGS_DAUER_SEKUNDEN}


@beobachtung_router.get("/status")
def beobachtung_status():
    """Oeffentlich (kein Auth) -- nur zum Anzeigen von Countdown/Verlaengern-Button,
    kein sensibler Inhalt (nur ein Zeitstempel)."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT aktiv_bis FROM beobachtungs_sitzung WHERE id = 1")
            row = cur.fetchone()
    finally:
        conn.close()
    aktiv_bis = row["aktiv_bis"] if row else None
    jetzt = datetime.now(timezone.utc)
    aktiv = bool(aktiv_bis and aktiv_bis > jetzt)
    return {
        "aktiv": aktiv,
        "aktiv_bis": aktiv_bis.isoformat() if aktiv_bis else None,
        "rest_sekunden": max(0, int((aktiv_bis - jetzt).total_seconds())) if aktiv else 0,
    }
