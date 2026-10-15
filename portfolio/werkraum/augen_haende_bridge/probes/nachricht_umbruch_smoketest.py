"""Wine/Windows: echtes Banner und echte Box neben der Raute mit langem Text: Umbruch, Hoehe, Position im Bildschirm."""
import json
import os
import sys
import time

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.nachricht_fenster import BannerFenster, TickerFenster

gui = Anwendung()
ziel = (0, 0, 1280, 720)
text = "Daniel: Das ist ein sehr langer Text, der in einem Banner und in der Box neben der Raute umgebrochen werden muss, damit man alles lesen kann."
jetzt = lambda: int(time.monotonic() * 1000)
raute = (600, 300, 648, 348)  # mitten im Ziel: Banner und Box wuerden sich ohne Ausweichen ueberdecken
lang = text * 4
t = TickerFenster(text=lang, farbe_hex="#00E5FF", raute_rechteck=raute, grenzen=lambda: ziel)
b = BannerFenster(text=lang, farbe_hex="#F2F2F2", ziel_rechteck=ziel, raute_rechteck=raute, jetzt_ms=jetzt,
                  meiden=lambda: [t.rechteck()])
b.zeige(aktivieren=False)
t.zeige(aktivieren=False)
gui.pumpen(300)
def schnitt(a, c):
    return a[0] < c[2] and c[0] < a[2] and a[1] < c[3] and c[1] < a[3]


ergebnis = {"ueberlappt": schnitt(b.rechteck(), t.rechteck()), "banner_ueber_raute": schnitt(b.rechteck(), raute), "banner_zeilen": len(b.zeilen), "banner_rect": b.rechteck(), "ticker_zeilen": len(t.zeilen), "ticker_rect": t.rechteck(),
            "banner_alpha_start": b.deckkraft_lesen()}
gui.pumpen(1500)
ergebnis["banner_alpha_nach_1_5s"] = b.deckkraft_lesen()
b.schliessen()
t.schliessen()
print(json.dumps({"status": "ok", **ergebnis}))
