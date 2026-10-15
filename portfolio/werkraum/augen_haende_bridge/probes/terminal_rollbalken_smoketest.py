"""Wine/Windows: echtes TerminalFenster mit Verlauf: Zeichnen mit Rollbalken, Rad, Griff und Menue-Koordinaten ohne Absturz."""
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster

gui = Anwendung()
f = TerminalFenster(100, 100, zeilen=20, spalten=60, name="Probe", ort="test", farbe_hex="#00E5FF")
f.modell.einspeisen(b"".join(b"zeile %d\r\n" % i for i in range(200)))
f.neu_zeichnen()
gui.pumpen(300)
ergebnis = {"verlauf": f.modell.verlauf_laenge(), "griff": f.griff_rechteck(), "balken": f.rollbalken_rechteck()}
links, oben, _, _ = f.gitter_rechteck()
f.bei_rad(120, 100 + links + 5, 100 + oben + 5, 0)
f.bei_rad(120, 100 + links + 5, 100 + oben + 5, 0)
gui.pumpen(100)
ergebnis["versatz_nach_rad"] = f.modell.verlauf_versatz()
griff = f.griff_rechteck()
f.bei_maus_runter(griff[0] + 2, (griff[1] + griff[3]) // 2, 1)
f.bei_maus_bewegt(griff[0] + 2, griff[1] - 30, 1)
f.bei_maus_hoch(griff[0] + 2, griff[1] - 30, 0)
gui.pumpen(100)
ergebnis["versatz_nach_ziehen"] = f.modell.verlauf_versatz()
ergebnis["zeile0"] = f.modell.zeile_text(0).strip()
f.schliessen()
print(json.dumps({"status": "ok", **ergebnis}))
