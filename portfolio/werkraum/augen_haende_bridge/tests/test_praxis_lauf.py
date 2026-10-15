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

        self.assertEqual([s["name"] for s in szenarien()], ["gemgem-allein", "menschlich", "nutzerin-anwendungsfaelle"])
        self.assertEqual(szenarien()[0]["schritte"], 23)
        self.assertTrue(szenario_pfad("menschlich").is_file())
        for schlecht in ("../x", "a/b", "", "GROSS", "x" * 41, "-x", 5, None):
            with self.assertRaises(PraxisFehler, msg=str(schlecht)):
                szenario_pfad(schlecht)
        with self.assertRaises(PraxisFehler) as c:
            szenario_pfad("gibtsnicht")
        self.assertEqual(str(c.exception), "szenario_unbekannt")

    def test_das_solo_szenario_hat_dieselben_schritte_wie_das_wechselnde_und_nur_andere_rollen(self):
        from augen_haende_bridge.praxis.lauf import lade_szenario, szenario_pfad

        a, b = lade_szenario(szenario_pfad("menschlich")), lade_szenario(szenario_pfad("gemgem-allein"))
        self.assertEqual(a["schritte"], b["schritte"], "keine stille Abweichung der Schritte")
        self.assertEqual((a.get("rollen", "wechselnd"), b["rollen"]), ("wechselnd", "a"))
        w = Welt()
        l = w.lauf(b, menue_freigabe=True)
        self.assertEqual({l.handelnder(n) for n in range(1, 24)}, {A}, "A handelt alle 23 Schritte, B schaut zu")

    def test_das_nutzerin_szenario_besteht_aus_anwendungsfaellen_ohne_entwicklerwerkzeuge(self):
        from augen_haende_bridge.praxis.lauf import lade_szenario, szenario_pfad

        s = lade_szenario(szenario_pfad("nutzerin-anwendungsfaelle"))
        self.assertEqual((s["rollen"], s["contract_version"], len(s["schritte"])), ("a", 2, 14))
        faelle = []
        for st in s["schritte"]:
            if st["teil"] not in faelle:
                faelle.append(st["teil"])
        self.assertEqual(faelle, ["1 Notiz schreiben und speichern", "2 Im Browser nachschlagen", "3 Datei finden und öffnen", "4 Mit der Bridge zusammenarbeiten", "5 Etwas zeigen"])
        for st in s["schritte"]:
            self.assertTrue(st["belege"], f"Schritt {st['nr']} braucht mindestens einen Beleg")
            for beleg in st["belege"]:
                self.assertNotIn(beleg["match"].get("command"), ("kapsel", "seed", "lease"), "kein Entwicklerwerkzeug im Nutzer-Szenario")
        self.assertEqual([st["nr"] for st in s["schritte"] if st.get("braucht")], [13], "nur der Menüschritt wartet auf Daniels Freigabe")
        w = Welt()
        l = w.lauf(s)
        self.assertEqual({l.handelnder(n) for n in range(1, 15)}, {A})

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

    def test_nur_die_ansage_geht_in_die_raute_kein_fazit_hinterher(self):
        w = Welt()
        l = w.lauf(klein())
        schritt_durch(w, l, 1, A, B)
        self.assertEqual([t for t, _ in w.raute], [A])  # vorher sagen, was auffällt, nie hinterher ein Fazit
        self.assertTrue(w.raute[0][1].startswith("Schritt 1 · Prüfe:"))
        self.assertEqual(w.zeilen[0]["status"], "ok")  # das Urteil steht trotzdem im Ledger

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
        self.assertEqual(l.status()["harness"], "completed")

    def test_status_zaehlt_fertige_und_zurueckgestellte(self):
        s = klein(3)
        s["schritte"][1]["braucht"] = "menue_freigabe"
        w = Welt()
        l = w.lauf(s)
        schritt_durch(w, l, 1, A, B)
        st = l.status()
        self.assertEqual((st["fertig"], st["zurueckgestellt"], st["schritt"], st["von"]), ([1], [2], 3, 3))


class WartezustandTests(unittest.TestCase):
    def test_jeder_agent_erfaehrt_worauf_er_wartet_und_wer_auf_ihn_wartet(self):
        w = Welt()
        l = w.lauf()
        dran, wartend = l.karte(A)["wartezustand"], l.karte(B)["wartezustand"]
        self.assertFalse(dran["wartet"])
        self.assertEqual(dran["auf_dich"], ["Gemgem"])
        self.assertTrue(wartend["wartet"])
        self.assertEqual((wartend["wer"], wartend["worauf"]), ("Claude", "die Ansage des Schritts in der Raute"))
        w.t += 42
        self.assertEqual(l.karte(B)["wartezustand"]["seit_s"], 42)


class HaltTests(unittest.TestCase):
    """Dritter echter Fehlversuch an einem Schritt: Halt, kein Überspringen, erst die benannte Ursache löst ihn."""

    def lauf(self, **kw):
        w = Welt()
        l = w.lauf(klein(3), **kw)
        return w, l

    def zu_getan(self, w, l):
        self.assertTrue(l.ansage(A, ansage(1))["ok"])
        w.t += 5

    def test_drei_fehlversuche_halten_an_und_stehen_im_ledger(self):
        w, l = self.lauf()
        self.zu_getan(w, l)
        for n in (1, 2):  # ohne Hände-Spur: spur_fehlt
            r = l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt")
            self.assertEqual((r["reason"], r["fehlversuche"]), ("spur_fehlt", n))
        r = l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt")
        self.assertEqual((r["reason"], r["fehlversuche"]), ("halt", 3))
        self.assertIsNotNone(l.halt)
        self.assertEqual([z["status"] for z in w.zeilen if z["status"] in ("fehlversuch", "halt")], ["fehlversuch", "fehlversuch", "fehlversuch", "halt"])
        k = l.karte(A)
        self.assertEqual(k["fehlversuche"]["halt"]["nr"], 1)
        self.assertIn("Halt an Schritt 1", k["tu_jetzt"])

    def test_im_halt_gibt_es_kein_ueberspringen_und_keinen_weiterweg(self):
        w, l = self.lauf()
        self.zu_getan(w, l)
        for _ in range(3):
            l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt")
        w.spur(A, "haende")  # auch mit jetzt vorhandener Spur geht es nicht weiter
        for aufruf in (lambda: l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt"), lambda: l.nicht_getestet(A, "ich überspringe das einfach mal"),
                       lambda: l.nochmal(A), lambda: l.ansage(A, ansage(1)), lambda: l.planaenderung(A, "ein anderer Plan für den Schritt"),
                       lambda: l.gesehen(A, "Der Zähler zeigt eins", "ok"), lambda: l.zuschauer(B, "Auf meinem Bild steht eins", "bestaetigt")):
            self.assertEqual(aufruf()["reason"], "halt")
        self.assertNotIn("zurueckgestellt", [z["status"] for z in w.zeilen])
        self.assertEqual(l.nr, 1)

    def test_ursache_loest_den_halt_am_selben_schritt_und_der_zaehler_beginnt_neu(self):
        w, l = self.lauf()
        self.zu_getan(w, l)
        for _ in range(3):
            l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt")
        self.assertEqual(l.ursache(A, "zu kurz")["reason"], "ursache_zu_kurz")
        self.assertIsNotNone(l.halt)
        self.assertTrue(l.ursache(B, "Der Körper war nicht an das Testfenster gebunden; jetzt gebunden und neu gemessen")["ok"])
        self.assertIsNone(l.halt)
        self.assertEqual(l.nr, 1)
        self.assertEqual(l.karte(A)["fehlversuche"]["n"], 0)
        w.spur(A, "haende")
        self.assertTrue(l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt")["ok"])
        self.assertIn("ursache", [z["status"] for z in w.zeilen])
        self.assertEqual(l.ursache(A, "noch eine Ursache ohne Halt, lang genug")["reason"], "kein_halt")

    def test_ueberspringen_gibt_es_auch_ohne_halt_nicht(self):
        w, l = self.lauf()
        self.zu_getan(w, l)
        r = l.nicht_getestet(A, "dieser Schritt klappt gerade nicht, ich lasse ihn aus")
        self.assertEqual(r["reason"], "kein_ueberspringen")
        self.assertIn("test nochmal", r["sage"])
        self.assertNotIn("zurueckgestellt", [z["status"] for z in w.zeilen])

    def test_zurueckstellen_nur_fuer_schritte_die_auf_die_menue_freigabe_warten(self):
        s = klein(3)
        s["schritte"][0]["braucht"] = "menue_freigabe"
        w = Welt()
        l = w.lauf(s)  # ohne Freigabe stellt der Lauf Schritt 1 von selbst zurück und steht bei Schritt 2
        self.assertEqual(l.nr, 2)
        self.assertEqual([z["status"] for z in w.zeilen], ["zurueckgestellt"])
        w2 = Welt()
        l2 = w2.lauf(s, menue_freigabe=True)
        self.assertEqual(l2.nr, 1, "mit Daniels Freigabe wird der Schritt gemacht, nicht zurückgestellt")

    def test_tippfehler_im_befehl_zaehlen_nicht_als_fehlversuch(self):
        w, l = self.lauf()
        self.zu_getan(w, l)
        for _ in range(5):
            self.assertEqual(l.getan(A, "kurz")["reason"], "text_zu_kurz")
        self.assertIsNone(l.halt)

    def test_nicht_dran_oder_falscher_knoten_zaehlt_nicht(self):
        w, l = self.lauf()
        for _ in range(5):
            self.assertEqual(l.getan(B, "Zeiger auf die Schaltfläche, einmal geklickt")["reason"], "jetzt_ansage")
        self.assertIsNone(l.halt)

    def test_die_raute_ohne_quittung_zaehlt_als_fehlversuch(self):
        w, l = self.lauf(raute=lambda tid, text: False) if False else (None, None)
        w = Welt()
        l = PraxisLauf(klein(3), A, B, namen={A: "Claude", B: "Gemgem"}, evidenz=w.evidenz, raute=lambda tid, text: False, ledger=w.zeilen.append,
                       jetzt=w.jetzt, jetzt_ms=w.jetzt_ms)
        for n in (1, 2):
            self.assertEqual(l.ansage(A, ansage(1))["fehlversuche"], n)
        self.assertEqual(l.ansage(A, ansage(1))["reason"], "halt")


class HilfeTests(unittest.TestCase):
    """Jedes Hindernis nennt die nächste Handlung; ein Zielwechsel nach der Ansage ist kein Fehlversuch; Stillstand und Erinnerung stehen in der Karte."""

    def test_fehlversuch_der_raute_nennt_klasse_und_den_grund_der_koerperquittung(self):
        w = Welt()
        l = PraxisLauf(klein(3), A, B, namen={A: "Claude", B: "Gemgem"}, evidenz=w.evidenz,
                       raute=lambda tid, text: {"ok": False, "grund": "feld_nicht_geoeffnet"}, ledger=w.zeilen.append, jetzt=w.jetzt, jetzt_ms=w.jetzt_ms)
        r = l.ansage(A, ansage(1))
        self.assertEqual((r["reason"], r["klasse"], r["next"]["grund"]), ("raute_nicht_erreichbar", "ausfuehrung", "feld_nicht_geoeffnet"))
        self.assertIn("außerhalb des Bildschirms", r["next"]["satz"])
        self.assertIn("zurückholen", r["next"]["satz"])

    def test_spur_fehlt_nennt_was_im_protokoll_fehlt(self):
        w = Welt()
        l = w.lauf(klein(3))
        l.ansage(A, ansage(1))
        w.t += 5
        r = l.getan(A, "Zeiger auf die Schaltfläche, einmal geklickt")
        self.assertEqual((r["reason"], r["klasse"]), ("spur_fehlt", "ausfuehrung"))
        self.assertIn("haende", r["next"]["satz"])

    def test_schrittbeleg_fehlt_nennt_den_fehlenden_beleg_wortlich(self):
        from augen_haende_bridge.praxis import hilfe

        st = {"belege": [{"id": "s10-1", "role": "handelnder", "match": {"command": "haende", "action_kind": "klick", "ok": True}},
                         {"id": "s10-2", "role": "handelnder", "match": {"command": "haende", "ok": False, "reason": "not_aus"}}]}
        r = hilfe.naechste_handlung({"reason": "schrittbeleg_fehlt", "belege": {"missing": ["s10-2"]}}, st)
        self.assertEqual(r["klasse"], "planung")
        self.assertIn("s10-2 (Handelnder): haende not_aus abgelehnt", r["next"]["satz"])
        self.assertNotIn("s10-1", r["next"]["satz"])
        r2 = hilfe.naechste_handlung({"reason": "schrittbeleg_fehlt", "belege": {"missing": ["s10-2"]}}, st, {"handelnder": "Opencode", "zuschauer": "Claude-Host"})
        self.assertIn("s10-2 (Opencode): haende", r2["next"]["satz"])

    def test_zielwechsel_nach_der_ansage_ist_kein_fehlversuch(self):
        w = Welt()
        w.t = 1.0
        l = w.lauf(klein(3))
        self.assertIsNone(l.ziel_gewechselt({A: "x:1", B: "x:1"}), "ohne Ansage gibt es nichts festzuhalten")
        l.z["targets"] = {A: "x:1", B: "x:1"}
        self.assertTrue(l.ansage(A, ansage(1))["ok"])
        self.assertIsNone(l.ziel_gewechselt({A: "x:1", B: "x:1"}))
        r = l.ziel_gewechselt({A: "x:2", B: "x:1"})
        self.assertEqual((r["ok"], r["reason"], r["klasse"]), (False, "ziel_gewechselt", "wahrnehmung"))
        self.assertEqual(r["ziele"], {"Claude": {"bei_ansage": "x:1", "jetzt": "x:2"}})
        self.assertIn("test nochmal", r["next"]["befehl"])
        self.assertEqual(l.fehlversuche.get(1, 0), 0)
        self.assertNotIn("fehlversuch", [z["status"] for z in w.zeilen])
        self.assertEqual(l.nochmal(A)["ok"], True)
        self.assertIsNone(l.ziel_gewechselt({A: "x:2", B: "x:1"}), "nach `nochmal` ist das Festgehaltene gelöscht")

    def test_ungebunden_bei_der_ansage_wird_als_wechsel_erkannt(self):
        w = Welt()
        w.t = 1.0
        l = w.lauf(klein(3))
        l.z["targets"] = {A: None, B: "x:1"}
        l.ansage(A, ansage(1))
        r = l.ziel_gewechselt({A: "x:5", B: "x:1"})
        self.assertIn("ungebunden → x:5", r["next"]["satz"])

    def test_schritt_der_das_ziel_selbst_aendert_ist_ausgenommen(self):
        w = Welt()
        s = klein(2)
        s["schritte"][0]["aendert_ziel"] = True
        w.t = 1.0
        l = w.lauf(s)
        l.z["targets"] = {A: "x:1", B: "x:1"}
        l.ansage(A, ansage(1))
        self.assertIsNone(l.ziel_gewechselt({A: "x:9", B: "x:1"}))

    def test_karte_vor_der_ansage_sagt_woran_zu_binden_ist(self):
        w = Welt()
        l = w.lauf(klein(3))
        self.assertIn("Binde dich", l.karte(A)["vorher_pruefen"])
        self.assertIn("festgehalten", l.karte(A)["vorher_pruefen"])
        self.assertNotIn("vorher_pruefen", l.karte(B))

    def test_stillstand_erscheint_nach_drei_minuten_in_der_karte(self):
        w = Welt()
        l = w.lauf(klein(3))
        self.assertNotIn("stillstand", l.karte(A))
        w.t += 200
        k = l.karte(A)
        self.assertEqual(k["stillstand"]["knoten"], "ansage")
        self.assertGreaterEqual(k["stillstand"]["seit_s"], 200)
        self.assertIn("bridge_cli.py lage", k["stillstand"]["satz"])

    def test_erinnerung_steht_nur_beim_passenden_schritt_in_der_karte(self):
        w = Welt()
        l = w.lauf(klein(3))
        l.erinnerung = {"nr": 1, "grund": "spur_fehlt", "faelle": [{"wann": "2026-10-03 18:00:00", "woher": "protokoll/raute", "text": "Ziel wechselte"}], "hinweis": "x"}
        self.assertEqual(l.karte(A)["erinnerung"]["faelle"][0]["text"], "Ziel wechselte")
        l.erinnerung["nr"] = 2
        self.assertNotIn("erinnerung", l.karte(A))


class ErinnerungTests(unittest.TestCase):
    AUSGABE = ("#121598 2026-10-03 17:57:47 protokoll/raute t-19961e705d   (0.28)\n    say: Schritt 9 (Chat): Ziel ist die Raute\n"
               "#63 2026-10-02 17:05:46 protokoll/nachricht t-87ddadff30   (0.39)\n    nachricht: Schritt 4 bestaetigt\n"
               "#9 2026-10-02 17:05:46 ledger/fehlversuch t-1 p-1 s9\n")

    def test_ausgabe_der_suche_wird_gelesen_und_kopfzeile_ohne_text_faellt_weg(self):
        from augen_haende_bridge.praxis import erinnerung

        f = erinnerung.lies(self.AUSGABE)
        self.assertEqual([x["id"] for x in f], [121598, 63])
        self.assertEqual((f[0]["wann"], f[0]["woher"], f[0]["abstand"]), ("2026-10-03 17:57:47", "protokoll/raute", 0.28))
        self.assertEqual(f[0]["text"], "say: Schritt 9 (Chat): Ziel ist die Raute")

    def test_suche_ruft_den_speicherprozess_mit_grund_und_titel(self):
        import subprocess
        from augen_haende_bridge.praxis import erinnerung

        gesehen = {}

        def fake(cmd, **kw):
            gesehen["cmd"], gesehen["kw"] = cmd, kw
            return subprocess.CompletedProcess(cmd, 0, stdout=self.AUSGABE, stderr="")

        f = erinnerung.aehnliche("schrittbeleg_fehlt", "Chat bedienen", klasse="planung", n=2, ausfuehren=fake, python=Path("/bin/true"))
        self.assertEqual(len(f), 2)
        self.assertEqual(gesehen["cmd"][1:4], ["-m", "augen_haende_bridge.speicher", "suche"])
        self.assertIn("schrittbeleg_fehlt Chat bedienen planung", gesehen["cmd"][4])
        self.assertEqual(gesehen["cmd"][-2:], ["-n", "2"])
        self.assertEqual(gesehen["kw"]["timeout"], 25.0)

    def test_fehler_zeitueberschreitung_und_fehlende_umgebung_geben_leer_zurueck(self):
        import subprocess
        from augen_haende_bridge.praxis import erinnerung

        def zeit(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd, 1)

        def schlecht(cmd, **kw):
            return subprocess.CompletedProcess(cmd, 2, stdout=self.AUSGABE, stderr="boom")

        self.assertEqual(erinnerung.aehnliche("x", "y", ausfuehren=zeit, python=Path("/bin/true")), [])
        self.assertEqual(erinnerung.aehnliche("x", "y", ausfuehren=schlecht, python=Path("/bin/true")), [])
        self.assertEqual(erinnerung.aehnliche("x", "y", python=Path("/nirgends/python")), [])


if __name__ == "__main__":
    unittest.main()
