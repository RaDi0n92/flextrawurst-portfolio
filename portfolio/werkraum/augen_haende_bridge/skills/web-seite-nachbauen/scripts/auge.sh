#!/bin/sh
# Baut Augen: rendert eine URL oder lokale Datei mit Chromium und legt einen Screenshot ab.
# Aufruf: auge.sh <ziel.png> <url|file://pfad> [breite=1440] [vms=9000] [hoehe=9000]
set -eu

ZIEL="${1:?ziel.png noetig}"
URL="${2:?url noetig}"
BREITE="${3:-1440}"
VMS="${4:-9000}"
HOEHE="${5:-9000}"

for b in chromium chromium-browser google-chrome; do
  command -v "$b" >/dev/null 2>&1 && { BROWSER="$b"; break; }
done
[ -z "${BROWSER:-}" ] && { echo "kein Chromium im PATH: which chromium google-chrome chromium-browser" >&2; exit 2; }

case "$URL" in /*) URL="file://$URL" ;; esac
mkdir -p "$(dirname "$ZIEL")"

"$BROWSER" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=1 --window-size="$BREITE,$HOEHE" \
  --screenshot="$ZIEL" --virtual-time-budget="$VMS" "$URL" 2>/dev/null || true

[ -s "$ZIEL" ] || { echo "Renderer hat nichts geschrieben: $ZIEL" >&2; exit 3; }
echo "$ZIEL $(wc -c < "$ZIEL") bytes  ${BREITE}x${HOEHE} vms=$VMS"