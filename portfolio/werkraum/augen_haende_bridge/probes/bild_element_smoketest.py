"""Wine/Windows: das schwebende Bild-Element als echtes Fenster: Größe, Deckkraft per Rad/Knopf, Menü nur mit Bedientaste, Abgleich mit dem Dokument."""
import io
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from PIL import Image

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.bild_element_fenster import BildElementFenster
from augen_haende_bridge.koerper.bild_elemente import BildElemente
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.objekte import Dokument, Objekt

gui = Anwendung()
puffer = io.BytesIO()
Image.new("RGB", (80, 40), (200, 40, 40)).save(puffer, format="PNG")
dok = Dokument("t")
dok.hinzufuegen(Objekt("b", "bild", [(0.1, 0.1), (0.3, 0.2)], bild=puffer.getvalue(), bildschirm=True, schwebend=True))
gedrueckt = {"mod": False}
menues = []
be = BildElemente(lambda x, y, b, h, **kw: BildElementFenster(x, y, b, h, **kw), menue=lambda oid, s, x, y: menues.append((oid, x, y)),
                  modifikator=lambda: gedrueckt["mod"])
GATE = (100, 100, 900, 600)
be.tick("t", dok, True, GATE, False)
gui.pumpen(100)
f = be.stand["b"].fenster
ergebnis = {"rechteck": f.rechteck(), "sichtbar": f.sichtbar()}
f.bei_rad(120, 10, 30, 0)
ergebnis["nach_rad"] = [f.deckkraft_prozent(), dok.objekte["b"].deckkraft]
f.bei_rechtsklick(10, 30, 0)
ergebnis["menue_ohne_taste"] = len(menues)
gedrueckt["mod"] = True
f.bei_rechtsklick(10, 30, 0)
ergebnis["menue_mit_taste"] = len(menues)
f.verschiebe(300, 300, 200, 20)
be.tick("t", dok, True, GATE, False)
be.tick("t", dok, True, GATE, False)
ergebnis["nach_ziehen_rechteck"] = f.rechteck()
ergebnis["punkte"] = [[round(v, 3) for v in p] for p in dok.objekte["b"].punkte]
ergebnis["ausnahme_privat"] = bool(f.aufnahme_ausnehmen(True))
print(json.dumps({"status": "ok", **ergebnis}))
be.schliessen()
