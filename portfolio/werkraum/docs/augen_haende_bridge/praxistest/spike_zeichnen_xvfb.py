# Aufruf: private Xvfb starten, dann  DISPLAY=:NN PYTHONPATH=augen_haende_bridge/src python3 spike_zeichnen_xvfb.py  (nie auf dem Desktop des Benutzers)
"""Spike Schritt 15 (private Xvfb, BRIDGE_BACKEND=linux): was liegt am Zielpunkt, wenn der Zeichenmodus offen ist?
Echte Klassen: ZeichenFenster (Editorfläche über dem Ziel), WerkzeugLeiste (eigenes Fenster), echter X11Backend."""
import os
import sys
import time

os.environ["BRIDGE_BACKEND"] = "linux"

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper.editor_logik import Editor
from augen_haende_bridge.koerper.komposition import Arbeitsflaechen
from augen_haende_bridge.koerper.zeichen_fenster import WerkzeugLeiste, ZeichenFenster


def pumpen(sek=0.4):
    ende = time.time() + sek
    while time.time() < ende:
        while Gtk.events_pending():
            Gtk.main_iteration()
        time.sleep(0.01)


ziel = Gtk.Window(title="Zielfenster")
ziel.move(100, 100)
ziel.resize(400, 300)
ziel.show_all()
pumpen()
ziel_xid = ziel.get_window().get_xid()
backend = ea.X11Backend()
vorher = backend.fenster_am_punkt(250, 250)

arbeit = Arbeitsflaechen()
dok = arbeit.dokument("desktop")
fenster_ref = {}
editor = Editor(dok, lambda: fenster_ref["f"].clientgroesse(), bei_aenderung=lambda: None, bei_beenden=lambda: None)
fenster = ZeichenFenster((100, 100, 500, 400), editor)
fenster_ref["f"] = fenster
leiste = WerkzeugLeiste(0, 0, editor)
leiste.verschiebe(100, 40)
fenster.zeige(aktivieren=True)
leiste.zeige(aktivieren=False)
pumpen(0.8)

print("Ziel-XID:", ziel_xid)
print("Fenster am Zielpunkt VOR dem Zeichenmodus :", vorher, "(gleich Ziel:", vorher == ziel_xid, ")")
am_punkt = backend.fenster_am_punkt(250, 250)
print("Fenster am Zielpunkt MIT Zeichenmodus     :", am_punkt, "(gleich Ziel:", am_punkt == ziel_xid, ")")
print("ZeichenFenster hwnd:", getattr(fenster, "hwnd", None), "| Rechteck:", fenster.rechteck() if hasattr(fenster, "rechteck") else "?")
print("Leiste hwnd:", getattr(leiste, "hwnd", None), "| Rechteck:", leiste.rechteck())
am_knopf = backend.fenster_am_punkt(*[(a + b) // 2 for a, b in zip(leiste.rechteck()[:2], leiste.rechteck()[2:])])
print("Fenster in der Mitte der Leiste           :", am_knopf, "(gleich Leiste:", am_knopf == getattr(leiste, "hwnd", None), ")")
print("Rechtecke der Leistenknöpfe (Name -> l,o,r,u), erste fünf:", list(leiste._rechtecke.items())[:5])
