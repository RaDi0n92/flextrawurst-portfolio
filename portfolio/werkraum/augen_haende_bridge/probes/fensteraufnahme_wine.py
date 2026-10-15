"""Wine-Probe der Windows-Fensteraufnahme (PrintWindow, G06.7): ein weißes und ein schwarzes Fenster, ein ungültiges Handle, ein minimiertes Fenster.
Ausgabe: eine JSON-Zeile."""

from __future__ import annotations

import ctypes
import json
from ctypes import wintypes

from augen_haende_bridge.koerper import fensteraufnahme as fa
from augen_haende_bridge.koerper import windows_fenster_bild as wfb

u = ctypes.WinDLL("user32", use_last_error=True)
u.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                              ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
u.CreateWindowExW.restype = ctypes.c_void_p
u.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
u.DestroyWindow.argtypes = [ctypes.c_void_p]

WS_POPUP, WS_VISIBLE, SS_WHITERECT, SS_BLACKRECT = 0x80000000, 0x10000000, 0x6, 0x4


def fenster(stil: int, b: int, h: int) -> int:
    return u.CreateWindowExW(0, "STATIC", "", WS_POPUP | WS_VISIBLE | stil, 40, 40, b, h, None, None, None, None)


def main() -> None:
    weiss, schwarz = fenster(SS_WHITERECT, 120, 80), fenster(SS_BLACKRECT, 90, 60)
    ergebnis: dict = {}
    for name, kennung in (("weiss", weiss), ("dunkel", schwarz)):  # SS_BLACKRECT malt unter Wine in der Rahmenfarbe des Themas: nur „dunkel“, nicht garantiert schwarz
        bild = wfb.fenster_bild(kennung)
        ergebnis[name] = None if bild is None else {"breite": bild[1], "hoehe": bild[2], "bytes": len(bild[0]), "leer": fa.ist_leer(*bild),
                                                    "alpha_ok": set(bild[0][3::4]) == {255}, "weiss_ok": set(bild[0][0:len(bild[0]):4]) == {255}}
    auf = fa.FensterAufnahme(wfb.fenster_bild)
    echt = auf.holen(weiss)
    ergebnis["entscheidung"] = {"echt": echt is not None and echt.aufnahme, "ohne_fenster": (auf.holen(0x7FFF1234) is None and auf.letzter_grund)}
    ergebnis["ungueltig"] = wfb.fenster_bild(0x7FFF1234)
    u.ShowWindow(weiss, 6)  # SW_MINIMIZE
    ergebnis["minimiert"] = wfb.fenster_bild(weiss)
    for k in (weiss, schwarz):
        u.DestroyWindow(k)
    print(json.dumps(ergebnis))


main()
