"""Native Windows overlay entry point for the Augen-und-Hände bridge.

This is a real desktop program, not a browser page.  The first native brick is
deliberately read-only: it opens an always-on-top overlay, connects to the
Greenfield TargetRegistry, shows real terminal provenance, and keeps input
behind the existing capability/lease gates.
"""

from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


HERE = Path(__file__).resolve()
SRC = HERE.parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from augen_haende_bridge.target_registry import TargetRecord, TargetRegistry  # noqa: E402
from augen_haende_bridge.bridge_runtime import BridgeRuntime  # noqa: E402
from augen_haende_bridge.windows_capture import WindowsScreenCapture  # noqa: E402
from augen_haende_bridge.windows_scanner import WindowsWindowScanner  # noqa: E402
from augen_haende_bridge.read_only_binding import (  # noqa: E402
    BindingError,
    BindingReadback,
    ReadOnlyTargetBinding,
    create_read_only_binding,
    read_back_binding,
)


BACKGROUND = "#0c141d"
PANEL = "#101e2a"
PANEL_2 = "#142737"
GRID = "#1b3345"
TEXT = "#d9e7ee"
MUTED = "#7895a5"
CYAN = "#69d7ff"
GOLD = "#e6bd58"
GREEN = "#61d6a0"
RED = "#f08080"


@dataclass
class AgentNode:
    agent_id: str
    label: str
    color: str
    x: float
    y: float


class BridgeOverlay:
    """Small native overlay shell that is safe to run before Windows adapters."""

    def __init__(self, registry: TargetRegistry | None = None) -> None:
        self.registry = registry or TargetRegistry()
        self.root = tk.Tk(className="AugenUndHaendeBridge")
        self.root.title("Augen & Hände Bridge")
        self.root.configure(bg=BACKGROUND)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        # Durchsichtigkeit je Bereich (Startwert 66 %) braucht ein natives Layered Window; Tk kann
        # nur das ganze Fenster durchsichtig machen. Bis dahin bleibt das Fenster deckend.
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<F12>", lambda _event: self.emergency_stop())
        self.root.bind("<Escape>", lambda _event: self.close())

        # The bridge is an overlay window, not a replacement desktop.
        # Keep a bounded, movable starting rectangle so the real application
        # beneath it remains visible and usable.
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.width = min(1180, max(900, screen_width - 80))
        self.height = min(760, max(620, screen_height - 120))
        self.root.minsize(900, 620)
        self.root.resizable(True, True)
        left = max(20, (screen_width - self.width) // 2)
        top = max(20, (screen_height - self.height) // 2)
        self.root.geometry(f"{self.width}x{self.height}+{left}+{top}")
        self.canvas = tk.Canvas(
            self.root,
            bg=BACKGROUND,
            highlightthickness=0,
            bd=0,
            cursor="arrow",
        )
        self.canvas.pack(fill="both", expand=True)

        self.selected_target_id = self.registry.selected_target_id
        self.selected_agent_id: str | None = None
        self.not_aus = False
        self.status = "bereit — Beobachtung aktiv, Eingabe gesperrt"
        self.banner_after: str | None = None
        self.bridge_runtime: BridgeRuntime | None = None
        self.inventory_request_id: str | None = None
        self.inventory_request_nonce = 0
        self.inventory_request_after: str | None = None
        self.last_inventory_captured_at_ms = -1
        self.native_capture = WindowsScreenCapture()
        self.native_scanner = WindowsWindowScanner()
        self.latest_native_frame = None
        self.latest_native_scan = None
        self.native_binding: ReadOnlyTargetBinding | None = None
        self.native_binding_readback: BindingReadback | None = None
        self.native_binding_counter = 0
        self.drag_origin: tuple[str, float, float] | None = None
        self.nodes = self._make_nodes()
        self.node_items: dict[str, tuple[int, int, int]] = {}
        self._draw()
        self._start_optional_bridge()
        if os.environ.get("BRIDGE_NATIVE_SCAN_ON_START") == "1":
            self.root.after(250, self.scan_windows_targets)

    def _start_optional_bridge(self) -> None:
        url = os.environ.get("BRIDGE_URL")
        token = os.environ.get("BRIDGE_TOKEN")
        if not url and not token:
            return
        if not url or not token:
            self.status = "Bridge-Konfiguration unvollständig — offline"
            self._draw()
            return
        try:
            self.bridge_runtime = BridgeRuntime(url, token, on_event=self._bridge_event)
            self.bridge_runtime.start()
            self.status = "Bridge verbindet …"
            self._draw()
        except (ValueError, RuntimeError) as exc:
            self.status = f"Bridge abgewiesen: {exc}"
            self._draw()

    def _bridge_event(self, event: dict[str, object]) -> None:
        self.root.after(0, lambda: self._apply_bridge_event(event))

    def _apply_bridge_event(self, event: dict[str, object]) -> None:
        kind = event.get("kind")
        if kind == "runtime.connected":
            self.status = "Bridge verbunden — Zielinventar wird gelesen …"
            self._request_bridge_inventory()
        elif kind == "runtime.inventory_requested":
            request_id = event.get("request_id")
            if isinstance(request_id, str):
                self._inventory_request_started(request_id)
        elif kind == "event" and event.get("event_kind") == "say":
            payload = event.get("payload")
            text = payload.get("text") if isinstance(payload, dict) else None
            if isinstance(text, str):
                self.banner_text = text
                self.status = "Bridge-Nachricht empfangen"
                if self.banner_after:
                    self.root.after_cancel(self.banner_after)
                self.banner_after = self.root.after(3300, self._clear_banner)
        elif kind == "event" and event.get("event_kind") == "target_inventory":
            payload = event.get("payload")
            if not isinstance(payload, dict):
                self.status = "Bridge-Readback: ungültige Antwort"
            elif payload.get("request_id") != self.inventory_request_id:
                self.status = "Bridge-Readback: verspätete/fremde Antwort ignoriert"
            elif payload.get("status") != "ok":
                self._clear_inventory_request()
                self.status = f"Bridge-Readback: {payload.get('status', 'unbekannt')}"
            else:
                captured_at_ms = payload.get("captured_at_ms")
                if type(captured_at_ms) is not int or captured_at_ms <= self.last_inventory_captured_at_ms:
                    self.status = "Bridge-Readback: veraltete Antwort ignoriert"
                else:
                    try:
                        count = self.registry.apply_remote_inventory(payload)
                    except ValueError as exc:
                        self.status = f"Bridge-Readback abgewiesen: {exc}"
                    else:
                        self.last_inventory_captured_at_ms = captured_at_ms
                        self._clear_inventory_request()
                        self.selected_target_id = self.registry.selected_target_id
                        self.status = f"Bridge-Readback: {count} VPS-Terminal(e) übernommen"
        elif kind == "runtime.failed":
            self._clear_inventory_request()
            self.status = f"Bridge getrennt: {event.get('reason', 'unbekannt')}"
        elif kind == "error":
            self.status = f"Bridge-Fehler: {event.get('reason', 'unbekannt')}"
        self._draw()

    def _make_nodes(self) -> dict[str, AgentNode]:
        # Rauten gibt es nur fuer Agenten, die es wirklich gibt und die gebunden sind (R023,
        # START_HIER Regel 4). Bis die App ihre Agenten aus einer echten Quelle bekommt, ist
        # diese Ebene leer - es wird nichts vorgetaeuscht.
        return {}

    def _draw(self) -> None:
        self.canvas.delete("all")
        self.node_items.clear()
        title = "Augen & Hände Bridge"
        if getattr(self, "latest_native_scan", None) is not None:
            title += f" · scan-received:{len(self.latest_native_scan.items)}"
        if getattr(self, "native_binding_readback", None) is not None and self.native_binding_readback.valid:
            title += " · binding-readback"
        if getattr(self, "banner_text", ""):
            title += " · say-received"
        self.root.title(title)
        self._draw_grid()
        self._draw_header()
        self._draw_target_rail()
        self._draw_nodes()
        self._draw_regie()
        self._draw_terminals()
        self._draw_banner()

    def _draw_grid(self) -> None:
        for x in range(0, self.width, 32):
            self.canvas.create_line(x, 0, x, self.height, fill=GRID, width=1)
        for y in range(0, self.height, 32):
            self.canvas.create_line(0, y, self.width, y, fill=GRID, width=1)

    def _draw_header(self) -> None:
        self.canvas.create_text(
            24,
            24,
            anchor="nw",
            text="AUGEN & HÄNDE — BRIDGE OVERLAY",
            fill=CYAN,
            font=("Segoe UI", 13, "bold"),
        )
        self.canvas.create_text(
            self.width - 24,
            26,
            anchor="ne",
            text="ECHTES PROGRAMM · OVERLAY · BEOBACHTUNG",
            fill=GREEN if not self.not_aus else RED,
            font=("Segoe UI", 10, "bold"),
        )
        self.canvas.create_text(
            self.width - 24,
            50,
            anchor="ne",
            text=self.status,
            fill=MUTED,
            font=("Segoe UI", 9),
        )

    def _draw_target_rail(self) -> None:
        x0, y0, x1, y1 = 24, 70, 270, self.height - 220
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=PANEL, outline=CYAN, width=1)
        self.canvas.create_text(x0 + 14, y0 + 14, anchor="nw", text="ZIELE / BINDUNGEN", fill=GOLD, font=("Segoe UI", 10, "bold"))
        self._button(
            x0 + 10,
            y1 - 72,
            x1 - 10,
            y1 - 40,
            "Windows-Fensterscan",
            self.scan_windows_targets,
            active=False,
        )
        self._button(
            x0 + 10,
            y1 - 36,
            x1 - 10,
            y1 - 8,
            "Bridge-Readback",
            self.refresh_bridge_targets,
            active=False,
        )
        y = y0 + 48
        for record in list(self.registry.records.values())[:8]:
            active = record.target.id == self.selected_target_id
            fill = PANEL_2 if active else PANEL
            outline = GOLD if active else GRID
            self.canvas.create_rectangle(x0 + 10, y, x1 - 10, y + 48, fill=fill, outline=outline, width=1)
            self.canvas.create_text(x0 + 18, y + 9, anchor="nw", text=record.target.label[:28], fill=TEXT, font=("Segoe UI", 9, "bold" if active else "normal"))
            self.canvas.create_text(x0 + 18, y + 28, anchor="nw", text=f"{record.source} · {record.availability}", fill=GREEN if record.availability == "available" else MUTED, font=("Segoe UI", 8))
            self._bind_rect((x0 + 10, y, x1 - 10, y + 48), lambda _event, target_id=record.target.id: self.select_target(target_id))
            y += 56
        # Native scanner entries are shown only after an explicit scan. They
        # are separate from the VPS registry and selection remains observe-only.
        native_scan = getattr(self, "latest_native_scan", None)
        if native_scan is not None:
            for item in native_scan.items:
                if y + 48 > y1 - 82:
                    break
                active = item.target_id == self.selected_target_id
                fill = PANEL_2 if active else PANEL
                outline = GOLD if active else CYAN
                self.canvas.create_rectangle(x0 + 10, y, x1 - 10, y + 48, fill=fill, outline=outline, width=1)
                self.canvas.create_text(x0 + 18, y + 9, anchor="nw", text=item.label[:28], fill=TEXT, font=("Segoe UI", 9, "bold" if active else "normal"))
                self.canvas.create_text(x0 + 18, y + 28, anchor="nw", text=f"{item.source} · {item.availability}", fill=GREEN if item.availability == "available" else MUTED, font=("Segoe UI", 8))
                self._bind_rect((x0 + 10, y, x1 - 10, y + 48), lambda _event, target_id=item.target_id: self.select_target(target_id))
                y += 56

    def _draw_nodes(self) -> None:
        for node in self.nodes.values():
            size = 58
            points = (node.x, node.y - size, node.x + size, node.y, node.x, node.y + size, node.x - size, node.y)
            poly = self.canvas.create_polygon(*points, outline=node.color, fill="#152532", width=2, tags=(f"node:{node.agent_id}",))
            label = self.canvas.create_text(node.x, node.y - 5, text=node.label, fill=TEXT, font=("Segoe UI", 10, "bold"), tags=(f"node:{node.agent_id}",))
            hint = self.canvas.create_text(node.x, node.y + 17, text="◆ Eingabe / Chat", fill=MUTED, font=("Segoe UI", 8), tags=(f"node:{node.agent_id}",))
            self.node_items[node.agent_id] = (poly, label, hint)
            for item in (poly, label, hint):
                self.canvas.tag_bind(item, "<ButtonPress-1>", lambda event, agent_id=node.agent_id: self._start_drag(event, agent_id))
                self.canvas.tag_bind(item, "<B1-Motion>", lambda event, agent_id=node.agent_id: self._drag(event, agent_id))
                self.canvas.tag_bind(item, "<ButtonRelease-1>", lambda _event, agent_id=node.agent_id: self._finish_drag(agent_id))

    def _draw_regie(self) -> None:
        x0, y0, x1, y1 = 24, self.height - 205, 270, self.height - 24
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=PANEL, outline=CYAN, width=1)
        self.canvas.create_text(x0 + 14, y0 + 14, anchor="nw", text="REGIE", fill=GOLD, font=("Segoe UI", 10, "bold"))
        agent = self.nodes.get(self.selected_agent_id)
        agent_text = f"Agent: {agent.label}" if agent else "Agent: keiner gebunden"
        self.canvas.create_text(x0 + 14, y0 + 44, anchor="nw", text=agent_text, fill=TEXT, font=("Segoe UI", 10))
        self._button(x0 + 14, y0 + 148, x1 - 14, y0 + 179, "Spruch senden", self.say, active=False)
        self.canvas.create_text(x0 + 14, y1 - 12, anchor="sw", text="pro Agent · pro Ziel · F12 Not-Aus", fill=MUTED, font=("Segoe UI", 8))

    def _draw_terminals(self) -> None:
        left = 300
        gap = 16
        width = max(190, (self.width - left - 30 - gap * 3) // 4)
        top = self.height - 205
        terminal_records = [
            record for record in self.registry.records.values()
            if record.target.kind.value == "linux.terminal"
        ][:4]
        for index in range(4):
            x0 = left + index * (width + gap)
            x1 = x0 + width
            self.canvas.create_rectangle(x0, top, x1, self.height - 24, fill=PANEL, outline=GRID, width=1)
            self.canvas.create_text(x0 + 12, top + 12, anchor="nw", text=f"Terminal ({index + 1})", fill=TEXT, font=("Segoe UI", 10, "bold"))
            target_id = terminal_records[index].target.id if index < len(terminal_records) else None
            record = terminal_records[index] if index < len(terminal_records) else None
            if record is None:
                line = "nicht registriert"
                provenance = "unavailable"
            else:
                line = record.target.label[:25]
                provenance = f"{record.source} · {record.availability}"
            self.canvas.create_text(x0 + 12, top + 42, anchor="nw", text=line, fill=GREEN if provenance.startswith("real") else TEXT, font=("Consolas", 9))
            self.canvas.create_text(x0 + 12, top + 62, anchor="nw", text=provenance, fill=MUTED, font=("Consolas", 8))
            self._button(x0 + 12, self.height - 62, x1 - 12, self.height - 32, "Fensterscanner", lambda target_id=target_id: self.inspect_terminal(target_id), active=False)

    def _draw_banner(self) -> None:
        if getattr(self, "banner_text", None):
            self.canvas.create_text(self.width / 2, 180, text=self.banner_text, fill=TEXT, font=("Segoe UI", 14, "bold"))

    def _button(self, x0: float, y0: float, x1: float, y1: float, text: str, command: Callable[[], None], *, active: bool) -> None:
        fill = "#204633" if active else PANEL_2
        outline = GREEN if active else GRID
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=1)
        self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=text, fill=TEXT, font=("Segoe UI", 9))
        self._bind_rect((x0, y0, x1, y1), lambda _event: command())

    def _bind_rect(self, rect: tuple[float, float, float, float], command: Callable[[tk.Event], None]) -> None:
        x0, y0, x1, y1 = rect
        tag = self.canvas.create_rectangle(x0, y0, x1, y1, outline="", fill="", tags=("hitbox",))
        self.canvas.tag_bind(tag, "<ButtonRelease-1>", command)

    def select_target(self, target_id: str) -> None:
        native_scan = getattr(self, "latest_native_scan", None)
        if native_scan is not None and any(item.target_id == target_id for item in native_scan.items):
            if self.selected_agent_id is None:
                self.status = "Kein Agent gebunden — ein Ziel wird immer an einen Agenten gebunden"
                self._draw()
                return
            self.native_binding_counter += 1
            try:
                binding = create_read_only_binding(
                    native_scan,
                    binding_id=f"native-binding-{self.native_binding_counter}",
                    agent_id=self.selected_agent_id,
                    target_id=target_id,
                )
                readback = read_back_binding(binding, native_scan)
            except BindingError as exc:
                self.native_binding = None
                self.native_binding_readback = None
                self.status = f"Zielbindung abgewiesen: {exc}"
            else:
                self.native_binding = binding
                self.native_binding_readback = readback
                if readback.valid:
                    self.selected_target_id = target_id
                    self.status = f"Ziel ausgewählt · {target_id} · observe-only"
                else:
                    self.status = f"Zielbindung stale: {readback.reason}"
            self._draw()
            return
        try:
            record = self.registry.select(target_id)
        except KeyError:
            self.status = f"Ziel unbekannt: {target_id}"
        else:
            self.selected_target_id = record.target.id
            self.status = f"Ziel gebunden: {record.target.label} · {record.source}/{record.availability}"
        self._draw()

    def _clear_inventory_request(self) -> None:
        self.inventory_request_id = None
        if self.inventory_request_after:
            self.root.after_cancel(self.inventory_request_after)
            self.inventory_request_after = None

    def _inventory_request_timeout(self, nonce: int) -> None:
        if nonce == self.inventory_request_nonce and self.inventory_request_id is not None:
            self.inventory_request_id = None
            self.inventory_request_after = None
            self.status = "Bridge-Readback: Antwort-Timeout"
            self._draw()

    def _request_bridge_inventory(self) -> None:
        if self.bridge_runtime is None or not self.bridge_runtime.connected:
            self.status = "Bridge-Readback nicht verfügbar — offline"
            self._draw()
            return
        self.inventory_request_nonce += 1
        nonce = self.inventory_request_nonce
        self._clear_inventory_request()

        def request() -> None:
            try:
                self.bridge_runtime.request_target_inventory()
            except RuntimeError as exc:
                self.root.after(0, lambda: self._inventory_request_failed(nonce, str(exc)))

        threading.Thread(target=request, name="bridge-inventory-request", daemon=True).start()

    def _inventory_request_started(self, request_id: str) -> None:
        self.inventory_request_id = request_id
        self.inventory_request_after = self.root.after(
            6000, lambda: self._inventory_request_timeout(self.inventory_request_nonce)
        )
        self.status = f"Bridge-Readback angefordert · {request_id[:12]}"
        self._draw()

    def _inventory_request_failed(self, nonce: int, reason: str) -> None:
        if nonce != self.inventory_request_nonce:
            return
        self._clear_inventory_request()
        self.status = f"Bridge-Readback abgewiesen: {reason}"
        self._draw()

    def refresh_bridge_targets(self) -> None:
        self._request_bridge_inventory()

    def scan_windows_targets(self) -> None:
        """Capture and inventory Windows once; never bind or inject input."""

        if not self.native_capture.available or not self.native_scanner.available:
            self.status = "Windows-Fensterscan: native Plattform nicht verfügbar"
            self._draw()
            return
        try:
            frame = self.native_capture.capture()
            snapshot = self.native_scanner.scan(
                frame_ref=frame.frame_ref,
                frame_hash=frame.frame_hash,
                captured_at_ms=frame.captured_at_ms,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            self.status = f"Windows-Fensterscan abgewiesen: {exc}"
            self._draw()
            return
        self.latest_native_frame = frame
        self.latest_native_scan = snapshot
        if self.native_binding is not None:
            self.native_binding_readback = read_back_binding(self.native_binding, snapshot)
        self.status = f"Windows-Fensterscan: {len(snapshot.items)} Ziel(e) · {frame.width}×{frame.height}"
        self._draw()
        auto_bind_target = os.environ.get("BRIDGE_NATIVE_BIND_TARGET_ID")
        if auto_bind_target:
            self.select_target(auto_bind_target)

    def inspect_terminal(self, target_id: str) -> None:
        record = self.registry.records.get(target_id)
        if record is None:
            self.status = f"Fensterscanner: {target_id} nicht registriert"
        else:
            snapshot = self.registry.inspect(target_id)
            self.status = f"Scanner: {record.target.label} · {snapshot.status} · read-only"
        self._draw()

    def say(self) -> None:
        if self.not_aus:
            self.status = "Not-Aus aktiv — Regiespruch blockiert"
        elif self.selected_agent_id not in self.nodes:
            self.status = "Kein Agent gebunden — kein Regiespruch"
        else:
            self.banner_text = f"{self.nodes[self.selected_agent_id].label}: Regiespruch sichtbar"
            self.status = "Regiespruch 3,3 s sichtbar"
            if self.banner_after:
                self.root.after_cancel(self.banner_after)
            self.banner_after = self.root.after(3300, self._clear_banner)
        self._draw()

    def _clear_banner(self) -> None:
        self.banner_text = ""
        self.banner_after = None
        self._draw()

    def _start_drag(self, event: tk.Event, agent_id: str) -> None:
        node = self.nodes[agent_id]
        self.drag_origin = (agent_id, event.x - node.x, event.y - node.y)
        self.selected_agent_id = agent_id

    def _drag(self, event: tk.Event, agent_id: str) -> None:
        if not self.drag_origin or self.drag_origin[0] != agent_id:
            return
        node = self.nodes[agent_id]
        node.x = event.x - self.drag_origin[1]
        node.y = event.y - self.drag_origin[2]
        self._draw()

    def _finish_drag(self, agent_id: str) -> None:
        if self.drag_origin and self.drag_origin[0] == agent_id:
            self.status = f"Raute {self.nodes[agent_id].label} verschoben"
        self.drag_origin = None
        self._draw()

    def emergency_stop(self) -> None:
        self.not_aus = True
        self.status = "NOT-AUS — alle Overlay-Fähigkeiten gesperrt"
        self._draw()

    def close(self) -> None:
        if self.banner_after:
            self.root.after_cancel(self.banner_after)
        self._clear_inventory_request()
        if self.bridge_runtime is not None:
            self.bridge_runtime.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    BridgeOverlay().run()


if __name__ == "__main__":
    main()
