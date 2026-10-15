"""Tastenkombinationen: die Bedientaste der Fenster und die Hotkeys der Rauten, beide von Daniel frei wählbar.

* `Bedientaste`: welche Tasten gehalten sein müssen, damit durchklickbare Fenster und die Raute Klicks annehmen
  (Standard Strg+Alt; Strg allein kollidiert mit Spielen, in denen Strg geduckt heißt). Auf deutschen Tastaturen ist
  Strg+Alt dasselbe wie AltGr: beim Tippen von @, { oder \\ werden die Fenster für einen Moment klickbar — harmlos.
* `Kombination`: ein Hotkey (Modifikatoren + Taste) mit Text wie „Strg+Alt+F5“, Erfassung per Tastendruck.
  Reine Buchstaben und Ziffern ohne Modifikator sind nicht erlaubt (ein globaler Hotkey würde das Tippen blockieren).
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from . import win32 as w

VK_STRG, VK_ALT, VK_UMSCHALT, VK_LWIN, VK_RWIN = 0x11, 0x12, 0x10, 0x5B, 0x5C

BEDIENTASTEN: dict[str, tuple[str, tuple[int, ...]]] = {
    "strg": ("Strg", (VK_STRG,)),
    "strg+alt": ("Strg+Alt", (VK_STRG, VK_ALT)),
    "alt": ("Alt", (VK_ALT,)),
    "strg+umschalt": ("Strg+Umschalt", (VK_STRG, VK_UMSCHALT)),
    "alt+umschalt": ("Alt+Umschalt", (VK_ALT, VK_UMSCHALT)),
}
STANDARD_BEDIENTASTE = "strg+alt"


def taste_gehalten(vk: int) -> bool:
    if w.user32 is None:  # kein Windows (Tests, Linux): keine Taste ist gehalten
        return False
    return bool(w.user32.GetAsyncKeyState(vk) & 0x8000)


class Bedientaste:
    def __init__(self, name: str = STANDARD_BEDIENTASTE, gehalten: Callable[[int], bool] = taste_gehalten):
        self._gehalten = gehalten
        self.name = STANDARD_BEDIENTASTE
        self.setzen(name)

    def setzen(self, name: object) -> None:
        if isinstance(name, str) and name in BEDIENTASTEN:
            self.name = name

    def text(self) -> str:
        return BEDIENTASTEN[self.name][0]

    def gedrueckt(self) -> bool:
        return all(self._gehalten(vk) for vk in BEDIENTASTEN[self.name][1])


MODIFIKATOREN = ((w.MOD_CONTROL, "Strg"), (w.MOD_ALT, "Alt"), (w.MOD_SHIFT, "Umschalt"), (w.MOD_WIN, "Win"))
_NAMEN = {vk: f"F{vk - 0x6F}" for vk in range(0x70, 0x88)}
_NAMEN.update({vk: chr(vk) for vk in list(range(0x30, 0x3A)) + list(range(0x41, 0x5B))})
_NAMEN.update({0x20: "Leertaste", 0x0D: "Enter", 0x09: "Tab", 0x2D: "Einfg", 0x2E: "Entf", 0x24: "Pos1", 0x23: "Ende",
               0x21: "BildAuf", 0x22: "BildAb", 0x25: "Links", 0x26: "Hoch", 0x27: "Rechts", 0x28: "Runter"})
_VK_VON_NAME = {name: vk for vk, name in _NAMEN.items()}
_FUNKTIONSTASTEN = set(range(0x70, 0x88))


@dataclass(frozen=True)
class Kombination:
    modifikatoren: int
    vk: int

    def text(self) -> str:
        teile = [name for maske, name in MODIFIKATOREN if self.modifikatoren & maske]
        teile.append(_NAMEN.get(self.vk, f"0x{self.vk:02X}"))
        return "+".join(teile)

    def zulaessig(self) -> bool:
        """Ohne Modifikator nur Funktionstasten (F1 bis F24); Tasten, die es nicht zu benennen gibt, nie."""
        if self.vk not in _NAMEN:
            return False
        return self.modifikatoren != 0 or self.vk in _FUNKTIONSTASTEN

    @staticmethod
    def aus_text(text: object) -> "Kombination | None":
        if not isinstance(text, str) or not text.strip():
            return None
        mods, vk = 0, None
        teile = [t.strip() for t in text.split("+") if t.strip()]
        if not teile:
            return None
        namen = {name: maske for maske, name in MODIFIKATOREN}
        for teil in teile[:-1]:
            if teil not in namen:
                return None
            mods |= namen[teil]
        vk = _VK_VON_NAME.get(teile[-1])
        if vk is None:
            return None
        kombi = Kombination(mods, vk)
        return kombi if kombi.zulaessig() else None


def standard_kombination(index: int) -> Kombination | None:
    """F13 bis F24 für die ersten zwölf Agenten, danach keine."""
    return Kombination(0, 0x7C + index) if 0 <= index < 12 else None


_ZU_PRUEFEN = [vk for vk in range(0x08, 0xFF) if vk not in (0x10, 0x11, 0x12, 0x5B, 0x5C, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5)
               and not 0x01 <= vk <= 0x06]


def modifikatoren_jetzt(gehalten: Callable[[int], bool] = taste_gehalten) -> int:
    mods = 0
    if gehalten(VK_STRG):
        mods |= w.MOD_CONTROL
    if gehalten(VK_ALT):
        mods |= w.MOD_ALT
    if gehalten(VK_UMSCHALT):
        mods |= w.MOD_SHIFT
    if gehalten(VK_LWIN) or gehalten(VK_RWIN):
        mods |= w.MOD_WIN
    return mods


class Erfasser:
    """Wartet auf den nächsten Tastendruck (mit den gehaltenen Modifikatoren) und meldet die Kombination; Esc bricht ab."""

    def __init__(self, gehalten: Callable[[int], bool] = taste_gehalten, jetzt: Callable[[], float] = time.monotonic,
                 schlafen: Callable[[float], None] = time.sleep, takt_s: float = 0.02):
        self._gehalten, self._jetzt, self._schlafen, self._takt_s = gehalten, jetzt, schlafen, takt_s

    def erfassen(self, timeout_s: float = 8.0) -> Kombination | None:
        """Blockiert (in einem eigenen Thread aufrufen). None bei Esc oder Zeitablauf."""
        ende = self._jetzt() + timeout_s
        # Tasten, die schon beim Start gehalten werden (z. B. der Klick-Enter), zählen nicht
        bereits = {vk for vk in _ZU_PRUEFEN if self._gehalten(vk)}
        while self._jetzt() < ende:
            for vk in _ZU_PRUEFEN:
                if vk in bereits or not self._gehalten(vk):
                    continue
                if vk == w.VK_ESCAPE:
                    return None
                return Kombination(modifikatoren_jetzt(self._gehalten), vk)
            bereits = {vk for vk in bereits if self._gehalten(vk)}
            self._schlafen(self._takt_s)
        return None

    def im_hintergrund(self, fertig: Callable[[Kombination | None], None], timeout_s: float = 8.0) -> threading.Thread:
        faden = threading.Thread(target=lambda: fertig(self.erfassen(timeout_s)), name="tastenkombi-erfassen", daemon=True)
        faden.start()
        return faden
