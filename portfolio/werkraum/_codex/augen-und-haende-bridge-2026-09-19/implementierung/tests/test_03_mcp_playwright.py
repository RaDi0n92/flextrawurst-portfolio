#!/usr/bin/env python3
"""
Playwright Verifikationstest für Phase 3: ChatGPT MCP Desktop Bridge
Pfad: /root/werkraum/_gemini/windows_bridge/tests/test_03_mcp_playwright.py
"""

import asyncio
import base64
import io
import json
import os
import subprocess
import sys
import time

from PIL import Image as PILImage, ImageDraw
from playwright.sync_api import sync_playwright

sys.path.insert(0, "/root/werkraum/_gemini/windows_bridge")
from mcp_desktop_bridge import windows_desktop_inspect, windows_desktop_act, windows_desktop_status

PROOF_SCREENSHOT = "/root/werkraum/_gemini/windows_bridge/tests/proof_step3_mcp.png"
SERVER_SCRIPT = "/root/werkraum/_gemini/windows_bridge/bridge_server.py"

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Augen & Hände Bridge — Phase 3 MCP Proof</title>
    <style>
        body { font-family: monospace; background: #0f172a; color: #f8fafc; padding: 20px; }
        h1 { color: #38bdf8; font-size: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .box { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; }
        .pass { color: #4ade80; font-weight: bold; }
        pre { background: #020617; padding: 8px; border-radius: 4px; font-size: 11px; overflow-x: auto; max-height: 200px; }
        #canvas-preview { max-width: 100%; border: 1px solid #38bdf8; border-radius: 4px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>◆ Augen & Hände Bridge — Phase 3 ChatGPT MCP Verifikation</h1>
    
    <div class="grid">
        <div class="box">
            <h3>1. MCP Status & Tool-Handshake</h3>
            <div>Bridge Server: <span id="mcp-status" class="pass">-</span></div>
            <pre id="status-dump">-</pre>
            
            <h3>2. Rauten-Banter via MCP (action="say")</h3>
            <div>Status: <span id="act-say-status" class="pass">-</span></div>
            <pre id="act-say-dump">-</pre>

            <h3>3. Input-Mutation via MCP (action="click")</h3>
            <div>Status: <span id="act-click-status" class="pass">-</span></div>
            <pre id="act-click-dump">-</pre>
        </div>

        <div class="box">
            <h3>4. MCP Desktop Inspect (Tor R6: Clamping)</h3>
            <div>Bildgröße & Payload: <span id="inspect-meta" class="pass">-</span></div>
            <div>Chromium Image Render Test: <span id="render-status" class="pass">BEREIT</span></div>
            <canvas id="canvas-preview"></canvas>
            <pre id="inspect-text">-</pre>
        </div>
    </div>
</body>
</html>
"""

def create_synthetic_frame() -> str:
    """Erzeugt ein synthetisches 1920x1080 Bild mit visuellen Markern für den Test."""
    img = PILImage.new("RGB", (1920, 1080), color="#090d16")
    draw = ImageDraw.Draw(img)
    
    # Gitternetz
    for x in range(0, 1920, 160):
        draw.line([(x, 0), (x, 1080)], fill="#1e293b", width=1)
    for y in range(0, 1080, 90):
        draw.line([(0, y), (1920, y)], fill="#1e293b", width=1)
        
    # Fenster-Simulation (Blender Viewport)
    draw.rectangle([100, 100, 1600, 900], outline="#38bdf8", width=3)
    draw.text((120, 120), "BLENDER VIEWPORT [100, 100, 1600, 900]", fill="#38bdf8")
    
    # Daniel Webcam Inlay Simulation
    draw.rectangle([1650, 850, 1900, 1050], fill="#334155", outline="#4ade80", width=2)
    draw.text((1660, 860), "WEBCAM INLAY", fill="#4ade80")
    
    # Rauten Simulation
    draw.text((1500, 150), "◆ Gemgem [F13]", fill="#00E5FF")
    draw.text((200, 150), "◆ Codex [F14]", fill="#FFD600")
    draw.text((200, 800), "◆ GPT [F17]", fill="#2979FF")
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

async def inject_frame_to_server(frame_b64: str):
    import websockets
    async with websockets.connect("ws://127.0.0.1:9880") as ws:
        await ws.send(json.dumps({
            "type": "register",
            "role": "client",
            "name": "Synthetic_Frame_Injector"
        }))
        await ws.recv() # welcome
        await ws.send(json.dumps({
            "type": "frame_telemetry",
            "timestamp": time.time(),
            "frame_b64": frame_b64,
            "screen_resolution": [1920, 1080],
            "focused_window": {
                "hwnd": 777888,
                "title": "Blender 4.2 - Synthetic Test",
                "rect": [100, 100, 1600, 900]
            },
            "webcam_inlay": {"active": True, "rect": [1650, 850, 250, 200]},
            "autonomous_play": False
        }))
        await ws.recv() # frame_ack

def run_proof():
    print("=== STARTE PLAYWRIGHT BEWEIS FÜR PHASE 3: CHATGPT MCP BRIDGE ===")
    
    # 1. Server starten
    proc = subprocess.Popen([sys.executable, SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.0)
    
    try:
        # 2. Test-Frame injizieren
        synthetic_b64 = create_synthetic_frame()
        asyncio.run(inject_frame_to_server(synthetic_b64))
        print("✓ Synthetischer 1080p-Frame in Bridge Server injiziert.")
        
        # 3. MCP windows_desktop_status testen
        status_res = asyncio.run(windows_desktop_status())
        assert status_res["status"] == "connected", f"MCP Status fehlgeschlagen: {status_res}"
        print("✓ MCP Tool 'windows_desktop_status' erfolgreich verifiziert.")

        # 4. MCP windows_desktop_act (action='say') testen
        say_res = asyncio.run(windows_desktop_act(agent_id="gpt", action="say", text="MCP Beweis: GPT spricht im Fenster!"))
        assert say_res["success"] is True
        assert say_res["action"] == "diamond_say"
        print("✓ MCP Tool 'windows_desktop_act(action=\"say\")' erfolgreich verifiziert.")

        # 5. MCP windows_desktop_act (action='click') testen
        click_res = asyncio.run(windows_desktop_act(agent_id="gpt", action="click", x=500, y=400, hwnd=777888))
        assert click_res["success"] is True
        print("✓ MCP Tool 'windows_desktop_act(action=\"click\")' erfolgreich verifiziert.")

        # 6. MCP windows_desktop_inspect testen
        inspect_res = asyncio.run(windows_desktop_inspect(scope="full", with_webcam=True))
        assert len(inspect_res) == 2, f"Inspect muss [Image, Text] zurückgeben, gab: {len(inspect_res)}"
        mcp_image, summary_text = inspect_res
        assert hasattr(mcp_image, "data"), "Erstes Element muss ein MCP Image Objekt sein!"
        image_bytes = mcp_image.data
        assert len(image_bytes) < 1_500_000, f"Tor R6 verletzt: Payload > 1.5MB ({len(image_bytes)} Bytes)"
        print(f"✓ MCP Tool 'windows_desktop_inspect' liefert Bild ({len(image_bytes)} Bytes < 1.5MB) und Zusammenfassung.")

        # 7. Playwright startet Chromium und rendert das Bild in ein echtes HTML Canvas
        img_b64_out = base64.b64encode(image_bytes).decode("utf-8")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/usr/local/bin/chromium",
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.set_content(HTML_TEMPLATE)
            
            # DOM befüllen und Bild in Canvas zeichnen
            page.evaluate(f"""() => {{
                document.getElementById('mcp-status').textContent = 'ONLINE (Port 9880)';
                document.getElementById('status-dump').textContent = JSON.stringify({json.dumps(status_res)}, null, 2);
                document.getElementById('act-say-status').textContent = 'PASS (3.3s/6.6s)';
                document.getElementById('act-say-dump').textContent = JSON.stringify({json.dumps(say_res)}, null, 2);
                document.getElementById('act-click-status').textContent = 'PASS ([500, 400])';
                document.getElementById('act-click-dump').textContent = JSON.stringify({json.dumps(click_res)}, null, 2);
                
                document.getElementById('inspect-meta').textContent = 'Payload: {len(image_bytes)} Bytes (Tor R6: PASS)';
                document.getElementById('inspect-text').textContent = {json.dumps(summary_text)};
                
                // Bild in Canvas laden
                const canvas = document.getElementById('canvas-preview');
                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = () => {{
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    window.canvasRendered = true;
                }};
                img.src = 'data:image/jpeg;base64,{img_b64_out}';
            }}""")
            
            # Warten bis Canvas gerendert ist
            page.wait_for_function("window.canvasRendered === true", timeout=4000)
            
            # Screenshot aufnehmen
            os.makedirs(os.path.dirname(PROOF_SCREENSHOT), exist_ok=True)
            page.screenshot(path=PROOF_SCREENSHOT)
            print(f"Beweis-Screenshot gespeichert: {PROOF_SCREENSHOT}")
            browser.close()

        print("=== PHASE 3 PLAYWRIGHT BEWEIS ERFOLGREICH BESTANDEN! ===")
        return 0

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    sys.exit(run_proof())
