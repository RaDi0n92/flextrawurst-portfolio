#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — Robuster Live Transcript & Thinking Streamer
Pfad: /root/werkraum/_gemini/windows_bridge/transcript_streamer.py

Liest kontinuierlich das aktive Antigravity-Transkript:
  /config/.gemini/antigravity-cli/brain/cbdf9ab1-af9d-4a57-ae20-5d2a074dcd33/.system_generated/logs/transcript.jsonl
Streamt:
  - Daniels Eingaben aus dem Chat [DANIEL (Chat)]
  - Gemgems Thinking [THINKING (Gemgem)]
  - Alle Tool-Aufrufe [TOOL] und Tool-Ergebnisse [TOOL_RESULT]
  - Gemgems Antworttext [GEMGEM (Antwort)]
  - Löst automatisch Raumbanner an der schwebenden Raute aus!
"""

import asyncio
import collections
import json
import logging
import os
import sys
import time
import websockets

TRANSCRIPT_PATH = "/config/.gemini/antigravity-cli/brain/cbdf9ab1-af9d-4a57-ae20-5d2a074dcd33/.system_generated/logs/transcript.jsonl"
DEFAULT_WS = os.environ.get("BRIDGE_WS_URL", "ws://127.0.0.1:9880")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] Streamer: %(message)s")
logger = logging.getLogger("TranscriptStreamer")

async def stream_transcript():
    logger.info(f"Transcript-Streamer gestartet für: {TRANSCRIPT_PATH}")
    
    last_processed_idx = -1
    
    while True:
        try:
            logger.info(f"Verbinde zu Bridge Server {DEFAULT_WS} ...")
            async with websockets.connect(DEFAULT_WS, ping_interval=None, ping_timeout=None) as ws:
                await ws.send(json.dumps({
                    "type": "register",
                    "role": "agent",
                    "name": "AntigravityTranscriptStreamer"
                }))
                await ws.recv() # Welcome
                logger.info("Verbunden mit Bridge Server! Lade Verlauf und starte Live-Streaming...")

                # Begrüßungszeile
                await ws.send(json.dumps({
                    "type": "terminal_telemetry",
                    "stream": "SYSTEM",
                    "text": "=== Antigravity 1:1 Live-Telemetrie aktiv ===",
                    "timestamp": time.time()
                }))

                # Beim ersten Verbinden: die letzten 20 Zeilen des Transkripts nachladen
                if os.path.exists(TRANSCRIPT_PATH) and last_processed_idx < 0:
                    with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="replace") as f:
                        recent_lines = collections.deque(f, maxlen=35)
                        for line in recent_lines:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                item = json.loads(line)
                                s_idx = item.get("step_index", 0)
                                if s_idx > last_processed_idx:
                                    last_processed_idx = s_idx
                                await dispatch_item(ws, item, is_backlog=True)
                            except Exception:
                                pass

                # Kontinuierliches Tailing via File-Pointer
                if os.path.exists(TRANSCRIPT_PATH):
                    with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="replace") as f:
                        # Zunächst an das Dateiende springen, wenn wir schon Initial-Backlog hatten
                        f.seek(0, os.SEEK_END)
                        while True:
                            line = f.readline()
                            if line:
                                line = line.strip()
                                if line:
                                    try:
                                        item = json.loads(line)
                                        s_idx = item.get("step_index", 0)
                                        if s_idx > last_processed_idx:
                                            last_processed_idx = s_idx
                                            await dispatch_item(ws, item, is_backlog=False)
                                    except websockets.exceptions.ConnectionClosed:
                                        raise
                                    except Exception:
                                        pass
                            else:
                                await asyncio.sleep(0.2)

        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            logger.warning(f"Socket getrennt ({e}). Reconnect in 1.5s...")
            await asyncio.sleep(1.5)
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}. Reconnect in 2s...", exc_info=True)
            await asyncio.sleep(2.0)

async def dispatch_item(ws: Any, item: dict, is_backlog: bool = False):
    step_idx = item.get("step_index", 0)
    msg_type = item.get("type", "")
    now = time.time()

    # 1. User Eingabe (Vollständig, unbeschnitten)
    if msg_type == "USER_INPUT":
        txt = item.get("content", "").strip()
        if txt:
            await ws.send(json.dumps({
                "type": "terminal_telemetry",
                "stream": "DANIEL (Chat)",
                "text": f"\n>>> [DANIEL #{step_idx}]:\n{txt}\n",
                "timestamp": now
            }))

    # 2. Agent Thinking & Tools & Content
    elif msg_type == "PLANNER_RESPONSE":
        # A) Thinking
        thinking = item.get("thinking", "")
        if thinking and not is_backlog:
            first_few = [l.strip() for l in thinking.split("\n") if l.strip()][:3]
            t_summary = "\n  ".join(first_few)
            await ws.send(json.dumps({
                "type": "terminal_telemetry",
                "stream": "THINKING (Gemgem)",
                "text": f"[{step_idx}] 🧠 Gedanke:\n  {t_summary[:300]}",
                "timestamp": now
            }))

        # B) Tool Calls
        tool_calls = item.get("tool_calls", [])
        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("args", {})
            summary = args.get("toolSummary", name)
            cmd = args.get("CommandLine", "")
            path = args.get("AbsolutePath", "") or args.get("TargetFile", "")
            detail = cmd if cmd else (path if path else summary)
            await ws.send(json.dumps({
                "type": "terminal_telemetry",
                "stream": "TOOL",
                "text": f"[{step_idx}] ⚙️ {name}: {detail[:90]}",
                "timestamp": now
            }))

        # C) Content (Agenten-Antwort an Daniel — VOLLSTÄNDIG, unbeschnitten!)
        content = item.get("content", "").strip()
        if content:
            await ws.send(json.dumps({
                "type": "terminal_telemetry",
                "stream": "GEMINI (Antwort)",
                "text": f"\n<<< [◆ GEMGEM #{step_idx}]:\n{content}\n",
                "timestamp": now
            }))

    # 3. Tool Resultate (Echter Output statt nur Zeitstempel-Header!)
    elif msg_type == "GENERIC":
        cnt = item.get("content", "").strip()
        if cnt:
            # Header überspringen
            lines = [l.rstrip() for l in cnt.splitlines() if l.strip()]
            filtered = []
            skip_header = True
            for l in lines:
                if skip_header and (
                    l.startswith("Created At:") or 
                    l.startswith("Completed At:") or 
                    l.startswith("The command exited with code") or 
                    l.startswith("File Path:") or 
                    l.startswith("Total Lines:") or 
                    l.startswith("Total Bytes:") or 
                    l.startswith("Showing lines")
                ):
                    continue
                skip_header = False
                filtered.append(l)

            preview = "\n  ".join(filtered[:4]) if filtered else (lines[0][:120] if lines else "Erledigt.")
            await ws.send(json.dumps({
                "type": "terminal_telemetry",
                "stream": "TOOL_RESULT",
                "text": f"[{step_idx}] ✓ Output:\n  {preview[:250]}",
                "timestamp": now
            }))

def main():
    asyncio.run(stream_transcript())

if __name__ == "__main__":
    main()
