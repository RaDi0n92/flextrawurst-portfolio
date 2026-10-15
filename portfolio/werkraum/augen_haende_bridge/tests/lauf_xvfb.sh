#!/bin/sh
# Führt Tests mit echten GTK-Fenstern NUR in einer eigenen, privaten Xvfb aus – nie auf dem Desktop des Benutzers.
# Aufruf: sh tests/lauf_xvfb.sh <unittest-Argumente>   z. B.  sh tests/lauf_xvfb.sh test_koerper_ampel_bedienung
cd "$(dirname "$0")" || exit 1
NR=$((200 + $$ % 700))
Xvfb ":$NR" -screen 0 1280x800x24 >/dev/null 2>&1 &
XPID=$!
trap 'kill $XPID 2>/dev/null' EXIT INT TERM
sleep 1.5
DISPLAY=":$NR" BRIDGE_TEST_XVFB=1 PYTHONPATH=../src:.. python3 -m unittest "$@"
