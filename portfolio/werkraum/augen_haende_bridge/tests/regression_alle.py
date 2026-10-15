"""Alle Tests des Projekts in einem Lauf: grün heißt, dass nur die bereits bekannten, von der Umgebung abhängigen Fehlschläge übrig bleiben.

Die drei bekannten Fehlschläge stehen in `test_terminal_adapter.py` (sie prüfen eine laufende KDE-Konsole des VPS und scheitern ohne sie, unabhängig von der Bridge).
Ein neuer Fehlschlag, ein neuer Fehler oder ein zusätzlicher, nicht aufgeführter Name macht den Lauf rot. Tests, die einen privaten Xvfb brauchen, werden hier übersprungen
(sie laufen in den Gates unter `xvfb-run`).
"""

import os
import sys
import unittest
from pathlib import Path

BEKANNT = {
    "test_terminal_adapter.TerminalAdapterTests.test_probe_command_echo_does_not_contain_full_marker",
    "test_terminal_adapter.TerminalAdapterTests.test_discovery_reads_real_session_identity_and_scrollback",
    "test_terminal_adapter.TerminalAdapterTests.test_registry_keeps_static_targets_and_marks_discovered_terminal_real",
}


def kurzname(test) -> str:
    teile = test.id().split(".")
    return ".".join(t for t in teile if t != "tests")


def main() -> int:
    wurzel = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(wurzel / "src"), str(wurzel / "tests"), str(wurzel)]
    os.environ.pop("BRIDGE_TEST_XVFB", None)
    suite = unittest.defaultTestLoader.discover(str(wurzel / "tests"), pattern="test_*.py", top_level_dir=str(wurzel / "tests"))
    ergebnis = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w")).run(suite)
    fehlgeschlagen = {kurzname(t) for t, _ in ergebnis.failures + ergebnis.errors}
    neu = sorted(fehlgeschlagen - BEKANNT)
    print(f"{ergebnis.testsRun} Tests, {len(ergebnis.skipped)} übersprungen, {len(fehlgeschlagen & BEKANNT)} bekannte Fehlschläge, {len(neu)} neue")
    for name in neu:
        print("NEU ROT:", name)
    if neu:
        for t, text in ergebnis.failures + ergebnis.errors:
            if kurzname(t) in neu:
                print(text[-1500:])
        return 1
    print("REGRESSION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
