#!/usr/bin/env python3
"""Welche laufenden Dienste wuerden beim Neustart die Datenbank nicht mehr finden?

Am 2026-09-18 um 15:04 wurden die eingebauten DB-Zugangsdaten entfernt
("security: remove Welt API DB credential fallbacks"). Seither faellt
db_runtime.py ohne FLEXTRAWURST_DB_URI auf einen absichtlich unbrauchbaren
Platzhalter zurueck. Ein Dienst, der die Variable nicht gesetzt bekommt, laeuft
nur noch so lange, wie sein Prozess lebt.

Rein lesend. Kein Wert einer Variable wird ausgegeben -- nur, ob sie gesetzt ist.
"""
import re
import subprocess
from datetime import datetime
from pathlib import Path

WELT = Path("/root/werkraum/welt")
UMSCHLAG = datetime(2026, 9, 18, 15, 4)


def laufende_dienste() -> list[str]:
    aus = subprocess.run(["systemctl", "list-units", "--type=service", "--state=running",
                          "--no-legend", "--no-pager", "--plain"],
                         capture_output=True, text=True, timeout=60).stdout
    return [z.split()[0] for z in aus.splitlines() if z.split() and z.split()[0].endswith(".service")]


def zeigt(name: str, feld: str) -> str:
    return subprocess.run(["systemctl", "show", name, "-p", feld, "--value"],
                          capture_output=True, text=True, timeout=30).stdout.strip()


def braucht_db(skript: Path) -> bool:
    """Zieht dieses Skript db_runtime herein -- direkt oder ueber einen Nachbarn?"""
    gesehen, rand = set(), [skript]
    while rand:
        p = rand.pop()
        if p in gesehen or not p.exists():
            continue
        gesehen.add(p)
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(r"\bdb_runtime\b", t):
            return True
        for m in re.findall(r"^\s*(?:from|import)\s+([a-z_][a-z0-9_]*)", t, re.M):
            nachbar = WELT / f"{m}.py"
            if nachbar.exists():
                rand.append(nachbar)
    return False


def main() -> None:
    print(f"{'Dienst':<36} {'gestartet':<12} {'DB_URI gesetzt':<15} Befund")
    print("-" * 92)
    minen, ok, egal = [], 0, 0
    for name in laufende_dienste():
        exec_zeile = zeigt(name, "ExecStart")
        skripte = [Path(s) for s in re.findall(r"(/[^\s;\"]+\.py)", exec_zeile)]
        skripte = [s for s in skripte if s.exists()]
        if not skripte or not any(braucht_db(s) for s in skripte):
            egal += 1
            continue
        umgebung = zeigt(name, "Environment") + " " + zeigt(name, "EnvironmentFiles") + " " + exec_zeile
        gesetzt = "FLEXTRAWURST_DB_URI=" in umgebung
        # Manche Dienste holen sich den Zugang selbst aus einer Ablage und brauchen
        # die Umgebungsvariable gar nicht. Das ist kein Befund, sondern ein anderer Weg.
        eigene_ablage = any(
            "flextrawurst-db.env" in s.read_text(encoding="utf-8", errors="replace")
            for s in skripte)
        if eigene_ablage and not gesetzt:
            print(f"{name:<36} {'':<12} {'eigene Ablage':<15} kein Befund — liest .agent/flextrawurst-db.env")
            ok += 1
            continue
        start_txt = zeigt(name, "ActiveEnterTimestamp")
        try:
            start = datetime.strptime(start_txt.split(" ", 1)[1], "%Y-%m-%d %H:%M:%S %Z")
        except (ValueError, IndexError):
            start = None
        start_s = start.strftime("%m-%d %H:%M") if start else "?"
        if gesetzt:
            befund = "ok"
            ok += 1
        elif start is not None and start < UMSCHLAG:
            befund = "MINE — laeuft aus dem Speicher, Neustart faende die DB nicht"
            minen.append(name)
        else:
            befund = "nach dem Umschlag gestartet, ohne Variable — pruefen"
            minen.append(name)
        print(f"{name:<36} {start_s:<12} {'ja' if gesetzt else 'NEIN':<15} {befund}")
    print("-" * 92)
    print(f"  {ok} in Ordnung · {len(minen)} auffaellig · {egal} ohne DB-Bezug uebersprungen")
    if minen:
        print("  auffaellig: " + ", ".join(minen))


if __name__ == "__main__":
    main()
