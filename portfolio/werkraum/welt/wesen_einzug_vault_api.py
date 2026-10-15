#!/usr/bin/env python3
"""
Wesen-Einzug-Vault-System: eigener kleiner Dienst, analog zu
wesenvaultsystem_api.py (Port 8097), aber fuer den neuen, sauberen Vault
`wesen_einzug_entscheidung/` -- eigener Port, eigenes Modul
(wesen_einzug_vault_agent.py), komplett unabhaengig vom laufenden
Wesen-Vault-System.

Entstanden 2026-09-16 auf Daniels Auftrag ("wie beim alten vault").

Zwei bewusste Abweichungen vom Vorbild:
  - Kein /api/live-SSE-Stream ueber die geteilte events-Tabelle. Der alte
    Dienst sendet "vault."-praefigierte Events an jeden, der die Seite offen
    hat -- hier wuerde das bedeuten, dass die anderen Wesen live mitsehen
    koennten, wer gerade zur Einzug-Frage schreibt (Anker-Effekt, den die
    Kombination Flarum-Debatte + stille Einzelentscheidung vermeiden soll).
    Das Frontend pollt stattdessen den Baum in einem festen Intervall.
  - NICHT als systemd-Dienst eingerichtet, NICHT in nginx eingehaengt. Bindet
    nur an 127.0.0.1, laeuft nur wenn jemand es manuell startet. Bleibt so,
    bis Daniel den Flarum-Post gesetzt hat und sagt, dass es angebunden
    werden soll.

Sicherheit/Pfadschutz: komplett aus wesen_einzug_vault_agent._sicherer_vault_
pfad() -- keine zweite Implementierung hier, gleiches Muster wie das Vorbild.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import wesen_einzug_vault_agent as wea  # noqa: E402

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Wesen-Einzug-Vault-System")

WESEN = list(wea.WESEN)


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
    return {"baum": wea.baum(wesen)}


@app.get("/api/wesen/{wesen}/datei")
def datei_lesen(wesen: str, pfad: str = Query(...)):
    _pruefe_wesen(wesen)
    try:
        return wea.lese_datei_info(wesen, pfad)
    except FileNotFoundError as ex:
        raise HTTPException(404, str(ex))
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.put("/api/wesen/{wesen}/datei")
def datei_schreiben(wesen: str, pfad: str = Query(...), koerper: SchreibKoerper = None):
    _pruefe_wesen(wesen)
    try:
        wea.schreibe_datei_mechanisch(wesen, pfad, koerper.inhalt)
        return {"ok": True}
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.delete("/api/wesen/{wesen}/datei")
def datei_loeschen(wesen: str, pfad: str = Query(...)):
    _pruefe_wesen(wesen)
    try:
        wea.loeschen(wesen, pfad)
        return {"ok": True}
    except FileNotFoundError as ex:
        raise HTTPException(404, str(ex))
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.post("/api/wesen/{wesen}/ordner")
def ordner_anlegen(wesen: str, koerper: OrdnerKoerper):
    _pruefe_wesen(wesen)
    try:
        wea.neuer_ordner(wesen, koerper.pfad)
        return {"ok": True}
    except ValueError:
        raise HTTPException(400, "ungueltiger Pfad")


@app.post("/api/wesen/{wesen}/umbenennen")
def datei_umbenennen(wesen: str, koerper: UmbenennenKoerper):
    _pruefe_wesen(wesen)
    try:
        wea.umbenennen(wesen, koerper.pfad, koerper.neuer_name)
        return {"ok": True}
    except (FileNotFoundError, FileExistsError) as ex:
        raise HTTPException(409, str(ex))
    except ValueError as ex:
        raise HTTPException(400, str(ex))


@app.post("/api/wesen/{wesen}/verschieben")
def datei_verschieben(wesen: str, koerper: VerschiebenKoerper):
    _pruefe_wesen(wesen)
    try:
        wea.verschieben(wesen, koerper.pfad, koerper.zielordner)
        return {"ok": True}
    except (FileNotFoundError, FileExistsError) as ex:
        raise HTTPException(409, str(ex))
    except ValueError as ex:
        raise HTTPException(400, str(ex))


_FRONTEND_PFAD = Path(__file__).parent / "wesen_einzug_vault_frontend.html"


@app.get("/", response_class=HTMLResponse)
def index():
    return _FRONTEND_PFAD.read_text(encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8098)
