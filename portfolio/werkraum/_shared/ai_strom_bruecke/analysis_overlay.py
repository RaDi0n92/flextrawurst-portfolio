#!/usr/bin/env python3
"""Visible pointer/target evidence overlay; never alters the source frame."""

from __future__ import annotations

import io
from typing import Mapping

from PIL import Image, ImageDraw, ImageFont


def render_analysis_overlay(
    payload: bytes,
    *,
    pointer_xy: Mapping[str, int] | None = None,
    target_xy: Mapping[str, int] | None = None,
    label: str | None = None,
) -> bytes:
    """Return a derived PNG with crosshair and optional target marker."""
    with Image.open(io.BytesIO(payload)).convert("RGBA") as image:
        draw = ImageDraw.Draw(image, "RGBA")
        if pointer_xy:
            x, y = int(pointer_xy["x"]), int(pointer_xy["y"])
            draw.line((x - 24, y, x + 24, y), fill=(255, 75, 75, 220), width=2)
            draw.line((x, y - 24, x, y + 24), fill=(255, 75, 75, 220), width=2)
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 255, 255, 240), width=2)
        if target_xy:
            x, y = int(target_xy["x"]), int(target_xy["y"])
            draw.rectangle((x - 16, y - 16, x + 16, y + 16), outline=(80, 220, 255, 240), width=2)
        if label:
            draw.rectangle((8, 8, min(image.width - 8, 8 + len(label) * 8), 30), fill=(0, 0, 0, 180))
            draw.text((12, 12), label, fill=(255, 255, 255, 255), font=ImageFont.load_default())
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
