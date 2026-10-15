"""Bounded predicates over recorded commands; never infer visible effects from input ACKs."""

from __future__ import annotations

FELDER = frozenset({"command", "befehl", "action_kind", "taste", "kombi", "ok", "reason", "status",
                    "resource_id", "unveraendert", "daniel_freigabe", "partner_in_queue", "loop_id",
                    "loop_grund", "loop_laeufe", "loop_budget", "lease_id", "empfaenger", "capture_fresh"})


def validiere(checks: object) -> None:
    if not isinstance(checks, list) or not 1 <= len(checks) <= 30:
        raise ValueError("belege_fehlen")
    ids = set()
    for c in checks:
        if not isinstance(c, dict) or not {"id", "role", "match"} <= set(c) or set(c) - {"id", "role", "match", "same_resource_as"}:
            raise ValueError("beleg_felder")
        if not isinstance(c["id"], str) or not c["id"] or c["id"] in ids or c["role"] not in ("handelnder", "zuschauer"):
            raise ValueError("beleg_identitaet")
        if not isinstance(c["match"], dict) or not c["match"] or not set(c["match"]) <= FELDER:
            raise ValueError("beleg_praedikat")
        for v in c["match"].values():
            values = v if isinstance(v, list) else [v]
            if not values or any(type(x) not in (str, int, bool) for x in values):
                raise ValueError("beleg_wert")
        if "same_resource_as" in c and (not isinstance(c["same_resource_as"], str) or c["same_resource_as"] not in ids):
            raise ValueError("beleg_vorgaenger")
        ids.add(c["id"])


def pruefe(checks: list[dict], events: list[dict], *, run_id: str, attempt_id: str,
           step: int, actors: dict[str, str], targets: dict[str, str | None], since_ms: int) -> dict:
    """An ordered subsequence of distinct events for this attempt, actor and bound target.

    Clock is the starter clock. A command started before the action phase cannot be
    retroactively admitted merely because its response arrived after the announcement.
    """
    validiere(checks)
    eligible = []
    for e in events:
        d = e.get("daten", {})
        p = d.get("praxis", {})
        # The proof belongs to one attempt, but the physical action may be
        # recorded while the runner is in the action, sight, or observer node.
        # Do not hard-code ``handeln`` here: ``see`` happens after ``getan``
        # advances the graph to ``sehen``.
        if (p.get("run_id"), p.get("attempt_id"), p.get("step")) != (run_id, attempt_id, step):
            continue
        if p.get("phase") not in ("handeln", "sehen", "zuschauer"):
            continue
        if type(p.get("started_ms")) is not int or p["started_ms"] < since_ms:
            continue
        tid = e.get("agent")
        if d.get("command") in ("haende", "weltdom", "see") and (not targets.get(tid) or p.get("target_id") != targets[tid]):
            continue
        eligible.append(e)
    found, missing, cursor, used = {}, [], 0, set()
    for c in checks:
        selected = None
        for i in range(cursor, len(eligible)):
            e, d = eligible[i], eligible[i].get("daten", {})
            if not e.get("id") or e["id"] in used:
                continue
            if e.get("agent") != actors[c["role"]]:
                continue
            if any(not any(type(d.get(k)) is type(v) and d.get(k) == v for v in (want if isinstance(want, list) else [want])) for k, want in c["match"].items()):
                continue
            previous = found.get(c.get("same_resource_as"))
            if "same_resource_as" in c and (not previous or not d.get("resource_id") or d["resource_id"] != previous["resource_id"]):
                continue
            selected = {"event_id": e["id"], "resource_id": d.get("resource_id")}
            used.add(e["id"])
            cursor = i + 1
            break
        if selected is None:
            missing.append(c["id"])
            # Later predicates must not leap over a missing predecessor.
            break
        found[c["id"]] = selected
    return {"ok": not missing, "missing": missing, "matched": found,
            "effect_verification": "AGENT_OBSERVATION_REQUIRED"}
