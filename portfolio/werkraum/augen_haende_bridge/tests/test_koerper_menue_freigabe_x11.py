"""Die Menü-Freigabe mit allem Echten: ein GTK-Menü (`menue_linux.zeige_menue`), der echte `X11Backend` und die echte Engine.

Läuft nur in einer privaten Xvfb (`sh tests/lauf_xvfb.sh test_koerper_menue_freigabe_x11`), nie auf dem Desktop des Benutzers.
"""

from __future__ import annotations

import os
import threading
import time
import unittest

from test_koerper_eingabe_adapter import ZIEL, stand

DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"


@unittest.skipUnless(DISPLAY, "braucht die private Xvfb (BRIDGE_TEST_XVFB=1)")
class MenueKetteTests(unittest.TestCase):
    EINTRAEGE = [(5, "Kira · bereit", 0x00000001), None, (7, "Raute: Deckkraft 80 % → nächste Stufe", 0), (8, "Raute größer", 0),
                 (17, "Farbe wählen …", 0), (19, "Ort der Elemente (Desktop oder Zielfenster) …", 0), (4, "Bridge beenden", 0), (26, "Kira pausieren (Prozess anhalten)", 0)]

    def _lauf(self, text, freigabe=True, art="raute"):
        """Öffnet das Menü im Hauptfaden und lässt einen zweiten Faden als Agent handeln. Gibt (gewählte Id, Ergebnis des Agenten) zurück."""
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import GLib

        from augen_haende_bridge.koerper import eingabe_adapter as ea
        from augen_haende_bridge.koerper import menue_linux as ml
        from augen_haende_bridge.koerper import offene_menues

        offene_menues.REGISTER.schliessen()
        ergebnis, menue_ref = {}, {}

        def agent():
            try:
                for _ in range(300):  # warten, bis der Körper das Menü kennt
                    if offene_menues.REGISTER.aktuell() is not None:
                        break
                    time.sleep(0.01)
                backend = ea.X11Backend()
                e = ea.HaendeEngine(backend, ziel_stand=lambda z: stand(), ziel_kennung=lambda z: 77, schlafen=time.sleep)
                e.menue_freigabe = freigabe
                ergebnis["r"] = e.ausfuehren("a-1", ea.Aktion("menue", text=text), ziel=ZIEL, bezug=None, lease_grund="", haende_erlaubt=True)
            except Exception as fehler:  # pragma: no cover - sichtbar machen statt hängen
                ergebnis["fehler"] = repr(fehler)
            finally:
                if "r" not in ergebnis or ergebnis["r"].status != "ausgefuehrt":
                    GLib.idle_add(lambda: (menue_ref["m"].popdown(), False)[1])  # das Menü bleibt sonst offen

        def vorab(menue):
            menue_ref["m"] = menue
            menue_ref["t"] = threading.Thread(target=agent, daemon=True)
            menue_ref["t"].start()

        with offene_menues.menue_art(art):
            gewaehlt = ml.zeige_menue(1, self.EINTRAEGE, 500, 300, vorab=vorab)
        menue_ref["t"].join(10)  # der Klick schließt das Menü schon, bevor der Agentenfaden sein Ergebnis hat
        self.assertNotIn("fehler", ergebnis, ergebnis.get("fehler"))
        return gewaehlt, ergebnis["r"]

    def test_ein_erlaubter_eintrag_wird_ueber_den_namen_ausgeloest(self):
        gewaehlt, r = self._lauf("Raute größer")
        self.assertEqual((r.status, r.accepted), ("ausgefuehrt", True), r.grund)
        self.assertEqual(gewaehlt, 8)

    def test_der_name_darf_nur_der_anfang_sein_der_zustand_im_text_stoert_nicht(self):
        gewaehlt, r = self._lauf("Raute: Deckkraft")
        self.assertEqual((r.status, gewaehlt), ("ausgefuehrt", 7))

    def test_bridge_beenden_wird_nicht_geklickt_das_menue_bleibt_unberuehrt(self):
        gewaehlt, r = self._lauf("Bridge beenden")
        self.assertEqual((r.status, r.grund, r.delivered), ("abgelehnt", "menue_eintrag_gesperrt", 0))
        self.assertEqual(gewaehlt, 0)

    def test_pausieren_ist_gesperrt(self):
        gewaehlt, r = self._lauf("Kira pausieren")
        self.assertEqual((r.status, r.grund, gewaehlt), ("abgelehnt", "menue_eintrag_gesperrt", 0))

    def test_farbe_waehlen_oeffnet_das_untermenue_und_ist_erlaubt(self):
        gewaehlt, r = self._lauf("Farbe wählen")
        self.assertEqual((r.status, gewaehlt), ("ausgefuehrt", 17))

    def test_ort_der_elemente_ist_gesperrt(self):
        gewaehlt, r = self._lauf("Ort der Elemente")
        self.assertEqual((r.status, r.grund, gewaehlt), ("abgelehnt", "menue_eintrag_gesperrt", 0))

    def test_ohne_freigabe_geschieht_nichts(self):
        gewaehlt, r = self._lauf("Raute größer", freigabe=False)
        self.assertEqual((r.status, r.grund, gewaehlt), ("abgelehnt", "menue_nicht_freigegeben", 0))

    def test_ein_menue_ohne_art_wird_nie_bedient(self):
        gewaehlt, r = self._lauf("Raute größer", art="")
        self.assertEqual((r.status, r.grund, gewaehlt), ("abgelehnt", "menue_eintrag_gesperrt", 0))

    def test_der_abgeblendete_statuseintrag_wird_nicht_ausgeloest(self):
        gewaehlt, r = self._lauf("Kira · bereit")
        self.assertEqual((r.status, gewaehlt), ("abgelehnt", 0))

    def _lauf_mit(self, eintraege, text, art):
        vorher = self.EINTRAEGE
        MenueKetteTests.EINTRAEGE = eintraege
        try:
            return self._lauf(text, art=art)
        finally:
            MenueKetteTests.EINTRAEGE = vorher

    FARBEN = [(3200 + i, f"● Farbe {i}", 0) for i in range(8)] + [None, (3299, "Standardfarbe", 0)]
    ANZEIGEORT = [(0, "Läuft auf: kde1", 0x00000001), (0, "Angezeigt auf: kde1", 0x00000001), None, (3900, "Anzeigeort wechseln zu vd1", 0), (3950, "Arbeitsziel auf vd1 legen (ganzer Desktop) …", 0)]

    def test_im_farb_untermenue_waehlt_der_agent_eine_farbe(self):
        gewaehlt, r = self._lauf_mit(self.FARBEN, "● Farbe 3", "raute.farbe")
        self.assertEqual((r.status, gewaehlt), ("ausgefuehrt", 3203))

    def test_im_farb_untermenue_ist_die_standardfarbe_erlaubt(self):
        gewaehlt, r = self._lauf_mit(self.FARBEN, "Standardfarbe", "raute.farbe")
        self.assertEqual((r.status, gewaehlt), ("ausgefuehrt", 3299))

    def test_im_anzeigeort_untermenue_wird_kein_wechsel_und_kein_ziel_ausgeloest(self):
        for text in ("Anzeigeort wechseln", "Arbeitsziel auf vd1"):
            with self.subTest(text):
                gewaehlt, r = self._lauf_mit(self.ANZEIGEORT, text, "raute.anzeigeort")
                self.assertEqual((r.status, r.grund, gewaehlt), ("abgelehnt", "menue_eintrag_gesperrt", 0))

    def test_der_agent_schliesst_das_anzeigeort_menue_ohne_etwas_zu_aendern(self):
        gewaehlt, r = self._lauf_mit(self.ANZEIGEORT, "schließen", "raute.anzeigeort")
        self.assertEqual((r.status, r.observed.get("menue"), gewaehlt), ("ausgefuehrt", "geschlossen", 0))

    def test_schliessen_geht_auch_in_einem_menue_ohne_art(self):
        gewaehlt, r = self._lauf("schließen", art="")
        self.assertEqual((r.status, gewaehlt), ("ausgefuehrt", 0))

    def test_nach_dem_schliessen_kennt_der_koerper_das_menue_nicht_mehr(self):
        from augen_haende_bridge.koerper import offene_menues

        self._lauf("Raute größer")
        self.assertIsNone(offene_menues.REGISTER.aktuell())


if __name__ == "__main__":
    unittest.main()
