"""Wine-Probe: erkennen die Hooks Daniels Eingabe (nicht injiziert) und unterscheiden sie von den Händen (injiziert, SendInput)? Phase 1: die Engine klickt und tippt, es darf nichts „physisch“ sein.
Phase 2: von außen kommen echte X-Eingaben (für Wine ist das Hardware); jetzt muss „physisch“ gezählt werden und die Hände stoppen. Ausgabe: Zeilen `PHASE1 {...}` und `ENDE {...}`."""

from __future__ import annotations

import ctypes
import json
import sys
import threading
import time
from ctypes import wintypes

sys.argv = sys.argv[:1]

from augen_haende_bridge.koerper import eingabe_adapter as ea  # noqa: E402
from augen_haende_bridge.koerper.uebernahme import Uebernahme, WindowsHooks  # noqa: E402

u = ctypes.WinDLL("user32", use_last_error=True)
u.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
u.CreateWindowExW.restype = wintypes.HWND
u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
u.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]


def pumpe(s):
    ende, msg = time.monotonic() + s, wintypes.MSG()
    while time.monotonic() < ende:
        while u.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            u.TranslateMessage(ctypes.byref(msg))
            u.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.005)


def rect(h):
    r = wintypes.RECT()
    u.GetWindowRect(wintypes.HWND(h), ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def main():
    h = int(u.CreateWindowExW(0x8, "STATIC", "Uebernahme", 0x80000000 | 0x10000000, 60, 60, 400, 300, None, None, None, None))
    pumpe(0.3)
    ziel = f"windows:window:{h}"
    engine = ea.HaendeEngine(ea.WindowsBackend(), ziel_stand=lambda z: ea.ZielStand(True, rect(h), False, h, 1.0), ziel_kennung=lambda z: h)
    ueb = Uebernahme(engine, pause_s=1.0)
    hooks = WindowsHooks(ueb)
    ok = hooks.start()
    pumpe(0.3)

    def tue(aktion, mit_bild=True):
        r = rect(h)
        bezug = ea.Bildbezug(ziel, 1, int(time.time() * 1000), r[2] - r[0], r[3] - r[1], r, h, 1.0) if mit_bild else None
        res = {}
        t = threading.Thread(target=lambda: res.update(r=engine.ausfuehren("a", aktion, ziel=ziel, bezug=bezug, lease_grund="", haende_erlaubt=True)))
        t.start()
        while t.is_alive():
            pumpe(0.02)
        pumpe(0.2)
        return res["r"]

    r1 = tue(ea.Aktion("klick", punkt=(50, 50)))
    r2 = tue(ea.Aktion("ziehen", punkt=(10, 10), bis=(200, 150), dauer_ms=300))
    print("PHASE1 " + json.dumps({"hooks": ok, "klick": r1.status, "ziehen": r2.status, "gesehen": dict(hooks.gesehen), "erkannt": ueb.erkannt}), flush=True)
    ende = time.monotonic() + 20
    while time.monotonic() < ende and ueb.erkannt == 0:
        pumpe(0.05)
    r3 = tue(ea.Aktion("klick", punkt=(50, 50)))
    time.sleep(1.2)
    ueb.tick()
    r4 = tue(ea.Aktion("klick", punkt=(50, 50)))
    r5 = None
    if r4.status != "ausgefuehrt":  # unter Wine löst die erste Bewegung nach fremder Eingabe ein Echo aus (Zeigersprung wird als Eingabe zurückgemeldet): nach der Pause ein zweiter Versuch
        time.sleep(1.2)
        ueb.tick()
        r5 = tue(ea.Aktion("klick", punkt=(50, 50)))
    print("ENDE " + json.dumps({"erkannt": ueb.erkannt, "gesehen": dict(hooks.gesehen), "waehrend_pause": [r3.status, r3.grund], "nach_pause": r4.status, "nach_pause_grund": r4.grund, "daniel": engine.daniel_uebernimmt, "zweiter_versuch": None if r5 is None else r5.status}), flush=True)


main()
