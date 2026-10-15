"""Kleine X11-Hilfen über python-xlib, von der Linux-Fensterschicht und dem Linux-Adapter gemeinsam benutzt.

Jeder Faden bekommt seine eigene Verbindung (python-xlib ist nicht fadensicher). Alle Funktionen sind lesend, außer wo der Name es sagt.
Fremde Fenster werden über ihre X-Kennung (`xid`) angesprochen; sie spielt unter Linux die Rolle des Fenstergriffs (`hwnd`).
"""

from __future__ import annotations

import threading

_lokal = threading.local()

Rechteck = tuple[int, int, int, int]


def anzeige():
    """Die X-Verbindung dieses Fadens (wird beim ersten Aufruf geöffnet)."""
    verbindung = getattr(_lokal, "anzeige", None)
    if verbindung is None:
        from Xlib import display

        verbindung = _lokal.anzeige = display.Display()
    return verbindung


def schliessen() -> None:
    verbindung = getattr(_lokal, "anzeige", None)
    if verbindung is not None:
        try:
            verbindung.close()
        finally:
            _lokal.anzeige = None


def _fenster(xid: int):
    return anzeige().create_resource_object("window", int(xid))


def _atom(name: str) -> int:
    return anzeige().intern_atom(name)


def fenster_existiert(xid: int) -> bool:
    from Xlib import error

    try:
        _fenster(xid).get_attributes()
        return True
    except (error.BadWindow, error.BadDrawable, error.XError):
        return False


def fenster_minimiert(xid: int) -> bool:
    """Steht das Fenster als Symbol (WM_STATE Iconic) oder als versteckt (_NET_WM_STATE_HIDDEN)?"""
    from Xlib import error

    try:
        fenster = _fenster(xid)
        zustand = fenster.get_full_property(_atom("_NET_WM_STATE"), 0)
        if zustand is not None and _atom("_NET_WM_STATE_HIDDEN") in list(zustand.value):
            return True
        wm_state = fenster.get_full_property(_atom("WM_STATE"), 0)
        if wm_state is not None and len(wm_state.value) and int(wm_state.value[0]) == 3:  # IconicState
            return True
        return fenster.get_attributes().map_state != 2  # nicht eingeblendet (IsViewable == 2)
    except (error.BadWindow, error.XError):
        return False


def fenster_sichtbar(xid: int) -> bool:
    from Xlib import error

    try:
        return _fenster(xid).get_attributes().map_state == 2
    except (error.BadWindow, error.XError):
        return False


def fenster_rechteck(xid: int) -> Rechteck | None:
    """Außenmaß des Fensters in Bildschirmkoordinaten (links, oben, rechts, unten), None wenn es nicht (mehr) da ist."""
    from Xlib import error

    try:
        fenster = _fenster(xid)
        geo = fenster.get_geometry()
        wurzel = anzeige().screen().root
        pos = fenster.translate_coords(wurzel, 0, 0)  # Ursprung des Fensters aus Sicht der Wurzel
        links, oben = -pos.x, -pos.y
        return links, oben, links + geo.width, oben + geo.height
    except (error.BadWindow, error.XError):
        return None


def vordergrund() -> int | None:
    """Das aktive Fenster (EWMH _NET_ACTIVE_WINDOW), sonst der Eingabefokus; None, wenn keines feststellbar ist."""
    wurzel = anzeige().screen().root
    aktiv = wurzel.get_full_property(_atom("_NET_ACTIVE_WINDOW"), 0)
    if aktiv is not None and len(aktiv.value) and int(aktiv.value[0]):
        return int(aktiv.value[0])
    fokus = anzeige().get_input_focus().focus
    return int(fokus.id) if hasattr(fokus, "id") and fokus.id > 1 else None


def arbeitsbereich() -> Rechteck:
    """Der Desktop ohne Leisten (EWMH _NET_WORKAREA), sonst der ganze Bildschirm."""
    wurzel = anzeige().screen().root
    bereich = wurzel.get_full_property(_atom("_NET_WORKAREA"), 0)
    if bereich is not None and len(bereich.value) >= 4:
        x, y, b, h = (int(v) for v in list(bereich.value)[:4])
        return x, y, x + b, y + h
    geo = wurzel.get_geometry()
    return 0, 0, geo.width, geo.height


def bildschirmgroesse() -> tuple[int, int]:
    geo = anzeige().screen().root.get_geometry()
    return geo.width, geo.height


def maus_position() -> tuple[int, int]:
    daten = anzeige().screen().root.query_pointer()
    return daten.root_x, daten.root_y


def fenstertitel(xid: int) -> str:
    from Xlib import error

    try:
        fenster = _fenster(xid)
        name = fenster.get_full_property(_atom("_NET_WM_NAME"), 0)
        if name is not None:
            return bytes(name.value).decode("utf-8", "replace") if not isinstance(name.value, str) else name.value
        alt = fenster.get_wm_name()
        return alt if isinstance(alt, str) else (alt.decode("latin-1") if alt else "")
    except (error.BadWindow, error.XError):
        return ""


def fenster_nach_vorn(xid: int) -> bool:
    """Das Fenster nach vorn holen: erst die Standardbitte an den Fenstermanager (_NET_ACTIVE_WINDOW), dann zusätzlich ganz nach oben.

    Verändert nur die Stapelreihenfolge fremder Fenster, nichts an ihrem Inhalt. Antwort: ob das Fenster noch existiert."""
    from Xlib import X, error, protocol

    try:
        d = anzeige()
        fenster = _fenster(xid)
        wurzel = d.screen().root
        ereignis = protocol.event.ClientMessage(window=fenster, client_type=_atom("_NET_ACTIVE_WINDOW"), data=(32, [2, X.CurrentTime, 0, 0, 0]))
        wurzel.send_event(ereignis, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        fenster.configure(stack_mode=X.Above)
        d.flush()
        return True
    except (error.BadWindow, error.BadDrawable, error.XError):
        return False


TON_DATEI = "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga"


def piepen() -> None:
    """Ein kurzer Warnton: der Klang des Desktops (paplay), sonst die X-Glocke. Scheitert still, die Anzeige gilt immer zuerst."""
    import os
    import subprocess

    try:
        if os.path.exists(TON_DATEI):
            subprocess.Popen(["paplay", TON_DATEI], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    except OSError:
        pass
    try:
        anzeige().bell(0)
        anzeige().flush()
    except Exception:
        pass
