"""Tests für koerper/scanner_anbindung.py: Scanner-Knopf → Auswahl → read-only Binding mit Rücklese.

Benutzt die echten Klassen `WindowsWindowScanner`, `WindowsScreenCapture`, `read_only_binding` und `HarnessRun`
mit einer kleinen Fake-Win32-API (wie `test_windows_scanner.py`/`test_windows_capture.py`).
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from augen_haende_bridge.harness import SCANNER_PROOF_SEQUENCE
from augen_haende_bridge.koerper.scanner_anbindung import (
    Bindung,
    eintrag_zu_ziel,
    mache_scanner_callback,
    snapshot_zu_eintraegen,
)
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster
from augen_haende_bridge.windows_capture import WindowsScreenCapture
from augen_haende_bridge.windows_scanner import WindowInfo, WindowsWindowScanner


class FakeWindowApi:
    def virtual_screen_rect(self):
        return (0, 0, 1920, 1080)

    def enumerate_windows(self):
        return [WindowInfo(hwnd=101, title="Blender", class_name="X", rect=(10, 10, 810, 610),
                           process_id=501, process_path="C:\\Blender\\blender.exe")]


class FakeCaptureApi:
    def virtual_screen_rect(self):
        return (0, 0, 4, 2)

    def capture_bgra(self, rect):
        return bytes(range(32))


def _terminal() -> TerminalFenster:
    t = object.__new__(TerminalFenster)
    t.hwnd = 999
    t.name = "codex"
    t.ziel_gebunden = False
    t.setze_ziel = Mock()
    return t


def _callback(terminal, gewaehlt: int, **kwargs):
    ergebnisse = {"bindung": None, "lauf": None}
    callback = mache_scanner_callback(
        terminal, scanner=WindowsWindowScanner(FakeWindowApi()), capture=WindowsScreenCapture(FakeCaptureApi()),
        agent_id="codex", menue_anzeigen=Mock(return_value=gewaehlt),
        gebunden=lambda b: ergebnisse.__setitem__("bindung", b),
        lauf_beendet=lambda lauf: ergebnisse.__setitem__("lauf", lauf), **kwargs)
    return callback, ergebnisse


class ReineFunktionenTests(unittest.TestCase):
    def test_desktop_und_fenster_werden_in_scan_reihenfolge_nummeriert(self) -> None:
        snapshot = WindowsWindowScanner(FakeWindowApi()).scan(frame_ref="frame://1", frame_hash="sha256:1")
        self.assertEqual(snapshot_zu_eintraegen(snapshot), [(1, "Windows kompletter Desktop", 0), (2, "Blender", 0)])

    def test_eintrag_zu_ziel(self) -> None:
        snapshot = WindowsWindowScanner(FakeWindowApi()).scan(frame_ref="frame://1", frame_hash="sha256:1")
        self.assertIsNone(eintrag_zu_ziel(snapshot, 0))
        self.assertIsNone(eintrag_zu_ziel(snapshot, 99))
        self.assertEqual(eintrag_zu_ziel(snapshot, 2), ("windows:window:101", "Blender"))


class BindungTests(unittest.TestCase):
    def test_auswahl_fuehrt_die_scanner_beweiskette_bis_zur_ruecklese(self) -> None:
        terminal = _terminal()
        callback, ergebnisse = _callback(terminal, 2)
        callback(300, 400)
        lauf = ergebnisse["lauf"]
        self.assertEqual([p for p in SCANNER_PROOF_SEQUENCE if p in lauf.proofs], list(SCANNER_PROOF_SEQUENCE[:7]))
        self.assertNotIn("PRE_ACTION_RESCAN", lauf.proofs)  # keine Aktion im ersten Körper
        terminal.setze_ziel.assert_called_once_with("Ziel: Blender", True)

    def test_die_bindung_ist_nur_beobachtend_und_traegt_generation_und_frame(self) -> None:
        callback, ergebnisse = _callback(_terminal(), 2)
        callback(0, 0)
        bindung: Bindung = ergebnisse["bindung"]
        self.assertEqual(bindung.binding.target_id, "windows:window:101")
        self.assertEqual(bindung.binding.agent_id, "codex")
        self.assertEqual({c.value for c in bindung.binding.capabilities}, {"observe"})
        self.assertEqual(bindung.binding.frame_hash, bindung.frame.frame_hash)
        self.assertEqual(bindung.item.rect, (10, 10, 810, 610))

    def test_abbruch_bindet_nichts_und_laesst_das_ziel_stehen(self) -> None:
        terminal = _terminal()
        callback, ergebnisse = _callback(terminal, 0)
        callback(0, 0)
        terminal.setze_ziel.assert_not_called()
        self.assertIsNone(ergebnisse["bindung"])
        self.assertNotIn("TARGET_SELECTED", ergebnisse["lauf"].proofs)

    def test_nicht_bindbares_ziel_meldet_den_grund_und_bleibt_ungebunden(self) -> None:
        terminal = _terminal()
        scanner = WindowsWindowScanner(None)  # kein Win32: Desktop nur als unavailable im Scan
        callback = mache_scanner_callback(terminal, scanner=scanner, capture=WindowsScreenCapture(FakeCaptureApi()),
                                          menue_anzeigen=Mock(return_value=1))
        callback(0, 0)
        text, gebunden = terminal.setze_ziel.call_args.args
        self.assertIn("nicht bindbar", text)
        self.assertIn("target_unavailable", text)
        self.assertFalse(gebunden)

    def test_fehlende_aufnahme_wird_sichtbar_statt_still_zu_scheitern(self) -> None:
        terminal = _terminal()
        callback = mache_scanner_callback(terminal, scanner=WindowsWindowScanner(FakeWindowApi()),
                                          capture=WindowsScreenCapture(None), menue_anzeigen=Mock(return_value=2))
        callback(0, 0)
        text, gebunden = terminal.setze_ziel.call_args.args
        self.assertIn("keine Aufnahme", text)
        self.assertFalse(gebunden)

    def test_gebundenes_ziel_bietet_bindung_loesen_an_und_loest(self) -> None:
        t = _terminal()
        t.ziel_gebunden = True
        t.ziel_text = "Ziel: Blender"
        geloest = []
        menue = Mock(return_value=3)  # Eintrag 1 = Desktop, 2 = Blender, 3 = „Bindung lösen“
        callback = mache_scanner_callback(
            t, scanner=WindowsWindowScanner(FakeWindowApi()), capture=WindowsScreenCapture(FakeCaptureApi()), agent_id="codex",
            menue_anzeigen=menue, geloest=lambda: geloest.append(1))
        callback(5, 5)
        eintraege = menue.call_args.args[1]
        self.assertEqual(eintraege[-1][1], "Bindung lösen (zurück zu ungebunden)")
        t.setze_ziel.assert_called_with("Ziel: Desktop (ungebunden)", False)
        self.assertEqual(geloest, [1])

    def test_ungebundenes_ziel_bietet_kein_loesen_an(self) -> None:
        t = _terminal()
        menue = Mock(return_value=0)
        callback = mache_scanner_callback(
            t, scanner=WindowsWindowScanner(FakeWindowApi()), capture=WindowsScreenCapture(FakeCaptureApi()), agent_id="codex",
            menue_anzeigen=menue)
        callback(5, 5)
        self.assertFalse(any(e and "lösen" in e[1] for e in menue.call_args.args[1]))

    def test_jeder_knopfdruck_scannt_neu(self) -> None:
        terminal = _terminal()
        scanner = WindowsWindowScanner(FakeWindowApi())
        capture = WindowsScreenCapture(FakeCaptureApi())
        scanner.scan = Mock(wraps=scanner.scan)
        capture.capture = Mock(wraps=capture.capture)
        callback = mache_scanner_callback(terminal, scanner=scanner, capture=capture, menue_anzeigen=Mock(return_value=1))
        callback(0, 0)
        callback(0, 0)
        self.assertEqual(capture.capture.call_count, 2)
        self.assertEqual(scanner.scan.call_count, 2)


if __name__ == "__main__":
    unittest.main()
