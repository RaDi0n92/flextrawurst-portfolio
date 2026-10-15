# Aufruf: private Xvfb starten, dann  DISPLAY=:NN PYTHONPATH=augen_haende_bridge/src python3 spike_menue_xvfb.py  (nie auf dem Desktop des Benutzers)
"""Spike Teil 2 (private Xvfb): Menüpunkte im echten X-Backend des Käfigs.
Fragen: (a) welches Fenster liegt an einem Menüpunkt, (b) welche Rechtecke haben die Einträge (GTK), (c) löst ein XTEST-Klick den Eintrag aus?"""
import sys
import time

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import GLib, Gtk

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import menue_linux as ml

backend = ea.X11Backend()

ziel = Gtk.Window(title="Zielfenster")
ziel.move(100, 100)
ziel.resize(300, 200)
ziel.show_all()
for _ in range(50):
    while Gtk.events_pending():
        Gtk.main_iteration()
    time.sleep(0.01)
ziel_xid = ziel.get_window().get_xid()

EINTRAEGE = [(10, "Freigeben: Seed 1", 0), (11, "Bridge beenden", 0), None, (12, "Pausieren", 0)]
bericht = {}


def messen():
    menue = bericht["menue"]
    fenster = menue.get_window()
    ok, ox, oy = fenster.get_origin()
    zeilen = []
    for kind in menue.get_children():
        if isinstance(kind, Gtk.SeparatorMenuItem):
            continue
        a = kind.get_allocation()
        zeilen.append((kind.get_label(), (ox + a.x, oy + a.y, ox + a.x + a.width, oy + a.y + a.height)))
    bericht["zeilen"] = zeilen
    bericht["menue_xid"] = fenster.get_xid()
    bericht["toplevel_xid"] = menue.get_toplevel().get_window().get_xid()
    bericht["tl_kind"] = [c.get_window().get_xid() for c in [menue.get_toplevel()]]
    erstes = zeilen[0][1]
    mitte = ((erstes[0] + erstes[2]) // 2, (erstes[1] + erstes[3]) // 2)
    bericht["fenster_am_eintrag"] = backend.fenster_am_punkt(*mitte)
    bericht["fenster_am_ziel"] = backend.fenster_am_punkt(150, 150)
    backend.maus_bewegen(*mitte)
    time.sleep(0.2)
    backend.maus_taste("links", True)
    backend.maus_taste("links", False)
    return False


def start():
    GLib.timeout_add(600, messen)
    return False


def vorab(menue):
    bericht["menue"] = menue
    GLib.idle_add(start)


gewaehlt = ml.zeige_menue(1, EINTRAEGE, 500, 300, vorab=vorab)
print("Menü-Toplevel-XID:", bericht.get("toplevel_xid"), "| Fenster am Eintrag gleich Toplevel:", bericht.get("fenster_am_eintrag") == bericht.get("toplevel_xid"))
print("Ziel-XID:", ziel_xid, "| Menü-XID:", bericht.get("menue_xid"))
print("Einträge (Text, Schirmrechteck):")
for t, r in bericht.get("zeilen", []):
    print("  ", t, r)
print("Fenster am Eintrag:", bericht.get("fenster_am_eintrag"), "| gleich Menü-XID:", bericht.get("fenster_am_eintrag") == bericht.get("menue_xid"))
print("Fenster am Ziel (Mitte):", bericht.get("fenster_am_ziel"), "| gleich Ziel-XID:", bericht.get("fenster_am_ziel") == ziel_xid)
print("gewählte Befehls-Id nach XTEST-Klick auf den ersten Eintrag:", gewaehlt, "(erwartet 10)")
