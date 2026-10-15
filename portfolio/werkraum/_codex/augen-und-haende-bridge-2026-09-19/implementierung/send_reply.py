#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — Agent Reply & Rauten-Banter Tool
Pfad: /root/werkraum/_gemini/windows_bridge/send_reply.py

Sendet eine Antwort oder Botschaft von einem AI-Strom:
  1. Als Rauten-Broadcast (3.3s Raumbanner, 6.6s Ticker) an die physische Desktop-Raute
  2. Als Terminal-Telemetrie direkt in den 1:1 Log-Stream des HUDs
"""

import argparse
import asyncio
import json
import sys
import time
import websockets

DEFAULT_WS = "ws://127.0.0.1:9880"

COLOR_MAP = {
    "gemini": "#00E5FF",
    "codex": "#FFD600",
    "claude": "#FF0055",
    "kimi": "#00E676",
    "gpt": "#2979FF"
}

async def send_message(agent: str, text: str, ws_url: str, banner_s: float, ticker_s: float):
    color = COLOR_MAP.get(agent.lower(), "#00E5FF")
    async with websockets.connect(ws_url) as ws:
        # Registrieren als Agent
        await ws.send(json.dumps({
            "type": "register",
            "role": "agent",
            "name": f"AgentReply_{agent}"
        }))
        await ws.recv() # Welcome
        
        # 1. Rauten-Broadcast senden
        await ws.send(json.dumps({
            "type": "diamond_say",
            "agent_id": agent.lower(),
            "color": color,
            "text": text,
            "banner_duration_s": banner_s,
            "ticker_duration_s": ticker_s,
            "timestamp": time.time()
        }))
        
        # 2. Terminal-Telemetrie senden
        await ws.send(json.dumps({
            "type": "terminal_telemetry",
            "stream": f"GEMINI ({agent.upper()})",
            "text": text,
            "timestamp": time.time()
        }))
        
    print(f"✓ Erfolgreich gesendet an HUD & Raute ({agent.upper()}): {text[:60]}...")

def main():
    parser = argparse.ArgumentParser(description="Sende Nachricht an Rauten-Broadcast & HUD-Terminal")
    parser.add_argument("--agent", default="gemini", choices=["gemini", "codex", "claude", "kimi", "gpt"])
    parser.add_argument("--text", required=True, help="Der Text der Nachricht")
    parser.add_argument("--banner-s", type=float, default=6.6, help="Dauer des Raumbanners in Sekunden")
    parser.add_argument("--ticker-s", type=float, default=12.0, help="Dauer des Rauten-Tickers in Sekunden")
    parser.add_argument("--ws-url", default=DEFAULT_WS)
    args = parser.parse_args()

    asyncio.run(send_message(args.agent, args.text, args.ws_url, args.banner_s, args.ticker_s))

if __name__ == "__main__":
    main()
