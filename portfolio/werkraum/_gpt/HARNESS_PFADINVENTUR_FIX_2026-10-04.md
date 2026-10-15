# Harness-/Pfadinventur-Fix – Arbeitschronik

Stand: 2026-10-04

Diese Datei dokumentiert ausschließlich, was in der laufenden ChatGPT-Session tatsächlich ausgeführt, geprüft, verändert oder live beobachtet wurde. Nicht umgesetzte Ideen werden nicht als erledigt dargestellt.

## 1. Ausgangsproblem reproduziert

- `agents.list_sessions(provider="codex")` wurde aufgerufen.
- Der Aufruf wurde vom Harness blockiert, weil `path_inventory_complete=false` war.
- `harness.graph` wurde gelesen und bestätigte, dass read-only Beobachtungswerkzeuge an die unvollständige VPS-Pfadinventur gekoppelt waren.
- Eine explizite Reparatur-Session `chatgpt-vps-fix-2026-10-04` wurde für `harness.path_scan` verwendet.
- Der Pfadscan wurde mehrfach fortgesetzt.
- Große Scan-Aufrufe liefen serverseitig weiter, obwohl der ChatGPT-/Code-Mode-Client mehrfach mit Timeout abbrach.
- Persistierte Zwischenstände wurden mit kleinen Probe-Aufrufen gegengeprüft, unter anderem:
  - 222080 gescannte Verzeichnisse, 82095 pending.
  - 282581 gescannte Verzeichnisse, 73725 pending, 6405371 gesehene Dateien.
- Dabei wurde praktisch bestätigt, dass der Vollscan als Freischaltungsweg ungeeignet ist: Beim Traversieren wurden weitere Verzeichnisse entdeckt und die Pending-Menge konnte wieder steigen.

## 2. Kontrollcode und Testbasis gelesen

Tatsächlich gelesen wurden unter anderem:

- `/root/werkraum/tools/vps_mcp/mcp_workflow_graph.py`
- `/root/werkraum/tools/vps_mcp/vps_mcp_server.py`
- `/root/werkraum/tools/vps_mcp/mcp_action_graph.py`
- `/root/werkraum/tools/vps_mcp/mcp_cognitive_graph.py`
- `/root/werkraum/tools/vps_mcp/tests/test_mcp_workflow_graph.py`

Im Workflow wurden insbesondere geprüft:

- Workflow-/Intent-Zustände.
- `_PATH_INVENTORY_TOOLS`.
- `_default_session()` und `workflow_runtime`.
- `preflight_action()`.
- `record_outcome()`.
- `graph_snapshot()`.
- Directive-, Experience- und Learning-Persistenz.
- Drift-/Kandidatenregel-Logik.
- später die neu eingebaute PostgreSQL-Layerarchitektur und Control-Leases.

Im Server wurden unter anderem geprüft:

- Harness-Toolwrapper.
- Directive-Context/Reminder/Output-Check.
- Experience-/Learning-Tools.
- TOOLS-Registry.
- zentraler Harness-Dispatcher.
- REST-/MCP-/OAuth-Routing.
- Layer-Control-Wrapper.
- Dashboard-Helferfunktionen.

## 3. Baseline

Vor den eigenen Workflow-Änderungen wurde ausgeführt:

`python3 -m pytest tests/test_mcp_workflow_graph.py -q`

Ergebnis: **23/23 Tests grün**.

## 4. Directive-/Autoritätsproblem reproduziert

- Es wurde bestätigt, dass modellseitig eingereichte USER_DIRECTIVE-Notizen als `UNVERIFIED_MODEL_CLAIM` gespeichert werden.
- Es wurde bestätigt, dass daraus keine harte Nutzerautorität entsteht.
- Der Directive-Denier verlangte bei Mutationen einen verifizierten positiven Autorisierungs-Constraint.
- Im damaligen Directive-Kontext lagen die älteren Nutzertexte mit `authority_verified=false`.
- `services.restart` wurde nach Reminder versucht und zunächst wegen fehlender verifizierter positiver Autorität geblockt.
- Später wurde im Directive-RAG erstmals ein echtes `TRUSTED_CLIENT_CAPTURE` mit `authority_verified=true` beobachtet:
  - `d-5b15fe27b5844dcb9c528373fba4648d`
- Ab diesem Zeitpunkt konnten eng begrenzte Kontroll-Edits wieder durch den normalen Harness-Pfad ausgeführt werden.

## 5. Server-/Client-Toolkatalog verglichen

Die öffentliche OpenAPI des laufenden MCP-Servers wurde gelesen:

`https://flextrawurst.de/werkzeugkoerper-[PFAD-GESCHWAERZT]/openapi.json`

Dabei wurde bestätigt:

- Experience-/Learning-Tools existierten serverseitig und in der öffentlichen OpenAPI.
- Im laufenden ChatGPT-Connector fehlten genau zehn dieser Tools:
  - `harness.experience_message`
  - `harness.learning_context`
  - `harness.self_observed_drift`
  - `harness.candidate_rule`
  - `harness.learning_test`
  - `harness.learning_cycle`
  - `harness.rule_feedback`
  - `harness.reassess_rule`
  - `harness.supersede_rule`
  - `harness.learning_status`
- Ein direkter dynamischer Zugriff über den aktuellen ChatGPT-Code-Mode wurde geprüft; die zehn Tools waren dort ebenfalls nicht aufrufbar.
- Damit wurde ein veralteter/abweichender Client-Toolkatalog gegenüber dem laufenden Server bestätigt.

## 6. Parallel arbeitende Session berücksichtigt

- Der gemeinsame Cognitive Graph wurde wiederholt gelesen, um Kollisionsrisiken mit einer parallelen Session zu erkennen.
- Die parallele Session legte Entscheidungen für Harness-Layer, PostgreSQL-Layerpersistenz, Control-Leases und Dashboard-Steuerung ab.
- Später wurden reale Änderungen an `mcp_workflow_graph.py` und `vps_mcp_server.py` über Dateizeitstempel bestätigt.
- Vor eigenen weiteren Änderungen wurden diese neuen Schnittstellen erneut gelesen.
- Die eigene PRIO-0-Implementierung wurde auf die bereits eingebaute PostgreSQL-Layerarchitektur aufgesetzt, statt eine zweite kanonische Scope-Ablage einzuführen.

## 7. Scope-Creep bei Codex erkannt

- Während der Diagnose wurde zusätzlich versucht, die aktuelle Codex-Sessionquelle zu finden.
- `/root/.codex/sessions` wurde per Pfadnavigation geprüft; dort lagen nur historische Daten bis August 2026.
- Im Servercode wurde bestätigt, dass `agents.list_sessions` für Codex weiterhin auf diesen alten Pfad zeigte.
- Alte Atlas-Codex-Mitschriften wurden ebenfalls als historisch erkannt.
- `codex-live.service` wurde als existierender Dienstpfad gefunden.
- Diese Codex-Pfadsuche war für den aktuellen Fix ein Nebenpfad.
- Nach Daniels Korrektur wurde dieser Nebenpfad gestoppt.

## 8. PRIO 0 als Auftragstreue festgelegt

Daniel legte fest, dass Auftragstreue noch vor bisherigen Harness-Prioritäten stehen muss.

Im gemeinsamen Cognitive Graph wurden dazu tatsächlich gesetzt:

- `n-b456b629bcf3`: `core.task_scope / mission_lock` als PRIO 0.
- Ein erster Implementationsvertrag `n-eae37f66d44a`.
- Nach Abgleich mit der PostgreSQL-Layerarchitektur wurde dieser erste Vertrag superseded.
- `n-cad5b84e73fa`: überarbeiteter Implementationsvertrag mit PostgreSQL-Layerstate als kanonischer Quelle.
- `n-7c7b5da93f66`: Regression-/Abnahmekriterien für PRIO 0.
- Der PRIO-0-Vertrag wurde mit dem bekannten Bootstrap-Deadlock als `BLOCKED_BY` verknüpft.

## 9. Tatsächliche Änderungen in mcp_workflow_graph.py

Folgende Änderungen wurden in dieser Session tatsächlich geschrieben und danach direkt gegengelesen:

### 9.1 Read-only Observation vor Pfadinventur

`_PREINVENTORY_OBSERVATION_TOOLS` wurde ergänzt für:

- `agents.list_sessions`
- `agents.read_session`
- `agents.search_sessions`
- `agents.compare_sessions`
- `database.query_readonly`
- `services.status`
- `services.logs`
- `atlas.stream_search`
- `atlas.stream_status`
- `atlas.map`
- `atlas.ai_stream_state`

Die Ausnahme greift nur solange `path_inventory_complete=false`.

Diese Observation-Werkzeuge werden als `NODE_NAVIGATE` erlaubt und bauen keinen Datei-Lesezustand auf.

### 9.2 PRIO-0-Knoten

- `NODE_TASK_SCOPE = "TASK_SCOPE"` wurde ergänzt.
- `core.task_scope` wurde als Core-Layer ergänzt.

### 9.3 Task-Scope-Auswertung

Implementiert wurden:

- `_task_scope_patterns()`
- `_task_scope_authority_verified()`
- `_task_scope_targets()`
- `task_scope_snapshot()`
- `_task_scope_preflight()`

`preflight_action()` prüft den harten Task-Scope jetzt vor `base_evaluate_action()` und damit vor den nachfolgenden Workflow-Gates.

### 9.4 Scope-Verhalten

- Harness-Control-Werkzeuge werden nicht vom Task-Scope selbst ausgesperrt.
- Unverifizierte TASK-Layer bleiben sichtbar, wirken aber nicht hart.
- Ein hart verifizierter TASK-Layer ohne `allowed_tool_patterns` blockiert fail-closed.
- Tool- und Zielmuster werden geprüft.
- Off-Scope liefert `TASK_SCOPE_BLOCK`.
- Sidequests werden dabei nicht automatisch weiterverfolgt.

### 9.5 Runtime-/Lernschleife

- `record_outcome()` behandelt `TASK_SCOPE_BLOCK` neutral:
  - kein Wechsel nach `RECOVER`.
  - kein Erhöhen von `blocked_streak`.
- `find_drift_point()` kennzeichnet diesen Fall mit eigenem Driftcode `TASK_SCOPE_BLOCK`.
- Für `TASK_SCOPE_BLOCK` wird keine automatische Kandidatenregel erzeugt.
- Damit wird ein bewusstes PRIO-0-Parken nicht als gewöhnlicher Agentenfehler gelernt.

### 9.6 Graphsicht

- `graph_snapshot()` enthält jetzt einen eigenen `task_scope`-Block.
- Die Graph-Prinzipien nennen PRIO 0 explizit.

## 10. Autoritätsfälschung gefunden und geschlossen

Bei einem Red-Team der neuen Task-Scope-Logik wurde festgestellt:

- `harness.create_layer` ist auch für ChatGPT aufrufbar.
- ChatGPT konnte dabei ein eigenes `provenance`-JSON mitsenden.
- Eine reine Prüfung auf `authority_verified=true` innerhalb dieses JSON wäre daher fälschbar gewesen.

Daraufhin wurde die Autoritätsprüfung verschärft.

### 10.1 Serverpersistierter CREATE-Actor

Der Layer-Snapshot wurde erweitert um:

- `created_actor`
- `created_event_at`

Diese Werte werden aus dem serverseitig persistierten `CREATE`-Event des Layers gelesen.

### 10.2 Harte PRIO-0-Autorität

Ein TASK-Layer wird nur hart autoritativ, wenn:

- `created_actor == "DANIEL_DASHBOARD"`
- `provenance.source == "CHATGPTHARNESS"`
- `provenance.authority_verified is True`

Ein von ChatGPT erzeugter TASK-Layer kann sich dadurch nicht über ein gefälschtes Provenienz-JSON selbst harte Nutzerautorität geben.

## 11. Control-Lease-Grenzen geprüft

Im Servercode wurde geprüft:

- ChatGPT darf einen Layer immer wieder auf `ACTIVE` setzen.
- `PAUSED` oder `ARCHIVED` verlangt eine aktive Control-Lease.
- `harness_control_allowed()` berücksichtigt:
  - Grantee.
  - nicht widerrufene Lease.
  - noch nicht abgelaufene Lease.
  - Layer-Pattern über `fnmatch`.
- Die öffentliche Tool-Registry enthält kein `harness.control_lease_grant` und kein `harness.control_lease_revoke` für ChatGPT.
- Lease-Grant/Revoke sind im Dashboard-Helferpfad mit Actor `DANIEL_DASHBOARD` verdrahtet.
- `tool_harness_create_layer()` setzt den Actor serverseitig fest auf `CHATGPT`; ein vom Toolargument mitgesendeter Actor wird nicht übernommen.

## 12. Regressionstests erweitert

Die vorhandene Datei

`/root/werkraum/tools/vps_mcp/tests/test_mcp_workflow_graph.py`

wurde erweitert.

Neue Testfälle prüfen unter anderem:

- Off-Scope blockiert vor den anderen Gates.
- Unverifizierter Scope wird nicht hart.
- Gefälschte Dashboard-Provenienz eines von ChatGPT erzeugten TASK-Layers wird nicht hart.
- Target-Mismatch wird geblockt.
- In-Scope-Aktionen laufen danach weiterhin durch die bisherigen Gates.
- Pre-Inventory-Observation baut keinen Read-State auf.
- `TASK_SCOPE_BLOCK` führt nicht nach `RECOVER`.
- `TASK_SCOPE_BLOCK` erzeugt keine automatische Lernregel.
- Graphsnapshot zeigt Task-Scope.
- Harness-Control bleibt vom Task-Scope-Block ausgenommen.
- `harness.wander` und weitere nicht-kontrollierende Harness-Nebenpfade bleiben task-scoped.
- Der enge Control-/Safety-Korridor bleibt erreichbar.
- ChatGPT kann ohne Dashboard-Lease weder `PAUSED` noch `ARCHIVED` setzen.
- ChatGPT kann Schutz ohne Lease wieder auf `ACTIVE` setzen.
- Lease-Grant/Revoke sind keine öffentlichen ChatGPT-Tools.
- `create_layer` verwendet serverseitig Actor `CHATGPT`.

## 13. Testläufe

Tatsächlich ausgeführte Teststände:

- Baseline: **23/23 grün**.
- Nach erster PRIO-0-/Observation-Erweiterung: zunächst **30 grün / 1 rot**.
- Der rote Test wurde untersucht.
- Ursache war ein Test-Seed mit `schema_version` statt des vom Loader erwarteten Schlüssels `schema`.
- Test-Seed wurde korrigiert.
- Danach: **31/31 grün**.
- Nach Autoritätsfälschungs-Test: **32/32 grün**.
- Nach zusätzlichen Server- und Task-Scope-Grenztests: **39/39 grün**.

Letzter tatsächlich ausgeführter Lauf:

`python3 -m pytest tests/test_mcp_workflow_graph.py -q`

Ergebnis:

`39 passed in 0.70s`

## 14. Live-Gegenprüfungen

- Der MCP-Dienst wurde mehrfach neu gestartet.
- Ein Restart-Aufruf meldete im Tool intern einen Fehler; anschließend wurde der reale Dienstzustand geprüft und bestätigte, dass der Restart tatsächlich erfolgt war.
- Ein späterer Restart wurde erneut aus einem gültigen Lesezustand angestoßen.
- Der Dienstzustand bestätigte danach einen neuen Prozessstart am 2026-10-04 um 21:22:52 CEST.
- Der Live-Graph zeigte `core.task_scope`.
- Core-Layer lieferten nach geladenem Sicherheitsupdate `created_actor="SYSTEM_BUILTIN"`.
- `agents.list_sessions(provider="codex", limit=1)` wurde ausschließlich als Gate-Probe ausgeführt.
- Dieser Call wurde trotz unvollständiger Pfadinventur live erlaubt.
- Die Laufspur zeigte:
  - node = `NAVIGATE`
  - Zustand blieb unverändert.
  - `paths=[]`
- Der Observation-Call baute damit keinen Datei-Lesezustand auf.
- Der historische Codex-Treffer wurde nach der Gate-Probe nicht weiter verfolgt.

## 15. Dashboard-Routing tatsächlich geprüft

- `_harness_dashboard_state()` und `_harness_dashboard_action()` existieren im Servercode.
- Darin sind unter anderem Layer-Steuerung, Full-Activate, Lease-Grant/Revoke, Feedback und Layer-Erzeugung mit Actor `DANIEL_DASHBOARD` implementiert.
- Der HTTP-Handler wurde gelesen.
- Zum Zeitpunkt der Prüfung gab es in `do_GET()` und `do_POST()` keinen verdrahteten `/chatgptharness`-Route-Branch.
- Externe Aufrufe von `https://flextrawurst.de/chatgptharness` lieferten entsprechend HTTP 404.
- Dieser Dashboard-Routing-Strang wurde in dieser Session nicht verändert, weil parallel eine andere Session daran arbeitete.

## 16. Dokumentationsauftrag

- Daniel beauftragte ausdrücklich, unter `/root/werkraum/_gpt/` eine rückwirkende Dokumentation nur über tatsächlich ausgeführte Arbeit abzulegen und bei Fortschritten zu aktualisieren.
- Ein früherer Schreibversuch wurde vom Harness blockiert, weil die konkrete Doku-Anweisung zu diesem Zeitpunkt noch nicht als verifizierte Schreibautorität vorlag.
- Später wurde der Parallelstrang ausdrücklich damit beauftragt, Trusted-Capture und Dokumentationsfreigabe herzustellen.
- Danach wurde bestätigt, dass die wartenden Sessions ihre Markdown-Dokus unter `/root/werkraum/_gpt/` wieder über `harness.directive_reminder` plus `vps.write_file` bzw. `vps.edit_file` schreiben dürfen.
- Diese Datei wird auf genau dem dafür festgelegten Pfad geschrieben:
  `/root/werkraum/_gpt/HARNESS_PFADINVENTUR_FIX_2026-10-04.md`

## 17. Stand bei Erstellung dieser Datei

Tatsächlich bestätigt:

- PRIO-0-Task-Scope ist im Workflow implementiert.
- Read-only Observation vor Abschluss der Pfadinventur ist eng freigeschaltet.
- Observation baut keinen falschen Read-State auf.
- Task-Scope-Blocks werden nicht als gewöhnlicher Recovery-/Lernfehler behandelt.
- Harte Task-Autorität ist an den serverseitigen Dashboard-CREATE-Actor gebunden.
- ChatGPT kann sich diese Autorität nicht über Provenienz-JSON selbst fälschen.
- ChatGPT kann Schutz ohne Dashboard-Lease nicht pausieren/archivieren.
- Nicht-kontrollierende Harness-Nebenpfade bleiben task-scoped.
- Der enge Control-/Safety-Korridor bleibt erreichbar.
- 39/39 Workflow-/Grenztests sind grün.
- Die neueste Workflow-Datei wurde nach Paralleländerungen vollständig gegengelesen.
- Der MCP-Dienst wurde nach dem letzten Stand neu gestartet und lief anschließend aktiv.

## 18. Dokumentation tatsächlich geschrieben und gegengelesen

- Nach Freigabe des Trusted-Capture-/Schreibpfads wurde diese Markdown-Datei tatsächlich neu angelegt.
- Der Schreibaufruf `vps.write_file` wurde vom Harness mit `ALLOW` freigegeben.
- Die Datei wurde unmittelbar danach vollständig mit `vps.read_file` zurückgelesen.
- Rücklesung bestätigt:
  - 332 Zeilen vor dieser Abschluss-Ergänzung.
  - Titel vorhanden.
  - Teststand `39/39` vorhanden.
  - Abschnitt zum Dokumentationsauftrag vorhanden.
  - Abschlusszustand vorhanden.
  - SHA-256 der vollständig zurückgelesenen ersten Fassung: `951589242974bf4c1ee5cfee3a3d1fac2c80c94c2af47cf7d8d3dd4b8e9f2d32`.
- Damit ist der zuvor offene Dokumentationspunkt tatsächlich ausgeführt und nicht mehr nur vorbereitet.
