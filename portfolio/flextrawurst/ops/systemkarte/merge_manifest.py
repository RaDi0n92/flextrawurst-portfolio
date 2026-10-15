#!/usr/bin/env python3
"""Fuegt die Manifeste der zwoelf Systemkarte-Diagramme zu i18n/systemkarte.json zusammen.

Aufruf: merge_manifest.py <cand-Ordner> <ziel.json>
Der cand-Ordner ist der Ausgabeordner von build_i18n.py (cand/de/<slug>/manifest.json und
cand/en/<slug>/manifest.json). Aus der Datei baut build_surface.ts (generateSystemkarteView)
den crawlbaren Text im Tab und die Sitemap-URLs.
"""
import json
import sys

ORDER = ["gesamtbild", "selbstbild", "langgraph-weltbild", "datenbank-rag", "vaults", "werkzeuge"]
STAND = "2026-10-01"


def main(cand: str, ziel: str) -> None:
    items = []
    for slug in ORDER:
        de = json.load(open(f"{cand}/de/{slug}/manifest.json", encoding="utf-8"))
        en = json.load(open(f"{cand}/en/{slug}/manifest.json", encoding="utf-8"))
        items.append({"slug": slug, "de": de, "en": en})
    json.dump({"stand": STAND, "items": items}, open(ziel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(items)} Diagramme -> {ziel}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
