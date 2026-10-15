# Welt-Brücke-Isolation — live am 2026-09-18

## Ergebnis

`welt-bruecke.service` läuft live nicht mehr als `root` und verbindet sich nicht mehr als `dak`. Der Prozess läuft als dynamischer systemd-User `flex_bridge`; PostgreSQL bindet denselben Namen über lokale Peer-Authentifizierung an die Rolle `flex_bridge`.

## Implementierung

- Code: `/root/werkraum/welt/bruecke.py` liest `BRUECKE_LOG_DIR` und `BRUECKE_LOG_PATH`, nutzt den neutralen Conninfo-Fallback `dbname=flextrawurst` und schreibt nur noch über den FileHandler.
- Unit-Quelle: `/root/werkraum/_codex/tools/systemd/welt-bruecke-isolated.service`.
- Installierte Unit: `/etc/systemd/system/welt-bruecke.service`.
- Prozessgrenze: `DynamicUser=yes`, `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateTmp=yes`, `PrivateDevices=yes`, eingeschränkte Unix-Sockets und leere Capability-Sets.
- Geheimnisgrenze: `/root/werkraum/.agent` ist für den Dienst unsichtbar. Der bestehende Drop-in `/etc/systemd/system/welt-bruecke.service.d/db-env.conf` bleibt als historische Root-Konfiguration erhalten; `ExecStart` überschreibt die Conninfo vor dem Python-Prozess.
- Log: `/var/log/flextrawurst/welt-bruecke.log`; der frühere doppelte StreamHandler ist entfernt.

## Datenbankgrenze

Die Rolle `flex_bridge` ist `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOREPLICATION` und `NOBYPASSRLS`. Die idempotente Provisionierung steht in `/root/werkraum/welt/migrate_welt_bruecke_service_role_20260918.sql`.

Sie hat `SELECT` sowie die benötigten `INSERT`-/`UPDATE`-Spaltenrechte auf `entity_states` und die benötigten `INSERT`-Spaltenrechte auf `events`. `DELETE`, DDL und Tabellenhoheit sind nicht erteilt; die Eigentümerschaft bleibt bei `dak`.

## Nachweise

1. Der Live-Prozess läuft als `flex_bridge` mit `DynamicUser=yes`.
2. `sudo -u flex_bridge psql 'dbname=flextrawurst user=flex_bridge host=/var/run/postgresql'` liefert `flex_bridge|flextrawurst`.
3. Der Dienststatus ist `active (running)`.
4. Der erste Live-Sync meldete `DB verbunden` und `Sync abgeschlossen — 0 Änderungen`.
5. Die sechs erwarteten Selbstmodell-Dateien sind für den dynamischen User lesbar; der Sync konnte sie ohne Root-Rechte verarbeiten.
6. Die parallele Welt-API blieb aktiv; der laufende Splitter-Dienst wurde nicht verändert.

## Grenzen und Wiederaufnahme

Das ist der zweite isolierte Dienstkörper. `welt-api.service`, GENI, Wesen-Live-Dienste und weitere Daemons laufen weiterhin als `root`; die globale Root-Grenze ist nicht geschlossen. Der alte Root-seitige DB-Environment-Drop-in bleibt eine sichtbare Rückrollspur und muss bei einer späteren systemweiten Provisionierung bewusst entfernt oder migriert werden.

Code-/Unit-/DB-Commit: `639e67c79c`.
