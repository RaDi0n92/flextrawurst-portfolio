from __future__ import annotations

import http.client
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 18108
PUBLIC_HOST = "127.0.0.1"
PUBLIC_PORT = 8879

_started = False
_lock = threading.Lock()
_server: ThreadingHTTPServer | None = None

_HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
}


class AtlasBridgeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _forward(self, *, body: bytes | None = None) -> None:
        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in _HOP_BY_HOP and key.lower() != "host"
        }
        headers["Host"] = f"{BACKEND_HOST}:{BACKEND_PORT}"
        headers["Accept-Encoding"] = "identity"
        connection = http.client.HTTPConnection(BACKEND_HOST, BACKEND_PORT, timeout=120)
        try:
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()
            payload = response.read()
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                if key.lower() in _HOP_BY_HOP or key.lower() == "content-length":
                    continue
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)
        except Exception as exc:
            payload = f"Gesamtatlas-Hauptkörper nicht erreichbar: {exc}".encode("utf-8", errors="replace")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)
        finally:
            connection.close()

    def do_GET(self) -> None:
        self._forward()

    def do_HEAD(self) -> None:
        self._forward()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        self._forward(body=self.rfile.read(length) if length else b"")

    def log_message(self, _format: str, *_args) -> None:
        return


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def ensure_public_bridge() -> bool:
    global _started, _server
    with _lock:
        if _started:
            return True
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if probe.connect_ex((PUBLIC_HOST, PUBLIC_PORT)) == 0:
                _started = True
                return True
        finally:
            probe.close()
        _server = ReusableThreadingHTTPServer((PUBLIC_HOST, PUBLIC_PORT), AtlasBridgeHandler)
        thread = threading.Thread(target=_server.serve_forever, name="gesamtatlas-public-bridge", daemon=True)
        thread.start()
        _started = True
        return True
