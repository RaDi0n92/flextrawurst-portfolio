"""Unprivileged client for the crawl-key helper."""

from __future__ import annotations

import json
import os
import socket


SOCKET_PATH = os.environ.get(
    "FLEXTRAWURST_CRAWLKEY_SOCKET",
    "/run/flextrawurst-crawlkey-helper.sock",
)


class CrawlKey:
    def __init__(self, system: str, url_prefix: str):
        self.system = system
        self.url_prefix = url_prefix

    def _request(self, action: str) -> str:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(5)
            connection.connect(SOCKET_PATH)
            connection.sendall(
                (json.dumps({"action": action, "system": self.system}) + "\n").encode("utf-8")
            )
            response = b""
            while not response.endswith(b"\n"):
                chunk = connection.recv(4096)
                if not chunk:
                    break
                response += chunk
                if len(response) > 4096:
                    raise RuntimeError("crawl-key helper response too large")
        if not response:
            raise RuntimeError("crawl-key helper returned no response")
        payload = json.loads(response.decode("utf-8"))
        if not payload.get("ok"):
            raise RuntimeError(payload.get("error", "crawl-key helper failed"))
        return str(payload.get("key", ""))

    def read(self) -> str:
        try:
            return self._request("read")
        except Exception:
            # Reads fail closed like the old file reader: no key means no access.
            return ""

    def crawl_url(self, host: str) -> str:
        return f"https://{host}{self.url_prefix}?key={self.read()}"

    def rotate(self) -> str:
        return self._request("rotate")
