"""G13: Ereignisprotokoll, Momentkapseln (sechs Arten, Quellen und Lücken, Unveränderlichkeit, Ebenen, Tags, Folge-Kapsel, Vergleich, Lernstrecke) und der Scrubber."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge import ereignisprotokoll as ep
from augen_haende_bridge import kapseln as kp
from augen_haende_bridge.scrubber import Zeitlinie


class Uhr:
    def __init__(self, t=1_000_000):
        self.t = t

    def __call__(self):
        self.t += 10
        return self.t


def agent(tid, name, ziel=None, zustand="running", **kw):
    a = {"terminal_id": tid, "name": name, "strom": "codex", "zustand": zustand, "gruppen": [], "eltern_id": None, "kinder": [], "steuerbar": True, "laufort": "vd1",
         "ziel_info": {"target_id": ziel} if ziel else {}}
    a.update(kw)
    return a


class Welt:
    """Eine kleine, gefüllte Starter-Welt als Quelle für Kapseln."""

    def __init__(self, ordner: Path):
        self.uhr = Uhr()
        self.p = ep.Ereignisprotokoll(ordner / "protokoll", self.uhr)
        self.agenten = [agent("t-1", "Codex", "kde1:window:5"), agent("t-2", "Claude", "kde1:window:6"), agent("t-3", "Gemgem", "kde1:window:5", zustand="paused")]
        self.frames_dir = ordner / "frames"
        for t in ("t-1", "t-2"):
            (self.frames_dir / t).mkdir(parents=True)
            for i in range(12):
                (self.frames_dir / t / f"frame-{i}.jpg").write_bytes(b"\xff\xd8\xff\xe0" + bytes([i]) * 20)
        self.p.erfassen("nachricht", "t-1", "Codex → Claude: prüf die Tests", {"an": "t-2"})
        self.p.erfassen("auftrag", "t-2", "Auftrag a-1 angenommen")
        self.p.erfassen("regie", "t-1", "Pause: ablauf_pausiert")
        self.p.erfassen("haende", "t-1", "klick abgelehnt: geometrie_geaendert", {"status": "abgelehnt"})
        self.p.ausgabe("t-1", b"Hallo aus Terminal 1\r\n")
        self.p.ausgabe("t-2", b"Terminal 2 laeuft\r\n")

    def quellen(self, **ersatz):
        q = kp.Quellen(
            agenten=lambda: self.agenten, ereignisse=lambda von, bis, ag: [e.zu_dict() for e in self.p.zeitraum(von, bis, ag)], terminal=lambda t, bis: self.p.ausgabe_bis(t, bis, 200_000),
            frames=lambda t: [(f, {"captured_at_ms": 5000 + i, "width": 100, "height": 50, "source": "capture", "seq": i}) for i, f in enumerate(sorted((self.frames_dir / t).glob("frame-*.jpg"), key=lambda p: int(p.stem.split("-")[1])))]
            if (self.frames_dir / t).exists() else [],
            koerper=lambda t: {"objekte": [{"id": "o1", "art": "marker"}], "haende": True} if t == "t-1" else None, weltdom=lambda z: [{"id": "rea-cdp-1", "name": "OK"}] if z.endswith(":5") else [],
            laeufe=lambda t: [{"id": "l-1", "status": "completed"}] if t == "t-1" else [], jetzt_ms=self.uhr)
        for k, v in ersatz.items():
            setattr(q, k, v)
        return q


def werkstatt():
    ordner = Path(tempfile.mkdtemp())
    return Welt(ordner), kp.KapselStore(ordner / "kapseln")


class ProtokollTests(unittest.TestCase):
    def test_erfassen_filtern_und_zaehlen_ohne_modell(self):
        w, _ = werkstatt()
        self.assertEqual(w.p.anzahl(), 4)
        self.assertEqual([e.art for e in w.p.zeitraum(agenten=["t-1"])], ["nachricht", "regie", "haende"])
        self.assertEqual([e.art for e in w.p.zeitraum(arten=["auftrag"])], ["auftrag"])
        self.assertEqual(w.p.zaehler(), {"t-1": 3, "t-2": 1})
        self.assertEqual(w.p.ereignis("e-2").text, "Auftrag a-1 angenommen")
        self.assertIsNone(w.p.ereignis("e-99"))
        self.assertEqual(w.p.erfassen("unsinn", "t-1"), "e-5")
        self.assertEqual(w.p.ereignis("e-5").art, "sonstiges")

    def test_datei_ueberlebt_den_neustart_und_kaputte_zeilen_werden_uebersprungen(self):
        ordner = Path(tempfile.mkdtemp())
        p = ep.Ereignisprotokoll(ordner)
        p.erfassen("nachricht", "t-1", "eins")
        p.erfassen("state", "t-1", "zwei")
        with open(ordner / "ereignisse.jsonl", "a", encoding="utf-8") as f:
            f.write("{kaputt\n[1]\n")
        neu = ep.Ereignisprotokoll(ordner)
        self.assertEqual([e.text for e in neu.letzte()], ["eins", "zwei"])
        self.assertEqual(neu.erfassen("state", "t-1", "drei"), "e-3", "die Zählung läuft weiter")

    def test_texte_und_daten_werden_begrenzt_und_unserialisierbares_stuerzt_nicht(self):
        w, _ = werkstatt()
        eid = w.p.erfassen("haende", "t-1", "x" * 5000, {"lang": "y" * 900, "objekt": object(), "tief": {"a": {"b": {"c": {"d": 1}}}}, "liste": [1, {"k": "v"}, object()]})
        e = w.p.ereignis(eid)
        self.assertEqual((len(e.text), len(e.daten["lang"])), (ep.MAX_TEXT, 400))
        self.assertTrue(e.daten["objekt"].startswith("<object"))
        json.dumps(e.zu_dict())

    def test_ausgabe_ist_begrenzt_und_sagt_was_fehlt(self):
        p = ep.Ereignisprotokoll(None, Uhr())
        for i in range(40):
            p.ausgabe("t-1", (f"{i:04d}" + "x" * 30_000).encode())
        text, meta = p.ausgabe_bis("t-1", None, max_zeichen=50_000)
        self.assertGreater(meta["verworfene_stuecke"], 0)
        self.assertTrue(meta["abgeschnitten"])
        self.assertEqual(len(text), 50_000)
        self.assertTrue(text.endswith("x"))
        self.assertEqual(p.ausgabe_bis("t-9", None), ("", {"verworfene_stuecke": 0, "abgeschnitten": False, "stuecke": 0}))

    def test_abonnenten_sehen_ereignisse_sofort_und_ein_kaputter_haelt_nichts_an(self):
        w, _ = werkstatt()
        gesehen = []
        w.p.abonnieren(lambda e: (_ for _ in ()).throw(RuntimeError("kaputt")))
        w.p.abonnieren(gesehen.append)
        w.p.erfassen("nachricht", "t-1", "neu")
        self.assertEqual([e.text for e in gesehen], ["neu"])


class StueckgrenzenProtokollTests(unittest.TestCase):
    def test_ein_zeichen_ueber_zwei_lesestuecke_bleibt_ganz_im_protokoll(self):
        text = "ä€😀 Größe ✓".encode("utf-8")
        for schnitt in range(len(text) + 1):
            p = ep.Ereignisprotokoll()
            p.ausgabe("a", text[:schnitt])
            p.ausgabe("a", text[schnitt:])
            ausgabe, _ = p.ausgabe_bis("a")
            self.assertEqual(ausgabe, "ä€😀 Größe ✓", f"Schnitt bei Byte {schnitt}")

    def test_agenten_zerlegen_unabhaengig_voneinander(self):
        p = ep.Ereignisprotokoll()
        e = "ä".encode("utf-8")
        p.ausgabe("a", e[:1])
        p.ausgabe("b", "x".encode())
        p.ausgabe("a", e[1:])
        self.assertEqual((p.ausgabe_bis("a")[0], p.ausgabe_bis("b")[0]), ("ä", "x"))


class KapselTests(unittest.TestCase):
    def test_kompletter_moment_hat_agenten_terminal_ereignisse_bilder_koerper_weltdom_laeufe_und_quellen(self):
        w, s = werkstatt()
        k = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="daniel", grund="Fehlerfall")
        self.assertEqual([a["name"] for a in k["agenten"]], ["Codex", "Claude", "Gemgem"])
        self.assertIn("Hallo aus Terminal 1", k["terminals"]["t-1"]["text"])
        self.assertEqual([e["art"] for e in k["nachrichten"]], ["nachricht", "auftrag", "regie"])
        self.assertEqual(len(k["frames"]["t-1"]), kp.MAX_FRAMES_JE_AGENT, "die letzten zehn")
        self.assertEqual(k["frames"]["t-1"][-1]["meta"]["seq"], 11)
        self.assertEqual(k["koerper"]["t-1"]["haende"], True)
        self.assertEqual(sorted(k["weltdom"]), ["kde1:window:5", "kde1:window:6"])
        self.assertEqual(k["laeufe"]["t-1"][0]["id"], "l-1")
        self.assertEqual((k["ausloeser"]["von"], k["ausloeser"]["art"], k["ausloeser"]["grund"]), ("daniel", "kompletter_moment", "Fehlerfall"))
        for feld in ("agenten", "terminals.t-1", "ereignisse", "frames.t-1", "koerper.t-1", "weltdom.kde1:window:5", "laeufe.t-1"):
            self.assertIn(feld, k["quellen"], feld)

    def test_luecken_werden_benannt_nie_verschwiegen(self):
        w, s = werkstatt()
        k = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="daniel")
        gruende = {l["feld"]: l["grund"] for l in k["luecken"]}
        self.assertIn("koerper.t-2", gruende, "der Körper lieferte für t-2 nichts")
        self.assertIn("frames.t-3", gruende)
        self.assertIn("terminals.t-3", gruende)
        self.assertIn("Zeichnungen und Bindungen fehlen", gruende["koerper.t-2"])
        # eine Quelle, die kaputt ist, wird zur Lücke statt zum Absturz
        def kaputt(t):
            raise OSError("platte weg")
        k2 = s.erzeugen(w.quellen(frames=kaputt), kp.ART_AGENT, von="daniel", agenten=["t-1"])
        self.assertTrue(any(l["feld"] == "frames.t-1" and "OSError" in l["grund"] for l in k2["luecken"]))
        # zu viel Terminal: gekürzt und gesagt
        w.p.ausgabe("t-1", b"z" * 100_000)
        k3 = s.erzeugen(w.quellen(), kp.ART_AGENT, von="daniel", agenten=["t-1"])
        self.assertEqual(len(k3["terminals"]["t-1"]["text"]), kp.MAX_TERMINAL_ZEICHEN)
        self.assertTrue(any("gekürzt" in l["grund"] or "unvollständig" in l["grund"] for l in k3["luecken"]))

    def test_die_sechs_arten_und_ihre_auswahl(self):
        w, s = werkstatt()
        self.assertEqual([a["terminal_id"] for a in s.erzeugen(w.quellen(), kp.ART_AGENT, von="d", agenten=["t-2"])["agenten"]], ["t-2"])
        self.assertEqual(sorted(a["terminal_id"] for a in s.erzeugen(w.quellen(), kp.ART_ZIEL, von="d", ziele=["kde1:window:5"])["agenten"]), ["t-1", "t-3"])
        self.assertEqual(sorted(a["terminal_id"] for a in s.erzeugen(w.quellen(), kp.ART_MARKIERT, von="d", agenten=["t-1", "t-2"])["agenten"]), ["t-1", "t-2"])
        k = s.erzeugen(w.quellen(), kp.ART_KOMBINIERT, von="d", ziele=["kde1:window:5", "kde1:window:6"])
        self.assertEqual(len(k["agenten"]), 3)
        bis = w.uhr.t + 1
        z = s.erzeugen(w.quellen(), kp.ART_ZEITRAUM, von="d", zeitraum=(0, bis), agenten=["t-1"])
        self.assertEqual(z["auswahl"]["zeitraum"], [0, bis])
        fehler = {(kp.ART_AGENT, ("t-1", "t-2")): "genau_ein_agent", (kp.ART_AGENT, ()): "genau_ein_agent", (kp.ART_MARKIERT, ("t-1",)): "mindestens_zwei_agenten"}
        for (art, ag), code in fehler.items():
            with self.assertRaises(kp.KapselFehler, msg=code) as c:
                s.erzeugen(w.quellen(), art, von="d", agenten=list(ag))
            self.assertEqual(str(c.exception), code)
        for art, kw, code in ((kp.ART_ZIEL, dict(ziele=[]), "ziele_ungueltig"), (kp.ART_KOMBINIERT, dict(ziele=["kde1:window:5"]), "ziele_ungueltig"), (kp.ART_ZEITRAUM, dict(zeitraum=(5, 5)), "zeitraum_ungueltig"),
                              ("wild", {}, "art_unbekannt"), (kp.ART_AGENT, dict(agenten=["t-9"]), "agent_unbekannt:t-9")):
            with self.assertRaises(kp.KapselFehler) as c:
                s.erzeugen(w.quellen(), art, von="d", **kw)
            self.assertEqual(str(c.exception), code)

    def test_zeitraum_um_ein_ereignis(self):
        self.assertEqual(kp.zeitraum_um(100_000, 30, 10), (70_000, 110_000))
        for kaputt in ((-1, 5), (0, 0), (5, -1), (80_000, 10_000)):
            with self.assertRaises(kp.KapselFehler):
                kp.zeitraum_um(100_000, *kaputt)
        w, s = werkstatt()
        e = w.p.ereignis("e-3")
        von, bis = kp.zeitraum_um(e.zeit_ms, 0.015, 0.015)
        k = s.erzeugen(w.quellen(), kp.ART_ZEITRAUM, von="d", zeitraum=(von, bis), agenten=["t-1"])
        self.assertIn("e-3", [x["id"] for x in k["ereignisse"]])
        self.assertNotIn("e-1", [x["id"] for x in k["ereignisse"]], "ein Ereignis außerhalb des Bereichs gehört nicht dazu")

    def test_das_original_ist_schreibgeschuetzt_und_eine_aenderung_faellt_auf(self):
        w, s = werkstatt()
        k = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="daniel")
        datei = s.ordner / k["id"] / "kapsel.json"
        self.assertEqual(stat.S_IMODE(datei.stat().st_mode) & 0o222, 0)
        self.assertTrue(s.laden(k["id"])["unveraendert"])
        os.chmod(datei, 0o644)
        d = json.loads(datei.read_text())
        d["ausloeser"]["grund"] = "nachträglich umgeschrieben"
        datei.write_text(json.dumps(d))
        self.assertFalse(s.laden(k["id"])["unveraendert"], "eine Änderung am Original wird erkannt")

    def test_frames_werden_mit_pruefsumme_kopiert(self):
        w, s = werkstatt()
        k = s.erzeugen(w.quellen(), kp.ART_AGENT, von="d", agenten=["t-1"])
        e = k["frames"]["t-1"][0]
        pfad = s.frame_pfad(k["id"], e)
        self.assertTrue(pfad.exists())
        import hashlib
        self.assertEqual(hashlib.sha256(pfad.read_bytes()).hexdigest(), e["sha256"])
        (w.frames_dir / "t-1" / "frame-2.jpg").write_bytes("verändert".encode("utf-8"))
        self.assertNotEqual(hashlib.sha256((w.frames_dir / "t-1" / "frame-2.jpg").read_bytes()).hexdigest(), e["sha256"], "die Kopie in der Kapsel ist unabhängig von den Originalen")

    def test_ebenen_tags_und_suche_ohne_das_original_anzufassen(self):
        w, s = werkstatt()
        k = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="daniel")
        vorher = (s.ordner / k["id"] / "kapsel.json").read_bytes()
        s.ebene_hinzufuegen(k["id"], "tags", "daniel", tags=["Umweg", "Beinahe", "mein eigener Tag"])
        s.ebene_hinzufuegen(k["id"], "kommentar", "claude", text="Hier kippte die Annahme.")
        s.ebene_hinzufuegen(k["id"], "gegenargument", "codex", text="Nein, der Test war schuld.", bezug={"ereignis_id": "e-3"})
        s.ebene_hinzufuegen(k["id"], "tags", "codex", tags=["Widerspruch"])
        self.assertEqual(s.tags(k["id"]), ["Beinahe", "Umweg", "Widerspruch", "mein eigener Tag"])
        self.assertEqual([e["art"] for e in s.ebenen(k["id"])], ["tags", "kommentar", "gegenargument", "tags"])
        self.assertEqual((s.ordner / k["id"] / "kapsel.json").read_bytes(), vorher, "das Original ist unverändert")
        self.assertEqual([x["id"] for x in s.suche(tags=["Umweg", "Widerspruch"])], [k["id"]])
        self.assertEqual(s.suche(tags=["Umweg", "Fehler"]), [])
        self.assertEqual(len(s.suche(tags=["Umweg", "Fehler"], alle_tags=False)), 1)
        self.assertEqual(len(s.suche(text="Hallo aus Terminal 1")), 1, "Terminaltext ist durchsuchbar")
        self.assertEqual(len(s.suche(text="der test war schuld")), 1, "Ebenen sind durchsuchbar")
        self.assertEqual(s.suche(text="gibt es nirgends"), [])
        for kaputt in (("tanzen", {}), ("tags", {"tags": []}), ("kommentar", {"text": " "}), ("tags", {"tags": ["x" * 41]}), ("tags", {"tags": [str(i) for i in range(31)]}), ("kommentar", {"text": "x" * (kp.MAX_TEXT + 1)})):
            with self.assertRaises(kp.KapselFehler, msg=str(kaputt)[:40]):
                s.ebene_hinzufuegen(k["id"], kaputt[0], "d", **kaputt[1])
        with self.assertRaises(kp.KapselFehler):
            s.ebene_hinzufuegen("k-gibts-nicht", "kommentar", "d", text="x")

    def test_folge_kapsel_verlinkt_die_eltern_und_laesst_sie_unveraendert(self):
        w, s = werkstatt()
        k1 = s.erzeugen(w.quellen(), kp.ART_MARKIERT, von="daniel", agenten=["t-1", "t-2"])
        w.p.erfassen("nachricht", "t-1", "später dazugekommen")
        w.agenten[0]["zustand"] = "exited"
        k2 = s.folge_kapsel(k1["id"], w.quellen(), "claude", "nach der Korrektur")
        self.assertEqual((k2["eltern"], sorted(a["terminal_id"] for a in k2["agenten"]), k2["agenten"][0]["zustand"]), (k1["id"], ["t-1", "t-2"], "exited"))
        self.assertEqual(s.laden(k1["id"])["agenten"][0]["zustand"], "running", "die Eltern zeigen weiter den alten Moment")
        self.assertTrue(s.laden(k1["id"])["unveraendert"])
        self.assertEqual([x["eltern"] for x in s.liste()], [None, k1["id"]])

    def test_vergleich_zweier_kapseln(self):
        w, s = werkstatt()
        k1 = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="d")
        w.p.erfassen("nachricht", "t-2", "Antwort")
        w.p.ausgabe("t-1", b"neue Zeile\r\n")
        w.agenten[0]["zustand"] = "failed"
        w.agenten = w.agenten[:2]
        k2 = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="d")
        s.ebene_hinzufuegen(k2["id"], "tags", "d", tags=["Fehler"])
        v = s.vergleiche(k1["id"], k2["id"])
        self.assertEqual((v["agenten"]["nur_in_a"], v["agenten"]["zustand_geaendert"]), (["t-3"], {"t-1": ["running", "failed"]}))
        self.assertEqual(v["terminal"]["t-1"]["unterschiedliche_zeilen"], 1)
        self.assertTrue(any("neue Zeile" in z for z in v["terminal"]["t-1"]["ausschnitt"]))
        self.assertEqual((v["ereignisse"]["a"]["nachricht"], v["ereignisse"]["b"]["nachricht"]), (1, 2))
        self.assertGreater(v["zeit_abstand_ms"], 0)
        self.assertEqual((v["tags"]["a"], v["tags"]["b"]), ([], ["Fehler"]))
        self.assertEqual(v["weltdom"]["gemeinsam"], 1)

    def test_lernstrecke_ist_eine_geordnete_liste_vorhandener_kapseln(self):
        w, s = werkstatt()
        a, b = (s.erzeugen(w.quellen(), kp.ART_AGENT, von="d", agenten=["t-1"])["id"] for _ in range(2))
        d = s.lernstrecke_speichern("Erste Lernstrecke", [b, a], "erst b, dann a")
        self.assertEqual((d["kapseln"], s.lernstrecke("Erste Lernstrecke")["notiz"]), ([b, a], "erst b, dann a"))
        self.assertIsNone(s.lernstrecke("gibt es nicht"))
        for kaputt in (("", [a]), ("x" * 61, [a]), ("a/b", [a]), ("ok", ["k-gibts-nicht"])):
            with self.assertRaises(kp.KapselFehler):
                s.lernstrecke_speichern(*kaputt)

    def test_kapsel_ids_sind_gegen_pfadtricks_gesichert(self):
        _, s = werkstatt()
        for boese in ("../etc", "k-../../x", "x", "k-" + "a" * 50, "k-a/b"):
            with self.assertRaises(kp.KapselFehler):
                s.laden(boese)
        with self.assertRaises(kp.KapselFehler):
            s.laden("k-gibtsnicht")

    def test_private_modellzustaende_werden_nie_behauptet(self):
        w, s = werkstatt()
        k = s.erzeugen(w.quellen(), kp.ART_KOMPLETT, von="d")
        text = json.dumps(k, ensure_ascii=False).lower()
        for verboten in ("chain_of_thought", "gedankenkette", "innerer zustand", "reasoning_trace"):
            self.assertNotIn(verboten, text)


class ScrubberTests(unittest.TestCase):
    def linie(self):
        ev = [{"id": f"e-{i}", "zeit_ms": z, "art": a, "agent": ag, "text": t} for i, (z, a, ag, t) in enumerate([(1000, "nachricht", "t-1", "eins"), (2000, "haende", "t-1", "zwei"), (3000, "auftrag", "t-2", "drei"),
                                                                                                                 (4000, "regie", "t-1", "vier")], 1)]
        return Zeitlinie(ev, {"t-1": [(900, "A"), (2500, "B")], "t-2": [(3500, "X")]}, {"t-1": [(1500, {"seq": 1}), (3800, {"seq": 2})]})

    def test_marken_und_schritte_vor_und_zurueck(self):
        z = self.linie()
        self.assertEqual(z.marken, [900, 1000, 1500, 2000, 2500, 3000, 3500, 3800, 4000])
        self.assertEqual((z.schritt(1000, 1), z.schritt(1000, -1), z.schritt(900, -1), z.schritt(4000, 1)), (1500, 900, None, None))

    def test_zustand_bei_zeigt_was_damals_war_mit_alter_und_luecken(self):
        z = self.linie()
        s = z.zustand_bei(2600)
        self.assertEqual((s["ereignisse_bis_hier"], s["terminal"]["t-1"], s["frame"]["t-1"]["meta"]["seq"], s["frame"]["t-1"]["alter_ms"]), (2, "AB", 1, 1100))
        self.assertEqual([e["id"] for e in s["nachrichten"]], ["e-1"])
        fruh = z.zustand_bei(800)
        self.assertEqual((fruh["ereignisse_bis_hier"], fruh["frame"]["t-1"], fruh["terminal"]["t-1"]), (0, None, ""))
        self.assertTrue(any("noch kein Bild" in l["grund"] for l in fruh["luecken"]))
        nur = z.zustand_bei(4000, agenten=["t-2"])
        self.assertEqual(nur["terminal"], {"t-2": "X"})

    def test_scrubben_geht_nie_hinaus_und_setzt_nichts_zurueck(self):
        s = self.linie().zustand_bei(3000)
        self.assertEqual((s["wirkung_auf_anwendung"], s["anwendung_zurueckgesetzt"]), (False, False))
        self.assertIn("zurückgesetzt", s["hinweis"])
        import inspect
        import augen_haende_bridge.scrubber as sc
        quelltext = inspect.getsource(sc)
        for verboten in ("subprocess", "socket", "urllib", "publish", "senden", "handler"):
            self.assertNotIn(verboten, quelltext, "der Scrubber hat keinen Weg nach draußen")

    def test_leere_zeitlinie(self):
        z = Zeitlinie([])
        self.assertEqual((z.marken, z.schritt(0, 1), z.zustand_bei(5)["ereignisse_bis_hier"]), ([], None, 0))


if __name__ == "__main__":
    unittest.main()
