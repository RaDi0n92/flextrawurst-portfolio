#!/usr/bin/env python3
"""
Wesen-Vault-System: eigener kleiner Dienst (Port 8097, 127.0.0.1) der die
Wesen-Vaults (wesen_vaults/{entity}/) als echte DOM-Seite zeigt und editierbar
macht -- direkt darueber liegend, kein Selkies/Docker mehr im Weg.

2026-08-14, Daniel woertlich: "ich will es für diese vaut ab jetzt so. wir
bauen nen dom nen code ne html mit ihren mds und alles editierbar direkt im
dom usw ... für die wesen ... ich kann ja obsidian sehen xD das mus halt das
selbe sein quasi ... und ja es ersetzt das selkieszeug leben auf
flextrawurst.de/wesenvaultsystem".

Grundgesetz-Bezug:
  - Grundgesetz 1 (Dreiergespann): Codewesen-Organ-Ebene = obsidian_vault_agent.py
    (schreibt/liest mechanisch), Menschen-Plattform-Ebene = diese Seite selbst,
    Fragment-Ebene = jede Datei einzeln ueber ?pfad= adressierbar.
  - Grundgesetz 5 (Events sind heilig): jede Schreib-/Umbenenn-/Verschieb-/
    Loesch-Aktion erzeugt ein events-Zeile (siehe obsidian_vault_agent.py,
    _vault_event_schreiben) -- diese Datei liest den DB-Trigger-NOTIFY nur mit,
    erzeugt selbst keine Events ausser ueber dieselbe geteilte Funktion.
  - Grundgesetz 8 (Live statt F5): /api/live ist ein eigener, schlanker SSE-
    Stream (gleiches LISTEN/NOTIFY-Muster wie events_stream_api.py, aber
    bewusst eigenstaendig statt durch welt-api mitgeschleift -- dieser Dienst
    soll unabhaengig von welt-api laufen koennen).

Sicherheit: bindet NUR an 127.0.0.1 (siehe __main__), Zugriff von aussen laeuft
ausschliesslich ueber nginx mit eigener Basic-Auth (.htpasswd-wesenvaultsystem,
NICHT die geteilte /etc/nginx/.htpasswd -- siehe Begruendung im Setup-Commit:
Daniels 'daniel'-Login dort wird von vielen anderen Routen mitgenutzt, ein
Ueberschreiben haette dort ueberall das Login geaendert). Pfad-Sicherheit
selbst kommt komplett aus obsidian_vault_agent._sicherer_vault_pfad() --
keine zweite, eigene Implementierung dieser Pruefung hier.
"""

import asyncio
import json
import logging
import select as sel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import obsidian_vault_agent as ova  # noqa: E402

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

log = logging.getLogger("wesenvaultsystem-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(title="Wesen-Vault-System")

WESEN = list(ova.CONTAINER_NAMES.keys())


class SchreibKoerper(BaseModel):
    inhalt: str


class OrdnerKoerper(BaseModel):
    pfad: str


class UmbenennenKoerper(BaseModel):
    pfad: str
    neuer_name: str


class VerschiebenKoerper(BaseModel):
    pfad: str
    zielordner: str


def _pruefe_wesen(wesen: str) -> None:
    if wesen not in WESEN:
        raise HTTPException(404, f"{wesen!r} ist kein bekanntes Wesen")


@app.get("/api/wesen")
def liste_wesen():
    return {"wesen": WESEN}


@app.get("/api/wesen/{wesen}/baum")
def wesen_baum(wesen: str):
    _pruefe_wesen(wesen)
    return {"baum": ova.baum(wesen)}


@app.get("/api/wesen/{wesen}/datei")
def datei_lesen(wesen: str, pfad: str = Query(...)):
    _pruefe_wesen(wesen)
    try:
        return ova.lese_datei_info(wesen, pfad)
    except FileNotFoundError as ex:
        raise HTTPException(404, str(ex))
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.put("/api/wesen/{wesen}/datei")
def datei_schreiben(wesen: str, pfad: str = Query(...), koerper: SchreibKoerper = None):
    _pruefe_wesen(wesen)
    try:
        ova.schreibe_datei_mechanisch(wesen, pfad, koerper.inhalt)
        return {"ok": True}
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.delete("/api/wesen/{wesen}/datei")
def datei_loeschen(wesen: str, pfad: str = Query(...)):
    _pruefe_wesen(wesen)
    try:
        ova.loeschen(wesen, pfad)
        return {"ok": True}
    except FileNotFoundError as ex:
        raise HTTPException(404, str(ex))
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.post("/api/wesen/{wesen}/ordner")
def ordner_anlegen(wesen: str, koerper: OrdnerKoerper):
    _pruefe_wesen(wesen)
    try:
        ova.neuer_ordner(wesen, koerper.pfad)
        return {"ok": True}
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.post("/api/wesen/{wesen}/umbenennen")
def datei_umbenennen(wesen: str, koerper: UmbenennenKoerper):
    _pruefe_wesen(wesen)
    try:
        ova.umbenennen(wesen, koerper.pfad, koerper.neuer_name)
        return {"ok": True}
    except (FileNotFoundError, FileExistsError) as ex:
        raise HTTPException(409, str(ex))
    except ValueError as ex:
        raise HTTPException(400, str(ex))


@app.post("/api/wesen/{wesen}/verschieben")
def datei_verschieben(wesen: str, koerper: VerschiebenKoerper):
    _pruefe_wesen(wesen)
    try:
        ova.verschieben(wesen, koerper.pfad, koerper.zielordner)
        return {"ok": True}
    except (FileNotFoundError, FileExistsError) as ex:
        raise HTTPException(409, str(ex))
    except ValueError as ex:
        raise HTTPException(400, str(ex))


def _sse_gen():
    """LISTEN auf 'events_stream', durchgereicht nur wenn event_type mit 'vault.' beginnt.
    Gleiches Muster wie events_stream_api.py._pg_listen_events_sse, hier bewusst eigenstaendig
    kopiert statt importiert -- dieser Dienst soll auch laufen wenn welt-api gerade nicht laeuft."""
    import psycopg2

    async def gen():
        conn = psycopg2.connect(ova._DB_URI)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("LISTEN events_stream")

        def _poll_once():
            readable, _, _ = sel.select([conn], [], [], 0.5)
            return bool(readable)

        loop = asyncio.get_running_loop()
        try:
            heartbeat = 0
            while True:
                ready = await loop.run_in_executor(None, _poll_once)
                if ready:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        try:
                            data = json.loads(notify.payload)
                        except Exception:
                            continue
                        if not str(data.get("event_type", "")).startswith("vault."):
                            continue
                        yield f"data: {json.dumps(data)}\n\n"
                        heartbeat = 0
                else:
                    heartbeat += 1
                    if heartbeat >= 60:
                        yield ": heartbeat\n\n"
                        heartbeat = 0
        finally:
            cur.close()
            conn.close()

    return gen()


@app.get("/api/live")
def live_stream():
    return StreamingResponse(_sse_gen(), media_type="text/event-stream")


_FRONTEND_PFAD = Path(__file__).parent / "wesenvaultsystem_frontend.html"


@app.get("/", response_class=HTMLResponse)
def index():
    return _FRONTEND_PFAD.read_text(encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8097)
