"""Der Einstiegspunkt des Körpers auf Linux (KDE 1 und KDE 2): dieselbe Verdrahtung wie unter Windows, mit der Linux-Fensterschicht und dem X11-Adapter.

Aufruf: `python3 -m augen_haende_bridge.koerper.haupt_linux --ort kde1` (das Skript `client_vps/koerper_linux_starten.sh` setzt alles). Umgebung:
`BRIDGE_URL` (Vorgabe ws://127.0.0.1:19880), `BRIDGE_TOKEN` oder `BRIDGE_TOKEN_DATEI` (Vorgabe runtime/tokens/desktop-<ort>.token), `BRIDGE_ORT`.
Der Ort benennt den Arbeitsplatz im Relay (`desktops.json`); ein unbekannter Ort wird vom Relay abgewiesen.
"""

from __future__ import annotations

import os
import sys

os.environ["BRIDGE_BACKEND"] = "linux"  # muss vor dem Import der Körper-Module stehen (plattform.py liest es einmal)

import socket  # noqa: E402
from pathlib import Path  # noqa: E402

ORTE = {"kde1": "KDE 1", "kde2": "KDE 2"}
STANDARD_URL = "ws://127.0.0.1:19880"


def _repo() -> Path:
    return Path(__file__).resolve().parents[3]


def token_datei(ort: str) -> Path:
    return Path(os.environ.get("BRIDGE_TOKEN_DATEI") or _repo() / "runtime" / "tokens" / f"desktop-{ort}.token")


def plattform_linux(ort: str):
    from augen_haende_bridge.windows_capture import WindowsScreenCapture
    from augen_haende_bridge.windows_scanner import WindowsWindowScanner

    from . import anzeigeort, linux_adapter as la, x11_helfer
    from .einstellungen import standard_pfad
    from .haupt import Plattform
    from .mikrofon import eingabegeraete

    api = la.LinuxWindowApi()
    capture_api = la.LinuxCaptureApi()
    name = ORTE.get(ort, ort)
    return Plattform(
        name="linux", ort=ort, pruefen=lambda: None, hook_bauen=lambda not_aus: la.LinuxNotAusHook(not_aus), quelle=la.LinuxQuelle(api),
        capture_api=capture_api, datei_waehlen=la.datei_waehlen, einstellungen_pfad=standard_pfad(ort), haende_senden=la.xtest_senden,
        scanner=WindowsWindowScanner(api, host=socket.gethostname(), ort=ort, desktop_label=f"{name} kompletter Desktop", quelle="x11"),
        capture=WindowsScreenCapture(capture_api, ort=ort),
        ziel_faehigkeit=anzeigeort.faehigkeit_fensteraufnahme if capture_api.fensterbild_moeglich else anzeigeort.faehigkeit_standard,
        mik_geraete=lambda: eingabegeraete(), anzeigename=name, fenster_bild=capture_api.capture_window if capture_api.fensterbild_moeglich else None,
        fenster_vor=x11_helfer.fenster_nach_vorn, piepen=x11_helfer.piepen)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ort = os.environ.get("BRIDGE_ORT", "")
    if "--ort" in argv:
        ort = argv[argv.index("--ort") + 1]
    from .haupt import VERSION, _log

    if "--version" in argv:
        print(f"AugenUndHaendeBridge {VERSION} (Linux)")
        return 0
    if ort not in ORTE:
        print(f"Unbekannter Ort {ort!r}: erlaubt sind {', '.join(sorted(ORTE))} (--ort oder BRIDGE_ORT)", file=sys.stderr)
        return 2
    url = os.environ.get("BRIDGE_URL", STANDARD_URL)
    datei = token_datei(ort)
    if "--selbsttest" in argv:
        from . import selbsttest_linux

        return selbsttest_linux.lauf(VERSION, ort, url, None if os.environ.get("BRIDGE_TOKEN") else datei, still="--still" in argv)
    if not os.environ.get("BRIDGE_TOKEN"):
        try:
            os.environ["BRIDGE_TOKEN"] = datei.read_text(encoding="utf-8").strip()
        except OSError as fehler:
            print(f"Zugangsdaten nicht lesbar ({datei}): {fehler}", file=sys.stderr)
            return 3
    os.environ["BRIDGE_URL"] = url
    try:
        from .haupt import _lauf

        return _lauf(plattform_linux(ort))
    except Exception:
        import traceback

        _log("Abbruch:\n" + traceback.format_exc())
        print("Die Bridge ist abgebrochen; Einzelheiten stehen im Log.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
