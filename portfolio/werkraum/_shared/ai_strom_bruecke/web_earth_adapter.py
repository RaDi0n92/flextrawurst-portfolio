#!/usr/bin/env python3
"""Model-free classification of the Google Earth Web surface.

Google Earth Web exposes controls in the browser DOM, while the geographic
surface is rendered by one or more canvas/WebGL layers.  This module keeps
those truths separate so a browser observation is never mislabeled as native
X11 Earth Pro or as a semantic place DOM.
"""

from __future__ import annotations

from typing import Any, Mapping


GOOGLE_EARTH_WEB_URL = "https://earth.google.com/web/"


def classify_google_earth_web_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Return an explicit DOM/canvas/native classification without inference."""
    canvases = list(snapshot.get("canvases") or [])
    controls = list(snapshot.get("dom_controls") or [])
    webgl_layers = [canvas for canvas in canvases if canvas.get("webgl") is True]
    return {
        "schema": "ai-strom-bruecke.google-earth-web-surface.v1",
        "url": snapshot.get("url"),
        "title": snapshot.get("title"),
        "dom_controls": controls,
        "dom_control_count": len(controls),
        "dom_controls_present": bool(controls),
        "canvases": canvases,
        "canvas_count": len(canvases),
        "webgl_layer_count": len(webgl_layers),
        "map_surface": "canvas-webgl" if webgl_layers else ("canvas" if canvases else "unknown"),
        "native_x11": False,
        "semantic_place_dom": False,
        "model_calls": 0,
        "classification_basis": ["browser-dom-controls", "canvas-inspection", "webgl-context-inspection"],
    }


def inspect_google_earth_web(page: Any) -> dict[str, Any]:
    """Inspect an existing Playwright page without typing or steering it."""
    snapshot = page.evaluate(
        """() => ({
          url: location.href,
          title: document.title,
          dom_controls: [...new Set([...document.querySelectorAll('button,[role="button"],[aria-label]')])]
            .map(node => ({
              tag: node.tagName.toLowerCase(),
              role: node.getAttribute('role'),
              aria_label: node.getAttribute('aria-label'),
              text: (node.innerText || '').trim()
            }))
            .filter(item => item.aria_label || item.text),
          canvases: [...document.querySelectorAll('canvas')].map(canvas => ({
            width: canvas.width,
            height: canvas.height,
            webgl: !!(canvas.getContext('webgl') || canvas.getContext('webgl2'))
          }))
        })"""
    )
    return classify_google_earth_web_snapshot(snapshot)

