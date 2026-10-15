"""Browser is a test peer, never presented as the Windows product."""
import asyncio
import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from playwright.async_api import async_playwright, expect

from augen_haende_bridge.transport import Journal, Principal, Relay
from augen_haende_bridge.transport_client import BridgeClient
from augen_haende_bridge.target_registry import PlatformUnavailableAdapter, TargetRegistry
from augen_haende_bridge.terminal_adapter import TerminalSessionRef

EVIDENCE = Path(__file__).parent / "evidence"
HTML = """<!doctype html><meta charset="utf-8"><title>Bridge transport proof</title>
<style>body{background:#17222b;color:#ecf2f4;font:18px sans-serif;padding:32px}
button{padding:12px;margin:8px}pre{white-space:pre-wrap;border:1px solid #678;padding:12px}</style>
<h1>Augen & Hände · Transport-Prüfstand</h1>
<p>ECHTER LOKALER WEBSOCKET · TESTTEILNEHMER · KEIN WINDOWS-OVERLAY</p>
<button id="connect">Verbinden</button><button id="say">Text senden</button>
<button id="refresh">VPS-Ziele lesen</button>
<button id="frame">Testbild senden</button><button id="receipt">Empfang bestätigen</button>
<button id="invalid">Fremdes Ziel prüfen</button><button id="close">Trennen</button>
<pre id="status">getrennt</pre><pre id="result"></pre><pre id="incoming"></pre>
<canvas id="canvas" width="160" height="80"></canvas>
<script>
let ws, welcome, event, counter=0;
const status=document.querySelector('#status'), result=document.querySelector('#result');
document.querySelector('#connect').onclick=()=>{
 ws=new WebSocket(window.PROOF.url);
 ws.onopen=()=>ws.send(JSON.stringify({v:1,kind:'hello',token:window.PROOF.token}));
 ws.onmessage=e=>{let m=JSON.parse(e.data);
  if(m.kind==='welcome'){welcome=m;status.textContent='verbunden: '+m.session_id;}
  else if(m.kind==='event'){event=m;document.querySelector('#incoming').textContent=JSON.stringify(m);}
  else result.textContent=JSON.stringify(m);
 };
 ws.onclose=()=>status.textContent='getrennt';
};
function send(kind,payload,target){ws.send(JSON.stringify({v:1,kind,epoch:welcome.epoch,
 id:'browser-'+(++counter),recipient:welcome.peer_id,target_id:target||welcome.target_id,payload}));}
document.querySelector('#say').onclick=()=>send('say',{text:'Hallo vom Browser-Testpeer'});
document.querySelector('#refresh').onclick=()=>send('target_inventory_request',{scope:'terminals'});
document.querySelector('#invalid').onclick=()=>send('say',{text:'darf nicht ankommen'},'foreign');
document.querySelector('#receipt').onclick=()=>ws.send(JSON.stringify({v:1,kind:'receipt',epoch:welcome.epoch,delivery_id:event.delivery_id}));
document.querySelector('#close').onclick=()=>ws.close();
document.querySelector('#frame').onclick=()=>{let c=document.querySelector('#canvas'),ctx=c.getContext('2d');
 ctx.fillStyle='#39b6b0';ctx.fillRect(0,0,160,80);ctx.fillStyle='#000';ctx.fillText('SYNTHETIC TEST',12,40);
 send('frame',{mime:'image/png',data:c.toDataURL('image/png').split(',')[1],source:'synthetic',captured_at_ms:Date.now(),width:160,height:80});};
</script>"""


async def run():
    with tempfile.TemporaryDirectory(prefix="bridge-proof-") as temp:
        class ProofAdapter:
            def discover(self):
                return [TerminalSessionRef("org.kde.konsole-proof", "/Sessions/1", 77, 88, "bash")]

            def inspect(self, **_kwargs):
                raise AssertionError("proof inventory does not inspect")

        agent_registry = TargetRegistry(ProofAdapter())
        overlay_registry = TargetRegistry(PlatformUnavailableAdapter())
        journal = Journal(Path(temp) / "proof.sqlite")
        desktop_token, agent_token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        relay = Relay([Principal("desktop", desktop_token, "agent", "test-desktop", True, True, False),
                       Principal("agent", agent_token, "desktop", "test-desktop", False, False, True)], journal)
        try:
            # Use the same loopback origin as the relay. Chromium blocks a
            # synthetic public origin reaching 127.0.0.1 via Local Network
            # Access Checks before the WebSocket handshake starts.
            async with relay.listen(origins=[None, re.compile(r"http://127\.0\.0\.1(?::[0-9]+)?")]) as server:
                url = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}"
                async with BridgeClient(url, agent_token) as agent, async_playwright() as pw:
                    binary = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or shutil.which("chromium")
                    browser_options = {"args": ["--no-proxy-server", "--proxy-server=direct://",
                                                 "--proxy-bypass-list=*", "--disable-features=BlockInsecurePrivateNetworkRequests"]}
                    if binary:
                        browser_options["executable_path"] = binary
                    browser = await pw.chromium.launch(**browser_options)
                    page = await browser.new_page(viewport={"width": 1100, "height": 820})
                    page.on("websocket", lambda socket: socket.on("socketerror", lambda error: print("browser websocket error:", error)))
                    page.on("console", lambda message: print("browser console:", message.text))
                    class QuietHandler(SimpleHTTPRequestHandler):
                        def log_message(self, *_args):
                            pass
                    web_root = Path(temp) / "web"
                    web_root.mkdir()
                    (web_root / "index.html").write_text(HTML, encoding="utf-8")
                    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(web_root), **kwargs)
                    http_server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
                    threading.Thread(target=http_server.serve_forever, daemon=True).start()
                    await page.goto(f"http://127.0.0.1:{http_server.server_port}/")
                    await page.evaluate("config => window.PROOF=config", {"url": url, "token": desktop_token})
                    await page.locator("#connect").click()
                    await expect(page.locator("#status")).to_have_text("verbunden: desktop")
                    old_epoch = await page.evaluate("welcome.epoch")
                    await page.locator("#say").click()
                    message = await agent.receive()
                    assert message["payload"]["text"] == "Hallo vom Browser-Testpeer"
                    await expect(page.locator("#result")).to_contain_text('"status":"forwarded"')
                    await agent.confirm_received(message)
                    assert (await agent.receive())["kind"] == "receipt_recorded"
                    await expect(page.locator("#result")).to_contain_text('"status":"received"')
                    await page.locator("#frame").click()
                    frame = await agent.receive()
                    assert frame["event_kind"] == "frame" and frame["payload"]["source"] == "synthetic"
                    import base64
                    assert hashlib.sha256(base64.b64decode(frame["payload"]["data"])).hexdigest() == frame["payload"]["sha256"]
                    await page.locator("#refresh").click()
                    request = await agent.receive()
                    assert request["event_kind"] == "target_inventory_request"
                    assert request["payload"] == {"scope": "terminals"}
                    await expect(page.locator("#result")).to_contain_text('"status":"forwarded"')
                    await agent.confirm_received(request)
                    assert (await agent.receive())["kind"] == "receipt_recorded"
                    await expect(page.locator("#result")).to_contain_text('"status":"received"')
                    inventory = agent_registry.bridge_inventory()
                    inventory_payload = {"request_id": request["id"], **inventory}
                    await agent.publish(
                        "target_inventory",
                        inventory_payload,
                        message_id=f"inventory-{request['id'][-80:]}",
                    )
                    assert (await agent.receive())["status"] == "forwarded"
                    applied_count = overlay_registry.apply_remote_inventory(inventory_payload)
                    assert applied_count == 1
                    assert "bridge-agent:terminal-1" in overlay_registry.records
                    await expect(page.locator("#incoming")).to_contain_text("Original-Terminal 1")
                    await page.locator("#receipt").click()
                    assert (await agent.receive())["status"] == "received"
                    await agent.publish("say", {"text": "Antwort vom Python-Testpeer"}, message_id="python-reply")
                    assert (await agent.receive())["status"] == "forwarded"
                    await expect(page.locator("#incoming")).to_contain_text("Antwort vom Python-Testpeer")
                    await page.locator("#receipt").click()
                    assert (await agent.receive())["status"] == "received"
                    await page.locator("#invalid").click()
                    await expect(page.locator("#result")).to_contain_text("grant_denied")
                    await page.locator("#close").click()
                    await expect(page.locator("#status")).to_have_text("getrennt")
                    # Wait for server-side close handling, not a fixed sleep.
                    for _ in range(100):
                        if "desktop" not in relay.connections:
                            break
                        await asyncio.sleep(.01)
                    assert "desktop" not in relay.connections
                    await page.locator("#connect").click()
                    await expect(page.locator("#status")).to_have_text("verbunden: desktop")
                    assert await page.evaluate("welcome.epoch") != old_epoch
                    rows = journal.db.execute("SELECT sequence,kind,session_id,message_id,status FROM events ORDER BY sequence").fetchall()
                    assert any(row[1] == "message.received" for row in rows)
                    assert any(row[1] == "request.denied" and row[4] == "grant_denied" for row in rows)
                    EVIDENCE.mkdir(exist_ok=True)
                    await page.screenshot(path=str(EVIDENCE / "transport_local_playwright.png"))
                    print(json.dumps({"status": "PASS",
                                      "scope": "local transport; Playwright browser; production inventory producer/consumer",
                                      "producer_targets": len(inventory["targets"]),
                                      "consumer_targets": applied_count,
                                      "events": rows}, ensure_ascii=False))
                    await browser.close()
                    http_server.shutdown()
        finally:
            journal.close()


if __name__ == "__main__":
    asyncio.run(run())
