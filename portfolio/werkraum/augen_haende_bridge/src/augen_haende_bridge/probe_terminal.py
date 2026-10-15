"""Lifecycle helper for an isolated real Konsole probe target."""

from __future__ import annotations

import os
import json
from pathlib import Path
import re
import select
import socket
import subprocess
import sys
import tempfile
import time

from .terminal_adapter import (
    KonsoleAdapter,
    TerminalProbeDelivery,
    TerminalSessionRef,
    build_probe_command,
)


PTY_WRAPPER = r'''
import fcntl
import json
import os
import pty
import selectors
import socket
import struct
import sys
import termios
import time

socket_path = sys.argv[1]
control_path = sys.argv[2]

def connect(path):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    for _ in range(100):
        try:
            client.connect(path)
            return client
        except OSError:
            time.sleep(0.05)
    raise SystemExit("probe controller unavailable")

client = connect(socket_path)
control = connect(control_path)

child_pid, master = pty.fork()
if child_pid == 0:
    os.execv("/bin/bash", ["/bin/bash", "--noprofile", "--norc"])

selector = selectors.DefaultSelector()
selector.register(master, selectors.EVENT_READ, "pty")
selector.register(client, selectors.EVENT_READ, "socket")
selector.register(control, selectors.EVENT_READ, "control")
control_buffer = bytearray()
while True:
    for key, _mask in selector.select():
        if key.data == "pty":
            data = os.read(master, 4096)
            if not data:
                raise SystemExit(0)
            # Keep Konsole's native presentation alive while also exposing
            # the same raw VT bytes to the bridge controller.
            os.write(1, data)
            client.sendall(data)
        elif key.data == "socket":
            data = client.recv(4096)
            if not data:
                raise SystemExit(0)
            os.write(master, data)
        elif key.data == "control":
            data = control.recv(4096)
            if not data:
                raise SystemExit(0)
            control_buffer.extend(data)
            while b"\n" in control_buffer:
                line, _, remainder = control_buffer.partition(b"\n")
                control_buffer = bytearray(remainder)
                try:
                    message = json.loads(line.decode("utf-8"))
                    if message.get("op") != "resize":
                        raise ValueError("unsupported_control_operation")
                    rows = int(message["rows"])
                    cols = int(message["cols"])
                    if rows <= 0 or cols <= 0 or rows > 1000 or cols > 1000:
                        raise ValueError("invalid_terminal_dimensions")
                    fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
                    observed = struct.unpack("HHHH", fcntl.ioctl(master, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)))
                    response = {"status": "observed", "rows": observed[0], "cols": observed[1]}
                except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
                    response = {"status": "failed", "error": str(exc)}
                control.sendall((json.dumps(response, sort_keys=True) + "\n").encode("utf-8"))
'''


class IsolatedProbeTerminal:
    """Starts only the terminal it owns and can therefore close it again."""

    def __init__(self, adapter: KonsoleAdapter) -> None:
        self.adapter = adapter
        self.process: subprocess.Popen[bytes] | None = None
        self.ref: TerminalSessionRef | None = None
        self._baseline: set[tuple[str, str]] = set()
        self._temp_dir: Path | None = None
        self._server: socket.socket | None = None
        self._connection: socket.socket | None = None
        self._control_server: socket.socket | None = None
        self._control_connection: socket.socket | None = None
        self._output_buffer = bytearray()

    def start(self, *, timeout_seconds: float = 8.0) -> TerminalSessionRef:
        if self.ref is not None:
            return self.ref
        if not self.adapter.available():
            raise RuntimeError("konsole or qdbus6 unavailable")
        self._baseline = {(ref.service, ref.session_path) for ref in self.adapter.discover()}
        konsole = "/usr/bin/konsole"
        if not Path(konsole).exists():
            raise RuntimeError("/usr/bin/konsole unavailable")
        self._temp_dir = Path(tempfile.mkdtemp(prefix="augen-haende-probe-"))
        socket_path = self._temp_dir / "controller.sock"
        control_path = self._temp_dir / "control.sock"
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(str(socket_path))
        self._server.listen(1)
        self._server.settimeout(0.2)
        self._control_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._control_server.bind(str(control_path))
        self._control_server.listen(1)
        self._control_server.settimeout(0.2)
        environment = os.environ.copy()
        self.process = subprocess.Popen(
            [
                konsole,
                "--separate",
                "--workdir",
                "/tmp",
                "-e",
                sys.executable,
                "-u",
                "-c",
                PTY_WRAPPER,
                str(socket_path),
                str(control_path),
            ],
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if self._connection is None and self._server is not None:
                try:
                    self._connection, _address = self._server.accept()
                except TimeoutError:
                    pass
            if self._control_connection is None and self._control_server is not None:
                try:
                    self._control_connection, _address = self._control_server.accept()
                except TimeoutError:
                    pass
            for ref in self.adapter.discover():
                if (
                    self._connection is not None
                    and self._control_connection is not None
                    and (ref.service, ref.session_path) not in self._baseline
                ):
                    self.ref = ref
                    return ref
            time.sleep(0.2)
        self.close()
        raise RuntimeError("isolated probe terminal did not become discoverable")

    def send_probe(self, *, marker: str) -> TerminalProbeDelivery:
        if not re.fullmatch(r"AUGEN_HAENDE_PROBE_[A-Z0-9_]+", marker):
            raise ValueError("probe marker is not a safe bridge token")
        if self._connection is None:
            return TerminalProbeDelivery(
                marker=marker,
                status="failed",
                method="pty-controller:unix-socket",
                command_shape="printf-split-marker",
                error="probe controller is not connected",
            )
        command = build_probe_command(marker).encode("utf-8")
        try:
            self._connection.sendall(command)
        except OSError as exc:
            return TerminalProbeDelivery(
                marker=marker,
                status="failed",
                method="pty-controller:unix-socket",
                command_shape="printf-split-marker",
                error=str(exc),
            )
        return TerminalProbeDelivery(
            marker=marker,
            status="delivered",
            method="pty-controller:unix-socket",
            command_shape="printf-split-marker",
        )

    def resize(self, *, rows: int, cols: int, timeout_seconds: float = 2.0) -> dict[str, object]:
        """Resize the owned PTY and return the kernel's winsize readback."""

        if rows <= 0 or cols <= 0 or rows > 1000 or cols > 1000:
            raise ValueError("invalid_terminal_dimensions")
        if self._control_connection is None:
            return {
                "status": "failed",
                "method": "pty-controller:control-socket",
                "requested": {"rows": rows, "cols": cols},
                "error": "resize controller is not connected",
            }
        request = (json.dumps({"op": "resize", "rows": rows, "cols": cols}) + "\n").encode("utf-8")
        try:
            self._control_connection.sendall(request)
            readable, _writable, _exceptional = select.select(
                [self._control_connection], [], [], max(0.0, timeout_seconds)
            )
            if not readable:
                return {
                    "status": "failed",
                    "method": "pty-controller:control-socket",
                    "requested": {"rows": rows, "cols": cols},
                    "error": "resize readback timed out",
                }
            response = self._control_connection.recv(4096)
            payload = json.loads(response.decode("utf-8").splitlines()[0])
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, IndexError) as exc:
            return {
                "status": "failed",
                "method": "pty-controller:control-socket",
                "requested": {"rows": rows, "cols": cols},
                "error": str(exc),
            }
        return {
            "method": "pty-controller:control-socket",
            "requested": {"rows": rows, "cols": cols},
            **payload,
        }

    def read_output(self, *, timeout_seconds: float = 0.2) -> bytes:
        """Read raw bytes emitted by the owned PTY without touching Konsole."""

        if self._connection is None:
            return b""
        chunks: list[bytes] = []
        wait = max(0.0, timeout_seconds)
        while True:
            readable, _writable, _exceptional = select.select([self._connection], [], [], wait)
            if not readable:
                break
            try:
                data = self._connection.recv(8192)
            except OSError:
                break
            if not data:
                break
            chunks.append(data)
            wait = 0.0
        output = b"".join(chunks)
        if output:
            self._output_buffer.extend(output)
            if len(self._output_buffer) > 64_000:
                del self._output_buffer[:-64_000]
        return output

    @property
    def output_buffer(self) -> bytes:
        return bytes(self._output_buffer)

    def close(self) -> None:
        process, self.process = self.process, None
        self.ref = None
        connection, self._connection = self._connection, None
        self._output_buffer.clear()
        if connection is not None:
            connection.close()
        control_connection, self._control_connection = self._control_connection, None
        if control_connection is not None:
            control_connection.close()
        server, self._server = self._server, None
        if server is not None:
            server.close()
        control_server, self._control_server = self._control_server, None
        if control_server is not None:
            control_server.close()
        if self._temp_dir is not None:
            socket_path = self._temp_dir / "controller.sock"
            if socket_path.exists():
                socket_path.unlink()
            control_path = self._temp_dir / "control.sock"
            if control_path.exists():
                control_path.unlink()
        if process is None:
            if self._temp_dir is not None:
                self._temp_dir.rmdir()
                self._temp_dir = None
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3.0)
        if self._temp_dir is not None:
            self._temp_dir.rmdir()
            self._temp_dir = None
