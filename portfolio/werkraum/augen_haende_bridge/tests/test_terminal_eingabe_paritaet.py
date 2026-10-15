"""Eingaben (R019): Sondertasten, Zeichen, Einfügen und Größenänderung kommen genau einmal und richtig an, durch das echte PTY des Starters.

Der Empfänger ist ein kleines Programm im Rohmodus, kein Shell-Prompt: es meldet jedes gelesene Byte als Hex (so trifft keine Probe einen laufenden
Agenten oder eine Shell). Die erwarteten Folgen sind von Hand nach xterm geschrieben, nicht aus dem Code abgeleitet."""
import base64
import time
import unittest

from augen_haende_bridge.koerper import terminal_modell as tm
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.anwendung import eingabe_stuecke
from test_terminal_launcher import LauncherCase, b64, entry, ev, wait_for

EMPFAENGER = r'''
import os, signal, tty
tty.setraw(0)
def winch(*_):
    spalten, zeilen = os.get_terminal_size(0)
    os.write(1, ("SIZE %d %d\n" % (zeilen, spalten)).encode())
signal.signal(signal.SIGWINCH, winch)
os.write(1, b"BEREIT\n")
while True:
    d = os.read(0, 65536)
    if not d:
        break
    os.write(1, ("HEX " + d.hex() + "\n").encode())
'''

# (Name, vk, Umschalt, Alt, Strg, erwartete xterm-Folge)
TASTEN = [
    ("Pfeil hoch", w.VK_UP, False, False, False, b"\x1b[A"),
    ("Pfeil runter", w.VK_DOWN, False, False, False, b"\x1b[B"),
    ("Pfeil rechts", w.VK_RIGHT, False, False, False, b"\x1b[C"),
    ("Pfeil links", w.VK_LEFT, False, False, False, b"\x1b[D"),
    ("Pos1", w.VK_HOME, False, False, False, b"\x1b[H"),
    ("Ende", w.VK_END, False, False, False, b"\x1b[F"),
    ("Einfg", w.VK_INSERT, False, False, False, b"\x1b[2~"),
    ("Entf", w.VK_DELETE, False, False, False, b"\x1b[3~"),
    ("Bild hoch", w.VK_PRIOR, False, False, False, b"\x1b[5~"),
    ("Bild runter", w.VK_NEXT, False, False, False, b"\x1b[6~"),
    ("F1", w.VK_F1, False, False, False, b"\x1bOP"),
    ("F4", w.VK_F1 + 3, False, False, False, b"\x1bOS"),
    ("F5", w.VK_F1 + 4, False, False, False, b"\x1b[15~"),
    ("F10", w.VK_F1 + 9, False, False, False, b"\x1b[21~"),
    ("F11", w.VK_F1 + 10, False, False, False, b"\x1b[23~"),
    ("F12", w.VK_F12, False, False, False, b"\x1b[24~"),
    ("Strg+Pfeil hoch", w.VK_UP, False, False, True, b"\x1b[1;5A"),
    ("Alt+Pfeil links", w.VK_LEFT, False, True, False, b"\x1b[1;3D"),
    ("Umschalt+F5", w.VK_F1 + 4, True, False, False, b"\x1b[15;2~"),
    ("Umschalt+Tab", w.VK_TAB, True, False, False, b"\x1b[Z"),
]


class TastenfolgenTests(unittest.TestCase):
    def test_sondertasten_entsprechen_xterm(self):
        for name, vk, umschalt, alt, strg, erwartet in TASTEN:
            with self.subTest(name):
                self.assertEqual(tm.taste_zu_bytes(vk, umschalt=umschalt, alt=alt, strg=strg), erwartet)

    def test_anwendungs_cursor_modus_nutzt_ss3(self):
        self.assertEqual(tm.taste_zu_bytes(w.VK_UP, anwendungs_cursor=True), b"\x1bOA")

    def test_zeichen_enter_ruecktaste_strg_c_esc_tab_und_alt(self):
        self.assertEqual(tm.zeichen_zu_bytes(0x0D), b"\r")
        self.assertEqual(tm.zeichen_zu_bytes(0x08), b"\x7f")  # xterm schickt DEL für die Rücktaste
        self.assertEqual(tm.zeichen_zu_bytes(0x03), b"\x03")  # Strg+C
        self.assertEqual(tm.zeichen_zu_bytes(0x1B), b"\x1b")
        self.assertEqual(tm.zeichen_zu_bytes(0x09), b"\t")
        self.assertEqual(tm.zeichen_zu_bytes(ord("x"), alt=True), b"\x1bx")
        self.assertEqual(tm.zeichen_zu_bytes(ord("ä")), "ä".encode())

    def test_einfuegen_mit_und_ohne_eingeklammerten_modus(self):
        self.assertEqual(tm.einfuegen_zu_bytes("a\r\nb\nc", True), b"\x1b[200~a\rb\rc\x1b[201~")
        self.assertEqual(tm.einfuegen_zu_bytes("a\nb", False), b"a\rb")


class EingabeDurchsPtyTests(LauncherCase):
    def setUp(self):
        super().setUp()
        import os
        self.skript = os.path.join(str(self.runtime_dir), "empfaenger.py")
        with open(self.skript, "w", encoding="utf-8") as f:
            f.write(EMPFAENGER)
        self.make(entry("empfaenger", f"python3 -u {self.skript}"))
        self.tid = self.start("empfaenger")
        self.assertTrue(wait_for(lambda: "BEREIT" in self.runtime.output(self.tid)))

    def empfangen(self) -> bytes:
        daten = b""
        for zeile in self.runtime.output(self.tid).split("\n")[:-1]:  # nur vollständige Zeilen: die letzte kann noch ankommen
            if zeile.startswith("HEX "):
                daten += bytes.fromhex(zeile[4:].strip())
        return daten

    def senden(self, daten: bytes):
        for stueck in eingabe_stuecke(daten):  # wie die Bridge: in Stücken bis MAX_TERMINAL_INPUT
            self.launcher.handle(ev("terminal_input", {"terminal_id": self.tid, "data": b64(stueck)}))

    def test_alle_sondertasten_kommen_genau_einmal_und_in_der_reihenfolge_an(self):
        gesendet = b""
        for name, vk, umschalt, alt, strg, erwartet in TASTEN:
            daten = tm.taste_zu_bytes(vk, umschalt=umschalt, alt=alt, strg=strg)
            self.senden(daten)
            gesendet += erwartet
        self.assertTrue(wait_for(lambda: self.empfangen() == gesendet, timeout=10), self.empfangen())
        time.sleep(0.5)
        self.assertEqual(self.empfangen(), gesendet)  # nichts kommt nachträglich doppelt an

    def test_zeichen_und_einfuegen_kommen_unveraendert_an(self):
        erwartet = b"\r\x7f\x03\x1b\t\x1bx" + "äöü€".encode() + b"\x1b[200~zeile1\rzeile2\x1b[201~"
        for code, alt in ((0x0D, False), (0x08, False), (0x03, False), (0x1B, False), (0x09, False), (ord("x"), True)):
            self.senden(tm.zeichen_zu_bytes(code, alt=alt))
        self.senden("äöü€".encode())
        self.senden(tm.einfuegen_zu_bytes("zeile1\nzeile2", True))
        self.assertTrue(wait_for(lambda: self.empfangen() == erwartet, timeout=10), self.empfangen())

    def test_langes_einfuegen_in_stuecken_kommt_vollstaendig_und_in_ordnung_an(self):
        text = "".join(f"zeile {i:05d} äöü\n" for i in range(2500))  # etwa 50 KB
        daten = tm.einfuegen_zu_bytes(text, True)
        self.senden(daten)
        self.assertTrue(wait_for(lambda: len(self.empfangen()) >= len(daten), timeout=20))
        time.sleep(0.5)
        self.assertEqual(self.empfangen(), daten)

    def test_groessenaenderung_kommt_an_und_wird_zurueckgelesen(self):
        self.launcher.handle(ev("terminal_resize", {"terminal_id": self.tid, "rows": 40, "cols": 120}))
        self.assertTrue(wait_for(lambda: "SIZE 40 120" in self.runtime.output(self.tid)), self.runtime.output(self.tid))
        session = self.launcher.sessions[self.tid]
        self.assertEqual((session.rows, session.cols), (40, 120))
        self.launcher.handle(ev("terminal_resize", {"terminal_id": self.tid, "rows": 20, "cols": 70}))
        self.assertTrue(wait_for(lambda: "SIZE 20 70" in self.runtime.output(self.tid)))

    def test_eingabe_fuer_eine_andere_sitzung_trifft_diese_nicht(self):
        self.launcher.handle(ev("terminal_input", {"terminal_id": "t-unbekannt", "data": b64(b"X")}))
        time.sleep(0.3)
        self.assertEqual(self.empfangen(), b"")


if __name__ == "__main__":
    unittest.main()
