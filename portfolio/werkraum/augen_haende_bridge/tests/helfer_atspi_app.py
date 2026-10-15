"""Ein kleines echtes GTK-Programm für die AT-SPI-Tests: Schaltfläche (zählt), Eingabefeld, Beschriftung. Schreibt den Stand in eine Datei, damit der Test von außen prüfen kann."""
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

stand = sys.argv[1]


def schreibe(*_):
    with open(stand, "w", encoding="utf-8") as f:
        f.write(f"{zaehler[0]}|{feld.get_text()}")
    return True


zaehler = [0]
fenster = Gtk.Window(title="AtspiPruefling")
fenster.set_default_size(320, 160)
kiste = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
etikett = Gtk.Label(label="Beschriftung eins")
knopf = Gtk.Button(label="Zählen")
feld = Gtk.Entry()
feld.set_text("")
knopf.connect("clicked", lambda *_: (zaehler.__setitem__(0, zaehler[0] + 1), schreibe()))
feld.connect("changed", schreibe)
for w in (etikett, knopf, feld):
    kiste.pack_start(w, False, False, 0)
fenster.add(kiste)
fenster.connect("destroy", Gtk.main_quit)
fenster.show_all()
GLib.timeout_add(200, schreibe)
Gtk.main()
