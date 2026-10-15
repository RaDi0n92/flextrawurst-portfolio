"""Bilderstrom in der Anwendung: Bindung startet ihn, Schalter, Not-Aus, Entfernen, Senden über den Sender."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper.bilderstrom import Bilderstrom
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen


def bindung(target_id="windows:window:4242"):
    frame = SimpleNamespace(width=64, height=32, bgra_bytes=bytes(64 * 32 * 4), captured_at_ms=5)
    item = SimpleNamespace(rect=(8, 8, 40, 24), target_id=target_id)
    snapshot = SimpleNamespace(items=[SimpleNamespace(rect=(0, 0, 64, 32))])
    return SimpleNamespace(frame=frame, item=item, snapshot=snapshot, binding=Mock())


def baue(strom=None, **extra):
    strom = strom if strom is not None else Mock(spec=Bilderstrom)
    strom.ziele = {}
    app, gui, gebaut = _gestartet(bilderstrom=strom, bild_kodieren=lambda *a: (b"\xff\xd8\xff", 32, 16), **extra)
    standard = list(strom.binden.call_args_list)  # Standard: jeder neue Agent sieht sofort den ganzen Desktop
    strom.binden.reset_mock()  # die Tests unten prüfen nur noch, was danach passiert
    app.standard_bindungen = standard
    return app, gebaut, strom


class BindenTests(unittest.TestCase):
    def test_neuer_agent_sieht_sofort_den_ganzen_desktop(self):
        app, gebaut, strom = baue()
        self.assertEqual([c.args for c in app.standard_bindungen], [("t-1", None)])

    def test_bindung_loesen_heisst_ganzer_desktop_und_nicht_keine_bilder(self):
        app, gebaut, strom = baue()
        app.ziel_loesen("t-1")
        strom.binden.assert_called_once_with("t-1", None)
        strom.loesen.assert_not_called()

    def test_fenster_ziel_startet_den_strom_mit_dem_fenster(self):
        app, gebaut, strom = baue()
        gebaut[0].kwargs["ziel_gebunden"](bindung("windows:window:4242"))
        strom.binden.assert_called_once_with("t-1", 4242)

    def test_desktop_ziel_startet_den_strom_ohne_fenster(self):
        app, gebaut, strom = baue()
        gebaut[0].kwargs["ziel_gebunden"](bindung("windows:desktop:0"))
        strom.binden.assert_called_once_with("t-1", None)

    def test_bei_not_aus_wird_nichts_gebunden(self):
        app, gebaut, strom = baue()
        app.not_aus.ausloesen("x")
        gebaut[0].kwargs["ziel_gebunden"](bindung())
        strom.binden.assert_not_called()

    def test_die_anwendung_laeuft_auch_ohne_strom(self):
        app, gebaut, _ = baue(strom=None)
        app.bilderstrom = None
        gebaut[0].kwargs["ziel_gebunden"](bindung())  # darf nicht scheitern

    def test_das_erste_bild_geht_weiter_sofort_hinaus(self):
        app, gebaut, strom = baue()
        gebaut[0].kwargs["ziel_gebunden"](bindung())
        arten = [k for k, _ in app.runtime.gesendet]
        self.assertIn("frame", arten)


class RauteSofortbildTests(unittest.TestCase):
    """Ein Agent sendet in seine Raute: jeder andere Agent im selben Gate bekommt sofort ein Bild."""

    def zwei(self):
        app, gebaut, strom = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=7), "t-2": SimpleNamespace(hwnd=7), "t-3": SimpleNamespace(hwnd=9)}
        app.ziel_schluessel = lambda tid: {"t-1": "w:7", "t-2": "w:7", "t-3": "w:9"}.get(tid)
        app.agenten = {t: SimpleNamespace(terminal_id=t, name=n) for t, n in (("t-1", "A"), ("t-2", "B"), ("t-3", "C"))}
        app.RAUTE_BILD_VERZOEGERUNG_S = 0.0
        app.log = Mock()
        return app, strom

    def warten(self, strom, n=1):
        import time

        for _ in range(100):
            if strom.sofort_senden.call_count >= n:
                return
            time.sleep(0.01)

    def test_nachbarn_sind_nur_agenten_im_selben_gate(self):
        app, strom = self.zwei()
        self.assertEqual(app._gate_nachbarn("t-1"), ["t-2"])
        self.assertEqual(app._gate_nachbarn("t-3"), [])

    def test_wer_nirgends_gebunden_ist_hat_kein_gate(self):
        app, strom = self.zwei()
        app.ziel_schluessel = lambda tid: None
        self.assertEqual(app._gate_nachbarn("t-1"), [])
        app._raute_gesendet("t-1")
        strom.sofort_senden.assert_not_called()

    def test_gesendet_in_die_raute_schickt_den_nachbarn_sofort_ein_bild(self):
        app, strom = self.zwei()
        app._raute_gesendet("t-1")
        self.warten(strom)
        strom.sofort_senden.assert_called_once_with(["t-2"])

    def test_der_agent_selbst_und_fremde_gates_bekommen_nichts(self):
        app, strom = self.zwei()
        app._raute_gesendet("t-3")
        import time

        time.sleep(0.1)
        strom.sofort_senden.assert_not_called()

    def test_say_ueber_den_relay_loest_es_aus(self):
        app, strom = self.zwei()
        app.agenten["t-1"].koerper = Mock()
        app._raute_sagt({"terminal_id": "t-1", "text": "Schritt 1 angesagt"})
        self.warten(strom)
        strom.sofort_senden.assert_called_once_with(["t-2"])

    def test_eine_meldung_schickt_dem_betroffenen_und_seinen_gate_nachbarn_ein_bild(self):
        app, strom = self.zwei()
        app.chat = Mock()
        app._meldung_posten("t-1", "⚠ [A] Not-Aus: aktiv")
        self.warten(strom)
        app.chat.empfangen.assert_called_once_with("Meldung", "⚠ [A] Not-Aus: aktiv")
        strom.sofort_senden.assert_called_once_with(["t-1", "t-2"])

    def test_eine_meldung_ohne_agent_oder_ohne_chat_ist_trotzdem_sicher(self):
        app, strom = self.zwei()
        app.chat = None
        app._meldung_posten(None, "allgemein")
        app._meldung_posten("t-3", "⚠ [C] kaputt")
        import time

        time.sleep(0.1)
        strom.sofort_senden.assert_called_once_with(["t-3"])

    def zeige_app(self):
        from augen_haende_bridge.koerper.komposition import Arbeitsflaechen

        app, strom = self.zwei()
        app.arbeit = Arbeitsflaechen()
        app.anzeige = None
        app.gui = Mock()
        return app, strom

    def test_eine_zeigegeste_ohne_empfaenger_sieht_jeder_im_selben_gate(self):
        app, strom = self.zeige_app()
        oid = app.zeige_overlay("t-1", "w:7", (0.5, 0.5), "hier", ())
        objekt = app.arbeit.dokument("w:7").objekte[oid]
        self.assertEqual(set(objekt.empfaenger), {"t-1", "t-2"})
        self.assertNotIn("t-3", objekt.empfaenger, "wer in einem anderen Gate steht, sieht sie nicht")
        self.warten(strom)
        strom.sofort_senden.assert_called_once_with(["t-2"])

    def test_eine_zeigegeste_mit_ausdruecklichen_empfaengern_bleibt_privat(self):
        app, strom = self.zeige_app()
        oid = app.zeige_overlay("t-1", "w:7", (0.5, 0.5), "nur du", ("t-3",))
        objekt = app.arbeit.dokument("w:7").objekte[oid]
        self.assertEqual(set(objekt.empfaenger), {"t-1", "t-3"})
        self.warten(strom)
        strom.sofort_senden.assert_called_once_with(["t-3"])

    def test_ein_fehler_beim_senden_wird_gemeldet_und_stoert_nichts(self):
        app, strom = self.zwei()
        strom.sofort_senden.side_effect = RuntimeError("boom")
        app._raute_gesendet("t-1")
        self.warten(strom)
        import time

        time.sleep(0.05)
        self.assertTrue(any("Sofortbild" in str(c) for c in app.log.call_args_list))


class SchalterTests(unittest.TestCase):
    def test_menutext_und_umschalten(self):
        app, gebaut, strom = baue()
        self.assertEqual(gebaut[0].kwargs["bilder_text"](), "kein Ziel gebunden")
        strom.ziele = {"t-1": object()}
        strom.an.return_value = True
        self.assertEqual(gebaut[0].kwargs["bilder_text"](), "an")
        strom.an.return_value = False
        self.assertEqual(gebaut[0].kwargs["bilder_text"](), "aus")
        gebaut[0].kwargs["bilder_umschalten"]()
        strom.umschalten.assert_called_once_with("t-1")


class LebenszyklusTests(unittest.TestCase):
    def test_strom_startet_mit_der_anwendung_und_stoppt_beim_beenden(self):
        app, _, strom = baue()
        strom.starten.assert_called_once_with()
        app.beenden()
        strom.stoppen.assert_called_once_with()

    def test_entfernter_agent_loest_seinen_strom(self):
        app, gebaut, strom = baue()
        app.agent_beenden("t-1")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        strom.loesen.assert_called_once_with("t-1")

    def test_verschwundenes_ziel_wird_an_der_raute_gemeldet(self):
        app, gebaut, strom = baue()
        app.strom_ziel_verschwunden("t-1")
        self.assertTrue(any("weg" in c.args[0] for c in gebaut[0].zeige_ticker.call_args_list))
        app.strom_ziel_verschwunden("t-99")


class SendenTests(unittest.TestCase):
    def test_strom_bild_geht_als_frame_ueber_den_sender(self):
        app, _, _ = baue()
        self.assertTrue(app.strom_senden("t-1", {"mime": "image/jpeg"}))
        self.assertEqual(app.runtime.gesendet[-1], ("frame", {"mime": "image/jpeg"}))

    def test_offline_wird_nichts_gesendet(self):
        app, _, _ = baue()
        app.status = "offline"
        self.assertFalse(app.strom_senden("t-1", {}))

    def test_bei_not_aus_sperrt_der_sender_frames(self):
        app, _, _ = baue()
        app.not_aus.ausloesen("x")
        n = len(app.runtime.gesendet)
        app.strom_senden("t-1", {"mime": "image/jpeg"})
        self.assertEqual(len(app.runtime.gesendet), n)

    def test_bericht_nennt_die_anzahl_gesendeter_bilder(self):
        app, _, strom = baue()
        strom.ziele = {"t-1": SimpleNamespace(gesendet=3)}
        self.assertEqual(app.bericht()["agenten"][0]["bilderstrom"], 3)



class AmpelDatenTests(unittest.TestCase):
    """Die Ampel liest den echten Zustand: Bilderstrom, Hände, Bindung, Verbindung und Fenster."""

    def lampen(self, app, gebaut, stand, ziel_text="Ziel: Desktop (ungebunden)", gebunden=False, probleme=frozenset()):
        app.bilderstrom.stand.return_value = stand
        app.bilderstrom.probleme.return_value = probleme
        gebaut[0].terminal.ziel_text, gebaut[0].terminal.ziel_gebunden = ziel_text, gebunden
        gebaut[0].terminal.rechteck.return_value = (10, 10, 300, 200)
        gebaut[0].raute.rechteck.return_value = (10, 10, 100, 60)
        return {l.kennung: l for l in __import__("augen_haende_bridge.koerper.ampel", fromlist=["lampen"]).lampen(app.ampel_zustand("t-1"))}

    FRISCH = {"an": True, "hwnd": None, "alter_s": 3.0, "gesendet": 1}

    def test_frisches_bild_ist_gruen_und_ein_langer_ausfall_rot(self):
        app, gebaut, strom = baue()
        self.assertEqual(self.lampen(app, gebaut, self.FRISCH)["bild"].farbe, "gruen")
        k = self.lampen(app, gebaut, {**self.FRISCH, "alter_s": 900.0})
        self.assertEqual((k["bild"].farbe, k["bild"].behebe), ("rot", "strom_neu"))

    def test_ohne_strom_ist_es_rot_und_nicht_still(self):
        app, gebaut, strom = baue()
        k = self.lampen(app, gebaut, None)
        self.assertEqual((k["strom"].farbe, k["strom"].behebe), ("rot", "desktop_binden"))

    def test_ablehnungsgruende_der_haende_kommen_mit_grund_in_die_lampen(self):
        from augen_haende_bridge.koerper.eingabe_adapter import Ergebnis
        app, gebaut, strom = baue()
        app._haende_ergebnis_senden({"terminal_id": "t-1", "auftrag_id": "a"}, Ergebnis("a", "abgelehnt", "punkt_verdeckt"))
        k = self.lampen(app, gebaut, self.FRISCH)
        self.assertEqual((k["gate:punkt_verdeckt"].farbe, k["gate:punkt_verdeckt"].behebe), ("rot", "fenster_vor"))
        self.assertEqual((k["hand"].farbe, k["hand"].wort), ("rot", "Ziel verdeckt"))

    def test_probleme_des_bilderstroms_werden_lampen(self):
        app, gebaut, strom = baue()
        k = self.lampen(app, gebaut, self.FRISCH, probleme=frozenset({"senden_abgelehnt"}))
        self.assertEqual(k["send"].farbe, "rot")

    def test_verschwundenes_fenster_ist_rot_bis_zum_naechsten_binden(self):
        app, gebaut, strom = baue()
        app.strom_ziel_verschwunden("t-1")
        self.assertEqual(self.lampen(app, gebaut, self.FRISCH)["weg"].farbe, "rot")
        app.ziel_loesen("t-1")
        self.assertEqual(self.lampen(app, gebaut, self.FRISCH)["weg"].farbe, "gruen")

    def test_terminal_ausserhalb_des_bildschirms_wird_rot(self):
        app, gebaut, strom = baue()
        app.bilderstrom.stand.return_value = self.FRISCH
        app.bilderstrom.probleme.return_value = frozenset()
        gebaut[0].terminal.ziel_text, gebaut[0].terminal.ziel_gebunden = "", False
        gebaut[0].raute.rechteck.return_value = (10, 10, 100, 60)
        gebaut[0].terminal.rechteck.return_value = (1500, 700, 99999, 99999)
        k = {l.kennung: l for l in __import__("augen_haende_bridge.koerper.ampel", fromlist=["lampen"]).lampen(app.ampel_zustand("t-1"))}
        self.assertEqual((k["auss"].farbe, k["auss"].behebe), ("rot", "terminal_holen"))

    def test_der_takt_fuellt_die_lampen_und_schreibt_das_dauerfeuer_in_den_chat(self):
        from augen_haende_bridge.koerper import ampel
        app, gebaut, strom = baue()
        app.chat = Mock()
        self.lampen(app, gebaut, {**self.FRISCH, "alter_s": 900.0})
        app.ampel_takt()
        erwartet = len(ampel.lampen(app.ampel_zustand("t-1")))
        self.assertEqual(len(app.ampel_lampen("Codex")), erwartet)
        self.assertGreater(erwartet, 40, "alle Gates des Systems sind Lampen")
        zeilen = [c.args for c in app.chat.empfangen.call_args_list]
        self.assertTrue(any(s == "Meldung" and "[Codex] Bilder kommen frisch an" in t for s, t in zeilen))

    def test_der_takt_piept_nur_beim_wechsel_auf_rot(self):
        app, gebaut, strom = baue(piepen=Mock())
        self.lampen(app, gebaut, {**self.FRISCH, "alter_s": 900.0})
        app.ampel_takt()
        app.ampel_takt()
        self.assertEqual(app._piepen.call_count, 1)


class AmpelAktionTests(unittest.TestCase):
    """Die Klicks auf die Lampen tun, was sie versprechen, und sagen es im Chat."""

    def baue_mit_ampel(self):
        app, gebaut, strom = baue(ampel_bauen=Mock(), fenster_vor=Mock(return_value=True), piepen=Mock())
        app.chat = Mock()
        return app, gebaut, strom

    def test_jeder_agent_bekommt_sein_eigenes_ampel_fenster(self):
        app, gebaut, strom = self.baue_mit_ampel()
        app._ampel_fuer("t-1")
        kwargs = app._ampel_bauen.call_args.kwargs
        self.assertEqual((kwargs["name"], kwargs["daten"], kwargs["aktion"], kwargs["menue"]), ("Codex", app.ampel_lampen, app.ampel_aktion, app.ampel_menue))
        self.assertIn("t-1", app.ampel_fenster)

    def test_desktop_binden_schaltet_auf_den_ganzen_desktop(self):
        app, gebaut, strom = self.baue_mit_ampel()
        app.ampel_aktion("Codex", "desktop_binden")
        strom.binden.assert_called_with("t-1", None)
        self.assertTrue(any("Desktop" in c.args[1] for c in app.chat.empfangen.call_args_list))

    def test_bilder_neu_starten_frischt_das_ziel_auf_und_sonst_den_desktop(self):
        app, gebaut, strom = self.baue_mit_ampel()
        strom.auffrischen.return_value = True
        app.ampel_aktion("Codex", "strom_neu")
        strom.auffrischen.assert_called_once_with("t-1")
        strom.auffrischen.return_value = False
        app.ampel_aktion("Codex", "strom_neu")
        strom.binden.assert_called_with("t-1", None)

    def test_fenster_nach_vorn_holt_das_gebundene_fenster_oder_sagt_ehrlich_nein(self):
        app, gebaut, strom = self.baue_mit_ampel()
        strom.stand.return_value = {"an": True, "hwnd": 4242, "alter_s": 3.0, "gesendet": 1}
        app.ampel_aktion("Codex", "fenster_vor")
        app._fenster_vor.assert_called_once_with(4242)
        strom.stand.return_value = {"an": True, "hwnd": None, "alter_s": 3.0, "gesendet": 1}
        app.ampel_aktion("Codex", "fenster_vor")
        self.assertIn("nicht gefunden", app.hinweis)

    def test_ein_klick_auf_eine_andere_lampe_erklaert_sie_im_chat(self):
        app, gebaut, strom = self.baue_mit_ampel()
        from augen_haende_bridge.koerper import ampel
        app.ampel_stand["Codex"] = ampel.lampen(ampel.Zustand(name="Codex", alter_s=3.0))
        app.ampel_aktion("Codex", "info:bild")
        text = app.chat.empfangen.call_args.args[1]
        self.assertIn("[Codex] Bilder kommen frisch an", text)

    def test_unbekannter_agent_und_unbekannte_aktion_tun_nichts(self):
        app, gebaut, strom = self.baue_mit_ampel()
        app.ampel_aktion("Niemand", "desktop_binden")
        app.ampel_aktion("Codex", "gibt_es_nicht")
        strom.binden.assert_not_called()



class AmpelHaendeUndMenueTests(unittest.TestCase):
    """Hände nach Aktionsart und Programm, und das Rechtsklick-Menü mit allen Funktionen."""

    def baue_mit_ampel(self):
        app, gebaut, strom = baue(ampel_bauen=Mock(), fenster_vor=Mock(return_value=True), piepen=Mock())
        app.chat = Mock()
        return app, gebaut, strom

    def baue_mit_fenster(self):
        app, gebaut, strom = baue(ampel_bauen=Mock())
        app.chat = Mock()
        strom.stand.return_value = {"an": True, "hwnd": None, "alter_s": 3.0, "gesendet": 1}
        strom.probleme.return_value = frozenset()
        gebaut[0].terminal.ziel_text, gebaut[0].terminal.ziel_gebunden = "Ziel: notiz.txt — Kate", True
        gebaut[0].terminal.rechteck.return_value = (10, 10, 300, 200)
        gebaut[0].raute.rechteck.return_value = (10, 10, 100, 60)
        return app, gebaut, strom

    def ergebnis(self, app, art, status="ausgefuehrt", grund=""):
        from augen_haende_bridge.koerper.eingabe_adapter import Ergebnis
        app._haende_ergebnis_senden({"terminal_id": "t-1", "auftrag_id": "a", "aktion": {"art": art}}, Ergebnis("a", status, grund))

    def lampen(self, app):
        from augen_haende_bridge.koerper import ampel
        return {l.name: l for l in ampel.lampen(app.ampel_zustand("t-1"))}

    def test_haende_werden_nach_aktionsart_und_programm_aufgeschluesselt(self):
        app, gebaut, strom = self.baue_mit_fenster()
        self.ergebnis(app, "klick")
        self.ergebnis(app, "tippe")
        self.ergebnis(app, "taste", "abgelehnt", "punkt_verdeckt")
        namen = self.lampen(app)
        self.assertEqual(namen["Hände: Klicken"].farbe, "gruen")
        self.assertEqual(namen["Hände: Tippen"].farbe, "gruen")
        self.assertEqual((namen["Hände: Tasten"].farbe, namen["Hände: Tasten"].behebe), ("rot", "fenster_vor"))
        self.assertEqual(namen["Hände in Kate"].farbe, "rot")  # die jüngste Aktion in Kate wurde abgelehnt

    def test_ohne_aktionen_gibt_es_keine_art_und_keine_programmlampen(self):
        app, gebaut, strom = self.baue_mit_fenster()
        self.assertFalse([n for n in self.lampen(app) if n.startswith("Hände: ") or n.startswith("Hände in ")])

    def test_das_menue_nennt_jede_funktion_ausgeschrieben_mit_zustand_in_klammern(self):
        app, gebaut, strom = self.baue_mit_fenster()
        self.ergebnis(app, "klick")
        app.ampel_takt()
        app._ampel_fuer("t-1")
        app.ampel_fenster["t-1"].deckkraft = 255
        app._menue_anzeigen = Mock(return_value=0)
        app.ampel_menue("Codex", 10, 10)
        eintraege = [e for e in app._menue_anzeigen.call_args.args[1] if e is not None]
        texte = [e[1] for e in eintraege]
        self.assertTrue(any(t.strip() == "Bilderstrom (läuft)" for t in texte))
        self.assertTrue(any(t.strip() == "Hände: Klicken (läuft)" for t in texte))
        self.assertTrue(any(t.startswith("Augen: Kommen Bilder") for t in texte), "Überschrift mit Erklärung")
        self.assertTrue(any(t.startswith("Ampel: Deckkraft") for t in texte))
        self.assertIn("Ampel größer", texte)
        self.assertIn("Ampel kleiner", texte)
        self.assertTrue(any(t.startswith("Ampel: ") and t.endswith("…") for t in texte), "Sichtbarkeitsregel wie bei der Raute")
        self.assertIn("Ampel ausblenden", texte)
        self.assertTrue(any(t.startswith("Durchklickbar,") for t in texte))
        self.assertFalse([t for t in texte if "BILD" in t.split() or "STRM" in t.split()], "keine Kürzel")

    def test_im_menue_zeigt_eine_rote_funktion_ihre_behebung_und_ein_klick_fuehrt_sie_aus(self):
        app, gebaut, strom = self.baue_mit_fenster()
        strom.stand.return_value = {"an": True, "hwnd": None, "alter_s": 900.0, "gesendet": 1}
        app.ampel_takt()
        app._ampel_fuer("t-1")
        app.ampel_fenster["t-1"].deckkraft = 255
        app._menue_anzeigen = Mock()
        eintraege = []

        def waehle(hwnd, liste, x, y):
            eintraege.extend(e for e in liste if e is not None)
            return next(e[0] for e in liste if e is not None and e[1].strip().startswith("Bilder kommen frisch an (kaputt"))

        app._menue_anzeigen.side_effect = waehle
        strom.auffrischen.return_value = True
        app.ampel_menue("Codex", 10, 10)
        zeile = next(e[1] for e in eintraege if e[1].strip().startswith("Bilder kommen frisch an"))
        self.assertIn("beheben: Bilder neu starten", zeile)
        strom.auffrischen.assert_called_once_with("t-1")

    def test_die_deckkraft_geht_ueber_das_menue_in_stufen(self):
        app, gebaut, strom = self.baue_mit_fenster()
        app.ampel_takt()
        app._ampel_fuer("t-1")
        fenster = app.ampel_fenster["t-1"]
        fenster.deckkraft = 255
        from augen_haende_bridge.koerper.anwendung import AMPEL_DECKKRAFT_ID
        app._menue_anzeigen = Mock(return_value=AMPEL_DECKKRAFT_ID)
        app.ampel_menue("Codex", 10, 10)
        fenster.deckkraft_weiter.assert_called_once()

    def test_groesser_und_kleiner_gehen_ueber_das_menue(self):
        app, gebaut, strom = self.baue_mit_fenster()
        app.ampel_takt()
        app._ampel_fuer("t-1")
        fenster = app.ampel_fenster["t-1"]
        fenster.deckkraft = 255
        from augen_haende_bridge.koerper.anwendung import AMPEL_GROESSER_ID, AMPEL_KLEINER_ID
        app._menue_anzeigen = Mock(return_value=AMPEL_GROESSER_ID)
        app.ampel_menue("Codex", 10, 10)
        fenster.groesser.assert_called_once_with()
        app._menue_anzeigen = Mock(return_value=AMPEL_KLEINER_ID)
        app.ampel_menue("Codex", 10, 10)
        fenster.groesser.assert_called_with(-0.3)

    def test_ein_klick_auf_eine_gruppenlampe_ohne_behebung_erklaert_die_gruppe_im_chat(self):
        app, gebaut, strom = self.baue_mit_ampel()
        from augen_haende_bridge.koerper import ampel
        app.ampel_stand["Codex"] = ampel.lampen(ampel.Zustand(name="Codex", alter_s=3.0))
        app.ampel_aktion("Codex", "gruppe:augen")
        texte = [c.args[1] for c in app.chat.empfangen.call_args_list]
        self.assertTrue(any("Kommen Bilder des Ziels" in t for t in texte))
        self.assertTrue(any("Bilderstrom (läuft)" in t for t in texte))


    def test_ausblenden_und_einblenden_ueber_das_menue(self):
        app, gebaut, strom = self.baue_mit_fenster()
        app.ampel_takt()
        app._ampel_fuer("t-1")
        fenster = app.ampel_fenster["t-1"]
        fenster.deckkraft = 255
        from augen_haende_bridge.koerper.anwendung import AMPEL_AUSBLENDEN_ID
        app._menue_anzeigen = Mock(return_value=AMPEL_AUSBLENDEN_ID)
        app.ampel_menue("Codex", 10, 10)
        fenster.verberge.assert_called_once()
        self.assertIn("t-1", app.ampel_ausgeblendet)
        app.ampel_menue("Codex", 10, 10)
        fenster.zeige.assert_called()
        self.assertNotIn("t-1", app.ampel_ausgeblendet)

    def test_die_sichtbarkeitsregel_laeuft_ueber_das_vorhandene_regel_menue(self):
        app, gebaut, strom = self.baue_mit_fenster()
        app.ampel_takt()
        app._ampel_fuer("t-1")
        app.ampel_fenster["t-1"].deckkraft = 255
        from augen_haende_bridge.koerper.anwendung import AMPEL_REGEL_ID
        app._menue_anzeigen = Mock(return_value=AMPEL_REGEL_ID)
        app.regel_menue = Mock()
        app.ampel_menue("Codex", 10, 10)
        app.regel_menue.assert_called_once_with("ampel:t-1", 10, 10)


    def test_die_ampel_ist_ein_element_wie_raute_und_terminal_im_ort_der_elemente(self):
        from augen_haende_bridge.koerper.anwendung import ORT_ELEMENTE
        self.assertIn(("ampel", "Ampel"), ORT_ELEMENTE)


    def test_zuruecksetzen_setzt_groesse_und_ausblenden_der_ampel_zurueck(self):
        app, gebaut, strom = self.baue_mit_fenster()
        app.ampel_takt()
        app._ampel_fuer("t-1")
        fenster = app.ampel_fenster["t-1"]
        fenster.rechteck.return_value = (0, 0, 150, 26)
        fenster.deckkraft = 255
        app.ampel_ausgeblendet.add("t-1")
        gebaut[0].farbe_hex = "#10c0ff"
        app._standard = {"ampel:t-1": ((5, 6, 155, 32), 245, None)}
        app._fenster_art = {k: v for k, v in app._fenster_art.items() if k == "ampel:t-1"}
        app.fenster_zuruecksetzen()
        fenster.faktor_setzen.assert_called_with(1.0)
        fenster.verschiebe.assert_called_with(5, 6, 150, 26)
        fenster.zeige.assert_called()
        self.assertEqual(app.ampel_ausgeblendet, set())


    def test_alle_ampeln_lassen_sich_auf_einmal_aus_und_einblenden(self):
        app, gebaut, strom = self.baue_mit_fenster()
        app.ampel_takt()
        app._ampel_fuer("t-1")
        fenster = app.ampel_fenster["t-1"]
        app.ampeln_umschalten()
        fenster.verberge.assert_called_once()
        self.assertEqual(app.ampel_ausgeblendet, {"t-1"})
        app.ampeln_umschalten()
        fenster.zeige.assert_called()
        self.assertEqual(app.ampel_ausgeblendet, set())


class NurTerminalStromTests(unittest.TestCase):
    def test_wieder_einschalten_bindet_den_desktop_wenn_der_agent_ohne_strom_gestartet_ist(self):
        app, gebaut, strom = baue()
        strom.ziele = {}
        app.nur_terminal_setzen("t-1", True)
        strom.binden.reset_mock()
        app.nur_terminal_setzen("t-1", False)
        strom.binden.assert_called_once_with("t-1", None)

    def test_hat_der_agent_schon_ein_ziel_bleibt_es_beim_einschalten(self):
        app, gebaut, strom = baue()
        strom.ziele = {"t-1": object()}
        app.nur_terminal_setzen("t-1", True)
        strom.binden.reset_mock()
        app.nur_terminal_setzen("t-1", False)
        strom.binden.assert_not_called()


if __name__ == "__main__":
    unittest.main()
