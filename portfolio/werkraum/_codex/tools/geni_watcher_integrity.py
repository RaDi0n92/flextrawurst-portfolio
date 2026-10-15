#!/usr/bin/env python3
"""Report-only integrity check for the GENI inbox watcher."""

from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path


TARGET = Path("/root/werkraum_geni/inbox_antworten_watcher.py")
EXPECTED_LINES = 429
EXPECTED_SHA256 = "cd11a721b9ac8ebefa8b46e4fdebb39f24289db12c5331d245c410491276661c"

LOGGER = logging.getLogger("geni-watcher-integrity")


def check_target() -> bool:
    """Check the known-good watcher and report discrepancies without changing it."""
    try:
        content = TARGET.read_bytes()
    except OSError as exc:
        LOGGER.error("ALERT target unreadable: %s (%s)", TARGET, exc)
        return False

    actual_lines = len(content.splitlines())
    actual_sha256 = hashlib.sha256(content).hexdigest()
    problems: list[str] = []

    if actual_lines != EXPECTED_LINES:
        problems.append(f"lines={actual_lines} expected={EXPECTED_LINES}")
    if actual_sha256 != EXPECTED_SHA256:
        problems.append(f"sha256={actual_sha256} expected={EXPECTED_SHA256}")

    if problems:
        LOGGER.error("ALERT watcher integrity mismatch: %s; %s", TARGET, "; ".join(problems))
        return False

    LOGGER.info("PASS watcher integrity: %s; lines=%d; sha256=%s", TARGET, actual_lines, actual_sha256)
    return True


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    return 0 if check_target() else 1


if __name__ == "__main__":
    raise SystemExit(main())
