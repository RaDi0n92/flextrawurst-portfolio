#!/usr/bin/env python3
"""Render the JSON produced by capture_surface_playwright.mjs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from surface_export import write_surface_artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.capture.read_text(encoding="utf-8"))
    manifest = write_surface_artifacts(payload, args.output)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

