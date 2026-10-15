# PLAN-G02 Zyklus M: Lokaler Not-Aus (F12) — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `ee7088726b` (Zyklus L, von der anderen Instanz committet und von mir geprüft:
429 Tests, drei bekannte Fehlschläge).

## Anlass

R066 / `78_augen_und_haende_bauplan.md` 3.1: „Not-Aus muss unabhängig vom WebSocket, MCP, Agentenstatus und UI-Thread
wirken.“ Bridge-Skill: „kein <1-ms-Not-Aus … ohne belastbaren Nachweis behaupten.“

## Build

- `koerper/notaus.py`: `NotAus` (thread-sicheres Flag mit Lauschern) und `TastaturHook` (`WH_KEYBOARD_LL` in eigenem
  Faden mit eigener Nachrichtenschleife; schluckt die Taste nicht). `koerper/win32.py`: Hook-Bindungen.
- `koerper/anwendung.py`: Not-Aus sperrt `terminal_input`, `frame` und `terminal_start`; die Sperre wird im
  Sender-Faden geprüft, wirkt also auch bei hängendem GUI-Thread. Schließen/Größe bleiben erlaubt. Anzeige „Not-Aus“
  an allen Rauten; Freigabe über das Raute-Menü.
- `koerper/erster_koerper.py`, `raute_fenster.py`: Menüpunkt „Not-Aus (F12)“ / „Aufheben“, Status „Not-Aus“.

## Ergebnis

Core: 443 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.

Wine (`PLAN_G02_M_NOTAUS_WINE_OUTPUT.json`): Hook installiert; F1 löst nichts aus; ein echter F12-Tastendruck setzt
das Flag, während der Haupt-Thread keine Nachrichten pumpt. Der gemessene Wert (1 ms) ist nur ein Hinweis unter Wine
und **keine** Latenzaussage.

## UNKNOWN / offen

- Native Windows (echte Tastatur, andere Programme im Vordergrund, erhöhte Rechte/UIPI): UNKNOWN.
- Der Not-Aus wirkt auf den ersten Körper (nichts geht mehr an die Agenten hinaus, Kamera/Mikrofon-Stopp folgt mit
  der Medienleiste); es gibt noch keine „Hände“, die er anhalten müsste.
- Ein Verbindungsabbruch allein löst ihn nicht aus.
- Playwright: nicht anwendbar.
