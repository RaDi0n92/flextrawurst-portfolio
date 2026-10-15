"""Korrigiert erfundene Jahre in Datumsangaben, die GENI selbst umformatiert hat.

2026-08-12, Fund in dokumentieren.py (siehe docs/systemdoku/52_verlaufsprotokolle.md,
fuenfter Fund): sie sieht rohe ISO-Zeitstempel als Kontext ("2026-08-09T22:01"),
formatiert sie beim Schreiben selbst ins deutsche Format um -- und vertut sich beim
kleinen quantisierten Modell reihenweise beim Jahr (2026 -> 2014, 2026 -> 207). Tag
und Monat treffen fast immer, nur das Jahr kippt.

Daniel, 2026-08-12: "2. oder?" -- programmatisch nachformatieren statt ihr zu vertrauen.

Ersetzt wird nur, wenn Tag+Monat eindeutig zu genau einem echten Jahr passen, das sie
im selben Lauf tatsaechlich gesehen hat -- sonst waere das Korrigieren selbst wieder
ein Erfinden, nur an anderer Stelle.

Gemeinsam genutzt von:
  - dokumentieren.py  (kennt die echten Zeitstempel als strukturierte Treffer-Dicts)
  - dialog.py         (kennt sie nur als rohe ISO-Zeitstempel im Systemprompt-Text)
"""

import re
from datetime import datetime

_DATUM_MUSTER = re.compile(r"\b(\d{1,2})[.:](\d{1,2})[.:](\d{2,4})\b")
_ISO_MUSTER = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})T")


def echte_jahre_aus_treffern(treffer: dict) -> dict:
    """Aus einem eintrag_id -> Treffer-Dict (mit 'zeit'-Feld) die echten Jahre je (Tag, Monat)."""
    echte = {}
    for t in treffer.values():
        zeit = t.get("zeit")
        if not zeit:
            continue
        try:
            dt = datetime.fromisoformat(zeit)
        except Exception:
            continue
        echte.setdefault((dt.day, dt.month), set()).add(dt.year)
    return echte


def echte_jahre_aus_text(kontext_text: str) -> dict:
    """Aus rohem Kontext-Text (enthaelt ISO-Zeitstempel wie '2026-08-09T22:01') dasselbe."""
    echte = {}
    for jahr, monat, tag in _ISO_MUSTER.findall(kontext_text or ""):
        echte.setdefault((int(tag), int(monat)), set()).add(int(jahr))
    return echte


def korrigieren(text: str, echte_jahre: dict) -> tuple:
    """Ersetzt jedes DD.MM.YYYY-artige Datum in `text`, dessen Jahr nicht zum echten
    Jahr fuer dasselbe (Tag, Monat) passt -- und nur, wenn dieses (Tag, Monat) eindeutig
    genau einem echten Jahr zuzuordnen ist. Gibt (korrigierter_text, anzahl) zurueck.
    """
    anzahl = 0

    def ersetzen(treffer):
        nonlocal anzahl
        tag, monat, jahr_roh = int(treffer.group(1)), int(treffer.group(2)), treffer.group(3)
        if not (1 <= tag <= 31 and 1 <= monat <= 12):
            return treffer.group(0)
        jahre = echte_jahre.get((tag, monat))
        if not jahre or len(jahre) != 1:
            return treffer.group(0)
        echtes_jahr = next(iter(jahre))
        if jahr_roh == str(echtes_jahr):
            return treffer.group(0)
        anzahl += 1
        return f"{tag:02d}.{monat:02d}.{echtes_jahr}"

    korrigiert = _DATUM_MUSTER.sub(ersetzen, text)
    return korrigiert, anzahl


def korrigieren_aus_kontext(text: str, kontext_text: str) -> tuple:
    """Bequemlichkeitsfunktion fuer dialog.py: Kontext-Text rein, korrigierter Text raus."""
    return korrigieren(text, echte_jahre_aus_text(kontext_text))
