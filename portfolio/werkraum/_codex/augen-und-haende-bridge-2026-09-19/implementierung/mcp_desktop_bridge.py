#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — ChatGPT & Multi-Agent MCP Server
Pfad: /root/werkraum/_gemini/windows_bridge/mcp_desktop_bridge.py

Bietet MCP-Tools für ChatGPT, Claude und CLI-Agenten:
  1. windows_desktop_inspect: Liefert internen Screenshot als MCP Image + Metadaten
  2. windows_desktop_act: Führt Mutationen aus oder sendet Rauten-Banter
  3. windows_desktop_status: Abfrage von Bridge-Status, Rauten und Autonomie

Entspricht:
  - Systemdoku 76: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md (Abschnitt 8)
  - Skill: /config/.agents/skills/augen-und-haende-bridge/SKILL.md (Tor R6: Payload Clamping)
"""

import asyncio
import base64
import io
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image as PILImage
from mcp.server.fastmcp import FastMCP, Image
import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] MCP: %(message)s")
logger = logging.getLogger("MCP_DesktopBridge")

BRIDGE_WS_URL = os.environ.get("BRIDGE_WS_URL", "ws://127.0.0.1:9880")
MAX_PAYLOAD_BYTES = 1_500_000  # Tor R6: Maximal 1.5 MB Payload für MCP
MAX_WIDTH = 1920
MAX_HEIGHT = 1080

mcp = FastMCP(
    "windows-desktop-bridge",
    instructions="Ermöglicht multimodale Inspektion und Steuerung von Daniels Windows-Desktop und den Linux-VPS Desktops."
)

async def _send_ws_request(request_payload: Dict[str, Any], timeout_s: float = 3.0) -> Dict[str, Any]:
    """Hilfsfunktion für asynchrone WebSocket-Abfragen an den Bridge-Server."""
    try:
        async with websockets.connect(BRIDGE_WS_URL) as ws:
            # Als MCP-Agent registrieren
            await ws.send(json.dumps({
                "type": "register",
                "role": "agent",
                "name": "ChatGPT_MCP_Bridge"
            }))
            
            # Erste Begrüßung abfangen
            await asyncio.wait_for(ws.recv(), timeout=timeout_s)
            
            # Anfrage senden
            await ws.send(json.dumps(request_payload))
            
            # Auf Antwort warten
            resp_raw = await asyncio.wait_for(ws.recv(), timeout=timeout_s)
            return json.loads(resp_raw)
    except asyncio.TimeoutError:
        return {"success": False, "error": f"Timeout ({timeout_s}s) beim Warten auf Bridge Server ({BRIDGE_WS_URL})"}
    except Exception as e:
        return {"success": False, "error": f"Verbindungsfehler zu Bridge Server: {e}"}

def _clamp_and_compress_image(b64_str: str) -> Tuple[bytes, Dict[str, Any]]:
    """
    Tor R6: MCP Base64 Payload Clamping für ChatGPT.
    Skaliert Bilder > 1920x1080 herunter und komprimiert mit JPEG q80.
    """
    raw_bytes = base64.b64decode(b64_str)
    img = PILImage.open(io.BytesIO(raw_bytes))
    
    orig_w, orig_h = img.size
    orig_size = len(raw_bytes)
    
    # Skalieren wenn nötig
    if orig_w > MAX_WIDTH or orig_h > MAX_HEIGHT:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), PILImage.Resampling.LANCZOS)
        
    out_buf = io.BytesIO()
    # In RGB konvertieren falls RGBA
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img.save(out_buf, format="JPEG", quality=80, optimize=True)
    clamped_bytes = out_buf.getvalue()
    
    meta = {
        "original_dimensions": [orig_w, orig_h],
        "clamped_dimensions": [img.width, img.height],
        "original_bytes": orig_size,
        "clamped_bytes": len(clamped_bytes),
        "clamped": len(clamped_bytes) < orig_size or [orig_w, orig_h] != [img.width, img.height]
    }
    return clamped_bytes, meta

@mcp.tool()
async def windows_desktop_inspect(scope: str = "full", with_webcam: bool = True) -> List[Any]:
    """
    Inspiziert den aktuellen Bildschirminhalt von Daniels Laptop.
    Liefert das Bild direkt als interne Bild-Payload (kein Datei-Upload im Chatverlauf)
    sowie Metadaten zu Fenstern, Bounding Box und aktiven Rauten.
    
    Args:
        scope: "full" für gesamten Desktop (1920x1080) oder "focused" für aktives Zielfenster.
        with_webcam: Ob das Webcam-Inlay im Gesamtbild sichtbar sein soll (Standard: True).
    """
    resp = await _send_ws_request({"type": "get_latest_frame"}, timeout_s=3.0)
    if not resp.get("success"):
        return [f"Fehler bei Bildschirminstruktion: {resp.get('error', 'Kein Frame empfangen')}"]
        
    meta = resp.get("meta", {})
    frame_b64 = resp.get("frame_b64", "")
    if not frame_b64:
        return ["Fehler: Leerer Frame-Puffer empfangen."]
        
    # Tor R6: Payload Clamping
    jpeg_bytes, clamp_meta = _clamp_and_compress_image(frame_b64)
    mcp_image = Image(data=jpeg_bytes, format="jpeg")
    
    summary_text = (
        f"=== DESKTOP FRAME INSPEKTION ===\n"
        f"Timestamp: {meta.get('timestamp')}\n"
        f"Frame-Hash: {meta.get('frame_hash')}\n"
        f"Fokussiertes Fenster: {json.dumps(meta.get('focused_window', {}), indent=2)}\n"
        f"Webcam-Inlay: {json.dumps(meta.get('webcam_inlay', {}))}\n"
        f"Autonomie-Modus: {meta.get('autonomous_play')}\n"
        f"Aktive Rauten: {list(meta.get('active_diamonds', {}).keys())}\n"
        f"Bild-Optimierung (Tor R6): {clamp_meta['clamped_dimensions']} ({clamp_meta['clamped_bytes']} Bytes)"
    )
    
    return [mcp_image, summary_text]

@mcp.tool()
async def windows_desktop_act(
    agent_id: str = "gpt",
    action: str = "click",
    x: int = 0,
    y: int = 0,
    text: str = "",
    button: str = "left",
    hotkey: str = "",
    hwnd: int = 0
) -> Dict[str, Any]:
    """
    Führt eine Interaktion auf Daniels Desktop aus oder sendet eine Nachricht über die Raute.
    
    Args:
        agent_id: Identifikator der KI ('gpt', 'gemini', 'codex', 'claude', 'kimi').
        action: 'click', 'mouse_down', 'mouse_up', 'move', 'type', 'hotkey', 'say', 'flick'.
        x: X-Koordinate (Pixel)
        y: Y-Koordinate (Pixel)
        text: Text zum Tippen oder Botschaft für die Raute (bei action='say')
        button: 'left', 'right', 'middle'
        hotkey: Tastenkombination (z.B. 'ctrl+s', 'f12', 'f13')
        hwnd: Optionales Fenster-Handle für Win32 PostMessage
    """
    # 1. Rauten-Banter (2-Stufen-Broadcast: 3.3s / 6.6s)
    if action == "say":
        color_map = {
            "gpt": "#2979FF",
            "gemini": "#00E5FF",
            "codex": "#FFD600",
            "claude": "#FF0055",
            "kimi": "#00E676"
        }
        payload = {
            "type": "diamond_say",
            "agent_id": agent_id,
            "color": color_map.get(agent_id, "#2979FF"),
            "text": text,
            "banner_duration_s": 3.3,
            "ticker_duration_s": 6.6
        }
        res = await _send_ws_request(payload)
        return {
            "success": True,
            "action": "diamond_say",
            "agent_id": agent_id,
            "text": text,
            "timings": "3.3s Banner / 6.6s Ticker",
            "server_ack": res
        }

    # 2. Input-Mutation
    mode = "cursor_borrow_flick" if action == "flick" else "post_message"
    payload = {
        "type": "input_mutation",
        "agent_id": agent_id,
        "mode": mode,
        "action": action,
        "x": x,
        "y": y,
        "text": text,
        "button": button,
        "hotkey": hotkey,
        "hwnd": hwnd
    }
    res = await _send_ws_request(payload)
    return {
        "success": True,
        "action": action,
        "coords": [x, y],
        "server_response": res
    }

@mcp.tool()
async def windows_desktop_status() -> Dict[str, Any]:
    """Prüft den Verbindungsstatus zum Bridge Server und den aktuellen Desktop-Zustand."""
    res = await _send_ws_request({"type": "ping", "timestamp": time.time()})
    return {
        "bridge_server_url": BRIDGE_WS_URL,
        "status": "connected" if "server_timestamp" in res else "offline",
        "details": res
    }

if __name__ == "__main__":
    mcp.run()
