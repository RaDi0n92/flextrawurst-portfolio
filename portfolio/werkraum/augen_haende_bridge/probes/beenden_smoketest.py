"""Wine-Probe: „Bridge beenden“ aus dem Regie-Menü mit echten Fenstern und einem laufenden Agenten.

Der Klick läuft als echte Mausnachricht auf den Regie-Knopf; das Menü ist durch eine feste Wahl ersetzt (kein Popup
unter Xvfb). Erwartet: die Nachrichtenschleife endet, alle Fenster sind zerstört. Ausgabe: eine JSON-Zeile.
"""

from __future__ import annotations

import ctypes
import json
import sys

from augen_haende_bridge.koerper import regie_fenster as r
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.anwendung import BEENDEN_ID, KoerperAnwendung
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.erster_koerper import ErsterKoerper, arbeitsflaeche
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.regie_fenster import RegieFenster

_u = ctypes.WinDLL("user32", use_last_error=True)
_u.SendMessageW.argtypes = [w.wintypes.HWND, ctypes.c_uint, w.wintypes.WPARAM, w.wintypes.LPARAM]
_u.SendMessageW.restype = w.wintypes.LPARAM
_u.IsWindow.argtypes = [w.wintypes.HWND]


class Runtime:
    def __init__(self, url, token, *, on_event):
        self.gestoppt = False

    def start(self): pass
    def stop(self): self.gestoppt = True
    def publish(self, kind, payload, *, message_id=None): return "id"


def main() -> int:
    gui = Anwendung()
    gui.starten()
    app = KoerperAnwendung(url="ws://x", token="t" * 40, gui=gui, koerper_bauen=lambda **kw: ErsterKoerper(**kw),
                           runtime_bauen=Runtime, regie_bauen=RegieFenster, chat_bauen=ChatFenster,
                           arbeitsflaeche=arbeitsflaeche, menue_anzeigen=lambda *a, **k: BEENDEN_ID)
    app.starten()
    app.ereignis({"kind": "runtime.connected", "welcome": {}})
    app.ereignis({"kind": "event", "event_kind": "terminal_list", "payload": {
        "request_id": "r", "starts": [{"start_id": "s", "name": "Simi", "ort": "Host"}], "terminals": []}})
    app.ereignis({"kind": "event", "event_kind": "terminal_state", "payload": {
        "terminal_id": "t-1", "start_id": "s", "name": "Simi", "state": "running", "exit_code": None, "reason": ""}})
    gui.pumpen(200)
    hwnds = {"regie": app.regie.hwnd, "chat": app.chat.hwnd, "raute": app.agenten["t-1"].koerper.raute.hwnd,
             "terminal": app.agenten["t-1"].koerper.terminal.hwnd}
    vorher = {k: bool(_u.IsWindow(h)) for k, h in hwnds.items()}
    links, oben, rechts, unten = r.knopf_rechtecke()["regie"]
    x, y = (links + rechts) // 2, (oben + unten) // 2
    _u.SendMessageW(hwnds["regie"], 0x0201, 1, (y << 16) | x)  # echter Klick auf den Regie-Knopf
    _u.SendMessageW(hwnds["regie"], 0x0202, 0, (y << 16) | x)
    gui.pumpen(500)
    print(json.dumps({
        "status": "ok", "fenster_vorher": vorher,
        "schleife_beendet": gui.beendet,
        "fenster_nachher": {k: bool(_u.IsWindow(h)) for k, h in hwnds.items()},
        "runtime_gestoppt": app.runtime.gestoppt, "abbau_fehler": getattr(app, "abbau_fehler", None),
    }, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
