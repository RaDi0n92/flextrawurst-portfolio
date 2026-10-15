"""Referenzfälle für die Terminalanzeige (R018): Eingabe sind echte VT100/xterm-Folgen, die erwartete Anzeige ist von Hand nach der
Terminal-Spezifikation (VT100/xterm, ECMA-48) geschrieben — nicht aus der Ausgabe des Modells abgeleitet. So prüft jeder Fall das Modell gegen
den Standard und nicht gegen sich selbst."""
import unittest

try:
    import pyte  # noqa: F401
except ImportError:
    pyte = None

if pyte is not None:
    from augen_haende_bridge.koerper import terminal_modell as tm


def zeilen(m):
    return [m.zeile_text(z).rstrip() for z in range(m.zeilen)]


@unittest.skipIf(pyte is None, "pyte nicht installiert")
class ReferenzTests(unittest.TestCase):
    def modell(self, zeilen_=6, spalten=20):
        return tm.TerminalModell(zeilen_, spalten)

    def test_cursor_positionierung_cup_cuu_cud_cuf_cub(self):
        m = self.modell()
        m.einspeisen(b"\x1b[3;5HA\x1b[2AB\x1b[3BC\x1b[4DD\x1b[2CE")
        # A bei (3,5)=Zeile 2 Spalte 4; danach Cursor Spalte 5. B zwei hoch: Zeile 0, Spalte 5; C drei runter: Zeile 3, Spalte 6;
        # D vier links: ab Spalte 3; E zwei rechts von Spalte 4: Spalte 6.
        z = zeilen(m)
        self.assertEqual(z[2][4], "A")
        self.assertEqual(z[0][5], "B")
        self.assertEqual(z[3][3], "D")
        self.assertEqual(z[3][6], "E")  # C stand in Spalte 6; D schreibt Spalte 3, der Cursor steht dann auf 4, zwei rechts = Spalte 6: E überschreibt C

    def test_zeile_loeschen_el_0_1_2(self):
        m = self.modell()
        m.einspeisen(b"abcdefghij\r\x1b[5C\x1b[0K")  # ab Cursor bis Ende löschen
        self.assertEqual(zeilen(m)[0], "abcde")
        m.einspeisen(b"\r\nabcdefghij\r\x1b[5C\x1b[1K")  # bis einschließlich Cursor löschen
        self.assertEqual(zeilen(m)[1].strip(), "ghij")
        m.einspeisen(b"\r\nabcdefghij\x1b[2K")  # ganze Zeile
        self.assertEqual(zeilen(m)[2], "")

    def test_bildschirm_loeschen_ed(self):
        m = self.modell()
        m.einspeisen(b"eins\r\nzwei\r\ndrei\r\n\x1b[2;1H\x1b[J")  # ab Cursor bis Ende
        self.assertEqual(zeilen(m)[:3], ["eins", "", ""])
        m.einspeisen(b"\x1b[2J")
        self.assertTrue(all(z == "" for z in zeilen(m)))

    def test_automatischer_umbruch_in_der_letzten_spalte(self):
        m = self.modell(4, 10)
        m.einspeisen(b"0123456789ab")
        self.assertEqual(zeilen(m)[:2], ["0123456789", "ab"])

    def test_umbruch_abgeschaltet_decawm(self):
        m = self.modell(4, 10)
        m.einspeisen(b"\x1b[?7l0123456789abc")
        self.assertEqual(zeilen(m)[0], "012345678c")  # alles Weitere überschreibt die letzte Spalte
        self.assertEqual(zeilen(m)[1], "")

    def test_scrollbereich_decstbm_und_zeile_einfuegen_loeschen(self):
        m = self.modell(6, 10)
        m.einspeisen(b"1\r\n2\r\n3\r\n4\r\n5\r\n6")
        m.einspeisen(b"\x1b[2;5r\x1b[5;1H\r\nneu")  # Bereich Zeilen 2 bis 5; Zeilenvorschub am unteren Rand scrollt nur den Bereich
        self.assertEqual(zeilen(m)[0], "1")
        self.assertEqual(zeilen(m)[5], "6")
        self.assertEqual(zeilen(m)[1:5], ["3", "4", "5", "neu"])
        m.einspeisen(b"\x1b[r\x1b[2;1H\x1b[L")  # Zeile einfügen an Zeile 2: Rest rutscht nach unten
        self.assertEqual(zeilen(m)[1], "")
        m.einspeisen(b"\x1b[M")  # Zeile löschen: wieder zurück
        self.assertEqual(zeilen(m)[1], "3")

    def test_tabulator_alle_acht_spalten(self):
        m = self.modell(3, 30)
        m.einspeisen(b"a\tb\t\tc")
        z = zeilen(m)[0]
        self.assertEqual((z.index("b"), z.index("c")), (8, 24))

    def test_cursor_sichern_und_wiederherstellen(self):
        m = self.modell()
        m.einspeisen(b"\x1b[3;4H\x1b7\x1b[1;1HX\x1b8Y")
        z = zeilen(m)
        self.assertEqual(z[0][0], "X")
        self.assertEqual(z[2][3], "Y")

    def test_fenstertitel_osc_wird_nicht_angezeigt(self):
        m = self.modell()
        m.einspeisen(b"\x1b]0;mein Titel\x07sichtbar\x1b]2;noch einer\x1b\\!")
        self.assertEqual(zeilen(m)[0], "sichtbar!")

    def test_rueckschritt_und_wagenruecklauf_ueberschreiben(self):
        m = self.modell()
        m.einspeisen(b"abc\x08\x08X\rZ")
        self.assertEqual(zeilen(m)[0], "ZXc")

    def test_umgekehrter_zeilenvorschub_am_oberen_rand_schiebt_nach_unten(self):
        m = self.modell(3, 10)
        m.einspeisen(b"eins\r\nzwei\r\ndrei\x1b[1;1H\x1bM")
        self.assertEqual(zeilen(m), ["", "eins", "zwei"])

    def test_linienzeichen_zeichensatz_dec_grafik(self):
        m = self.modell()
        m.einspeisen(b"\x1b(0lqqk\r\nx  x\r\nmqqj\x1b(B")
        self.assertEqual(zeilen(m)[:3], ["┌──┐", "│  │", "└──┘"])

    def test_utf8_bleibt_nach_dem_linienzeichensatz_erhalten(self):
        m = self.modell()
        m.einspeisen("\x1b(0q\x1b(B äöü ┌─┐ 日".encode())
        self.assertEqual(zeilen(m)[0], "─ äöü ┌─┐ 日")

    def test_umschalten_mit_shift_out_und_in(self):
        m = self.modell()
        m.einspeisen(b"\x1b)0\x0eqq\x0fq")  # G1 = Linienzeichen, SO schaltet auf G1, SI zurück auf G0 (ASCII)
        self.assertEqual(zeilen(m)[0], "──q")

    def test_unicode_breite_zeichen_und_kombinierende(self):
        m = self.modell(3, 12)
        m.einspeisen("日本áb".encode())  # zwei breite Zeichen (je 2 Zellen), a mit Akzent (kombinierend), b
        self.assertEqual(m.zelle(0, 0).zeichen, "日")
        self.assertTrue(m.zelle(0, 0).breit)
        import unicodedata
        self.assertEqual(unicodedata.normalize("NFC", m.zelle(0, 4).zeichen), "á")  # a mit kombinierendem Akzent bleibt in EINER Zelle
        self.assertEqual(m.zelle(0, 5).zeichen, "b")

    def test_inverse_und_zuruecksetzen_ueber_mehrere_zeilen(self):
        m = self.modell()
        m.einspeisen(b"\x1b[7mrev\x1b[27m norm\x1b[0m")
        rev, norm = m.zelle(0, 0), m.zelle(0, 5)
        self.assertEqual((rev.vordergrund, rev.hintergrund), (tm.STANDARD_BG, tm.STANDARD_FG))
        self.assertEqual((norm.vordergrund, norm.hintergrund), (tm.STANDARD_FG, tm.STANDARD_BG))

    def test_verlauf_zaehlt_genau_die_hinausgescrollten_zeilen(self):
        m = self.modell(5, 10)
        m.einspeisen(b"".join(b"%d\r\n" % i for i in range(20)))  # 20 Zeilen + leere Cursorzeile: 21 Zeilen, 5 sichtbar
        self.assertEqual(m.verlauf_laenge(), 16)
        m.zu_versatz(m.verlauf_laenge())
        self.assertEqual([z.strip() for z in zeilen(m)], ["0", "1", "2", "3", "4"])

    def test_groesse_verkleinern_haelt_den_unteren_teil_und_vergroessern_ergaenzt_leer(self):
        m = self.modell(6, 20)
        m.einspeisen(b"a\r\nb\r\nc\r\nd\r\ne\r\nf")
        m.groesse_setzen(3, 20)
        self.assertEqual(zeilen(m), ["d", "e", "f"])  # die jüngsten Zeilen bleiben sichtbar
        m.groesse_setzen(5, 20)
        self.assertEqual(len(zeilen(m)), 5)
        self.assertIn("f", zeilen(m))


if __name__ == "__main__":
    unittest.main()
