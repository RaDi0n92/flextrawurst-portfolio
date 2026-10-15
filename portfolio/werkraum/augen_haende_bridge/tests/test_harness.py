from __future__ import annotations

import unittest

from augen_haende_bridge import (
    BUILD_CONTEXT_SOURCES,
    BUILD_CYCLE_SEQUENCE,
    BUILD_CYCLE_SKILL_PATHS,
    BRIDGE_FOCUS_ANCHORS,
    MCP_P0_PROOF_SEQUENCE,
    CHATGPT_FIRST_SLICE_PROOF_SEQUENCE,
    ChatGPTEventLane,
    ChatGPTHarnessRun,
    BuildCycleRun,
    FocusContract,
    HarnessEdge,
    HarnessGraph,
    HarnessNode,
    HarnessRun,
    MCPPreflightRun,
    NodeKind,
    RunStatus,
    SessionContinuity,
    SCANNER_PROOF_SEQUENCE,
)


def demo_graph() -> HarnessGraph:
    return HarnessGraph(
        id="demo",
        start_node_id="state-start",
        nodes={
            "state-start": HarnessNode("state-start", NodeKind.STATE, "Start"),
            "action-say": HarnessNode("action-say", NodeKind.ACTION, "Say", capability="say", target_id="win"),
            "observe": HarnessNode("observe", NodeKind.OBSERVATION, "Observe"),
            "gate": HarnessNode("gate", NodeKind.GATE, "Playwright proof"),
            "done": HarnessNode("done", NodeKind.STATE, "Done"),
        },
        edges=(
            HarnessEdge("state-start", "action-say"),
            HarnessEdge("action-say", "observe", "observed"),
            HarnessEdge("observe", "gate"),
            HarnessEdge("gate", "done", "pass"),
        ),
    )


def focus_contract(next_step: str = "native-first-contact") -> FocusContract:
    return FocusContract(
        goal_id="G01",
        next_step=next_step,
        preserved_anchors=BRIDGE_FOCUS_ANCHORS,
        forbidden_drift=("synthetic_surface_as_product", "chatgpt_hidden_in_g09"),
    )


class HarnessTests(unittest.TestCase):
    def test_build_cycle_requires_both_skill_reads_and_context(self) -> None:
        run = BuildCycleRun("cycle-1", build_step_id="native-first-contact", focus_contract=focus_contract())
        run.start()
        run.attest("skill_opening_read", detail="opening contracts", read_paths=tuple(BUILD_CYCLE_SKILL_PATHS))
        run.attest(
            "context_rehydrated",
            detail="docs git code evidence reconstructed",
            context_sources=tuple(BUILD_CONTEXT_SOURCES),
        )
        run.attest("skill_prebuild_read", detail="pre-build reread", read_paths=tuple(BUILD_CYCLE_SKILL_PATHS))
        run.attest("build_step_executed", detail="one isolated first-contact change")
        run.attest("evidence_recorded", detail="core and platform evidence classified")
        run.attest("skill_closing_read", detail="post-build contract check", read_paths=tuple(BUILD_CYCLE_SKILL_PATHS))
        run.attest("protocol_recorded", detail="handoff recorded")

        self.assertEqual(run.status, RunStatus.COMPLETED)
        self.assertEqual(tuple(run.phases), BUILD_CYCLE_SEQUENCE)
        self.assertIsNone(run.next_phase)

    def test_build_cycle_blocks_when_prebuild_skill_read_is_skipped(self) -> None:
        run = BuildCycleRun("cycle-2", build_step_id="scanner", focus_contract=focus_contract("scanner"))
        run.start()
        run.attest("skill_opening_read", detail="opening contracts", read_paths=tuple(BUILD_CYCLE_SKILL_PATHS))
        run.attest(
            "context_rehydrated",
            detail="docs git code evidence reconstructed",
            context_sources=tuple(BUILD_CONTEXT_SOURCES),
        )
        with self.assertRaisesRegex(RuntimeError, "expected skill_prebuild_read"):
            run.attest("build_step_executed", detail="attempted build")
        self.assertEqual(run.status, RunStatus.BLOCKED)

    def test_build_cycle_requires_closing_skill_read_before_protocol(self) -> None:
        run = BuildCycleRun("cycle-3", build_step_id="terminal", focus_contract=focus_contract("terminal"))
        run.start()
        run.attest("skill_opening_read", detail="opening contracts", read_paths=tuple(BUILD_CYCLE_SKILL_PATHS))
        run.attest(
            "context_rehydrated",
            detail="docs git code evidence reconstructed",
            context_sources=tuple(BUILD_CONTEXT_SOURCES),
        )
        run.attest("skill_prebuild_read", detail="pre-build reread", read_paths=tuple(BUILD_CYCLE_SKILL_PATHS))
        run.attest("build_step_executed", detail="one isolated terminal change")
        run.attest("evidence_recorded", detail="evidence classified")
        with self.assertRaisesRegex(RuntimeError, "expected skill_closing_read"):
            run.attest("protocol_recorded", detail="premature handoff")
        self.assertEqual(run.status, RunStatus.BLOCKED)

    def test_build_cycle_blocks_without_focus_contract(self) -> None:
        run = BuildCycleRun("cycle-focus", build_step_id="native-first-contact")
        with self.assertRaisesRegex(RuntimeError, "focus contract"):
            run.start()
        self.assertEqual(run.status, RunStatus.BLOCKED)

    def test_build_cycle_blocks_when_a_decision_anchor_is_missing(self) -> None:
        contract = FocusContract(
            goal_id="G01",
            next_step="native-first-contact",
            preserved_anchors=tuple(anchor for anchor in BRIDGE_FOCUS_ANCHORS if anchor != "chatgpt_slice_after_native_path"),
            forbidden_drift=("chatgpt_hidden_in_g09",),
        )
        run = BuildCycleRun("cycle-anchor", build_step_id="native-first-contact", focus_contract=contract)
        with self.assertRaisesRegex(RuntimeError, "missing_focus_anchors"):
            run.start()
        self.assertEqual(run.status, RunStatus.BLOCKED)

    def test_mcp_p0_runs_for_a_provider_and_keeps_atlas_scope(self) -> None:
        run = MCPPreflightRun(
            "mcp-p0-codex",
            ai_stream_id="codex",
            access_path="mcp_provider",
            server_id="vps-mcp",
            tool_profile="atlas",
        )
        run.start()
        run.attest("configured")
        run.attest("reachable")
        run.attest("handshake_succeeded", session_id="mcp-codex-1")
        run.attest("tools_list_received", tool_count=148)
        run.attest("atlas_read_verified", tool_name="atlas.read")

        self.assertEqual(run.status, RunStatus.COMPLETED)
        self.assertEqual(run.continuity, SessionContinuity.ALIVE)
        self.assertEqual(run.to_dict()["tool_profile"], "atlas")
        self.assertEqual(run.to_dict()["proofs"], list(MCP_P0_PROOF_SEQUENCE))

    def test_mcp_p0_blocks_when_a_handshake_is_only_claimed(self) -> None:
        run = MCPPreflightRun(
            "mcp-p0-claude",
            ai_stream_id="claude",
            access_path="mcp_provider",
            server_id="vps-mcp",
        )
        run.start()
        run.attest("configured")
        run.attest("reachable")
        with self.assertRaisesRegex(RuntimeError, "session_mode"):
            run.attest("handshake_succeeded")
        self.assertEqual(run.status, RunStatus.BLOCKED)
        self.assertEqual(run.last_error, "session_mode_unattested")

    def test_mcp_p0_accepts_an_explicit_stateless_transport(self) -> None:
        run = MCPPreflightRun(
            "mcp-p0-stateless",
            ai_stream_id="codex",
            access_path="mcp_provider",
            server_id="vps-mcp",
        )
        run.start()
        run.attest("configured")
        run.attest("reachable")
        run.attest("handshake_succeeded", session_mode="stateless")
        self.assertEqual(run.session_mode, "stateless")
        self.assertIsNone(run.session_id)

    def test_mcp_p0_surfaces_session_shipwreck_states(self) -> None:
        run = MCPPreflightRun(
            "mcp-p0-gemini",
            ai_stream_id="gemini",
            access_path="mcp_provider",
            server_id="vps-mcp",
        )
        run.start()
        run.attest("configured")
        run.attest("reachable")
        run.attest("handshake_succeeded", session_id="mcp-gemini-1")
        run.mark_continuity(SessionContinuity.CONTEXT_COMPACTED)
        self.assertEqual(run.continuity, SessionContinuity.CONTEXT_COMPACTED)
        run.mark_continuity(SessionContinuity.SESSION_CHANGED, new_session_id="mcp-gemini-2")
        self.assertEqual(run.session_id, "mcp-gemini-2")
        run.mark_continuity(SessionContinuity.HANDOFF_REQUIRED)
        self.assertEqual(run.status, RunStatus.BLOCKED)

    def test_chatgpt_chat_and_action_lanes_are_distinct(self) -> None:
        run = ChatGPTHarnessRun("gpt-run", session_id="gpt-session", target_id="firefox")
        run.start()
        message = run.record_chat_message("msg-1", sender="daniel")

        self.assertEqual(message.lane, ChatGPTEventLane.CHAT)
        self.assertEqual(run.events[0].event_type, "chat.message")

        with self.assertRaisesRegex(RuntimeError, "plain_chat_cannot_trigger_action"):
            run.record_action(
                "call-1",
                sender="chatgpt",
                tool_name="windows_desktop_act",
                caused_by_event_id=message.event_id,
            )
        self.assertEqual(run.status, RunStatus.BLOCKED)
        self.assertEqual(run.block_reason, "plain_chat_cannot_trigger_action")

    def test_chatgpt_explicit_action_is_not_a_plain_chat_trigger(self) -> None:
        run = ChatGPTHarnessRun("gpt-run-explicit", session_id="gpt-session", target_id="firefox")
        run.start()
        run.record_chat_message("msg-1", sender="daniel")
        action = run.record_action(
            "call-1",
            sender="chatgpt",
            tool_name="windows_desktop_act",
            explicit_dispatch=True,
        )
        self.assertEqual(action.lane, ChatGPTEventLane.ACTION)
        self.assertTrue(action.explicit_dispatch)

    def test_chatgpt_first_slice_proofs_are_ordered_and_serializable(self) -> None:
        run = ChatGPTHarnessRun("gpt-run-proof", session_id="gpt-session", target_id="firefox")
        run.start()
        run.record_chat_message("msg-1", sender="daniel")
        for proof in CHATGPT_FIRST_SLICE_PROOF_SEQUENCE:
            run.attest(proof)

        self.assertEqual(run.status, RunStatus.COMPLETED)
        self.assertEqual(run.to_dict()["proofs"], list(CHATGPT_FIRST_SLICE_PROOF_SEQUENCE))

    def test_chatgpt_unknown_sender_blocks_before_it_enters_the_ledger(self) -> None:
        run = ChatGPTHarnessRun("gpt-run-sender", session_id="gpt-session")
        run.start()
        with self.assertRaisesRegex(RuntimeError, "unknown ChatGPT sender"):
            run.record_chat_message("msg-1", sender="pretend_system")
        self.assertEqual(run.status, RunStatus.BLOCKED)

    def test_graph_runs_only_with_capability_and_target(self) -> None:
        run = HarnessRun("run-1", demo_graph(), capabilities=frozenset({"say"}), target_id="win")
        run.start()
        self.assertEqual(run.step().id, "action-say")
        self.assertEqual(run.step("observed").id, "observe")
        self.assertEqual(run.step().id, "gate")
        self.assertEqual(run.step("pass").id, "done")
        run.step()
        self.assertEqual(run.status, RunStatus.COMPLETED)

    def test_missing_capability_blocks_at_action_node(self) -> None:
        run = HarnessRun("run-2", demo_graph(), capabilities=frozenset(), target_id="win")
        run.start()
        run.step()
        run.step()
        self.assertEqual(run.status, RunStatus.BLOCKED)
        self.assertIn("missing capability", run.trace[-1].detail)

    def test_checkpoint_can_create_a_new_branch(self) -> None:
        run = HarnessRun("run-parent", demo_graph(), capabilities=frozenset({"say"}), target_id="win")
        run.target_capabilities["win"] = frozenset({"say", "capture"})
        run.attest("state.observed")
        run.start()
        run.step()
        run.checkpoint("before-observation")
        branch = run.fork("before-observation", new_run_id="run-branch")
        self.assertEqual(branch.status, RunStatus.READY)
        self.assertEqual(branch.parent_run_id, "run-parent")
        self.assertEqual(branch.branched_from_checkpoint, "before-observation")
        self.assertEqual(branch.current_node_id, "action-say")
        self.assertEqual(branch.target_capabilities, {"win": frozenset({"say", "capture"})})
        self.assertIn("state.observed", branch.proofs)

    def test_gate_blocks_without_pass_signal(self) -> None:
        run = HarnessRun("run-3", demo_graph(), capabilities=frozenset({"say"}), target_id="win")
        run.start()
        run.step()
        run.step("observed")
        run.step()
        run.step("fail")
        self.assertEqual(run.status, RunStatus.BLOCKED)
        self.assertEqual(run.trace[-1].event, "blocked")

    def test_target_capability_profile_is_fail_closed(self) -> None:
        graph = HarnessGraph(
            id="target-capability",
            start_node_id="action",
            nodes={
                "action": HarnessNode(
                    "action",
                    NodeKind.ACTION,
                    "Capture",
                    target_id="window-1",
                    required_capabilities=frozenset({"capture"}),
                ),
            },
            edges=(),
        )
        run = HarnessRun(
            "run-target-capability",
            graph,
            target_id="window-1",
            target_capabilities={"window-1": frozenset({"overlay"})},
        )
        run.start()
        run.step()
        self.assertEqual(run.status, RunStatus.BLOCKED)
        self.assertIn("missing capability: capture", run.trace[-1].detail)

    def test_required_proof_blocks_until_attested(self) -> None:
        graph = HarnessGraph(
            id="proof-gate",
            start_node_id="observe",
            nodes={
                "observe": HarnessNode(
                    "observe",
                    NodeKind.OBSERVATION,
                    "Observed",
                    required_proofs=frozenset({"state.observed"}),
                ),
            },
            edges=(),
        )
        run = HarnessRun("run-proof", graph)
        run.start()
        run.step()
        self.assertEqual(run.status, RunStatus.BLOCKED)
        self.assertIn("missing proof: state.observed", run.trace[-1].detail)

        run.status = RunStatus.READY
        run.attest("state.observed", detail="read back from target")
        run.start()
        run.step()
        self.assertEqual(run.status, RunStatus.COMPLETED)

    def test_scanner_proofs_are_attested_in_live_order(self) -> None:
        run = HarnessRun("run-scanner", demo_graph())
        for proof in SCANNER_PROOF_SEQUENCE:
            run.attest(proof)
        self.assertEqual(tuple(sorted(run.proofs, key=SCANNER_PROOF_SEQUENCE.index)), SCANNER_PROOF_SEQUENCE)
        run.attest(SCANNER_PROOF_SEQUENCE[-1])
        self.assertEqual(run.trace[-1].event, "proof.duplicate")

        blocked = HarnessRun("run-scanner-blocked", demo_graph())
        blocked.attest("TARGET_SELECTED")
        self.assertEqual(blocked.status, RunStatus.BLOCKED)
        self.assertIn("expected SCAN_REQUESTED", blocked.trace[-1].detail)
