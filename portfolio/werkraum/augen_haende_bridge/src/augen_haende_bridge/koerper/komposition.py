"""Komposition je Empfänger (G08, R043, R044): Objekte, die nur für bestimmte Agenten gedacht sind, werden **nur in deren Bild** gemalt.

Nie auf den physischen Bildschirm, nie in das Bild eines anderen Agenten, nie in Chat oder Export. Was auf dem Bildschirm steht (`bildschirm=True`), ist
ohnehin im Basisbild jedes Agenten, der diesen Bereich sieht, und wird hier nicht noch einmal gemalt (sonst doppelt).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image

from .objekte import Dokument
from .zeichnen_render import rendern

Rechteck = tuple[int, int, int, int]


@dataclass
class Komposit:
    """Was für einen Agenten gilt: eine Marke, die sich ändert, wenn sich sein Inhalt ändert, und die Funktion, die ihn in ein Bild malt."""

    token: bytes
    anwenden: Callable[[Image.Image], Image.Image]


def token_fuer(dokument: Dokument, tid: str, gate: Rechteck) -> bytes:
    objekte = dokument.fuer_empfaenger(tid)
    if not objekte:
        return b""
    h = hashlib.blake2b(digest_size=8)
    h.update(f"{dokument.version}:{gate}".encode())
    return h.digest()


def komponiere(bild: Image.Image, dokument: Dokument, tid: str, gate: Rechteck, ausschnitt: Rechteck) -> Image.Image:
    """`bild` ist der Ausschnitt (Bildschirmkoordinaten `ausschnitt`) des Gates `gate`. Liefert dasselbe Bild mit den Objekten, die `tid` sehen soll."""
    objekte = dokument.fuer_empfaenger(tid)
    gb, gh = gate[2] - gate[0], gate[3] - gate[1]
    if not objekte or gb <= 0 or gh <= 0:
        return bild
    ueberlagerung = rendern(objekte, gb, gh)
    ueberlagerung = ueberlagerung.crop((ausschnitt[0] - gate[0], ausschnitt[1] - gate[1], ausschnitt[2] - gate[0], ausschnitt[3] - gate[1]))
    if ueberlagerung.size != bild.size:
        ueberlagerung = ueberlagerung.resize(bild.size)
    ergebnis = bild.convert("RGBA")
    ergebnis.alpha_composite(ueberlagerung)
    return ergebnis.convert("RGB")


class Arbeitsflaechen:
    """Alle Dokumente der Bridge, je Gate eines (Schlüssel = das gebundene Ziel). Die Bilderstrom-Aufnahme fragt hier, was ein Agent in seinem Gate sehen soll."""

    def __init__(self):
        self.dokumente: dict[str, Dokument] = {}
        self.gespeichert: dict[str, dict] = {}  # stabiler Name → gespeichertes Dokument
        self.stabil: dict[str, str] = {}  # Gate-Schlüssel dieses Laufs → stabiler Name

    def dokument(self, ziel_schluessel: str) -> Dokument:
        if ziel_schluessel not in self.dokumente:
            self.dokumente[ziel_schluessel] = Dokument(ziel_schluessel)
        return self.dokumente[ziel_schluessel]

    # ---- Speichern: Objekte „bleiben, bis Daniel sie entfernt“ (R051), auch über einen Neustart ---------------------------
    def laden(self, pfad) -> None:
        import json
        self.gespeichert = {}
        try:
            roh = json.loads(pfad.read_text(encoding="utf-8"))
            if isinstance(roh, dict) and isinstance(roh.get("ziele"), dict):
                self.gespeichert = {str(k): v for k, v in roh["ziele"].items() if isinstance(v, dict)}
        except (OSError, ValueError):
            self.gespeichert = {}

    def zuordnen(self, ziel_schluessel: str, stabil: str) -> None:
        """Dieses Gate (z. B. ein Fenster mit wechselndem Handle) bekommt einen stabilen Namen (z. B. „chrome.exe“): ein leeres Dokument holt dann die gespeicherten Objekte."""
        self.stabil[ziel_schluessel] = stabil
        dok = self.dokument(ziel_schluessel)
        if not dok.objekte and stabil in self.gespeichert:
            geladen = Dokument.aus_dict(self.gespeichert[stabil], ziel_schluessel)
            dok.objekte = geladen.objekte
            dok._z = geladen._z
            dok.version += 1

    def speichern(self, pfad) -> bool:
        import json
        for schluessel, dok in self.dokumente.items():
            stabil = self.stabil.get(schluessel, "desktop" if schluessel == "desktop" else None)
            if stabil is None:
                continue
            if dok.objekte:
                self.gespeichert[stabil] = dok.zu_dict()
            else:
                self.gespeichert.pop(stabil, None)
        try:
            pfad.parent.mkdir(parents=True, exist_ok=True)
            temp = pfad.with_suffix(".tmp")
            temp.write_text(json.dumps({"version": 1, "ziele": self.gespeichert}, ensure_ascii=False), encoding="utf-8")
            temp.replace(pfad)
            return True
        except OSError:
            return False

    def komposit(self, tid: str, ziel_schluessel: str | None, gate: Rechteck, ausschnitt_screen: Rechteck) -> Komposit | None:
        """Für den Bilderstrom: gibt es für diesen Agenten in seinem Gate etwas zu komponieren? Sonst None (keine Mehrarbeit, kein verändertes Bild)."""
        dokument = self.dokumente.get(ziel_schluessel) if ziel_schluessel else None
        if dokument is None or not dokument.fuer_empfaenger(tid):
            return None
        return Komposit(token_fuer(dokument, tid, gate),
                        lambda bild, d=dokument: komponiere(bild, d, tid, gate, ausschnitt_screen))
