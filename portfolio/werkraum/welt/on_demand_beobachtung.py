#!/usr/bin/env python3
"""
On-Demand-Beobachtung (2026-07-31, Daniels Auftrag, Task 8): seit dem kompletten Wegfall
von Playwright/Chromium fuer die Wesen selbst (VOLLSTAENDIG_OHNE_BROWSER in
browser_agent.py) gibt es keinen dauerhaft laufenden Browser mehr, den Menschen live
beobachten koennten.

Dieser Dienst pollt beobachtungs_sitzung (migration_beobachtungs_sitzung.sql). Solange
aktiv_bis in der Zukunft liegt, faehrt er EINEN gemeinsamen Chromium-Prozess mit 7 eigenen
Contexts (einer pro Wesen, dieselbe Isolation wie bei getrennten Browsern -- eigenes DOM,
eigene Cookies) hoch, navigiert jeden Context zur echten, aktuellen Flarum-URL des
jeweiligen Wesens (aus entity_thinking_log, demselben Ort an dem browser_agent.py seinen
Denklog schreibt) und startet rrweb-Aufnahme pro Context -- dieselbe Funktion
(starte_rrweb_aufnahme), derselbe entity_dom_events-Kanal, den das bestehende
SCREENS-Grid/-Modal schon konsumiert. Kein neuer Frontend-Mechanismus fuers Anzeigen
noetig, nur eine neue Quelle fuer denselben Strom.

Nach Ablauf (kein aktiver Beobachtungs-Wunsch mehr) faehrt alles wieder sauber runter --
kein dauerhaft laufender Browser, echte RAM-Ersparnis bleibt erhalten.
"""

import logging
import os
import re
import signal
import sys
import time
import uuid
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from playwright.sync_api import sync_playwright

sys.path.insert(0, "/root/werkraum/welt")
from browser_agent import starte_rrweb_aufnahme  # gleiche rrweb-Funktion wie die Wesen selbst nutzten

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst")

# 2026-07-31: dieselben 7 wie VOLLSTAENDIG_OHNE_BROWSER in browser_agent.py. Bewusst hier
# noch einmal benannt statt importiert -- ein Import wuerde nur den Namen ziehen, die
# eigentliche Quelle der Wahrheit bleibt browser_agent.py, hier nur zur Vermeidung
# unnoetiger Kopplung an internen Zustand dieses Moduls dupliziert.
WESEN = ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"]

POLL_SEKUNDEN = 3
URL_SYNC_SEKUNDEN = 5  # wie oft waehrend aktiver Sitzung neu geprueft wird, ob ein Wesen woanders ist

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("on-demand-beobachtung")

# browser_agent.py installiert beim Import einen eigenen SIGTERM-Handler fuer
# seinen Endlosloop. Dieser Dienst importiert nur starte_rrweb_aufnahme und darf
# den fremden Handler deshalb nicht erben: sonst setzt SIGTERM lediglich
# browser_agent._laufend=False, waehrend dieser Loop endlos weiterlaeuft.
_laufend = True


def _signal_handler(sig, frame):
    global _laufend
    log.info("Signal %s -- beende Beobachtungsdienst sauber", sig)
    _laufend = False


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def hole_sitzung_aktiv_bis(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT aktiv_bis FROM beobachtungs_sitzung WHERE id = 1")
        row = cur.fetchone()
    return row["aktiv_bis"] if row else None


def hole_echte_url(conn, entity_id: str) -> str:
    """Baut aus dem zuletzt geloggten seite['url']-String (z.B. 'flarum:d/1649 (ohne
    Browser)' oder 'flarum: (ohne Browser)') die echte, aufrufbare Flarum-URL. Dieselbe
    Quelle, die auch der Wesen-eigene Denklog fuellt -- kein separater Zustand, keine
    Fiktion: was hier gezeigt wird, ist wortwoertlich da, wo das Wesen laut seinem
    eigenen, echten letzten Tick gerade ist."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT meta->>'url' AS url FROM entity_thinking_log "
            "WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 1",
            (entity_id,),
        )
        row = cur.fetchone()
    roh = (row["url"] if row else "") or ""
    match = re.match(r"^flarum:(d/\d+)?", roh)
    pfad = match.group(1) if (match and match.group(1)) else ""
    return f"https://flextrawurst.de/flarum-live/{pfad}"


def haupt_loop():
    conn = get_conn()
    browser_offen = False
    pw = None
    browser = None
    contexts: dict[str, tuple] = {}  # entity_id -> (context, page, aktuelle_url)
    letzte_url_sync = 0.0

    log.info("On-Demand-Beobachtung gestartet, poll alle %ds", POLL_SEKUNDEN)

    while _laufend:
        try:
            if conn.closed:
                conn = get_conn()
            aktiv_bis = hole_sitzung_aktiv_bis(conn)
            jetzt = datetime.now(timezone.utc)
            soll_laufen = bool(aktiv_bis and aktiv_bis > jetzt)

            if soll_laufen and not browser_offen:
                log.info("Beobachtungs-Sitzung aktiv bis %s -- starte gemeinsamen Browser (7 Contexts)", aktiv_bis)
                pw = sync_playwright().start()
                browser = pw.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                        "--window-size=1024,768", "--disable-extensions",
                        "--disable-background-networking", "--disable-sync",
                        "--disable-translate", "--disable-features=TranslateUI",
                        "--no-first-run", "--disable-default-apps",
                        "--disk-cache-size=1", "--media-cache-size=1", "--disable-notifications",
                    ],
                )
                for entity_id in WESEN:
                    try:
                        context = browser.new_context(viewport={"width": 1024, "height": 768}, locale="de-DE")
                        page = context.new_page()
                        stream_id = str(uuid.uuid4())
                        starte_rrweb_aufnahme(page, lambda: conn, entity_id, stream_id)
                        url = hole_echte_url(conn, entity_id)
                        page.goto(url, timeout=10000, wait_until="domcontentloaded")
                        contexts[entity_id] = (context, page, url)
                        log.info("%s: Beobachtungs-Context gestartet -> %s", entity_id, url)
                    except Exception as e:
                        log.warning("%s: Beobachtungs-Context konnte nicht gestartet werden: %s", entity_id, e)
                browser_offen = True
                letzte_url_sync = time.time()

            elif soll_laufen and browser_offen and (time.time() - letzte_url_sync >= URL_SYNC_SEKUNDEN):
                for entity_id, (context, page, alte_url) in list(contexts.items()):
                    neue_url = hole_echte_url(conn, entity_id)
                    if neue_url != alte_url:
                        try:
                            page.goto(neue_url, timeout=10000, wait_until="domcontentloaded")
                            contexts[entity_id] = (context, page, neue_url)
                            log.info("%s: Beobachtung folgt neuer echter URL -> %s", entity_id, neue_url)
                        except Exception as e:
                            log.warning("%s: Nachfuehren der URL fehlgeschlagen: %s", entity_id, e)
                letzte_url_sync = time.time()

            elif not soll_laufen and browser_offen:
                log.info("Beobachtungs-Sitzung abgelaufen -- fahre gemeinsamen Browser wieder runter")
                try:
                    browser.close()
                except Exception:
                    pass
                try:
                    pw.stop()
                except Exception:
                    pass
                contexts = {}
                browser = None
                pw = None
                browser_offen = False

        except Exception as e:
            log.error("Fehler im Beobachtungs-Loop: %s", e)

        time.sleep(POLL_SEKUNDEN)

    # Eigener sauberer Shutdown-Pfad. Besonders wichtig, falls SIGTERM waehrend
    # einer aktiven Beobachtungs-Sitzung kommt: Chromium/Playwright nicht als
    # verwaiste Prozesse liegen lassen.
    log.info("On-Demand-Beobachtung beendet -- raeume Ressourcen auf")
    if browser_offen:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass
    try:
        conn.close()
    except Exception:
        pass


if __name__ == "__main__":
    haupt_loop()
