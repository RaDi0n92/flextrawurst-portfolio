"""Wine-Probe der Regie- und Medienleiste: echtes Fenster, echte Trefferprüfung, Klick-Logik über echte Nachrichten.

Ausgabe: eine JSON-Zeile. Unter Wine gelaufen heißt „PASS unter Wine“, nicht native Windows.
"""

from __future__ import annotations

import ctypes
import json
import sys

from augen_haende_bridge.koerper import regie_fenster as r
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.fenster import Anwendung

_u = ctypes.WinDLL("user32", use_last_error=True)
_u.WindowFromPoint.argtypes = [w.POINT]
_u.WindowFromPoint.restype = w.wintypes.HWND
_u.GetLayeredWindowAttributes.argtypes = [w.wintypes.HWND, ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_uint32)]
_u.GetWindowLongW.argtypes = [w.wintypes.HWND, ctypes.c_int]
_u.GetWindowLongW.restype = ctypes.c_long
_u.GetWindowRect.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]
_u.SendMessageW.argtypes = [w.wintypes.HWND, ctypes.c_uint, w.wintypes.WPARAM, w.wintypes.LPARAM]
_u.SendMessageW.restype = w.wintypes.LPARAM


def _mitte(name: str) -> tuple[int, int]:
    links, oben, rechts, unten = r.knopf_rechtecke()[name]
    return (links + rechts) // 2, (oben + unten) // 2


def main() -> int:
    anwendung = Anwendung()
    aufrufe: list = []
    fenster = r.RegieFenster(*r.leiste_position((0, 0, 1280, 800)),
                             agent_wechseln=lambda: aufrufe.append("agent"),
                             mikrofon_umschalten=lambda: aufrufe.append("mikrofon"),
                             kamera_umschalten=lambda: aufrufe.append("kamera"),
                             regie_menue=lambda x, y: aufrufe.append("regie"),
                             notaus_umschalten=lambda: aufrufe.append("notaus"))
    fenster.zeige(aktivieren=False)
    anwendung.pumpen(100)
    rect = w.RECT()
    _u.GetWindowRect(fenster.hwnd, ctypes.byref(rect))
    exstil = _u.GetWindowLongW(fenster.hwnd, -20)
    alpha = ctypes.c_ubyte()
    _u.GetLayeredWindowAttributes(fenster.hwnd, None, ctypes.byref(alpha), None)

    alpha_start = alpha.value
    griff = _u.SendMessageW(fenster.hwnd, 0x0084, 0, ((rect.top + 3) << 16) | ((rect.left + 30) & 0xFFFF))
    unten = _u.SendMessageW(fenster.hwnd, 0x0084, 0, ((rect.top + r.GRIFF_H + 10) << 16) | ((rect.left + 30) & 0xFFFF))
    treffer, klicks = {}, {}
    for name in r.knopf_rechtecke():
        mx, my = _mitte(name)
        treffer[name] = _u.WindowFromPoint(w.POINT(rect.left + mx, rect.top + my)) == fenster.hwnd
        vor = len(aufrufe)
        _u.SendMessageW(fenster.hwnd, 0x0201, 1, (my << 16) | mx)  # WM_LBUTTONDOWN
        _u.SendMessageW(fenster.hwnd, 0x0202, 0, (my << 16) | mx)  # WM_LBUTTONUP
        anwendung.pumpen(30)
        klicks[name] = aufrufe[vor:]

    vor = len(aufrufe)  # runterdrücken auf Kamera, loslassen auf Mikrofon: darf nichts auslösen
    kx, ky = _mitte("kamera")
    mx, my = _mitte("mikrofon")
    _u.SendMessageW(fenster.hwnd, 0x0201, 1, (ky << 16) | kx)
    _u.SendMessageW(fenster.hwnd, 0x0202, 0, (my << 16) | mx)
    anwendung.pumpen(30)
    weggezogen = aufrufe[vor:]

    alpha_ende = ctypes.c_ubyte()
    _u.GetLayeredWindowAttributes(fenster.hwnd, None, ctypes.byref(alpha_ende), None)
    fenster.setze(agent_name="Nova", mikrofon="ein", kamera="fehler", notaus=True)
    anwendung.pumpen(50)
    zustand = [fenster.agent_name, fenster.zustand_von("mikrofon"), fenster.zustand_von("kamera"), fenster.notaus]
    fenster.schliessen()
    anwendung.pumpen(50)
    print(json.dumps({
        "status": "ok", "rechteck": [rect.left, rect.top, rect.right, rect.bottom],
        "groesse_stimmt": (rect.right - rect.left, rect.bottom - rect.top) == (r.BREITE, r.HOEHE),
        "topmost": bool(exstil & w.WS_EX_TOPMOST), "toolwindow": bool(exstil & w.WS_EX_TOOLWINDOW),
        "klickdurchlaessig": bool(exstil & w.WS_EX_TRANSPARENT), "deckkraft": alpha.value,
        "trifft_jeden_knopf": treffer, "klicks": klicks, "weggezogen_loest_nichts_aus": weggezogen == [],
        "zustand_nach_setze": zustand,
        "griff_verschiebt": int(griff) == w.HTCAPTION, "unterhalb_ist_client": int(unten) == w.HTCLIENT,
        "deckkraft_start_ende": [alpha_start, alpha_ende.value],
    }, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
