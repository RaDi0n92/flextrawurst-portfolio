#!/usr/bin/env python3
"""Fail-closed validation for the G12 Windows witness output.

This validator only reads a witness JSON and an explicitly supplied PNG.  It
does not create, edit, or infer native Windows evidence.  A valid result shows
that the witness artifacts are internally consistent; it is not itself a
replacement for the Windows run or the human click.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SCAN_MARKER = re.compile(r"^Augen & Hände Bridge · scan-received:\d+$")
BINDING_MARKER = re.compile(r"^Augen & Hände Bridge · scan-received:\d+ · binding-readback$")


@dataclass(frozen=True)
class ValidationReport:
    status: str
    checks: tuple[str, ...]
    failures: tuple[str, ...]
    unknowns: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "checks": list(self.checks),
            "failures": list(self.failures),
            "unknowns": list(self.unknowns),
        }


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError:
        return None
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        return None
    return width, height


def validate_native_binding(payload: dict[str, Any], screenshot: Path | None) -> ValidationReport:
    checks: list[str] = []
    failures: list[str] = []
    unknowns: list[str] = []

    def require(condition: bool, check: str, failure: str) -> None:
        if condition:
            checks.append(check)
        else:
            failures.append(failure)

    require(payload.get("status") == "PASS", "witness status PASS", "witness status is not PASS")
    require(payload.get("native_windows") is True, "native_windows=true", "native_windows is not true")
    require(payload.get("input_exercised") is False, "input_exercised=false", "input_exercised is not false")
    require(payload.get("target_selection") == "manual_click", "target_selection=manual_click", "manual click was not recorded")
    require(payload.get("binding_readback") == "native_marker", "binding_readback=native_marker", "native binding readback was not recorded")
    require(payload.get("transport") == "ssh-local-forward", "transport=ssh-local-forward", "unexpected transport")

    scanner_marker = payload.get("scanner_marker")
    binding_marker = payload.get("binding_marker")
    require(isinstance(scanner_marker, str) and bool(SCAN_MARKER.fullmatch(scanner_marker)), "scanner marker valid", "scanner marker is missing or malformed")
    require(isinstance(binding_marker, str) and bool(BINDING_MARKER.fullmatch(binding_marker)), "binding marker valid", "binding marker is missing or malformed")

    window = payload.get("window")
    if not isinstance(window, dict):
        failures.append("window evidence is missing")
    else:
        require(window.get("visible") is True, "native window visible", "native window is not visible")
        require(isinstance(window.get("hwnd"), int) and window["hwnd"] > 0, "hwnd present", "hwnd is missing or invalid")
        require(isinstance(window.get("process_id"), int) and window["process_id"] > 0, "process_id present", "process_id is missing or invalid")
        rect = window.get("rect")
        require(
            isinstance(rect, dict)
            and isinstance(rect.get("width"), int)
            and isinstance(rect.get("height"), int)
            and rect["width"] > 0
            and rect["height"] > 0,
            "native window dimensions positive",
            "native window rectangle is missing or invalid",
        )

    if screenshot is None:
        unknowns.append("PNG path was not supplied; the JSON path may be Windows-local")
    elif not screenshot.is_file():
        unknowns.append(f"PNG file not found: {screenshot}")
    else:
        dimensions = _png_dimensions(screenshot)
        if dimensions is None:
            failures.append("PNG signature or IHDR is invalid")
        else:
            checks.append(f"PNG readable ({dimensions[0]}x{dimensions[1]})")

    status = "FAIL" if failures else "UNKNOWN" if unknowns else "PASS"
    return ValidationReport(status, tuple(checks), tuple(failures), tuple(unknowns))


def _load_payload(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("witness JSON root must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", required=True, type=Path, dest="json_path")
    parser.add_argument("--screenshot", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        report = validate_native_binding(_load_payload(args.json_path), args.screenshot)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "failures": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps(report.as_dict(), ensure_ascii=False))
    return {"PASS": 0, "UNKNOWN": 2, "FAIL": 1}[report.status]


if __name__ == "__main__":
    sys.exit(main())
