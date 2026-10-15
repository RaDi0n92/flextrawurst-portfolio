"""Eine Bildfolge als Quelle für einen Agenten (R038): die Bilder eines Ordners nacheinander, mit Start, Pause, Fortsetzen und Stop.

Die Bridge sendet im Abstand `takt_s` das jeweils nächste Bild (Quelle „file“) und zählt mit. Ein Stop beendet die Folge, ein Pause hält sie an der Stelle fest.
Not-Aus und „nur Terminal“ stoppen sie. Es läuft nichts, was Daniel nicht gestartet hat, und nichts startet von selbst neu.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Callable
from dataclasses import dataclass, field

ENDUNGEN = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
MAX_BILDER = 500
TAKT_S = 2.0


def bilder_im_ordner(ordner: str) -> list[str]:
    """Die Bilddateien eines Ordners in Namensreihenfolge (höchstens MAX_BILDER)."""
    try:
        namen = sorted(n for n in os.listdir(ordner) if n.lower().endswith(ENDUNGEN))
    except OSError:
        return []
    return [os.path.join(ordner, n) for n in namen[:MAX_BILDER]]


@dataclass
class Folge:
    pfade: list[str]
    index: int = 0
    pausiert: bool = False
    laeuft: bool = True
    fehler: int = 0
    stopp: threading.Event = field(default_factory=threading.Event)
    faden: threading.Thread | None = None

    def text(self) -> str:
        if not self.laeuft:
            return "beendet"
        return f"{'pausiert' if self.pausiert else 'läuft'} ({min(self.index, len(self.pfade))}/{len(self.pfade)})"


class Bildfolgen:
    """Je Agent höchstens eine Folge."""

    def __init__(self, senden: Callable[[str, str], bool], takt_s: float = TAKT_S, fertig: Callable[[str], None] = lambda tid: None):
        self._senden, self._takt_s, self._fertig = senden, takt_s, fertig
        self.folgen: dict[str, Folge] = {}
        self._sperre = threading.Lock()

    def starten(self, tid: str, pfade: list[str]) -> bool:
        if not pfade:
            return False
        self.stoppen(tid)
        folge = Folge(list(pfade))
        folge.faden = threading.Thread(target=self._lauf, args=(tid, folge), daemon=True, name=f"bildfolge-{tid}")
        with self._sperre:
            self.folgen[tid] = folge
        folge.faden.start()
        return True

    def _lauf(self, tid: str, folge: Folge) -> None:
        while not folge.stopp.is_set() and folge.index < len(folge.pfade):
            if folge.pausiert:
                if folge.stopp.wait(0.1):
                    break
                continue
            pfad = folge.pfade[folge.index]
            if not self._senden(tid, pfad):
                folge.fehler += 1
            folge.index += 1
            if folge.stopp.wait(self._takt_s):
                break
        folge.laeuft = False
        self._fertig(tid)

    def pausieren(self, tid: str, an: bool) -> None:
        folge = self.folgen.get(tid)
        if folge is not None and folge.laeuft:
            folge.pausiert = an

    def stoppen(self, tid: str) -> None:
        with self._sperre:
            folge = self.folgen.pop(tid, None)
        if folge is not None:
            folge.stopp.set()
            folge.laeuft = False
            if folge.faden is not None and folge.faden is not threading.current_thread():
                folge.faden.join(timeout=2.0)

    def alle_stoppen(self) -> None:
        for tid in list(self.folgen):
            self.stoppen(tid)

    def text(self, tid: str) -> str:
        folge = self.folgen.get(tid)
        return folge.text() if folge is not None else "keine"
