# AGI-Strom Windows Bridge

Dieses Modul verbindet externe AI-Ströme (Gemini, Codex, Claude, Kimi, GPT) vom Linux-VPS direkt mit Daniels physischem Windows-Laptop.

## Systemdokumentation
Die vollständige System- und Architektur-Dokumentation liegt unter:
[`/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`](file:///root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md)

## Hauptkomponenten

1. **`bridge_server.py`:**
   * WebSocket-Server auf dem VPS (Standard-Port 9880).
   * Empfängt Desktop-Frames, Webcam-Streams, Window-Trees und Regie-Events.
   * Sendet Gedankenströme, Tool-Logs und Klick-/Tasten-Befehle an den Laptop.

2. **`agent_orchestrator.py`:**
   * Multi-Agent Hub: Koordiniert 1 bis 5+ Agenten (Gemini, Codex, Claude etc.).
   * Rollenvergabe (z. B. Stratege, Executor, Scout, Watcher).

3. **`input_arbitrator.py`:**
   * Control-Lease & Kollisionsschutz.
   * Admin-Prio für Daniel: Jede physische Maus-/Tastaturbewegung von Daniel überschreibt die KI sofort.
   * Trennung zwischen Modus A (Hintergrund-Bedienung via Win32 `PostMessage`) und Modus B (Gemeinsamer Mauszeiger mit Token-Passing für Spiele/Multiplayer).

4. **`harness_engine.py`:**
   * Kreativ-befreiendes Makro- und Aktionssystem für Spiele und Mehrschrittigkeit.
   * State-Machine- und DAG-basierte Aktionsketten mit visueller Vorher/Nachher-Prüfung.

5. **`client_windows/`:**
   * Der Windows-Client (`windows_copilot_gui.py`).
   * Standalone Tkinter/Win32-Anwendung mit HUD, Regieknöpfen, Fenster-Filterung, Live-Webcam PiP und Not-Aus (`F12`).
   * Kann direkt per Python gestartet oder als portable `windows_bridge.exe` ausgeführt werden.
