#!/usr/bin/env python3
"""Evidence-based Earth status-bar and pointer perception.

No model is involved here.  OCR is an optional local executable; parsing is
deterministic and always keeps the raw text plus a confidence/source claim.
"""

from __future__ import annotations

import io
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from PIL import Image

from .contracts import CoordinateClaim, CoordinateKind


_DECIMAL = re.compile(
    r"(?P<lat>[+-]?\d{1,3}(?:[.,]\d+)?)\s*[°º]?\s*(?P<latdir>[NS])?"
    r"[^\dNSWE+-]+(?P<lon>[+-]?\d{1,3}(?:[.,]\d+)?)\s*[°º]?\s*(?P<londir>[EOW])?",
    re.IGNORECASE,
)
_DMS = re.compile(
    r"(?P<latdeg>\d{1,3})\s*[°º]\s*(?P<latmin>\d{1,2})['′]\s*"
    r"(?P<latsec>[\d.,]+)[\"″]\s*(?P<latdir>[NS])"
    r"[^\dNSWE]+(?P<londeg>\d{1,3})\s*[°º]\s*(?P<lonmin>\d{1,2})['′]\s*"
    r"(?P<lonsec>[\d.,]+)[\"″]\s*(?P<londir>[EOW])",
    re.IGNORECASE,
)
_ALTITUDE = re.compile(
    r"(?P<value>[\d.,]+)\s*(?P<unit>m|km)\b|(?:höhe|altitude|eye)\s*[:=]?\s*(?P<bare>[\d.,]+)",
    re.IGNORECASE,
)


def _number(value: str) -> float:
    return float(value.replace(".", "").replace(",", ".")) if value.count(",") else float(value)


def _dms(degrees: str, minutes: str, seconds: str, direction: str) -> float:
    value = _number(degrees) + _number(minutes) / 60 + _number(seconds) / 3600
    return -value if direction.upper() in {"S", "W", "O"} and direction.upper() != "E" else value


def _normalize_direction(value: float, direction: str | None, latitude: bool) -> float:
    if not direction:
        return value
    direction = direction.upper()
    if direction in {"S", "W"} or (direction == "O" and not latitude):
        return -abs(value)
    return abs(value)


def parse_earth_status_text(
    raw_text: str,
    *,
    frame_id: str,
    pointer_xy: dict[str, int] | None,
    coordinate_kind: CoordinateKind = CoordinateKind.POINTER,
    source: str = "earth-statusbar-ocr",
    observed_at: float | None = None,
) -> CoordinateClaim:
    """Parse DMS or decimal coordinates without guessing missing values."""
    text = " ".join(raw_text.replace("\n", " ").split())
    latitude = longitude = None
    match = _DMS.search(text)
    if match:
        latitude = _dms(match["latdeg"], match["latmin"], match["latsec"], match["latdir"])
        longitude = _dms(match["londeg"], match["lonmin"], match["lonsec"], match["londir"])
    else:
        match = _DECIMAL.search(text)
        if match:
            latitude = _normalize_direction(_number(match["lat"]), match["latdir"], True)
            longitude = _normalize_direction(_number(match["lon"]), match["londir"], False)

    elevation = eye_altitude = None
    altitude_matches = list(_ALTITUDE.finditer(text))
    if altitude_matches:
        values = []
        for altitude in altitude_matches:
            raw = altitude.group("value") or altitude.group("bare")
            value = _number(raw)
            if altitude.group("unit") and altitude.group("unit").lower() == "km":
                value *= 1000
            values.append(value)
        eye_altitude = values[-1]

    valid = latitude is not None and longitude is not None
    confidence = 0.92 if valid and match is not None else 0.0
    if valid and coordinate_kind == CoordinateKind.UNKNOWN:
        confidence *= 0.7
    normalized = (
        f"{latitude:.8f},{longitude:.8f}"
        if valid
        else "unparsed"
    )
    return CoordinateClaim(
        claim_id=f"claim-{uuid.uuid4().hex}",
        frame_id=frame_id,
        pointer_xy=pointer_xy,
        coordinate_kind=coordinate_kind,
        latitude=latitude,
        longitude=longitude,
        elevation_m=elevation,
        eye_altitude_m=eye_altitude,
        raw_text=raw_text,
        normalized_text=normalized,
        confidence=confidence,
        source=source,
        observed_at=observed_at if observed_at is not None else time.time(),
        metadata={"parse_valid": valid},
    )


def ocr_status_bar(
    frame: bytes,
    *,
    crop: tuple[int, int, int, int] | None = None,
    tesseract_binary: str = "tesseract",
) -> str:
    """Run local OCR if available; never silently replace it with a model."""
    executable = shutil.which(tesseract_binary)
    if not executable:
        raise RuntimeError("lokales OCR-Programm nicht verfügbar")
    with Image.open(io.BytesIO(frame)) as image:
        if crop:
            image = image.crop(crop)
        with tempfile.TemporaryDirectory(prefix="ai-strom-ocr-") as directory:
            source = Path(directory) / "status.png"
            image.save(source, format="PNG")
            result = subprocess.run(
                [executable, str(source), "stdout", "--psm", "6"],
                check=True,
                capture_output=True,
                text=True,
                timeout=3,
            )
            return result.stdout.strip()


def coordinate_plausible(claim: CoordinateClaim) -> bool:
    if claim.latitude is None or claim.longitude is None:
        return False
    return -90 <= claim.latitude <= 90 and -180 <= claim.longitude <= 180


def local_pixel_rate(
    first: CoordinateClaim,
    second: CoordinateClaim,
) -> dict[str, float]:
    """Return an explicitly local approximation, never a global promise."""
    if not first.pointer_xy or not second.pointer_xy:
        raise ValueError("beide Claims brauchen pointer_xy")
    dx = second.pointer_xy["x"] - first.pointer_xy["x"]
    dy = second.pointer_xy["y"] - first.pointer_xy["y"]
    if dx == 0 and dy == 0:
        raise ValueError("identische Pixelpositionen kalibrieren keine Rate")
    result: dict[str, float] = {}
    if dx:
        result["d_lon_per_pixel"] = (second.longitude or 0) - (first.longitude or 0)
        result["d_lon_per_pixel"] /= dx
    if dy:
        result["d_lat_per_pixel"] = (second.latitude or 0) - (first.latitude or 0)
        result["d_lat_per_pixel"] /= dy
    return result
