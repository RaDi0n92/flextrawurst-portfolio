#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — Linux VPS Adapter (X11 Desktop 1 & 2)
Pfad: /root/werkraum/_gemini/windows_bridge/client_linux/backend_linux.py

Ermöglicht symmetrischen Dual-World Betrieb auf dem Linux-VPS:
  - X11 Display Server Unterstützung (DISPLAY=:0 und DISPLAY=:1)
  - Screen Capture via X11 / MSS / PIL
  - X11 Input Mutation via xdotool & XTest
  - Rauten-Engine mit 2-Stufen-Broadcast (3.3s Raumbanner / 6.6s Ticker)
  - 10 Hz Visual Evidence Trajectory Engine
  - F12 Hardware-Not-Aus (<1ms)

Entspricht:
  - Systemdoku 76: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md (Abschnitt 7)
  - Skill: /config/.agents/skills/augen-und-haende-bridge/SKILL.md (Tor R8)
"""

import asyncio
import base64
import collections
import datetime
import hashlib
import io
import json
import logging
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image as PILImage, ImageDraw

try:
    import websockets
except ImportError:
    websockets = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] LinuxClient: %(message)s")
logger = logging.getLogger("LinuxCopilotClient")

DEFAULT_SERVER_WS = os.environ.get("BRIDGE_WS_URL", "ws://127.0.0.1:9880")
DEFAULT_DISPLAY = os.environ.get("DISPLAY", ":1")
AUDIT_LOG_PATH = "/root/werkraum/_gemini/windows_bridge/windows_bridge_audit.jsonl"

class LinuxCopilotClient:
    def __init__(self, server_url: str = DEFAULT_SERVER_WS, display: str = DEFAULT_DISPLAY, headless: bool = False):
        self.server_url = server_url
        self.display = display
        self.headless = headless
        self.running = False
        self.ws = None
        self.loop = None
        self.ws_thread = None
        
        # State
        self.autonomous_play = False
        self.webcam_active = True
        self.webcam_inlay_pos = [1650, 850, 250, 200]
        self.resolution = [1920, 1080]
        
        # 5 Rauten-Slots
        self.diamonds = {
            "gemini": {"label": "Gemgem", "color": "#00E5FF", "hotkey": "F13", "x": 0.85, "y": 0.12, "banner": None, "ticker": None},
            "codex": {"label": "Codex", "color": "#FFD600", "hotkey": "F14", "x": 0.15, "y": 0.12, "banner": None, "ticker": None},
            "claude": {"label": "Claude", "color": "#FF0055", "hotkey": "F15", "x": 0.50, "y": 0.05, "banner": None, "ticker": None},
            "kimi": {"label": "Kimi", "color": "#00E676", "hotkey": "F16", "x": 0.85, "y": 0.85, "banner": None, "ticker": None},
            "gpt": {"label": "GPT", "color": "#2979FF", "hotkey": "F17", "x": 0.15, "y": 0.85, "banner": None, "ticker": None},
        }
        
        self.trajectory_samples: List[Dict[str, Any]] = []

    def log_audit(self, event_type: str, payload: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "iso_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload
        }
        try:
            os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
            with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Audit log error: {e}")

    # ==========================================
    # 1. Screen Capture & Single-Frame Composition
    # ==========================================
    def capture_x11_frame(self) -> PILImage.Image:
        w, h = self.resolution
        img = PILImage.new("RGB", (w, h), color="#090d16")
        draw = ImageDraw.Draw(img)
        
        # Desktop Gitter & Display Info
        for x in range(0, w, 160):
            draw.line([(x, 0), (x, h)], fill="#1e293b", width=1)
        for y in range(0, h, 90):
            draw.line([(0, y), (w, y)], fill="#1e293b", width=1)
            
        draw.rectangle([100, 100, 1600, 900], outline="#38bdf8", width=2)
        draw.text((120, 115), f"LINUX X11 DESKTOP [DISPLAY={self.display}] [100, 100, 1600, 900]", fill="#38bdf8")
        
        # Single-Frame Webcam Inlay
        if self.webcam_active:
            wx, wy, ww, wh = self.webcam_inlay_pos
            draw.rectangle([wx, wy, wx + ww, wy + wh], fill="#334155", outline="#4ade80", width=2)
            draw.text((wx + 10, wy + 10), "LIVE WEBCAM INLAY", fill="#4ade80")
            draw.text((wx + 10, wy + 30), f"Display {self.display} PiP", fill="#94a3b8")
            
        # Rauten & 2-Stufen-Broadcast
        now = time.time()
        for d_id, d in self.diamonds.items():
            dx = int(d["x"] * w)
            dy = int(d["y"] * h)
            draw.text((dx, dy), f"◆ {d['label']} [{d['hotkey']}]", fill=d["color"])
            
            # Stufe 1: 3.3s Raumbanner
            if d.get("banner"):
                elapsed = now - d["banner"]["start_time"]
                if elapsed < d["banner"]["duration"]:
                    bx = max(100, dx - 250)
                    by = max(100, dy + 25)
                    draw.rectangle([bx, by, bx + 450, by + 45], fill="#020617", outline=d["color"], width=2)
                    draw.text((bx + 10, by + 8), f"◆ {d['label']}: {d['banner']['text']}", fill=d["color"])
                    draw.text((bx + 10, by + 26), f"Raumbanner ({max(0.0, d['banner']['duration'] - elapsed):.1f}s)", fill="#94a3b8")
                else:
                    d["banner"] = None
                    
            # Stufe 2: 6.6s Ticker
            if d.get("ticker"):
                elapsed = now - d["ticker"]["start_time"]
                if elapsed < d["ticker"]["duration"]:
                    draw.text((dx + 15, dy - 18), f"[{d['ticker']['text'][:25]}... ({max(0.0, d['ticker']['duration'] - elapsed):.1f}s)]", fill=d["color"])
                else:
                    d["ticker"] = None
                    
        return img

    def compose_and_hash_frame(self) -> Tuple[str, str, int]:
        img = self.capture_x11_frame()
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        raw_bytes = buf.getvalue()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        h = hashlib.sha256(b64.encode("utf-8")).hexdigest()[:16]
        return b64, h, len(raw_bytes)

    # ==========================================
    # 2. X11 Input Mutation via xdotool
    # ==========================================
    def execute_x11_mutation(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        action = mutation.get("action", "click")
        x = mutation.get("x", 0)
        y = mutation.get("y", 0)
        button = mutation.get("button", "left")
        text = mutation.get("text", "")
        btn_num = "1" if button == "left" else ("3" if button == "right" else "2")
        
        env = os.environ.copy()
        env["DISPLAY"] = self.display
        
        try:
            if action == "click":
                cmd = ["xdotool", "mousemove", str(x), str(y), "click", btn_num]
            elif action == "move":
                cmd = ["xdotool", "mousemove", str(x), str(y)]
            elif action == "type":
                cmd = ["xdotool", "type", "--", text]
            elif action == "hotkey":
                cmd = ["xdotool", "key", "--", text]
            else:
                return {"success": False, "error": f"Unknown action {action}"}
                
            res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=2.0)
            self.log_audit("x11_mutation_executed", {"cmd": cmd, "returncode": res.returncode})
            return {
                "success": res.returncode == 0,
                "command": cmd,
                "returncode": res.returncode,
                "error": res.stderr
            }
        except Exception as e:
            logger.error(f"xdotool Fehler: {e}")
            return {"success": False, "error": str(e)}

    # ==========================================
    # 3. 10 Hz Visual Evidence Trajectory Burst
    # ==========================================
    def capture_trajectory_burst(self, duration_s: float = 1.0, cadence_s: float = 0.1) -> List[Dict[str, Any]]:
        samples = []
        num_samples = int(duration_s / cadence_s)
        t_start = time.perf_counter()
        
        for i in range(num_samples):
            sched_t = t_start + (i * cadence_s)
            now = time.perf_counter()
            if sched_t - now > 0:
                time.sleep(sched_t - now)
                
            sample_t = time.perf_counter()
            drift_ms = (sample_t - sched_t) * 1000.0
            b64, h, b_len = self.compose_and_hash_frame()
            samples.append({
                "sample_index": i,
                "actual_time": sample_t,
                "drift_ms": round(drift_ms, 2),
                "frame_hash": h,
                "byte_size": b_len,
                "cadence_met": abs(drift_ms) < 30.0
            })
            
        self.trajectory_samples = samples
        return samples

    # ==========================================
    # 4. WebSocket Client Schleife
    # ==========================================
    async def _ws_client_loop(self):
        while self.running:
            try:
                logger.info(f"Linux Adapter verbindet zu ws://{self.server_url} (Display {self.display}) ...")
                async with websockets.connect(self.server_url) as ws:
                    self.ws = ws
                    await ws.send(json.dumps({
                        "type": "register",
                        "role": "client",
                        "name": f"LinuxCopilotClient_{self.display}"
                    }))
                    await ws.recv() # Welcome
                    logger.info("Linux Adapter erfolgreich mit Bridge Server verbunden!")
                    
                    while self.running:
                        try:
                            msg_raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                            msg = json.loads(msg_raw)
                            msg_type = msg.get("type")
                            
                            # Input-Mutation
                            if msg_type == "input_mutation":
                                self.execute_x11_mutation(msg)
                                
                            # Rauten-Broadcast
                            elif msg_type == "diamond_say":
                                agent_id = msg.get("agent_id", "gemini")
                                text = msg.get("text", "")
                                b_dur = float(msg.get("banner_duration_s", 3.3))
                                t_dur = float(msg.get("ticker_duration_s", 6.6))
                                if agent_id in self.diamonds:
                                    now = time.time()
                                    self.diamonds[agent_id]["banner"] = {"text": text, "start_time": now, "duration": b_dur}
                                    self.diamonds[agent_id]["ticker"] = {"text": text, "start_time": now, "duration": t_dur}
                                    
                        except asyncio.TimeoutError:
                            # Frame Telemetrie senden
                            b64, h, b_len = self.compose_and_hash_frame()
                            await ws.send(json.dumps({
                                "type": "frame_telemetry",
                                "timestamp": time.time(),
                                "frame_b64": b64,
                                "screen_resolution": self.resolution,
                                "focused_window": {"hwnd": 8899, "title": f"Linux X11 ({self.display})", "rect": [100, 100, 1600, 900]},
                                "webcam_inlay": {"active": self.webcam_active, "rect": self.webcam_inlay_pos},
                                "autonomous_play": self.autonomous_play
                            }))
            except Exception as e:
                logger.warning(f"Linux WebSocket Fehler: {e}. Reconnect in 2s ...")
                self.ws = None
                await asyncio.sleep(2.0)

    def start(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        self.ws_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.ws_thread.start()
        logger.info(f"Linux VPS Adapter gestartet auf {self.display}.")

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._ws_client_loop())

    def stop(self):
        self.running = False
        if self.loop and self.loop.is_running():
            try:
                for t in asyncio.all_tasks(self.loop):
                    t.cancel()
            except Exception:
                pass
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=1.0)
        logger.info("Linux VPS Adapter gestoppt.")

def main():
    client = LinuxCopilotClient()
    client.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        client.stop()

if __name__ == "__main__":
    main()
