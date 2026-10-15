"""Policy for the opt-in visual companion of the AI-Strom-Brücke.

The existing DOM-only policy remains untouched. This policy is deliberately
separate so a caller must choose the screenshot-capable channel explicitly.
Screenshots are captured through Firefox WebDriver BiDi; native X11, OCR and
vision-model calls are still outside this bridge.
"""

from __future__ import annotations


POLICY_ID = "ai-strom-bruecke.visual.v1"
PERCEPTION_SOURCE = "firefox-webdriver-bidi-dom+screenshot"


def status() -> dict[str, object]:
    return {
        "policy": POLICY_ID,
        "perception_source": PERCEPTION_SOURCE,
        "screenshots": "allowed-via-firefox-bidi",
        "screenshot_interval_ms": 100,
        "screenshot_interval_contract": "fixed-100ms",
        "screenshot_format": {"type": "image/jpeg", "quality": 0.3},
        "cadence_reporting": "scheduled-vs-captured-with-missed-ticks",
        "frame_evaluation": "hash-plus-deterministic-pixel-diff",
        "vision_models": "forbidden",
        "ocr": "forbidden",
        "native_x11": "forbidden",
        "xdotool": "forbidden",
        "allowed_browser_channel": "Firefox WebDriver BiDi DOM + browsingContext.captureScreenshot",
        "allowed_input": ["keyboard", "mouse-click", "mouse-wheel"],
        "dom_selector_input": "forbidden",
        "batch_input": "one-input.performActions-without-intermediate-screenshots",
        "focus_sync": "browsingContext.activate-before-action",
        "control_lease": "shared-with-dom-only-bridge",
    }
