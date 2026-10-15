"""Ampel: LED-Farben, Blinken, Pieps-Wunsch und Behebe-Aktionen (rein, ohne Fenster)."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import ampel
from augen_haende_bridge.koerper.ampel import GELB, GRAU, GRUEN, ROT


def augen(**ueber):
    werte = dict(an=True, nur_terminal=False, strom_vorhanden=True, alter_s=5.0, gesperrt=False)
    werte.update(ueber)
    return ampel.augen_led(**werte)


class AugenTests(unittest.TestCase):
    def test_frisches_bild_ist_gruen_und_nennt_das_alter(self):
        led = augen(alter_s=7.4)
        self.assertEqual((led.farbe, led.wort, led.blinkt, led.piepen), (GRUEN, "Bild 7 s", False, False))

    def test_das_keepalive_von_15_sekunden_bleibt_gruen(self):
        self.assertEqual(augen(alter_s=15.0).farbe, GRUEN)

    def test_gelb_zwischen_20_und_45_sekunden(self):
        self.assertEqual(augen(alter_s=30.0).farbe, GELB)

    def test_ein_langer_ausfall_ist_rot_blinkt_piept_und_bietet_den_neustart_an(self):
        led = augen(alter_s=212 * 60)  # so lange fehlte dem Gutachter heute das Bild
        self.assertEqual((led.farbe, led.blinkt, led.piepen, led.behebe), (ROT, True, True, "strom_neu"))
        self.assertIn("212 min", led.wort)

    def test_kein_strom_ist_rot_und_bietet_den_desktop_an(self):
        led = augen(strom_vorhanden=False, alter_s=None)
        self.assertEqual((led.farbe, led.behebe, led.piepen), (ROT, "desktop_binden", True))

    def test_erstes_bild_steht_noch_aus_ist_nur_gelb(self):
        self.assertEqual(augen(alter_s=None).farbe, GELB)

    def test_augen_aus_per_knopf_ist_grau_und_laesst_sich_einschalten(self):
        led = augen(an=False)
        self.assertEqual((led.farbe, led.behebe), (GRAU, "strom_neu"))

    def test_nur_terminal_ist_grau_ohne_alarm(self):
        led = augen(nur_terminal=True, strom_vorhanden=False, alter_s=None)
        self.assertEqual((led.farbe, led.piepen, led.blinkt), (GRAU, False, False))

    def test_not_aus_blinkt_rot_ohne_pieps(self):
        led = augen(gesperrt=True)
        self.assertEqual((led.farbe, led.blinkt, led.piepen), (ROT, True, False))


class HaendeTests(unittest.TestCase):
    def test_ohne_aktion_ist_grau(self):
        self.assertEqual(ampel.haende_led(haende_an=True, letztes=None).farbe, GRAU)

    def test_ausgefuehrte_aktion_ist_gruen(self):
        self.assertEqual(ampel.haende_led(haende_an=True, letztes=("ausgefuehrt", "", 3.0)).farbe, GRUEN)

    def test_verdeckt_ist_rot_mit_behebe_knopf_und_blinkt_zuerst(self):
        led = ampel.haende_led(haende_an=True, letztes=("abgelehnt", "punkt_verdeckt", 4.0))
        self.assertEqual((led.farbe, led.wort, led.behebe, led.blinkt, led.piepen), (ROT, "Ziel verdeckt", "fenster_vor", True, True))

    def test_nach_zwoelf_sekunden_hoert_das_blinken_auf_die_farbe_bleibt(self):
        led = ampel.haende_led(haende_an=True, letztes=("abgelehnt", "punkt_verdeckt", 30.0))
        self.assertEqual((led.farbe, led.blinkt, led.piepen), (ROT, False, False))

    def test_daniel_bedient_ist_gelb_ohne_alarm(self):
        led = ampel.haende_led(haende_an=True, letztes=("abgelehnt", "daniel_uebernimmt", 2.0))
        self.assertEqual((led.farbe, led.blinkt, led.piepen, led.behebe), (GELB, False, False, None))

    def test_kein_bezugsbild_und_zu_altes_bild_bieten_den_neustart_der_bilder_an(self):
        for grund in ("frame_unbekannt", "frame_veraltet"):
            self.assertEqual(ampel.haende_led(haende_an=True, letztes=("abgelehnt", grund, 2.0)).behebe, "strom_neu")

    def test_fenster_weg_bietet_den_desktop_an(self):
        self.assertEqual(ampel.haende_led(haende_an=True, letztes=("abgelehnt", "ziel_weg", 2.0)).behebe, "desktop_binden")

    def test_unbekannter_grund_wird_im_klartext_gezeigt_und_nicht_verschluckt(self):
        led = ampel.haende_led(haende_an=True, letztes=("abgelehnt", "neu_erfunden", 2.0))
        self.assertEqual((led.farbe, led.wort), (ROT, "neu_erfunden"))

    def test_eine_alte_aktion_ist_nur_noch_ruhe(self):
        self.assertEqual(ampel.haende_led(haende_an=True, letztes=("abgelehnt", "punkt_verdeckt", 600.0)).farbe, GRAU)

    def test_haende_aus_ist_grau(self):
        self.assertEqual(ampel.haende_led(haende_an=False, letztes=("abgelehnt", "ziel_weg", 1.0)).farbe, GRAU)


class ZielUndLaufTests(unittest.TestCase):
    def test_gebunden_zeigt_das_ziel_im_klartext(self):
        led = ampel.ziel_led(gebunden=True, ziel_text="Ziel: notiz.txt — Kate", fenster_weg=False)
        self.assertEqual((led.farbe, led.wort), (GRUEN, "notiz.txt — Kate"))

    def test_ungebunden_heisst_ganzer_desktop_und_ist_gelb(self):
        self.assertEqual(ampel.ziel_led(gebunden=False, ziel_text="Ziel: Desktop (ungebunden)", fenster_weg=False).farbe, GELB)

    def test_fenster_weg_blinkt_piept_und_bietet_den_desktop_an(self):
        led = ampel.ziel_led(gebunden=True, ziel_text="x", fenster_weg=True)
        self.assertEqual((led.farbe, led.blinkt, led.piepen, led.behebe), (ROT, True, True, "desktop_binden"))

    def test_kein_lauf_ist_grau(self):
        self.assertEqual(ampel.lauf_led(lauf=None).farbe, GRAU)

    def test_wer_dran_ist_und_worauf_gewartet_wird_steht_da(self):
        led = ampel.lauf_led(lauf={"knoten": "s7.handeln", "dran": "Opencode", "wartet_auf": "Bild", "seit_s": 30})
        self.assertEqual(led.farbe, GRUEN)
        self.assertIn("Opencode wartet auf Bild", led.wort)

    def test_langes_warten_wird_gelb_dann_rot_mit_pieps(self):
        mitte = ampel.lauf_led(lauf={"knoten": "s7.handeln", "dran": "Opencode", "wartet_auf": "Bild", "seit_s": 90})
        lang = ampel.lauf_led(lauf={"knoten": "s7.handeln", "dran": "Opencode", "wartet_auf": "Bild", "seit_s": 400})
        self.assertEqual(mitte.farbe, GELB)
        self.assertEqual((lang.farbe, lang.piepen), (ROT, True))


class PiepsTests(unittest.TestCase):
    def zeilen(self, farbe_alter):
        led = ampel.augen_led(an=True, nur_terminal=False, strom_vorhanden=True, alter_s=farbe_alter, gesperrt=False)
        return [("Opencode", [led])]

    def test_piepen_nur_beim_wechsel_auf_rot(self):
        piept, zustand = ampel.neue_pieps({}, self.zeilen(500.0))
        self.assertTrue(piept)
        piept2, zustand = ampel.neue_pieps(zustand, self.zeilen(520.0))
        self.assertFalse(piept2)  # bleibt rot: keine Dauerschleife
        piept3, zustand = ampel.neue_pieps(zustand, self.zeilen(3.0))
        self.assertFalse(piept3)
        piept4, _ = ampel.neue_pieps(zustand, self.zeilen(500.0))
        self.assertTrue(piept4)  # wieder rot nach Grün: es piept erneut



class GesamtTests(unittest.TestCase):
    def zeile(self, *farben):
        return ("A", [ampel.Led("x", f, "w") for f in farben])

    def test_alles_gruen_oder_grau_ist_alles_gut(self):
        self.assertEqual(ampel.gesamt([self.zeile(GRUEN, GRAU)]), (GRUEN, "ALLES GUT", False))

    def test_gelb_ist_achtung_ohne_blinken(self):
        self.assertEqual(ampel.gesamt([self.zeile(GRUEN, GELB, GELB)]), (GELB, "2 ACHTUNG", False))

    def test_rot_gewinnt_blinkt_und_zaehlt_ueber_alle_agenten(self):
        farbe, wort, blinkt = ampel.gesamt([self.zeile(ROT, GELB), self.zeile(ROT, GRUEN)])
        self.assertEqual((farbe, wort, blinkt), (ROT, "2 PROBLEME", True))
        self.assertEqual(ampel.gesamt([self.zeile(ROT)])[1], "1 PROBLEM")

    def test_ohne_agent_steht_es_da(self):
        self.assertEqual(ampel.gesamt([])[1], "KEIN AGENT")



def katalog(**ueber):
    werte = dict(name="Opencode", alter_s=3.0, ziel_zustand="ok", aufnahme="frisch")  # ein gesunder Agent hat ein sichtbares Ziel mit frischer Aufnahme
    werte.update(ueber)
    return {l.kennung: l for l in ampel.lampen(ampel.Zustand(**werte))}


class KatalogTests(unittest.TestCase):
    def test_die_festen_lampen_stehen_in_fester_reihenfolge_mit_ausgeschriebenem_namen(self):
        erg = ampel.lampen(ampel.Zustand(name="A", alter_s=1.0, ziel_zustand="ok", aufnahme="frisch"))
        fest = [l for l in erg if not l.kennung.startswith(("gate:", "raute:", "art:", "ziel:"))]
        self.assertEqual(tuple(l.kennung for l in fest), ampel.KATALOG)
        self.assertTrue(all(len(l.name) > 8 and l.name == ampel.NAMEN[l.kennung] for l in fest), "keine Kürzel")
        self.assertTrue(all(l.wort for l in erg), "jede Lampe trägt ein Wort")
        self.assertEqual(len({l.name for l in erg}), len(erg), "jeder Name kommt nur einmal vor")

    def test_ein_gesunder_agent_hat_nur_laeuft_und_keine_gelbe_oder_graue_lampe(self):
        farben = {k: l.farbe for k, l in katalog().items()}
        self.assertEqual(set(farben.values()), {GRUEN})  # alles läuft, der ganze Desktop ist der Normalfall

    def test_ganzer_desktop_ist_der_normalzustand_und_keine_warnung(self):
        l = katalog(gebunden=False, ziel_text="Ziel: Desktop (ungebunden)")["bind"]
        self.assertEqual(l.farbe, GRUEN)
        self.assertIn("Desktop", l.wort)

    def test_noch_keine_haende_aktion_ist_bereit_und_nicht_aus(self):
        l = katalog(letztes=None)["hand"]
        self.assertEqual((l.farbe, l.wort), (GRUEN, "bereit, noch keine Aktion"))

    def test_die_probleme_des_bilderstroms_haben_je_eine_lampe(self):
        k = katalog(probleme=frozenset({"ziel_unsichtbar", "aufnahme_rueckfall", "senden_abgelehnt"}))
        self.assertEqual((k["sicht"].farbe, k["sicht"].behebe), (ROT, "fenster_vor"))
        self.assertEqual(k["aufn"].farbe, GELB)
        self.assertEqual((k["send"].farbe, k["send"].behebe, k["send"].piepen), (ROT, "strom_neu", True))

    def test_ablehnungsgruende_der_haende_haben_je_eine_gate_lampe_und_klingen_ab(self):
        k = katalog(gruende={"punkt_verdeckt": 4.0, "frame_unbekannt": 200.0, "daniel_uebernimmt": 3.0, "lease_fehlt": 10.0})
        v = k["gate:punkt_verdeckt"]
        self.assertEqual((v.farbe, v.behebe, v.blinkt), (ROT, "fenster_vor", True))
        self.assertEqual(k["gate:frame_unbekannt"].farbe, GRUEN)  # vor 200 s: abgeklungen
        self.assertEqual(k["gate:daniel_uebernimmt"].farbe, GELB)
        self.assertEqual(k["gate:lease_fehlt"].farbe, GELB)

    def test_fenster_weg_und_terminal_ausserhalb_bieten_ihre_hilfe_an(self):
        k = katalog(fenster_weg=True, terminal_draussen=True)
        self.assertEqual((k["weg"].farbe, k["weg"].behebe), (ROT, "desktop_binden"))
        self.assertEqual((k["bind"].farbe, k["bind"].behebe), (ROT, "desktop_binden"))
        self.assertEqual((k["auss"].farbe, k["auss"].behebe), (ROT, "terminal_holen"))

    def test_verbindung_und_not_aus(self):
        k = katalog(verbunden=False, gesperrt=True)
        self.assertEqual((k["verb"].farbe, k["verb"].piepen), (ROT, True))
        self.assertEqual((k["nota"].farbe, k["nota"].blinkt), (ROT, True))

    def test_kein_strom_ist_rot_und_nur_terminal_ist_still(self):
        self.assertEqual(katalog(strom_vorhanden=False, alter_s=None)["strom"].farbe, ROT)
        k = katalog(nur_terminal=True, strom_vorhanden=False, alter_s=None)
        self.assertEqual((k["strom"].farbe, k["bild"].farbe), (GRAU, GRAU))

    def test_augen_aus_per_knopf_ist_grau_und_laesst_sich_einschalten(self):
        l = katalog(an=False)["strom"]
        self.assertEqual((l.farbe, l.behebe), (GRAU, "strom_neu"))


class HaendeAufgeschluesseltTests(unittest.TestCase):
    ERFOLG = ("ausgefuehrt", "", 5.0)

    def test_je_aktionsart_und_je_programm_eine_lampe_mit_ausgeschriebenem_namen(self):
        k = katalog(haende_arten={"klick": self.ERFOLG, "tippe": self.ERFOLG, "taste": ("abgelehnt", "punkt_verdeckt", 3.0)},
                    haende_ziele={"Kate": self.ERFOLG, "Chromium": ("abgelehnt", "frame_unbekannt", 2.0)})
        namen = {l.name: l for l in k.values()}
        self.assertEqual(namen["Hände: Klicken"].farbe, GRUEN)
        self.assertEqual(namen["Hände: Tippen"].farbe, GRUEN)
        self.assertEqual((namen["Hände: Tasten"].farbe, namen["Hände: Tasten"].behebe), (ROT, "fenster_vor"))
        self.assertEqual(namen["Hände in Kate"].farbe, GRUEN)
        self.assertEqual((namen["Hände in Chromium"].farbe, namen["Hände in Chromium"].behebe), (ROT, "strom_neu"))

    def test_nichts_dazuerfinden_ohne_beobachtete_aktionen_gibt_es_keine_art_und_keine_programmlampe(self):
        self.assertFalse([k for k in katalog() if k.startswith(("art:", "ziel:"))])

    def test_eine_alte_ablehnung_ist_nur_noch_achtung_nicht_mehr_kaputt(self):
        l = katalog(haende_arten={"klick": ("abgelehnt", "punkt_verdeckt", 900.0)})["art:klick"]
        self.assertEqual((l.farbe, l.blinkt, l.piepen), (GELB, False, False))
        self.assertIn("zuletzt", l.wort)

    def test_eine_unbekannte_aktionsart_wird_im_klartext_gezeigt(self):
        self.assertEqual(katalog(haende_arten={"schweben": self.ERFOLG})["art:schweben"].name, "Hände: Schweben")


class MenueUndFlaecheTests(unittest.TestCase):
    def test_menuezeile_schreibt_die_funktion_aus_und_setzt_den_zustand_in_klammern(self):
        k = katalog()
        self.assertEqual(ampel.menue_zeile(k["strom"]), "Bilderstrom (läuft)")
        rot = katalog(alter_s=900.0)["bild"]
        self.assertEqual(ampel.menue_zeile(rot), f"Bilder kommen frisch an (kaputt: {rot.wort})")
        self.assertTrue(ampel.menue_zeile(katalog(verbunden=False)["verb"]).startswith("Verbindung zur Bridge (kaputt"))

    def test_die_flaeche_zeigt_die_schlimmste_farbe(self):
        self.assertEqual(ampel.schlimmste(list(katalog().values())), GRUEN)
        self.assertEqual(ampel.schlimmste(list(katalog(probleme=frozenset({"aufnahme_rueckfall"})).values())), GELB)
        self.assertEqual(ampel.schlimmste(list(katalog(fenster_weg=True, probleme=frozenset({"aufnahme_rueckfall"})).values())), ROT)


class ChatDauerfeuerTests(unittest.TestCase):
    def rote(self, **ueber):
        return ampel.lampen(ampel.Zustand(name="Opencode", alter_s=900.0, **ueber))

    def test_eine_rote_lampe_wird_gemeldet_und_dann_alle_zwanzig_sekunden_wiederholt(self):
        z1, rot, zeiten = ampel.chat_meldungen({}, {}, 100.0, "Opencode", self.rote())
        self.assertEqual(len(z1), 1)
        self.assertIn("[Opencode] Bilder kommen frisch an", z1[0])
        self.assertIn("Ampel-Knopf: Bilder neu starten", z1[0])
        z2, rot, zeiten = ampel.chat_meldungen(rot, zeiten, 110.0, "Opencode", self.rote())
        self.assertEqual(z2, [])  # noch keine zwanzig Sekunden
        z3, rot, zeiten = ampel.chat_meldungen(rot, zeiten, 121.0, "Opencode", self.rote())
        self.assertEqual(len(z3), 1)  # Dauerfeuer, bis es behoben ist

    def test_wenn_es_behoben_ist_kommt_einmal_wieder_in_ordnung_und_dann_ruhe(self):
        _z, rot, zeiten = ampel.chat_meldungen({}, {}, 100.0, "Opencode", self.rote())
        gut = ampel.lampen(ampel.Zustand(name="Opencode", alter_s=2.0))
        z, rot, zeiten = ampel.chat_meldungen(rot, zeiten, 105.0, "Opencode", gut)
        self.assertEqual(z, ["✓ [Opencode] Bilder kommen frisch an: wieder in Ordnung"])
        z, rot, zeiten = ampel.chat_meldungen(rot, zeiten, 110.0, "Opencode", gut)
        self.assertEqual(z, [])

    def test_hoechstens_drei_zeilen_je_aufruf_und_die_agenten_stoeren_sich_nicht(self):
        viele = ampel.lampen(ampel.Zustand(name="A", alter_s=900.0, fenster_weg=True, terminal_draussen=True, verbunden=False,
                                           probleme=frozenset({"senden_abgelehnt"})))
        zeilen, rot, zeiten = ampel.chat_meldungen({}, {}, 100.0, "A", viele)
        self.assertEqual(len(zeilen), 3)
        zeilen_b, rot_b, _z = ampel.chat_meldungen(rot, zeiten, 100.0, "B", self.rote())
        self.assertEqual(len(zeilen_b), 1)  # B hat eigene Takte
        self.assertTrue(any(k[0] == "A" for k in rot_b))  # A bleibt rot gemerkt



class GatesVollstaendigTests(unittest.TestCase):
    """Die Ampel kennt jedes Gate des Käfigs und jeden Grund des Bilderstroms: kommt im Code ein Grund dazu, schlägt dieser Test an."""

    def test_jeder_ablehnungsgrund_des_kaefigs_hat_eine_lampe(self):
        from augen_haende_bridge.koerper.eingabe_adapter import GRUENDE
        in_tabelle = {g[0] for g in ampel.HAENDE_GATES}
        self.assertEqual(sorted(set(GRUENDE) - in_tabelle), [], "Gründe des Käfigs ohne Lampe")
        self.assertEqual(sorted(in_tabelle - set(GRUENDE)), [], "Lampen für Gründe, die der Käfig nicht kennt")

    def test_die_gates_stehen_in_der_pruefreihenfolge_des_kaefigs(self):
        import inspect
        import re
        from augen_haende_bridge.koerper import eingabe_adapter
        quelltext = inspect.getsource(eingabe_adapter.pruefe)
        reihenfolge = []
        for grund in re.findall(r'Entscheidung\(False, "([a-z_]+)"\)|return Entscheidung\(False, (lease_grund)\)', quelltext):
            g = grund[0] or "lease_fehlt"
            if g not in reihenfolge:
                reihenfolge.append(g)
        tabelle = [g[0] for g in ampel.HAENDE_GATES if g[0] in reihenfolge]
        self.assertEqual(tabelle, [g for g in reihenfolge if g in tabelle])

    def test_gate_gruende_ohne_eigene_lampe_sind_durch_eine_bestehende_abgedeckt(self):
        k = katalog()
        for grund, lampe in ampel.ABGEDECKT_DURCH.items():
            self.assertIn(lampe, k)
            self.assertNotIn(f"gate:{grund}", k)

    def test_jeder_grund_des_bilderstroms_hat_eine_lampe(self):
        import inspect
        import re
        from augen_haende_bridge.koerper import bilderstrom
        gruende = set(re.findall(r'self\._stumm\([a-z"]+, "([a-z_]+)"', inspect.getsource(bilderstrom.Bilderstrom)))
        self.assertTrue(gruende, "der Test muss die Gründe im Quelltext finden")
        self.assertEqual(sorted(gruende - set(ampel.AUGEN_GRUENDE)), [], "Gründe des Bilderstroms ohne Lampe")
        k = katalog()
        for grund, lampe in ampel.AUGEN_GRUENDE.items():
            self.assertIn(lampe, k, grund)

    def test_jedes_gate_zeigt_seine_ablehnung_und_wird_danach_wieder_ruhig(self):
        for grund, _name, farbe, behebe, frisch in ampel.HAENDE_GATES:
            if grund in ampel.ABGEDECKT_DURCH:
                continue
            roh = katalog(gruende={grund: 1.0})[f"gate:{grund}"]
            self.assertEqual((roh.farbe, roh.behebe), (farbe, behebe), grund)
            alt = katalog(gruende={grund: frisch + 1})[f"gate:{grund}"]
            self.assertEqual(alt.farbe, GRUEN, grund)

    def test_jeder_grund_der_raute_ansage_hat_eine_lampe(self):
        from augen_haende_bridge.koerper.anwendung import KoerperAnwendung
        gruende = set(KoerperAnwendung.HAENDE_GRUENDE) | {"agent_unbekannt", "nur_terminal"}
        in_tabelle = {g[0] for g in ampel.RAUTE_GATES} | set(ampel.RAUTE_ABGEDECKT)
        self.assertEqual(sorted(gruende - in_tabelle), [], "Gründe der Raute-Ansage ohne Lampe")
        self.assertEqual(sorted(in_tabelle - gruende), [], "Lampen für Gründe, die die Raute-Ansage nicht kennt")
        k = katalog()
        for grund, _name, farbe in ampel.RAUTE_GATES:
            roh = katalog(gruende={f"raute:{grund}": 1.0})[f"raute:{grund}"]
            self.assertEqual(roh.farbe, farbe, grund)
            self.assertEqual(katalog(gruende={f"raute:{grund}": 999.0})[f"raute:{grund}"].farbe, GRUEN, grund)
        for lampe in ampel.RAUTE_ABGEDECKT.values():
            self.assertIn(lampe, k)

    def test_jeder_zustand_des_ziel_fensters_und_jede_aufnahmefaehigkeit_hat_eine_lampe(self):
        from augen_haende_bridge.koerper import anzeigeort
        self.assertEqual(sorted(set(anzeigeort.ZIEL_ZUSTAENDE) - set(ampel.ZIEL_ZUSTAND_LAMPE)), [])
        self.assertEqual(sorted(set(anzeigeort.ZIEL_FAEHIGKEITEN) - set(ampel.AUFNAHME_LAMPE)), [])
        for zustand in anzeigeort.ZIEL_ZUSTAENDE:
            farbe = ampel.ZIEL_ZUSTAND_LAMPE[zustand][0]
            self.assertEqual(katalog(ziel_zustand=zustand)["zustand"].farbe, farbe, zustand)
        for faehig in anzeigeort.ZIEL_FAEHIGKEITEN:
            self.assertEqual(katalog(aufnahme=faehig)["aufnahme"].farbe, ampel.AUFNAHME_LAMPE[faehig][0], faehig)

    def test_ein_minimiertes_oder_geschlossenes_ziel_ist_rot_und_bietet_hilfe_an(self):
        self.assertEqual((katalog(ziel_zustand="minimiert")["zustand"].farbe, katalog(ziel_zustand="minimiert")["zustand"].behebe), (ROT, "fenster_vor"))
        self.assertEqual(katalog(ziel_zustand="weg")["zustand"].behebe, "desktop_binden")

    def test_jeder_grund_der_anzeigeort_befehle_ist_bekannt_und_die_lampe_zeigt_ihn(self):
        from augen_haende_bridge.koerper import anzeigeort
        self.assertEqual(sorted(set(anzeigeort.GRUND_TEXT) ^ set(ampel.ANZEIGEORT_GRUENDE)), [])
        self.assertEqual(katalog(anzeigeort_grund=("ort_offline", 5.0))["anzeigeort"].farbe, GELB)
        self.assertEqual(katalog(anzeigeort_grund=("ort_offline", 500.0))["anzeigeort"].farbe, GRUEN)

    def test_die_selbstbild_kamera_zeigt_ihren_fehler(self):
        self.assertEqual(katalog(kamera="fehler")["kamera"].farbe, ROT)
        self.assertEqual(katalog(kamera="ein")["kamera"].farbe, GRUEN)

    def test_ein_ausschnitt_ausserhalb_des_bilds_wird_rot(self):
        self.assertEqual(katalog(probleme=frozenset({"ausschnitt_leer"}))["ausschnitt"].farbe, ROT)


if __name__ == "__main__":
    unittest.main()
