# G01 — Plattform- und Voraussetzungen-Nachweis

Datum: 2026-09-19  
Pfad: `/root/werkraum/augen_haende_bridge/`  
Scope: side-effect-free Preflight auf dem aktuellen VPS

## Ausführung

```text
PYTHONPATH=src python3 -m augen_haende_bridge.preflight
```

## Ergebnis

```text
AVAILABLE    host.os: Linux 6.8.0-138-generic (x86_64)
NOT_PROVEN   windows.native_runner: current host is not Windows; native EXE launch still requires a Windows run
NOT_PROVEN   windows.packager.pyinstaller: PyInstaller is not installed on this host
AVAILABLE    native.overlay.entrypoint: Tkinter import is available; actual native window behavior still needs a display
AVAILABLE    kde.live_session: qdbus=/usr/bin/qdbus6, display=:1, desktop=KDE
NOT_PROVEN   original.terminal.readback: requires the live terminal/session selected by Daniel; no process is attached by preflight
AVAILABLE    transport.websocket_dependency: Python websockets module is importable
NOT_PROVEN   native.window.evidence: requires a real Windows desktop capture/click/focus/DPI/stop run
```

## Bedeutung

- `AVAILABLE` ist ein lokaler Voraussetzungenbeleg, keine Produktabnahme.
- `NOT_PROVEN` bleibt als offene G01-Bedingung sichtbar; daraus wird kein Erfolg konstruiert.
- G01 ist deshalb noch nicht abgeschlossen: Windows-Native-Build und native Overlay-Interaktion brauchen noch gezielte Live-Proben. Die lokale read-only-Rücklese echter KDE-Konsole-Sessions ist inzwischen bewiesen.

## Zusätzlicher Live-Readback

Der vorhandene read-only-Konsole-Adapter wurde gegen die aktuelle KDE-Session
ausgeführt. Er entdeckte vier echte Sessions und las `getAllDisplayedText` zurück:

```text
DISCOVERED=4
1: org.kde.konsole-1060933 /Sessions/1 session_pid=1060977 foreground_pid=1060992 chars=1106 status=observed
2: org.kde.konsole-396627  /Sessions/1 session_pid=396669 foreground_pid=398997 chars=360 status=observed
3: org.kde.konsole-396725  /Sessions/1 session_pid=396766 foreground_pid=1157351 chars=982 status=observed
4: org.kde.konsole-396779  /Sessions/1 session_pid=396822 foreground_pid=396848 chars=1084 status=observed
```

Das beweist die lokale read-only-Rücklese aus echten KDE-Konsole-Fenstern.
Es beweist weder Windows-Overlay-Zugriff noch Eingabe in diese laufenden
Sessions; beides bleibt absichtlich eine getrennte Freigabe- und Beweisstufe.

## Tests

- `PYTHONPATH=src python3 -m unittest tests.test_preflight -v`: 2 Tests grün.
- Vollständige vorhandene unittest-Menge: 37 Tests grün.
- Die Transport-Playwright-Probe bleibt der vorhandene Beleg unter `/root/werkraum/augen_haende_bridge/tests/evidence/TRANSPORT_LOCAL_PLAYWRIGHT_EVIDENCE.md`; dieser Preflight behauptet keinen zusätzlichen Browser- oder Windows-Beleg.
