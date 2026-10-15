# Splitter-Physik-Isolation — live am 2026-09-18

## Ergebnis

`splitter-physik.service` läuft live nicht mehr als `root` und verbindet sich nicht mehr als `dak`. Der Prozess läuft als dynamischer systemd-User `flex_splitter`; PostgreSQL bindet denselben Namen über lokale Peer-Authentifizierung an die Rolle `flex_splitter`.

## Implementierung

- Code: `/root/werkraum/welt/splitter_daemon.py` akzeptiert `SPLITTER_LOG_PATH` und enthält keinen Passwort-Fallback mehr; der neutrale Fallback ist `dbname=flextrawurst`.
- DB-Provisionierung: `/root/werkraum/welt/migrate_splitter_service_role_20260918.sql` ist die idempotente Migration für Rolle und Spaltenrechte.
- Unit-Quelle: `/root/werkraum/_codex/tools/systemd/splitter-physik-isolated.service`.
- Installierte Unit: `/etc/systemd/system/splitter-physik.service`.
- Prozessgrenze: `DynamicUser=yes`, `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateTmp=yes`, `PrivateDevices=yes`, `RestrictAddressFamilies=AF_UNIX`, leere Capability-Bounding- und Ambient-Sets.
- Geheimnisgrenze: `/root/werkraum/.agent` ist für den Dienst unsichtbar. Der alte Drop-in `/etc/systemd/system/splitter-physik.service.d/db-env.conf` bleibt als bestehende Herkunft erhalten; `ExecStart` überschreibt die Conninfo vor dem Python-Prozess mit der Peer-Verbindung. Eine spätere Wartung kann diesen alten Drop-in separat entfernen, sobald der Rückrollpfad bewusst festgelegt ist.
- Log: `/var/log/flextrawurst/splitter-physik.log`, über `LogsDirectory=flextrawurst`.

## Datenbankgrenze

Die Rolle `flex_splitter` ist `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOREPLICATION` und `NOBYPASSRLS`. Sie hat nur Zugriff auf die fünf vom Daemon tatsächlich verwendeten Tabellen:

- `SELECT` auf `splitter`, `events`, `splitter_verbindungen`, `gedankenblasen`, `wesen_entwicklung`;
- erforderliche Spaltenrechte für `INSERT` und `UPDATE` auf `splitter`;
- `INSERT` und `splitter_generiert`-Update auf `events`;
- `INSERT` und notwendige Upsert-Updates auf `splitter_verbindungen`;
- Zustandsupdates auf `gedankenblasen` und `wesen_entwicklung`.

`DELETE` ist für alle fünf Tabellen nicht erteilt. Tabellenbesitzer bleibt `dak`; die neue Rolle kann keine DDL-Änderung anlegen.

## Nachweise

1. Der Live-Prozess läuft als `flex_splitter` mit `DynamicUser=yes`.
2. `sudo -u flex_splitter psql 'dbname=flextrawurst user=flex_splitter host=/var/run/postgresql'` liefert `flex_splitter|flextrawurst`.
3. Der Dienststatus ist `active (running)`.
4. Nach dem Neustart liefen mehrere Ticks erfolgreich: `Tick 0`, `Tick 1` und `Tick 2`, jeweils ohne Fehler.
5. Syntaxprüfung von `/root/werkraum/welt/splitter_daemon.py` bestanden.
6. Die dokumentierte Sicherheitsmatrix aus 38 Tests bestanden: Dienstschlüssel, Kontostatus, Dienstrechte, Einsammel-Identität und passive Websocket-Widerrufe.
7. `graphify update .` konnte nicht ausgeführt werden; `graphify` ist in der Arbeitsumgebung nicht installiert.

## Grenzen und Wiederaufnahme

Das ist nur der erste Dienstkörper. `welt-api.service`, GENI, Wesen-Live-Dienste und weitere Daemons laufen weiterhin als `root`; die globale Root-Grenze ist nicht geschlossen. Die PostgreSQL-Rolle wurde live angelegt und ist durch `/root/werkraum/welt/migrate_splitter_service_role_20260918.sql` reproduzierbar dokumentiert. Die Migration muss als PostgreSQL-Administrator ausgeführt werden.

Der alte Conninfo-Drop-in bleibt absichtlich erhalten, damit kein unbestätigter Rückrollpfad gelöscht wird. Er ist keine effektive Datenbankberechtigung des laufenden Python-Prozesses, aber weiterhin eine Root-seitige Konfigurationsspur.

Code-/Unit-Commit: `7d984c12d9`.
Sicherungspunkte davor: `c2353e768a`, `ef24bee6b0`, `3a35e6a6b7`.
