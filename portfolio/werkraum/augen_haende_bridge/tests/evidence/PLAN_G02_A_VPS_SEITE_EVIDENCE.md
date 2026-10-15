# PLAN-G02, Zyklus A — VPS-Seite: Relay-Erweiterung und Terminal-Starter

Datum: 2026-09-21 · Autor: claude bei Daniels VPS · Ort: vd1 (`/config`), Docker-Weg auf dem Host geprüft, Repo `/root/werkraum`

Gemeint ist G02 aus `/root/werkraum/docs/augen_haende_bridge/PLAN.md` (nicht Codex' frühere Zählung). G02 besteht aus mehreren Zyklen; dieser ist
der erste und deckt nur die Linux-Seite ab: was das Windows-Programm später ansprechen wird. Das Windows-Fenster ist nicht Teil dieses Zyklus.

## Fokusvertrag dieses Zyklus

- Ziel: G02 des Plans. Nächster einzelner Stein: das Relay um Terminal- und Raute-Nachrichten erweitern und den Starter bauen, der Startlisten-Einträge
  in Linux-PTYs hält.
- Erhaltungsanker: Der Körper besteht aus Terminal, Scanner je Terminal, Raute, Kamera und Mikrofon (BE03). Kein Overlay als Fläche (R118).
  1:1 nur für Sitzungen, die die Bridge selbst startet (BE01); der Desktop kann nur Einträge der Startliste starten (BE02), nie einen Befehl.
  Harness und beide Skills bleiben unverändert (BE04). Die exe geht erst mit dem kompletten ersten Körper an Daniel (BE03).
- Verbotene Drift: keine Anbindung bestehender Sessions, kein Befehl vom Desktop, keine Attrappe, kein Relay-Token im Agentenprozess.

## Gebaut

| Datei | Inhalt |
| --- | --- |
| `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/transport.py` | neue Nachrichten `terminal_list_request`, `terminal_list`, `terminal_start`, `terminal_state`, `terminal_close`, `terminal_input`, `terminal_resize`, `terminal_output`, `raute_say`; `frame` darf `terminal_id` tragen; zwei neue Fähigkeiten je Principal (`terminal_control` für den Desktop, `terminal_serve` für den Starter) |
| `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/bridge_runtime.py` | Quittung nur für zuverlässige Ereignisse; `publish()` für Aufrufer außerhalb der Schleife |
| `/root/werkraum/augen_haende_bridge/client_vps/terminal_launcher.py` | Startliste und Orte laden, PTY je Terminal, Strom, Eingabe, Größe, Schließen, Bildablage je Terminal, Sprech-Socket für Agenten |
| `/root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py` | `say` (Text erscheint in der Raute) und `see` (Pfad des letzten Bildes vom Scanner); nur Standardbibliothek |
| `/root/werkraum/augen_haende_bridge/client_vps/starts.json`, `orte.json` | Startliste nach BE02 (Claude, Codex, Gemgem in vd1; Anthropic-Claude, Gravity in vd2; Haiku, GLM, Kimi auf dem Host) und die drei Orte |
| `/root/werkraum/augen_haende_bridge/client_vps/bridge_server.py` | startet Relay, Starter und den bisherigen Inventar-Agenten gemeinsam; neue Optionen `--starts`, `--orte`, `--runtime-dir` |

Entwurfsentscheidungen, die im Code stehen:

- Ströme (`terminal_output`, `terminal_input`, `terminal_resize`) laufen ohne Journal, ohne Quittung und ohne Ergebnis an den Absender. Tastatureingaben und
  Terminalinhalt landen nie im Journal; ein Test prüft das an der SQLite-Datei selbst.
- Der Starter ist mehrfädig. Deshalb startet er Prozesse mit `subprocess.Popen` plus `setsid -c` (Sitzungsführer mit dieser PTY als Steuerterminal) und nicht mit
  `pty.fork()`; Python-Code zwischen `fork` und `exec` kann in einem mehrfädigen Prozess hängen.
- Ereignisse des Relays werden nicht in dem Thread verarbeitet, der sie empfängt (`publish` wartet auf genau diesen Thread), sondern in einem eigenen Arbeiter-Thread.
- Der Agent im Terminal bekommt nur `BRIDGE_TERMINAL_ID`, `BRIDGE_TERMINAL_TOKEN` und `BRIDGE_RUNTIME_DIR`; die Umgebung ist eine Allowlist.
  Bei Docker wird das Token per `-e NAME` (ohne Wert) durchgereicht und steht nie in der Prozessliste.
- `docker exec` läuft nach dem Ende des Clients im Container weiter. Beim Schließen findet der Starter deshalb alle Prozesse des Terminals im Container über
  `BRIDGE_TERMINAL_ID` in deren Umgebung und beendet sie (erst SIGHUP, nach 1,5 s SIGTERM, nach 4 s SIGKILL).

## Belege

**Suite:** `cd /root/werkraum/augen_haende_bridge && PYTHONPATH=src:. python3 -m unittest discover -s tests -q` → **165 Tests OK**
(Ausgangsstand 121; neu: `test_transport_terminal.py` 9, `test_terminal_launcher.py` 34, `test_bridge_server_terminal.py` 1; `test_bridge_server.py` prüft die neuen Grants).
Die Starter-Tests verwenden echte PTYs, einen echten Unix-Socket und ein echtes Relay über Loopback; nur die Ausgabe des Starters in `FakeRuntime` wird für
Einzeltests aufgefangen.

Ende-zu-Ende ohne Attrappe: `tests/test_bridge_server_terminal.py` startet den echten Server-Prozess, verbindet sich als Desktop und durchläuft
Liste → Start (`starting`, `running`) → Strom (Bytes des Programms) → Eingabe → `bridge_cli.py say` **im Terminal selbst** (kommt als `raute_say` mit der
richtigen `terminal_id` an) → `exited` mit Exit-Code 0. Die frühere G08-Probe (`tests/bridge_server_smoke.py`) läuft unverändert weiter grün.

**Docker-Weg auf dem Host** (ssh als root auf `172.17.0.1`, Python 3.12.3, gegen die echten Container):

| Prüfung | Ergebnis |
| --- | --- |
| Start in `virtuellerdesktop1` (`/config`) und `virtuellerdesktop2` | beide laufen, Ausgabe kommt an, Exit-Code 5 bzw. 0 wird gemeldet |
| Fenstergröße 31×101 beim Start | `stty size` im Container zeigt `31 101` |
| Größenänderung auf 45×133 | im Container sichtbar (`45 133`) |
| Laufzeitordner im Container | Host-`/root/.bridge-probe-run` erscheint als `/vps_root/.bridge-probe-run` |
| Token in der Host-Prozessliste | nicht vorhanden (`ps -eo args`) |
| Schließen | `exited` mit 129 (SIGHUP); der `sleep 30` im Container ist danach weg |

## Terminalkette nach Skill (V3.1)

| Glied | Stand |
| --- | --- |
| `session_owned`, `pty_connected` | PASS — die Bridge startet und hält die PTY (Linux und Docker) |
| `vt_output_received` | PASS — rohe Bytes kommen über das Relay beim Desktop-Peer an |
| `input_accepted`, `input_delivered`, `input_echoed` | PASS — Eingabe über das Relay landet in der PTY und wird vom Terminal zurückgespiegelt (`GOT:pong`) |
| `rendered` | **offen** — die Darstellung ist das Windows-Terminalfenster, nächster Zyklus |
| `state_observed`, `audited` | Zustand (`starting`/`running`/`exited`/`failed`) wird gemeldet; ein Audit der Tastatur gibt es absichtlich nicht |

## Nicht belegt / offen

- Windows-Darstellung des Terminals und alles, was Daniels Bildschirm betrifft: **UNKNOWN**, kommt in den nächsten Zyklen.
- Wiederaufsetzen eines Terminals nach einer Trennung: Das Terminal läuft weiter, die Ausgabe während der Trennung geht verloren (Strom ist live). Wie das
  Fenster danach den Bildschirm neu bekommt, ist noch offen.
- `forward_stream` hält den Sperr-Lock des Relays beim Senden; ein sehr langsamer Desktop könnte bis zu 2 s blockieren. Bisher nicht gemessen.
- GLM und Kimi: Ordner unbestätigt (`bestaetigt: false` in `starts.json`).
- Playwright: In diesem Zyklus gibt es keinen browserbedienbaren Pfad; Playwright kommt zuletzt (BE04) am Ende von G02.
- Körper-Tor `tests/pruefe_koerper.py` läuft (Exit 0), prüft aber noch den alten Tk-Körper `client_windows/overlay_app.py`; es wird auf den neuen Körper ausgerichtet,
  sobald er steht.
- `graphify update .` versucht: `graphify: command not found` — Blocker weiter offen.
