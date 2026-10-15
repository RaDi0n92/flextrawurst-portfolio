# PLAN-G02 Zyklus I: Raute klickdurchlässig, Modifikator-Bedienung, Status und Schließen — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `8ad3805d47`.

## Anlass

`ERLEBEN.md`: „Klicks fallen physikalisch durch die Raute hindurch. Daniel kann mitten im Match nie versehentlich
die Raute anklicken, den Fokus verlieren und sterben.“ Bedienung per F13–F24 oder „mit Klick bei gedrückter
Modifikatortaste“. `PLAN.md` G02: „Eine tatsächliche Raute mit kleinem Nachrichtenbereich, Verbindung und Status
und ein erreichbares Schließen.“

## Build-Schritt

- `src/augen_haende_bridge/koerper/raute_fenster.py`: Fenster wird klickdurchlässig erzeugt
  (`WS_EX_TRANSPARENT`, `WS_EX_NOACTIVATE`). Ein Timer (80 ms) liest `GetAsyncKeyState` der Modifikatortaste
  (Standard Strg) und nimmt nur solange das Transparenz-Bit weg; während eines Zugs bleibt sie bedienbar.
  Ziehen, Klick (Chat) und Rechtsklick (Menü) wirken nur bedienbar. Der Rand zeigt den Status
  (offline/verbindet/verbunden/beendet/Fehler); bedienbar ist er hell. Fenstertitel „◆ Name [Hotkey]“.
- `src/augen_haende_bridge/koerper/erster_koerper.py`: Raute-Menü mit abgeblendeter Statuszeile, „Chat
  öffnen/schließen“, „Terminal ein-/ausblenden“, „<Name> beenden“, „Bridge beenden“ (Callbacks an den Besitzer).
- Tests: `tests/test_koerper_raute_fenster.py` (neu aufgebaut), `tests/test_koerper_erster_koerper.py` (Menü).
- `probes/koerper_smoketest.py`: drückt Strg in der Probe wirklich (`keybd_event`) und prüft den Weg über den
  echten Modifikator-Timer.

## Ergebnis

Core: 389 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.

Wine (Rohausgabe `PLAN_G02_I_RAUTE_KLICKDURCHLAESSIG_WINE_OUTPUT.json`):

| Zustand | Transparenz-Bit | Klick in die Mitte | Klick in die Quadratecken |
| --- | --- | --- | --- |
| ohne Strg | gesetzt | fällt durch | fällt durch |
| Strg gedrückt (Timer) | weg | trifft die Raute | fällt durch (Rautenform) |
| Strg losgelassen | gesetzt | fällt durch | fällt durch |

Deckkraft-Alpha 87 (34 %, R031), Fenstertitel `◆ testagent [F13]`.

Playwright: nicht anwendbar, kein browserbedienbarer Pfad. Native Windows: **UNKNOWN**.

## Offen

- Hotkey-Registrierung F13–F24 und Status aus der echten Verbindung: mit der Anwendung (Relay-Anschluss).
- Die Wahl der Modifikatortaste (Strg) steht in keinem Dokument fest; sie ist ein Konstruktorparameter.
