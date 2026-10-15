"""Wine-Probe der Hände: ein Auftrag `raute_tippen` drückt per SendInput die Tastenkombination der Raute, tippt in das Eingabefeld
und bestätigt mit Enter. Echte Fenster, echter Hotkey, echtes SendInput. Ausgabe: eine JSON-Zeile."""

from __future__ import annotations

import json
import sys
import time

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.anwendung import KoerperAnwendung
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.erster_koerper import ErsterKoerper, arbeitsflaeche
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.regie_fenster import RegieFenster
from augen_haende_bridge.koerper.tasten_senden import Haende
from augen_haende_bridge.koerper.tastenkombi import Kombination


class Runtime:
    def __init__(self, url, token, *, on_event):
        pass

    def start(self): pass
    def stop(self): pass
    def publish(self, kind, payload, *, message_id=None): return "id"


def pumpen_bis(gui, bedingung, sekunden=8.0):
    ende = time.monotonic() + sekunden
    while time.monotonic() < ende:
        gui.pumpen(50)
        if bedingung():
            return True
    return bedingung()


def main() -> int:
    gui = Anwendung()
    gui.starten()
    app = KoerperAnwendung(url="ws://x", token="t" * 40, gui=gui, koerper_bauen=lambda **kw: ErsterKoerper(**kw),
                           runtime_bauen=Runtime, regie_bauen=RegieFenster, chat_bauen=ChatFenster,
                           arbeitsflaeche=arbeitsflaeche, haende=Haende())
    app.starten()
    app.ereignis({"kind": "runtime.connected", "welcome": {}})
    app.ereignis({"kind": "event", "event_kind": "terminal_list", "payload": {
        "request_id": "r", "starts": [{"start_id": "s", "name": "Simi", "ort": "Host"}], "terminals": []}})
    app.ereignis({"kind": "event", "event_kind": "terminal_state", "payload": {
        "terminal_id": "t-1", "start_id": "s", "name": "Simi", "state": "running", "exit_code": None, "reason": ""}})
    gui.pumpen(200)
    agent = app.agenten["t-1"]
    app._hotkey_erfasst("t-1", Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74))
    gui.pumpen(100)
    ergebnis: dict = {"kombination": agent.hotkey}

    app.ereignis({"kind": "event", "event_kind": "raute_tippen",
                  "payload": {"terminal_id": "t-1", "text": "Ich sehe den Turm äöü"}})
    angekommen = pumpen_bis(gui, lambda: any(e[0] == "Simi" for e in app.chat.verlauf), 10.0)
    ergebnis["chat_verlauf"] = [list(e)[:2] for e in app.chat.verlauf]
    ergebnis["text_angekommen"] = angekommen
    ergebnis["feld_danach_zu"] = agent.koerper.eingabe is None
    ergebnis["haende_fertig"] = pumpen_bis(gui, lambda: not agent.haende_laufen, 5.0)

    # Hände aus: nichts passiert
    agent.haende = False
    vor = len(app.chat.verlauf)
    app.ereignis({"kind": "event", "event_kind": "raute_tippen", "payload": {"terminal_id": "t-1", "text": "soll nicht"}})
    gui.pumpen(600)
    ergebnis["haende_aus_tippt_nicht"] = len(app.chat.verlauf) == vor and agent.koerper.eingabe is None
    agent.haende = True

    # Not-Aus: nichts passiert
    app.not_aus.ausloesen("probe")
    app.ereignis({"kind": "event", "event_kind": "raute_tippen", "payload": {"terminal_id": "t-1", "text": "auch nicht"}})
    gui.pumpen(600)
    ergebnis["not_aus_tippt_nicht"] = len(app.chat.verlauf) == vor and agent.koerper.eingabe is None
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    app.beenden()
    gui.pumpen(300)
    return 0


if __name__ == "__main__":
    sys.exit(main())
