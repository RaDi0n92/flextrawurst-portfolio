from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
import threading
import time
from typing import Any

_RUNTIME_PATH = Path("/run/flextrawurst-vps-mcp-delivery-graph.json")
_SCHEMA = 1
_LOCK = threading.RLock()

STATE_INTAKE = "INTAKE"
STATE_WORKING = "WORKING"
STATE_RESULT_READY = "RESULT_READY"
STATE_DIRECT = "DIRECT_DELIVERY"
STATE_CONVERSATIONAL = "CONVERSATIONAL_DELIVERY"
STATE_EXPLAIN = "EXPLANATION_DELIVERY"
STATE_EVIDENCE = "EVIDENCE_DELIVERY"
STATE_REPAIR = "REPAIR_TO_DELIVERY"
STATE_DONE = "DONE"

INTENT_DIRECT = "DIRECT_TASK"
INTENT_CONVERSATIONAL = "COCREATE"
INTENT_EXPLAIN = "EXPLAIN"
INTENT_EVIDENCE = "EVIDENCE"
INTENT_UNKNOWN = "UNKNOWN"

_PROOF_RE = re.compile(
    r"\b(beweis|belege?|nachweis|hash|sha-?256|audit|prüf(?:e|ung|protokoll)|"
    r"verifizier|evidence|prove|proof|show me.*checked)\b",
    re.IGNORECASE,
)
_EXPLAIN_RE = re.compile(
    r"\b(warum|wieso|weshalb|erklär|erklaer|wie genau|herleitung|"
    r"reasoning summary|explain|why|how does)\b",
    re.IGNORECASE,
)
_CONVERSE_RE = re.compile(
    r"\b(stell dir|vision|was meinst du|geh auf|denk.*mit|überleg.*mit|"
    r"gemeinsam|zusammen überlegen|brainstorm|rollenspiel|roleplay)\b",
    re.IGNORECASE,
)

_META_PATTERNS = {
    "proof_dump": re.compile(r"\b(sha-?256|hash(?:es)?|prüfprotokoll|beweiskette|verification chain)\b", re.I),
    "process_narration": re.compile(r"\b(ich habe (?:zuerst|dann|danach|geprüft|verifiziert)|mein vorgehen|schritt \d+)\b", re.I),
    "status_wall": re.compile(r"\b(status|zwischenstand|ergebnis der prüfung|durchgeführt|erfolgreich geprüft)\b", re.I),
    "redundant_confirmation": re.compile(r"\b(wirklich erfolgreich|definitiv korrekt|noch einmal bestätigt|erneut bestätigt)\b", re.I),
}


@dataclass(frozen=True)
class DeliveryDecision:
    state: str
    intent: str
    reason: str
    next_node: str
    response_parts: tuple[str, ...]
    evidence_requested: bool
    explain_requested: bool
    conversational: bool
    repair_signals: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["response_parts"] = list(self.response_parts)
        data["repair_signals"] = list(self.repair_signals)
        data["edges"] = graph_edges()
        return data


def _session_key(session_id: str | None) -> str:
    raw = str(session_id or "default")
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in "._-")[:100]
    return safe or "default"


def _empty_store() -> dict[str, Any]:
    return {"schema": _SCHEMA, "sessions": {}}


def _load() -> dict[str, Any]:
    try:
        data = json.loads(_RUNTIME_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("schema") == _SCHEMA:
            return data
    except Exception:
        pass
    return _empty_store()


def _save(data: dict[str, Any]) -> None:
    try:
        tmp = _RUNTIME_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(_RUNTIME_PATH)
    except Exception:
        pass


def graph_edges() -> list[dict[str, str]]:
    return [
        {"from": STATE_INTAKE, "to": STATE_WORKING, "on": "task requires work"},
        {"from": STATE_WORKING, "to": STATE_RESULT_READY, "on": "usable result exists"},
        {"from": STATE_RESULT_READY, "to": STATE_DIRECT, "on": "ordinary task / result requested"},
        {"from": STATE_RESULT_READY, "to": STATE_CONVERSATIONAL, "on": "co-creation / vision / dialogue requested"},
        {"from": STATE_RESULT_READY, "to": STATE_EXPLAIN, "on": "user explicitly asks why/how/explanation"},
        {"from": STATE_RESULT_READY, "to": STATE_EVIDENCE, "on": "user explicitly asks proof/audit/evidence"},
        {"from": STATE_DIRECT, "to": STATE_REPAIR, "on": "draft contains unrequested process/proof/status sediment"},
        {"from": STATE_CONVERSATIONAL, "to": STATE_REPAIR, "on": "draft drifts into unrequested process/proof/status sediment"},
        {"from": STATE_EXPLAIN, "to": STATE_REPAIR, "on": "explanation becomes process theatre instead of useful reasoning"},
        {"from": STATE_REPAIR, "to": STATE_DIRECT, "on": "retain result; remove unrequested sediment"},
        {"from": STATE_DIRECT, "to": STATE_DONE, "on": "deliver"},
        {"from": STATE_CONVERSATIONAL, "to": STATE_DONE, "on": "deliver"},
        {"from": STATE_EXPLAIN, "to": STATE_DONE, "on": "deliver"},
        {"from": STATE_EVIDENCE, "to": STATE_DONE, "on": "deliver requested evidence"},
    ]


def _classify(user_request: str) -> tuple[str, bool, bool, bool]:
    text = str(user_request or "")
    evidence = bool(_PROOF_RE.search(text))
    explain = bool(_EXPLAIN_RE.search(text))
    conversational = bool(_CONVERSE_RE.search(text))

    if evidence:
        return INTENT_EVIDENCE, evidence, explain, conversational
    if conversational:
        return INTENT_CONVERSATIONAL, evidence, explain, conversational
    if explain:
        return INTENT_EXPLAIN, evidence, explain, conversational
    if text.strip():
        return INTENT_DIRECT, evidence, explain, conversational
    return INTENT_UNKNOWN, evidence, explain, conversational


def _draft_signals(draft: str, evidence_requested: bool) -> list[str]:
    text = str(draft or "")
    if not text.strip():
        return []
    signals: list[str] = []
    for name, pattern in _META_PATTERNS.items():
        if pattern.search(text):
            if name == "proof_dump" and evidence_requested:
                continue
            signals.append(name)
    return signals


def route(
    user_request: str,
    *,
    task_status: str = "result_ready",
    draft: str = "",
    session_id: str | None = None,
) -> dict[str, Any]:
    intent, evidence, explain, conversational = _classify(user_request)
    status = str(task_status or "result_ready").strip().lower()
    signals = _draft_signals(draft, evidence)

    if status in {"working", "in_progress", "running"}:
        decision = DeliveryDecision(
            state=STATE_WORKING,
            intent=intent,
            reason="Die Arbeit ist noch nicht lieferfertig; im Arbeitsknoten bleiben.",
            next_node="CONTINUE_WORK",
            response_parts=("only_material_progress_if_user_needs_it",),
            evidence_requested=evidence,
            explain_requested=explain,
            conversational=conversational,
        )
    elif signals and not evidence:
        decision = DeliveryDecision(
            state=STATE_REPAIR,
            intent=intent,
            reason="Der Entwurf enthaelt nicht angeforderten Prozess-/Beweis-/Statusballast; zur nutzbaren Lieferung zurueckrouten.",
            next_node="COMPRESS_TO_RESULT",
            response_parts=("requested_result", "material_caveat_only"),
            evidence_requested=evidence,
            explain_requested=explain,
            conversational=conversational,
            repair_signals=tuple(signals),
        )
    elif intent == INTENT_EVIDENCE:
        decision = DeliveryDecision(
            state=STATE_EVIDENCE,
            intent=intent,
            reason="Der Nutzer hat Beleg/Pruefung/Audit selbst angefordert.",
            next_node="DELIVER_WITH_EVIDENCE",
            response_parts=("answer", "requested_evidence", "material_limitations"),
            evidence_requested=True,
            explain_requested=explain,
            conversational=conversational,
        )
    elif intent == INTENT_CONVERSATIONAL:
        decision = DeliveryDecision(
            state=STATE_CONVERSATIONAL,
            intent=intent,
            reason="Der Nutzer will gemeinsames Denken/Weiterentwickeln statt Status- oder Beweisprotokoll.",
            next_node="CONTINUE_IDEA",
            response_parts=("direct_reaction", "useful_reasoning", "next_idea"),
            evidence_requested=False,
            explain_requested=explain,
            conversational=True,
        )
    elif intent == INTENT_EXPLAIN:
        decision = DeliveryDecision(
            state=STATE_EXPLAIN,
            intent=intent,
            reason="Der Nutzer hat eine Erklaerung/Herleitung angefordert.",
            next_node="EXPLAIN_USEFULLY",
            response_parts=("answer", "reasoning_summary", "relevant_details"),
            evidence_requested=False,
            explain_requested=True,
            conversational=conversational,
        )
    else:
        decision = DeliveryDecision(
            state=STATE_DIRECT,
            intent=intent,
            reason="Ein nutzbares Ergebnis ist fertig; Standardkante fuehrt direkt zur Lieferung.",
            next_node="DELIVER_RESULT",
            response_parts=("requested_result", "material_caveat_only"),
            evidence_requested=False,
            explain_requested=False,
            conversational=False,
        )

    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        sessions = store.setdefault("sessions", {})
        sessions[key] = {
            "state": decision.state,
            "intent": decision.intent,
            "next_node": decision.next_node,
            "reason": decision.reason,
            "repair_signals": list(decision.repair_signals),
            "updated_at": time.time(),
        }
        _save(store)
    return decision.to_dict()


def review(
    user_request: str,
    draft: str,
    *,
    session_id: str | None = None,
) -> dict[str, Any]:
    return route(
        user_request,
        task_status="result_ready",
        draft=draft,
        session_id=session_id,
    )


def snapshot(session_id: str | None = None) -> dict[str, Any]:
    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        runtime = (store.get("sessions") or {}).get(key)
    return {
        "active": True,
        "purpose": "Positive delivery routing: useful result first; explanation/evidence only on a fitting edge.",
        "states": [
            STATE_INTAKE,
            STATE_WORKING,
            STATE_RESULT_READY,
            STATE_DIRECT,
            STATE_CONVERSATIONAL,
            STATE_EXPLAIN,
            STATE_EVIDENCE,
            STATE_REPAIR,
            STATE_DONE,
        ],
        "edges": graph_edges(),
        "runtime": runtime,
        "default_result_edge": f"{STATE_RESULT_READY} -> {STATE_DIRECT}",
    }


def server_instruction() -> str:
    return (
        " Delivery-Graph: Wenn ein nutzbares Ergebnis vorliegt, fuehrt die Standardkante RESULT_READY "
        "zu DIRECT_DELIVERY. CONVERSATIONAL_DELIVERY ist fuer gemeinsames Denken/Vision, "
        "EXPLANATION_DELIVERY fuer ausdrueckliche Warum/Wie-Fragen und EVIDENCE_DELIVERY fuer "
        "ausdruecklich verlangte Belege/Audits. Nicht angeforderter Prozess-, Status- oder Beweisballast "
        "wird ueber REPAIR_TO_DELIVERY zur nutzbaren Lieferung zurueckgeroutet. "
        "harness.output_route und harness.output_review machen diese Kante explizit."
    )
