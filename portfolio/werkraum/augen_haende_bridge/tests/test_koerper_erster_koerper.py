"""Tests für koerper/erster_koerper.py: die Verdrahtung zwischen Raute, Terminal und Nachricht (den Chat hält die Anwendung).

Alle vier Fensterklassen sind injizierbar (`raute_klasse` usw.) — genau deshalb ist diese Verdrahtung vollständig
ohne Windows/Wine testbar, obwohl jede einzelne Fensterklasse selbst `require_windows()` verlangt.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper.erster_koerper import (
    MENUE_AGENT_BEENDEN,
    MENUE_BRIDGE_BEENDEN,
    MENUE_GROESSER,
    MENUE_RAUTE_REGEL,
    MENUE_TERMINAL_DURCHKLICK,
    MENUE_TERMINAL_REGEL,
    MENUE_KLEINER,
    MENUE_TRANSPARENZ,
    MENUE_NOTAUS,
    MENUE_STATUS,
    MENUE_TERMINAL,
    ErsterKoerper,
)
from augen_haende_bridge.koerper import stil


def _bauen(**overrides):
    raute_instance = Mock()
    raute_instance.rechteck.return_value = (100, 100, 148, 148)
    terminal_instance = Mock()
    raute_klasse = Mock(return_value=raute_instance)
    terminal_klasse = Mock(return_value=terminal_instance)
    banner_klasse = Mock(side_effect=lambda **kwargs: Mock())
    ticker_klasse = Mock(side_effect=lambda **kwargs: Mock())
    gesprochen = Mock()
    kwargs = dict(name="codex", ort="vd1", raute_klasse=raute_klasse, terminal_klasse=terminal_klasse,
                  banner_klasse=banner_klasse, ticker_klasse=ticker_klasse, gesprochen=gesprochen,
                  scanner=Mock(), capture=Mock(), ziel_rechteck=lambda: ZIEL, jetzt_ms=lambda: 5000)
    kwargs.update(overrides)
    koerper = ErsterKoerper(**kwargs)
    # Index 5 ist die Banner-Klasse; die Ticker-Klasse steht am Körper selbst (koerper._ticker_klasse).
    return koerper, raute_klasse, raute_instance, terminal_klasse, terminal_instance, banner_klasse, gesprochen


ZIEL = (0, 0, 1920, 1040)


class KonstruktionTests(unittest.TestCase):
    def test_scanner_wird_nachtraeglich_am_terminal_verbunden(self) -> None:
        _koerper, _rk, _ri, _tk, terminal_instance, _nk, _ck = _bauen()
        terminal_instance.scanner_verbinden.assert_called_once()
        verbundener_callback = terminal_instance.scanner_verbinden.call_args.args[0]
        self.assertTrue(callable(verbundener_callback))

    def test_raute_bekommt_die_koerpereigenen_callbacks(self) -> None:
        koerper, raute_klasse, _ri, _tk, _ti, _nk, _ck = _bauen()
        aufruf = raute_klasse.call_args
        self.assertNotIn("klick_gewuenscht", aufruf.kwargs)  # die Raute gehört dem Agenten, sie hat keinen Klick-Zweck
        self.assertEqual(aufruf.kwargs["nachricht_gesendet"], koerper._raute_hat_gesprochen)

    def test_farbe_hex_ist_ohne_angabe_deterministisch_aus_den_agentenfarben(self) -> None:
        koerper1, *_ = _bauen(farbe_hex=None)
        koerper2, *_ = _bauen(farbe_hex=None)
        self.assertEqual(koerper1.farbe_hex, koerper2.farbe_hex)
        self.assertIn(koerper1.farbe_hex, stil.AGENTENFARBEN)

    def test_farbe_hex_wird_uebernommen_wenn_angegeben(self) -> None:
        koerper, *_ = _bauen(farbe_hex="#123456")
        self.assertEqual(koerper.farbe_hex, "#123456")


class RauteSprichtTests(unittest.TestCase):
    def test_eine_nachricht_erzeugt_nur_den_ticker_neben_der_raute_und_kein_banner(self) -> None:
        koerper, _rk, _ri, _tk, _ti, banner_klasse, _ck = _bauen()
        koerper._raute_hat_gesprochen("Shader kompiliert!")

        banner_klasse.assert_not_called()  # Daniel 2026-10-04: kein zweites, größeres Textfeld im Bild
        self.assertIsNone(koerper.banner)
        koerper._ticker_klasse.assert_called_once_with(text="Shader kompiliert!", farbe_hex=koerper.farbe_hex,
                                                       raute_rechteck=(100, 100, 148, 148),
                                                       geschlossen=koerper._ticker_geschlossen, grenzen=koerper._bildschirm,
                                                       meiden=koerper._banner_rechtecke)
        koerper.ticker.zeige.assert_called_once_with(aktivieren=False)

    def test_eine_neue_nachricht_schliesst_den_noch_offenen_ticker(self) -> None:
        koerper, *_ = _bauen()
        koerper._raute_hat_gesprochen("eins")
        alter_ticker = koerper.ticker
        koerper._raute_hat_gesprochen("zwei")
        alter_ticker.schliessen.assert_called_once_with()
        self.assertIsNot(koerper.ticker, alter_ticker)
        self.assertIsNone(koerper.banner)

    def test_ticker_folgt_der_verschobenen_raute(self) -> None:
        koerper, _rk, raute_instance, *_ = _bauen()
        koerper._raute_hat_gesprochen("eins")
        raute_instance.rechteck.return_value = (300, 300, 348, 348)
        koerper._raute_verschoben(300, 300)
        koerper.ticker.an_raute.assert_called_once_with((300, 300, 348, 348))

    def test_verschieben_ohne_ticker_bricht_nicht(self) -> None:
        koerper, *_ = _bauen()
        koerper._raute_verschoben(1, 1)

    def test_gesprochenes_geht_an_den_besitzer_fuer_den_gemeinsamen_chat(self) -> None:
        koerper, _rk, _ri, _tk, _ti, _nk, gesprochen = _bauen()
        koerper._raute_hat_gesprochen("Shader kompiliert!")
        gesprochen.assert_called_once_with("codex", "Shader kompiliert!")

    def test_hinweis_der_bridge_steht_als_box_an_der_raute(self) -> None:
        koerper, *_ = _bauen()
        koerper.zeige_ticker("Hände: aus", "#F2F2F2")
        aufruf = koerper._ticker_klasse.call_args.kwargs
        self.assertEqual((aufruf["text"], aufruf["farbe_hex"], aufruf["raute_rechteck"]),
                         ("Hände: aus", "#F2F2F2", (100, 100, 148, 148)))
        koerper.ticker.zeige.assert_called_once_with(aktivieren=False)

    def test_daniels_worte_sind_eine_box_neben_der_raute_in_seiner_farbe_und_kein_banner(self) -> None:
        koerper, _rk, _ri, _tk, _ti, banner_klasse, _ck = _bauen()
        koerper.zeige_daniel("Daniel: Go!", "#F2F2F2")
        aufruf = koerper._ticker_klasse.call_args.kwargs
        self.assertEqual((aufruf["text"], aufruf["farbe_hex"], aufruf["raute_rechteck"]),
                         ("Daniel: Go!", "#F2F2F2", (100, 100, 148, 148)))
        koerper.ticker.zeige.assert_called_once_with(aktivieren=False)
        banner_klasse.assert_not_called()
        self.assertIsNone(koerper.banner)

    def test_neue_worte_von_daniel_ersetzen_die_alte_box(self) -> None:
        koerper, *_ = _bauen()
        koerper.zeige_daniel("eins", "#F2F2F2")
        alt = koerper.ticker
        koerper.zeige_daniel("zwei", "#F2F2F2")
        alt.schliessen.assert_called_once_with()

    def test_neuer_ticker_ersetzt_den_alten(self) -> None:
        koerper, *_ = _bauen()
        koerper.zeige_ticker("eins", "#F2F2F2")
        alt = koerper.ticker
        koerper.zeige_ticker("zwei", "#F2F2F2")
        alt.schliessen.assert_called_once_with()

    def test_zielbereich_folgt_dem_gebundenen_fenster_und_haelt_das_letzte_rechteck_wenn_es_weg_ist(self) -> None:
        from types import SimpleNamespace
        from augen_haende_bridge.koerper import erster_koerper as ek
        koerper, *_ = _bauen()
        zustand = {"werte": (True, False, (100, 100, 500, 400))}
        original = ek.fenster_zustand
        ek.fenster_zustand = lambda hwnd: zustand["werte"]
        try:
            koerper._ziel_gebunden(SimpleNamespace(item=SimpleNamespace(rect=(100, 100, 500, 400), target_id="windows:window:42")))
            self.assertEqual(koerper.ziel_rechteck(), (100, 100, 500, 400))
            zustand["werte"] = (True, False, (300, 200, 700, 500))  # Fenster verschoben
            self.assertEqual(koerper.ziel_rechteck(), (300, 200, 700, 500))
            zustand["werte"] = (True, True, None)  # minimiert
            self.assertEqual(koerper.ziel_rechteck(), (300, 200, 700, 500))
            zustand["werte"] = (False, False, None)  # geschlossen
            self.assertEqual(koerper.ziel_rechteck(), (300, 200, 700, 500))
        finally:
            ek.fenster_zustand = original

    def test_bindung_loesen_setzt_den_zielbereich_auf_den_desktop_zurueck(self) -> None:
        from types import SimpleNamespace
        koerper, *_ = _bauen()
        koerper._ziel_gebunden(SimpleNamespace(item=SimpleNamespace(rect=(1, 2, 3, 4), target_id="windows:window:42")))
        koerper._ziel_geloest()
        self.assertIsNone(koerper.bindung)
        self.assertEqual(koerper.ziel_rechteck(), koerper._arbeitsflaeche())

    def test_selbst_geschlossene_banner_und_ticker_raeumen_ihre_referenz_auf(self) -> None:
        koerper, *_ = _bauen()
        koerper._raute_hat_gesprochen("eins")
        koerper._banner_geschlossen()
        koerper._ticker_geschlossen()
        self.assertIsNone(koerper.banner)
        self.assertIsNone(koerper.ticker)


class ZielGebundenTests(unittest.TestCase):
    def test_bindung_macht_das_gebundene_fenster_zum_zielbereich_und_wird_gemeldet(self) -> None:
        gemeldet = Mock()
        koerper, *_ = _bauen(ziel_gebunden=gemeldet)
        self.assertEqual(koerper.ziel_rechteck(), ZIEL)
        bindung = Mock()
        bindung.item.rect = (10, 10, 810, 610)
        koerper._ziel_gebunden(bindung)
        self.assertEqual(koerper.ziel_rechteck(), (10, 10, 810, 610))
        self.assertIs(koerper.bindung, bindung)
        gemeldet.assert_called_once_with(bindung)

    def test_bindung_ohne_rechteck_faellt_auf_die_arbeitsflaeche_zurueck(self) -> None:
        koerper, *_ = _bauen()
        bindung = Mock()
        bindung.item.rect = None
        koerper._ziel_gebunden(bindung)
        self.assertEqual(koerper.ziel_rechteck(), ZIEL)


class RauteMenueTests(unittest.TestCase):
    def _mit_menue(self, gewaehlt: int):
        menue_anzeigen = Mock(return_value=gewaehlt)
        agent_beenden, bridge_beenden = Mock(), Mock()
        koerper, _rk, raute_instance, _tk, terminal_instance, _nk, _ck = _bauen(
            menue_anzeigen=menue_anzeigen, agent_beenden=agent_beenden, bridge_beenden=bridge_beenden)
        raute_instance.status = "verbunden"
        raute_instance.hwnd = 4711
        return koerper, menue_anzeigen, agent_beenden, bridge_beenden, terminal_instance

    def test_menue_zeigt_den_status_als_abgeblendete_kopfzeile(self) -> None:
        koerper, *_ = self._mit_menue(0)
        kopf = koerper.menue_eintraege()[0]
        from augen_haende_bridge.koerper import menue
        self.assertEqual(kopf, (MENUE_STATUS, "codex · verbunden", menue.ABGEBLENDET))

    def test_menue_oeffnet_an_der_raute_und_abbruch_tut_nichts(self) -> None:
        koerper, menue_anzeigen, agent_beenden, bridge_beenden, _t = self._mit_menue(0)
        koerper._raute_menue(10, 20)
        self.assertEqual(menue_anzeigen.call_args.args[0], 4711)
        self.assertEqual(menue_anzeigen.call_args.args[2:], (10, 20))
        agent_beenden.assert_not_called()
        bridge_beenden.assert_not_called()

    def test_agent_beenden_und_bridge_beenden_sind_erreichbar(self) -> None:
        koerper, _m, agent_beenden, _b, _t = self._mit_menue(MENUE_AGENT_BEENDEN)
        koerper._raute_menue(0, 0)
        agent_beenden.assert_called_once_with()
        koerper2, _m2, _a2, bridge_beenden, _t2 = self._mit_menue(MENUE_BRIDGE_BEENDEN)
        koerper2._raute_menue(0, 0)
        bridge_beenden.assert_called_once_with()

    def test_terminal_ein_und_ausblenden(self) -> None:
        koerper, _m, _a, _b, terminal = self._mit_menue(MENUE_TERMINAL)
        terminal.sichtbar.return_value = True
        koerper._raute_menue(0, 0)
        terminal.verberge.assert_called_once_with()
        terminal.sichtbar.return_value = False
        koerper._raute_menue(0, 0)
        terminal.zeige.assert_called_once_with()

    def test_not_aus_ist_im_menue_erreichbar_und_hebt_sich_wieder_auf(self) -> None:
        from augen_haende_bridge.koerper.notaus import NotAus
        na = NotAus()
        koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=MENUE_NOTAUS), not_aus=na)
        koerper.raute.status = "verbunden"
        self.assertIn("Not-Aus (F12)", [e[1] for e in koerper.menue_eintraege() if e])
        koerper._raute_menue(0, 0)
        self.assertTrue(na.aktiv)
        self.assertIn("Not-Aus aufheben", [e[1] for e in koerper.menue_eintraege() if e])
        koerper._raute_menue(0, 0)
        self.assertFalse(na.aktiv)

    def test_menue_hat_keinen_chat_eintrag_der_chat_gehoert_der_anwendung(self) -> None:
        koerper, *_ = _bauen()
        koerper.raute.status = "verbunden"
        self.assertFalse(any("Chat" in e[1] for e in koerper.menue_eintraege() if e))

    def test_transparenz_und_groesse_aus_dem_menue(self) -> None:
        for wahl, erwartet in ((MENUE_TRANSPARENZ, "deckkraft_weiter"), (MENUE_GROESSER, "groesse_setzen"),
                               (MENUE_KLEINER, "groesse_setzen")):
            koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=wahl))
            koerper.raute.status = "verbunden"
            koerper.raute.groesse = 48
            koerper.raute.deckkraft_prozent.return_value = 34
            koerper._raute_menue(0, 0)
            getattr(koerper.raute, erwartet).assert_called_once()
        koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=MENUE_GROESSER))
        koerper.raute.groesse = 48
        koerper._raute_menue(0, 0)
        koerper.raute.groesse_setzen.assert_called_once_with(60)


class SichtbarkeitsTests(unittest.TestCase):
    def test_x_am_terminal_merkt_sich_das_ausblenden(self) -> None:
        koerper, _rk, _ri, terminal_klasse, terminal_instance, _nk, _ck = _bauen()
        self.assertFalse(koerper.terminal_ausgeblendet)
        terminal_klasse.call_args.kwargs["schliessen_gewuenscht"]()
        self.assertTrue(koerper.terminal_ausgeblendet)
        terminal_instance.verberge.assert_called_once_with()

    def test_einblenden_aus_dem_menue_hebt_das_ausblenden_auf(self) -> None:
        koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=MENUE_TERMINAL))
        koerper.terminal.sichtbar.return_value = True
        koerper._raute_menue(0, 0)
        self.assertTrue(koerper.terminal_ausgeblendet)
        koerper.terminal.sichtbar.return_value = False
        koerper._raute_menue(0, 0)
        self.assertFalse(koerper.terminal_ausgeblendet)

    def test_ohne_erlaubnis_kein_banner_kein_ticker_aber_der_chat_bekommt_es(self) -> None:
        koerper, _rk, _ri, _tk, _ti, banner_klasse, gesprochen = _bauen(meldungen_zeigen=lambda: False)
        koerper._raute_hat_gesprochen("hallo")
        gesprochen.assert_called_once_with("codex", "hallo")
        banner_klasse.assert_not_called()
        self.assertIsNone(koerper.ticker)
        koerper.zeige_ticker("Hände: aus", "#F2F2F2")
        self.assertIsNone(koerper.ticker)
        koerper.zeige_daniel("Daniel: Go!", "#F2F2F2")
        banner_klasse.assert_not_called()

    def test_menue_hat_regeleintraege_mit_dem_aktuellen_text(self) -> None:
        koerper, *_ = _bauen(regeltext=lambda element: f"{element}-regel")
        koerper.raute.status = "verbunden"
        texte = [e[1] for e in koerper.menue_eintraege() if e]
        self.assertIn("Raute: raute-regel …", texte)
        self.assertIn("Terminal: terminal-regel …", texte)

    def test_regeleintraege_rufen_den_besitzer_mit_dem_element_und_ort(self) -> None:
        aufrufe = []
        for wahl in (MENUE_RAUTE_REGEL, MENUE_TERMINAL_REGEL):
            koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=wahl), regel_menue=lambda e, x, y: aufrufe.append((e, x, y)))
            koerper._raute_menue(7, 8)
        self.assertEqual(aufrufe, [("raute", 7, 8), ("terminal", 7, 8)])


class DurchklickMenueTests(unittest.TestCase):
    def test_menue_zeigt_den_durchklick_zustand_und_schaltet_ihn(self) -> None:
        aufrufe = []
        koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=MENUE_TERMINAL_DURCHKLICK),
                             durchklick_text=lambda e: "an", durchklick_umschalten=aufrufe.append)
        koerper.raute.status = "verbunden"
        self.assertIn("Terminal: durchklickbar, Strg zum Bedienen — an", [e[1] for e in koerper.menue_eintraege() if e])
        koerper._raute_menue(0, 0)
        self.assertEqual(aufrufe, ["terminal"])


class EingabefeldTests(unittest.TestCase):
    def feld(self, **ueber):
        feld = Mock()
        feld.rechteck.return_value = (0, 0, 380, 34)
        klasse = Mock(return_value=feld)
        koerper, *_ = _bauen(eingabe_klasse=klasse, bildschirm=lambda: (0, 0, 1920, 1080), **ueber)
        return koerper, klasse, feld

    def test_die_kombination_oeffnet_ein_feld_rechts_neben_der_raute_und_fokussiert_es(self) -> None:
        koerper, klasse, feld = self.feld()
        koerper.eingabe_oeffnen()
        kwargs = klasse.call_args.kwargs
        self.assertEqual((kwargs["name"], kwargs["farbe_hex"]), ("codex", koerper.farbe_hex))
        feld.verschiebe.assert_called_once_with(148 + 8, 124 - 17)
        feld.aktivieren.assert_called_once_with()

    def test_der_text_ist_die_rede_des_agenten(self) -> None:
        koerper, klasse, feld = self.feld()
        koerper.eingabe_oeffnen()
        self.assertEqual(klasse.call_args.kwargs["gesendet"], koerper.raute.sagen)

    def test_zweiter_aufruf_fokussiert_das_vorhandene_feld(self) -> None:
        koerper, klasse, feld = self.feld()
        koerper.eingabe_oeffnen()
        koerper.eingabe_oeffnen()
        klasse.assert_called_once()
        self.assertEqual(feld.aktivieren.call_count, 2)

    def test_geschlossenes_feld_wird_vergessen_und_kann_neu_geoeffnet_werden(self) -> None:
        koerper, klasse, feld = self.feld()
        koerper.eingabe_oeffnen()
        klasse.call_args.kwargs["geschlossen"]()
        self.assertIsNone(koerper.eingabe)
        koerper.eingabe_oeffnen()
        self.assertEqual(klasse.call_count, 2)

    def test_schliessen_schliesst_auch_das_feld(self) -> None:
        koerper, klasse, feld = self.feld()
        koerper.eingabe_oeffnen()
        koerper.schliessen()
        feld.schliessen.assert_called_once_with()


class LebenszyklusTests(unittest.TestCase):
    def test_zeigen_zeigt_terminal_und_raute(self) -> None:
        koerper, _rk, raute_instance, _tk, terminal_instance, _nk, _ck = _bauen()
        koerper.zeigen()
        terminal_instance.zeige.assert_called_once_with()
        raute_instance.zeige.assert_called_once_with(aktivieren=False)  # die Raute nimmt nie den Fokus

    def test_schliessen_ohne_nachricht_bricht_nicht(self) -> None:
        koerper, _rk, raute_instance, _tk, terminal_instance, _nk, _ck = _bauen()
        koerper.schliessen()
        raute_instance.schliessen.assert_called_once_with()
        terminal_instance.schliessen.assert_called_once_with()

    def test_schliessen_schliesst_auch_den_ticker(self) -> None:
        koerper, *_ = _bauen()
        koerper._raute_hat_gesprochen("eins")
        ticker = koerper.ticker
        koerper.schliessen()
        ticker.schliessen.assert_called_once_with()
        self.assertIsNone(koerper.banner)


if __name__ == "__main__":
    unittest.main()
