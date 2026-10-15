"""Tasten unter X11 in der Sprache des Körpers (Windows-Tastencodes): Übersetzung, Zustandsabfrage und globale Hotkeys.

Der Körper denkt in Windows-Tastencodes (`VK_*`, Modifikatoren `MOD_*`). Hier stehen die Tabellen dazu und die zwei X11-Aufgaben, die kein
Fenster erledigen kann: den Tastenzustand lesen (wird gerade Strg gehalten?) und eine Taste systemweit abfangen (Hotkey, Not-Aus), auch wenn ein
anderes Programm den Fokus hat.
"""

from __future__ import annotations

import queue
import threading
import time
from collections.abc import Callable

from . import win32 as w

# X-Keysym (unverschoben) -> Windows-Tastencode
KEYSYM_ZU_VK: dict[int, int] = {
    0xFF08: 0x08, 0xFF09: 0x09, 0xFE20: 0x09, 0xFF0D: 0x0D, 0xFF8D: 0x0D, 0xFF1B: 0x1B, 0x0020: 0x20,
    0xFF55: 0x21, 0xFF56: 0x22, 0xFF57: 0x23, 0xFF50: 0x24, 0xFF51: 0x25, 0xFF52: 0x26, 0xFF53: 0x27, 0xFF54: 0x28,
    0xFF63: 0x2D, 0xFFFF: 0x2E, 0xFFE1: 0x10, 0xFFE2: 0x10, 0xFFE3: 0x11, 0xFFE4: 0x11, 0xFFE9: 0x12, 0xFFEA: 0x12, 0xFE03: 0x12,
    0xFFEB: 0x5B, 0xFFEC: 0x5C, 0xFFE5: 0x14, 0xFF7F: 0x90, 0xFF14: 0x91, 0xFF13: 0x13, 0xFF67: 0x5D,
    0xFFAA: 0x6A, 0xFFAB: 0x6B, 0xFFAD: 0x6D, 0xFFAE: 0x6E, 0xFFAF: 0x6F,
    0x003B: 0xBA, 0x003D: 0xBB, 0x002C: 0xBC, 0x002D: 0xBD, 0x002E: 0xBE, 0x002F: 0xBF, 0x0060: 0xC0,
    0x005B: 0xDB, 0x005C: 0xDC, 0x005D: 0xDD, 0x0027: 0xDE,
}
for _i in range(10):
    KEYSYM_ZU_VK[0x30 + _i] = 0x30 + _i  # Ziffern
    KEYSYM_ZU_VK[0xFFB0 + _i] = 0x60 + _i  # Ziffernblock
for _i in range(26):
    KEYSYM_ZU_VK[0x61 + _i] = 0x41 + _i  # a..z
    KEYSYM_ZU_VK[0x41 + _i] = 0x41 + _i  # A..Z
for _i in range(24):
    KEYSYM_ZU_VK[0xFFBE + _i] = 0x70 + _i  # F1..F24

VK_ZU_KEYSYM: dict[int, int] = {}
for _keysym, _vk in KEYSYM_ZU_VK.items():
    VK_ZU_KEYSYM.setdefault(_vk, _keysym)
for _i in range(26):
    VK_ZU_KEYSYM[0x41 + _i] = 0x61 + _i  # Buchstaben als Kleinbuchstaben-Keysym
VK_ZU_KEYSYM[0x0D] = 0xFF0D
VK_ZU_KEYSYM[0x09] = 0xFF09

# Windows-Modifikator (MOD_*) -> X-Maske
X_SHIFT, X_LOCK, X_CONTROL, X_MOD1, X_MOD2, X_MOD4 = 0x1, 0x2, 0x4, 0x8, 0x10, 0x40


def modifikatoren_zu_maske(modifikatoren: int) -> int:
    maske = 0
    if modifikatoren & w.MOD_SHIFT:
        maske |= X_SHIFT
    if modifikatoren & w.MOD_CONTROL:
        maske |= X_CONTROL
    if modifikatoren & w.MOD_ALT:
        maske |= X_MOD1
    if modifikatoren & w.MOD_WIN:
        maske |= X_MOD4
    return maske


def vk_aus_keysym(keysym: int) -> int:
    return KEYSYM_ZU_VK.get(int(keysym), 0)


def _keycodes(anzeige, keysym: int) -> list[int]:
    """Die Tastencodes dieser Anzeige, die den Keysym erzeugen (python-xlib liefert Paare aus Code und Spalte)."""
    return [int(c[0] if isinstance(c, tuple) else c) for c in anzeige.keysym_to_keycodes(keysym) if (c[0] if isinstance(c, tuple) else c)]


# ---- Zustand --------------------------------------------------------------------------------------------------------
def taste_unten(vk: int) -> bool:
    """Wird diese Taste (Windows-Tastencode) gerade gehalten? Shift, Strg, Alt zählen links wie rechts."""
    from . import x11_helfer as x

    anzeige = x.anzeige()
    keysyms = [VK_ZU_KEYSYM[vk]] if vk in VK_ZU_KEYSYM else []
    if vk == 0x10:
        keysyms = [0xFFE1, 0xFFE2]
    elif vk == 0x11:
        keysyms = [0xFFE3, 0xFFE4]
    elif vk == 0x12:
        keysyms = [0xFFE9, 0xFFEA]
    if vk in (0x01, 0x02):  # Maustasten
        maske = anzeige.screen().root.query_pointer().mask
        return bool(maske & (0x100 if vk == 0x01 else 0x400))
    belegung = anzeige.query_keymap()
    for keysym in keysyms:
        for code in _keycodes(anzeige, keysym):
            if belegung[code // 8] & (1 << (code % 8)):
                return True
    return False


# ---- Globale Hotkeys -------------------------------------------------------------------------------------------------
class HotkeyFaden:
    """Fängt Tastenkombinationen systemweit ab (XGrabKey auf der Wurzel) und ruft sie über `abliefern` im GUI-Faden auf.

    Jede Kombination wird auch mit gedrückter Feststell- und Num-Taste abgefangen, sonst ginge sie bei aktiver Num-Taste verloren."""

    def __init__(self, abliefern: Callable[[Callable[[], None]], None]):
        self._abliefern = abliefern
        self._befehle: queue.SimpleQueue = queue.SimpleQueue()
        self._ziele: dict[tuple[int, int], Callable[[], None]] = {}  # (Keycode, Maske ohne Lock/Num) -> Aufruf
        self._stop = threading.Event()
        self._faden: threading.Thread | None = None
        self._ergebnisse: dict[int, bool] = {}
        self._zaehler = 0
        self._bereit = threading.Event()

    def starten(self) -> None:
        if self._faden is None:
            self._faden = threading.Thread(target=self._lauf, name="hotkeys-x11", daemon=True)
            self._faden.start()
            self._bereit.wait(2.0)

    def beenden(self) -> None:
        self._stop.set()

    def eintragen(self, vk: int, modifikatoren: int, aufruf: Callable[[], None], warten_s: float = 2.0) -> bool:
        """Kombination abfangen. False, wenn X sie nicht hergibt (schon von einem anderen Programm belegt) oder der Keysym unbekannt ist."""
        self.starten()
        self._zaehler += 1
        nummer = self._zaehler
        self._befehle.put(("grab", nummer, vk, modifikatoren, aufruf))
        ende = time.monotonic() + warten_s
        while time.monotonic() < ende:
            if nummer in self._ergebnisse:
                return self._ergebnisse.pop(nummer)
            time.sleep(0.005)
        return False

    def loeschen(self, vk: int, modifikatoren: int) -> None:
        self._befehle.put(("ungrab", 0, vk, modifikatoren, None))

    def _lauf(self) -> None:
        from Xlib import X, error
        from Xlib import display as xdisplay

        anzeige = xdisplay.Display()
        wurzel = anzeige.screen().root
        self._bereit.set()
        lock_varianten = (0, X_LOCK, X_MOD2, X_LOCK | X_MOD2)

        def schluessel(vk: int, mod: int) -> tuple[int, int] | None:
            keysym = VK_ZU_KEYSYM.get(vk)
            if keysym is None:
                return None
            codes = _keycodes(anzeige, keysym)
            return (codes[0], modifikatoren_zu_maske(mod)) if codes else None

        try:
            while not self._stop.is_set():
                try:
                    befehl, nummer, vk, mod, aufruf = self._befehle.get_nowait()
                except queue.Empty:
                    befehl = None
                if befehl == "grab":
                    ziel = schluessel(vk, mod)
                    ok = False
                    if ziel is not None:
                        fehler: list = []
                        for lock in lock_varianten:
                            wurzel.grab_key(ziel[0], ziel[1] | lock, True, X.GrabModeAsync, X.GrabModeAsync,
                                            onerror=lambda e, f=fehler: f.append(e))
                        anzeige.sync()
                        ok = not fehler
                        if ok:
                            self._ziele[ziel] = aufruf
                    self._ergebnisse[nummer] = ok
                elif befehl == "ungrab":
                    ziel = schluessel(vk, mod)
                    if ziel is not None:
                        for lock in lock_varianten:
                            wurzel.ungrab_key(ziel[0], ziel[1] | lock)
                        anzeige.sync()
                        self._ziele.pop(ziel, None)
                while anzeige.pending_events():
                    ereignis = anzeige.next_event()
                    if ereignis.type == X.KeyPress:
                        maske = ereignis.state & (X_SHIFT | X_CONTROL | X_MOD1 | X_MOD4)
                        aufruf = self._ziele.get((ereignis.detail, maske))
                        if aufruf is not None:
                            self._abliefern(aufruf)
                time.sleep(0.01)
        except (error.XError, OSError):
            pass
        finally:
            try:
                anzeige.close()
            except Exception:
                pass
