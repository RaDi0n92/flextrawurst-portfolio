#!/usr/bin/env bash
set -euo pipefail
umask 027
APP='/root/werkraum/WorldWORDS-ANTIBIBEL-Website'
BACKUPS="$APP/backups"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$BACKUPS/.tmp-$STAMP-$$"
FINAL="$BACKUPS/$STAMP"
mkdir -p "$TMP"
cleanup() { [[ -d "$TMP" ]] && rm -rf "$TMP"; }
trap cleanup EXIT

cd "$APP"
"$APP/.venv/bin/python" manage.py export_public_registry --mirror-open-source
pg_dump --format=custom --compress=9 --file="$TMP/database.dump" worldwords_antibibel
if [[ -d media ]]; then tar -C "$APP" -czf "$TMP/media.tar.gz" media; fi
cp -a exports/public-current "$TMP/public-current"
{
  printf 'created_utc=%s\n' "$STAMP"
  printf 'database=worldwords_antibibel\n'
  printf 'app_version=1.0.0\n'
  printf 'host=%s\n' "$(hostname)"
} > "$TMP/BACKUP_INFO.txt"
(
  cd "$TMP"
  find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)
mv "$TMP" "$FINAL"
trap - EXIT
find "$BACKUPS" -mindepth 1 -maxdepth 1 -type d -name '20????????T??????Z' -mtime +30 -exec rm -rf {} +
printf 'backup=%s\n' "$FINAL"
