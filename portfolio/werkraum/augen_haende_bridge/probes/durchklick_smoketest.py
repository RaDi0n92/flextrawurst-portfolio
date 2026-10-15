"""Wine-Probe des Durchklick-Modus: Chat, Regieleiste und Terminal lassen Klicks durch, bis Strg gehalten wird.

Geprüft mit echten Fenstern: `WindowFromPoint` in der Fenstermitte, echter Strg-Druck per keybd_event, der echte
`DurchklickVerwalter`. Ausgabe: eine JSON-Zeile. Unter Wine gelaufen heißt „PASS unter Wine“, nicht native Windows.
"""

from __future__ import annotations

import ctypes
import json
import sys
import time

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.durchklick import DurchklickVerwalter
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.regie_fenster import RegieFenster
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster

KEYEVENTF_KEYUP = 0x0002
_u = ctypes.WinDLL("user32", use_last_error=True)
_u.WindowFromPoint.argtypes = [w.POINT]
_u.WindowFromPoint.restype = w.wintypes.HWND
_u.GetWindowRect.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]
_u.GetWindowLongW.argtypes = [w.wintypes.HWND, ctypes.c_int]
_u.GetWindowLongW.restype = ctypes.c_long
_u.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_uint32, ctypes.c_size_t]
_u.keybd_event.restype = None


def treffer(hwnd) -> bool:
    r = w.RECT()
    _u.GetWindowRect(hwnd, ctypes.byref(r))
    return _u.WindowFromPoint(w.POINT((r.left + r.right) // 2, (r.top + r.bottom) // 2)) == hwnd


def main() -> int:
    anwendung = Anwendung()
    fenster = {
        "chat": ChatFenster(100, 100),
        "regie": RegieFenster(500, 100),
        "terminal": TerminalFenster(100, 400, zeilen=12, spalten=40, name="Simi", ort="Host", farbe_hex="#00E5FF"),
    }
    for f in fenster.values():
        f.zeige(aktivieren=False)
    anwendung.pumpen(200)
    v = DurchklickVerwalter()
    for name, f in fenster.items():
        v.registrieren(name, f, aktiv=True)
    anwendung.pumpen(50)
    ohne_strg = {n: treffer(f.hwnd) for n, f in fenster.items()}

    _u.keybd_event(w.VK_CONTROL, 0, 0, 0)  # echter Strg-Druck
    time.sleep(0.2)
    v.tick()
    anwendung.pumpen(50)
    mit_strg = {n: treffer(f.hwnd) for n, f in fenster.items()}
    _u.keybd_event(w.VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)
    v.tick()
    anwendung.pumpen(50)
    strg_wieder_los = {n: treffer(f.hwnd) for n, f in fenster.items()}

    v.setzen("chat", False)  # Chat einzeln auf „immer bedienbar“
    anwendung.pumpen(50)
    einzeln = {n: treffer(f.hwnd) for n, f in fenster.items()}
    exstil = {n: bool(_u.GetWindowLongW(f.hwnd, -20) & w.WS_EX_TRANSPARENT) for n, f in fenster.items()}
    for f in fenster.values():
        f.schliessen()
    anwendung.pumpen(50)
    print(json.dumps({
        "status": "ok",
        "ohne_strg_trifft_fenster": ohne_strg, "mit_strg_trifft_fenster": mit_strg,
        "strg_wieder_los_trifft_fenster": strg_wieder_los,
        "chat_einzeln_aus_trifft_fenster": einzeln, "exstil_transparent_am_ende": exstil,
    }, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
