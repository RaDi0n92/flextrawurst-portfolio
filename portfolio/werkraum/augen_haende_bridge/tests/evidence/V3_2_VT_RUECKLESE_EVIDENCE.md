EVIDENCE_VERSION: 1
STAGE: V3.2 VT readback
OUTCOME: PASS

## Gegenstand

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py`
liest den echten rohen PTY-Strom des isolierten Probe-Terminals. Die native
Konsole-Rücklese bleibt separat und wird nicht durch diesen Reader ersetzt.

## Belege

- Text/Cursor/SGR: PASS — Unit-Test liest `hello`, positioniert `red` in Zeile
  2/Spalte 3 und bewahrt SGR 31.
- Alternate Screen: PASS — Unit-Test trennt `CSI ?1049h`-Inhalt vom Primary-
  Screen und stellt den Primary-Screen mit `CSI ?1049l` wieder her.
- Resize: PASS — Unit-Test bewahrt sichtbare Zellen und begrenzt den Cursor
  auf die neue Dimension.
- Unbekannte Sequenzen: PASS — `CSI 6n` erscheint in
  `unsupported_sequences`, statt still als unterstützt zu gelten.
- Realer PTY-Lauf: PASS — der Probeweg meldete Status `observed`, Kanalstatus
  `completed`, den Marker im rohen PTY-Output und im Konsole-Scrollback sowie
  einen serialisierten VT-Zustand.

## Prüfungen

- `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 66 Tests grün.
- `PYTHONPATH=src python3 tests/playwright_proof.py` — Exit 0.
- `PYTHONPATH=src python3 tests/playwright_guardian.py` — Exit 0.

## Grenzen

Keine Windows-ConPTY-Abnahme, kein vollständiger VT-Emulator und kein
native-EXE-/Fensterscanner-Beleg. `graphify update .` konnte nicht ausgeführt
werden, weil `graphify` in der Umgebung fehlt.
