#!/usr/bin/env python3
"""Prüft einen Skill-Ordner und sagt freundlich und genau, was zu tun ist.

Aufruf:  python3 skill_pruefen.py ORDNER [--cli=PFAD_ZU_bridge_cli.py] [--szenario-ordner=ORDNER]
Ausgabe: je Befund eine Zeile „Fehler“ (muss behoben werden) oder „Hinweis“ (lohnt sich). Endet mit Code 0, wenn kein Fehler vorliegt, sonst 1.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parent.parent.parent
STANDARD_CLI = REPO / "client_vps" / "bridge_cli.py"
SZENARIO_ORDNER = REPO / "src" / "augen_haende_bridge" / "praxis"
DROHWOERTER = ("MUSS", "NIEMALS", "UNBEDINGT", "VERBOTEN", "ACHTUNG", "SOFORT")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def kopf(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M)) if m else None


def bekannte_befehle(cli: Path) -> set[str]:
    """Die ersten Wörter hinter „bridge_cli.py“ in der Hilfe des Werkzeugs."""
    try:
        spec = importlib.util.spec_from_file_location("bridge_cli_pruef", cli)
        modul = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(cli.parent.parent / "src"))
        spec.loader.exec_module(modul)
        return set(re.findall(r"^\s*bridge_cli\.py (\w[\w-]*)", modul.__doc__ or "", re.M)) | {"hilfe"}
    except Exception:
        return set()


LESBAR_GRENZE = 110  # Daniels Regel: Absätze etwa 100 Zeichen; Tabellen, Code, Verweise mit Adresse und Kopf sind ausgenommen


def lange_zeilen(text: str) -> list[int]:
    """Nummern der Zeilen, die als Fließtext zu lang sind (ohne Kopf, Tabellen und Codeblöcke)."""
    ergebnis, im_code, kopf_ende = [], False, 0
    zeilen = text.splitlines()
    if zeilen and zeilen[0] == "---":
        kopf_ende = next((i for i in range(1, len(zeilen)) if zeilen[i] == "---"), 0) + 1
    for nr, z in enumerate(zeilen, 1):
        if nr <= kopf_ende:
            continue
        if z.lstrip().startswith("```"):
            im_code = not im_code
        elif not im_code and not z.startswith("|") and "http" not in z and len(z) > LESBAR_GRENZE:
            ergebnis.append(nr)
    return ergebnis


def pruefen(ordner: Path, cli: Path = STANDARD_CLI, szenario_ordner: Path = SZENARIO_ORDNER) -> list[tuple[str, str]]:
    befunde: list[tuple[str, str]] = []
    f = lambda t: befunde.append(("Fehler", t))
    h = lambda t: befunde.append(("Hinweis", t))
    datei = ordner / "SKILL.md"
    if not datei.is_file():
        f(f"In {ordner} fehlt die Datei SKILL.md — ohne sie ist es noch kein Skill.")
        return befunde
    text = datei.read_text(encoding="utf-8")
    k = kopf(text)
    if k is None:
        f("Der Kopf fehlt: SKILL.md beginnt mit „---“, dann name und description, dann „---“.")
        return befunde
    name, beschr = k.get("name", ""), k.get("description", "")
    if not name:
        f("Im Kopf fehlt name.")
    elif name != ordner.name:
        f(f"name („{name}“) und Ordnername („{ordner.name}“) sollten gleich sein, sonst findet man den Skill nicht.")
    elif not NAME.fullmatch(name):
        f("name: nur kleine Buchstaben, Ziffern, Bindestriche (höchstens 40).")
    if not beschr:
        f("Im Kopf fehlt description — sie ist der Auslöser des Skills.")
    else:
        if len(beschr) > 1024:
            f(f"description ist {len(beschr)} Zeichen lang; erlaubt sind 1024. Sag dort nur, *wann* der Skill passt, nicht, wie er funktioniert.")
        if re.match(r"^(ich|du|wir|ihr)\b", beschr.strip(), re.I):
            h("description in dritter Person schreiben („Führt …“, „Zeigt …“), nicht in Ich- oder Du-Form.")
        if not re.search(r"(?<!nicht )verwenden|use when|\bwenn\b", beschr.lower()):  # „Nicht verwenden“ ist ein Gegenfall, kein Auslöser
            h("description sollte Auslöser nennen („Verwenden, wenn …“), damit der Agent den Skill im richtigen Moment findet.")
        if not re.search(r"nicht verwenden|don'?t use|nicht für", beschr, re.I):
            h("description sollte auch sagen, wann der Skill *nicht* passt (Gegenfälle) — das verhindert Fehlgriffe.")
        if "@" in beschr:
            f("In der description stehen noch @…@-Platzhalter aus der Vorlage.")
    if "@" in text.split("---", 2)[-1] and re.search(r"@[^@\n]+@", text.split("---", 2)[-1]):
        f("Im Text stehen noch @…@-Platzhalter aus der Vorlage; fülle sie aus oder streiche sie.")
    zeilen = len(text.splitlines())
    if zeilen >= 500:
        f(f"SKILL.md hat {zeilen} Zeilen; unter 500 bleiben. Schwere Inhalte gehören in references/.")
    texte = [("SKILL.md", text)] + ([(f"references/{r.name}", r.read_text(encoding="utf-8")) for r in sorted((ordner / "references").glob("*.md"))] if (ordner / "references").is_dir() else [])
    for name_, t_ in texte:
        lang = lange_zeilen(t_)
        if lang:
            h(f"{name_}: {len(lang)} Zeilen sind länger als {LESBAR_GRENZE} Zeichen (zuerst Zeile {lang[0]}). Kürzere Absätze lesen sich besser.")
    for wort in DROHWOERTER:
        if re.search(rf"\b{wort}\b", text):
            h(f"„{wort}“ in Großbuchstaben wirkt drohend. Erklär lieber den Grund (das Warum).")
    if not re.search(r"warum", text, re.I):
        h("Ein Abschnitt „Warum das so ist“ hilft dem Agenten, auch unvorhergesehene Fälle richtig zu lösen.")
    if not re.search(r"fertig|ende|erledigt|exit|belege?|beleg", text, re.I):
        h("Sag, woran man „fertig“ erkennt, und dass jeder Schritt etwas zeigt, das man ansehen kann (Beleg).")
    for ref in sorted(set(re.findall(r"`(references/[^`\s]+)`", text) + re.findall(r"`(scripts/[^`\s]+)`", text))):
        if not (ordner / ref).exists():
            f(f"Verwiesen wird auf {ref}, die Datei gibt es nicht.")
        if ref.count("/") > 1:
            h(f"{ref} liegt tiefer als eine Ebene; flache Ordner werden verlässlicher gefunden.")
    refs = ordner / "references"
    if refs.is_dir():
        for r in sorted(list(refs.glob("*.md")) + list(refs.glob("*.txt"))):
            rl = r.read_text(encoding="utf-8").splitlines()
            if len(rl) > 300 and not any("inhalt" in z.lower() for z in rl[:20]):
                h(f"{r.name} hat {len(rl)} Zeilen; ein Inhaltsverzeichnis am Anfang hilft beim gezielten Lesen.")
            if f"references/{r.name}" not in text:
                h(f"references/{r.name} wird in SKILL.md nicht erwähnt; der Agent öffnet sie nur, wenn der Text sagt, wann.")
    cmds = bekannte_befehle(cli) if cli.is_file() else set()
    if cmds:
        for snippet in re.findall(r"`([^`\n]*(?:bridge_cli\.py|bridge\.sh)[^`\n]*)`", text):
            m = re.search(r"(?:bridge_cli\.py|bridge\.sh)\s+(\w[\w-]*)", snippet)
            if m and m.group(1) not in cmds:
                f(f"Der Befehl „{m.group(1)}“ in `{snippet.strip()[:60]}` steht nicht in der Hilfe von bridge_cli.py — gibt es ihn (noch) nicht?")
    sz = szenario_ordner / f"szenario_{name}.json"
    if sz.is_file():
        try:
            from augen_haende_bridge.praxis.lauf import PraxisFehler, lade_szenario

            lade_szenario(sz)
        except ImportError:
            sys.path.insert(0, str(REPO / "src"))
            from augen_haende_bridge.praxis.lauf import PraxisFehler, lade_szenario

            try:
                lade_szenario(sz)
            except PraxisFehler as e:
                f(f"Das Szenario {sz.name} ist ungültig: {e}.")
        except PraxisFehler as e:
            f(f"Das Szenario {sz.name} ist ungültig: {e}.")
        if f"--szenario={name}" not in text:
            h(f"Es gibt ein Szenario {sz.name}; nenne in SKILL.md den Start: `bridge_cli.py test start <Partner> --szenario={name}`.")
    return befunde


def main(argv: list[str]) -> int:
    opt = {a[2:].partition("=")[0]: a[2:].partition("=")[2] for a in argv if a.startswith("--")}
    pos = [a for a in argv if not a.startswith("--")]
    if len(pos) != 1:
        print(__doc__)
        return 2
    befunde = pruefen(Path(pos[0]).resolve(), Path(opt.get("cli") or STANDARD_CLI), Path(opt.get("szenario-ordner") or SZENARIO_ORDNER))
    for art, text in befunde:
        print(f"{art}: {text}")
    fehler = sum(1 for a, _ in befunde if a == "Fehler")
    print(f"\n{fehler} Fehler, {len(befunde) - fehler} Hinweise." + (" Schön, nichts im Weg." if not befunde else (" Fast geschafft." if not fehler else " Mit diesen Änderungen steht der Skill.")))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
