"""Aufklappmenüs und Zwischenablage für Linux (GTK 3): dieselben Aufrufe wie `menue.py` unter Windows.

`zeige_menue` blockiert, bis gewählt oder abgebrochen wurde, und liefert die Befehls-Id oder 0, genau wie TrackPopupMenuEx mit TPM_RETURNCMD.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: F401

from . import offene_menues
from . import win32 as w

Eintrag = tuple[int, str, int] | None


def baue_menue(eintraege: Sequence[Eintrag]):
    """(Menü, Ergebnis): das GTK-Menü zu den Einträgen; ein gewählter Eintrag trägt seine Befehls-Id in `ergebnis["id"]` ein."""
    menue = Gtk.Menu()
    ergebnis = {"id": 0, "punkte": []}  # „punkte“: (Befehls-Id, Text, Widget) je Eintrag, für das Register der offenen Menüs
    for eintrag in eintraege:
        if eintrag is None:
            menue.append(Gtk.SeparatorMenuItem())
            continue
        befehl, text, flags = eintrag
        if flags & w.MF_CHECKED:
            punkt = Gtk.CheckMenuItem.new_with_label(text)
            punkt.set_active(True)
            punkt.set_draw_as_radio(False)
        else:
            punkt = Gtk.MenuItem.new_with_label(text)
        punkt.set_sensitive(not (flags & w.MF_GRAYED) and befehl != 0)
        ergebnis["punkte"].append((befehl, text, punkt))
        punkt.connect("activate", lambda _p, b=befehl: ergebnis.__setitem__("id", b))
        menue.append(punkt)
    return menue, ergebnis


def _registrieren(menue, punkte, art: str, versuche: list) -> bool:
    """Trägt das offene Menü mit Einträgen und Schirmrechtecken ins Register ein (der Körper kennt sein eigenes Menü). Wiederholt, bis GTK die Größen kennt.
    Ohne Eintrag bleibt jede Menü-Aktion eines Agenten abgelehnt; ein Fehler hier macht nie etwas frei."""
    try:
        fenster = menue.get_window()
        zuweisungen = [p.get_allocation() for _b, _t, p in punkte]
        if (fenster is None or not zuweisungen or all(a.width <= 1 for a in zuweisungen)) and versuche[0] < 40:
            versuche[0] += 1
            return True  # GLib ruft noch einmal auf
        if fenster is None:
            return False
        _ok, ox, oy = fenster.get_origin()
        eintraege = [offene_menues.MenueEintrag(b, t, (ox + a.x, oy + a.y, ox + a.x + a.width, oy + a.y + a.height), bool(p.get_sensitive()))
                     for (b, t, p), a in zip(punkte, zuweisungen)]
        def schliessen():
            try:
                GLib.idle_add(lambda: (menue.popdown(), False)[1])
            except Exception:
                pass

        offene_menues.REGISTER.oeffnen(menue.get_toplevel().get_window().get_xid(), art, eintraege, schliessen)
    except Exception:
        offene_menues.REGISTER.schliessen()
    return False


def zeige_menue(hwnd: int, eintraege: Sequence[Eintrag], x: int, y: int, *, nach_oben: bool = False, rechtsbuendig: bool = False,
                vorab: "Callable[[Gtk.Menu], None] | None" = None) -> int:
    """Blockiert, bis gewählt oder abgebrochen wurde; liefert die Befehls-Id oder 0. `vorab` (nur für Tests) bekommt das Menü, bevor es sich zeigt."""
    menue, ergebnis = baue_menue(eintraege)
    schleife = GLib.MainLoop()
    for signal in ("deactivate", "selection-done", "hide"):  # je nach Grab-Lage meldet GTK das Ende über ein anderes Signal
        menue.connect(signal, lambda _m: GLib.idle_add(schleife.quit))
    menue.show_all()
    if vorab is not None:
        vorab(menue)
    breite, hoehe = menue.get_preferred_width()[1], menue.get_preferred_height()[1]
    links = int(x) - (breite if rechtsbuendig else 0)
    oben = int(y) - (hoehe if nach_oben else 0)
    # Ohne auslösendes Ereignis (der Körper öffnet Menüs aus eigenem Anlass) geht nur das klassische popup mit Ortsfunktion.
    menue.popup(None, None, lambda _m, *_rest: (links, oben, True), None, 0, Gtk.get_current_event_time())
    art = offene_menues.aktuelle_art()
    GLib.idle_add(_registrieren, menue, ergebnis["punkte"], art, [0])
    try:
        schleife.run()
    finally:
        offene_menues.REGISTER.schliessen()  # solange das Menü offen ist, kennt der Körper es; danach nicht mehr
    menue.destroy()
    return int(ergebnis["id"])


def text_aus_zwischenablage(hwnd: int) -> str:
    zwischenablage = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    return zwischenablage.wait_for_text() or ""


def text_in_zwischenablage(hwnd: int, text: str) -> bool:
    zwischenablage = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    zwischenablage.set_text(text, -1)
    zwischenablage.store()
    return True
