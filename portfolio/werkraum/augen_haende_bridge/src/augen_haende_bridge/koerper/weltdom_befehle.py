"""Die Befehle der Agenten an den WorldDOM (G11), streng geprüft — vom Starter vor dem Senden und vom Körper beim Empfang (zwei Prüfungen, eine Wahrheit).

`liste` misst und zeigt Knoten; `aktion` handelt an einem Knoten; `zeige` ist eine Zeigegeste (Darstellung oder Einfügung); `anker_neu` und `anker_weg` verwalten bewusst angelegte Knoten.
Handelnde Befehle (`aktion` außer `lesen`, `zeige` mit `einfuegen`) brauchen die Lease des Agenten auf das Ziel (G10).
"""

from __future__ import annotations

HERKUENFTE = ("real", "inferred", "authored", "projected")
AKTIONEN = ("klick", "text_setzen", "lesen")
BEFEHLE = ("liste", "aktion", "zeige", "anker_neu", "anker_weg", "profil_speichern", "profil_laden", "profil_liste", "profil_weg", "markiert")


def _text(v, lang: int, leer: bool = False):
    return v if isinstance(v, str) and (leer or v) and len(v) <= lang and "\x00" not in v else None


def _punkt(v):
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(type(c) is int and -100_000 <= c <= 100_000 for c in v):
        return (v[0], v[1])
    return None


def pruefe_args(befehl: str, args: object, intern: bool = False) -> dict | None:
    """Die bereinigte Fassung der Argumente oder None, wenn etwas fehlt, falsch typisiert ist oder nicht dazugehört. `intern`: der Starter hat den Urheber ergänzt (kommt nie vom Agenten selbst)."""
    if befehl not in BEFEHLE or not isinstance(args, dict):
        return None
    erlaubt = {"liste": {"herkunft", "rolle", "text", "neu_messen"}, "aktion": {"knoten", "aktion", "text", "erwartung"}, "zeige": {"punkt", "modus", "aktion", "text", "empfaenger"},
               "anker_neu": {"name", "punkt", "herkunft"}, "anker_weg": {"knoten"}, "profil_speichern": {"name", "passt_auf", "beschreibung"},
               "profil_laden": {"name", "version"}, "profil_liste": {"passt_auf", "alle"}, "profil_weg": {"name", "aktiv"}, "markiert": {"neu_messen"}}[befehl]
    if intern and befehl in ("zeige", "anker_neu", "profil_speichern", "profil_laden"):
        erlaubt = erlaubt | {"urheber"}
        if "urheber" in args and _text(args["urheber"], 60) is None:
            return None
    if not set(args) <= erlaubt:
        return None
    if befehl == "markiert":
        return dict(args) if type(args.get("neu_messen", True)) is bool else None
    if befehl == "liste":
        if args.get("herkunft") is not None and args["herkunft"] not in HERKUENFTE:
            return None
        if any(k in args and args[k] is not None and _text(args[k], 100) is None for k in ("rolle", "text")):
            return None
        if "neu_messen" in args and type(args["neu_messen"]) is not bool:
            return None
        return dict(args)
    if befehl == "aktion":
        if _text(args.get("knoten"), 120) is None or args.get("aktion") not in AKTIONEN:
            return None
        if "text" in args and args["text"] is not None and _text(args["text"], 500, leer=True) is None:
            return None
        if "erwartung" in args and args["erwartung"] is not None and _text(args["erwartung"], 300, leer=True) is None:
            return None
        if args["aktion"] == "text_setzen" and not isinstance(args.get("text"), str):
            return None
        return dict(args)
    if befehl == "zeige":
        p = _punkt(args.get("punkt"))
        if p is None or args.get("modus") not in ("praesentieren", "einfuegen"):
            return None
        if args.get("aktion", "klick") not in ("klick", "text_setzen"):
            return None
        if "text" in args and args["text"] is not None and _text(args["text"], 500, leer=True) is None:
            return None
        emp = args.get("empfaenger", [])
        if not isinstance(emp, list) or len(emp) > 8 or any(_text(e, 96) is None for e in emp):
            return None
        return {**args, "punkt": list(p), "empfaenger": list(emp)}
    if befehl == "anker_neu":
        if _text(args.get("name"), 200) is None or args.get("herkunft", "authored") not in ("authored", "projected"):
            return None
        if args.get("punkt") is not None and _punkt(args["punkt"]) is None:
            return None
        return {**args, **({"punkt": list(_punkt(args["punkt"]))} if args.get("punkt") is not None else {})}
    if befehl in ("profil_speichern", "profil_laden", "profil_weg"):
        if _text(args.get("name"), 60) is None:
            return None
        if "beschreibung" in args and _text(args["beschreibung"], 300, leer=True) is None:
            return None
        if "version" in args and args["version"] is not None and (type(args["version"]) is not int or not 1 <= args["version"] <= 10_000):
            return None
        if "aktiv" in args and type(args["aktiv"]) is not bool:
            return None
    if befehl in ("profil_speichern", "profil_liste") and "passt_auf" in args:
        pa = args["passt_auf"]
        if not isinstance(pa, dict) or len(pa) > 3 or any(k not in ("programm", "seite", "spiel") or _text(v, 80) is None for k, v in pa.items()):
            return None
    if befehl == "profil_liste" and "alle" in args and type(args["alle"]) is not bool:
        return None
    if befehl.startswith("profil_"):
        return dict(args)
    return dict(args) if _text(args.get("knoten"), 120) is not None else None


def braucht_lease(befehl: str, args: dict) -> bool:
    """Handelnde Befehle brauchen die Lease; Messen, Lesen, Darstellen und das Verwalten eigener Anker nicht."""
    if befehl == "aktion":
        return args.get("aktion") != "lesen"
    if befehl == "zeige":
        return args.get("modus") == "einfuegen"
    return False
