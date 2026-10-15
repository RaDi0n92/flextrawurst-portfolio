"""Linux (eigener Xvfb): echte GTK-Fenster der Linux-Fensterschicht, bedient mit echten X-Ereignissen (XTEST).

Prüft: Zeigen und Zeichnen, Maus (Klick, Doppelklick, Rechtsklick, Bewegung, Rad), Tasten und Zeichen, Verschieben und Größenändern über Trefferwerte,
Mindestgröße, Timer, Fensterform, Durchklick, Pixel-Alpha-Fenster mit Formmaske, Menü, Zwischenablage, Hotkey. Gibt am Ende `linux fenster probe ok` aus.
"""
import os
import sys
import time

os.environ["BRIDGE_BACKEND"] = "linux"
import faulthandler
import sys

if os.environ.get("BRIDGE_TEST_XVFB") != "1":  # die Probe tippt Tasten und bewegt den Zeiger: nur auf einem eigenen, privaten Xvfb
    print("Abbruch: nur unter `xvfb-run … env BRIDGE_TEST_XVFB=1` starten (nie auf einem sichtbaren Desktop).", file=sys.stderr)
    sys.exit(2)
faulthandler.dump_traceback_later(60, exit=True)  # die Probe darf nie ewig hängen

from Xlib import X, XK
from Xlib.ext import shape, xtest
from PIL import Image

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper import x11_helfer as x
from augen_haende_bridge.koerper.fenster import Anwendung, Fenster, Leinwand, Schrift
from augen_haende_bridge.koerper.pixel_fenster import PixelFenster
from augen_haende_bridge.koerper import menue, tasten_x11

anzeige = x.anzeige()
app = Anwendung()
app.starten()
ereignisse: list[tuple] = []


def pruefe(bedingung, text):
    if not bedingung:
        print("FEHLER:", text, "| Ereignisse:", ereignisse[-6:], file=sys.stderr)
        sys.exit(1)


class Probe(Fenster):
    klasse = "AuHProbe"

    def zeichnen(self, l):
        ereignisse.append(("zeichnen", l.breite, l.hoehe))
        l.fuellen(w.rgb(10, 20, 30))
        l.fuellen(w.rgb(200, 0, 0), 5, 5, 25, 25)

    def treffer(self, sx, sy):
        links, oben, rechts, unten = self.rechteck()
        cx, cy = sx - links, sy - oben
        if cx >= rechts - links - 8 and cy >= unten - oben - 8:
            return w.HTBOTTOMRIGHT
        return w.HTCAPTION if cy < 12 else w.HTCLIENT

    def bei_maus_runter(self, x_, y_, f): ereignisse.append(("runter", x_, y_, f))
    def bei_maus_hoch(self, x_, y_, f): ereignisse.append(("hoch", x_, y_, f))
    def bei_doppelklick(self, x_, y_, f): ereignisse.append(("doppel", x_, y_))
    def bei_rechtsklick(self, x_, y_, f): ereignisse.append(("rechts", x_, y_))
    def bei_maus_bewegt(self, x_, y_, f): ereignisse.append(("bewegt", x_, y_))
    def bei_rad(self, d, sx, sy, f): ereignisse.append(("rad", d, sx, sy))
    def bei_taste(self, vk, lp, sys_): ereignisse.append(("taste", vk, sys_))
    def bei_zeichen(self, c, sys_): ereignisse.append(("zeichen", c))
    def bei_fokus(self, h): ereignisse.append(("fokus", h))
    def bei_groesse(self, b, h): ereignisse.append(("groesse", b, h))

    def bei_nachricht(self, msg, wp, lp):
        if msg == w.WM_GETMINMAXINFO:
            import ctypes
            info = ctypes.cast(lp, ctypes.POINTER(w.MINMAXINFO)).contents
            info.ptMinTrackSize.x, info.ptMinTrackSize.y = 60, 40
            return 0
        if msg == w.WM_SETCURSOR:
            return None


def pumpe(ms=150):
    app.pumpen(ms)


def maus(xk, yk):
    xtest.fake_input(anzeige, X.MotionNotify, x=xk, y=yk)
    anzeige.sync()
    pumpe(60)


def taste_druecken(keysym):
    code = anzeige.keysym_to_keycode(keysym)
    xtest.fake_input(anzeige, X.KeyPress, code)
    xtest.fake_input(anzeige, X.KeyRelease, code)
    anzeige.sync()
    pumpe(80)


def klick(knopf, mal=1):
    for _ in range(mal):
        xtest.fake_input(anzeige, X.ButtonPress, knopf)
        xtest.fake_input(anzeige, X.ButtonRelease, knopf)
        anzeige.sync()
        pumpe(40)


f = Probe(100, 100, 300, 200, titel="Probe")
f.zeige()
pumpe(300)
pruefe(f.sichtbar(), "Fenster nicht sichtbar")
pruefe(any(e[0] == "zeichnen" and e[1:] == (300, 200) for e in ereignisse), "zeichnen nicht mit 300x200 aufgerufen")
pruefe(f.rechteck() == (100, 100, 400, 300), f"rechteck {f.rechteck()}")
pruefe(f.hwnd and x.fenster_existiert(f.hwnd), "hwnd ist keine X-Kennung")
pruefe(x.fenster_rechteck(f.hwnd) == (100, 100, 400, 300), f"X-Rechteck {x.fenster_rechteck(f.hwnd)}")
pruefe(f.leinwand.bild.getpixel((10, 10)) == (200, 0, 0) and f.leinwand.bild.getpixel((50, 50)) == (10, 20, 30), "Leinwandpixel")

# Maus: Klick im Clientbereich (cy >= 12)
maus(150, 160)
ereignisse.clear()
klick(1)
pruefe(("runter", 50, 60, 1) in ereignisse and any(e[0] == "hoch" and e[1:3] == (50, 60) for e in ereignisse), f"Klick: {ereignisse}")
ereignisse.clear()
klick(1, 2)  # zweiter Klick schnell hinterher
pruefe(any(e[0] == "doppel" for e in ereignisse), f"Doppelklick: {ereignisse}")
time.sleep(0.6)
ereignisse.clear()
klick(3)
pruefe(("rechts", 50, 60) in ereignisse, f"Rechtsklick: {ereignisse}")
ereignisse.clear()
klick(4)
klick(5)
pruefe(("rad", 120, 150, 160) in ereignisse and ("rad", -120, 150, 160) in ereignisse, f"Rad (Bildschirmkoordinaten): {ereignisse}")

# Tasten: a, Enter, Pfeil
ereignisse.clear()
taste_druecken(XK.XK_a)
taste_druecken(XK.XK_Return)
taste_druecken(XK.XK_Left)
vks = [e[1] for e in ereignisse if e[0] == "taste"]
pruefe(0x41 in vks and 0x0D in vks and 0x25 in vks, f"Tasten {vks}")
pruefe(("zeichen", 97) in ereignisse and ("zeichen", 13) in ereignisse, f"Zeichen {ereignisse}")

# Verschieben über HTCAPTION: Zeile y < 12
maus(150, 105)
xtest.fake_input(anzeige, X.ButtonPress, 1)
anzeige.sync()
pumpe(40)
for schritt in range(1, 6):
    maus(150 + schritt * 20, 105 + schritt * 10)
xtest.fake_input(anzeige, X.ButtonRelease, 1)
anzeige.sync()
pumpe(120)
pruefe(f.rechteck()[:2] == (200, 150), f"Verschieben: {f.rechteck()}")

# Größe ändern über HTBOTTOMRIGHT (rechts unten 8 px)
links, oben, rechts, unten = f.rechteck()
maus(rechts - 3, unten - 3)
xtest.fake_input(anzeige, X.ButtonPress, 1)
anzeige.sync()
pumpe(40)
maus(rechts + 50, unten + 30)
maus(rechts + 100, unten + 60)
xtest.fake_input(anzeige, X.ButtonRelease, 1)
anzeige.sync()
pumpe(150)
pruefe(f.clientgroesse() == (403, 263), f"Größe ändern: {f.clientgroesse()}")  # 300+103, 200+63: Zug von (rechts-3, unten-3) nach (rechts+100, unten+60)
pruefe(f.leinwand.breite == 403 and f.leinwand.hoehe == 263, "Leinwand folgt der Größe")
# Mindestgröße
f.verschiebe(200, 150, 10, 10)
pumpe(200)
b, h = f.clientgroesse()
pruefe(b >= 60 and h >= 40, f"Mindestgröße ignoriert: {b}x{h}")
f.verschiebe(200, 150, 300, 200)
pumpe(150)

# Timer
zaehler = []
f.starte_timer(7, 30, lambda: zaehler.append(1))
pumpe(250)
f.stoppe_timer(7)
n = len(zaehler)
pumpe(120)
pruefe(n >= 3 and len(zaehler) == n, f"Timer: {n}/{len(zaehler)}")

# Fensterform und Durchklick
f.setze_form([(0, 0), (299, 0), (299, 199)])  # Dreieck
pumpe(100)
fenster_x = anzeige.create_resource_object("window", f.hwnd)
anzeige.sync()
rects = fenster_x.shape_get_rectangles(shape.SK.Bounding).rectangles
pruefe(len(rects) > 5 and max(r.width for r in rects) >= 290, f"Form: {len(rects)} Rechtecke")
f.setze_form(None)
f.durchklick_setzen(True)
pumpe(100)
eingabe = fenster_x.shape_get_rectangles(shape.SK.Input).rectangles
pruefe(len(eingabe) == 0, f"Durchklick: Eingabeform {len(eingabe)} Rechtecke")
f.durchklick_setzen(False)
pumpe(100)
pruefe(w.user32.GetWindowLongPtrW(f.hwnd, w.GWL_EXSTYLE) & w.WS_EX_TRANSPARENT == 0, "Stil nach Durchklick aus")

# Pixel-Alpha-Fenster ohne Compositor: Formmaske
p = PixelFenster(500, 100, 200, 100, titel="Pixel", durchklickbar=True)
bild = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
for yy in range(20, 60):
    for xx in range(30, 110):
        bild.putpixel((xx, yy), (255, 0, 0, 255))
pruefe(p.setze_rgba(bild) and p.angenommen, "PixelFenster nahm das Bild nicht an")
p.zeige(aktivieren=False)
pumpe(200)
px = anzeige.create_resource_object("window", p.hwnd)
rects = px.shape_get_rectangles(shape.SK.Bounding).rectangles
flaeche = sum(r.width * r.height for r in rects)
pruefe(abs(flaeche - 80 * 40) < 80 * 40 * 0.05, f"Formmaske {flaeche} statt {80 * 40}")
pruefe(len(px.shape_get_rectangles(shape.SK.Input).rectangles) == 0, "PixelFenster nicht durchklickbar")
halb = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
for yy in range(0, 100):
    for xx in range(0, 200):
        halb.putpixel((xx, yy), (0, 255, 0, 128))
p.setze_rgba(halb)
pumpe(150)
rects = px.shape_get_rectangles(shape.SK.Bounding).rectangles
flaeche = sum(r.width * r.height for r in rects)
pruefe(0.35 * 20000 < flaeche < 0.65 * 20000, f"halbdurchsichtig gerastert: {flaeche} von 20000")

# Schrift und Leinwand
s = Schrift(1, "Consolas", 16, fest=True)
pruefe(s.zellbreite > 4 and s.zellhoehe >= 14, f"Schrift {s.zellbreite}x{s.zellhoehe}")
pruefe(s.hat_glyphen(1, "A\U0001F600")[0] is True, "Glyphe A")
l = Leinwand(120, 40)
l.fuellen(w.rgb(0, 0, 0))
l.text(2, 2, "Hallo", w.rgb(255, 255, 255), s, zellbreite=s.zellbreite)
pruefe(sum(1 for px_ in l.bild.getdata() if px_ != (0, 0, 0)) > 50, "Text wurde nicht gezeichnet")
l.polygon([(10, 30), (30, 30), (20, 38)], w.rgb(255, 0, 0), w.rgb(255, 255, 0), 1)
pruefe(l.bild.getpixel((20, 33)) == (255, 0, 0), "Polygon")
l.bgr_zeichnen(bytes([255, 0, 0] * 4), 2, 2, 100, 10, 8, 8)
pruefe(l.bild.getpixel((103, 13)) == (0, 0, 255), "bgr_zeichnen (BGR -> RGB)")

# Menü und Zwischenablage
def waehle(menue_):
    from gi.repository import GLib
    from gi.repository import Gtk
    kinder = [k for k in menue_.get_children() if k.get_sensitive() and not isinstance(k, Gtk.SeparatorMenuItem)]
    GLib.timeout_add(120, lambda: (kinder[1].activate(), menue_.popdown(), False)[-1])

auswahl = menue.zeige_menue(f.hwnd, [(1, "Eins", 0), None, (2, "Zwei", w.MF_CHECKED), (3, "Drei", w.MF_GRAYED)], 300, 300, vorab=waehle)
pruefe(auswahl == 2, f"Menü lieferte {auswahl}")
abbruch = menue.zeige_menue(f.hwnd, [(1, "Eins", 0)], 300, 300, vorab=lambda m: __import__("gi.repository.GLib", fromlist=["GLib"]).timeout_add(100, lambda: (m.popdown(), False)[-1]))
pruefe(abbruch == 0, f"Abbruch lieferte {abbruch}")
pruefe(menue.text_in_zwischenablage(f.hwnd, "größe ändern ✓") and menue.text_aus_zwischenablage(f.hwnd) == "größe ändern ✓", "Zwischenablage")

# Tastenzustand
code = anzeige.keysym_to_keycode(XK.XK_Control_L)
xtest.fake_input(anzeige, X.KeyPress, code)
anzeige.sync()
pumpe(60)
pruefe(w.user32.GetKeyState(w.VK_CONTROL) & 0x8000, "Strg gehalten nicht erkannt")
xtest.fake_input(anzeige, X.KeyRelease, code)
anzeige.sync()
pumpe(60)
pruefe(not (w.user32.GetAsyncKeyState(w.VK_CONTROL) & 0x8000), "Strg losgelassen nicht erkannt")

# Globale Hotkeys: Strg+Alt+H und die einzelne Taste F11 (wie der Not-Aus F12), von jedem Fenster aus, auch ohne Fokus.
# (Strg+Alt+F1..F12 ist bei X-Servern das Umschalten der virtuellen Konsole und kommt bei keinem Programm an.)
getroffen = []
pruefe(app.hotkey_setzen("probe", w.MOD_CONTROL | w.MOD_ALT, 0x48, lambda: getroffen.append("strg-alt-h")), "Hotkey Strg+Alt+H nicht eintragbar")
pruefe(app.hotkey_setzen("einzeln", 0, 0x7A, lambda: getroffen.append("f11")), "Hotkey F11 nicht eintragbar")
for ks in (XK.XK_Control_L, XK.XK_Alt_L):
    xtest.fake_input(anzeige, X.KeyPress, anzeige.keysym_to_keycode(ks))
h = anzeige.keysym_to_keycode(XK.XK_h)
xtest.fake_input(anzeige, X.KeyPress, h)
xtest.fake_input(anzeige, X.KeyRelease, h)
for ks in (XK.XK_Alt_L, XK.XK_Control_L):
    xtest.fake_input(anzeige, X.KeyRelease, anzeige.keysym_to_keycode(ks))
f11 = anzeige.keysym_to_keycode(XK.XK_F11)
xtest.fake_input(anzeige, X.KeyPress, f11)
xtest.fake_input(anzeige, X.KeyRelease, f11)
anzeige.sync()
pumpe(400)
pruefe(getroffen == ["strg-alt-h", "f11"], f"Hotkeys {getroffen}")
# Ersetzen unter demselben Namen: die alte Kombination ist frei, die neue gilt
getroffen.clear()
pruefe(app.hotkey_setzen("einzeln", 0, 0x79, lambda: getroffen.append("f10")), "Hotkey F10 nicht eintragbar")
for kc in (anzeige.keysym_to_keycode(XK.XK_F11), anzeige.keysym_to_keycode(XK.XK_F10)):
    xtest.fake_input(anzeige, X.KeyPress, kc)
    xtest.fake_input(anzeige, X.KeyRelease, kc)
anzeige.sync()
pumpe(400)
pruefe(getroffen == ["f10"], f"Hotkey ersetzt: {getroffen}")
app.hotkey_loeschen("einzeln")
app.hotkey_loeschen("probe")

# Fenster schließen
f.schliessen()
pumpe(100)
pruefe(f.hwnd not in __import__("augen_haende_bridge.koerper.fenster_linux", fromlist=["x"])._fenster, "Fenster nicht abgemeldet")
p.schliessen()
app.beenden()
print("linux fenster probe ok")
