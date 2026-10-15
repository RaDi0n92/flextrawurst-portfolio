"""Tests für koerper/kamera.py: Zustand, Sequenzierung und Fehlerbericht — mit einer injizierten Fake-Quelle für die
Logik, und einem echten `Cv2KameraQuelle`-Lauf gegen diesen Container (ohne Kamera-Hardware), um zu belegen, dass ein
fehlendes Gerät kontrolliert als benannter Fehlschlag zurückkommt statt als unbehandelte Ausnahme (G07: "Gerätefehler
... zurückgelesen"; `pruefe_koerper.py` V04 verbietet eine bloße Boolean-Attrappe)."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper.kamera import Cv2KameraQuelle, Kamera, KameraFehler

try:
    import cv2  # noqa: F401

    _CV2_DA = True
except ImportError:
    _CV2_DA = False


class FakeKameraQuelle:
    def __init__(self, *, oeffnen_ergebnis: bool = True, frames=None, wirft: Exception | None = None):
        self.oeffnen_ergebnis = oeffnen_ergebnis
        self.frames = list(frames or [])
        self.wirft = wirft
        self.oeffnen_aufrufe: list[int] = []
        self.geschlossen = False

    def oeffnen(self, index: int) -> bool:
        self.oeffnen_aufrufe.append(index)
        if self.wirft is not None:
            raise self.wirft
        return self.oeffnen_ergebnis

    def lesen(self):
        if not self.frames:
            return None
        return self.frames.pop(0)

    def schliessen(self) -> None:
        self.geschlossen = True


class EinschaltenTests(unittest.TestCase):
    def test_erfolgreiches_einschalten_setzt_aktiv_und_loescht_den_fehler(self) -> None:
        quelle = FakeKameraQuelle(oeffnen_ergebnis=True)
        kamera = Kamera(quelle=quelle)
        self.assertTrue(kamera.einschalten(0))
        self.assertTrue(kamera.aktiv)
        self.assertIsNone(kamera.letzter_fehler)

    def test_fehlendes_geraet_meldet_sich_statt_zu_taeuschen(self) -> None:
        quelle = FakeKameraQuelle(oeffnen_ergebnis=False)
        kamera = Kamera(quelle=quelle)
        self.assertFalse(kamera.einschalten(0))
        self.assertFalse(kamera.aktiv)
        self.assertEqual(kamera.letzter_fehler, "kamera_nicht_gefunden")

    def test_fehlendes_cv2_wird_als_kamerafehler_durchgereicht_statt_als_absturz(self) -> None:
        quelle = FakeKameraQuelle(wirft=KameraFehler("cv2_nicht_installiert"))
        kamera = Kamera(quelle=quelle)
        self.assertFalse(kamera.einschalten(0))
        self.assertEqual(kamera.letzter_fehler, "cv2_nicht_installiert")

    def test_zweimaliges_einschalten_oeffnet_das_geraet_nur_einmal(self) -> None:
        quelle = FakeKameraQuelle()
        kamera = Kamera(quelle=quelle)
        kamera.einschalten(2)
        kamera.einschalten(2)
        self.assertEqual(quelle.oeffnen_aufrufe, [2])


class FrameLesenTests(unittest.TestCase):
    def test_frames_tragen_eine_fortlaufende_sequenz_alter_und_herkunft(self) -> None:
        zeiten = iter([100, 116, 133])
        quelle = FakeKameraQuelle(frames=[(640, 480, b"\x00" * 12), (640, 480, b"\x01" * 12)])
        kamera = Kamera(quelle=quelle, jetzt_ms=lambda: next(zeiten))
        kamera.einschalten(1)

        erster = kamera.frame_lesen()
        self.assertEqual(erster.sequenz, 1)
        self.assertEqual(erster.aufgenommen_ms, 100)
        self.assertEqual((erster.breite, erster.hoehe), (640, 480))
        self.assertEqual(erster.bgr, b"\x00" * 12)
        self.assertEqual(erster.quelle, "cv2:1")

        zweiter = kamera.frame_lesen()
        self.assertEqual(zweiter.sequenz, 2)
        self.assertEqual(zweiter.aufgenommen_ms, 116)

    def test_ausgeschaltete_kamera_liefert_keine_frames(self) -> None:
        kamera = Kamera(quelle=FakeKameraQuelle(frames=[(1, 1, b"x")]))
        self.assertIsNone(kamera.frame_lesen())

    def test_ein_leerer_lesevorgang_meldet_einen_fehler_ohne_die_kamera_abzuschalten(self) -> None:
        quelle = FakeKameraQuelle(frames=[])
        kamera = Kamera(quelle=quelle)
        kamera.einschalten(0)
        self.assertIsNone(kamera.frame_lesen())
        self.assertEqual(kamera.letzter_fehler, "kein_frame")
        self.assertTrue(kamera.aktiv)  # ein einzelner leerer Lesevorgang ist kein Abschalten


class AusschaltenTests(unittest.TestCase):
    def test_ausschalten_gibt_das_geraet_frei(self) -> None:
        quelle = FakeKameraQuelle()
        kamera = Kamera(quelle=quelle)
        kamera.einschalten(0)
        kamera.ausschalten()
        self.assertFalse(kamera.aktiv)
        self.assertTrue(quelle.geschlossen)

    def test_ausschalten_ohne_vorheriges_einschalten_fasst_die_quelle_nicht_an(self) -> None:
        quelle = FakeKameraQuelle()
        Kamera(quelle=quelle).ausschalten()
        self.assertFalse(quelle.geschlossen)


@unittest.skipUnless(_CV2_DA, "cv2 nicht installiert")
class Cv2KameraQuelleTests(unittest.TestCase):
    """Echter cv2-Lauf gegen diesen Container: keine Kamera-Hardware vorhanden, das Fehlen wird kontrolliert gemeldet."""

    def test_fehlende_kamera_hardware_wird_zu_einem_benannten_fehlschlag_statt_einer_ausnahme(self) -> None:
        kamera = Kamera(quelle=Cv2KameraQuelle())
        ergebnis = kamera.einschalten(0)
        self.assertFalse(ergebnis)
        self.assertFalse(kamera.aktiv)
        self.assertIsNotNone(kamera.letzter_fehler)


class AutoIndexQuelle:
    """Mehrere Geräte: `geraete` bildet Index → Verhalten ('aus' geht nicht auf, 'leer' geht auf aber liefert kein Bild, 'bild' ok)."""

    def __init__(self, geraete):
        self.geraete, self.aktuell, self.offen, self.versuche = geraete, None, [], []

    def oeffnen(self, index):
        self.versuche.append(index)
        art = self.geraete.get(index, "aus")
        if art == "aus":
            return False
        self.aktuell = index
        self.offen.append(index)
        return True

    def lesen(self):
        return (2, 1, b"\x00" * 6) if self.geraete.get(self.aktuell) == "bild" else None

    def schliessen(self):
        if self.offen:
            self.offen.pop()


class AutoIndexTests(unittest.TestCase):
    def test_ohne_index_wird_das_erste_geraet_mit_bild_genommen(self) -> None:
        q = AutoIndexQuelle({1: "bild", 2: "bild"})
        k = Kamera(quelle=q)
        self.assertTrue(k.einschalten())
        self.assertEqual(k._index, 1)
        self.assertEqual(q.versuche, [0, 1])

    def test_geraet_das_aufgeht_aber_kein_bild_liefert_wird_uebersprungen_und_geschlossen(self) -> None:
        q = AutoIndexQuelle({0: "leer", 3: "bild"})
        k = Kamera(quelle=q)
        self.assertTrue(k.einschalten())
        self.assertEqual(k._index, 3)
        self.assertEqual(q.offen, [3])  # das leere Gerät wurde wieder geschlossen

    def test_keine_kamera_ist_ein_benannter_fehler(self) -> None:
        k = Kamera(quelle=AutoIndexQuelle({}))
        self.assertFalse(k.einschalten())
        self.assertEqual(k.letzter_fehler, "kamera_nicht_gefunden")

    def test_fehlende_bibliothek_bleibt_als_fehlertext_sichtbar(self) -> None:
        k = Kamera(quelle=FakeKameraQuelle(wirft=KameraFehler("opencv_fehlt")))
        self.assertFalse(k.einschalten())
        self.assertEqual(k.letzter_fehler, "opencv_fehlt")

    def test_expliziter_index_wird_nicht_durchsucht(self) -> None:
        q = AutoIndexQuelle({0: "bild", 2: "bild"})
        k = Kamera(quelle=q)
        self.assertTrue(k.einschalten(2))
        self.assertEqual(q.versuche, [2])
        k.ausschalten()
        q2 = AutoIndexQuelle({0: "bild"})
        k2 = Kamera(quelle=q2)
        self.assertFalse(k2.einschalten(2))
        self.assertEqual(q2.versuche, [2])

    def test_alter_fehler_wird_beim_naechsten_versuch_zurueckgesetzt(self) -> None:
        q = AutoIndexQuelle({})
        k = Kamera(quelle=q)
        k.einschalten()
        q.geraete = {1: "bild"}
        self.assertTrue(k.einschalten())
        self.assertIsNone(k.letzter_fehler)


if __name__ == "__main__":
    unittest.main()
