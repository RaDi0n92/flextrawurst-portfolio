#!/usr/bin/env python3
"""
Prueft laufende systemd-Units gegen eine gespeicherte Baseline ihrer ExecStart-Flags.

Entstanden aus einer Archiv-Notiz vom 07./08.07.2026 (Cache-Ram-Regressionskrise) und
geborgen am 13.08.2026 -- siehe docs/systemdoku/12_ollama_gemma4.md, Nachtrag 2026-08-13,
und docs/systemdoku/53_geborgene_konzepte_aus_vor_reset_archiv.md.

Verwendung:
    python3 config_waechter.py check              -- vergleicht Live-Config gegen Baseline
    python3 config_waechter.py update              -- schreibt Live-Config als neue Baseline
    python3 config_waechter.py update --nur EINHEIT -- Baseline nur fuer eine Unit aktualisieren
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASELINE_PATH = Path(__file__).parent / "config_waechter_baseline.json"

TRACKED_UNITS = [
    "llama-hauhaucs.service",
    "llama-hauhaucs-hintergrund.service",
]

ARGV_RE = re.compile(r"argv\[\]=(.*?) ; ignore_errors=")


def live_execstart(unit: str) -> str:
    out = subprocess.check_output(
        ["systemctl", "show", unit, "-p", "ExecStart", "--value"],
        text=True,
    ).strip()
    match = ARGV_RE.search(out)
    if not match:
        raise RuntimeError(f"{unit}: konnte argv[] nicht aus ExecStart lesen -- Unit inaktiv oder unbekannt?")
    return match.group(1)


def parse_flags(argv: str) -> dict:
    tokens = argv.split()
    flags: dict[str, str | bool] = {}
    i = 1  # Token 0 ist der Programmpfad selbst
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("--"):
            hat_wert = i + 1 < len(tokens) and not tokens[i + 1].startswith("--")
            if hat_wert:
                flags[tok] = tokens[i + 1]
                i += 2
            else:
                flags[tok] = True
                i += 1
        else:
            i += 1
    return flags


def load_baseline() -> dict:
    if not BASELINE_PATH.exists():
        return {}
    return json.loads(BASELINE_PATH.read_text())


def save_baseline(baseline: dict) -> None:
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n")


def cmd_check(_args) -> int:
    baseline = load_baseline()
    if not baseline:
        print(f"Keine Baseline unter {BASELINE_PATH} -- erst 'update' ausfuehren.")
        return 1

    gesamt_abweichungen = 0
    for unit in TRACKED_UNITS:
        if unit not in baseline:
            print(f"[{unit}] keine Baseline hinterlegt -- 'update --nur {unit}' ausfuehren.")
            gesamt_abweichungen += 1
            continue
        try:
            live = parse_flags(live_execstart(unit))
        except RuntimeError as e:
            print(f"[{unit}] {e}")
            gesamt_abweichungen += 1
            continue

        erwartet = baseline[unit]["flags"]
        abweichungen = []
        for flag, wert in erwartet.items():
            if flag not in live:
                abweichungen.append(f"  {flag}: erwartet {wert!r}, fehlt jetzt komplett")
            elif str(live[flag]) != str(wert):
                abweichungen.append(f"  {flag}: erwartet {wert!r}, live {live[flag]!r}")
        for flag in live:
            if flag not in erwartet:
                abweichungen.append(f"  {flag}: neu, nicht in Baseline (live {live[flag]!r})")

        if abweichungen:
            print(f"[{unit}] {len(abweichungen)} Abweichung(en) von der Baseline vom {baseline[unit]['aktualisiert']}:")
            print("\n".join(abweichungen))
            gesamt_abweichungen += len(abweichungen)
        else:
            print(f"[{unit}] unveraendert seit {baseline[unit]['aktualisiert']}.")

    if gesamt_abweichungen:
        print(f"\n{gesamt_abweichungen} Abweichung(en) insgesamt. "
              f"Wenn die Aenderung beabsichtigt war: 'update' ausfuehren, um sie als neue Baseline zu uebernehmen.")
        return 1
    print("\nAlles unveraendert.")
    return 0


def cmd_update(args) -> int:
    baseline = load_baseline()
    ziel_units = [args.nur] if args.nur else TRACKED_UNITS
    jetzt = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for unit in ziel_units:
        if unit not in TRACKED_UNITS:
            print(f"[{unit}] nicht in TRACKED_UNITS -- ueberspringe (erst im Skript eintragen).")
            continue
        try:
            live = parse_flags(live_execstart(unit))
        except RuntimeError as e:
            print(f"[{unit}] {e} -- ueberspringe.")
            continue

        alt = baseline.get(unit, {}).get("flags")
        if alt is not None and alt != live:
            geaendert = {k for k in set(alt) | set(live) if alt.get(k) != live.get(k)}
            print(f"[{unit}] Baseline aktualisiert -- geaendert: {', '.join(sorted(geaendert))}")
        else:
            print(f"[{unit}] Baseline {'neu gesetzt' if alt is None else 'unveraendert'}.")

        baseline[unit] = {"aktualisiert": jetzt, "flags": live}

    save_baseline(baseline)
    print(f"Geschrieben nach {BASELINE_PATH}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Live-Config gegen Baseline vergleichen")

    p_update = sub.add_parser("update", help="Live-Config als neue Baseline uebernehmen")
    p_update.add_argument("--nur", metavar="EINHEIT", help="nur diese eine Unit aktualisieren")

    args = parser.parse_args()
    if args.cmd == "check":
        return cmd_check(args)
    return cmd_update(args)


if __name__ == "__main__":
    sys.exit(main())
