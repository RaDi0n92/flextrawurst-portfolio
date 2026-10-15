"""Wine-Probe der Windows-Hände (SendInput): ein echtes Win32-Fenster zählt Klicks, Zeigerbewegungen, Tasten, Zeichen und Rad; die Engine mit dem WindowsBackend bedient es.
Dazu der Beobachter für Daniels eigene Eingabe (Hooks mit dem Injected-Merkmal). Ausgabe: eine JSON-Zeile."""

from __future__ import annotations

import ctypes
import json
import sys
import threading
import time
from ctypes import wintypes

from augen_haende_bridge.koerper.eingabe_adapter import Aktion, Bildbezug, HaendeEngine, WindowsBackend, ZielStand

u = ctypes.WinDLL("user32", use_last_error=True)
k = ctypes.WinDLL("kernel32", use_last_error=True)
LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class WNDCLASSW(ctypes.Structure):
    _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HANDLE), ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HANDLE), ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]


u.DefWindowProcW.argtypes, u.DefWindowProcW.restype = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM], LRESULT
u.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
u.CreateWindowExW.restype = wintypes.HWND
u.RegisterClassW.argtypes, u.RegisterClassW.restype = [ctypes.POINTER(WNDCLASSW)], wintypes.ATOM
u.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
u.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
u.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
u.IsWindow.argtypes = [wintypes.HWND]

stand = {"klick_runter": 0, "klick_hoch": 0, "bewegt": 0, "tasten": [], "zeichen": "", "rad": 0, "gedrueckt": False, "ziehen_ende": None}
WM = {0x0200: "move", 0x0201: "ldown", 0x0202: "lup", 0x0100: "keydown", 0x0102: "char", 0x020A: "wheel", 0x0101: "keyup"}


@WNDPROC
def proc(hwnd, msg, wp, lp):
    if msg == 0x0201:
        stand["klick_runter"] += 1
        stand["gedrueckt"] = True
    elif msg == 0x0202:
        stand["klick_hoch"] += 1
        stand["gedrueckt"] = False
        stand["ziehen_ende"] = [lp & 0xFFFF, (lp >> 16) & 0xFFFF]
    elif msg == 0x0200 and stand["gedrueckt"]:
        stand["bewegt"] += 1
    elif msg == 0x0100:
        stand["tasten"].append(int(wp))
    elif msg == 0x0102:
        stand["zeichen"] += chr(wp)
    elif msg == 0x020A:
        stand["rad"] += 1
    return u.DefWindowProcW(hwnd, msg, wp, lp)


def hauptfenster() -> int:
    klasse = WNDCLASSW()
    klasse.lpfnWndProc, klasse.lpszClassName = proc, "HaendeProbe"
    klasse.hbrBackground = ctypes.c_void_p(6)  # COLOR_WINDOW + 1
    u.RegisterClassW(ctypes.byref(klasse))
    h = u.CreateWindowExW(0x8, "HaendeProbe", "Haendeprobe", 0x80000000 | 0x10000000, 60, 60, 400, 300, None, None, None, None)  # TOPMOST popup
    return int(h)


def pumpe(sekunden: float) -> None:
    ende = time.monotonic() + sekunden
    msg = wintypes.MSG()
    while time.monotonic() < ende:
        while u.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            u.TranslateMessage(ctypes.byref(msg))
            u.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.005)


def rect(h):
    r = wintypes.RECT()
    return (r.left, r.top, r.right, r.bottom) if u.GetWindowRect(wintypes.HWND(h), ctypes.byref(r)) else None


def main() -> None:
    h = hauptfenster()
    pumpe(0.5)
    ziel = f"windows:window:{h}"
    engine = HaendeEngine(WindowsBackend(), ziel_stand=lambda z: ZielStand(bool(u.IsWindow(wintypes.HWND(h))), rect(h), False, h, 1.0), ziel_kennung=lambda z: h)
    ergebnis: dict = {}

    def tue(name, aktion, mit_bild=True):
        r = rect(h)
        bezug = Bildbezug(ziel, 1, int(time.time() * 1000), r[2] - r[0], r[3] - r[1], r, h, 1.0) if mit_bild else None
        res = {}
        faden = threading.Thread(target=lambda: res.update(r=engine.ausfuehren(name, aktion, ziel=ziel, bezug=bezug, lease_grund="", haende_erlaubt=True)))
        faden.start()
        while faden.is_alive():
            pumpe(0.02)  # das Fenster braucht seine Nachrichtenschleife
        pumpe(0.2)
        ergebnis[name] = {"status": res["r"].status, "grund": res["r"].grund, "delivered": res["r"].delivered, "observed": res["r"].observed}

    tue("klick", Aktion("klick", punkt=(100, 100)))
    tue("tippen", Aktion("tippen", text="Hallo äö"), mit_bild=False)
    tue("taste", Aktion("taste", kombi="Strg+A"), mit_bild=False)
    tue("rad", Aktion("rad", punkt=(100, 100), dy=2))
    tue("ziehen", Aktion("ziehen", punkt=(20, 20), bis=(300, 200), dauer_ms=400))
    be = WindowsBackend()
    ergebnis["fokus"] = {"ergebnis": bool(be.fokus_geben(h)), "vorn_ist_ziel": be.tastatur_fokus() == h}
    ergebnis["fenster"] = {"klick_runter": stand["klick_runter"], "klick_hoch": stand["klick_hoch"], "bewegt": stand["bewegt"], "zeichen": stand["zeichen"], "tasten": stand["tasten"],
                           "rad": stand["rad"], "gedrueckt": stand["gedrueckt"], "ziehen_ende": stand["ziehen_ende"]}
    ergebnis["rect"] = list(rect(h))
    print(json.dumps(ergebnis))
    sys.stdout.flush()


main()
