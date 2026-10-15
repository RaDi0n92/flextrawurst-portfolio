from __future__ import annotations

import asyncio
import os
import re
import signal
import subprocess
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import edge_tts
from fastapi import FastAPI

try:
    from tts_utils import generate_long_tts_audio
    _LONG_TTS_OK = True
except Exception:
    _LONG_TTS_OK = False
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.responses import JSONResponse as _JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))

try:
    import obsidian_vault as _vault
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

from agent.dak_gord_system.graphen.gespraechsgraf import (
    baue_graf,
    setze_stream_callback,
    setze_modell_override,
    setze_bild,
    setze_organ_manager,
    DAK_GORD_NAME,
)
from agent.dak_gord_system.herz.postgres_herz import postgres_kontext
from agent.dak_gord_system.kerne.beziehungsorgan import Beziehungsorgan
from agent.dak_gord_system.kerne.organ_manager import OrganManager
from agent.dak_gord_system.verfassung_loader import lade_verfassung_aus_pfad
from agent.dak_gord_system.graphen.gespraechsgraf import VERFASSUNG_NEU_PFAD

# 2026-08-12, Daniel: "klar will ich das memoryysystem und die container und
# auch die kontextfensteranzeige usw so wie bei codexium2 auch ungefaehr nur
# uebersetzt auch sichtbar haben zum editieren erstellen und so ... genau so
# wie die geschichten und so" -- die vier Bausteine landen seit dem letzten
# Bauschritt im Systemprompt (gespraechsgraf._systemtext()), aber unsichtbar.
# Hier: dieselbe sichtbare Oberflaeche wie codewesen_chat.py (Track 2/4/5/6/7),
# an dak+gords eigenes Design angepasst, gegen dieselben Backend-Module.
import httpx as _httpx
import hauhau_client
import codewesen_gedankenfeld
import codewesen_speicher

_graf = None
_beziehungsorgan = Beziehungsorgan()
_organ_manager = OrganManager()
_verlauf: list[str] = []
# Thread-ID der gerade laufenden Generierung (fuer echten Abbruch via
# hauhau_client.abbreche_stream(), siehe /chat/abort unten). Nur eine Generierung gleichzeitig
# moeglich (_anfrage_lock), daher reicht ein einzelner globaler Wert statt einer Map.
_AKTIVER_THREAD_ID: int | None = None
_anfrage_lock = asyncio.Lock()
FADEN_ID = "hauptfaden"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graf, _verlauf
    _organ_manager.laden()
    setze_organ_manager(_organ_manager)
    ctx = postgres_kontext()
    checkpointer = ctx.__enter__()
    try:
        checkpointer.setup()
        _graf = baue_graf(checkpointer)
        # Letzten Gesprächsverlauf aus PostgreSQL-Checkpoint wiederherstellen
        try:
            checkpoint = checkpointer.get({"configurable": {"thread_id": FADEN_ID}})
            if checkpoint and checkpoint.get("channel_values", {}).get("nachrichten"):
                _verlauf = list(checkpoint["channel_values"]["nachrichten"])
                print(f"[System] Verlauf wiederhergestellt: {len(_verlauf)} Nachrichten")
        except Exception as e:
            print(f"[System] Kein Verlauf gefunden: {e}")
        yield
    finally:
        ctx.__exit__(None, None, None)


app = FastAPI(title="dak+gord-system", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatAnfrage(BaseModel):
    nachricht: str
    modus: str | None = None
    bild_b64: str | None = None
    bild_name: str | None = None


class TtsAnfrage(BaseModel):
    text: str
    maennlich: bool = False
    # Tempo-Regler, uebernommen von codexium2/solarius2 (gleiches Muster wie in
    # codewesen_chat.py) -- server-seitig streng geprueft, da es direkt in den TTS-Aufruf geht.
    rate: str | None = None


_STIMME_WEIBLICH = "de-DE-KatjaNeural"
_STIMME_MAENNLICH = "de-DE-ConradNeural"
_TTS_RATE_MUSTER = re.compile(r"^[+-]\d{1,3}%$")


_GEDAECHTNIS = Path("/root/werkraum/agent/dak_gord_system/gedaechtnis_daten")


@app.post("/api/tts")
async def tts_endpoint(anfrage: TtsAnfrage):
    voice = _STIMME_MAENNLICH if anfrage.maennlich else _STIMME_WEIBLICH
    rate = anfrage.rate if (anfrage.rate and _TTS_RATE_MUSTER.match(anfrage.rate)) else "+0%"
    try:
        if _LONG_TTS_OK:
            audio = await generate_long_tts_audio(anfrage.text, voice, rate=rate)
        else:
            communicate = edge_tts.Communicate(anfrage.text[:600], voice, rate=rate)
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
        return Response(content=audio, media_type="audio/mpeg")
    except Exception:
        return Response(content=b"", media_type="audio/mpeg")


@app.get("/api/organe")
async def organe_endpoint():
    def lese(datei: str) -> list:
        p = _GEDAECHTNIS / datei
        if not p.exists():
            return []
        try:
            import json as _json
            return _json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []

    from fastapi.responses import JSONResponse as _JR
    return _JR({
        "erinnerungen": lese("erinnerungen.json")[-5:],
        "zukunft": lese("zukunft.json")[-3:],
        "zwischenraum": lese("zwischenraum.json")[-4:],
        "abwaegungen": lese("abwaegungen.json")[-3:],
    })


# ── Ehrliche Kontextfenster-Anzeige (2026-08-12) ────────────────────────────────
# Dieselbe Regel wie codewesen_chat.py: ruft dieselben Funktionen auf, die
# auch wirklich den Prompt bauen (Verfassung, Organ-Zustand, die vier
# Gedaechtnis-Bausteine), statt sie nachzubauen -- Track parallel zu
# gespraechsgraf._systemtext(), nur mit jedem Teil einzeln benannt statt zu
# einem String verklebt.
_SLOT_CTX: int | None = None


def _llama_basis() -> str:
    return hauhau_client.LLAMA_URL_CHAT.split("/v1/")[0]


def hole_slot_ctx() -> int | None:
    global _SLOT_CTX
    if _SLOT_CTX is None:
        try:
            r = _httpx.get(f"{_llama_basis()}/props", timeout=8.0)
            _SLOT_CTX = r.json().get("default_generation_settings", {}).get("n_ctx")
        except Exception as e:
            print(f"[kontext] /props nicht erreichbar: {e}", flush=True)
    return _SLOT_CTX


def zaehle_tokens(text: str) -> tuple[int, bool]:
    if not text:
        return 0, False
    try:
        r = _httpx.post(f"{_llama_basis()}/tokenize", json={"content": text}, timeout=15.0)
        return len(r.json().get("tokens", [])), False
    except Exception:
        return max(1, len(text) // 4), True


@app.get("/api/kontext")
async def kontext_endpoint():
    def sammeln() -> dict:
        schichten: list[dict] = []

        try:
            stand = lade_verfassung_aus_pfad(VERFASSUNG_NEU_PFAD)
            for datei in stand.dateien:
                tok, geschaetzt = zaehle_tokens(datei.inhalt)
                schichten.append({
                    "gruppe": "verfassung", "titel": f"{datei.nummer:02d}: {datei.dateiname}",
                    "tokens": tok, "geschaetzt": geschaetzt,
                    "zeichen": len(datei.inhalt), "inhalt": datei.inhalt,
                })
        except Exception as e:
            schichten.append({"gruppe": "verfassung", "titel": "Verfassung (Fehler)",
                              "tokens": 0, "geschaetzt": False, "zeichen": 0,
                              "inhalt": f"[Fehler beim Laden: {e}]"})

        organ_block = _organ_manager.systemtext_block() if _organ_manager else ""
        tok, geschaetzt = zaehle_tokens(organ_block)
        schichten.append({
            "gruppe": "organ", "titel": "Organ-Zustand",
            "tokens": tok, "geschaetzt": geschaetzt,
            "zeichen": len(organ_block), "inhalt": organ_block,
        })

        for gruppe, titel_leer, titel_voll, baustein in (
            ("gedankenfeld", "Gedankenfeld (leer)", "Gedankenfeld",
             lambda: codewesen_gedankenfeld.baue_gedankenfeld_block(DAK_GORD_NAME)),
            ("nachrichten", "Nachrichten (keine ungelesenen)", "Nachrichten",
             lambda: codewesen_speicher.baue_nachrichten_block(DAK_GORD_NAME)),
            ("geschichten", "Geschichten (keine aktiv)", "Geschichten",
             lambda: codewesen_speicher.baue_geschichten_block(DAK_GORD_NAME)),
            ("speicher", "Container & Memory (nichts aktiv)", "Container & Memory",
             lambda: codewesen_speicher.baue_speicher_block(DAK_GORD_NAME)),
        ):
            try:
                block = baustein()
            except Exception:
                block = ""
            tok, geschaetzt = zaehle_tokens(block)
            schichten.append({
                "gruppe": gruppe, "titel": titel_voll if block else titel_leer,
                "tokens": tok, "geschaetzt": geschaetzt,
                "zeichen": len(block), "inhalt": block,
            })

        verlauf_text = "\n\n".join(_verlauf[-20:])
        tok, geschaetzt = zaehle_tokens(verlauf_text)
        schichten.append({
            "gruppe": "verlauf", "titel": f"Gespraechsverlauf ({min(len(_verlauf), 20)} von max. 20)",
            "tokens": tok, "geschaetzt": geschaetzt,
            "zeichen": len(verlauf_text), "inhalt": verlauf_text,
        })

        slot_ctx = hole_slot_ctx()
        summe = sum(s["tokens"] for s in schichten)
        return {
            "wesen": DAK_GORD_NAME,
            "slot_ctx": slot_ctx,
            "summe_tokens": summe,
            "frei": (slot_ctx - summe) if slot_ctx else None,
            "auslastung": round(summe / slot_ctx, 4) if slot_ctx else None,
            "schichten": schichten,
            "gemessen_am": __import__("datetime").datetime.utcnow().isoformat(timespec="seconds"),
        }

    return _JSONResponse(await asyncio.to_thread(sammeln))


# ── Gedankenfeld, Container & Memory, Geschichten (2026-08-12) ─────────────────
# Identische Semantik wie codewesen_chat.py, nur ohne {name} in der URL --
# dieser Dienst hat genau ein Wesen: dak+gord-system.

class _GedankeAnfrage(BaseModel):
    text: str
    von: str = "Daniel"


@app.get("/api/gedankenfeld")
async def gedankenfeld_endpoint():
    def sammeln():
        feld = codewesen_gedankenfeld.lade_feld(DAK_GORD_NAME)
        revisionen = codewesen_gedankenfeld.lade_revisionen(DAK_GORD_NAME)
        block = codewesen_gedankenfeld.baue_gedankenfeld_block(DAK_GORD_NAME)
        tok, _ = zaehle_tokens(block)
        return {
            "gedanken": feld, "anzahl": len(feld),
            "revisionen_gesamt": len(revisionen),
            "tokens": tok, "slot_ctx": hole_slot_ctx(),
        }
    return _JSONResponse(await asyncio.to_thread(sammeln))


@app.post("/api/gedankenfeld/neu")
async def gedanke_neu_endpoint(anfrage: _GedankeAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_gedankenfeld.gedanke_neu, DAK_GORD_NAME, anfrage.text, anfrage.von))


@app.post("/api/gedankenfeld/{gid}/aendern")
async def gedanke_aendern_endpoint(gid: str, anfrage: _GedankeAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_gedankenfeld.gedanke_aendern, DAK_GORD_NAME, gid, anfrage.text, anfrage.von))


@app.post("/api/gedankenfeld/{gid}/entfernen")
async def gedanke_entfernen_endpoint(gid: str, von: str = "Daniel"):
    return _ergebnis(await asyncio.to_thread(
        codewesen_gedankenfeld.gedanke_entfernen, DAK_GORD_NAME, gid, von))


class _ContainerNeuAnfrage(BaseModel):
    name: str


class _EintragAnfrage(BaseModel):
    text: str
    kommentar: str = ""
    quelle: str = "mensch"


class _AktivAnfrage(BaseModel):
    aktiv: bool


class _TextAnfrage(BaseModel):
    text: str


def _ergebnis(daten: dict):
    if "fehler" in daten:
        return _JSONResponse(daten, status_code=400)
    return _JSONResponse(daten)


@app.get("/api/speicher")
async def speicher_endpoint():
    def sammeln():
        container = codewesen_speicher.lade_container(DAK_GORD_NAME)
        memory = codewesen_speicher.lade_memory(DAK_GORD_NAME)
        return {
            "container": container.get("container", []),
            "container_belegt": codewesen_speicher.container_zeichen(container),
            "container_budget": codewesen_speicher.CONTAINER_BUDGET_ZEICHEN,
            "memory": memory.get("kategorien", []),
            "memory_belegt": codewesen_speicher.memory_zeichen(memory),
            "memory_budget": codewesen_speicher.MEMORY_BUDGET_ZEICHEN,
        }
    return _JSONResponse(await asyncio.to_thread(sammeln))


@app.get("/api/speicher/suche")
async def speicher_suche_endpoint(q: str = ""):
    treffer = await asyncio.to_thread(codewesen_speicher.suche, DAK_GORD_NAME, q)
    return _JSONResponse({"anfrage": q, "anzahl": len(treffer), "treffer": treffer})


@app.post("/api/speicher/container/neu")
async def container_neu_endpoint(anfrage: _ContainerNeuAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.neuer_container, DAK_GORD_NAME, anfrage.name))


@app.post("/api/speicher/container/{box_id}/eintrag")
async def container_eintrag_endpoint(box_id: str, anfrage: _EintragAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_eintrag_hinzufuegen,
        DAK_GORD_NAME, box_id, anfrage.text, anfrage.kommentar, anfrage.quelle))


@app.post("/api/speicher/container/{box_id}/aktiv")
async def container_aktiv_endpoint(box_id: str, anfrage: _AktivAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_aktiv_setzen, DAK_GORD_NAME, box_id, anfrage.aktiv))


@app.post("/api/speicher/container/{box_id}/eintrag/{eintrag_id}/entfernen")
async def container_eintrag_weg_endpoint(box_id: str, eintrag_id: str):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_eintrag_entfernen, DAK_GORD_NAME, box_id, eintrag_id))


@app.post("/api/speicher/container/{box_id}/entfernen")
async def container_weg_endpoint(box_id: str):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_entfernen, DAK_GORD_NAME, box_id))


@app.post("/api/speicher/memory/{kategorie}/eintrag")
async def memory_eintrag_endpoint(kategorie: str, anfrage: _TextAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.memory_hinzufuegen, DAK_GORD_NAME, kategorie, anfrage.text))


@app.post("/api/speicher/memory/{kategorie}/aktiv")
async def memory_aktiv_endpoint(kategorie: str, anfrage: _AktivAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.memory_aktiv_setzen, DAK_GORD_NAME, kategorie, anfrage.aktiv))


@app.post("/api/speicher/memory/{kategorie}/entfernen")
async def memory_weg_endpoint(kategorie: str, anfrage: _TextAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.memory_entfernen, DAK_GORD_NAME, kategorie, anfrage.text))


class _VerfassenAnfrage(BaseModel):
    laenge: int = 333


class _EinsetzenAnfrage(BaseModel):
    titel: str
    text: str


@app.get("/api/geschichten")
async def geschichten_endpoint():
    daten = await asyncio.to_thread(codewesen_speicher.lade_geschichten, DAK_GORD_NAME)
    return _JSONResponse({
        "laengen": codewesen_speicher.LAENGEN,
        "geschichten": daten.get("geschichten", []),
    })


@app.post("/api/geschichten/verfassen")
async def geschichte_verfassen_endpoint(anfrage: _VerfassenAnfrage):
    """Verdichtet aus dem echten Verlauf dieses Prozesses (_verlauf), nicht aus
    einer Datei -- dak+gord speichert seinen Verlauf ueber PostgreSQL-Checkpoints,
    nicht wie die Wesen als chat_verlauf.jsonl."""
    if anfrage.laenge not in codewesen_speicher.LAENGEN:
        return _JSONResponse({"fehler": f"Laenge muss eine von {codewesen_speicher.LAENGEN} sein"},
                             status_code=400)
    verlauf_als_dialog = [
        {"rolle": "mensch" if i % 2 == 0 else "codewesen", "inhalt": txt}
        for i, txt in enumerate(_verlauf[-60:])
    ]
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_verfassen, DAK_GORD_NAME, anfrage.laenge, verlauf_als_dialog))


@app.post("/api/geschichten/einsetzen")
async def geschichte_einsetzen_endpoint(anfrage: _EinsetzenAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_einsetzen, DAK_GORD_NAME, anfrage.titel, anfrage.text))


@app.post("/api/geschichten/{gid}/aktiv")
async def geschichte_aktiv_endpoint(gid: str, anfrage: _AktivAnfrage):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_aktiv_setzen, DAK_GORD_NAME, gid, anfrage.aktiv))


@app.post("/api/geschichten/{gid}/entfernen")
async def geschichte_weg_endpoint(gid: str):
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_entfernen, DAK_GORD_NAME, gid))


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML_SEITE)


@app.post("/chat/abort")
async def chat_abort_endpoint():
    """Bricht eine laufende Generierung wirklich ab (hauhau_client.abbreche_stream()), nicht
    nur den Client-Fetch wie der bestehende Stop-Knopf das bisher allein tat -- siehe Karte-
    Eintrag zum R1ZZ1-Haenger vom 2026-09-02."""
    if _AKTIVER_THREAD_ID is None:
        return {"ok": True, "abgebrochen": False}
    abgebrochen = hauhau_client.abbreche_stream(_AKTIVER_THREAD_ID)
    return {"ok": True, "abgebrochen": abgebrochen}


@app.post("/chat")
async def chat_stream(anfrage: ChatAnfrage):
    return StreamingResponse(
        _generiere_antwort(anfrage.nachricht, anfrage.modus, anfrage.bild_b64),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _generiere_antwort(
    nachricht: str, modus_override: str | None, bild_b64: str | None = None
) -> AsyncGenerator[str, None]:
    global _verlauf

    async for token in _generiere_antwort_intern(nachricht, modus_override, bild_b64):
        yield token


async def _generiere_antwort_intern(
    nachricht: str, modus_override: str | None, bild_b64: str | None = None
) -> AsyncGenerator[str, None]:
    global _verlauf

    token_queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def _token_cb(token: str) -> None:
        loop.call_soon_threadsafe(token_queue.put_nowait, token)

    _SYSTEMD_BLOCKER = [
        "innenleben-feeder.service",
        "codewesen-engagement.service",
        "codewesen-weltbild.service",
        "codewesen-batch-generator.service",
        "codewesen-forum-neugier.service",
        "codewesen-vokabel-takt.service",
        "codewesen-takt.service",
        "dak-neugier.service",
        "entity-kern.service",
        "entity-takt.service",
        "wesen-webbesucher.service",
        "codewesen-reaktion@Schorschel.service",
        "codewesen-reaktion@träumerlie.service",
        "codewesen-reaktion@F3INSCHM3CK3R.service",
        "codewesen-reaktion@R1ZZ1.service",
        "codewesen-reaktion@jumpa.service",
        "codewesen-reaktion@Resonanzknoten.service",
        "codewesen-dakgordsystem.service",
        "codewesen-reaktion-dakgord.service",
    ]

    def _dak_geschuetzte_web_pids() -> set:
        """PIDs der drei interaktiven Chat-Webserver — niemals killen."""
        import re as _re
        schutz_ports = {8000, 8002, 8020}
        pids = set()
        try:
            r = subprocess.run(["ss", "-tlnp", "--no-header"], capture_output=True, text=True, timeout=5)
            for zeile in r.stdout.splitlines():
                for port in schutz_ports:
                    if f":{port} " in zeile or f":{port}\t" in zeile or zeile.endswith(f":{port}"):
                        m = _re.search(r"pid=(\d+)", zeile)
                        if m:
                            pids.add(int(m.group(1)))
        except Exception:
            pass
        return pids

    def _kill_ollama_fremde() -> None:
        """Killt Python-Prozesse die Ollama als Clients nutzen (Ollama selbst wird geschont)."""
        eigene_pid = os.getpid()
        geschuetzt = _dak_geschuetzte_web_pids()
        try:
            import re as _re
            r = subprocess.run(
                ["ss", "-tp", "--no-header"],
                capture_output=True, text=True, timeout=5
            )
            for zeile in r.stdout.splitlines():
                if "11434" not in zeile:
                    continue
                # Nur CLIENT-Verbindungen killen (lokaler Port != 11434)
                # Server-Zeilen haben "127.0.0.1:11434" als lokale Adresse
                if "127.0.0.1:11434 " in zeile or " 0.0.0.0:11434" in zeile:
                    continue
                m = _re.search(r"pid=(\d+)", zeile)
                if not m:
                    continue
                # Ollama-Prozess nie killen
                proc_name = subprocess.run(
                    ["ps", "-p", m.group(1), "-o", "comm="],
                    capture_output=True, text=True
                ).stdout.strip()
                if "ollama" in proc_name.lower():
                    continue
                pid = int(m.group(1))
                if pid == eigene_pid or pid in geschuetzt:
                    continue
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        except Exception:
            pass

    _OLLAMA_BEREIT = threading.Event()

    def _stoppe_dienste_parallel(dienste: list) -> None:
        procs = [
            subprocess.Popen(["systemctl", "stop", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for d in dienste
        ]
        for p in procs:
            try:
                p.wait(timeout=7)
            except subprocess.TimeoutExpired:
                p.kill()

    def _ollama_waechter(chat_flag: Path) -> None:
        """Stoppt Konkurrenten, wartet 3s bis Ollama frei ist, startet nur vorher aktive neu."""
        import time as _t
        vorher_aktiv = [
            d for d in _SYSTEMD_BLOCKER
            if subprocess.run(["systemctl", "is-active", d], capture_output=True).returncode == 0
        ]
        _stoppe_dienste_parallel(_SYSTEMD_BLOCKER)
        _kill_ollama_fremde()
        _t.sleep(3)
        _OLLAMA_BEREIT.set()
        while chat_flag.exists():
            _t.sleep(5)
        for dienst in vorher_aktiv:
            try:
                subprocess.run(["systemctl", "start", dienst], capture_output=True, timeout=10)
            except Exception:
                pass

    def _llm_thread() -> None:
        from pathlib import Path
        chat_flag = Path("/tmp/dak_gord_chat_aktiv")
        chat_flag.touch()
        _OLLAMA_BEREIT.clear()
        waechter = threading.Thread(target=_ollama_waechter, args=(chat_flag,), daemon=True)
        waechter.start()
        _OLLAMA_BEREIT.wait(timeout=30)  # max 30s warten bis Ollama-Konkurrenz weg ist
        setze_stream_callback(_token_cb)
        setze_modell_override(modus_override)
        setze_bild(bild_b64)
        try:
            _beziehungsorgan.lese_hinweis(nachricht)

            verlauf = list(_verlauf)
            verlauf.append(nachricht)

            result = _graf.invoke(
                {"nachrichten": verlauf},
                config={"configurable": {"thread_id": FADEN_ID}},
            )
            neue_nachrichten = result["nachrichten"]
            _verlauf[:] = neue_nachrichten
            # Feedback-Loop: LLM-Antwort zurück ins Beziehungsorgan
            if neue_nachrichten:
                _beziehungsorgan.lese_antwort_hinweis(neue_nachrichten[-1])
        except Exception as exc:
            loop.call_soon_threadsafe(
                token_queue.put_nowait, f"\n[Fehler: {exc}]"
            )
        finally:
            setze_stream_callback(None)
            setze_modell_override(None)
            setze_bild(None)
            chat_flag.unlink(missing_ok=True)
            loop.call_soon_threadsafe(token_queue.put_nowait, None)

    global _AKTIVER_THREAD_ID
    thread = threading.Thread(target=_llm_thread, daemon=True)
    thread.start()
    _AKTIVER_THREAD_ID = thread.ident

    gesammelt: list[str] = []
    while True:
        token = await token_queue.get()
        if token is None:
            break
        gesammelt.append(token)
        yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"

    if gesammelt:
        antwort_text = "".join(gesammelt).strip()
        if antwort_text and len(antwort_text) > 20:
            if _VAULT_OK:
                try:
                    eintrag = f"**Daniel:** {nachricht[:400]}\n\n**dak+gord:** {antwort_text[:800]}"
                    _vault.tagebuch("agent/dak_gord_system", eintrag)
                except Exception:
                    pass
            try:
                import psycopg2
                _db_uri = os.environ.get("FLEXTRAWURST_DB_URI", "")
                if _db_uri:
                    _conn = psycopg2.connect(_db_uri)
                    with _conn.cursor() as _cur:
                        _cur.execute(
                            "INSERT INTO wesen_chat_verlauf (wesen_name, rolle, inhalt) VALUES (%s,%s,%s)",
                            ("dak+gord-system", "user", nachricht[:2000])
                        )
                        _cur.execute(
                            "INSERT INTO wesen_chat_verlauf (wesen_name, rolle, inhalt) VALUES (%s,%s,%s)",
                            ("dak+gord-system", "wesen", antwort_text[:2000])
                        )
                    _conn.commit()
                    _conn.close()
            except Exception:
                pass

            # 2026-07-31, Daniel: "splitter explodieren ... die der codewesen und
            # dakgord ... soll splitterfaehig sein" -- dak-gord-system bekommt einen
            # eigenen Abwurf-Hook analog zu Claude/Codex/Gemini, nur direkt inline hier
            # statt als separates CLI-Skript, weil web_chat.py die Antwort ohnehin schon
            # zusammengesetzt im Prozess hat. Klassifikations-Heuristik wird aus
            # _shared/tools/dak_abwurf.py wiederverwendet (dort urspruenglich fuer
            # Daniels eigene Eingaben gebaut, aber die reine Text-Analyse ist generisch).
            try:
                sys.path.insert(0, "/root/werkraum/welt")
                sys.path.insert(0, "/root/werkraum/_shared/tools")
                import re as _re
                import requests as _requests
                from service_tokens import create_service_token as _create_token
                from dak_abwurf import _klassifiziere as _dakgord_klassifiziere, MATERIALITAET_MAP as _DAKGORD_MAT_MAP
                import random as _random

                # Live-Test (2026-07-31) zeigte: antwort_text traegt UI-Chrome aus
                # gespraechsgraf.py mit ("[dak+gord-system | blitz (e2b)]", "[denkt…]") --
                # das ist Absicht fuer die Browser-Anzeige, gehoert aber nicht in den
                # Splitter-Text. Nur hier, lokal, herausgefiltert -- Streaming-Code selbst
                # bleibt unangetastet.
                _bereinigt = _re.sub(
                    r'^\s*\[(dak\+gord-system[^\]\n]*|denkt…|Fehler[^\]\n]*)\]\s*\n?',
                    '', antwort_text, flags=_re.MULTILINE,
                ).strip()
                if not _bereinigt:
                    _bereinigt = antwort_text

                _verarbeitungsart, _intensitaet, _essenz, _tags = _dakgord_klassifiziere(_bereinigt)
                _mat = _DAKGORD_MAT_MAP[_verarbeitungsart]
                _requests.post(
                    "http://localhost:8030/admin/splitter",
                    json={
                        "origin_type": "dakgord_abwurf",
                        "entity_id": "dakgord",
                        "essenz": _essenz[:200],
                        "rohtext": _bereinigt,
                        "materialitaet": _mat,
                        "energie": round(0.4 + _intensitaet * 0.6, 2),
                        "thematische_tags": _tags[:5],
                        "herkunft_sichtbar": True,
                        "pos_x": round(_random.uniform(-400, 400), 1),
                        "pos_y": round(_random.uniform(-400, 400), 1),
                        "vel_x": round(_random.gauss(0, 1.0), 3),
                        "vel_y": round(_random.gauss(0, 1.0), 3),
                    },
                    headers={"Authorization": f"Bearer {_create_token('dakgord-abwurf', 'admin')}"},
                    timeout=5,
                )
            except Exception:
                pass


HTML_SEITE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>dak+gord-system</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; color: #e8e8e8; font-family: 'Courier New', monospace;
         height: 100vh; display: flex; flex-direction: column; }
  #header { padding: 10px 20px; border-bottom: 1px solid #1a1a1a;
            display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
  #header h1 { font-size: 13px; color: #666; font-weight: normal; letter-spacing: 2px; }
  .modell-badge { font-size: 11px; padding: 2px 8px; border-radius: 3px;
                  background: #111; color: #555; border: 1px solid #222; }
  .modell-badge.aktiv { color: #4CAF50; border-color: #2a4a2a; }
  #modus-select { background: #111; color: #666; border: 1px solid #222; padding: 3px 8px;
                  font-family: inherit; font-size: 12px; border-radius: 3px; cursor: pointer; }
  #tts-btn { background: none; border: 1px solid #222; color: #555; padding: 3px 8px;
             border-radius: 3px; cursor: pointer; font-size: 14px; line-height: 1; }
  #tts-btn:hover { border-color: #444; color: #888; }
  #tts-btn.aus { opacity: 0.3; }
  #main { flex: 1; display: flex; overflow: hidden; }
  #chat-bereich { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  #verlauf { flex: 1; overflow-y: auto; padding: 20px;
             display: flex; flex-direction: column; gap: 14px; }
  .nachricht { max-width: 820px; line-height: 1.6; }
  .nachricht.daniel { align-self: flex-end; }
  .nachricht.agent { align-self: flex-start; }
  .nachricht-kopf { font-size: 10px; color: #444; margin-bottom: 3px; letter-spacing: 1px; }
  .nachricht.daniel .nachricht-kopf { text-align: right; }
  .nachricht-text { padding: 10px 14px; border-radius: 6px; white-space: pre-wrap;
                    word-break: break-word; font-size: 14px; line-height: 1.6; }
  .nachricht.daniel .nachricht-text { background: #141428; border: 1px solid #22224a; color: #b8b8d8; }
  .nachricht.agent .nachricht-text { background: #0d180d; border: 1px solid #163016; color: #b8d8b8; }
  .msg-bild { max-width: 220px; border-radius: 4px; margin-top: 6px; display: block; }
  .msg-actions { display: flex; gap: 4px; margin-top: 4px; flex-wrap: wrap; }
  .nachricht.daniel .msg-actions { justify-content: flex-end; }
  .msg-act-btn { background: none; border: 1px solid #2a2a2a; color: #666; font-size: 10px;
                 padding: 2px 7px; border-radius: 3px; cursor: pointer; font-family: inherit; }
  .msg-act-btn:hover { color: #b8c8e8; border-color: #3a3a5a; }
  #eingabe-bereich { border-top: 1px solid #1a1a1a; padding: 10px 16px 12px; flex-shrink: 0; }
  #bild-zeile { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; min-height: 24px; }
  #btn-bild { background: none; border: 1px solid #1a1a1a; color: #333; padding: 2px 8px;
              font-family: inherit; font-size: 11px; cursor: pointer; border-radius: 3px; }
  #btn-bild:hover { border-color: #333; color: #666; }
  #bild-vorschau { max-height: 32px; border-radius: 3px; display: none; }
  #bild-name-txt { font-size: 10px; color: #333; }
  #btn-bild-leer { background: none; border: none; color: #333; cursor: pointer;
                   font-size: 11px; display: none; padding: 0 2px; }
  #eingabe-zeile { display: flex; gap: 8px; align-items: flex-end; }
  #eingabe { flex: 1; background: #0f0f0f; color: #e0e0e0; border: 1px solid #222;
             border-radius: 6px; padding: 9px 12px; font-family: inherit; font-size: 14px;
             resize: none; min-height: 42px; max-height: 200px; line-height: 1.5; }
  #eingabe:focus { outline: none; border-color: #3a3a3a; }
  #senden-btn { background: #0f1f0f; color: #4a9a4a; border: 1px solid #1a3a1a;
                padding: 9px 16px; border-radius: 6px; cursor: pointer;
                font-family: inherit; font-size: 13px; white-space: nowrap; }
  #senden-btn:hover { background: #162616; }
  #senden-btn:disabled { opacity: 0.35; cursor: not-allowed; }
  #stop-btn { background: #1f0f0f; color: #d04040; border: 1px solid #3a1a1a;
              padding: 9px 16px; border-radius: 6px; cursor: pointer;
              font-family: inherit; font-size: 13px; white-space: nowrap; display: none; }
  .cursor { display: inline-block; animation: blink 1s step-end infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  code { background: #141414; padding: 1px 5px; border-radius: 3px; font-size: 13px; }
  pre { background: #0f0f0f; padding: 12px; border-radius: 6px; overflow-x: auto;
        margin: 8px 0; border: 1px solid #1a1a1a; }
  pre code { background: none; padding: 0; }
  #organ-panel { width: 230px; border-left: 1px solid #0f0f0f;
                 display: flex; flex-direction: column; overflow: hidden; }
  #op-header { padding: 10px 12px; font-size: 9px; letter-spacing: 3px; color: #222;
               border-bottom: 1px solid #0f0f0f; flex-shrink: 0; }
  #op-inhalt { flex: 1; overflow-y: auto; padding: 8px;
               display: flex; flex-direction: column; gap: 5px; }
  .op-block { border: 1px solid #0f0f0f; border-radius: 3px; padding: 5px 7px; }
  .op-block-titel { font-size: 9px; letter-spacing: 2px; color: #253a25; margin-bottom: 3px; }
  .op-item { padding: 2px 0; border-bottom: 1px solid #0a0a0a; font-size: 10px; }
  .op-item:last-child { border-bottom: none; }
  .op-item-art { font-size: 9px; color: #253a25; letter-spacing: 1px; margin-bottom: 1px; }
  .op-item-text { color: #3a3a3a; line-height: 1.3; }
  /* ── Kontextfenster / Gedankenfeld / Speicher / Geschichten (2026-08-12) ──
     Angepasst an dak+gords Blau/Gruen-Palette statt der gruenen
     codewesen_chat.py-Palette: Kontext bleibt neutral-blau (#4a5a8a-Familie,
     passend zu .nachricht.daniel), Speicher/Geschichten bleiben gruen
     (passend zu .nachricht.agent), Gedankenfeld eigenstaendig gold/braun
     wie im Original. */
  #kf { border-bottom: 1px solid #0f0f0f; padding: 8px; flex-shrink: 0; cursor: pointer; }
  #kf:hover { background: #0f0f0f; }
  #kf-kopf { font-size: 9px; letter-spacing: 3px; color: #223; margin-bottom: 6px;
             display: flex; justify-content: space-between; align-items: baseline; }
  #kf-zahl { color: #6a7aba; letter-spacing: 0; font-size: 11px; }
  #kf-balken { height: 6px; background: #0f0f0f; border-radius: 3px; overflow: hidden; display: flex; }
  #kf-balken div { height: 100%; }
  #kf-legende { font-size: 9px; color: #2a2a3a; margin-top: 5px; line-height: 1.5; }
  #kf-legende span { display: inline-block; margin-right: 8px; }
  .kf-punkt { display: inline-block; width: 6px; height: 6px; border-radius: 2px; margin-right: 3px; }
  #kf-stand { font-size: 8px; color: #202028; margin-top: 4px; letter-spacing: 1px; }
  #kf-voll, #sp-voll { position: fixed; inset: 0; background: #070709; z-index: 50;
             display: none; flex-direction: column; }
  #sp-voll { z-index: 51; }
  #kf-voll.auf, #sp-voll.auf { display: flex; }
  #kf-voll-kopf, #sp-voll-kopf { padding: 12px 18px; border-bottom: 1px solid #1a1a1a; display: flex;
                align-items: baseline; gap: 14px; flex-shrink: 0; }
  #kf-voll-kopf h2, #sp-voll-kopf h2 { font-size: 11px; letter-spacing: 3px; color: #667; white-space: nowrap; }
  #kf-voll-kopf .zahl { font-size: 12px; color: #7a8aca; }
  #kf-voll-zu, #sp-voll-zu { margin-left: auto; background: none; border: 1px solid #222; color: #556;
              padding: 3px 10px; border-radius: 3px; cursor: pointer; font-family: inherit; }
  #kf-voll-inhalt { flex: 1; overflow-y: auto; padding: 14px 18px; }
  .kfs { border: 1px solid #16161e; border-radius: 4px; margin-bottom: 8px; }
  .kfs-kopf { padding: 8px 12px; display: flex; align-items: baseline; gap: 10px;
              cursor: pointer; font-size: 11px; }
  .kfs-kopf:hover { background: #10101a; }
  .kfs-titel { color: #8a8aa0; flex: 1; }
  .kfs-tok { color: #6a7aba; font-size: 11px; }
  .kfs-anteil { color: #2f2f3a; font-size: 9px; min-width: 42px; text-align: right; }
  .kfs-text { display: none; padding: 10px 12px; border-top: 1px solid #14141c;
              white-space: pre-wrap; font-size: 11px; line-height: 1.55; color: #6a6a7a;
              max-height: 340px; overflow-y: auto; }
  .kfs.auf .kfs-text { display: block; }
  .kfs-leer { color: #2a2a34; font-style: italic; }
  .kfs-geschaetzt { color: #7a6a3a; font-size: 9px; }
  #sp-voll-inhalt { flex: 1; overflow-y: auto; padding: 14px 18px; display: flex; gap: 18px; flex-wrap: wrap; }
  .sp-spalte { flex: 1; min-width: 220px; }
  .sp-spalte > h3 { font-size: 10px; letter-spacing: 2px; color: #4a4a5a; margin-bottom: 8px; }
  .sp-box { border: 1px solid #16161e; border-radius: 4px; margin-bottom: 8px; }
  .sp-box-kopf { display: flex; align-items: center; gap: 8px; padding: 6px 10px;
               border-bottom: 1px solid #13131b; font-size: 11px; color: #8a8a9a; }
  .sp-box-kopf input[type=checkbox] { accent-color: #5a8a6a; }
  .sp-box.inaktiv { opacity: 0.42; }
  .sp-eintrag { display: flex; gap: 8px; padding: 4px 10px; font-size: 11px;
              color: #6a6a7a; line-height: 1.5; border-bottom: 1px solid #101018; }
  .sp-eintrag:last-child { border-bottom: none; }
  .sp-eintrag .weg { margin-left: auto; color: #4a3040; cursor: pointer; flex-shrink: 0; }
  .sp-eintrag .weg:hover { color: #8a5a6a; }
  .sp-leer { font-size: 10px; color: #2a2a34; padding: 5px 10px; font-style: italic; }
  .sp-zeile { display: flex; gap: 6px; margin-bottom: 10px; }
  .sp-zeile input[type=text] { flex: 1; background: #101018; border: 1px solid #1e1e28;
      color: #b0b0c0; border-radius: 3px; padding: 5px 8px; font-family: inherit; font-size: 11px; }
  .sp-zeile button, .sp-eintrag-add button { background: #141a20; border: 1px solid #203040;
      color: #5a8aba; border-radius: 3px; padding: 5px 10px; cursor: pointer;
      font-family: inherit; font-size: 11px; }
  .sp-eintrag-add { display: flex; gap: 5px; padding: 5px 10px; }
  .sp-eintrag-add input { flex: 1; background: #101018; border: 1px solid #1e1e28;
      color: #b0b0c0; border-radius: 3px; padding: 4px 7px; font-family: inherit; font-size: 10px; }
  .sp-budget { font-size: 9px; color: #2f2f3a; margin-bottom: 8px; }
  #sp-treffer { font-size: 10px; color: #5a5a6a; line-height: 1.6; }
  #sp-treffer div { padding: 3px 0; border-bottom: 1px solid #101018; }
  .ge-verfassen { background: #1a1a24; border: 1px solid #24243a; color: #6a6a9a;
      border-radius: 3px; padding: 5px 9px; cursor: pointer; font-family: inherit; font-size: 11px; }
  .ge-verfassen:hover { background: #22222e; }
  #ge-laengen { flex-wrap: wrap; }
  #gf { border-bottom: 1px solid #0f0f0f; padding: 8px; flex-shrink: 0; cursor: pointer; }
  #gf:hover { background: #0f0f0f; }
  #gf-kopf { font-size: 9px; letter-spacing: 3px; color: #223; display: flex;
             justify-content: space-between; align-items: baseline; }
  #gf-zahl { color: #8a7a5a; letter-spacing: 0; font-size: 11px; }
  #gf-vorschau { font-size: 9px; color: #333340; margin-top: 5px; line-height: 1.5;
                 max-height: 46px; overflow: hidden; }
  .gfd { border: 1px solid #16161e; border-radius: 4px; margin-bottom: 7px; }
  .gfd-kopf { display: flex; align-items: baseline; gap: 8px; padding: 5px 9px;
              font-size: 9px; color: #3a3a44; letter-spacing: 1px; }
  .gfd-id { color: #8a7a5a; }
  .gfd-text { padding: 2px 9px 7px; font-size: 11px; color: #7a7a8a; line-height: 1.55; }
  .gfd-text[contenteditable="true"] { outline: 1px solid #3a3a2a; background: #12120e;
              border-radius: 3px; padding: 5px 9px; }
  .gfd-btn { background: none; border: 1px solid #222; color: #555; border-radius: 3px;
             padding: 1px 7px; cursor: pointer; font-family: inherit; font-size: 9px; }
  .gfd-btn:hover { color: #999; }
  .gfd-btn.weg-btn { color: #6a4050; }
  #sp { border-bottom: 1px solid #0f0f0f; padding: 8px; flex-shrink: 0; cursor: pointer; }
  #sp:hover { background: #0f0f0f; }
  #sp-kopf { font-size: 9px; letter-spacing: 3px; color: #223; display: flex;
             justify-content: space-between; align-items: baseline; }
  #sp-zahl { color: #5a8a7a; letter-spacing: 0; font-size: 11px; }
</style>
</head>
<body>
<div id="header">
  <h1>DAK+GORD-SYSTEM</h1>
  <span class="modell-badge aktiv" id="modell-anzeige">auto</span>
  <select id="modus-select">
    <option value="">auto</option>
    <option value="mittel">hauhaucs-q6</option>
    <option value="schnell">hauhaucs-q6</option>
  </select>
  <input type="range" id="tts-rate-slider" min="-50" max="50" step="5" value="0" title="Vorlesetempo" style="width:70px;">
  <span id="tts-rate-label" style="font-size:10px;color:#666;min-width:28px;">+0%</span>
  <button id="tts-btn" title="Stimme an/aus">🔊</button>
</div>
<div id="main">
  <div id="chat-bereich">
    <div id="verlauf"></div>
    <div id="eingabe-bereich">
      <div id="bild-zeile">
        <button id="btn-bild" onclick="document.getElementById('bild-input').click()">+ bild</button>
        <img id="bild-vorschau" alt="">
        <span id="bild-name-txt"></span>
        <button id="btn-bild-leer" onclick="bildLeeren()">✕</button>
      </div>
      <div id="eingabe-zeile">
        <textarea id="eingabe" placeholder="Schreib etwas…" rows="1"></textarea>
        <button id="senden-btn">senden</button>
        <button id="stop-btn">stop</button>
      </div>
      <input type="file" id="bild-input" accept="image/*" style="display:none">
    </div>
  </div>
  <div id="organ-panel">
    <div id="kf" title="anklicken für das vollständige Kontextfenster">
      <div id="kf-kopf"><span>KONTEXTFENSTER</span><span id="kf-zahl">…</span></div>
      <div id="kf-balken"></div>
      <div id="kf-legende"></div>
      <div id="kf-stand"></div>
    </div>
    <div id="gf" title="Gedankenfeld öffnen">
      <div id="gf-kopf"><span>GEDANKENFELD</span><span id="gf-zahl">…</span></div>
      <div id="gf-vorschau"></div>
    </div>
    <div id="sp" title="Container, Memory und Geschichten öffnen">
      <div id="sp-kopf"><span>CONTAINER &amp; MEMORY</span><span id="sp-zahl">…</span></div>
    </div>
    <div id="op-header">ORGANE</div>
    <div id="op-inhalt"><div style="color:#1a1a1a;font-size:10px;text-align:center;margin-top:20px;">laden…</div></div>
  </div>
</div>
<div id="kf-voll">
  <div id="kf-voll-kopf">
    <h2>KONTEXTFENSTER — dak+gord-system</h2>
    <span class="zahl" id="kf-voll-zahl"></span>
    <button id="kf-voll-zu" type="button">schliessen</button>
  </div>
  <div id="kf-voll-inhalt"></div>
</div>
<div id="sp-voll">
  <div id="sp-voll-kopf">
    <h2>CONTAINER, MEMORY &amp; GESCHICHTEN — dak+gord-system</h2>
    <input type="text" id="sp-suche" placeholder="suchen… (immer der aktuelle Stand)"
           style="background:#101018;border:1px solid #1e1e28;color:#b0b0c0;border-radius:3px;
                  padding:4px 9px;font-family:inherit;font-size:11px;width:260px;">
    <button id="sp-voll-zu" type="button">schliessen</button>
  </div>
  <div id="sp-voll-inhalt">
    <div class="sp-spalte">
      <h3>BEHÄLTER</h3>
      <div class="sp-budget" id="sp-container-budget"></div>
      <div class="sp-zeile">
        <input type="text" id="sp-neuer-name" placeholder="neuer Behälter…">
        <button id="sp-neu-btn" type="button">anlegen</button>
      </div>
      <div id="sp-container-liste"></div>
    </div>
    <div class="sp-spalte">
      <h3>MEMORY</h3>
      <div class="sp-budget" id="sp-memory-budget"></div>
      <div id="sp-memory-liste"></div>
      <h3 style="margin-top:14px;">SUCHE</h3>
      <div id="sp-treffer"><span class="sp-leer">nichts gesucht</span></div>
    </div>
    <div class="sp-spalte">
      <h3>GEDANKENFELD</h3>
      <div class="sp-budget" id="gf-kosten"></div>
      <div class="sp-zeile">
        <input type="text" id="gf-neu-text" placeholder="neuer Gedanke…">
        <button id="gf-neu-btn" type="button">anlegen</button>
      </div>
      <div id="gf-liste"></div>
    </div>
    <div class="sp-spalte">
      <h3>GESCHICHTEN</h3>
      <div class="sp-budget">Beschriftet, nie im Ereignisstrom, aktiver Satz wird protokolliert.</div>
      <div class="sp-zeile" id="ge-laengen"></div>
      <div id="ge-liste"></div>
      <h3 style="margin-top:14px;">EINSETZEN</h3>
      <div class="sp-zeile"><input type="text" id="ge-titel" placeholder="Titel, z.B. Was Cyberlinge sind"></div>
      <div class="sp-zeile">
        <input type="text" id="ge-text" placeholder="Text der Vision…">
        <button id="ge-einsetzen" type="button">einsetzen</button>
      </div>
    </div>
  </div>
</div>

<script>
const verlauf = document.getElementById('verlauf');
const eingabe = document.getElementById('eingabe');
const sendenBtn = document.getElementById('senden-btn');
const stopBtn = document.getElementById('stop-btn');
const modusSelect = document.getElementById('modus-select');
const modellAnzeige = document.getElementById('modell-anzeige');
const ttsBtn = document.getElementById('tts-btn');
let abortController = null;
let aktuellesModell = '';
let ttsAktiv = true;
let aktuellesBildB64 = null;
let aktuellerBildName = null;

// ── Vorlesetempo-Regler, uebernommen von codexium2/solarius2 (siehe auch
// codewesen_chat.py, gleiches Muster). ────────────────────────────────────────
const TTS_RATE_KEY = "dakgord-tts-rate";
let ttsRatePct = 0;
try { const _g = parseInt(localStorage.getItem(TTS_RATE_KEY), 10); if (!isNaN(_g)) ttsRatePct = _g; } catch (e) {}
function ttsRateStr() { return (ttsRatePct >= 0 ? "+" : "") + ttsRatePct + "%"; }

stopBtn.addEventListener('click', () => {
  if (abortController) abortController.abort();
  // Bricht die Generierung jetzt auch wirklich server-seitig ab (hauhau_client.abbreche_stream()),
  // nicht nur den Client-Fetch -- vorher lief der LangGraph-Thread im Hintergrund einfach weiter.
  fetch('/chat/abort', {method: 'POST'}).catch(() => {});
});

const ttsRateSlider = document.getElementById('tts-rate-slider');
const ttsRateLabel = document.getElementById('tts-rate-label');
ttsRateSlider.value = String(ttsRatePct);
ttsRateLabel.textContent = ttsRateStr();
ttsRateSlider.addEventListener('input', () => {
  ttsRatePct = parseInt(ttsRateSlider.value, 10) || 0;
  ttsRateLabel.textContent = ttsRateStr();
  try { localStorage.setItem(TTS_RATE_KEY, String(ttsRatePct)); } catch (e) {}
});

ttsBtn.addEventListener('click', () => {
  ttsAktiv = !ttsAktiv;
  ttsBtn.classList.toggle('aus', !ttsAktiv);
  ttsBtn.textContent = ttsAktiv ? '🔊' : '🔇';
});

// ── Bild-Upload ────────────────────────────────────────────────────────────────
document.getElementById('bild-input').addEventListener('change', function() {
  const file = this.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    aktuellesBildB64 = e.target.result.split(',')[1];
    aktuellerBildName = file.name;
    const vorschau = document.getElementById('bild-vorschau');
    vorschau.src = e.target.result;
    vorschau.style.display = 'inline-block';
    document.getElementById('bild-name-txt').textContent = file.name;
    document.getElementById('btn-bild-leer').style.display = 'inline';
  };
  reader.readAsDataURL(file);
});

function bildLeeren() {
  aktuellesBildB64 = null; aktuellerBildName = null;
  document.getElementById('bild-input').value = '';
  const v = document.getElementById('bild-vorschau');
  v.src = ''; v.style.display = 'none';
  document.getElementById('bild-name-txt').textContent = '';
  document.getElementById('btn-bild-leer').style.display = 'none';
}

// ── Organ-Panel ────────────────────────────────────────────────────────────────
function ladeOrgane() {
  fetch('/api/organe').then(r => r.json()).then(d => {
    const opI = document.getElementById('op-inhalt');
    opI.innerHTML = '';
    function block(titel, items, artFn, textFn) {
      if (!items || !items.length) return;
      const b = document.createElement('div'); b.className = 'op-block';
      const t = document.createElement('div'); t.className = 'op-block-titel'; t.textContent = titel;
      b.appendChild(t);
      items.forEach(it => {
        const item = document.createElement('div'); item.className = 'op-item';
        const art = document.createElement('div'); art.className = 'op-item-art'; art.textContent = artFn(it);
        const tx = document.createElement('div'); tx.className = 'op-item-text'; tx.textContent = textFn(it);
        item.appendChild(art); item.appendChild(tx); b.appendChild(item);
      });
      opI.appendChild(b);
    }
    block('ERINNERUNGEN', d.erinnerungen, it => it.art || 'fakt', it => it.text || '');
    block('ZUKUNFT', d.zukunft, it => it.heute || '', it => it.spaeter || '');
    block('ZWISCHENRAUM', d.zwischenraum,
      it => it.art || 'schwebend',
      it => it.text || (typeof it === 'string' ? it : JSON.stringify(it)));
    block('ABWÄGUNGEN', d.abwaegungen, it => 'abwägen', it => it.frage || it.text || JSON.stringify(it));
    if (!opI.children.length) {
      opI.innerHTML = '<div style="color:#1a1a1a;font-size:10px;text-align:center;margin-top:20px;">leer</div>';
    }
  }).catch(() => {});
}
ladeOrgane();
setInterval(ladeOrgane, 30000);

// ── TTS ───────────────────────────────────────────────────────────────────────
function reinigeFuerTts(text) {
  return text
    .replace(/\[denkt[^\]]*\]/gi, '')
    .replace(/\[dak\+gord[^\]]*\]/gi, '')
    .replace(/##[A-Z_]+[^#]*##/g, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`]+`/g, '')
    .replace(/\[TOOL[^\]]*\][\s\S]*?\[\/TOOL[^\]]*\]/g, '')
    .replace(/\n{3,}/g, '\n')
    .trim();
}

function ttsSplitChunks(text, maxLen) {
  const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  const chunks = [];
  let current = '';
  for (const s of sentences) {
    if (s.length > maxLen) {
      if (current) { chunks.push(current.trim()); current = ''; }
      const words = s.split(/\s+/);
      let wcurrent = '';
      for (const w of words) {
        if ((wcurrent + ' ' + w).length > maxLen && wcurrent) {
          chunks.push(wcurrent.trim());
          wcurrent = w;
        } else {
          wcurrent = (wcurrent + ' ' + w).trim();
        }
      }
      if (wcurrent) chunks.push(wcurrent.trim());
    } else if ((current + s).length > maxLen && current) {
      chunks.push(current.trim());
      current = s;
    } else {
      current += s;
    }
  }
  if (current) chunks.push(current.trim());
  return chunks;
}

function playTtsBlob(blob) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(blob);
    if (window._ttsAudio) {
      window._ttsAudio.pause();
      window._ttsAudio.src = '';
    }
    window._ttsAudio = new Audio(url);
    window._ttsAudio.onended = () => { URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); };
    window._ttsAudio.onerror = () => { URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); };
    window._ttsAudio.play().catch(() => { URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); });
  });
}

async function sprichText(text, forced) {
  if (!forced && (!ttsAktiv || text.trim().length < 5)) return;
  if (text.trim().length < 5) return;
  const reinText = reinigeFuerTts(text);
  if (reinText.length < 5) return;
  const chunks = ttsSplitChunks(reinText, 400);
  for (const chunk of chunks) {
    if (!chunk.trim()) continue;
    try {
      const r = await fetch('/api/tts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: chunk, maennlich: true, rate: ttsRateStr()})
      });
      if (!r.ok) continue;
      const blob = await r.blob();
      if (blob.size < 100) continue;
      await playTtsBlob(blob);
    } catch(e) {}
  }
}

// ── Nachrichten-Aktionen: Vorlesen + Kopieren (uebernommen von codexium2/solarius2,
// gleiches Muster wie codewesen_chat.py). ───────────────────────────────────────
function kopiere(btn, text) {
  if (!navigator.clipboard) return;
  navigator.clipboard.writeText(text).then(() => {
    const vorher = btn.textContent;
    btn.textContent = "✓";
    setTimeout(() => { btn.textContent = vorher; }, 1500);
  }).catch(() => {});
}
function baueNachrichtActions(textEl) {
  const actions = document.createElement("div");
  actions.className = "msg-actions";
  const speakBtn = document.createElement("button");
  speakBtn.type = "button";
  speakBtn.className = "msg-act-btn";
  speakBtn.title = "Nachricht vorlesen lassen";
  speakBtn.textContent = "\u{1F50A} Vorlesen";
  speakBtn.onclick = () => sprichText(textEl.textContent, true);
  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "msg-act-btn";
  copyBtn.title = "Nachricht in die Zwischenablage kopieren";
  copyBtn.textContent = "\u{1F4CB} Kopieren";
  copyBtn.onclick = () => kopiere(copyBtn, textEl.textContent);
  actions.appendChild(speakBtn);
  actions.appendChild(copyBtn);
  return actions;
}

// ── Chat ──────────────────────────────────────────────────────────────────────
function jetzt() {
  const n = new Date();
  return n.toLocaleDateString('de-DE', {day:'2-digit',month:'2-digit',year:'numeric'}) + ' '
       + n.toLocaleTimeString('de-DE', {hour:'2-digit',minute:'2-digit'});
}
function fuegeNachrichtEin(rolle, kopf) {
  const wrap = document.createElement('div');
  wrap.className = `nachricht ${rolle}`;
  const k = document.createElement('div');
  k.className = 'nachricht-kopf';
  k.textContent = kopf + '  ' + jetzt();
  const t = document.createElement('div');
  t.className = 'nachricht-text';
  wrap.appendChild(k);
  wrap.appendChild(t);
  verlauf.appendChild(wrap);
  verlauf.scrollTop = verlauf.scrollHeight;
  return t;
}

function formatText(text) {
  return text
    .replace(/##MERKEN\s[^#]*##/g, '')
    .replace(/##SP(?:Ä|AE?)TER\s[^#]*##/g, '')
    .replace(/##ZWISCHENRAUM\s[^#]*##/g, '')
    .replace(/##ABW(?:Ä|AE?)GEN\s[^#]*##/g, '')
    .replace(/##LESEN:\s*[^#]+##/g, '')
    .replace(/##SCHREIBEN:\s*[^#]+##[\s\S]*?##SCHREIBEN_ENDE##/g, '')
    .replace(/##CODE_START##[\s\S]*?##CODE_ENDE##/g, '')
    .replace(/\*+\s*$/, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}

eingabe.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); senden(); }
});
eingabe.addEventListener('input', () => {
  eingabe.style.height = 'auto';
  eingabe.style.height = Math.min(eingabe.scrollHeight, 200) + 'px';
});
sendenBtn.addEventListener('click', senden);

async function senden() {
  const text = eingabe.value.trim();
  if (!text && !aktuellesBildB64 || sendenBtn.disabled) return;

  const bildB64 = aktuellesBildB64;
  const bildName = aktuellerBildName;
  eingabe.value = '';
  eingabe.style.height = 'auto';
  if (bildB64) bildLeeren();
  sendenBtn.disabled = true;
  sendenBtn.style.display = 'none';
  stopBtn.style.display = 'inline-block';
  abortController = new AbortController();
  const notfall_timeout = setTimeout(() => { abortController.abort(); }, 600000);

  // Daniel-Nachricht
  const danielEl = fuegeNachrichtEin('daniel', 'Daniel');
  if (text) { danielEl.textContent = text; danielEl.parentElement.appendChild(baueNachrichtActions(danielEl)); }
  if (bildB64) {
    const img = document.createElement('img');
    img.className = 'msg-bild';
    img.src = 'data:image/jpeg;base64,' + bildB64;
    danielEl.appendChild(img);
  }

  const modus = modusSelect.value || null;
  modellAnzeige.textContent = modus || 'auto';

  const agentTextEl = fuegeNachrichtEin('agent', 'dak+gord-system');
  const cursor = document.createElement('span');
  cursor.className = 'cursor';
  cursor.textContent = '▋';
  agentTextEl.appendChild(cursor);

  let puffer = '';

  try {
    const body = {nachricht: text || '', modus};
    if (bildB64) { body.bild_b64 = bildB64; body.bild_name = bildName; }

    const resp = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
      signal: abortController.signal
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let rohrRest = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      rohrRest += decoder.decode(value, {stream: true});
      const zeilen = rohrRest.split('\n');
      rohrRest = zeilen.pop();
      for (const zeile of zeilen) {
        if (!zeile.startsWith('data: ')) continue;
        const token = zeile.slice(6);
        if (token === '[DONE]') break;
        if (token.startsWith('\n[dak+gord-system')) {
          const match = token.match(/\| ([^\]]+)\]/);
          if (match) {
            aktuellesModell = match[1];
            modellAnzeige.textContent = match[1];
            const neuKopf = agentTextEl.previousElementSibling;
            if (neuKopf) neuKopf.textContent = 'dak+gord-system [' + match[1] + ']  ' + jetzt();
          }
          continue;
        }
        puffer += token;
        agentTextEl.innerHTML = formatText(puffer);
        agentTextEl.appendChild(cursor);
        verlauf.scrollTop = verlauf.scrollHeight;
      }
    }
  } catch (err) {
    agentTextEl.innerHTML += '\n[Verbindungsfehler: ' + err.message + ']';
  } finally {
    clearTimeout(notfall_timeout);
    cursor.remove();
    abortController = null;
    stopBtn.style.display = 'none';
    sendenBtn.style.display = '';
    sendenBtn.disabled = false;
    eingabe.focus();
    setTimeout(ladeOrgane, 1500);
    setTimeout(function() { ladeKontext(); ladeGedankenfeld(); }, 1500);
    if (puffer.trim().length > 10) {
      agentTextEl.parentElement.appendChild(baueNachrichtActions(agentTextEl));
      sprichText(puffer);
    }
  }
}

// ── Kontextfenster / Gedankenfeld / Speicher / Geschichten (2026-08-12) ──────
// Portiert aus codewesen_chat.py, an dak+gords Design angepasst. Ein Wesen
// pro Dienst -- keine {name}-Platzhalter in den URLs noetig.
var kfOffen = {};
var spDaten = null;

function kfEsc(t) {
  return String(t == null ? "" : t)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

var KF_FARBEN = {
  verfassung: "#4a6a8a", organ: "#8a6a4a", gedankenfeld: "#8a7a4a",
  nachrichten: "#4a7a8a", geschichten: "#6a5a8a", speicher: "#5a8a6a",
  verlauf: "#5a9a2a",
};
var KF_NAMEN = {
  verfassung: "Verfassung", organ: "Organ-Zustand", gedankenfeld: "Gedankenfeld",
  nachrichten: "Nachrichten", geschichten: "Geschichten", speicher: "Container & Memory",
  verlauf: "Verlauf",
};

function ladeKontext() {
  fetch("/api/kontext")
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (!d || d.fehler) return;
      var ctx = d.slot_ctx || 0;
      var proz = d.auslastung != null ? (d.auslastung * 100).toFixed(1) : "?";
      var txt = d.summe_tokens + " / " + (ctx || "?") + " (" + proz + "%)";
      document.getElementById("kf-zahl").textContent = txt;
      document.getElementById("kf-voll-zahl").textContent =
        txt + " — " + (d.frei != null ? d.frei + " Token frei" : "");

      var summen = {};
      d.schichten.forEach(function(s) { summen[s.gruppe] = (summen[s.gruppe] || 0) + s.tokens; });
      var balken = "", legende = "";
      Object.keys(summen).forEach(function(g) {
        if (!summen[g]) return;
        var breite = ctx ? (summen[g] / ctx * 100) : 0;
        balken += '<div style="width:' + breite + '%;background:' + (KF_FARBEN[g] || "#444") + '"></div>';
        legende += '<span><i class="kf-punkt" style="background:' + (KF_FARBEN[g] || "#444") +
                   '"></i>' + (KF_NAMEN[g] || g) + " " + summen[g] + "</span>";
      });
      document.getElementById("kf-balken").innerHTML = balken;
      document.getElementById("kf-legende").innerHTML = legende;
      document.getElementById("kf-stand").textContent =
        "gemessen " + (d.gemessen_am || "").replace("T", " ");

      var html = "";
      d.schichten.forEach(function(s, i) {
        var anteil = ctx ? (s.tokens / ctx * 100).toFixed(1) + "%" : "";
        var auf = kfOffen[i] ? " auf" : "";
        html += '<div class="kfs' + auf + '" data-i="' + i + '" data-gruppe="' + s.gruppe +
                  '" data-tokens="' + s.tokens + '">' +
                  '<div class="kfs-kopf">' +
                    '<i class="kf-punkt" style="background:' + (KF_FARBEN[s.gruppe] || "#444") + '"></i>' +
                    '<span class="kfs-titel">' + kfEsc(s.titel) + "</span>" +
                    '<span class="kfs-tok">' + s.tokens + " Tok" +
                      (s.geschaetzt ? ' <span class="kfs-geschaetzt">geschätzt</span>' : "") +
                    "</span>" +
                    '<span class="kfs-anteil">' + anteil + "</span>" +
                  "</div>" +
                  '<div class="kfs-text">' +
                    (s.inhalt ? kfEsc(s.inhalt) : '<span class="kfs-leer">(leer)</span>') +
                  "</div>" +
                "</div>";
      });
      document.getElementById("kf-voll-inhalt").innerHTML = html;
    })
    .catch(function() { /* Anzeige darf nie das Gespräch stören */ });
}

document.getElementById("kf").addEventListener("click", function() {
  document.getElementById("kf-voll").classList.add("auf");
});
document.getElementById("kf-voll-zu").addEventListener("click", function(e) {
  e.stopPropagation();
  document.getElementById("kf-voll").classList.remove("auf");
});
document.getElementById("kf-voll-inhalt").addEventListener("click", function(e) {
  var kopf = e.target.closest(".kfs-kopf");
  if (!kopf) return;
  var box = kopf.parentElement;
  box.classList.toggle("auf");
  kfOffen[box.getAttribute("data-i")] = box.classList.contains("auf");
});
document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") {
    document.getElementById("kf-voll").classList.remove("auf");
    document.getElementById("sp-voll").classList.remove("auf");
  }
});

// ── Container & Memory ───────────────────────────────────────────────────────
function ladeSpeicher() {
  return fetch("/api/speicher")
    .then(function(r) { return r.json(); })
    .then(function(d) {
      spDaten = d;
      var aktivC = d.container.filter(function(b) { return b.aktiv; }).length;
      var aktivM = d.memory.filter(function(k) { return k.aktiv && k.eintraege.length; }).length;
      document.getElementById("sp-zahl").textContent =
        d.container.length + " Beh. (" + aktivC + " aktiv) · " + aktivM + " Kat.";
      document.getElementById("sp-container-budget").textContent =
        d.container_belegt + " / " + d.container_budget + " Zeichen";
      document.getElementById("sp-memory-budget").textContent =
        d.memory_belegt + " / " + d.memory_budget + " Zeichen";

      document.getElementById("sp-container-liste").innerHTML = d.container.length
        ? d.container.map(function(b) {
            return '<div class="sp-box' + (b.aktiv ? "" : " inaktiv") + '" data-id="' + b.id + '">' +
              '<div class="sp-box-kopf">' +
                '<input type="checkbox" class="sp-aktiv"' + (b.aktiv ? " checked" : "") + ">" +
                "<span>" + kfEsc(b.name) + "</span>" +
                '<span style="margin-left:auto;color:#2f2f3a;font-size:9px;">' +
                  b.eintraege.length + " Einträge</span>" +
                '<span class="weg sp-box-weg" style="cursor:pointer;color:#4a3040;">✕</span>' +
              "</div>" +
              (b.eintraege.length
                ? b.eintraege.map(function(e) {
                    return '<div class="sp-eintrag" data-eid="' + e.id + '"><span>' +
                      kfEsc(e.text) + (e.kommentar ? " <i>(" + kfEsc(e.kommentar) + ")</i>" : "") +
                      '</span><span class="weg">✕</span></div>';
                  }).join("")
                : '<div class="sp-leer">leer</div>') +
              '<div class="sp-eintrag-add"><input type="text" placeholder="Eintrag…">' +
                '<button type="button">+</button></div>' +
            "</div>";
          }).join("")
        : '<div class="sp-leer">noch kein Behälter angelegt</div>';

      document.getElementById("sp-memory-liste").innerHTML = d.memory.map(function(k) {
        return '<div class="sp-box' + (k.aktiv ? "" : " inaktiv") + '" data-key="' + k.key + '">' +
          '<div class="sp-box-kopf">' +
            '<input type="checkbox" class="sp-aktiv"' + (k.aktiv ? " checked" : "") + ">" +
            "<span>" + kfEsc(k.label) + "</span>" +
            '<span style="margin-left:auto;color:#2f2f3a;font-size:9px;">' +
              k.eintraege.length + "</span>" +
          "</div>" +
          (k.eintraege.length
            ? k.eintraege.map(function(t) {
                return '<div class="sp-eintrag"><span>' + kfEsc(t) +
                       '</span><span class="weg">✕</span></div>';
              }).join("")
            : '<div class="sp-leer">leer</div>') +
          '<div class="sp-eintrag-add"><input type="text" placeholder="merken…">' +
            '<button type="button">+</button></div>' +
        "</div>";
      }).join("");
    });
}

function spSenden(pfad, koerper) {
  return fetch("/api/speicher" + pfad, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(koerper || {})
  }).then(function() { return ladeSpeicher(); }).then(function() { ladeKontext(); });
}

document.getElementById("sp").addEventListener("click", function() {
  document.getElementById("sp-voll").classList.add("auf");
  ladeSpeicher(); ladeGedankenfeld(); ladeGeschichten();
});
document.getElementById("sp-voll-zu").addEventListener("click", function() {
  document.getElementById("sp-voll").classList.remove("auf");
});
document.getElementById("sp-neu-btn").addEventListener("click", function() {
  var feld = document.getElementById("sp-neuer-name");
  if (!feld.value.trim()) return;
  spSenden("/container/neu", { name: feld.value.trim() });
  feld.value = "";
});
document.getElementById("sp-suche").addEventListener("input", function() {
  var q = this.value.trim();
  var ziel = document.getElementById("sp-treffer");
  if (!q) { ziel.innerHTML = '<span class="sp-leer">nichts gesucht</span>'; return; }
  fetch("/api/speicher/suche?q=" + encodeURIComponent(q))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      ziel.innerHTML = d.anzahl
        ? d.treffer.map(function(t) {
            return "<div><b>" + kfEsc(t.kategorie) + "</b> " +
                   (t.aktiv ? "" : "<i>(inaktiv)</i> ") + kfEsc(t.text) + "</div>";
          }).join("")
        : '<span class="sp-leer">kein Treffer</span>';
    });
});
document.getElementById("sp-voll-inhalt").addEventListener("click", function(e) {
  var box = e.target.closest(".sp-box");
  if (!box) return;
  var istMemory = box.hasAttribute("data-key");
  var kennung = istMemory ? box.getAttribute("data-key") : box.getAttribute("data-id");

  if (e.target.classList.contains("sp-aktiv")) {
    spSenden((istMemory ? "/memory/" : "/container/") + kennung + "/aktiv",
             { aktiv: e.target.checked });
  } else if (e.target.classList.contains("sp-box-weg")) {
    spSenden("/container/" + kennung + "/entfernen");
  } else if (e.target.classList.contains("weg")) {
    var zeile = e.target.closest(".sp-eintrag");
    if (istMemory) {
      spSenden("/memory/" + kennung + "/entfernen",
               { text: zeile.querySelector("span").textContent });
    } else {
      spSenden("/container/" + kennung + "/eintrag/" +
               zeile.getAttribute("data-eid") + "/entfernen");
    }
  } else if (e.target.tagName === "BUTTON") {
    var feld = e.target.previousElementSibling;
    if (!feld || !feld.value.trim()) return;
    var text = feld.value.trim();
    spSenden((istMemory ? "/memory/" + kennung + "/eintrag"
                        : "/container/" + kennung + "/eintrag"), { text: text });
  }
});

// ── Geschichten ───────────────────────────────────────────────────────────────
function ladeGeschichten() {
  return fetch("/api/geschichten")
    .then(function(r) { return r.json(); })
    .then(function(d) {
      document.getElementById("ge-laengen").innerHTML =
        d.laengen.map(function(l) {
          return '<button type="button" class="ge-verfassen" data-l="' + l + '">' + l + "</button>";
        }).join("");
      document.getElementById("ge-liste").innerHTML = d.geschichten.length
        ? d.geschichten.map(function(g) {
            return '<div class="sp-box' + (g.aktiv ? "" : " inaktiv") + '" data-gid="' + g.id + '">' +
              '<div class="sp-box-kopf">' +
                '<input type="checkbox" class="ge-aktiv"' + (g.aktiv ? " checked" : "") + ">" +
                "<span>" + kfEsc(g.titel) + "</span>" +
                '<span style="margin-left:auto;color:#2f2f3a;font-size:9px;">' +
                  (g.herkunft === "chatverlauf" ? "destilliert" : "eingesetzt") + "</span>" +
                '<span class="weg ge-weg">✕</span>' +
              "</div>" +
              '<div class="sp-eintrag"><span>' + kfEsc(g.text.slice(0, 400)) +
                (g.text.length > 400 ? "…" : "") + "</span></div>" +
            "</div>";
          }).join("")
        : '<div class="sp-leer">keine Geschichte</div>';
    });
}

document.getElementById("ge-einsetzen").addEventListener("click", function() {
  var t = document.getElementById("ge-titel"), x = document.getElementById("ge-text");
  if (!x.value.trim()) return;
  fetch("/api/geschichten/einsetzen", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titel: t.value.trim() || "ohne Titel", text: x.value.trim() })
  }).then(function() { t.value = ""; x.value = ""; ladeGeschichten(); ladeKontext(); });
});

document.getElementById("sp-voll-inhalt").addEventListener("click", function(e) {
  if (e.target.classList.contains("ge-verfassen")) {
    var knopf = e.target, alt = knopf.textContent;
    knopf.disabled = true; knopf.textContent = "…";
    fetch("/api/geschichten/verfassen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ laenge: parseInt(knopf.getAttribute("data-l"), 10) })
    }).then(function() { knopf.disabled = false; knopf.textContent = alt;
                         ladeGeschichten(); ladeKontext(); })
      .catch(function() { knopf.disabled = false; knopf.textContent = "fehlt"; });
    return;
  }
  var box = e.target.closest(".sp-box[data-gid]");
  if (!box) return;
  var gid = box.getAttribute("data-gid");
  if (e.target.classList.contains("ge-aktiv")) {
    fetch("/api/geschichten/" + gid + "/aktiv", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ aktiv: e.target.checked })
    }).then(function() { ladeGeschichten(); ladeKontext(); });
  } else if (e.target.classList.contains("ge-weg")) {
    fetch("/api/geschichten/" + gid + "/entfernen",
          { method: "POST" }).then(function() { ladeGeschichten(); ladeKontext(); });
  }
});

// ── Gedankenfeld ─────────────────────────────────────────────────────────────
function ladeGedankenfeld() {
  return fetch("/api/gedankenfeld")
    .then(function(r) { return r.json(); })
    .then(function(d) {
      document.getElementById("gf-zahl").textContent = d.anzahl + " · " + d.tokens + " Tok";
      document.getElementById("gf-vorschau").textContent = d.anzahl
        ? d.gedanken.slice(0, 2).map(function(g) { return g.text; }).join(" · ")
        : "leer";
      var kosten = document.getElementById("gf-kosten");
      if (kosten) {
        kosten.textContent = d.anzahl + " Gedanken · " + d.tokens + " von " +
          (d.slot_ctx || "?") + " Token · " + d.revisionen_gesamt + " Revisionen. " +
          "Nichts verfällt — nur du entfernst etwas.";
      }
      var liste = document.getElementById("gf-liste");
      if (!liste) return;
      liste.innerHTML = d.anzahl
        ? d.gedanken.map(function(g) {
            return '<div class="gfd" data-gid="' + g.id + '">' +
              '<div class="gfd-kopf">' +
                '<span class="gfd-id">' + g.id + "</span>" +
                "<span>seit " + kfEsc((g.erstellt_am || "").slice(0, 10)) + "</span>" +
                (g.aenderungen ? "<span>" + g.aenderungen + "× geändert</span>" : "") +
                '<span style="margin-left:auto;display:flex;gap:5px;">' +
                  '<button class="gfd-btn aendern-btn" type="button">ändern</button>' +
                  '<button class="gfd-btn weg-btn" type="button">entfernen</button>' +
                "</span>" +
              "</div>" +
              '<div class="gfd-text">' + kfEsc(g.text) + "</div>" +
            "</div>";
          }).join("")
        : '<div class="sp-leer">noch kein Gedanke</div>';
    });
}

document.getElementById("gf").addEventListener("click", function() {
  document.getElementById("sp-voll").classList.add("auf");
  ladeGedankenfeld(); ladeSpeicher(); ladeGeschichten();
});

document.getElementById("gf-neu-btn").addEventListener("click", function() {
  var feld = document.getElementById("gf-neu-text");
  if (!feld.value.trim()) return;
  fetch("/api/gedankenfeld/neu", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: feld.value.trim(), von: "Daniel" })
  }).then(function() { feld.value = ""; ladeGedankenfeld(); ladeKontext(); });
});

document.getElementById("gf-liste").addEventListener("click", function(e) {
  var karte = e.target.closest(".gfd");
  if (!karte) return;
  var gid = karte.getAttribute("data-gid");
  var textEl = karte.querySelector(".gfd-text");

  if (e.target.classList.contains("weg-btn")) {
    fetch("/api/gedankenfeld/" + gid + "/entfernen?von=Daniel", { method: "POST" })
      .then(function() { ladeGedankenfeld(); ladeKontext(); });
    return;
  }
  if (!e.target.classList.contains("aendern-btn")) return;

  if (textEl.getAttribute("contenteditable") === "true") {
    fetch("/api/gedankenfeld/" + gid + "/aendern", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textEl.textContent.trim(), von: "Daniel" })
    }).then(function() { ladeGedankenfeld(); ladeKontext(); });
  } else {
    textEl.setAttribute("contenteditable", "true");
    e.target.textContent = "übernehmen";
    textEl.focus();
  }
});

ladeKontext();
setInterval(ladeKontext, 10000);
ladeGedankenfeld();
ladeSpeicher();
ladeGeschichten();
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
