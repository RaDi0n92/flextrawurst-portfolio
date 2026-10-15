"""Tests für koerper/fenster.py: die Win32-Gating-Weiche und die reine Nachrichtenverteilung.

`Schrift`, `Leinwand`, `Fenster` und `Anwendung` brauchen für ihren Konstruktor echtes (oder Wine-)Windows und werden hier
nicht instanziiert. Die Verteil-Logik in `Fenster.nachricht()` und im modulweiten `_wndproc` ist dagegen reines Python –
sie route Nachrichten an die passenden `bei_*`-Handler, ohne selbst eine DLL anzufassen. Um sie ohne Windows zu prüfen,
wird ein `Fenster` per `object.__new__` gebaut (der Konstruktor wird also bewusst übersprungen) und mit genau den
Attributen versehen, die `nachricht()` braucht; jede Methode, die tatsächlich `user32`/`gdi32` anfassen würde
(`leinwand_anpassen`, `treffer`-Aufrufer außerhalb des Tests), wird für den jeweiligen Test gezielt ersetzt.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from augen_haende_bridge.koerper import fenster
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.fenster import Anwendung, Fenster, Leinwand, Schrift


class GatingTests(unittest.TestCase):
    def test_schrift_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            Schrift(hdc=1, name="Consolas", hoehe_px=16)

    def test_leinwand_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            Leinwand(100, 100)

    def test_fenster_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            Fenster(0, 0, 100, 100)

    def test_anwendung_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            Anwendung()


def _spy_fenster() -> tuple[Fenster, Mock]:
    """Ein Fenster ohne echten Konstruktor, mit einem Mock, der jeden bei_*-Aufruf aufzeichnet."""
    f = object.__new__(Fenster)
    f.hwnd = 42
    f.leinwand = None
    f._timer = {}
    spion = Mock()
    for name in ("bei_groesse", "bei_zerstoert", "bei_timer", "bei_maus_runter", "bei_maus_hoch", "bei_doppelklick",
                 "bei_rechtsklick", "bei_maus_bewegt", "bei_rad", "bei_taste", "bei_zeichen", "bei_hotkey",
                 "bei_fokus", "bei_maus_verloren", "bei_dpi", "bei_nachricht", "treffer", "leinwand_anpassen"):
        setattr(f, name, getattr(spion, name))
    return f, spion


class NachrichtVerteilungTests(unittest.TestCase):
    def test_wm_erasebkgnd_meldet_selbst_gezeichnet(self) -> None:
        f, _ = _spy_fenster()
        self.assertEqual(f.nachricht(w.WM_ERASEBKGND, 0, 0), 1)

    def test_wm_size_ruft_leinwand_anpassen_und_bei_groesse_mit_der_clientgroesse(self) -> None:
        f, spion = _spy_fenster()
        f.clientgroesse = Mock(return_value=(640, 480))
        self.assertIsNone(f.nachricht(w.WM_SIZE, 0, 0))
        spion.leinwand_anpassen.assert_called_once_with()
        spion.bei_groesse.assert_called_once_with(640, 480)

    def test_wm_timer_ruft_registrierten_aufruf_statt_bei_timer(self) -> None:
        f, spion = _spy_fenster()
        eigener_aufruf = Mock()
        f._timer[7] = eigener_aufruf
        self.assertEqual(f.nachricht(w.WM_TIMER, 7, 0), 0)
        eigener_aufruf.assert_called_once_with()
        spion.bei_timer.assert_not_called()

    def test_wm_timer_ohne_registrierten_aufruf_faellt_auf_bei_timer_zurueck(self) -> None:
        f, spion = _spy_fenster()
        self.assertEqual(f.nachricht(w.WM_TIMER, 9, 0), 0)
        spion.bei_timer.assert_called_once_with(9)

    def test_wm_destroy_ruft_bei_zerstoert_und_gibt_eine_vorhandene_leinwand_frei(self) -> None:
        f, spion = _spy_fenster()
        leinwand = Mock()
        f.leinwand = leinwand
        self.assertIsNone(f.nachricht(w.WM_DESTROY, 0, 0))
        spion.bei_zerstoert.assert_called_once_with()
        leinwand.freigeben.assert_called_once_with()
        self.assertIsNone(f.leinwand)

    def test_wm_destroy_ohne_leinwand_bricht_nicht(self) -> None:
        f, spion = _spy_fenster()
        self.assertIsNone(f.leinwand)
        self.assertIsNone(f.nachricht(w.WM_DESTROY, 0, 0))
        spion.bei_zerstoert.assert_called_once_with()

    def test_maustasten_dekodieren_vorzeichenbehaftete_koordinaten(self) -> None:
        f, spion = _spy_fenster()
        spion.bei_maus_runter.return_value = 0
        lparam = w.make_lparam(-3, 5)
        self.assertEqual(f.nachricht(w.WM_LBUTTONDOWN, 0x11, lparam), 0)
        spion.bei_maus_runter.assert_called_once_with(-3, 5, 0x11)

    def test_maus_hoch_doppelklick_und_rechtsklick_routen_getrennt(self) -> None:
        f, spion = _spy_fenster()
        lparam = w.make_lparam(1, 2)
        f.nachricht(w.WM_LBUTTONUP, 0, lparam)
        f.nachricht(w.WM_LBUTTONDBLCLK, 0, lparam)
        f.nachricht(w.WM_RBUTTONUP, 0, lparam)
        spion.bei_maus_hoch.assert_called_once_with(1, 2, 0)
        spion.bei_doppelklick.assert_called_once_with(1, 2, 0)
        spion.bei_rechtsklick.assert_called_once_with(1, 2, 0)

    def test_mausrad_zerlegt_delta_und_koordinaten_getrennt(self) -> None:
        f, spion = _spy_fenster()
        lparam = w.make_lparam(10, 20)
        wparam = w.make_lparam(0x0001, 120)  # loword = Tastenflags, hiword = Delta (WHEEL_DELTA)
        f.nachricht(w.WM_MOUSEWHEEL, wparam, lparam)
        spion.bei_rad.assert_called_once_with(120, 10, 20, 0x0001)

    def test_tasten_und_zeichen_unterscheiden_system_und_normaltaste(self) -> None:
        f, spion = _spy_fenster()
        f.nachricht(w.WM_KEYDOWN, w.VK_RETURN, 0)
        f.nachricht(w.WM_SYSKEYDOWN, w.VK_F1, 0)
        f.nachricht(w.WM_CHAR, ord("a"), 0)
        f.nachricht(w.WM_SYSCHAR, ord("b"), 0)
        spion.bei_taste.assert_any_call(w.VK_RETURN, 0, False)
        spion.bei_taste.assert_any_call(w.VK_F1, 0, True)
        spion.bei_zeichen.assert_any_call(ord("a"), False)
        spion.bei_zeichen.assert_any_call(ord("b"), True)

    def test_hotkey_fokus_und_verlorene_maus_werden_weitergereicht(self) -> None:
        f, spion = _spy_fenster()
        f.nachricht(w.WM_HOTKEY, 3, 0)
        f.nachricht(w.WM_KILLFOCUS, 0, 0)
        f.nachricht(w.WM_SETFOCUS, 0, 0)
        f.nachricht(w.WM_CAPTURECHANGED, 0, 0)
        spion.bei_hotkey.assert_called_once_with(3)
        spion.bei_fokus.assert_any_call(False)
        spion.bei_fokus.assert_any_call(True)
        spion.bei_maus_verloren.assert_called_once_with()

    def test_nchittest_liefert_das_ergebnis_von_treffer_zurueck(self) -> None:
        f, spion = _spy_fenster()
        spion.treffer.return_value = w.HTCAPTION
        lparam = w.make_lparam(50, 60)
        self.assertEqual(f.nachricht(w.WM_NCHITTEST, 0, lparam), w.HTCAPTION)
        spion.treffer.assert_called_once_with(50, 60)

    def test_dpichanged_liest_die_neue_dpi_aus_dem_hiword(self) -> None:
        f, spion = _spy_fenster()
        wparam = w.make_lparam(0, 144)
        f.nachricht(w.WM_DPICHANGED, wparam, 0)
        spion.bei_dpi.assert_called_once_with(144)

    def test_unbekannte_nachricht_faellt_auf_bei_nachricht_zurueck(self) -> None:
        f, spion = _spy_fenster()
        spion.bei_nachricht.return_value = 123
        self.assertEqual(f.nachricht(0x9999, 1, 2), 123)
        spion.bei_nachricht.assert_called_once_with(0x9999, 1, 2)

    def test_default_handler_geben_keine_aktion_vor(self) -> None:
        f = object.__new__(Fenster)
        self.assertIsNone(f.bei_groesse(1, 1))
        self.assertIsNone(f.bei_zerstoert())
        self.assertIsNone(f.bei_timer(1))
        self.assertIsNone(f.bei_maus_runter(0, 0, 0))
        self.assertIsNone(f.bei_hotkey(1))
        self.assertIsNone(f.bei_nachricht(1, 2, 3))
        self.assertIsNone(f.treffer(0, 0))


class WndProcTests(unittest.TestCase):
    """Weißkasten-Test des modulweiten Dispatchers; räumt seinen globalen Zustand danach wieder auf."""

    def setUp(self) -> None:
        self._alte_fenster = dict(fenster._fenster)
        self._alte_entstehend = list(fenster._entstehend)
        fenster._fenster.clear()
        fenster._entstehend.clear()

    def tearDown(self) -> None:
        fenster._fenster.clear()
        fenster._fenster.update(self._alte_fenster)
        fenster._entstehend.clear()
        fenster._entstehend.extend(self._alte_entstehend)

    def test_ein_entstehendes_fenster_erhaelt_seinen_hwnd_beim_ersten_wndproc_aufruf(self) -> None:
        f, spion = _spy_fenster()
        f.hwnd = None
        fenster._entstehend.append(f)
        with patch.object(w, "user32", Mock()):
            ergebnis = fenster._wndproc(hwnd=777, msg=w.WM_ERASEBKGND, wparam=0, lparam=0)
        self.assertEqual(f.hwnd, 777)
        self.assertIs(fenster._fenster[777], f)
        self.assertEqual(ergebnis, 1)

    def test_ausnahme_im_handler_geht_an_anwendung_fehler_statt_die_schleife_zu_sprengen(self) -> None:
        f, spion = _spy_fenster()
        fenster._fenster[42] = f
        spion.bei_hotkey.side_effect = RuntimeError("kaputt")
        aufgezeichnet = []
        fake_user32 = Mock(DefWindowProcW=Mock(return_value=0))
        with patch.object(Anwendung, "fehler_aufruf", lambda wo, e: aufgezeichnet.append((wo, e))), \
             patch.object(w, "user32", fake_user32):
            ergebnis = fenster._wndproc(hwnd=42, msg=w.WM_HOTKEY, wparam=1, lparam=0)
        self.assertEqual(len(aufgezeichnet), 1)
        self.assertEqual(aufgezeichnet[0][0], "fenster")
        self.assertIsInstance(aufgezeichnet[0][1], RuntimeError)
        fake_user32.DefWindowProcW.assert_called_once_with(42, w.WM_HOTKEY, 1, 0)
        self.assertEqual(ergebnis, 0)

    def test_ein_none_ergebnis_faellt_durch_zu_defwindowprocw(self) -> None:
        f, spion = _spy_fenster()
        fenster._fenster[42] = f
        spion.bei_hotkey.return_value = None
        with patch.object(w, "user32", Mock(DefWindowProcW=Mock(return_value=99))):
            ergebnis = fenster._wndproc(hwnd=42, msg=w.WM_HOTKEY, wparam=1, lparam=0)
        self.assertEqual(ergebnis, 99)

    def test_wm_destroy_entfernt_das_fenster_aus_der_registrierung(self) -> None:
        f, spion = _spy_fenster()
        fenster._fenster[42] = f
        with patch.object(w, "user32", Mock(DefWindowProcW=Mock(return_value=0))):
            fenster._wndproc(hwnd=42, msg=w.WM_DESTROY, wparam=0, lparam=0)
        self.assertNotIn(42, fenster._fenster)

    def test_unbekannter_hwnd_ohne_entstehendes_fenster_geht_direkt_an_defwindowprocw(self) -> None:
        with patch.object(w, "user32", Mock(DefWindowProcW=Mock(return_value=55))):
            ergebnis = fenster._wndproc(hwnd=999, msg=w.WM_ERASEBKGND, wparam=0, lparam=0)
        self.assertEqual(ergebnis, 55)


if __name__ == "__main__":
    unittest.main()
