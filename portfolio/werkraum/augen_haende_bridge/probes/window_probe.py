"""G01-Probe: Kann ein reines Win32-Fenster (ctypes, ohne Tk) die Eigenschaften tragen, die der erste Körper braucht?

Vier kleine Fenster liegen sich gegenseitig im Weg:
  TARGET   normales Fenster, zählt Klicks und getippte Zeichen (das »Programm darunter«)
  LAYERED  oberstes Fenster, 34 % Deckkraft (= 66 % transparent), fängt Klicks ab
  THRU     oberstes Fenster mit WS_EX_TRANSPARENT: Klicks fallen zum Fenster darunter durch
  DIAMOND  oberstes Fenster mit Rautenform (Fensterregion): Klicks an den Ecken fallen durch
Esc schließt alles. Beim Ende steht ein Ergebnis als JSON-Zeile auf stdout.
Die Probe klickt nicht selbst; ein Treiber (xdotool unter Wine, ein Mensch unter Windows) tut das.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
from ctypes import wintypes

if os.name != "nt":
    print(json.dumps({"status": "unavailable", "reason": "not_windows"}))
    sys.exit(0)

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_EX_TOPMOST = 0x00000008
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000
WS_EX_NOACTIVATE = 0x08000000
GWL_EXSTYLE = -20
LWA_ALPHA = 0x2
WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_CLOSE = 0x0010
WM_KEYDOWN = 0x0100
WM_CHAR = 0x0102
WM_LBUTTONDOWN = 0x0201
WM_SETFOCUS = 0x0007
VK_ESCAPE = 0x1B
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON), ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", wintypes.HICON),
    ]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", wintypes.RECT),
                ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL), ("rgbReserved", ctypes.c_byte * 32)]


user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
user32.RegisterClassExW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.CreateWindowExW.restype = wintypes.HWND
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.BeginPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
user32.BeginPaint.restype = wintypes.HDC
user32.EndPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.HBRUSH]
user32.InvalidateRect.argtypes = [wintypes.HWND, ctypes.c_void_p, wintypes.BOOL]
user32.SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, ctypes.c_ubyte, wintypes.DWORD]
user32.SetLayeredWindowAttributes.restype = wintypes.BOOL
user32.GetLayeredWindowAttributes.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.COLORREF),
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(wintypes.DWORD)]
user32.GetLayeredWindowAttributes.restype = wintypes.BOOL
user32.SetWindowRgn.argtypes = [wintypes.HWND, wintypes.HRGN, wintypes.BOOL]
user32.GetWindowRgnBox.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRgnBox.restype = ctypes.c_int
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetFocus.argtypes = [wintypes.HWND]
gdi32.CreateSolidBrush.argtypes = [wintypes.COLORREF]
gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
gdi32.CreatePolygonRgn.argtypes = [ctypes.POINTER(wintypes.POINT), ctypes.c_int, ctypes.c_int]
gdi32.CreatePolygonRgn.restype = wintypes.HRGN
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.TextOutW.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.LPCWSTR, ctypes.c_int]
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE


def rgb(r: int, g: int, b: int) -> int:
    return r | (g << 8) | (b << 16)


STATE: dict[str, dict] = {}
NAMES: dict[int, str] = {}
KEYS_TYPED: list[str] = []


def refresh_title(name: str) -> None:
    info = STATE[name]
    user32.SetWindowTextW(info["hwnd"], f"PROBE-{name} clicks={info['clicks']}")
    user32.InvalidateRect(info["hwnd"], None, True)


def wndproc(hwnd, msg, wparam, lparam):
    name = NAMES.get(int(hwnd) if hwnd else 0)
    if msg == WM_PAINT and name:
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
        rect = wintypes.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rect))
        brush = gdi32.CreateSolidBrush(STATE[name]["color"])
        user32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
        gdi32.SetBkMode(hdc, 1)
        label = f"{name} clicks={STATE[name]['clicks']}"
        gdi32.TextOutW(hdc, 8, 8, label, len(label))
        user32.EndPaint(hwnd, ctypes.byref(ps))
        return 0
    if msg == WM_LBUTTONDOWN and name:
        STATE[name]["clicks"] += 1
        refresh_title(name)
        return 0
    if msg == WM_CHAR and name:
        KEYS_TYPED.append(chr(wparam))
        return 0
    if msg == WM_KEYDOWN and wparam == VK_ESCAPE:
        user32.PostQuitMessage(0)
        return 0
    if msg == WM_CLOSE:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


CALLBACK = WNDPROC(wndproc)


def make_window(name: str, x: int, y: int, w: int, h: int, style: int, ex_style: int, color: int) -> int:
    hwnd = user32.CreateWindowExW(ex_style, "BridgeProbe", f"PROBE-{name}", style, x, y, w, h,
                                  None, None, kernel32.GetModuleHandleW(None), None)
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())
    NAMES[int(hwnd)] = name
    STATE[name] = {"hwnd": hwnd, "clicks": 0, "color": color, "rect": (x, y, w, h)}
    return hwnd


def main() -> int:
    dpi_ok = bool(user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2))) \
        if hasattr(user32, "SetProcessDpiAwarenessContext") else False
    user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p] if hasattr(user32, "SetProcessDpiAwarenessContext") else None
    wc = WNDCLASSEXW()
    wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
    wc.lpfnWndProc = CALLBACK
    wc.hInstance = kernel32.GetModuleHandleW(None)
    wc.lpszClassName = "BridgeProbe"
    if not user32.RegisterClassExW(ctypes.byref(wc)):
        raise ctypes.WinError(ctypes.get_last_error())

    make_window("TARGET", 100, 100, 320, 240, WS_OVERLAPPEDWINDOW, 0, rgb(210, 225, 245))
    layered = make_window("LAYERED", 150, 130, 160, 100, WS_POPUP, WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_LAYERED, rgb(240, 200, 60))
    thru = make_window("THRU", 330, 150, 100, 100, WS_POPUP, WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_LAYERED | WS_EX_TRANSPARENT, rgb(120, 220, 160))
    diamond = make_window("DIAMOND", 240, 250, 100, 100, WS_POPUP, WS_EX_TOPMOST | WS_EX_TOOLWINDOW, rgb(230, 120, 190))

    alpha_set = bool(user32.SetLayeredWindowAttributes(layered, 0, 87, LWA_ALPHA))  # 34 % Deckkraft
    thru_alpha = bool(user32.SetLayeredWindowAttributes(thru, 0, 87, LWA_ALPHA))
    points = (wintypes.POINT * 4)(wintypes.POINT(50, 0), wintypes.POINT(99, 50), wintypes.POINT(50, 99), wintypes.POINT(0, 50))
    region = gdi32.CreatePolygonRgn(points, 4, 1)
    region_set = bool(user32.SetWindowRgn(diamond, region, True))

    # Getrennte Basisaufnahme: eigene Fenster aus der Bildschirmaufnahme nehmen (Windows 10, Version 2004+).
    affinity = {"available": hasattr(user32, "SetWindowDisplayAffinity")}
    if affinity["available"]:
        user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
        user32.SetWindowDisplayAffinity.restype = wintypes.BOOL
        user32.GetWindowDisplayAffinity.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowDisplayAffinity.restype = wintypes.BOOL
        affinity["set_exclude_from_capture"] = bool(user32.SetWindowDisplayAffinity(layered, 0x11))
        affinity["set_error"] = ctypes.get_last_error()
        got_aff = wintypes.DWORD(0xFFFF)
        affinity["readback_ok"] = bool(user32.GetWindowDisplayAffinity(layered, ctypes.byref(got_aff)))
        affinity["readback_value"] = int(got_aff.value)

    for name in ("TARGET", "LAYERED", "THRU", "DIAMOND"):
        user32.ShowWindow(STATE[name]["hwnd"], SW_SHOW)
        refresh_title(name)
    user32.SetForegroundWindow(STATE["TARGET"]["hwnd"])
    user32.SetFocus(STATE["TARGET"]["hwnd"])

    key = wintypes.COLORREF(0)
    got_alpha = ctypes.c_ubyte(0)
    flags = wintypes.DWORD(0)
    readback_ok = bool(user32.GetLayeredWindowAttributes(layered, ctypes.byref(key), ctypes.byref(got_alpha), ctypes.byref(flags)))
    box = wintypes.RECT()
    region_type = int(user32.GetWindowRgnBox(diamond, ctypes.byref(box)))
    rects = {}
    for n in STATE:
        r = wintypes.RECT()
        user32.GetWindowRect(STATE[n]["hwnd"], ctypes.byref(r))
        rects[n] = [r.left, r.top, r.right, r.bottom]
    # Welches Fenster bekäme einen Klick? WindowFromPoint ist die Windows-eigene Trefferlogik
    # (überspringt WS_EX_TRANSPARENT, beachtet Fensterregionen) und hängt nicht vom Anzeigesystem ab.
    user32.WindowFromPoint.argtypes = [wintypes.POINT]
    user32.WindowFromPoint.restype = wintypes.HWND
    by_hwnd = {int(STATE[n]["hwnd"]): n for n in STATE}
    hit_points = {
        "nur_target": (400, 320), "in_layered": (200, 180), "in_thru": (380, 200),
        "diamant_ecke": (245, 255), "diamant_mitte": (290, 300), "ausserhalb_alles": (700, 600),
    }
    hits = {}
    for label, (px, py) in hit_points.items():
        found = user32.WindowFromPoint(wintypes.POINT(px, py))
        hits[label] = by_hwnd.get(int(found) if found else 0, "anderes/keins")
    setup = {
        "display_affinity": affinity,
        "hit_tests": hits,
        "rects": rects,
        "dpi_awareness_v2": dpi_ok,
        "layered_alpha_set": alpha_set, "layered_alpha_readback": int(got_alpha.value) if readback_ok else None,
        "layered_flags_readback": int(flags.value) if readback_ok else None,
        "thru_alpha_set": thru_alpha,
        "diamond_region_set": region_set, "diamond_region_type": region_type,
        "diamond_region_box": [box.left, box.top, box.right, box.bottom],
        "exstyle": {n: hex(user32.GetWindowLongW(STATE[n]["hwnd"], GWL_EXSTYLE) & 0xFFFFFFFF) for n in STATE},
    }
    print(json.dumps({"event": "ready", **setup}, ensure_ascii=False), flush=True)

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    print(json.dumps({
        "event": "done",
        "clicks": {n: STATE[n]["clicks"] for n in STATE},
        "keys_typed": "".join(KEYS_TYPED),
        **setup,
    }, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
