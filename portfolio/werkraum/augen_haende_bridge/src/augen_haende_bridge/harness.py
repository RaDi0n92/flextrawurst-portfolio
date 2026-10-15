"""Declarative creative harness: nodes, edges, states, gates and branches."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeKind(str, Enum):
    STATE = "state"
    ACTION = "action"
    OBSERVATION = "observation"
    GATE = "gate"


class RunStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ABORTED = "aborted"


BUILD_CYCLE_SEQUENCE: tuple[str, ...] = (
    "skill_opening_read",
    "context_rehydrated",
    "skill_prebuild_read",
    "build_step_executed",
    "evidence_recorded",
    "skill_closing_read",
    "protocol_recorded",
)

BUILD_CYCLE_SKILL_PATHS: frozenset[str] = frozenset(
    {
        "/config/.agents/skills/augen-und-haende-bridge/SKILL.md",
        "/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md",
    }
)

BUILD_CONTEXT_SOURCES: frozenset[str] = frozenset({"docs", "git", "code", "evidence"})

# These are the current non-negotiable decisions that must survive every
# bridge build cycle. They are deliberately identifiers, not free-form prose,
# so a caller cannot silently omit one while retelling the plan.
BRIDGE_FOCUS_ANCHORS: tuple[str, ...] = (
    "legacy_gemini_prototype_retired",
    "synthetic_proof_surface_not_product",
    "native_bridge_before_product_surface",
    "chatgpt_slice_after_native_path",
    "chatgpt_not_folded_into_multi_agent",
)


@dataclass(frozen=True)
class FocusContract:
    """The semantic handrail for one build cycle.

    BuildCycleRun already enforced *how* the cycle was documented. This
    contract also records *what must survive* the cycle and the one concrete
    next step, so a long context cannot quietly replace the current plan.
    """

    goal_id: str
    next_step: str
    preserved_anchors: tuple[str, ...]
    forbidden_drift: tuple[str, ...]

    def validate(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("missing_focus_goal_id")
        if not self.next_step.strip():
            raise ValueError("missing_focus_next_step")
        missing = set(BRIDGE_FOCUS_ANCHORS) - set(self.preserved_anchors)
        if missing:
            raise ValueError(f"missing_focus_anchors:{','.join(sorted(missing))}")
        if not self.forbidden_drift:
            raise ValueError("missing_forbidden_drift")


@dataclass(frozen=True)
class BuildCycleAttestation:
    """One explicit, human/agent-attested phase of a build cycle."""

    phase: str
    detail: str
    read_paths: tuple[str, ...] = ()
    context_sources: tuple[str, ...] = ()


@dataclass
class BuildCycleRun:
    """Fail-closed ordering gate for one small bridge build/proof step.

    The harness does not pretend to read files on its own. It requires the
    caller to attest the actual skill/context reads, build, evidence and final
    documentation in the only accepted order.
    """

    id: str
    build_step_id: str
    focus_contract: FocusContract | None = None
    status: RunStatus = RunStatus.READY
    phases: list[str] = field(default_factory=list)
    attestations: list[BuildCycleAttestation] = field(default_factory=list)
    block_reason: str | None = None

    def start(self) -> None:
        if not self.build_step_id:
            self._block("missing_build_step_id")
            raise RuntimeError("build_step_id is required")
        if self.focus_contract is None:
            self._block("missing_focus_contract")
            raise RuntimeError("focus contract is required")
        try:
            self.focus_contract.validate()
        except ValueError as exc:
            self._block(str(exc))
            raise RuntimeError(f"invalid focus contract: {exc}") from exc
        if self.status not in {RunStatus.READY, RunStatus.PAUSED}:
            raise RuntimeError(f"cannot start build cycle in state {self.status.value}")
        self.status = RunStatus.RUNNING

    def attest(
        self,
        phase: str,
        *,
        detail: str,
        read_paths: tuple[str, ...] = (),
        context_sources: tuple[str, ...] = (),
    ) -> None:
        """Record one phase and reject skipped or unauditable steps."""

        if self.status != RunStatus.RUNNING:
            raise RuntimeError(f"build cycle is not running: {self.status.value}")
        if phase not in BUILD_CYCLE_SEQUENCE:
            self._block(f"unknown_build_cycle_phase:{phase}")
            raise RuntimeError(f"unknown build cycle phase: {phase}")
        expected = BUILD_CYCLE_SEQUENCE[len(self.phases)]
        if phase != expected:
            self._block(f"expected:{expected};got:{phase}")
            raise RuntimeError(f"build cycle phase order expected {expected}, got {phase}")
        if not detail.strip():
            self._block(f"missing_detail:{phase}")
            raise RuntimeError(f"build cycle phase requires detail: {phase}")
        if phase in {"skill_opening_read", "skill_prebuild_read", "skill_closing_read"}:
            missing = BUILD_CYCLE_SKILL_PATHS - set(read_paths)
            if missing:
                self._block(f"missing_skill_paths:{','.join(sorted(missing))}")
                raise RuntimeError(f"skill phase missing paths: {sorted(missing)}")
        if phase == "context_rehydrated":
            missing = BUILD_CONTEXT_SOURCES - set(context_sources)
            if missing:
                self._block(f"missing_context_sources:{','.join(sorted(missing))}")
                raise RuntimeError(f"context phase missing sources: {sorted(missing)}")
        self.phases.append(phase)
        self.attestations.append(
            BuildCycleAttestation(
                phase=phase,
                detail=detail,
                read_paths=tuple(sorted(set(read_paths))),
                context_sources=tuple(sorted(set(context_sources))),
            )
        )
        if len(self.phases) == len(BUILD_CYCLE_SEQUENCE):
            self.status = RunStatus.COMPLETED

    @property
    def next_phase(self) -> str | None:
        if len(self.phases) >= len(BUILD_CYCLE_SEQUENCE):
            return None
        return BUILD_CYCLE_SEQUENCE[len(self.phases)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "build_step_id": self.build_step_id,
            "focus_contract": {
                "goal_id": self.focus_contract.goal_id,
                "next_step": self.focus_contract.next_step,
                "preserved_anchors": list(self.focus_contract.preserved_anchors),
                "forbidden_drift": list(self.focus_contract.forbidden_drift),
            }
            if self.focus_contract is not None
            else None,
            "status": self.status.value,
            "block_reason": self.block_reason,
            "phases": list(self.phases),
            "next_phase": self.next_phase,
            "attestations": [
                {
                    "phase": attestation.phase,
                    "detail": attestation.detail,
                    "read_paths": list(attestation.read_paths),
                    "context_sources": list(attestation.context_sources),
                }
                for attestation in self.attestations
            ],
        }

    def _block(self, reason: str) -> None:
        self.status = RunStatus.BLOCKED
        self.block_reason = reason


class ChatGPTEventLane(str, Enum):
    """The two ledgers that must never be conflated in the ChatGPT layer."""

    CHAT = "chat"
    ACTION = "action"


CHATGPT_FIRST_SLICE_PROOF_SEQUENCE: tuple[str, ...] = (
    "session_is_real",
    "target_bound",
    "binding_read_back",
    "chat_message_submitted",
    "message_delivered",
    "chatgpt_turn_received",
    "response_rendered",
    "sender_identity_correct",
    "tool_not_triggered_by_plain_chat",
    "target_observed",
    "proof_attested",
)

CHATGPT_ALLOWED_SENDERS = frozenset({"daniel", "chatgpt", "bridge_context"})

AI_STREAM_IDS = frozenset({"chatgpt", "codex", "claude", "gemini"})
MCP_ACCESS_PATHS = frozenset({"mcp_chatgpt_web", "mcp_provider", "terminal_direct"})
MCP_SESSION_MODES = frozenset({"unknown", "stateful", "stateless"})


class SessionContinuity(str, Enum):
    ALIVE = "alive"
    RECONNECTING = "reconnecting"
    CONTEXT_COMPACTED = "context_compacted"
    SESSION_CHANGED = "session_changed"
    LOST = "lost"
    HANDOFF_REQUIRED = "handoff_required"


MCP_P0_PROOF_SEQUENCE: tuple[str, ...] = (
    "configured",
    "reachable",
    "handshake_succeeded",
    "tools_list_received",
    "atlas_read_verified",
)


@dataclass
class MCPPreflightRun:
    """Small read-only MCP health gate shared by all AI-stream adapters."""

    id: str
    ai_stream_id: str
    access_path: str
    server_id: str
    tool_profile: str = "atlas"
    session_id: str | None = None
    session_mode: str = "unknown"
    status: RunStatus = RunStatus.READY
    continuity: SessionContinuity = SessionContinuity.LOST
    proofs: list[str] = field(default_factory=list)
    tool_count: int | None = None
    atlas_tool_name: str | None = None
    last_error: str | None = None

    def start(self) -> None:
        if self.ai_stream_id not in AI_STREAM_IDS:
            self._block(f"unknown_ai_stream:{self.ai_stream_id}")
            raise RuntimeError(f"unknown AI stream: {self.ai_stream_id}")
        if self.access_path not in MCP_ACCESS_PATHS:
            self._block(f"unknown_access_path:{self.access_path}")
            raise RuntimeError(f"unknown MCP access path: {self.access_path}")
        if not self.server_id or not self.tool_profile:
            self._block("missing_server_or_tool_profile")
            raise RuntimeError("MCP server and tool profile are required")
        self.status = RunStatus.RUNNING
        self.continuity = SessionContinuity.RECONNECTING

    def attest(
        self,
        proof: str,
        *,
        session_id: str | None = None,
        tool_count: int | None = None,
        tool_name: str | None = None,
        session_mode: str | None = None,
    ) -> None:
        """Record one observed P0 fact, never skipping a failed stage."""

        self._ensure_running()
        if proof not in MCP_P0_PROOF_SEQUENCE:
            self._block(f"unknown_mcp_p0_proof:{proof}")
            raise RuntimeError(f"unknown MCP-P0 proof: {proof}")
        expected = MCP_P0_PROOF_SEQUENCE[len(self.proofs)]
        if proof != expected:
            self._block(f"expected:{expected};got:{proof}")
            raise RuntimeError(f"MCP-P0 proof order expected {expected}, got {proof}")
        if proof == "handshake_succeeded":
            selected_session_mode = session_mode or ("stateful" if session_id else "unknown")
            if selected_session_mode not in MCP_SESSION_MODES:
                self._block(f"unknown_session_mode:{selected_session_mode}")
                raise RuntimeError(f"unknown MCP session mode: {selected_session_mode}")
            if selected_session_mode == "stateful" and not session_id:
                self._block("stateful_handshake_without_session_id")
                raise RuntimeError("stateful handshake requires session_id")
            if selected_session_mode == "stateless" and session_id:
                self._block("stateless_handshake_with_session_id")
                raise RuntimeError("stateless handshake must not carry session_id")
            if selected_session_mode == "unknown":
                self._block("session_mode_unattested")
                raise RuntimeError("handshake_succeeded requires stateful or stateless session_mode")
            self.session_mode = selected_session_mode
            self.session_id = session_id
            self.continuity = SessionContinuity.ALIVE
        if proof == "tools_list_received":
            if tool_count is None or tool_count < 0:
                self._block("tools_list_without_count")
                raise RuntimeError("tools_list_received requires a non-negative tool_count")
            self.tool_count = tool_count
        if proof == "atlas_read_verified":
            if not tool_name:
                self._block("atlas_read_without_tool_name")
                raise RuntimeError("atlas_read_verified requires tool_name")
            self.atlas_tool_name = tool_name
        self.proofs.append(proof)
        if len(self.proofs) == len(MCP_P0_PROOF_SEQUENCE):
            self.status = RunStatus.COMPLETED
            self.continuity = SessionContinuity.ALIVE

    def mark_continuity(self, state: SessionContinuity, *, new_session_id: str | None = None) -> None:
        """Expose context loss/reconnect/session replacement instead of hiding it."""

        if state is SessionContinuity.SESSION_CHANGED:
            if not new_session_id or new_session_id == self.session_id:
                self._block("session_changed_without_new_id")
                raise RuntimeError("session_changed requires a new session_id")
            self.session_id = new_session_id
        self.continuity = state
        if state in {SessionContinuity.LOST, SessionContinuity.HANDOFF_REQUIRED}:
            self.status = RunStatus.BLOCKED

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "ai_stream_id": self.ai_stream_id,
            "access_path": self.access_path,
            "server_id": self.server_id,
            "tool_profile": self.tool_profile,
            "session_id": self.session_id,
            "session_mode": self.session_mode,
            "status": self.status.value,
            "continuity": self.continuity.value,
            "proofs": list(self.proofs),
            "tool_count": self.tool_count,
            "atlas_tool_name": self.atlas_tool_name,
            "last_error": self.last_error,
        }

    def _ensure_running(self) -> None:
        if self.status != RunStatus.RUNNING:
            raise RuntimeError(f"MCP-P0 run is not running: {self.status.value}")

    def _block(self, reason: str) -> None:
        self.status = RunStatus.BLOCKED
        self.last_error = reason
        self.continuity = SessionContinuity.LOST


@dataclass(frozen=True)
class ChatGPTLedgerEvent:
    """An auditable event from the ChatGPT chat or action lane."""

    event_id: str
    session_id: str
    lane: ChatGPTEventLane
    event_type: str
    sender: str
    target_id: str | None = None
    tool_name: str | None = None
    caused_by_event_id: str | None = None
    explicit_dispatch: bool = False


@dataclass
class ChatGPTHarnessRun:
    """Machine-checkable contract for the first real ChatGPT vertical slice."""

    id: str
    session_id: str
    target_id: str | None = None
    status: RunStatus = RunStatus.READY
    events: list[ChatGPTLedgerEvent] = field(default_factory=list)
    proofs: list[str] = field(default_factory=list)
    block_reason: str | None = None

    def start(self) -> None:
        if self.status not in {RunStatus.READY, RunStatus.PAUSED}:
            raise RuntimeError(f"cannot start ChatGPT run in state {self.status.value}")
        self.status = RunStatus.RUNNING

    def record_chat_message(
        self,
        event_id: str,
        *,
        sender: str,
        target_id: str | None = None,
    ) -> ChatGPTLedgerEvent:
        self._ensure_running()
        self._ensure_sender(sender)
        event = ChatGPTLedgerEvent(
            event_id=event_id,
            session_id=self.session_id,
            lane=ChatGPTEventLane.CHAT,
            event_type="chat.message",
            sender=sender,
            target_id=target_id or self.target_id,
        )
        self._append_unique(event)
        return event

    def record_action(
        self,
        event_id: str,
        *,
        sender: str,
        tool_name: str,
        target_id: str | None = None,
        caused_by_event_id: str | None = None,
        explicit_dispatch: bool = False,
    ) -> ChatGPTLedgerEvent:
        self._ensure_running()
        self._ensure_sender(sender)
        parent = self._event(caused_by_event_id) if caused_by_event_id else None
        if parent is not None and parent.lane is ChatGPTEventLane.CHAT and not explicit_dispatch:
            self._block("plain_chat_cannot_trigger_action")
            raise RuntimeError("plain_chat_cannot_trigger_action")
        event = ChatGPTLedgerEvent(
            event_id=event_id,
            session_id=self.session_id,
            lane=ChatGPTEventLane.ACTION,
            event_type="action.requested",
            sender=sender,
            target_id=target_id or self.target_id,
            tool_name=tool_name,
            caused_by_event_id=caused_by_event_id,
            explicit_dispatch=explicit_dispatch,
        )
        self._append_unique(event)
        return event

    def attest(self, proof: str) -> None:
        """Attest the first-slice proofs in order and fail closed on drift."""

        self._ensure_running()
        if proof not in CHATGPT_FIRST_SLICE_PROOF_SEQUENCE:
            self._block(f"unknown_proof:{proof}")
            raise RuntimeError(f"unknown ChatGPT proof: {proof}")
        expected = CHATGPT_FIRST_SLICE_PROOF_SEQUENCE[len(self.proofs)]
        if proof != expected:
            self._block(f"expected:{expected};got:{proof}")
            raise RuntimeError(f"ChatGPT proof order expected {expected}, got {proof}")
        if proof == "sender_identity_correct" and any(
            event.sender not in CHATGPT_ALLOWED_SENDERS for event in self.events
        ):
            self._block("unknown_sender_identity")
            raise RuntimeError("unknown_sender_identity")
        if proof == "tool_not_triggered_by_plain_chat" and any(
            event.lane is ChatGPTEventLane.ACTION
            and event.caused_by_event_id is not None
            and self._event(event.caused_by_event_id).lane is ChatGPTEventLane.CHAT
            and not event.explicit_dispatch
            for event in self.events
        ):
            self._block("plain_chat_cannot_trigger_action")
            raise RuntimeError("plain_chat_cannot_trigger_action")
        self.proofs.append(proof)
        if len(self.proofs) == len(CHATGPT_FIRST_SLICE_PROOF_SEQUENCE):
            self.status = RunStatus.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "target_id": self.target_id,
            "status": self.status.value,
            "block_reason": self.block_reason,
            "proofs": list(self.proofs),
            "events": [
                {
                    "event_id": event.event_id,
                    "session_id": event.session_id,
                    "lane": event.lane.value,
                    "event_type": event.event_type,
                    "sender": event.sender,
                    "target_id": event.target_id,
                    "tool_name": event.tool_name,
                    "caused_by_event_id": event.caused_by_event_id,
                    "explicit_dispatch": event.explicit_dispatch,
                }
                for event in self.events
            ],
        }

    def _ensure_running(self) -> None:
        if self.status != RunStatus.RUNNING:
            raise RuntimeError(f"ChatGPT run is not running: {self.status.value}")

    def _ensure_sender(self, sender: str) -> None:
        if sender not in CHATGPT_ALLOWED_SENDERS:
            self._block(f"unknown_sender:{sender}")
            raise RuntimeError(f"unknown ChatGPT sender: {sender}")

    def _append_unique(self, event: ChatGPTLedgerEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self.events):
            raise ValueError(f"duplicate ChatGPT event id: {event.event_id}")
        self.events.append(event)

    def _event(self, event_id: str | None) -> ChatGPTLedgerEvent:
        if event_id is None:
            raise KeyError("event id is required")
        for event in self.events:
            if event.event_id == event_id:
                return event
        raise KeyError(f"unknown ChatGPT event: {event_id}")

    def _block(self, reason: str) -> None:
        self.status = RunStatus.BLOCKED
        self.block_reason = reason


SCANNER_PROOF_SEQUENCE: tuple[str, ...] = (
    "SCAN_REQUESTED",
    "FRAME_CAPTURED",
    "INVENTORY_READ",
    "TARGET_SELECTED",
    "IDENTITY_VERIFIED",
    "BINDING_CREATED",
    "BINDING_READ_BACK",
    "PRE_ACTION_RESCAN",
    "TARGET_STATE_OBSERVED",
)


@dataclass(frozen=True)
class HarnessNode:
    id: str
    kind: NodeKind
    label: str
    capability: str | None = None
    target_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    required_capabilities: frozenset[str] = frozenset()
    required_proofs: frozenset[str] = frozenset()


@dataclass(frozen=True)
class HarnessEdge:
    source: str
    target: str
    condition: str = "always"


@dataclass(frozen=True)
class HarnessTrace:
    sequence: int
    node_id: str
    event: str
    status: str
    detail: str


@dataclass(frozen=True)
class HarnessCheckpoint:
    name: str
    node_id: str
    trace_length: int


@dataclass
class HarnessGraph:
    id: str
    start_node_id: str
    nodes: dict[str, HarnessNode]
    edges: tuple[HarnessEdge, ...]

    def validate(self) -> None:
        if not self.id or not self.start_node_id:
            raise ValueError("graph id and start node are required")
        if self.start_node_id not in self.nodes:
            raise ValueError(f"missing start node: {self.start_node_id}")
        for edge in self.edges:
            if edge.source not in self.nodes or edge.target not in self.nodes:
                raise ValueError(f"edge references unknown node: {edge}")

    def next_edges(self, node_id: str, signal: str) -> tuple[HarnessEdge, ...]:
        return tuple(
            edge
            for edge in self.edges
            if edge.source == node_id and edge.condition in {"always", signal}
        )


@dataclass
class HarnessRun:
    id: str
    graph: HarnessGraph
    capabilities: frozenset[str] = frozenset()
    target_capabilities: dict[str, frozenset[str]] = field(default_factory=dict)
    proofs: frozenset[str] = frozenset()
    target_id: str | None = None
    current_node_id: str | None = None
    status: RunStatus = RunStatus.READY
    parent_run_id: str | None = None
    branched_from_checkpoint: str | None = None
    trace: list[HarnessTrace] = field(default_factory=list)
    checkpoints: dict[str, HarnessCheckpoint] = field(default_factory=dict)

    def start(self) -> None:
        self.graph.validate()
        if self.status not in {RunStatus.READY, RunStatus.PAUSED}:
            raise RuntimeError(f"cannot start run in state {self.status.value}")
        if self.current_node_id is None:
            self.current_node_id = self.graph.start_node_id
        self.status = RunStatus.RUNNING
        self._trace("entered", "running", "run started or resumed")

    def pause(self) -> None:
        if self.status != RunStatus.RUNNING:
            raise RuntimeError("only a running harness can pause")
        self.status = RunStatus.PAUSED
        self._trace("paused", "paused", "operator pause")

    def abort(self, reason: str = "operator") -> None:
        if self.status in {RunStatus.COMPLETED, RunStatus.ABORTED}:
            return
        self.status = RunStatus.ABORTED
        self._trace("aborted", "aborted", reason)

    def checkpoint(self, name: str) -> HarnessCheckpoint:
        if self.current_node_id is None:
            raise RuntimeError("run has no current node")
        checkpoint = HarnessCheckpoint(name, self.current_node_id, len(self.trace))
        self.checkpoints[name] = checkpoint
        self._trace(self.current_node_id, "checkpoint", name)
        return checkpoint

    def attest(self, proof: str, *, detail: str = "") -> None:
        """Record an observed proof without pretending it executed an action."""

        if not proof:
            raise ValueError("proof is required")
        if proof in SCANNER_PROOF_SEQUENCE:
            if proof in self.proofs:
                self._trace(self.current_node_id or "", "proof.duplicate", proof)
                return
            next_index = sum(step in self.proofs for step in SCANNER_PROOF_SEQUENCE)
            expected = SCANNER_PROOF_SEQUENCE[next_index]
            if proof != expected:
                self.status = RunStatus.BLOCKED
                self._trace(
                    self.current_node_id or "",
                    "proof.blocked",
                    f"scanner proof order: expected {expected}, got {proof}",
                )
                return
        self.proofs = frozenset((*self.proofs, proof))
        self._trace(self.current_node_id or "", "proof.attested", detail or proof)

    def _available_capabilities(self, node: HarnessNode) -> frozenset[str]:
        if node.target_id is None or not self.target_capabilities:
            return self.capabilities
        return self.target_capabilities.get(node.target_id, frozenset())

    def step(self, signal: str = "always") -> HarnessNode:
        if self.status != RunStatus.RUNNING:
            raise RuntimeError("only a running harness can step")
        if self.current_node_id is None:
            raise RuntimeError("run has no current node")
        node = self.graph.nodes[self.current_node_id]

        required_capabilities = set(node.required_capabilities)
        if node.capability:
            required_capabilities.add(node.capability)
        missing_capabilities = required_capabilities - set(self._available_capabilities(node))
        if missing_capabilities:
            self.status = RunStatus.BLOCKED
            missing = ", ".join(sorted(missing_capabilities))
            self._trace(node.id, "blocked", f"missing capability: {missing}")
            return node

        missing_proofs = set(node.required_proofs) - set(self.proofs)
        if missing_proofs:
            self.status = RunStatus.BLOCKED
            missing = ", ".join(sorted(missing_proofs))
            self._trace(node.id, "blocked", f"missing proof: {missing}")
            return node

        if node.kind == NodeKind.ACTION:
            if node.capability and node.capability not in self._available_capabilities(node):
                self.status = RunStatus.BLOCKED
                self._trace(node.id, "blocked", f"missing capability: {node.capability}")
                return node
            if node.target_id and node.target_id != self.target_id:
                self.status = RunStatus.BLOCKED
                self._trace(node.id, "blocked", f"target mismatch: {node.target_id}")
                return node
            self._trace(node.id, "action.ready", "ready for bridge dispatch")
        elif node.kind == NodeKind.GATE and signal != "pass":
            self.status = RunStatus.BLOCKED
            self._trace(node.id, "blocked", f"gate signal was {signal}")
            return node

        edges = self.graph.next_edges(node.id, signal)
        if not edges:
            self.status = RunStatus.COMPLETED
            self._trace(node.id, "completed", "no further edge")
            return node
        self.current_node_id = edges[0].target
        self._trace(self.current_node_id, "entered", f"via {edges[0].condition}")
        return self.graph.nodes[self.current_node_id]

    def fork(self, checkpoint_name: str, *, new_run_id: str) -> "HarnessRun":
        checkpoint = self.checkpoints.get(checkpoint_name)
        if checkpoint is None:
            raise KeyError(f"unknown checkpoint: {checkpoint_name}")
        branch = HarnessRun(
            id=new_run_id,
            graph=self.graph,
            capabilities=self.capabilities,
            target_capabilities=dict(self.target_capabilities),
            proofs=self.proofs,
            target_id=self.target_id,
            current_node_id=checkpoint.node_id,
            status=RunStatus.READY,
            parent_run_id=self.id,
            branched_from_checkpoint=checkpoint_name,
            trace=list(self.trace[: checkpoint.trace_length]),
            checkpoints=dict(self.checkpoints),
        )
        branch._trace(checkpoint.node_id, "branched", checkpoint_name)
        return branch

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "current_node_id": self.current_node_id,
            "target_id": self.target_id,
            "target_capabilities": {
                target_id: sorted(capabilities)
                for target_id, capabilities in self.target_capabilities.items()
            },
            "proofs": sorted(self.proofs),
            "parent_run_id": self.parent_run_id,
            "branched_from_checkpoint": self.branched_from_checkpoint,
            "trace": [trace.__dict__ for trace in self.trace],
            "checkpoints": {name: checkpoint.__dict__ for name, checkpoint in self.checkpoints.items()},
        }

    def _trace(self, node_id: str, event: str, detail: str) -> None:
        self.trace.append(HarnessTrace(len(self.trace) + 1, node_id, event, self.status.value, detail))
