"""Firefox BiDi additions used only by the opt-in visual bridge."""

from __future__ import annotations

import base64
import binascii
import os
from typing import Any, Mapping

from websockets.sync.client import connect

from .firefox_dom import FirefoxDomError, FirefoxDomSession


SCREENSHOT_FORMAT = {"type": "image/jpeg", "quality": 0.3}


class FirefoxVisualSession(FirefoxDomSession):
    """DOM session with an explicit Firefox BiDi screenshot operation."""

    def connect(self) -> "FirefoxVisualSession":
        """Connect with a larger BiDi frame limit for PNG response payloads."""
        try:
            max_size = int(os.getenv("AI_STROM_BRUECKE_VISUAL_MAX_MESSAGE_BYTES", "8388608"))
            self._socket = connect(
                self.websocket_url,
                open_timeout=self.timeout,
                close_timeout=self.timeout,
                max_size=max_size,
            )
            result = self.command(
                "session.new",
                {"capabilities": {"alwaysMatch": {"acceptInsecureCerts": True}}},
            )
        except Exception as exc:  # pragma: no cover - transport details vary by Firefox build
            self.close()
            raise FirefoxDomError(f"Firefox-BiDi nicht erreichbar: {self.websocket_url}: {exc}") from exc
        self.session_id = result.get("sessionId") if isinstance(result, dict) else None
        return self

    def capture_screenshot(self, context_id: str, *, origin: str = "viewport") -> bytes:
        if origin not in {"viewport", "document"}:
            raise FirefoxDomError(f"Unbekannter Screenshot-Ursprung: {origin}")
        result = self.command(
            "browsingContext.captureScreenshot",
            {"context": context_id, "origin": origin, "format": dict(SCREENSHOT_FORMAT)},
        )
        encoded = result.get("data")
        if not isinstance(encoded, str) or not encoded:
            raise FirefoxDomError(f"Firefox-BiDi-Screenshot lieferte keine Daten: {result}")
        try:
            return base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise FirefoxDomError("Firefox-BiDi-Screenshot war kein gültiges Base64-PNG") from exc

    def activate_context(self, context_id: str) -> dict[str, Any]:
        """Bring the controlled Firefox browsing context to the foreground."""
        return self.command("browsingContext.activate", {"context": context_id})

    def perform_input_batch(self, context_id: str, commands: list[Mapping[str, Any]]) -> dict[str, Any]:
        """Dispatch physical keyboard/mouse commands as one BiDi action tick.

        No observation is performed here.  The caller owns the lease and can
        start its 100 ms observation loop only after this single command has
        returned.  Keyboard and pointer sources run in parallel according to
        WebDriver's action timeline; commands of the same source stay ordered.
        """
        keyboard: list[dict[str, Any]] = []
        pointer: list[dict[str, Any]] = []
        wheel: list[dict[str, Any]] = []

        for index, item in enumerate(commands):
            kind = item.get("type")
            if kind == "key":
                key = item.get("key")
                if not isinstance(key, str) or not key:
                    raise FirefoxDomError(f"Batch command {index}: key fehlt")
                keyboard.extend(
                    [{"type": "keyDown", "value": key}, {"type": "keyUp", "value": key}]
                )
            elif kind == "keyhold":
                key = item.get("key")
                duration_ms = item.get("duration_ms", 350)
                if not isinstance(key, str) or not key:
                    raise FirefoxDomError(f"Batch command {index}: key fehlt")
                if not isinstance(duration_ms, int) or duration_ms < 0:
                    raise FirefoxDomError(f"Batch command {index}: duration_ms ist ungültig")
                keyboard.extend(
                    [
                        {"type": "keyDown", "value": key},
                        {"type": "pause", "duration": duration_ms},
                        {"type": "keyUp", "value": key},
                    ]
                )
            elif kind == "click":
                try:
                    x = int(item["x"])
                    y = int(item["y"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise FirefoxDomError(f"Batch command {index}: click x/y fehlen") from exc
                button = {"left": 0, "middle": 1, "right": 2}.get(item.get("button", "left"))
                if button is None:
                    raise FirefoxDomError(f"Batch command {index}: button ist ungültig")
                pointer.extend(
                    [
                        {"type": "pointerMove", "x": x, "y": y, "origin": "viewport"},
                        {"type": "pointerDown", "button": button},
                        {"type": "pointerUp", "button": button},
                    ]
                )
            elif kind == "wheel":
                try:
                    x = int(item.get("x", 0))
                    y = int(item.get("y", 0))
                    delta_x = int(item.get("delta_x", 0))
                    delta_y = int(item.get("delta_y", 0))
                except (TypeError, ValueError) as exc:
                    raise FirefoxDomError(f"Batch command {index}: wheel-Werte sind ungültig") from exc
                wheel.append(
                    {
                        "type": "scroll",
                        "x": x,
                        "y": y,
                        "deltaX": delta_x,
                        "deltaY": delta_y,
                        "duration": 0,
                    }
                )
            else:
                raise FirefoxDomError(
                    f"Batch command {index}: nur key, keyhold, click und wheel sind erlaubt"
                )

        sources: list[dict[str, Any]] = []
        if keyboard:
            sources.append({"type": "key", "id": "ai-strom-batch-keyboard", "actions": keyboard})
        if pointer:
            sources.append(
                {
                    "type": "pointer",
                    "id": "ai-strom-batch-pointer",
                    "parameters": {"pointerType": "mouse"},
                    "actions": pointer,
                }
            )
        if wheel:
            sources.append({"type": "wheel", "id": "ai-strom-batch-wheel", "actions": wheel})
        if not sources:
            raise FirefoxDomError("Leerer Input-Batch")
        return self.command("input.performActions", {"context": context_id, "actions": sources})
