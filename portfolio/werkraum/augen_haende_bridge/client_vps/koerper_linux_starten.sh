#!/bin/sh
# Startet den Körper der Bridge auf einem Linux-Desktop (KDE 1 oder KDE 2): sh koerper_linux_starten.sh kde1 [--selbsttest]
# Läuft im Desktop-Container (vd1 für kde1, vd2 für kde2). Die Zugangsdaten legt der Relay beim ersten Start unter runtime/tokens/ an.
set -eu
ORT="${1:-}"
case "$ORT" in
  kde1|kde2) ;;
  *) echo "Aufruf: $0 kde1|kde2 [--selbsttest]" >&2; exit 2 ;;
esac
shift
HIER="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$HIER")"
export BRIDGE_ORT="$ORT"
export BRIDGE_TOKEN_DATEI="${BRIDGE_TOKEN_DATEI:-$REPO/runtime/tokens/desktop-$ORT.token}"
export PYTHONPATH="$REPO/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m augen_haende_bridge.koerper.haupt_linux --ort "$ORT" "$@"
