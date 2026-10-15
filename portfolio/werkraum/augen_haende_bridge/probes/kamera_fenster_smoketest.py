"""Wine/Windows: echtes KameraFenster mit synthetischem Bild: Zeichnen (gespiegelt, skaliert), Groesse aendern, Pixel pruefen."""
import ctypes
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper.fenster import Anwendung, Leinwand
from augen_haende_bridge.koerper.kamera_fenster import KameraFenster, KOPF_H

gui = Anwendung()
f = KameraFenster(200, 200, breite=240, hoehe=190, name="Probe", farbe_hex="#00E5FF")
f.zeige(aktivieren=False)
b, h = 64, 48
# linke Haelfte rot, rechte Haelfte blau (BGR)
zeile = b"\x00\x00\xff" * (b // 2) + b"\xff\x00\x00" * (b // 2)
f.bild_setzen(zeile * h, b, h)
gui.pumpen(200)
l = Leinwand(240, 190)
f.zeichnen(l)
bits = (ctypes.c_ubyte * (240 * 190 * 4)).from_address(l._bits.value)


def pixel(x, y):
    i = (y * 240 + x) * 4
    return bits[i + 2], bits[i + 1], bits[i]  # R, G, B


mitte_y = KOPF_H + (190 - KOPF_H) // 2
ergebnis = {"links": pixel(60, mitte_y), "rechts": pixel(180, mitte_y), "kopf": pixel(120, 2)}
# gespiegelt: links im Fenster muss BLAU sein (war rechts im Bild), rechts ROT
f.verschiebe(200, 200, 400, 300)
gui.pumpen(200)
ergebnis["groesse"] = f.clientgroesse()
f.schliessen()
print(json.dumps({"status": "ok", **ergebnis}))
