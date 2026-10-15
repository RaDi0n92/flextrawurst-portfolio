"""Bilderstrom: Ausschnitt je Ziel, nur Änderungen, Lebenszeichen, Not-Aus, verschwundenes Fenster."""

from __future__ import annotations

import base64
import time
import unittest

from augen_haende_bridge.koerper.bilderstrom import Bilderstrom, ausschnitt_hash

BREITE, HOEHE = 20, 10


def frame(farbe=0):
    return bytes([farbe]) * (BREITE * HOEHE * 4)


def punkt_gesetzt(roh: bytes, x: int, y: int, wert=255) -> bytes:
    b = bytearray(roh)
    b[(y * BREITE + x) * 4] = wert
    return bytes(b)


class Basis(unittest.TestCase):
    def strom(self, **ueber):
        self.roh = frame()
        self.erfassungen = 0
        self.gesendet = []
        self.kodiert = []
        self.zeit = {"t": 0.0}
        self.verschwunden = []
        self.fenster = {7: (2, 2, 12, 8)}

        def erfassen():
            self.erfassungen += 1
            return self.roh, BREITE, HOEHE

        def kodieren(raw, b, h, ausschnitt):
            self.kodiert.append(ausschnitt)
            return b"\xff\xd8\xffJPEG", ausschnitt[2] - ausschnitt[0], ausschnitt[3] - ausschnitt[1]

        def senden(tid, payload):
            self.gesendet.append((tid, payload))
            return self.sende_ok

        self.sende_ok = True
        werte = dict(erfassen=erfassen, bildschirm=lambda: (0, 0, BREITE, HOEHE), fenster_rect=self.fenster.get,
                     senden=senden, kodieren=kodieren, uhr=lambda: self.zeit["t"], jetzt_ms=lambda: 12345,
                     ziel_verschwunden=self.verschwunden.append, keepalive_s=15.0)
        werte.update(ueber)
        return Bilderstrom(**werte)


class SofortSendenTests(Basis):
    def test_sendet_jetzt_auch_bei_unveraendertem_fenster_und_nur_an_die_genannten(self):
        s = self.strom()
        s.binden("a", 7)
        s.binden("b", 7)
        s.binden("c", None)
        self.assertEqual(s.tick(), 3)
        self.gesendet.clear()
        self.assertEqual(s.tick(), 0, "unverändert, Keepalive noch nicht fällig: der Takt sendet nichts")
        self.assertEqual(s.sofort_senden(["a", "b"]), 2)
        self.assertEqual({t for t, _ in self.gesendet}, {"a", "b"})

    def test_wer_keine_augen_an_hat_oder_kein_ziel_bekommt_nichts(self):
        s = self.strom()
        s.binden("a", 7)
        s.binden("b", 7)
        s.tick()
        s.umschalten("b")  # Augen aus
        self.gesendet.clear()
        self.assertEqual(s.sofort_senden(["b", "unbekannt"]), 0)
        self.assertEqual(self.gesendet, [])
        self.assertEqual(s.sofort_senden([]), 0)

    def test_folgenummer_laeuft_weiter_und_der_verlauf_kennt_das_bild(self):
        s = self.strom()
        s.binden("a", 7)
        s.tick()
        s.sofort_senden(["a"])
        self.assertEqual([p["seq"] for t, p in self.gesendet], [0, 1])
        self.assertIsNotNone(s.bezug("a", 1))

    def test_not_aus_sperrt_auch_das_sofortbild(self):
        s = self.strom(gesperrt=lambda: True)
        s.binden("a", 7)
        self.assertEqual(s.sofort_senden(["a"]), 0)
        self.assertEqual(self.gesendet, [])


class SendenTests(Basis):
    def test_ohne_ziel_wird_nichts_aufgenommen(self):
        s = self.strom()
        self.assertEqual(s.tick(), 0)
        self.assertEqual(self.erfassungen, 0)

    def test_desktop_ziel_sendet_den_ganzen_bildschirm_als_jpeg_mit_metadaten(self):
        s = self.strom()
        s.binden("t-1", None)
        self.assertEqual(s.tick(), 1)
        tid, p = self.gesendet[0]
        self.assertEqual(tid, "t-1")
        self.assertEqual((p["mime"], p["source"], p["terminal_id"], p["width"], p["height"], p["captured_at_ms"]),
                         ("image/jpeg", "capture", "t-1", BREITE, HOEHE, 12345))
        self.assertTrue(base64.b64decode(p["data"]).startswith(b"\xff\xd8\xff"))
        self.assertEqual(self.kodiert[0], (0, 0, BREITE, HOEHE))

    def test_fenster_ziel_wird_auf_das_fenster_zugeschnitten(self):
        s = self.strom()
        s.binden("t-1", 7)
        s.tick()
        self.assertEqual(self.kodiert[0], (2, 2, 12, 8))

    def test_ausschnitt_folgt_dem_fenster(self):
        s = self.strom()
        s.binden("t-1", 7)
        s.tick()
        self.fenster[7] = (4, 1, 14, 7)
        self.roh = punkt_gesetzt(self.roh, 5, 3)  # irgendeine Änderung im neuen Ausschnitt
        s.tick()
        self.assertEqual(self.kodiert[-1], (4, 1, 14, 7))

    def test_festes_rechteck_ohne_fenster(self):
        s = self.strom()
        s.binden("t-1", None, (1, 1, 5, 5))
        s.tick()
        self.assertEqual(self.kodiert[0], (1, 1, 5, 5))

    def test_ein_frame_fuer_alle_agenten(self):
        s = self.strom()
        s.binden("a", 7)
        s.binden("b", None)
        self.assertEqual(s.tick(), 2)
        self.assertEqual(self.erfassungen, 1)
        self.assertEqual({t for t, _ in self.gesendet}, {"a", "b"})


class KeepaliveTests(unittest.TestCase):
    def test_der_keepalive_liegt_deutlich_unter_dem_hoechstalter_des_bezugsbilds(self):
        from augen_haende_bridge.koerper.bilderstrom import KEEPALIVE_S
        from augen_haende_bridge.koerper.eingabe_adapter import MAX_BILD_ALTER_MS

        self.assertLessEqual(KEEPALIVE_S * 1000 + 2000, MAX_BILD_ALTER_MS / 2, "Keepalive plus ein Takt höchstens die Hälfte des erlaubten Alters")


class SofortTests(Basis):
    """`see` fordert ein frisches Bild an: bei unverändertem Fenster kommt es beim nächsten Takt, nicht erst mit dem Keepalive nach 15 s."""

    def test_ohne_anforderung_wartet_ein_unverändertes_fenster_auf_den_keepalive(self):
        s = self.strom()
        s.binden("t-1", 7)
        self.assertEqual(s.tick(), 1)
        self.zeit["t"] += 2
        self.assertEqual(s.tick(), 0)

    def test_mit_anforderung_kommt_das_bild_beim_naechsten_takt_auch_ohne_aenderung(self):
        s = self.strom()
        s.binden("t-1", 7)
        s.tick()
        self.zeit["t"] += 2
        self.assertTrue(s.sofort("t-1"))
        self.assertEqual(s.tick(), 1)
        self.assertEqual(len(self.gesendet), 2)
        self.zeit["t"] += 2
        self.assertEqual(s.tick(), 0, "danach gilt wieder der normale Takt")

    def test_ohne_ziel_oder_bei_ausgeschaltetem_strom_gibt_es_nichts_zu_senden(self):
        s = self.strom()
        self.assertFalse(s.sofort("t-1"))
        s.binden("t-1", 7)
        s.ziele["t-1"].an = False
        self.assertFalse(s.sofort("t-1"))
        self.assertEqual(s.tick(), 0)


class AenderungenTests(Basis):
    def test_unveraendertes_bild_wird_nicht_erneut_gesendet(self):
        s = self.strom()
        s.binden("t-1", None)
        self.assertEqual(s.tick(), 1)
        self.zeit["t"] = 2
        self.assertEqual(s.tick(), 0)
        self.assertEqual(s.ziele["t-1"].uebersprungen, 1)

    def test_nach_dem_keepalive_kommt_trotzdem_ein_bild(self):
        s = self.strom()
        s.binden("t-1", None)
        s.tick()
        self.zeit["t"] = 16
        self.assertEqual(s.tick(), 1)

    def test_aenderung_im_ausschnitt_sendet_sofort(self):
        s = self.strom()
        s.binden("t-1", 7)
        s.tick()
        self.zeit["t"] = 2
        self.roh = punkt_gesetzt(self.roh, 5, 4)
        self.assertEqual(s.tick(), 1)

    def test_aenderung_ausserhalb_des_ausschnitts_sendet_nichts(self):
        s = self.strom()
        s.binden("t-1", 7)
        s.tick()
        self.zeit["t"] = 2
        self.roh = punkt_gesetzt(self.roh, 18, 0)
        self.assertEqual(s.tick(), 0)

    def test_fehlgeschlagenes_senden_wird_beim_naechsten_takt_wiederholt(self):
        s = self.strom()
        s.binden("t-1", None)
        self.sende_ok = False
        self.assertEqual(s.tick(), 0)
        self.sende_ok = True
        self.zeit["t"] = 2
        self.assertEqual(s.tick(), 1)


class SteuerungTests(Basis):
    def test_not_aus_nimmt_nichts_auf(self):
        gesperrt = {"an": True}
        s = self.strom(gesperrt=lambda: gesperrt["an"])
        s.binden("t-1", None)
        self.assertEqual(s.tick(), 0)
        self.assertEqual(self.erfassungen, 0)
        gesperrt["an"] = False
        self.assertEqual(s.tick(), 1)

    def test_verschwundenes_fenster_schaltet_auf_den_ganzen_desktop_und_meldet_es_einmal(self):
        s = self.strom()
        s.binden("t-1", 7)
        s.tick()
        del self.fenster[7]
        self.zeit["t"] = 2
        s.tick()
        s.tick()
        self.assertEqual(self.verschwunden, ["t-1"])
        self.assertTrue(s.an("t-1"))  # die Augen bleiben an
        self.assertIsNone(s.ziele["t-1"].hwnd)  # Ziel ist jetzt der ganze Bildschirm
        self.zeit["t"] = 4
        self.roh = punkt_gesetzt(self.roh, 1, 1)
        self.assertEqual(s.tick(), 1)  # und es kommen weiter Bilder
        self.assertEqual(self.gesendet[-1][1]["width"], BREITE)

    def test_umschalten_aus_und_wieder_an_sendet_sofort_ein_frisches_bild(self):
        s = self.strom()
        s.binden("t-1", None)
        s.tick()
        self.assertFalse(s.umschalten("t-1"))
        self.zeit["t"] = 1
        self.assertEqual(s.tick(), 0)
        self.assertTrue(s.umschalten("t-1"))
        self.assertEqual(s.tick(), 1)

    def test_loesen_und_unbekannter_agent(self):
        s = self.strom()
        s.binden("t-1", None)
        s.loesen("t-1")
        self.assertEqual(s.tick(), 0)
        self.assertFalse(s.umschalten("gibtsnicht"))
        self.assertFalse(s.an("gibtsnicht"))

    def test_neubindung_behaelt_den_schalter(self):
        s = self.strom()
        s.binden("t-1", None)
        s.umschalten("t-1")
        s.binden("t-1", 7)
        self.assertFalse(s.an("t-1"))

    def test_ausschnitt_ausserhalb_des_frames_wird_uebersprungen(self):
        s = self.strom()
        s.binden("t-1", None, (100, 100, 200, 200))
        self.assertEqual(s.tick(), 0)


class FadenTests(Basis):
    def test_faden_ruft_tick_und_ueberlebt_fehler(self):
        fehler = []
        aufrufe = {"n": 0}

        def erfassen():
            aufrufe["n"] += 1
            if aufrufe["n"] == 1:
                raise OSError("aufnahme")
            return frame(), BREITE, HOEHE

        s = self.strom(erfassen=erfassen, fehler=fehler.append, takt_s=0.01)
        s.binden("t-1", None)
        s.starten()
        ende = time.monotonic() + 3
        while time.monotonic() < ende and not self.gesendet:
            time.sleep(0.01)
        s.stoppen()
        self.assertTrue(self.gesendet)
        self.assertTrue(any("Bilderstrom" in f for f in fehler))


class HashTests(unittest.TestCase):
    def test_hash_reagiert_nur_auf_den_ausschnitt(self):
        a = frame()
        b = punkt_gesetzt(a, 18, 0)
        c = punkt_gesetzt(a, 5, 4)
        ausschnitt = (2, 2, 12, 8)
        self.assertEqual(ausschnitt_hash(a, BREITE, ausschnitt), ausschnitt_hash(b, BREITE, ausschnitt))
        self.assertNotEqual(ausschnitt_hash(a, BREITE, ausschnitt), ausschnitt_hash(c, BREITE, ausschnitt))


class KeineStilleTests(Basis):
    """Jeder Grund, aus dem ein Ziel kein Bild bekommt, steht im Log (nichts geschieht still und heimlich)."""

    def mit_log(self, **ueber):
        self.log = []
        return self.strom(fehler=self.log.append, **ueber)

    def test_verschwundenes_fenster_wird_gemeldet_und_der_strom_geht_auf_den_desktop(self):
        s = self.mit_log()
        s.binden("a", 7)
        del self.fenster[7]
        s.tick()
        self.assertTrue(any("fenster_weg" in z for z in self.log))
        self.zeit["t"] += 1.0
        self.assertEqual(s.tick(), 1)  # kein Stillstand: der ganze Desktop wird gesendet
        self.fenster[8] = (2, 2, 12, 8)
        s.binden("a", 8)  # ein neues Fenster bekommt sofort wieder Bilder, nichts wird mehr vererbt
        self.zeit["t"] += 1.0
        self.assertEqual(s.tick(), 1)

    def test_senden_abgelehnt_steht_im_log_und_wird_gedrosselt(self):
        s = self.mit_log()
        s.binden("a", 7)
        self.sende_ok = False
        s.tick()
        s.tick()
        gemeldet = [z for z in self.log if "senden_abgelehnt" in z]
        self.assertEqual(len(gemeldet), 1)  # zweimal derselbe Grund innerhalb einer Minute: eine Zeile
        self.zeit["t"] += 61.0
        s.tick()
        self.assertEqual(len([z for z in self.log if "senden_abgelehnt" in z]), 2)

    def test_not_aus_und_unsichtbares_ziel_haben_einen_grund(self):
        gesperrt = {"an": True}
        s = self.mit_log(gesperrt=lambda: gesperrt["an"], ziel_sichtbar=lambda hwnd: False)
        s.binden("a", 7)
        s.tick()
        self.assertTrue(any("gesperrt" in z for z in self.log))
        gesperrt["an"] = False
        self.zeit["t"] += 1.0
        s.tick()
        self.assertTrue(any("ziel_unsichtbar" in z for z in self.log))

    def test_herzschlag_kommt_einmal_pro_minute(self):
        s = self.mit_log()
        s.binden("a", 7)
        self.zeit["t"] = 100.0
        s.tick()
        s.tick()
        self.assertEqual(len([z for z in self.log if "Bilderstrom lebt" in z]), 1)
        self.zeit["t"] += 61.0
        s.tick()
        self.assertEqual(len([z for z in self.log if "Bilderstrom lebt" in z]), 2)


if __name__ == "__main__":
    unittest.main()
