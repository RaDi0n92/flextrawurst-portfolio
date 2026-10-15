# Betrieb

## Dienste

- `worldwords-antibibel.service`: Gunicorn auf `127.0.0.1:18093`
- `worldwords-antibibel-backup.timer`: täglicher atomarer Backupdurchlauf
- PostgreSQL-Datenbank: `worldwords_antibibel`
- Testdatenbank: `worldwords_antibibel_test`

## Standardbefehle

```bash
systemctl status worldwords-antibibel.service
journalctl -u worldwords-antibibel.service -n 100 --no-pager
curl -fsS https://flextrawurst.de/WORLDwordsANTIbibel/health/

sudo -u worldwords .venv/bin/python manage.py migrate
sudo -u worldwords .venv/bin/python manage.py collectstatic --noinput
systemctl restart worldwords-antibibel.service

systemctl start worldwords-antibibel-backup.service
systemctl list-timers worldwords-antibibel-backup.timer --all
```

## Backup und Rücklesung

Jeder Backupordner enthält:

- `database.dump` im PostgreSQL-Custom-Format
- `media.tar.gz`
- den aktuellen öffentlichen Snapshot
- `SHA256SUMS`
- `BACKUP_INFO.txt`

Prüfung:

```bash
cd backups/<zeitstempel>
sha256sum -c SHA256SUMS
pg_restore --list database.dump
```

Ein Restore wird zuerst in eine neue Datenbank durchgeführt und geprüft. Niemals ungeprüft über die Produktionsdatenbank schreiben.

## Veröffentlichung

```bash
sudo -u worldwords .venv/bin/python manage.py export_public_registry --mirror-open-source
```

Der Export enthält keine E-Mail-Adressen, Passwortdaten, privaten Nachrichten oder internen Moderationsnotizen.

## Adminzugang

Der initiale Daniel-Zugang liegt ausschließlich auf dem Server in `secrets/admin-initial-credentials.txt`. Das Passwort wird nicht in Git, Berichte oder öffentliche Exporte geschrieben. Nach der ersten persönlichen Anmeldung wird es über die Website geändert.
