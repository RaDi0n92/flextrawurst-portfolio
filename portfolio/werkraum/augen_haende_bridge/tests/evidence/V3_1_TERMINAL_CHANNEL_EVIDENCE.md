EVIDENCE_VERSION: 1
STAGE: V3.1 terminal channel
OUTCOME: PASS

## Redteam-Korrektur 2026-09-20

Der erste Bericht war bei der Markerform zu großzügig: Ein ungeteiltes
`printf-marker`-Kommando konnte den Marker bereits im PTY-Command-Echo
enthalten. Das wurde in beiden Probewegen korrigiert. Die aktuelle Form
`printf-split-marker` teilt den sicheren Marker in zwei Shell-Argumente; der
vollständige Marker kann damit nicht aus dem bloßen Command-Echo stammen.
Zusätzlich wartet der Readback-Loop jetzt auf beide Zeugen (`raw PTY` **und**
`Konsole-Scrollback`) statt bei nur einem Treffer vorzeitig abzubrechen.

## Gegenstand

Geprüft wurde der neue Terminalkanal unter
`/root/werkraum/augen_haende_bridge/` mit einem isolierten, von der Bridge
besessenen Konsole-/PTY-Ziel. Die laufenden Original-Terminals wurden nicht
beschrieben oder verändert.

## Belegkette

- `session_owned`: PASS — der isolierte Prozess und seine Konsole-Session
  wurden durch `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py`
  gestartet und mit PID/Session-Referenz registriert.
- `pty_connected`: PASS — der Controller meldete die verbundene
  `pty-controller:unix-socket`-Verbindung zurück.
- `vt_output_received`: PASS — rohe PTY-Bytes wurden über den Controller
  gelesen; der Lauf meldete `raw_output_bytes: 68` nach dem Marker.
- `rendered`: PASS — die native Konsole-Rücklese
  `konsole-dbus:getAllDisplayedText` war verfügbar.
- `input_accepted`: PASS — der Bridge-Core akzeptierte ausschließlich den
  gebundenen Terminal-Request mit Lease.
- `input_delivered`: PASS — die markierte Eingabe wurde über
  `pty-controller:unix-socket` mit der Form `printf-split-marker` zugestellt;
  ein Unit-Test prüft, dass der vollständige Marker nicht im Command-Echo steht.
- `input_echoed`: PASS — `AUGEN_HAENDE_PROBE_0001` wurde im rohen PTY-Output
  wiedergefunden.
- `state_observed`: PASS — derselbe Marker wurde im nativen Konsole-Scrollback
  wiedergefunden.
- `audited`: PASS — `action.delivered`, `action.echoed`, `action.observed`
  und `action.audited` wurden im Core-Audit gelesen; der Terminalkanal trug die
  Audit-Sequenz zurück.

## Ausgeführte Prüfungen

- `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 62 Tests grün.
- `PYTHONPATH=src python3 tests/playwright_proof.py` — sichtbarer
  B4.5b-Probeweg mit Create, Safe Marker, Rücklese und Close grün.
- `PYTHONPATH=src python3 tests/playwright_guardian.py` — Guardian-Regression
  grün; Browserbeweis bleibt ausdrücklich Browserbeweis.

## Nicht durch diesen Bericht belegt

- Keine Windows-native EXE-Abnahme.
- Kein Windows-ConPTY, kein Win32-Hit-Test und kein nativer Windows-Not-Aus.
- Keine Eingabe in Daniels laufende Original-Agentensession.
- Kein vollständiger VT-Renderer mit Resize-/Alternate-Screen-Abnahme.
