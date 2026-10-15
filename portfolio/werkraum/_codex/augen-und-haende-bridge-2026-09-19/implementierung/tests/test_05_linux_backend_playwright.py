#!/usr/bin/env python3
"""
Playwright Verifikationstest für Phase 6: Linux VPS Adapter (X11 Desktop)
Pfad: /root/werkraum/_gemini/windows_bridge/tests/test_05_linux_backend_playwright.py
"""

import asyncio
import base64
import json
import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, "/root/werkraum/_gemini/windows_bridge")
sys.path.insert(0, "/root/werkraum/_gemini/windows_bridge/client_linux")
from backend_linux import LinuxCopilotClient

PROOF_SCREENSHOT = "/root/werkraum/_gemini/windows_bridge/tests/proof_step5_linux_backend.png"
SERVER_SCRIPT = "/root/werkraum/_gemini/windows_bridge/bridge_server.py"

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Augen & Hände Bridge — Phase 6 Linux Adapter Proof</title>
    <style>
        body { font-family: monospace; background: #0f172a; color: #f8fafc; padding: 20px; }
        h1 { color: #38bdf8; font-size: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .box { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; }
        .pass { color: #4ade80; font-weight: bold; }
        pre { background: #020617; padding: 8px; border-radius: 4px; font-size: 11px; overflow-x: auto; max-height: 180px; }
        canvas { max-width: 100%; border: 1px solid #38bdf8; border-radius: 4px; background: #000; }
    </style>
</head>
<body>
    <h1>◆ Augen & Hände Bridge — Phase 6 Linux VPS Adapter (X11) Verifikation</h1>
    
    <div class="grid">
        <div class="box">
            <h3>1. X11 Dual-World Symmetrie</h3>
            <div>Display Server: <span id="disp-val" class="pass">-</span></div>
            <div>xdotool Mutation: <span id="xdotool-status" class="pass">-</span></div>
            <pre id="mutation-dump">-</pre>

            <h3>2. 10 Hz Trajectory Engine (X11)</h3>
            <div>Cadence: <span id="cadence-status" class="pass">100ms (10 Hz)</span></div>
            <div>Jitter: <span id="jitter-val">-</span></div>
            <pre id="trajectory-dump">-</pre>

            <h3>3. Rauten-Engine (X11)</h3>
            <div>Status: <span id="diamond-status" class="pass">3.3s Raumbanner / 6.6s Ticker</span></div>
            <pre id="diamond-dump">-</pre>
        </div>

        <div class="box">
            <h3>4. X11 Desktop Frame mit Rauten-Banner</h3>
            <canvas id="canvas-x11"></canvas>
            <div style="font-size:11px; color:#94a3b8; margin-top:5px;">
                Chromium Render-Beweis für DISPLAY=:1
            </div>
        </div>
    </div>
</body>
</html>
"""

def run_proof():
    print("=== STARTE PLAYWRIGHT BEWEIS FÜR PHASE 6: LINUX VPS ADAPTER ===")
    
    # 1. Server starten
    proc = subprocess.Popen([sys.executable, SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.0)
    
    client = LinuxCopilotClient(server_url="ws://127.0.0.1:9880", display=os.environ.get("DISPLAY", ":1"))
    client.start()
    time.sleep(1.0)
    
    try:
        # 2. Test: xdotool Input Mutation
        mut_res = client.execute_x11_mutation({"action": "move", "x": 500, "y": 400})
        assert mut_res["success"] is True, f"xdotool Fehler: {mut_res}"
        print(f"✓ xdotool X11 Mutation auf {client.display} erfolgreich: {mut_res['command']}")

        # 3. Test: 10 Hz Trajectory Burst
        samples = client.capture_trajectory_burst(duration_s=0.5, cadence_s=0.1)
        assert len(samples) == 5, f"Erwartet 5 Samples, war {len(samples)}"
        avg_drift = sum(abs(s["drift_ms"]) for s in samples) / len(samples)
        assert avg_drift < 40.0, f"Drift zu hoch: {avg_drift}ms"
        print(f"✓ 10 Hz Trajectory auf Linux: 5 Samples erfasst, Jitter: {avg_drift:.2f}ms.")

        # 4. Test: Rauten-Banter
        now = time.time()
        client.diamonds["codex"]["banner"] = {
            "text": "Linux X11 Symmetrie bewiesen!",
            "start_time": now,
            "duration": 3.3
        }
        client.diamonds["codex"]["ticker"] = {
            "text": "Linux X11 Symmetrie bewiesen!",
            "start_time": now,
            "duration": 6.6
        }
        b64_frame, h_frame, size_frame = client.compose_and_hash_frame()
        print("✓ Rauten-Banter auf Linux Frame gerendert.")

        # 5. Playwright Verifikation
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/usr/local/bin/chromium",
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.set_content(HTML_TEMPLATE)

            page.evaluate(f"""() => {{
                document.getElementById('disp-val').textContent = '{client.display}';
                document.getElementById('xdotool-status').textContent = 'PASS (xdotool move 500 400)';
                document.getElementById('mutation-dump').textContent = JSON.stringify({json.dumps(mut_res)}, null, 2);
                document.getElementById('jitter-val').textContent = 'Avg Jitter: {avg_drift:.2f} ms';
                document.getElementById('trajectory-dump').textContent = JSON.stringify({json.dumps(samples)}, null, 2);
                document.getElementById('diamond-dump').textContent = JSON.stringify({json.dumps(client.diamonds['codex']['banner'])}, null, 2);

                const canvas = document.getElementById('canvas-x11');
                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = () => {{
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    window.canvasDrawn = true;
                }};
                img.src = 'data:image/jpeg;base64,{b64_frame}';
            }}""")

            page.wait_for_function("window.canvasDrawn === true", timeout=4000)
            os.makedirs(os.path.dirname(PROOF_SCREENSHOT), exist_ok=True)
            page.screenshot(path=PROOF_SCREENSHOT)
            print(f"Beweis-Screenshot gespeichert: {PROOF_SCREENSHOT}")
            browser.close()

        print("=== PHASE 6 PLAYWRIGHT BEWEIS ERFOLGREICH BESTANDEN! ===")
        return 0

    finally:
        client.stop()
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    sys.exit(run_proof())
