"""Linux-Adapter: Fensterinventar, Aufnahme, Eingabe, Not-Aus, Sichtquelle, Dateiwahl. Braucht einen X-Server (wird unter xvfb-run geprüft)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

# Diese Tests tippen echte Tasten (XTEST), bewegen den Zeiger und legen Fenster an: das darf nie auf einem sichtbaren Desktop geschehen. Sie laufen nur,
# wenn der Aufrufer ausdrücklich bestätigt, dass DISPLAY ein eigener, privater Xvfb ist (die Gates starten sie über `xvfb-run … env BRIDGE_TEST_XVFB=1`).
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
if DISPLAY:
    from Xlib import X, XK, display as xdisplay
    from Xlib.ext import xtest

    from augen_haende_bridge.koerper import fenster_linux as fl
    from augen_haende_bridge.koerper import linux_adapter as la
    from augen_haende_bridge.koerper import tasten_x11 as t
    from augen_haende_bridge.koerper import win32 as w
    from augen_haende_bridge.koerper import x11_helfer as x
    from augen_haende_bridge.koerper.notaus import NotAus
    from augen_haende_bridge.koerper.tasten_senden import Haende, kombination_ereignisse, text_ereignisse
    from augen_haende_bridge.koerper.tastenkombi import Kombination
    from augen_haende_bridge.windows_scanner import WindowsWindowScanner
    from augen_haende_bridge.contracts import TargetKind

pytestmark = unittest.skipUnless(DISPLAY, "kein X-Server")


class XFall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DISPLAY:
            raise unittest.SkipTest("kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
        cls.app = fl.Anwendung()
        cls.app.starten()

    def setUp(self):
        self.fenster: list = []
        self.xfenster: list = []
        self.anzeige = x.anzeige()

    def tearDown(self):
        for f in self.fenster:
            f.schliessen()
        for f in self.xfenster:
            try:
                f.destroy()
            except Exception:
                pass
        self.anzeige.sync()
        self.app.pumpen(50)
        fl.AUSGENOMMEN.clear()

    def pumpe(self, ms=100):
        self.app.pumpen(ms)

    def gtk(self, x_, y_, b, h, titel="", **kw):
        f = fl.Fenster(x_, y_, b, h, titel=titel, **kw)
        f.zeige(aktivieren=False)
        self.fenster.append(f)
        self.pumpe(120)
        return f

    def farbfenster(self, x_, y_, b, h, rgb):
        """Ein einfarbiges X-Fenster ohne Fensterverwaltung: der Server malt den Hintergrund selbst."""
        wurzel = self.anzeige.screen().root
        farbe = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
        fenster = wurzel.create_window(x_, y_, b, h, 0, self.anzeige.screen().root_depth, X.InputOutput, X.CopyFromParent,
                                       background_pixel=farbe, override_redirect=True)
        fenster.map()
        self.anzeige.sync()
        self.xfenster.append(fenster)
        time.sleep(0.05)
        return fenster


class InventarTests(XFall):
    def test_nennt_echte_fenster_oben_zuerst_mit_allen_angaben(self):
        a = self.gtk(50, 50, 200, 120, "Alpha")
        b = self.gtk(120, 90, 200, 120, "Beta")
        infos = la.LinuxWindowApi().enumerate_windows()
        ids = [i.hwnd for i in infos]
        self.assertIn(a.hwnd, ids)
        self.assertIn(b.hwnd, ids)
        self.assertLess(ids.index(b.hwnd), ids.index(a.hwnd), "das zuletzt gezeigte Fenster muss oben stehen")
        info = next(i for i in infos if i.hwnd == a.hwnd)
        self.assertEqual((info.title, info.rect, info.visible, info.process_id), ("Alpha", (50, 50, 250, 170), True, os.getpid()))
        self.assertTrue(info.process_path and "python" in info.process_path.lower(), info.process_path)

    def test_versteckte_fenster_fehlen(self):
        a = self.gtk(50, 50, 200, 120, "Alpha")
        a.verberge()
        self.pumpe(100)
        self.assertNotIn(a.hwnd, [i.hwnd for i in la.LinuxWindowApi().enumerate_windows()])

    def test_der_scanner_nimmt_die_linux_fensterliste_mit_arbeitsplatz_kennung(self):
        a = self.gtk(50, 50, 200, 120, "Alpha")
        scanner = WindowsWindowScanner(la.LinuxWindowApi(), host="vd1", ort="kde1", desktop_label="KDE 1 kompletter Desktop", quelle="x11")
        snap = scanner.scan(frame_ref="kde1://desktop/1", frame_hash="sha256:abc")
        self.assertEqual(snap.default_target_id, "kde1:desktop")
        self.assertEqual(snap.items[0].kind, TargetKind.LINUX_KDE_DESKTOP)
        fenster = next(i for i in snap.items if i.target_id == f"kde1:window:{a.hwnd}")
        self.assertEqual((fenster.kind, fenster.host, fenster.label, fenster.source), (TargetKind.LINUX_WINDOW, "vd1", "Alpha", "x11.window-enum"))
        self.assertEqual([i.z_order for i in snap.items[1:]], list(range(1, len(snap.items))))
        self.assertEqual(snap.items[0].rect, (0, 0) + x.bildschirmgroesse())
        erste = fenster.generation
        zweite = next(i for i in scanner.scan(frame_ref="r", frame_hash="h").items if i.target_id == fenster.target_id).generation
        self.assertEqual(erste, zweite, "dieselbe Generation, solange es dasselbe Fenster ist")

    def test_windows_vorgaben_des_scanners_bleiben(self):
        class Leer:
            def virtual_screen_rect(self):
                return 0, 0, 10, 10

            def enumerate_windows(self):
                return []

        snap = WindowsWindowScanner(Leer()).scan(frame_ref="r", frame_hash="h")
        self.assertEqual((snap.default_target_id, snap.items[0].kind, snap.source), ("windows:desktop", TargetKind.WINDOWS_DESKTOP, "win32.window-enum"))


class AufnahmeTests(XFall):
    def pixel(self, bgra: bytes, breite: int, x_: int, y_: int) -> tuple[int, int, int]:
        i = (y_ * breite + x_) * 4
        return bgra[i + 2], bgra[i + 1], bgra[i]  # als (R, G, B)

    def test_der_desktop_hat_die_richtigen_pixel(self):
        self.farbfenster(100, 100, 200, 150, (255, 0, 0))
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        links, oben, rechts, unten = api.virtual_screen_rect()
        daten = api.capture_bgra((links, oben, rechts, unten))
        self.assertEqual(len(daten), (rechts - links) * (unten - oben) * 4)
        b = rechts - links
        self.assertEqual(self.pixel(daten, b, 150, 150), (255, 0, 0))
        self.assertEqual(daten[3], 255, "Alpha ist voll")

    def test_ein_ausschnitt_mit_versatz_und_rand(self):
        self.farbfenster(100, 100, 200, 150, (0, 0, 255))
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        daten = api.capture_bgra((250, 200, 400, 300))  # rechts unten ragt über das Fenster hinaus
        self.assertEqual(len(daten), 150 * 100 * 4)
        self.assertEqual(self.pixel(daten, 150, 10, 10), (0, 0, 255))  # (260, 210) liegt im Fenster
        self.assertNotEqual(self.pixel(daten, 150, 120, 80), (0, 0, 255))  # (370, 280) liegt dahinter

    def test_ein_verdecktes_fenster_kommt_vollstaendig_ohne_fremde_pixel(self):
        rot = self.farbfenster(100, 100, 200, 150, (255, 0, 0))
        self.farbfenster(150, 120, 200, 150, (0, 255, 0))  # liegt über dem roten und überdeckt es teilweise
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        b = 200
        daten, breite, hoehe = api.capture_window(rot.id)
        self.assertEqual((breite, hoehe), (200, 150))
        alle = {self.pixel(daten, b, i, j) for i in range(0, 200, 7) for j in range(0, 150, 7)}
        self.assertEqual(alle, {(255, 0, 0)}, f"fremde Pixel im Fensterbild: {alle}")
        desktop = api.capture_bgra((0, 0) + x.bildschirmgroesse(), ohne_bridge=False)
        self.assertEqual(self.pixel(desktop, x.bildschirmgroesse()[0], 200, 150), (0, 255, 0), "der Desktop zeigt dort das obere Fenster")

    def test_nicht_eingeblendete_fenster_liefern_kein_bild(self):
        rot = self.farbfenster(100, 100, 200, 150, (255, 0, 0))
        rot.unmap()
        self.anzeige.sync()
        self.assertIsNone(la.LinuxCaptureApi(ausnahmen=lambda: set()).capture_window(rot.id))
        self.assertIsNone(la.LinuxCaptureApi(ausnahmen=lambda: set()).capture_window(0x7FFFFFF))

    def test_die_fenster_der_bridge_fehlen_im_desktopbild(self):
        self.farbfenster(100, 100, 200, 150, (255, 0, 0))
        bridge = self.farbfenster(150, 120, 100, 100, (0, 255, 0))  # ein Fenster der Bridge über dem roten
        api = la.LinuxCaptureApi(ausnahmen=lambda: {bridge.id})
        self.assertTrue(api.umleitung_moeglich)
        self.assertTrue(fl.AUFNAHME_AUSNAHME_MOEGLICH)
        b = x.bildschirmgroesse()[0]
        mit = api.capture_bgra((0, 0) + x.bildschirmgroesse(), ohne_bridge=False)
        ohne = api.capture_bgra((0, 0) + x.bildschirmgroesse())
        self.assertEqual(self.pixel(mit, b, 200, 150), (0, 255, 0))
        self.assertEqual(self.pixel(ohne, b, 200, 150), (255, 0, 0), "darunter liegt das rote Fenster")
        self.assertEqual(self.pixel(ohne, b, 110, 110), (255, 0, 0))

    def test_ein_gtk_fenster_der_bridge_meldet_die_ausnahme_wahrheitsgemaess(self):
        class Gelb(fl.Fenster):
            def zeichnen(self, leinwand):
                leinwand.fuellen(w.rgb(255, 255, 0))

        self.farbfenster(280, 280, 200, 150, (255, 0, 0))
        fl.AUFNAHME_AUSNAHME_MOEGLICH = False
        f = Gelb(300, 300, 100, 60, titel="Bridge")
        f.zeige(aktivieren=False)
        self.fenster.append(f)
        self.pumpe(200)
        self.assertFalse(f.aufnahme_ausnehmen(True), "ohne Adapter wird die Ausnahme nicht versprochen")
        api = la.LinuxCaptureApi()
        self.assertTrue(f.aufnahme_ausnehmen(True))
        self.assertIn(f.hwnd, fl.AUSGENOMMEN)
        b = x.bildschirmgroesse()[0]
        voll = (0, 0) + x.bildschirmgroesse()
        self.assertEqual(self.pixel(api.capture_bgra(voll, ohne_bridge=False), b, 350, 330), (255, 255, 0), "ohne Ausnahme ist das Bridge-Fenster im Bild")
        self.assertEqual(self.pixel(api.capture_bgra(voll), b, 350, 330), (255, 0, 0), "mit Ausnahme sieht man das Fenster darunter")
        f.aufnahme_ausnehmen(False)
        self.assertNotIn(f.hwnd, fl.AUSGENOMMEN)

    def test_unter_einem_compositor_kommt_das_fensterbild_ueber_die_benannte_pixmap(self):
        """Ein Compositor besitzt `_NET_WM_CM_S0` und leitet jedes Fenster selbst um (hier: manuell vom Test); das Fensterbild muss trotzdem
        vollständig und ohne fremde Pixel kommen, nur das Auslassen der Bridge-Fenster im Desktopbild bleibt unmöglich."""
        from Xlib.ext import composite

        rot = self.farbfenster(100, 100, 200, 150, (255, 0, 0))
        gruen = self.farbfenster(150, 120, 200, 150, (0, 255, 0))
        compositor = self.farbfenster(10, 10, 10, 10, (1, 2, 3))
        compositor.set_selection_owner(self.anzeige.intern_atom("_NET_WM_CM_S0"), X.CurrentTime)
        for f in (rot, gruen):
            f.composite_redirect_window(composite.RedirectManual)
        self.anzeige.sync()
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        self.assertFalse(api.umleitung_moeglich)
        self.assertTrue(api.fensterbild_moeglich)
        daten, breite, hoehe = api.capture_window(rot.id)
        self.assertEqual((breite, hoehe), (200, 150))
        alle = {self.pixel(daten, 200, i, j) for i in range(0, 200, 7) for j in range(0, 150, 7)}
        self.assertEqual(alle, {(255, 0, 0)}, f"fremde Pixel im Fensterbild: {alle}")
        self.assertEqual(api._umgeleitet, set(), "unter einem Compositor leitet die Bridge selbst nichts um")

    def test_unter_einem_compositor_der_nur_den_rahmen_umleitet_wird_der_client_ausgeschnitten(self):
        """Xfwm4 leitet den Rahmen (Toplevel) um, nicht das Client-Fenster darin: dessen benannte Pixmap gibt BadMatch. Das Fensterbild
        kommt dann aus dem Rahmen, ausgeschnitten auf den Client, ohne Titelleiste und ohne das, was davor liegt."""
        from Xlib.ext import composite

        rahmen = self.farbfenster(100, 100, 220, 170, (0, 0, 255))  # blau: Rahmen mit Titelleiste
        farbe = 255 << 16
        client = rahmen.create_window(10, 30, 200, 130, 0, self.anzeige.screen().root_depth, X.InputOutput, X.CopyFromParent, background_pixel=farbe)
        client.map()
        self.farbfenster(150, 120, 200, 150, (0, 255, 0))  # liegt über dem Rahmen
        compositor = self.farbfenster(10, 10, 10, 10, (1, 2, 3))
        compositor.set_selection_owner(self.anzeige.intern_atom("_NET_WM_CM_S0"), X.CurrentTime)
        rahmen.composite_redirect_window(composite.RedirectManual)
        self.anzeige.sync()
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        self.assertTrue(api.fensterbild_moeglich)
        daten, breite, hoehe = api.capture_window(client.id)
        self.assertEqual((breite, hoehe), (200, 130))
        alle = {self.pixel(daten, 200, i, j) for i in range(0, 200, 9) for j in range(0, 130, 9)}
        self.assertEqual(alle, {(255, 0, 0)}, f"fremde Pixel (Rahmen, Titelleiste oder Fenster davor): {alle}")

    def test_ohne_compositor_und_ohne_umleitung_gibt_es_kein_fensterbild(self):
        """Ohne Composite-Erweiterung gäbe es weder Umleitung noch Compositor: `fensterbild_moeglich` bleibt falsch (der Rückfall ist dann sichtbar)."""
        api = la.LinuxCaptureApi.__new__(la.LinuxCaptureApi)
        api.umleitung_moeglich = False
        original = la.LinuxCaptureApi._composite_ab_0_2
        la.LinuxCaptureApi._composite_ab_0_2 = staticmethod(lambda: False)
        try:
            self.assertFalse(la.LinuxCaptureApi._compositor_leitet_um())
        finally:
            la.LinuxCaptureApi._composite_ab_0_2 = original

    def test_ein_laufender_compositor_macht_die_ausnahme_unmoeglich_und_das_wird_gemeldet(self):
        fl.AUFNAHME_AUSNAHME_MOEGLICH = False
        fenster = self.farbfenster(10, 10, 10, 10, (1, 2, 3))
        fenster.set_selection_owner(self.anzeige.intern_atom("_NET_WM_CM_S0"), X.CurrentTime)
        self.anzeige.sync()
        api = la.LinuxCaptureApi(ausnahmen=lambda: {fenster.id})
        self.assertFalse(api.umleitung_moeglich)
        self.assertFalse(fl.AUFNAHME_AUSNAHME_MOEGLICH)
        daten = api.capture_bgra((0, 0, 50, 50))  # fällt auf die unveränderte Aufnahme zurück, ohne Fehler
        self.assertEqual(len(daten), 50 * 50 * 4)


class EingabeFall(XFall):
    class Empfaenger(fl.Fenster if DISPLAY else object):
        def __init__(self, *a, **k):
            self.zeichen, self.tasten = [], []
            super().__init__(*a, **k)

        def bei_zeichen(self, code, syskey):
            self.zeichen.append(code)

        def bei_taste(self, vk, lparam, syskey):
            self.tasten.append(vk)

    def empfaenger(self):
        f = self.Empfaenger(200, 200, 300, 100, titel="Eingabefeld")
        f.zeige(aktivieren=False)
        self.fenster.append(f)
        self.pumpe(150)
        xtest.fake_input(self.anzeige, X.MotionNotify, x=250, y=250)  # ohne Fensterverwaltung geht die Tastatur an das Fenster unter dem Zeiger
        self.anzeige.sync()
        self.pumpe(100)
        return f


class EingabeTests(EingabeFall):
    def senden_und_pumpen(self, ereignisse) -> int:
        """Wie im echten Betrieb: gesendet wird aus einem Arbeitsfaden, der GUI-Faden verarbeitet währenddessen die Ereignisse."""
        ergebnis: list[int] = []
        faden = threading.Thread(target=lambda: ergebnis.append(la.xtest_senden(ereignisse)))
        faden.start()
        while faden.is_alive():
            self.app.pumpen(20)
        self.pumpe(300)
        return ergebnis[0]

    def tippen(self, text: str):
        f = self.empfaenger()
        n = self.senden_und_pumpen(text_ereignisse(text))
        return f, n

    def test_ascii_und_satzzeichen(self):
        f, n = self.tippen("Hallo, Welt! 42 (ok) a/b?")
        self.assertEqual("".join(chr(c) for c in f.zeichen), "Hallo, Welt! 42 (ok) a/b?")

    def test_umlaute_sonderzeichen_und_emoji(self):
        text = "Grüße äöüß € ✓ 😀 日本"
        f, n = self.tippen(text)
        self.assertEqual("".join(chr(c) for c in f.zeichen), text)

    def test_die_belegung_wird_nach_dem_tippen_wiederhergestellt(self):
        vorher = self.anzeige.get_keyboard_mapping(self.anzeige.display.info.min_keycode, 255 - self.anzeige.display.info.min_keycode + 1)
        self.tippen("😀✓")
        nachher = self.anzeige.get_keyboard_mapping(self.anzeige.display.info.min_keycode, 255 - self.anzeige.display.info.min_keycode + 1)
        self.assertEqual(list(vorher), list(nachher))

    def test_tastenkombination_kommt_als_tasten_an(self):
        f = self.empfaenger()
        self.senden_und_pumpen(kombination_ereignisse(Kombination(w.MOD_CONTROL | w.MOD_SHIFT, 0x4B)))
        for vk in (0x11, 0x10, 0x4B):
            self.assertIn(vk, f.tasten, f.tasten)
        self.assertLess(f.tasten.index(0x11), f.tasten.index(0x4B))

    def test_zeilenumbruch_wird_zu_leerzeichen_und_enter_ist_ein_enter(self):
        f, _n = self.tippen("a\nb")
        self.assertEqual("".join(chr(c) for c in f.zeichen), "a b")
        f.zeichen.clear()
        self.senden_und_pumpen([(w.VK_RETURN, 0, 0), (w.VK_RETURN, 0, la.KEYEVENTF_KEYUP)])
        self.assertEqual(f.zeichen, [13])

    def test_unbekannte_taste_wird_nicht_vorgetaeuscht(self):
        self.assertEqual(la.xtest_senden([(0xFF, 0, 0)]), 0)

    def test_der_schreibe_auftrag_der_haende_laeuft_bis_ins_eingabefeld(self):
        f = self.empfaenger()
        ergebnis_liste: list = []
        faden = threading.Thread(target=lambda: ergebnis_liste.append(Haende(senden=la.xtest_senden).schreiben(
            "Grüße von der Raute 😀", Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x48), feld_hat_fokus=lambda: True,
            gesperrt=lambda: False, feld_schliessen=lambda: None)))
        faden.start()
        while faden.is_alive():
            self.app.pumpen(20)
        self.pumpe(400)
        ergebnis = ergebnis_liste[0]
        self.assertTrue(ergebnis.ok, ergebnis)
        self.assertEqual("".join(chr(c) for c in f.zeichen if c >= 32), "Grüße von der Raute 😀")
        self.assertIn(13, f.zeichen, "am Ende kommt Enter")
        self.assertIn(0x48, f.tasten, "zuerst die Tastenkombination der Raute")

    def test_gesperrt_tippt_nichts(self):
        f = self.empfaenger()
        ergebnis = Haende(senden=la.xtest_senden).schreiben(
            "x", Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x48), feld_hat_fokus=lambda: True, gesperrt=lambda: True, feld_schliessen=lambda: None)
        self.pumpe(200)
        self.assertEqual((ergebnis.ok, ergebnis.grund, f.zeichen, f.tasten), (False, "gesperrt", [], []))


class NotAusTests(EingabeFall):
    def taste(self, keysym):
        d = xdisplay.Display()
        code = d.keysym_to_keycode(keysym)
        xtest.fake_input(d, X.KeyPress, code)
        xtest.fake_input(d, X.KeyRelease, code)
        d.sync()
        d.close()

    def test_f12_loest_aus_auch_wenn_der_gui_faden_blockiert_ist(self):
        f = self.empfaenger()
        not_aus = NotAus()
        hook = la.LinuxNotAusHook(not_aus)
        self.assertTrue(hook.start(), hook.fehler)
        self.addCleanup(hook.stop)
        self.taste(XK.XK_F1)
        time.sleep(0.2)
        self.assertFalse(not_aus.aktiv, "eine andere Taste darf nichts auslösen")
        sender = threading.Thread(target=lambda: self.taste(XK.XK_F12))
        sender.start()
        beginn = time.monotonic()
        while not not_aus.aktiv and time.monotonic() - beginn < 3:
            time.sleep(0.005)  # der GUI-Faden (dieser) pumpt währenddessen nichts
        sender.join()
        self.assertTrue(not_aus.aktiv)
        self.assertEqual(not_aus.grund, "F12")
        self.pumpe(200)
        self.assertIn(0x7B, f.tasten, "die Taste wird nicht geschluckt: das Fenster bekommt sie auch")

    def test_nach_dem_beenden_loest_nichts_mehr_aus(self):
        not_aus = NotAus()
        hook = la.LinuxNotAusHook(not_aus)
        self.assertTrue(hook.start(), hook.fehler)
        hook.stop()
        self.assertFalse(hook.installiert)
        self.taste(XK.XK_F12)
        time.sleep(0.3)
        self.assertFalse(not_aus.aktiv)

    def test_andere_taste_waehlbar(self):
        not_aus = NotAus()
        hook = la.LinuxNotAusHook(not_aus, vk=0x7A, name="F11")
        self.assertTrue(hook.start(), hook.fehler)
        self.addCleanup(hook.stop)
        self.taste(XK.XK_F11)
        time.sleep(0.3)
        self.assertEqual((not_aus.aktiv, not_aus.grund), (True, "F11"))


class QuelleTests(XFall):
    def test_offene_programme_ohne_die_eigenen_und_der_bildschirm(self):
        self.gtk(50, 50, 200, 120, "Alpha Fenster")
        quelle = la.LinuxQuelle()
        programme = quelle.offene_programme()
        self.assertTrue(any(p.titel == "Alpha Fenster" and "python" in p.programm for p in programme), programme)
        self.assertEqual([p for p in quelle.offene_programme(ohne_pid=os.getpid()) if p.titel == "Alpha Fenster"], [])
        self.assertEqual(quelle.bildschirm(), (0, 0) + x.bildschirmgroesse())

    def test_ohne_fensterverwaltung_gibt_es_keinen_vordergrund_aber_auch_keinen_fehler(self):
        self.assertIn(type(la.LinuxQuelle().vordergrund()).__name__, ("NoneType", "Vordergrund"))


@unittest.skipUnless(shutil.which("openbox"), "openbox fehlt")
class FensterverwalterTests(XFall):
    """Mit einem echten Fensterverwalter (EWMH): Stapelliste und aktives Fenster, wie bei KDE."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # eigene, leere Einstellungen: die mitgelieferte Regel „Fenster maximieren“ dieses Containers würde sonst jedes Fenster auf Bildschirmgröße ziehen
        cls.rc = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False)
        cls.rc.write('<?xml version="1.0"?><openbox_config xmlns="http://openbox.org/3.4/rc"><applications/></openbox_config>')
        cls.rc.close()
        cls.wm = subprocess.Popen(["openbox", "--sm-disable", "--config-file", cls.rc.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)

    @classmethod
    def tearDownClass(cls):
        cls.wm.terminate()
        try:
            cls.wm.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.wm.kill()
        os.unlink(cls.rc.name)

    def test_stapelreihenfolge_und_vordergrund_kommen_vom_fensterverwalter(self):
        a = self.gtk(50, 50, 200, 120, "WM Alpha")
        b = self.gtk(300, 90, 200, 120, "WM Beta")
        self.pumpe(300)
        ids = [i.hwnd for i in la.LinuxWindowApi().enumerate_windows()]
        self.assertIn(a.hwnd, ids)
        self.assertIn(b.hwnd, ids)
        a.fokus_erzwingen()
        self.pumpe(400)
        vorn = la.LinuxQuelle().vordergrund()
        self.assertIsNotNone(vorn)
        self.assertEqual(vorn.titel, "WM Alpha")
        self.assertEqual(vorn.pid, os.getpid())
        rect = x.fenster_rechteck(a.hwnd)
        self.assertEqual((rect[2] - rect[0], rect[3] - rect[1]), (200, 120), "die Fensterbeschreibung nennt das Innenmaß, nicht den Rahmen")


class DateiwahlTests(XFall):
    def test_abbruch_liefert_none(self):
        from gi.repository import GLib, Gtk

        self.assertIsNone(la.datei_waehlen(0, vorab=lambda d: GLib.timeout_add(150, lambda: d.response(Gtk.ResponseType.CANCEL) or False)))

    def test_gewaehlte_datei_wird_geliefert(self):
        from gi.repository import GLib, Gtk

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as datei:
            pfad = datei.name

        def vorab(dialog):
            dialog.set_filename(pfad)
            GLib.timeout_add(150, lambda: dialog.response(Gtk.ResponseType.OK) or False)

        self.assertEqual(la.datei_waehlen(0, vorab=vorab), pfad)
        os.unlink(pfad)


if __name__ == "__main__":
    unittest.main()
