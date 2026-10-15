"""DOM-only control channel for a Firefox Remote Agent (WebDriver BiDi).

This module is deliberately independent of screenshots, X11 capture and
Playwright.  It talks to Firefox's browser-level BiDi endpoint, reads the
actual document/canvas DOM, and sends browser input actions.  A native Earth
Pro window must never be passed to this adapter: it is for Firefox web pages
such as Google Earth Web only.
"""

from __future__ import annotations

import itertools
import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from websockets.sync.client import connect


class FirefoxDomError(RuntimeError):
    """A Firefox BiDi transport or browser-command failure."""


@dataclass(frozen=True)
class FirefoxDomTarget:
    context_id: str
    url: str
    title: str


def discover_websocket_url(host: str = "127.0.0.1", port: int = 9222) -> str:
    """Discover Firefox's BiDi WebSocket URL, with its documented fallback."""
    candidates = (
        f"http://{host}:{port}/json/version",
        f"http://{host}:{port}/json",
    )
    for endpoint in candidates:
        try:
            with urllib.request.urlopen(endpoint, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            continue
        if isinstance(payload, Mapping):
            for key in ("webSocketUrl", "webSocketDebuggerUrl"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return value
            if isinstance(payload.get("value"), Mapping):
                value = payload["value"].get("webSocketUrl")
                if isinstance(value, str) and value:
                    return value
    return f"ws://{host}:{port}/session"


class FirefoxDomSession:
    """Small synchronous WebDriver BiDi client for model-free DOM work."""

    def __init__(self, websocket_url: str | None = None, *, timeout: float = 10.0):
        self.websocket_url = websocket_url or os.getenv(
            "AI_STROM_BRUECKE_FIREFOX_BIDI_URL",
            discover_websocket_url(
                os.getenv("AI_STROM_BRUECKE_FIREFOX_BIDI_HOST", "127.0.0.1"),
                int(os.getenv("AI_STROM_BRUECKE_FIREFOX_BIDI_PORT", "9222")),
            ),
        )
        self.timeout = timeout
        self._socket: Any = None
        self._ids = itertools.count(1)
        self.events: list[dict[str, Any]] = []
        self.session_id: str | None = None
        self.held_buttons: set[str] = set()
        self.held_keys: set[str] = set()

    def connect(self) -> "FirefoxDomSession":
        try:
            self._socket = connect(self.websocket_url, open_timeout=self.timeout, close_timeout=self.timeout)
            result = self.command(
                "session.new",
                {"capabilities": {"alwaysMatch": {"acceptInsecureCerts": True}}},
            )
        except Exception as exc:  # pragma: no cover - transport details vary by Firefox build
            self.close()
            raise FirefoxDomError(f"Firefox-BiDi nicht erreichbar: {self.websocket_url}: {exc}") from exc
        self.session_id = result.get("sessionId") if isinstance(result, Mapping) else None
        return self

    def close(self) -> None:
        if self._socket is not None:
            try:
                if self.session_id is not None:
                    command_id = next(self._ids)
                    self._socket.send(json.dumps({"id": command_id, "method": "session.end", "params": {}}))
                    # Drain the matching response so Firefox can release the
                    # session before the transport is closed.
                    for _ in range(20):
                        message = json.loads(self._socket.recv(timeout=self.timeout))
                        if message.get("id") == command_id:
                            break
            except Exception:
                # Cleanup must never hide the original browser/test error.
                pass
            try:
                self._socket.close()
            finally:
                self._socket = None
                self.session_id = None
                self.held_buttons.clear()
                self.held_keys.clear()

    def __enter__(self) -> "FirefoxDomSession":
        return self.connect()

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def command(self, method: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if self._socket is None:
            raise FirefoxDomError("Firefox-BiDi-Sitzung ist nicht verbunden")
        command_id = next(self._ids)
        self._socket.send(json.dumps({"id": command_id, "method": method, "params": dict(params or {})}))
        while True:
            try:
                message = json.loads(self._socket.recv(timeout=self.timeout))
            except Exception as exc:
                raise FirefoxDomError(f"Firefox-BiDi-Antwort fehlt für {method}: {exc}") from exc
            if message.get("type") == "event":
                self.events.append(message)
                continue
            if message.get("id") != command_id:
                continue
            if message.get("type") == "error" or message.get("error"):
                raise FirefoxDomError(f"Firefox-BiDi {method} fehlgeschlagen: {message}")
            result = message.get("result")
            if not isinstance(result, Mapping):
                raise FirefoxDomError(f"Firefox-BiDi {method} lieferte kein Ergebnis: {message}")
            return dict(result)

    def contexts(self) -> list[dict[str, Any]]:
        result = self.command("browsingContext.getTree", {"maxDepth": 0})
        return list(result.get("contexts") or [])

    def target(self, context_id: str | None = None) -> FirefoxDomTarget:
        contexts = self.contexts()
        if context_id:
            context = next((item for item in contexts if item.get("context") == context_id), None)
        else:
            context = contexts[0] if contexts else None
        if not context:
            raise FirefoxDomError("Kein Firefox-DOM-Kontext gefunden")
        return FirefoxDomTarget(
            context_id=str(context["context"]),
            url=str(context.get("url", "")),
            title=str(context.get("userContext", "")),
        )

    def evaluate(self, expression: str, context_id: str) -> Any:
        result = self.command(
            "script.evaluate",
            {
                "expression": expression,
                "target": {"context": context_id},
                "awaitPromise": True,
                "resultOwnership": "none",
            },
        )
        value = result.get("result")
        if not isinstance(value, Mapping):
            raise FirefoxDomError(f"DOM-Ausdruck lieferte keinen Wert: {result}")
        if value.get("type") == "exception":
            raise FirefoxDomError(f"DOM-Ausdruck fehlgeschlagen: {value}")
        return _deserialize_remote_value(value)

    def inspect_google_earth(self, context_id: str) -> dict[str, Any]:
        """Read Google Earth Web's DOM/canvas facts without a frame."""
        value = self.evaluate(
            """(() => ({
              url: location.href,
              title: document.title,
              dom_controls: [...new Set([...document.querySelectorAll(
                'button,[role="button"],[aria-label]'
              )])].map(node => ({
                tag: node.tagName.toLowerCase(),
                role: node.getAttribute('role'),
                aria_label: node.getAttribute('aria-label'),
                text: (node.innerText || '').trim()
              })).filter(item => item.aria_label || item.text),
              canvases: [...document.querySelectorAll('canvas')].map(canvas => {
                const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
                return {width: canvas.width, height: canvas.height, webgl: !!gl};
              }),
              screenshot_used: false,
              native_x11: false,
              semantic_place_dom: false
            }))()""",
            context_id,
        )
        if not isinstance(value, Mapping):
            raise FirefoxDomError("Google-Earth-DOM-Bericht ist kein Objekt")
        report = dict(value)
        canvases = list(report.get("canvases") or [])
        report["map_surface"] = "canvas-webgl" if any(item.get("webgl") for item in canvases) else "canvas"
        report["model_calls"] = 0
        return report

    def navigate(self, context_id: str, url: str) -> dict[str, Any]:
        return self.command("browsingContext.navigate", {"context": context_id, "url": url, "wait": "complete"})

    def click_selector(self, context_id: str, selector: str) -> Any:
        escaped = json.dumps(selector)
        return self.evaluate(
            f"""(() => {{ const node = document.querySelector({escaped}); if (!node) throw new Error('selector not found'); node.click(); return true; }})()""",
            context_id,
        )

    def pointer_move(self, context_id: str, x: int, y: int) -> dict[str, Any]:
        return self.command(
            "input.performActions",
            {
                "context": context_id,
                "actions": [{"type": "pointer", "id": "ai-strom-pointer", "parameters": {"pointerType": "mouse"}, "actions": [{"type": "pointerMove", "x": int(x), "y": int(y), "origin": "viewport"}]}],
            },
        )

    def pointer_down(self, context_id: str, x: int, y: int, button: str = "left") -> dict[str, Any]:
        button_number = {"left": 0, "middle": 1, "right": 2}[button]
        result = self.command(
            "input.performActions",
            {"context": context_id, "actions": [{"type": "pointer", "id": "ai-strom-pointer", "parameters": {"pointerType": "mouse"}, "actions": [{"type": "pointerMove", "x": int(x), "y": int(y), "origin": "viewport"}, {"type": "pointerDown", "button": button_number}]}]},
        )
        self.held_buttons.add(button)
        return result

    def pointer_up(self, context_id: str, button: str = "left") -> dict[str, Any]:
        button_number = {"left": 0, "middle": 1, "right": 2}[button]
        result = self.command(
            "input.performActions",
            {"context": context_id, "actions": [{"type": "pointer", "id": "ai-strom-pointer", "parameters": {"pointerType": "mouse"}, "actions": [{"type": "pointerUp", "button": button_number}]}]},
        )
        self.held_buttons.discard(button)
        return result

    def wheel(self, context_id: str, delta_x: int = 0, delta_y: int = 0, x: int = 0, y: int = 0) -> dict[str, Any]:
        return self.command(
            "input.performActions",
            {"context": context_id, "actions": [{"type": "wheel", "id": "ai-strom-wheel", "actions": [{"type": "scroll", "x": int(x), "y": int(y), "deltaX": int(delta_x), "deltaY": int(delta_y), "duration": 0}]}]},
        )

    def key_down(self, context_id: str, key: str) -> dict[str, Any]:
        result = self.command(
            "input.performActions",
            {"context": context_id, "actions": [{"type": "key", "id": "ai-strom-keyboard", "actions": [{"type": "keyDown", "value": key}]}]},
        )
        self.held_keys.add(key)
        return result

    def key_up(self, context_id: str, key: str) -> dict[str, Any]:
        result = self.command(
            "input.performActions",
            {"context": context_id, "actions": [{"type": "key", "id": "ai-strom-keyboard", "actions": [{"type": "keyUp", "value": key}]}]},
        )
        self.held_keys.discard(key)
        return result

    def release_actions(self, context_id: str) -> dict[str, Any]:
        result = self.command("input.releaseActions", {"context": context_id})
        self.held_buttons.clear()
        self.held_keys.clear()
        return result

    def pointer_click(self, context_id: str, x: int, y: int, button: str = "left") -> dict[str, Any]:
        button_number = {"left": 0, "middle": 1, "right": 2}[button]
        actions = [{"type": "pointerMove", "x": int(x), "y": int(y), "origin": "viewport"}, {"type": "pointerDown", "button": button_number}, {"type": "pointerUp", "button": button_number}]
        return self.command(
            "input.performActions",
            {"context": context_id, "actions": [{"type": "pointer", "id": "ai-strom-pointer", "parameters": {"pointerType": "mouse"}, "actions": actions}]},
        )


def _deserialize_remote_value(value: Mapping[str, Any]) -> Any:
    """Convert Firefox's BiDi remote-value envelope to ordinary Python."""
    value_type = value.get("type")
    raw = value.get("value")
    if value_type == "object" and isinstance(raw, list):
        return {str(pair[0]): _deserialize_remote_value(pair[1]) for pair in raw if isinstance(pair, list) and len(pair) == 2 and isinstance(pair[1], Mapping)}
    if value_type == "array" and isinstance(raw, list):
        return [_deserialize_remote_value(item) if isinstance(item, Mapping) else item for item in raw]
    if value_type in {"null", "undefined"}:
        return None
    if value_type in {"string", "number", "boolean", "bigint"}:
        return raw
    return raw
