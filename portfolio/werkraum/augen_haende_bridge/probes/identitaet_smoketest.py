"""Wine/Windows: echte Raute, Terminal und Regieleiste mit neuem Namen und neuer Farbe; Fenstertitel, Breite und Pixelfarbe folgen."""
import ctypes
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.fenster import Anwendung, Leinwand
from augen_haende_bridge.koerper.raute_fenster import RauteFenster
from augen_haende_bridge.koerper.regie_fenster import RegieFenster
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster

gui = Anwendung()


def titel(hwnd):
    puffer = ctypes.create_unicode_buffer(200)
    w.user32.GetWindowTextW(hwnd, puffer, 200)
    return puffer.value


raute = RauteFenster(100, 100, name="Codex", farbe_hex="#00E5FF", hotkey="F13")
terminal = TerminalFenster(300, 100, name="Codex", ort="vd1", farbe_hex="#00E5FF")
breite_vorher = raute.rechteck()[2] - raute.rechteck()[0]
raute.setze_identitaet(name="Chef vom Dienst", farbe_hex="#FF9100")
terminal.setze_identitaet(name="Chef vom Dienst", farbe_hex="#FF9100")
gui.pumpen(200)
breite_nachher = raute.rechteck()[2] - raute.rechteck()[0]
regie = RegieFenster(30, 400)
regie.setze(mikrofon="ein", kamera="startet", agent_name="Chef")
gui.pumpen(100)
l = Leinwand(regie.clientgroesse()[0], regie.clientgroesse()[1])
regie.zeichnen(l)
print(json.dumps({"status": "ok", "raute_titel": titel(raute.hwnd), "terminal_titel": titel(terminal.hwnd), "raute_breiter": breite_nachher > breite_vorher,
                  "raute_farbe": raute.farbe_hex, "terminal_farbe": terminal.farbe_hex, "regie_gezeichnet": True}))
for f in (raute, terminal, regie):
    f.schliessen()
