#!/bin/sh
# Ruft das Werkzeug der Bridge auf, egal ob du auf dem Host oder in einem virtuellen Desktop läufst.
# Aufruf: sh bridge.sh test karte   (alles nach dem Skriptnamen geht 1:1 an bridge_cli.py)
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for p in "$SCRIPT_DIR/../../../client_vps/bridge_cli.py" \
         /root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py \
         /vps_root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py; do
  if [ -f "$p" ]; then exec python3 "$p" "$@"; fi
done
echo "bridge_cli.py nicht gefunden. Prüfe, ob du in einem Bridge-Terminal läufst (BRIDGE_TERMINAL_ID gesetzt?)." >&2
exit 3
