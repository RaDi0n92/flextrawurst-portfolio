"""Server-side safety boundary for the AI-Strom-Brücke.

The bridge has exactly one allowed browser path: Firefox WebDriver BiDi and
the page's DOM.  This module is intentionally small so every entry point can
use the same fail-closed decision instead of relying on documentation or an
agent remembering a convention.
"""

from __future__ import annotations

POLICY_ID = "ai-strom-bruecke.dom-only.v1"
PERCEPTION_SOURCE = "firefox-webdriver-bidi-dom"


def status() -> dict[str, object]:
    return {
        "policy": POLICY_ID,
        "perception_source": PERCEPTION_SOURCE,
        "screenshots": "forbidden",
        "vision_models": "forbidden",
        "ocr": "forbidden",
        "native_x11": "forbidden",
        "xdotool": "forbidden",
        "allowed_browser_channel": "Firefox WebDriver BiDi DOM",
    }


def reject(operation: str) -> None:
    """Fail closed for every legacy/native/visual operation."""
    raise SystemExit(
        f"AI-Strom-Brücke: {operation} abgewiesen — Policy {POLICY_ID}: "
        "nur Firefox-BiDi-DOM ist erlaubt; Screenshots, Vision, OCR und "
        "native X11/xdotool sind serverseitig gesperrt."
    )
