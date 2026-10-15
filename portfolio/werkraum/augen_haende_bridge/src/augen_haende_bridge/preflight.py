"""Honest, side-effect-free G01 platform preflight.

This reports what the current host can prove without pretending to be a
Windows desktop or a user's live KDE session.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Probe:
    name: str
    status: str
    detail: str


def _which(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def collect_probes() -> list[Probe]:
    system = platform.system()
    probes: list[Probe] = [
        Probe("host.os", "available", f"{system} {platform.release()} ({platform.machine()})"),
    ]

    if system == "Windows":
        probes.append(Probe("windows.native_runner", "available", "running on Windows"))
    else:
        probes.append(Probe(
            "windows.native_runner", "not_proven",
            "current host is not Windows; native EXE launch still requires a Windows run",
        ))

    pyinstaller = _which("pyinstaller") or ("python-module" if importlib.util.find_spec("PyInstaller") else None)
    probes.append(Probe(
        "windows.packager.pyinstaller",
        "available" if pyinstaller else "not_proven",
        pyinstaller or "PyInstaller is not installed on this host",
    ))

    probes.append(Probe(
        "native.overlay.entrypoint",
        "available" if importlib.util.find_spec("tkinter") else "not_proven",
        "Tkinter import is available; actual native window behavior still needs a display",
    ))

    display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    desktop = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION")
    qdbus = _which("qdbus6", "qdbus")
    probes.append(Probe(
        "kde.live_session",
        "available" if qdbus and display else "not_proven",
        f"qdbus={qdbus or 'missing'}, display={display or 'missing'}, desktop={desktop or 'unknown'}",
    ))

    probes.append(Probe(
        "original.terminal.readback",
        "not_proven",
        "requires the live terminal/session selected by Daniel; no process is attached by preflight",
    ))

    websockets = importlib.util.find_spec("websockets")
    probes.append(Probe(
        "transport.websocket_dependency",
        "available" if websockets else "not_proven",
        "Python websockets module is importable" if websockets else "websockets module is missing",
    ))

    probes.append(Probe(
        "native.window.evidence",
        "not_proven",
        "requires a real Windows desktop capture/click/focus/DPI/stop run",
    ))
    return probes


def main() -> int:
    parser = argparse.ArgumentParser(description="Report G01 bridge prerequisites without side effects")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    probes = collect_probes()
    if args.json:
        print(json.dumps([asdict(probe) for probe in probes], indent=2))
    else:
        for probe in probes:
            print(f"{probe.status.upper():12} {probe.name}: {probe.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
