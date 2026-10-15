from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from augen_haende_bridge import (
    MCP_PROVIDER_PROFILES,
    MCPProbeConfig,
    RunStatus,
    known_provider_profile,
    run_mcp_p0,
)


class _MCPHandler(BaseHTTPRequestHandler):
    session_header = "test-session-123"
    include_session = True
    atlas_is_error = False

    def log_message(self, *_args) -> None:
        return

    def do_GET(self) -> None:
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Bearer scope="tools"')
        self.end_headers()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length))
        method = request.get("method")
        if method == "initialize":
            payload = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "test-mcp", "version": "0"},
                },
            }
            self.send_response(200)
            if self.include_session:
                self.send_header("Mcp-Session-Id", self.session_header)
        elif method == "tools/list":
            payload = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"tools": [{"name": "atlas_hybrid_search"}]},
            }
            self.send_response(200)
        elif method == "tools/call":
            payload = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "isError": self.atlas_is_error,
                    "content": [{"type": "text", "text": "ok"}],
                },
            }
            self.send_response(200)
        else:
            payload = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601}}
            self.send_response(404)
        body = json.dumps(payload).encode()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class MCPP0RunnerTests(unittest.TestCase):
    def test_known_provider_profiles_are_non_secret_and_complete(self) -> None:
        self.assertEqual(set(MCP_PROVIDER_PROFILES), {"chatgpt", "codex", "claude", "gemini"})
        for stream in MCP_PROVIDER_PROFILES:
            profile = known_provider_profile(stream)
            self.assertTrue(profile.endpoint.startswith("https://"))
            self.assertEqual(profile.session_mode, "stateless")

    def setUp(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _MCPHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.endpoint = f"http://127.0.0.1:{self.server.server_address[1]}/mcp"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()

    def config(self, **kwargs):
        values = {
            "ai_stream_id": "codex",
            "access_path": "mcp_provider",
            "server_id": "test-mcp",
            "endpoint": self.endpoint,
        }
        values.update(kwargs)
        return MCPProbeConfig(**values)

    def test_runner_blocks_missing_session_id_before_tools_list(self) -> None:
        _MCPHandler.include_session = False
        result = run_mcp_p0(self.config())
        self.assertEqual(result.run.status, RunStatus.BLOCKED)
        self.assertEqual(result.run.last_error, "session_mode_unattested")
        self.assertEqual(result.run.proofs, ["configured", "reachable"])

    def test_runner_blocks_before_atlas_without_bearer_token(self) -> None:
        _MCPHandler.include_session = False
        result = run_mcp_p0(self.config(session_mode="stateless"))
        self.assertEqual(result.run.status, RunStatus.BLOCKED)
        self.assertEqual(result.run.last_error, "atlas_read_requires_bearer_token")
        self.assertEqual(result.run.proofs, ["configured", "reachable", "handshake_succeeded", "tools_list_received"])

    def test_runner_completes_with_session_and_authorized_atlas_read(self) -> None:
        _MCPHandler.include_session = True
        result = run_mcp_p0(self.config(bearer_token="test-only-token"))
        self.assertEqual(result.run.status, RunStatus.COMPLETED)
        self.assertEqual(result.run.session_id, "test-session-123")
        self.assertEqual(result.run.tool_count, 1)
        self.assertEqual(result.run.atlas_tool_name, "atlas_hybrid_search")
        self.assertEqual(result.run.session_mode, "stateful")
        self.assertTrue(result.atlas_content_observed)
        self.assertTrue(result.checked_at.endswith("+00:00"))


if __name__ == "__main__":
    unittest.main()
