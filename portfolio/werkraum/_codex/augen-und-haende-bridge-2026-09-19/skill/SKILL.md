---
name: augen-und-haende-bridge
description: Vollständige Bau-, Test-, Kompilierungs- und Betriebs-Harness für die AGI-Strom Desktop Bridge zwischen Linux-VPS und Daniels Windows-Laptop (HUD, Single-Frame Webcam-Inlay, Rauten-Anker mit 2-Stufen-Broadcast, Win32/ViGEm Input-Arbitrierung und ChatGPT MCP-Integration).
---

# Augen & Hände Desktop Bridge — Execution-Harness & Bau-Skill

Dieser Skill steuert die modulare Entwicklung, Kompilierung, Verifikation und den operativen Betrieb der **Augen & Hände Desktop Bridge** ([`/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`](file:///root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md)).

Die Bridge verbindet externe AI-Ströme (Gemini, Codex, Claude, Kimi, GPT) direkt mit Daniels physischem Windows-Laptop sowie den Virtuellen Desktops des Linux-VPS.

---

## 1. Fundamente & Kern-Gesetze

1. **Single-Frame-Inlay-Prinzip:**  
   Die Laptop-Webcam wird direkt per OpenCV als Bild-im-Bild (PiP) in den Desktop-Screenshot eingestanzt. Vision-Modelle erhalten **genau ein einziges Bild** mit vollem Raumbezug (Screen + Daniel live in der Ecke).
2. **Rauten-Anker & 2-Stufen-Broadcast:**  
   Jeder Agent besitzt im aktiven Zielfenster eine frei verschiebbare Raute (`◆`) mit Tastatur-/Klickhinweis `[+Enter / Klick]`. Beim Senden erzeugt sie:
   * **Stufe 1 (Raum-Banner):** 3.3 Sekunden Standzeit, fenstergebunden, mit Zugkraft zur Raute, schneller Transparenz-Fade-Out.
   * **Stufe 2 (Rauten-Ticker):** 6.6 Sekunden Standzeit (doppelte Zeit), kleine Schrift direkt neben der Raute für entspanntes Nachlesen.
3. **Input-Trennung (3 Ebenen):**
   * *Ebene 1 (Desktop-Apps):* Win32 `PostMessage(hwnd, WM_..., ...)` — Klicks und Tasten direkt ins Hintergrundfenster ohne Störung von Daniels physischer Maus.
   * *Ebene 2 (Spiele mit Shared Mouse):* Token-Passing / Control-Lease mit visuellem Timer.
   * *Ebene 3 (Spiele mit Gamepads):* Virtuelle Xbox-Controller via ViGEm/vJoy. Bis zu 4 KIs steuern parallele Controller ohne Maus-Kollision.
4. **Hardware-Prio vs. Autonomie-Freigabe:**  
   Standardmäßig entzieht jede physische Mausbewegung von Daniel der KI sofort die Kontrolle (`DANIEL_OVERRIDE`). Wird im HUD `[ Modus: Volle Agenten-Autonomie ]` aktiviert, dürfen KIs ungestört spielen. **Not-Aus bleibt immer `F12` (<1ms Kill-Switch).**
5. **Kein Tab-Wechsel (1:1 Terminal & Konsole):**  
   Das Windows-HUD streamt rohe Shell-Ausgaben (`stdout`/`stderr`), Thinking-Prozesse und Tool-Logs live. Über eine integrierte Eingabeleiste kann Daniel direkt eingreifen.
6. **ChatGPT MCP-Schnittstelle:**  
   ChatGPT kommuniziert über atomare MCP-Tools (`windows_desktop_inspect`, `windows_desktop_act`), verarbeitet Frames rein intern als Base64-JPEG ohne Chatverlauf-Verschmutzung und reagiert auf In-Flight-Folgeaufträge während seiner Live-Denkschleife.
7. **Die 10 Hz (0,1s / 100ms) Visual Evidence Trajectory Engine (Codex Blender-Skill Gesetz):**  
   Übernommen aus [`/config/.agents/skills/blender-live-reference-qa/SKILL.md`](file:///config/.agents/skills/blender-live-reference-qa/SKILL.md): Jede Aktion oder Transition über 100ms wird im 10 Hz Takt (alle 100ms) mit Zeitstempel und Hash gesampelt. Drei Zeugen (visueller Frame, Window-State-Readback, Delta) garantieren lückenlose Verifikation von Cooldowns, Menüs und Animationen, ohne das 8GB-ThinkPad zu überhitzen.
8. **Dual-World Symmetrie (Windows ThinkPad & Linux VPS Virtueller Desktop 1 & 2):**  
   Vollständige Symmetrie zwischen Win32 (`VK_F13..F24`, Desktop Duplication, `PostMessage`) und Linux X11 (`XK_F13..F24`, `DISPLAY=:0` und `:1`, `xdotool`, `XTestFakeKeyEvent`). Die Rauten, die 10 Hz Evidenz und das HUD laufen auf beiden Plattformen identisch.
9. **Das ThinkPad-Sparsamkeits-Gesetz (<60 MB RAM, 0 MB VRAM, 0% Idle-CPU, 1080p Native):**  
   Verbot von schwerfälligem Electron-Slop. Pure Win32/Tkinter Implementierung (<50MB RAM im Ruhezustand). Keine VRAM-Belastung auf Daniels Laptop (2GB VRAM bleiben frei für Spiele/Blender). Event-Driven Snapshots und 10 Hz Burst-Cadence statt Dauer-Streaming-Ofen.
10. **Sub-Frame Cursor Borrowing (12ms Flick) & UI Automation API:**  
   Reagiert eine hardwarebeschleunigte App nicht auf Hintergrund-`PostMessage`, leiht sich die Bridge den Hardware-Cursor für exakt 12 Millisekunden (`SendInput`) und stellt Daniels physische Position noch im selben Frame wieder her. Alternativ wird der OS-Accessibility-Tree (`IUIAutomationInvokePattern`) genutzt.

---

## 2. Bau- und Ausführungs-DAG

```text
[01_VPS_BRIDGE_SERVER] ──► [02_INPUT_ARBITRATOR] ──► [03_CHATGPT_MCP_BRIDGE]
          │                                                    │
          ▼                                                    ▼
[04_WINDOWS_COPILOT_GUI] ◄─────────────────────────────────────┘
          │
          ├──► [05_BUILD_STANDALONE_EXE] (PyInstaller .bat)
          ├──► [06_LINUX_VPS_ADAPTER] (X11 / Virtueller Desktop 1+2)
          └──► [07_AUDIT_AND_LOOPBACK_TEST]
```

---

## 3. Die 7 Phasen & Modul-Spezifikationen

### Phase 1: VPS WebSocket Server (`bridge_server.py`)
* **Pfad:** [`/root/werkraum/_gemini/windows_bridge/bridge_server.py`](file:///root/werkraum/_gemini/windows_bridge/bridge_server.py)
* **Netzwerk:** Async WebSocket Server auf Port `9880`.
* **Aufgaben:**
  * Empfängt Desktop-Frames (JPEG Base64) + Fenster-Metadaten vom Client.
  * Hält Ringpuffer für die letzten 10 Frames für Zero-Latency Vision-Inspektion.
  * Streamt Terminal-Telemetrie und Agenten-Gedanken an das Windows-HUD.
  * Verteilt Regie-Signale (`Weiter so`, `Mach mal`, `Pause`, `Denk neu`) an verbundene CLI-Agenten.

### Phase 2: Input Arbitrator (`input_arbitrator.py`)
* **Pfad:** [`/root/werkraum/_gemini/windows_bridge/input_arbitrator.py`](file:///root/werkraum/_gemini/windows_bridge/input_arbitrator.py)
* **Logik:**
  * **Win32 Message Builder:** Berechnet `lParam = (y << 16) | (x & 0xFFFF)` für relative Fensterkoordinaten.
  * **Click-Cage:** Verwirft Klicks außerhalb der Bounding-Box zugewiesener Fenster.
  * **Lease-Manager:** Vergibt Zeitscheiben bei Shared-Mouse-Betrieb.
  * **ViGEm Controller Manager:** Mappt virtuelle Buttons und Joysticks für bis zu 4 KIs.
  * **Autonomie-Status:** Prüft `autonomous_play`-Flag vs. `F12`-Killswitch.

### Phase 3: ChatGPT MCP Desktop Bridge (`mcp_desktop_bridge.py`)
* **Pfad:** [`/root/werkraum/_gemini/windows_bridge/mcp_desktop_bridge.py`](file:///root/werkraum/_gemini/windows_bridge/mcp_desktop_bridge.py)
* **MCP Tools:**
  1. `windows_desktop_inspect(scope="full|focused", with_webcam=True)`:
     * Rückgabe: `{"content": [{"type": "image", "data": "<base64_jpeg>", "mimeType": "image/jpeg"}, {"type": "text", "text": "Window: Blender, HWND: 12345, Active Diamonds: Gemini, Codex"}]}`
  2. `windows_desktop_act(agent_id="gpt", action="click|type|hotkey|say", x=..., y=..., text=...)`:
     * Führt Aktionen aus oder postet eine Nachricht über die ChatGPT-Raute.

### Phase 4: Windows Copilot GUI (`client_windows/windows_copilot_gui.py`)
* **Pfad:** [`/root/werkraum/_gemini/windows_bridge/client_windows/windows_copilot_gui.py`](file:///root/werkraum/_gemini/windows_bridge/client_windows/windows_copilot_gui.py)
* **Technologie:** Python 3 + Tkinter + MSS + OpenCV + PyWin32.
* **UI-Elemente:**
  1. **Floating HUD:** Kompakte Leiste mit Regie-Knöpfen (`Weiter so`, `Mach mal`, `Go!`, `Warte kurz`, `Pause`, `Denk nach`, `Denk neu`).
  2. **Live Terminal View:** Text-Box mit farbigen ANSI-Logs, `stdout`/`stderr` und Thinking-Output.
  3. **Remote Prompt Eingabe:** Textleiste mit Enter-Trigger zum direkten Absenden.
  4. **Webcam-Overlay:** Frei verschiebbares PiP-Videofenster mit `[X] Webcam-Inlay` Toggle.
  5. **Fenster-Manager:** Checkboxen für aktiven Desktop-Scope (Kompletter Screen vs. selektierte Fenster).
  6. **Rauten-Engine:**
     * Frei verschiebbare Rauten (`◆`) pro Agentenslot mit Label `[+Enter / Klick]`.
     * Render-Engine für das 3.3s-Raumbanner (dynamischer Fade-Out) und den 6.6s-Ticker.

### Phase 5: Executable Build-Script (`build_exe.bat`)
* **Pfad:** [`/root/werkraum/_gemini/windows_bridge/client_windows/build_exe.bat`](file:///root/werkraum/_gemini/windows_bridge/client_windows/build_exe.bat)
* **Befehl:**
  ```bat
  pyinstaller --noconfirm --onedir --windowed --name "AugenUndHaendeBridge" ^
      --add-data "assets;assets" ^
      --hidden-import "websockets" ^
      --hidden-import "mss" ^
      --hidden-import "cv2" ^
      --hidden-import "win32gui" ^
      --hidden-import "win32con" ^
      --hidden-import "win32api" ^
      windows_copilot_gui.py
  ```

### Phase 6: Linux VPS Adapter (`client_linux/backend_linux.py`)
* **Pfad:** [`/root/werkraum/_gemini/windows_bridge/client_linux/backend_linux.py`](file:///root/werkraum/_gemini/windows_bridge/client_linux/backend_linux.py)
* **Technologie:** X11, `xdotool`, `mss` für Linux, Xcomposite Fensteraufnahme.
* Ermöglicht denselben Dual-World Betrieb auf Virtueller Desktop 1 und 2.

### Phase 7: Audit- und Loopback-Test
* Lokaler Testlauf via Loopback-WebSocket (`ws://127.0.0.1:9880`).
* Prüfung der F12-Latenz (<1ms).
* Verifikation der 3.3s / 6.6s Broadcast-Timer.
* Audit-Eintrag in `windows_bridge_audit.jsonl`.

---

## 4. JSON-Protokoll-Spezifikation

### A. Client ➔ Server Frame Telemetrie
```json
{
  "type": "frame_telemetry",
  "timestamp": 1789759200.123,
  "frame_b64": "<base64_data>",
  "screen_resolution": [1920, 1080],
  "focused_window": {
    "hwnd": 983042,
    "title": "Blender [C:\\render\\scene.blend]",
    "rect": [100, 100, 1600, 900]
  },
  "webcam_inlay": {
    "active": true,
    "rect": [1650, 850, 250, 200]
  },
  "autonomous_play": false,
  "active_diamonds": {
    "gemini": {"color": "#00E5FF", "x": 0.85, "y": 0.12},
    "codex": {"color": "#FFD600", "x": 0.15, "y": 0.12}
  }
}
```

### B. Agent ➔ Client Rauten-Broadcast
```json
{
  "type": "diamond_say",
  "agent_id": "gemini",
  "color": "#00E5FF",
  "text": "Shader kompiliert! Nicht anfassen!",
  "banner_duration_s": 3.3,
  "ticker_duration_s": 6.6
}
```

### C. Server ➔ Client Input Mutation
```json
{
  "type": "input_mutation",
  "mode": "post_message",
  "hwnd": 983042,
  "action": "click",
  "x": 450,
  "y": 320,
  "button": "left"
}
```

---

## 5. Die 8 Redteam-Schleusen (R1 bis R8 — Die unerbittliche Härtung gegen Sollbruchstellen)

Bevor eine Code-Zeile als bestanden gilt, muss sie diese 8 Stress-Gates durchlaufen:

* **Tor R1: DPI-Skalierungs- & Koordinaten-Drift (Per-Monitor DPI V2):**  
  *Gefahr:* Auf Windows-Laptops mit 125% oder 150% Skalierung treffen simulierte Klicks meilenweit daneben.  
  *Härtung:* Zwingender Aufruf von `ctypes.windll.shcore.SetProcessDpiAwareness(2)` beim Client-Start. Relative Fenster-Koordinaten werden hardwarenah über `ScreenToClient(hwnd, pt)` verifiziert.
* **Tor R2: UIPI & Rechte-Ebenen-Falle (User Interface Privilege Isolation):**  
  *Gefahr:* Läuft ein Spiel oder Editor als Administrator, verwirft Windows alle `PostMessage`-Aufrufe eines normalen User-Prozesses stillschweigend ohne Fehlermeldung.  
  *Härtung:* Client prüft mit `OpenProcessToken` die Integrity-Level. Läuft das Zielfenster mit Elevated Privileges, warnt das HUD sofort gelb und bietet einen sauberen UAC-Elevate-Restart an.
* **Tor R3: Exclusive Fullscreen vs. DWM-Overlay Trap:**  
  *Gefahr:* Echte DirectX-Exclusive-Fullscreen-Spiele zeichnen an Windows DWM vorbei, wodurch das HUD und die Rauten unsichtbar werden.  
  *Härtung:* Client erkennt Fullscreen-Modi via `GetWindowRect` und schlägt vor, auf „Borderless Windowed“ umzuschalten, oder blendet virtuelle Gamepad-Steuerung ein.
* **Tor R4: Webcam-Inlay Ringpuffer & Memory-Leak-Schutz:**  
  *Gefahr:* 30 FPS Kamera-Captures bei langsamerem Netzwerk stauen unkomprimierte Frames im RAM auf.  
  *Härtung:* Fester Ringpuffer der Größe 1 (`deque(maxlen=1)`). Ältere Frames werden sofort verworfen. Garbage Collector wird proaktiv überwacht.
* **Tor R5: WebSocket-Latenz-Jitter & Disconnect-Recovery:**  
  *Gefahr:* Kurze WLAN-Wackler frieren die Klick-Schleife ein oder erzeugen Phantom-Klicks.  
  *Härtung:* Heartbeat-Ping alle 1.000ms. Bei Verbindungsverlust stoppt der Client alle Klicks in <10ms und schaltet in den sicheren Standby mit Auto-Reconnect.
* **Tor R6: MCP Base64 Payload Clamping für ChatGPT:**  
  *Gefahr:* Zu große 4K-Screenshots sprengen ChatGPTs MCP-Tool-Buffer oder erzeugen Timeouts.  
  *Härtung:* Screenshots werden für MCP deterministisch auf maximal 1920x1080 herunterskaliert und als JPEG mit Qualität 80 komprimiert (<1.5 MB Payload).
* **Tor R7: F12 Hardware Killswitch Latenz-Beweis (<1ms Not-Aus):**  
  *Gefahr:* Wenn ein Python-Thread im GUI-Eventloop hängt, reagiert der Not-Aus nicht rechtzeitig.  
  *Härtung:* `F12` wird über einen dedizierten systemweiten Low-Level-Keyboard-Hook (`WH_KEYBOARD_LL`) abgefangen, der direkt den OS-Injektions-Treiber abwürgt, völlig unabhängig von Tkinter.
* **Tor R8: 3.3s/6.6s Spatial Vector Sync bei Fenster-Verschiebung:**  
  *Gefahr:* Zieht Daniel das Spielfenster während eines laufenden Bannereffekts über den Monitor, bleibt das Banner an den alten Koordinaten kleben.  
  *Härtung:* Das Banner und der Rauten-Ticker sind mathematisch an die relative Position `(rel_x, rel_y)` des Fenster-Handles gekoppelt und wandern im 60Hz-Takt mit dem Fenster mit.

---

## 6. Das Skalpell-Bau-Ritual (Ziegelstein für Ziegelstein, kein Chaos)

Um das gefürchtete „KI-Struktur-Chaoscode-Koma“ vollständig auszuschließen, gilt das eiserne Skalpell-Ritual:

1. **Kein Massen-Dump:** Niemals mehrere Module gleichzeitig ungetestet erzeugen.
2. **Ein Ziegelstein nach dem anderen:**
   * **Schritt 1:** Server (`bridge_server.py`) bauen ➔ isoliert starten ➔ WebSocket Loopback testen ➔ Git Commit.
   * **Schritt 2:** Arbitrator (`input_arbitrator.py`) bauen ➔ Klickberechnung mit Unit-Test prüfen ➔ Git Commit.
   * **Schritt 3:** MCP-Bridge (`mcp_desktop_bridge.py`) bauen ➔ Schema validieren ➔ Git Commit.
   * **Schritt 4:** Windows Copilot GUI (`client_windows/windows_copilot_gui.py`) aufbauen ➔ Tkinter/Inlay prüfen ➔ Git Commit.
   * **Schritt 5:** Build-Script (`build_exe.bat`) & Linux Backend (`backend_linux.py`) fertigstellen ➔ Git Commit.
3. **Datei-Beweis vor Weitergang:** Kein Schritt gilt als abgeschlossen ohne zeilenweisen Terminal-Test oder Exit-Code 0.

---

## 7. Verifikations-Checkliste vor Freigabe

1. **Datei-Beweis:** Jede Datei existiert mit absolutem Pfad unter `/root/werkraum/_gemini/windows_bridge/`.
2. **Failsafe-Check:** Physische Mausbewegung setzt `lockout_until = now() + 2.0s`.
3. **Webcam-Check:** Beim Umschalten des Toggles verschwindet das Inlay im gerenderten Stream ohne Artefakte.
4. **Timing-Check:** Rauten-Banner verschwindet nach exakt 3.3s, der Ticker bleibt bis 6.6s stehen.
5. **No-Naked-Paths:** Alle Berichte und Ausgaben enthalten vollständige absolute Pfade.

