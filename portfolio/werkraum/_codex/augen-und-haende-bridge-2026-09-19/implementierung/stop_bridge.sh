#!/usr/bin/env bash
# Augen & Hände Desktop Bridge — Stopp-Skript
# Pfad: /root/werkraum/_gemini/windows_bridge/stop_bridge.sh

DIR="/root/werkraum/_gemini/windows_bridge"

echo "=== STOPPE AUGEN & HÄNDE DESKTOP BRIDGE ==="
pkill -f "$DIR/transcript_streamer.py" 2>/dev/null && echo "✓ Transcript Streamer beendet." || true
pkill -f "$DIR/client_windows/windows_copilot_gui.py" 2>/dev/null && echo "✓ Copilot HUD beendet." || echo "Copilot HUD lief nicht."
pkill -f "$DIR/bridge_server.py" 2>/dev/null && echo "✓ Bridge Server beendet." || echo "Bridge Server lief nicht."
echo "=== ALLES GESTOPPT ==="
