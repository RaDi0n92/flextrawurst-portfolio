"""G11: Set-of-Mark — nummerierte Rahmen um bedienbare Knoten, Tabelle Nummer → Kennung, nur Gemessenes, begrenzt, echtes Bild."""

from __future__ import annotations

import io
import unittest

from PIL import Image

from augen_haende_bridge.koerper import weltdom_markierung as wm
from augen_haende_bridge.koerper.weltdom import WeltDom
from augen_haende_bridge.koerper.weltdom_dienst import WeltdomDienst

BEREICH = (100, 200, 500, 400)  # Bildschirmrechteck des Bildes: 400 x 200
B, H = 400, 200


def knoten(i, rect, herkunft="real", f=("klick",), **kw):
    return {"id": f"n-{i}", "rect": list(rect) if rect else None, "herkunft": herkunft, "faehigkeiten": list(f), "rolle": "button", "name": f"Knopf {i}", "alter_ms": 5, **kw}


def bgra(farbe=(255, 255, 255, 255)):
    return bytes(farbe) * (B * H)


class AuswahlTests(unittest.TestCase):
    def test_nur_bedienbare_gemessene_nicht_veraltete_mit_ort(self):
        ks = [knoten(1, (110, 210, 150, 230)), knoten(2, None), knoten(3, (110, 210, 150, 230), herkunft="projected"), knoten(4, (110, 210, 150, 230), f=("lesen",)), knoten(5, (110, 210, 150, 230), veraltet=True),
              knoten(6, (120, 220, 160, 240), herkunft="inferred"), knoten(7, (130, 230, 170, 250), herkunft="authored", f=("zeigen",))]
        gewaehlt, weg = wm.auswaehlen(ks)
        self.assertEqual([k["id"] for k in gewaehlt], ["n-1", "n-7", "n-6"], "echte vor eigenen vor erschlossenen")
        self.assertEqual(weg, 0)

    def test_kleine_vor_grossen_und_begrenzt(self):
        ks = [knoten(i, (100, 200, 100 + 5 + i, 200 + 5 + i)) for i in range(wm.MAX_MARKEN + 10)]
        gewaehlt, weg = wm.auswaehlen(ks)
        self.assertEqual((len(gewaehlt), weg, gewaehlt[0]["id"]), (wm.MAX_MARKEN, 10, "n-0"))


class BildTests(unittest.TestCase):
    def test_rahmen_liegen_an_der_richtigen_stelle_und_die_tabelle_nennt_kennungen(self):
        m = wm.markieren(bgra(), B, H, BEREICH, [knoten(1, (140, 240, 240, 290)), knoten(2, (300, 300, 380, 380), herkunft="inferred")])
        self.assertEqual([(t["nr"], t["knoten"], t["herkunft"]) for t in m["tabelle"]], [(1, "n-1", "real"), (2, "n-2", "inferred")])
        bild = Image.open(io.BytesIO(m["jpeg"])).convert("RGB")
        self.assertEqual(bild.size, (B, H))
        blau = bild.getpixel((40, 40))  # linke Kante des ersten Rahmens: (140 - 100, 240 - 200)
        self.assertLess(blau[0], 120)
        self.assertGreater(blau[2], 180, f"Rahmenfarbe echt = blau, war {blau}")
        self.assertGreater(sum(bild.getpixel((250, 40))), 700, "außerhalb der Rahmen bleibt es weiß")
        orange = bild.getpixel((200, 120))  # linke Kante des zweiten Rahmens
        self.assertTrue(orange[0] > 200 and orange[2] < 120, f"erschlossen = orange, war {orange}")

    def test_knoten_ausserhalb_des_bildes_werden_gezaehlt_nicht_gemalt(self):
        m = wm.markieren(bgra(), B, H, BEREICH, [knoten(1, (900, 900, 950, 950)), knoten(2, (110, 210, 150, 230))])
        self.assertEqual([t["knoten"] for t in m["tabelle"]], ["n-2"])
        self.assertEqual(m["weggelassen"], 1)
        self.assertEqual(m["tabelle"][0]["nr"], 1, "Nummern bleiben fortlaufend")

    def test_gross_skaliertes_bild_wird_verkleinert_und_bleibt_unter_der_grenze(self):
        gross = bytes((10, 20, 30, 255)) * (4000 * 2000)
        m = wm.markieren(gross, 4000, 2000, (0, 0, 4000, 2000), [knoten(1, (100, 100, 400, 300))])
        self.assertLessEqual((m["breite"], m["hoehe"]), (1920, 1080))
        self.assertLessEqual(len(m["jpeg"]), 1_000_000)


class DienstTests(unittest.TestCase):
    def test_markiert_liefert_jpeg_tabelle_und_den_hinweis_zum_handeln_ueber_kennungen(self):
        w = WeltDom()
        w.anker_anlegen("z", "Slot", (110, 210, 150, 230), urheber="Daniel", jetzt_ms=1000, relativ=(0.1, 0.1, 0.1, 0.1))
        d = WeltdomDienst(w, bild=lambda z: (bgra(), B, H, BEREICH), jetzt_ms=lambda: 1000)
        r = d.markiert("z", neu_messen=False)
        self.assertEqual(r["status"], "ok")
        self.assertTrue(r["_jpeg"].startswith(b"\xff\xd8"))
        self.assertEqual([t["name"] for t in r["tabelle"]], ["Slot"])
        self.assertIn("Knoten-Kennung", r["hinweis"])

    def test_ohne_aufnahme_wird_abgelehnt(self):
        d = WeltdomDienst(WeltDom(), bild=lambda z: None)
        self.assertEqual(d.markiert("z", neu_messen=False)["grund"], "keine_aufnahme")

    def test_befehlspruefung(self):
        from augen_haende_bridge.koerper import weltdom_befehle as wb

        self.assertEqual(wb.pruefe_args("markiert", {}), {})
        self.assertEqual(wb.pruefe_args("markiert", {"neu_messen": False}), {"neu_messen": False})
        for schlecht in ({"neu_messen": "ja"}, {"x": 1}):
            self.assertIsNone(wb.pruefe_args("markiert", schlecht))
        self.assertFalse(wb.braucht_lease("markiert", {}))


if __name__ == "__main__":
    unittest.main()
