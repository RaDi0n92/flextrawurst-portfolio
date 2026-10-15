#!/usr/bin/env python3
"""Legt das Gerüst eines neuen Skills an: Ordner, SKILL.md aus der Vorlage, references/, scripts/ — und mit --mit-szenario ein Szenario für die Praxis-Harness.

Aufruf:  python3 skill_geruest.py NAME [--titel="Lesbarer Titel"] [--mit-szenario] [--ziel=ORDNER] [--szenario-ordner=ORDNER]
Es wird nie etwas überschrieben: gibt es den Skill oder das Szenario schon, bricht das Skript ab und sagt, was da ist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
VORLAGEN = HIER.parent / "references"
SKILLS_ORDNER = HIER.parent.parent  # der Ordner, in dem dieser Skill liegt
SZENARIO_ORDNER = SKILLS_ORDNER.parent / "src" / "augen_haende_bridge" / "praxis"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def optionen(argv: list[str]) -> tuple[list[str], dict]:
    woerter, opt = [], {}
    for a in argv:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            opt[k] = v if _ else True
        else:
            woerter.append(a)
    return woerter, opt


def erzeugen(name: str, titel: str, ziel: Path, mit_szenario: bool, szenario_ordner: Path) -> list[str]:
    if not NAME.fullmatch(name):
        raise SystemExit("Der Name darf nur kleine Buchstaben, Ziffern und Bindestriche enthalten (höchstens 40, nicht mit Bindestrich beginnen).")
    skill = ziel / name
    if skill.exists():
        raise SystemExit(f"Es gibt schon einen Ordner {skill}. Ich überschreibe nichts — nimm einen anderen Namen oder bearbeite den vorhandenen Skill.")
    szenario = szenario_ordner / f"szenario_{name}.json"
    if mit_szenario and szenario.exists():
        raise SystemExit(f"Es gibt schon ein Szenario {szenario}. Ich überschreibe nichts.")
    angelegt = []
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir()
    text = (VORLAGEN / "vorlage-skill.md.txt").read_text(encoding="utf-8").replace("@NAME@", name).replace("@TITEL@", titel)
    if mit_szenario:
        text = text.replace("## So fängst du an\n", f"## So fängst du an\n`bridge_cli.py test start <Partner> --szenario={name}` — danach führt `test karte` durch jeden Schritt.\n\n", 1)
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    angelegt += [str(skill / "SKILL.md"), str(skill / "references"), str(skill / "scripts")]
    if mit_szenario:
        szenario_ordner.mkdir(parents=True, exist_ok=True)
        szenario.write_text((VORLAGEN / "vorlage-szenario.json.txt").read_text(encoding="utf-8").replace("@NAME@", name).replace("@TITEL@", titel), encoding="utf-8")
        angelegt.append(str(szenario))
    return angelegt


def main(argv: list[str]) -> int:
    woerter, opt = optionen(argv)
    if len(woerter) != 1 or not set(opt) <= {"titel", "mit-szenario", "ziel", "szenario-ordner"}:
        print(__doc__)
        return 2
    name = woerter[0]
    angelegt = erzeugen(name, str(opt.get("titel") or name.replace("-", " ").capitalize()), Path(opt.get("ziel") or SKILLS_ORDNER), bool(opt.get("mit-szenario")), Path(opt.get("szenario-ordner") or SZENARIO_ORDNER))
    print("Angelegt:")
    for a in angelegt:
        print("  " + a)
    print("Nächster Schritt: die @…@-Stellen in SKILL.md ausfüllen, dann skill_pruefen.py laufen lassen.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
