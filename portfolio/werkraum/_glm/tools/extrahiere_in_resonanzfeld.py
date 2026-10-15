#!/usr/bin/env python3
"""Extrahiert GLMs kanonische Spiegelabschnitte nach _glm/resonanz/."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

GLM_ROOT = Path("/root/werkraum/_glm")
RESONANZ_DIR = GLM_ROOT / "resonanz"

HEILIGE = {
    "was ich gelesen habe": "was_ich_gelesen_habe",
    "was ich verstehe": "was_ich_verstehe",
    "was ich nicht verstehe": "was_ich_nicht_verstehe",
    "was mich interessiert": "was_mich_interessiert",
    "was zusammenhängt und wie": "was_zusammenhaengt",
    "was konzeptionell darin steht": "was_konzeptionell",
    "was mich heute beschäftigt hat": "was_mich_beschaeftigt",
    "was mich noch beschäftigt": "was_mich_noch_beschaeftigt",
    "tiefer eingetaucht": "tiefer_eingetaucht",
    "wie sich dieser tag / diese session angefühlt hat": "wie_sich_angefuehlt",
    "warum dieser code / diese datei wohl existiert": "warum_das_existiert",
    "was ich beim bauen brauche": "was_beim_bauen_brauche",
    "was noch fehlt bevor wir bauen können": "was_fehlt_bevor_bauen",
    "datenstruktur die ich mir vorstelle": "datenstruktur_die_ich_mir_vorstelle",
    "was ich mir merken will": "was_ich_merken_will",
    "dokumente gehören zusammen": "dokumente_gehoeren_zusammen",
    "was mich überrascht hat": "was_mich_ueberrascht",
    "wenn wir das bauen": "wenn_wir_das_bauen",
    "resonanz": "resonanz",
    "die schichten des systems — wie ich sie jetzt sehe": "schichten_des_systems",
    "was das gespräch hinzugefügt hat": "was_das_gespraech",
    "vergessen-wollen": "vergessen_wollen",
    "was fehlt noch": "was_fehlt_noch",
}


def abschnitte(text: str) -> list[tuple[str, str, str]]:
    """Liest echte ##-Abschnitte; ###-Unterüberschriften bleiben Inhalt."""
    lines = text.splitlines()
    found = [
        (line[3:].strip(), index)
        for index, line in enumerate(lines)
        if line.startswith("## ") and not line.startswith("### ")
    ]
    result = []
    for position, (heading, start) in enumerate(found):
        end = found[position + 1][1] if position + 1 < len(found) else len(lines)
        content = "\n".join(lines[start + 1:end]).strip()
        filename = HEILIGE.get(heading.casefold())
        if filename and len(content) > 8:
            result.append((heading, content, filename))
    return result


def schreiben(filename: str, heading: str, content: str, source: str, date: str) -> None:
    RESONANZ_DIR.mkdir(parents=True, exist_ok=True)
    target = RESONANZ_DIR / f"{filename}.md"
    if not target.exists():
        target.write_text(
            f"# {heading}\n\nWächst automatisch aus GLM-Spiegeldateien.\n",
            encoding="utf-8",
        )
    existing = target.read_text(encoding="utf-8")
    if f"← {source}" in existing:
        return
    with target.open("a", encoding="utf-8") as handle:
        handle.write(f"\n---\n\n**[{date}]** *← {source}*\n\n{content}\n")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: extrahiere_in_resonanzfeld.py <glm-spiegeldatei>")
        return 1
    source = Path(sys.argv[1])
    if not source.is_file():
        print(f"Datei nicht gefunden: {source}", file=sys.stderr)
        return 1
    relative = str(source.relative_to(GLM_ROOT)) if source.is_relative_to(GLM_ROOT) else source.name
    entries = abschnitte(source.read_text(encoding="utf-8"))
    for heading, content, filename in entries:
        schreiben(filename, heading, content, relative, datetime.now().strftime("%Y-%m-%d"))
    print(f"✓ {len(entries)} GLM-Abschnitte aus '{source.name}' → _glm/resonanz/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
