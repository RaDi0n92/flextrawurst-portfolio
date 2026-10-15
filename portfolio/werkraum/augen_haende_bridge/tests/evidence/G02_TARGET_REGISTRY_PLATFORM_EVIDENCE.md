# G02 — Plattformneutraler TargetRegistry-Kern

**STAGE:** G02 target registry platform boundary
**DATE:** 2026-09-20
**OUTCOME:** PASS (Core/Browser slice), native Windows remains NOT_PROVEN

## FocusContract

- **Goal:** Die Windows-EXE darf beim Erzeugen des TargetRegistry keinen lokalen Linux-/KDE-Discoverypfad starten.
- **Next stone:** Stabile Terminal-Identität und getrennte UI-Slot-Abbildung vor jeder echten Terminal-Eingabe.
- **Preserved anchors:** `win-desktop` als Default, `kde-1`/`kde-2`, synthetischer `terminal-1`-Fallback, explizites `terminal-probe`, read-only-Scannergrenze.
- **Forbidden drift:** Kein qdbus-Aufruf auf Windows, kein stilles Umschreiben eines ausgewählten Ziels, kein Playwright- oder Linux-Beleg als Windows-Nativbeweis.

## Implemented

- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py` wählt auf `os.name == "nt"` den expliziten `PlatformUnavailableAdapter`; der lokale Windows-Client übernimmt dadurch keine KDE-Erkennung.
- `refresh_terminals()` entfernt nur zuvor entdeckte Sessions, stellt den synthetischen Fallback wieder her, bewahrt `terminal-probe` und setzt eine verschwundene Auswahl fail-closed auf `win-desktop` zurück.
- Der Adapter wird per `is not None` übernommen; ein absichtlich falsy Test-Double kann den Sicherheitsentscheid nicht umgehen.

## Core evidence

- `PYTHONPATH=src python3 -m unittest discover -s tests -v` → **80 Tests OK**.
- `python3 -m py_compile src/augen_haende_bridge/target_registry.py client_windows/overlay_app.py src/augen_haende_bridge/windows_scanner.py` → **PASS**.
- Tests decken Windows-Konstruktion ohne `shutil.which`/`subprocess.run`, stale Auswahl, synthetischen Fallback und Erhalt von `terminal-probe` ab.

## Playwright evidence

- `/root/werkraum/augen_haende_bridge/tests/transport_playwright_proof.py` → **PASS**, lokaler Transport mit sichtbarem Browser-Witness.
- `/root/werkraum/augen_haende_bridge/tests/reference_surface_proof.py` → **PASS**, Referenz-Surface mit sichtbarer Scanner-/Target-Interaktion.
- Diese beiden Belege beweisen browserbedienbare lokale Pfade. Sie ersetzen ausdrücklich keinen Windows-EXE-, Win32-, Capture-, Hit-Test- oder nativen Eingabebeleg.

## Independent review

- Claude Opus: **approve with required follow-ups**. Bestätigt den Plattformentscheid und den Fallback-/Probe-Erhalt; fordert stabile Session-Identität, einen echten Live-Refresh-Aufruf und zusätzliche Integrations-Tests.
- Gemini/Antigravity: Der ursprüngliche Cross-Platform-Hinweis war **valide**. Zwei nachträgliche behauptete `inspect`-Signaturfehler sind durch Diff und 80 lokale Tests widerlegt; `TargetRegistry.refresh_terminals()` ruft `inspect` nicht auf.
- ChatGPT/Codex-with-ChatGPT: **nicht als Review behauptet**. Der lokale Connector-Doctor war erfolgreich, aber aktuell existiert noch keine gebundene ChatGPT-Projektsession (`session: null`, `projectReady: false`); daher gab es keinen echten ChatGPT-Diff-Review.

## Open boundary

Die Registry verwendet für entdeckte Konsole-Sessions weiterhin die historischen Slot-IDs `terminal-1..N`. Vor Input/Binding muss G03 die Identität aus `service + session_path` stabilisieren und die vier sichtbaren Slots separat abbilden. Außerdem muss der Windows-Overlay-Refresh an den echten Bridge-Readback angeschlossen werden; Konstruktion allein ist noch kein Live-Scanner.
