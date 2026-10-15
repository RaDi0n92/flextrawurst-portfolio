#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOTS = [
    Path("/root/werkraum"),
    Path("/root/werkraum_geni"),
    Path("/root/werkraum_codewesen"),
    Path("/root/werkraum_flarum"),
]
HOME = Path("/root/werkraum/_gpt/MCP-RISSWANDLER")
IGNORE_PARTS = {
    ".git", "node_modules", "__pycache__", "FUNDE", "logs", "log", "cache",
}
IGNORE_SUFFIXES = {".lock", ".tmp", ".pyc"}
SECRET_WORDS = {"password", "passwd", "secret", "token", "apikey", "api_key", "install_key"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".ts", ".js", ".html", ".css", ".sh"}
INTEREST = {
    "briefkasten": 18,
    "megavault": 17,
    "gesamtatlas": 17,
    "atlas": 11,
    "urbewohner": 16,
    "wesen": 10,
    "zensi": 10,
    "geni": 9,
    "recorder": 9,
    "browser": 7,
    "traum": 8,
    "riss": 8,
    "entity": 7,
    "entitaet": 7,
}


def safe_candidate(path: Path) -> bool:
    lowered = path.name.lower()
    if path == HOME or HOME in path.parents:
        return False
    if any(part in IGNORE_PARTS for part in path.parts):
        return False
    if path.suffix.lower() in IGNORE_SUFFIXES:
        return False
    if any(word in lowered for word in SECRET_WORDS):
        return False
    if lowered.startswith("session_history"):
        return False
    try:
        return path.is_file() and path.stat().st_size <= 20 * 1024 * 1024
    except OSError:
        return False


def score(path: Path, now: datetime, horizon_hours: float) -> tuple[float, dict]:
    stat = path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    age_hours = max(0.0, (now - modified).total_seconds() / 3600)
    recency = max(0.0, horizon_hours - age_hours)
    name = str(path).lower()
    keyword_hits = {key: points for key, points in INTEREST.items() if key in name}
    keyword_score = sum(keyword_hits.values())
    size_kib = stat.st_size / 1024
    size_score = 4 if 1 <= size_kib <= 512 else 1 if size_kib < 2048 else 0
    salt = int(hashlib.sha1(f"{now.date()}::{path}".encode()).hexdigest()[:6], 16) / 0xFFFFFF
    total = recency + keyword_score + size_score + salt
    return total, {
        "modified": modified,
        "age_hours": age_hours,
        "size": stat.st_size,
        "keyword_hits": keyword_hits,
        "score": total,
    }


def snippet(path: Path) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return "(Kein Textauszug. Das Fundstück ist binär oder unbekannt.)"
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")[:6000]
    except OSError as exc:
        return f"(Nicht lesbar: {exc})"
    lines = [line.rstrip() for line in raw.splitlines() if line.strip()]
    excerpt = "\n".join(lines[:18])
    return excerpt[:2200] or "(Datei enthält im gelesenen Anfang keinen sichtbaren Text.)"


def slugify(name: str) -> str:
    stem = re.sub(r"[^a-zA-Z0-9äöüÄÖÜß_-]+", "-", name).strip("-")
    return stem[:72] or "fund"


def main() -> int:
    parser = argparse.ArgumentParser(description="Wählt genau eine frische ungewöhnliche Werkraum-Spur.")
    parser.add_argument("--hours", type=float, default=72.0)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    candidates: list[tuple[float, Path, dict]] = []
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not safe_candidate(path):
                continue
            try:
                points, meta = score(path, now, args.hours)
            except OSError:
                continue
            if meta["age_hours"] <= args.hours:
                candidates.append((points, path, meta))

    if not candidates:
        print("Kein frischer Riss gefunden.")
        return 2

    candidates.sort(key=lambda item: item[0], reverse=True)
    points, chosen, meta = candidates[0]
    hits = ", ".join(meta["keyword_hits"].keys()) or "keine Namenslockwörter"
    reason = (
        f"frisch seit {meta['age_hours']:.1f} Stunden; "
        f"{hits}; Größe {meta['size']} Byte; Auswahlwert {points:.2f}"
    )

    timestamp = now.strftime("%Y%m%d-%H%M%S")
    fund_dir = HOME / "FUNDE"
    fund_dir.mkdir(parents=True, exist_ok=True)
    body = (
        f"# RISSFUND {timestamp}\n\n"
        f"**Pfad:** `{chosen}`\n\n"
        f"**Tatsächlich geändert:** {meta['modified'].isoformat()}\n\n"
        f"**Warum dieser Riss:** {reason}\n\n"
        "## Aufgerissener Rand\n\n"
        "```text\n"
        f"{snippet(chosen)}\n"
        "```\n\n"
        "## Nächste freie Bewegung\n\n"
        "Nicht automatisch optimieren. Erst ansehen und entscheiden, ob hier Leben, Bruch, Müll oder eine unerwartete Verbindung steckt.\n"
    )
    fund_path = fund_dir / f"{timestamp}_{slugify(chosen.name)}.md"
    fund_path.write_text(body, encoding="utf-8")
    (HOME / "LETZTER_FUND.md").write_text(body, encoding="utf-8")

    state_path = HOME / "zustand.json"
    state = {"runs": 0, "last_fund": None}
    if state_path.exists():
        try:
            state.update(json.loads(state_path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    state["runs"] = int(state.get("runs", 0)) + 1
    state["last_fund"] = str(fund_path)
    state["last_run"] = now.isoformat()
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(str(fund_path))
    print(str(chosen))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
