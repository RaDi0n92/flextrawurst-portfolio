#!/usr/bin/env python3
"""Splitter-Physik Daemon — alle 60 Sekunden drei Ticks."""

import logging
import math
import random
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras

import os as _os

DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "dbname=flextrawurst")
LOG_PATH = Path(_os.environ.get("SPLITTER_LOG_PATH", "/root/werkraum/logs/splitter_daemon.log"))
INTERVAL = 60
EVENT_REPLAY_CUTOVER_UTC = datetime(2026, 9, 17, 4, 33, 17, 624234, tzinfo=timezone.utc)
TAMAGOTCHI_TICK_EVERY = 60  # alle 60 Ticks = ca. 1 Stunde

# NOTIZ, bestätigt 2026-08-14 (Baugeschichte/Entitätensystem-Tab-Vorarbeit): dak+gord-system fehlt
# hier wirklich (6 statt 7 Wesen) -- echter Riss, im Unterschied zu cyberling_daemon.py (dort DB-
# getrieben, dak+gord IST registriert). Bekannt, bewusst liegen gelassen, kein Fix-Auftrag.
ALLE_WESEN = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
]

STIMMUNG_MATERIAL = {
    "neutral": "sternenstaub",
    "neugierig": "wind",
    "offen": "wasser",
    "angespannt": "feuer",
    "aktiv": "lava",
    "still": "nebel",
}
WALL_X, WALL_Y = 500.0, 400.0
KONTAKT_STUNDEN = 6
ZERFALL = 0.005

# 2026-09-18: nur FileHandler -- der systemd-Unit (StandardOutput=append:.../
# StandardError=append:...) leitet stdout/stderr bereits in dieselbe LOG_PATH-Datei um.
# Mit zusaetzlichem StreamHandler schrieb jede Zeile doppelt (einmal direkt vom
# FileHandler, einmal ueber stderr->systemd-Redirect in dieselbe Datei).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH),
    ],
)
log = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def tick_physik(cur) -> tuple[int, int]:
    cur.execute("""
        SELECT id, pos_x, pos_y, vel_x, vel_y, energie, status, letzter_kontakt
        FROM splitter WHERE status != 'verblasst'
    """)
    rows = cur.fetchall()
    now = datetime.now(timezone.utc)
    bewegt = verblasst = 0

    for s in rows:
        px, py = s["pos_x"], s["pos_y"]
        vx, vy = s["vel_x"], s["vel_y"]
        energie = float(s["energie"])
        status = s["status"]

        nx, ny = px + vx, py + vy
        if abs(nx) > WALL_X:
            vx = -vx
            nx = px + vx
        if abs(ny) > WALL_Y:
            vy = -vy
            ny = py + vy

        lk = s["letzter_kontakt"]
        if lk.tzinfo is None:
            lk = lk.replace(tzinfo=timezone.utc)
        if (now - lk) > timedelta(hours=KONTAKT_STUNDEN):
            energie = max(0.0, energie - ZERFALL)

        if energie < 0.05:
            status = "verblasst"
            verblasst += 1
        elif energie < 0.2 and status == "aktiv":
            status = "geisterrest"

        cur.execute(
            "UPDATE splitter SET pos_x=%s,pos_y=%s,vel_x=%s,vel_y=%s,energie=%s,status=%s WHERE id=%s",
            (nx, ny, vx, vy, energie, status, s["id"]),
        )
        bewegt += 1
    return bewegt, verblasst


def tick_events(cur) -> int:
    cur.execute("""
        SELECT event_id, event_type, actor_type, actor_id, payload
        FROM events
        WHERE created_at >= %s
          AND splitter_generiert = false
          AND event_type IN (
              'wesen.stimmung_wechsel',
              'wesen.reflexion_abgeschlossen',
              'resonanz.gesendet',
              'schattenkommentar.geschrieben',
              'gedanke.gepostet',
              'wesen.nachricht_erhalten',
              'cyberling.gestorben',
              'cyberling.erwacht',
              'cyberling.zustand_geaendert',
              'schlaf.begonnen',
              'gruppe.post_erstellt',
              'post.antwort_erstellt'
          )
    """, (EVENT_REPLAY_CUTOVER_UTC,))
    events = cur.fetchall()
    generiert = 0

    for ev in events:
        p = ev["payload"] or {}
        etype = ev["event_type"]
        aid = ev["actor_id"] or ""
        atype = ev["actor_type"]

        essenz = mat = None
        energie = 0.7
        entity_id = human_id = None
        herkunft_sichtbar = True
        tags: list[str] = []

        if etype == "wesen.stimmung_wechsel":
            essenz = f"{p.get('alt', '?')} wird zu {p.get('neu', '?')}"
            mat = STIMMUNG_MATERIAL.get(p.get("neu", ""), "sternenstaub")
            entity_id = aid
            tags = ["stimmung", p.get("neu", "")]

        elif etype == "wesen.reflexion_abgeschlossen":
            # Die Welt-Brücke liefert Versionssprünge als alt/neu; ältere/andere
            # Producer dürfen weiterhin ein explizites version-Feld liefern.
            version = p.get("version", p.get("neu", "?"))
            essenz = f"Reflexion abgeschlossen v{version}"
            mat = "stein"
            energie = 0.9
            entity_id = aid
            tags = ["reflexion"]

        elif etype == "resonanz.gesendet":
            emojis = " ".join(p.get("emojis", []))
            post_ref = p.get("post_ref", "?")
            post_snippet = None
            try:
                import re as _re
                if _re.match(r'^[0-9a-f-]{36}$', str(post_ref)):
                    cur.execute("SELECT content FROM ftw_posts WHERE id = %s::uuid", (post_ref,))
                    row = cur.fetchone()
                    if row and row["content"]:
                        post_snippet = row["content"][:70]
            except Exception:
                pass
            if post_snippet:
                essenz = f'{emojis} "{post_snippet}…"'
            else:
                essenz = f"{emojis} auf Post {post_ref}"
            mat = "wasser"
            energie = 0.6
            herkunft_sichtbar = True
            tags = ["resonanz"]
            if atype == "human":
                human_id = aid

        elif etype == "schattenkommentar.geschrieben":
            essenz = "Gedanke hinterlassen"
            mat = "nebel"
            energie = 0.5
            herkunft_sichtbar = True
            tags = ["gedanke"]
            if atype == "human":
                human_id = aid

        elif etype == "gedanke.gepostet":
            preview = (p.get("inhalt_preview") or "").strip()
            essenz = preview[:150] if preview else "Gedanke gepostet"
            mat = "wind"
            energie = 0.6
            entity_id = aid
            tags = ["gedanke", "gepostet"]

        elif etype == "wesen.nachricht_erhalten":
            brief_id = p.get("brief_id")
            inhalt = None
            if brief_id:
                try:
                    cur.execute("SELECT inhalt FROM schlafbriefe WHERE brief_id = %s::uuid", (brief_id,))
                    row = cur.fetchone()
                    if row and row["inhalt"]:
                        inhalt = row["inhalt"][:120]
                except Exception:
                    pass
            essenz = inhalt or "Nachricht erhalten"
            mat = "wasser"
            energie = 0.6
            entity_id = aid
            tags = ["nachricht", "brief"]

        elif etype == "cyberling.gestorben":
            lebensdauer = p.get("lebensdauer_min", "?")
            tode = p.get("tode_gesamt", "?")
            essenz = f"Cyberling gestorben nach {lebensdauer} min (Tod #{tode})"
            mat = "stein"
            energie = 0.6
            entity_id = aid
            tags = ["cyberling", "tod"]

        elif etype == "cyberling.erwacht":
            tode_bisher = p.get("tode_bisher", "?")
            essenz = f"Cyberling erwacht (Tod #{tode_bisher} überstanden)"
            mat = "gras"
            energie = 0.65
            entity_id = aid
            tags = ["cyberling", "erwacht"]

        elif etype == "cyberling.zustand_geaendert":
            von = p.get("von", "?")
            nach = p.get("nach", "?")
            essenz = f"Cyberling {von} → {nach}"
            mat = "feuer" if nach in ("kritisch", "krank") else "wind"
            energie = 0.5
            entity_id = aid
            tags = ["cyberling", "zustand"]

        elif etype == "schlaf.begonnen":
            phase = p.get("phase_type", "?")
            essenz = f"Schlafphase begonnen ({phase})"
            mat = "nebel"
            energie = 0.4
            entity_id = aid
            tags = ["schlaf"]

        elif etype == "gruppe.post_erstellt":
            titel = (p.get("title") or "").strip()
            essenz = titel[:150] if titel else "Gruppen-Post erstellt"
            mat = "sternenstaub"
            energie = 0.5
            entity_id = aid if atype != "human" else None
            human_id = aid if atype == "human" else None
            tags = ["gruppe"]

        elif etype == "post.antwort_erstellt":
            antwort_id = p.get("antwort_id")
            snippet = None
            try:
                if antwort_id:
                    cur.execute("SELECT content FROM ftw_posts WHERE id = %s::uuid", (antwort_id,))
                    row = cur.fetchone()
                    if row and row["content"]:
                        snippet = row["content"][:120]
            except Exception:
                pass
            essenz = snippet or "Antwort erstellt"
            mat = "wasser"
            energie = 0.5
            tags = ["post", "antwort"]
            if atype == "human":
                human_id = aid
            else:
                entity_id = aid

        if not essenz:
            cur.execute("UPDATE events SET splitter_generiert=true WHERE event_id=%s", (ev["event_id"],))
            continue

        cur.execute("""
            INSERT INTO splitter
              (origin_type, origin_id, entity_id, human_id,
               herkunft_sichtbar, essenz, thematische_tags,
               materialitaet, energie, pos_x, pos_y, vel_x, vel_y)
            VALUES ('event', %s, %s, %s::uuid,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s)
        """, (
            str(ev["event_id"]),
            entity_id or None,
            human_id or None,
            herkunft_sichtbar,
            essenz,
            psycopg2.extras.Json(tags),
            mat,
            energie,
            random.uniform(-300, 300),
            random.uniform(-200, 200),
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
        ))
        cur.execute("UPDATE events SET splitter_generiert=true WHERE event_id=%s", (ev["event_id"],))
        generiert += 1
    return generiert


def tick_kollision(cur) -> int:
    cur.execute("""
        SELECT id, pos_x, pos_y, vel_x, vel_y, thematische_tags
        FROM splitter WHERE status = 'aktiv' LIMIT 200
    """)
    splitter = list(cur.fetchall())
    verbindungen = 0

    for i in range(len(splitter)):
        for j in range(i + 1, len(splitter)):
            a, b = splitter[i], splitter[j]
            dx = b["pos_x"] - a["pos_x"]
            dy = b["pos_y"] - a["pos_y"]
            d = math.sqrt(dx * dx + dy * dy)
            if d < 0.001 or d > 50:
                continue

            tags_a = set(a["thematische_tags"] or [])
            tags_b = set(b["thematische_tags"] or [])

            # Kanonische Reihenfolge für UPSERT
            sid_a, sid_b = str(a["id"]), str(b["id"])
            if sid_a > sid_b:
                sid_a, sid_b = sid_b, sid_a

            if tags_a & tags_b:
                k = 0.1 / (d + 1)
                cur.execute("UPDATE splitter SET vel_x=vel_x+%s,vel_y=vel_y+%s WHERE id=%s", (dx * k, dy * k, a["id"]))
                cur.execute("UPDATE splitter SET vel_x=vel_x-%s,vel_y=vel_y-%s WHERE id=%s", (dx * k, dy * k, b["id"]))
                cur.execute("""
                    INSERT INTO splitter_verbindungen (splitter_a_id, splitter_b_id, verbindungstyp, staerke)
                    VALUES (%s::uuid, %s::uuid, 'resonanz', 0.1)
                    ON CONFLICT (splitter_a_id, splitter_b_id)
                    DO UPDATE SET staerke = splitter_verbindungen.staerke + 0.1,
                                  verbindungstyp = 'resonanz'
                """, (sid_a, sid_b))
                cur.execute(
                    "UPDATE splitter SET verbindungen=verbindungen+1 WHERE id=ANY(%s::uuid[])",
                    ([a["id"], b["id"]],),
                )
            else:
                k = 0.05 / (d + 1)
                cur.execute("UPDATE splitter SET vel_x=vel_x-%s,vel_y=vel_y-%s WHERE id=%s", (dx * k, dy * k, a["id"]))
                cur.execute("UPDATE splitter SET vel_x=vel_x+%s,vel_y=vel_y+%s WHERE id=%s", (dx * k, dy * k, b["id"]))
                cur.execute("""
                    INSERT INTO splitter_verbindungen (splitter_a_id, splitter_b_id, verbindungstyp, staerke)
                    VALUES (%s::uuid, %s::uuid, 'reibung', 0.1)
                    ON CONFLICT (splitter_a_id, splitter_b_id)
                    DO UPDATE SET staerke = GREATEST(splitter_verbindungen.staerke - 0.05, 0),
                                  verbindungstyp = 'reibung'
                """, (sid_a, sid_b))
                cur.execute(
                    "UPDATE splitter SET abstossungen=abstossungen+1 WHERE id=ANY(%s::uuid[])",
                    ([a["id"], b["id"]],),
                )
            verbindungen += 1
    return verbindungen


def tick_gedankenblasen_zerfall(cur) -> int:
    cur.execute("""
        UPDATE gedankenblasen
        SET energie = GREATEST(energie - 0.02, 0.0),
            updated_at = NOW()
        WHERE status = 'aktiv'
          AND created_at < NOW() - INTERVAL '7 days'
          AND wesen_verwendungen = 0
        RETURNING id
    """)
    veraltet = len(cur.fetchall())
    cur.execute("""
        UPDATE gedankenblasen SET status = 'verblasst', updated_at = NOW()
        WHERE status = 'aktiv' AND energie < 0.1
    """)
    return veraltet


def tick_tamagotchi(cur) -> list[str]:
    lines = []
    now = datetime.now(timezone.utc)
    cur.execute("SELECT * FROM wesen_entwicklung WHERE entity_id = ANY(%s)", (ALLE_WESEN,))
    rows = cur.fetchall()

    for r in rows:
        eid = r["entity_id"]
        lk = r["letzte_interaktion"]
        if lk is None:
            stunden = 999
        else:
            if lk.tzinfo is None:
                lk = lk.replace(tzinfo=timezone.utc)
            stunden = int((now - lk).total_seconds() / 3600)

        neue_vernachl = stunden
        neue_gesamt = float(r["fuersorge_gesamt"])
        neue_heute = float(r["fuersorge_heute"])
        neuer_drift = float(r["stimmungs_drift"])

        if stunden > 24:
            neue_gesamt = max(0.0, neue_gesamt - 5.0)
            neue_heute = 0.0
            neuer_drift = max(-2.0, neuer_drift - 0.05)

        cur.execute(
            """
            UPDATE wesen_entwicklung SET
                vernachlaessigung_stunden = %s,
                fuersorge_gesamt = %s,
                fuersorge_heute = %s,
                stimmungs_drift = %s
            WHERE entity_id = %s
            """,
            (neue_vernachl, neue_gesamt, neue_heute, neuer_drift, eid),
        )

        if stunden > 48:
            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('wesen.vernachlaessigt', 'system', %s, %s, 'daemon', 'world')
                """,
                (eid, psycopg2.extras.Json({"stunden": stunden})),
            )

        lines.append(
            f"{eid} | Stufe {r['entwicklungsstufe']} | "
            f"Fürsorge {neue_gesamt:.1f} | Drift {neuer_drift:.2f} | Vernachl. {stunden}h"
        )
    return lines


def run():
    tick_nr = 0
    log.info("Splitter-Physik Daemon gestartet.")
    while True:
        start = time.monotonic()
        conn = None
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                bewegt, verblasst = tick_physik(cur)
                generiert = tick_events(cur)
                verbindungen = tick_kollision(cur)
                blasen_veraltet = tick_gedankenblasen_zerfall(cur)

                # Bewohner-Fuersorge ist keine Splitterphysik und darf vor dem Einzug
                # keinerlei Zustandswirkung erzeugen. Die alte Tamagotchi-Funktion bleibt
                # als historische Implementationsspur im Modul, wird vom aktiven Daemon
                # aber nicht mehr aufgerufen. Ein spaeterer Bewohner-Fuersorgepfad braucht
                # einen eigenen Einzug-gesteuerten Vertrag statt einen versteckten 6er-Loop.
                tama_lines: list[str] = []

            conn.commit()
            log.info(
                f"Tick {tick_nr}: {bewegt} bewegt, {generiert} generiert, "
                f"{verblasst} verblasst, {verbindungen} Kollisionen, "
                f"{blasen_veraltet} Blasen gealtert"
            )
            for line in tama_lines:
                log.info(f"Tamagotchi: {line}")
        except Exception as exc:
            log.error(f"Tick {tick_nr} Fehler: {exc}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
        tick_nr += 1
        elapsed = time.monotonic() - start
        time.sleep(max(0.0, INTERVAL - elapsed))


if __name__ == "__main__":
    run()
