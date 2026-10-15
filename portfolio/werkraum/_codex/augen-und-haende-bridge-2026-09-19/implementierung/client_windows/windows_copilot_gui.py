#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — Windows Copilot GUI & HUD
Pfad: /root/werkraum/_gemini/windows_bridge/client_windows/windows_copilot_gui.py

Das leichtgewichtige Windows-Client-HUD (<50MB RAM, 0% Idle CPU):
  - Floating HUD mit Regie-Knöpfen (Gruppe A: Tempo/Freigabe, Gruppe B: Denkstrategie)
  - 1:1 Terminal-Stream & Remote-Konsole mit Enter-Trigger
  - Frei verschiebbares Webcam-Inlay mit Ein/Aus-Schalter (Single-Frame PiP)
  - Rauten-Engine für 5 AI-Ströme mit 2-Stufen-Broadcast (3.3s Raumbanner / 6.6s Ticker)
  - 10 Hz Visual Evidence Trajectory Engine (100ms Cadence)
  - Hardware-Not-Aus (F12) und Klick-Käfig-Schutz
  - Vollständiges Tkinter GUI Interface für interaktive Nutzung

Entspricht:
  - Systemdoku 76: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md
  - Skill: /config/.agents/skills/augen-und-haende-bridge/SKILL.md
"""

import asyncio
import base64
import collections
import datetime
import glob
import hashlib
import io
import json
import logging
import os
import platform
import queue
import re
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image as PILImage, ImageDraw, ImageFont

try:
    import websockets
except ImportError:
    websockets = None

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
except ImportError:
    tk = None
    ttk = None
    scrolledtext = None

# Optionale native Treiber auf Windows
try:
    import mss
except ImportError:
    mss = None

try:
    import cv2
except ImportError:
    cv2 = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] GUI: %(message)s")
logger = logging.getLogger("WindowsCopilotGUI")

DEFAULT_SERVER_WS = os.environ.get("BRIDGE_WS_URL", "ws://127.0.0.1:9880")
AUDIT_LOG_PATH = "/root/werkraum/_gemini/windows_bridge/windows_bridge_audit.jsonl"

class RautenSlot:
    def __init__(self, agent_id: str, label: str, color: str, hotkey: str, x_ratio: float, y_ratio: float):
        self.agent_id = agent_id
        self.label = label
        self.color = color
        self.hotkey = hotkey
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.active_banner: Optional[Dict[str, Any]] = None
        self.active_ticker: Optional[Dict[str, Any]] = None

class WindowsCopilotClient:
    def __init__(self, server_url: str = DEFAULT_SERVER_WS, headless: bool = False):
        self.server_url = server_url
        self.headless = headless
        self.running = False
        self.ws = None
        self.loop = None
        self.ws_thread = None
        self.hud_gui = None
        
        # Thread-sichere Message Queue für GUI Updates
        self.gui_queue = queue.Queue()
        
        # Einstellungen
        self.autonomous_play = False
        self.webcam_active = True
        self.webcam_inlay_pos = [1400, 550, 250, 180] # x, y, w, h
        # Bildschirmauflösung dynamisch erkennen
        self.resolution = [1808, 800]
        try:
            if tk:
                _probe = tk.Tk()
                sw = _probe.winfo_screenwidth()
                sh = _probe.winfo_screenheight()
                if sw > 100 and sh > 100:
                    self.resolution = [sw, sh]
                _probe.destroy()
        except Exception:
            pass
        
        # 5 Rauten-Slots
        self.diamonds: Dict[str, RautenSlot] = {
            "gemini": RautenSlot("gemini", "Gemgem", "#00E5FF", "F13", 0.85, 0.12),
            "codex": RautenSlot("codex", "Codex", "#FFD600", "F14", 0.15, 0.12),
            "claude": RautenSlot("claude", "Claude", "#FF0055", "F15", 0.50, 0.05),
            "kimi": RautenSlot("kimi", "Kimi", "#00E676", "F16", 0.85, 0.85),
            "gpt": RautenSlot("gpt", "GPT", "#2979FF", "F17", 0.15, 0.85),
        }
        
        # Terminal & Log Puffer
        self.terminal_logs = collections.deque(maxlen=300)
        self.latest_captured_frame: Optional[PILImage.Image] = None
        self.latest_frame_hash: str = ""
        self.locked_window: Optional[Dict[str, Any]] = None
        
        # 10 Hz Trajectory Engine State
        self.trajectory_active = False
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
    def capture_screen_frame(self) -> PILImage.Image:
        """
        Nativer Screenshot (1920x1080).
        Nutzt MSS auf Windows wenn verfügbar, sonst PIL.ImageGrab oder Synthese.
        """
        w, h = self.resolution
        img = None
        
        # 1. Versuch: MSS native Capture
        if mss:
            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    sct_img = sct.grab(monitor)
                    img = PILImage.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    if img.size != (w, h):
                        img = img.resize((w, h), PILImage.Resampling.LANCZOS)
            except Exception:
                img = None
                
        # 2. Versuch: PIL ImageGrab
        if img is None:
            try:
                from PIL import ImageGrab
                grabbed = ImageGrab.grab()
                img = grabbed.convert("RGB")
                if img.size != (w, h):
                    img = img.resize((w, h), PILImage.Resampling.LANCZOS)
            except Exception:
                img = None

        # 3. Fallback: Synthetischer Desktop Frame
        if img is None:
            img = PILImage.new("RGB", (w, h), color="#0f172a")
            draw = ImageDraw.Draw(img)
            for x in range(0, w, 160):
                draw.line([(x, 0), (x, h)], fill="#1e293b", width=1)
            for y in range(0, h, 90):
                draw.line([(0, y), (w, y)], fill="#1e293b", width=1)
            draw.rectangle([100, 100, 1600, 900], outline="#38bdf8", width=2)
            draw.text((120, 115), "AKTIVES ZIELFENSTER [100, 100, 1600, 900]", fill="#38bdf8")

        draw = ImageDraw.Draw(img)
        
        # Single-Frame Webcam-Inlay (PiP) einstempeln wenn aktiv
        if self.webcam_active:
            wx, wy, ww, wh = self.webcam_inlay_pos
            # Wenn OpenCV Kamera verfügbar ist, echtes Bild einblenden
            cam_frame = None
            if cv2:
                try:
                    cap = cv2.VideoCapture(0)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            cam_frame = PILImage.fromarray(frame).resize((ww, wh))
                        cap.release()
                except Exception:
                    pass
            
            if cam_frame:
                img.paste(cam_frame, (wx, wy))
                draw.rectangle([wx, wy, wx + ww, wy + wh], outline="#4ade80", width=2)
            else:
                draw.rectangle([wx, wy, wx + ww, wy + wh], fill="#334155", outline="#4ade80", width=2)
                draw.text((wx + 10, wy + 10), "LIVE WEBCAM (Daniel)", fill="#4ade80")
                draw.text((wx + 10, wy + 30), "[X] Inlay aktiv (Single-Frame)", fill="#94a3b8")
            
        # Rauten auf den Frame zeichnen
        now = time.time()
        for d in self.diamonds.values():
            dx = int(d.x_ratio * w)
            dy = int(d.y_ratio * h)
            draw.text((dx, dy), f"◆ {d.label} [{d.hotkey}]", fill=d.color)
            
            # Stufe 1: Raumbanner (3.3s Standzeit)
            if d.active_banner:
                elapsed = now - d.active_banner["start_time"]
                if elapsed < d.active_banner["duration"]:
                    bx = max(100, dx - 250)
                    by = max(100, dy + 25)
                    draw.rectangle([bx, by, bx + 450, by + 45], fill="#020617", outline=d.color, width=2)
                    draw.text((bx + 10, by + 8), f"◆ {d.label}: {d.active_banner['text']}", fill=d.color)
                    draw.text((bx + 10, by + 26), f"Raumbanner (noch {max(0.0, d.active_banner['duration'] - elapsed):.1f}s)", fill="#94a3b8")
                else:
                    d.active_banner = None
                    
            # Stufe 2: Rauten-Ticker (6.6s Standzeit)
            if d.active_ticker:
                elapsed = now - d.active_ticker["start_time"]
                if elapsed < d.active_ticker["duration"]:
                    tx = dx + 15
                    ty = dy - 18
                    draw.text((tx, ty), f"[{d.active_ticker['text'][:25]}... ({max(0.0, d.active_ticker['duration'] - elapsed):.1f}s)]", fill=d.color)
                else:
                    d.active_ticker = None
                    
        return img

    def compose_and_hash_frame(self) -> Tuple[str, str, int]:
        img = self.capture_screen_frame()
        self.latest_captured_frame = img
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        img_bytes = buf.getvalue()
        b64_str = base64.b64encode(img_bytes).decode("utf-8")
        h = hashlib.sha256(b64_str.encode("utf-8")).hexdigest()[:16]
        self.latest_frame_hash = h
        return b64_str, h, len(img_bytes)

    # ==========================================
    # 2. 10 Hz Visual Evidence Trajectory Engine
    # ==========================================
    def capture_trajectory_burst(self, duration_s: float = 1.0, cadence_s: float = 0.1) -> List[Dict[str, Any]]:
        samples = []
        num_samples = int(duration_s / cadence_s)
        t_start = time.perf_counter()
        
        for i in range(num_samples):
            scheduled_t = t_start + (i * cadence_s)
            now = time.perf_counter()
            sleep_needed = scheduled_t - now
            if sleep_needed > 0:
                time.sleep(sleep_needed)
                
            sample_t = time.perf_counter()
            drift_ms = (sample_t - scheduled_t) * 1000.0
            
            _, frame_hash, byte_size = self.compose_and_hash_frame()
            sample = {
                "sample_index": i,
                "scheduled_time": scheduled_t,
                "actual_time": sample_t,
                "drift_ms": round(drift_ms, 2),
                "frame_hash": frame_hash,
                "byte_size": byte_size,
                "cadence_met": abs(drift_ms) < 30.0
            }
            samples.append(sample)
            
        self.trajectory_samples = samples
        self.log_audit("trajectory_burst_captured", {
            "samples_count": len(samples),
            "cadence_s": cadence_s,
            "avg_drift_ms": round(sum(s["drift_ms"] for s in samples) / len(samples), 2)
        })
        return samples

    # ==========================================
    # 3. Regie-Knöpfe & Eingabe-Aktionen
    # ==========================================
    def send_director_command(self, command: str):
        logger.info(f"Regie-Knopf gedrückt: {command}")
        self.log_audit("gui_director_command", {"command": command})
        if self.ws and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps({"type": "director_event", "command": command})),
                self.loop
            )

    def send_console_prompt(self, text: str, target_agent: str = "all"):
        if not text.strip():
            return
        logger.info(f"Remote-Konsole Eingabe: '{text}' -> {target_agent}")
        self.log_audit("gui_console_prompt", {"text": text, "target_agent": target_agent})
        if self.ws and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps({
                    "type": "console_prompt",
                    "text": text,
                    "target_agent": target_agent
                })),
                self.loop
            )

    def trigger_emergency_stop(self):
        logger.warning("F12 NOT-AUS IM HUD GEDRÜCKT!")
        self.log_audit("gui_emergency_stop", {"source": "hud_button"})
        if self.ws and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps({"type": "emergency_stop"})),
                self.loop
            )

    def toggle_autonomy(self, enabled: bool):
        self.autonomous_play = enabled
        logger.info(f"Autonomie-Modus umgeschaltet: {self.autonomous_play}")
        self.log_audit("gui_toggle_autonomy", {"autonomous_play": self.autonomous_play})
        if self.ws and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps({"type": "set_autonomy", "autonomous_play": self.autonomous_play})),
                self.loop
            )

    def toggle_webcam(self, enabled: bool):
        self.webcam_active = enabled
        logger.info(f"Webcam-Inlay umgeschaltet: {self.webcam_active}")
        self.log_audit("gui_toggle_webcam", {"webcam_active": self.webcam_active})

    def set_locked_window(self, win_data: Optional[Dict[str, Any]]):
        self.locked_window = win_data
        logger.info(f"Click-Cage Zielfenster aktualisiert: {win_data}")
        self.log_audit("window_cage_updated", {"locked_window": win_data})

    def _get_kwin_dbus_env(self) -> Dict[str, str]:
        """Ermittelt das DBUS_SESSION_BUS_ADDRESS Environment aus aktiven Desktop-Prozessen."""
        env = os.environ.copy()
        if "DBUS_SESSION_BUS_ADDRESS" not in env or not env["DBUS_SESSION_BUS_ADDRESS"]:
            for p in glob.glob("/proc/[0-9]*/cmdline"):
                try:
                    with open(p, "rb") as f:
                        cmd = f.read().decode("utf-8", errors="ignore")
                        if "kwin_wayland" in cmd or "plasmashell" in cmd:
                            pid = p.split("/")[2]
                            with open(f"/proc/{pid}/environ", "rb") as ef:
                                entries = ef.read().split(b"\x00")
                                for entry in entries:
                                    if entry.startswith(b"DBUS_SESSION_BUS_ADDRESS="):
                                        env["DBUS_SESSION_BUS_ADDRESS"] = entry.split(b"=", 1)[1].decode("utf-8")
                                        return env
                except Exception:
                    continue
        return env

    def _scan_win32_windows(self) -> List[Dict[str, Any]]:
        """Scannt sichtbare Win32 Fenster unter Windows."""
        results = []
        try:
            import win32gui
            def enum_cb(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    txt = win32gui.GetWindowText(hwnd).strip()
                    if txt and not txt.startswith("Default IME") and not txt.startswith("MSCTFIME"):
                        r = win32gui.GetWindowRect(hwnd)
                        w = r[2] - r[0]
                        h = r[3] - r[1]
                        if w > 100 and h > 60:
                            results.append({
                                "id": str(hwnd),
                                "title": txt,
                                "raw_title": txt,
                                "rect": [r[0], r[1], r[2], r[3]],
                                "size": [w, h],
                                "minimized": False
                            })
            win32gui.EnumWindows(enum_cb, None)
        except Exception as e:
            logger.warning(f"Win32 Fenster-Scan fehlgeschlagen: {e}")
        return results

    def _scan_kwin_wayland_windows(self) -> List[Dict[str, Any]]:
        """
        Liest alle nativen Wayland- und XWayland-Fenster direkt vom KWin-Compositor via DBus.
        Findet Chromium, Firefox, Blender und alle weiteren echten KDE-Fenster (inkl. minimierter).
        """
        results = []
        env = self._get_kwin_dbus_env()
        try:
            out = subprocess.check_output(
                ["qdbus6", "--literal", "org.kde.KWin", "/WindowsRunner", "org.kde.krunner1.Match", ""],
                env=env,
                timeout=2.0
            ).decode("utf-8", errors="replace")

            items = re.findall(
                r"\[Argument: \(sssida\{sv\}\) \"([^\"]+)\", \"([^\"]+)\", \"([^\"]*)\", ([0-9.]+), ([0-9]+)",
                out
            )
            seen_uuids = set()
            for match_id, title, icon, relevance, category in items:
                uuid_m = re.search(r"\{[0-9a-fA-F-]+\}", match_id)
                uuid = uuid_m.group(0) if uuid_m else match_id
                if uuid in seen_uuids:
                    continue
                seen_uuids.add(uuid)

                try:
                    winfo_raw = subprocess.check_output(
                        ["qdbus6", "org.kde.KWin", "/KWin", "org.kde.KWin.getWindowInfo", uuid],
                        env=env,
                        timeout=1.5
                    ).decode("utf-8", errors="replace")

                    winfo = {}
                    for line in winfo_raw.splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            winfo[k.strip()] = v.strip()

                    x = int(winfo.get("x", 0))
                    y = int(winfo.get("y", 0))
                    w = int(winfo.get("width", 0))
                    h = int(winfo.get("height", 0))
                    is_minimized = winfo.get("minimized", "false").lower() == "true"
                    resource_class = winfo.get("resourceClass", "")
                    caption = winfo.get("caption", title)

                    # KWin-Systemflächen filtern
                    if resource_class in ["plasmashell", "krunner", "kded6"]:
                        continue

                    display_title = caption or title
                    if is_minimized:
                        display_title += " (Minimiert)"
                    if resource_class and resource_class.lower() not in display_title.lower():
                        display_title = f"[{resource_class.upper()}] {display_title}"

                    results.append({
                        "id": uuid,
                        "match_id": match_id,
                        "title": display_title,
                        "raw_title": caption or title,
                        "rect": [x, y, x + w, y + h],
                        "size": [w, h],
                        "minimized": is_minimized,
                        "resourceClass": resource_class
                    })
                except Exception as e:
                    logger.debug(f"getWindowInfo Fehler fuer {uuid}: {e}")
                    continue
        except Exception as e:
            logger.debug(f"KWin Wayland DBus Scan nicht verfuegbar: {e}")

        return results

    def _scan_x11_windows(self) -> List[Dict[str, Any]]:
        """Fallback: Liest Fenster via xdotool & xwininfo auf DISPLAY."""
        results = []
        display = os.environ.get("DISPLAY", ":1")
        env = os.environ.copy()
        env["DISPLAY"] = display
        try:
            out = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--name", ""], env=env).decode("utf-8")
            win_ids = [w.strip() for w in out.splitlines() if w.strip()]
            seen = set()
            for wid in win_ids:
                if wid in seen:
                    continue
                seen.add(wid)
                try:
                    name = subprocess.check_output(["xdotool", "getwindowname", wid], env=env).decode("utf-8", errors="replace").strip()
                    if not name or name.strip().lower() == "desktop" or name == "xfce4-panel" or name == "popdown":
                        continue
                    geom_raw = subprocess.check_output(["xwininfo", "-id", wid], env=env).decode("utf-8", errors="replace")
                    x_m = re.search(r"Absolute upper-left X:\s+(-?\d+)", geom_raw)
                    y_m = re.search(r"Absolute upper-left Y:\s+(-?\d+)", geom_raw)
                    w_m = re.search(r"Width:\s+(\d+)", geom_raw)
                    h_m = re.search(r"Height:\s+(\d+)", geom_raw)
                    if not (x_m and y_m and w_m and h_m):
                        continue
                    x, y = int(x_m.group(1)), int(y_m.group(1))
                    w, h = int(w_m.group(1)), int(h_m.group(1))
                    if w > 80 and h > 50:
                        results.append({
                            "id": str(wid),
                            "title": name,
                            "raw_title": name,
                            "rect": [x, y, x + w, y + h],
                            "size": [w, h],
                            "minimized": False
                        })
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Linux X11 Fenster-Scan fehlgeschlagen: {e}")
        return results

    def activate_window(self, win_data: Dict[str, Any]) -> bool:
        """
        Bringt ein Fenster in den Vordergrund und stellt minimierte Fenster wieder her.
        Funktioniert unter Windows (Win32 API) sowie Linux Wayland (KWin DBus) und X11.
        """
        if platform.system() == "Windows":
            try:
                import win32gui, win32con
                hwnd = int(win_data.get("id", 0))
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return True
            except Exception as e:
                logger.warning(f"Win32 Fenster-Aktivierung fehlgeschlagen: {e}")
                return False

        # Linux KWin Wayland
        match_id = win_data.get("match_id")
        win_id = win_data.get("id")
        if match_id or win_id:
            env = self._get_kwin_dbus_env()
            mid = match_id or f"0_{win_id}"
            try:
                subprocess.run(
                    ["qdbus6", "org.kde.KWin", "/WindowsRunner", "org.kde.krunner1.Run", mid, ""],
                    env=env,
                    timeout=2.0,
                    capture_output=True
                )
                time.sleep(0.15)
                # Aktualisiere Geometrie nach Unminimieren
                if win_id:
                    uuid_m = re.search(r"\{[0-9a-fA-F-]+\}", str(win_id))
                    target_uuid = uuid_m.group(0) if uuid_m else str(win_id)
                    winfo_raw = subprocess.check_output(
                        ["qdbus6", "org.kde.KWin", "/KWin", "org.kde.KWin.getWindowInfo", target_uuid],
                        env=env,
                        timeout=1.5
                    ).decode("utf-8", errors="replace")
                    winfo = {}
                    for line in winfo_raw.splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            winfo[k.strip()] = v.strip()
                    x = int(winfo.get("x", win_data["rect"][0]))
                    y = int(winfo.get("y", win_data["rect"][1]))
                    w = int(winfo.get("width", win_data["size"][0]))
                    h = int(winfo.get("height", win_data["size"][1]))
                    win_data["rect"] = [x, y, x + w, y + h]
                    win_data["size"] = [w, h]
                    win_data["minimized"] = False
                return True
            except Exception as e:
                logger.warning(f"KWin Fenster-Aktivierung fehlgeschlagen: {e}")

        # Linux X11 Fallback
        try:
            wid = win_data.get("id")
            if wid:
                env = os.environ.copy()
                env["DISPLAY"] = os.environ.get("DISPLAY", ":1")
                subprocess.run(["xdotool", "windowactivate", str(wid)], env=env, timeout=1.5, capture_output=True)
                return True
        except Exception as e:
            logger.warning(f"xdotool windowactivate fehlgeschlagen: {e}")

        return False

    def scan_open_windows(self) -> List[Dict[str, Any]]:
        """
        Scannt alle sichtbaren Fenster auf dem aktiven Desktop.
        - Windows: EnumWindows via Win32 API
        - Linux Wayland (KWin): KWin Compositor DBus Schnittstelle (/WindowsRunner & /KWin)
        - Linux X11: xdotool / xwininfo auf DISPLAY
        """
        if platform.system() == "Windows":
            return self._scan_win32_windows()

        # Linux: Zuerst KWin Wayland DBus probieren
        kwin_windows = self._scan_kwin_wayland_windows()
        if kwin_windows:
            return kwin_windows

        # Fallback auf Linux X11 (xdotool)
        return self._scan_x11_windows()

    # ==========================================
    # 4. WebSocket Client Schleife
    # ==========================================
    async def _ws_client_loop(self):
        while self.running:
            try:
                logger.info(f"Verbinde zu Bridge Server {self.server_url} ...")
                async with websockets.connect(self.server_url, ping_interval=None, ping_timeout=None) as ws:
                    self.ws = ws
                    await ws.send(json.dumps({
                        "type": "register",
                        "role": "client",
                        "name": "WindowsCopilotClient_ThinkPad"
                    }))
                    welcome = await ws.recv()
                    logger.info("Mit Bridge Server verbunden!")
                    self.gui_queue.put({"event": "connected", "status": True})
                    
                    while self.running:
                        try:
                            msg_raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                            msg = json.loads(msg_raw)
                            msg_type = msg.get("type")
                            
                            # Rauten-Broadcast empfangen
                            if msg_type == "diamond_say":
                                agent_id = msg.get("agent_id", "gemini")
                                text = msg.get("text", "")
                                b_dur = float(msg.get("banner_duration_s", 3.3))
                                t_dur = float(msg.get("ticker_duration_s", 6.6))
                                
                                if agent_id in self.diamonds:
                                    slot = self.diamonds[agent_id]
                                    now = time.time()
                                    slot.active_banner = {"text": text, "start_time": now, "duration": b_dur}
                                    slot.active_ticker = {"text": text, "start_time": now, "duration": t_dur}
                                    logger.info(f"Rauten-Banter aktiviert für {agent_id}: {text}")
                                    self.gui_queue.put({"event": "diamond_say", "agent_id": agent_id, "text": text})
                                    
                            # Terminal-Telemetrie
                            elif msg_type == "terminal_telemetry":
                                stream = msg.get("stream", "LOG")
                                text = msg.get("text", "")
                                self.gui_queue.put({"event": "log", "stream": stream, "text": text})
                                
                            # Terminal leeren
                            elif msg_type == "terminal_clear":
                                self.gui_queue.put({"event": "clear"})
                                
                            # Autonomie-Update
                            elif msg_type == "autonomy_updated":
                                self.autonomous_play = msg.get("autonomous_play", False)
                                self.gui_queue.put({"event": "autonomy", "state": self.autonomous_play})

                        except asyncio.TimeoutError:
                            b64, h, b_len = self.compose_and_hash_frame()
                            focused = {
                                "hwnd": self.locked_window["id"] if self.locked_window else "desktop",
                                "title": self.locked_window["title"] if self.locked_window else "Full Desktop",
                                "rect": self.locked_window["rect"] if self.locked_window else [0, 0, self.resolution[0], self.resolution[1]],
                                "locked": self.locked_window is not None
                            }
                            await ws.send(json.dumps({
                                "type": "frame_telemetry",
                                "timestamp": time.time(),
                                "frame_b64": b64,
                                "screen_resolution": self.resolution,
                                "focused_window": focused,
                                "webcam_inlay": {"active": self.webcam_active, "rect": self.webcam_inlay_pos},
                                "autonomous_play": self.autonomous_play
                            }))
                            
            except Exception as e:
                logger.warning(f"WebSocket Verbindung verloren: {e}. Reconnect in 2s ...")
                self.ws = None
                self.gui_queue.put({"event": "connected", "status": False})
                await asyncio.sleep(2.0)

    def start(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        self.ws_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.ws_thread.start()
        logger.info("Windows Copilot Client gestartet.")

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._ws_client_loop())

    def stop(self):
        self.running = False
        if self.loop and self.loop.is_running():
            try:
                for task in asyncio.all_tasks(self.loop):
                    task.cancel()
            except Exception:
                pass
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=1.0)
        logger.info("Windows Copilot Client gestoppt.")

# ==========================================
# 5. Physisches Schwebendes Rauten-Fenster (Desktop Overlay)
# ==========================================
class FloatingDiamondWindow:
    def __init__(self, parent_root: Any, agent_id: str, label: str, color: str, default_x: int, default_y: int):
        self.parent = parent_root
        self.agent_id = agent_id
        self.label = label
        self.color = color
        self.x = default_x
        self.y = default_y
        self.active_banner = None
        self.active_ticker = None
        
        self.win = tk.Toplevel(parent_root)
        self.win.overrideredirect(True)
        try:
            self.win.wm_attributes("-topmost", True)
        except Exception:
            pass
        self.win.configure(bg="#020617")
        self.win.geometry(f"190x38+{self.x}+{self.y}")
        
        # Leuchtender Rahmen
        self.border_frame = tk.Frame(self.win, bg=self.color, padx=2, pady=2)
        self.border_frame.pack(fill=tk.BOTH, expand=True)
        
        self.inner_frame = tk.Frame(self.border_frame, bg="#0f172a", padx=6, pady=2)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.diamond_lbl = tk.Label(
            self.inner_frame,
            text=f"◆ {self.label}",
            font=("Segoe UI", 10, "bold"),
            bg="#0f172a",
            fg=self.color,
            cursor="fleur"
        )
        self.diamond_lbl.pack(side=tk.LEFT)
        
        self.status_lbl = tk.Label(
            self.inner_frame,
            text="[Bereit]",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg="#94a3b8"
        )
        self.status_lbl.pack(side=tk.RIGHT, padx=2)
        
        # Drag & Drop Bindings
        for w in (self.win, self.border_frame, self.inner_frame, self.diamond_lbl, self.status_lbl):
            w.bind("<ButtonPress-1>", self._on_drag_start)
            w.bind("<B1-Motion>", self._on_drag_motion)
            
        self.banner_win = None
        
    def _on_drag_start(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.win.winfo_x()
        self._win_start_y = self.win.winfo_y()

    def _on_drag_motion(self, event):
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        self.x = self._win_start_x + dx
        self.y = self._win_start_y + dy
        self.win.geometry(f"+{self.x}+{self.y}")
        if self.banner_win and self.banner_win.winfo_exists():
            self.banner_win.geometry(f"+{self.x - 100}+{self.y + 44}")

    def show_broadcast(self, text: str, banner_s: float = 3.3, ticker_s: float = 6.6):
        self.status_lbl.config(text="● Spricht...", fg=self.color)
        
        if not self.banner_win or not self.banner_win.winfo_exists():
            self.banner_win = tk.Toplevel(self.parent)
            self.banner_win.overrideredirect(True)
            try:
                self.banner_win.wm_attributes("-topmost", True)
            except Exception:
                pass
            self.banner_win.configure(bg="#020617")
            
        bx = max(10, self.x - 120)
        by = self.y + 44
        self.banner_win.geometry(f"440x75+{bx}+{by}")
        
        for w in self.banner_win.winfo_children():
            w.destroy()
            
        b_border = tk.Frame(self.banner_win, bg=self.color, padx=2, pady=2)
        b_border.pack(fill=tk.BOTH, expand=True)
        b_inner = tk.Frame(b_border, bg="#020617", padx=8, pady=6)
        b_inner.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(b_inner, text=f"◆ {self.label} Raumbanner", font=("Segoe UI", 9, "bold"), bg="#020617", fg=self.color)
        title.pack(anchor="w")
        
        content = tk.Label(b_inner, text=text, font=("Segoe UI", 9), bg="#020617", fg="#f8fafc", wraplength=420, justify="left")
        content.pack(anchor="w", pady=(2, 0))
        
        now = time.time()
        self.active_banner = {"text": text, "end_time": now + banner_s}
        self.active_ticker = {"text": text, "end_time": now + banner_s + ticker_s}
        
        def _phase_tick():
            t_now = time.time()
            if self.active_banner and t_now < self.active_banner["end_time"]:
                rem = max(0.0, self.active_banner["end_time"] - t_now)
                title.config(text=f"◆ {self.label} Raumbanner ({rem:.1f}s)")
                self.parent.after(100, _phase_tick)
            elif self.active_ticker and t_now < self.active_ticker["end_time"]:
                self.active_banner = None
                rem = max(0.0, self.active_ticker["end_time"] - t_now)
                title.config(text=f"◆ {self.label} Rauten-Ticker ({rem:.1f}s)")
                self.parent.after(100, _phase_tick)
            else:
                self.active_banner = None
                self.active_ticker = None
                self.status_lbl.config(text="[Bereit]", fg="#94a3b8")
                if self.banner_win and self.banner_win.winfo_exists():
                    self.banner_win.destroy()
                    self.banner_win = None
                    
        self.parent.after(100, _phase_tick)

# ==========================================
# 6. Vollständiges Tkinter HUD Interface
# ==========================================
class WindowsCopilotHUD:
    def __init__(self, client: WindowsCopilotClient):
        self.client = client
        self.client.hud_gui = self
        
        if not tk:
            raise RuntimeError("Tkinter ist in dieser Python-Umgebung nicht verfügbar.")
            
        self.root = tk.Tk()
        self.root.title("◆ Augen & Hände Desktop Bridge — Windows HUD")
        self.root.geometry("780x620+50+50")
        self.root.minsize(450, 520)
        self.root.configure(bg="#0f172a")
        
        # Stets im Vordergrund halten
        try:
            self.root.wm_attributes("-topmost", True)
        except Exception:
            pass
            
        # Physische Schwebende Desktop-Rauten instanziieren
        self.diamond_windows: Dict[str, FloatingDiamondWindow] = {}
        # Gemgem (Cyan) als primäre schwebende Raute oben rechts
        sw = self.client.resolution[0]
        gem_x = max(100, sw - 240)
        self.diamond_windows["gemini"] = FloatingDiamondWindow(
            self.root, "gemini", "Gemgem", "#00E5FF", gem_x, 30
        )
            
        # F12 Hotkey binden
        self.root.bind_all("<F12>", lambda e: self.on_emergency_stop())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        # 1. Header & Status-Leiste
        header_frame = tk.Frame(self.root, bg="#1e293b", padx=12, pady=8)
        header_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        title_lbl = tk.Label(
            header_frame,
            text="◆ AUGEN & HÄNDE DESKTOP BRIDGE",
            font=("Segoe UI", 12, "bold"),
            bg="#1e293b",
            fg="#38bdf8"
        )
        title_lbl.pack(side=tk.LEFT)
        
        self.conn_badge = tk.Label(
            header_frame,
            text="● Verbinde...",
            font=("Segoe UI", 9, "bold"),
            bg="#334155",
            fg="#f59e0b",
            padx=8,
            pady=2
        )
        self.conn_badge.pack(side=tk.RIGHT, padx=4)

        cadence_lbl = tk.Label(
            header_frame,
            text="📸 1080p | 10 Hz Cadence",
            font=("Segoe UI", 9),
            bg="#1e293b",
            fg="#94a3b8"
        )
        cadence_lbl.pack(side=tk.RIGHT, padx=8)

        # 2. Regie-Knöpfe Panel
        regie_frame = tk.LabelFrame(
            self.root,
            text=" REGIE-KNÖPFE (MILLISEKUNDEN-ENTSCHEIDUNGEN) ",
            bg="#0f172a",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=8
        )
        regie_frame.pack(fill=tk.X, padx=8, pady=4)

        # Gruppe A: Freigabe & Tempo
        row_a = tk.Frame(regie_frame, bg="#0f172a")
        row_a.pack(fill=tk.X, pady=(0, 4))
        
        btn_style = {"bg": "#1e293b", "fg": "#f8fafc", "activebackground": "#38bdf8", "activeforeground": "#0f172a", "font": ("Segoe UI", 9), "relief": tk.FLAT, "padx": 6, "pady": 4}
        
        tk.Button(row_a, text="👍 Weiter so", command=lambda: self.client.send_director_command("weiter_so"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_a, text="🛠️ Mach mal", command=lambda: self.client.send_director_command("mach_mal"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_a, text="🚀 Go!", command=lambda: self.client.send_director_command("go"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_a, text="⏳ Warte kurz", command=lambda: self.client.send_director_command("warte_kurz"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_a, text="⏸️ Pause", command=lambda: self.client.send_director_command("pause"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_a, text="✅ Ja", command=lambda: self.client.send_director_command("ja"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_a, text="❌ Nein", command=lambda: self.client.send_director_command("nein"), **btn_style).pack(side=tk.LEFT, padx=2)

        # Gruppe B: Denkstrategie
        row_b = tk.Frame(regie_frame, bg="#0f172a")
        row_b.pack(fill=tk.X)
        
        tk.Button(row_b, text="🧠 Denk nach", command=lambda: self.client.send_director_command("denk_nach"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_b, text="🔄 Denk neu", command=lambda: self.client.send_director_command("denk_neu"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_b, text="🎯 Fokus", command=lambda: self.client.send_director_command("konzentrier_dich"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_b, text="💡 Andere Idee?", command=lambda: self.client.send_director_command("andere_idee"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_b, text="↩️ Undo", command=lambda: self.client.send_director_command("undo"), **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(row_b, text="📸 Neu scannen", command=lambda: self.client.compose_and_hash_frame(), **btn_style).pack(side=tk.LEFT, padx=2)

        # 3. Hardware-Schutz & Toggles Bar
        toggles_frame = tk.Frame(self.root, bg="#1e293b", padx=8, pady=6)
        toggles_frame.pack(fill=tk.X, padx=8, pady=4)
        
        self.webcam_var = tk.BooleanVar(value=self.client.webcam_active)
        cb_webcam = tk.Checkbutton(
            toggles_frame,
            text="Webcam-Inlay aktiv (Single-Frame PiP)",
            variable=self.webcam_var,
            command=self.on_toggle_webcam,
            bg="#1e293b",
            fg="#f8fafc",
            selectcolor="#0f172a",
            activebackground="#1e293b",
            font=("Segoe UI", 9)
        )
        cb_webcam.pack(side=tk.LEFT, padx=6)

        self.autonomy_var = tk.BooleanVar(value=self.client.autonomous_play)
        cb_autonomy = tk.Checkbutton(
            toggles_frame,
            text="Volle Agenten-Autonomie",
            variable=self.autonomy_var,
            command=self.on_toggle_autonomy,
            bg="#1e293b",
            fg="#f8fafc",
            selectcolor="#0f172a",
            activebackground="#1e293b",
            font=("Segoe UI", 9)
        )
        cb_autonomy.pack(side=tk.LEFT, padx=6)

        btn_stop = tk.Button(
            toggles_frame,
            text="🛑 NOT-AUS (F12)",
            bg="#ef4444",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=3,
            command=self.on_emergency_stop
        )
        btn_stop.pack(side=tk.RIGHT, padx=6)

        # 3b. Echter Fenster-Scanner & Click-Cage (KI-Eingrenzung)
        cage_frame = tk.LabelFrame(
            self.root,
            text=" 🎯 FENSTER-SCANNER & CLICK-CAGE (KI-EINGRENZUNG) ",
            bg="#0f172a",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=4
        )
        cage_frame.pack(fill=tk.X, padx=8, pady=4)

        c_row1 = tk.Frame(cage_frame, bg="#0f172a")
        c_row1.pack(fill=tk.X, pady=(0, 2))

        self.scanned_windows: List[Dict[str, Any]] = []
        self.selected_window_var = tk.StringVar(value="[Kein Fenster gewählt — Freier Desktop]")

        self.window_dropdown = ttk.Combobox(
            c_row1,
            textvariable=self.selected_window_var,
            state="readonly",
            width=36
        )
        self.window_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.window_dropdown.bind("<<ComboboxSelected>>", self.on_window_selected)

        btn_scan = tk.Button(
            c_row1,
            text="🔍 Fenster scannen",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT,
            padx=6,
            pady=1,
            command=self.scan_and_update_windows
        )
        btn_scan.pack(side=tk.LEFT, padx=2)

        self.btn_lock = tk.Button(
            c_row1,
            text="🔒 Sperren",
            bg="#334155",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=1,
            command=self.toggle_window_lock
        )
        self.btn_lock.pack(side=tk.LEFT, padx=(4, 2))

        self.cage_status_lbl = tk.Label(
            cage_frame,
            text="🔓 Status: KI frei auf gesamtem Desktop (kein Fenster gesperrt)",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg="#facc15",
            anchor="w"
        )
        self.cage_status_lbl.pack(fill=tk.X, padx=2)

        # 4. 1:1 Live Terminal View
        term_frame = tk.LabelFrame(
            self.root,
            text=" 1:1 TERMINAL, THINKING & LOG STREAM ",
            bg="#0f172a",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=4
        )
        term_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.term_box = scrolledtext.ScrolledText(
            term_frame,
            bg="#020617",
            fg="#4ade80",
            font=("Consolas", 9),
            insertbackground="#38bdf8",
            relief=tk.FLAT,
            height=10
        )
        self.term_box.pack(fill=tk.BOTH, expand=True)
        
        # Tags für Farbkodierung
        self.term_box.tag_config("gemini", foreground="#00E5FF", font=("Consolas", 9, "bold"))
        self.term_box.tag_config("daniel", foreground="#FACC15", font=("Consolas", 9, "bold"))
        self.term_box.tag_config("tool", foreground="#C084FC", font=("Consolas", 9))
        self.term_box.tag_config("tool_result", foreground="#6EE7B7", font=("Consolas", 8))
        self.term_box.tag_config("thinking", foreground="#94A3B8", font=("Consolas", 8, "italic"))
        self.term_box.tag_config("system", foreground="#38BDF8", font=("Consolas", 9))
        self.term_box.tag_config("error", foreground="#EF4444", font=("Consolas", 9, "bold"))
        self.term_box.tag_config("log", foreground="#4ADE80", font=("Consolas", 9))
        self.term_box.tag_config("stdout", foreground="#4ADE80", font=("Consolas", 9))
        self.term_box.tag_config("stderr", foreground="#F87171", font=("Consolas", 9))
        self.term_box.tag_config("shell_cmd", foreground="#38BDF8", font=("Consolas", 9, "bold"))
        
        self.term_box.insert(tk.END, "=== AUGEN & HÄNDE INTERAKTIVES TERMINAL INITIALISIERT ===\n", "system")

        # 5. Remote-Konsole Eingabe (Prompt an Gemgem) — Ehrlich ohne Multi-AI-Mock
        console_frame = tk.Frame(self.root, bg="#1e293b", padx=8, pady=6)
        console_frame.pack(fill=tk.X, padx=8, pady=(4, 8))

        # Zeile 1: Label & Button
        c_top = tk.Frame(console_frame, bg="#1e293b")
        c_top.pack(fill=tk.X, pady=(0, 4))

        prompt_lbl = tk.Label(
            c_top,
            text="Prompt an Gemgem (VPS CLI):",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg="#38bdf8"
        )
        prompt_lbl.pack(side=tk.LEFT, padx=(2, 6))

        self.target_agent_var = tk.StringVar(value="gemini")

        send_btn = tk.Button(
            c_top,
            text="Senden ↵ (Enter)",
            bg="#38bdf8",
            fg="#0f172a",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=1,
            command=self.on_send_prompt
        )
        send_btn.pack(side=tk.RIGHT, padx=2)

        # Zeile 2: Volle Breite Eingabezeile
        self.prompt_entry = tk.Entry(
            console_frame,
            font=("Segoe UI", 10),
            bg="#020617",
            fg="#f8fafc",
            insertbackground="#38bdf8",
            relief=tk.FLAT
        )
        self.prompt_entry.pack(fill=tk.X, expand=True, padx=2)
        self.prompt_entry.bind("<Return>", lambda e: self.on_send_prompt())
        self.prompt_entry.focus_set()

        # Beim Start Fenster initial scannen
        self.root.after(500, self.scan_and_update_windows)

    def scan_and_update_windows(self):
        self.scanned_windows = self.client.scan_open_windows()
        titles = ["[Kein Fenster gewählt — Freier Desktop]"]
        for w in self.scanned_windows:
            short_t = (w["title"][:45] + "...") if len(w["title"]) > 45 else w["title"]
            titles.append(f"{short_t} (ID: {w['id']}, {w['size'][0]}x{w['size'][1]})")
        self.window_dropdown["values"] = titles
        self.selected_window_var.set(titles[0])
        self.on_window_selected()
        self.term_box.insert(tk.END, f"\n[SCAN]: {len(self.scanned_windows)} offene Fenster erkannt (Wayland/X11).\n", "system")
        self.term_box.see(tk.END)

    def on_window_selected(self, event=None):
        val = self.selected_window_var.get()
        if val == "[Kein Fenster gewählt — Freier Desktop]":
            self.client.set_locked_window(None)
            self.btn_lock.config(text="🔒 Sperren", bg="#334155", fg="#94a3b8")
            self.cage_status_lbl.config(text="🔓 Status: KI frei auf gesamtem Desktop (kein Fenster gesperrt)", fg="#facc15")
            return

        idx = self.window_dropdown.current() - 1
        if 0 <= idx < len(self.scanned_windows):
            target = self.scanned_windows[idx]
            if self.client.locked_window and self.client.locked_window.get("id") == target["id"]:
                self.cage_status_lbl.config(text=f"🔒 EINGESPERRT: '{target['title']}' | Käfig: {target['rect']}", fg="#4ade80")
            else:
                self.cage_status_lbl.config(text=f"Bereit zur Sperrung: '{target['title']}' | Box: {target['rect']}", fg="#38bdf8")

    def toggle_window_lock(self):
        val = self.selected_window_var.get()
        if val == "[Kein Fenster gewählt — Freier Desktop]":
            self.client.set_locked_window(None)
            self.btn_lock.config(text="🔒 Sperren", bg="#334155", fg="#94a3b8")
            self.cage_status_lbl.config(text="🔓 Status: KI frei auf gesamtem Desktop (kein Fenster gesperrt)", fg="#facc15")
            return

        idx = self.window_dropdown.current() - 1
        if 0 <= idx < len(self.scanned_windows):
            target = self.scanned_windows[idx]
            if self.client.locked_window:
                # Entsperren
                self.client.set_locked_window(None)
                self.btn_lock.config(text="🔒 Sperren", bg="#334155", fg="#94a3b8")
                self.cage_status_lbl.config(text=f"🔓 Entsperrt (Bereit: '{target['title']}')", fg="#facc15")
                self.term_box.insert(tk.END, f"\n[CLICK-CAGE]: KI entsperrt — wieder freier Desktop-Scope.\n", "system")
            else:
                # Fenster aktivieren / unminimieren falls minimiert
                self.client.activate_window(target)
                # Sperren
                self.client.set_locked_window(target)
                self.btn_lock.config(text="🔓 Entsperren", bg="#ef4444", fg="#ffffff")
                self.cage_status_lbl.config(text=f"🔒 EINGESPERRT IN: '{target['title']}' | Käfig: {target['rect']}", fg="#4ade80")
                self.term_box.insert(tk.END, f"\n[CLICK-CAGE]: KI eingesperrt in '{target['title']}' (ID: {target['id']}, Box: {target['rect']})! Klicks außerhalb werden verworfen.\n", "system")
            self.term_box.see(tk.END)

    def on_toggle_webcam(self):
        val = self.webcam_var.get()
        self.client.toggle_webcam(val)

    def on_toggle_autonomy(self):
        val = self.autonomy_var.get()
        self.client.toggle_autonomy(val)

    def on_emergency_stop(self):
        self.client.trigger_emergency_stop()
        self.term_box.insert(tk.END, "\n[NOT-AUS]: F12 ausgelöst! Alle KIs sofort eingefroren!\n", "error")
        self.term_box.see(tk.END)

    def on_send_prompt(self):
        text = self.prompt_entry.get().strip()
        if text:
            target = self.target_agent_var.get()
            self.client.send_console_prompt(text, target_agent=target)
            now_str = datetime.datetime.now().strftime("%H:%M:%S")
            self.term_box.insert(tk.END, f"\n[{now_str}] [Daniel -> {target}]: {text}\n", "daniel")
            self.term_box.see(tk.END)
            self.prompt_entry.delete(0, tk.END)

    def _poll_queue(self):
        while not self.client.gui_queue.empty():
            item = self.client.gui_queue.get_nowait()
            evt = item.get("event")
            if evt == "connected":
                if item.get("status"):
                    self.conn_badge.config(text="● Verbunden", bg="#064e3b", fg="#4ade80")
                else:
                    self.conn_badge.config(text="● Offline", bg="#7f1d1d", fg="#f87171")
            elif evt == "clear":
                self.term_box.delete("1.0", tk.END)
                self.term_box.insert(tk.END, "=== TERMINAL GELEERT ===\n", "system")
            elif evt == "log":
                stream = item.get("stream", "LOG")
                text = item.get("text", "")
                
                if stream == "STDOUT":
                    self.term_box.insert(tk.END, text + "\n", "stdout")
                elif stream == "STDERR":
                    self.term_box.insert(tk.END, text + "\n", "stderr")
                elif stream == "SHELL_CMD":
                    self.term_box.insert(tk.END, f"\n{text}\n", "shell_cmd")
                elif stream == "SHELL_EXIT":
                    self.term_box.insert(tk.END, f"{text}\n", "system")
                else:
                    tag = "log"
                    if "DANIEL" in stream:
                        tag = "daniel"
                    elif "GEMINI" in stream or "GEMGEM" in stream:
                        tag = "gemini"
                    elif "THINKING" in stream:
                        tag = "thinking"
                    elif "TOOL_RESULT" in stream:
                        tag = "tool_result"
                    elif "TOOL" in stream:
                        tag = "tool"
                    elif "ERROR" in stream:
                        tag = "error"
                    elif "SYSTEM" in stream or "INBOX" in stream:
                        tag = "system"
                    self.term_box.insert(tk.END, f"{text}\n", tag)
                self.term_box.see(tk.END)
            elif evt == "diamond_say":
                agent = item.get("agent_id", "gemini")
                txt = item.get("text", "")
                b_dur = float(item.get("banner_duration_s", 3.3))
                t_dur = float(item.get("ticker_duration_s", 6.6))
                # Physische Schwebende Raute am Bildschirm aktualisieren
                if agent in self.diamond_windows:
                    self.diamond_windows[agent].show_broadcast(txt, b_dur, t_dur)
                elif "gemini" in self.diamond_windows:
                    self.diamond_windows["gemini"].show_broadcast(f"[{agent.upper()}]: {txt}", b_dur, t_dur)
                # Auch im Terminal farblich ausgeben
                self.term_box.insert(tk.END, f"\n[◆ {agent.upper()}]: {txt}\n", "gemini")
                self.term_box.see(tk.END)
            elif evt == "autonomy":
                self.autonomy_var.set(item.get("state"))
                
        self.root.after(100, self._poll_queue)

    def run(self):
        self.client.start()
        self.root.mainloop()

    def on_close(self):
        self.client.stop()
        self.root.destroy()

def main():
    headless = "--headless" in sys.argv
    client = WindowsCopilotClient(headless=headless)
    
    if headless or not tk:
        logger.info("Starte Windows Copilot Client im Headless / Konsolen-Modus ...")
        client.start()
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            client.stop()
    else:
        logger.info("Starte Windows Copilot GUI HUD ...")
        hud = WindowsCopilotHUD(client)
        hud.run()

if __name__ == "__main__":
    main()
