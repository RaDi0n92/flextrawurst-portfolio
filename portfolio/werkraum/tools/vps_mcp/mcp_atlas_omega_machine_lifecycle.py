from __future__ import annotations

import datetime as dt
import hashlib
import json
import socket
import subprocess
from pathlib import Path
from typing import Any

from mcp_atlas_omega_api import gate as omega_gate

WORLD_MODEL = "VERIFIED_FULL_BASELINE_PLUS_VISIBLE_LIVE_DELTA"
MAX_SYSTEMCTL_OUTPUT_BYTES = 65536
MAX_SECTION_JSON_BYTES = 262144
ALLOWED_UNIT_FIELDS = ("Id", "LoadState", "UnitFileState", "ActiveState", "SubState", "MainPID", "ActiveEnterTimestamp", "NextElapseUSecMonotonic")
SECTIONS = (
    "status", "manifest", "truth_ring", "journey", "capsules", "projects",
    "relationships", "versions", "original_references", "gaps", "runtime",
    "lifecycle", "preflight",
)
VPS_MCP_ROOT = Path("/root/werkraum/tools/vps_mcp")
PRODUCT_FILES = {
    "core": VPS_MCP_ROOT / "mcp_atlas_omega.py",
    "api": VPS_MCP_ROOT / "mcp_atlas_omega_api.py",
    "lean": VPS_MCP_ROOT / "mcp_atlas_omega_lean.py",
    "publisher": VPS_MCP_ROOT / "publish_omega_lean_binding.py",
    "server": VPS_MCP_ROOT / "vps_mcp_server.py",
}
UNITS = (
    "vps-mcp.service", "gesamtatlas-world.service",
    "mcp-gesamtatlas-light.timer", "mcp-gesamtatlas-full.timer",
)

class MachineLifecycleError(RuntimeError):
    pass

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def _file_ref(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise MachineLifecycleError(f"Gebundene Produktdatei fehlt oder ist Symlink: {path}")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}

def _port_open(port: int) -> bool:
    sock = socket.socket()
    sock.settimeout(0.35)
    try:
        return sock.connect_ex(("127.0.0.1", port)) == 0
    finally:
        sock.close()

def _unit_state(unit: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["systemctl", "show", unit, "-p", "Id", "-p", "LoadState", "-p", "UnitFileState",
         "-p", "ActiveState", "-p", "SubState", "-p", "MainPID", "-p", "ActiveEnterTimestamp",
         "-p", "NextElapseUSecMonotonic", "--no-pager"],
        capture_output=True, text=True, timeout=15, check=False,
    )
    stdout_bytes = len(proc.stdout.encode("utf-8"))
    stderr_bytes = len(proc.stderr.encode("utf-8"))
    if stdout_bytes > MAX_SYSTEMCTL_OUTPUT_BYTES or stderr_bytes > MAX_SYSTEMCTL_OUTPUT_BYTES:
        raise MachineLifecycleError("systemctl output budget exceeded")
    values: dict[str, Any] = {"returncode": proc.returncode}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if key in ALLOWED_UNIT_FIELDS:
                values[key] = value
    values["output_budget"] = {"limit_bytes": MAX_SYSTEMCTL_OUTPUT_BYTES, "stdout_bytes": stdout_bytes, "stderr_bytes": stderr_bytes}
    return values

def _contract() -> dict[str, Any]:
    value = omega_gate()
    if not isinstance(value, dict) or value.get("ok") is not True:
        raise MachineLifecycleError("Omega-Gate konnte nicht dynamisch aufgelöst werden")
    if value.get("world_model") != WORLD_MODEL:
        raise MachineLifecycleError("Unerwartetes Weltmodell")
    baseline = value.get("verified_full_baseline") or {}
    pointer = value.get("verified_full_baseline_pointer") or {}
    live = value.get("current_live_state") or {}
    if not baseline.get("all_verification_checks_pass") or int(baseline.get("verification_check_count") or 0) < 1:
        raise MachineLifecycleError("Verifizierter Grundstand besitzt keine vollständige dynamische PASS-Prüfung")
    if pointer.get("baseline_id") != baseline.get("baseline_id") or pointer.get("revision") != baseline.get("revision"):
        raise MachineLifecycleError("Pointer und Grundstand widersprechen sich")
    if live.get("baseline_id") != baseline.get("baseline_id") or live.get("baseline_revision") != baseline.get("revision"):
        raise MachineLifecycleError("Live-Nachlauf bindet nicht an den Grundstand")
    return value

def _essentials(value: dict[str, Any]) -> dict[str, Any]:
    pointer = value["verified_full_baseline_pointer"]
    baseline = value["verified_full_baseline"]
    live = value["current_live_state"]
    return {
        "world_model": value["world_model"],
        "baseline_id": baseline["baseline_id"],
        "baseline_revision": baseline["revision"],
        "live_delta_id": live["live_delta_id"],
        "live_revision": live["revision"],
        "revision_distance_from_baseline": live["revision_distance_from_baseline"],
        "current_live_revision_fully_verified": live["current_live_revision_fully_verified"],
        "requires_new_full_verification": live["requires_new_full_verification"],
        "pointer": {k: pointer.get(k) for k in ("path", "bytes", "sha256", "pointer_class")},
        "baseline": {k: baseline.get(k) for k in ("path", "bytes", "sha256", "verification_check_count", "all_verification_checks_pass")},
        "full_refresh": dict(baseline["full_refresh"]),
        "full_verification": dict(baseline["full_verification"]),
        "live_delta": dict(value["live_delta"]),
        "mcp_world_ready": bool(value.get("mcp_world_ready")),
        "final_scan_ready": bool(value.get("final_scan_ready")),
        "read_only": True,
        "production_mutation_performed": False,
    }

def _runtime() -> dict[str, Any]:
    return {
        "sampled_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "units": {unit: _unit_state(unit) for unit in UNITS},
        "ports": {"8091": _port_open(8091), "18108": _port_open(18108)},
        "read_only": True,
        "production_mutation_performed": False,
        "einschraenkung": "Beobachtung über systemctl show und lokale TCP-Verbindung; keine Dienst- oder Timeränderung.",
    }

def section(args: dict[str, Any] | None = None) -> dict[str, Any]:
    args = args or {}
    requested = str(args.get("section") or "status")
    if requested not in SECTIONS:
        raise MachineLifecycleError(f"Unbekannter Maschinenabschnitt: {requested}")
    contract = _contract()
    core = _essentials(contract)
    common = {
        "ok": True, "section": requested, "schema_version": "1.0",
        "contract_id": "omega.machine_lifecycle.v1", "read_only": True,
        "production_mutation_performed": False,
    }
    if requested == "status":
        payload = {**common, **core, "child_easy_explanation": contract.get("child_easy_explanation")}
    elif requested == "manifest":
        payload = {**common, **core, "available_sections": list(SECTIONS),
                   "source_manifest": dict(contract["source_manifest"]),
                   "product_files": {name: _file_ref(path) for name, path in PRODUCT_FILES.items()},
                   "candidate_module": _file_ref(Path(__file__).resolve())}
    elif requested == "truth_ring":
        payload = {**common, **core, "readiness_semantics": dict(contract["readiness_semantics"]),
                   "ready_markers": dict(contract["ready_markers"])}
    elif requested == "journey":
        payload = {**common, **core, "stations": [
            {"position": index, "section": name, "tool": "atlas_omega_machine"}
            for index, name in enumerate(SECTIONS, 1)
        ]}
    elif requested == "capsules":
        material = {k: core[k] for k in ("baseline_id", "baseline_revision", "live_delta_id", "live_revision", "requires_new_full_verification", "current_live_revision_fully_verified", "mcp_world_ready", "final_scan_ready")}
        if material["current_live_revision_fully_verified"]:
            human_summary = "Grundstand und aktueller sichtbarer Stand wurden gemeinsam vollständig geprüft."
            child_summary = "Das kontrollierte Buch und der aktuelle Zettelstand sind gemeinsam vollständig kontrolliert."
        else:
            human_summary = "Geprüfter Grundstand plus sichtbar neuer, noch nicht vollverifizierter Nachlauf."
            child_summary = "Das kontrollierte Buch bleibt; neue Zettel brauchen noch den großen Kontrollgang."
        payload = {**common, "human": {**material, "summary": human_summary},
                   "child": {**material, "summary": child_summary},
                   "machine": {**material, "schema": "omega.machine.capsule.v1"}}
    elif requested == "projects":
        payload = {**common, **core, "projects": [
            {"id": "gesamtatlas-omega", "datenstand": "BESTAETIGT", "pointer": core["pointer"]},
            {"id": "omega-machine-lifecycle", "datenstand": "READ_ONLY_RUNTIME_VIEW", "module": _file_ref(Path(__file__).resolve())},
        ]}
    elif requested == "relationships":
        payload = {**common, **core, "relationships": [
            {"from": core["pointer"]["path"], "to": core["baseline"]["path"], "kind": "POINTS_TO"},
            {"from": core["baseline_id"], "to": core["live_delta_id"], "kind": "BASELINE_PLUS_VISIBLE_DELTA"},
            {"from": core["baseline"]["path"], "to": core["full_verification"]["path"], "kind": "PROVEN_BY"},
        ]}
    elif requested == "versions":
        payload = {**common, **core, "versions": [
            {"id": core["baseline_id"], "revision": core["baseline_revision"], "kind": "VERIFIED_FULL_BASELINE"},
            {"id": core["live_delta_id"], "revision": core["live_revision"], "kind": "VISIBLE_LIVE_DELTA"},
        ]}
    elif requested == "original_references":
        payload = {**common, **core, "references": [core["pointer"], core["baseline"], core["full_refresh"], core["full_verification"], core["live_delta"]]}
    elif requested == "gaps":
        gaps = []
        if core["requires_new_full_verification"]:
            gaps.append({"id": "LIVE_NOT_FULLY_REVERIFIED", "status": "OPEN_VISIBLE_BOUNDARY"})
        if not core["mcp_world_ready"]:
            gaps.append({"id": "MCP_WORLD_READY_ABSENT", "status": "CLOSED_GATE"})
        if not core["final_scan_ready"]:
            gaps.append({"id": "FINAL_SCAN_READY_ABSENT", "status": "CLOSED_GATE"})
        payload = {**common, **core, "gaps": gaps}
    elif requested == "runtime":
        payload = {**common, **core, "runtime": _runtime()}
    elif requested == "lifecycle":
        payload = {**common, **core, "lifecycle": {
            "verified_baseline_preserved": True,
            "visible_delta_active": bool(contract["readiness_semantics"].get("live_delta_mechanism_active")),
            "light_state_may_not_replace_baseline": True,
            "new_full_verification_recommended": bool(contract["readiness_semantics"].get("new_full_verification_recommended")),
            "timers": _runtime()["units"],
        }}
    else:
        runtime = _runtime()
        payload = {**common, **core, "preflight": {
            "captured_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "product_files": {name: _file_ref(path) for name, path in PRODUCT_FILES.items()},
            "candidate_module": _file_ref(Path(__file__).resolve()),
            "runtime": runtime,
            "authorized_activation_restart_count": 1,
            "activation_executed": False,
            "rollback_required_before_activation": True,
            "rollback_restart_is_conditional_on_failed_postconditions": True,
        }}
    payload["einschraenkung"] = "Dynamische read-only Maschinenansicht. Keine Aktivierung, kein Restart, kein Timer-Eingriff und kein Ready-Marker."
    measured = len(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    if measured > MAX_SECTION_JSON_BYTES:
        raise MachineLifecycleError(f"section output budget exceeded: {measured}")
    payload["output_budget"] = {"limit_bytes": MAX_SECTION_JSON_BYTES, "measured_payload_bytes_before_budget_field": measured}
    return payload
