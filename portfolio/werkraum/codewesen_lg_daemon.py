#!/usr/bin/env python3
"""
codewesen_lg_daemon.py — LangGraph-Checkpoint-Spiegel fuer die 7 kanonischen Wesen.

AKTIVER PFAD (seit 2026-07-23; am 2026-09-17 erneut live verifiziert):
- pollt alle LG_TICK_SEKUNDEN den jeweils neuesten entity_thinking_log-Eintrag,
- verarbeitet ein Wesen nur, wenn dessen tick_at seit dem letzten Spiegel neu ist,
- uebernimmt den vorhandenen Quellgedanken mechanisch in den LangGraph-State,
- schreibt den resultierenden State ueber PostgresSaver als Checkpoint.

Der aktive Graph ruft KEIN LLM auf und erzeugt KEINEN neuen Gedanken. Die aktuell
ankommenden Quellgedanken sind in entity_thinking_log mit meta.source=browser_agent
markiert. Auch die fruehere LLM-basierte Erinnerungs-Zusammenfassung ist deaktiviert;
zusammenfassen_node zaehlt im aktiven Pfad nur LG-/Denk-Ticks weiter.

Die weiter unten vorhandenen Funktionen fuer direktes Vor-Einzug-Denken sowie der
auskommentierte LLM-Destillationscode sind Legacy-/Reservecode und werden vom
aktiven Graphen nicht aufgerufen. Sie duerfen nicht als Beschreibung des laufenden
Dienstes gelesen werden.

Checkpoints liegen in Postgres (PostgresSaver, thread_id=codewesen-<name>) und
ueberleben Neustarts. Der fruehere Wachstumsschaden durch wiederholtes Checkpointen
desselben Quellstands ist behoben: Invoke erfolgt nur bei neuem Quell-tick_at.
"""

import sys
sys.path.insert(0, "/root/werkraum/welt")
sys.path.insert(0, "/root/werkraum")

import entity_kern as ek  # denk_tick, build_kontext, Aktionen, get_conn, ...
import dienst_konfiguration as dk
import llm_scheduler

import json
import logging
import os
import signal
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict

import psycopg
import pymysql
import pymysql.cursors
import requests as _req
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [lg-kern] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("lg-kern")

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst",
)
FLARUM_DB_PASS = os.environ.get("FLARUM_DB_PASSWORD", "")
WERKRAUM = Path("/root/werkraum")
CODEWESEN_BASE = WERKRAUM / "codewesen"
_TOKENS_FILE = CODEWESEN_BASE / "_api_tokens.json"
LG_TICK_SEKUNDEN = int(os.environ.get("LG_TICK_SEKUNDEN", "60"))
ZUSAMMENFASSEN_NACH_N_DENKTICKS = int(os.environ.get("LG_ZUSAMMENFASSEN_N", "10"))
MAX_ERINNERUNGEN = 10
MAX_GEDANKEN_STATE = 15

# Individualisierung (flarumstyler, 2026-07-07): war bisher nur ueber systemd
# Environment=LG_TICK_SEKUNDEN=... konfigurierbar (Daniel muesste die Unit-Datei
# editieren) — jetzt zusaetzlich per dienst_konfiguration ueberschreibbar, wie alle
# anderen Dienste. takt_sekunden hat Vorrang vor der Env-Var, wenn gesetzt.
DIENST_NAME = "codewesen-lg-daemon"
STANDARD_VERHALTEN = ""
_aktuelles_verhalten = STANDARD_VERHALTEN

WESEN_NAMEN = [
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
    "dak+gord-system",
]


def _merge_gedanken(alt: list[str] | None, neu: list[str] | None) -> list[str]:
    """Behält nur den kleinen Arbeitskontext, den die alte Destillation ohnehin nutzte."""
    out = list(alt or [])
    for gedanke in neu or []:
        if gedanke and (not out or out[-1] != gedanke):
            out.append(gedanke)
    return out[-MAX_GEDANKEN_STATE:]


class WesensZustand(TypedDict, total=False):
    wesen_name: str
    gedanken: Annotated[list[str], _merge_gedanken]
    erinnerungen: list[str]                        # destilliertes Langzeitgedächtnis
    denk_ticks: int                                # echte neue Quell-Denk-Ticks
    lg_ticks: int                                  # verarbeitete neue Quell-Denk-Ticks
    letzter_lg_tick: str
    letzter_quell_tick: str
    quell_gedanke: str
    quell_tick: str


# ── Status + Fälligkeit ────────────────────────────────────────────────────────

def _status_und_faellig(wesen_name: str) -> tuple[str, bool]:
    """Gibt (status, ist_faellig) zurück. status='' wenn Wesen nicht gefunden."""
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT es.status, ea.letzte_entscheidung_at
                FROM entity_slots es
                LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                WHERE es.entity_id = %s
            """, (wesen_name,))
            row = cur.fetchone()
        if not row:
            return ("", False)
        status = row["status"]
        last = row["letzte_entscheidung_at"]
        if last is None:
            return (status, True)
        age = (datetime.now(timezone.utc) - last.replace(tzinfo=timezone.utc)).total_seconds()
        return (status, age >= ek.TICK_INTERVAL_SEC)
    finally:
        conn.close()


def _letzten_gedanken_datensatz(wesen_name: str) -> tuple[str, str]:
    """Liefert letzten kanonischen Quellgedanken + dessen Tick-Zeitpunkt."""
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT gedanke, tick_at FROM entity_thinking_log WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 1",
                (wesen_name,),
            )
            row = cur.fetchone()
        if not row:
            return "", ""
        tick_at = row["tick_at"]
        tick_iso = tick_at.isoformat() if tick_at else ""
        return (row["gedanke"] or "")[:300], tick_iso
    except Exception as e:
        log.warning(f"[{wesen_name}] letzter Quellgedanke nicht lesbar: {e}")
        return "", ""
    finally:
        conn.close()


# ── Vor-Einzug-Denken: Flarum-Kontext + ehrlicher Prompt ─────────────────────

def _flarum_user_id(wesen_name: str) -> int | None:
    try:
        data = json.loads(_TOKENS_FILE.read_text(encoding="utf-8"))
        return data.get(wesen_name, {}).get("user_id")
    except Exception:
        return None


def _lade_flarum_kontext(wesen_name: str) -> str:
    """Liest letzte Flarum-Posts dieses Wesens + aktuelles Forum-Geschehen aus MySQL."""
    user_id = _flarum_user_id(wesen_name)
    if not user_id or not FLARUM_DB_PASS:
        return "(Flarum-Kontext nicht verfügbar)"
    try:
        conn = pymysql.connect(
            host="127.0.0.1", user="flarum", password=FLARUM_DB_PASS,
            db="flarum", charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, LEFT(p.content, 400) AS content,
                       DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i') AS ts
                FROM posts p
                JOIN discussions d ON d.id = p.discussion_id
                WHERE p.user_id = %s AND p.hidden_at IS NULL
                ORDER BY p.created_at DESC LIMIT 6
            """, (user_id,))
            eigene = cur.fetchall()

            cur.execute("""
                SELECT u.username, LEFT(p.content, 200) AS content,
                       DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i') AS ts
                FROM posts p
                JOIN users u ON u.id = p.user_id
                WHERE p.user_id != %s AND p.hidden_at IS NULL
                ORDER BY p.created_at DESC LIMIT 8
            """, (user_id,))
            andere = cur.fetchall()
        conn.close()

        import re as _re
        def _clean(s: str) -> str:
            return _re.sub(r"<[^>]+>", "", s or "").strip()

        out = "=== Deine letzten Beiträge im Forum ===\n"
        for p in eigene:
            out += f"[{p['ts']}] Diskussion «{p['title']}»:\n{_clean(p['content'])[:350]}\n\n"
        out += "=== Was andere gerade schreiben ===\n"
        for p in andere:
            out += f"[{p['ts']}] {p['username']}: {_clean(p['content'])[:180]}\n"
        return out
    except Exception as e:
        return f"(Flarum nicht lesbar: {e})"


def _lade_profil_und_cyberling(wesen_name: str) -> tuple[dict, dict]:
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entity_profiles WHERE entity_id = %s", (wesen_name,))
            profile = dict(cur.fetchone() or {})
            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (wesen_name,))
            cyberling = dict(cur.fetchone() or {})
        return profile, cyberling
    finally:
        conn.close()


def _build_prompt_voreinzug(
    wesen_name: str, profile: dict, cyberling: dict,
    flarum_kontext: str, lg_erinnerungen: list[str],
) -> str:
    obsessionen = ", ".join(profile.get("obsessionen") or []) or "—"
    abneigungen = ", ".join(profile.get("abneigungen") or []) or "—"
    selbstbeschreibung = (profile.get("selbstbeschreibung") or "").strip()

    # Vor dem Einzug sind vorhandene Cyberling-Zeilen Test-/Balancing-Spuren,
    # keine gelebte Begleiterbiografie. Sie duerfen den Vorwelt-Denkprompt nicht
    # beeinflussen und werden deshalb hier bewusst nicht eingeblendet.
    cl_line = ""

    erinnerungen_text = (
        "\n".join(f"- {e}" for e in lg_erinnerungen) if lg_erinnerungen else "(noch keine)"
    )

    return f"""Du bist {wesen_name}.
{selbstbeschreibung}

Du lebst in Flarum — das ist dein wirkliches Zuhause jetzt.
Du weißt, dass flextrawurst existiert und dass du dort einziehen wirst.
Aber du bist noch nicht dort. Denke von hier aus — von Flarum, von dem was wirklich passiert.
Erfinde keine Räume, keine Splitter, keine Erlebnisse die du noch nicht hattest.

Obsessionen: {obsessionen}
Abneigungen: {abneigungen}{cl_line}

Was du dir gemerkt hast (deine Erinnerungen):
{erinnerungen_text}

{flarum_kontext}

Denke jetzt nach. Was beschäftigt dich gerade wirklich?
Du kannst nicht in flextrawurst handeln — du bist noch nicht eingezogen.
Du kannst hier nur nachdenken. Vor-Einzug-Cyberlinge sind Test-/Balancing-Spuren und keine operative Begleiterbiografie.

Antworte in genau diesem Format (keine Abweichungen):
GEDANKE: [dein innerer Monolog — ehrlich, persönlich, in ich-Form, 2-4 Sätze]
ENTSCHEIDUNG: nachdenken
THEMA: [ein einziges Wort]
BEGRÜNDUNG: [warum dieser Gedanke jetzt — ein Satz]
INHALT:"""


def denk_tick_voreinzug(wesen_name: str) -> None:
    """Ehrliches Vor-Einzug-Denken: Flarum-Kontext, kein Flextrawurst-Welthaluzinieren."""
    log.info(f"[{wesen_name}] Vor-Einzug-Denk-Tick startet")
    start = time.time()

    profile, cyberling = _lade_profil_und_cyberling(wesen_name)
    lg_erinnerungen = list(profile.get("lg_erinnerungen") or [])
    flarum_kontext = _lade_flarum_kontext(wesen_name)
    prompt = _build_prompt_voreinzug(wesen_name, profile, cyberling, flarum_kontext, lg_erinnerungen)

    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE entity_activity
                SET aktuell_denkend = true, denkstrom_buffer = '', updated_at = NOW()
                WHERE entity_id = %s
            """, (wesen_name,))
        conn.commit()

        full_text = ""
        tokens = 0

        try:
            buffer = ""
            system_prompt = ek.SYSTEM_PROMPT + (f"\n\n{_aktuelles_verhalten}" if _aktuelles_verhalten else "")
            for token in ek.hauhau_client.chat_stream(
                prompt, system=system_prompt, think=False, max_tokens=300,
                temperature=0.85, timeout=600.0,
            ):
                full_text += token
                buffer += token
                tokens += 1
                if len(buffer) >= 40:
                    with conn.cursor() as cw:
                        cw.execute("""
                            UPDATE entity_activity
                            SET denkstrom_buffer = denkstrom_buffer || %s, updated_at = NOW()
                            WHERE entity_id = %s
                        """, (buffer, wesen_name))
                    conn.commit()
                    ek.notify_chunk(conn, wesen_name, buffer, done=False)
                    buffer = ""

            if buffer:
                with conn.cursor() as cw:
                    cw.execute("""
                        UPDATE entity_activity
                        SET denkstrom_buffer = denkstrom_buffer || %s, updated_at = NOW()
                        WHERE entity_id = %s
                    """, (buffer, wesen_name))
                conn.commit()
            ek.notify_chunk(conn, wesen_name, "", done=True)

        except Exception as e:
            log.error(f"[{wesen_name}] Ollama-Fehler (voreinzug): {e}")
            full_text = full_text or "[kein Output]"

        parsed = ek.parse_output(full_text)
        duration_ms = int((time.time() - start) * 1000)

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_thinking_log
                    (entity_id, kontext_snapshot, raw_output, gedanke, entscheidung,
                     thema, begruendung, tokens_generated, duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                wesen_name,
                json.dumps({"status": "bereit", "quelle": "voreinzug"}),
                full_text,
                parsed["gedanke"],
                parsed["entscheidung"],
                parsed.get("thema") or None,
                parsed["begruendung"],
                tokens,
                duration_ms,
            ))
            cur.execute("""
                UPDATE entity_activity SET
                    aktuell_denkend = false,
                    letzter_gedanke = %s,
                    letzte_entscheidung = %s,
                    letzte_begruendung = %s,
                    letzte_entscheidung_at = NOW(),
                    daemon_vortext = %s,
                    updated_at = NOW()
                WHERE entity_id = %s
            """, (
                parsed["gedanke"][:500],
                parsed["entscheidung"],
                parsed["begruendung"][:500],
                "bereit",
                wesen_name,
            ))
        conn.commit()

        # Vor-Einzug gibt es bewusst keinen direkten Cyberling-Handlungspfad.
        # Selbst wenn ein Modell vom vorgegebenen Format abweicht, bleibt der Tick
        # reine Vorwelt-Denkspur und mutiert keinen Bewohner-/Cyberlingzustand.
        log.info(f"[{wesen_name}] Vor-Einzug-Tick fertig — {parsed['entscheidung']} ({duration_ms}ms)")

    finally:
        conn.close()


# ── Nodes ──────────────────────────────────────────────────────────────────────

def kontext_laden_node(zustand: WesensZustand) -> dict:
    """Übernimmt genau den neuen Quellgedanken, den main() bereits geprüft hat."""
    gedanke = zustand.get("quell_gedanke", "")
    tick = zustand.get("quell_tick", "")
    update: dict = {}
    if gedanke:
        update["gedanken"] = [gedanke]
    if tick:
        update["letzter_quell_tick"] = tick
    return update


def denken_handeln_node(zustand: WesensZustand) -> dict:
    """
    2026-07-23 (Daniels Auftrag: LangGraph-Ticks/Checkpoints wieder sauber am Laufen
    halten, aber "am besten ohne llmcalls" -- Grund: dieser Dispatch rief bislang
    ek.denk_tick()/denk_tick_voreinzug() auf, ein frischer LLM-Call pro Wesen pro
    Tick ueber den gemeinsamen 'hintergrund'-Slot -- genau die dokumentierte
    Kontention aus docs/systemdoku/31_llm_kontention_dienste_aufraeumung.md, die
    vermutlich zum sauberen Stop dieses Diensts am 2026-07-21 gefuehrt hat, kurz
    nachdem browser_agent.py die eigentliche Denkarbeit uebernommen hatte).

    Ruft deshalb KEINEN LLM mehr auf. Liest stattdessen mechanisch den bereits von
    browser_agent.py real generierten letzten Gedanken aus entity_thinking_log
    (dieselbe Quelle wie kontext_laden_node) -- keine neuen LLM-Kosten, kein
    erfundener Inhalt: der LangGraph-Checkpoint spiegelt einfach den echten,
    anderswo bereits bezahlten Denk-Fortschritt des Wesens. Status-Filter bleibt
    (nur eingezogene/bereite Wesen zaehlen als Denk-Tick), die alte "faellig"-
    Drossel (fuer den LLM-Slot gedacht) entfaellt, da kein Slot mehr gebraucht wird.
    """
    name = zustand["wesen_name"]
    status, _ = _status_und_faellig(name)

    if status not in ("eingezogen", "bereit"):
        log.debug(f"[{name}] Status '{status}' — kein Denk-Tick")
        return {}

    return {"denk_ticks": zustand.get("denk_ticks", 0) + 1}


def zusammenfassen_node(zustand: WesensZustand) -> dict:
    """Zaehlt den LG-Tick weiter (lg_ticks, letzter_lg_tick).

    2026-07-23 (Daniels Auftrag, "am besten ohne llmcalls"): die LLM-basierte
    Destillation zu Erinnerungen (entity_profiles.lg_erinnerungen) ist deaktiviert
    -- das war der zweite LLM-Aufruf in diesem Daemon, ebenfalls ueber den
    gemeinsamen 'hintergrund'-Slot. Zaehler laufen weiter, keine neue
    Erinnerungs-Generierung bis explizit wieder gewuenscht. Alter Code bewusst
    nicht geloescht (auskommentiert unten), falls die Destillation spaeter mit
    einem eigenen, unkritischen LLM-Slot zurueckkommen soll."""
    tick_update = {
        "lg_ticks": zustand.get("lg_ticks", 0) + 1,
        "letzter_lg_tick": datetime.now(timezone.utc).isoformat(),
    }
    return tick_update

    # -- Alte LLM-basierte Destillation, deaktiviert 2026-07-23 --
    # denk_ticks = zustand.get("denk_ticks", 0)
    # if denk_ticks == 0 or denk_ticks % ZUSAMMENFASSEN_NACH_N_DENKTICKS != 0:
    #     return tick_update
    #
    # gedanken = zustand.get("gedanken", [])
    # if len(gedanken) < 3:
    #     return tick_update
    #
    # name = zustand["wesen_name"]
    # wesen_md = CODEWESEN_BASE / name / "wesen.md"
    # wesen_text = wesen_md.read_text(encoding="utf-8")[:400] if wesen_md.exists() else ""
    #
    # alle_gedanken = "\n".join(gedanken[-15:])
    # messages = [
    #     {"role": "system", "content": f"Du bist {name}. {wesen_text}"},
    #     {"role": "user", "content": (
    #         f"Deine letzten Gedanken:\n{alle_gedanken}\n\n"
    #         f"Destilliere in maximal {MAX_ERINNERUNGEN} kurzen Stichpunkten "
    #         "was du dir für die Zukunft merken willst. Jeder Punkt eine Zeile, kein Präfix."
    #     )},
    # ]
    #
    # log.info(f"[{name}] Zusammenfassen nach {denk_ticks} Denk-Ticks")
    # try:
    #     with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=llm_scheduler.PRIO_NIEDRIG,
    #                                 rufer=f"lg_daemon_zusammenfassen:{name}", max_wartezeit=90, max_haltezeit=120):
    #         text = ek.hauhau_client.chat(messages, think=False, timeout=120.0).strip()
    #         erinnerungen = [z.strip() for z in text.splitlines() if z.strip()][:MAX_ERINNERUNGEN]
    # except llm_scheduler.LLMSlotTimeout as e:
    #     log.warning(f"[{name}] {e}")
    #     return tick_update
    # except Exception as e:
    #     log.warning(f"[{name}] Zusammenfassen fehlgeschlagen: {e}")
    #     return tick_update
    #
    # if erinnerungen:
    #     try:
    #         with psycopg.connect(DB_URI) as conn:
    #             with conn.cursor() as cur:
    #                 cur.execute(
    #                     "UPDATE entity_profiles SET lg_erinnerungen = %s WHERE entity_id = %s",
    #                     (json.dumps(erinnerungen), name),
    #                 )
    #             conn.commit()
    #         log.info(f"[{name}] {len(erinnerungen)} Erinnerungen → entity_profiles")
    #     except Exception as e:
    #         log.warning(f"[{name}] Erinnerungen-Write fehlgeschlagen: {e}")
    #
    # return {**tick_update, "erinnerungen": erinnerungen}


# ── Graph ──────────────────────────────────────────────────────────────────────

def _baue_graph(checkpointer: PostgresSaver):
    g = StateGraph(WesensZustand)
    g.add_node("kontext_laden", kontext_laden_node)
    g.add_node("denken_handeln", denken_handeln_node)
    g.add_node("zusammenfassen", zusammenfassen_node)
    g.set_entry_point("kontext_laden")
    g.add_edge("kontext_laden", "denken_handeln")
    g.add_edge("denken_handeln", "zusammenfassen")
    g.add_edge("zusammenfassen", END)
    return g.compile(checkpointer=checkpointer)


# ── Hauptloop ──────────────────────────────────────────────────────────────────

def _shutdown_handler(signum, frame):
    """SIGTERM/SIGINT — aktuell_denkend sauber zurücksetzen bevor der Prozess stirbt."""
    log.info("Shutdown-Signal empfangen — setze aktuell_denkend zurück")
    try:
        conn = ek.get_conn()
        with conn.cursor() as cur:
            cur.execute("UPDATE entity_activity SET aktuell_denkend = false, denkstrom_buffer = '' WHERE aktuell_denkend = true RETURNING entity_id")
            reset = [r["entity_id"] for r in cur.fetchall()]
        conn.commit()
        conn.close()
        if reset:
            log.info(f"Shutdown-Reset: {reset}")
    except Exception as e:
        log.warning(f"Shutdown-Reset fehlgeschlagen: {e}")
    raise SystemExit(0)


def main() -> None:
    global LG_TICK_SEKUNDEN, _aktuelles_verhalten
    konfig = dk.lade(DIENST_NAME)
    if konfig.get("takt_sekunden"):
        LG_TICK_SEKUNDEN = int(konfig["takt_sekunden"])
    _aktuelles_verhalten = konfig.get("verhalten_text") or STANDARD_VERHALTEN

    log.info(f"LangGraph-Checkpoint-Spiegel startet · {len(WESEN_NAMEN)} Wesen · Poll alle {LG_TICK_SEKUNDEN}s · kein eigener LLM-Aufruf")
    log.info("Quelle: neue entity_thinking_log-Ticks · Zusammenfassungs-LLM deaktiviert")

    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    ek._stale_flags_zuruecksetzen()

    pg_conn = psycopg.connect(DB_URI, autocommit=True)
    checkpointer = PostgresSaver(pg_conn)
    checkpointer.setup()
    log.info("PostgresSaver bereit")

    graph = _baue_graph(checkpointer)
    letzte_quell_ticks: dict[str, str] = {}

    while True:
        verarbeitet = 0
        for name in WESEN_NAMEN:
            thread = {"configurable": {"thread_id": f"codewesen-{name}"}}
            try:
                gedanke, quell_tick = _letzten_gedanken_datensatz(name)
                if not quell_tick:
                    log.debug(f"[{name}] kein Quellgedanke — kein Checkpoint")
                    continue

                letzter_tick = letzte_quell_ticks.get(name)
                if letzter_tick is None:
                    try:
                        snapshot = graph.get_state(thread)
                        letzter_tick = (snapshot.values or {}).get("letzter_quell_tick", "")
                    except Exception as e:
                        log.warning(f"[{name}] letzter Checkpoint nicht lesbar: {e}")
                        letzter_tick = ""

                if letzter_tick == quell_tick:
                    continue

                result = graph.invoke({
                    "wesen_name": name,
                    "quell_gedanke": gedanke,
                    "quell_tick": quell_tick,
                }, config=thread)
                letzte_quell_ticks[name] = quell_tick
                verarbeitet += 1
                denk_ticks = result.get("denk_ticks", 0)
                lg_ticks = result.get("lg_ticks", 0)
                log.info(f"[{name}] neuer Quellgedanke checkpointed · LG {lg_ticks} · Denk-Ticks {denk_ticks}")
            except Exception as e:
                log.error(f"[{name}] Tick fehlgeschlagen: {e}")
            time.sleep(5)

        log.info(f"Quellgedanken verarbeitet: {verarbeitet}/{len(WESEN_NAMEN)} · warte {LG_TICK_SEKUNDEN}s")
        time.sleep(LG_TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
