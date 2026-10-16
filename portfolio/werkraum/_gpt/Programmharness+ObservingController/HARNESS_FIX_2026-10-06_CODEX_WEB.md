# Harness-Fix – Arbeitschronik vom 2026-10-06

**Autor / Kennung:** `codex_web`  
**Arbeitsort:** Codex in der offiziellen ChatGPT-App, verbunden mit dem VPS über Flextraxtreme MCP.  
**Abgrenzung:** Das ist `codex_web`, nicht die separate Codex-Installation im VPS-Terminal.  
**Status:** Die beschriebenen Codeänderungen sind auf dem VPS eingespielt und der Dienst wurde live als aktiv bestätigt. Eine Testsuite wurde in diesem Durchgang nicht ausgeführt.

Diese Chronik hält fest, welche problematischen Harness-Einstellungen vorgefunden und welche Änderungen tatsächlich vorgenommen und live gegengeprüft wurden. Sie behauptet nicht, dass jeder denkbare Harness-Pfad vollständig regressionsgetestet wurde.

## Anlass und Ziel

Die Harness sollte ChatGPT bei der Arbeit mit dem VPS orientieren und Änderungen nachvollziehbar machen. In der vorherigen Konfiguration waren mehrere Schutzmechanismen jedoch zu breit gekoppelt: Eine unvollständige Vollinventur konnte gewöhnliche Lese- und Arbeitsaktionen blockieren; Sitzungszustand konnte zwischen Gesprächen geteilt werden; und aus modellgenerierten Annahmen konnten faktisch harte Regeln entstehen.

Der Umbau sollte diese konkreten Fehlwirkungen beseitigen, vorhandene Historie erhalten und die Entscheidungen an tatsächliche Aktionen, konkrete Ziele und verifizierte Provenienz binden.

## Vorherige Einstellungen und ihre Fehlwirkungen

| Vorherige Einstellung | Warum sie falsch wirkte | Änderung |
| --- | --- | --- |
| Nicht erkannter ChatGPT-Sitzungen fiel auf einen gemeinsamen Zustand mit dem Schlüssel `default` zurück. | Unabhängige Gespräche konnten alten Workflow-Zustand und alte Blockierungen teilen. Ein frischer Chat war dadurch nicht zuverlässig frisch. | Pro authentifizierter ChatGPT-Sitzung wird nun eine abgeleitete, gehashte Sitzungs-ID verwendet. |
| Eine vollständige VPS-Pfadinventur war Voraussetzung für breite Lese- und Arbeitsaktionen. | Der VPS enthält sehr große Verzeichnisbestände. Der Scan konnte praktisch endlos sein und harmlose Beobachtungen unnötig sperren. | Die Inventur bleibt unvollständig und verfügbar, ist aber keine globale Voraussetzung mehr für normale Leseaktionen. |
| Ein allgemeiner RECOVER-/Verify-Zustand und ein globaler Zähler für „Lesen seit der letzten Mutation“ beeinflussten auch unverbundene Aktionen. | Eine Änderung an Datei A konnte dadurch Prüfungen bei Datei B oder bei nicht betroffenen Aktionen erzwingen. | Prüfung und Recovery richten sich nun nach einem konkret ausstehenden Ziel; bestehende Dateiänderungen behalten ihre zielbezogenen Direkt-Leseprüfungen. |
| Dienstneustarts waren an den speziellen CONTROL_PLANE-Modus gebunden. | Ein benannter, vom Server validierter Dienstneustart wurde wegen des Arbeitsmodus blockiert, obwohl der Neustart selbst eine klar klassifizierbare Aktion ist. | Ein benannter Dienstneustart wird als Kontroll-Neustart klassifiziert; die serverseitige Prüfung des Dienstnamens bleibt bestehen. |
| OpenAI-Client-Metadaten konnten als Beleg für einen `TRUSTED_CLIENT_CAPTURE` und damit für harte Nutzerautorität gelten. | Die Herkunft war damit nicht zuverlässig von einer modellgenerierten Behauptung unterscheidbar. Client-Typ oder Modelltext darf für sich keine Nutzerautorisierung beweisen. | Für harte Autorität zählt nun `DASHBOARD_VERIFIED_CAPTURE`. Ältere Capture-Einträge bleiben als Historie gespeichert, werden aber nicht mehr als harte Durchsetzungsquelle verwendet. |
| Mutationen brauchten praktisch einen Direktiven-Reminder und positive verifizierte Autorität; unklare oder fehlende Daten konnten blockieren. | Das erzeugte einen Autorisierungs-Deadlock und machte aus nicht verifizierten Modellannahmen unnötige Verbote. | Nur ausdrücklich Dashboard-verifizierte DENY-/Invarianten dürfen hart blockieren. Bei nicht erreichbarer Policy-DB entsteht keine Sperre aus veralteten modellgenerierten Angaben. |
| Selbst erzeugte oder gelernte Regeln konnten Aktionen hart sperren; Lern-/Reassessment-Pfade konnten Modell- oder Testbelege zu aktivierenden Regeln machen. | Eine frühere Fehlinterpretation konnte sich dadurch selbst verstärken und künftig wie eine Nutzeranweisung wirken. | Assistant-generierte gelernte Regeln haben keine harte Blockierwirkung; Modell-/Testbelege aktivieren Regeln nicht automatisch. Eine schädliche breite Regel erhielt zusätzlich HARMFUL-Feedback, ohne den Reassessment-Lauf auszulösen. |
| Die Ausgabeprüfung wurde als Pflichtschritt für normale Antworten behandelt. | Eine zusätzliche Prüfung war ohne konkreten Nutzen ein weiterer globaler Gate und konnte die Arbeit unnötig stoppen. | Die Ausgabeprüfung ist für normale Antworten optional. |
| Direkter Tool-Dispatcher und `harness.check_action` konnten unterschiedliche Regeln anwenden. | Eine Aktion konnte im Preflight geblockt werden, obwohl der registrierte Dispatcher sie direkt ausführte, oder umgekehrt. | Dispatcher und Preflight verwenden dieselbe Policy, auch bei direkt registrierten Harness-Tools und pausiertem Master-Layer. |
| Shell-Risikotexte passten teils nicht zur tatsächlich ausgeführten und begrenzten Aktion. | Die Begründung war für Nutzer nicht verlässlich und konnte die Risikoklasse falsch darstellen. | Klassifikation und Begründung wurden korrigiert. Konkrete Befehle laufen über den vorhandenen Pfad-, Zeit-, Ausgabe- und Mount-Sandbox-Pfad; Bulk- und Hintergrundaktionen bleiben blockiert. |
| Persistierte Beschreibungen einiger CORE-Layer entsprachen noch alten Verhaltensregeln. | Dashboard-/DB-Kontext konnte so einen überholten Zweck oder eine überholte Wirkung vermitteln. | Eine append-only Migration aktualisierte genau passende alte Built-in-Beschreibungen und ließ abweichend angepasste Beschreibungen unangetastet. |

## Tatsächlich geänderte Dateien

Auf dem VPS wurden diese drei Dateien geändert:

- `/root/werkraum/tools/vps_mcp/mcp_workflow_graph.py`
- `/root/werkraum/tools/vps_mcp/mcp_action_graph.py`
- `/root/werkraum/tools/vps_mcp/vps_mcp_server.py`

Vorherige Fassungen liegen jeweils als `.pre_harness_fix_20261006.bak` neben den Dateien.

Die Layer-Beschreibungs-Migration wurde in PostgreSQL append-only protokolliert. Bestätigt wurden die aktualisierten Definitionen für `core.path_inventory`, `core.learned_rules`, `core.directives`, `core.verify_recover`, `core.output_check` und `core.client_capture`. Angepasste Definitionen, die nicht exakt dem alten eingebauten Text entsprachen, sollten dabei erhalten bleiben.

## Live-Stand nach dem Fix

- Der systemd-Dienst `vps-mcp` wurde neu gestartet; eine anschließende Statusabfrage bestätigte ihn als aktiv, mit PID `3347308`, seit 2026-10-06 17:38:01 UTC.
- Beim Neustart trennte sich der MCP-Aufruf erwartbar während des Prozesswechsels und meldete einen internen RPC-Fehler. Die nachfolgende Statusabfrage bestätigte den laufenden Dienst. Der RPC-Fehler war daher kein Beleg für einen fehlgeschlagenen Neustart.
- Der aktuelle ChatGPT-Workflow verwendet einen gehashten Sitzungsbezeichner statt des gemeinsamen `default`-Schlüssels. Der beobachtete Graph-Stand war `FOCUSED_READING` / `DISCOVER`, ohne offene Pending-Aktion. Die Pfadinventur ist weiterhin unvollständig; sie blockiert den normalen Lesezugriff nicht.
- Der Preflight ließ `vps.shell git status` mit passender Sandbox-Begründung zu. Das Kommando selbst wurde dabei **nicht** ausgeführt.
- Der Preflight ließ den benannten Neustart des Dienstes `vps-mcp` im Modus `DISCOVER` zu. Die serverseitige Dienstnamenprüfung bleibt bestehen.
- Ein alter breiter Lernregel-Datensatz bleibt aus Historiengründen in der Datenbank sichtbar. Er wurde nicht gelöscht oder neu bewertet; der geänderte Code gibt solchen modellgenerierten Regeln keine harte Steuerwirkung.

## Prüfgrenzen und verbleibender Stand

In diesem Durchgang wurden Live-Status, Workflow-Graph, Policy-Preflight und die persistierten Layer-Beschreibungen nachgelesen. **Es wurde keine Testdatei und keine vollständige Testsuite ausgeführt.** Der Code ist damit live aktiv und die genannten Fälle wurden gezielt gegengeprüft; eine Aussage „alle Regressionen ausgeschlossen“ wäre nicht belegt.

Die alte Datenbankhistorie, frühere Sitzungszustände und unvollständigen Inventurdaten wurden nicht pauschal gelöscht. Neue ChatGPT-Sitzungen erhalten getrennte Workflow-IDs. Das teilt den internen Workflow-Zustand nicht automatisch zwischen Chats; frühere Gesprächsinhalte oder VPS-Historie können nur dann in einem neuen Chat verwendet werden, wenn sie dort im Kontext vorliegen oder gezielt über verfügbare History-/MCP-Werkzeuge abgerufen werden.

## Fortschritt

- [x] Zu breite Inventur- und Recovery-Blockaden gelockert.
- [x] Workflow-Zustand pro ChatGPT-Sitzung isoliert.
- [x] Autoritätsquelle und Wirkung modellgenerierter Direktiven-/Lerninhalte korrigiert.
- [x] Aktionseinstufung, Dispatcher-Preflight und Shell-Begründungen angeglichen.
- [x] Persistierte CORE-Layer-Beschreibungen aktualisiert und nachgelesen.
- [x] Dienstneustart und gezielte Live-Preflights bestätigt.
- [ ] Regressionstests ausführen; in diesem Durchgang nicht erfolgt.
