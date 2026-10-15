EVIDENCE_VERSION: 1
STAGE: V3.3 PTY resize roundtrip
OUTCOME: PASS

## Belegkette

- `resize_requested`: PASS — die sichtbare Proof-Surface löste den expliziten
  Button `Resize owned PTY to 40x120` aus.
- `resize_delivered`: PASS — der besessene PTY-Wrapper erhielt ausschließlich
  eine strukturierte `resize`-Nachricht über den separaten Control-Socket.
- `kernel_resize_applied`: PASS — der Wrapper setzte `TIOCSWINSZ`.
- `kernel_resize_observed`: PASS — der Wrapper las danach `TIOCGWINSZ` und
  meldete `rows: 40`, `cols: 120` zurück.
- `renderer_resized`: PASS — `VTScreenState` übernahm die beobachtete Größe;
  der sichtbare Renderer-Readback zeigte ebenfalls 40×120.

## Prüfungen

- `PYTHONPATH=src python3 -m unittest discover -s tests` — 66 Tests grün.
- `PYTHONPATH=src python3 tests/playwright_proof.py` — Exit 0, inklusive
  sichtbarem Resize-Button und DOM-Rücklese.
- `PYTHONPATH=src python3 tests/playwright_guardian.py` — Exit 0.
- Separater direkter Runtime-Lauf — Status `observed`, beobachtete Größe
  40×120.

## Grenzen

Der Beleg ist Linux-PTY-spezifisch. Windows-ConPTY, native EXE, DPI-/Font-
Readback, KDE-Arbeitsflächen und der echte Fensterscanner sind offen.
