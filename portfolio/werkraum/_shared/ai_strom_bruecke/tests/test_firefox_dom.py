import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from ai_strom_bruecke.firefox_dom import FirefoxDomSession, discover_websocket_url


class _VersionHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        payload = json.dumps({"webSocketUrl": "ws://127.0.0.1:9999/session"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        return


def test_firefox_bidi_discovery_prefers_websocket_url():
    server = HTTPServer(("127.0.0.1", 0), _VersionHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert discover_websocket_url("127.0.0.1", server.server_port) == "ws://127.0.0.1:9999/session"
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_firefox_dom_command_requires_connection():
    session = FirefoxDomSession("ws://127.0.0.1:1/session")
    try:
        session.command("browsingContext.getTree")
    except RuntimeError as exc:
        assert "nicht verbunden" in str(exc)
    else:
        raise AssertionError("unverbundener DOM-Befehl wurde akzeptiert")


def test_firefox_dom_input_contract_tracks_holds_and_release():
    session = FirefoxDomSession("ws://unused")
    calls = []

    def command(method, params=None):
        calls.append((method, params or {}))
        return {}

    session.command = command
    session.pointer_down("ctx", 10, 20, "middle")
    session.pointer_move("ctx", 15, 25)
    session.key_down("ctx", "w")
    assert session.held_buttons == {"middle"}
    assert session.held_keys == {"w"}
    session.release_actions("ctx")
    assert session.held_buttons == set()
    assert session.held_keys == set()
    assert [item[0] for item in calls] == [
        "input.performActions",
        "input.performActions",
        "input.performActions",
        "input.releaseActions",
    ]
