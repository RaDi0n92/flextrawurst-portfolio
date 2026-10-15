"""Linux-Adapter des Körpers (X11): das, was unter Windows Win32 außerhalb der Fenster leistet.

* `LinuxWindowApi`: Fensterinventar für den Scanner (gleiche Form wie `Win32WindowApi`: sichtbare Fenster, oben zuerst, mit Titel, Klasse, Prozess, Lage).
* `LinuxCaptureApi`: Aufnahme des Desktops und einzelner Fenster. Ein Fenster wird über XComposite (automatische Umleitung) auch dann vollständig
  gelesen, wenn ein anderes es verdeckt; der Desktop wird auf Wunsch **ohne die Fenster der Bridge** zusammengesetzt (R044, Bridge-im-Bild).
  Die Umleitung ändert nichts an dem, was Daniel sieht. Läuft schon ein Compositor, sind beide Fähigkeiten nicht verfügbar und das wird gemeldet.
* `xtest_senden`: Tasten und Text per XTEST in beliebige Fenster (Umlaute, Emoji, jede Taste), in der Form der Windows-`SendInput`-Ereignisse.
* `LinuxNotAusHook`: der lokale F12-Not-Aus über XRecord in eigenem Faden: unabhängig vom GUI-Faden, schluckt die Taste nicht.
* `LinuxQuelle`: Vordergrund, offene Programme und Bildschirm für die Sichtbarkeitsregeln.
* `datei_waehlen`: der GTK-Dialog „Datei öffnen“ für Bilder.

Fremde Fenster werden über ihre X-Kennung angesprochen; sie ist unter Linux der `hwnd`. Der Adapter liest nur und tippt nur, wenn man ihn dazu auffordert.
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable

from augen_haende_bridge.windows_scanner import WindowInfo

from . import fenster_linux as fl
from . import tasten_x11 as t
from . import win32 as w
from . import x11_helfer as x

Rechteck = tuple[int, int, int, int]
KEYEVENTF_KEYUP, KEYEVENTF_UNICODE = 0x0002, 0x0004
BELEGUNG_WARTEN_S = 0.06  # Pause um das kurze Umbelegen eines freien Tastencodes (Zeichen, die die Tastenbelegung nicht kennt)


def _atom(name: str) -> int:
    return x.anzeige().intern_atom(name)


def _prozess(xid: int) -> tuple[int | None, str | None]:
    """(PID, Pfad der Programmdatei) eines Fensters über _NET_WM_PID; None, wenn es keine nennt."""
    from Xlib import error

    try:
        eigenschaft = x.anzeige().create_resource_object("window", int(xid)).get_full_property(_atom("_NET_WM_PID"), 0)
    except (error.BadWindow, error.XError):
        return None, None
    if eigenschaft is None or not len(eigenschaft.value):
        return None, None
    pid = int(eigenschaft.value[0])
    try:
        return pid, os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return pid, None


def _klasse(xid: int) -> str:
    from Xlib import error

    try:
        wm_class = x.anzeige().create_resource_object("window", int(xid)).get_wm_class()
    except (error.BadWindow, error.XError):
        return ""
    return wm_class[1] if wm_class else ""


def _stapel_von_oben() -> list[int]:
    """Alle Fenster, die für Programme gelten, von oben nach unten: erst die Liste des Fensterverwalters (EWMH), sonst die X-Stapelung der Wurzel."""
    anzeige = x.anzeige()
    wurzel = anzeige.screen().root
    liste = wurzel.get_full_property(_atom("_NET_CLIENT_LIST_STACKING"), 0)
    if liste is not None and len(liste.value):
        return [int(k) for k in reversed(list(liste.value))]
    return [int(k.id) for k in reversed(wurzel.query_tree().children)]


class LinuxWindowApi:
    """Die Fensterliste für den Scanner (`WindowApi`)."""

    def virtual_screen_rect(self) -> Rechteck:
        breite, hoehe = x.bildschirmgroesse()
        return 0, 0, breite, hoehe

    def enumerate_windows(self) -> list[WindowInfo]:
        from Xlib import error

        fenster: list[WindowInfo] = []
        for xid in _stapel_von_oben():
            try:
                if not x.fenster_sichtbar(xid):
                    continue
                rect = x.fenster_rechteck(xid)
                if rect is None or rect[2] - rect[0] < 2 or rect[3] - rect[1] < 2:
                    continue
                titel = x.fenstertitel(xid)
                klasse = _klasse(xid)
                pid, pfad = _prozess(xid)
                fenster.append(WindowInfo(hwnd=int(xid), title=titel or klasse or f"X11 {xid}", class_name=klasse, rect=rect,
                                          process_id=pid, process_path=pfad, visible=True))
            except (error.BadWindow, error.XError):
                continue
        return fenster

    # dieselben Namen wie bei Win32WindowApi: von der Sichtquelle benutzt
    def _window_text(self, xid: int) -> str:
        return x.fenstertitel(xid)

    def _process_path(self, pid: int | None) -> str | None:
        if not pid:
            return None
        try:
            return os.readlink(f"/proc/{pid}/exe")
        except OSError:
            return None


# ---- Aufnahme --------------------------------------------------------------------------------------------------------------
class LinuxCaptureApi:
    """Aufnahme des Desktops (`CaptureApi`) und einzelner Fenster."""

    def __init__(self, ausnahmen: Callable[[], set[int]] | None = None):
        self._ausnahmen = ausnahmen if ausnahmen is not None else (lambda: fl.AUSGENOMMEN)
        self._umgeleitet: set[int] = set()
        self.umleitung_moeglich = self._pruefe_umleitung()
        # Das Bild genau eines Fensters (G06.7) gibt es mit eigener Umleitung (kein Compositor) und unter einem laufenden Compositor,
        # der jedes Fenster schon selbst umleitet: dann genügt die benannte Fensterpixmap. Nur das Auslassen der Bridge-Fenster im
        # Desktopbild braucht die eigene Umleitung (`umleitung_moeglich`).
        self.fensterbild_moeglich = self.umleitung_moeglich or self._compositor_leitet_um()
        if self.umleitung_moeglich:
            fl.AUFNAHME_AUSNAHME_MOEGLICH = True  # ab jetzt melden die Fenster der Bridge „aus der Aufnahme ausgenommen“ wahrheitsgemäß

    @staticmethod
    def _composite_ab_0_2() -> bool:
        anzeige = x.anzeige()
        if not anzeige.has_extension("Composite"):
            return False
        try:
            version = anzeige.composite_query_version()
        except Exception:
            return False
        return (version.major_version, version.minor_version) >= (0, 2)

    @staticmethod
    def _compositor_besitzt_bildschirm() -> bool:
        besitzer = x.anzeige().get_selection_owner(_atom("_NET_WM_CM_S0"))
        return not (besitzer == 0 or getattr(besitzer, "id", 0) == 0)

    @classmethod
    def _pruefe_umleitung(cls) -> bool:
        return cls._composite_ab_0_2() and not cls._compositor_besitzt_bildschirm()  # ein laufender Compositor hat die Umleitung selbst

    @classmethod
    def _compositor_leitet_um(cls) -> bool:
        return cls._composite_ab_0_2() and cls._compositor_besitzt_bildschirm()

    def virtual_screen_rect(self) -> Rechteck:
        breite, hoehe = x.bildschirmgroesse()
        return 0, 0, breite, hoehe

    # ---- Bausteine
    def _abbild(self, zeichenflaeche, rect: Rechteck):
        """Pillow-Bild (RGBA) eines Zeichenbereichs (Fenster, Wurzel oder Pixmap)."""
        from PIL import Image

        links, oben, rechts, unten = rect
        bild = zeichenflaeche.get_image(links, oben, rechts - links, unten - oben, 2, 0xFFFFFFFF)  # 2 = ZPixmap
        return Image.frombuffer("RGBA", (rechts - links, unten - oben), bytes(bild.data), "raw", "BGRA", 0, 1)

    def _umleiten(self, xid: int) -> bool:
        from Xlib import error
        from Xlib.ext import composite

        if xid in self._umgeleitet:
            return True
        try:
            fenster = x.anzeige().create_resource_object("window", int(xid))
            fenster.composite_redirect_window(composite.RedirectAutomatic)
            x.anzeige().sync()
        except (error.BadAccess, error.BadWindow, error.XError):
            return False
        self._umgeleitet.add(xid)
        return True

    def _benannte_pixmap(self, fenster):
        """Die benannte Pixmap dieses Fensters oder None, wenn es nicht umgeleitet ist (BadMatch kommt erst nach dem Abgleich mit dem Server)."""
        from Xlib import error

        fang = error.CatchError(error.BadMatch, error.BadWindow, error.BadDrawable)
        pixmap = fenster.composite_name_window_pixmap(onerror=fang)
        x.anzeige().sync()
        if fang.get_error() is not None:
            return None
        return pixmap

    def _compositor_pixmap(self, fenster):
        """Unter einem Compositor ist oft nur der Rahmen (Toplevel unter der Wurzel) umgeleitet, nicht das Client-Fenster darin.
        Gibt (Pixmap, Versatz des Fensters in ihr) zurück, vom Fenster selbst bis zum obersten Vorfahren; (None, None), wenn keines lesbar ist."""
        aktuell = fenster
        while True:
            pixmap = self._benannte_pixmap(aktuell)
            if pixmap is not None:
                if aktuell.id == fenster.id:
                    return pixmap, (0, 0)
                ort = aktuell.translate_coords(fenster, 0, 0)
                return pixmap, (ort.x, ort.y)
            baum = aktuell.query_tree()
            if baum.parent is None or baum.parent.id == baum.root.id:
                return None, None
            aktuell = baum.parent

    def _fensterbild(self, xid: int):
        """Das ganze Fenster samt Unterfenstern, auch verdeckt, als RGBA-Bild; None, wenn es nicht (mehr) lesbar ist."""
        from Xlib import error

        anzeige = x.anzeige()
        try:
            fenster = anzeige.create_resource_object("window", int(xid))
            if fenster.get_attributes().map_state != 2:  # nur eingeblendete Fenster haben aktuellen Inhalt
                return None
            geo = fenster.get_geometry()
            if geo.width < 1 or geo.height < 1:
                return None
            if self.umleitung_moeglich:
                if not self._umleiten(xid):
                    return None
                pixmap, (dx, dy) = fenster.composite_name_window_pixmap(), (0, 0)
            else:  # ein Compositor leitet schon um: sein Rahmen liefert die Pixmap, das Client-Fenster wird daraus ausgeschnitten
                pixmap, versatz = self._compositor_pixmap(fenster)
                if pixmap is None:
                    return None
                dx, dy = versatz
            try:
                bild = self._abbild(pixmap, (dx, dy, dx + geo.width, dy + geo.height))
            finally:
                pixmap.free()
            if geo.depth != 32:
                bild.putalpha(255)
            return bild
        except (error.BadWindow, error.BadMatch, error.BadDrawable, error.XError):
            self._umgeleitet.discard(xid)
            return None

    def capture_window(self, xid: int) -> tuple[bytes, int, int] | None:
        """(BGRA, Breite, Höhe) dieses Fensters unabhängig davon, was davor liegt; None, wenn nicht lesbar."""
        bild = self._fensterbild(xid)
        if bild is None:
            return None
        return self._als_bgra(bild), bild.size[0], bild.size[1]

    @staticmethod
    def _als_bgra(bild) -> bytes:
        r, g, b, a = bild.split()
        from PIL import Image

        return Image.merge("RGBA", (b, g, r, a)).tobytes()

    def _enthaelt(self, xid: int, gesucht: set[int], tiefe: int = 3) -> bool:
        from Xlib import error

        if xid in gesucht:
            return True
        if tiefe <= 0:
            return False
        try:
            kinder = x.anzeige().create_resource_object("window", int(xid)).query_tree().children
        except (error.BadWindow, error.XError):
            return False
        return any(self._enthaelt(int(k.id), gesucht, tiefe - 1) for k in kinder)

    def capture_bgra(self, rect: Rechteck, ohne_bridge: bool | None = None) -> bytes:
        """BGRA-Bytes des Bereichs. `ohne_bridge` (Vorgabe: wenn Fenster ausgenommen sind): Fenster der Bridge werden nicht gezeigt."""
        links, oben, rechts, unten = rect
        wurzel = x.anzeige().screen().root
        bild = self._abbild(wurzel, rect)
        bild.putalpha(255)
        ausnahmen = set(self._ausnahmen())
        if (ohne_bridge is None and ausnahmen) or ohne_bridge:
            if self.umleitung_moeglich and ausnahmen:
                bild = self._ohne(bild, rect, ausnahmen, wurzel)
        return self._als_bgra(bild)

    def _ohne(self, bild, rect: Rechteck, ausnahmen: set[int], wurzel):
        """Setzt den Desktop aus den Bildern der anderen Fenster zusammen (von unten nach oben), so dass die Fenster der Bridge fehlen."""
        from Xlib import error

        links, oben, rechts, unten = rect
        for kind in wurzel.query_tree().children:  # X-Stapelreihenfolge, unten zuerst
            try:
                attribute = kind.get_attributes()
                if attribute.map_state != 2 or attribute.win_class == 2:  # nicht eingeblendet oder nur Eingabe
                    continue
                if self._enthaelt(int(kind.id), ausnahmen):
                    continue
                geo = kind.get_geometry()
                fx, fy = geo.x, geo.y
                if fx >= rechts or fy >= unten or fx + geo.width <= links or fy + geo.height <= oben:
                    continue
                fensterbild = self._fensterbild(int(kind.id))
            except (error.BadWindow, error.XError):
                continue
            if fensterbild is None:
                continue
            dx, dy = fx - links, fy - oben  # Lage im Ausschnitt; was links oder oberhalb herausragt, wird abgeschnitten
            bild.alpha_composite(fensterbild, (max(0, dx), max(0, dy)), (max(0, -dx), max(0, -dy)))
        return bild


# ---- Eingabe ---------------------------------------------------------------------------------------------------------------
class _Tastatur:
    """Tasten und Zeichen per XTEST (eine Verbindung je Faden, die der Aufrufer hält)."""

    def __init__(self):
        from Xlib import X
        from Xlib.ext import xtest

        self._X, self._xtest = X, xtest
        self.anzeige = x.anzeige()
        self._hoch_unterdrueckt: set[int] = set()

    def _code(self, vk: int) -> int | None:
        keysym = t.VK_ZU_KEYSYM.get(vk)
        if keysym is None:
            return None
        codes = t._keycodes(self.anzeige, keysym)
        return codes[0] if codes else None

    def vk(self, vk: int, runter: bool) -> bool:
        code = self._code(vk)
        if code is None:
            return False
        self._xtest.fake_input(self.anzeige, self._X.KeyPress if runter else self._X.KeyRelease, code)
        self.anzeige.sync()
        return True

    def zeichen(self, codepunkt: int) -> bool:
        """Tippt ein Zeichen (Drücken und Loslassen), auch wenn die Tastenbelegung es nicht kennt: dann wird ein freier Tastencode kurz damit belegt."""
        if codepunkt in (0x0A, 0x0D):
            return self.vk(w.VK_RETURN, True) and self.vk(w.VK_RETURN, False)
        if codepunkt == 0x09:
            return self.vk(w.VK_TAB, True) and self.vk(w.VK_TAB, False)
        keysym = codepunkt if codepunkt <= 0xFF else 0x01000000 | codepunkt
        for code, spalte in self._codes_mit_spalte(keysym):
            if spalte in (0, 1):  # Grundbelegung oder mit Umschalt
                umschalt = spalte == 1
                if umschalt:
                    self.vk(w.VK_SHIFT, True)
                self._xtest.fake_input(self.anzeige, self._X.KeyPress, code)
                self._xtest.fake_input(self.anzeige, self._X.KeyRelease, code)
                if umschalt:
                    self.vk(w.VK_SHIFT, False)
                self.anzeige.sync()
                return True
        return self._ueber_leeren_code(keysym)

    def _codes_mit_spalte(self, keysym: int) -> list[tuple[int, int]]:
        return [(int(c[0]), int(c[1])) for c in self.anzeige.keysym_to_keycodes(keysym) if c[0]]

    def _ueber_leeren_code(self, keysym: int) -> bool:
        anzeige = self.anzeige
        erster = anzeige.display.info.min_keycode
        belegung = anzeige.get_keyboard_mapping(erster, anzeige.display.info.max_keycode - erster + 1)
        frei = next((erster + i for i, zeile in enumerate(belegung) if not any(zeile)), None)
        if frei is None:
            return False
        anzeige.change_keyboard_mapping(frei, [(keysym, keysym, keysym, keysym)])
        anzeige.sync()
        time.sleep(BELEGUNG_WARTEN_S)  # die Programme brauchen einen Augenblick, um die neue Belegung zu übernehmen
        self._xtest.fake_input(anzeige, self._X.KeyPress, frei)
        self._xtest.fake_input(anzeige, self._X.KeyRelease, frei)
        anzeige.sync()
        time.sleep(BELEGUNG_WARTEN_S)  # und die Taste auswerten, bevor die alte Belegung zurückkommt
        anzeige.change_keyboard_mapping(frei, [(0, 0, 0, 0)])
        anzeige.sync()
        return True


_sender_lokal = threading.local()


def xtest_senden(ereignisse: list[tuple[int, int, int]]) -> int:
    """Gegenstück zu `windows_sendinput`: führt (vk, scan, flags)-Ereignisse aus und liefert, wie viele gesendet wurden."""
    tastatur = getattr(_sender_lokal, "tastatur", None)
    if tastatur is None:
        tastatur = _sender_lokal.tastatur = _Tastatur()
    gesendet = 0
    hoch_ersatz: int | None = None
    for vk, scan, flags in ereignisse:
        if flags & KEYEVENTF_UNICODE:
            if flags & KEYEVENTF_KEYUP:
                gesendet += 1
                continue
            if 0xD800 <= scan <= 0xDBFF:  # erste Hälfte eines Zeichenpaars: auf die zweite warten
                hoch_ersatz = scan
                gesendet += 1
                continue
            if 0xDC00 <= scan <= 0xDFFF and hoch_ersatz is not None:
                scan = 0x10000 + ((hoch_ersatz - 0xD800) << 10) + (scan - 0xDC00)
                hoch_ersatz = None
            if tastatur.zeichen(scan):
                gesendet += 1
        elif tastatur.vk(vk, not (flags & KEYEVENTF_KEYUP)):
            gesendet += 1
    return gesendet


# ---- Not-Aus ---------------------------------------------------------------------------------------------------------------
class LinuxNotAusHook:
    """Der lokale Not-Aus (F12) über XRecord: eigener Faden, eigene Verbindung, kein GUI-Faden nötig; die Taste kommt weiter bei den Programmen an."""

    def __init__(self, not_aus, *, vk: int = w.VK_F12, name: str = "F12"):
        self.not_aus, self.vk, self.name = not_aus, vk, name
        self.installiert = False
        self.fehler: str | None = None
        self._faden: threading.Thread | None = None
        self._bereit = threading.Event()
        self._kontext = None
        self._steuer = None

    def start(self, timeout: float = 5.0) -> bool:
        self._faden = threading.Thread(target=self._lauf, name="notaus-xrecord", daemon=True)
        self._faden.start()
        self._bereit.wait(timeout)
        return self.installiert

    def _lauf(self) -> None:
        from Xlib import X, display
        from Xlib.protocol import rq
        from Xlib.ext import record

        try:
            daten = display.Display()
            steuer = display.Display()
            if not daten.has_extension("RECORD"):
                self.fehler = "XRecord fehlt"
                self._bereit.set()
                return
            keysym = t.VK_ZU_KEYSYM.get(self.vk)
            codes = t._keycodes(daten, keysym) if keysym else []
            if not codes:
                self.fehler = "Taste nicht belegt"
                self._bereit.set()
                return
            code = codes[0]
            kontext = daten.record_create_context(0, [record.AllClients], [{
                "core_requests": (0, 0), "core_replies": (0, 0), "ext_requests": (0, 0, 0, 0), "ext_replies": (0, 0, 0, 0),
                "delivered_events": (0, 0), "device_events": (X.KeyPress, X.KeyPress), "errors": (0, 0),
                "client_started": False, "client_died": False}])
        except Exception as fehler:
            self.fehler = f"XRecord nicht verfügbar: {fehler!r}"
            self._bereit.set()
            return
        self._kontext, self._steuer = kontext, steuer

        def rueckruf(antwort) -> None:
            if antwort.category != record.FromServer or antwort.client_swapped or not antwort.data:
                return
            rest = antwort.data
            while len(rest):
                ereignis, rest = rq.EventField(None).parse_binary_value(rest, daten.display, None, None)
                if ereignis.type == X.KeyPress and ereignis.detail == code:
                    self.not_aus.ausloesen(self.name)

        self.installiert = True
        self._bereit.set()
        try:
            daten.record_enable_context(kontext, rueckruf)  # blockiert, bis der Kontext beendet wird
        except Exception as fehler:
            self.fehler = f"XRecord beendet: {fehler!r}"
        finally:
            self.installiert = False
            try:
                daten.record_free_context(kontext)
            except Exception:
                pass

    def stop(self) -> None:
        if self._kontext is not None and self._steuer is not None:
            try:
                self._steuer.record_disable_context(self._kontext)
                self._steuer.flush()
            except Exception:
                pass
        if self._faden is not None:
            self._faden.join(timeout=3.0)


# ---- Sichtquelle -----------------------------------------------------------------------------------------------------------
class LinuxQuelle:
    """Vordergrundprogramm und offene Programme für die Sichtbarkeitsregeln (Gegenstück zu `WindowsQuelle`)."""

    def __init__(self, api: LinuxWindowApi | None = None):
        self._api = api if api is not None else LinuxWindowApi()

    def vordergrund(self):
        from .sichtbarkeit import Vordergrund, dateiname

        xid = x.vordergrund()
        if not xid:
            return None
        pid, pfad = _prozess(xid)
        if not pid:
            return None
        return Vordergrund(pid, dateiname(pfad), x.fenstertitel(xid))

    def bildschirm(self) -> Rechteck:
        return self._api.virtual_screen_rect()

    def offene_programme(self, ohne_pid: int | None = None):
        from .sichtbarkeit import Programm, dateiname

        gesehen: dict[str, Programm] = {}
        for fenster in self._api.enumerate_windows():
            if fenster.process_id == ohne_pid:
                continue
            name = dateiname(fenster.process_path)
            if not name or name in gesehen or not (fenster.title or "").strip():
                continue
            gesehen[name] = Programm(name, fenster.title)
        return sorted(gesehen.values(), key=lambda p: p.programm)


# ---- Dateiwahl -------------------------------------------------------------------------------------------------------------
def datei_waehlen(hwnd: int, titel: str = "Bild für den Agenten wählen", vorab=None) -> str | None:
    """Pfad der gewählten Datei oder None (Abbruch). `vorab` (nur für Tests) bekommt den Dialog, bevor er läuft."""
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    dialog = Gtk.FileChooserDialog(title=titel, action=Gtk.FileChooserAction.OPEN)
    dialog.add_buttons("Abbrechen", Gtk.ResponseType.CANCEL, "Öffnen", Gtk.ResponseType.OK)
    bilder = Gtk.FileFilter()
    bilder.set_name("Bilder (png, jpg, bmp, gif, webp)")
    for muster in ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.webp"):
        bilder.add_pattern(muster)
    alle = Gtk.FileFilter()
    alle.set_name("Alle Dateien")
    alle.add_pattern("*")
    dialog.add_filter(bilder)
    dialog.add_filter(alle)
    if vorab is not None:
        vorab(dialog)
    try:
        antwort = dialog.run()
        return dialog.get_filename() if antwort == Gtk.ResponseType.OK else None
    finally:
        dialog.destroy()
