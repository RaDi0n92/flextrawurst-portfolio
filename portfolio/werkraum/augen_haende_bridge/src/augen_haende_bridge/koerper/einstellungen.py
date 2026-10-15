"""Was Daniel an den Fenstern einstellt, bleibt: Ort, Größe, Deckkraft und Sichtbarkeitsregel je Fenster.

Eine kleine JSON-Datei unter `%LOCALAPPDATA%\\AugenUndHaendeBridge\\einstellungen.json`. Schlüssel: `regie`, `chat`,
`raute:<Agentenname>`, `terminal:<Agentenname>`. Eine fehlende oder kaputte Datei ist kein Fehler (es gelten dann die
Standardplätze), und eine nicht schreibbare Datei wird nur gemeldet, nie zum Absturz. Gespeicherte Orte werden beim
Anwenden auf den sichtbaren Bildschirm geklemmt, damit ein abgesteckter Monitor kein Fenster verschluckt.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path

VERSION = 1
Rechteck = tuple[int, int, int, int]


def standard_pfad(ort: str | None = None) -> Path:
    """Windows: `%LOCALAPPDATA%\\AugenUndHaendeBridge\\einstellungen.json`. Linux: `$XDG_CONFIG_HOME` (sonst `~/.config`), je Desktop-Ort eine eigene Datei."""
    basis = os.environ.get("LOCALAPPDATA")
    if basis:
        return Path(basis) / "AugenUndHaendeBridge" / "einstellungen.json"
    konfig = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(konfig) / "AugenUndHaendeBridge" / (f"einstellungen-{ort}.json" if ort else "einstellungen.json")


def klemmen(x: int, y: int, breite: int, hoehe: int, bildschirm: Rechteck, sichtbar_mindestens: int = 40) -> tuple[int, int]:
    """Position so schieben, dass mindestens `sichtbar_mindestens` Pixel des Fensters auf dem Bildschirm liegen."""
    links, oben, rechts, unten = bildschirm
    x = max(links + sichtbar_mindestens - breite, min(x, rechts - sichtbar_mindestens))
    y = max(oben, min(y, unten - sichtbar_mindestens))
    return x, y


class Einstellungen:
    def __init__(self, pfad: Path | None = None):
        self.pfad = pfad
        self.daten: dict[str, dict] = {}
        self.fehler: str | None = None

    def laden(self) -> None:
        self.daten = {}
        if self.pfad is None or not self.pfad.exists():
            return
        try:
            inhalt = json.loads(self.pfad.read_text(encoding="utf-8"))
        except (OSError, ValueError) as fehler:
            self.fehler = f"Einstellungen nicht gelesen: {fehler!r}"[:200]
            return
        elemente = inhalt.get("elemente") if isinstance(inhalt, dict) else None
        if isinstance(elemente, dict):
            self.daten = {str(k): v for k, v in elemente.items() if isinstance(v, dict)}

    def element(self, schluessel: str) -> dict:
        return dict(self.daten.get(schluessel, {}))

    def setzen(self, schluessel: str, werte: dict) -> None:
        self.daten[schluessel] = {k: v for k, v in werte.items() if v is not None}

    def speichern(self) -> bool:
        if self.pfad is None:
            return False
        try:
            self.pfad.parent.mkdir(parents=True, exist_ok=True)
            temp = self.pfad.with_suffix(".tmp")
            temp.write_text(json.dumps({"version": VERSION, "elemente": self.daten}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
            os.replace(temp, self.pfad)
            self.fehler = None
            return True
        except OSError as fehler:
            self.fehler = f"Einstellungen nicht gespeichert: {fehler!r}"[:200]
            return False


def erfassen(fenster, art: str) -> dict:
    """Ort, Größe und Deckkraft eines Fensters als Daten."""
    links, oben, rechts, unten = fenster.rechteck()
    daten: dict = {"x": links, "y": oben, "b": rechts - links, "h": unten - oben, "deckkraft": fenster.deckkraft}
    if art == "raute":
        daten["groesse"] = getattr(fenster, "groesse", None)
    if art == "ampel":
        daten["faktor"] = getattr(fenster, "faktor", None)
    return daten


def _ganzzahl(wert: object) -> int | None:
    return wert if isinstance(wert, int) and not isinstance(wert, bool) and -100000 < wert < 100000 else None


def anwenden(fenster, daten: dict, art: str, bildschirm: Callable[[], Rechteck] | None = None) -> None:
    """Gespeicherte Werte zurück auf das Fenster; Unbrauchbares wird übergangen."""
    alpha = _ganzzahl(daten.get("deckkraft"))
    if alpha is not None and 0 <= alpha <= 255:
        fenster.setze_deckkraft(alpha)
    if art == "raute":
        groesse = _ganzzahl(daten.get("groesse"))
        if groesse is not None:
            fenster.groesse_setzen(groesse)
    if art == "ampel":
        faktor = daten.get("faktor")
        if isinstance(faktor, (int, float)) and not isinstance(faktor, bool) and 0.5 <= faktor <= 5:
            fenster.faktor_setzen(float(faktor))
    x, y = _ganzzahl(daten.get("x")), _ganzzahl(daten.get("y"))
    if x is None or y is None:
        return
    links, oben, rechts, unten = fenster.rechteck()
    breite, hoehe = rechts - links, unten - oben
    if art in ("chat", "terminal", "kamera"):
        b, h = _ganzzahl(daten.get("b")), _ganzzahl(daten.get("h"))
        if b is not None and h is not None and 80 <= b <= 4000 and 60 <= h <= 4000:
            breite, hoehe = b, h
    if bildschirm is not None:
        x, y = klemmen(x, y, breite, hoehe, bildschirm())
    fenster.verschiebe(x, y, breite, hoehe)
