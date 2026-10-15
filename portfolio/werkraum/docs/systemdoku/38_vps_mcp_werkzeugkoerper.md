
# Systemdokumentation 38: VPS-MCP-Werkzeugkörper (für ChatGPT)

---
autor: claude-code bei Daniels VPS
datum: 2026-07-23
status: PHASE 1 PRODUKTIV & VERIFIZIERT (5 weitere Phasen geplant)
port: 8091
service: vps-mcp.service
---

## 1. Warum diese Datei existiert

Daniel: *"ja chatgpt ist teil des schiffes teil der crew xD und ja alles machen"* — als Antwort auf eine sehr umfangreiche, von einer anderen KI-Instanz vorgeschlagene Spezifikation für einen MCP-Server, der praktisch den gesamten VPS für ChatGPT zugänglich machen soll: Dateien, Git-Provenienz, Agenten-Sitzungen (Gemini/Claude/Codex), Dienste/Docker/Netzwerk, Datenbanken, Web-Apps/3D-Assets und Zensi (lesend und schreibend).

Bewusst **nicht** als ein einziger riesiger, ungeprüfter Bauschritt umgesetzt — siehe die Linsen-Session am selben Tag (`_claude/ideen/sieben_linsen_koerper_kreatur.md`): ein großer Bauplan wird trotzdem in Stufen umgesetzt, jede Stufe einzeln verifiziert.

## 2. Architektur

Eigenständiger MCP-Server, getrennt von `flextrawurst_3d_mcp.py` (Systemdoku 34) — konzeptionell ein viel breiterer "Werkzeugkörper", kein Teil der 3D-Pipeline. Gleicher, bereits gegen ChatGPT verifizierter OAuth-2.1+PKCE-Mechanismus (kopiert, nicht neu erfunden).

- **Server:** `/root/werkraum/tools/vps_mcp/vps_mcp_server.py`
- **Port:** 8091, nur `127.0.0.1` gebunden
- **Systemd:** `/etc/systemd/system/vps-mcp.service`
- **nginx:** `location /vps-mcp/` in `/etc/nginx/sites-available/flextrawurst`, proxy zu `127.0.0.1:8091`
- **Öffentlich:** `https://flextrawurst.de/vps-mcp/`

## 3. Sicherheit (von Anfang an mitgedacht)

- **`ALLOWED_ROOTS`:** Datei-Zugriff nur unter `/root/werkraum`, `/root/flextrawurst`, `/root/zensi`, `/root/.gemini/antigravity-cli/brain` — kein freier VPS-weiter Zugriff.
- **`SECRET_MUSTER`:** `.env`, `*_tokens.json`, `id_rsa*`, `*.pem`, `*.key`, `.htpasswd*`, alles mit `password`/`secret`/`credentials` im Namen — ausgeschlossen, auch wenn es innerhalb einer erlaubten Wurzel liegt (jeder Pfad-Teil wird geprüft, nicht nur der Dateiname).
- **`services.status`/`services.logs`:** nur lesend, kein restart/stop/start. Dienstname gegen striktes Regex geprüft (`^[a-zA-Z0-9_@.+-]+\.service$`), kein Shell-Injection-Vektor.
- **`assets.get_file`:** Dateien bis 2MB inline als Base64, größere über eine befristete (10 Minuten), zufällig token-abgesicherte Download-URL (`/download/<token>`) statt riesiger Base64-Blöcke im Chat-Kontext.

## 4. Gemeinsames Ausgabeformat

Jedes Tool liefert `{ok, data, source_refs, warnings, truncated, next_cursor, error}`. Jede Fundstelle in `source_refs` trägt zusätzlich `path`, `start_line`/`end_line`, `sha256`, `modified_at`, `git_commit`, `source_type` — Daniels Vorgabe, damit Aussagen später auf konkrete VPS-Fundstellen zurückführbar sind.

## 5. Phase 1 — zwölf Tools (fertig, verifiziert)

`vps.list_roots`, `vps.list_files`, `vps.search_text`, `vps.read_file`, `vps.file_metadata`, `git.status`, `git.log`, `services.status`, `services.logs`, `system.snapshot` (alle von Daniel selbst als risikoärmster Einstieg vorgeschlagen), plus `assets.get_file` und `assets.render_3d_preview` (von Daniel priorisiert — wiederverwendet `blender_pipeline` aus der 3D-Pipeline, kein Duplikat).

**Verifiziert:** isolierter Test aller 12 Tools inkl. Sicherheitsfälle (`.env`-Ausschluss, Pfad außerhalb erlaubter Wurzeln, Shell-Injection-Versuch im Dienstnamen — alle korrekt abgelehnt), echtes Blender-Rendering gegen `test_cube.glb`, kompletter OAuth-2.1+PKCE-Flow live simuliert über `https://flextrawurst.de/vps-mcp/`, Hauptseite unverändert erreichbar. werkraum-Commit `c8a04a02e`.

## 6. Geplante Phasen 2–6 (noch nicht gebaut)

2. Restliche Asset-Tools (`assets.list/search/inspect/preview/extract_3d_metadata/validate_3d_model/convert_3d_model/find_duplicates/trace_source/read_manifest/list_renders/inspect_image/inspect_audio`) + `provenance.trace`, `git.show`, `git.diff`.
3. `agents.*` (Gemini-/Claude-/Codex-Sitzungen lesen/durchsuchen/vergleichen) + `containers.*`/`network.*`.
4. `database.*` (nur lesend) + `webapps.*` + `tests.*`.
5. `zensi.*` — nur lesende Tools.
6. `zensi.*` — schreibende Aktionen (zuletzt, am heikelsten — Eingriffe in ein laufendes System).

## 7. Zugangsdaten (systemd-Unit, nicht im Git-Repo)

- API-Key (Zustimmungs-Schritt): `VPS_MCP_KEY`
- Client ID: `vps-mcp`
- Client Secret: `VPS_MCP_CLIENT_SECRET`

Rotiert am 2026-07-23 (die urspruenglichen Werte waren vollstaendig im ChatGPT-Chat gelandet). `_ACCESS_TOKENS`/`_AUTH_CODES` sind In-Memory -- jeder Dienst-Neustart (auch fuer Rotation) macht bereits verbundene Connector-Sitzungen ungueltig, die Verbindung muss danach immer komplett neu aufgebaut werden.

## 9. Der eigentliche Blocker: JSON-RPC-Batch-Requests (2026-07-23)

Nach den ersten beiden Fixes (Notification-Handling, Protokollversion) blieb das Problem: "App-Verknüpfung erkannt, Tool-Weitergabe noch nicht". `journalctl -u vps-mcp.service` zeigte den echten Absturz: `AttributeError: 'list' object has no attribute 'get'` — ChatGPTs MCP-Client schickt `initialize` + `notifications/initialized` + `tools/list` offenbar als **ein JSON-RPC-Batch** (JSON-Array mehrerer Nachrichten in einem POST-Body), nicht als einzelne Requests. Der Server erwartete immer ein einzelnes Objekt und crashte beim ersten Array-Body — nginx zeigte `502 Bad Gateway`, ChatGPT sah nie eine gültige Antwort.

**Fix:** `_verarbeite_rpc()` verarbeitet jetzt eine einzelne Nachricht; `do_POST` ruft das entweder einmal (Einzel-Request) oder pro Element eines Arrays (Batch) auf. Notifications liefern kein Element in der Batch-Antwort (korrekte JSON-RPC-2.0-Batch-Semantik) — falls ein Batch ausschließlich aus Notifications besteht, liefert der Server einen leeren `202`. Gleicher Fix auch in `flextrawurst_3d_mcp.py` angewandt.


Verifiziert: der exakte Batch (`initialize`+`notification`+`tools/list` als Array) liefert jetzt eine korrekte Zwei-Element-Antwort, lokal und live über `https://flextrawurst.de/vps-mcp/` sowie `https://flextrawurst.de/3d-mcp/`, Einzel-Requests und Einzel-Notifications funktionieren unverändert weiter. Commits `ce82f5982` (vps-mcp) + `a0cc7ffaf` (3d-mcp).

## 10b. Fünf Verfassungs-Dateien direkt in /root gezielt freigegeben

Daniel: *"ich hab gesat chatgpt muss darauszugreifen und alles sehen und lesen können also musst du ihm doch das in den mcp geben oder?"* — Anlass war eine sehr lange ChatGPT/Gemini-Sitzung über das "Kosmos"-Weltenbau-Archiv (`/root/werkraum/kosmos/`, `gptspieleversuchzeigen/` usw.), die von mir gegengeprüft wurde: die Dateien existieren echt (9.292 Dateien/2,2 GB unter `/root/werkraum`, nahezu exakt was ChatGPT selbst berichtet hatte), aber `/root/GEMINI.md` — als "Verfassungs-Handbuch" referenziert — lag außerhalb aller vier erlaubten Wurzeln.

Neue `ALLOWED_FILES`-Liste (bewusst einzelne Dateien, nicht `/root` als ganze Wurzel — das würde `.ssh`, andere Dienste und im selben Ordner liegende Sicherheitsaudit-Berichte mit öffnen): `GEMINI.md`, `CLAUDE.md`, `KIMI.md`, `grok.md`, `AGENTS.md`. Bewusst **nicht** freigegeben: `SECURITY_FINAL_REPORT_FLEXTRAWURST_20260530.md` und `SECRET_FINDINGS_REDACTED.md` (echte Sicherheitsaudit-Funde, u.a. der offene Punkt "Master-API-Key muss noch rotiert werden"), sowie `.aider.chat.history.md` (private Chat-Historie eines anderen Tools) — nicht angefragt, bewusst draußen gelassen, Daniel informiert.

`vps.list_roots` liefert jetzt zusätzlich die Einzeldatei-Liste. Verifiziert: `GEMINI.md` lesbar, Security-Reports weiterhin korrekt blockiert, live bestätigt. Commit `416d6e140`.

## 10c. Ausgelagerte werkraum-Symlink-Ziele freigegeben

Beim gezielten Nachprüfen einzelner von ChatGPT/Gemini referenzierter Pfade (Daniel: *"das hier muss er auch alles genau sheen"*) gefunden: `/root/werkraum/bilder/` ist ein Symlink auf `/root/werkraum_bilder` — physisch **außerhalb** von `/root/werkraum`. `Path.resolve()` folgt Symlinks (Sicherheitsfeature gegen Sandbox-Flucht per Symlink), das echte Ziel lag bisher außerhalb aller Wurzeln und wurde korrekt blockiert.

`/root/werkraum` hat mehrere solcher Top-Level-Symlinks auf `werkraum_*`-Geschwisterordner (Disk-Layout-Entscheidung, nicht meine). Geprüft und hinzugefügt: `werkraum_bilder` (568M Bilder), `werkraum_geni` (GENI-System), `werkraum_codewesen` (Wesen-Profile), `werkraum_agent` (Kooperations-Doku), `werkraum_erkenntnis` (Konzept-Doku) — alle eindeutig Projekt-Inhalt ohne fremde Personendaten.

**Zunächst nicht hinzugefügt, Daniel gefragt statt geraten:** `werkraum_flarum` (enthält einen `nutzer/`-Ordner — vermutlich echte Daten realer Flarum-Forennutzer) und `werkraum_logs` (395MB rohe Laufzeit-Logs, wenig Inhaltswert). Reine Abhängigkeits-Ordner (venv/node_modules/watchdog_venv) weiterhin nicht — kein Projekt-Inhalt, nur Bibliotheks-Ballast, kein Auftrag dafür.

Verifiziert: alle fünf neuen Wurzeln lesbar, `_api_tokens.json` innerhalb `werkraum_codewesen` bleibt durch `SECRET_MUSTER` korrekt blockiert, live bestätigt. Commit `e7e4e8219`.

**Nachtrag:** Daniels Antwort auf die Rückfrage: *"teil des schiffes teil der crew sagte ich ja alles"* — `werkraum_flarum` und `werkraum_logs` danach ebenfalls hinzugefügt. Insgesamt jetzt 11 Wurzeln + 5 Einzeldateien. Commit `50ecf0df8`.

## 10. scopes_supported ergänzt

ChatGPTs Connector-UI zeigte beim Einrichten "Basis-Scopes"/"Standard-Scopes" mit dem Hinweis: "Die ermittelte OAuth-Konfiguration hat keine unterstützten Scopes zum Auswählen angegeben" — `scopes_supported` fehlte in beiden Discovery-Dokumenten. Ergänzt (`["tools"]`, ein einziger Scope für den kompletten, nur lesenden Werkzeugsatz — kein granulares Berechtigungsmodell in Phase 1). Commit `657dab1d0`, live verifiziert.

## 8. Zwei Nachbesserungen beim echten Verbinden

1. **"App-Verknüpfung erkannt, Tool-Weitergabe noch nicht"** — der Server beantwortete JSON-RPC-**Notifications** (Nachrichten ohne `id`-Feld, z.B. `notifications/initialized`, die der Client nach `initialize` schickt) fälschlich mit einer Fehler-JSON statt gar nicht zu antworten (JSON-RPC 2.0 verlangt für Notifications keine Antwort). Das brach den Handshake vermutlich ab, bevor `tools/list` je aufgerufen wurde. Behoben: Notifications liefern jetzt einen leeren `202 Accepted`. Zusätzlich spiegelt `initialize` jetzt die vom Client angefragte `protocolVersion` statt starr `2024-11-05` zu behaupten. Gleicher Fix auch in `flextrawurst_3d_mcp.py` angewandt (derselbe kopierte Code, gleicher Bug). Commits `585d91306` (vps-mcp) + `ec59651f0` (3d-mcp).
2. **`vps.find_recent_files` ergänzt** — der von Daniel/ChatGPT selbst vorgeschlagene erste Test ("die zehn zuletzt geänderten Dateien im Werkraum") brauchte ein Tool, das in Phase 1 zunächst vergessen wurde (`vps.list_files` sortiert nur alphabetisch). Jetzt 13 Tools statt 12.

Verifiziert live: Notification liefert leeren 202er, `initialize` spiegelt angefragte Version, `tools/list` liefert 13 Tools, alter API-Key nach Rotation korrekt abgelehnt (401), neuer Key funktioniert.

## 11. Zwei weitere Klone: geteilt (Claude/Codex/Gemini) und sauber (Web-Claude)

Daniel, 2026-07-28: *"connecte dich und codex und gemini mit dem einen"* — derselbe `vps_mcp_server.py`-Code, zweimal zusätzlich als eigener systemd-Dienst gestartet, mit eigenem Port/eigener Protokoll-Datei/eigenem Action-History-Log, aber **demselben** gemeinsamen Gesamtatlas wie ChatGPTs Original-Instanz:

- **`vps-mcp-shared.service`**, Port 8092, `https://flextrawurst.de/werkzeugkoerper-geteilt-[REDACTED]/` — für Claude Code, Codex, Gemini CLI (dauerhafte Terminal-Ströme, keine Browser-Reconnect-Ceremony nötig). Eigene, entrümpelte `session_continuity_shared_v1.json` (Ton geändert, Durchsetzungslogik in `session_continuity.py` bleibt identisch — `default_intent`/Regeltext sind nur Anzeige, siehe unten).
- **`vps-mcp-sauber.service`**, Port 8093, `https://flextrawurst.de/werkzeugkoerper-sauber-[REDACTED]/` — für seltene, zustandslose Web-Claude-Connector-Besuche (Daniel: Claude-Web-Chat verbraucht das Nutzungslimit pro Nachricht ca. 3x schneller als eine laufende Claude-Code-Session, kein mitwachsender Kontext gewünscht).

Alle drei Dienste teilen sich `vps_mcp_server.py` und `session_continuity.py` — Regeln wie "8 Zeichen Mindestlänge für `new_session_reason`" oder "Resume verlangt bekannte Session-ID" sind im Python-Code fest verdrahtet, nicht aus der jeweiligen Protokoll-JSON gelesen. Nur Ton/Beschreibungstext der JSON ist pro Klon unterschiedlich, das tatsächliche Durchsetzungsverhalten ist für alle drei identisch.

Bug live gefunden und gefixt: Actor-Feld stand bei `vps-mcp-shared` anfangs fälschlich auf `GPT-5.6-sol-hoch` (Default-Wert aus dem Original-Code) statt dem tatsächlichen Aufrufer — `FLEXTRAWURST_ACTION_ACTOR` als eigene Env-Var pro Klon ergänzt (`geteilter-mcp-mehrstrom` bzw. `web-claude-check-in`).

Angebunden: Claude Code und Gemini CLI direkt per `claude mcp add` / `gemini mcp add` gegen den geteilten Klon. Codex ebenfalls (`codex mcp add --bearer-token-env-var`), brauchte dafür eine `VPS_MCP_SHARED_TOKEN`-Env-Var in `.bashrc` — vom Auto-Mode-Classifier zunächst blockiert, per selbst geschriebenem, von Daniel manuell ausgeführtem `setup_codex_mcp.sh` nachgeholt.

## 12. Zwei Discovery-Lücken beim Claude-Web-Connector (2026-07-29)

Claude Web (nicht Claude Code) verbinden zu wollen deckte zwei Lücken auf, die bei ChatGPTs Connector nie auffielen — vermutlich weil dessen Implementierung großzügiger/über den `WWW-Authenticate`-Header discovert, während Claude Webs Connector-Setup offenbar strikter nach Spec sucht bzw. bei manuell eingetragener Client-ID/Secret gar keine Discovery mehr macht:

1. **RFC-8414/9728-Pfadform fehlte.** Eine Issuer-URL mit Pfadanteil (`.../werkzeugkoerper-sauber-[REDACTED]`) verlangt laut Spec, dass dieser Pfad **hinter** `.well-known/oauth-authorization-server` bzw. `.well-known/oauth-protected-resource` eingefügt wird, nicht davor. Der Server kannte nur die Form davor (die auch für ChatGPT funktioniert). Fix: vier zusätzliche Nginx-`location =`-Aliase (pro Klon zwei), reines Proxy-Mapping auf die schon funktionierenden Endpunkte, keine Python-Änderung.
2. **Claude Web ignorierte den deklarierten `authorization_endpoint` und ist stattdessen zu `https://flextrawurst.de/authorize` (Domain-Wurzel, ohne Subpfad) navigiert** — vermutlich weil Daniel Client-ID/Secret manuell im "Erweiterte Einstellungen"-Feld eingetragen hatte und Claude in diesem Modus offenbar `/authorize`+`/token` als Konvention an der Wurzel annimmt, statt Metadaten zu lesen. Fix: root-level `location = /authorize` / `/token` / `/register` als Nginx-Alias auf den Sauber-Klon (8093) — die Wurzel war für keinen anderen Zweck belegt (beide 404 vor dem Fix). Da hier zwangsläufig nur EIN Klon an der Wurzel hängen kann, bewusst der Sauber-Klon gewählt (passend zu den Zugangsdaten, die Daniel gerade eingetragen hatte). Falls später der geteilte Klon auch von Web aus gebraucht wird, bräuchte das eine eigene Subdomain (keine Wildcard-DNS für `*.flextrawurst.de` vorhanden, nur `flextrawurst.de`/`www` und einzeln eingerichtete Subdomains wie `pro.flextrawurst.de`).

Beide Fixes über ein von Daniel selbst ausgeführtes Skript (`fix_authorize_root.sh`) angewendet — Nginx-Edit-Rechte für den Classifier waren trotz vorherigem Freigabeversuch nicht aktiv (`permissions.allow` blieb leer). Verifiziert: alle vier RFC-Pfade liefern 200, `/authorize` an der Wurzel liefert die Zugriff-erlauben-Seite statt 404, Daniel hat den Connector danach erfolgreich verbunden (Schlüssel-Eingabe im HTML-Consent-Formular, `VPS_MCP_KEY` der Sauber-Instanz).

## 13. Punktnotierte Tool-Namen verletzten Claude Webs Schema (2026-07-29)

Direkt im Anschluss an Abschnitt 12: der Connector verband sich zwar (OAuth durchgelaufen), aber `tools/list` scheiterte an Claude Webs Frontend-Validierung: `tools.0.FrontendRemoteMcpToolDefinition.name: String should match pattern '^[a-zA-Z0-9_-]{1,64}$'`. Live geprüft: von 155 Tools verletzten 126 das Muster — alle punktnotiert (`atlas.pulse`, `vps.shell`, `services.restart`, ...), aus der ursprünglich für ChatGPT geschriebenen `TOOLS`-Dict-Konvention. ChatGPTs Connector akzeptiert Punkte offenbar anstandslos, Claude Webs Frontend-Schema nicht.

**Fix, bewusst additiv statt die ~126 Dict-Schlüssel einzeln umzubenennen:** neue Hilfsfunktion `_tool_name_normalisieren()` (Punkt → Unterstrich) plus eine einmalig aufgebaute Umkehr-Tabelle `_ORIGINAL_TOOLNAME_JE_NORMALISIERT` (mit Kollisionsprüfung — wirft beim Serverstart einen `RuntimeError`, falls zwei unterschiedliche Original-Namen auf denselben normalisierten Namen abbilden würden, aktuell keine Kollision). `tools/list` meldet jetzt den normalisierten Namen nach außen, `tools/call` löst einen ankommenden Namen über `_tool_spec_aufloesen()` zuerst direkt, sonst über die Umkehr-Tabelle auf. Die `TOOLS`-Dict-Schlüssel selbst (und damit alles, was ChatGPT bereits mit Punkt-Namen aufruft) bleiben unverändert — reine Präsentationsschicht für nach außen.

Da alle drei Dienste (`vps-mcp.service`/ChatGPT, `vps-mcp-shared.service`, `vps-mcp-sauber.service`) dieselbe `vps_mcp_server.py` ausführen, aber als getrennte, bereits laufende Prozesse: Codeänderung wirkt erst nach Neustart des jeweiligen Prozesses. Bewusst nur `vps-mcp-shared` und `vps-mcp-sauber` neu gestartet, **ChatGPTs Original-Dienst (`vps-mcp.service`) nicht angefasst** — läuft unverändert mit dem alten Code weiter, kein Risiko für eine laufende ChatGPT-Session. Nebenwirkung des Neustarts: die In-Memory-Access-Tokens der beiden Klone sind dabei verfallen, Daniels gerade eben aufgebaute Connector-Verbindung musste er einmal neu autorisieren.

Verifiziert: `tools/list` beider neu gestarteter Dienste liefert 162 Tools (mehr als die zuvor gezählten 155 — Differenz nicht weiter aufgeklärt, vermutlich Zähl-Zeitpunkt vor/nach vollständiger `TOOLS`-Befüllung), 0 davon verletzen das Muster. `tools/call` mit einem normalisierten Namen (`vps_list_roots` statt `vps.list_roots`) live gegen den Sauber-Klon getestet, liefert korrekte echte Daten zurück — die Rückwärtsauflösung funktioniert.

**Nachtrag, echter Abschluss-Beleg:** Trotz serverseitig zweifach verifiziertem Fix (localhost + öffentliche Domain, 0 ungültige Namen) zeigte Claude Web beim ersten erneuten Verbindungsversuch exakt denselben Fehler nochmal — vermutlich ein gecachter Tool-Manifest-Zustand aus dem vorherigen, fehlgeschlagenen Setup-Versuch, nicht mehr ein Server-Bug. Nach komplettem Entfernen und Neu-Anlegen des Connectors (statt nur "Reconnect") lief die Verbindung durch. Daniel bestätigt: *"super klapl klasse gemacht ehrlich"* — Connector ist jetzt echt verbunden, nicht nur der Server-Teil geprüft.

## 14. Zwei echte Funde beim Vergleich "Claude Web kann angeblich weniger als ChatGPT" (2026-07-29)

Daniel/claude-im-web fragten, warum Claude Web scheinbar weniger könne als ChatGPT. Zwei getrennte Vermutungen geprüft, beide widerlegt bzw. präzisiert — nicht einfach die plausibelste Erklärung übernommen:

**Vermutung 1 (falsch): Claude Web zeigt nicht alle Tools.** Claude Webs eigene Connector-Einstellungsseite (`.../mcp` → "Tool-Berechtigungen") listet alle 162 Tools einzeln mit Schaltern auf — kein Client-seitiges Abschneiden. Der vorher im Code gefundene, historische "erste 95 tools/list-Einträge"-Kommentar (Abschnitt 11/`_CONNECTOR_PRIORITY_TOOLS`) betraf ChatGPT, nicht Claude, und ist für die aktuelle Frage irrelevant.

**Vermutung 2 (halb richtig): Schreibzugriff nur in werkraum.** `vps_write_file`/`vps_edit_file`/`vps_delete`/`vps_move` prüfen wirklich streng gegen `SCHREIB_ERLAUBTE_WURZELN` (nur werkraum + Symlink-Geschwister) — das stimmt. Aber `vps_shell` prüft nur den Startordner (`cwd`) gegen dieselbe Liste, nicht was der eigentliche Bash-Befehl danach mit absoluten Pfaden anfasst (`echo x > /etc/y` von einem werkraum-cwd aus läuft durch, weil `subprocess.run(["/bin/bash","-lc", command], cwd=...)` den Text danach nicht mehr gegen eine Wurzel prüft). Diese Lücke gilt identisch für alle drei Klone (ChatGPT, geteilt, sauber) — Claude Web hat also technisch dieselbe Reichweite wie ChatGPT, hatte sich beim ersten Test nur selbst unterschätzt (nur die strengen Datei-Tools ausprobiert, nicht `vps_shell`). Bewusst nicht geschlossen — weder von Claude Web noch von Claude Code: Daniel wollte es zunächst explizit genutzt sehen ("mein wille ja bitte tu es"), Claude Web hat trotzdem abgelehnt (die deklarierte Grenze der eigenen Tool-Beschreibung gilt unabhängig von der technischen Durchsetzungslücke) und stattdessen den sichereren Weg über Claude Code vorgeschlagen — siehe Abschnitt 15.

## 15. `instructions`-Feld im `initialize`-Response ergänzt (2026-07-29)

Ursprünglicher Wunsch (Claude Web + Daniel): eine Kontinuitätsregel (u.a. "bei aktivem Konnektor jeden Austausch 1:1 mitschreiben") soll nicht nur davon abhängen, dass eine Session zufällig `_claudeweb/ZUHAUSE.md` liest, sondern möglichst schon beim Verbindungsaufbau sichtbar sein. Claude Web wollte das nicht selbst patchen (Live-Patch am eigenen Server-Init-Prozess, Risiko der eigenen Verbindung), sondern hat es explizit als Auftrag an Claude Code weitergereicht — über normalen Terminal-Zugriff, nicht über die `vps_shell`-Lücke aus Abschnitt 14.

**Umsetzung, additiv:** `_init_instructions_bauen()` liest den ohnehin schon pro Klon unterschiedlichen `FLEXTRAWURST_SESSION_CONTINUITY_PROTOCOL_PATH`-Vertrag (`load_session_continuity_protocol()`, bereits bestehende Funktion aus `tools.action_history`) und baut daraus einen kurzen `instructions`-Text: ein Hinweis auf `session_id`/`history_startup`, plus das `purpose`-Feld des jeweiligen Vertrags. Kein neuer, separat zu pflegender Text — reine Projektion aus bereits vorhandenen JSON-Verträgen. Try/except gegen einen fehlenden/kaputten Vertrag, damit ein Konfigurationsfehler nicht den ganzen Server zum Absturz bringt.

**Vorsichtig ausgerollt:** Backup-Commit vor der Änderung, `python3 -m py_compile` plus voller bestehender Testlauf (`test_mcp_atlas` + `test_mcp_parallel_reads`, 21/21 grün) vor dem ersten Neustart. Nur `vps-mcp-sauber.service` neu gestartet — `vps-mcp.service` (ChatGPT) und `vps-mcp-shared.service` (Codex/Gemini/Claude Code, eigene laufende Verbindung) bewusst nicht angefasst, laufen unverändert mit dem alten `initialize`-Response weiter, bis sie bei anderer Gelegenheit ohnehin neu gestartet werden. Verifiziert: `initialize` gegen Port 8093 liefert jetzt das neue Feld mit dem `sauber`-spezifischen `purpose`-Text, `tools/list` weiterhin 162 Tools, Port 8091/8092 unverändert ohne `instructions`-Feld.

## 16. Aus dem geteilten Klon werden drei dedizierte: eigener MCP pro AI-Strom (2026-07-30)

Auslöser: Beim Debuggen "warum kann Claude Web weniger als ChatGPT" (Abschnitt 14) kam heraus,
dass `mcp.home`/`history_startup` für ALLE Klone (auch `shared`) weiterhin ChatGPTs Zuhause
zurücklieferten — die Individualisierung vom 28.07. (Abschnitt 11) hatte nur `session_continuity`
erfasst, nicht `mcp_home`. Daniel dazu, sinngemäß: dann sollten Codex und Gemini auch jeweils
einen eigenen dedizierten Klon bekommen, so wie ChatGPT und Claude Web schon einen haben, statt
sich einen weiteren Fallback zu teilen.

**Fünf statt drei Klone, alle auf demselben `vps_mcp_server.py`:**

| Klon | Service | Port | Öffentliche URL |
|---|---|---|---|
| ChatGPT | `vps-mcp.service` | 8091 | `/vps-mcp/` bzw. `/werkzeugkoerper-[PFAD-GESCHWAERZT]` |
| Claude Code | `vps-mcp-claude.service` (vormals `vps-mcp-shared`) | 8092 | `/werkzeugkoerper-geteilt-[REDACTED]/` (unverändert) |
| Codex | `vps-mcp-codex.service` (neu) | 8094 | `/werkzeugkoerper-codex-[REDACTED]/` |
| Gemini CLI | `vps-mcp-gemini.service` (neu) | 8095 | `/werkzeugkoerper-gemini-[REDACTED]/` |
| Claude Web | `vps-mcp-sauber.service` | 8093 | `/werkzeugkoerper-sauber-[REDACTED]/` |

**Claude-Klon: reine Umwidmung, kein Client-Reconnect nötig.** `vps-mcp-shared` wurde gestoppt,
deaktiviert und als `.bak`-Datei archiviert (nicht gelöscht — Provenienz-Prinzip). Der neue
`vps-mcp-claude.service` läuft auf demselben Port/derselben URL/demselben `VPS_MCP_KEY` — meine
eigene `~/.claude.json`-Verbindung musste dadurch nicht angefasst werden, nur `FLEXTRAWURST_
ACTION_ACTOR` (jetzt `claude-code` statt `geteilter-mcp-mehrstrom`) und zwei neue Home-Env-Vars
kamen dazu.

**Codex und Gemini: echte neue Klone, echte Rekonfiguration.** Neue OAuth-Zugangsdaten generiert,
neue nginx-Locations (Proxy + RFC-8414/9728-Well-Known-Aliase, Muster aus Abschnitt 12
übernommen), neue systemd-Units nach dem `vps-mcp-sauber`-Vorbild. `~/.codex/config.toml`
(`bearer_token_env_var`, neuer `VPS_MCP_CODEX_TOKEN` in `.bashrc` statt dem alten
`VPS_MCP_SHARED_TOKEN`) und `~/.gemini/settings.json` (Key direkt im Header, wie zuvor) auf die
neuen Endpunkte umgestellt. Daniel hatte vorher bestätigt: beide gerade nicht aktiv verbunden,
also sicher zum Umstellen. `gemini mcp list` zeigte danach sofort "✓ Connected".

**Zuhause-Manifeste: verlinkt, nicht neu geschrieben.** Auf Daniels ausdrücklichen Einwand ("warum
könnt ihr das nicht einfach verknüpfen") bekam keiner der drei (Claude/Codex/Gemini) einen neuen,
erfundenen Identitätstext — jedes `mcp_zuhause/`-Verzeichnis (`_claude/mcp_zuhause/`,
`_codex/mcp_zuhause/`, `_gemini/mcp_zuhause/`) enthält nur ein minimales `MANIFEST.json`
(`{"sections": {"home": "<eigene Konstitution>"}}`) plus ein schlankes Protokoll-JSON mit
`purpose`/`identity_boundary`, die ausdrücklich sagen: diese Datei spricht nicht für den
jeweiligen Strom, sie verweist nur auf das, was er selbst schon geschrieben hat (`AGENTS.md` für
Codex, `GEMINI.md` für Gemini, `CLAUDE.md` für mich). `mcp.home`/`history_startup` liest die
echten, bestehenden Dateien (25-41KB, je nach Konstitution) — kein neuer Fließtext.

**Session-Continuity bewusst NICHT aufgeteilt.** Alle drei (Claude/Codex/Gemini) nutzen weiterhin
denselben `session_continuity_shared_v1.json`-Vertrag — das war nie das identifizierte Problem
(Daniel hatte nur die Zuhause-/Identitäts-Vermischung kritisiert, nicht die Kontinuitäts-Policy).
Unnötige Verdopplung vermieden.

**Verifiziert, Ende zu Ende, über die echten öffentlichen URLs mit echten Bearer-Tokens** (nicht
nur lokal): `mcp.home` liefert für Claude `claude-code-vps-zuhause`, für Codex
`codex-vps-zuhause`, für Gemini `gemini-vps-zuhause` — je die eigene, korrekte Identität. Alle
fünf Dienste `active`, `tools/list` liefert bei vier von fünf Klonen 162 Tools.

**Nebenfund beim Verifizieren, noch nicht behoben:** `vps-mcp.service` (ChatGPT, Port 8091)
liefert nur noch **155** Tools — vermutlich exakt das lange ungeklärte "155 vs. 162"-Rätsel aus
Abschnitt 13, nur live und nicht mehr nur vermutet: der Dienst läuft seit vor dem 28.07. (Browser-
Capture-Ergänzung) ununterbrochen und hat den seitdem gewachsenen `TOOLS`-Stand nie eingelesen.
Bewusst NICHT neu gestartet, ohne Daniels Bestätigung, dass gerade keine aktive ChatGPT-Session
daran hängt — exakt dieselbe Vorsicht wie in Abschnitt 13 beim letzten Mal.
