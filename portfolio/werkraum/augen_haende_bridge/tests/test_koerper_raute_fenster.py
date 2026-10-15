"""Tests für koerper/raute_fenster.py: Klickdurchlässigkeit mit Modifikator-Bedienung, Status, Ziehen/Klick/Menü.

`RauteFenster.__init__` baut ein echtes Win32-Fenster samt Form und Schrift und braucht Windows oder Wine — das
prüft `probes/koerper_smoketest.py`. Die Logik hier läuft per `object.__new__`-Fixture ohne Konstruktor.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.raute_fenster import (
    GROESSE,
    TIMER_MODIFIKATOR,
    RauteFenster,
    abmessung,
    beschriftung,
    exstil_fuer,
    raute_text,
    status_farbe,
)


def _baue(**overrides) -> RauteFenster:
    f = object.__new__(RauteFenster)
    f.name = "codex"
    f.farbe_hex = "#FFD600"
    f.farbe = w.rgb_hex(f.farbe_hex)
    f.kuerzel = "CO"
    f.hotkey = "F14"
    f.status = "offline"
    f._modifikator_vk = w.VK_CONTROL
    f._klick = Mock()
    f._menue = Mock()
    f._verschoben = Mock()
    f._nachricht_gesendet = Mock()
    f.letzte_nachricht = ""
    f.bedienbar = True
    f.groesse = GROESSE
    f.breite = GROESSE
    f._modifikator = None
    f.deckkraft = 255
    f.hotkey = "F14"
    f._ziehanker = None
    f._fenster_anker = None
    f._ziehen = False
    f.f_kuerzel = Mock()
    f.hwnd = 999
    f.leinwand = None
    f._timer = {}
    f.erfasse_maus = Mock()
    f.gib_maus_frei = Mock()
    f.maus_position = Mock(return_value=(500, 500))
    f.rechteck = Mock(return_value=(400, 400, 400 + GROESSE, 400 + GROESSE))
    f.verschiebe = Mock()
    f.neu_zeichnen = Mock()
    for name, wert in overrides.items():
        setattr(f, name, wert)
    return f


class GroesseTests(unittest.TestCase):
    def test_gezeichnet_wird_in_der_aktuellen_breite_und_hoehe(self) -> None:
        for groesse, breite in ((28, 60), (52, 160), (96, 300), (144, 400)):
            f = _baue(groesse=groesse, breite=breite)
            f.f_kuerzel = Mock(zellhoehe=20)
            f.f_kuerzel.breite.return_value = 10
            leinwand = Mock()
            f.zeichnen(leinwand)
            punkte = leinwand.polygon.call_args.args[0]
            self.assertEqual(punkte, [(breite // 2, 0), (breite, groesse // 2), (breite // 2, groesse), (0, groesse // 2)])

    def test_beschriftung_sitzt_in_der_mitte_der_raute(self) -> None:
        f = _baue(groesse=96, breite=300)
        f.f_kuerzel = Mock(zellhoehe=20)
        f.f_kuerzel.breite.return_value = 100
        leinwand = Mock()
        f.zeichnen(leinwand)
        x, y, text = leinwand.text.call_args.args[0:3]
        self.assertEqual((x, y), (150 - 50, 48 - 10))
        self.assertEqual(text, "codex [F14]")

    def test_raute_ist_nicht_gleichseitig(self) -> None:
        breite, hoehe = abmessung(52, 110, 18)
        self.assertGreater(breite, hoehe * 1.8 - 1)

    def test_text_passt_in_die_raute(self) -> None:
        for groesse, textbreite, texthoehe in ((52, 110, 18), (52, 40, 18), (96, 240, 34), (28, 60, 11)):
            breite, hoehe = abmessung(groesse, textbreite, texthoehe)
            self.assertLessEqual(textbreite / breite + texthoehe / hoehe, 1.0, (groesse, textbreite))

    def test_langer_name_wird_gekuerzt_und_hotkey_bleibt_sichtbar(self) -> None:
        self.assertEqual(raute_text("Claude-Host", "F13"), "Claude-Host [F13]")
        t = raute_text("EinSehrLangerAgentenname", "Strg+Alt+F5")
        self.assertTrue(t.endswith("[Strg+Alt+F5]") and "…" in t)
        self.assertEqual(raute_text("Codex", None), "Codex")


class ReineFunktionenTests(unittest.TestCase):
    def test_bedienbar_nimmt_nur_das_transparent_bit_weg(self) -> None:
        exstil = w.WS_EX_TOPMOST | w.WS_EX_LAYERED | w.WS_EX_TRANSPARENT
        self.assertEqual(exstil_fuer(exstil, True), w.WS_EX_TOPMOST | w.WS_EX_LAYERED)

    def test_klickdurchlaessig_setzt_das_transparent_bit(self) -> None:
        self.assertEqual(exstil_fuer(w.WS_EX_TOPMOST, False), w.WS_EX_TOPMOST | w.WS_EX_TRANSPARENT)

    def test_beschriftung_wie_in_erleben(self) -> None:
        self.assertEqual(beschriftung("Codex", "F14"), "◆ Codex [F14]")
        self.assertEqual(beschriftung("Codex", None), "◆ Codex")

    def test_statusfarben_und_unbekannter_status_ist_fehler(self) -> None:
        self.assertEqual(status_farbe("verbunden"), stil.FARBE_OK)
        self.assertEqual(status_farbe("offline"), stil.FARBE_TEXT_GEDAEMPFT)
        self.assertEqual(status_farbe("irgendwas"), stil.FARBE_FEHLER)


class GatingTests(unittest.TestCase):
    def test_konstruktor_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            RauteFenster(0, 0, name="codex")

    def test_umriss_ist_eine_raute_aus_vier_ecken(self) -> None:
        mitte = GROESSE // 2
        self.assertEqual(RauteFenster.umriss(), [(mitte, 0), (GROESSE, mitte), (mitte, GROESSE), (0, mitte)])


class ModifikatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.user32 = Mock()
        self.user32.GetWindowLongPtrW.return_value = w.WS_EX_TOPMOST | w.WS_EX_LAYERED | w.WS_EX_TRANSPARENT
        patcher = patch.object(w, "user32", self.user32)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_gedrueckter_modifikator_macht_die_raute_bedienbar(self) -> None:
        f = _baue(bedienbar=False)
        self.user32.GetAsyncKeyState.return_value = -32768  # 0x8000 als vorzeichenbehafteter short
        f.bei_timer(TIMER_MODIFIKATOR)
        self.assertTrue(f.bedienbar)
        self.user32.GetAsyncKeyState.assert_called_with(w.VK_CONTROL)
        self.user32.SetWindowLongPtrW.assert_called_once_with(999, w.GWL_EXSTYLE, w.WS_EX_TOPMOST | w.WS_EX_LAYERED)

    def test_losgelassener_modifikator_macht_sie_wieder_klickdurchlaessig(self) -> None:
        f = _baue(bedienbar=True)
        self.user32.GetAsyncKeyState.return_value = 0
        self.user32.GetWindowLongPtrW.return_value = w.WS_EX_TOPMOST | w.WS_EX_LAYERED
        f.bei_timer(TIMER_MODIFIKATOR)
        self.assertFalse(f.bedienbar)
        self.user32.SetWindowLongPtrW.assert_called_once_with(
            999, w.GWL_EXSTYLE, w.WS_EX_TOPMOST | w.WS_EX_LAYERED | w.WS_EX_TRANSPARENT)

    def test_waehrend_eines_zugs_bleibt_sie_bedienbar(self) -> None:
        f = _baue(bedienbar=True, _ziehanker=(500, 500))
        self.user32.GetAsyncKeyState.return_value = 0
        f.bei_timer(TIMER_MODIFIKATOR)
        self.assertTrue(f.bedienbar)
        self.user32.SetWindowLongPtrW.assert_not_called()

    def test_unveraenderter_zustand_fasst_den_fensterstil_nicht_an(self) -> None:
        f = _baue(bedienbar=False)
        self.user32.GetAsyncKeyState.return_value = 0
        f.bei_timer(TIMER_MODIFIKATOR)
        self.user32.SetWindowLongPtrW.assert_not_called()


class ZiehenKlickMenueTests(unittest.TestCase):
    def test_ohne_modifikator_faengt_die_raute_keinen_klick(self) -> None:
        f = _baue(bedienbar=False)
        f.bei_maus_runter(10, 10, 0)
        f.bei_maus_hoch(10, 10, 0)
        f.erfasse_maus.assert_not_called()
        f._klick.assert_not_called()

    def test_klick_ohne_bewegung_loest_den_klick_callback_aus(self) -> None:
        f = _baue()
        f.bei_maus_runter(10, 10, 0)
        f.bei_maus_hoch(10, 10, 0)
        f._klick.assert_called_once_with()
        f._verschoben.assert_not_called()

    def test_bewegung_ueber_der_schwelle_zieht_statt_zu_klicken(self) -> None:
        f = _baue(maus_position=Mock(side_effect=[(500, 500), (520, 500)]))
        f.bei_maus_runter(10, 10, 0)
        f.bei_maus_bewegt(0, 0, 0x0001)
        f.verschiebe.assert_called_once_with(420, 400)
        f._verschoben.assert_called_once_with(420, 400)
        f.bei_maus_hoch(0, 0, 0)
        f._klick.assert_not_called()

    def test_bewegung_unterhalb_der_schwelle_zieht_noch_nicht(self) -> None:
        f = _baue(maus_position=Mock(side_effect=[(500, 500), (502, 500)]))
        f.bei_maus_runter(10, 10, 0)
        f.bei_maus_bewegt(0, 0, 0x0001)
        f.verschiebe.assert_not_called()

    def test_verlorene_maus_erfassung_setzt_den_ziehzustand_zurueck(self) -> None:
        f = _baue()
        f.bei_maus_runter(10, 10, 0)
        f.bei_maus_verloren()
        self.assertIsNone(f._ziehanker)
        f.bei_maus_hoch(10, 10, 0)
        f._klick.assert_not_called()  # kein Runter mehr offen, also auch kein Klick

    def test_rechtsklick_mit_modifikator_oeffnet_das_menue_an_der_bildschirmstelle(self) -> None:
        f = _baue()
        f.bei_rechtsklick(5, 7, 0)
        f._menue.assert_called_once_with(405, 407)

    def test_rechtsklick_ohne_modifikator_oeffnet_nichts(self) -> None:
        f = _baue(bedienbar=False)
        f.bei_rechtsklick(5, 7, 0)
        f._menue.assert_not_called()


class StatusUndSprechenTests(unittest.TestCase):
    def test_setze_status_zeichnet_nur_bei_aenderung_neu(self) -> None:
        f = _baue()
        f.setze_status("verbunden")
        f.setze_status("verbunden")
        self.assertEqual(f.status, "verbunden")
        f.neu_zeichnen.assert_called_once_with()

    def test_sagen_merkt_sich_die_nachricht_und_meldet_sie(self) -> None:
        f = _baue()
        f.sagen("Shader kompiliert!")
        self.assertEqual(f.letzte_nachricht, "Shader kompiliert!")
        f._nachricht_gesendet.assert_called_once_with("Shader kompiliert!")

    def test_bei_zerstoert_gibt_die_schrift_frei(self) -> None:
        f = _baue()
        schrift = f.f_kuerzel
        f.bei_zerstoert()
        schrift.freigeben.assert_called_once_with()
        self.assertIsNone(f.f_kuerzel)


if __name__ == "__main__":
    unittest.main()
