"""Current VPS relay entrypoint for the loopback-only SSH hand-off.

The relay never binds a public interface.  Windows reaches it through an SSH
LocalForward and therefore still connects to 127.0.0.1 from the client side.
This entrypoint starts the terminal launcher beside the relay: it starts only
entries of the start list (starts.json, places in orte.json) in Linux PTYs the
bridge itself holds (decision BE01/BE02). The desktop never sends a command.
The earlier read-only inventory agent keeps answering as before.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import sys
from pathlib import Path

# Allow direct execution from the repository without requiring installation.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from augen_haende_bridge.transport import Journal, Principal, Relay  # noqa: E402
from augen_haende_bridge.bridge_runtime import BridgeRuntime  # noqa: E402
from client_vps.anzeigeorte import Verteiler, baue_principals, lade_desktops  # noqa: E402
from client_vps.bridge_agent import build_inventory_agent  # noqa: E402
from client_vps.terminal_launcher import Launcher, load_orte, load_starts  # noqa: E402


DEFAULT_PORT = 19880
DEFAULT_RUNTIME = _ROOT / "runtime"
DEFAULT_JOURNAL = DEFAULT_RUNTIME / "bridge-relay.sqlite3"
DEFAULT_STARTS = _ROOT / "client_vps" / "starts.json"
DEFAULT_ORTE = _ROOT / "client_vps" / "orte.json"
DEFAULT_DESKTOPS = _ROOT / "client_vps" / "desktops.json"
MIN_TOKEN_LENGTH = 32


def _token(name: str) -> str:
    value = os.environ.get(name, "")
    if len(value) < MIN_TOKEN_LENGTH:
        raise RuntimeError(f"{name} must contain at least {MIN_TOKEN_LENGTH} characters")
    return value


def _spracherkennung():
    """Whisper für Daniels Sprache; fehlt die Bibliothek oder ist BRIDGE_SPRACHERKENNUNG=aus gesetzt, läuft die Bridge ohne (mit Hinweis)."""
    if os.environ.get("BRIDGE_SPRACHERKENNUNG", "").lower() in ("aus", "0", "nein", "off"):
        print("Spracherkennung aus (BRIDGE_SPRACHERKENNUNG)", file=sys.stderr, flush=True)
        return None
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        print("Spracherkennung aus: faster_whisper ist nicht installiert", file=sys.stderr, flush=True)
        return None
    from client_vps.sprache import WhisperTranskriber

    transkriber = WhisperTranskriber()
    print(f"Spracherkennung: Whisper {transkriber.modell} ({transkriber.sprache}), wird beim Start geladen",
          file=sys.stderr, flush=True)
    return transkriber


def build_principals(*, desktop_token: str, agent_token: str) -> tuple[Principal, Principal]:
    """Create the fixed G08 grants without exposing credentials in output."""

    if len(desktop_token) < MIN_TOKEN_LENGTH or len(agent_token) < MIN_TOKEN_LENGTH:
        raise ValueError("strong_tokens_required")
    if desktop_token == agent_token:
        raise ValueError("distinct_tokens_required")
    return (
        Principal(
            "desktop",
            desktop_token,
            "agent",
            "desktop-main",
            can_publish_frames=True,
            can_request_inventory=True,
            can_control_terminals=True,
        ),
        Principal(
            "agent",
            agent_token,
            "desktop",
            "desktop-main",
            can_publish_inventory=True,
            can_serve_terminals=True,
        ),
    )


async def _wait_for_agent(runtime, timeout: float) -> None:
    deadline = asyncio.get_running_loop().time() + timeout
    while not runtime.connected:
        if runtime.failure is not None:
            raise RuntimeError(f"vps_agent_failed: {runtime.failure!r}")
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("vps_agent_connection_timeout")
        await asyncio.sleep(0.05)


def _install_stop_handlers(stop: asyncio.Event) -> list[signal.Signals]:
    loop = asyncio.get_running_loop()
    installed: list[signal.Signals] = []

    def request_stop() -> None:
        stop.set()

    for signal_name in ("SIGINT", "SIGTERM"):
        signal_value = getattr(signal, signal_name, None)
        if signal_value is None:
            continue
        try:
            loop.add_signal_handler(signal_value, request_stop)
        except (NotImplementedError, RuntimeError):
            continue
        installed.append(signal_value)
    return installed


def _report_failures(event: dict[str, object]) -> None:
    if event.get("kind") in {"runtime.failed", "error"}:
        print(json.dumps(event, ensure_ascii=False), flush=True)


async def run_server(
    *,
    port: int,
    journal_path: Path,
    startup_timeout: float,
    starts_path: Path = DEFAULT_STARTS,
    orte_path: Path = DEFAULT_ORTE,
    runtime_dir: Path = DEFAULT_RUNTIME,
    desktops_path: Path | None = DEFAULT_DESKTOPS,
) -> int:
    # G06: mehrere Desktops (Anzeigeorte) aus desktops.json; fehlt die Datei, bleibt es beim einen Desktop von früher.
    desktops = lade_desktops(desktops_path, runtime_dir) if desktops_path is not None and Path(desktops_path).is_file() else None
    if desktops is not None:
        principals = baue_principals(desktops)
        inventar = next((d for d in desktops if d.ort == "windows"), desktops[0])
        agent_token = inventar.agent_token
    else:
        desktop_token = _token("BRIDGE_DESKTOP_TOKEN")
        agent_token = _token("BRIDGE_AGENT_TOKEN")
        principals = build_principals(desktop_token=desktop_token, agent_token=agent_token)
    orte = load_orte(orte_path)
    starts = load_starts(starts_path, orte)

    journal_path.parent.mkdir(parents=True, exist_ok=True)
    journal = Journal(journal_path)
    relay = Relay(principals, journal)
    launcher: Launcher | None = None

    def on_event(event: dict[str, object]) -> None:
        _report_failures(event)
        if launcher is not None:
            launcher.on_event(event)

    verteiler = None
    weitere: dict[str, BridgeRuntime] = {}
    if desktops is not None:
        # Je Desktop eine Verbindung des Starters; Ereignisse tragen den Ort, von dem sie kommen. Windows behält den Inventar-Agenten wie bisher.
        laufzeiten: dict[str, object] = {}
        verteiler = Verteiler(desktops, laufzeiten)
        agent_runtime, _registry = build_inventory_agent(f"ws://127.0.0.1:{port}", agent_token, on_event=verteiler.ereignis_von(inventar.ort, on_event))
        laufzeiten[inventar.ort] = agent_runtime
        for d in desktops:
            if d.ort != inventar.ort:
                weitere[d.ort] = laufzeiten[d.ort] = BridgeRuntime(f"ws://127.0.0.1:{port}", d.agent_token, on_event=verteiler.ereignis_von(d.ort, on_event))
    else:
        agent_runtime, _registry = build_inventory_agent(f"ws://127.0.0.1:{port}", agent_token, on_event=on_event)
    transkriber = _spracherkennung()
    launcher = Launcher(agent_runtime, starts, orte, runtime_dir, transkriber=transkriber, verteiler=verteiler)
    stop = asyncio.Event()
    installed_handlers: list[signal.Signals] = []
    agent_socket = None

    try:
        async with relay.listen(port) as server:
            actual_port = server.sockets[0].getsockname()[1]
            # The agent must use the actual port when --port 0 is used.
            agent_runtime.url = f"ws://127.0.0.1:{actual_port}"
            for weitere_laufzeit in weitere.values():
                weitere_laufzeit.url = f"ws://127.0.0.1:{actual_port}"
            installed_handlers = _install_stop_handlers(stop)
            launcher.start()
            agent_socket = launcher.serve_agents(runtime_dir / "agent.sock")
            agent_runtime.start()
            for weitere_laufzeit in weitere.values():
                weitere_laufzeit.start()  # verbindet sich, sobald der Relay läuft; ein fehlender Desktop stört die anderen nicht
            try:
                await _wait_for_agent(agent_runtime, startup_timeout)
                print(
                    f"Bridge relay ready: ws://127.0.0.1:{actual_port} "
                    f"(loopback-only; terminal launcher and read-only inventory agent connected, "
                    f"{len(starts)} start entries, {len(desktops) if desktops else 1} desktop(s))",
                    flush=True,
                )
                await stop.wait()
            finally:
                await asyncio.to_thread(launcher.shutdown)
                if agent_socket is not None:
                    await asyncio.to_thread(agent_socket.shutdown)
                    agent_socket.server_close()
                await asyncio.to_thread(agent_runtime.stop)
                for weitere_laufzeit in weitere.values():
                    await asyncio.to_thread(weitere_laufzeit.stop)
    finally:
        for signal_value in installed_handlers:
            try:
                asyncio.get_running_loop().remove_signal_handler(signal_value)
            except (RuntimeError, ValueError):
                pass
        journal.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--journal", type=Path, default=DEFAULT_JOURNAL)
    parser.add_argument("--starts", type=Path, default=DEFAULT_STARTS)
    parser.add_argument("--orte", type=Path, default=DEFAULT_ORTE)
    parser.add_argument("--desktops", type=Path, default=DEFAULT_DESKTOPS, help="Desktops (Anzeigeorte); fehlt die Datei, gibt es nur den einen Desktop von früher")
    parser.add_argument("--runtime-dir", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--startup-timeout", type=float, default=10.0)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    if args.startup_timeout <= 0:
        parser.error("--startup-timeout must be positive")
    try:
        return asyncio.run(
            run_server(
                port=args.port,
                journal_path=args.journal,
                startup_timeout=args.startup_timeout,
                starts_path=args.starts,
                orte_path=args.orte,
                runtime_dir=args.runtime_dir.resolve(),
                desktops_path=args.desktops,
            )
        )
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
