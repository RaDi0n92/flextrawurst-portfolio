"""Konsole adapter for the first live Linux target slice.

Discovery and inspection are safe by default. Input delivery is exposed only
as a marked probe primitive; the bridge must still authorize it with its own
lease before calling it.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import shutil
import subprocess
import time
from typing import Callable, Sequence


@dataclass(frozen=True)
class TerminalSessionRef:
    service: str
    session_path: str
    session_pid: int | None
    foreground_pid: int | None
    title: str


@dataclass(frozen=True)
class TerminalDiscovery:
    """One discovery attempt, including whether its result is trustworthy."""

    refs: tuple[TerminalSessionRef, ...]
    status: str
    error: str | None = None


@dataclass(frozen=True)
class TerminalSnapshot:
    target_id: str
    source: str
    availability: str
    status: str
    capture_method: str
    captured_at_ms: int
    session_pid: int | None
    foreground_pid: int | None
    title: str
    output: str
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "target_id": self.target_id,
            "source": self.source,
            "availability": self.availability,
            "status": self.status,
            "capture_method": self.capture_method,
            "captured_at_ms": self.captured_at_ms,
            "session_pid": self.session_pid,
            "foreground_pid": self.foreground_pid,
            "title": self.title,
            "output": self.output,
            "error": self.error,
        }


@dataclass(frozen=True)
class TerminalProbeDelivery:
    marker: str
    status: str
    method: str
    command_shape: str
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "marker": self.marker,
            "status": self.status,
            "method": self.method,
            "command_shape": self.command_shape,
            "error": self.error,
        }


Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def build_probe_command(marker: str) -> str:
    """Build a reversible probe whose full marker is absent from command echo."""

    split_at = max(1, len(marker) // 2)
    left, right = marker[:split_at], marker[split_at:]
    return f"printf '%s%s\\n' '{left}' '{right}'\n"


class KonsoleAdapter:
    """Discover and inspect real KDE Konsole sessions via D-Bus."""

    def __init__(self, *, runner: Runner | None = None, command: str = "qdbus6") -> None:
        self.command = command
        self.runner = runner or self._default_runner

    def _default_runner(self, argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=2.0,
        )

    def available(self) -> bool:
        return shutil.which(self.command) is not None

    def _run(self, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return self.runner([self.command, "--session", *args])

    def _call(self, ref: TerminalSessionRef, method: str, *arguments: str) -> str:
        result = self._run(
            ["--literal", ref.service, ref.session_path, method, *arguments]
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "qdbus call failed").strip())
        value = result.stdout.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        return value

    @staticmethod
    def _integer(value: str) -> int | None:
        try:
            return int(value.strip())
        except (TypeError, ValueError):
            return None

    def discover(self) -> list[TerminalSessionRef]:
        return list(self.discover_result().refs)

    def discover_result(self) -> TerminalDiscovery:
        if not self.available():
            return TerminalDiscovery((), "unavailable", "adapter_not_available")
        try:
            services_result = self._run([])
        except (OSError, subprocess.SubprocessError) as exc:
            return TerminalDiscovery((), "error", str(exc))
        if services_result.returncode != 0:
            return TerminalDiscovery(
                (), "error", (services_result.stderr or services_result.stdout or "service discovery failed").strip()
            )
        services = sorted(
            line.strip()
            for line in services_result.stdout.splitlines()
            if line.strip().startswith("org.kde.konsole-")
        )
        discovered: list[TerminalSessionRef] = []
        failures: list[str] = []
        for service in services:
            try:
                objects = self._run([service])
            except (OSError, subprocess.SubprocessError) as exc:
                failures.append(f"{service}: {exc}")
                continue
            if objects.returncode != 0:
                failures.append(f"{service}: object discovery failed")
                continue
            session_paths = sorted(
                {
                    line.strip()
                    for line in objects.stdout.splitlines()
                    if line.strip().startswith("/Sessions/")
                }
            )
            for session_path in session_paths:
                provisional = TerminalSessionRef(service, session_path, None, None, "")
                try:
                    session_pid = self._integer(
                        self._call(provisional, "org.kde.konsole.Session.processId")
                    )
                    foreground_pid = self._integer(
                        self._call(provisional, "org.kde.konsole.Session.foregroundProcessId")
                    )
                    title = self._call(provisional, "org.kde.konsole.Session.title", "0")
                except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
                    failures.append(f"{service}{session_path}: {exc}")
                    continue
                discovered.append(
                    TerminalSessionRef(service, session_path, session_pid, foreground_pid, title)
                )
        if failures:
            return TerminalDiscovery(tuple(discovered), "degraded", "; ".join(failures[:3]))
        return TerminalDiscovery(tuple(discovered), "ok")

    def inspect(self, *, target_id: str, ref: TerminalSessionRef) -> TerminalSnapshot:
        captured_at_ms = int(time.time() * 1000)
        try:
            output = self._call(
                ref,
                "org.kde.konsole.Session.getAllDisplayedText",
                "true",
            )
            if len(output) > 12_000:
                output = output[-12_000:]
            return TerminalSnapshot(
                target_id=target_id,
                source="real",
                availability="available",
                status="observed",
                capture_method="konsole-dbus:getAllDisplayedText",
                captured_at_ms=captured_at_ms,
                session_pid=ref.session_pid,
                foreground_pid=ref.foreground_pid,
                title=ref.title,
                output=output,
            )
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            return TerminalSnapshot(
                target_id=target_id,
                source="real",
                availability="unavailable",
                status="error",
                capture_method="konsole-dbus:getAllDisplayedText",
                captured_at_ms=captured_at_ms,
                session_pid=ref.session_pid,
                foreground_pid=ref.foreground_pid,
                title=ref.title,
                output="",
                error=str(exc),
            )

    def send_probe(self, *, ref: TerminalSessionRef, marker: str) -> TerminalProbeDelivery:
        """Send one reversible printf probe to an explicitly selected session.

        The marker is deliberately restricted to a safe token. This method is
        not a general terminal or shell API and never accepts arbitrary text.
        """

        if not re.fullmatch(r"AUGEN_HAENDE_PROBE_[A-Z0-9_]+", marker):
            raise ValueError("probe marker is not a safe bridge token")
        command = build_probe_command(marker)
        try:
            self._call(ref, "org.kde.konsole.Session.sendText", command)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            return TerminalProbeDelivery(
                marker=marker,
                status="failed",
                method="konsole-dbus:sendText",
                command_shape="printf-split-marker",
                error=str(exc),
            )
        return TerminalProbeDelivery(
            marker=marker,
            status="delivered",
            method="konsole-dbus:sendText",
            command_shape="printf-split-marker",
        )
