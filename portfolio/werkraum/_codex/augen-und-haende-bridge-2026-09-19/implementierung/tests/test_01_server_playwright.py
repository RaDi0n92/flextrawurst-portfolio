#!/usr/bin/env python3
"""
Playwright Verifikationstest für Phase 1: Bridge WebSocket Server
Pfad: /root/werkraum/_gemini/windows_bridge/tests/test_01_server_playwright.py
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from playwright.sync_api import sync_playwright

SERVER_SCRIPT = "/root/werkraum/_gemini/windows_bridge/bridge_server.py"
PROOF_SCREENSHOT = "/root/werkraum/_gemini/windows_bridge/tests/proof_step1_server.png"
AUDIT_LOG = "/root/werkraum/_gemini/windows_bridge/windows_bridge_audit.jsonl"
PORT = 9880

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Augen & Hände Bridge — Phase 1 Playwright Proof</title>
    <style>
        body { font-family: monospace; background: #0f172a; color: #f8fafc; padding: 20px; }
        h1 { color: #38bdf8; font-size: 20px; }
        .box { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .success { color: #4ade80; font-weight: bold; }
        .fail { color: #f87171; font-weight: bold; }
        #logs { white-space: pre-wrap; font-size: 12px; height: 150px; overflow-y: auto; background: #020617; padding: 10px; border-radius: 4px; border: 1px solid #1e293b; }
        .diamond-banner { background: rgba(0, 229, 255, 0.2); border: 2px solid #00E5FF; padding: 10px; border-radius: 6px; margin-top: 10px; }
        .diamond-ticker { font-size: 11px; color: #00E5FF; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>◆ Augen & Hände Bridge — Playwright Verifikations-Dashboard (Port 9880)</h1>
    
    <div class="box">
        <div><strong>WebSocket Status:</strong> <span id="ws-status">Verbinde...</span></div>
        <div><strong>Server Zeit:</strong> <span id="srv-time">-</span></div>
        <div><strong>Frame Telemetrie:</strong> <span id="frame-status">-</span></div>
        <div><strong>Rauten-Broadcast:</strong> <span id="diamond-status">-</span></div>
        <div><strong>Click-Cage Test:</strong> <span id="cage-status">-</span></div>
    </div>

    <div id="diamond-container"></div>

    <div class="box">
        <strong>Ereignis-Log:</strong>
        <div id="logs"></div>
    </div>

    <script>
        const logsEl = document.getElementById('logs');
        function log(msg) {
            logsEl.textContent += new Date().toISOString().substring(11, 19) + ' ' + msg + '\\n';
            logsEl.scrollTop = logsEl.scrollHeight;
        }

        const ws = new WebSocket('ws://127.0.0.1:9880');
        window.testResults = {
            connected: false,
            welcomeReceived: false,
            frameArrived: false,
            diamondSayReceived: false,
            clickCageBlocked: false,
            pongReceived: false
        };

        ws.onopen = () => {
            log('WebSocket verbunden zu Port 9880');
            document.getElementById('ws-status').className = 'success';
            document.getElementById('ws-status').textContent = 'VERBUNDEN';
            window.testResults.connected = true;

            // 1. Registrieren als Client
            ws.send(JSON.stringify({
                type: 'register',
                role: 'client',
                name: 'Playwright_Test_Browser'
            }));

            // 2. Ping senden
            ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));

            // 3. Test-Frame senden (1920x1080)
            setTimeout(() => {
                log('Sende Test-Frame Telemetrie...');
                ws.send(JSON.stringify({
                    type: 'frame_telemetry',
                    timestamp: Date.now() / 1000,
                    frame_b64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
                    screen_resolution: [1920, 1080],
                    focused_window: {
                        hwnd: 123456,
                        title: 'Blender 4.2 [Scene.blend]',
                        rect: [100, 100, 1600, 900]
                    },
                    webcam_inlay: { active: true, rect: [1650, 850, 250, 200] },
                    autonomous_play: false
                }));
            }, 300);

            // 4. Rauten-Broadcast testen
            setTimeout(() => {
                log('Sende Rauten-Broadcast (Gemini, 3.3s/6.6s)...');
                ws.send(JSON.stringify({
                    type: 'diamond_say',
                    agent_id: 'gemini',
                    color: '#00E5FF',
                    text: 'Playwright Beweis: 3.3s Raumbanner & 6.6s Ticker aktiv!',
                    banner_duration_s: 3.3,
                    ticker_duration_s: 6.6
                }));
            }, 600);

            // 5. Klick-Käfig Verletzung testen (Koordinate 50,50 liegt außerhalb [100,100,1600,900])
            setTimeout(() => {
                log('Teste Klick-Käfig Verletzung (Punkt 50,50 außerhalb Blender)...');
                ws.send(JSON.stringify({
                    type: 'input_mutation',
                    hwnd: 123456,
                    action: 'click',
                    x: 50,
                    y: 50,
                    button: 'left'
                }));
            }, 900);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            log('Empfangen: ' + data.type);

            if (data.type === 'welcome') {
                window.testResults.welcomeReceived = true;
                document.getElementById('srv-time').textContent = new Date(data.server_time * 1000).toLocaleTimeString();
            }
            if (data.type === 'pong') {
                window.testResults.pongReceived = true;
                log('Pong erfolgreich empfangen!');
            }
            if (data.type === 'frame_ack' || data.type === 'frame_arrived') {
                window.testResults.frameArrived = true;
                document.getElementById('frame-status').className = 'success';
                document.getElementById('frame-status').textContent = 'EMPFANGEN (Hash: ' + (data.frame_hash || data.meta?.frame_hash) + ')';
            }
            if (data.type === 'diamond_say') {
                window.testResults.diamondSayReceived = true;
                document.getElementById('diamond-status').className = 'success';
                document.getElementById('diamond-status').textContent = data.text;
                
                const container = document.getElementById('diamond-container');
                container.innerHTML = `
                    <div class="diamond-banner" style="border-color: ${data.color}">
                        <strong>◆ [${data.agent_id.toUpperCase()}]:</strong> ${data.text}
                        <div class="diamond-ticker">⏱️ Standzeit: ${data.banner_duration_s}s Banner / ${data.ticker_duration_s}s Ticker</div>
                    </div>
                `;
            }
            if (data.type === 'input_rejected' && data.reason === 'click_cage_violation') {
                window.testResults.clickCageBlocked = true;
                document.getElementById('cage-status').className = 'success';
                document.getElementById('cage-status').textContent = 'BLOCKED (Käfig aktiv: [50,50] verworfen)';
                log('Klick-Käfig hat ungültigen Klick korrekt abgewehrt!');
            }
        };

        ws.onerror = (err) => {
            log('WebSocket Fehler: ' + JSON.stringify(err));
            document.getElementById('ws-status').className = 'fail';
            document.getElementById('ws-status').textContent = 'FEHLER';
        };
    </script>
</body>
</html>
"""

def run_proof():
    print("=== STARTE PLAYWRIGHT BEWEIS FÜR PHASE 1: BRIDGE WEBSOCKET SERVER ===")
    
    # 1. Server im Hintergrund starten
    proc = subprocess.Popen([sys.executable, SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.0)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/usr/local/bin/chromium",
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = browser.new_page(viewport={"width": 1024, "height": 768})
            page.set_content(HTML_PAGE)
            
            # Warten bis alle Tests durchlaufen sind (max 4 Sekunden)
            start_wait = time.time()
            passed = False
            while time.time() - start_wait < 4.0:
                results = page.evaluate("window.testResults")
                if (results.get("connected") and 
                    results.get("welcomeReceived") and 
                    results.get("frameArrived") and 
                    results.get("diamondSayReceived") and 
                    results.get("clickCageBlocked") and 
                    results.get("pongReceived")):
                    passed = True
                    break
                time.sleep(0.2)
            
            # Screenshot als unanfechtbaren Beweis aufnehmen
            os.makedirs(os.path.dirname(PROOF_SCREENSHOT), exist_ok=True)
            page.screenshot(path=PROOF_SCREENSHOT)
            print(f"Beweis-Screenshot gespeichert: {PROOF_SCREENSHOT}")
            
            results = page.evaluate("window.testResults")
            print("Playwright Testergebnisse:")
            for k, v in results.items():
                print(f"  - {k}: {'PASS' if v else 'FAIL'}")
                
            browser.close()
            
            assert passed, f"Nicht alle Kriterien erfüllt: {results}"
            print("=== PHASE 1 PLAYWRIGHT BEWEIS ERFOLGREICH BESTANDEN! ===")
            return 0
            
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    sys.exit(run_proof())
