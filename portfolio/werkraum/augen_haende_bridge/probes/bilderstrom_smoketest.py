"""Wine-Probe des Bilderstroms mit echter Bildschirmaufnahme: sind Raute und Ticker (Layered Windows) im Bild, folgt der Ausschnitt
einem fremden Fenster (notepad), werden unveränderte Bilder übersprungen? Ausgabe: eine JSON-Zeile."""

from __future__ import annotations

import base64
import ctypes
import io
import json
import subprocess
import sys
import time

from PIL import Image

from augen_haende_bridge import windows_capture
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.bilderstrom import Bilderstrom
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.nachricht_fenster import TickerFenster
from augen_haende_bridge.koerper.raute_fenster import RauteFenster
from augen_haende_bridge.windows_capture import Win32CaptureApi

_u = ctypes.WinDLL("user32", use_last_error=True)
_u.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
_u.FindWindowW.restype = w.wintypes.HWND
_u.GetWindowRect.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]


def pixel(roh: bytes, breite: int, x: int, y: int) -> tuple[int, int, int]:
    i = (y * breite + x) * 4
    return roh[i + 2], roh[i + 1], roh[i]  # RGB aus BGRA


def nah(a, b, toleranz=40) -> bool:
    return all(abs(x - y) <= toleranz for x, y in zip(a, b))


def main() -> int:
    anwendung = Anwendung()
    api = Win32CaptureApi()
    virtuell = api.virtual_screen_rect()
    ergebnis: dict = {"bildschirm": list(virtuell)}

    raute = RauteFenster(200, 200, name="Simi", farbe_hex="#00E5FF", hotkey="F13")
    raute.zeige(aktivieren=False)
    ticker = TickerFenster(text="Daniel: Go!", farbe_hex="#F2F2F2", raute_rechteck=raute.rechteck(), geschlossen=lambda: None)
    ticker.zeige(aktivieren=False)
    anwendung.pumpen(300)
    l, o, r, u = raute.rechteck()
    mitte_x, mitte_y = l + 12, (o + u) // 2  # links in der Raute, dort steht kein Text
    cyan = (0, 229, 255)

    def aufnahme_farbe(mit_flag: bool) -> tuple[int, int, int]:
        alt = windows_capture.CAPTUREBLT
        windows_capture.CAPTUREBLT = alt if mit_flag else 0
        try:
            roh = api.capture_bgra(virtuell)
        finally:
            windows_capture.CAPTUREBLT = alt
        return pixel(roh, virtuell[2] - virtuell[0], mitte_x - virtuell[0], mitte_y - virtuell[1])

    mit, ohne = aufnahme_farbe(True), aufnahme_farbe(False)
    ergebnis["raute_im_bild"] = {"mit_captureblt": list(mit), "ohne_captureblt": list(ohne),
                                 "mit_ist_raute": nah(mit, cyan), "ohne_ist_raute": nah(ohne, cyan)}

    gesendet: list = []

    def erfassen():
        return api.capture_bgra(virtuell), virtuell[2] - virtuell[0], virtuell[3] - virtuell[1]

    strom = Bilderstrom(erfassen=erfassen, bildschirm=lambda: virtuell, senden=lambda tid, p: gesendet.append((tid, p)) or True,
                        fenster_rect=lambda hwnd: (lambda rc: (rc.left, rc.top, rc.right, rc.bottom) if _u.GetWindowRect(hwnd, ctypes.byref(rc)) else None)(w.RECT()),
                        takt_s=0.2, keepalive_s=60.0)
    strom.binden("t-1", None)
    n1 = strom.tick()
    bild = Image.open(io.BytesIO(base64.b64decode(gesendet[0][1]["data"]))).convert("RGB")
    jpeg_pixel = bild.getpixel((mitte_x - virtuell[0], mitte_y - virtuell[1]))
    ergebnis["desktop_strom"] = {"gesendet": n1, "groesse": [gesendet[0][1]["width"], gesendet[0][1]["height"]],
                                 "raute_im_jpeg": nah(jpeg_pixel, cyan, 60), "jpeg_pixel": list(jpeg_pixel)}
    n2 = strom.tick()
    ergebnis["unveraendert_uebersprungen"] = n2 == 0

    notepad = subprocess.Popen(["notepad.exe"])
    time.sleep(2.0)
    anwendung.pumpen(100)
    hwnd = _u.FindWindowW("Notepad", None)
    if hwnd:
        rc = w.RECT()
        _u.GetWindowRect(hwnd, ctypes.byref(rc))
        strom.binden("t-2", int(hwnd))
        vor = len(gesendet)
        strom.tick()
        neu = [p for t, p in gesendet[vor:] if t == "t-2"]
        ergebnis["fenster_strom"] = {"notepad_rect": [rc.left, rc.top, rc.right, rc.bottom],
                                     "bild": [neu[0]["width"], neu[0]["height"]] if neu else None,
                                     "passt": bool(neu) and [neu[0]["width"], neu[0]["height"]] == [rc.right - rc.left, rc.bottom - rc.top]}
        notepad.kill()
        time.sleep(1.0)
        anwendung.pumpen(100)
        ergebnis["fenster_weg_beendet_den_strom"] = strom.tick() >= 0 and not strom.an("t-2")
    else:
        ergebnis["fenster_strom"] = "notepad nicht gefunden"
        notepad.kill()
    ticker.schliessen()
    raute.schliessen()
    anwendung.pumpen(50)
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
