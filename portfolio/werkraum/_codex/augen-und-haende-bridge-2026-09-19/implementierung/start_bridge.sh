#!/usr/bin/env bash
# Augen & Hände Desktop Bridge — Starter für Virtueller Desktop 1
# Pfad: /root/werkraum/_gemini/windows_bridge/start_bridge.sh

set -e

DIR="/root/werkraum/_gemini/windows_bridge"
SERVER_LOG="$DIR/bridge_server.log"
GUI_LOG="$DIR/copilot_gui.log"

export DISPLAY="${DISPLAY:-:1}"

echo "=== STARTE AUGEN & HÄNDE DESKTOP BRIDGE AUF $DISPLAY ==="

# 1. Altes beenden falls vorhanden
pkill -f "$DIR/transcript_streamer.py" 2>/dev/null || true
pkill -f "$DIR/bridge_server.py" 2>/dev/null || true
pkill -f "$DIR/client_windows/windows_copilot_gui.py" 2>/dev/null || true
sleep 0.5

# 2. Bridge WebSocket Server starten
echo "[1/4] Starte WebSocket Server (Port 9880)..."
setsid nohup python3 "$DIR/bridge_server.py" < /dev/null > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!
sleep 1.0

# Prüfen ob Port 9880 aktiv ist
if ! ss -tulpn | grep -q 9880; then
    echo "[FEHLER] Server konnte nicht auf Port 9880 starten! Siehe $SERVER_LOG"
    exit 1
fi
echo "✓ Server läuft (PID: $SERVER_PID, Port: 9880)"

# 3. Tkinter Copilot HUD starten auf DISPLAY=:1
echo "[2/4] Starte Tkinter Copilot HUD und Physische Raute auf $DISPLAY..."
DISPLAY="$DISPLAY" setsid nohup python3 "$DIR/client_windows/windows_copilot_gui.py" < /dev/null > "$GUI_LOG" 2>&1 &
GUI_PID=$!
sleep 1.5

# Prüfen ob Tkinter Fenster existiert
WIN_ID=$(xdotool search --name "Windows HUD" 2>/dev/null | head -n 1 || true)
if [ -n "$WIN_ID" ]; then
    echo "✓ Tkinter HUD Fenster ist sichtbar auf $DISPLAY! (X11 Window-ID: $WIN_ID, PID: $GUI_PID)"
else
    echo "⚠️ Fenster noch nicht im Window-Manager registriert, prüfe Log: $GUI_LOG"
fi

# 4. Live Transcript & Thinking Streamer starten
echo "[3/4] Starte Live Transcript & Thinking Streamer..."
setsid nohup python3 "$DIR/transcript_streamer.py" < /dev/null > "$DIR/transcript_streamer.log" 2>&1 &
STREAMER_PID=$!
echo "✓ Transcript Streamer läuft (PID: $STREAMER_PID)"

echo "=== BRIDGE ERFOLGREICH GESTARTET! (Raute bleibt still bis zu aktivem Signal) ==="
