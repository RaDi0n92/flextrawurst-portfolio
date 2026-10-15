"""Ein echtes GTK-Programm für die Hände-Tests: Schaltfläche (zählt Klicks), Eingabefeld, Schieberegler, Zeichenfläche (merkt Zeigerweg und gedrückte Tasten), Zähler für Doppelklicks.
Schreibt seinen Stand laufend als JSON in die übergebene Datei, damit der Test von außen die Wirkung prüfen kann."""
import json
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

stand_datei = sys.argv[1]
titel = sys.argv[2] if len(sys.argv) > 2 else "Haendeprobe"
stand = {"klicks": 0, "doppel": 0, "rechts": 0, "text": "", "regler": 0.0, "zug_start": None, "zug_ende": None, "zug_punkte": 0, "gedrueckt": False, "tasten": [], "rad": 0, "fokus": False}


def rect_von(w):
    gw = fenster.get_window()
    if gw is None:
        return None
    _ok, ox, oy = gw.get_origin()
    t = w.translate_coordinates(fenster, 0, 0)
    if t is None:
        return None
    a = w.get_allocation()
    return [ox + t[0], oy + t[1], ox + t[0] + a.width, oy + t[1] + a.height]


def schreibe(*_):
    anzeigen()
    stand["rects"] = {n: rect_von(w) for n, w in (("knopf", knopf), ("feld", feld), ("regler", regler), ("flaeche", flaeche))}
    stand["text"] = feld.get_text()
    stand["regler"] = regler.get_value()
    stand["fokus"] = fenster.is_active() or feld.has_focus()
    with open(stand_datei, "w", encoding="utf-8") as f:
        json.dump(stand, f)
    return True


fenster = Gtk.Window(title=titel)
fenster.set_default_size(420, 300)
fenster.move(40, 40)
kiste = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
knopf = Gtk.Button(label="Zaehlen")
feld = Gtk.Entry()
regler = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
flaeche = Gtk.EventBox()
flaeche.set_size_request(400, 120)
zeichen = Gtk.DrawingArea()  # sichtbar: die gezogene Linie (Szenario Schritt 6 „Linie ziehen“); Ereignisse nimmt weiter die EventBox
flaeche.add(zeichen)
linie: list[tuple[float, float]] = []
neu_ziehen, anfang = [False], [(0.0, 0.0)]
zaehler = Gtk.Label(label="Doppel 0 · Rechts 0 · Rad 0 · Zug 0")  # sichtbar: die Zähler, die sonst nur in der JSON-Datei stehen (Szenario Schritt 6: „Zähler steigen“)
flaeche.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)


def klick(*_):
    stand["klicks"] += 1
    knopf.set_label(f"Zaehlen · {stand['klicks']}")  # der Zähler muss im Fenster sichtbar sein (Szenario Schritt 2: „Zähler steht eins höher“), nicht nur in der JSON-Datei
    schreibe()


def taste(widget, ereignis):
    stand["tasten"].append([Gdk.keyval_name(ereignis.keyval), int(ereignis.state & 0xFF)])
    schreibe()
    return False


def zeichnen(w, cr):
    cr.set_source_rgb(0.93, 0.93, 0.93)
    cr.paint()
    cr.set_source_rgb(0.1, 0.1, 0.1)
    cr.set_line_width(3)
    for i, (x, y) in enumerate(linie):
        cr.line_to(x, y) if i else cr.move_to(x, y)
    cr.stroke()
    return False


def anzeigen():
    zaehler.set_text(f"Doppel {stand['doppel']} · Rechts {stand['rechts']} · Rad {stand['rad']} · Zug {stand['zug_punkte']}")
    zeichen.queue_draw()


def druecken(w, e):
    if e.type == Gdk.EventType.BUTTON_PRESS and e.button == 1:
        # Ein Klick löscht die letzte Linie und ihren Zähler nicht: sie gelten, bis ein neuer Zug wirklich beginnt (erste Bewegung bei gedrückter Taste).
        stand["gedrueckt"], stand["zug_start"], neu_ziehen[0] = True, [int(e.x_root), int(e.y_root)], True
        anfang[0] = (e.x, e.y)
    elif e.type == Gdk.EventType._2BUTTON_PRESS:
        stand["doppel"] += 1
    if e.type == Gdk.EventType.BUTTON_PRESS and e.button == 3:
        stand["rechts"] += 1
    schreibe()
    return True


def loslassen(w, e):
    if e.button == 1:
        stand["gedrueckt"], stand["zug_ende"] = False, [int(e.x_root), int(e.y_root)]
    schreibe()
    return True


def bewegung(w, e):
    if stand["gedrueckt"]:
        if neu_ziehen[0]:
            neu_ziehen[0] = False
            stand["zug_punkte"] = 0
            linie.clear()
            linie.append(anfang[0])
        stand["zug_punkte"] += 1
        stand["zug_ende"] = [int(e.x_root), int(e.y_root)]
        linie.append((e.x, e.y))
        schreibe()
    return True


def rad(w, e):
    stand["rad"] += 1 if e.direction == Gdk.ScrollDirection.DOWN else -1
    schreibe()
    return True


knopf.connect("clicked", klick)
fenster.connect("key-press-event", taste)
flaeche.connect("button-press-event", druecken)
flaeche.connect("button-release-event", loslassen)
flaeche.connect("motion-notify-event", bewegung)
flaeche.connect("scroll-event", rad)
zeichen.connect("draw", zeichnen)
for w in (knopf, feld, regler, flaeche, zaehler):
    kiste.pack_start(w, False, False, 2)
fenster.add(kiste)
fenster.connect("destroy", Gtk.main_quit)
fenster.show_all()
GLib.timeout_add(150, schreibe)
Gtk.main()
