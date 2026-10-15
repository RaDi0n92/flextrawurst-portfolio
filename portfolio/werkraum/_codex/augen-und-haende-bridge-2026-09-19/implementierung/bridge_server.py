#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — WebSocket Server & Telemetrie-Router
Pfad: /root/werkraum/_gemini/windows_bridge/bridge_server.py

Verbindet externe AI-Ströme (Gemini, Codex, Claude, Kimi, GPT) mit
Daniels Windows-ThinkPad und den Virtuellen Desktops des Linux-VPS.

Entspricht:
  - Systemdokumentation 76: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md
  - Execution-Harness: /config/.agents/skills/augen-und-haende-bridge/SKILL.md
"""

import asyncio
import collections
import datetime
import hashlib
import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional, Set

try:
    import websockets
    from websockets.asyncio.server import ServerConnection
except ImportError:
    import websockets
    ServerConnection = Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BridgeServer")

AUDIT_LOG_PATH = "/root/werkraum/_gemini/windows_bridge/windows_bridge_audit.jsonl"
DEFAULT_WS_PORT = int(os.environ.get("BRIDGE_PORT", "9880"))
DEFAULT_HOST = os.environ.get("BRIDGE_HOST", "0.0.0.0")

class BridgeServer:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_WS_PORT):
        self.host = host
        self.port = port
        
        # Verbunden Clients nach Rolle
        self.clients: Set[Any] = set()       # Desktop-Clients (Windows / Linux)
        self.agents: Set[Any] = set()        # AI-Ströme / MCP-Bridges
        self.observers: Set[Any] = set()     # HUDs, Web-Watcher, Playwright
        self.connections: Dict[Any, Dict[str, Any]] = {}
        
        # State-Management
        self.frame_ring_buffer = collections.deque(maxlen=10)
        self.latest_frame: Optional[Dict[str, Any]] = None
        self.message_history = collections.deque(maxlen=50) # Chat/Terminal Verlauf
        self.active_diamonds: Dict[str, Dict[str, Any]] = {
            "gemini": {"color": "#00E5FF", "label": "Gemgem", "hotkey": "F13", "x": 0.85, "y": 0.12},
            "codex": {"color": "#FFD600", "label": "Codex", "hotkey": "F14", "x": 0.15, "y": 0.12},
            "claude": {"color": "#FF0055", "label": "Claude", "hotkey": "F15", "x": 0.50, "y": 0.05},
            "kimi": {"color": "#00E676", "label": "Kimi", "hotkey": "F16", "x": 0.85, "y": 0.85},
            "gpt": {"color": "#2979FF", "label": "GPT", "hotkey": "F17", "x": 0.15, "y": 0.85},
        }
        self.autonomous_play: bool = False
        self.lockout_until: float = 0.0
        self.running: bool = False
        self.trajectory_samples = collections.deque(maxlen=100)
        self._server = None

    def log_audit(self, event_type: str, payload: Dict[str, Any]):
        """Schreibt ein unveränderbares Audit-Event nach windows_bridge_audit.jsonl."""
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
            logger.error(f"Audit-Log Fehler: {e}")

    async def register_connection(self, ws: Any, role: str, name: str):
        self.connections[ws] = {"role": role, "name": name, "connected_at": time.time()}
        if role == "client":
            self.clients.add(ws)
        elif role == "agent":
            self.agents.add(ws)
        else:
            self.observers.add(ws)
            
        logger.info(f"Verbindung registriert: {name} (Rolle: {role}) | Gesamt: {len(self.connections)}")
        self.log_audit("connection_registered", {"role": role, "name": name})
        
        # Initiale Begrüßung, Status & Verlauf senden
        await ws.send(json.dumps({
            "type": "welcome",
            "server_time": time.time(),
            "autonomous_play": self.autonomous_play,
            "active_diamonds": self.active_diamonds,
            "has_frame": self.latest_frame is not None,
            "history": list(self.message_history)
        }))

    def unregister_connection(self, ws: Any):
        info = self.connections.pop(ws, None)
        if ws in self.clients:
            self.clients.remove(ws)
        if ws in self.agents:
            self.agents.remove(ws)
        if ws in self.observers:
            self.observers.remove(ws)
            
        if info:
            logger.info(f"Verbindung getrennt: {info['name']} ({info['role']})")
            self.log_audit("connection_closed", info)

    async def broadcast(self, targets: Set[Any], message: Dict[str, Any], exclude: Optional[Any] = None):
        """Sendet Nachricht parallel an Zielgruppe."""
        if not targets:
            return
        payload = json.dumps(message, ensure_ascii=False)
        tasks = []
        for ws in list(targets):
            if ws != exclude:
                try:
                    tasks.append(ws.send(payload))
                except Exception:
                    pass
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def handle_message(self, ws: Any, raw_data: str):
        try:
            msg = json.loads(raw_data)
        except Exception as e:
            logger.warning(f"Ungültiges JSON empfangen: {e}")
            return

        msg_type = msg.get("type", "unknown")

        # 1. Registrierung
        if msg_type == "register":
            role = msg.get("role", "observer")
            name = msg.get("name", "unnamed")
            await self.register_connection(ws, role, name)
            return

        # Sicherstellen, dass Verbindung bekannt ist
        if ws not in self.connections:
            await self.register_connection(ws, "observer", "anonymous")

        # 2. Frame-Telemetrie vom Desktop-Client
        if msg_type == "frame_telemetry":
            await self._handle_frame_telemetry(ws, msg)

        # 3. Rauten-Broadcast von Agenten (2-Stufen: 3.3s Banner / 6.6s Ticker)
        elif msg_type == "diamond_say":
            await self._handle_diamond_say(ws, msg)

        # 4. Input-Mutation an Desktop-Client
        elif msg_type == "input_mutation":
            await self._handle_input_mutation(ws, msg)

        # 5. Regie-Event vom HUD
        elif msg_type == "director_event":
            await self._handle_director_event(ws, msg)

        # 6. Terminal-Telemetrie (Logs / Thinking / Tools)
        elif msg_type == "terminal_telemetry":
            await self._handle_terminal_telemetry(ws, msg)

        # 7. Remote-Konsole Prompt von Daniel
        elif msg_type == "console_prompt":
            await self._handle_console_prompt(ws, msg)

        # 8. Ping / Heartbeat
        elif msg_type == "ping":
            await ws.send(json.dumps({
                "type": "pong",
                "client_timestamp": msg.get("timestamp"),
                "server_timestamp": time.time()
            }))

        # 9. Frame-Abfrage (z. B. für MCP-Tool)
        elif msg_type == "get_latest_frame":
            await self._handle_get_latest_frame(ws, msg)

        # 10. Trajektorien-Sample (10 Hz Engine)
        elif msg_type == "trajectory_sample":
            self.trajectory_samples.append(msg)
            await self.broadcast(self.observers, msg)

        # 11. Autonomie-Toggle
        elif msg_type == "set_autonomy":
            self.autonomous_play = bool(msg.get("autonomous_play", False))
            logger.info(f"Autonomie-Modus gesetzt: {self.autonomous_play}")
            self.log_audit("autonomy_toggled", {"autonomous_play": self.autonomous_play})
            await self.broadcast(self.connections.keys(), {
                "type": "autonomy_updated",
                "autonomous_play": self.autonomous_play
            })

        # 12. Not-Aus Signal (F12)
        elif msg_type == "emergency_stop":
            logger.warning("F12 NOT-AUS EMPFANGEN! Alle Aktionen sofort einfrieren.")
            self.lockout_until = time.time() + 10.0  # 10s Zwangs-Sperre
            self.log_audit("emergency_stop_triggered", {"sender": self.connections[ws]["name"]})
            await self.broadcast(self.connections.keys(), {
                "type": "emergency_stop_ack",
                "locked_until": self.lockout_until,
                "timestamp": time.time()
            })

    async def _handle_frame_telemetry(self, ws: Any, msg: Dict[str, Any]):
        frame_b64 = msg.get("frame_b64", "")
        # Hash berechnen
        frame_hash = hashlib.sha256(frame_b64.encode("utf-8")).hexdigest()[:16] if frame_b64 else "empty"
        
        telemetry = {
            "timestamp": msg.get("timestamp", time.time()),
            "frame_hash": frame_hash,
            "screen_resolution": msg.get("screen_resolution", [1920, 1080]),
            "focused_window": msg.get("focused_window", {}),
            "webcam_inlay": msg.get("webcam_inlay", {"active": False}),
            "autonomous_play": msg.get("autonomous_play", self.autonomous_play),
            "active_diamonds": msg.get("active_diamonds", self.active_diamonds)
        }
        
        # Im Ringpuffer ablegen
        self.frame_ring_buffer.append({
            "meta": telemetry,
            "frame_b64": frame_b64
        })
        self.latest_frame = {
            "meta": telemetry,
            "frame_b64": frame_b64
        }
        
        # Bestätigung an den sendenden Client
        await ws.send(json.dumps({
            "type": "frame_ack",
            "frame_hash": frame_hash,
            "timestamp": telemetry["timestamp"]
        }))
        
        # Leichte Benachrichtigung an Observer und Agents
        await self.broadcast(
            self.observers.union(self.agents),
            {
                "type": "frame_arrived",
                "meta": telemetry
            },
            exclude=ws
        )

    async def _handle_diamond_say(self, ws: Any, msg: Dict[str, Any]):
        agent_id = msg.get("agent_id", "gemini")
        color = msg.get("color", self.active_diamonds.get(agent_id, {}).get("color", "#00E5FF"))
        text = msg.get("text", "")
        banner_dur = float(msg.get("banner_duration_s", 3.3))
        ticker_dur = float(msg.get("ticker_duration_s", 6.6))
        
        broadcast_msg = {
            "type": "diamond_say",
            "agent_id": agent_id,
            "color": color,
            "text": text,
            "banner_duration_s": banner_dur,
            "ticker_duration_s": ticker_dur,
            "timestamp": time.time()
        }
        logger.info(f"Rauten-Broadcast [{agent_id}]: {text}")
        self.log_audit("diamond_say", broadcast_msg)
        # An alle Clients (zum Rendern im HUD/Overlay) und Observers senden
        await self.broadcast(self.clients.union(self.observers), broadcast_msg)

    async def _handle_input_mutation(self, ws: Any, msg: Dict[str, Any]):
        # Hardware-Schutzprüfung
        now = time.time()
        if now < self.lockout_until and not self.autonomous_play:
            logger.warning("Input abgewiesen: Hardware-Lockout aktiv!")
            await ws.send(json.dumps({
                "type": "input_rejected",
                "reason": "hardware_lockout",
                "lockout_remaining_s": round(self.lockout_until - now, 2)
            }))
            return

        action = msg.get("action", "click")
        x = msg.get("x", 0)
        y = msg.get("y", 0)
        hwnd = msg.get("hwnd", 0)
        
        # Klick-Käfig Prüfung (wenn Fenster-Sperre aktiv)
        focused = self.latest_frame.get("meta", {}).get("focused_window") if self.latest_frame else None
        if focused and focused.get("locked"):
            rect = focused.get("rect")
            if rect and len(rect) == 4:
                rx1, ry1, rx2, ry2 = rect
                if not (rx1 <= x <= rx2 and ry1 <= y <= ry2):
                    logger.warning(f"Klick-Käfig Verletzung: ({x},{y}) außerhalb [{rx1},{ry1},{rx2},{ry2}] von '{focused.get('title')}'")
                    self.log_audit("click_cage_blocked", {"x": x, "y": y, "rect": rect, "window": focused.get("title")})
                    await ws.send(json.dumps({
                        "type": "input_rejected",
                        "reason": "click_cage_violation",
                        "coords": [x, y],
                        "rect": rect,
                        "locked_window": focused.get("title")
                    }))
                    return

        self.log_audit("input_mutation_dispatched", msg)
        # An aktive Desktop-Clients weiterleiten
        await self.broadcast(self.clients, msg)

    async def _handle_director_event(self, ws: Any, msg: Dict[str, Any]):
        command = msg.get("command", "unknown")
        logger.info(f"Regie-Befehl von HUD: {command}")
        self.log_audit("director_command", msg)
        # An alle AI-Agenten verteilen
        await self.broadcast(self.agents.union(self.observers), {
            "type": "director_command",
            "command": command,
            "timestamp": time.time(),
            "source": self.connections[ws]["name"]
        })

    async def _handle_terminal_telemetry(self, ws: Any, msg: Dict[str, Any]):
        # Streamt Logs / Thinking an das HUD
        await self.broadcast(self.clients.union(self.observers), msg, exclude=ws)

    SHELL_COMMANDS = {
        "ls", "dir", "git", "python", "python3", "bash", "sh", "cd", "pwd", "cat", 
        "echo", "ps", "top", "df", "free", "mkdir", "rm", "cp", "mv", "touch", 
        "tail", "head", "grep", "whoami", "id", "uptime", "curl", "wget", "find",
        "ss", "netstat", "which", "clear", "env", "uname", "export", "date"
    }

    def _is_shell_command(self, text: str) -> bool:
        t = text.strip()
        if not t:
            return False
        if t.startswith("$") or t.startswith("!"):
            return True
        first_word = t.split()[0].lower()
        return first_word in self.SHELL_COMMANDS

    async def _execute_shell_command(self, cmd: str):
        cmd_clean = cmd.lstrip("$!").strip()
        if cmd_clean == "clear":
            await self.broadcast(self.clients.union(self.observers), {
                "type": "terminal_clear",
                "timestamp": time.time()
            })
            return

        logger.info(f"Führe Shell-Befehl aus: {cmd_clean}")
        await self.broadcast(self.clients.union(self.observers), {
            "type": "terminal_telemetry",
            "stream": "SHELL_CMD",
            "text": f"$ {cmd_clean}",
            "timestamp": time.time()
        })
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd_clean,
                cwd="/root/werkraum",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=20.0)
            
            stdout_text = stdout_bytes.decode("utf-8", errors="replace").strip()
            stderr_text = stderr_bytes.decode("utf-8", errors="replace").strip()
            
            if stdout_text:
                for line in stdout_text.splitlines()[:60]:
                    await self.broadcast(self.clients.union(self.observers), {
                        "type": "terminal_telemetry",
                        "stream": "STDOUT",
                        "text": line,
                        "timestamp": time.time()
                    })
            if stderr_text:
                for line in stderr_text.splitlines()[:25]:
                    await self.broadcast(self.clients.union(self.observers), {
                        "type": "terminal_telemetry",
                        "stream": "STDERR",
                        "text": f"ERR: {line}",
                        "timestamp": time.time()
                    })
            await self.broadcast(self.clients.union(self.observers), {
                "type": "terminal_telemetry",
                "stream": "SHELL_EXIT",
                "text": f"[Status: Exit {proc.returncode}]",
                "timestamp": time.time()
            })
        except asyncio.TimeoutError:
            await self.broadcast(self.clients.union(self.observers), {
                "type": "terminal_telemetry",
                "stream": "STDERR",
                "text": "[TIMEOUT: Befehl dauerte länger als 20 Sekunden]",
                "timestamp": time.time()
            })
        except Exception as e:
            await self.broadcast(self.clients.union(self.observers), {
                "type": "terminal_telemetry",
                "stream": "STDERR",
                "text": f"[FEHLER: {e}]",
                "timestamp": time.time()
            })

    async def _handle_console_prompt(self, ws: Any, msg: Dict[str, Any]):
        prompt_text = msg.get("text", "").strip()
        target_agent = msg.get("target_agent", "all")
        if not prompt_text:
            return
            
        logger.info(f"Remote-Konsole Prompt: '{prompt_text}' -> {target_agent}")
        self.log_audit("console_prompt", msg)
        
        # In dauerhafte Inbox-Datei schreiben
        inbox_path = "/root/werkraum/_gemini/windows_bridge/prompt_inbox.jsonl"
        inbox_entry = {
            "timestamp": time.time(),
            "iso_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "text": prompt_text,
            "target_agent": target_agent,
            "sender": self.connections.get(ws, {}).get("name", "HUD_Client")
        }
        try:
            with open(inbox_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(inbox_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Fehler beim Schreiben der prompt_inbox: {e}")

        # An Agents & Observers weiterleiten
        await self.broadcast(self.agents.union(self.observers), {
            "type": "console_prompt",
            "text": prompt_text,
            "target_agent": target_agent,
            "timestamp": time.time()
        })
        
        # Echte Shell-Ausführung wenn es ein Shell-Kommando ist
        if self._is_shell_command(prompt_text):
            asyncio.create_task(self._execute_shell_command(prompt_text))
        else:
            await self.broadcast(self.clients.union(self.observers), {
                "type": "terminal_telemetry",
                "stream": "SYSTEM",
                "text": f"[INBOX]: Text für {target_agent} in prompt_inbox.jsonl abgelegt. (Für Shell-Befehle: '$ befehl' oder Kommandos wie 'git status', 'ls')",
                "timestamp": time.time()
            })

    async def _handle_get_latest_frame(self, ws: Any, msg: Dict[str, Any]):
        if not self.latest_frame:
            await ws.send(json.dumps({
                "type": "latest_frame_response",
                "success": False,
                "error": "No frame captured yet"
            }))
            return
            
        await ws.send(json.dumps({
            "type": "latest_frame_response",
            "success": True,
            "meta": self.latest_frame["meta"],
            "frame_b64": self.latest_frame["frame_b64"]
        }))

    async def ws_handler(self, websocket: Any):
        try:
            async for raw_data in websocket:
                await self.handle_message(websocket, raw_data)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Fehler in ws_handler: {e}")
        finally:
            self.unregister_connection(websocket)

    async def start(self):
        self.running = True
        logger.info(f"Starte Augen & Hände Bridge WebSocket Server auf ws://{self.host}:{self.port} ...")
        self._server = await websockets.serve(self.ws_handler, self.host, self.port, ping_interval=None, ping_timeout=None)
        self.log_audit("server_started", {"host": self.host, "port": self.port})
        logger.info("Server erfolgreich gestartet und lauscht auf Verbindungen.")

    async def stop(self):
        self.running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("Bridge WebSocket Server gestoppt.")
            self.log_audit("server_stopped", {})

async def main():
    server = BridgeServer()
    await server.start()
    try:
        await asyncio.Future()  # läuft endlos
    except (KeyboardInterrupt, asyncio.CancelledError):
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
