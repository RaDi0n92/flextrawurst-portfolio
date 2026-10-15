"""Durchklickbare Fenster nach dem Vorbild der Raute: Klicks gehen an das Programm darunter, solange Strg nicht gehalten wird.

Gilt je Fenster einstellbar für Chat, Regieleiste und Terminal (die Raute macht es von sich aus). Umgesetzt mit dem
Fensterstil WS_EX_TRANSPARENT, der auch Fenster anderer Programme (Spiele) durchlässt. Die Tastatur bleibt beim Fenster,
das sie hat: ein einmal angeklicktes Terminal oder der Chat nimmt weiter Eingaben an, auch wenn Strg wieder los ist.
Der Not-Aus F12 hängt nicht an der Maus. Der STOP-Knopf der Leiste braucht im Durchklick-Modus ebenfalls Strg.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass


def strg_gedrueckt() -> bool:
    from . import win32 as w

    return bool(w.user32.GetAsyncKeyState(w.VK_CONTROL) & 0x8000)


@dataclass
class _Eintrag:
    fenster: object
    aktiv: bool
    zuletzt: bool | None = None


class DurchklickVerwalter:
    _erzwungen_bis = 0.0

    def __init__(self, strg: Callable[[], bool] = strg_gedrueckt, takt_s: float = 0.08):
        self._strg = strg
        self._takt_s = takt_s
        self.eintraege: dict[str, _Eintrag] = {}
        self._stop = threading.Event()

    def registrieren(self, schluessel: str, fenster, aktiv: bool = True) -> None:
        self.eintraege[schluessel] = _Eintrag(fenster, aktiv)
        self._anwenden(self.eintraege[schluessel], self._strg())

    def entfernen(self, schluessel: str) -> None:
        self.eintraege.pop(schluessel, None)

    def aktiv(self, schluessel: str) -> bool:
        eintrag = self.eintraege.get(schluessel)
        return eintrag.aktiv if eintrag is not None else False

    def setzen(self, schluessel: str, aktiv: bool) -> None:
        eintrag = self.eintraege.get(schluessel)
        if eintrag is not None:
            eintrag.aktiv = aktiv
            self._anwenden(eintrag, self._strg())

    def umschalten(self, schluessel: str) -> bool:
        self.setzen(schluessel, not self.aktiv(schluessel))
        return self.aktiv(schluessel)

    def gehoert(self, kennung: int | None) -> bool:
        """Ist dieses Fenster (Kennung des Fensters, nicht seines Rahmens) eines, das die Verwaltung durchklickbar hält?"""
        if kennung is None:
            return False
        return any(getattr(e.fenster, "hwnd", None) == int(kennung) for e in list(self.eintraege.values()))

    def erzwingen(self, sekunden: float) -> None:
        """Die Hände eines Agenten bedienen ein Bridge-Fenster: für diese Zeit gelten alle Fenster wie bei gehaltener Bedientaste (klickbar). `0` hebt es auf.
        Der Aufrufer lässt danach `tick` im GUI-Thread laufen, damit der Stil schon vor der Aktion stimmt."""
        self._erzwungen_bis = time.monotonic() + sekunden if sekunden > 0 else 0.0

    def tick(self) -> None:
        """Im GUI-Thread: je Fenster den Stil an den Zustand der Strg-Taste anpassen."""
        strg = self._strg() or time.monotonic() < self._erzwungen_bis
        for eintrag in list(self.eintraege.values()):
            self._anwenden(eintrag, strg)

    @staticmethod
    def _anwenden(eintrag: _Eintrag, strg: bool) -> None:
        durchlaessig = eintrag.aktiv and not strg
        if durchlaessig == eintrag.zuletzt:
            return
        eintrag.zuletzt = durchlaessig
        try:
            eintrag.fenster.durchklick_setzen(durchlaessig)
        except Exception:
            eintrag.zuletzt = None  # beim nächsten Takt erneut versuchen

    def starten(self, gui_post: Callable[[Callable[[], None]], None]) -> None:
        def lauf() -> None:
            while not self._stop.wait(self._takt_s):
                gui_post(self.tick)

        threading.Thread(target=lauf, name="durchklick", daemon=True).start()

    def stoppen(self) -> None:
        self._stop.set()
