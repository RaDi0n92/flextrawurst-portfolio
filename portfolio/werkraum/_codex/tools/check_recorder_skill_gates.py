#!/usr/bin/env python3
"""Deterministic contract/evidence gate for Browser Recorder work.

The gate deliberately knows nothing about whether a claim is true on screen.
It only enforces that the required skill contracts exist and that a human-readable
evidence report explicitly records PASS for every marker of the selected stage.
Missing evidence is a failure, never an implicit pass.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CODEX_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = CODEX_ROOT / "skills" / "registry.json"
MARKER_RE = re.compile(r"^\s*-\s*(REC-[A-Z0-9-]+)\s*:\s*PASS\b", re.MULTILINE)


class GateFailure(RuntimeError):
    pass


def load_registry(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateFailure(f"registry unreadable: {path}: {exc}") from exc
    if data.get("version") != 1:
        raise GateFailure("registry version must be 1")
    if not isinstance(data.get("markers"), list) or not data["markers"]:
        raise GateFailure("registry has no markers")
    if not isinstance(data.get("stages"), dict) or not data["stages"]:
        raise GateFailure("registry has no stages")
    return data


def validate_contracts(registry: dict, registry_path: Path) -> dict[str, str]:
    marker_to_skill: dict[str, str] = {}
    seen_skills: set[str] = set()
    skills_root = registry_path.parent
    for entry in registry["markers"]:
        marker = entry.get("id")
        skill = entry.get("skill")
        if not isinstance(marker, str) or not re.fullmatch(r"REC-[A-Z0-9-]+", marker):
            raise GateFailure(f"invalid marker id: {marker!r}")
        if marker in marker_to_skill:
            raise GateFailure(f"duplicate marker: {marker}")
        if not isinstance(skill, str) or not re.fullmatch(r"[a-z0-9-]+", skill):
            raise GateFailure(f"invalid skill name for {marker}: {skill!r}")
        if skill in seen_skills:
            raise GateFailure(f"a skill is assigned to more than one marker: {skill}")
        seen_skills.add(skill)
        skill_file = skills_root / skill / "SKILL.md"
        if not skill_file.is_file():
            raise GateFailure(f"missing SKILL.md for {marker}: {skill_file}")
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = re.search(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not frontmatter:
            raise GateFailure(f"missing frontmatter: {skill_file}")
        if not re.search(rf"^name:\s*{re.escape(skill)}\s*$", frontmatter.group(1), re.MULTILINE):
            raise GateFailure(f"frontmatter name mismatch for {skill_file}")
        description = re.search(r"^description:\s*(.+)$", frontmatter.group(1), re.MULTILINE)
        if not description or not description.group(1).strip() or "TODO" in description.group(1):
            raise GateFailure(f"missing usable description: {skill_file}")
        if not re.search(rf"Marker:\s*`{re.escape(marker)}`", text):
            raise GateFailure(f"marker {marker} missing from {skill_file}")
        marker_to_skill[marker] = skill

    known = set(marker_to_skill)
    for stage, markers in registry["stages"].items():
        if not isinstance(markers, list) or not markers:
            raise GateFailure(f"stage {stage} has no required markers")
        unknown = sorted(set(markers) - known)
        if unknown:
            raise GateFailure(f"stage {stage} references unknown markers: {', '.join(unknown)}")
    return marker_to_skill


def evidence_markers(text: str) -> set[str]:
    return set(MARKER_RE.findall(text))


def run_contracts(registry_path: Path) -> dict:
    registry = load_registry(registry_path)
    marker_to_skill = validate_contracts(registry, registry_path)
    return {"ok": True, "mode": "contracts", "markers": len(marker_to_skill), "skills": len(marker_to_skill)}


def run_evidence(registry_path: Path, stage: str, evidence_path: Path) -> dict:
    registry = load_registry(registry_path)
    marker_to_skill = validate_contracts(registry, registry_path)
    if stage not in registry["stages"]:
        raise GateFailure(f"unknown stage: {stage}")
    if not evidence_path.is_file():
        raise GateFailure(f"evidence report missing: {evidence_path}")
    text = evidence_path.read_text(encoding="utf-8")
    if not re.search(r"^EVIDENCE_VERSION:\s*1\s*$", text, re.MULTILINE):
        raise GateFailure("evidence report must contain EVIDENCE_VERSION: 1")
    required = list(registry["stages"][stage])
    passed = evidence_markers(text)
    missing = [marker for marker in required if marker not in passed]
    if missing:
        names = ", ".join(f"{marker} ({marker_to_skill[marker]})" for marker in missing)
        raise GateFailure(f"missing explicit PASS evidence for: {names}")
    if not re.search(r"^OUTCOME:\s*PASS\s*$", text, re.MULTILINE):
        raise GateFailure("evidence report must contain OUTCOME: PASS")
    return {"ok": True, "mode": "evidence", "stage": stage, "evidence": str(evidence_path), "markers": required}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("contracts", "evidence"))
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--stage")
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "contracts":
            result = run_contracts(args.registry)
        else:
            if not args.stage or not args.evidence:
                raise GateFailure("evidence mode requires --stage and --evidence")
            result = run_evidence(args.registry, args.stage, args.evidence)
    except GateFailure as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
