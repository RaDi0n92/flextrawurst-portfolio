"""Die Menü-Freigabe im Käfig: ein Agent nennt einen Menüeintrag beim Namen; Koordinaten nimmt der Körper dafür nie an.

Reine Logik und Engine mit Attrappe (kein Display nötig). Der echte Ablauf mit einem GTK-Menü steht in `test_koerper_menue_freigabe_x11.py`.
"""

from __future__ import annotations

import unittest

from test_koerper_eingabe_adapter import ZIEL, Attrappe, engine, lauf, pruefen

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import menue_freigabe, offene_menues
from augen_haende_bridge.koerper.eingabe_adapter import Aktion
from augen_haende_bridge.koerper.offene_menues import MenueEintrag, OffenesMenue

MENUE_KENNUNG = 555
MENUE = OffenesMenue(MENUE_KENNUNG, "raute", (
    MenueEintrag(7, "Raute: Deckkraft 80 % → nächste Stufe", (500, 300, 674, 327)),
    MenueEintrag(8, "Raute größer", (500, 327, 674, 354)),
    MenueEintrag(9, "Raute kleiner", (500, 354, 674, 381), aktiv=False),
    MenueEintrag(17, "Farbe wählen …", (500, 381, 674, 408)),
    MenueEintrag(19, "Ort der Elemente (Desktop oder Zielfenster) …", (500, 489, 674, 516)),
    MenueEintrag(4, "Bridge beenden", (500, 408, 674, 435)),
    MenueEintrag(26, "Kira pausieren (Prozess anhalten)", (500, 435, 674, 462)),
    MenueEintrag(5, "Kira · bereit", (500, 462, 674, 489), aktiv=False),
))


def menue_pruefen(text, **kw):
    werte = dict(menue_freigabe_an=True, menue_offen=MENUE)
    werte.update(kw)
    return pruefen(Aktion("menue", text=text), bezug=None, **werte)


class AktionTests(unittest.TestCase):
    def test_menue_nennt_den_eintrag_beim_namen(self):
        a = Aktion.aus_dict({"art": "menue", "text": "Raute größer"})
        self.assertEqual((a.art, a.text), ("menue", "Raute größer"))

    def test_koordinaten_fuer_ein_menue_werden_nie_angenommen(self):
        self.assertIsNone(Aktion.aus_dict({"art": "menue", "text": "Raute größer", "punkt": [10, 10]}))
        self.assertIsNone(Aktion.aus_dict({"art": "menue", "text": "x", "bis": [1, 1]}))

    def test_ohne_oder_mit_zu_langem_namen_ist_die_aktion_ungueltig(self):
        self.assertIsNone(Aktion.aus_dict({"art": "menue"}))
        self.assertIsNone(Aktion.aus_dict({"art": "menue", "text": ""}))
        self.assertIsNone(Aktion.aus_dict({"art": "menue", "text": "x" * (ea.MAX_MENUE_TEXT + 1)}))

    def test_zu_dict_und_zurueck(self):
        a = Aktion("menue", text="Raute größer")
        self.assertEqual(Aktion.aus_dict(a.zu_dict()), a)


class KaefigMenueTests(unittest.TestCase):
    def test_ohne_freigabe_wird_jede_menue_aktion_abgelehnt(self):
        e = menue_pruefen("Raute größer", menue_freigabe_an=False)
        self.assertEqual((e.ok, e.grund), (False, "menue_nicht_freigegeben"))

    def test_ohne_offenes_menue_wird_abgelehnt(self):
        e = menue_pruefen("Raute größer", menue_offen=None)
        self.assertEqual((e.ok, e.grund), (False, "menue_nicht_offen"))

    def test_erlaubter_eintrag_liefert_die_mitte_des_eintrags(self):
        e = menue_pruefen("Raute größer")
        self.assertTrue(e.ok)
        self.assertEqual(e.start, (587, 340))

    def test_der_name_ist_ohne_gross_und_kleinschreibung_und_als_anfang_gueltig(self):
        self.assertTrue(menue_pruefen("raute GRÖßER").ok)
        self.assertTrue(menue_pruefen("Raute: Deckkraft").ok)  # der Text enthält einen Zustand („80 %“); der Anfang genügt, wenn er eindeutig ist

    def test_ein_mehrdeutiger_anfang_wird_abgelehnt(self):
        e = menue_pruefen("Raute")
        self.assertEqual((e.ok, e.grund), (False, "menue_eintrag_unklar"))

    def test_ein_unbekannter_name_wird_abgelehnt(self):
        e = menue_pruefen("Festplatte formatieren")
        self.assertEqual((e.ok, e.grund), (False, "menue_eintrag_unbekannt"))

    def test_beenden_und_anhalten_sind_immer_gesperrt(self):
        for name in ("Bridge beenden", "Kira pausieren"):
            with self.subTest(name):
                e = menue_pruefen(name)
                self.assertEqual((e.ok, e.grund), (False, "menue_eintrag_gesperrt"))

    def test_ein_nicht_aufgelisteter_eintrag_ist_gesperrt_der_standard_ist_nein(self):
        e = menue_pruefen("Ort der Elemente")
        self.assertEqual((e.ok, e.grund), (False, "menue_eintrag_gesperrt"))

    def test_ein_abgeblendeter_erlaubter_eintrag_wird_abgelehnt(self):
        e = menue_pruefen("Raute kleiner")
        self.assertEqual((e.ok, e.grund), (False, "menue_eintrag_abgeblendet"))

    def test_die_sperrliste_gewinnt_auch_gegen_die_erlaubnisliste(self):
        alt = menue_freigabe.ERLAUBT["raute"]
        menue_freigabe.ERLAUBT["raute"] = alt | {4, 26}  # irrtümlich aufgenommen
        try:
            for name in ("Bridge beenden", "Kira pausieren"):
                with self.subTest(name):
                    self.assertEqual(menue_pruefen(name).grund, "menue_eintrag_gesperrt")
        finally:
            menue_freigabe.ERLAUBT["raute"] = alt

    def test_ein_unbekannte_menueart_erlaubt_nichts(self):
        fremd = OffenesMenue(MENUE_KENNUNG, "", MENUE.eintraege)
        self.assertEqual(menue_pruefen("Raute größer", menue_offen=fremd).grund, "menue_eintrag_gesperrt")

    def test_not_aus_und_haende_aus_gehen_vor(self):
        self.assertEqual(menue_pruefen("Raute größer", not_aus=True).grund, "not_aus")
        self.assertEqual(menue_pruefen("Raute größer", haende_erlaubt=False).grund, "haende_aus")
        self.assertEqual(menue_pruefen("Raute größer", profil_erlaubt=False).grund, "profil_erlaubt_nicht")

    def test_die_lease_bleibt_noetig(self):
        self.assertEqual(menue_pruefen("Raute größer", lease_grund="lease_fehlt").grund, "lease_fehlt")

    def test_jeder_grund_hat_einen_text(self):
        for grund in ("menue_nicht_freigegeben", "menue_nicht_offen", "menue_eintrag_unbekannt", "menue_eintrag_unklar", "menue_eintrag_gesperrt", "menue_eintrag_abgeblendet"):
            self.assertIn(grund, ea.GRUENDE)


class IdTests(unittest.TestCase):
    def test_die_ids_stimmen_mit_den_konstanten_des_koerpers_ueberein(self):
        from augen_haende_bridge.koerper import erster_koerper as ek

        for befehl, name in menue_freigabe.RAUTE_IDS.items():
            with self.subTest(name):
                self.assertEqual(getattr(ek, name), befehl)

    def test_die_sperrliste_enthaelt_beenden_notaus_anhalten_und_die_schranken(self):
        namen = {menue_freigabe.RAUTE_IDS[i] for i in menue_freigabe.IMMER_GESPERRT}
        for n in ("MENUE_AGENT_BEENDEN", "MENUE_BRIDGE_BEENDEN", "MENUE_NOTAUS", "MENUE_PAUSE", "MENUE_HAENDE", "MENUE_PROFIL", "MENUE_AUSNAHME"):
            self.assertIn(n, namen)

    def test_im_raute_menue_ist_nur_erlaubt_was_das_aussehen_aendert_oder_ein_geprueftes_untermenue_oeffnet(self):
        self.assertEqual({menue_freigabe.RAUTE_IDS[i] for i in menue_freigabe.ERLAUBT["raute"]},
                         {"MENUE_TRANSPARENZ", "MENUE_GROESSER", "MENUE_KLEINER", "MENUE_FARBE", "MENUE_ANZEIGEORT"})

    def test_ort_der_elemente_und_zeichnen_bleiben_gesperrt(self):
        for name in ("MENUE_ORT", "MENUE_ZEICHNEN", "MENUE_BILD_ELEMENT", "MENUE_BILD_DATEI", "MENUE_BILDFOLGE", "MENUE_PLAETZE", "MENUE_TERMINAL", "MENUE_BILDER"):
            with self.subTest(name):
                self.assertEqual(menue_freigabe.pruefe_eintrag("raute", getattr(__import__("augen_haende_bridge.koerper.erster_koerper", fromlist=["x"]), name)), "menue_eintrag_gesperrt")

    def test_die_farb_ids_stimmen_mit_der_anwendung_ueberein(self):
        from augen_haende_bridge.koerper import anwendung as an
        from augen_haende_bridge.koerper import stil

        self.assertEqual((menue_freigabe.FARBE_WAHL_ID, menue_freigabe.FARBE_STANDARD_ID, menue_freigabe.ANZAHL_FARBEN), (an.FARBE_WAHL_ID, an.FARBE_STANDARD_ID, len(stil.AGENTENFARBEN)))


class UntermenueTests(unittest.TestCase):
    def test_jede_farbe_und_die_standardfarbe_sind_erlaubt_nichts_daneben(self):
        for i in range(menue_freigabe.ANZAHL_FARBEN):
            self.assertEqual(menue_freigabe.pruefe_eintrag("raute.farbe", menue_freigabe.FARBE_WAHL_ID + i), "")
        self.assertEqual(menue_freigabe.pruefe_eintrag("raute.farbe", menue_freigabe.FARBE_STANDARD_ID), "")
        for fremd in (menue_freigabe.FARBE_WAHL_ID + menue_freigabe.ANZAHL_FARBEN, menue_freigabe.FARBE_WAHL_ID - 1, 4, 3900, 3950):
            self.assertEqual(menue_freigabe.pruefe_eintrag("raute.farbe", fremd), "menue_eintrag_gesperrt", fremd)

    def test_im_anzeigeort_menue_ist_kein_eintrag_erlaubt_weder_wechsel_noch_ziel(self):
        for befehl in (3900, 3901, 3950, 3951, 0, 1):
            self.assertEqual(menue_freigabe.pruefe_eintrag("raute.anzeigeort", befehl), "menue_eintrag_gesperrt", befehl)

    def test_die_sperrliste_des_raute_menues_trifft_ids_anderer_menues_nicht(self):
        # Befehls-Ids gelten nur innerhalb eines Menüs: die 4 (Bridge beenden im Raute-Menü) ist in einem anderen Menü keine Sperre, aber auch nicht erlaubt
        self.assertEqual(menue_freigabe.pruefe_eintrag("raute.farbe", 4), "menue_eintrag_gesperrt")
        self.assertNotIn(4, menue_freigabe.ERLAUBT["raute.farbe"])


class SchliessenTests(unittest.TestCase):
    def _mit_schliessen(self, geschlossen):
        return OffenesMenue(MENUE_KENNUNG, "raute.anzeigeort", MENUE.eintraege, schliessen=lambda: geschlossen.append(1))

    def test_schliessen_ist_in_jedem_offenen_menue_erlaubt_auch_ohne_art(self):
        for art in ("raute", "raute.anzeigeort", ""):
            with self.subTest(art):
                offen = OffenesMenue(MENUE_KENNUNG, art, MENUE.eintraege, schliessen=lambda: None)
                self.assertTrue(menue_pruefen("schließen", menue_offen=offen).ok)
                self.assertTrue(menue_pruefen("Schliessen", menue_offen=offen).ok)

    def test_ohne_freigabe_geht_auch_schliessen_nicht(self):
        self.assertEqual(menue_pruefen("schließen", menue_freigabe_an=False, menue_offen=self._mit_schliessen([])).grund, "menue_nicht_freigegeben")

    def test_ein_menue_ohne_schliessen_funktion_hat_keinen_solchen_eintrag(self):
        self.assertEqual(menue_pruefen("schließen").grund, "menue_eintrag_unbekannt")

    def test_die_engine_ruft_schliessen_auf_und_klickt_nichts(self):
        geschlossen = []
        e, b, _z = engine(Attrappe(am_punkt=MENUE_KENNUNG))
        e.menue_freigabe = True
        e.menue_offen = lambda: self._mit_schliessen(geschlossen)
        r = lauf(e, Aktion("menue", text="schließen"), bezug=None)
        self.assertEqual((r.status, r.delivered, r.observed.get("menue")), ("ausgefuehrt", 1, "geschlossen"))
        self.assertEqual(geschlossen, [1])
        self.assertEqual(b.log, [])  # keine Maus, keine Taste

    def test_ist_das_menue_zwischen_pruefung_und_schliessen_zu_wird_abgebrochen(self):
        e, b, _z = engine(Attrappe())
        e.menue_freigabe = True
        abrufe = iter([self._mit_schliessen([]), None])
        e.menue_offen = lambda: next(abrufe)
        r = lauf(e, Aktion("menue", text="schließen"), bezug=None)
        self.assertEqual((r.status, r.grund), ("abgebrochen", "menue_nicht_offen"))


class EngineMenueTests(unittest.TestCase):
    def _engine(self, am_punkt=MENUE_KENNUNG, offen=MENUE, freigabe=True):
        e, b, zeit = engine(Attrappe(am_punkt=am_punkt))
        e.menue_freigabe = freigabe
        e.menue_offen = lambda: offen
        return e, b

    def test_ein_erlaubter_eintrag_wird_in_seiner_mitte_angeklickt(self):
        e, b = self._engine()
        r = lauf(e, Aktion("menue", text="Raute größer"), bezug=None)
        self.assertEqual((r.status, r.accepted), ("ausgefuehrt", True))
        self.assertEqual(b.log[:3], [("bewegen", 587, 340), ("maus", "links", True), ("maus", "links", False)])
        self.assertEqual(b.runter_maus, set())

    def test_ohne_freigabe_geschieht_nichts(self):
        e, b = self._engine(freigabe=False)
        r = lauf(e, Aktion("menue", text="Raute größer"), bezug=None)
        self.assertEqual((r.status, r.grund, b.log), ("abgelehnt", "menue_nicht_freigegeben", []))

    def test_ein_gesperrter_eintrag_wird_nicht_angeruehrt(self):
        e, b = self._engine()
        r = lauf(e, Aktion("menue", text="Bridge beenden"), bezug=None)
        self.assertEqual((r.status, r.grund, b.log), ("abgelehnt", "menue_eintrag_gesperrt", []))

    def test_liegt_ein_anderes_fenster_am_punkt_wird_nicht_geklickt(self):
        e, b = self._engine(am_punkt=999)
        r = lauf(e, Aktion("menue", text="Raute größer"), bezug=None)
        self.assertEqual((r.status, r.grund), ("abgebrochen", "punkt_verdeckt"))
        self.assertEqual([x for x in b.log if x[0] == "maus"], [])

    def test_liegt_nach_dem_schliessen_wieder_das_ziel_am_punkt_wird_nicht_geklickt(self):
        e, b = self._engine()
        b.fenster_am_punkt = lambda x, y: 77  # das Menü ist zu, am Punkt liegt wieder das Ziel
        r = lauf(e, Aktion("menue", text="Raute größer"), bezug=None)
        self.assertEqual((r.status, r.grund), ("abgebrochen", "punkt_verdeckt"))
        self.assertEqual([x for x in b.log if x[0] == "maus"], [])

    def test_ist_das_menue_zwischen_pruefung_und_klick_zu_wird_nicht_geklickt(self):
        e, b = self._engine()
        abrufe = iter([MENUE, None])  # erster Abruf: Käfig, zweiter Abruf: unmittelbar vor dem Klick
        e.menue_offen = lambda: next(abrufe)
        r = lauf(e, Aktion("menue", text="Raute größer"), bezug=None)
        self.assertEqual((r.status, r.grund), ("abgebrochen", "punkt_verdeckt"))
        self.assertEqual([x for x in b.log if x[0] == "maus"], [])

    def test_das_register_ist_der_standard_und_ohne_eintrag_geschieht_nichts(self):
        e, b, _ = engine(Attrappe(am_punkt=MENUE_KENNUNG))
        e.menue_freigabe = True
        offene_menues.REGISTER.schliessen()
        r = lauf(e, Aktion("menue", text="Raute größer"), bezug=None)
        self.assertEqual((r.status, r.grund), ("abgelehnt", "menue_nicht_offen"))


class RegisterTests(unittest.TestCase):
    def test_oeffnen_aktuell_schliessen(self):
        reg = offene_menues.OffeneMenues()
        self.assertIsNone(reg.aktuell())
        reg.oeffnen(5, "raute", [MenueEintrag(7, "a", (0, 0, 10, 10))])
        self.assertEqual((reg.aktuell().kennung, reg.aktuell().art), (5, "raute"))
        reg.schliessen(6)  # ein fremdes Menü schließt dieses nicht
        self.assertIsNotNone(reg.aktuell())
        reg.schliessen(5)
        self.assertIsNone(reg.aktuell())

    def test_die_art_gilt_nur_im_block(self):
        self.assertEqual(offene_menues.aktuelle_art(), "")
        with offene_menues.menue_art("raute"):
            self.assertEqual(offene_menues.aktuelle_art(), "raute")
        self.assertEqual(offene_menues.aktuelle_art(), "")


class DanielsSchalterTests(unittest.TestCase):
    def _app(self, engine):
        from types import SimpleNamespace

        from augen_haende_bridge.koerper.anwendung import KoerperAnwendung

        app = KoerperAnwendung.__new__(KoerperAnwendung)
        app.haende_engine, app.status, app.meldungen = engine, "verbunden", []
        app.log = lambda text: app.meldungen.append(("log", text))
        app._setze_status = lambda status, text: app.meldungen.append(("status", text))
        return app, SimpleNamespace

    def test_nach_dem_start_ist_die_freigabe_aus(self):
        e, _b, _z = engine(Attrappe())
        self.assertFalse(e.menue_freigabe)

    def test_daniels_schalter_wechselt_zwischen_an_und_aus_und_meldet_es(self):
        e, _b, _z = engine(Attrappe())
        app, _ = self._app(e)
        app.menue_freigabe_umschalten()
        self.assertTrue(e.menue_freigabe)
        app.menue_freigabe_umschalten()
        self.assertFalse(e.menue_freigabe)
        self.assertEqual([m for m in app.meldungen if m[0] == "log"], [("log", "menue_freigabe an (Daniel, Regie-Menü)"), ("log", "menue_freigabe aus (Daniel, Regie-Menü)")])
        self.assertEqual(len([m for m in app.meldungen if m[0] == "status"]), 2)

    def test_ohne_engine_geschieht_nichts(self):
        app, _ = self._app(None)
        app.menue_freigabe_umschalten()
        self.assertEqual(app.meldungen, [])

    def test_das_regie_menue_selbst_ist_fuer_agenten_nie_bedienbar(self):
        # es wird ohne menue_art(...) geöffnet; ohne Art gibt es keine Erlaubnis
        self.assertEqual(offene_menues.aktuelle_art(), "")
        self.assertNotIn("", menue_freigabe.ERLAUBT)

    def test_die_menue_id_kollidiert_mit_keiner_anderen_konstante_der_anwendung(self):
        from augen_haende_bridge.koerper import anwendung as an

        werte = [v for k, v in vars(an).items() if k.endswith("_ID") and isinstance(v, int) and k != "MENUE_FREIGABE_ID"]
        self.assertNotIn(an.MENUE_FREIGABE_ID, werte)


class CliTests(unittest.TestCase):
    def _antwort(self, argv):
        import importlib.util
        import pathlib

        pfad = pathlib.Path(__file__).resolve().parent.parent / "client_vps" / "bridge_cli.py"
        spec = importlib.util.spec_from_file_location("bridge_cli_menue_test", pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        gesendet = []
        modul.ask = lambda anfrage, *a, **k: gesendet.append(anfrage) or {"ok": True}
        modul._haende(argv)
        return gesendet

    def test_menue_sendet_die_aktion_mit_dem_namen_und_ohne_koordinaten(self):
        gesendet = self._antwort(["menue", "Raute", "größer"])
        self.assertEqual(gesendet, [{"cmd": "haende", "aktion": {"art": "menue", "text": "Raute größer"}}])

    def test_menue_ohne_namen_ist_ein_falscher_aufruf(self):
        self.assertEqual(self._antwort(["menue"]), [])

    def test_die_vom_cli_gebaute_aktion_ist_fuer_den_koerper_gueltig(self):
        aktion = Aktion.aus_dict(self._antwort(["menue", "Raute größer"])[0]["aktion"])
        self.assertEqual((aktion.art, aktion.text), ("menue", "Raute größer"))


class SteuerprofilTests(unittest.TestCase):
    def test_die_menue_aktion_braucht_geteilte_maus_wie_ein_klick(self):
        from augen_haende_bridge.koerper import steuerprofil

        self.assertTrue(steuerprofil.profil("geteilte_maus").erlaubt("menue"))
        self.assertFalse(steuerprofil.profil("hintergrund").erlaubt("menue"))
        self.assertFalse(steuerprofil.profil("controller").erlaubt("menue"))


if __name__ == "__main__":
    unittest.main()
