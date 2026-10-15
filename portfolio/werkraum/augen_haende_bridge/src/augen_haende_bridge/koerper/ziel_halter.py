"""Ort der Elemente bei gebundenem Zielfenster (R121, Daniels Beschluss vom 2026-10-01).

Ist als Ziel eines Agenten ein einzelnes Fenster gebunden (z. B. ein Browser), kann Daniel für jedes Element dieses Agenten (Raute, Terminal,
Selbstbild) wählen: **Desktop** (wie bisher) oder **im Ziel**. Im Ziel gilt:

* das Element ist eingerahmt: es bleibt ganz innerhalb des Zielfensters, auch beim Ziehen und wenn das Zielfenster kleiner wird;
* es wandert mit, wenn das Zielfenster verschoben wird, und bleibt an derselben Stelle im Fenster;
* es wird mit dem Zielfenster minimiert (versteckt) und kommt mit ihm zurück;
* es verschwindet, wenn das Zielfenster geschlossen wird (es geht nicht zurück auf den Desktop);
* hat der Agent kein Fenster mehr als Ziel (Desktop gebunden oder gelöst), steht das Element wieder auf dem Desktop.

Elemente auf „Desktop“ bleiben von all dem unberührt. Die Prüfung läuft in einem Takt im GUI-Thread (`tick`).
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field

Rechteck = tuple[int, int, int, int]
ORT_DESKTOP, ORT_ZIEL = "desktop", "ziel"
TAKT_S = 0.15


def klemmen(position: tuple[int, int], groesse: tuple[int, int], ziel: Rechteck) -> tuple[int, int]:
    """Obere linke Ecke so, dass ein Element dieser Größe ganz im Ziel liegt; ist es größer als das Ziel, sitzt es an der oberen linken Ecke."""
    x = max(ziel[0], min(position[0], ziel[2] - groesse[0]))
    y = max(ziel[1], min(position[1], ziel[3] - groesse[1]))
    return max(ziel[0], x), max(ziel[1], y)


def fenster_zustand(hwnd: int) -> tuple[bool, bool, Rechteck | None]:
    """(gibt es das Fenster noch, ist es minimiert, sein Rechteck in Bildschirmkoordinaten)."""
    import ctypes

    from . import win32 as w

    if not w.user32.IsWindow(hwnd):
        return False, False, None
    if w.user32.IsIconic(hwnd):
        return True, True, None
    rect = w.RECT()
    if not w.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False, False, None
    return True, False, (rect.left, rect.top, rect.right, rect.bottom)


@dataclass
class Element:
    fenster: object
    ziel_hwnd: Callable[[], int | None]
    nutzer_verborgen: Callable[[], bool] = lambda: False
    ort: str = ORT_DESKTOP
    rel: tuple[int, int] = (0, 0)
    gesetzt: tuple[int, int] | None = None  # wohin dieser Halter das Element zuletzt gestellt hat (Abweichung = Daniel hat es verschoben)
    letztes_ziel: Rechteck | None = None
    versteckt: bool = False
    grund: str = ""


class ZielHalter:
    def __init__(self, zustand: Callable[[int], tuple[bool, bool, Rechteck | None]] = fenster_zustand,
                 melden: Callable[[], None] = lambda: None, takt_s: float = TAKT_S):
        self._zustand, self._melden, self._takt_s = zustand, melden, takt_s
        self.elemente: dict[str, Element] = {}
        self._stop = threading.Event()

    # ---- Verwalten -------------------------------------------------------------------------------------------------
    def anmelden(self, schluessel: str, fenster, ziel_hwnd: Callable[[], int | None],
                 nutzer_verborgen: Callable[[], bool] = lambda: False) -> None:
        self.elemente[schluessel] = Element(fenster, ziel_hwnd, nutzer_verborgen)

    def abmelden(self, schluessel: str) -> None:
        self.elemente.pop(schluessel, None)

    def ort(self, schluessel: str) -> str:
        element = self.elemente.get(schluessel)
        return element.ort if element is not None else ORT_DESKTOP

    def versteckt(self, schluessel: str) -> bool:
        """Hält gerade das Zielfenster (minimiert oder geschlossen) dieses Element versteckt? (Die Sichtbarkeitsregel fragt das.)"""
        element = self.elemente.get(schluessel)
        return bool(element and element.versteckt)

    def hat_fenster_ziel(self, schluessel: str) -> bool:
        element = self.elemente.get(schluessel)
        return bool(element and element.ziel_hwnd() is not None)

    def setze_ort(self, schluessel: str, ort: str) -> str | None:
        """Wechselt den Ort. Liefert None bei Erfolg, sonst einen Satz, warum es nicht geht."""
        element = self.elemente.get(schluessel)
        if element is None:
            return "Unbekanntes Element"
        if ort == ORT_DESKTOP:
            element.ort, element.letztes_ziel, element.gesetzt = ORT_DESKTOP, None, None
            self._zeigen(element)
            self._melden()
            return None
        hwnd = element.ziel_hwnd()
        if hwnd is None:
            return "Kein einzelnes Fenster als Ziel gebunden (ein ganzer Desktop hat keinen Rahmen)"
        existiert, minimiert, rect = self._zustand(hwnd)
        if not existiert:
            return "Das Zielfenster gibt es nicht mehr"
        element.ort = ORT_ZIEL
        links, oben, _r, _u = element.fenster.rechteck()
        if rect is not None:
            element.rel = (links - rect[0], oben - rect[1])
        element.letztes_ziel, element.gesetzt, element.versteckt = None, None, False
        self.tick()
        self._melden()
        return None

    # ---- Takt ------------------------------------------------------------------------------------------------------
    def tick(self) -> None:
        for element in list(self.elemente.values()):
            if element.ort != ORT_ZIEL:
                continue
            hwnd = element.ziel_hwnd()
            if hwnd is None:  # kein Fenster mehr als Ziel: das Element steht wieder auf dem Desktop
                element.ort, element.letztes_ziel, element.gesetzt = ORT_DESKTOP, None, None
                self._zeigen(element)
                self._melden()
                continue
            existiert, minimiert, rect = self._zustand(hwnd)
            if not existiert:
                self._verstecken(element, "Zielfenster geschlossen")
                continue
            if minimiert or rect is None:
                self._verstecken(element, "Zielfenster minimiert")
                continue
            if element.versteckt:
                self._zeigen(element)
                element.letztes_ziel = None  # frisch nach dem Zurückkommen: an der gemerkten Stelle im Fenster
            self._nachfuehren(element, rect)

    @staticmethod
    def _nachfuehren(element: Element, ziel: Rechteck) -> None:
        links, oben, rechts, unten = element.fenster.rechteck()
        groesse = (rechts - links, unten - oben)
        if element.letztes_ziel is not None and element.gesetzt is not None and (links, oben) != element.gesetzt:
            element.rel = (links - ziel[0], oben - ziel[1])  # Daniel hat das Element verschoben: neue Stelle im Fenster merken
        soll = klemmen((ziel[0] + element.rel[0], ziel[1] + element.rel[1]), groesse, ziel)
        if soll != (links, oben):
            element.fenster.verschiebe(soll[0], soll[1])
        element.gesetzt = soll
        element.rel = (soll[0] - ziel[0], soll[1] - ziel[1])
        element.letztes_ziel = ziel

    def _verstecken(self, element: Element, grund: str) -> None:
        if not element.versteckt:
            element.versteckt, element.grund = True, grund
            element.fenster.verberge()
            self._melden()
        else:
            element.grund = grund

    def _zeigen(self, element: Element) -> None:
        was_versteckt = element.versteckt
        element.versteckt, element.grund = False, ""
        if was_versteckt and not element.nutzer_verborgen():
            element.fenster.zeige(aktivieren=False)
            self._melden()

    # ---- Hintergrundtakt -------------------------------------------------------------------------------------------
    def starten(self, gui_post: Callable[[Callable[[], None]], None]) -> None:
        def lauf() -> None:
            while not self._stop.wait(self._takt_s):
                if any(e.ort == ORT_ZIEL for e in self.elemente.values()):
                    gui_post(self.tick)

        threading.Thread(target=lauf, name="ziel-halter", daemon=True).start()

    def stoppen(self) -> None:
        self._stop.set()
