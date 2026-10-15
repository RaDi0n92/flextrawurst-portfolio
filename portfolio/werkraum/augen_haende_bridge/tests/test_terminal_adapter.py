from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from augen_haende_bridge import (
    KonsoleAdapter,
    TargetRegistry,
    TerminalDiscovery,
    TerminalSessionRef,
    TerminalSnapshot,
)
from augen_haende_bridge.target_registry import (
    PlatformUnavailableAdapter,
    _default_terminal_adapter,
    stable_terminal_identity,
)


class FakeQdbus:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(argv)
        if argv == ["qdbus6", "--session"]:
            return subprocess.CompletedProcess(argv, 0, "org.kde.konsole-123\n", "")
        if argv == ["qdbus6", "--session", "org.kde.konsole-123"]:
            return subprocess.CompletedProcess(argv, 0, "/Sessions/1\n", "")
        if any("Session.processId" in value for value in argv):
            return subprocess.CompletedProcess(argv, 0, "123\n", "")
        if any("Session.foregroundProcessId" in value for value in argv):
            return subprocess.CompletedProcess(argv, 0, "456\n", "")
        if any("Session.title" in value for value in argv):
            return subprocess.CompletedProcess(argv, 0, '"bash"\n', "")
        if any("Session.getAllDisplayedText" in value for value in argv):
            return subprocess.CompletedProcess(argv, 0, '"prompt\nprobe-marker"\n', "")
        if any("Session.sendText" in value for value in argv):
            return subprocess.CompletedProcess(argv, 0, "", "")
        return subprocess.CompletedProcess(argv, 1, "", "unexpected qdbus call")


class TerminalAdapterTests(unittest.TestCase):
    def test_discovery_reads_real_session_identity_and_scrollback(self) -> None:
        fake = FakeQdbus()
        adapter = KonsoleAdapter(runner=fake, command="qdbus6")

        refs = adapter.discover()
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].service, "org.kde.konsole-123")
        self.assertEqual(refs[0].session_pid, 123)
        self.assertEqual(refs[0].foreground_pid, 456)
        self.assertEqual(refs[0].title, "bash")

        snapshot = adapter.inspect(target_id="terminal-1", ref=refs[0])
        self.assertEqual(snapshot.status, "observed")
        self.assertEqual(snapshot.source, "real")
        self.assertIn("probe-marker", snapshot.output)
        self.assertEqual(snapshot.capture_method, "konsole-dbus:getAllDisplayedText")

    def test_registry_keeps_static_targets_and_marks_discovered_terminal_real(self) -> None:
        fake = FakeQdbus()
        registry = TargetRegistry(KonsoleAdapter(runner=fake, command="qdbus6"))

        self.assertIn("kde-2", registry.records)
        self.assertEqual(registry.records["terminal-1"].source, "real")
        self.assertEqual(registry.records["terminal-1"].availability, "available")
        self.assertEqual(registry.selected_target_id, "win-desktop")

    def test_windows_default_does_not_construct_local_kde_adapter(self) -> None:
        adapter = _default_terminal_adapter("nt")
        self.assertIsInstance(adapter, PlatformUnavailableAdapter)
        self.assertEqual(adapter.discover(), [])

    def test_windows_registry_constructor_never_spawns_kde_discovery(self) -> None:
        with (
            patch("augen_haende_bridge.target_registry.os.name", "nt"),
            patch(
                "augen_haende_bridge.terminal_adapter.shutil.which",
                side_effect=AssertionError("Windows registry must not probe qdbus"),
            ),
            patch(
                "augen_haende_bridge.terminal_adapter.subprocess.run",
                side_effect=AssertionError("Windows registry must not spawn qdbus"),
            ),
        ):
            registry = TargetRegistry()

        self.assertIsInstance(registry.adapter, PlatformUnavailableAdapter)
        self.assertIn("win-desktop", registry.records)

    def test_refresh_removes_closed_discovered_sessions_but_keeps_static_fallback(self) -> None:
        class MutableAdapter:
            refs = [
                TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "first"),
                TerminalSessionRef("org.kde.konsole-2", "/Sessions/1", 3, 4, "second"),
            ]

            def discover(self):
                return list(self.refs)

            def inspect(self, **_kwargs):
                raise AssertionError("not needed for refresh replacement")

        adapter = MutableAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        self.assertEqual(registry.records["terminal-1"].source, "real")
        registry.select("terminal-2")

        adapter.refs = []
        registry.refresh_terminals()

        self.assertNotIn("terminal-2", registry.records)
        self.assertEqual(registry.records["terminal-1"].source, "synthetic")
        self.assertEqual(registry.selected_target_id, "win-desktop")

    def test_refresh_preserves_explicit_probe_target(self) -> None:
        class EmptyAdapter:
            def discover(self):
                return []

            def inspect(self, **_kwargs):
                raise AssertionError("not needed for probe preservation")

        registry = TargetRegistry(EmptyAdapter())  # type: ignore[arg-type]
        probe = registry.register_probe(
            TerminalSessionRef("org.kde.konsole-probe", "/Sessions/9", 9, 10, "probe")
        )

        registry.refresh_terminals()

        self.assertIn("terminal-probe", registry.records)
        self.assertEqual(registry.records["terminal-probe"], probe)

    def test_selected_live_session_survives_refresh(self) -> None:
        class StableAdapter:
            ref = TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "first")

            def discover(self):
                return [self.ref]

        registry = TargetRegistry(StableAdapter())  # type: ignore[arg-type]
        registry.select("terminal-1")

        registry.refresh_terminals()

        self.assertEqual(registry.selected_target_id, "terminal-1")
        self.assertEqual(registry.selected().stable_identity, stable_terminal_identity(StableAdapter.ref))

    def test_probe_session_is_not_duplicated_by_standard_discovery(self) -> None:
        class ProbeAwareAdapter:
            ref = TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "probe")

            def discover(self):
                return [self.ref]

        adapter = ProbeAwareAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        registry.select("terminal-1")
        registry.register_probe(adapter.ref)

        registry.refresh_terminals()

        self.assertIn("terminal-probe", registry.records)
        self.assertEqual(registry.selected_target_id, "terminal-probe")
        self.assertNotEqual(registry.records.get("terminal-1", None), registry.records["terminal-probe"])
        self.assertEqual(registry.records["terminal-probe"].stable_identity, stable_terminal_identity(adapter.ref))
        self.assertEqual(registry.records["terminal-1"].source, "synthetic")

    def test_refresh_keeps_surviving_session_identity_in_its_slot(self) -> None:
        class MutableAdapter:
            refs = [
                TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "first"),
                TerminalSessionRef("org.kde.konsole-2", "/Sessions/1", 3, 4, "second"),
            ]

            def discover(self):
                return list(self.refs)

        adapter = MutableAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        second_identity = stable_terminal_identity(adapter.refs[1])

        adapter.refs = [adapter.refs[1]]
        registry.refresh_terminals()

        self.assertEqual(registry.records["terminal-2"].stable_identity, second_identity)
        self.assertEqual(registry.records["terminal-1"].source, "synthetic")
        self.assertEqual(registry.records["terminal-2"].target.label, "Original-Terminal 2 — second")

    def test_new_session_cannot_steal_remembered_slot_from_survivor(self) -> None:
        class ReorderingAdapter:
            first = TerminalSessionRef("org.kde.konsole-2", "/Sessions/1", 2, 3, "survivor")
            second = TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "closing")
            new = TerminalSessionRef("org.kde.konsole-3", "/Sessions/1", 4, 5, "new")
            refs = [first, second]

            def discover(self):
                return list(self.refs)

        adapter = ReorderingAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        survivor_identity = stable_terminal_identity(adapter.first)

        adapter.refs = [adapter.new, adapter.first]
        registry.refresh_terminals()

        self.assertEqual(registry.records["terminal-1"].stable_identity, survivor_identity)
        self.assertEqual(registry.records["terminal-1"].target.label, "Original-Terminal 1 — survivor")
        self.assertEqual(registry.records["terminal-2"].target.label, "Original-Terminal 2 — new")

    def test_pid_reuse_creates_new_identity_and_drops_old_selection(self) -> None:
        class ReusedPidAdapter:
            ref = TerminalSessionRef("org.kde.konsole-7", "/Sessions/1", 7, 8, "old")

            def discover(self):
                return [self.ref]

        adapter = ReusedPidAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        registry.select("terminal-1")
        old_identity = registry.records["terminal-1"].stable_identity

        adapter.ref = TerminalSessionRef("org.kde.konsole-7", "/Sessions/1", 99, 100, "new")
        registry.refresh_terminals()

        self.assertNotEqual(registry.records["terminal-1"].stable_identity, old_identity)
        self.assertEqual(registry.selected_target_id, "win-desktop")

    def test_record_wire_dict_does_not_expose_internal_identity(self) -> None:
        record = TargetRegistry(PlatformUnavailableAdapter()).records["win-desktop"]
        self.assertNotIn("stable_identity", record.to_dict())

    def test_bridge_inventory_applies_remote_terminals_atomically(self) -> None:
        registry = TargetRegistry(PlatformUnavailableAdapter())
        payload = {
            "status": "ok",
            "captured_at_ms": 10,
            "targets": [{
                "id": "terminal-1",
                "kind": "linux.terminal",
                "host": "vps",
                "label": "Original-Terminal 1 — bash",
                "source": "real",
                "availability": "available",
                "capture_method": "konsole-dbus:getAllDisplayedText",
                "identity": "org.kde.konsole-1|/Sessions/1|pid=7",
            }],
        }

        self.assertEqual(registry.apply_remote_inventory(payload), 1)
        remote_id = "bridge-agent:terminal-1"
        self.assertEqual(registry.records[remote_id].source, "bridge-agent:real")
        self.assertEqual(registry.records[remote_id].availability, "unavailable")
        self.assertEqual(registry.records[remote_id].stable_identity, payload["targets"][0]["identity"])

        registry.select(remote_id)
        self.assertEqual(registry.apply_remote_inventory({
            "status": "ok", "captured_at_ms": 11, "targets": []
        }), 0)
        self.assertEqual(registry.records["terminal-1"].source, "synthetic")
        self.assertEqual(registry.selected_target_id, "win-desktop")

    def test_bridge_inventory_rejects_unknown_target_kind(self) -> None:
        registry = TargetRegistry(PlatformUnavailableAdapter())
        with self.assertRaisesRegex(ValueError, "invalid_remote_inventory_target_kind"):
            registry.apply_remote_inventory({
                "status": "ok", "captured_at_ms": 10, "targets": [{
                    "id": "terminal-1", "kind": "windows.desktop", "host": "vps",
                    "label": "wrong", "source": "real", "availability": "available",
                    "capture_method": "test", "identity": "identity",
                }],
            })

    def test_bridge_inventory_exports_real_sessions_but_not_probe(self) -> None:
        class ProbeAdapter:
            refs = [TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "real")]

            def discover(self):
                return list(self.refs)

        registry = TargetRegistry(ProbeAdapter())  # type: ignore[arg-type]
        registry.register_probe(TerminalSessionRef("org.kde.konsole-probe", "/Sessions/9", 9, 10, "probe"))
        inventory = registry.bridge_inventory()

        self.assertEqual([item["id"] for item in inventory["targets"]], ["terminal-1"])
        self.assertEqual(inventory["targets"][0]["identity"], registry.records["terminal-1"].stable_identity)

    def test_refresh_swaps_complete_record_snapshot(self) -> None:
        class MutableAdapter:
            refs = [TerminalSessionRef("org.kde.konsole-1", "/Sessions/1", 1, 2, "first")]

            def discover(self):
                return list(self.refs)

        adapter = MutableAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        old_records = registry.records
        adapter.refs = []
        registry.refresh_terminals()

        self.assertIsNot(registry.records, old_records)
        self.assertEqual(old_records["terminal-1"].source, "real")
        self.assertEqual(registry.records["terminal-1"].source, "synthetic")

    def test_probe_can_be_released_and_return_to_discovery(self) -> None:
        class ProbeAdapter:
            ref = TerminalSessionRef("org.kde.konsole-4", "/Sessions/1", 4, 5, "probe")

            def discover(self):
                return [self.ref]

        adapter = ProbeAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        probe = registry.register_probe(adapter.ref)
        registry.select("terminal-probe")

        self.assertTrue(registry.unregister_probe(stable_identity=probe.stable_identity))
        self.assertNotIn("terminal-probe", registry.records)
        self.assertEqual(registry.selected_target_id, "win-desktop")
        registry.refresh_terminals()
        self.assertEqual(registry.records["terminal-1"].source, "real")

    def test_degraded_discovery_preserves_last_complete_snapshot(self) -> None:
        class FailingAdapter:
            ref = TerminalSessionRef("org.kde.konsole-8", "/Sessions/1", 8, 9, "stable")
            result = TerminalDiscovery((ref,), "ok")

            def discover(self):
                return list(self.result.refs)

            def discover_result(self):
                return self.result

        adapter = FailingAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        old_identity = registry.records["terminal-1"].stable_identity
        adapter.result = TerminalDiscovery((), "degraded", "temporary qdbus failure")

        registry.refresh_terminals()

        self.assertEqual(registry.records["terminal-1"].source, "real")
        self.assertEqual(registry.records["terminal-1"].stable_identity, old_identity)

    def test_refresh_result_is_discarded_when_probe_mutates_registry_mid_discovery(self) -> None:
        class ReentrantAdapter:
            ref = TerminalSessionRef("org.kde.konsole-9", "/Sessions/1", 9, 10, "probe")
            registry = None
            calls = 0

            def discover(self):
                return [self.ref]

            def discover_result(self):
                self.calls += 1
                if self.registry is not None:
                    self.registry.register_probe(self.ref)
                return TerminalDiscovery((self.ref,), "ok")

        adapter = ReentrantAdapter()
        registry = TargetRegistry(adapter)  # type: ignore[arg-type]
        adapter.registry = registry

        registry.refresh_terminals()

        self.assertEqual(adapter.calls, 2)
        self.assertIn("terminal-probe", registry.records)
        self.assertNotIn("terminal-1", registry._discovered_terminal_ids)

    def test_unavailable_static_target_is_explicit(self) -> None:
        class NoKonsole:
            def discover(self):
                return []

            def inspect(self, **_kwargs):
                raise AssertionError("static unavailable target must not call adapter")

        registry = TargetRegistry(NoKonsole())  # type: ignore[arg-type]
        snapshot = registry.inspect("terminal-1")
        self.assertEqual(snapshot.status, "unavailable")
        self.assertEqual(snapshot.source, "synthetic")
        self.assertEqual(snapshot.availability, "unavailable")

    def test_snapshot_is_machine_readable(self) -> None:
        snapshot = TerminalSnapshot(
            target_id="terminal-1",
            source="real",
            availability="available",
            status="observed",
            capture_method="test",
            captured_at_ms=10,
            session_pid=1,
            foreground_pid=2,
            title="bash",
            output="ok",
        )
        self.assertEqual(snapshot.to_dict()["status"], "observed")

    def test_probe_command_echo_does_not_contain_full_marker(self) -> None:
        fake = FakeQdbus()
        adapter = KonsoleAdapter(runner=fake, command="qdbus6")
        ref = adapter.discover()[0]
        marker = "AUGEN_HAENDE_PROBE_0007"

        delivery = adapter.send_probe(ref=ref, marker=marker)

        self.assertEqual(delivery.status, "delivered")
        self.assertEqual(delivery.command_shape, "printf-split-marker")
        send_call = next(call for call in fake.calls if any("Session.sendText" in value for value in call))
        command = send_call[-1]
        self.assertNotIn(marker, command)
        self.assertIn("printf '%s%s\\n'", command)


if __name__ == "__main__":
    unittest.main()
