"""Lokaler Not-Aus (R066, `78_augen_und_haende_bauplan.md` 3.1): wirkt unabhängig von Verbindung, Agentenstatus und
GUI-Thread.

`NotAus` ist ein thread-sicheres Flag mit Lauschern. Der `TastaturHook` (F12) läuft in einem eigenen Faden mit
eigener Nachrichtenschleife (`WH_KEYBOARD_LL`); er setzt das Flag direkt, ohne den GUI-Thread zu brauchen. Wer etwas
sendet oder aufnimmt, fragt `aktiv` ab. Der Not-Aus schluckt die Taste nicht. Die Latenz ist nicht gemessen und wird
nicht behauptet.
"""

from __future__ import annotations

import ctypes
import threading
from collections.abc import Callable

from . import win32 as w

WM_KEYDOWN_NACHRICHTEN = (w.WM_KEYDOWN, w.WM_SYSKEYDOWN)


class NotAus:
    def __init__(self) -> None:
        self._ereignis = threading.Event()
        self._sperre = threading.Lock()
        self.grund = ""
        self._bei_ausloesen: list[Callable[[str], None]] = []
        self._bei_freigabe: list[Callable[[], None]] = []

    @property
    def aktiv(self) -> bool:
        return self._ereignis.is_set()

    def bei_ausloesen(self, aufruf: Callable[[str], None]) -> None:
        self._bei_ausloesen.append(aufruf)

    def bei_freigabe(self, aufruf: Callable[[], None]) -> None:
        self._bei_freigabe.append(aufruf)

    def ausloesen(self, grund: str = "") -> bool:
        """True beim ersten Auslösen; ein zweites Auslösen ändert nichts."""
        with self._sperre:
            if self._ereignis.is_set():
                return False
            self.grund = grund
            self._ereignis.set()
        for aufruf in list(self._bei_ausloesen):
            try:
                aufruf(grund)
            except Exception:  # ein kaputter Lauscher darf die anderen nicht aufhalten
                pass
        return True

    def freigeben(self) -> bool:
        with self._sperre:
            if not self._ereignis.is_set():
                return False
            self._ereignis.clear()
            self.grund = ""
        for aufruf in list(self._bei_freigabe):
            try:
                aufruf()
            except Exception:
                pass
        return True


def ist_ausloeser(nachricht: int, vk: int, erwartet: int) -> bool:
    return nachricht in WM_KEYDOWN_NACHRICHTEN and vk == erwartet


class TastaturHook:
    """Systemweiter Low-Level-Hook in eigenem Faden; unabhängig vom GUI-Thread."""

    def __init__(self, not_aus: NotAus, *, vk: int = w.VK_F12, name: str = "F12"):
        self.not_aus, self.vk, self.name = not_aus, vk, name
        self.installiert = False
        self.fehler: str | None = None
        self._faden: threading.Thread | None = None
        self._faden_id = 0
        self._bereit = threading.Event()
        self._hook = None
        self._proc = None  # Referenz halten, sonst räumt ctypes den Rückruf ab

    def start(self, timeout: float = 5.0) -> bool:
        w.require_windows()
        self._faden = threading.Thread(target=self._lauf, name="notaus-hook", daemon=True)
        self._faden.start()
        self._bereit.wait(timeout)
        return self.installiert

    def _lauf(self) -> None:
        self._faden_id = int(w.kernel32.GetCurrentThreadId())

        def rueckruf(n_code, wparam, lparam):
            if n_code == w.HC_ACTION:
                info = ctypes.cast(lparam, ctypes.POINTER(w.KBDLLHOOKSTRUCT)).contents
                if ist_ausloeser(int(wparam), int(info.vkCode), self.vk):
                    self.not_aus.ausloesen(self.name)
            return w.user32.CallNextHookEx(None, n_code, wparam, lparam)

        self._proc = w.HOOKPROC(rueckruf)
        self._hook = w.user32.SetWindowsHookExW(w.WH_KEYBOARD_LL, self._proc, w.kernel32.GetModuleHandleW(None), 0)
        if not self._hook:
            self.fehler = f"SetWindowsHookExW fehlgeschlagen: {w.last_error()}"
            self._bereit.set()
            return
        self.installiert = True
        self._bereit.set()
        nachricht = w.MSG()
        while w.user32.GetMessageW(ctypes.byref(nachricht), None, 0, 0) > 0:
            w.user32.TranslateMessage(ctypes.byref(nachricht))
            w.user32.DispatchMessageW(ctypes.byref(nachricht))
        w.user32.UnhookWindowsHookEx(self._hook)
        self.installiert = False

    def stop(self) -> None:
        if self._faden is not None and self._faden.is_alive() and self._faden_id:
            w.user32.PostThreadMessageW(self._faden_id, w.WM_QUIT, 0, 0)
            self._faden.join(timeout=3.0)
