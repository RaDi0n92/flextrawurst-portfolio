"""Ziel-Schlüssel des Körpers: `<ort>:window:<kennung>` für ein Fenster, `desktop` für den ganzen Desktop dieses Arbeitsplatzes.

Der Ort benennt den Arbeitsplatz: `windows` für Daniels Laptop, `kde1` und `kde2` für die Linux-Desktops. Die Fensterkennung ist unter Windows der
Fenstergriff (`hwnd`), unter Linux die X-Kennung. Bisher stand der Ort fest als `windows` im Code; jetzt benutzen alle Stellen diese Hilfen.
"""

from __future__ import annotations

import re

_FENSTER = re.compile(r"([a-z][a-z0-9]*):window:(\d+)\Z")


def fenster_schluessel(ort: str, kennung: int) -> str:
    return f"{ort}:window:{int(kennung)}"


def ist_fenster(schluessel: object) -> bool:
    return isinstance(schluessel, str) and _FENSTER.match(schluessel) is not None


def fenster_kennung(schluessel: object) -> int | None:
    treffer = _FENSTER.match(schluessel) if isinstance(schluessel, str) else None
    return int(treffer.group(2)) if treffer else None


def ort_von(schluessel: object) -> str | None:
    """Der Arbeitsplatz eines Fenster-Schlüssels; None für `desktop` und Unbekanntes."""
    treffer = _FENSTER.match(schluessel) if isinstance(schluessel, str) else None
    return treffer.group(1) if treffer else None
