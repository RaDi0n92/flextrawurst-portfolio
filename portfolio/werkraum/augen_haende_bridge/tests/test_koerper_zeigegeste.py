"""G11: Zeigegesten — Inhaltshaftung, Warnung statt blindem Klick nach Layoutwechsel, Darstellung und Einfügung als getrennte Wege (echter Chromium, echte Arbeitsfläche)."""

from __future__ import annotations

import os
import time
import unittest

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import weltdom as wd
from augen_haende_bridge.koerper import weltdom_quellen as wq
from augen_haende_bridge.koerper import zeigegeste as zg
from augen_haende_bridge.koerper.komposition import Arbeitsflaechen
from augen_haende_bridge.koerper.objekte import Objekt
from augen_haende_bridge.koerper.weltdom_aktion import AktionsDienst
from tests.test_koerper_cdp import CHROMIUM, BrowserFall

DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
ZIEL = "kde1:window:42"
RECT = (100, 100, 500, 400)


def bezug(**kw):
    werte = dict(ziel=ZIEL, seq=3, captured_at_ms=10_000, breite=400, hoehe=300, rect=RECT, generation="g", dpi=1.0, bild_rect=RECT)
    werte.update(kw)
    return ea.Bildbezug(**werte)


def stand(**kw):
    werte = dict(vorhanden=True, rect=RECT, minimiert=False, generation="g", dpi=1.0)
    werte.update(kw)
    return ea.ZielStand(**werte)


def knopf(**kw):
    werte = dict(id="rea-cdp-1", ziel=ZIEL, herkunft="real", quelle="cdp", rolle="button", name="OK", rect=(300, 200, 360, 230), gemessen_ms=9_000, ttl_ms=5000, faehigkeiten=("klick",), aufloesung="cdp",
                 anker={"backend_id": 1, "rolle": "button", "name": "OK"})
    werte.update(kw)
    return wd.Knoten(**werte)


class GesteLogikTests(unittest.TestCase):
    def setUp(self):
        self.welt = wd.WeltDom()
        self.welt.ersetze(ZIEL, "real", "cdp", [knopf()])
        self.g = zg.erzeugen(ZIEL, (210, 110), bezug(), "codex", self.welt, 10_000)  # Bildschirmpunkt (310, 210): im Knopf

    def test_die_geste_haftet_am_inhalt_unter_dem_punkt(self):
        self.assertEqual((self.g.schirm, self.g.knoten_id, self.g.knoten_name), ((310, 210), "rea-cdp-1", "OK"))
        self.assertEqual(tuple(round(v, 4) for v in self.g.relativ), (0.525, 0.3667))
        leer = zg.erzeugen(ZIEL, (5, 5), bezug(), "codex", self.welt, 10_000)
        self.assertEqual((leer.knoten_id, leer.knoten_name), (None, ""), "ohne Inhalt unter dem Punkt bleibt es eine reine Fenstergeste")

    def test_bedienbares_geht_vor_dem_text_darin(self):
        text = knopf(id="rea-cdp-t", rolle="StaticText", name="OK", rect=(310, 205, 350, 225), faehigkeiten=("lesen",))
        self.welt.ersetze(ZIEL, "real", "cdp", [knopf(), text])
        g = zg.erzeugen(ZIEL, (210, 110), bezug(), "codex", self.welt, 10_000)
        self.assertEqual(g.knoten_id, "rea-cdp-1", "der Knopf, nicht das kleinere Etikett darin")

    def test_echte_knoten_gehen_vor_erschlossenen_und_erfundene_zaehlen_nicht(self):
        gross = wd.Knoten("inf-1", ZIEL, "inferred", "flaeche", "flaeche", "", "", (200, 150, 500, 400), 0.6, 9_000, 8000, 3, ("zeigen",), "koordinate")
        self.welt.ersetze(ZIEL, "inferred", "flaeche", [gross])
        self.welt.anker_anlegen(ZIEL, "Eigener Anker", (300, 200, 360, 230), urheber="daniel", jetzt_ms=9_500)
        g = zg.erzeugen(ZIEL, (210, 110), bezug(), "codex", self.welt, 10_000)
        self.assertEqual(g.knoten_id, "rea-cdp-1")

    def test_pruefungen_gueltig_fensterbindung_veraltet(self):
        self.assertEqual(zg.pruefen(self.g, stand(), 11_000, self.welt).status, "gueltig")
        self.assertEqual(zg.pruefen(self.g, stand(), 11_000, self.welt).schirm, (310, 210))
        p = zg.pruefen(self.g, stand(rect=(200, 150, 600, 450)), 11_000, self.welt)
        self.assertEqual((p.status, p.grund, p.schirm), ("fensterbindung", "fenster_verschoben", (410, 260)), "gleiche Größe, anderer Ort: die Geste folgt dem Fenster")
        self.assertIn("nicht dem Inhalt", p.warnung)
        for stand_, grund in ((None, "ziel_weg"), (stand(vorhanden=False), "ziel_weg"), (stand(minimiert=True), "ziel_minimiert"), (stand(generation="anderes"), "ziel_ersetzt")):
            p = zg.pruefen(self.g, stand_, 11_000, self.welt)
            self.assertEqual((p.status, p.grund, p.schirm), ("veraltet", grund, None), grund)
        p = zg.pruefen(self.g, stand(), 10_000 + zg.MAX_GESTE_ALTER_MS + 1, self.welt)
        self.assertEqual((p.status, p.grund), ("veraltet", "geste_zu_alt"))

    def test_layoutwechsel_loest_am_inhalt_neu_auf_oder_warnt(self):
        gross = stand(rect=(100, 100, 600, 400))
        neu = knopf(rect=(500, 200, 560, 230))
        p = zg.pruefen(self.g, gross, 11_000, self.welt, neu_aufloesen=lambda k: neu)
        self.assertEqual((p.status, p.schirm, p.knoten.id), ("neu_aufgeloest", (530, 215), "rea-cdp-1"))
        for ersatz in (lambda k: None, lambda k: knopf(rect=None), lambda k: knopf(herkunft="inferred", rect=(1, 1, 2, 2))):
            p = zg.pruefen(self.g, gross, 11_000, self.welt, neu_aufloesen=ersatz)
            self.assertEqual((p.status, p.grund, p.schirm, p.benutzbar), ("veraltet", "layout_geaendert", None, False))
        ohne_inhalt = zg.erzeugen(ZIEL, (5, 5), bezug(), "codex", self.welt, 10_000)
        self.assertEqual(zg.pruefen(ohne_inhalt, gross, 11_000, self.welt, neu_aufloesen=lambda k: neu).status, "veraltet", "eine Geste ohne Inhalt kann nicht neu aufgelöst werden")

    def test_dpi_wechsel_ist_ein_layoutwechsel(self):
        self.assertEqual(zg.pruefen(self.g, stand(dpi=1.5), 11_000, self.welt).status, "veraltet")

    def test_praesentieren_aendert_die_anwendung_nicht_und_sagt_es(self):
        gesetzt = []
        p = zg.pruefen(self.g, stand(), 11_000, self.welt)
        r = zg.praesentieren(self.g, p, stand(), lambda ziel, rel, text: gesetzt.append((ziel, rel, text)) or "o-1")
        self.assertEqual((r["status"], r["wirkung_in_anwendung"], r["overlay_objekt"]), ("praesentiert", False, "o-1"))
        self.assertEqual([(z, tuple(round(v, 4) for v in rel), t) for z, rel, t in gesetzt], [(ZIEL, (0.525, 0.3667), "codex: OK")])
        veraltet = zg.pruefen(self.g, stand(rect=(100, 100, 600, 400)), 11_000, self.welt)
        r = zg.praesentieren(self.g, veraltet, stand(rect=(100, 100, 600, 400)), lambda *a: "o-2")
        self.assertEqual((r["status"], r["pruefung"], bool(r["warnung"])), ("praesentiert", "veraltet", True), "eine veraltete Geste darf gezeigt werden, mit Warnung")
        self.assertEqual(zg.praesentieren(self.g, p, stand(), lambda *a: None)["status"], "fehler")

    def test_einfuegen_lehnt_veraltete_gesten_ab_und_fuehrt_nie_den_alten_pixel_aus(self):
        haende = []
        veraltet = zg.pruefen(self.g, stand(rect=(100, 100, 600, 400)), 11_000, self.welt)
        r = zg.einfuegen(self.g, veraltet, aktion="klick", text=None, dienst=None, haende_klick=lambda z, p: haende.append(p) or {"status": "ausgefuehrt"})
        self.assertEqual((r["status"], r["grund"], r["wirkung_in_anwendung"], haende), ("abgelehnt", "layout_geaendert", False, []))

    def test_einfuegen_ohne_inhalt_nur_klick_ueber_die_haende_auf_den_berechneten_punkt(self):
        haende = []
        leer = zg.erzeugen(ZIEL, (5, 5), bezug(), "codex", self.welt, 10_000)
        p = zg.pruefen(leer, stand(rect=(200, 150, 600, 450)), 11_000, self.welt)
        r = zg.einfuegen(leer, p, aktion="klick", text=None, dienst=None, haende_klick=lambda z, punkt: haende.append(punkt) or {"status": "ausgefuehrt"})
        self.assertEqual((r["status"], r["wirkung_in_anwendung"], haende), ("eingefuegt", True, [(205, 155)]), "dem Fenster gefolgt")
        self.assertEqual(zg.einfuegen(leer, p, aktion="text_setzen", text="x", dienst=None, haende_klick=None)["grund"], "kein_inhalt_und_nur_klick")


@unittest.skipUnless(DISPLAY and CHROMIUM, "kein privater Xvfb oder kein Chromium")
class InhaltshaftungRealTests(BrowserFall):
    """Ein echtes Beispiel: der Knopf wandert, wenn die Fensterbreite sich ändert (rechtsbündig). Die Geste folgt ihm; der alte Pixel würde danebenliegen."""

    def vorbereiten(self, s):
        s.auswerten("(() => { const st = document.createElement('style'); st.textContent = '#knopf { position: fixed; right: 20px; top: 20px; }'; document.head.appendChild(st); })()")
        s.befehl("Emulation.setDeviceMetricsOverride", width=800, height=500, deviceScaleFactor=1, mobile=False)
        time.sleep(0.3)

    def messen(self, s):
        welt = wd.WeltDom()
        ks = wq.aus_cdp(ZIEL, s, int(time.time() * 1000), inhalt_ursprung=(0, 0))
        welt.ersetze(ZIEL, "real", "cdp", ks)
        return welt, {(k.rolle, k.name): k for k in ks}

    def test_die_geste_folgt_dem_knopf_nach_dem_layoutwechsel_und_klickt_ihn(self):
        with self.seite() as s:
            self.vorbereiten(s)
            welt, n = self.messen(s)
            k = n[("button", "Zaehlen")]
            mitte = ((k.rect[0] + k.rect[2]) // 2, (k.rect[1] + k.rect[3]) // 2)
            w, h = s.fenstermass()
            fenster = (0, 0, w, h)
            g = zg.erzeugen(ZIEL, mitte, ea.Bildbezug(ZIEL, 1, int(time.time() * 1000), w, h, fenster, "seite", None, fenster), "claude", welt, int(time.time() * 1000))
            self.assertEqual(g.knoten_name, "Zaehlen")
            s.befehl("Emulation.setDeviceMetricsOverride", width=500, height=500, deviceScaleFactor=1, mobile=False)  # Layoutwechsel: der Knopf wandert nach links
            time.sleep(0.3)
            self.assertNotEqual(s.auswerten(f"document.elementFromPoint({mitte[0]}, {mitte[1]}) && document.elementFromPoint({mitte[0]}, {mitte[1]}).id"), "knopf", "der alte Pixel trifft den Knopf nicht mehr")
            w2, h2 = s.fenstermass()
            st = ea.ZielStand(True, (0, 0, w2, h2), False, "seite", None)

            def neu(alt):
                welt2, n2 = self.messen(s)
                return n2.get((alt.rolle, alt.name))

            p = zg.pruefen(g, st, int(time.time() * 1000), welt, neu_aufloesen=neu)
            self.assertEqual(p.status, "neu_aufgeloest", (p.status, p.grund))
            self.assertNotEqual(p.schirm, g.schirm, "der neue Punkt ist ein anderer")
            self.assertEqual(s.auswerten(f"document.elementFromPoint({p.schirm[0]}, {p.schirm[1]}).id"), "knopf", "der neu aufgelöste Punkt trifft den Knopf")
            dienst = AktionsDienst(welt, cdp_seite=lambda z: s, jetzt_ms=lambda: int(time.time() * 1000), schlafen=time.sleep)
            vorher = int(s.auswerten("document.getElementById('zahl').innerText"))
            # die Einfügung: eine echte Handlung mit eigenem Beleg
            welt.ersetze(ZIEL, "real", "cdp", wq.aus_cdp(ZIEL, s, int(time.time() * 1000), inhalt_ursprung=(0, 0)))
            r = zg.einfuegen(g, p, aktion="klick", text=None, dienst=dienst, haende_klick=None)
            self.assertEqual((r["status"], r["wirkung_in_anwendung"]), ("eingefuegt", True), r)
            self.assertEqual(int(s.auswerten("document.getElementById('zahl').innerText")), vorher + 1)

    def test_ohne_neuaufloesung_warnt_die_geste_und_nichts_wird_geklickt(self):
        with self.seite() as s:
            self.vorbereiten(s)
            welt, n = self.messen(s)
            k = n[("button", "Zaehlen")]
            mitte = ((k.rect[0] + k.rect[2]) // 2, (k.rect[1] + k.rect[3]) // 2)
            w, h = s.fenstermass()
            g = zg.erzeugen(ZIEL, mitte, ea.Bildbezug(ZIEL, 1, int(time.time() * 1000), w, h, (0, 0, w, h), "seite", None, (0, 0, w, h)), "claude", welt, int(time.time() * 1000))
            s.befehl("Emulation.setDeviceMetricsOverride", width=500, height=500, deviceScaleFactor=1, mobile=False)
            time.sleep(0.3)
            w2, h2 = s.fenstermass()
            p = zg.pruefen(g, ea.ZielStand(True, (0, 0, w2, h2), False, "seite", None), int(time.time() * 1000), welt)
            self.assertEqual((p.status, p.schirm), ("veraltet", None))
            vorher = s.auswerten("document.getElementById('zahl').innerText")
            klicks = []
            r = zg.einfuegen(g, p, aktion="klick", text=None, dienst=None, haende_klick=lambda z, pt: klicks.append(pt) or {"status": "ausgefuehrt"})
            self.assertEqual((r["status"], r["wirkung_in_anwendung"], klicks), ("abgelehnt", False, []))
            self.assertEqual(s.auswerten("document.getElementById('zahl').innerText"), vorher)
            self.assertTrue(r["warnung"])


class DarstellungRealTests(unittest.TestCase):
    """Die Darstellung geht in die echte gemeinsame Arbeitsfläche (G08) und nur dorthin."""

    def test_das_zeichen_steht_in_der_arbeitsflaeche_fuer_die_gewaehlten_empfaenger_und_die_anwendung_merkt_nichts(self):
        arbeit = Arbeitsflaechen()
        welt = wd.WeltDom()
        welt.ersetze(ZIEL, "real", "cdp", [knopf()])
        g = zg.erzeugen(ZIEL, (210, 110), bezug(), "codex", welt, 10_000)
        angefasst = []

        def overlay(ziel, rel, text):
            return arbeit.dokument(ziel).hinzufuegen(Objekt("zeige-1", "marker", [rel], text=text, bildschirm=True, empfaenger=("t-1", "t-2")))

        r = zg.praesentieren(g, zg.pruefen(g, stand(), 11_000, welt), stand(), overlay)
        self.assertEqual((r["status"], r["wirkung_in_anwendung"]), ("praesentiert", False))
        dok = arbeit.dokument(ZIEL)
        self.assertEqual([o.id for o in dok.fuer_empfaenger("t-1")], ["zeige-1"])
        self.assertEqual([o.id for o in dok.fuer_empfaenger("t-3")], [], "wer nicht gewählt ist, sieht es nicht")
        self.assertEqual([tuple(round(v, 4) for v in p) for p in dok.objekte["zeige-1"].punkte], [(0.525, 0.3667)])
        self.assertEqual(angefasst, [], "es gab keinen Aufruf an die Anwendung")


if __name__ == "__main__":
    unittest.main()
