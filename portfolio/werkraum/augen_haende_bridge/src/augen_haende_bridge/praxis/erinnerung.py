"""Die Erinnerung: nach einem Fehlversuch ähnliche frühere Fälle aus dem Ereignisspeicher (PostgreSQL, Hybridsuche aus Bedeutung und Wort) holen.

Die Suche läuft als eigener Prozess mit dem Python der Speicher-Umgebung (`/root/bridge_speicher/venv`): Das Modell und die Datenbankbibliothek gehören nicht in den Relay.
Fehlt die Umgebung oder dauert die Suche zu lang, ist die Antwort leer; die Erinnerung ist eine Hilfe und hält nie einen Lauf auf.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

SPEICHER_PYTHON = Path(os.environ.get("BRIDGE_SPEICHER_PYTHON", "/root/bridge_speicher/venv/bin/python"))
PROJEKT = Path(__file__).resolve().parents[3]
KOPF = re.compile(r"^#(\d+) (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (\S+)\s+(.*?)\s*(?:\(([\d.]+)\))?\s*$")
MAX_TEXT = 220


def frage(grund: str, titel: str, klasse: str = "") -> str:
    """Die Suchfrage: Grund und Schritt, wie sie in den Ereignissen stehen."""
    return " ".join(t for t in (grund, titel, klasse, "Ursache") if t)


def lies(ausgabe: str) -> list[dict]:
    """Die Ausgabe von `speicher suche` als Liste: wann, woher, Text. Kopfzeile `#id Zeit quelle/art agent …`, darunter eingerückt der Text."""
    faelle: list[dict] = []
    aktuell: dict | None = None
    for zeile in ausgabe.splitlines():
        m = KOPF.match(zeile)
        if m:
            aktuell = {"id": int(m.group(1)), "wann": m.group(2), "woher": m.group(3), "abstand": float(m.group(5)) if m.group(5) else None, "text": ""}
            faelle.append(aktuell)
        elif aktuell is not None and zeile.startswith("    "):
            aktuell["text"] = zeile.strip()[:MAX_TEXT]
    return [f for f in faelle if f["text"]]


def aehnliche(grund: str, titel: str, *, klasse: str = "", n: int = 3, timeout: float = 25.0, python: Path | None = None,
              ausfuehren: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> list[dict]:
    py = python or SPEICHER_PYTHON
    if not Path(py).exists() and ausfuehren is subprocess.run:
        return []
    env = {**os.environ, "PYTHONPATH": str(PROJEKT / "src")}
    try:
        r = ausfuehren([str(py), "-m", "augen_haende_bridge.speicher", "suche", frage(grund, titel, klasse), "-n", str(n)],
                       cwd=str(PROJEKT), env=env, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return []
    return lies(r.stdout)[:n] if r.returncode == 0 else []
