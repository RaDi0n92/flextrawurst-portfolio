"""Wine-Probe: Die Tastenkombination einer Raute öffnet das Eingabefeld; der Agent tippt, Enter = seine Rede.

Echte Fenster, echter Hotkey (RegisterHotKey) und echter Tastendruck. Ausgabe: eine JSON-Zeile.
"""

from __future__ import annotations

import ctypes
import json
import sys
import time

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.anwendung import KoerperAnwendung
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.erster_koerper import ErsterKoerper, arbeitsflaeche
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.regie_fenster import RegieFenster
from augen_haende_bridge.koerper.tastenkombi import Kombination

KEYEVENTF_KEYUP = 0x0002
_u = ctypes.WinDLL("user32", use_last_error=True)
_u.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_uint32, ctypes.c_size_t]
_u.keybd_event.restype = None
_u.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
_u.FindWindowW.restype = w.wintypes.HWND
_u.IsWindowVisible.argtypes = [w.wintypes.HWND]
_u.GetWindowRect.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]
_u.SendMessageW.argtypes = [w.wintypes.HWND, ctypes.c_uint, w.wintypes.WPARAM, w.wintypes.LPARAM]
_u.SendMessageW.restype = w.wintypes.LPARAM


class Runtime:
    def __init__(self, url, token, *, on_event):
        pass

    def start(self): pass
    def stop(self): pass
    def publish(self, kind, payload, *, message_id=None): return "id"


def taste(vk: int, unten: bool) -> None:
    _u.keybd_event(vk, 0, 0 if unten else KEYEVENTF_KEYUP, 0)


def feld():
    hwnd = _u.FindWindowW("AuHEingabe", None)
    return hwnd if hwnd and _u.IsWindowVisible(hwnd) else None


def main() -> int:
    gui = Anwendung()
    gui.starten()
    app = KoerperAnwendung(url="ws://x", token="t" * 40, gui=gui, koerper_bauen=lambda **kw: ErsterKoerper(**kw),
                           runtime_bauen=Runtime, regie_bauen=RegieFenster, chat_bauen=ChatFenster,
                           arbeitsflaeche=arbeitsflaeche)
    app.starten()
    app.ereignis({"kind": "runtime.connected", "welcome": {}})
    app.ereignis({"kind": "event", "event_kind": "terminal_list", "payload": {
        "request_id": "r", "starts": [{"start_id": "s", "name": "Simi", "ort": "Host"}], "terminals": []}})
    app.ereignis({"kind": "event", "event_kind": "terminal_state", "payload": {
        "terminal_id": "t-1", "start_id": "s", "name": "Simi", "state": "running", "exit_code": None, "reason": ""}})
    gui.pumpen(200)
    agent = app.agenten["t-1"]
    ergebnis: dict = {"raute_text": agent.koerper.raute.text(), "raute_groesse": [agent.koerper.raute.breite, agent.koerper.raute.groesse]}

    app._hotkey_erfasst("t-1", Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74))  # so, als hätte Daniel sie festgelegt
    gui.pumpen(100)
    ergebnis["raute_text_nach_festlegen"] = agent.koerper.raute.text()
    ergebnis["feld_vorher_offen"] = feld() is not None

    taste(w.VK_CONTROL, True)  # echter Tastendruck: der Agent drückt die Kombination aus der Raute
    taste(w.VK_MENU, True)
    taste(0x74, True)
    taste(0x74, False)
    taste(w.VK_MENU, False)
    taste(w.VK_CONTROL, False)
    gui.pumpen(500)
    hwnd = feld()
    ergebnis["feld_nach_kombination_offen"] = hwnd is not None
    if hwnd:
        r = w.RECT()
        _u.GetWindowRect(hwnd, ctypes.byref(r))
        raute = agent.koerper.raute.rechteck()
        daneben = r.left >= raute[2] or r.right <= raute[0]  # rechts daneben, am Bildschirmrand links daneben
        ergebnis["feld_neben_der_raute"] = {"raute": list(raute), "feld": [r.left, r.top, r.right, r.bottom],
                                            "ueberlappt_nicht": daneben,
                                            "mitte_passt": abs((r.top + r.bottom) // 2 - (raute[1] + raute[3]) // 2) <= 4}
        for zeichen in "Hallo Welt":
            _u.SendMessageW(hwnd, 0x0102, ord(zeichen), 0)  # WM_CHAR, wie getippt
        gui.pumpen(100)
        _u.SendMessageW(hwnd, 0x0102, 0x0D, 0)  # Enter
        gui.pumpen(400)
    ergebnis["feld_nach_enter_offen"] = feld() is not None
    ergebnis["chat_verlauf"] = [list(e)[:2] for e in app.chat.verlauf]
    ergebnis["raute_letzte_nachricht"] = agent.koerper.raute.letzte_nachricht
    ergebnis["banner_und_ticker"] = [agent.koerper.banner is not None, agent.koerper.ticker is not None]

    # Esc bricht ab
    app.eingabe_oeffnen("t-1")
    gui.pumpen(200)
    hwnd2 = feld()
    if hwnd2:
        _u.SendMessageW(hwnd2, 0x0102, ord("x"), 0)
        _u.SendMessageW(hwnd2, 0x0102, 0x1B, 0)
        gui.pumpen(300)
    ergebnis["esc"] = {"offen_vorher": hwnd2 is not None, "offen_nachher": feld() is not None,
                        "chat_unveraendert": len(app.chat.verlauf) == len(ergebnis["chat_verlauf"])}
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    app.beenden()
    gui.pumpen(300)
    return 0


if __name__ == "__main__":
    sys.exit(main())
