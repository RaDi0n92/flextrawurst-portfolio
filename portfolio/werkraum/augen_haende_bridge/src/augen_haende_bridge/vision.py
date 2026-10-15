"""Vision sessions, bounded frame history and recipient-aware visibility."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class SessionState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class FrameSource(str, Enum):
    LIVE_CAPTURE = "live_capture"
    FILE = "file"
    SYNTHETIC = "synthetic"
    REPLAY = "replay"


class FrameVisibility(str, Enum):
    DANIEL = "daniel"
    SHARED_GATE = "shared_gate"
    AGENT = "agent"
    LOCAL_ONLY = "local_only"


@dataclass(frozen=True)
class FrameSnapshot:
    frame_id: str
    timestamp_ms: int
    source: FrameSource
    visibility: FrameVisibility
    payload_ref: str
    owner_agent_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def visible_to(
        self,
        *,
        agent_id: str | None = None,
        daniel: bool = False,
        shared_gate: bool = False,
    ) -> bool:
        if self.visibility == FrameVisibility.DANIEL:
            return daniel
        if self.visibility == FrameVisibility.SHARED_GATE:
            return shared_gate
        if self.visibility == FrameVisibility.AGENT:
            return agent_id is not None and agent_id == self.owner_agent_id
        return False


@dataclass
class VisionSession:
    id: str
    surface_id: str = "surface:windows:bridge"
    target_id: str | None = None
    max_frames: int = 10
    state: SessionState = SessionState.CREATED
    parent_session_id: str | None = None
    branched_from_frame_id: str | None = None
    _frames: deque[FrameSnapshot] = field(default_factory=deque, repr=False)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("session id must not be empty")
        if self.max_frames < 1:
            raise ValueError("max_frames must be positive")
        self._frames = deque(self._frames, maxlen=self.max_frames)

    def start(self) -> None:
        if self.state == SessionState.STOPPED:
            raise RuntimeError("stopped session cannot be restarted")
        self.state = SessionState.RUNNING

    def pause(self) -> None:
        if self.state != SessionState.RUNNING:
            raise RuntimeError("only a running session can be paused")
        self.state = SessionState.PAUSED

    def resume(self) -> None:
        if self.state != SessionState.PAUSED:
            raise RuntimeError("only a paused session can be resumed")
        self.state = SessionState.RUNNING

    def stop(self) -> None:
        if self.state == SessionState.STOPPED:
            return
        self.state = SessionState.STOPPED

    def append_frame(self, frame: FrameSnapshot) -> None:
        if self.state != SessionState.RUNNING:
            raise RuntimeError("frames can only be appended while session is running")
        self._frames.append(frame)

    def frames(self) -> tuple[FrameSnapshot, ...]:
        return tuple(self._frames)

    def frames_for(
        self,
        *,
        agent_id: str | None = None,
        daniel: bool = False,
        shared_gate: bool = False,
    ) -> tuple[FrameSnapshot, ...]:
        return tuple(
            frame
            for frame in self._frames
            if frame.visible_to(agent_id=agent_id, daniel=daniel, shared_gate=shared_gate)
        )

    def scrub(self, frame_id: str, *, new_session_id: str) -> "VisionSession":
        frames = list(self._frames)
        try:
            checkpoint_index = next(index for index, frame in enumerate(frames) if frame.frame_id == frame_id)
        except StopIteration as exc:
            raise KeyError(f"unknown frame checkpoint: {frame_id}") from exc

        branch = VisionSession(
            id=new_session_id,
            surface_id=self.surface_id,
            target_id=self.target_id,
            max_frames=self.max_frames,
            state=SessionState.PAUSED,
            parent_session_id=self.id,
            branched_from_frame_id=frame_id,
            _frames=deque(frames[: checkpoint_index + 1]),
        )
        return branch
