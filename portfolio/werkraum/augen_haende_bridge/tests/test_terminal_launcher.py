"""VPS-Starter: echte Linux-PTYs, echter Sprech-Socket, echtes Relay. Keine Attrappen für Prozess, Socket oder Verbindung."""
import asyncio
import base64
import json
import os
import queue
import secrets
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from augen_haende_bridge.bridge_runtime import BridgeRuntime
from augen_haende_bridge.transport import Journal, Principal, Relay
from client_vps import bridge_cli
from client_vps.terminal_launcher import (
    Launcher, Ort, StartEntry, TerminalSession, build_command, load_orte, load_starts, remote_kill,
    ENV_ALLOW, KEEP_FRAMES, MAX_TERMINALS, REMOTE_KILL_SCRIPT,
)

CONFIG = Path(__file__).resolve().parents[1] / "client_vps"
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aE1sAAAAASUVORK5CYII="


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def ev(kind, payload, event_id="e1"):
    return {"kind": "event", "event_kind": kind, "id": event_id, "payload": payload}


def wait_for(predicate, timeout=8.0, step=0.02):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = predicate()
        if value:
            return value
        time.sleep(step)
    return predicate()


class FakeRuntime:
    """Nimmt auf, was der Starter senden würde. Der Starter selbst läuft echt."""

    def __init__(self):
        self.sent = []
        self.threads = []
        self._lock = threading.Lock()

    def publish(self, kind, payload, *, message_id=None):
        with self._lock:
            self.sent.append((kind, payload, message_id))
            self.threads.append(threading.current_thread().name)
        return message_id or "x"

    def of(self, kind):
        with self._lock:
            return [p for k, p, _ in self.sent if k == kind]

    def output(self, terminal_id=None) -> str:
        chunks = [base64.b64decode(p["data"]) for p in self.of("terminal_output")
                  if terminal_id is None or p["terminal_id"] == terminal_id]
        return b"".join(chunks).decode("utf-8", "replace")

    def states(self, terminal_id=None):
        return [p["state"] for p in self.of("terminal_state") if terminal_id is None or p["terminal_id"] == terminal_id]


def entry(start_id, programm, ort="Host", ordner="/tmp", name=None):
    return StartEntry(start_id, name or start_id, ort, ordner, programm)


class LauncherCase(unittest.TestCase):
    def setUp(self):
        self.runtime_dir = Path(tempfile.mkdtemp(prefix="bl-", dir="/tmp"))
        self.runtime = FakeRuntime()
        self.orte = {"Host": Ort("host", None)}
        self.starts = {}
        self.launcher = None
        self.addCleanup(shutil.rmtree, self.runtime_dir, True)

    def make(self, *entries):
        self.starts = {e.start_id: e for e in entries}
        self.launcher = Launcher(self.runtime, self.starts, self.orte, self.runtime_dir)
        self.addCleanup(self.launcher.shutdown)
        return self.launcher

    def start(self, start_id, rows=30, cols=100):
        self.launcher.handle(ev("terminal_start", {"start_id": start_id, "rows": rows, "cols": cols}))
        terminal_id = wait_for(lambda: (self.runtime.of("terminal_state") or [{}])[0].get("terminal_id"))
        self.assertTrue(terminal_id)
        return terminal_id


class ConfigTests(unittest.TestCase):
    def test_shipped_config_loads_and_matches_be02(self):
        orte = load_orte(CONFIG / "orte.json")
        starts = load_starts(CONFIG / "starts.json", orte)
        self.assertEqual(set(orte), {"Host", "vd1", "vd2"})
        self.assertEqual({s.ort for s in starts.values()}, {"Host", "vd1", "vd2"})
        self.assertEqual(starts["haiku-host"].ordner, "/home/claude_haiku")
        self.assertEqual(orte["vd1"].seen("/root/werkraum/x"), "/vps_root/werkraum/x")
        self.assertEqual(orte["Host"].seen("/root/werkraum/x"), "/root/werkraum/x")
        self.assertEqual(orte["vd1"].seen("/rootfoo/x"), "/rootfoo/x")

    def test_bad_config_is_refused(self):
        orte = {"Host": Ort("host", None)}
        base = {"start_id": "a", "name": "A", "ort": "Host", "ordner": "/tmp", "programm": "true"}
        cases = {
            "invalid_start_id": {**base, "start_id": "bad id"},
            "invalid_ordner": {**base, "ordner": "relativ"},
            "unknown_ort": {**base, "ort": "nirgends"},
            "invalid_programm": {**base, "programm": "a\nb"},
        }
        for reason, item in cases.items():
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
                json.dump({"starts": [item]}, handle)
            self.addCleanup(os.unlink, handle.name)
            with self.assertRaisesRegex(ValueError, reason):
                load_starts(Path(handle.name), orte)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump({"starts": [base, base]}, handle)
        self.addCleanup(os.unlink, handle.name)
        with self.assertRaisesRegex(ValueError, "invalid_start_id"):
            load_starts(Path(handle.name), orte)


class CommandTests(unittest.TestCase):
    def test_child_environment_is_an_allowlist_without_relay_secrets(self):
        secrets_in_env = {"BRIDGE_RELAY_TOKEN": "geheim-relay", "AWS_SECRET_ACCESS_KEY": "geheim-aws",
                          "ANTHROPIC_API_KEY": "geheim-key"}
        with mock.patch.dict(os.environ, secrets_in_env):
            _, _, env = build_command(entry("a", "true"), Ort("host", None), "t-1", "tok", Path("/r/run"))
        self.assertTrue(set(env) <= set(ENV_ALLOW) | {"TERM", "COLORTERM", "BRIDGE_TERMINAL_ID",
                                                       "BRIDGE_TERMINAL_TOKEN", "BRIDGE_RUNTIME_DIR"})
        self.assertNotIn("geheim", json.dumps(env))
        self.assertEqual(env["BRIDGE_TERMINAL_ID"], "t-1")
        self.assertEqual(env["BRIDGE_RUNTIME_DIR"], "/r/run")

    def test_host_command_uses_interactive_bash_in_the_folder(self):
        argv, cwd, _ = build_command(entry("a", "claude", ordner="/home/claude_haiku"), Ort("host", None),
                                     "t-1", "tok", Path("/r/run"))
        self.assertEqual(argv, ["bash", "-ic", "claude"])
        self.assertEqual(cwd, "/home/claude_haiku")

    def test_docker_command_keeps_the_token_out_of_the_process_list(self):
        ort = Ort("docker", "virtuellerdesktop1", "/root", "/vps_root")
        argv, cwd, env = build_command(entry("a", "codex", ort="vd1", ordner="/config"), ort, "t-1", "tok-geheim",
                                       Path("/root/werkraum/augen_haende_bridge/runtime"))
        self.assertIsNone(cwd)
        self.assertEqual(argv[:6], ["docker", "exec", "-it", "-w", "/config", "-e"])
        self.assertEqual(argv[-4:], ["virtuellerdesktop1", "bash", "-ic", "codex"])
        self.assertNotIn("tok-geheim", " ".join(argv))
        self.assertEqual(env["BRIDGE_TERMINAL_TOKEN"], "tok-geheim")
        self.assertEqual(env["BRIDGE_RUNTIME_DIR"], "/vps_root/werkraum/augen_haende_bridge/runtime")
        passed = [argv[i + 1] for i, a in enumerate(argv) if a == "-e"]
        self.assertEqual(set(passed), {"TERM", "COLORTERM", "BRIDGE_TERMINAL_ID", "BRIDGE_TERMINAL_TOKEN",
                                       "BRIDGE_RUNTIME_DIR"})


class RemoteKillTests(unittest.TestCase):
    def test_script_signals_only_the_processes_of_that_terminal(self):
        mine = subprocess.Popen(["sleep", "30"], env={**os.environ, "BRIDGE_TERMINAL_ID": "t-mine"})
        longer = subprocess.Popen(["sleep", "30"], env={**os.environ, "BRIDGE_TERMINAL_ID": "t-mine2"})
        plain = subprocess.Popen(["sleep", "30"])
        for proc in (mine, longer, plain):
            self.addCleanup(proc.wait)
            self.addCleanup(proc.kill)
        subprocess.run(["sh", "-c", REMOTE_KILL_SCRIPT, "sh", "t-mine", "15"], check=True)
        self.assertEqual(mine.wait(timeout=5), -15)
        self.assertIsNone(longer.poll())
        self.assertIsNone(plain.poll())

    def test_remote_kill_ignores_host_places_and_odd_ids(self):
        with mock.patch("client_vps.terminal_launcher.subprocess.run") as run:
            remote_kill(Ort("host", None), "t-1", 1)
            remote_kill(Ort("docker", "c"), "t 1; rm", 1)
            remote_kill(Ort("docker", "c"), "../x", 1)
        run.assert_not_called()
        with mock.patch("client_vps.terminal_launcher.subprocess.run") as run:
            remote_kill(Ort("docker", "virtuellerdesktop1"), "t-1", 1)
        argv = run.call_args[0][0]
        self.assertEqual(argv[:4], ["docker", "exec", "virtuellerdesktop1", "sh"])
        self.assertEqual(argv[-3:], ["sh", "t-1", "1"])

    def test_close_reaches_the_remote_side_first(self):
        calls = []
        session = TerminalSession("t-r", entry("r", "sleep 60"), "tok", ["bash", "-ic", "sleep 60"], "/tmp",
                                  dict(os.environ), 24, 80, lambda data: None, lambda code: calls.append(("exit", code)),
                                  remote_kill=lambda sig: calls.append(("kill", sig)))
        session.start()
        self.addCleanup(session._proc.kill)
        session.close()
        self.assertEqual(calls[0], ("kill", 1))
        self.assertTrue(wait_for(lambda: ("exit", -1) in calls))


class ProcessTests(LauncherCase):
    def test_start_stream_input_and_exit_code_on_a_real_pty(self):
        self.make(entry("echo", "printf 'READY\\n'; read line; printf 'GOT:%s\\n' \"$line\"; exit 3"))
        terminal_id = self.start("echo")
        self.assertTrue(wait_for(lambda: "READY" in self.runtime.output()))
        self.assertEqual(self.runtime.states()[:2], ["starting", "running"])
        self.launcher.handle(ev("terminal_input", {"terminal_id": terminal_id, "data": b64(b"abc\n")}))
        self.assertTrue(wait_for(lambda: "GOT:abc" in self.runtime.output()))
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states()))
        last = self.runtime.of("terminal_state")[-1]
        self.assertEqual((last["state"], last["exit_code"]), ("exited", 3))
        seqs = [p["seq"] for p in self.runtime.of("terminal_output")]
        self.assertEqual(seqs, list(range(len(seqs))))

    def test_window_size_is_set_and_follows_resize(self):
        self.make(entry("size", "stty size; read x; stty size"))
        terminal_id = self.start("size", rows=30, cols=100)
        self.assertTrue(wait_for(lambda: "30 100" in self.runtime.output()))
        self.launcher.handle(ev("terminal_resize", {"terminal_id": terminal_id, "rows": 40, "cols": 120}))
        self.launcher.handle(ev("terminal_input", {"terminal_id": terminal_id, "data": b64(b"\n")}))
        self.assertTrue(wait_for(lambda: "40 120" in self.runtime.output()))

    def test_child_sees_its_terminal_identity_but_no_relay_secret(self):
        self.make(entry("env", "env"))
        with mock.patch.dict(os.environ, {"BRIDGE_RELAY_TOKEN": "geheim-relay", "OPENAI_API_KEY": "geheim-key"}):
            terminal_id = self.start("env")
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states()))
        text = self.runtime.output()
        self.assertIn(f"BRIDGE_TERMINAL_ID={terminal_id}", text)
        self.assertIn(f"BRIDGE_RUNTIME_DIR={self.runtime_dir}", text)
        self.assertIn("BRIDGE_TERMINAL_TOKEN=", text)
        self.assertNotIn("geheim", text)

    def test_unknown_start_id_fails_and_nothing_runs(self):
        self.make(entry("echo", "true"))
        self.launcher.handle(ev("terminal_start", {"start_id": "rm -rf /", "rows": 30, "cols": 100}))
        (state,) = self.runtime.of("terminal_state")
        self.assertEqual((state["state"], state["reason"]), ("failed", "unknown_start_id"))
        self.assertEqual(self.launcher.sessions, {})

    def test_start_limit(self):
        self.make(entry("sleep", "sleep 30"))
        for _ in range(MAX_TERMINALS):
            self.launcher.handle(ev("terminal_start", {"start_id": "sleep", "rows": 24, "cols": 80}))
        self.launcher.handle(ev("terminal_start", {"start_id": "sleep", "rows": 24, "cols": 80}))
        last = self.runtime.of("terminal_state")[-1]
        self.assertEqual((last["state"], last["reason"]), ("failed", "too_many_terminals"))
        self.assertEqual(len(self.launcher.sessions), MAX_TERMINALS)

    def test_failed_program_reports_its_exit_code(self):
        self.make(entry("bad", "exit 127"))
        self.start("bad")
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states()))
        self.assertEqual(self.runtime.of("terminal_state")[-1]["exit_code"], 127)

    def test_exit_is_reported_even_when_a_detached_child_keeps_the_pty_open(self):
        self.make(entry("detached", "setsid sleep 4 & exit 0"))
        started = time.monotonic()
        self.start("detached")
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states(), timeout=3))
        self.assertLess(time.monotonic() - started, 3)
        self.assertEqual(self.runtime.of("terminal_state")[-1]["exit_code"], 0)

    def test_missing_folder_reports_failed_not_a_crash(self):
        self.make(entry("nowhere", "true", ordner="/gibt/es/nicht"))
        self.launcher.handle(ev("terminal_start", {"start_id": "nowhere", "rows": 24, "cols": 80}))
        last = self.runtime.of("terminal_state")[-1]
        self.assertEqual(last["state"], "failed")
        self.assertIn("FileNotFoundError", last["reason"])

    def test_close_ends_a_running_program(self):
        self.make(entry("sleep", "sleep 60"))
        terminal_id = self.start("sleep")
        self.assertTrue(wait_for(lambda: "running" in self.runtime.states()))
        self.launcher.handle(ev("terminal_close", {"terminal_id": terminal_id}))
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states(), timeout=8))
        self.assertLess(self.runtime.of("terminal_state")[-1]["exit_code"], 0)

    def test_input_for_unknown_or_finished_terminal_is_ignored(self):
        self.make(entry("bad", "exit 0"))
        terminal_id = self.start("bad")
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states()))
        self.launcher.handle(ev("terminal_input", {"terminal_id": terminal_id, "data": b64(b"x")}))
        self.launcher.handle(ev("terminal_input", {"terminal_id": "t-unbekannt", "data": b64(b"x")}))
        self.launcher.handle(ev("terminal_resize", {"terminal_id": "t-unbekannt", "rows": 5, "cols": 5}))
        self.launcher.handle(ev("terminal_close", {"terminal_id": "t-unbekannt"}))

    def test_list_reports_starts_and_only_live_terminals(self):
        self.make(entry("sleep", "sleep 60"), entry("bad", "exit 0"))
        self.launcher.handle(ev("terminal_start", {"start_id": "bad", "rows": 24, "cols": 80}))
        self.launcher.handle(ev("terminal_start", {"start_id": "sleep", "rows": 24, "cols": 80}))
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states()))
        self.launcher.handle(ev("terminal_list_request", {}, event_id="list-1"))
        listing = self.runtime.of("terminal_list")[-1]
        self.assertEqual(listing["request_id"], "list-1")
        self.assertEqual({s["start_id"] for s in listing["starts"]}, {"sleep", "bad"})
        self.assertEqual([t["start_id"] for t in listing["terminals"]], ["sleep"])

    def test_events_are_handled_off_the_caller_thread(self):
        self.make(entry("sleep", "sleep 60"))
        self.launcher.start()
        self.launcher.on_event(ev("terminal_list_request", {}, event_id="q1"))
        self.assertTrue(wait_for(lambda: self.runtime.of("terminal_list")))
        self.assertEqual(set(self.runtime.threads), {"launcher-events"})

    def test_unknown_events_and_non_events_are_ignored(self):
        self.make(entry("sleep", "sleep 60"))
        self.launcher.handle({"kind": "receipt_recorded"})
        self.launcher.handle(ev("say", {"text": "x"}))
        self.launcher.handle({"kind": "event", "event_kind": "terminal_start", "payload": "kein-dict"})
        self.assertEqual(self.runtime.sent, [])

    def test_publish_failure_never_stops_the_reader(self):
        class Broken(FakeRuntime):
            def publish(self, kind, payload, *, message_id=None):
                raise RuntimeError("bridge_runtime_not_connected")

        self.runtime = Broken()
        self.make(entry("echo", "printf 'A\\n'; exit 0"))
        self.launcher.handle(ev("terminal_start", {"start_id": "echo", "rows": 24, "cols": 80}))
        self.assertTrue(wait_for(lambda: self.launcher.dropped >= 3))


class FrameTests(LauncherCase):
    def frame(self, terminal_id, stamp, mime="image/png"):
        return {"mime": mime, "data": PNG, "source": "capture", "captured_at_ms": stamp, "width": 1, "height": 1,
                "terminal_id": terminal_id}

    def test_frame_is_stored_per_terminal_with_latest_pointer(self):
        self.make(entry("sleep", "sleep 60"))
        self.launcher.handle(ev("frame", self.frame("t-abc", 1000)))
        meta = self.launcher.latest_frame("t-abc")
        self.assertEqual(meta["file"], "frame-1000.png")
        self.assertEqual(meta["relative_path"], "frames/t-abc/frame-1000.png")
        self.assertEqual((self.runtime_dir / meta["relative_path"]).read_bytes(), base64.b64decode(PNG))
        self.assertGreaterEqual(meta["age_ms"], 0)
        self.assertIsNone(self.launcher.latest_frame("t-anders"))

    def test_only_the_newest_frames_are_kept(self):
        self.make(entry("sleep", "sleep 60"))
        for stamp in range(1000, 1000 + KEEP_FRAMES + 3):
            self.launcher.handle(ev("frame", self.frame("t-abc", stamp)))
        files = sorted(p.name for p in (self.runtime_dir / "frames" / "t-abc").glob("frame-*"))
        self.assertEqual(len(files), KEEP_FRAMES)
        self.assertEqual(files[-1], f"frame-{1000 + KEEP_FRAMES + 2}.png")
        self.assertEqual(self.launcher.latest_frame("t-abc")["file"], files[-1])

    def test_frame_without_terminal_goes_to_the_desktop_folder(self):
        self.make(entry("sleep", "sleep 60"))
        payload = self.frame("x", 5)
        del payload["terminal_id"]
        self.launcher.handle(ev("frame", payload))
        self.assertEqual(self.launcher.latest_frame("_desktop")["file"], "frame-5.png")

    def test_terminal_id_can_not_escape_the_frames_folder(self):
        self.make(entry("sleep", "sleep 60"))
        self.launcher.handle(ev("frame", self.frame("../../evil", 1)))
        self.assertFalse((self.runtime_dir / "frames").exists() and any((self.runtime_dir / "frames").iterdir()))
        self.assertFalse((self.runtime_dir.parent / "evil").exists())
        self.assertIsNone(self.launcher.latest_frame("../../evil"))


class AgentSocketTests(LauncherCase):
    def setUp(self):
        super().setUp()
        self.make(entry("sleep", "sleep 60"))
        self.terminal_id = self.start("sleep")
        self.session = self.launcher.sessions[self.terminal_id]
        self.socket_path = self.runtime_dir / "agent.sock"
        self.server = self.launcher.serve_agents(self.socket_path)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.env = {"BRIDGE_TERMINAL_ID": self.terminal_id, "BRIDGE_TERMINAL_TOKEN": self.session.token,
                    "BRIDGE_RUNTIME_DIR": str(self.runtime_dir)}

    def raw(self, data: bytes) -> dict:
        with socket.socket(socket.AF_UNIX) as sock:
            sock.settimeout(3)
            sock.connect(str(self.socket_path))
            sock.sendall(data)
            return json.loads(sock.makefile().readline())

    def test_say_becomes_a_raute_message_for_that_terminal(self):
        reply = bridge_cli.ask({"cmd": "say", "text": "Hast du deinen Turm ungedeckt gelassen?"}, self.env)
        self.assertEqual(reply, {"ok": True})
        (sent,) = self.runtime.of("raute_say")
        self.assertEqual(sent, {"terminal_id": self.terminal_id, "text": "Hast du deinen Turm ungedeckt gelassen?"})

    def test_schreibe_becomes_a_raute_tippen_message_for_that_terminal(self):
        reply = bridge_cli.ask({"cmd": "schreibe", "text": "Ich sehe den Turm"}, self.env)
        self.assertTrue(reply["ok"])
        (sent,) = self.runtime.of("raute_tippen")
        self.assertEqual(sent, {"terminal_id": self.terminal_id, "text": "Ich sehe den Turm"})
        self.assertEqual(self.runtime.of("raute_say"), [])

    def test_schreibe_refuses_empty_and_too_long_text_and_wrong_token(self):
        self.assertEqual(bridge_cli.ask({"cmd": "schreibe", "text": ""}, self.env)["reason"], "invalid_text")
        self.assertEqual(bridge_cli.ask({"cmd": "schreibe", "text": "x" * 501}, self.env)["reason"], "invalid_text")
        self.assertEqual(bridge_cli.ask({"cmd": "schreibe", "text": 5}, self.env)["reason"], "invalid_text")
        bad = {**self.env, "BRIDGE_TERMINAL_TOKEN": "falsch"}
        self.assertEqual(bridge_cli.ask({"cmd": "schreibe", "text": "x"}, bad)["reason"], "unknown_terminal_or_token")
        self.assertEqual(self.runtime.of("raute_tippen"), [])

    def test_cli_schreibe_and_hilfe(self):
        with mock.patch.dict(os.environ, self.env), mock.patch("builtins.print") as printed:
            self.assertEqual(bridge_cli.main(["schreibe", "Hallo", "Welt"]), 0)
            self.assertEqual(self.runtime.of("raute_tippen")[-1]["text"], "Hallo Welt")
            self.assertEqual(bridge_cli.main(["hilfe"]), 0)
            self.assertIn("schreibe", printed.call_args[0][0])

    def test_cli_main_prints_json_and_uses_exit_code(self):
        with mock.patch.dict(os.environ, self.env), mock.patch("builtins.print") as printed:
            self.assertEqual(bridge_cli.main(["say", "Hallo", "Welt"]), 0)
            self.assertEqual(json.loads(printed.call_args[0][0]), {"ok": True})
            self.assertEqual(bridge_cli.main(["see"]), 1)
            self.assertEqual(json.loads(printed.call_args[0][0])["reason"], "no_frame_yet")
            self.assertEqual(bridge_cli.main(["unsinn"]), 2)
        self.assertEqual(self.runtime.of("raute_say")[-1]["text"], "Hallo Welt")

    def test_see_returns_the_latest_frame_path_as_the_agent_sees_it(self):
        self.launcher.handle(ev("frame", {"mime": "image/png", "data": PNG, "source": "capture",
                                          "captured_at_ms": 42, "width": 1, "height": 1,
                                          "terminal_id": self.terminal_id}))
        reply = bridge_cli.ask({"cmd": "see"}, self.env)
        self.assertTrue(reply["ok"])
        self.assertEqual(reply["frame"]["path"], str(self.runtime_dir / "frames" / self.terminal_id / "frame-42.png"))
        self.assertEqual(Path(reply["frame"]["path"]).read_bytes(), base64.b64decode(PNG))

    def test_wrong_token_or_terminal_is_refused(self):
        bad = {**self.env, "BRIDGE_TERMINAL_TOKEN": "falsch"}
        self.assertEqual(bridge_cli.ask({"cmd": "say", "text": "x"}, bad)["reason"], "unknown_terminal_or_token")
        other = {**self.env, "BRIDGE_TERMINAL_ID": "t-anders"}
        self.assertEqual(bridge_cli.ask({"cmd": "say", "text": "x"}, other)["reason"], "unknown_terminal_or_token")
        self.assertEqual(self.runtime.of("raute_say"), [])

    def test_missing_environment_and_missing_socket_are_explicit(self):
        self.assertTrue(bridge_cli.ask({"cmd": "see"}, {})["reason"].startswith("not_in_bridge_terminal"))
        gone = {**self.env, "BRIDGE_RUNTIME_DIR": "/tmp/gibt-es-nicht"}
        self.assertTrue(bridge_cli.ask({"cmd": "see"}, gone)["reason"].startswith("launcher_unreachable"))

    def test_bad_requests_are_refused(self):
        self.assertEqual(self.raw(b"kein json\n")["reason"], "invalid_request")
        self.assertEqual(self.raw(b"[1, 2]\n")["reason"], "invalid_request")
        self.assertEqual(self.raw(b"x" * 70_000)["reason"], "invalid_request")
        for text in ("", "x" * 8001, 5):
            self.assertEqual(bridge_cli.ask({"cmd": "say", "text": text}, self.env)["reason"], "invalid_text")
        self.assertEqual(bridge_cli.ask({"cmd": "rm"}, self.env)["reason"], "unknown_command")
        self.assertEqual(self.runtime.of("raute_say"), [])

    def test_finished_terminal_can_not_speak(self):
        self.launcher.handle(ev("terminal_close", {"terminal_id": self.terminal_id}))
        self.assertTrue(wait_for(lambda: self.session.state == "exited", timeout=8))
        self.assertEqual(bridge_cli.ask({"cmd": "say", "text": "x"}, self.env)["reason"], "terminal_not_running")


class RelayIntegrationTests(unittest.TestCase):
    """Desktop-Seite und Starter über ein echtes Relay: Liste, Start, Strom, Eingabe, Ende."""

    def test_full_path_over_a_real_relay(self):
        asyncio.run(self._run())

    async def _run(self):
        runtime_dir = Path(tempfile.mkdtemp(prefix="bl-", dir="/tmp"))
        self.addCleanup(shutil.rmtree, runtime_dir, True)
        desktop_token, agent_token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        journal = Journal(runtime_dir / "events.sqlite")
        relay = Relay([
            Principal("desktop", desktop_token, "agent", "launcher-target", can_publish_frames=True, can_control_terminals=True),
            Principal("agent", agent_token, "desktop", "launcher-target", can_serve_terminals=True),
        ], journal)
        starts = {"echo": entry("echo", "printf 'READY\\n'; read line; printf 'GOT:%s\\n' \"$line\"; exit 4", name="Echo")}
        desktop_events: queue.Queue = queue.Queue()
        launcher = None
        async with relay.listen() as server:
            port = server.sockets[0].getsockname()[1]
            agent_runtime = BridgeRuntime(f"ws://127.0.0.1:{port}", agent_token, on_event=lambda e: launcher.on_event(e))
            launcher = Launcher(agent_runtime, starts, {"Host": Ort("host", None)}, runtime_dir)
            launcher.start()
            desktop = BridgeRuntime(f"ws://127.0.0.1:{port}", desktop_token, on_event=desktop_events.put)
            agent_runtime.start()
            desktop.start()
            try:
                for _ in range(200):
                    if desktop.connected and agent_runtime.connected:
                        break
                    await asyncio.sleep(.01)
                self.assertTrue(desktop.connected and agent_runtime.connected)

                def next_event(kind, timeout=8.0):
                    end = time.monotonic() + timeout
                    while time.monotonic() < end:
                        try:
                            event = desktop_events.get(timeout=.1)
                        except queue.Empty:
                            continue
                        if event.get("event_kind") == kind:
                            return event
                    raise AssertionError(f"kein {kind} angekommen")

                request_id = await asyncio.to_thread(desktop.publish, "terminal_list_request", {})
                listing = (await asyncio.to_thread(next_event, "terminal_list"))["payload"]
                self.assertEqual(listing["request_id"], request_id)
                self.assertEqual([s["start_id"] for s in listing["starts"]], ["echo"])

                await asyncio.to_thread(desktop.publish, "terminal_start", {"start_id": "echo", "rows": 30, "cols": 100})
                seen = []
                while True:
                    state = (await asyncio.to_thread(next_event, "terminal_state"))["payload"]
                    seen.append(state["state"])
                    if state["state"] == "running":
                        terminal_id = state["terminal_id"]
                        break
                self.assertEqual(seen, ["starting", "running"])

                collected = b""
                while b"READY" not in collected:
                    out = (await asyncio.to_thread(next_event, "terminal_output"))["payload"]
                    self.assertEqual(out["terminal_id"], terminal_id)
                    collected += base64.b64decode(out["data"])
                await asyncio.to_thread(desktop.publish, "terminal_input",
                                        {"terminal_id": terminal_id, "data": b64(b"pong\n")})
                while b"GOT:pong" not in collected:
                    collected += base64.b64decode((await asyncio.to_thread(next_event, "terminal_output"))["payload"]["data"])
                final = (await asyncio.to_thread(next_event, "terminal_state"))["payload"]
                self.assertEqual((final["state"], final["exit_code"]), ("exited", 4))
                rows = str(journal.db.execute("SELECT * FROM messages").fetchall()) + \
                    str(journal.db.execute("SELECT * FROM events").fetchall())
                self.assertNotIn("pong", rows)
                self.assertNotIn(b64(b"pong\n"), rows)
            finally:
                launcher.shutdown()
                await asyncio.gather(asyncio.to_thread(desktop.stop), asyncio.to_thread(agent_runtime.stop))
        journal.close()


if __name__ == "__main__":
    unittest.main()


class GrosseEingabeTests(unittest.TestCase):
    def test_write_schreibt_auch_bei_teilweisem_os_write_alles(self):
        sitzung = TerminalSession("t", StartEntry("x", "X", "vd1", "/", "true", True), "tok", ["true"], None, {}, 24, 80,
                                  lambda daten: None, lambda code: None)
        sitzung.state, sitzung.fd = "running", 7
        angenommen = []

        def os_write(fd, daten):
            teil = bytes(daten[:1000])  # nimmt höchstens 1000 Bytes pro Aufruf an
            angenommen.append(teil)
            return len(teil)

        with mock.patch("client_vps.terminal_launcher.os.write", side_effect=os_write):
            sitzung.write(b"x" * 8192)
        self.assertEqual(b"".join(angenommen), b"x" * 8192)

    def test_write_wartet_bei_vollem_puffer_und_gibt_nichts_auf(self):
        sitzung = TerminalSession("t", StartEntry("x", "X", "vd1", "/", "true", True), "tok", ["true"], None, {}, 24, 80,
                                  lambda daten: None, lambda code: None)
        sitzung.state, sitzung.fd = "running", 7
        ablauf = [BlockingIOError(), BlockingIOError(), 5]
        angenommen = []

        def os_write(fd, daten):
            wert = ablauf.pop(0)
            if isinstance(wert, Exception):
                raise wert
            angenommen.append(bytes(daten[:wert]))
            return wert

        with mock.patch("client_vps.terminal_launcher.os.write", side_effect=os_write):
            sitzung.write(b"hallo")
        self.assertEqual(angenommen, [b"hallo"])

    def test_echtes_pty_nimmt_100_kb_vollstaendig_an(self):
        argv = ["bash", "-c", "stty raw -echo; head -c 102400 | md5sum"]
        ausgabe = bytearray()
        sitzung = TerminalSession("t", StartEntry("x", "X", "vd1", "/", "true", True), "tok", argv, None, dict(os.environ), 24, 200,
                                  ausgabe.extend, lambda code: None)
        sitzung.start()
        time.sleep(0.3)
        daten = bytes((i * 7) % 251 + 1 for i in range(102400))  # keine Steuerzeichen wie Ctrl-D im Strom
        daten = bytes(b if b > 31 else 65 for b in daten)
        sitzung.write(daten)
        import hashlib
        erwartet = hashlib.md5(daten).hexdigest()
        self.assertTrue(wait_for(lambda: erwartet.encode() in bytes(ausgabe), timeout=15), bytes(ausgabe)[-200:])
        sitzung.close()


class LagebildTests(LauncherCase):
    """Jeder Agent weiß jederzeit, was für ihn klappt: der Körper meldet, der Relay gibt es zurück; fehlt die Meldung, sagt er „unbekannt“."""

    def setUp(self):
        super().setUp()
        self.make(entry("a", "/bin/sleep 30"))
        self.tid = self.start("a")

    def meldung(self, farbe="gruen", wort="läuft"):
        return {"terminal_id": self.tid, "lampen": [
            {"k": "bild", "n": "Bilder kommen frisch an", "f": farbe, "w": wort, "b": "", "g": "augen"},
            {"k": "hand", "n": "Hände insgesamt", "f": "gruen", "w": "läuft", "b": "", "g": "haende"},
            {"k": "zustand", "n": "Zustand des Ziel-Fensters", "f": "gruen", "w": "sichtbar", "b": "", "g": "ziel"}]}

    def test_ohne_meldung_ist_die_lage_unbekannt(self):
        antwort = self.launcher._agent_befehl(self.tid, "lage", {})
        self.assertTrue(antwort["ok"])
        self.assertFalse(antwort["bekannt"])
        self.assertIn("Lage unbekannt", antwort["sage"])

    def test_die_meldung_des_koerpers_kommt_beim_agenten_an(self):
        self.launcher.handle(ev("lage", self.meldung("rot", "KEIN BILD seit 4 min")))
        antwort = self.launcher._agent_befehl(self.tid, "lage", {})
        self.assertTrue(antwort["bekannt"])
        self.assertEqual(antwort["gruppen"]["augen"]["zustand"], "kaputt")
        self.assertEqual(antwort["probleme"][0]["funktion"], "Bilder kommen frisch an")
        self.assertIn("bridge_cli.py say", antwort["sage"])

    def test_eine_alte_meldung_gilt_nicht_mehr(self):
        self.launcher.handle(ev("lage", self.meldung()))
        t = self.launcher.lage[self.tid][0]
        self.launcher.lage[self.tid] = (t - 60, self.launcher.lage[self.tid][1])
        antwort = self.launcher._agent_befehl(self.tid, "lage", {})
        self.assertFalse(antwort["bekannt"])
        self.assertIn("alt", antwort["sage"])

    def test_ungueltige_oder_fremde_meldungen_werden_nicht_gespeichert(self):
        self.launcher.handle(ev("lage", {"terminal_id": self.tid, "lampen": [{"f": "lila"}]}))
        self.launcher.handle(ev("lage", {**self.meldung(), "terminal_id": "t-gibtesnicht"}))
        self.assertNotIn(self.tid, self.launcher.lage)
        self.assertNotIn("t-gibtesnicht", self.launcher.lage)

    def test_jede_antwort_des_praxistests_traegt_die_kurzfassung(self):
        antwort = self.launcher._agent_befehl(self.tid, "test", {"befehl": "karte"})
        self.assertIn("Lage unbekannt", antwort["lage"])
        self.launcher.handle(ev("lage", self.meldung("gelb", "verdeckt")))
        antwort = self.launcher._agent_befehl(self.tid, "test", {"befehl": "karte"})
        self.assertIn("Hinweis", antwort["lage"])
        self.launcher.handle(ev("lage", self.meldung()))
        self.assertEqual(self.launcher._agent_befehl(self.tid, "test", {"befehl": "status"})["lage"], "Lage: alles läuft.")


class HaendeEreignisGrundTests(LauncherCase):
    """Der Käfig meldet seinen Ablehnungsgrund als `grund`; das Ereignis `haende` muss ihn als `reason` tragen, sonst zählt der Praxistest nie eine abgelehnte Aktion."""

    def setUp(self):
        super().setUp()
        self.make(entry("a", "/bin/sleep 30"))
        self.tid = self.start("a")

    def test_grund_des_kaefigs_steht_im_ereignis(self):
        self.launcher._agent_befehl_roh = lambda tid, cmd, req: {"ok": False, "status": "abgelehnt", "grund": "ausserhalb"}
        self.launcher._agent_befehl(self.tid, "haende", {"aktion": {"art": "klick"}})
        ereignis = [e for e in self.launcher.kapseln.protokoll._ereignisse if e.art == "haende"][-1]
        self.assertEqual((ereignis.daten["ok"], ereignis.daten["reason"]), (False, "ausserhalb"))

    def test_reason_der_relay_antwort_bleibt_vorrangig(self):
        self.launcher._agent_befehl_roh = lambda tid, cmd, req: {"ok": False, "reason": "lease_fehlt", "grund": "x"}
        self.launcher._agent_befehl(self.tid, "haende", {"aktion": {"art": "klick"}})
        ereignis = [e for e in self.launcher.kapseln.protokoll._ereignisse if e.art == "haende"][-1]
        self.assertEqual(ereignis.daten["reason"], "lease_fehlt")

    def test_die_zaehlung_abgelehnter_versuche_findet_den_ausserhalb_klick(self):
        self.launcher._agent_befehl_roh = lambda tid, cmd, req: {"ok": False, "status": "abgelehnt", "grund": "ausserhalb"}
        self.launcher._agent_befehl(self.tid, "haende", {"aktion": {"art": "klick"}})
        self.assertEqual(self.launcher.praxis.evidenz(self.tid, "haende_abgelehnt", 0), 1)


class SeeFrischTests(LauncherCase):
    """`see` ruft beim Körper ein frisches Bild ab und wartet kurz darauf; ohne Körper gilt das letzte Bild mit seinem wahren Alter."""

    def setUp(self):
        super().setUp()
        self.make(entry("a", "/bin/sleep 30"))
        self.tid = self.start("a")
        self.veroeffentlicht = []
        self.launcher._publish = lambda kind, payload, message_id=None, ort=None: self.veroeffentlicht.append((kind, payload))
        self.launcher.SEE_WARTE_S = 0.6

    def frame(self, captured_ms):
        p = {"mime": "image/png", "data": PNG, "source": "capture", "captured_at_ms": captured_ms, "width": 1, "height": 1, "terminal_id": self.tid, "seq": 1}
        self.launcher.store_frame(p, None)

    def test_see_fordert_ein_bild_an_und_nimmt_das_neue(self):
        self.frame(int(time.time() * 1000) - 60_000)  # ein altes Bild
        threading.Timer(0.25, lambda: self.frame(int(time.time() * 1000))).start()
        meta = self.launcher.frisches_bild(self.tid)
        self.assertEqual(self.veroeffentlicht[-1], ("bild_sofort", {"terminal_id": self.tid}))
        self.assertGreaterEqual(meta["captured_at_ms"], int(time.time() * 1000) - 5_000, "das neue Bild, nicht das alte")

    def test_ohne_neues_bild_gilt_das_letzte_mit_wahrem_alter_nach_der_wartezeit(self):
        alt = int(time.time() * 1000) - 60_000
        self.frame(alt)
        t0 = time.monotonic()
        meta = self.launcher.frisches_bild(self.tid)
        self.assertGreaterEqual(time.monotonic() - t0, 0.5)
        self.assertEqual(meta["captured_at_ms"], alt, "das letzte Bild, mit seiner echten Aufnahmezeit: die Belegprüfung erkennt daran, dass es nicht frisch ist")

    def test_ohne_jedes_bild_kommt_none(self):
        self.assertIsNone(self.launcher.frisches_bild(self.tid))


class ZustellReihenfolgeTests(LauncherCase):
    def test_nachrichten_kommen_je_empfaenger_in_der_gesendeten_reihenfolge_an(self):
        from types import SimpleNamespace

        l = self.make()
        geschrieben = []

        class Sitzung:
            terminal_id, state = "t-x", "running"

            def write(self, data):
                geschrieben.append(data)

            def close(self):
                pass

        l._schlafen = lambda s: None
        sitzung = Sitzung()
        l.sessions["t-x"] = sitzung
        for rolle in range(2):
            geschrieben.clear()
            zust = [SimpleNamespace(an="t-x", name="X", text=f"nachricht-{i:03d}") for i in range(200)]
            for a in range(0, 200, 7):  # in kleinen Stapeln aus mehreren Threads, wie bei vielen Absendern
                l._zustellen(zust[a:a + 7])
            wait_for(lambda: len([g for g in geschrieben if g.startswith(b"nachricht-")]) == 200, 10)
            texte = [g.decode() for g in geschrieben if g.startswith(b"nachricht-")]
            self.assertEqual(texte, [f"nachricht-{i:03d}" for i in range(200)], "Reihenfolge je Empfänger bleibt")
            self.assertEqual(len(geschrieben), 400, "nach jedem Text kommt genau ein Enter")
            self.assertTrue(all(geschrieben[i + 1] == b"\r" for i in range(0, 400, 2)), "Text und Enter vermischen sich nie")
        self.assertEqual(l._zustell_laeuft, set(), "der Arbeiter beendet sich, wenn nichts mehr da ist")


class WiederaufnahmeTests(LauncherCase):
    def test_list_traegt_die_identitaet_der_sitzung(self):
        self.make(entry("sleep", "sleep 60"))
        terminal_id = self.start("sleep")
        self.launcher.handle(ev("terminal_list_request", {}, event_id="list-1"))
        eintrag = self.runtime.of("terminal_list")[-1]["terminals"][0]
        self.assertEqual(eintrag["terminal_id"], terminal_id)
        self.assertEqual(eintrag["pid"], self.launcher.sessions[terminal_id].pid)
        self.assertAlmostEqual(eintrag["gestartet"], time.time(), delta=60)
        self.launcher.handle(ev("terminal_list_request", {}, event_id="list-2"))
        zweiter = self.runtime.of("terminal_list")[-1]["terminals"][0]
        self.assertEqual((zweiter["pid"], zweiter["gestartet"]), (eintrag["pid"], eintrag["gestartet"]))  # dieselbe Sitzung

    def test_attach_spielt_die_gemerkte_ausgabe_noch_einmal_mit_replay_markierung(self):
        self.make(entry("echo", "printf 'eins\\nzwei\\ndrei\\n'; sleep 30"))
        terminal_id = self.start("echo")
        self.assertTrue(wait_for(lambda: "drei" in self.runtime.output(terminal_id)))
        vorher = len(self.runtime.of("terminal_output"))
        original = self.runtime.output(terminal_id)
        self.launcher.handle(ev("terminal_attach", {"terminal_id": terminal_id}))
        neu = self.runtime.of("terminal_output")[vorher:]
        self.assertTrue(neu)
        self.assertTrue(neu[0].get("replay"))
        self.assertTrue(all("replay" not in p for p in neu[1:]))
        wiederholt = b"".join(base64.b64decode(p["data"]) for p in neu).decode("utf-8", "replace")
        self.assertEqual(wiederholt, original)
        seqs = [p["seq"] for p in self.runtime.of("terminal_output")]
        self.assertEqual(seqs, list(range(len(seqs))))  # die Folge reißt nicht ab

    def test_attach_beruehrt_die_sitzung_nicht(self):
        self.make(entry("cat", "cat"))
        terminal_id = self.start("cat")
        pid = self.launcher.sessions[terminal_id].pid
        self.launcher.handle(ev("terminal_input", {"terminal_id": terminal_id, "data": b64(b"hallo\n")}))
        self.assertTrue(wait_for(lambda: self.runtime.output(terminal_id).count("hallo") >= 1))
        for _ in range(3):
            self.launcher.handle(ev("terminal_attach", {"terminal_id": terminal_id}))
        self.launcher.handle(ev("terminal_input", {"terminal_id": terminal_id, "data": b64(b"nochmal\n")}))
        self.assertTrue(wait_for(lambda: "nochmal" in self.runtime.output(terminal_id)))
        session = self.launcher.sessions[terminal_id]
        self.assertEqual((session.pid, session.state), (pid, "running"))  # keine neue Shell, nicht beendet
        self.assertEqual(len(self.launcher.sessions), 1)

    def test_attach_fuer_unbekannte_oder_beendete_sitzung_tut_nichts(self):
        self.make(entry("bad", "echo hallo"))
        self.launcher.handle(ev("terminal_attach", {"terminal_id": "t-unbekannt"}))
        self.launcher.handle(ev("terminal_start", {"start_id": "bad", "rows": 24, "cols": 80}))
        self.assertTrue(wait_for(lambda: "exited" in self.runtime.states()))
        vorher = len(self.runtime.of("terminal_output"))
        terminal_id = self.runtime.of("terminal_state")[0]["terminal_id"]
        self.launcher.handle(ev("terminal_attach", {"terminal_id": terminal_id}))
        self.assertEqual(len(self.runtime.of("terminal_output")), vorher)

    def test_der_gemerkte_puffer_ist_begrenzt_und_beginnt_an_einer_zeilengrenze(self):
        self.make(entry("sleep", "sleep 60"))
        terminal_id = self.start("sleep")
        self.launcher._seq[terminal_id] = 0
        zeile = b"x" * 99 + b"\n"
        for _ in range(7000):  # etwa 700 KB, mehr als der Puffer
            self.launcher._output(terminal_id, zeile)
        puffer = self.launcher.sessions[terminal_id].replay
        self.assertLessEqual(len(puffer), 512 * 1024)
        self.assertTrue(puffer.startswith(b"x" * 99 + b"\n"))
        self.assertGreater(len(puffer), 400 * 1024)

    def test_ausgabe_und_wiederaufnahme_vermischen_sich_nicht(self):
        self.make(entry("sleep", "sleep 60"))
        terminal_id = self.start("sleep")
        self.launcher._seq[terminal_id] = 0
        self.launcher.sessions[terminal_id].replay.clear()
        for i in range(200):
            self.launcher._output(terminal_id, b"%05d\n" % i)

        def stoerer():
            for i in range(200, 400):
                self.launcher._output(terminal_id, b"%05d\n" % i)

        faden = threading.Thread(target=stoerer)
        vorher = len(self.runtime.of("terminal_output"))
        faden.start()
        self.launcher.attach(terminal_id)
        faden.join()
        neu = self.runtime.of("terminal_output")[vorher:]
        marker = [i for i, p in enumerate(neu) if p.get("replay")]
        self.assertEqual(len(marker), 1)
        i = marker[0]
        wiederholt = b"".join(base64.b64decode(p["data"]) for p in neu[i:i + 1])
        self.assertTrue(wiederholt.startswith(b"00000\n"))
        seqs = [p["seq"] for p in self.runtime.of("terminal_output")]
        self.assertEqual(seqs, sorted(seqs))
        self.assertEqual(len(seqs), len(set(seqs)))
