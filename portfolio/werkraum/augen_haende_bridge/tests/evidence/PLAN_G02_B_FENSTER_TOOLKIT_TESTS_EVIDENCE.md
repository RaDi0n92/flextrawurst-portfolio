# PLAN-G02 Zyklus B: Fenster-Toolkit-Tests — Evidence

Datum: 2026-09-24. Ausgangslage: `virtuellerdesktop1` war 3-4 Tage vor diesem Zyklus abgestürzt und musste über
`anthropic_claude` wiederhergestellt werden; diese Sitzung knüpft an den zuletzt dokumentierten Stand
(`0682b9c5c3`, PLAN-G02-A) und den danach ungecommittet gebliebenen `koerper/`-Stand an.

## Fund bei der Wiederaufnahme

Nach `0682b9c5c3` (2026-09-21 00:04) lag, mit Zeitstempeln bis 00:22 Uhr desselben Tages, bereits ein vollständiges
neues Modul `src/augen_haende_bridge/koerper/` im Arbeitsbaum: `win32.py`, `fenster.py`, `menue.py`, `stil.py`,
`terminal_fenster.py`, `terminal_modell.py` sowie `tests/test_koerper_terminal_modell.py`. Das ist Stein 3
(Win32-Fenster-Toolkit) und Stein 4 (Terminalfenster) aus der vorherigen Zyklusplanung, bereits als lauffähiger
Code, aber ungetestet (außer `terminal_modell.py`) und ungecommittet.

Das wurde zuerst per Sicherheits-Commit `341708d702` gesichert (zusammen mit vier `docs/opus/`-Advisory-Notizen,
ebenfalls ungecommittet vorgefunden), bevor an diesem Zyklus weitergearbeitet wurde.

## Umgebung

Der `venv` unter `/root/werkraum/.venv` (in diesem Container sichtbar als `/vps_root/werkraum_venv`) zeigte per
`pyvenv.cfg` auf `/usr/bin/python3` — das ist nach der Wiederherstellung des Containers jetzt Python 3.14 statt
der ursprünglichen 3.12, wodurch `pyte` und `websockets` fehlten. Beide wurden neu installiert
(`pyte==0.8.2`, `websockets==16.1.1`, letzteres passend zum in `pyproject.toml` gepinnten Wert). Nebenwirkung: ein
zuvor installiertes `websockets 17.1` wurde dabei systemweit auf 16.1.1 zurückgesetzt.

## Build-Schritt

Fünf neue Testdateien für den Win32-Körper-Teil geschrieben, keine Produktionsdatei geändert:

- `tests/test_koerper_win32.py` — reine Helfer (`rgb`, `loword`/`hiword`, `signed_loword`/`signed_hiword`,
  `make_lparam`) und die Linux/Windows-Weiche (`WINDOWS`, `require_windows()`, `last_error()`).
- `tests/test_koerper_stil.py` — Deckkraft-Umrechnung (inkl. der dokumentierten 1-%-Toleranz in `naechste_stufe`),
  Kürzel-Bildung, Farbaufhellung.
- `tests/test_koerper_menue.py` — Windows-Gating (Popup-Menü, Zwischenablage lesen/schreiben verlangen alle
  `require_windows()`, da keine injizierbare Fake-API existiert wie beim Fensterscanner).
- `tests/test_koerper_fenster.py` — `Fenster.nachricht()` und der modulweite `_wndproc`-Dispatcher, per
  `object.__new__` ohne echten Konstruktor gebaut und mit Mock-Handlern bestückt; prüft die komplette
  Nachrichtenverteilungstabelle (Maus, Tastatur, Timer, Fokus, Hotkey, NCHITTEST, DPI) sowie das
  entstehende-Fenster/Ausnahme-/DefWindowProcW-Verhalten des Dispatchers.
- `tests/test_koerper_terminal_fenster.py` — Geometrie (Gitter-, Knopf-, Scanner-Rechtecke), Trefferprüfung an
  Kanten/Ecken/Titelzeile, Maus-Auswahl-Drag im Zeichengitter, Knopf-Routing (schließen/verbergen/deckkraft/scanner
  inkl. Wegzieh-Abbruch), Mausrad (Deckkraft über der Titelzeile vs. Verlauf über dem Gitter), Tastatur-Routing
  (AltGr wird nicht als Strg+Alt gewertet, Strg+Umschalt+C/V und Umschalt+Einfügen, unbekannte Tasten), WM_CHAR
  inkl. UTF-16-Ersatzpaar-Zusammensetzung, Zwischenablage (`kopieren`/`einfuegen` mit gepatchten Menü-Funktionen),
  Größen-/Zeichen-/Cursor-Timer-Routing, `bei_nachricht` (GETMINMAXINFO, MOUSEACTIVATE, MOVE, SETCURSOR).

104 neue Tests, alle grün unter Linux.

## Testergebnis

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 287 tests (Ausgangsstand 183)
FAILED (failures=2, errors=1)
```

Die drei Fehlschläge liegen unverändert in `test_terminal_adapter.py`
(`test_probe_command_echo_does_not_contain_full_marker`,
`test_discovery_reads_real_session_identity_and_scrollback`,
`test_registry_keeps_static_targets_and_marks_discovered_terminal_real`) — Dateidatum 20.09., also vor diesem
Zyklus und vor dem Absturz. Sie hängen an der Erkennung einer echten laufenden Terminalsitzung, die in dieser
Bash-Werkzeugumgebung ohne interaktives TTY vermutlich nicht wie erwartet auffindbar ist; kein Bezug zu `koerper/`.

Zusätzlich: `python3 tests/pruefe_koerper.py` — **PASS** (0 von 4 beanstandeten Dingen), prüft aber weiterhin
`client_windows/overlay_app.py` (den alten Tk-Bestand), nicht den neuen `koerper/`-Körper. Das Tor auf den neuen
Körper umzustellen ist weiterhin ein späterer, offener Schritt (siehe Bauprotokoll/Stein 7) und wurde in diesem
Zyklus bewusst nicht angefasst, da `koerper/` noch keine lauffähige Gesamtfläche ist.

## Ergebnis

**PASS** für die reine Logik unter Linux (Geometrie, Trefferprüfung, Tastatur-/Zeichen-Kodierung, Auswahl- und
Knopf-Zustandsmaschine, Nachrichtenverteilung). **UNKNOWN** für alles, was echtes Windows- oder Wine-Fensterverhalten
braucht (tatsächliche Pixel, echte GDI-/DPI-Aufrufe, echte Zwischenablage) — das bleibt ein späterer, nativer Beleg.
Kein Windows-Overlay wurde in diesem Zyklus gestartet oder behauptet.

## Was als Nächstes fällig ist

Kamera- und Mikrofon-Module sowie das Raute-Fenster (Banner 3,3 s, Ticker 6,6 s, Chat) für den ersten Körper bauen,
danach das Terminalfenster real an den Fensterscanner (`windows_scanner.py`)/das Relay anschließen und den Körper
einmal unter Wine tatsächlich starten.
