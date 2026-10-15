---
name: augen-und-haende-bridge-codex-manifest
datum: 2026-09-19
status: uebernahme-in-arbeit
autor: codex bei Daniels VPS
herkunft: Gemini-Bridge-Snapshot 2026-09-19
---

# Augen & Hände Desktop Bridge — Codex-Manifest

Dieses Manifest übernimmt die Arbeit nicht heimlich und ersetzt keine Gemini-Herkunft. Es macht aus der vorhandenen Vision einen überprüfbaren Codex-Bauvertrag. Die Gemini-Originale bleiben lesbar, wiedererkennbar und rückrollbar; der nächste technische Schritt darf sie nur mit eigenem Backup-Commit und nachweisbarer Prüfung verändern.

## Gesicherte Herkunft

Die drei Schichten liegen als unveränderte Kopien unter `/root/werkraum/_codex/_import_gemini_grundriss/augen-und-haende-bridge-2026-09-19/`:

1. Systemdoku: `/root/werkraum/_codex/_import_gemini_grundriss/augen-und-haende-bridge-2026-09-19/dokumentation/76_augen_und_haende_bridge.md`
2. Skill: `/root/werkraum/_codex/_import_gemini_grundriss/augen-und-haende-bridge-2026-09-19/skill/SKILL.md`
3. Implementierung, Tests, Beweisbilder, Inbox und Auditspur: `/root/werkraum/_codex/_import_gemini_grundriss/augen-und-haende-bridge-2026-09-19/implementierung/`

Die lebende Gemini-Arbeitsquelle bleibt `/root/werkraum/_gemini/windows_bridge/`. Die laufende Systemdokumentation bleibt `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`. Dieses Manifest ist die Codex-Steuerung darüber, nicht deren stiller Ersatz.

## Was erhalten bleibt

Die eigentliche Idee ist tragfähig und bleibt erhalten:

- ein einzelner Raum-Frame mit Desktop, Fensterzustand und optionalem Webcam-Inlay;
- Rauten als sichtbare, räumliche Agenten-Anker mit Banner und Ticker;
- Fensterbindung und Click-Cage statt blindem Desktop-Klicken;
- ein Mensch-Override und ein echter, unabhängiger Not-Aus;
- mehrere Agenten mit sichtbarer Provenienz, statt eines anonymen Automationsbreis;
- MCP-Inspektion als strukturierte Bild-/Metadaten-Schnittstelle;
- 10-Hz-Trajektorie als Belegkette für Übergänge, nicht als Behauptung aus einem Standbild.

Die kreative Sprache darf bleiben. Sie darf nur keine Sicherheits- oder Testbehauptung ersetzen.

## Tatsächlicher Stand bei der Übernahme

| Schicht | Wirklichkeit | Codex-Urteil |
|---|---|---|
| WebSocket-Server | `/root/werkraum/_gemini/windows_bridge/bridge_server.py` läuft manuell als `root` auf `0.0.0.0:9880` | funktionsfähig, aber nicht freigabefähig |
| HUD/Client | `/root/werkraum/_gemini/windows_bridge/client_windows/windows_copilot_gui.py` läuft und verbindet sich | sichtbarer Prototyp, Wayland-Capture noch unklar |
| KWin-Scanner | Code und neuer Test unter `/root/werkraum/_gemini/windows_bridge/client_windows/` und `/root/werkraum/_gemini/windows_bridge/tests/` vorhanden | neuer als der alte Gesamtbericht, separat nachzuweisen |
| Input-Arbitrator | `/root/werkraum/_gemini/windows_bridge/input_arbitrator.py` besteht isolierte Tests | im echten Serverpfad nicht integriert |
| F12 | `Tkinter.bind_all()` im HUD | kein globaler `WH_KEYBOARD_LL`-Nachweis |
| MCP | `/root/werkraum/_gemini/windows_bridge/mcp_desktop_bridge.py` ist vorhanden | kein laufender MCP-Prozess; Antwort- und Payload-Grenzen nachhärten |
| Transcript/Linux-Adapter | `/root/werkraum/_gemini/windows_bridge/transcript_streamer.py` und `/root/werkraum/_gemini/windows_bridge/client_linux/backend_linux.py` sind vorhanden | beim Übernahmestand nicht dauerhaft laufend |
| Shell | `create_subprocess_shell()` verarbeitet Prompt-Text als `root` | kritischer Blocker; bis zur Entfernung nicht exponieren |
| Audit | `/root/werkraum/_gemini/windows_bridge/windows_bridge_audit.jsonl` erhält Ereignisse | nicht unveränderbar und nicht als Sicherheitsgrenze zu behandeln |
| Beweise | `/root/werkraum/_gemini/windows_bridge/tests/playwright_proof_report.json` meldet R1–R8 PASS | älter als die letzte KWin-Änderung und teilweise isoliert |

## Nicht verhandelbare Codex-Regeln

1. **Vision, Code und Beleg getrennt halten.** Ein grüner Unit-Test beweist nicht, dass der laufende Pfad dieselbe Komponente verwendet.
2. **Keine Rollen aus Clientdaten glauben.** `agent`, `client` und `observer` brauchen eine echte, serverseitig geprüfte Berechtigung.
3. **Keine Shell aus Prompt-Text.** Shell-Zugriff wird entfernt oder über einen eng begrenzten, separat sandboxierten Broker mit argv-Whitelist, Pfadgrenzen, Benutzergrenze und Timeout-Kill ersetzt.
4. **Kein Root-Desktop-Daemon.** Der Bridge-Prozess bekommt einen eigenen Benutzer, systemd-Sandboxing, begrenzte Schreibpfade und eine definierte lokale oder authentifizierte Netzwerkgrenze.
5. **Not-Aus muss unabhängig sein.** HUD-Bindings, Test-Latenz und ein echter globaler Hook sind drei verschiedene Dinge.
6. **Der Arbitrator muss im Produktionspfad liegen.** `input_arbitrator.py` darf nicht nur ein schönes Testobjekt bleiben.
7. **Payload-Limits werden hart erzwungen.** Bildgröße, Base64-Eingang, Textlänge, Nachrichtenrate und Ringpuffer bekommen serverseitige Grenzen.
8. **Fehler werden nach außen sichtbar.** MCP meldet keine Erfolgsmeldung, wenn der Bridge-Server abgelehnt oder nichts ausgeführt hat.
9. **Jede Behauptung bekommt einen aktuellen Beleg.** Der Beleg nennt Commit, Testpfad, Prozesspfad, Zeitpunkt und bei Live-Aktionen eine Rücklese.
10. **Gemini bleibt Herkunft, nicht Sündenbock.** Gute kreative Entscheidungen werden bewahrt; falsche technische Gewissheiten werden präzise korrigiert.

## Codex-Baufolge

### Tor 0 — Herkunft und Stop-Grenze

Erledigt: drei Kopien, Hash-Prüfung und dieses Manifest. Bis Tor 3 bleibt die Bridge nicht öffentlich exponiert und bekommt keine weiteren Kreativfunktionen.

### Tor 1 — Prozess- und Netzgrenze

Den manuellen Start unter `/root/werkraum/_gemini/windows_bridge/start_bridge.sh` durch einen kontrollierten Dienst ersetzen oder mindestens auf Loopback begrenzen. Der Prozess darf nicht als `root` laufen. Rollback und tatsächliche Endpunkte werden vor und nach dem Umschalten gelesen.

### Tor 2 — Protokollvertrauen

Serverseitige Handshake-Authentifizierung, Rollenrechte und Nachrichten-Schema einführen. Mutationen, Autonomie, Frames, Prompt-Inbox und Not-Aus bekommen getrennte Berechtigungen. Unbekannte oder übergroße Nachrichten werden verworfen und auditiert.

### Tor 3 — Shell und Schreibmacht

`create_subprocess_shell()` aus dem Bridge-Pfad entfernen. Der Prompt darf Text bleiben; ein möglicher Ausführungswunsch wird als explizite, begrenzte Aktion behandelt. Kein `rm`, `mv`, `curl`, `bash` oder ähnliches aus freiem Text.

### Tor 4 — Echte Input-Kette

Den Click-Cage- und Lease-Zustand in einen gemeinsamen Produktions-Arbitrator überführen. Für Windows und Linux wird jeweils bewiesen: erlaubte Aktion, blockierte Aktion, Fensterwechsel, Disconnect und Not-Aus.

### Tor 5 — Failsafe

Den tatsächlichen Hook beziehungsweise die tatsächliche Plattformfähigkeit prüfen. Bei Disconnect, Prozessfehler, Auth-Fehler und Frame-Staleness muss der Client in sicheren Standby gehen. „<1 ms“ wird nur mit einem passenden Live-Beleg behauptet.

### Tor 6 — Capture und KWin

Echten Frame-Rücklesepfad gegen synthetischen Fallback unterscheiden. Wayland-, X11- und Windows-Pfade bekommen getrennte Statuswerte. Webcam bleibt opt-in; Scope- und `with_webcam`-Parameter müssen tatsächlich wirken.

### Tor 7 — MCP und Beweiskette

MCP-Antworten spiegeln echte Serverergebnisse. Bild- und Textgrenzen werden vor Annahme und vor Ausgabe erzwungen. Der aktuelle KWin-Test und alle vorherigen R-Tore laufen gegen genau den Code und Prozess, der freigegeben werden soll.

### Tor 8 — Erst danach kreative Erweiterung

Rauten-Banter, Multi-Agenten-Leases, ViGEm und 10-Hz-Trajektorien werden erweitert, sobald die darunterliegende Sicherheits- und Belegkette trägt. Die Vision wird dadurch nicht kleiner; sie bekommt einen Boden.

## Abnahmeformel

Ein Bridge-Schritt ist erst fertig, wenn alle fünf Aussagen gleichzeitig wahr sind:

```text
Vision erhalten
  + echter Produktionspfad
  + negativer Sicherheitsbeleg
  + aktueller Live-Rücklesebeleg
  + rückrollbarer Commit
  = freigabefähiger Schritt
```

Bis dahin heißt der Zustand ehrlich `Prototyp`, `isoliert bestanden`, `live ungeprüft` oder `blockiert` — niemals pauschal `PASS`.

## Nächster konkreter Codex-Schritt

Als nächstes wird nur die Sicherheitsbasis von Tor 1 bis Tor 3 bearbeitet: Backup, Prozessgrenze, Authentifizierung und Entfernung der Root-Shell. Dabei bleibt die Gemini-Kopie unter `/root/werkraum/_codex/_import_gemini_grundriss/augen-und-haende-bridge-2026-09-19/` unangetastet und dient als Vergleichs- und Herkunftszeugnis.
