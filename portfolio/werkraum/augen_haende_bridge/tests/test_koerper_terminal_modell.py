"""Terminalmodell des Körpers: echter pyte-Bildschirm, keine Attrappe. Läuft unter Linux und Wine."""
import unittest

try:
    import pyte  # noqa: F401
except ImportError:  # pyte gehört zum Körper, nicht zum Kern
    pyte = None

if pyte is not None:
    from augen_haende_bridge.koerper import terminal_modell as tm


@unittest.skipIf(pyte is None, "pyte nicht installiert")
class ModellTests(unittest.TestCase):
    def modell(self, zeilen=10, spalten=40, antworten=None):
        return tm.TerminalModell(zeilen, spalten, antwort=(antworten.append if antworten is not None else None))

    def test_text_farben_und_attribute(self):
        m = self.modell()
        m.einspeisen(b"\x1b[31mrot\x1b[0m \x1b[1;44mfett\x1b[0m \x1b[7mumgekehrt\x1b[0m")
        self.assertEqual(m.zeile_text(0).rstrip(), "rot fett umgekehrt")
        rot = m.zelle(0, 0)
        self.assertEqual((rot.zeichen, rot.vordergrund, rot.hintergrund), ("r", (197, 15, 31), tm.STANDARD_BG))
        fett = m.zelle(0, 4)
        self.assertTrue(fett.fett)
        self.assertEqual(fett.hintergrund, (0, 55, 218))
        umgekehrt = m.zelle(0, 9)
        self.assertEqual((umgekehrt.vordergrund, umgekehrt.hintergrund), (tm.STANDARD_BG, tm.STANDARD_FG))

    def test_256_und_truecolor(self):
        m = self.modell()
        m.einspeisen(b"\x1b[38;5;196ma\x1b[38;5;1mb\x1b[38;2;10;20;30mc\x1b[48;5;21md")
        self.assertEqual(m.zelle(0, 0).vordergrund, (255, 0, 0))
        self.assertEqual(m.zelle(0, 1).vordergrund, (205, 0, 0))  # 8-Bit-Farben behalten die xterm-Werte, benannte Farben die Palette
        self.assertEqual(m.zelle(0, 2).vordergrund, (10, 20, 30))
        self.assertEqual(m.zelle(0, 3).hintergrund, (0, 0, 255))

    def test_cursor_und_breite_zeichen_und_zerschnittenes_utf8(self):
        m = self.modell()
        m.einspeisen(b"\x1b[5;10H")
        self.assertEqual(m.cursor(), (4, 9, True))
        m.einspeisen("你".encode()[:2])
        m.einspeisen("你".encode()[2:] + "é".encode()[:1])
        m.einspeisen("é".encode()[1:])
        breit, stumm = m.zelle(4, 9), m.zelle(4, 10)
        self.assertTrue(breit.breit and breit.zeichen == "你")
        self.assertTrue(stumm.stumm)
        self.assertEqual(m.zelle(4, 11).zeichen, "é")

    def test_cursor_kann_versteckt_werden(self):
        m = self.modell()
        m.einspeisen(b"\x1b[?25l")
        self.assertFalse(m.cursor()[2])
        m.einspeisen(b"\x1b[?25h")
        self.assertTrue(m.cursor()[2])

    def test_alternate_screen_haelt_und_stellt_den_hauptschirm_wieder_her(self):
        m = self.modell()
        m.einspeisen(b"haupt\r\nzweite")
        vorher = (m.zeile_text(0), m.zeile_text(1), m.cursor())
        m.einspeisen(b"\x1b[?1049h")
        self.assertTrue(m.bildschirm.alternativ)
        self.assertEqual(m.zeile_text(0).strip(), "")
        m.einspeisen(b"\x1b[H\x1b[2JTUI-Inhalt")
        self.assertEqual(m.zeile_text(0).rstrip(), "TUI-Inhalt")
        m.einspeisen(b"\x1b[?1049l")
        self.assertFalse(m.bildschirm.alternativ)
        self.assertEqual((m.zeile_text(0), m.zeile_text(1), m.cursor()), vorher)

    def test_alternate_screen_schreibt_keinen_verlauf(self):
        m = self.modell(zeilen=5)
        m.einspeisen(b"\x1b[?1049h" + b"\r\n".join(b"z%d" % i for i in range(40)))
        self.assertEqual(len(m.bildschirm.history.top), 0)
        m.einspeisen(b"\x1b[?1049l")
        m.blaettern(1)
        self.assertFalse(m.im_verlauf())

    def test_verlauf_blaettern_und_zurueck_bei_neuer_ausgabe(self):
        m = self.modell(zeilen=5)
        m.einspeisen(b"\r\n".join(b"zeile %d" % i for i in range(30)))
        unten = m.zeile_text(4).rstrip()
        m.blaettern(2)
        self.assertTrue(m.im_verlauf())
        self.assertNotEqual(m.zeile_text(4).rstrip(), unten)
        m.einspeisen(b"\r\nneu")
        self.assertFalse(m.im_verlauf())
        m.blaettern(1)
        m.blaettern(-5)
        self.assertFalse(m.im_verlauf())

    def test_groesse_aendern(self):
        m = self.modell(zeilen=10, spalten=40)
        m.einspeisen(b"abc")
        self.assertTrue(m.groesse_setzen(20, 60))
        self.assertEqual((m.zeilen, m.spalten), (20, 60))
        self.assertFalse(m.groesse_setzen(20, 60))
        self.assertTrue(m.zeile_text(0).startswith("abc"))

    def test_terminal_antwortet_auf_abfragen_in_die_sitzung(self):
        antworten = []
        m = self.modell(antworten=antworten)
        m.einspeisen(b"\x1b[3;7H\x1b[6n")
        self.assertEqual(antworten[-1], b"\x1b[3;7R")
        m.einspeisen(b"\x1b[c")
        self.assertTrue(antworten[-1].startswith(b"\x1b[?"))

    def test_modi_werden_gelesen(self):
        m = self.modell()
        self.assertFalse(m.anwendungs_cursor())
        self.assertFalse(m.eingeklammertes_einfuegen())
        m.einspeisen(b"\x1b[?1h\x1b[?2004h")
        self.assertTrue(m.anwendungs_cursor())
        self.assertTrue(m.eingeklammertes_einfuegen())
        m.einspeisen(b"\x1b[?1l\x1b[?2004l")
        self.assertFalse(m.anwendungs_cursor())
        self.assertFalse(m.eingeklammertes_einfuegen())

    def test_umgebrochener_langer_befehl_wird_ohne_zeilenwechsel_kopiert(self):
        m = self.modell(zeilen=5, spalten=20)
        befehl = "git commit -m 'ein ziemlich langer Befehl mit Leerzeichen'"
        m.einspeisen(befehl.encode() + b"\r\nnaechste")
        m.auswahl_setzen((0, 0), (3, 20))
        self.assertEqual(m.auswahl_text(), befehl + "\nnaechste")

    def test_echter_zeilenwechsel_bleibt_auch_in_voller_zeile_erhalten_wenn_sie_mit_leerzeichen_endet(self):
        m = self.modell(zeilen=4, spalten=10)
        m.einspeisen(b"123456789 \r\nzweite")
        m.auswahl_setzen((0, 0), (1, 10))
        self.assertEqual(m.auswahl_text(), "123456789\nzweite")

    def test_alles_markieren_laesst_leere_zeilen_unten_weg(self):
        m = self.modell(zeilen=6, spalten=20)
        m.einspeisen(b"eins\r\nzwei")
        m.alles_markieren()
        self.assertEqual(m.auswahl_text(), "eins\nzwei")

    def test_blaettern_zeilenweise_und_versatz(self):
        m = self.modell(zeilen=5, spalten=20)
        m.einspeisen(b"".join(b"z%d\r\n" % i for i in range(30)))
        self.assertGreater(m.verlauf_laenge(), 20)
        self.assertEqual(m.verlauf_versatz(), 0)
        self.assertEqual(m.blaettern_zeilen(3), 3)
        self.assertEqual(m.verlauf_versatz(), 3)
        self.assertEqual(m.blaettern_zeilen(-1), -1)
        self.assertEqual(m.blaettern_zeilen(-10), -2)  # nur bis zur Gegenwart
        self.assertEqual(m.verlauf_versatz(), 0)
        self.assertEqual(m.blaettern_zeilen(-1), 0)

    def test_blaettern_ganz_nach_oben_endet_am_aeltesten_verlauf(self):
        m = self.modell(zeilen=5, spalten=20)
        m.einspeisen(b"".join(b"z%d\r\n" % i for i in range(30)))
        gesamt = m.verlauf_laenge()
        m.zu_versatz(10_000)
        self.assertEqual(m.verlauf_versatz(), gesamt)
        self.assertEqual(m.zeile_text(0).rstrip(), "z0")
        m.zu_versatz(0)
        self.assertEqual(m.verlauf_versatz(), 0)
        self.assertFalse(m.im_verlauf())

    def test_auswahl_wandert_beim_blaettern_mit_dem_text(self):
        m = self.modell(zeilen=5, spalten=20)
        m.einspeisen(b"".join(b"z%d\r\n" % i for i in range(30)))
        m.auswahl_setzen((1, 0), (2, 5))
        text = m.auswahl_text()
        m.blaettern_zeilen(1)
        self.assertEqual(m.auswahl, ((2, 0), (3, 5)))
        self.assertEqual(m.auswahl_text(), text)

    def test_im_alternate_screen_gibt_es_nichts_zu_blaettern(self):
        m = self.modell(zeilen=5, spalten=20)
        m.einspeisen(b"".join(b"z%d\r\n" % i for i in range(30)))
        m.einspeisen(b"\x1b[?1049h")
        self.assertEqual(m.blaettern_zeilen(3), 0)

    def test_rad_meldung_nur_wenn_das_programm_mausereignisse_will(self):
        m = self.modell()
        self.assertIsNone(m.rad_meldung(True, 4, 9))
        m.einspeisen(b"\x1b[?1000h")
        self.assertEqual(m.rad_meldung(True, 4, 9), b"\x1b[M" + bytes([96, 42, 37]))
        m.einspeisen(b"\x1b[?1006h")
        self.assertEqual(m.rad_meldung(True, 4, 9), b"\x1b[<64;10;5M")
        self.assertEqual(m.rad_meldung(False, 0, 0), b"\x1b[<65;1;1M")
        m.einspeisen(b"\x1b[?1000l")
        self.assertIsNone(m.rad_meldung(True, 4, 9))

    def _bildschirm(self, m):
        return [[m.zelle(z, sp) for sp in range(m.spalten)] for z in range(m.zeilen)]

    def test_zuruecksetzen_leert_alles_auch_den_alternate_screen_und_das_rueckblaettern(self):
        m = self.modell(zeilen=5, spalten=20)
        m.einspeisen(b"".join(b"z%d\r\n" % i for i in range(30)))
        m.einspeisen(b"\x1b[?1049h\x1b[2;3Halternativ")
        m.auswahl_setzen((0, 0), (1, 5))
        self.assertTrue(m.bildschirm.alternativ)
        m.zuruecksetzen()
        self.assertFalse(m.bildschirm.alternativ)
        self.assertEqual(m.verlauf_laenge(), 0)
        self.assertIsNone(m.auswahl)
        self.assertTrue(all(m.zeile_text(z).strip() == "" for z in range(m.zeilen)))
        self.assertEqual(m.cursor()[:2], (0, 0))

    def test_wiederaufnahme_baut_bildschirm_und_rueckblaettern_identisch_wieder_auf(self):
        """Original: laufender Strom ab Start. Wiederaufnahme: Bridge hat anderen Inhalt, setzt zurück, bekommt dieselben Bytes noch einmal."""
        strom = (b"\x1b[1;31mrot fett\x1b[0m und \x1b[38;2;10;200;30mtruecolor\x1b[0m\r\n"
                 + "Umlaute: äöüß, Wide: 日本語, Emoji: ✓\r\n".encode()
                 + b"".join(b"zeile %02d\r\n" % i for i in range(40))
                 + b"\x1b[?1049h\x1b[H\x1b[2Jvollbild\x1b[3;4Hmitte\x1b[?1049l"
                 + b"\x1b[3A\x1b[Kueberschrieben\r\n$ ")
        original = self.modell(zeilen=8, spalten=40)
        original.einspeisen(strom)
        andere = self.modell(zeilen=8, spalten=40)
        andere.einspeisen(b"voellig anderer Inhalt\r\n" * 20 + b"\x1b[?1049hnoch ein Vollbild")
        andere.zuruecksetzen()
        for i in range(0, len(strom), 7):  # in kleinen Stücken, wie sie ankommen
            andere.einspeisen(strom[i:i + 7])
        self.assertEqual(self._bildschirm(andere), self._bildschirm(original))
        self.assertEqual(andere.cursor(), original.cursor())
        self.assertEqual(andere.verlauf_laenge(), original.verlauf_laenge())
        self.assertFalse(andere.bildschirm.alternativ)
        original.zu_versatz(10_000)
        andere.zu_versatz(10_000)
        self.assertEqual(self._bildschirm(andere), self._bildschirm(original))  # auch ganz oben im Verlauf gleich

    def test_auswahl_text_und_wort(self):
        m = self.modell()
        m.einspeisen(b"erste zeile\r\nzweite  zeile")
        m.auswahl_setzen((0, 6), (1, 6))
        self.assertEqual(m.auswahl_text(), "zeile\nzweite")
        self.assertTrue(m.ist_ausgewaehlt(0, 7))
        self.assertFalse(m.ist_ausgewaehlt(0, 2))
        m.auswahl_setzen(None)
        self.assertEqual(m.auswahl_text(), "")
        self.assertEqual(m.wort_bei(1, 2), ((1, 0), (1, 6)))

    def test_farbnamen_und_ungueltiges(self):
        self.assertEqual(tm.farbe_rgb("default", (1, 2, 3)), (1, 2, 3))
        self.assertEqual(tm.farbe_rgb("brightblue", (0, 0, 0)), (59, 120, 255))
        self.assertEqual(tm.farbe_rgb("ff8000", (0, 0, 0)), (255, 128, 0))
        self.assertEqual(tm.farbe_rgb("kaputt", (9, 9, 9)), (9, 9, 9))


@unittest.skipIf(pyte is None, "pyte nicht installiert")
class TastenTests(unittest.TestCase):
    VK = tm.VK if pyte is not None else {}

    def test_pfeile_normal_anwendung_und_mit_modifikatoren(self):
        self.assertEqual(tm.taste_zu_bytes(self.VK["UP"]), b"\x1b[A")
        self.assertEqual(tm.taste_zu_bytes(self.VK["UP"], anwendungs_cursor=True), b"\x1bOA")
        self.assertEqual(tm.taste_zu_bytes(self.VK["RIGHT"], strg=True), b"\x1b[1;5C")
        self.assertEqual(tm.taste_zu_bytes(self.VK["LEFT"], umschalt=True, alt=True), b"\x1b[1;4D")
        self.assertEqual(tm.taste_zu_bytes(self.VK["HOME"]), b"\x1b[H")
        self.assertEqual(tm.taste_zu_bytes(self.VK["END"], anwendungs_cursor=True), b"\x1bOF")

    def test_navigationstasten(self):
        self.assertEqual(tm.taste_zu_bytes(self.VK["DELETE"]), b"\x1b[3~")
        self.assertEqual(tm.taste_zu_bytes(self.VK["INSERT"]), b"\x1b[2~")
        self.assertEqual(tm.taste_zu_bytes(self.VK["PRIOR"]), b"\x1b[5~")
        self.assertEqual(tm.taste_zu_bytes(self.VK["NEXT"], strg=True), b"\x1b[6;5~")

    def test_funktionstasten(self):
        f = self.VK["F1"]
        self.assertEqual(tm.taste_zu_bytes(f), b"\x1bOP")
        self.assertEqual(tm.taste_zu_bytes(f + 3), b"\x1bOS")
        self.assertEqual(tm.taste_zu_bytes(f + 4), b"\x1b[15~")
        self.assertEqual(tm.taste_zu_bytes(f + 11), b"\x1b[24~")
        self.assertEqual(tm.taste_zu_bytes(f + 1, umschalt=True), b"\x1b[1;2Q")
        self.assertEqual(tm.taste_zu_bytes(f + 8, strg=True), b"\x1b[20;5~")

    def test_sonderfaelle_und_tasten_die_als_zeichen_kommen(self):
        self.assertEqual(tm.taste_zu_bytes(self.VK["TAB"], umschalt=True), b"\x1b[Z")
        self.assertIsNone(tm.taste_zu_bytes(self.VK["TAB"]))
        self.assertEqual(tm.taste_zu_bytes(self.VK["SPACE"], strg=True), b"\x00")
        self.assertIsNone(tm.taste_zu_bytes(ord("A")))

    def test_zeichen(self):
        self.assertEqual(tm.zeichen_zu_bytes(0x0D), b"\r")
        self.assertEqual(tm.zeichen_zu_bytes(0x08), b"\x7f")
        self.assertEqual(tm.zeichen_zu_bytes(0x09), b"\t")
        self.assertEqual(tm.zeichen_zu_bytes(0x1B), b"\x1b")
        self.assertEqual(tm.zeichen_zu_bytes(0x03), b"\x03")
        self.assertEqual(tm.zeichen_zu_bytes(ord("ä")), "ä".encode())
        self.assertEqual(tm.zeichen_zu_bytes(ord("x"), alt=True), b"\x1bx")
        self.assertEqual(tm.zeichen_zu_bytes(0x0D, alt=True), b"\x1b\r")
        self.assertIsNone(tm.zeichen_zu_bytes(0xD83D))

    def test_einfuegen(self):
        self.assertEqual(tm.einfuegen_zu_bytes("a\r\nb\nc", False), b"a\rb\rc")
        self.assertEqual(tm.einfuegen_zu_bytes("x", True), b"\x1b[200~x\x1b[201~")




@unittest.skipIf(pyte is None, "pyte nicht installiert")
class StueckgrenzenTests(unittest.TestCase):
    TEXT = "ä€😀 Größe \x1b[31mrot\x1b[0m ✓".encode("utf-8")

    def test_an_jeder_stueckgrenze_kommt_derselbe_bildschirm_heraus(self):
        ganz = tm.TerminalModell(4, 40)
        ganz.einspeisen(self.TEXT)
        for schnitt in range(len(self.TEXT) + 1):
            m = tm.TerminalModell(4, 40)
            m.einspeisen(self.TEXT[:schnitt])
            m.einspeisen(self.TEXT[schnitt:])
            self.assertEqual(m.zeile_text(0), ganz.zeile_text(0), f"Schnitt bei Byte {schnitt}")
        self.assertTrue(ganz.zeile_text(0).startswith("ä€😀 Größe rot ✓"))
        self.assertNotIn("\ufffd", ganz.zeile_text(0))

    def test_byteweise_zerstueckelt_geht_auch(self):
        m = tm.TerminalModell(4, 40)
        for b in self.TEXT:
            m.einspeisen(bytes([b]))
        self.assertTrue(m.zeile_text(0).startswith("ä€😀 Größe rot ✓"))


if __name__ == "__main__":
    unittest.main()
