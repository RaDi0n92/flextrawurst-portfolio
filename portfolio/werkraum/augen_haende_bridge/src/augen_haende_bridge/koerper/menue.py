"""Aufklappmenüs (Scanner-Auswahl, Startliste, Regie) als native Popup-Menüs und die Zwischenablage."""

from __future__ import annotations

import ctypes
from collections.abc import Sequence

from . import win32 as w

Eintrag = tuple[int, str, int] | None  # (Befehls-Id, Text, Flags) oder None für eine Trennlinie
ABGEBLENDET = w.MF_GRAYED
GEHAKT = w.MF_CHECKED


def zeige_menue(hwnd: int, eintraege: Sequence[Eintrag], x: int, y: int, *, nach_oben: bool = False, rechtsbuendig: bool = False) -> int:
    """Blockiert, bis gewählt oder abgebrochen wurde. Liefert die Befehls-Id oder 0."""
    w.require_windows()
    menue = w.user32.CreatePopupMenu()
    try:
        for eintrag in eintraege:
            if eintrag is None:
                w.user32.AppendMenuW(menue, w.MF_SEPARATOR, 0, None)
                continue
            befehl, text, flags = eintrag
            w.user32.AppendMenuW(menue, w.MF_STRING | flags, befehl, text)
        w.user32.SetForegroundWindow(hwnd)
        ausrichtung = (w.TPM_BOTTOMALIGN if nach_oben else 0) | (w.TPM_RIGHTALIGN if rechtsbuendig else w.TPM_LEFTALIGN)
        return int(w.user32.TrackPopupMenuEx(menue, w.TPM_RETURNCMD | w.TPM_NONOTIFY | ausrichtung, x, y, hwnd, None))
    finally:
        w.user32.DestroyMenu(menue)


def text_aus_zwischenablage(hwnd: int) -> str:
    w.require_windows()
    if not w.user32.OpenClipboard(hwnd):
        return ""
    try:
        handle = w.user32.GetClipboardData(w.CF_UNICODETEXT)
        if not handle:
            return ""
        zeiger = w.kernel32.GlobalLock(handle)
        if not zeiger:
            return ""
        try:
            return ctypes.wstring_at(zeiger)
        finally:
            w.kernel32.GlobalUnlock(handle)
    finally:
        w.user32.CloseClipboard()


def text_in_zwischenablage(hwnd: int, text: str) -> bool:
    w.require_windows()
    daten = (text + "\0").encode("utf-16-le")
    speicher = w.kernel32.GlobalAlloc(w.GMEM_MOVEABLE, len(daten))
    if not speicher:
        return False
    zeiger = w.kernel32.GlobalLock(speicher)
    ctypes.memmove(zeiger, daten, len(daten))
    w.kernel32.GlobalUnlock(speicher)
    if not w.user32.OpenClipboard(hwnd):
        return False
    try:
        w.user32.EmptyClipboard()
        return bool(w.user32.SetClipboardData(w.CF_UNICODETEXT, speicher))  # das System besitzt den Speicher ab jetzt
    finally:
        w.user32.CloseClipboard()


def _linux_einhaengen() -> None:
    from .plattform import ist_linux

    if ist_linux():
        from . import menue_linux as ml

        g = globals()
        for name in ("zeige_menue", "text_aus_zwischenablage", "text_in_zwischenablage"):
            g[name] = getattr(ml, name)


_linux_einhaengen()
