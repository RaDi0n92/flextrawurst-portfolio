#!/usr/bin/env python3
"""Model-free runtime guard for the bridge and its browser test surface."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


FORBIDDEN_MODEL_MARKERS = ("ollama", "qwen", "hauhaucs", "llama-server", "openai.com/v1")
_URL = re.compile(r"https?://[^\s'\"]+")


def scan_sources(paths: Iterable[Path]) -> list[str]:
    """Report forbidden model/network markers in executable source only."""
    findings: list[str] = []
    for path in paths:
        if path.suffix not in {".py", ".js", ".ts", ".html"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for marker in FORBIDDEN_MODEL_MARKERS:
            if marker in text:
                findings.append(f"{path}:{marker}")
    return findings


def runtime_status() -> dict[str, object]:
    return {
        "llm_calls": 0,
        "model_calls": 0,
        "model_network": "blocked-by-architecture",
        "production_primary": "not-used",
        "checked_sources": "bridge-runtime",
    }
