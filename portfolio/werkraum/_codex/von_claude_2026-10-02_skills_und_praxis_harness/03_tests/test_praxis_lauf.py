"""Praxistest-Graph: Reihenfolge, Rollen, echte Spuren statt Behauptungen, Lesezeit, Planänderung, Widerspruch, Zurückstellen, Wiederholung, Kür — und ein freundlicher Ton."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge.praxis.lauf import MAX_KLAERRUNDEN, PraxisFehler, PraxisLauf, baue_graph, lade_szenario

A, B = "t-a", "t-b"


class Welt:
    """Eine steuerbare Uhr und ein Protokoll, in das der Test echte Spuren legt."""

    def __init__(self):
        self.t = 0.0
        self.spuren: list[tuple[str, str, int]] = []
        self.raute: list[tuple[str, str]] = []
        self.zeilen: list[dict] = []

    def jetzt(self):
        return self.t

    def jetzt_ms(self):
        return int(self.t * 1000)

    def spur(self, tid, art):
        self.t += 0.01
        self.spuren.append((tid, art, self.jetzt_ms()))

    def evidenz(self, tid, art, seit_ms):
        return sum(1 for t, a, ms in self.spuren if t == tid and a == art and ms >= seit_ms)

    def lauf(self, szenario=None, **kw):
        return PraxisLauf(szenario or lade_szenario(), A, B, namen={A: "Claude", B: "Gemgem"}, evidenz=self.evidenz, raute=lambda tid, text: self.raute.append((tid, text)) or True, ledger=self.zeilen.append,
                          jetzt=self.jetzt, jetzt_ms=self.jetzt_ms, **kw)


def ansage(nr, titel="x"):
    return f"Schritt {nr} · Prüfe: {titel} · Mache: klicken · Erwarte: Zähler steigt"


def klein(n=3):
    return {"id": "klein", "schritte": [{"nr": i, "teil": "T", "ziel": "Z", "titel": f"Titel {i}", "pruefe": "p", "mache": "m", "erwarte": "e", "evidenz": ["haende"]} for i in range(1, n + 1)]}


def schritt_durch(w, l, nr, handelnder, zuschauer, urteil="ok", z_urteil="bestaetigt"):
    assert l.ansage(handelnder, ansage(nr))["ok"]
    w.t += 5
    w.spur(handelnder, "haende")
    assert l.getan(handelnder, "Zeiger auf die Schaltfläche, einmal geklickt")["ok"]
    w.spur(handelnder, "sehen")
    assert l.gesehen(handelnder, "Der Zähler zeigt jetzt eins", urteil)["ok"]
    w.spur(zuschauer, "sehen")
    return l.zuschauer(zuschauer, "Auf meinem Bild steht der Zähler auf eins", z_urteil)


class GraphTests(unittest.TestCase):
    def test_szenario_und_graph_sind_gueltig_und_vollstaendig_verkabelt(self):
        s = lade_szenario()
        g = baue_graph(s)
        self.assertEqual(len(s["schritte"]), 23)
        self.assertEqual(len(g.nodes), 23 * 7 + 1)
        for nr in (1, 12, 23):
            for art in ("ansage", "lesen", "handeln", "sehen", "urteil", "zuschauer", "klaeren"):
                self.assertIn(f"s{nr}.{art}", g.nodes)
        self.assertEqual([e.target for e in g.next_edges("s1.zuschauer", "bestaetigt")], ["s2.ansage"])
        self.assertEqual([e.target for e in g.next_edges("s1.zuschauer", "widerspruch")][0], "s1.klaeren")
        self.assertEqual([e.target for e in g.next_edges("s23.zuschauer", "bestaetigt")], ["ende"])

    def test_ungueltige_szenarien(self):
        d = Path(tempfile.mkdtemp())
        for name, inhalt in (("a", "kein json"), ("b", json.dumps({"schritte": []})), ("c", json.dumps({"schritte": [{"nr": 2, "teil": "T", "ziel": "Z", "titel": "t", "pruefe": "p", "mache": "m", "erwarte": "e"}]})),
                             ("d", json.dumps({"schritte": [{**klein(1)["schritte"][0], "evidenz": ["zaubern"]}]}))):
            (d / name).write_text(inhalt)
            with self.assertRaises(PraxisFehler, msg=name):
                lade_szenario(d / name)
        with self.assertRaises(PraxisFehler):
            PraxisLauf(klein(), A, A)


class SzenarienTests(unittest.TestCase):
    def test_szenarien_werden_nach_namen_gefunden_und_nur_schlichte_namen_sind_erlaubt(self):
        from augen_haende_bridge.praxis.lauf import szenario_pfad, szenarien

        self.assertEqual([s["name"] for s in szenarien()], ["menschlich"])
        self.assertEqual(szenarien()[0]["schritte"], 23)
        self.assertTrue(szenario_pfad("menschlich").is_file())
        for schlecht in ("../x", "a/b", "", "GROSS", "x" * 41, "-x", 5, None):
            with self.assertRaises(PraxisFehler, msg=str(schlecht)):
                szenario_pfad(schlecht)
        with self.assertRaises(PraxisFehler) as c:
            szenario_pfad("gibtsnicht")
        self.assertEqual(str(c.exception), "szenario_unbekannt")

    def test_rollenmodus_a_laesst_immer_denselben_handeln(self):
        s = {**klein(3), "rollen": "a"}
        w = Welt()
        l = w.lauf(s)
        self.assertEqual([l.handelnder(n) for n in (1, 2, 3)], [A, A, A])
        schritt_durch(w, l, 1, A, B)
        self.assertEqual((l.nr, l.handelnder()), (2, A))
        with self.assertRaises(PraxisFehler):
            lade_szenario_aus({**klein(1), "rollen": "wild"})


def lade_szenario_aus(d):
    p = Path(tempfile.mkdtemp()) / "s.json"
    p.write_text(json.dumps(d))
    return lade_szenario(p)


class ReihenfolgeTests(unittest.TestCase):
    def test_der_volle_weg_eines_schritts_und_die_rollen_wechseln(self):
        w = Welt()
        l = w.lauf(klein())
        self.assertEqual((l.art, l.handelnder(), l.zuschauer_von()), ("ansage", A, B))
        r = schritt_durch(w, l, 1, A, B)
        self.assertTrue(r["ok"], r)
        self.assertIn("Weiter mit Schritt 2", r["sage"])
        self.assertEqual((l.nr, l.art, l.handelnder()), (2, "ansage", B), "ungerade Schritte handelt A, gerade B")
        r = schritt_durch(w, l, 2, B, A)
        r = schritt_durch(w, l, 3, A, B)
        self.assertTrue(r.get("ende"), r)
        self.assertEqual(l.knoten, "ende")
        self.assertEqual([z["status"] for z in w.zeilen], ["ok", "ok", "ok"])
        self.assertEqual(w.zeilen[0]["handelnder"], "Claude")
        self.assertEqual(w.zeilen[1]["handelnder"], "Gemgem")

    def test_die_ansage_geht_in_die_raute_des_handelnden_und_danach_gesehen_und_bestaetigung_in_die_eigene(self):
        w = Welt()
        l = w.lauf(klein())
        schritt_durch(w, l, 1, A, B)
        self.assertEqual([t for t, _ in w.raute], [A, A, B])
        self.assertTrue(w.raute[0][1].startswith("Schritt 1 · Prüfe:"))
        self.assertIn("Gesehen:", w.raute[1][1])
        self.assertIn("Bestätigt:", w.raute[2][1])

    def test_die_reihenfolge_laesst_sich_nicht_ueberspringen_und_der_ton_bleibt_freundlich(self):
        w = Welt()
        l = w.lauf(klein())
        for r in (l.getan(A, "Zeiger geklickt, Zähler eins"), l.gesehen(A, "Zähler eins gesehen", "ok"), l.zuschauer(B, "bestätigt, Zähler eins", "bestaetigt")):
            self.assertEqual((r["ok"], r["reason"]), (False, "jetzt_ansage"))
            self.assertTrue(r["sage"].startswith("Fast"), r["sage"])
            self.assertIn("test karte", r["sage"])
        self.assertEqual(l.art, "ansage", "kein Sprung, kein Absturz")

    def test_nur_der_dran_ist_darf_und_der_andere_wird_freundlich_gebremst(self):
        w = Welt()
        l = w.lauf(klein())
        r = l.ansage(B, ansage(1))
        self.assertEqual((r["ok"], r["reason"]), (False, "nicht_dein_zug"))
        self.assertIn("Gerade ist Claude dran", r["sage"])
        l.ansage(A, ansage(1))
        w.t += 5
        w.spur(A, "haende")
        l.getan(A, "Zeiger geklickt, Zähler eins")
        w.spur(A, "sehen")
        l.gesehen(A, "Zähler zeigt eins", "ok")
        self.assertEqual(l.zuschauer(A, "ich bestätige mich selbst", "bestaetigt")["reason"], "nicht_dein_zug", "man bestätigt sich nicht selbst")


class AnsageTests(unittest.TestCase):
    def test_eine_unvollstaendige_ansage_bekommt_die_vorlage_statt_einer_ablehnung(self):
        w = Welt()
        l = w.lauf(klein())
        r = l.ansage(A, "Ich klicke mal")
        self.assertEqual((r["ok"], r["reason"]), (False, "ansage_unvollstaendig"))
        self.assertIn("Fast!", r["sage"])
        self.assertIn("Vorlage: Schritt 1 · Prüfe: p · Mache: m · Erwarte: e", r["sage"])
        self.assertEqual(w.raute, [], "nichts wurde in die Raute geschrieben")
        self.assertFalse(l.ansage(A, "x" * 400)["ok"])
        self.assertFalse(l.ansage(A, ansage(2))["ok"], "die Nummer muss zum Schritt passen")
        self.assertTrue(l.ansage(A, "schritt 1 · pruefe: a · mache: b · erwarte: c")["ok"], "ohne Umlaute und in Kleinbuchstaben geht es auch")

    def test_ohne_erreichbare_raute_wird_nichts_angenommen(self):
        w = Welt()
        l = PraxisLauf(klein(), A, B, evidenz=w.evidenz, raute=lambda tid, text: False, jetzt=w.jetzt, jetzt_ms=w.jetzt_ms)
        r = l.ansage(A, ansage(1))
        self.assertEqual((r["ok"], r["reason"]), (False, "raute_nicht_erreichbar"))
        self.assertEqual(l.art, "ansage")


class LesezeitTests(unittest.TestCase):
    def test_vor_ablauf_der_lesezeit_geht_nichts_und_danach_von_selbst(self):
        w = Welt()
        l = w.lauf(klein())
        r = l.ansage(A, ansage(1))
        self.assertGreaterEqual(r["lesezeit_s"], 4.0)
        w.t += 1
        w.spur(A, "haende")
        g = l.getan(A, "Zeiger geklickt, Zähler eins")
        self.assertEqual((g["ok"], g["reason"]), (False, "jetzt_lesen"))
        self.assertIn("Sekunden Lesezeit", g["sage"])
        self.assertIn("Noch", l.karte(A)["tu_jetzt"])
        w.t += 10
        self.assertEqual(l.karte(A)["knoten"], "handeln")

    def test_laengere_ansagen_bekommen_mehr_lesezeit(self):
        w = Welt()
        l = w.lauf(klein())
        kurz = l.ansage(A, "Schritt 1 · Prüfe: a · Mache: b · Erwarte: c")["lesezeit_s"]
        l2 = w.lauf(klein())
        lang = l2.ansage(A, "Schritt 1 · Prüfe: " + "sehr ausführlich " * 8 + "· Mache: b · Erwarte: c")["lesezeit_s"]
        self.assertGreater(lang, kurz)


class SpurenTests(unittest.TestCase):
    def vorbereiten(self):
        w = Welt()
        l = w.lauf(klein())
        l.ansage(A, ansage(1))
        w.t += 5
        return w, l

    def test_ohne_echte_haendespur_gibt_es_kein_getan_aber_eine_klare_hilfe(self):
        w, l = self.vorbereiten()
        r = l.getan(A, "Ich habe geklickt, wirklich")
        self.assertEqual((r["ok"], r["reason"], r["fehlt"]), (False, "spur_fehlt", ["haende"]))
        self.assertIn("kann Daniel dir noch nicht zuschauen", r["sage"])
        self.assertIn("Führe den Schritt jetzt aus: m", r["sage"], "die Hilfe nennt, was zu tun ist")
        self.assertEqual(l.art, "handeln")

    def test_eine_spur_von_vor_der_ansage_oder_vom_anderen_agenten_zaehlt_nicht(self):
        w = Welt()
        w.spur(A, "haende")  # davor
        l = w.lauf(klein())
        w.t += 1
        l.ansage(A, ansage(1))
        w.t += 5
        w.spur(B, "haende")  # vom anderen
        self.assertEqual(l.getan(A, "Ich habe geklickt, wirklich")["reason"], "spur_fehlt")
        w.spur(A, "haende")
        self.assertTrue(l.getan(A, "Ich habe geklickt, wirklich")["ok"])

    def test_ohne_neues_bild_kein_gesehen_und_ohne_eigenen_blick_keine_bestaetigung(self):
        w, l = self.vorbereiten()
        w.spur(A, "haende")
        l.getan(A, "Zeiger geklickt, Zähler eins")
        self.assertEqual(l.gesehen(A, "Zähler zeigt eins", "ok")["reason"], "spur_fehlt")
        w.spur(A, "sehen")
        self.assertTrue(l.gesehen(A, "Zähler zeigt eins", "ok")["ok"])
        r = l.zuschauer(B, "Ich bestätige das einfach mal", "bestaetigt")
        self.assertEqual((r["ok"], r["reason"]), (False, "spur_fehlt"))
        self.assertIn("eigenes Bild", r["sage"])
        w.spur(B, "sehen")
        self.assertTrue(l.zuschauer(B, "Auf meinem Bild steht eins", "bestaetigt")["ok"])

    def test_abgelehnte_versuche_sind_eine_eigene_spur_fuer_negativtests(self):
        w = Welt()
        s = klein(1)
        s["schritte"][0]["evidenz"] = ["haende_abgelehnt"]
        l = w.lauf(s)
        l.ansage(A, ansage(1))
        w.t += 5
        w.spur(A, "haende")
        self.assertEqual(l.getan(A, "Klick außerhalb versucht")["reason"], "spur_fehlt")
        w.spur(A, "haende_abgelehnt")
        self.assertTrue(l.getan(A, "Klick außerhalb versucht")["ok"])

    def test_text_und_urteil_werden_geprueft(self):
        w, l = self.vorbereiten()
        w.spur(A, "haende")
        self.assertEqual(l.getan(A, "ja")["reason"], "text_zu_kurz")
        l.getan(A, "Zeiger geklickt, Zähler eins")
        w.spur(A, "sehen")
        self.assertEqual(l.gesehen(A, "Zähler zeigt eins", "super")["reason"], "urteil_ungueltig")
        self.assertEqual(l.gesehen(A, "nö", "ok")["reason"], "text_zu_kurz")


class WeichenTests(unittest.TestCase):
    def test_planaenderung_fuehrt_zurueck_zur_ansage_und_bleibt_im_verlauf(self):
        w = Welt()
        l = w.lauf(klein())
        l.ansage(A, ansage(1))
        w.t += 5
        l.karte(A)
        r = l.planaenderung(A, "Statt Klick nehme ich die Tastatur, weil das Feld den Fokus hat")
        self.assertTrue(r["ok"], r)
        self.assertEqual((l.nr, l.art), (1, "ansage"))
        self.assertIn("neu an", r["sage"])
        self.assertTrue(l.ansage(A, "Planänderung: " + ansage(1))["ok"])
        self.assertEqual(l.z["plaene"], ["Statt Klick nehme ich die Tastatur, weil das Feld den Fokus hat"])
        r = l.planaenderung(B, "Ich ändere den Plan des anderen")
        self.assertEqual((r["ok"], r["reason"]), (False, "jetzt_" + l.art), "nur der Handelnde ändert den Plan")

    def test_widerspruch_fuehrt_ueber_klaeren_zurueck_zum_hinsehen_und_nach_zwei_runden_steht_der_streit_offen_im_protokoll(self):
        w = Welt()
        l = w.lauf(klein(2))
        r = schritt_durch(w, l, 1, A, B, z_urteil="widerspruch")
        self.assertTrue(r["ok"])
        self.assertIn("schaut noch einmal hin", r["sage"])
        self.assertEqual((l.nr, l.art), (1, "sehen"))
        for runde in range(1, MAX_KLAERRUNDEN + 1):
            w.spur(A, "sehen")
            self.assertTrue(l.gesehen(A, f"Beim zweiten Hinsehen: Runde {runde}", "anders")["ok"])
            w.spur(B, "sehen")
            r = l.zuschauer(B, f"Immer noch anders auf meinem Bild {runde}", "widerspruch")
            self.assertTrue(r["ok"])
        self.assertEqual((l.nr, l.art), (2, "ansage"), "nach zwei Klärrunden geht es weiter")
        z = w.zeilen[0]
        self.assertEqual((z["status"], z["klaerrunden"], z["zuschauer_urteil"]), ("offen_streit", 2, "widerspruch"))

    def test_ein_fehler_urteil_des_handelnden_steht_als_fehler_im_protokoll_und_der_lauf_geht_weiter(self):
        w = Welt()
        l = w.lauf(klein(2))
        schritt_durch(w, l, 1, A, B, urteil="fehler")
        self.assertEqual(w.zeilen[0]["status"], "fehler")
        self.assertEqual(l.nr, 2)

    def test_zurueckgestellte_schritte_werden_uebersprungen_solange_etwas_fehlt_und_wieder_aufgenommen_wenn_es_da_ist(self):
        s = klein(3)
        s["schritte"][1]["braucht"] = "menue_freigabe"
        w = Welt()
        l = w.lauf(s)
        schritt_durch(w, l, 1, A, B)
        self.assertEqual(l.nr, 3, "Schritt 2 wartet auf die Menü-Freigabe")
        z = [x for x in w.zeilen if x["status"] == "zurueckgestellt"][0]
        self.assertEqual(z["nr"], 2)
        self.assertIn("Menü-Fenster", z["grund"])
        w2 = Welt()
        l2 = w2.lauf(s, menue_freigabe=True)
        schritt_durch(w2, l2, 1, A, B)
        self.assertEqual(l2.nr, 2)

    def test_nochmal_beginnt_den_schritt_neu_und_laesst_den_ersten_versuch_im_verlauf(self):
        w = Welt()
        l = w.lauf(klein())
        l.ansage(A, ansage(1))
        w.t += 5
        w.spur(A, "haende")
        l.getan(A, "Zeiger geklickt, Zähler eins")
        spuren_vorher = len(l.run.trace)
        r = l.nochmal(A)
        self.assertTrue(r["ok"], r)
        self.assertEqual((l.nr, l.art, l.z["wiederholung"]), (1, "ansage", 1))
        self.assertIn("w1", l.run.id)
        self.assertGreaterEqual(len(l.run.trace), 1)
        self.assertEqual(l.nochmal(B)["reason"], "nicht_dein_zug")
        self.assertTrue(spuren_vorher > 0)

    def test_kuer_und_entdeckung_sind_jederzeit_moeglich_und_nie_pflicht(self):
        w = Welt()
        l = w.lauf(klein())
        r = l.kuer(B, "Mir fällt auf, dass die Raute beim Schreiben kurz flackert")
        self.assertTrue(r["ok"])
        self.assertIn("Gute Beobachtung", r["sage"])
        self.assertEqual(l.kuer(A, "ok")["reason"], "text_zu_kurz")
        self.assertEqual(w.zeilen[-1]["status"], "entdeckung")
        self.assertEqual(l.status()["entdeckungen"], 1)
        schritt_durch(w, l, 1, A, B)
        self.assertEqual(w.zeilen[-1]["notizen"], ["Gemgem: Mir fällt auf, dass die Raute beim Schreiben kurz flackert"])


class KarteTests(unittest.TestCase):
    def test_die_karte_sagt_je_rolle_was_jetzt_zu_tun_ist(self):
        w = Welt()
        l = w.lauf(lade_szenario())
        k = l.karte(A)
        self.assertEqual((k["schritt"], k["von"], k["du"], k["knoten"], k["handelnder"]), (1, 23, "handelnder", "ansage", "Claude"))
        self.assertIn("test ansage", k["tu_jetzt"])
        self.assertTrue(k["ansage_vorlage"].startswith("Schritt 1 · Prüfe:"))
        self.assertLessEqual(len(k["ansage_vorlage"]), 300)
        kb = l.karte(B)
        self.assertEqual(kb["du"], "zuschauer")
        self.assertIn("Schau zu", kb["tu_jetzt"])
        self.assertIn("Daniel das Fenster im Kopf sieht", k["kuer"], "die freiwillige Kür steht auf der Karte")

    def test_das_ende_wird_gewuerdigt(self):
        w = Welt()
        l = w.lauf(klein(1))
        schritt_durch(w, l, 1, A, B)
        k = l.karte(A)
        self.assertTrue(k["ende"])
        self.assertIn("Danke euch beiden", k["sage"])
        self.assertEqual(l.status()["harness"], "running")

    def test_status_zaehlt_fertige_und_zurueckgestellte(self):
        s = klein(3)
        s["schritte"][1]["braucht"] = "menue_freigabe"
        w = Welt()
        l = w.lauf(s)
        schritt_durch(w, l, 1, A, B)
        st = l.status()
        self.assertEqual((st["fertig"], st["zurueckgestellt"], st["schritt"], st["von"]), ([1], [2], 3, 3))


if __name__ == "__main__":
    unittest.main()
