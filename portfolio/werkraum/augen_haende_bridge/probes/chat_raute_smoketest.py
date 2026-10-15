"""Wine-Probe für den gemeinsamen Chat und die Raute-Einstellungen: echte Fenster, echte Trefferprüfung.

Ausgabe: eine JSON-Zeile. Unter Wine gelaufen heißt „PASS unter Wine“, nicht native Windows.
"""

from __future__ import annotations

import ctypes
import json
import sys

from augen_haende_bridge.koerper import chat_fenster as c
from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.raute_fenster import GROESSE, RauteFenster

_u = ctypes.WinDLL("user32", use_last_error=True)
_u.GetWindowRect.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]
_u.GetLayeredWindowAttributes.argtypes = [w.wintypes.HWND, ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_uint32)]
_u.SendMessageW.argtypes = [w.wintypes.HWND, ctypes.c_uint, w.wintypes.WPARAM, w.wintypes.LPARAM]
_u.SendMessageW.restype = w.wintypes.LPARAM
_u.GetWindowRgnBox.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]


def rect_von(hwnd) -> list[int]:
    r = w.RECT()
    _u.GetWindowRect(hwnd, ctypes.byref(r))
    return [r.left, r.top, r.right, r.bottom]


def alpha_von(hwnd) -> int:
    a = ctypes.c_ubyte()
    _u.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(a), None)
    return a.value


def nchittest(hwnd, x: int, y: int) -> int:
    return int(_u.SendMessageW(hwnd, 0x0084, 0, ((y & 0xFFFF) << 16) | (x & 0xFFFF)))


def main() -> int:
    anwendung = Anwendung()
    ergebnis: dict = {}

    empfangen, gewechselt = [], []
    chat = c.ChatFenster(200, 300, gesendet=empfangen.append, empfaenger_wechseln=lambda: gewechselt.append(1))
    chat.zeige(aktivieren=False)
    anwendung.pumpen(100)
    l, o, r, u = rect_von(chat.hwnd)
    breite = r - l
    knoepfe = c.kopf_rechtecke(breite)

    def mitte(rechteck):
        return (rechteck[0] + rechteck[2]) // 2, (rechteck[1] + rechteck[3]) // 2

    ergebnis["chat"] = {
        "rechteck": [l, o, r, u], "topmost": bool(_u.GetWindowLongW(chat.hwnd, -20) & w.WS_EX_TOPMOST)
        if hasattr(_u, "GetWindowLongW") else None,
        "kopf_ist_verschieben": nchittest(chat.hwnd, l + 20, o + 10) == w.HTCAPTION,
        "linke_kante": nchittest(chat.hwnd, l, o + 100) == w.HTLEFT,
        "ecke_unten_rechts": nchittest(chat.hwnd, r - 1, u - 1) == w.HTBOTTOMRIGHT,
        "knopf_deckkraft_ist_client": nchittest(chat.hwnd, l + mitte(knoepfe["deckkraft"])[0], o + 12) == w.HTCLIENT,
        "inneres_ist_client": nchittest(chat.hwnd, l + 100, o + 100) == w.HTCLIENT,
    }
    vor = alpha_von(chat.hwnd)
    x, y = mitte(knoepfe["deckkraft"])
    _u.SendMessageW(chat.hwnd, 0x0201, 1, (y << 16) | x)
    _u.SendMessageW(chat.hwnd, 0x0202, 0, (y << 16) | x)
    anwendung.pumpen(30)
    ergebnis["chat"]["deckkraft_vorher_nachher"] = [vor, alpha_von(chat.hwnd)]
    x, y = mitte(knoepfe["empfaenger"])
    _u.SendMessageW(chat.hwnd, 0x0201, 1, (y << 16) | x)
    _u.SendMessageW(chat.hwnd, 0x0202, 0, (y << 16) | x)
    anwendung.pumpen(30)
    ergebnis["chat"]["empfaenger_klick_wechselt"] = len(gewechselt) == 1
    for zeichen in "Go!":
        _u.SendMessageW(chat.hwnd, 0x0102, ord(zeichen), 0)  # WM_CHAR
    _u.SendMessageW(chat.hwnd, 0x0102, 0x0D, 0)
    anwendung.pumpen(30)
    ergebnis["chat"]["enter_gibt_text_an_besitzer"] = empfangen == ["Go!"]
    chat.empfaenger_setzen("Simi", w.rgb_hex("#00E5FF"))
    chat.farbe_setzen("Simi", w.rgb_hex("#00E5FF"))
    chat.empfangen("Simi", "Hallo Daniel")
    chat.empfangen("Daniel → Simi", "Go!")
    anwendung.pumpen(30)
    ergebnis["chat"]["verlauf"] = [list(e) for e in chat.verlauf]
    chat.schliessen()

    raute = RauteFenster(600, 200, name="Simi", farbe_hex="#00E5FF")
    raute.zeige(aktivieren=False)
    anwendung.pumpen(100)
    vorher = rect_von(raute.hwnd)
    raute.groesse_setzen(72)
    anwendung.pumpen(50)
    nachher = rect_von(raute.hwnd)
    box = w.RECT()
    _u.GetWindowRgnBox(raute.hwnd, ctypes.byref(box))
    alpha_a = alpha_von(raute.hwnd)
    raute.deckkraft_weiter()
    anwendung.pumpen(30)
    alpha_b = alpha_von(raute.hwnd)
    raute.groesse_setzen(96)
    raute.neu_zeichnen()
    anwendung.pumpen(100)
    lw, lh = raute.leinwand.breite, raute.leinwand.hoehe
    daten = raute.leinwand.bgra()

    def pixel(x: int, y: int) -> list[int]:
        i = (y * lw + x) * 4
        return list(daten[i:i + 3])

    gezeichnet = {"leinwand": [lw, lh], "oben_mitte_innen": pixel(lw // 2, lh // 4 + 2), "links_innen": pixel(lw // 4 + 6, lh // 2),
                  "rechts_innen": pixel(3 * lw // 4 - 6, lh // 2), "ausserhalb_ecke": pixel(4, 4)}
    raute.groesse_setzen(1000)  # geklemmt
    anwendung.pumpen(30)
    gross = rect_von(raute.hwnd)
    raute.groesse_setzen(1)
    anwendung.pumpen(30)
    klein = rect_von(raute.hwnd)
    ergebnis["raute"] = {
        "hoehe_vorher_nachher": [vorher[3] - vorher[1], nachher[3] - nachher[1]],
        "breite_vorher_nachher": [vorher[2] - vorher[0], nachher[2] - nachher[0]],
        "form_folgt": [box.right - box.left, box.bottom - box.top], "position_bleibt": vorher[:2] == nachher[:2],
        "deckkraft_vorher_nachher": [alpha_a, alpha_b], "max_geklemmt_hoehe": gross[3] - gross[1],
        "min_geklemmt_hoehe": klein[3] - klein[1], "gezeichnet_bei_96": gezeichnet,
    }
    raute.schliessen()
    anwendung.pumpen(50)
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
