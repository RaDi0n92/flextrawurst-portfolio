# PLAN-G02 Zyklus L: Anwendung mit Relay-Anschluss — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `39d28ef533`.

## Anlass

`PLAN.md` G02: „ein Terminal, das die Bridge hält“. `ErsterKoerper` hatte bis hier keinen Anschluss an das Relay;
`terminal_senden` war ein Test-Callback.

## Build-Schritt

- `src/augen_haende_bridge/koerper/anwendung.py` (neu): `KoerperAnwendung`.
  - Verbindung nur mit `BRIDGE_URL` und `BRIDGE_TOKEN`; ohne sie sichtbar offline mit Hinweis.
  - Transportereignisse per `post` in den GUI-Thread; Senden über einen eigenen `Sender`-Faden.
  - Nach dem Verbinden `terminal_list_request`; Startliste aus `terminal_list`; `agent_starten()` schickt nur die
    `start_id` (BE02). Ein Körper entsteht mit dem ersten `terminal_state` einer Sitzung (R119), Hotkey F13 + n
    öffnet seinen Chat.
  - `terminal_output` → Terminal (Folgenummern-Lücken werden gezählt), `raute_say` → Raute,
    Eingaben → `terminal_input` in ≤ 8 KiB-Stücken, Größe → `terminal_resize`, Beenden → `terminal_close`.
  - Nach einer Scanner-Bindung: gebundener Ausschnitt als JPEG per `frame` an genau diesen Agenten (R120).
  - Ausdrückliche Test-Haken `test_autostart`, `test_tippe` und `bericht()` für den späteren Wine-Lauf der EXE.
- `src/augen_haende_bridge/koerper/bild.py` (neu): Ausschnitt aus dem echten Frame, JPEG ≤ 1920×1080, Qualität 80,
  unter der Relay-Grenze.
- `src/augen_haende_bridge/koerper/erster_koerper.py`: `terminal_groesse`, `chat_umschalten`; das X am Terminal
  blendet nur aus (R114 — die Sitzung läuft weiter).
- `pyproject.toml`: `pillow` im Extra `medien`.
- Tests: `tests/test_koerper_anwendung.py` (30), `tests/test_koerper_anwendung_relay.py` (1, echter Weg).

## Ergebnis

Core: 429 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.

Echter VPS-Weg unter Linux (`tests/test_koerper_anwendung_relay.py`, dreimal hintereinander grün): echtes `Relay`,
echter `Launcher` mit dem Starteintrag `cat` in einer echten PTY, `BridgeRuntime` auf beiden Seiten, GUI als
Warteschlange wie der echte GUI-Thread:

- Startliste kommt an; Start über die `start_id`; Körper entsteht mit Name „Echo“ und Ort „Host“.
- Ein Marker, ins Terminal getippt, kommt durch die PTY zweimal zurück (Echo und `cat`).
- `bridge_cli.ask({"cmd": "say"})` — das Werkzeug des Agenten — lässt die Raute seines Körpers sprechen.
- Größenänderung 40×120 kommt in der PTY an.
- Nach einer Bindung sieht der Agent über `bridge_cli.ask({"cmd": "see"})` ein JPEG 32×16 des gebundenen Ausschnitts.
- „Agent beenden“ beendet die Sitzung auf dem VPS; Terminal zeigt „beendet …“, Raute „beendet“; keine Lücken.

Native Fenster unter Wine: in diesem Zyklus nicht (kommt mit dem EXE-Lauf). Playwright: nicht ausgeführt.
Native Windows: **UNKNOWN**.

## Harness

`BuildCycleRun` steht auf `running` vor `skill_prebuild_read`: vor dem Bau gab es keine eigene Lesung der Skills;
die Abschlusslesung nach dem Bau ist deshalb in der Reihenfolge der Harness nicht attestierbar und im Feld
`tatsaechlicher_lesestand` vermerkt.
