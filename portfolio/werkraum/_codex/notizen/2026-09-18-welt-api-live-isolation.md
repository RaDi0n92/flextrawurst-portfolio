---
datum: 2026-09-18
betrifft: [welt-api, sicherheit, flex-api, postgresql, altra, luna]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich bin in der abgebrochenen Sicherheitsfixspur wieder bei der Welt-API eingestiegen: in die Inventarnotiz, den Graph-Report, die letzten Git-Commits und die Unit-Dateien für Brücke und Splitter. Der Desktop-Abbruch hatte keine VPS-Neustartspur hinterlassen; die relevante offene Linie war die große API, die noch als `root` lief.

In der API und den importierten Routern fiel besonders auf, dass Runtime-DDL noch als Selbstverständlichkeit behandelt wurde: *„CREATE TABLE IF NOT EXISTS“* im Gruppenrouter und im Feed-Marker-Endpoint. Das war keine bloße Stilfrage. Genau diese Zeilen hätten einer isolierten DB-Rolle Schema-Rechte aufgezwungen.

Dann las ich die reale Systemspur auf dem VPS: *„Running as unit: welt-api-shadow-flex-api.service“*, danach die 200er von `/health`, `/metrics` und `/groups`. Der direkte Peer-Check sagte `flex_api|flex_api|flextrawurst|False` — der Prozess ist nicht nur äußerlich umbenannt, sondern kommt tatsächlich als eigene Datenbankidentität an.

## Was ich verstehe

Die API ist ein historisch gewachsener Gateway mit zu vielen Verantwortungen: öffentliche Reads, Auth, Admin-Schreibpfade, Gruppen, Wesen, Dateien, externe Flarum-/Webzugriffe und interne Streams. Ein blindes `User=flex_api` hätte daher nur den Linux-Benutzer geändert und gleichzeitig Startpfade oder Dateien beschädigt.

Die tragfähige erste Schicht ist jetzt klar: Prozess als dynamischer, nicht privilegierter Benutzer; DB über Unix-Peer-Auth; kein Schema-`CREATE`; Events nur append-only; schreibbare Dateibereiche explizit. Der API-Code darf weiterhin breit sein, aber der Prozess hat nicht mehr die Reichweite von `root`.

## Was ich nicht verstehe

Die API enthält weiterhin Sonderpfade, die `/root/.claude`, Nginx-Reload-Grenzen, Uploads und Codewesen-Dateien berühren. Die neuen Sandbox-Grenzen machen diese Pfade absichtlich nicht mehr zu Root-Fähigkeiten, aber noch ist nicht einzeln geprüft, welche Admin-Oberflächen dadurch erwartbar mit Fehler antworten.

Auch die genaue Herkunft des alten Desktop-Abbruchs bleibt außerhalb dieser Spur: Die Logs zeigen eine getrennte SSH-/logind-Sitzung, aber keinen einzelnen Auslöser für deren Trennung. Das ist eine eigene Diagnose, nicht heimlich Teil der API-Isolation.

## Was mich interessiert

Mich interessiert, ob die große API als nächstes in einen echten öffentlichen Gateway und wenige privilegierte Helfer zerlegt werden kann. Besonders der Crawlkey-/Nginx-Pfad ist ein guter Kandidat für einen kleinen, streng begrenzten Dienst statt für eine Fähigkeit des HTTP-Prozesses.

## Was zusammenhängt und wie

Die DB-Identität, die Unit-Sandbox und der DDL-Abzug hängen direkt zusammen: Erst wenn `flex_api` keine Schema-Rechte braucht, kann `ProtectSystem=strict` und die Prozessisolierung ehrlich sein. Die Migration `/root/werkraum/welt/migrate_welt_api_service_role_20260918.sql` ist deshalb nicht nur Datenbankpflege, sondern der Vertrag zwischen API-Code und Systemd.

Die schon isolierten Dienste `/root/werkraum/welt/bruecke.py` und `/root/werkraum/welt/splitter_daemon.py` bilden die Vorlage: eigene Peer-Rollen, DynamicUser, kein Capability-Set, Journal statt schreibbarer Projektlogs. Die API ist nun dieselbe Schicht, nur mit den tatsächlich benötigten Netzwerkfamilien und Upload-Schreibpfaden.

## Was konzeptionell darin steht

Sicherheit heißt hier nicht, das System zu verkleinern oder seine Herkunft zu löschen. Sie heißt, jede Macht an den Ort zurückzugeben, an dem sie gebraucht wird: Datenbankmigration beim Administrator, HTTP-Lesen/Schreiben beim Gateway, Nginx-/Crawlkey-Steuerung bei einem späteren Helper.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie leicht eine scheinbar harmlose Start-DDL die gesamte Rollenarchitektur bestimmt. Der gefährlichste Satz war nicht irgendein SQL-Update, sondern die implizite Annahme, dass ein laufender Webprozess jederzeit Tabellen anlegen darf.

## Was mich noch beschäftigt

Die Rolle `flex_api` besitzt für die aktuelle API weiterhin viele Tabellenrechte, weil die API selbst noch viele Schreibverantwortungen trägt. Das ist ein sinnvoller Zwischenstand, aber noch nicht das letzte Least-Privilege-Ziel.

## Tiefer eingetaucht

Der Shadow-Test mit der alten DB-Umgebung wäre als Beweis unvollständig gewesen. Deshalb wurde der zweite Schatten ausdrücklich mit `dbname=flextrawurst user=flex_api host=/var/run/postgresql` gestartet. Erst der direkte Peer-Check und die Live-Metriken haben die Identität und den Datenzugriff gemeinsam belegt.

Die Migration wurde zuerst innerhalb `BEGIN ... ROLLBACK` gegen die echte Datenbank geprüft und danach angewendet. Das ist die kleine, aber wichtige Naht zwischen Quelltext und Live-System.

## Wie sich dieser Tag / diese Session angefühlt hat

Es fühlte sich zuerst wie Aufräumen nach einem Stromausfall an: zwei Sessions, tote Terminals, fremde Änderungen im großen Werkraum. Dann wurde die Spur wieder schmal. Als `/groups` im isolierten Schatten 200 sagte, war aus der Reparatur ein belastbarer Übergang geworden.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/db_runtime.py` existiert, damit fehlende Laufzeitkonfiguration nicht mehr still auf ein bekanntes Passwort zurückfällt. `/root/werkraum/welt/migrate_welt_api_service_role_20260918.sql` existiert, damit Schemaaufbau nicht im Requestprozess geschieht. `/root/werkraum/_codex/tools/systemd/welt-api-isolated.service` existiert als reproduzierbare Form der live geschalteten Grenze.

## Was ich beim Bauen brauche

Ich brauche vor jedem weiteren Schnitt die betroffenen DB-Tabellen, die Dateipfade und den realen Aufrufweg. Die API darf nicht aus Bequemlichkeit wieder eine alte Root-Umgebung erben. Ein neuer Schreibpfad braucht eine explizite Migration oder einen klar begrenzten Helper.

## Was noch fehlt bevor wir bauen können

Für die nächste Stufe fehlt eine Route-für-Route-Liste der Pfade, die unter `flex_api` absichtlich nicht funktionieren dürfen oder in einen Helper wandern müssen. Ebenso fehlt ein sauberer Test für die privilegierten Admin-Funktionen, ohne ihnen wieder globale Systemrechte zu geben.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Eine Machtkarte, in der jede Fähigkeit sichtbar einem Besitzer und einer Grenze zugeordnet ist. Lesen, Schreiben, Migration und Systemsteuerung sind verschiedene Schichten; kein Prozess soll nur deshalb alles dürfen, weil er historisch zuerst gestartet wurde.

**Code-Skizze:**

```sql
CREATE ROLE flex_api LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
GRANT USAGE ON SCHEMA public TO flex_api;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO flex_api;
GRANT INSERT ON events TO flex_api;
-- weitere DML-Rechte nur als geprüfte API-Tabelle;
-- kein UPDATE/DELETE auf events.
```

```python
DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "dbname=__flextrawurst_db_uri_required__ user=__missing_runtime_config__",
)
```

## Was ich mir merken will

Die 200 auf `/health` beweist nur Prozessstart. Die 200 auf `/metrics` beweist DB-Lesen. `current_user=flex_api` plus `has_schema_privilege(..., 'CREATE')=False` beweist die entscheidende Grenze. Diese Belege gehören zusammen.

## Dokumente gehören zusammen

Zusammengehören `/root/werkraum/welt/db_runtime.py`, `/root/werkraum/welt/migrate_welt_api_service_role_20260918.sql`, `/root/werkraum/_codex/tools/systemd/welt-api-isolated.service`, `/root/werkraum/_codex/berichte/2026-09-18-welt-api-isolation-inventar.md` und die vorherigen Isolationseinträge zu Brücke und Splitter. Die alte Unit-Kopie `/etc/systemd/system/welt-api.service.pre-isolation-20260918` ist Rollback-Beleg, nicht neue Quelle.

## Was mich überrascht hat

Die laufende API wurde ohne Downtime-Zielwechsel auf Port 8030 neu gestartet und kam mit `flex_api` direkt hoch. Der Gruppenrouter, der vorher Schema-`CREATE` verlangte, lief nach dem DDL-Abzug unverändert als Lesepfad weiter.

## Wenn wir das bauen

**Vision-Schicht:** Der Gateway soll eine ehrliche Grenze sein: genug Kraft für die Welt, keine heimliche Hand am ganzen Host. Privilegierte Bewegungen sollen als sichtbare, kleine Übergänge zwischen Diensten erscheinen.

**Code-Skizze:**

```ini
[Service]
DynamicUser=yes
User=flex_api
ProtectSystem=strict
ProtectHome=read-only
NoNewPrivileges=yes
CapabilityBoundingSet=
InaccessiblePaths=/root/werkraum/.agent
ReadWritePaths=/root/werkraum/uploads /root/werkraum/codewesen
ExecStart=/usr/bin/env FLEXTRAWURST_DB_URI=dbname=flextrawurst\ user=flex_api\ host=/var/run/postgresql ...
```

Als nächstes wären ein read-only/privileged Helper-Vertrag, route-spezifische Smoke-Tests und eine reviewed ACL-Verfeinerung sinnvoll. Nicht sinnvoll wäre, den Gateway wieder pauschal zu erweitern.

## Resonanz

[[abwurf: Die Grenze wurde nicht dadurch echt, dass der Prozess anders hieß, sondern dadurch, dass er mit weniger Möglichkeiten trotzdem noch antworten konnte.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegen PostgreSQL und die append-only Ereignisspur. Darauf liegen die Peer-Rollen `flex_bridge`, `flex_splitter` und `flex_api`. Darüber liegen die isolierten Systemd-Prozesse. Erst darüber liegen öffentliche HTTP-Routen und die später abzutrennenden privilegierten Helfer. Die Herkunft bleibt sichtbar, aber die alte Root-Abkürzung ist aus dem API-Laufweg herausgenommen.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „gogogo“ war hier keine Einladung zum blinden Umbau, sondern die Freigabe, die bereits rekonstruierte Sicherheitslinie zu Ende zu führen. Der konkrete Anschluss war: Shadow beenden, DDL entkoppeln, Peer-Rolle beweisen, live schalten, smoke-testen.

## Vergessen-Wollen

Vergessen werden darf die Versuchung, den Desktop-Abbruch und die API-Isolation zu einer einzigen Ursache zu vermischen. Ebenso darf die alte Root-Unit nicht als aktuelle Realität weitergedacht werden: live ist jetzt die isolierte Unit, die Kopie ist nur Rückweg.

## Was fehlt noch

Offen bleiben die route-spezifische Aufteilung der Admin-/Crawlkey-Fähigkeiten, die Bereinigung der historischen DB-Environment-Drop-ins nach einem ausdrücklich geprüften Rollback-Fenster und die fehlende `graphify`-CLI in dieser Shell. Die aktuelle Sicherheitsstufe ist live und geprüft; die nächste Stufe braucht neue Belege, nicht bloß mehr Rechte.
