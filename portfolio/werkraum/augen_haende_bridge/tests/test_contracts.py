from __future__ import annotations

from dataclasses import replace
import unittest

from augen_haende_bridge import (
    ActionKind,
    ActionRequest,
    Agent,
    Binding,
    Capability,
    DecisionStatus,
    Lease,
    Target,
    TargetScanItem,
    TargetScanSnapshot,
    TargetKind,
    InMemoryBridgeCore,
    InputArbitrator,
    FrameSnapshot,
    FrameSource,
    FrameVisibility,
    SessionState,
    VisionSession,
    TargetBounds,
    evaluate_action,
)


WINDOWS_SURFACE = "surface:windows:bridge"


class ContractPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = {
            "codex": Agent("codex", "Codex"),
            "gemini": Agent("gemini", "Gemini"),
        }
        self.targets = {
            "win-desktop": Target(
                "win-desktop", TargetKind.WINDOWS_DESKTOP, "Windows kompletter Desktop", "thinkpad"
            ),
            "kde-1": Target(
                "kde-1", TargetKind.LINUX_KDE_DESKTOP, "Linux KDE Desktop 1", "vps"
            ),
            "term-1": Target(
                "term-1", TargetKind.LINUX_TERMINAL, "Original-Terminal 1", "vps"
            ),
        }
        self.bindings = [
            Binding(
                "codex",
                "win-desktop",
                capabilities=frozenset({Capability.OBSERVE, Capability.OVERLAY}),
            ),
            Binding(
                "gemini",
                "kde-1",
                capabilities=frozenset({Capability.OBSERVE, Capability.TERMINAL}),
            ),
        ]
        self.leases = {
            "lease-gemini-kde": Lease(
                "lease-gemini-kde", "gemini", "kde-1", Capability.TERMINAL, expires_at_ms=2_000
            )
        }

    def request(self, **overrides: object) -> ActionRequest:
        values: dict[str, object] = {
            "request_id": "req-1",
            "session_id": "session-1",
            "agent_id": "gemini",
            "surface_id": WINDOWS_SURFACE,
            "target_id": "kde-1",
            "capability": Capability.TERMINAL,
            "action": ActionKind.TERMINAL,
            "lease_id": "lease-gemini-kde",
        }
        values.update(overrides)
        return ActionRequest(**values)  # type: ignore[arg-type]

    def evaluate(self, request: ActionRequest, *, emergency_stop: bool = False):
        return evaluate_action(
            request,
            agents=self.agents,
            targets=self.targets,
            bindings=self.bindings,
            leases=self.leases,
            now_ms=1_000,
            emergency_stop=emergency_stop,
        )

    def test_linux_target_and_windows_surface_are_separate(self) -> None:
        result = self.evaluate(self.request())
        self.assertEqual(result.status, DecisionStatus.ACCEPTED)
        self.assertEqual(result.target_id, "kde-1")
        self.assertEqual(result.audit_event, "action.accepted")

    def test_unbound_linux_target_cannot_fall_through_to_windows(self) -> None:
        result = self.evaluate(self.request(target_id="win-desktop"))
        self.assertEqual(result.status, DecisionStatus.DENIED)
        self.assertEqual(result.reason, "agent_target_not_bound")

    def test_expired_lease_denies_terminal_action(self) -> None:
        result = evaluate_action(
            self.request(),
            agents=self.agents,
            targets=self.targets,
            bindings=self.bindings,
            leases=self.leases,
            now_ms=2_000,
        )
        self.assertEqual(result.status, DecisionStatus.DENIED)
        self.assertEqual(result.reason, "lease_expired")

    def test_emergency_stop_denies_even_valid_request(self) -> None:
        result = self.evaluate(self.request(), emergency_stop=True)
        self.assertEqual(result.status, DecisionStatus.DENIED)
        self.assertEqual(result.reason, "emergency_stop_active")

    def test_overlay_can_be_bound_to_windows_desktop_without_input_lease(self) -> None:
        result = self.evaluate(
            self.request(
                request_id="req-win-overlay",
                agent_id="codex",
                target_id="win-desktop",
                capability=Capability.OVERLAY,
                action=ActionKind.OVERLAY,
                lease_id=None,
            )
        )
        self.assertEqual(result.status, DecisionStatus.ACCEPTED)

    def test_request_is_explicitly_serializable(self) -> None:
        payload = self.request().to_dict()
        self.assertEqual(payload["surface_id"], WINDOWS_SURFACE)
        self.assertEqual(payload["target_id"], "kde-1")
        self.assertEqual(payload["capability"], "terminal")

    def test_target_scan_snapshot_keeps_visual_and_structured_witnesses(self) -> None:
        item = TargetScanItem(
            target_id="windows.window:1234",
            generation="proc-44:created-1000",
            kind=TargetKind.WINDOWS_WINDOW,
            label="Browser",
            host="thinkpad",
            rect=(10, 20, 800, 600),
            z_order=2,
            virtual_desktop="windows-vdesk-1",
            process_id=44,
            process_path="C:/browser.exe",
            source="native",
            availability="available",
            capabilities=frozenset({"capture", "overlay"}),
        )
        snapshot = TargetScanSnapshot(
            scan_id="scan-1",
            captured_at_ms=1000,
            source="windows.native.scanner",
            frame_ref="memory://frame-1",
            frame_hash="sha256:frame-1",
            default_target_id="windows.desktop:thinkpad",
            items=(item,),
        )

        payload = snapshot.to_dict()
        self.assertEqual(payload["default_target_id"], "windows.desktop:thinkpad")
        self.assertEqual(payload["items"][0]["generation"], "proc-44:created-1000")
        self.assertEqual(payload["items"][0]["capabilities"], ["capture", "overlay"])


class LoopbackCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.core = InMemoryBridgeCore()
        self.core.add_agent(Agent("gemini", "Gemini"))
        self.core.add_target(Target("kde-1", TargetKind.LINUX_KDE_DESKTOP, "KDE Desktop 1", "vps"))
        self.core.add_binding(
            Binding(
                "gemini",
                "kde-1",
                capabilities=frozenset({Capability.OBSERVE, Capability.TERMINAL}),
            )
        )
        self.core.add_lease(Lease("lease-1", "gemini", "kde-1", Capability.TERMINAL, 2_000))

    def test_loopback_records_request_then_policy_decision(self) -> None:
        request = ActionRequest(
            request_id="req-loopback",
            session_id="session-loopback",
            agent_id="gemini",
            surface_id=WINDOWS_SURFACE,
            target_id="kde-1",
            capability=Capability.TERMINAL,
            action=ActionKind.TERMINAL,
            lease_id="lease-1",
        )
        result = self.core.handle(request, now_ms=1_000)

        self.assertEqual(result.status, DecisionStatus.ACCEPTED)
        self.assertEqual([event.event_type for event in self.core.audit], [
            "action.requested",
            "action.accepted",
        ])
        self.assertEqual(self.core.audit[-1].details["reason"], "policy_allows_dispatch")

    def test_loopback_never_dispatches_a_platform_action(self) -> None:
        request = ActionRequest(
            request_id="req-no-dispatch",
            session_id="session-loopback",
            agent_id="gemini",
            surface_id=WINDOWS_SURFACE,
            target_id="kde-1",
            capability=Capability.TERMINAL,
            action=ActionKind.TERMINAL,
            lease_id="lease-1",
        )
        self.core.handle(request, now_ms=1_000)
        self.assertNotIn("action.dispatched", [event.event_type for event in self.core.audit])

    def test_emergency_stop_is_audited_and_blocks_following_request(self) -> None:
        self.core.set_emergency_stop(True, reason="test")
        request = ActionRequest(
            request_id="req-stopped",
            session_id="session-loopback",
            agent_id="gemini",
            surface_id=WINDOWS_SURFACE,
            target_id="kde-1",
            capability=Capability.TERMINAL,
            action=ActionKind.TERMINAL,
            lease_id="lease-1",
        )
        result = self.core.handle(request, now_ms=1_000)
        self.assertEqual(result.reason, "emergency_stop_active")
        self.assertEqual(self.core.audit[0].event_type, "emergency_stop.changed")


class VisionSessionTests(unittest.TestCase):
    def frame(self, frame_id: str, visibility: FrameVisibility, owner: str | None = None):
        return FrameSnapshot(
            frame_id=frame_id,
            timestamp_ms=int(frame_id.removeprefix("f-")),
            source=FrameSource.LIVE_CAPTURE,
            visibility=visibility,
            payload_ref=f"memory://{frame_id}",
            owner_agent_id=owner,
        )

    def test_start_pause_resume_stop_controls_frame_ingress(self) -> None:
        session = VisionSession("vision-1", target_id="win-desktop")
        with self.assertRaises(RuntimeError):
            session.append_frame(self.frame("f-1", FrameVisibility.SHARED_GATE))

        session.start()
        session.append_frame(self.frame("f-1", FrameVisibility.SHARED_GATE))
        session.pause()
        with self.assertRaises(RuntimeError):
            session.append_frame(self.frame("f-2", FrameVisibility.SHARED_GATE))
        session.resume()
        session.append_frame(self.frame("f-2", FrameVisibility.SHARED_GATE))
        session.stop()
        self.assertEqual(session.state, SessionState.STOPPED)

    def test_ring_is_bounded_and_visibility_is_recipient_specific(self) -> None:
        session = VisionSession("vision-2", max_frames=3)
        session.start()
        session.append_frame(self.frame("f-1", FrameVisibility.DANIEL))
        session.append_frame(self.frame("f-2", FrameVisibility.AGENT, owner="codex"))
        session.append_frame(self.frame("f-3", FrameVisibility.AGENT, owner="gemini"))
        session.append_frame(self.frame("f-4", FrameVisibility.SHARED_GATE))

        self.assertEqual([frame.frame_id for frame in session.frames()], ["f-2", "f-3", "f-4"])
        self.assertEqual([frame.frame_id for frame in session.frames_for(agent_id="codex")], ["f-2"])
        self.assertEqual([frame.frame_id for frame in session.frames_for(agent_id="gemini")], ["f-3"])
        self.assertEqual([frame.frame_id for frame in session.frames_for(shared_gate=True)], ["f-4"])
        self.assertEqual([frame.frame_id for frame in session.frames_for(daniel=True)], [])

    def test_scrub_creates_a_paused_branch_with_provenance(self) -> None:
        session = VisionSession("vision-parent", max_frames=5)
        session.start()
        for index in range(1, 4):
            session.append_frame(self.frame(f"f-{index}", FrameVisibility.SHARED_GATE))

        branch = session.scrub("f-2", new_session_id="vision-branch")
        self.assertEqual(branch.state, SessionState.PAUSED)
        self.assertEqual(branch.parent_session_id, "vision-parent")
        self.assertEqual(branch.branched_from_frame_id, "f-2")
        self.assertEqual([frame.frame_id for frame in branch.frames()], ["f-1", "f-2"])


class InputArbitratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.core = InMemoryBridgeCore()
        self.core.add_agent(Agent("codex", "Codex"))
        self.core.add_target(Target("win-window", TargetKind.WINDOWS_WINDOW, "Testfenster", "thinkpad"))
        self.core.add_binding(
            Binding("codex", "win-window", capabilities=frozenset({Capability.INPUT}))
        )
        self.core.add_lease(Lease("lease-input", "codex", "win-window", Capability.INPUT, 2_000))
        self.arbitrator = InputArbitrator(self.core)
        self.arbitrator.set_bounds(TargetBounds("win-window", 100, 100, 500, 400))

    def request(self, request_id: str = "req-input") -> ActionRequest:
        return ActionRequest(
            request_id=request_id,
            session_id="session-input",
            agent_id="codex",
            surface_id=WINDOWS_SURFACE,
            target_id="win-window",
            capability=Capability.INPUT,
            action=ActionKind.CLICK,
            lease_id="lease-input",
        )

    def test_inside_target_cage_is_ready_but_not_dispatched(self) -> None:
        decision = self.arbitrator.authorize(self.request(), x=200, y=200, now_ms=1_000)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "ready_for_adapter_dispatch")
        self.assertNotIn("action.dispatched", [event.event_type for event in self.core.audit])

    def test_outside_target_cage_is_denied(self) -> None:
        decision = self.arbitrator.authorize(self.request(), x=99, y=200, now_ms=1_000)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "outside_target_cage")

    def test_human_override_blocks_matching_target(self) -> None:
        self.arbitrator.set_human_override("win-window")
        decision = self.arbitrator.authorize(self.request(), x=200, y=200, now_ms=1_000)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "human_override_active")

    def test_human_override_without_target_blocks_all_targets(self) -> None:
        self.arbitrator.set_human_override(None)
        decision = self.arbitrator.authorize(self.request(), x=200, y=200, now_ms=1_000)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "human_override_active")

    def test_emergency_stop_blocks_valid_input(self) -> None:
        self.arbitrator.trigger_emergency_stop()
        decision = self.arbitrator.authorize(self.request(), x=200, y=200, now_ms=1_000)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "emergency_stop_active")

    def test_wrong_lease_is_rejected_by_core_policy(self) -> None:
        decision = self.arbitrator.authorize(
            replace(self.request("req-wrong-lease"), lease_id="missing"),
            x=200,
            y=200,
            now_ms=1_000,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "unknown_lease")
