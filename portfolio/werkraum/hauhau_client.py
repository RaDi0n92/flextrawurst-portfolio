"""
Zentraler Client fuer hauhaucs (llama-server, Port 11436, OpenAI-Format).
Ersetzt direkte Ollama-Aufrufe (Port 11434) in allen Codewesen-/GENI-/welt-Skripten.

Getestet gegen: llama-hauhaucs-hintergrund.service (Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive, Q6_K_P).
enable_thinking wird ueber chat_template_kwargs gesteuert (per Request, kein Server-Neustart noetig).
images: Liste von rohen Base64-Strings (jpeg), werden als OpenAI image_url Content-Parts angehaengt.
"""
import asyncio
import contextlib
import json
import os
import subprocess
import threading
import time
import datetime
import httpx

# 2026-07-23 Daniel-Entscheidung nach einem echten Vorfall: die separate
# Chat-Instanz (frueher llama-hauhaucs.service, Port 11435) sollte laut altem
# Kommentar hier nur "~1GB Mehrkosten" durch mmap-Sharing verursachen -- real
# hat sie den Server mit ~60GB RAM-Bedarf fuer zwei volle 35B-Modelle fast
# lahmgelegt (487MB frei, 31GB im Swap, praktisch alles haengte). Daniel,
# woertlich: "so wie es bei dakgordsystem im chat immer war" -- zurueck zu
# EINEM geladenen Modell (Hintergrund-Instanz, Port 11436) fuer alles.
# Chat-Prioritaet kommt jetzt wieder ueber einen aktiven Waechter-Mechanismus
# statt ueber einen physisch getrennten zweiten Prozess -- gleiches Prinzip
# wie web_chat.py's _ollama_waechter fuer dak+gord (dort unangetastet, eigener
# funktionierender Ollama-Mechanismus), hier zentral fuer alle hauhau_client-
# Nutzer: Zensi, Codewesen-Chat, GENI, Codexium/SolarIUS (hauhau_client.ts).
LLAMA_URL_HINTERGRUND = "http://localhost:11436/v1/chat/completions"
# 2026-08-04, nach einem LIVE-Test (nicht nach einer Rechnung -- Daniel dazu:
# "rechnung bringt nix können wir erst dokumentieren wenn wir es live testen"):
# der Chat hat wieder eine eigene Instanz auf 11435.
#
# Warum das diesmal traegt, obwohl es am 23.07. schiefging: damals liefen beide
# Instanzen mit --cache-ram 16384 bzw. 12288, zusammen 28 GB Prompt-Cache --
# mehr als das Modell selbst. Gemessen wurde inzwischen: dieser Cache hat bei
# 1232 Speicherungen exakt 0 Ladevorgaenge (Hybrid-Bug llama.cpp #24055) und
# lag komplett im Swap. Beide Units laufen jetzt mit --cache-ram 0.
#
# Live gemessen mit zwei laufenden Instanzen (siehe docs/systemdoku/31):
#   Mlocked bleibt 28,56 GB -- die Modellgewichte werden geteilt, auch beim mlock
#   MemAvailable faellt nur um 1,38 GB
#   die zweite Instanz liefert stabil 9,5-13,0 tok/s, mit und ohne Parallellast
#
# 2026-08-21: Chat-Instanz (Port 11435) laeuft jetzt auf einem anderen Modell
# als die Hintergrund-Instanz (Nemotron 3 Nano PRISM 30B-A3B Q8_0 statt
# hauhaucs-q6) -- die obige mmap-Sharing-Rechnung gilt deshalb nicht mehr,
# beide Modelle sind unterschiedliche Dateien und belegen RAM additiv. Kein
# Vision-mmproj fuer dieses Modell verfuegbar -- images= geht an diese
# Instanz zwar weiterhin durch, wird vom Modell aber nicht ausgewertet.
LLAMA_URL_CHAT = "http://localhost:11435/v1/chat/completions"

# Der Prioritaets-Waechter stoppte Hintergrunddienste, damit der Chat einen der
# zwei geteilten Slots bekam. Mit einer eigenen Chat-Instanz ist das nicht mehr
# noetig -- und es war ohnehin wirkungslos: von den 19 gelisteten Units ist eine
# aktiv, 16 disabled, 2 masked, und die sieben tatsaechlich rechnenden
# browser-agent@-Dienste stehen gar nicht darauf. Auf False kostet jeder
# Chat-Aufruf 1 Sekunde weniger. Auf True zurueckdrehen, falls der Chat je
# wieder auf der Hintergrund-Instanz landet.
WAECHTER_AKTIV = False

# Abbrechbarkeit fuer synchrone LLM-Aufrufe (urspruenglich 2026-09-02 nur chat_stream()).
# Laufende chat()/chat_stream()-Requests tragen ihren httpx.Client unter der Thread-ID ein;
# abbreche_stream(thread_id) bleibt als kompatibler Name erhalten und kann beide Formen
# unterbrechen — auch waehrend auf die ersten Response-Headers gewartet wird.
_AKTIVE_STREAMS: dict[int, "httpx.Client"] = {}


def abbreche_stream(thread_id: int) -> bool:
    """Bricht einen laufenden synchronen chat()/chat_stream()-Request des Threads ab.
    Gibt True zurueck wenn dort tatsaechlich etwas lief und geschlossen wurde, sonst False."""
    client = _AKTIVE_STREAMS.get(thread_id)
    if client is None:
        return False
    try:
        client.close()
    except Exception:
        pass
    return True
# 2026-08-21: Chat und Hintergrund laufen seitdem auf unterschiedlichen
# Modellen (siehe Kommentar bei LLAMA_URL_CHAT) -- deshalb zwei Konstanten
# statt einer, je nach Ziel-URL in _build_payload gewaehlt.
MODEL_CHAT = "hauhaucs-q6"
MODEL_HINTERGRUND = "hauhaucs-q6"

# Gleiche Liste wie _SYSTEMD_BLOCKER in web_chat.py -- bewusst dupliziert statt
# importiert (kein Import-Kreis, web_chat.py haengt selbst nicht von hier ab
# fuer diese Liste). Bei Aenderungen an einer Stelle auch die andere pflegen.
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

_PRIORITAETS_LOCK = threading.Lock()
_AKTIVE_CHATS = 0
_VORHER_AKTIV_MERKEN: list = []


def _dienste_parallel(aktion: str, dienste: list) -> None:
    procs = [
        subprocess.Popen(["systemctl", aktion, d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for d in dienste
    ]
    for p in procs:
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()


class _PrioritaetsWache:
    """Context-Manager: stoppt beim ersten gleichzeitigen Chat-Aufruf die
    bekannten Hintergrund-Konkurrenten der einen llama-server-Instanz, wartet
    kurz, startet erst wieder wenn der LETZTE gleichzeitige Chat-Aufruf fertig
    ist. Referenz-gezaehlt ueber Modul-globale Variablen (nicht Instanz-
    Attribute) -- sonst wuerde bei ueberlappenden Aufrufen die urspruenglich
    gemerkte "vorher aktiv"-Liste beim falschen __exit__ verloren gehen."""

    def __enter__(self):
        global _AKTIVE_CHATS, _VORHER_AKTIV_MERKEN
        with _PRIORITAETS_LOCK:
            _AKTIVE_CHATS += 1
            if _AKTIVE_CHATS == 1:
                _VORHER_AKTIV_MERKEN = [
                    d for d in _SYSTEMD_BLOCKER
                    if subprocess.run(["systemctl", "is-active", d], capture_output=True).returncode == 0
                ]
                _dienste_parallel("stop", _SYSTEMD_BLOCKER)
                time.sleep(1.0)
        return self

    def __exit__(self, *exc):
        global _AKTIVE_CHATS, _VORHER_AKTIV_MERKEN
        with _PRIORITAETS_LOCK:
            _AKTIVE_CHATS = max(0, _AKTIVE_CHATS - 1)
            if _AKTIVE_CHATS == 0 and _VORHER_AKTIV_MERKEN:
                _dienste_parallel("start", _VORHER_AKTIV_MERKEN)
                _VORHER_AKTIV_MERKEN = []
        return False


class _APrioritaetsWache:
    """Async-Variante von _PrioritaetsWache fuer achat/achat_stream -- fuehrt
    die blockierenden systemctl-Aufrufe in einem Thread aus (asyncio.to_thread),
    damit der Event-Loop waehrenddessen nicht haengt."""

    async def __aenter__(self):
        self._wache = _PrioritaetsWache()
        await asyncio.to_thread(self._wache.__enter__)
        return self

    async def __aexit__(self, *exc):
        await asyncio.to_thread(self._wache.__exit__, *exc)
        return False

# Leichtgewichtiges Trace-Log fuer Slot-0-Anfragen (Chat-Prioritaet) — getrennt von den schweren
# Chat-Verlaeufen, damit ein Haenger auf Slot 0 sofort einer Quelle (Datei/Charakter) zugeordnet
# werden kann. Ausgeloest 2026-07-06: zwei Haenger konnten trotz gruendlicher Recherche (alle
# Chat-Endpunkte, alle Logs, alle Dateizeiten geprueft) nicht zurueckverfolgt werden.
CHAT_PRIORITAET_TRACE = "/root/werkraum/_shared/chat_prioritaet_trace.jsonl"


def trace_prioritaet(quelle, zeichen):
    """Von den Chat-Endpunkten VOR jedem id_slot=0-Aufruf zu rufen — quelle z.B.
    'codewesen_chat:Schorschel', zeichen = Laenge des gesendeten Prompts."""
    try:
        with open(CHAT_PRIORITAET_TRACE, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "quelle": quelle, "zeichen": zeichen, "pid": os.getpid(),
            }) + "\n")
    except Exception:
        pass


def _normalize_messages(prompt_or_messages, system, images=None):
    if isinstance(prompt_or_messages, str):
        base = [{"role": "system", "content": system}] if system else []
        messages = base + [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = list(prompt_or_messages)
        if system:
            messages = [{"role": "system", "content": system}] + messages

    if images:
        letzte = dict(messages[-1])
        text = letzte.get("content", "")
        content = [{"type": "text", "text": text}] if text else []
        for b64 in images:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        letzte["content"] = content
        messages = messages[:-1] + [letzte]

    return messages


def _build_payload(messages, stream, think, max_tokens, temperature, top_p, top_k, min_p,
                    presence_penalty, dry_multiplier, extra):
    """Gibt (payload, url, ist_chat) zurueck. `id_slot=0` explizit in extra =>
    Live-Chat => Prioritaets-Wache greift beim Aufruf (siehe _PrioritaetsWache).
    ist_chat wird aus `extra` (den vom Aufrufer tatsaechlich uebergebenen
    kwargs) berechnet -- id_slot geht nie ins ausgehende Payload (siehe unten),
    darum kann es auch nicht aus dem fertigen payload zurueckgelesen werden.

    2026-07-23 Fund beim Testen der neuen Ein-Instanz-Architektur: ein
    explizites "id_slot" im HTTP-Payload laesst DIESEN llama-server (Port
    11436, --parallel 2) komplett haengen -- egal ob id_slot=0 oder 1, egal
    ob stream=true/false, reproduziert pur mit curl ohne jeden Python-Code
    drumherum. Frueher war id_slot=0 fuers Routing zur eigenen Chat-Instanz
    (Port 11435) noetig -- das gibt es nicht mehr, der Parameter geht deshalb
    NIE mehr ins ausgehende Payload, nur noch intern fuer ist_chat/die Wache."""
    ist_chat = extra.get("id_slot") == 0
    payload = {
        "model": MODEL_CHAT if ist_chat else MODEL_HINTERGRUND,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "min_p": min_p,
        "presence_penalty": presence_penalty,
        "dry_multiplier": dry_multiplier,
        "chat_template_kwargs": {"enable_thinking": think},
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    extra_ohne_id_slot = {k: v for k, v in extra.items() if k != "id_slot"}
    payload.update(extra_ohne_id_slot)
    url = LLAMA_URL_CHAT if ist_chat else LLAMA_URL_HINTERGRUND
    return payload, url, ist_chat


def _parse_sse_line(line):
    if not line or not line.startswith("data: "):
        return None
    data = line[len("data: "):]
    if data.strip() == "[DONE]":
        return None
    chunk = json.loads(data)
    return chunk["choices"][0].get("delta", {}).get("content")


def chat_raw(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
             temperature=5.5, top_p=0.8, top_k=20, min_p=0.0, presence_penalty=1.5,
             dry_multiplier=0.8, timeout=300.0, **extra) -> dict:
    """Synchroner, nicht-streamender Aufruf, gibt die volle Response als dict zurueck
    (fuer Tool-Calls / choices[0].message.tool_calls o.ae., wo mehr als content gebraucht wird)."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload, url, ist_chat = _build_payload(messages, False, think, max_tokens, temperature, top_p, top_k,
                                             min_p, presence_penalty, dry_multiplier, extra)
    with (_PrioritaetsWache() if (ist_chat and WAECHTER_AKTIV) else contextlib.nullcontext()):
        with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            return r.json()


def chat(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
         temperature=5.5, top_p=0.8, top_k=20, min_p=0.0, presence_penalty=1.5,
         dry_multiplier=0.8, timeout=300.0, **extra) -> str:
    """Synchroner, nicht-streamender Aufruf. Nimmt einen Prompt-String oder eine messages-Liste."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload, url, ist_chat = _build_payload(messages, False, think, max_tokens, temperature, top_p, top_k,
                                             min_p, presence_penalty, dry_multiplier, extra)
    with (_PrioritaetsWache() if (ist_chat and WAECHTER_AKTIV) else contextlib.nullcontext()):
        with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
            tid = threading.get_ident()
            _AKTIVE_STREAMS[tid] = client
            try:
                r = client.post(url, json=payload)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            finally:
                _AKTIVE_STREAMS.pop(tid, None)


def chat_stream(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
                temperature=5.5, top_p=0.8, top_k=20, min_p=0.0, presence_penalty=1.5,
                dry_multiplier=0.8, timeout=300.0, **extra):
    """Synchroner Generator, liefert Text-Chunks."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload, url, ist_chat = _build_payload(messages, True, think, max_tokens, temperature, top_p, top_k,
                                             min_p, presence_penalty, dry_multiplier, extra)
    with (_PrioritaetsWache() if (ist_chat and WAECHTER_AKTIV) else contextlib.nullcontext()):
        with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
            # Abbrechbarkeit (2026-09-02, Daniel-Auftrag, siehe web_chat.py): rein additiv, kein
            # bestehender Aufrufer muss davon wissen. Registriert den Client BEVOR .stream()
            # aufgerufen wird -- der eigentliche Haenger (R1ZZ1, >50 Min) trat schon beim Warten
            # auf die ersten Response-Headers auf, also innerhalb von .stream() selbst, bevor "r"
            # ueberhaupt existiert. client.close() von aussen (siehe abbreche_stream()) unterbricht
            # deshalb bewusst den Client, nicht nur das Response-Objekt -- deckt beide Phasen ab
            # (Warten auf Headers UND Lesen des Bodys).
            tid = threading.get_ident()
            _AKTIVE_STREAMS[tid] = client
            try:
                with client.stream("POST", url, json=payload) as r:
                    r.raise_for_status()
                    for line in r.iter_lines():
                        content = _parse_sse_line(line)
                        if content:
                            yield content
            finally:
                _AKTIVE_STREAMS.pop(tid, None)


async def achat(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
                 temperature=5.5, top_p=0.8, top_k=20, min_p=0.0, presence_penalty=1.5,
                 dry_multiplier=0.8, timeout=300.0, **extra) -> str:
    """Asynchroner, nicht-streamender Aufruf."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload, url, ist_chat = _build_payload(messages, False, think, max_tokens, temperature, top_p, top_k,
                                             min_p, presence_penalty, dry_multiplier, extra)
    async with (_APrioritaetsWache() if (ist_chat and WAECHTER_AKTIV) else contextlib.AsyncExitStack()):
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]


async def achat_stream(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
                        temperature=5.5, top_p=0.8, top_k=20, min_p=0.0, presence_penalty=1.5,
                        dry_multiplier=0.8, timeout=300.0, **extra):
    """Asynchroner Generator, liefert Text-Chunks."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload, url, ist_chat = _build_payload(messages, True, think, max_tokens, temperature, top_p, top_k,
                                             min_p, presence_penalty, dry_multiplier, extra)
    async with (_APrioritaetsWache() if (ist_chat and WAECHTER_AKTIV) else contextlib.AsyncExitStack()):
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
            async with client.stream("POST", url, json=payload) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    content = _parse_sse_line(line)
                    if content:
                        yield content
