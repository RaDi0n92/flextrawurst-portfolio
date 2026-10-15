"""Sichtbarkeit pro Fenster: jedes Fenster des Körpers (Raute, Terminal, Chat, Regieleiste) hat seine eigene Regel.

* `immer`: das Fenster steht auf dem Desktop und bleibt, wo Daniel es hinlegt (Standard).
* `programm`: das Fenster erscheint nur, solange dieses Programm (oder Spiel, Fenster: gemeint ist die exe des
  Vordergrundfensters) vorn ist, und verschwindet, sobald ein anderes Programm vorn ist.

Die Regel greift nur an den **Kanten** (Programm wird vorn / verliert den Vordergrund), nicht dauernd. So bleibt
Daniels eigene Bedienung (Terminal per X ausblenden, wieder einblenden) erhalten. Steht eines der eigenen Fenster
vorn (Chat tippen, Terminal benutzen), gilt weiter das zuletzt gesehene fremde Programm.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Callable
from dataclasses import dataclass

MODUS_IMMER, MODUS_PROGRAMM = "immer", "programm"


@dataclass(frozen=True)
class Regel:
    modus: str = MODUS_IMMER
    programm: str = ""  # Dateiname der exe, klein geschrieben, z. B. "notepad.exe"
    beschriftung: str = ""  # nur zur Anzeige, z. B. das Fenstertitel-Beispiel beim Aussuchen

    def text(self) -> str:
        return "immer sichtbar" if self.modus == MODUS_IMMER else f"nur bei {self.programm}"

    def zu_dict(self) -> dict:
        return {"modus": self.modus, "programm": self.programm, "beschriftung": self.beschriftung}

    @staticmethod
    def aus_dict(daten: object) -> "Regel":
        """Tolerant gegenüber kaputten Dateien: alles Unklare wird zu „immer sichtbar“."""
        if not isinstance(daten, dict) or daten.get("modus") != MODUS_PROGRAMM:
            return IMMER
        programm = daten.get("programm")
        if not isinstance(programm, str) or not programm.strip():
            return IMMER
        beschriftung = daten.get("beschriftung")
        return Regel(MODUS_PROGRAMM, programm.strip().lower(), beschriftung[:80] if isinstance(beschriftung, str) else "")


IMMER = Regel()


def programm_regel(programm: str, beschriftung: str = "") -> Regel:
    return Regel(MODUS_PROGRAMM, programm.strip().lower(), beschriftung)


@dataclass(frozen=True)
class Vordergrund:
    pid: int
    programm: str  # Dateiname der exe, klein geschrieben; "" wenn unbekannt
    titel: str = ""


@dataclass(frozen=True)
class Programm:
    programm: str
    titel: str  # Beispieltitel eines Fensters dieses Programms


def dateiname(pfad: str | None) -> str:
    return os.path.basename((pfad or "").replace("\\", "/")).lower()


class WindowsQuelle:
    """Vordergrundfenster und offene Programme über die vorhandene Fensteraufzählung des Scanners."""

    def __init__(self, api=None):
        if api is None:
            from augen_haende_bridge.windows_scanner import Win32WindowApi
            api = Win32WindowApi()
        self._api = api

    def vordergrund(self) -> Vordergrund | None:
        from . import win32 as w

        hwnd = w.user32.GetForegroundWindow()
        if not hwnd:
            return None
        import ctypes
        from ctypes import wintypes

        pid = wintypes.DWORD()
        self._api.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        pid_wert = int(pid.value)
        if not pid_wert:
            return None
        return Vordergrund(pid_wert, dateiname(self._api._process_path(pid_wert)), self._api._window_text(hwnd))

    def bildschirm(self) -> tuple[int, int, int, int]:
        return self._api.virtual_screen_rect()

    def offene_programme(self, ohne_pid: int | None = None) -> list[Programm]:
        gesehen: dict[str, Programm] = {}
        for fenster in self._api.enumerate_windows():
            if fenster.process_id == ohne_pid:
                continue
            name = dateiname(fenster.process_path)
            if not name or name in gesehen or not (fenster.title or "").strip():
                continue
            gesehen[name] = Programm(name, fenster.title)
        return sorted(gesehen.values(), key=lambda p: p.programm)


@dataclass
class Element:
    fenster: object
    regel: Regel = IMMER
    nutzer_verborgen: Callable[[], bool] = lambda: False
    zuletzt: bool | None = None  # ob die Regel zuletzt „passt“ war; None = noch nie geprüft


class Sichtbarkeit:
    def __init__(self, quelle, eigene_pid: int | None = None, takt_s: float = 0.3):
        self._quelle = quelle
        self._eigene_pid = eigene_pid if eigene_pid is not None else os.getpid()
        self._takt_s = takt_s
        self.elemente: dict[str, Element] = {}
        self.letzter: Vordergrund | None = None  # zuletzt gesehenes fremdes Vordergrundprogramm
        self._stop = threading.Event()
        self._faden: threading.Thread | None = None

    # ---- Verwaltung -------------------------------------------------------------------------------------------
    def registrieren(self, schluessel: str, fenster, regel: Regel = IMMER,
                     nutzer_verborgen: Callable[[], bool] = lambda: False) -> None:
        self.elemente[schluessel] = Element(fenster, regel, nutzer_verborgen)
        self._anwenden(self.elemente[schluessel], mit_kante=False)

    def entfernen(self, schluessel: str) -> None:
        self.elemente.pop(schluessel, None)

    def regel(self, schluessel: str) -> Regel:
        element = self.elemente.get(schluessel)
        return element.regel if element is not None else IMMER

    def regel_setzen(self, schluessel: str, regel: Regel) -> None:
        element = self.elemente.get(schluessel)
        if element is None:
            return
        element.regel = regel
        element.zuletzt = None
        self._anwenden(element, mit_kante=False)

    def sichtbar_erlaubt(self, schluessel: str) -> bool:
        """Darf dieses Fenster gerade Meldungen zeigen (z. B. Banner/Ticker an einer Raute)?"""
        element = self.elemente.get(schluessel)
        if element is None or element.regel.modus == MODUS_IMMER:
            return True
        return self._passt(element.regel)

    # ---- Prüfen ----------------------------------------------------------------------------------------------
    def _passt(self, regel: Regel) -> bool:
        return regel.modus == MODUS_IMMER or (self.letzter is not None and self.letzter.programm == regel.programm)

    def tick(self) -> None:
        """Im GUI-Thread: Vordergrund lesen und die Regeln an den Kanten anwenden."""
        try:
            vorn = self._quelle.vordergrund()
        except Exception:
            return
        if vorn is None or vorn.pid == self._eigene_pid:
            return  # eigene Fenster vorn (Chat tippen, Terminal benutzen): es gilt weiter das letzte fremde Programm
        if vorn == self.letzter:
            return
        self.letzter = vorn
        for element in list(self.elemente.values()):
            self._anwenden(element, mit_kante=True)

    def _anwenden(self, element: Element, *, mit_kante: bool) -> None:
        if element.regel.modus == MODUS_IMMER:
            element.zuletzt = None
            return
        if self.letzter is None:
            return  # noch kein fremdes Programm gesehen: nichts tun
        passt = self._passt(element.regel)
        if mit_kante and passt == element.zuletzt:
            return
        element.zuletzt = passt
        if passt:
            if not element.nutzer_verborgen():
                element.fenster.zeige(aktivieren=False)
        else:
            element.fenster.verberge()

    # ---- Hintergrundtakt -------------------------------------------------------------------------------------
    def starten(self, gui_post: Callable[[Callable[[], None]], None], nebenbei: Callable[[], None] | None = None,
                nebenbei_alle_s: float = 30.0) -> None:
        """Ein Faden stößt `tick` im GUI-Thread an (Fenster dürfen nur dort angefasst werden)."""
        def lauf() -> None:
            vergangen = 0.0
            while not self._stop.wait(self._takt_s):
                gui_post(self.tick)
                vergangen += self._takt_s
                if nebenbei is not None and vergangen >= nebenbei_alle_s:
                    vergangen = 0.0
                    gui_post(nebenbei)

        self._faden = threading.Thread(target=lauf, name="sichtbarkeit", daemon=True)
        self._faden.start()

    def stoppen(self) -> None:
        self._stop.set()
