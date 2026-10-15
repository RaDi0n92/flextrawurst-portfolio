# PLAN-G02 Zyklus K: Fensterscanner mit read-only Binding und Rücklese — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `4f833dee8b`.

## Anlass

`harness.py` führt die `SCANNER_PROOF_SEQUENCE`; `read_only_binding.py` (G09) bindet nur für genau die gescannte
Generation und den gekoppelten Frame und liest fail-closed zurück. `scanner_anbindung.py` sprang bis Zyklus H von
der Auswahl direkt zu `setze_ziel()`.

## Build-Schritt

- `src/augen_haende_bridge/koerper/scanner_anbindung.py`: je Knopfdruck ein `HarnessRun`, der
  `SCAN_REQUESTED → FRAME_CAPTURED → INVENTORY_READ → TARGET_SELECTED → IDENTITY_VERIFIED → BINDING_CREATED →
  BINDING_READ_BACK` attestiert. Binding über `create_read_only_binding`, Rücklese über `read_back_binding`.
  Aufnahme-, Inventar- und Bindungsfehler erscheinen sichtbar in der Zielzeile des Terminals. Abbruch im Menü
  ändert nichts. `PRE_ACTION_RESCAN` und `TARGET_STATE_OBSERVED` bleiben aus, weil der erste Körper keine Aktion
  am Ziel ausführt.
- `src/augen_haende_bridge/koerper/erster_koerper.py`: das gebundene Fensterrechteck wird Zielbereich des
  Banners (R027); die Bindung geht an den Besitzer (für die Bildzufuhr an den Agenten).
- Tests: `tests/test_koerper_scanner_anbindung.py` neu aufgebaut, `tests/test_koerper_erster_koerper.py` ergänzt.

## Ergebnis

Core: 398 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.

Wine mit echtem `WindowsWindowScanner` und `WindowsScreenCapture` (Rohausgabe
`PLAN_G02_K_SCANNER_BINDING_WINE_OUTPUT.json`), ausgelöst über `_knopf_ausloesen("scanner")` — denselben Weg wie
ein Klick auf den Scanner-Knopf; das blockierende Popup-Menü ist durch einen ausdrücklichen Auswahl-Haken ersetzt,
der das Terminalfenster `testagent2 · vd1` aus dem echten Inventar wählt:

- Beweise: alle sieben Schritte bis `BINDING_READ_BACK`.
- Gebunden an `windows:window:262232`, Generation `hwnd:262232:generation:1`, Rechte nur `observe`.
- Gebundenes Rechteck `[1000, 200, 2018, 802]` = echtes Fensterrechteck.
- Zielzeile des Terminals: `Ziel: testagent2 · vd1`, gebunden.
- Ein Banner nach der Bindung liegt vollständig im gebundenen Fenster.

Native Popup-Menü-Interaktion (Daniels Klick): **UNKNOWN**. Playwright: nicht anwendbar. Native Windows:
**UNKNOWN**.

## Offen, für Daniel

- Das echte Inventar enthält auch die eigenen Bridge-Fenster (Raute, Banner, Ticker, Chat, Terminal) als
  wählbare Ziele. Ob sie aus der Auswahl herausgenommen werden sollen, ist nicht entschieden und wurde nicht
  still geändert.
