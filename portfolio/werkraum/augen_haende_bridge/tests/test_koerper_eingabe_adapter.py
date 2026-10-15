"""G10: die Hände — Käfig (reine Logik), Engine (mit Attrappe) und die echten Plattformaufrufe gegen echte Fenster unter Xvfb."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper.eingabe_adapter import Aktion, Bildbezug, HaendeEngine, LeaseTabelle, ZielStand
from augen_haende_bridge.koerper.notaus import NotAus

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
ZIEL = "kde1:window:77"
RECT = (100, 100, 500, 400)  # 400 x 300


def bezug(**kw):
    werte = dict(ziel=ZIEL, seq=3, captured_at_ms=10_000, breite=400, hoehe=300, rect=RECT, generation="g1", dpi=1.0)
    werte.update(kw)
    return Bildbezug(**werte)


def stand(**kw):
    werte = dict(vorhanden=True, rect=RECT, minimiert=False, generation="g1", dpi=1.0)
    werte.update(kw)
    return ZielStand(**werte)


def pruefen(aktion, **kw):
    werte = dict(ziel=ZIEL, bezug=bezug(), stand=stand(), lease_grund="", not_aus=False, haende_erlaubt=True, profil_erlaubt=True, jetzt_ms=11_000)
    werte.update(kw)
    return ea.pruefe(aktion, **werte)


KLICK = Aktion("klick", punkt=(10, 20))


class KaefigTests(unittest.TestCase):
    def test_erlaubter_klick_wird_auf_den_bildschirm_umgerechnet(self):
        e = pruefen(KLICK)
        self.assertEqual((e.ok, e.start), (True, (110, 120)))

    def test_skalierung_zwischen_bild_und_fenster(self):
        halb = bezug(breite=200, hoehe=150)  # das Bild ist halb so groß wie das Fenster
        e = pruefen(Aktion("klick", punkt=(100, 75)), bezug=halb)
        self.assertEqual(e.start, (300, 250), "die Bildmitte ist die Fenstermitte")
        e = pruefen(Aktion("ziehen", punkt=(0, 0), bis=(199, 149), dauer_ms=200), bezug=halb)
        self.assertEqual((e.start, e.ende), ((100, 100), (498, 398)))

    def test_jeder_ablehnungsgrund_hat_seinen_fall(self):
        faelle = {
            "not_aus": dict(not_aus=True),
            "verbindung_weg": dict(verbindung=False),
            "daniel_uebernimmt": dict(daniel_uebernimmt=True),
            "haende_aus": dict(haende_erlaubt=False),
            "profil_erlaubt_nicht": dict(profil_erlaubt=False),
            "kein_ziel": dict(ziel=""),
            "lease_fehlt": dict(lease_grund="lease_fehlt"),
            "lease_abgelaufen": dict(lease_grund="lease_abgelaufen"),
            "lease_fremd": dict(lease_grund="lease_fremd"),
            "ziel_weg": dict(stand=stand(vorhanden=False)),
            "ziel_minimiert": dict(stand=stand(minimiert=True, rect=None)),
            "frame_unbekannt": dict(bezug=None),
            "frame_anderes_ziel": dict(bezug=bezug(ziel="kde1:window:99")),
            "frame_veraltet": dict(jetzt_ms=10_000 + ea.MAX_BILD_ALTER_MS + 1),
            "ziel_ersetzt": dict(stand=stand(generation="anderes-fenster")),
            "geometrie_geaendert": dict(stand=stand(rect=(110, 100, 510, 400))),
        }
        for grund, kw in faelle.items():
            e = pruefen(KLICK, **kw)
            self.assertEqual((e.ok, e.grund), (False, grund), grund)
            self.assertIn(grund, ea.GRUENDE)

    def test_dpi_wechsel_ist_geometrie_geaendert(self):
        self.assertEqual(pruefen(KLICK, stand=stand(dpi=1.5)).grund, "geometrie_geaendert")
        self.assertTrue(pruefen(KLICK, stand=stand(dpi=None)).ok, "ohne Angabe wird nicht verglichen")

    def test_punkte_ausserhalb_werden_abgelehnt(self):
        for p in ((-1, 5), (400, 5), (5, 300), (5, -1)):
            self.assertEqual(pruefen(Aktion("klick", punkt=p)).grund, "ausserhalb", p)
        self.assertEqual(pruefen(Aktion("ziehen", punkt=(5, 5), bis=(500, 5), dauer_ms=200)).grund, "ausserhalb", "auch das Ziehen-Ende zählt")
        self.assertTrue(pruefen(Aktion("klick", punkt=(399, 299))).ok)

    def test_der_desktop_ist_kein_ziel_fuer_haende(self):
        self.assertEqual(pruefen(KLICK, ziel="desktop").grund, "kein_ziel")

    def test_tastatur_braucht_kein_bild_aber_ein_ziel_und_keine_gesperrte_taste(self):
        self.assertTrue(pruefen(Aktion("tippen", text="hallo"), bezug=None).ok)
        self.assertTrue(pruefen(Aktion("taste", kombi="Strg+S"), bezug=None).ok)
        self.assertEqual(pruefen(Aktion("taste", kombi="F12"), bezug=None).grund, "notaus_taste")
        self.assertEqual(pruefen(Aktion("taste", kombi="Strg+F12"), bezug=None).grund, "notaus_taste")
        for k in ("Strg+Alt+Entf", "ctrl+alt+delete"):
            self.assertEqual(pruefen(Aktion("taste", kombi=k), bezug=None).grund, "systemtaste", k)
        self.assertEqual(pruefen(Aktion("tippen", text="x"), bezug=None, stand=stand(vorhanden=False)).grund, "ziel_weg")

    def test_reihenfolge_stopp_vor_rechten_vor_ziel_vor_bild(self):
        e = pruefen(KLICK, not_aus=True, haende_erlaubt=False, bezug=None)
        self.assertEqual(e.grund, "not_aus")
        e = pruefen(KLICK, haende_erlaubt=False, bezug=None)
        self.assertEqual(e.grund, "haende_aus")

    def test_aktionen_werden_streng_gelesen(self):
        gut = [{"art": "klick", "punkt": [1, 2]}, {"art": "ziehen", "punkt": [1, 2], "bis": [5, 6], "dauer_ms": 500}, {"art": "tippen", "text": "x"}, {"art": "taste", "kombi": "Strg+S"},
               {"art": "rad", "punkt": [1, 1], "dy": 3}, {"art": "doppelklick", "punkt": [1, 2], "taste": "rechts"}]
        for d in gut:
            a = Aktion.aus_dict(d)
            self.assertIsNotNone(a, d)
            self.assertEqual(Aktion.aus_dict(a.zu_dict()), a, "Runde über das Wörterbuch")
        schlecht = [None, 5, {}, {"art": "klick"}, {"art": "klick", "punkt": [1]}, {"art": "klick", "punkt": ["1", 2]}, {"art": "klick", "punkt": [1, 2], "x": 1}, {"art": "magie"},
                    {"art": "klick", "punkt": [1, 2], "taste": "mitte2"}, {"art": "ziehen", "punkt": [1, 2], "bis": [3, 4], "dauer_ms": 10}, {"art": "ziehen", "punkt": [1, 2], "bis": [3, 4], "dauer_ms": 99999},
                    {"art": "tippen", "text": ""}, {"art": "tippen", "text": "x" * 501}, {"art": "taste", "kombi": ""}, {"art": "rad", "punkt": [1, 1], "dy": 0}, {"art": "rad", "punkt": [1, 1], "dy": 99},
                    {"art": "klick", "punkt": [1, 2], "dauer_ms": "300"}, {"art": "klick", "punkt": [True, 2]}]
        for d in schlecht:
            self.assertIsNone(Aktion.aus_dict(d), d)

    def test_tastenkombinationen_in_windows_tastencodes(self):
        self.assertEqual(ea.kombi_zu_vk("Strg+Umschalt+S"), ([0x11, 0x10], 0x53))
        self.assertEqual(ea.kombi_zu_vk("ctrl+a"), ([0x11], 0x41))
        self.assertEqual(ea.kombi_zu_vk("F5"), ([], 0x74))
        self.assertEqual(ea.kombi_zu_vk("Alt+Tab"), ([0x12], 0x09))
        self.assertEqual(ea.kombi_zu_vk("Enter"), ([], 0x0D))
        for kaputt in ("", "Quatsch+x", "Strg+ä", "F25"):
            self.assertIsNone(ea.kombi_zu_vk(kaputt), kaputt)


class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.t = [0.0]
        self.l = LeaseTabelle(uhr=lambda: self.t[0], standard_ttl_s=10, max_ttl_s=60)

    def test_ein_halter_zugleich_und_ablauf_gibt_frei(self):
        a, _ = self.l.erwerben(ZIEL, "agent-a")
        self.assertEqual(self.l.erwerben(ZIEL, "agent-b"), (None, "belegt"))
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-a"), "")
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-b"), "lease_fremd")
        self.assertEqual(self.l.pruefen("l-falsch", ZIEL, "agent-a"), "lease_fehlt")
        self.t[0] = 10.5
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-a"), "lease_abgelaufen")
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-a"), "lease_fehlt", "danach ist sie entfernt")
        b, grund = self.l.erwerben(ZIEL, "agent-b")
        self.assertEqual(grund, "")
        self.assertEqual(self.l.pruefen(b.id, ZIEL, "agent-b"), "")

    def test_abgelaufen_wird_benannt_wenn_sie_noch_da_ist(self):
        a, _ = self.l.erwerben(ZIEL, "agent-a", ttl_s=5)
        self.t[0] = 5.0
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-a"), "lease_abgelaufen")

    def test_verlaengern_freigeben_entziehen_und_grenzen(self):
        a, _ = self.l.erwerben(ZIEL, "agent-a", ttl_s=5)
        self.t[0] = 4
        a2, _ = self.l.erwerben(ZIEL, "agent-a", ttl_s=5)
        self.assertEqual(a2.id, a.id)
        self.t[0] = 8
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-a"), "", "verlängert")
        self.assertFalse(self.l.freigeben(ZIEL, "agent-b"))
        self.assertTrue(self.l.freigeben(ZIEL, "agent-a"))
        self.assertEqual(self.l.pruefen(a.id, ZIEL, "agent-a"), "lease_fehlt")
        self.l.erwerben("kde1:window:1", "a")
        self.l.erwerben("kde1:window:2", "b")
        self.assertEqual(self.l.alle_entziehen(), 2)
        lang, _ = self.l.erwerben(ZIEL, "a", ttl_s=10_000)
        self.assertLessEqual(lang.bis - self.t[0], 60, "höchstens max_ttl")
        self.assertEqual(self.l.erwerben("kde1:window:8", "a", ttl_s=0), (None, "ttl_ungueltig"))
        self.assertEqual(self.l.erwerben("kde1:window:9", "a", ttl_s=-1), (None, "ttl_ungueltig"))

    def test_verschiedene_ziele_sind_unabhaengig(self):
        a, _ = self.l.erwerben("kde1:window:1", "agent-a")
        b, _ = self.l.erwerben("windows:window:2", "agent-b")
        self.assertEqual((self.l.pruefen(a.id, "kde1:window:1", "agent-a"), self.l.pruefen(b.id, "windows:window:2", "agent-b")), ("", ""))


class Attrappe(ea.Backend):
    """Merkt jede Eingabe; kann eine Verzögerung je Bewegung und einen Fehler simulieren."""

    name = "attrappe"

    def __init__(self, am_punkt=77, fokus=77, bewegung_s=0.0):
        self.log, self.am_punkt, self.fokus, self.bewegung_s, self.fehler_bei = [], am_punkt, fokus, bewegung_s, None
        self.runter_maus, self.runter_tasten = set(), set()
        self.pos = (0, 0)

    def _pruefe_fehler(self, was):
        if self.fehler_bei == was:
            return False
        return True

    def maus_bewegen(self, x, y):
        time.sleep(self.bewegung_s)
        self.pos = (x, y)
        self.log.append(("bewegen", x, y))
        return True

    def maus_taste(self, taste, runter):
        (self.runter_maus.add if runter else self.runter_maus.discard)(taste)
        self.log.append(("maus", taste, runter))
        return self._pruefe_fehler("maus")

    def rad(self, dy):
        self.log.append(("rad", dy))
        return True

    def taste(self, vk, runter):
        if self.fehler_bei == ("taste", vk) and runter:
            return False
        (self.runter_tasten.add if runter else self.runter_tasten.discard)(vk)
        self.log.append(("taste", vk, runter))
        return True

    def text(self, text):
        self.log.append(("text", text))
        return len(text) * 2

    def maus_position(self):
        return self.pos

    def fenster_am_punkt(self, x, y):
        return self.am_punkt

    def tastatur_fokus(self):
        return self.fokus

    def fokus_geben(self, kennung):
        self.fokus = kennung
        return True


def engine(backend=None, **kw):
    backend = backend or Attrappe()
    zeit = {"stand": stand()}
    e = HaendeEngine(backend, ziel_stand=lambda z: zeit["stand"], ziel_kennung=lambda z: 77, jetzt_ms=lambda: 11_000, schlafen=lambda s: None, **kw)
    return e, backend, zeit


def lauf(e, aktion, **kw):
    werte = dict(ziel=ZIEL, bezug=bezug(), lease_grund="", haende_erlaubt=True)
    werte.update(kw)
    return e.ausfuehren("a-1", aktion, **werte)


class EngineTests(unittest.TestCase):
    def test_klick_trennt_accepted_delivered_observed_und_audited(self):
        protokoll = []
        e, b, _ = engine(protokoll=protokoll.append)
        r = lauf(e, KLICK)
        self.assertEqual((r.status, r.accepted, r.delivered, r.audited), ("ausgefuehrt", True, 3, True))
        self.assertEqual(r.observed["zeiger"], [110, 120])
        self.assertEqual(b.log, [("bewegen", 110, 120), ("maus", "links", True), ("maus", "links", False)])
        self.assertEqual((protokoll[0]["ergebnis"]["status"], protokoll[0]["aktion"]["art"], protokoll[0]["ziel"]), ("ausgefuehrt", "klick", ZIEL))

    def test_abgelehnt_sendet_nichts_und_ist_nicht_accepted(self):
        e, b, _ = engine()
        r = lauf(e, KLICK, haende_erlaubt=False)
        self.assertEqual((r.status, r.grund, r.accepted, r.delivered), ("abgelehnt", "haende_aus", False, 0))
        self.assertEqual(b.log, [])

    def test_ein_anderes_fenster_vor_dem_punkt_stoppt_vor_dem_ersten_klick(self):
        e, b, _ = engine(Attrappe(am_punkt=99))
        r = lauf(e, KLICK)
        self.assertEqual((r.status, r.grund, r.delivered), ("abgebrochen", "punkt_verdeckt", 0))
        self.assertEqual(b.log, [])

    def test_doppelklick_und_rad_und_rechtsklick(self):
        e, b, _ = engine()
        self.assertEqual(lauf(e, Aktion("doppelklick", punkt=(5, 5))).delivered, 6)
        self.assertEqual(lauf(e, Aktion("klick", punkt=(5, 5), taste="rechts")).status, "ausgefuehrt")
        self.assertIn(("maus", "rechts", True), b.log)
        r = lauf(e, Aktion("rad", punkt=(5, 5), dy=-3))
        self.assertEqual((r.status, r.delivered), ("ausgefuehrt", 4))
        self.assertIn(("rad", -3), b.log)

    def test_ziehen_laeuft_in_schritten_und_laesst_los(self):
        e, b, _ = engine()
        r = lauf(e, Aktion("ziehen", punkt=(10, 10), bis=(210, 110), dauer_ms=300))
        self.assertEqual(r.status, "ausgefuehrt")
        bewegungen = [x for x in b.log if x[0] == "bewegen"]
        self.assertGreaterEqual(len(bewegungen), 10)
        self.assertEqual(bewegungen[0][1:], (110, 110))
        self.assertEqual(bewegungen[-1][1:], (310, 210))
        self.assertEqual(e.gedrueckt, set())
        self.assertEqual(b.runter_maus, set())

    def test_not_aus_mitten_im_ziehen_laesst_sofort_los_und_meldet_abgebrochen(self):
        na = NotAus()
        b = Attrappe(bewegung_s=0.01)
        e, _, _ = engine(b, not_aus=na)
        e._schlafen = time.sleep
        ergebnis = {}
        t = threading.Thread(target=lambda: ergebnis.update(r=lauf(e, Aktion("ziehen", punkt=(10, 10), bis=(300, 200), dauer_ms=3000))))
        t.start()
        time.sleep(0.4)
        self.assertEqual(b.runter_maus, {"links"}, "die Maustaste ist gerade gedrückt")
        na.ausloesen("F12")
        t.join(5)
        r = ergebnis["r"]
        self.assertEqual((r.status, r.grund), ("abgebrochen", "not_aus"))
        self.assertEqual((b.runter_maus, e.gedrueckt), (set(), set()), "nichts bleibt gedrückt")
        self.assertLess(len([x for x in b.log if x[0] == "bewegen"]), 150, "das Ziehen hat nicht zu Ende gemacht")
        self.assertEqual(lauf(e, KLICK).grund, "not_aus", "danach geht nichts, bis jemand freigibt")
        na.freigeben()
        self.assertEqual(lauf(e, KLICK).status, "ausgefuehrt")

    def test_verbindungsabbruch_stoppt_und_laesst_los(self):
        b = Attrappe(bewegung_s=0.01)
        e, _, _ = engine(b)
        e._schlafen = time.sleep
        ergebnis = {}
        t = threading.Thread(target=lambda: ergebnis.update(r=lauf(e, Aktion("ziehen", punkt=(10, 10), bis=(300, 200), dauer_ms=3000))))
        t.start()
        time.sleep(0.3)
        e.verbindung_verloren()
        t.join(5)
        self.assertEqual((ergebnis["r"].status, ergebnis["r"].grund), ("abgebrochen", "verbindung_weg"))
        self.assertEqual(b.runter_maus, set())
        self.assertEqual(lauf(e, KLICK).grund, "verbindung_weg")
        e.verbindung_da()
        self.assertEqual(lauf(e, KLICK).status, "ausgefuehrt")

    def test_wird_das_ziel_mitten_im_ziehen_verschoben_hoert_es_auf(self):
        b = Attrappe()
        e, _, zeit = engine(b)
        zaehler = [0]
        original = b.maus_bewegen

        def bewegen(x, y):
            zaehler[0] += 1
            if zaehler[0] == 6:
                zeit["stand"] = stand(rect=(120, 100, 520, 400))
            return original(x, y)

        b.maus_bewegen = bewegen
        r = lauf(e, Aktion("ziehen", punkt=(10, 10), bis=(300, 200), dauer_ms=600))
        self.assertEqual((r.status, r.grund), ("abgebrochen", "geometrie_geaendert"))
        self.assertEqual(b.runter_maus, set())

    def test_hotkey_drueckt_in_der_reihenfolge_und_laesst_in_umgekehrter_los(self):
        e, b, _ = engine()
        r = lauf(e, Aktion("taste", kombi="Strg+Umschalt+S"), bezug=None)
        self.assertEqual(r.status, "ausgefuehrt")
        self.assertEqual([x for x in b.log if x[0] == "taste"], [("taste", 0x11, True), ("taste", 0x10, True), ("taste", 0x53, True), ("taste", 0x53, False), ("taste", 0x10, False), ("taste", 0x11, False)])

    def test_scheitert_eine_taste_mitten_in_der_kombination_bleibt_nichts_haengen(self):
        b = Attrappe()
        b.fehler_bei = ("taste", 0x53)
        e, _, _ = engine(b)
        r = lauf(e, Aktion("taste", kombi="Strg+Umschalt+S"), bezug=None)
        self.assertEqual((r.status, r.grund), ("fehler", "backend_fehler"))
        self.assertEqual((b.runter_tasten, e.gedrueckt), (set(), set()), "Strg und Umschalt wurden wieder losgelassen")

    def test_tippen_prueft_den_fokus_vor_jedem_stueck_und_bricht_ab_wenn_er_wegfaellt(self):
        b = Attrappe()
        e, _, _ = engine(b)
        original = b.text

        def text(t):
            n = original(t)
            b.fokus = 5  # nach dem ersten Stück nimmt ein anderes Fenster die Tastatur
            return n

        b.text = text
        b.fokus_geben = lambda k: True  # und ließe sich nicht zurückholen: tastatur_fokus bleibt 5
        r = lauf(e, Aktion("tippen", text="x" * 30), bezug=None)
        self.assertIn(r.grund, ("fokus_verloren", "fokus_nicht_erreichbar"))
        self.assertEqual(len([x for x in b.log if x[0] == "text"]), 0 if r.grund == "fokus_nicht_erreichbar" else 1, "nach dem Verlust wird nichts mehr getippt")

    def test_fokus_wird_gegeben_wenn_es_geht_und_sonst_ehrlich_gemeldet(self):
        b = Attrappe(fokus=5)
        e, _, _ = engine(b)
        r = lauf(e, Aktion("tippen", text="hallo"), bezug=None)
        self.assertEqual((r.status, b.fokus), ("ausgefuehrt", 77))
        b2 = Attrappe(fokus=5)
        b2.fokus_geben = lambda k: False
        e2, _, _ = engine(b2)
        r = lauf(e2, Aktion("tippen", text="hallo"), bezug=None)
        self.assertEqual((r.status, r.grund, b2.log), ("abgebrochen", "fokus_nicht_erreichbar", []))

    def test_der_not_aus_schluessel_wird_auch_ueber_den_tastencode_erkannt(self):
        e, b, _ = engine(notaus_vk=0x7B)
        r = lauf(e, Aktion("taste", kombi="F12"), bezug=None)
        self.assertEqual((r.status, r.grund), ("abgelehnt", "notaus_taste"))
        self.assertEqual(b.log, [])

    def test_ein_kaputtes_protokoll_wird_gemeldet_nicht_verschluckt(self):
        def kaputt(_):
            raise OSError("platte voll")

        e, _, _ = engine(protokoll=kaputt)
        r = lauf(e, KLICK)
        self.assertEqual((r.status, r.audited), ("ausgefuehrt", False), "die Eingabe lief, aber sie ist nicht protokolliert: das steht im Ergebnis")

    def test_backend_fehler_beim_klick_wird_fehler_und_laesst_los(self):
        b = Attrappe()
        b.fehler_bei = "maus"
        e, _, _ = engine(b)
        r = lauf(e, KLICK)
        self.assertEqual((r.status, r.grund), ("fehler", "backend_fehler"))
        self.assertEqual(b.runter_maus, set())


HELFER = Path(__file__).resolve().parent / "helfer_gtk_haende.py"
if not HELFER.exists():
    HELFER = WURZEL / "tests" / "helfer_gtk_haende.py"


class GtkProgramm:
    """Ein echtes GTK-Fenster in einem eigenen Prozess; sein Stand kommt aus einer Datei."""

    def __init__(self, titel: str, x: int = 40, y: int = 40):
        self.titel = titel
        self.datei = Path(tempfile.mkdtemp()) / "stand.json"
        self.prozess = subprocess.Popen([sys.executable, str(HELFER), str(self.datei), titel], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.xid = None
        ende = time.monotonic() + 20
        while time.monotonic() < ende and self.xid is None:
            time.sleep(0.2)
            self.xid = self._suche()
        if self.xid is None:
            raise RuntimeError("GTK-Fenster nicht erschienen")
        self.bewegen(x, y)
        time.sleep(0.4)

    def _suche(self):
        from augen_haende_bridge.koerper import x11_helfer as x

        wurzel = x.anzeige().screen().root
        for kind in wurzel.query_tree().children:
            try:
                name = kind.get_wm_name()
            except Exception:
                continue
            if name == self.titel:
                return int(kind.id)
        return None

    def bewegen(self, x: int, y: int):
        from augen_haende_bridge.koerper import x11_helfer as x_

        f = x_.anzeige().create_resource_object("window", self.xid)
        f.configure(x=x, y=y)
        x_.anzeige().sync()
        time.sleep(0.4)

    def stand(self) -> dict:
        for _ in range(20):
            try:
                return json.loads(self.datei.read_text())
            except (OSError, ValueError):
                time.sleep(0.1)
        raise RuntimeError("kein Stand")

    def warte(self, bedingung, sekunden=5.0) -> dict:
        ende = time.monotonic() + sekunden
        s = self.stand()
        while time.monotonic() < ende and not bedingung(s):
            time.sleep(0.1)
            s = self.stand()
        return s

    def rect(self):
        from augen_haende_bridge.koerper import x11_helfer as x

        return x.fenster_rechteck(self.xid)

    def widget_mitte(self, name: str) -> tuple[int, int]:
        """Mitte eines Bedienelements in Bildkoordinaten (das Bild ist das ganze Fenster, 1:1)."""
        r = self.stand()["rects"][name]
        w = self.rect()
        return (r[0] + r[2]) // 2 - w[0], (r[1] + r[3]) // 2 - w[1]

    def beenden(self):
        self.prozess.terminate()
        try:
            self.prozess.wait(5)
        except subprocess.TimeoutExpired:
            self.prozess.kill()


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class X11HaendeTests(unittest.TestCase):
    def setUp(self):
        from augen_haende_bridge.koerper import x11_helfer as x
        from augen_haende_bridge.koerper.eingabe_adapter import X11Backend

        self.x = x
        self.a = GtkProgramm("HaendeA")
        self.addCleanup(self.a.beenden)
        self.backend = X11Backend()
        self.addCleanup(self.backend.schliessen)
        self.keys = {}
        self.na = NotAus()
        self.protokoll = []
        self.engine = HaendeEngine(self.backend, not_aus=self.na, ziel_stand=self.stand_von, ziel_kennung=lambda z: self.keys.get(z), protokoll=self.protokoll.append)
        self.keys["kde1:window:%d" % self.a.xid] = self.a.xid
        self.ziel_a = "kde1:window:%d" % self.a.xid
        self.seq = 0

    def stand_von(self, ziel):
        xid = self.keys.get(ziel)
        rect = self.x.fenster_rechteck(xid) if xid else None
        return ZielStand(rect is not None, rect, False, xid, 1.0)

    def bild(self, prog=None):
        prog = prog or self.a
        self.seq += 1
        r = prog.rect()
        return Bildbezug("kde1:window:%d" % prog.xid, self.seq, int(time.time() * 1000), r[2] - r[0], r[3] - r[1], r, prog.xid, 1.0)

    def tu(self, aktion, prog=None, **kw):
        prog = prog or self.a
        ziel = "kde1:window:%d" % prog.xid
        werte = dict(ziel=ziel, bezug=self.bild(prog), lease_grund="", haende_erlaubt=True)
        werte.update(kw)
        return self.engine.ausfuehren("a-%d" % self.seq, aktion, **werte)

    def test_klick_auf_die_schaltflaeche_wirkt_wirklich(self):
        r = None
        for _ in range(2):
            r = self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf")))
            self.assertEqual((r.status, r.accepted, r.delivered >= 3, r.audited), ("ausgefuehrt", True, True, True))
        s = self.a.warte(lambda s: s["klicks"] >= 2)
        self.assertEqual(s["klicks"], 2, "das Programm hat die zwei Klicks gezählt")
        self.assertEqual(self.protokoll[-1]["ergebnis"]["status"], "ausgefuehrt")

    def test_tippen_und_tastenkombination_wirken_im_eingabefeld(self):
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("feld"))).status, "ausgefuehrt")
        r = self.tu(Aktion("tippen", text="Grüße 🌍 abc"), bezug=None)
        self.assertEqual(r.status, "ausgefuehrt", r.grund)
        self.assertEqual(self.a.warte(lambda s: s["text"] == "Grüße 🌍 abc")["text"], "Grüße 🌍 abc")
        self.assertEqual(self.tu(Aktion("taste", kombi="Strg+A"), bezug=None).status, "ausgefuehrt")
        self.assertEqual(self.tu(Aktion("tippen", text="x"), bezug=None).status, "ausgefuehrt")
        self.assertEqual(self.a.warte(lambda s: s["text"] == "x")["text"], "x", "Strg+A markierte alles, das nächste Zeichen ersetzte es")
        self.assertEqual(self.tu(Aktion("taste", kombi="Strg+Umschalt+Z"), bezug=None).status, "ausgefuehrt")
        self.assertEqual(self.a.warte(lambda s: any(t[0] == "Z" and t[1] & 5 == 5 for t in s["tasten"]))["tasten"][-1][0], "Z")
        self.assertEqual(self.backend_keymap_leer(), True, "keine Taste bleibt gedrückt")

    def backend_keymap_leer(self) -> bool:
        return not any(self.x.anzeige().query_keymap())

    def test_doppelklick_rechtsklick_und_mausrad(self):
        mitte = self.a.widget_mitte("flaeche")
        self.assertEqual(self.tu(Aktion("doppelklick", punkt=mitte)).status, "ausgefuehrt")
        self.assertEqual(self.tu(Aktion("klick", punkt=mitte, taste="rechts")).status, "ausgefuehrt")
        self.assertEqual(self.tu(Aktion("rad", punkt=mitte, dy=3)).status, "ausgefuehrt")
        s = self.a.warte(lambda s: s["doppel"] >= 1 and s["rechts"] >= 1 and s["rad"] >= 3)
        self.assertEqual((s["doppel"], s["rechts"], s["rad"]), (1, 1, 3))

    def test_ziehen_hat_ein_echtes_ergebnis_und_laesst_los(self):
        r = self.a.stand()["rects"]["flaeche"]
        w = self.a.rect()
        von, bis = (r[0] + 40 - w[0], r[1] + 30 - w[1]), (r[0] + 300 - w[0], r[1] + 90 - w[1])
        ergebnis = self.tu(Aktion("ziehen", punkt=von, bis=bis, dauer_ms=400))
        self.assertEqual(ergebnis.status, "ausgefuehrt", ergebnis.grund)
        s = self.a.warte(lambda s: s["zug_punkte"] > 3 and not s["gedrueckt"])
        self.assertEqual((s["zug_start"], s["zug_ende"]), ([r[0] + 40, r[1] + 30], [r[0] + 300, r[1] + 90]))
        self.assertGreater(s["zug_punkte"], 5, "viele Zwischenschritte, kein Sprung")
        self.assertFalse(s["gedrueckt"])
        self.assertEqual(ergebnis.observed["zeiger"], ergebnis.observed["erwartet"])
        self.assertEqual(self.x.anzeige().screen().root.query_pointer().mask & 0x100, 0, "Taste 1 ist nicht mehr gedrückt")

    def test_schieberegler_per_klick_auf_die_spur(self):
        r = self.a.stand()["rects"]["regler"]
        w = self.a.rect()
        punkt = (r[0] + int((r[2] - r[0]) * 0.75) - w[0], (r[1] + r[3]) // 2 - w[1])
        self.assertEqual(self.tu(Aktion("klick", punkt=punkt)).status, "ausgefuehrt")
        self.assertGreater(self.a.warte(lambda s: s["regler"] > 30)["regler"], 30)

    # ---- Negativtests an echten Fenstern ------------------------------------------------------------------------------------
    def test_ein_fenster_davor_verhindert_den_klick(self):
        b = GtkProgramm("HaendeB", 40, 40)
        self.addCleanup(b.beenden)
        self.keys["kde1:window:%d" % b.xid] = b.xid
        bezug = self.bild(self.a)  # der Agent hat A gesehen, bevor B davor kam
        self.x.anzeige().create_resource_object("window", b.xid).configure(stack_mode=1 - 1)  # Above
        self.x.anzeige().sync()
        time.sleep(0.3)
        mitte = self.a.widget_mitte("knopf")
        r = self.tu(Aktion("klick", punkt=mitte), bezug=bezug)
        self.assertEqual((r.status, r.grund, r.delivered), ("abgebrochen", "punkt_verdeckt", 0))
        self.assertEqual(self.a.stand()["klicks"], 0)
        self.assertEqual(b.stand()["klicks"], 0, "auch das falsche Fenster bekommt keinen Klick")

    def test_falsches_ziel_veraltetes_bild_und_verschobenes_fenster(self):
        b = GtkProgramm("HaendeB", 600, 40)
        self.addCleanup(b.beenden)
        ziel_b = "kde1:window:%d" % b.xid
        self.keys[ziel_b] = b.xid
        mitte = self.a.widget_mitte("knopf")
        r = self.tu(Aktion("klick", punkt=mitte), prog=b, bezug=self.bild(self.a))
        self.assertEqual((r.grund, r.delivered), ("frame_anderes_ziel", 0), "Bild von A, Ziel B")
        alt = self.bild(self.a)
        r = self.tu(Aktion("klick", punkt=mitte), bezug=Bildbezug(alt.ziel, alt.seq, alt.captured_at_ms - 60_000, alt.breite, alt.hoehe, alt.rect, alt.generation, 1.0))
        self.assertEqual(r.grund, "frame_veraltet")
        gesehen = self.bild(self.a)
        self.a.bewegen(90, 70)
        r = self.tu(Aktion("klick", punkt=mitte), bezug=gesehen)
        self.assertEqual((r.status, r.grund, r.delivered), ("abgelehnt", "geometrie_geaendert", 0))
        self.assertEqual(self.a.stand()["klicks"] + b.stand()["klicks"], 0, "keiner der Klicks ist angekommen")

    def test_ohne_lease_ohne_rechte_und_im_not_aus_geht_nichts(self):
        mitte = self.a.widget_mitte("knopf")
        self.assertEqual(self.tu(Aktion("klick", punkt=mitte), lease_grund="lease_abgelaufen").grund, "lease_abgelaufen")
        self.assertEqual(self.tu(Aktion("klick", punkt=mitte), haende_erlaubt=False).grund, "haende_aus")
        self.na.ausloesen("test")
        self.assertEqual(self.tu(Aktion("klick", punkt=mitte)).grund, "not_aus")
        self.na.freigeben()
        time.sleep(0.3)
        self.assertEqual(self.a.stand()["klicks"], 0)

    def test_zwei_agenten_arbeiten_unabhaengig_an_zwei_fenstern(self):
        b = GtkProgramm("HaendeB", 600, 40)
        self.addCleanup(b.beenden)
        ziel_b = "kde1:window:%d" % b.xid
        self.keys[ziel_b] = b.xid
        fehler = []

        def arbeit(prog, n):
            try:
                for _ in range(n):
                    r = self.tu(Aktion("klick", punkt=prog.widget_mitte("knopf")), prog=prog)
                    if r.status != "ausgefuehrt":
                        fehler.append((prog.titel, r.grund))
            except Exception as e:  # pragma: no cover
                fehler.append((prog.titel, repr(e)))

        faeden = [threading.Thread(target=arbeit, args=(self.a, 12)), threading.Thread(target=arbeit, args=(b, 9))]
        [f.start() for f in faeden]
        [f.join(60) for f in faeden]
        self.assertEqual(fehler, [])
        self.assertEqual((self.a.warte(lambda s: s["klicks"] >= 12)["klicks"], b.warte(lambda s: s["klicks"] >= 9)["klicks"]), (12, 9), "jeder Klick landete im richtigen Fenster")


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class X11StopTests(X11HaendeTests):
    """Der lokale Stop an echten Fenstern: F12 über den echten Hook, Verbindungsabbruch, hängende Tasten."""

    def setUp(self):
        super().setUp()
        from augen_haende_bridge.koerper.linux_adapter import LinuxNotAusHook

        self.hook = LinuxNotAusHook(self.na)
        self.assertTrue(self.hook.start(), self.hook.fehler)
        self.addCleanup(lambda: self.hook.stop() if hasattr(self.hook, "stop") else None)

    def lange_aktion(self):
        r = self.a.stand()["rects"]["flaeche"]
        w = self.a.rect()
        ergebnis = {}
        aktion = Aktion("ziehen", punkt=(r[0] + 20 - w[0], r[1] + 20 - w[1]), bis=(r[0] + 380 - w[0], r[1] + 100 - w[1]), dauer_ms=5000)
        faden = threading.Thread(target=lambda: ergebnis.update(r=self.tu(aktion)))
        faden.start()
        self.a.warte(lambda s: s["gedrueckt"], 5)
        return faden, ergebnis

    def f12_druecken(self):
        from augen_haende_bridge.koerper import linux_adapter as la

        la.xtest_senden([(0x7B, 0, 0), (0x7B, 0, 0x0002)])

    def test_f12_stoppt_ein_laufendes_ziehen_und_nichts_bleibt_gedrueckt(self):
        faden, ergebnis = self.lange_aktion()
        t0 = time.monotonic()
        self.f12_druecken()
        self.assertTrue(self.na.aktiv or self.warte_na())
        faden.join(5)
        dauer = time.monotonic() - t0
        r = ergebnis["r"]
        self.assertEqual((r.status, r.grund), ("abgebrochen", "not_aus"))
        s = self.a.warte(lambda s: not s["gedrueckt"])
        self.assertFalse(s["gedrueckt"])
        self.assertEqual(self.x.anzeige().screen().root.query_pointer().mask & 0x100, 0, "die Maustaste ist losgelassen")
        self.assertTrue(self.backend_keymap_leer())
        print(f"[gemessen] F12 bis Ende des Auftrags: {dauer * 1000:.0f} ms (Messwert dieses Laufs, keine Zusage)")

    def warte_na(self):
        ende = time.monotonic() + 3
        while time.monotonic() < ende and not self.na.aktiv:
            time.sleep(0.01)
        return self.na.aktiv

    def test_f12_wirkt_auch_wenn_der_gui_faden_haengt(self):
        faden, ergebnis = self.lange_aktion()
        threading.Timer(0.5, self.f12_druecken).start()
        time.sleep(1.5)  # der „GUI-Faden“ (dieser) tut nichts und pumpt nichts
        faden.join(5)
        self.assertEqual((ergebnis["r"].status, ergebnis["r"].grund), ("abgebrochen", "not_aus"))
        self.assertFalse(self.a.stand()["gedrueckt"])

    def test_verbindungsabbruch_stoppt_das_ziehen(self):
        faden, ergebnis = self.lange_aktion()
        t0 = time.monotonic()
        self.engine.verbindung_verloren()
        faden.join(5)
        self.assertEqual((ergebnis["r"].status, ergebnis["r"].grund), ("abgebrochen", "verbindung_weg"))
        self.assertFalse(self.a.warte(lambda s: not s["gedrueckt"])["gedrueckt"])
        print(f"[gemessen] Verbindungsabbruch bis Ende des Auftrags: {(time.monotonic() - t0) * 1000:.0f} ms")
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf"))).grund, "verbindung_weg")

    def test_hotkey_von_f12_wird_nicht_gesendet_und_haengende_tasten_gibt_es_nicht(self):
        r = self.tu(Aktion("taste", kombi="Strg+F12"), bezug=None)
        self.assertEqual(r.grund, "notaus_taste")
        self.assertFalse(self.na.aktiv, "der Körper hat seinen eigenen Not-Aus nicht ausgelöst")
        self.assertTrue(self.backend_keymap_leer())

    def test_nach_dem_not_aus_geht_es_erst_nach_freigabe_wieder(self):
        faden, ergebnis = self.lange_aktion()
        self.f12_druecken()
        faden.join(5)
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf"))).grund, "not_aus")
        self.na.freigeben()
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf"))).status, "ausgefuehrt")


@unittest.skipUnless(__import__("shutil").which("wine") and Path("/config/wine-bridge-build/prefix").exists(), "Wine fehlt")
class WineHaendeTests(unittest.TestCase):
    """Die Windows-Fassung (SendInput) gegen ein echtes Win32-Fenster unter Wine: das Fenster zählt, was wirklich bei ihm ankam."""

    @classmethod
    def setUpClass(cls):
        env = {**os.environ, "PYTHONPATH": str(WURZEL / "src"), "WINEPREFIX": "/config/wine-bridge-build/prefix", "WINEARCH": "win64", "WINEDEBUG": "-all", "WINEDLLOVERRIDES": "mscoree,mshtml="}
        lauf = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1280x800x24", "wine", "C:\\Python313\\python.exe", str(WURZEL / "probes" / "haende_wine.py")], env=env, capture_output=True, text=True, timeout=240)
        zeilen = [z for z in lauf.stdout.splitlines() if z.startswith("{")]
        if not zeilen:
            raise AssertionError(lauf.stdout[-500:] + lauf.stderr[-500:])
        cls.r = json.loads(zeilen[0])

    def test_alle_aktionen_sind_ausgefuehrt(self):
        for name in ("klick", "tippen", "taste", "rad", "ziehen"):
            self.assertEqual((self.r[name]["status"], self.r[name]["grund"]), ("ausgefuehrt", ""), name)

    def test_das_fenster_hat_klick_zeichen_taste_rad_und_ziehen_wirklich_empfangen(self):
        f = self.r["fenster"]
        self.assertEqual((f["klick_runter"], f["klick_hoch"]), (2, 2), "ein Klick und ein Ziehen")
        self.assertEqual(f["zeichen"][:8], "Hallo äö")
        self.assertEqual(f["tasten"][-2:], [0x11, 0x41], "Strg dann A")
        self.assertGreaterEqual(f["rad"], 1)
        self.assertGreater(f["bewegt"], 5, "das Ziehen kam in Schritten an")
        self.assertEqual(f["ziehen_ende"], [300 - 0, 200 - 0], "Ende des Ziehens in Fensterkoordinaten")
        self.assertFalse(f["gedrueckt"], "die Maustaste ist losgelassen")

    def test_zeiger_wurde_auf_den_berechneten_bildschirmpunkt_gesetzt(self):
        self.assertEqual(self.r["klick"]["observed"]["zeiger"], [self.r["rect"][0] + 100, self.r["rect"][1] + 100])
        self.assertEqual(self.r["ziehen"]["observed"]["zeiger"], self.r["ziehen"]["observed"]["erwartet"])


@unittest.skipUnless(__import__("shutil").which("wine") and __import__("shutil").which("Xvfb") and Path("/config/wine-bridge-build/prefix").exists(), "Wine oder Xvfb fehlt")
class WineUebernahmeTests(unittest.TestCase):
    """Windows-Hooks mit dem Injected-Merkmal: die Hände (SendInput) sind „injiziert“, fremde X-Eingabe ist für Wine Hardware. Keine echte Hardware, kein natives Windows."""

    def test_haende_sind_injiziert_fremde_eingabe_stoppt_sie_und_nach_der_pause_geht_es_weiter(self):
        nummer = next(n for n in range(90, 200) if not Path(f"/tmp/.X11-unix/X{n}").exists())
        xv = subprocess.Popen(["Xvfb", f":{nummer}", "-screen", "0", "1280x800x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(xv.terminate)
        time.sleep(1.5)
        env = {**os.environ, "DISPLAY": f":{nummer}", "PYTHONPATH": str(WURZEL / "src"), "WINEPREFIX": "/config/wine-bridge-build/prefix", "WINEARCH": "win64", "WINEDEBUG": "-all",
               "WINEDLLOVERRIDES": "mscoree,mshtml="}
        p = subprocess.Popen(["wine", "C:\\Python313\\python.exe", str(WURZEL / "probes" / "uebernahme_wine.py")], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.addCleanup(p.kill)
        phase1 = ende = None
        for zeile in p.stdout:
            if zeile.startswith("PHASE1"):
                phase1 = json.loads(zeile.split(" ", 1)[1])
                from Xlib import X, display
                from Xlib.ext import xtest

                d = display.Display(f":{nummer}")
                for i in range(6):
                    xtest.fake_input(d, X.MotionNotify, 0, 0, d.screen().root, 300 + i * 7, 300)
                    d.sync()
                    time.sleep(0.05)
            elif zeile.startswith("ENDE"):
                ende = json.loads(zeile.split(" ", 1)[1])
        p.wait(timeout=60)
        self.assertTrue(phase1["hooks"], "Hooks installiert")
        self.assertEqual((phase1["klick"], phase1["ziehen"], phase1["gesehen"]["physisch"], phase1["erkannt"]), ("ausgefuehrt", "ausgefuehrt", 0, 0), "eigene Eingabe löst nie die Übernahme aus")
        self.assertGreater(phase1["gesehen"]["injiziert"], 20)
        self.assertGreaterEqual(ende["erkannt"], 1, "fremde Eingabe wurde erkannt")
        self.assertEqual(ende["waehrend_pause"], ["abgelehnt", "daniel_uebernimmt"])
        self.assertTrue(ende["nach_pause"] == "ausgefuehrt" or ende["zweiter_versuch"] == "ausgefuehrt", "nach der Pause arbeiten die Hände wieder")


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class X11UebernahmeTests(X11HaendeTests):
    """Daniel übernimmt (X11, gezählt): eine zweite Eingabequelle spielt Daniel."""

    def setUp(self):
        super().setUp()
        from Xlib import display

        from augen_haende_bridge.koerper.uebernahme import Uebernahme, X11Aufzeichnung

        self.ausnahme = [False]
        self.ueb = Uebernahme(self.engine, ausnahme=lambda: self.ausnahme[0], pause_s=1.0)
        self.aufz = X11Aufzeichnung(self.ueb.ereignis_x11)
        self.assertTrue(self.aufz.start(), self.aufz.fehler)
        self.addCleanup(self.aufz.stop)
        self.daniel = display.Display()
        self.addCleanup(self.daniel.close)

    def daniel_bewegt(self, n=12, ort=(700, 500)):
        from Xlib import X
        from Xlib.ext import xtest

        for i in range(n):
            xtest.fake_input(self.daniel, X.MotionNotify, 0, 0, self.daniel.screen().root, ort[0] + i * 5, ort[1])
            self.daniel.sync()
            time.sleep(0.01)

    def langes_ziehen(self, dauer=3000):
        r = self.a.stand()["rects"]["flaeche"]
        w = self.a.rect()
        ergebnis = {}
        aktion = Aktion("ziehen", punkt=(r[0] + 20 - w[0], r[1] + 20 - w[1]), bis=(r[0] + 380 - w[0], r[1] + 100 - w[1]), dauer_ms=dauer)
        faden = threading.Thread(target=lambda: ergebnis.update(r=self.tu(aktion)))
        faden.start()
        self.a.warte(lambda s: s["gedrueckt"], 5)
        return faden, ergebnis

    def test_ruhe_fuer_die_raute_nur_taste_und_klick_zaehlen_nicht_der_zeiger(self):
        """Echtes XRecord: Zeigerbewegung allein (Selkies-Rauschen) ändert die Ruhe nicht; eine Taste oder ein Klick von Daniel schon."""
        from Xlib import X
        from Xlib.ext import xtest

        time.sleep(0.5)
        self.daniel_bewegt(20)
        time.sleep(0.4)
        self.assertEqual(self.ueb.ruhig_seit(), float("inf"), "Zeigerrauschen allein ist kein Tippen oder Klicken")
        taste = self.daniel.keysym_to_keycode(0x61)  # a
        xtest.fake_input(self.daniel, X.KeyPress, taste)
        xtest.fake_input(self.daniel, X.KeyRelease, taste)
        self.daniel.sync()
        time.sleep(0.4)
        self.assertLess(self.ueb.ruhig_seit(), 2.0, "eine Taste von Daniel setzt die Ruhe zurück")
        self.ueb.letzte_eingabe = None
        xtest.fake_input(self.daniel, X.ButtonPress, 1)
        xtest.fake_input(self.daniel, X.ButtonRelease, 1)
        self.daniel.sync()
        time.sleep(0.4)
        self.assertLess(self.ueb.ruhig_seit(), 2.0, "ein Klick von Daniel setzt die Ruhe zurück")

    def test_eigene_eingabe_loest_nie_die_uebernahme_aus(self):
        faden, ergebnis = self.langes_ziehen(1500)
        faden.join(10)
        self.assertEqual(ergebnis["r"].status, "ausgefuehrt", (ergebnis["r"].grund, ergebnis["r"].observed))
        for aktion, bezug in ((Aktion("klick", punkt=self.a.widget_mitte("knopf")), True), (Aktion("rad", punkt=self.a.widget_mitte("flaeche"), dy=3), True), (Aktion("tippen", text="abc"), False)):
            r = self.tu(aktion) if bezug else self.tu(aktion, bezug=None)
            self.assertEqual(r.status, "ausgefuehrt", (aktion.art, r.grund, r.observed))
        time.sleep(0.5)
        self.assertEqual(self.ueb.erkannt, 0, "kein einziger falscher Alarm")

    def test_daniel_bewegt_die_maus_mitten_im_ziehen_die_haende_stoppen_und_lassen_los(self):
        faden, ergebnis = self.langes_ziehen()
        self.daniel_bewegt()
        faden.join(5)
        r = ergebnis["r"]
        self.assertEqual((r.status, r.grund), ("abgebrochen", "daniel_uebernimmt"))
        self.assertFalse(self.a.warte(lambda s: not s["gedrueckt"])["gedrueckt"])
        self.assertEqual(self.x.anzeige().screen().root.query_pointer().mask & 0x100, 0)
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf"))).grund, "daniel_uebernimmt", "während der Pause geht nichts")
        time.sleep(1.2)
        self.ueb.tick()
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf"))).status, "ausgefuehrt", "nach der Pause wieder")

    def test_daniel_im_ruhezustand_sperrt_die_haende_fuer_die_pause(self):
        time.sleep(0.3)
        self.daniel_bewegt(8)
        time.sleep(0.2)
        r = self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf")))
        self.assertEqual((r.status, r.grund, r.delivered), ("abgelehnt", "daniel_uebernimmt", 0))
        self.assertEqual(self.a.stand()["klicks"], 0)

    def test_daniels_ausnahme_laesst_die_haende_weiterarbeiten_aber_der_not_aus_bleibt(self):
        self.ausnahme[0] = True
        faden, ergebnis = self.langes_ziehen(1500)
        self.daniel_bewegt()
        faden.join(10)
        self.assertEqual(ergebnis["r"].status, "ausgefuehrt", "mit der Ausnahme läuft das Ziehen trotz Daniels Eingabe zu Ende")
        self.assertGreater(self.ueb.ignoriert, 0)
        self.assertEqual(self.ueb.erkannt, 0)
        self.ausnahme[0] = False
        faden, ergebnis = self.langes_ziehen(3000)
        self.ausnahme[0] = True  # Ausnahme gilt, und trotzdem stoppt F12
        from augen_haende_bridge.koerper import linux_adapter as la
        from augen_haende_bridge.koerper.linux_adapter import LinuxNotAusHook

        hook = LinuxNotAusHook(self.na)
        self.assertTrue(hook.start())
        self.addCleanup(hook.stop)
        la.xtest_senden([(0x7B, 0, 0), (0x7B, 0, 0x0002)])
        faden.join(5)
        self.assertEqual((ergebnis["r"].status, ergebnis["r"].grund), ("abgebrochen", "not_aus"))

    def test_der_not_aus_stoppt_auch_waehrend_daniel_uebernommen_hat(self):
        self.daniel_bewegt(8)
        time.sleep(0.2)
        self.na.ausloesen("F12")
        self.assertEqual(self.tu(Aktion("klick", punkt=self.a.widget_mitte("knopf"))).grund, "not_aus", "der Not-Aus steht vor der Übernahme")


for _name in [n for n in dir(X11HaendeTests) if n.startswith("test_") and n not in X11StopTests.__dict__]:
    setattr(X11UebernahmeTests, _name, None) if _name not in X11UebernahmeTests.__dict__ else None
    setattr(X11StopTests, _name, None)  # die Stop-Klasse erbt nur die Hilfen, nicht die Tests der Hände-Klasse (sie liefen sonst doppelt)


if __name__ == "__main__":
    unittest.main()
