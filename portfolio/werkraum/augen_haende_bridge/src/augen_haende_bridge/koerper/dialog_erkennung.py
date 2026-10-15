"""Wartet der Agent auf einen Dialog seines eigenen Programms? Die Bridge sieht ihn nur im Terminalbild: hier wird er erkannt.

Berechtigungs-, Vertrauens- und Ja/Nein-Dialoge (Claude Code, Opencode, Codex, Gemini …) blockieren den Agenten, und nichts in der Bridge zeigt es: Lampen
bleiben blau, während Agenten aufeinander warten. Die Erkennung liest die letzten Bildschirmzeilen des Terminals und sucht bekannte Wortlaute. Sie rät nicht:
ein Treffer braucht mindestens eine Antwortzeile des Dialogs UND dessen Fragezeile; bekannt sind nur die Muster unten (bei einem neuen Wortlaut kommt
ein Muster dazu). Eine Erkennung ist ein Hinweis an Daniel und den Agenten, nie eine Handlung: beantwortet wird der Dialog von Daniel.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

LETZTE_ZEILEN = 24  # nur das Ende des Bildschirms: Dialoge stehen unten, alter Text darüber ist kein Dialog


@dataclass(frozen=True)
class Dialog:
    art: str  # berechtigung | vertrauen | ja_nein
    frage: str  # die Fragezeile, wie sie im Terminal steht (gekürzt)
    antworten: tuple[str, ...]  # die erkannten Antwortzeilen


# (art, Muster der Fragezeile, Muster der Antwortzeilen, Frage und Antwort dürfen dieselbe Zeile sein);
# beide müssen im Endstück des Bildschirms vorkommen
MUSTER = (
    ("vertrauen", re.compile(r"trust (this|the) folder|do you trust|Security guide", re.I), re.compile(r"Yes, I trust|No, exit", re.I), False),
    ("berechtigung", re.compile(r"permission|allow|erlaub", re.I), re.compile(r"Allow once|Allow always|Reject|Always allow|Deny", re.I), False),
    ("ja_nein", re.compile(r"\(y/n\)|\[y/N\]|\[Y/n\]|Do you want to|Möchtest du|Proceed\?", re.I), re.compile(r"\bYes\b|\bNo\b|\(y/n\)|\[y/N\]|\[Y/n\]|Ja\b|Nein\b", re.I), True),
)


# Eine Antwortzeile mit mindestens zwei dieser Wahlmöglichkeiten nebeneinander ist ein Berechtigungsdialog, auch ohne Fragezeile (Opencode zeigt nur den Pfad
# und darunter „Allow once · Allow always · Reject“); ein einzelnes Wort in Fließtext genügt nicht.
WAHL = re.compile(r"Allow once|Allow always|Reject|Always allow|Deny", re.I)


def _wahlzeile(ende: list[str]) -> Dialog | None:
    for i in range(len(ende) - 1, -1, -1):
        if len({w.lower() for w in WAHL.findall(ende[i])}) >= 2:
            pfad = next((z for z in reversed(ende[:i]) if z.lstrip("- ").startswith(("/", "~", "./"))), "")
            return Dialog("berechtigung", ("Zugriff auf " + pfad.lstrip("- ").strip()) if pfad else "Berechtigung", (ende[i][:80],))
    return None


def erkenne(zeilen: list[str]) -> Dialog | None:
    """`zeilen`: die sichtbaren Bildschirmzeilen des Terminals (oben zuerst). Gibt den Dialog zurück, auf den der Agent wartet, sonst None."""
    ende = [z.strip() for z in zeilen[-LETZTE_ZEILEN:] if z.strip()]
    if not ende:
        return None
    for art, frage_muster, antwort_muster, gleiche_zeile in MUSTER:
        antworten = tuple(z[:80] for z in ende if antwort_muster.search(z))
        if not antworten:
            continue
        fragen = [z for z in ende if frage_muster.search(z) and (gleiche_zeile or z not in antworten)]
        if fragen:
            return Dialog(art, fragen[-1][:100], antworten[:4])
    return _wahlzeile(ende)
