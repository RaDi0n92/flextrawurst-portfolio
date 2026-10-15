"""Wine/Windows: echtes Zielfenster und echte Elemente: Mitwandern, Einrahmen, Schliessen; Knoepfe 'Ort' und 'A+H' im Terminal."""
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.kamera_fenster import KameraFenster
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster
from augen_haende_bridge.koerper.ziel_halter import ORT_ZIEL, ZielHalter

gui = Anwendung()
ziel = ChatFenster(400, 200, breite=500, hoehe=400)  # irgendein echtes Fenster dient als Zielfenster
ziel.zeige(aktivieren=False)
element = KameraFenster(450, 260, name="Probe", farbe_hex="#00E5FF")
element.zeige(aktivieren=False)
gui.pumpen(100)
halter = ZielHalter()
halter.anmelden("kamera:t", element, lambda: ziel.hwnd)
fehler = halter.setze_ort("kamera:t", ORT_ZIEL)
rel = halter.elemente["kamera:t"].rel
ziel.verschiebe(700, 300)
gui.pumpen(100)
halter.tick()
a = element.rechteck()
mitgewandert = (a[0] - 700, a[1] - 300) == rel
# eingerahmt: Zielfenster schrumpft, Element muss drin bleiben
ziel.verschiebe(700, 300, 300, 200)
gui.pumpen(100)
halter.tick()
b = element.rechteck()
z = ziel.rechteck()
drin = z[0] <= b[0] and b[2] <= z[2] and z[1] <= b[1] and b[3] <= z[3]
# Zielfenster schliessen -> Element verschwindet
ziel.schliessen()
gui.pumpen(100)
halter.tick()
verschwunden = halter.versteckt("kamera:t")

# Terminal-Knoepfe
gerufen = []
t = TerminalFenster(100, 100, zeilen=10, spalten=60, name="P", ort="x", farbe_hex="#00E5FF",
                    ort_gewuenscht=lambda x, y: gerufen.append(("ort", x, y)), augen_umschalten=lambda: gerufen.append("augen"))
t.zeige(aktivieren=False)
gui.pumpen(100)
k = t.leiste_knopf_rechtecke()
s = t.scanner_rechteck()
frei = k["augen"][2] <= s[0] and k["ort"][2] <= k["augen"][0]
for name in ("augen", "ort"):
    r = k[name]
    t.bei_maus_runter((r[0] + r[2]) // 2, (r[1] + r[3]) // 2, 1)
    t.bei_maus_hoch((r[0] + r[2]) // 2, (r[1] + r[3]) // 2, 0)
t.setze_augen(False)
t.setze_ort_text("Ort")
gui.pumpen(100)
print(json.dumps({"status": "ok", "ort_fehler": fehler, "mitgewandert": mitgewandert, "eingerahmt": drin, "verschwunden_beim_schliessen": verschwunden,
                  "knoepfe_ueberlappen_nicht": frei, "callbacks": [g if isinstance(g, str) else g[0] for g in gerufen]}))
element.schliessen()
t.schliessen()
