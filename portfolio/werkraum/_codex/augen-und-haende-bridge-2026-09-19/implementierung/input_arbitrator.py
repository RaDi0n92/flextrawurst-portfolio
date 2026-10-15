#!/usr/bin/env python3
"""
Augen & Hände Desktop Bridge — Input Arbitrator & Multi-Agent Dispatcher
Pfad: /root/werkraum/_gemini/windows_bridge/input_arbitrator.py

Verwaltet:
  1. Win32 PostMessage Builder (relative Koordinaten & wParam/lParam)
  2. Sub-Frame Cursor Borrowing (12ms Flick) Fallback
  3. Klick-Käfig (Hardware-Guard gegen Out-of-Bounds Klicks)
  4. Shared Mouse Lease Manager (Token-Passing für RTS/Strategie)
  5. ViGEm Gamepad Manager (Virtuelle Controller für bis zu 4 KIs)
  6. Hardware-Not-Aus (F12) und Daniel-Override (<1ms)
  7. Symmetrische Linux X11 Schnittstelle (xdotool / XTest)

Entspricht:
  - Systemdoku 76: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md
  - Skill: /config/.agents/skills/augen-und-haende-bridge/SKILL.md
"""

import collections
import datetime
import json
import logging
import os
import platform
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("InputArbitrator")

AUDIT_LOG_PATH = "/root/werkraum/_gemini/windows_bridge/windows_bridge_audit.jsonl"

# Win32 Windows-Nachrichten Konstanten
WM_MOUSEMOVE   = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP   = 0x0208
WM_MOUSEWHEEL  = 0x020A
WM_KEYDOWN     = 0x0100
WM_KEYUP       = 0x0101
WM_CHAR        = 0x0102

# F13 bis F24 Virtual Key Codes
VK_F13 = 0x7C
VK_F14 = 0x7D
VK_F15 = 0x7E
VK_F16 = 0x7F
VK_F17 = 0x80
VK_F18 = 0x81
VK_F19 = 0x82
VK_F20 = 0x83
VK_F21 = 0x84
VK_F22 = 0x85
VK_F23 = 0x86
VK_F24 = 0x87

class InputArbitrator:
    def __init__(self, autonomous_play: bool = False):
        self.autonomous_play = autonomous_play
        self.lockout_until: float = 0.0
        self.active_lease_holder: Optional[str] = None
        self.lease_expires_at: float = 0.0
        self.system_is_windows = platform.system() == "Windows"
        
        # Virtuelle Gamepads (bis zu 4 KIs)
        self.gamepads: Dict[int, Dict[str, Any]] = {
            i: {
                "connected": False,
                "assigned_agent": None,
                "buttons": {},
                "axes": {"lx": 0.0, "ly": 0.0, "rx": 0.0, "ry": 0.0, "lt": 0.0, "rt": 0.0}
            }
            for i in range(4)
        }
        
        # Statistik & Sentinels
        self.stats = {
            "total_mutations": 0,
            "blocked_cage": 0,
            "blocked_lockout": 0,
            "borrow_flicks_executed": 0,
            "gamepad_events": 0
        }

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
            logger.error(f"Audit Log Error: {e}")

    # ==========================================
    # 1. Sicherheits- & Not-Aus-Funktionen
    # ==========================================
    def trigger_emergency_stop(self, reason: str = "F12 Hardware Not-Aus") -> Dict[str, Any]:
        """Kappt alle Inputs in <1ms und setzt 10 Sekunden Zwangs-Sperre."""
        t_start = time.perf_counter()
        self.lockout_until = time.time() + 10.0
        self.active_lease_holder = None
        self.lease_expires_at = 0.0
        
        # Gamepad Sticks zentrieren
        for gp in self.gamepads.values():
            gp["axes"] = {"lx": 0.0, "ly": 0.0, "rx": 0.0, "ry": 0.0, "lt": 0.0, "rt": 0.0}
            gp["buttons"] = {}
            
        elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        result = {
            "emergency_stop_triggered": True,
            "reason": reason,
            "latency_ms": round(elapsed_ms, 3),
            "locked_until": self.lockout_until
        }
        self.log_audit("emergency_stop_executed", result)
        logger.warning(f"NOT-AUS AUSGELÖST in {elapsed_ms:.3f}ms: {reason}")
        return result

    def on_physical_user_activity(self):
        """Wird aufgerufen wenn Daniel physische Maus/Tastatur bewegt."""
        if not self.autonomous_play:
            self.lockout_until = time.time() + 2.0
            if self.active_lease_holder:
                logger.info(f"Daniel Override: Entziehe {self.active_lease_holder} die Kontrolle.")
                self.active_lease_holder = None
            self.log_audit("daniel_override", {"lockout_s": 2.0})

    def is_locked(self) -> Tuple[bool, float]:
        now = time.time()
        if now < self.lockout_until and not self.autonomous_play:
            return True, round(self.lockout_until - now, 2)
        return False, 0.0

    # ==========================================
    # 2. Klick-Käfig (Bounding Box Guard)
    # ==========================================
    def check_click_cage(self, x: int, y: int, bounding_box: Optional[List[int]]) -> bool:
        """Prüft, ob der Klick innerhalb des zugewiesenen Fenster-Rechtecks [x1, y1, x2, y2] liegt."""
        if not bounding_box or len(bounding_box) != 4:
            return True  # Vollbild-Scope
        x1, y1, x2, y2 = bounding_box
        in_bounds = (x1 <= x <= x2) and (y1 <= y <= y2)
        if not in_bounds:
            self.stats["blocked_cage"] += 1
            self.log_audit("click_cage_violation", {
                "click_coords": [x, y],
                "bounding_box": bounding_box
            })
        return in_bounds

    # ==========================================
    # 3. Win32 Message Builder (Relative Koordinaten)
    # ==========================================
    @staticmethod
    def build_win32_lparam(rel_x: int, rel_y: int) -> int:
        """Erzeugt Win32 lParam: (y << 16) | (x & 0xFFFF)."""
        return ((int(rel_y) & 0xFFFF) << 16) | (int(rel_x) & 0xFFFF)

    def generate_post_messages(
        self,
        hwnd: int,
        action: str,
        rel_x: int,
        rel_y: int,
        button: str = "left"
    ) -> List[Dict[str, Any]]:
        """
        Erzeugt das Win32 PostMessage-Paket.
        Wichtig: IMMER WM_MOUSEMOVE vor DOWN/UP für Electron/Chromium Hit-Test!
        """
        lparam = self.build_win32_lparam(rel_x, rel_y)
        messages = []

        # 1. Vorbereitendes WM_MOUSEMOVE
        messages.append({
            "hwnd": hwnd,
            "msg": WM_MOUSEMOVE,
            "wparam": 0,
            "lparam": lparam,
            "desc": "WM_MOUSEMOVE"
        })

        if action == "click":
            if button == "left":
                messages.append({"hwnd": hwnd, "msg": WM_LBUTTONDOWN, "wparam": 0x0001, "lparam": lparam, "desc": "WM_LBUTTONDOWN"})
                messages.append({"hwnd": hwnd, "msg": WM_LBUTTONUP, "wparam": 0x0000, "lparam": lparam, "desc": "WM_LBUTTONUP"})
            elif button == "right":
                messages.append({"hwnd": hwnd, "msg": WM_RBUTTONDOWN, "wparam": 0x0002, "lparam": lparam, "desc": "WM_RBUTTONDOWN"})
                messages.append({"hwnd": hwnd, "msg": WM_RBUTTONUP, "wparam": 0x0000, "lparam": lparam, "desc": "WM_RBUTTONUP"})
        elif action == "mouse_down":
            msg = WM_LBUTTONDOWN if button == "left" else WM_RBUTTONDOWN
            messages.append({"hwnd": hwnd, "msg": msg, "wparam": 1, "lparam": lparam, "desc": "DOWN"})
        elif action == "mouse_up":
            msg = WM_LBUTTONUP if button == "left" else WM_RBUTTONUP
            messages.append({"hwnd": hwnd, "msg": msg, "wparam": 0, "lparam": lparam, "desc": "UP"})
            
        return messages

    # ==========================================
    # 4. Sub-Frame Cursor Borrowing (12ms Flick Fallback)
    # ==========================================
    def execute_cursor_borrow_flick(
        self,
        target_x: int,
        target_y: int,
        button: str = "left",
        flick_duration_ms: float = 12.0
    ) -> Dict[str, Any]:
        """
        Simuliert das 12ms Cursor Borrowing:
        1. Sichert Daniels physische Cursor-Position
        2. Springt zur Zielposition
        3. Sendet echten Hardware-Klick
        4. Wartet 12ms
        5. Stellt Daniels Original-Cursor wieder her
        """
        t_start = time.perf_counter()
        # Auf Windows: Echte Win32 Hardware Cursor Manipulation
        if self.system_is_windows:
            try:
                import ctypes
                class POINT(ctypes.Structure):
                    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                pt = POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                original_x, original_y = pt.x, pt.y
                
                # 1. Zum Ziel springen
                ctypes.windll.user32.SetCursorPos(target_x, target_y)
                # 2. Hardware Klick
                down_flag = 0x0002 if button == "left" else 0x0008
                up_flag = 0x0004 if button == "left" else 0x0010
                ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
            except Exception as e:
                logger.error(f"Win32 Cursor Borrow Fehler: {e}")
                original_x, original_y = (960, 540)
        else:
            # Auf Linux / Mock simulieren wir die Zeitmessung und den Ablauf
            original_x, original_y = (960, 540)  # Standard-Mitte als Referenz
        
        # Präziser 12ms Schlaf
        target_sleep_s = flick_duration_ms / 1000.0
        time.sleep(target_sleep_s)
        
        if self.system_is_windows:
            try:
                import ctypes
                # 3. Physischen Cursor wiederherstellen
                ctypes.windll.user32.SetCursorPos(original_x, original_y)
            except Exception:
                pass
        
        actual_duration_ms = (time.perf_counter() - t_start) * 1000.0
        self.stats["borrow_flicks_executed"] += 1
        
        result = {
            "action": "cursor_borrow_flick",
            "target_coords": [target_x, target_y],
            "restored_coords": [original_x, original_y],
            "target_duration_ms": flick_duration_ms,
            "actual_duration_ms": round(actual_duration_ms, 2),
            "status": "restored"
        }
        self.log_audit("cursor_borrow_flick_executed", result)
        return result

    # ==========================================
    # 5. Shared Mouse Lease Manager (Token-Passing)
    # ==========================================
    def request_mouse_lease(self, agent_id: str, duration_s: float = 3.0) -> Dict[str, Any]:
        now = time.time()
        locked, rem = self.is_locked()
        if locked:
            return {"granted": False, "reason": "hardware_lockout", "remaining_s": rem}
            
        if self.active_lease_holder and self.active_lease_holder != agent_id and now < self.lease_expires_at:
            return {
                "granted": False,
                "reason": "lease_held_by_other",
                "current_holder": self.active_lease_holder,
                "expires_in_s": round(self.lease_expires_at - now, 2)
            }
            
        self.active_lease_holder = agent_id
        self.lease_expires_at = now + duration_s
        self.log_audit("mouse_lease_granted", {"agent_id": agent_id, "duration_s": duration_s})
        return {
            "granted": True,
            "agent_id": agent_id,
            "duration_s": duration_s,
            "expires_at": self.lease_expires_at
        }

    def release_mouse_lease(self, agent_id: str):
        if self.active_lease_holder == agent_id:
            self.active_lease_holder = None
            self.lease_expires_at = 0.0
            self.log_audit("mouse_lease_released", {"agent_id": agent_id})

    # ==========================================
    # 6. ViGEm Gamepad Manager (Virtuelle Controller)
    # ==========================================
    def assign_gamepad(self, slot: int, agent_id: str) -> bool:
        if slot not in self.gamepads:
            return False
        self.gamepads[slot]["connected"] = True
        self.gamepads[slot]["assigned_agent"] = agent_id
        self.log_audit("gamepad_assigned", {"slot": slot, "agent_id": agent_id})
        return True

    def update_gamepad_state(
        self,
        slot: int,
        axes: Optional[Dict[str, float]] = None,
        buttons: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        if slot not in self.gamepads:
            return {"success": False, "error": f"Invalid slot {slot}"}
            
        gp = self.gamepads[slot]
        if axes:
            gp["axes"].update(axes)
        if buttons:
            gp["buttons"].update(buttons)
            
        self.stats["gamepad_events"] += 1
        return {
            "success": True,
            "slot": slot,
            "assigned_agent": gp["assigned_agent"],
            "axes": gp["axes"],
            "buttons": gp["buttons"]
        }

    # ==========================================
    # 7. Symmetrische Ausführung (Win32 oder X11)
    # ==========================================
    def dispatch_action(self, mutation: Dict[str, Any], bounding_box: Optional[List[int]] = None) -> Dict[str, Any]:
        self.stats["total_mutations"] += 1
        
        # 1. Lockout prüfen
        locked, rem = self.is_locked()
        if locked:
            self.stats["blocked_lockout"] += 1
            return {"success": False, "reason": "hardware_lockout", "remaining_s": rem}
            
        x = mutation.get("x", 0)
        y = mutation.get("y", 0)
        action = mutation.get("action", "click")
        button = mutation.get("button", "left")
        hwnd = mutation.get("hwnd", 0)
        mode = mutation.get("mode", "post_message")
        
        # 2. Klick-Käfig prüfen
        if not self.check_click_cage(x, y, bounding_box):
            return {"success": False, "reason": "click_cage_violation", "coords": [x, y]}

        # 3. Ausführung nach Modus
        if mode == "cursor_borrow_flick":
            flick_res = self.execute_cursor_borrow_flick(x, y, button=button)
            return {"success": True, "mode": "cursor_borrow_flick", "details": flick_res}
            
        elif mode == "post_message":
            # Relative Koordinaten zum Fenster berechnen wenn Bounding-Box da
            rel_x = x - (bounding_box[0] if bounding_box else 0)
            rel_y = y - (bounding_box[1] if bounding_box else 0)
            messages = self.generate_post_messages(hwnd, action, rel_x, rel_y, button)
            
            # Echte Win32 PostMessage Ausführung auf Windows
            if self.system_is_windows and hwnd:
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    for m in messages:
                        user32.PostMessageW(m["hwnd"], m["msg"], m["wparam"], m["lparam"])
                except Exception as e:
                    logger.error(f"Win32 PostMessage Dispatch Fehler: {e}")
                    
            return {
                "success": True,
                "mode": "post_message",
                "hwnd": hwnd,
                "relative_coords": [rel_x, rel_y],
                "messages_generated": len(messages),
                "messages": messages
            }
            
        elif mode == "x11":
            # Linux X11 Symmetrie
            cmd = ["xdotool", "mousemove", str(x), str(y), "click", "1" if button == "left" else "3"]
            try:
                subprocess.run(cmd, capture_output=True, timeout=1.0)
            except Exception as e:
                logger.warning(f"xdotool Ausführung fehlgeschlagen: {e}")
            return {"success": True, "mode": "x11", "command": cmd}

        return {"success": False, "reason": f"Unknown mode {mode}"}
