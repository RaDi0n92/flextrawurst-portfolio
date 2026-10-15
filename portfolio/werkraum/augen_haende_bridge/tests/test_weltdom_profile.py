"""G11: WorldDOM-Profile — gemeinsam Angelegtes pro Programm, Seite oder Spiel speichern, versionieren, wiederfinden und laden; nichts überschreiben, nichts löschen, nichts raten."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge.koerper import weltdom_befehle as wb
from augen_haende_bridge.koerper.weltdom import WeltDom
from augen_haende_bridge.koerper.weltdom_dienst import WeltdomDienst
from augen_haende_bridge.koerper.weltdom_profile import ProfilFehler, ProfilSpeicher

ZIEL = "kde1:window:42"
FENSTER = (100, 200, 1100, 1000)  # 1000 x 800


def welt_mit_ankern():
    w = WeltDom()
    w.anker_anlegen(ZIEL, "Suchfeld", (600, 400, 640, 440), urheber="Daniel", jetzt_ms=1, relativ=(0.5, 0.25, 0.04, 0.05))
    w.anker_anlegen(ZIEL, "Notiz ohne Ort", None, urheber="Codex", jetzt_ms=1, relativ=None, herkunft="projected")
    w.anker_anlegen(ZIEL, "Nur Bildschirmort", (10, 10, 20, 20), urheber="Daniel", jetzt_ms=1)  # ohne relative Lage
    return w


class SpeicherTests(unittest.TestCase):
    def test_speichern_nimmt_nur_eigene_anker_mit_relativer_lage_und_nennt_den_rest(self):
        p = ProfilSpeicher()
        r = p.speichern(welt_mit_ankern(), ZIEL, "Browser Suche", urheber="Daniel", jetzt_ms=5, passt_auf={"programm": "firefox", "seite": "example.org"})
        self.assertEqual((r["version"], r["anker"], r["ohne_relative_lage_nicht_mitgenommen"]), (1, 1, 1))
        self.assertEqual([a["name"] for a in p.version("Browser Suche")["anker"]], ["Suchfeld"], "projizierte Knoten gehören nicht hinein")

    def test_jede_speicherung_ist_eine_neue_version_und_die_alte_bleibt(self):
        p, w = ProfilSpeicher(), welt_mit_ankern()
        p.speichern(w, ZIEL, "A", urheber="Daniel", jetzt_ms=1)
        w.anker_anlegen(ZIEL, "Zweiter", (700, 500, 720, 520), urheber="Daniel", jetzt_ms=2, relativ=(0.6, 0.37, 0.02, 0.03))
        r = p.speichern(w, ZIEL, "A", urheber="Daniel", jetzt_ms=3)
        self.assertEqual(r["version"], 2)
        self.assertEqual((len(p.version("A", 1)["anker"]), len(p.version("A", 2)["anker"])), (1, 2))
        self.assertIsNone(p.version("A", 3))

    def test_ungueltige_eingaben_und_leere_ziele(self):
        p = ProfilSpeicher()
        for name in ("", "../böse", "x" * 61, 5):
            with self.assertRaises(ProfilFehler):
                p.speichern(welt_mit_ankern(), ZIEL, name, urheber="D", jetzt_ms=1)
        for passt in ({"farbe": "rot"}, {"programm": ""}, {"programm": 5}, {"programm": "x" * 81}):
            with self.assertRaises(ProfilFehler):
                p.speichern(welt_mit_ankern(), ZIEL, "A", urheber="D", jetzt_ms=1, passt_auf=passt)
        with self.assertRaises(ProfilFehler) as c:
            p.speichern(WeltDom(), ZIEL, "Leer", urheber="D", jetzt_ms=1)
        self.assertEqual(str(c.exception), "keine_eigenen_anker")
        self.assertEqual(p.liste(), [], "nichts Halbes bleibt zurück")

    def test_ueberlebt_den_neustart_und_ignoriert_kaputte_dateien(self):
        pfad = Path(tempfile.mkdtemp()) / "profile.json"
        ProfilSpeicher(pfad).speichern(welt_mit_ankern(), ZIEL, "A", urheber="D", jetzt_ms=1, passt_auf={"spiel": "Doom"})
        neu = ProfilSpeicher(pfad)
        self.assertEqual(neu.liste()[0]["letzte"]["passt_auf"], {"spiel": "Doom"})
        pfad.write_text("kaputt{")
        k = ProfilSpeicher(pfad)
        self.assertEqual((k.liste(), bool(k.fehler)), ([], True))
        pfad.write_text(json.dumps({"version": 1, "profile": {"ok": {"versionen": [{"version": 1, "anker": []}]}, "../x": {"versionen": [{"version": 1, "anker": []}]}, "leer": {"versionen": []}}}))
        self.assertEqual([e["name"] for e in ProfilSpeicher(pfad).liste()], ["ok"])


class LadenTests(unittest.TestCase):
    def setUp(self):
        self.p = ProfilSpeicher()
        self.p.speichern(welt_mit_ankern(), ZIEL, "Browser Suche", urheber="Daniel", jetzt_ms=1)

    def test_laden_legt_die_anker_in_einem_anderen_fenster_an_derselben_relativen_stelle_an(self):
        neu = WeltDom()
        r = self.p.laden_in(neu, "kde2:window:7", "Browser Suche", FENSTER, urheber="Codex", jetzt_ms=9)
        self.assertEqual((r["geladen"], r["version"], r["ohne_fenster_uebersprungen"]), (1, 1, 0))
        k = neu.liste("kde2:window:7", herkunft="authored")[0]
        self.assertEqual(k.rect, (600, 400, 640, 440), "0,5 x 1000 + 100 = 600 und 0,25 x 800 + 200 = 400")
        self.assertEqual((k.urheber, k.name), ("Codex", "Suchfeld"))
        self.assertIn("aus Profil Browser Suche v1", k.wert)
        kleiner = WeltDom()
        self.p.laden_in(kleiner, "z2", "Browser Suche", (0, 0, 500, 400), urheber="Codex", jetzt_ms=9)
        self.assertEqual(kleiner.liste("z2")[0].rect, (250, 100, 270, 120), "bei halber Fenstergröße bleibt die Stelle relativ gleich")

    def test_ohne_bekanntes_fenster_wird_nichts_geraten(self):
        r = self.p.laden_in(WeltDom(), "z", "Browser Suche", None, urheber="D", jetzt_ms=1)
        self.assertEqual((r["geladen"], r["ohne_fenster_uebersprungen"]), (0, 1))

    def test_unbekannte_profile_versionen_und_ausgeblendete(self):
        with self.assertRaises(ProfilFehler) as c:
            self.p.laden_in(WeltDom(), "z", "Gibt es nicht", FENSTER, urheber="D", jetzt_ms=1)
        self.assertEqual(str(c.exception), "profil_unbekannt")
        with self.assertRaises(ProfilFehler) as c:
            self.p.laden_in(WeltDom(), "z", "Browser Suche", FENSTER, urheber="D", jetzt_ms=1, version=9)
        self.assertEqual(str(c.exception), "version_unbekannt")
        self.assertTrue(self.p.ausblenden("Browser Suche"))
        self.assertEqual(self.p.liste(), [])
        self.assertEqual(len(self.p.liste(mit_ausgeblendeten=True)), 1, "ausgeblendet ist nicht gelöscht")
        with self.assertRaises(ProfilFehler):
            self.p.laden_in(WeltDom(), "z", "Browser Suche", FENSTER, urheber="D", jetzt_ms=1)
        self.assertTrue(self.p.ausblenden("Browser Suche", True))
        self.assertEqual(self.p.laden_in(WeltDom(), "z", "Browser Suche", FENSTER, urheber="D", jetzt_ms=1)["geladen"], 1)
        self.assertFalse(self.p.ausblenden("gibts nicht"))

    def test_passende_findet_ueber_namen_und_laedt_nie_von_selbst(self):
        self.p.speichern(welt_mit_ankern(), ZIEL, "Doom Karte", urheber="D", jetzt_ms=1, passt_auf={"spiel": "Doom Eternal", "programm": "doom.exe"})
        self.p.speichern(welt_mit_ankern(), ZIEL, "Seite", urheber="D", jetzt_ms=1, passt_auf={"programm": "firefox", "seite": "example.org/suche"})
        self.assertEqual([e["name"] for e in self.p.passende(spiel="doom")], ["Doom Karte"])
        self.assertEqual([e["name"] for e in self.p.passende(programm="Firefox", seite="example.org")], ["Seite"])
        self.assertEqual(self.p.passende(programm="firefox", seite="andere.de"), [])
        self.assertEqual(self.p.passende(), [])
        self.assertEqual(self.p.passende(farbe="rot"), [])


class DienstUndBefehleTests(unittest.TestCase):
    def dienst(self, rect=FENSTER):
        bezug = (lambda tid, ziel, seq: SimpleNamespace(rect=rect)) if rect else (lambda tid, ziel, seq: None)
        return WeltdomDienst(welt_mit_ankern(), bezug=bezug, profile=ProfilSpeicher(), jetzt_ms=lambda: 1000)

    def test_dienst_speichern_liste_laden_weg(self):
        d = self.dienst()
        self.assertEqual(d.profil_speichern(ZIEL, "P", "Daniel", {"programm": "firefox"})["status"], "ok")
        self.assertEqual([e["name"] for e in d.profil_liste({"programm": "firefox"})["profile"]], ["P"])
        r = d.profil_laden("t-1", "kde2:window:7", "P", 3, "Codex")
        self.assertEqual((r["status"], r["geladen"], r["fenster_bekannt"]), ("ok", 1, True))
        self.assertEqual(d.profil_laden("t-1", "z", "nix", 3, "C")["grund"], "profil_unbekannt")
        self.assertEqual(d.profil_weg("P")["status"], "ok")
        self.assertEqual(d.profil_liste(None)["profile"], [])
        self.assertEqual(d.profil_weg("nix")["status"], "unaufloesbar")

    def test_ohne_bild_kein_geratener_ort(self):
        d = self.dienst(rect=None)
        d.profil_speichern(ZIEL, "P", "Daniel", None)
        r = d.profil_laden("t-1", "z", "P", None, "C")
        self.assertEqual((r["geladen"], r["ohne_fenster_uebersprungen"], r["fenster_bekannt"]), (0, 1, False))

    def test_ohne_profilspeicher_eine_klare_ablehnung(self):
        d = WeltdomDienst(WeltDom())
        self.assertEqual(d.profil_liste(None)["grund"], "profile_nicht_verfuegbar")
        self.assertEqual(d.profil_speichern(ZIEL, "P", "D", None)["grund"], "profile_nicht_verfuegbar")

    def test_befehle_werden_streng_geprueft(self):
        gut = [("profil_speichern", {"name": "P"}), ("profil_speichern", {"name": "P", "passt_auf": {"programm": "x"}, "beschreibung": "b"}), ("profil_laden", {"name": "P", "version": 2}),
               ("profil_liste", {}), ("profil_liste", {"passt_auf": {"spiel": "x"}, "alle": True}), ("profil_weg", {"name": "P", "aktiv": True})]
        for b, a in gut:
            self.assertIsNotNone(wb.pruefe_args(b, a), (b, a))
        schlecht = [("profil_speichern", {}), ("profil_speichern", {"name": ""}), ("profil_speichern", {"name": "P", "passt_auf": {"farbe": "r"}}), ("profil_speichern", {"name": "P", "extra": 1}),
                    ("profil_laden", {"name": "P", "version": 0}), ("profil_laden", {"name": "P", "version": True}), ("profil_liste", {"alle": "ja"}), ("profil_weg", {"name": "P", "aktiv": "ja"}),
                    ("profil_speichern", {"name": "P", "urheber": "ich"})]
        for b, a in schlecht:
            self.assertIsNone(wb.pruefe_args(b, a), (b, a))
        self.assertIsNotNone(wb.pruefe_args("profil_laden", {"name": "P", "urheber": "Starter"}, intern=True))
        for b in ("profil_speichern", "profil_laden", "profil_liste", "profil_weg"):
            self.assertFalse(wb.braucht_lease(b, {}), "Profile verwalten braucht keine Lease: sie handeln nicht an der Anwendung")


if __name__ == "__main__":
    unittest.main()
