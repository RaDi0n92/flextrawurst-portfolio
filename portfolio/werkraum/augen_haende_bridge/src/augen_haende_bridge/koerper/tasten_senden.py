"""Die Hände des Agenten, eng begrenzt: echte Tastendrücke über SendInput, nur für das Eingabefeld seiner eigenen Raute.

Ein Auftrag `schreibe "Text"` macht genau dies: die Tastenkombination der Raute des Agenten drücken (öffnet sein Eingabefeld),
warten, bis das Feld wirklich offen ist **und die Tastatur hat**, den Text tippen und mit Enter bestätigen. Bei jedem Schritt wird geprüft,
dass das Feld noch vorn steht; sonst bricht der Auftrag ab und es wird **nichts weiter** gedrückt (ein Tastendruck in ein fremdes
Fenster wäre ein Schaden). Not-Aus (F12), ein ausgeschalteter Hände-Schalter und ein fehlender Hotkey verhindern den Auftrag ganz.
"""

from __future__ import annotations

import ctypes
import time
from collections.abc import Callable
from dataclasses import dataclass

from . import win32 as w
from .tastenkombi import Kombination

KEYEVENTF_KEYUP, KEYEVENTF_UNICODE = 0x0002, 0x0004
VK_RETURN = 0x0D
MODIFIKATOR_TASTEN = ((w.MOD_CONTROL, 0x11), (w.MOD_ALT, 0x12), (w.MOD_SHIFT, 0x10), (w.MOD_WIN, 0x5B))
TEXT_STUECK = 8  # Zeichen je SendInput-Aufruf; dazwischen wird die Fokusprüfung wiederholt
WARTE_FELD_S = 2.5
WARTE_RUHE_S = 6.0  # so lange wartet der Schreibweg darauf, dass Daniel nicht tippt oder klickt, bevor er aufgibt

Ereignis = tuple[int, int, int]  # (vk, scan, flags)


def text_ereignisse(text: str) -> list[Ereignis]:
    """Unicode-Tastenereignisse (Drücken und Loslassen je UTF-16-Einheit); Zeilenumbrüche werden zu Leerzeichen."""
    daten = text.replace("\r", " ").replace("\n", " ").encode("utf-16-le")
    einheiten = [int.from_bytes(daten[i:i + 2], "little") for i in range(0, len(daten), 2)]
    ereignisse: list[Ereignis] = []
    for einheit in einheiten:
        ereignisse.append((0, einheit, KEYEVENTF_UNICODE))
        ereignisse.append((0, einheit, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))
    return ereignisse


def kombination_ereignisse(kombi: Kombination) -> list[Ereignis]:
    mods = [vk for maske, vk in MODIFIKATOR_TASTEN if kombi.modifikatoren & maske]
    runter = [(vk, 0, 0) for vk in mods] + [(kombi.vk, 0, 0)]
    hoch = [(kombi.vk, 0, KEYEVENTF_KEYUP)] + [(vk, 0, KEYEVENTF_KEYUP) for vk in reversed(mods)]
    return runter + hoch


def enter_ereignisse() -> list[Ereignis]:
    return [(VK_RETURN, 0, 0), (VK_RETURN, 0, KEYEVENTF_KEYUP)]


def windows_sendinput(ereignisse: list[Ereignis]) -> int:
    """Schickt die Ereignisse über SendInput; liefert, wie viele das System angenommen hat."""
    w.require_windows()
    ulong_ptr = ctypes.c_size_t

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_uint32),
                    ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ulong_ptr)]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16), ("dwFlags", ctypes.c_uint32),
                    ("time", ctypes.c_uint32), ("dwExtraInfo", ulong_ptr)]

    class _Vereinigung(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_uint32), ("u", _Vereinigung)]

    feld = (INPUT * len(ereignisse))()
    for i, (vk, scan, flags) in enumerate(ereignisse):
        feld[i].type = 1  # INPUT_KEYBOARD
        feld[i].u.ki = KEYBDINPUT(vk, scan, flags, 0, 0)
    dll = ctypes.WinDLL("user32", use_last_error=True)
    dll.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
    dll.SendInput.restype = ctypes.c_uint
    return int(dll.SendInput(len(ereignisse), feld, ctypes.sizeof(INPUT)))


@dataclass
class Ergebnis:
    ok: bool
    grund: str = ""


class Haende:
    """Führt einen `schreibe`-Auftrag aus. Alles Äußere ist einspeisbar (Senden, Feld-Abfrage, Uhr), damit es ohne Windows testbar ist."""

    def __init__(self, senden: Callable[[list[Ereignis]], int] = windows_sendinput,
                 uhr: Callable[[], float] = time.monotonic, schlafen: Callable[[float], None] = time.sleep):
        self._senden, self._uhr, self._schlafen = senden, uhr, schlafen

    def schreiben(self, text: str, kombi: Kombination | None, *, feld_hat_fokus: Callable[[], bool],
                  gesperrt: Callable[[], bool], feld_schliessen: Callable[[], None],
                  ruhig: Callable[[], bool] = lambda: True, eigene_markieren: Callable[[], None] = lambda: None) -> Ergebnis:
        """`ruhig()`: Daniel tippt und klickt gerade nicht. Ohne Ruhe drückt dieser Weg nichts: Die Tastenkombination der Raute holt sich den Fokus
        und würde Daniels Eingabe in das Feld des Agenten lenken, oder der Text des Agenten in Daniels Feld. `eigene_markieren()` läuft vor jedem Senden,
        damit die eigenen Tasten nicht als Eingabe von Daniel zählen."""
        if not text.strip():
            return Ergebnis(False, "leerer_text")
        if kombi is None:
            return Ergebnis(False, "keine_tastenkombination")
        if gesperrt():
            return Ergebnis(False, "gesperrt")
        ruhe_ende = self._uhr() + WARTE_RUHE_S
        while not ruhig():
            if gesperrt():
                return Ergebnis(False, "gesperrt")
            if self._uhr() >= ruhe_ende:
                return Ergebnis(False, "daniel_uebernimmt")
            self._schlafen(0.1)
        eigene_markieren()
        if not self._senden(kombination_ereignisse(kombi)):
            return Ergebnis(False, "sendinput_fehlgeschlagen")
        ende = self._uhr() + WARTE_FELD_S
        while not feld_hat_fokus():
            if self._uhr() >= ende:
                return Ergebnis(False, "feld_nicht_geoeffnet")
            self._schlafen(0.05)
        ereignisse = text_ereignisse(text)
        for i in range(0, len(ereignisse), TEXT_STUECK * 2):
            if gesperrt() or not feld_hat_fokus():
                feld_schliessen()
                return Ergebnis(False, "gesperrt" if gesperrt() else "fokus_verloren")
            eigene_markieren()
            self._senden(ereignisse[i:i + TEXT_STUECK * 2])
            self._schlafen(0.02)
        if gesperrt() or not feld_hat_fokus():
            feld_schliessen()
            return Ergebnis(False, "gesperrt" if gesperrt() else "fokus_verloren")
        eigene_markieren()
        self._senden(enter_ereignisse())
        return Ergebnis(True)
