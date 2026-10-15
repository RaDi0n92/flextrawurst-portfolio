"""Wine-Probe: Raute mit Name und Tastenkombination, Erfassen einer Kombination per echtem Tastendruck, Hotkey-Wechsel.

Ausgabe: eine JSON-Zeile. Unter Wine gelaufen heißt „PASS unter Wine“, nicht native Windows.
"""

from __future__ import annotations

import ctypes
import json
import sys
import threading
import time

from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.raute_fenster import RauteFenster
from augen_haende_bridge.koerper.tastenkombi import Bedientaste, Erfasser

KEYEVENTF_KEYUP = 0x0002
_u = ctypes.WinDLL("user32", use_last_error=True)
_u.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_uint32, ctypes.c_size_t]
_u.keybd_event.restype = None


def taste(vk: int, unten: bool) -> None:
    _u.keybd_event(vk, 0, 0 if unten else KEYEVENTF_KEYUP, 0)


def main() -> int:
    anwendung = Anwendung()
    anwendung.starten()
    ergebnis: dict = {}

    raute = RauteFenster(200, 200, name="Claude-Host", farbe_hex="#00E5FF", hotkey="F13")
    raute.zeige(aktivieren=False)
    anwendung.pumpen(100)
    l, o, r, u = raute.rechteck()
    vor = (r - l, u - o)
    daten = raute.leinwand.bgra()
    bw, bh = raute.leinwand.breite, raute.leinwand.hoehe
    text_farbe = stil.FARBE_GRUND
    rot, gruen, blau = text_farbe & 0xFF, (text_farbe >> 8) & 0xFF, (text_farbe >> 16) & 0xFF

    def text_pixel() -> int:
        d = raute.leinwand.bgra()
        n = 0
        for y in range(bh // 4, 3 * bh // 4):
            for x in range(bw // 6, 5 * bw // 6):
                i = (y * bw + x) * 4
                if (d[i], d[i + 1], d[i + 2]) == (blau, gruen, rot):
                    n += 1
        return n

    n1 = text_pixel()
    raute.setze_hotkey("Strg+Alt+F5")
    anwendung.pumpen(100)
    l2, o2, r2, u2 = raute.rechteck()
    bw, bh = raute.leinwand.breite, raute.leinwand.hoehe
    n2 = text_pixel()
    ergebnis["raute"] = {"groesse_mit_f13": list(vor), "groesse_mit_langer_kombination": [r2 - l2, u2 - o2],
                          "ungleichseitig": (r - l) > (u - o) * 1.5, "wird_breiter_mit_laengerem_text": (r2 - l2) > (r - l),
                          "position_bleibt": (l, o) == (l2, o2), "textpixel_f13": n1, "textpixel_lang": n2,
                          "leinwand_folgt": [bw, bh] == [r2 - l2, u2 - o2]}
    raute.schliessen()
    anwendung.pumpen(50)

    # Erfassen einer Kombination per echtem Tastendruck (Strg+Alt+F5)
    erg: list = []
    e = Erfasser()
    faden = e.im_hintergrund(erg.append, 5.0)
    time.sleep(0.3)
    taste(w.VK_CONTROL, True)
    taste(w.VK_MENU, True)
    time.sleep(0.15)
    taste(0x74, True)
    time.sleep(0.15)
    taste(0x74, False)
    taste(w.VK_MENU, False)
    taste(w.VK_CONTROL, False)
    faden.join(6)
    ergebnis["erfassen"] = {"kombination": erg[0].text() if erg and erg[0] else None}

    # Bedientaste Strg+Alt: nur beide zusammen
    b = Bedientaste("strg+alt")
    taste(w.VK_CONTROL, True)
    time.sleep(0.15)
    nur_strg = b.gedrueckt()
    taste(w.VK_MENU, True)
    time.sleep(0.15)
    beide = b.gedrueckt()
    taste(w.VK_MENU, False)
    taste(w.VK_CONTROL, False)
    time.sleep(0.15)
    ergebnis["bedientaste_strg_alt"] = {"nur_strg": nur_strg, "beide": beide, "losgelassen": b.gedrueckt()}

    # Hotkey anmelden, wechseln, auslösen
    treffer = []
    ok1 = anwendung.hotkey_setzen("agent:x", 0, 0x7C, lambda: treffer.append("F13"))
    ok2 = anwendung.hotkey_setzen("agent:x", w.MOD_CONTROL | w.MOD_ALT, 0x74, lambda: treffer.append("Strg+Alt+F5"))
    ok_doppelt = anwendung.hotkey_setzen("agent:y", w.MOD_CONTROL | w.MOD_ALT, 0x74, lambda: treffer.append("doppelt"))
    anwendung.pumpen(50)
    taste(0x7C, True)
    taste(0x7C, False)
    anwendung.pumpen(300)
    nach_altem = list(treffer)
    taste(w.VK_CONTROL, True)
    taste(w.VK_MENU, True)
    taste(0x74, True)
    taste(0x74, False)
    taste(w.VK_MENU, False)
    taste(w.VK_CONTROL, False)
    anwendung.pumpen(400)
    ergebnis["hotkey"] = {"anmelden": ok1, "wechseln": ok2, "doppelte_kombination_abgelehnt": not ok_doppelt,
                          "alter_hotkey_loest_nicht_mehr_aus": nach_altem == [], "ausgeloest": treffer}
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
