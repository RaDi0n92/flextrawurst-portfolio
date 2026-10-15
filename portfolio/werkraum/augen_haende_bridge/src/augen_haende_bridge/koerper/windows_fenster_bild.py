"""Windows: das Bild eines Fensters über PrintWindow mit PW_RENDERFULLCONTENT (G06.7, R123).

PrintWindow lässt das Fenster sich selbst in einen Speicher zeichnen, auch wenn ein anderes davorliegt; PW_RENDERFULLCONTENT (Windows 8.1 und neuer) bezieht Fenster mit
DirectComposition (Chromium, UWP) ein. Das Ergebnis ist **nicht immer richtig**: manche Spiele und hardwarebeschleunigte Fenster liefern Schwarz oder nichts. Darum liefert diese
Funktion nur das Bild; ob es leer ist, entscheidet `fensteraufnahme.ist_leer`, und der Bilderstrom fällt dann sichtbar auf den Bildschirmausschnitt zurück.

Minimierte Fenster werden nicht aufgenommen (ihr Inhalt ist nicht aktuell), geschlossene auch nicht: None.
"""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes

PW_RENDERFULLCONTENT = 0x2
BI_RGB, DIB_RGB_COLORS = 0, 0
MAX_PIXEL = 16_000_000


class _Kopf(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32), ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16),
                ("biCompression", ctypes.c_uint32), ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]


class _Info(ctypes.Structure):
    _fields_ = [("kopf", _Kopf), ("farben", ctypes.c_uint32 * 3)]


_dll: tuple | None = None


def _bindungen():
    global _dll
    if _dll is None:
        u = ctypes.WinDLL("user32", use_last_error=True)
        g = ctypes.WinDLL("gdi32", use_last_error=True)
        h = ctypes.c_void_p
        u.IsWindow.argtypes, u.IsWindow.restype = [h], ctypes.c_int
        u.IsIconic.argtypes, u.IsIconic.restype = [h], ctypes.c_int
        u.GetWindowRect.argtypes, u.GetWindowRect.restype = [h, ctypes.POINTER(wintypes.RECT)], ctypes.c_int
        u.GetDC.argtypes, u.GetDC.restype = [h], h
        u.ReleaseDC.argtypes, u.ReleaseDC.restype = [h, h], ctypes.c_int
        u.PrintWindow.argtypes, u.PrintWindow.restype = [h, h, ctypes.c_uint], ctypes.c_int
        g.CreateCompatibleDC.argtypes, g.CreateCompatibleDC.restype = [h], h
        g.CreateCompatibleBitmap.argtypes, g.CreateCompatibleBitmap.restype = [h, ctypes.c_int, ctypes.c_int], h
        g.SelectObject.argtypes, g.SelectObject.restype = [h, h], h
        g.GetDIBits.argtypes, g.GetDIBits.restype = [h, h, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.POINTER(_Info), ctypes.c_uint], ctypes.c_int
        g.DeleteObject.argtypes, g.DeleteObject.restype = [h], ctypes.c_int
        g.DeleteDC.argtypes, g.DeleteDC.restype = [h], ctypes.c_int
        _dll = (u, g)
    return _dll


def fenster_bild(hwnd: int) -> tuple[bytes, int, int] | None:
    """(BGRA, Breite, Höhe) des ganzen Fensters oder None (nicht da, minimiert, zu groß, PrintWindow lehnt ab)."""
    if os.name != "nt":
        return None
    u, g = _bindungen()
    kennung = ctypes.c_void_p(int(hwnd))
    if not u.IsWindow(kennung) or u.IsIconic(kennung):
        return None
    rect = wintypes.RECT()
    if not u.GetWindowRect(kennung, ctypes.byref(rect)):
        return None
    breite, hoehe = rect.right - rect.left, rect.bottom - rect.top
    if breite <= 0 or hoehe <= 0 or breite * hoehe > MAX_PIXEL:
        return None
    bildschirm = u.GetDC(ctypes.c_void_p())
    speicher = bitmap = alt = None
    try:
        speicher = g.CreateCompatibleDC(bildschirm)
        bitmap = g.CreateCompatibleBitmap(bildschirm, breite, hoehe)
        if not speicher or not bitmap:
            return None
        alt = g.SelectObject(speicher, bitmap)
        if not u.PrintWindow(kennung, speicher, PW_RENDERFULLCONTENT):
            return None
        info = _Info()
        info.kopf.biSize = ctypes.sizeof(_Kopf)
        info.kopf.biWidth, info.kopf.biHeight = breite, -hoehe  # von oben nach unten
        info.kopf.biPlanes, info.kopf.biBitCount, info.kopf.biCompression = 1, 32, BI_RGB
        puffer = (ctypes.c_ubyte * (breite * hoehe * 4))()
        if g.GetDIBits(speicher, bitmap, 0, hoehe, ctypes.cast(puffer, ctypes.c_void_p), ctypes.byref(info), DIB_RGB_COLORS) != hoehe:
            return None
        roh = bytearray(puffer)
        roh[3::4] = b"\xff" * (breite * hoehe)  # GDI lässt Alpha bei 0 (undefiniert): ein PrintWindow-Bild ist undurchsichtig, sonst hielte `ist_leer` es für durchsichtig
        return bytes(roh), breite, hoehe
    finally:
        if speicher and alt:
            g.SelectObject(speicher, alt)
        if bitmap:
            g.DeleteObject(bitmap)
        if speicher:
            g.DeleteDC(speicher)
        u.ReleaseDC(ctypes.c_void_p(), bildschirm)
