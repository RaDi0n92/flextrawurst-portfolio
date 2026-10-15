#!/usr/bin/env python3
"""Schreibt GLMs [[abwurf: ...]]-Marker nach _glm/abwuerfe.md."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

GLM_ROOT = Path("/root/werkraum/_glm")
ABWUERFE = GLM_ROOT / "abwuerfe.md"


def material(text: str) -> str:
    lower = text.casefold()
    signals = {
        "lava": ("fehler", "verlust", "widerspruch", "spannung"),
        "wasser": ("resonanz", "verbindung", "trägt", "berührt"),
        "sternenstaub": ("überrascht", "neu", "erkenntnis"),
        "gras": ("freude", "offen", "wächst"),
        "nebel": ("unklar", "offen", "vielleicht", "warte"),
    }
    scores = {name: sum(lower.count(signal) for signal in words) for name, words in signals.items()}
    winner = max(scores, key=scores.get)
    return winner if scores[winner] else "nebel"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: spiegel_abwurf.py <glm-spiegeldatei>")
        return 1
    source = Path(sys.argv[1])
    if not source.is_file():
        print(f"Datei nicht gefunden: {source}", file=sys.stderr)
        return 1
    markers = [item.strip() for item in re.findall(r"\[\[abwurf:\s*(.+?)\]\]", source.read_text(encoding="utf-8"))]
    markers = [item for item in markers if len(item) >= 10]
    if not markers:
        print(f"— keine GLM-Abwürfe in '{source.name}'")
        return 0
    ABWUERFE.parent.mkdir(parents=True, exist_ok=True)
    with ABWUERFE.open("a", encoding="utf-8") as handle:
        for entry in markers:
            handle.write(
                f"- [{datetime.now():%Y-%m-%d %H:%M}] **{material(entry)}** "
                f"← {source.name}: »{entry}«\n"
            )
    print(f"✓ {len(markers)} GLM-Abwurf/Abwürfe → _glm/abwuerfe.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
