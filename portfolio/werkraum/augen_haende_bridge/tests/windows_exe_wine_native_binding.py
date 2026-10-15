"""Run the packaged scan -> read-only binding path under Wine.

Wine proves only the packaged Windows API path. The native Windows boundary
remains explicitly UNKNOWN.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "dist" / "AugenUndHaendeBridge" / "AugenUndHaendeBridge.exe"
WINE_PREFIX = Path(os.environ.get("WINEPREFIX", "/tmp/augen-haende-winbuild.ieRV30/wine"))
MARKER = "binding-readback"


def window_tree() -> str:
    result = subprocess.run(
        ["xwininfo", "-root", "-tree"],
        env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":1")},
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def main() -> None:
    wine = shutil.which("wine")
    xwininfo = shutil.which("xwininfo")
    if wine is None or xwininfo is None:
        raise RuntimeError("wine_and_xwininfo_required")
    if not EXE.is_file() or not WINE_PREFIX.is_dir():
        raise RuntimeError("packaged_exe_or_wine_prefix_missing")
    with tempfile.TemporaryDirectory(prefix="bridge-g11-") as temp:
        log_path = Path(temp) / "wine.log"
        with log_path.open("wb") as log:
            env = {
                **os.environ,
                "DISPLAY": os.environ.get("DISPLAY", ":1"),
                "WINEPREFIX": str(WINE_PREFIX),
                "WINEARCH": "win64",
                "WINEDEBUG": "-all",
                "BRIDGE_NATIVE_SCAN_ON_START": "1",
                "BRIDGE_NATIVE_BIND_TARGET_ID": "windows:desktop",
            }
            process = subprocess.Popen([wine, str(EXE)], env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                observed = ""
                for _ in range(160):
                    observed = window_tree()
                    if MARKER in observed:
                        print({
                            "status": "PASS",
                            "scope": "packaged Windows scan -> observe-only binding under Wine",
                            "native_windows": "UNKNOWN",
                            "marker": next(line.strip() for line in observed.splitlines() if MARKER in line),
                        })
                        return
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
                output = log_path.read_text(errors="replace")[-4000:]
                raise RuntimeError(f"native_binding_marker_timeout output={output!r}")
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()


if __name__ == "__main__":
    main()
