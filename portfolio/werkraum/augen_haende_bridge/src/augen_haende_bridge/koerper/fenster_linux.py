"""Fenstergerüst des Körpers für Linux: GTK 3 als Fensterschicht, Pillow als Zeichenfläche, python-xlib für alles, was GTK nicht kann.

Diese Datei hat dieselben Namen, Parameter und Wirkungen wie `fenster.py` (Win32/GDI): `Schrift`, `Leinwand`, `Fenster`, `Zentrale`,
`Anwendung`, `bild_ausnahme_setzen`, dazu `PixelFenster`. Die Fenster des Körpers (Raute, Terminal, Chat, Regie, Zeichnen …) laufen dadurch unverändert:
dieselbe Zeichenlogik auf der `Leinwand`, dieselben `bei_*`-Handler, dieselbe Treffertestung (`treffer` liefert Windows-Trefferwerte wie HTCAPTION).
Gewählt wird sie über `plattform.py` (BRIDGE_BACKEND=linux).

Unterschiede zu Windows, die der Körper wissen muss, und wie sie behandelt werden:
* Es gibt keine Nachrichten. Aus den GTK-Ereignissen werden die `bei_*`-Aufrufe gebildet; wenige Windows-Nachrichten, auf die Fenster hören
  (`WM_GETMINMAXINFO`, `WM_SETCURSOR`, `WM_MOVE`), werden an `bei_nachricht` nachgebildet.
* Verschieben (HTCAPTION) und Größenändern (HTLEFT … HTBOTTOMRIGHT) macht die Schicht selbst, so wie Windows es bei diesen Trefferwerten täte; das gilt
  auch ohne Fensterverwaltung.
* Deckkraft braucht einen Compositor; ohne ihn bleibt das Fenster undurchsichtig (`set_opacity` wird versucht). `PixelFenster` löst das mit einer Formmaske,
  halbdurchsichtiges wird gerastert (Dithering).
* Aus der Aufnahme ausnehmen kann erst der Linux-Adapter (er setzt `AUFNAHME_AUSNAHME_MOEGLICH`); bis dahin wird nur gemerkt und `False` gemeldet.
"""

from __future__ import annotations

import ctypes
import os
import queue
import subprocess
import threading
import time
from collections.abc import Callable
from typing import Any

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
try:
    gi.require_version("GdkX11", "3.0")
    from gi.repository import GdkX11  # noqa: F401  (macht Gdk.Window.get_xid verfügbar)
except (ValueError, ImportError):  # pragma: no cover
    GdkX11 = None
from gi.repository import Gdk, GLib, Gtk
from PIL import Image, ImageDraw, ImageFont

from . import tasten_x11 as t
from . import win32 as w

Gtk.init_check()

AUFNAHME_AUSNAHME_MOEGLICH = False  # setzt der Linux-Adapter, sobald seine Aufnahme die Fenster der Bridge wirklich auslässt
AUSGENOMMEN: set[int] = set()  # X-Kennungen der Fenster, die aus der Aufnahme bleiben sollen (liest der Adapter)
WM_AUH_POST = w.WM_APP + 1

# ---- Schrift -------------------------------------------------------------------------------------------------------------
_FAMILIEN = {
    "cascadia mono": "DejaVu Sans Mono", "consolas": "DejaVu Sans Mono", "courier new": "Liberation Mono",
    "segoe ui": "Noto Sans", "tahoma": "Liberation Sans", "arial": "Liberation Sans",
    "segoe ui symbol": "DejaVu Sans", "ms gothic": "Noto Sans CJK JP", "segoe ui emoji": "DejaVu Sans", "arial unicode ms": "Noto Sans",
}
SCHRIFT_ERSATZ_LINUX = ("DejaVu Sans", "Noto Sans CJK JP", "Noto Sans Symbols", "Noto Sans Symbols 2", "FreeSans")
_datei_cache: dict[tuple[str, bool], tuple[str, str]] = {}


def _schriftdatei(name: str, fett: bool) -> tuple[str, str]:
    """(Dateipfad, tatsächliche Familie) der Linux-Schrift, die für den Windows-Schriftnamen steht (Metrik- oder Charaktergleiche)."""
    schluessel = (name.lower(), fett)
    if schluessel not in _datei_cache:
        familie = _FAMILIEN.get(name.lower(), name)
        try:
            ausgabe = subprocess.run(["fc-match", "-f", "%{file}|%{family}", familie + (":bold" if fett else "")],
                                     capture_output=True, text=True, timeout=5).stdout
            pfad, _, tatsaechlich = ausgabe.partition("|")
        except (OSError, subprocess.SubprocessError):
            pfad, tatsaechlich = "", ""
        _datei_cache[schluessel] = (pfad.strip(), tatsaechlich.split(",")[0].strip())
    return _datei_cache[schluessel]


class Schrift:
    """Eine Schrift mit gemessener Zellgröße (für Zeichengitter) oder Zeilenhöhe (für Text); `hdc` wird nur der Form halber angenommen."""

    def __init__(self, hdc, name: str, hoehe_px: int, *, fett: bool = False, fest: bool = True):
        self.name = name
        pfad, self.tatsaechlich = _schriftdatei(name, fett)
        groesse = max(4, abs(int(hoehe_px)))
        try:
            self._font = ImageFont.truetype(pfad, groesse) if pfad else ImageFont.load_default(size=groesse)
        except OSError:
            self._font = ImageFont.load_default(size=groesse)
        ascent, descent = self._font.getmetrics()
        self.ascent = ascent
        self.zellhoehe = max(1, ascent + descent)
        if fest:
            self.zellbreite = max(1, round(self._font.getlength("0")))
        else:
            self.zellbreite = max(1, round(self._font.getlength("abcdefghijklmnopqrstuvwxyz") / 26))
        self._leer: dict[int, bytes] = {}
        self._ersatz_fonts: list | None = None
        self._font_fuer: dict[str, Any] = {}
        self._groesse = groesse
        self._fett = fett
        self.handle = 1

    def _hat(self, font, zeichen: str) -> bool:
        """Besitzt diese Schrift ein Glyph für das Zeichen (statt des Ersatzkästchens, das sie für Unbekanntes malt)?"""
        schluessel = id(font)
        if schluessel not in self._leer:
            self._leer[schluessel] = bytes(font.getmask("\uffff"))
        maske = bytes(font.getmask(zeichen))
        return not (len(maske) > 0 and maske == self._leer[schluessel])

    def _ersatz(self) -> list:
        """Die Schriften, die einspringen, wenn die eigene ein Zeichen nicht kennt (wie die Schriftverknüpfung unter Windows)."""
        if self._ersatz_fonts is None:
            self._ersatz_fonts = []
            for familie in SCHRIFT_ERSATZ_LINUX:
                pfad, _ = _schriftdatei(familie, self._fett)
                try:
                    if pfad:
                        self._ersatz_fonts.append(ImageFont.truetype(pfad, self._groesse))
                except OSError:
                    continue
        return self._ersatz_fonts

    def font_fuer(self, zeichen: str):
        """Die Schrift, die dieses Zeichen darstellt: die eigene, sonst die erste Ersatzschrift mit Glyph, sonst die eigene (Kästchen)."""
        font = self._font_fuer.get(zeichen)
        if font is None:
            font = self._font
            if ord(zeichen) > 0x7E and not self._hat(self._font, zeichen):
                for ersatz in self._ersatz():
                    if self._hat(ersatz, zeichen):
                        font = ersatz
                        break
            self._font_fuer[zeichen] = font
        return font

    def hat_glyphen(self, hdc, zeichen: str) -> list[bool]:
        """Für jedes Zeichen: besitzt diese Schrift ein Glyph dafür (statt des Ersatzkästchens)?"""
        if self._leer is None:
            self._leer = bytes(self._font.getmask("￿"))
        antwort = []
        for z in zeichen:
            maske = self._font.getmask(z)
            antwort.append(not (len(bytes(maske)) > 0 and bytes(maske) == self._leer))
        return antwort

    def breite(self, hdc, text: str) -> int:
        if not text:
            return 0
        if all(ord(z) <= 0x7E for z in text):
            return int(round(self._font.getlength(text)))
        return int(round(sum(self.font_fuer(z).getlength(z) for z in text)))

    def freigeben(self) -> None:
        self.handle = None


def _rgb(farbe: int) -> tuple[int, int, int]:
    """COLORREF (0x00BBGGRR) in (R, G, B)."""
    return farbe & 0xFF, (farbe >> 8) & 0xFF, (farbe >> 16) & 0xFF


class Leinwand:
    """Hintergrundpuffer (RGB), auf den ein Fenster zeichnet und der dann in das Fenster kopiert wird. Farben sind COLORREF wie unter Windows."""

    def __init__(self, breite: int, hoehe: int):
        self.breite, self.hoehe = max(1, breite), max(1, hoehe)
        self.bild = Image.new("RGB", (self.breite, self.hoehe), (0, 0, 0))
        self._z = ImageDraw.Draw(self.bild)
        self.hdc = 1

    def bgr_zeichnen(self, bgr: bytes, bild_b: int, bild_h: int, x: int, y: int, breite: int, hoehe: int, *, spiegeln: bool = False) -> bool:
        if breite < 1 or hoehe < 1 or bild_b < 1 or bild_h < 1 or len(bgr) < bild_b * bild_h * 3:
            return False
        quelle = Image.frombuffer("RGB", (bild_b, bild_h), bgr, "raw", "BGR", 0, 1)
        if (bild_b, bild_h) != (breite, hoehe):
            quelle = quelle.resize((breite, hoehe), Image.BILINEAR)
        if spiegeln:
            quelle = quelle.transpose(Image.FLIP_LEFT_RIGHT)
        self.bild.paste(quelle, (x, y))
        return True

    def fuellen(self, farbe: int, links: int = 0, oben: int = 0, rechts: int | None = None, unten: int | None = None) -> None:
        rechts = self.breite if rechts is None else rechts
        unten = self.hoehe if unten is None else unten
        if rechts <= links or unten <= oben:
            return
        self._z.rectangle((links, oben, rechts - 1, unten - 1), fill=_rgb(farbe))

    def text(self, x: int, y: int, text: str, farbe: int, schrift: Schrift, *, hintergrund: int | None = None,
             zellbreite: int | None = None, breiten: list[int] | None = None) -> None:
        """Text ab (x, y). Mit `zellbreite` bekommt jedes Zeichen genau diese Breite (Zeichengitter), mit `breiten` je Zeichen eine eigene."""
        if not text:
            return
        abstaende = breiten if breiten is not None else ([zellbreite] * len(text) if zellbreite else None)
        if hintergrund is not None:
            breite = sum(abstaende) if abstaende else schrift.breite(self.hdc, text)
            self._z.rectangle((x, y, x + breite - 1, y + schrift.zellhoehe - 1), fill=_rgb(hintergrund))
        vordergrund = _rgb(farbe)
        if abstaende is None:
            if all(ord(z) <= 0x7E for z in text):
                self._z.text((x, y), text, fill=vordergrund, font=schrift._font, anchor="la")
                return
            laufend = float(x)
            for zeichen in text:  # einzelne Zeichen aus Ersatzschriften (Pfeile, Symbole, Kästchen) mit deren eigener Breite
                font = schrift.font_fuer(zeichen)
                if zeichen != " ":
                    self._z.text((round(laufend), y), zeichen, fill=vordergrund, font=font, anchor="la")
                laufend += font.getlength(zeichen)
            return
        laufend = x
        for zeichen, schritt in zip(text, abstaende):
            if zeichen != " ":
                self._z.text((laufend, y), zeichen, fill=vordergrund, font=schrift.font_fuer(zeichen), anchor="la")
            laufend += schritt

    def polygon(self, punkte: list[tuple[int, int]], fuellfarbe: int, randfarbe: int | None = None, randbreite: int = 1) -> None:
        if len(punkte) < 3:
            return
        self._z.polygon(punkte, fill=_rgb(fuellfarbe), outline=_rgb(randfarbe) if randfarbe is not None else None,
                        width=randbreite if randfarbe is not None else 1)

    def linie(self, x1: int, y1: int, x2: int, y2: int, farbe: int, breite: int = 1) -> None:
        self._z.line([(x1, y1), (x2, y2)], fill=_rgb(farbe), width=max(1, breite))

    def rahmen(self, links: int, oben: int, rechts: int, unten: int, farbe: int, breite: int = 1) -> None:
        for i in range(breite):
            self.fuellen(farbe, links + i, oben + i, rechts - i, oben + i + 1)
            self.fuellen(farbe, links + i, unten - i - 1, rechts - i, unten - i)
            self.fuellen(farbe, links + i, oben + i, links + i + 1, unten - i)
            self.fuellen(farbe, rechts - i - 1, oben + i, rechts - i, unten - i)

    def auf(self, hdc, x: int = 0, y: int = 0) -> None:
        """Auf das Ziel kopieren; `hdc` ist hier der Cairo-Kontext des Fensters (unter Windows der Gerätekontext). Entspricht dem BitBlt."""
        daten = bytearray(self.bild.tobytes("raw", "BGRX"))
        flaeche = cairo.ImageSurface.create_for_data(daten, cairo.FORMAT_RGB24, self.breite, self.hoehe, self.breite * 4)
        hdc.set_source_surface(flaeche, x, y)
        hdc.paint()

    def bgra(self) -> bytes:
        rgba = self.bild.convert("RGBA")
        r, g, b, a = rgba.split()
        return Image.merge("RGBA", (b, g, r, a)).tobytes()

    def freigeben(self) -> None:
        pass


# ---- Fenster -------------------------------------------------------------------------------------------------------------
_fenster: dict[int, "Fenster"] = {}
_aus_dem_bild = False


def bild_ausnahme_setzen(ausnehmen: bool) -> int:
    """Alle Fenster der Bridge aus der Bildschirmaufnahme ausnehmen oder wieder aufnehmen lassen. Liefert, bei wie vielen es angenommen wurde."""
    global _aus_dem_bild
    _aus_dem_bild = ausnehmen
    return sum(1 for f in list(_fenster.values()) if f.aufnahme_ausnehmen(ausnehmen))


_CURSOR_IDC = {w.IDC_ARROW: "default", w.IDC_IBEAM: "text", w.IDC_HAND: "pointer", w.IDC_SIZEALL: "move"}
_CURSOR_HT = {w.HTLEFT: "ew-resize", w.HTRIGHT: "ew-resize", w.HTTOP: "ns-resize", w.HTBOTTOM: "ns-resize",
              w.HTTOPLEFT: "nwse-resize", w.HTBOTTOMRIGHT: "nwse-resize", w.HTTOPRIGHT: "nesw-resize", w.HTBOTTOMLEFT: "nesw-resize"}
_RAND_HT = (w.HTLEFT, w.HTRIGHT, w.HTTOP, w.HTBOTTOM, w.HTTOPLEFT, w.HTTOPRIGHT, w.HTBOTTOMLEFT, w.HTBOTTOMRIGHT)
MK_LBUTTON, MK_RBUTTON, MK_SHIFT, MK_CONTROL = 0x1, 0x2, 0x4, 0x8
GEO_WARTEN_S = 0.6  # so lange gilt eine eigene Lage-/Größenanforderung, bevor die Meldungen des Servers wieder maßgeblich sind
_EREIGNISSE = (Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK
               | Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK
               | Gdk.EventMask.FOCUS_CHANGE_MASK | Gdk.EventMask.STRUCTURE_MASK | Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)


def _flags(zustand: Gdk.ModifierType) -> int:
    flags = 0
    if zustand & Gdk.ModifierType.BUTTON1_MASK:
        flags |= MK_LBUTTON
    if zustand & Gdk.ModifierType.BUTTON3_MASK:
        flags |= MK_RBUTTON
    if zustand & Gdk.ModifierType.SHIFT_MASK:
        flags |= MK_SHIFT
    if zustand & Gdk.ModifierType.CONTROL_MASK:
        flags |= MK_CONTROL
    return flags


def rechtecke_aus_maske(maske) -> list[tuple[int, int, int, int]]:
    """Eine Wahrheitsmaske (Zeilen von oben nach unten) als möglichst wenige Rechtecke (x, y, Breite, Höhe): waagerechte Läufe, gleiche Läufe
    übereinanderliegender Zeilen werden zu einem hohen Rechteck."""
    import numpy as np

    hoehe, _breite = maske.shape
    ergebnis: list[tuple[int, int, int, int]] = []
    offen: dict[tuple[int, int], int] = {}  # (x, Breite) -> Zeile, in der der Lauf begann
    for y in range(hoehe + 1):
        laeufe: set[tuple[int, int]] = set()
        if y < hoehe:
            zeile = np.concatenate(([False], maske[y], [False]))
            wechsel = np.flatnonzero(zeile[1:] != zeile[:-1])
            laeufe = {(int(a), int(b - a)) for a, b in zip(wechsel[0::2], wechsel[1::2])}
        for lauf in [k for k in offen if k not in laeufe]:
            start = offen.pop(lauf)
            ergebnis.append((lauf[0], start, lauf[1], y - start))
        for lauf in laeufe:
            offen.setdefault(lauf, y)
    return ergebnis


def _x_form_setzen(xid: int, rechtecke: list[tuple[int, int, int, int]] | None, art: str = "bounding") -> None:
    """Setzt (oder löscht mit None) die Fensterform per XShape. GDK setzt die Begrenzungsform bei Toplevels nicht durch, darum direkt."""
    from Xlib import X
    from Xlib.ext import shape

    from . import x11_helfer as xh

    anzeige = xh.anzeige()
    fenster = anzeige.create_resource_object("window", int(xid))
    ziel = shape.SK.Bounding if art == "bounding" else shape.SK.Input
    if rechtecke is None:
        fenster.shape_mask(shape.SO.Set, ziel, 0, 0, X.NONE)
    else:
        erste = True
        for i in range(0, max(1, len(rechtecke)), 16000):  # eine Anfrage fasst nur begrenzt viele Rechtecke
            fenster.shape_rectangles(shape.SO.Set if erste else shape.SO.Union, ziel, X.Unsorted, 0, 0, rechtecke[i:i + 16000])
            erste = False
    anzeige.sync()


class Fenster:
    """Basis aller Fenster des Körpers. Unterklassen überschreiben `zeichnen` und die `bei_*`-Handler."""

    klasse = "AuHFenster"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW
    klassenstil = w.CS_DBLCLKS
    fokus_weg = ""

    def __init__(self, x: int, y: int, breite: int, hoehe: int, *, titel: str = "", deckkraft: int | None = None,
                 durchklickbar: bool = False, nicht_aktivieren: bool = False):
        self.hwnd: int | None = None
        self.titel = titel
        self.breite, self.hoehe = breite, hoehe
        self.deckkraft = deckkraft
        self.leinwand: Leinwand | None = None
        self._timer: dict[int, int] = {}
        self._timer_aufruf: dict[int, Callable[[], None]] = {}
        self._exstil = self.exstil | (w.WS_EX_LAYERED if deckkraft is not None else 0) | (w.WS_EX_NOACTIVATE if nicht_aktivieren else 0)
        if durchklickbar:
            self._exstil |= w.WS_EX_TRANSPARENT | w.WS_EX_LAYERED
        self._nicht_aktivieren = nicht_aktivieren
        self._aktion: dict[str, Any] | None = None  # laufendes Verschieben oder Größenändern: Art, Startpunkt, Ausgangsrechteck
        self._erfasst = False
        self._letzter_klick: tuple[float, float, float] | None = None  # Zeit, x, y des letzten Linksklicks (Doppelklick-Erkennung)
        self._min_groesse = (1, 1)
        self._position = (x, y)
        self._geo = (int(x), int(y), max(1, int(breite)), max(1, int(hoehe)))  # maßgebliche Lage und Größe: GTK setzt Verschieben und Größenändern erst später um
        self._geo_bis: float = 0.0  # bis wann eine eigene Anforderung gilt (die Konfigurationsmeldungen des Servers dürfen sie bis dahin nicht überschreiben)
        self._form_bounding: list | None = None  # gesetzte Fensterform (Rechtecke) oder None
        self._form_eingabe: list | None = None  # gesetzte Eingabeform: [] = nichts nimmt Klicks an (durchklickbar), None = ganz normal
        self._ausgenommen = False
        self._zerstoert = False
        win = self._win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        win.set_title(titel)
        win.set_decorated(False)
        win.set_skip_taskbar_hint(bool(self._exstil & w.WS_EX_TOOLWINDOW))
        win.set_skip_pager_hint(bool(self._exstil & w.WS_EX_TOOLWINDOW))
        win.set_keep_above(bool(self._exstil & w.WS_EX_TOPMOST))
        win.set_accept_focus(not nicht_aktivieren)
        win.set_focus_on_map(not nicht_aktivieren)
        win.set_default_size(max(1, breite), max(1, hoehe))
        win.set_app_paintable(True)
        win.set_can_focus(True)
        win.add_events(_EREIGNISSE)
        win.move(x, y)
        win.connect("draw", self._bei_draw)
        win.connect("configure-event", self._bei_configure)
        win.connect("button-press-event", self._bei_maus_runter)
        win.connect("button-release-event", self._bei_maus_hoch)
        win.connect("motion-notify-event", self._bei_maus_bewegt)
        win.connect("scroll-event", self._bei_rad)
        win.connect("key-press-event", self._bei_taste)
        win.connect("focus-in-event", lambda *_a: self._fokus(True))
        win.connect("focus-out-event", lambda *_a: self._fokus(False))
        win.connect("grab-broken-event", lambda *_a: self._grab_verloren())
        win.connect("map-event", lambda *_a: self._formen_anwenden() or False)
        win.connect("destroy", self._bei_destroy)
        win.realize()
        gdkfenster = win.get_window()
        self.hwnd = int(gdkfenster.get_xid()) if hasattr(gdkfenster, "get_xid") else id(win)
        _fenster[self.hwnd] = self
        self._min_groesse_lesen()
        self.leinwand_anpassen()
        if _aus_dem_bild:
            self.aufnahme_ausnehmen(True)
        if deckkraft is not None or durchklickbar:
            self.setze_deckkraft(255 if deckkraft is None else deckkraft)
        if durchklickbar:
            self.durchklick_setzen(True)

    # ---- Zustand ----------------------------------------------------------------------------------------------------
    def aufnahme_ausnehmen(self, ausnehmen: bool) -> bool:
        """Merkt die Ausnahme für die Aufnahme des Linux-Adapters. Meldet nur dann True, wenn dieser sie wirklich umsetzt."""
        self._ausgenommen = ausnehmen
        if self.hwnd:
            (AUSGENOMMEN.add if ausnehmen else AUSGENOMMEN.discard)(self.hwnd)
        return AUFNAHME_AUSNAHME_MOEGLICH

    def rechteck(self) -> tuple[int, int, int, int]:
        x, y, breite, hoehe = self._geo
        return x, y, x + breite, y + hoehe

    def clientgroesse(self) -> tuple[int, int]:
        return self._geo[2], self._geo[3]

    def leinwand_anpassen(self) -> None:
        breite, hoehe = self.clientgroesse()
        if breite <= 0 or hoehe <= 0:
            return
        if self.leinwand is None or (self.leinwand.breite, self.leinwand.hoehe) != (breite, hoehe):
            self.leinwand = Leinwand(breite, hoehe)

    def setze_deckkraft(self, alpha: int) -> None:
        self.deckkraft = max(0, min(255, int(alpha)))
        self._win.set_opacity(self.deckkraft / 255.0)  # wirkt nur mit Compositor

    def deckkraft_lesen(self) -> int | None:
        return self.deckkraft

    def setze_form(self, punkte: list[tuple[int, int]] | None) -> None:
        """Fensterform aus einem Polygon in Fensterkoordinaten; None entfernt die Form."""
        if not self.hwnd:
            return
        if punkte is None:
            self._form_bounding = None
            _x_form_setzen(self.hwnd, None)
            return
        import numpy as np

        breite, hoehe = self.clientgroesse()
        maske = Image.new("L", (max(1, breite), max(1, hoehe)), 0)
        ImageDraw.Draw(maske).polygon(punkte, fill=255)
        self._form_bounding = rechtecke_aus_maske(np.asarray(maske) > 0)
        _x_form_setzen(self.hwnd, self._form_bounding)

    def _formen_anwenden(self) -> None:
        """GDK setzt Form und Eingabeform eines Fensters beim Einblenden und bei Größenänderungen zurück: die gemerkten Formen werden dann erneut gesetzt."""
        if not self.hwnd or self._zerstoert:
            return
        if self._form_bounding is not None:
            _x_form_setzen(self.hwnd, self._form_bounding)
        if self._form_eingabe is not None:
            _x_form_setzen(self.hwnd, self._form_eingabe, "input")

    def verschiebe(self, x: int, y: int, breite: int | None = None, hoehe: int | None = None) -> None:
        if breite is None or hoehe is None:
            links, oben, rechts, unten = self.rechteck()
            breite = rechts - links if breite is None else breite
            hoehe = unten - oben if hoehe is None else hoehe
        breite, hoehe = max(1, int(breite), self._min_groesse[0]), max(1, int(hoehe), self._min_groesse[1])  # wie bei Windows: nie kleiner als die Mindestgröße
        self._geo = (int(x), int(y), breite, hoehe)
        self._geo_bis = time.monotonic() + GEO_WARTEN_S
        self._win.move(int(x), int(y))
        self._win.resize(breite, hoehe)
        self._position = (int(x), int(y))
        self.leinwand_anpassen()

    def fokus_erzwingen(self) -> bool:
        """Dieses Fenster nach vorn und mit der Tastatur. Liefert, ob es danach den Fokus hat; `fokus_weg` nennt den Weg."""
        self.fokus_weg = ""
        if self._win.has_toplevel_focus():
            self.fokus_weg = "schon vorn"
            return True
        self._win.present_with_time(Gdk.CURRENT_TIME)
        gdkfenster = self._win.get_window()
        if gdkfenster is not None:
            gdkfenster.focus(Gdk.CURRENT_TIME)
        self.fokus_weg = "present"  # die Übernahme des Fokus ist unter X11 asynchron; wer wissen will, ob es geklappt hat, fragt nach (nie die Schleife hier anhalten)
        return self._win.has_toplevel_focus()

    def durchklick_setzen(self, an: bool) -> None:
        """Klicks fallen durch das Fenster (an) oder werden von ihm angenommen (aus)."""
        if an:
            self._exstil |= w.WS_EX_TRANSPARENT
        else:
            self._exstil &= ~w.WS_EX_TRANSPARENT
        self._form_eingabe = [] if an else None  # leere Eingabeform: alle Klicks gehen an das Fenster darunter
        if self.hwnd:
            _x_form_setzen(self.hwnd, self._form_eingabe, "input")

    def oben(self) -> None:
        gdkfenster = self._win.get_window()
        if gdkfenster is not None:
            gdkfenster.raise_()

    def zeige(self, aktivieren: bool = True) -> None:
        self._win.set_focus_on_map(aktivieren and not self._nicht_aktivieren)
        self._win.show()
        gdkfenster = self._win.get_window()
        if gdkfenster is not None:
            gdkfenster.raise_()
        self.neu_zeichnen()

    def verberge(self) -> None:
        self._win.hide()

    def sichtbar(self) -> bool:
        return bool(self._win.get_mapped())

    def neu_zeichnen(self) -> None:
        self._win.queue_draw()

    def mauszeiger(self, art: int | str) -> None:
        name = art if isinstance(art, str) else _CURSOR_IDC.get(art, "default")
        gdkfenster = self._win.get_window()
        if gdkfenster is not None:
            gdkfenster.set_cursor(Gdk.Cursor.new_from_name(Gdk.Display.get_default(), name))

    def erfasse_maus(self) -> None:
        self._erfasst = True  # GTK hält die Maus nach einem Klick ohnehin fest, bis die Taste losgelassen wird

    def gib_maus_frei(self) -> None:
        if self._erfasst:
            self._erfasst = False
            self.bei_maus_verloren()

    def starte_timer(self, ident: int, ms: int, aufruf: Callable[[], None] | None = None) -> None:
        self._timer_stoppen(ident, behalte_aufruf=aufruf is None)
        if aufruf is not None:
            self._timer_aufruf[ident] = aufruf

        def tick() -> bool:
            if self._zerstoert:
                return False
            try:
                auf = self._timer_aufruf.get(ident)
                if auf is not None:
                    auf()
                else:
                    self.bei_timer(ident)
            except Exception as fehler:
                Anwendung.fehler("timer", fehler)
            return True

        self._timer[ident] = GLib.timeout_add(max(1, int(ms)), tick)

    def _timer_stoppen(self, ident: int, behalte_aufruf: bool) -> None:
        quelle = self._timer.pop(ident, None)
        if quelle is not None:
            GLib.source_remove(quelle)
        if not behalte_aufruf:
            self._timer_aufruf.pop(ident, None)

    def stoppe_timer(self, ident: int) -> None:
        self._timer_stoppen(ident, behalte_aufruf=False)

    def schliessen(self) -> None:
        if not self._zerstoert:
            self._win.destroy()

    def maus_position(self) -> tuple[int, int]:
        seat = Gdk.Display.get_default().get_default_seat()
        _bildschirm, x, y = seat.get_pointer().get_position()
        return x, y

    # ---- Gleichwertigkeit mit der Nachrichtenverteilung --------------------------------------------------------------
    def nachricht(self, msg: int, wparam: int, lparam: int) -> int | None:
        """Nur zur Gleichheit der Schnittstelle: Tests und Fenster dürfen Nachrichten einspeisen; die wichtigsten werden hier verteilt."""
        if msg == w.WM_LBUTTONDOWN:
            return self.bei_maus_runter(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_LBUTTONUP:
            return self.bei_maus_hoch(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_LBUTTONDBLCLK:
            return self.bei_doppelklick(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_RBUTTONUP:
            return self.bei_rechtsklick(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_MOUSEMOVE:
            return self.bei_maus_bewegt(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg in (w.WM_KEYDOWN, w.WM_SYSKEYDOWN):
            return self.bei_taste(wparam, lparam, msg == w.WM_SYSKEYDOWN)
        if msg in (w.WM_CHAR, w.WM_SYSCHAR):
            return self.bei_zeichen(wparam, msg == w.WM_SYSCHAR)
        if msg == w.WM_TIMER:
            auf = self._timer_aufruf.get(wparam)
            if auf is not None:
                auf()
            else:
                self.bei_timer(wparam)
            return 0
        return self.bei_nachricht(msg, wparam, lparam)

    # ---- GTK-Ereignisse -> bei_*-Aufrufe -----------------------------------------------------------------------------
    def _sicher(self, aufruf, *args):
        try:
            return aufruf(*args)
        except Exception as fehler:  # ein Handler darf die Schleife nie beenden
            Anwendung.fehler("fenster", fehler)
            return None

    def _bei_draw(self, _widget, cr) -> bool:
        self.leinwand_anpassen()
        if self.leinwand is not None:
            self._sicher(self.zeichnen, self.leinwand)
            self.leinwand.auf(cr)
        return True

    def _bei_configure(self, _widget, ereignis) -> bool:
        neue_pos = (int(ereignis.x), int(ereignis.y))
        gemeldet = (neue_pos[0], neue_pos[1], int(ereignis.width), int(ereignis.height))
        if time.monotonic() >= self._geo_bis or gemeldet == self._geo:
            self._geo, self._geo_bis = gemeldet, 0.0  # der Server hat die Anforderung umgesetzt (oder sie ist verfallen): ab jetzt gilt, was er meldet
        self.leinwand_anpassen()
        self._formen_anwenden()
        self._sicher(self.bei_groesse, *self.clientgroesse())
        if neue_pos != self._position:
            self._position = neue_pos
            self._sicher(self.bei_nachricht, w.WM_MOVE, 0, w.make_lparam(*neue_pos))
        self._min_groesse_lesen()
        return False

    def _min_groesse_lesen(self) -> None:
        """Fragt wie Windows per WM_GETMINMAXINFO nach der kleinsten Größe und gibt sie dem Fenster als Hinweis."""
        info = w.MINMAXINFO()
        info.ptMinTrackSize.x = info.ptMinTrackSize.y = 0
        antwort = self._sicher(self.bei_nachricht, w.WM_GETMINMAXINFO, 0, ctypes.addressof(info))
        mb, mh = int(info.ptMinTrackSize.x), int(info.ptMinTrackSize.y)
        if antwort is not None and (mb > 0 or mh > 0) and (mb, mh) != self._min_groesse:
            self._min_groesse = (max(1, mb), max(1, mh))
            geo = Gdk.Geometry()
            geo.min_width, geo.min_height = self._min_groesse
            self._win.set_geometry_hints(None, geo, Gdk.WindowHints.MIN_SIZE)

    def _treffer(self, rx: float, ry: float) -> int:
        antwort = self._sicher(self.treffer, int(rx), int(ry))
        return w.HTCLIENT if antwort is None else int(antwort)

    def _bei_maus_runter(self, _widget, ereignis) -> bool:
        if ereignis.type != Gdk.EventType.BUTTON_PRESS:
            return True  # 2BUTTON_PRESS/3BUTTON_PRESS ersetzt unsere eigene Doppelklick-Erkennung (Windows liefert den zweiten Klick als Doppelklick)
        if ereignis.button == 1:
            ht = self._treffer(ereignis.x_root, ereignis.y_root)
            if ht == w.HTCAPTION or ht in _RAND_HT:
                self._aktion = {"ht": ht, "start": (ereignis.x_root, ereignis.y_root), "rechteck": self.rechteck()}
                return True
            jetzt = time.monotonic()
            frueher = self._letzter_klick
            einstellungen = Gtk.Settings.get_default()
            zeit = einstellungen.get_property("gtk-double-click-time") / 1000.0
            abstand = einstellungen.get_property("gtk-double-click-distance")
            if frueher and jetzt - frueher[0] <= zeit and abs(ereignis.x - frueher[1]) <= abstand and abs(ereignis.y - frueher[2]) <= abstand:
                self._letzter_klick = None
                self._sicher(self.bei_doppelklick, int(ereignis.x), int(ereignis.y), _flags(ereignis.state) | MK_LBUTTON)
            else:
                self._letzter_klick = (jetzt, ereignis.x, ereignis.y)
                self._sicher(self.bei_maus_runter, int(ereignis.x), int(ereignis.y), _flags(ereignis.state) | MK_LBUTTON)
        return True

    def _bei_maus_hoch(self, _widget, ereignis) -> bool:
        if ereignis.button == 1:
            if self._aktion is not None:
                self._aktion = None
                return True
            self._sicher(self.bei_maus_hoch, int(ereignis.x), int(ereignis.y), _flags(ereignis.state) & ~MK_LBUTTON)
        elif ereignis.button == 3:
            if self._treffer(ereignis.x_root, ereignis.y_root) == w.HTCLIENT:
                self._sicher(self.bei_rechtsklick, int(ereignis.x), int(ereignis.y), _flags(ereignis.state))
        return True

    def _bei_maus_bewegt(self, _widget, ereignis) -> bool:
        if self._aktion is not None:
            self._ziehen_aktion(ereignis.x_root, ereignis.y_root)
            return True
        ht = self._treffer(ereignis.x_root, ereignis.y_root)
        if ht in _CURSOR_HT:
            self.mauszeiger(_CURSOR_HT[ht])
        else:
            if ht == w.HTCAPTION:
                self.mauszeiger(w.IDC_ARROW)
            else:  # wie WM_SETCURSOR: das Fenster darf den Zeiger bestimmen, sonst Pfeil
                if not self._sicher(self.bei_nachricht, w.WM_SETCURSOR, self.hwnd or 0, w.make_lparam(w.HTCLIENT, w.WM_MOUSEMOVE)):
                    self.mauszeiger(w.IDC_ARROW)
            self._sicher(self.bei_maus_bewegt, int(ereignis.x), int(ereignis.y), _flags(ereignis.state))
        return True

    def _ziehen_aktion(self, rx: float, ry: float) -> None:  # nicht „_ziehen“: Raute und Terminal führen ein eigenes Bool-Attribut dieses Namens
        a = self._aktion
        dx, dy = int(rx - a["start"][0]), int(ry - a["start"][1])
        l, o, r, u = a["rechteck"]
        ht = a["ht"]
        if ht == w.HTCAPTION:
            self._geo = (l + dx, o + dy, r - l, u - o)
            self._geo_bis = time.monotonic() + GEO_WARTEN_S
            self._win.move(l + dx, o + dy)
            return
        self._geo_bis = time.monotonic() + GEO_WARTEN_S
        mb, mh = self._min_groesse
        if ht in (w.HTLEFT, w.HTTOPLEFT, w.HTBOTTOMLEFT):
            l = min(l + dx, r - mb)
        if ht in (w.HTRIGHT, w.HTTOPRIGHT, w.HTBOTTOMRIGHT):
            r = max(r + dx, l + mb)
        if ht in (w.HTTOP, w.HTTOPLEFT, w.HTTOPRIGHT):
            o = min(o + dy, u - mh)
        if ht in (w.HTBOTTOM, w.HTBOTTOMLEFT, w.HTBOTTOMRIGHT):
            u = max(u + dy, o + mh)
        self._geo = (l, o, max(1, r - l), max(1, u - o))
        self._win.move(l, o)
        self._win.resize(max(1, r - l), max(1, u - o))
        self.leinwand_anpassen()

    def _bei_rad(self, _widget, ereignis) -> bool:
        if ereignis.direction == Gdk.ScrollDirection.UP:
            delta = 120
        elif ereignis.direction == Gdk.ScrollDirection.DOWN:
            delta = -120
        elif ereignis.direction == Gdk.ScrollDirection.SMOOTH:
            delta = -int(round(ereignis.delta_y * 120))
        else:
            return True
        if delta:
            self._sicher(self.bei_rad, delta, int(ereignis.x_root), int(ereignis.y_root), _flags(ereignis.state))
        return True

    def _vk(self, ereignis) -> int:
        keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
        ok, keyval, *_ = keymap.translate_keyboard_state(ereignis.hardware_keycode, Gdk.ModifierType(0), ereignis.group)
        vk = t.vk_aus_keysym(keyval if ok else ereignis.keyval)
        return vk or t.vk_aus_keysym(ereignis.keyval)

    def _bei_taste(self, _widget, ereignis) -> bool:
        vk = self._vk(ereignis)
        alt = bool(ereignis.state & Gdk.ModifierType.MOD1_MASK) or vk == w.VK_MENU
        if vk:
            self._sicher(self.bei_taste, vk, 0, alt)
        zeichen = ereignis.string
        if not zeichen and vk == w.VK_RETURN:
            zeichen = "\r"
        if not zeichen and not (ereignis.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)):
            unicode_zeichen = Gdk.keyval_to_unicode(ereignis.keyval)  # Zeichen jenseits von Latin-1 liefert GDK nicht im String-Feld
            zeichen = chr(unicode_zeichen) if unicode_zeichen else ""
        for z in zeichen or "":
            self._sicher(self.bei_zeichen, ord(z), alt)
        return True

    def _fokus(self, hat: bool) -> bool:
        self._sicher(self.bei_fokus, hat)
        return False

    def _grab_verloren(self) -> bool:
        self._erfasst = False
        self._sicher(self.bei_maus_verloren)
        return False

    def _bei_destroy(self, _widget) -> None:
        self._zerstoert = True
        for quelle in list(self._timer.values()):
            GLib.source_remove(quelle)
        self._timer.clear()
        self._sicher(self.bei_zerstoert)
        if self.leinwand is not None:
            self.leinwand.freigeben()
            self.leinwand = None
        if self.hwnd:
            _fenster.pop(self.hwnd, None)
            AUSGENOMMEN.discard(self.hwnd)

    # ---- Überschreibbare Handler -------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        leinwand.fuellen(0)

    def treffer(self, x: int, y: int) -> int | None:
        return None

    def bei_groesse(self, breite: int, hoehe: int) -> None: ...
    def bei_zerstoert(self) -> None: ...
    def bei_timer(self, ident: int) -> None: ...
    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_doppelklick(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_rad(self, delta: int, x: int, y: int, flags: int) -> int | None: return None
    def bei_taste(self, vk: int, lparam: int, syskey: bool) -> int | None: return None
    def bei_zeichen(self, code: int, syskey: bool) -> int | None: return None
    def bei_hotkey(self, ident: int) -> int | None: return None
    def bei_fokus(self, hat_fokus: bool) -> None: ...
    def bei_maus_verloren(self) -> None: ...
    def bei_dpi(self, dpi: int) -> None: ...
    def bei_nachricht(self, msg: int, wparam: int, lparam: int) -> int | None: return None


class PixelFenster(Fenster):
    """Fenster mit Pixel-Alpha (G08-Anzeige und Editorfläche). Mit Compositor echtes Alpha; ohne ihn eine Formmaske, halbdurchsichtiges gerastert."""

    klasse = "AuHPixel"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW | w.WS_EX_LAYERED

    def __init__(self, x: int, y: int, breite: int, hoehe: int, *, titel: str = "", durchklickbar: bool = True, nicht_aktivieren: bool = True):
        self.letztes_bild: Image.Image | None = None
        self.angenommen = False
        self._gerastert = False
        self._cairo_bild: cairo.ImageSurface | None = None
        self._cairo_daten: bytearray | None = None
        super().__init__(x, y, breite, hoehe, titel=titel, deckkraft=None, durchklickbar=False, nicht_aktivieren=nicht_aktivieren)
        screen = Gdk.Screen.get_default()
        self.compositor = bool(screen.is_composited() and screen.get_rgba_visual() is not None)
        if self.compositor:
            self._win.unrealize()
            self._win.set_visual(screen.get_rgba_visual())
            self._win.realize()
            self.hwnd_neu()
        if durchklickbar:
            self.durchklick_setzen(True)

    def hwnd_neu(self) -> None:
        gdkfenster = self._win.get_window()
        neu = int(gdkfenster.get_xid())
        _fenster.pop(self.hwnd, None)
        self.hwnd = neu
        _fenster[neu] = self

    def setze_rgba(self, bild: Image.Image) -> bool:
        breite, hoehe = self.clientgroesse()
        if breite <= 0 or hoehe <= 0:
            return False
        if bild.size != (breite, hoehe):
            bild = bild.resize((breite, hoehe))
        self.letztes_bild = bild
        rgba = bild.convert("RGBA")
        if self.compositor:
            r, g, b, a = rgba.split()
            from PIL import ImageChops
            r, g, b = ImageChops.multiply(r, a), ImageChops.multiply(g, a), ImageChops.multiply(b, a)  # Cairo erwartet vormultipliziert
            daten = bytearray(Image.merge("RGBA", (b, g, r, a)).tobytes())
            self._cairo_bild = cairo.ImageSurface.create_for_data(daten, cairo.FORMAT_ARGB32, breite, hoehe, breite * 4)
            self._cairo_daten = daten
            self._gerastert = False
            self.angenommen = True
        else:
            import numpy as np
            alpha = np.asarray(rgba.getchannel("A"), dtype=np.uint8)
            halb = int(((alpha > 0) & (alpha < 255)).sum())
            if halb and halb <= 40000:  # wenig Halbdurchsichtiges: rastern (Bayer), das ergibt den Eindruck von Durchsichtigkeit
                bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.uint8) * 16 + 8
                schwelle = np.tile(bayer, (hoehe // 4 + 1, breite // 4 + 1))[:hoehe, :breite]
                maske = (alpha > schwelle) | (alpha == 255)
            elif halb:  # große halbdurchsichtige Flächen würden Hunderttausende Rechtecke ergeben: ab einem Viertel Deckkraft ganz zeigen
                maske = alpha >= 64
            else:
                maske = alpha > 0
            self._form_bounding = rechtecke_aus_maske(maske) if maske.any() else [(0, 0, 1, 1)]
            if self.hwnd:
                _x_form_setzen(self.hwnd, self._form_bounding)
            daten = bytearray(Image.composite(rgba.convert("RGB"), Image.new("RGB", rgba.size, (0, 0, 0)), Image.fromarray(maske.astype(np.uint8) * 255)).tobytes("raw", "BGRX"))
            self._cairo_bild = cairo.ImageSurface.create_for_data(daten, cairo.FORMAT_RGB24, breite, hoehe, breite * 4)
            self._cairo_daten = daten
            self._gerastert = True
            self.angenommen = True
        self.neu_zeichnen()
        return self.angenommen

    def verschiebe(self, x: int, y: int, breite: int | None = None, hoehe: int | None = None) -> None:
        super().verschiebe(x, y, breite, hoehe)
        if self.letztes_bild is not None:
            self.setze_rgba(self.letztes_bild)

    def _bei_draw(self, _widget, cr) -> bool:
        if self._cairo_bild is not None:
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.set_source_surface(self._cairo_bild, 0, 0)
            cr.paint()
        return True


class Zentrale:
    """Stellvertreter für das unsichtbare Fenster der Windows-Fassung (dort nimmt es Hotkeys und Aufträge an)."""

    def __init__(self, anwendung: "Anwendung"):
        self.anwendung = anwendung
        self.hwnd = 1
        self.hotkeys: dict[int, Callable[[], None]] = {}


class Anwendung:
    """Die GTK-Schleife des GUI-Threads und die Brücke für Aufträge aus anderen Threads."""

    _aktuell: "Anwendung | None" = None
    fehler_aufruf: Callable[[str, BaseException], None] | None = None

    def __init__(self):
        Anwendung._aktuell = self
        self._aufgaben: queue.SimpleQueue[Callable[[], None]] = queue.SimpleQueue()
        self.zentrale: Zentrale | None = None
        self._hotkeys: t.HotkeyFaden | None = None
        self._hotkey_namen: dict[str, tuple[int, int]] = {}
        self.beendet = False

    @classmethod
    def fehler(cls, wo: str, fehler: BaseException) -> None:
        if cls.fehler_aufruf is not None:
            cls.fehler_aufruf(wo, fehler)

    def dpi_bewusst(self) -> bool:
        return True  # GTK/X11 rechnet in Bildpunkten des Bildschirms

    def starten(self) -> None:
        self.zentrale = Zentrale(self)

    def post(self, aufgabe: Callable[[], None]) -> None:
        """Aus jedem Thread erlaubt: führt `aufgabe` im GUI-Thread aus."""
        self._aufgaben.put(aufgabe)
        GLib.idle_add(self._abarbeiten_idle)

    def _abarbeiten_idle(self) -> bool:
        self.abarbeiten()
        return False

    def abarbeiten(self) -> None:
        while True:
            try:
                aufgabe = self._aufgaben.get_nowait()
            except queue.Empty:
                return
            try:
                aufgabe()
            except Exception as fehler:
                Anwendung.fehler("post", fehler)

    def _faden(self) -> "t.HotkeyFaden":
        if self._hotkeys is None:
            self._hotkeys = t.HotkeyFaden(self.post)
        return self._hotkeys

    def hotkey(self, modifikatoren: int, vk: int, aufruf: Callable[[], None]) -> bool:
        return self._faden().eintragen(vk, modifikatoren & ~w.MOD_NOREPEAT, aufruf)

    def hotkey_setzen(self, name: str, modifikatoren: int, vk: int, aufruf: Callable[[], None]) -> bool:
        """Hotkey unter einem Namen (neu oder ersetzend). Schlägt die neue Kombination fehl (belegt), bleibt die alte."""
        modifikatoren &= ~w.MOD_NOREPEAT
        alt = self._hotkey_namen.get(name)
        if alt is not None and alt == (modifikatoren, vk):
            return self._faden().eintragen(vk, modifikatoren, aufruf)  # gleiche Kombination: nur den Aufruf ersetzen
        if not self._faden().eintragen(vk, modifikatoren, aufruf):
            return False
        if alt is not None:
            self._faden().loeschen(alt[1], alt[0])
        self._hotkey_namen[name] = (modifikatoren, vk)
        return True

    def hotkey_loeschen(self, name: str) -> None:
        alt = self._hotkey_namen.pop(name, None)
        if alt is not None and self._hotkeys is not None:
            self._hotkeys.loeschen(alt[1], alt[0])

    def schleife(self) -> int:
        Gtk.main()
        self.beendet = True
        return 0

    def pumpen(self, maximal_ms: int = 0) -> None:
        """Für Tests: verarbeitet die anstehenden Ereignisse, ohne zu blockieren."""
        ende = time.monotonic() + maximal_ms / 1000
        while True:
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)
            if time.monotonic() >= ende:
                return
            time.sleep(0.005)

    def beenden(self, code: int = 0) -> None:
        if Gtk.main_level() > 0:
            Gtk.main_quit()
        self.beendet = True
        if self._hotkeys is not None:
            self._hotkeys.beenden()
