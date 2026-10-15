"""Das Lagebild eines Agenten: was für ihn gerade klappt und was nicht — vollständig, belegt und mit Alter.

Der Körper misst (Ampel, 44 Funktionen) und meldet die Lampen eines Agenten an den Relay; der Relay gibt sie dem Agenten zurück (`bridge_cli.py lage`,
und als Kurzfassung in jeder Antwort des Praxistests). Fehlt die Meldung oder ist sie alt, sagt das Lagebild genau das: „unbekannt“ ist ein Zustand,
nie ein stilles Grün. Wer etwas nicht selbst beheben kann, teilt es mit (`bridge_cli.py say`).
"""

from __future__ import annotations

ALTER_UNBEKANNT_S = 20.0  # älter als das (der Körper meldet alle 5 s): das Lagebild gilt nicht mehr
MAX_LAMPEN = 90
WORT = {"gruen": "läuft", "gelb": "Achtung", "rot": "kaputt", "grau": "aus"}
GRUPPEN = (("augen", "Augen"), ("haende", "Hände"), ("ziel", "Ziel"))
RANG = {"rot": 0, "gelb": 1, "grau": 2, "gruen": 3}
MITTEILEN = 'Was du nicht selbst beheben kannst, teilst du in deiner Raute mit: bridge_cli.py say "…" (was nicht klappt, seit wann, was du versucht hast).'


def nutzlast(terminal_id: str, lampen: list, gruppe_von) -> dict:
    """Körperseite: die Lampen eines Agenten als schlanke Liste für den Relay. `gruppe_von(kennung)` ordnet sie Augen, Hände oder Ziel zu."""
    return {"terminal_id": terminal_id, "lampen": [{"k": str(l.kennung)[:40], "n": str(l.name)[:90], "f": str(l.farbe), "w": str(l.wort)[:90],
                                                    "b": str(l.behebe)[:30] if l.behebe else "", "g": gruppe_von(l.kennung)} for l in lampen[:MAX_LAMPEN]]}


def gueltig(payload: object) -> bool:
    if not isinstance(payload, dict) or not isinstance(payload.get("terminal_id"), str) or not isinstance(payload.get("lampen"), list):
        return False
    return all(isinstance(l, dict) and l.get("f") in WORT and isinstance(l.get("n"), str) and isinstance(l.get("w"), str) and l.get("g") in dict(GRUPPEN)
               for l in payload["lampen"][:MAX_LAMPEN])


def bewerte(payload: dict | None, alter_s: float | None) -> dict:
    """Relaisseite: aus der letzten Meldung das Lagebild. Ohne Meldung oder bei zu altem Stand ist `bekannt` falsch."""
    if payload is None or alter_s is None:
        return {"bekannt": False, "alter_s": None, "gruppen": {}, "probleme": [], "grund": "Der Körper hat noch nichts über dich gemeldet."}
    if alter_s > ALTER_UNBEKANNT_S:
        return {"bekannt": False, "alter_s": round(alter_s), "gruppen": {}, "probleme": [],
                "grund": f"Die letzte Meldung des Körpers ist {alter_s:.0f} s alt (er meldet alle 5 s): Körper, Verbindung oder Relay prüfen."}
    gruppen, probleme = {}, []
    for g, name in GRUPPEN:
        teile = [l for l in payload["lampen"] if l["g"] == g]
        if not teile:
            gruppen[g] = {"name": name, "zustand": "unbekannt", "wort": "keine Messung"}
            continue
        schlimmste = min(teile, key=lambda l: RANG[l["f"]])
        gruppen[g] = {"name": name, "zustand": WORT[schlimmste["f"]], "wort": schlimmste["w"] if schlimmste["f"] != "gruen" else ""}
    for l in sorted(payload["lampen"], key=lambda l: RANG[l["f"]]):
        if l["f"] in ("rot", "gelb"):
            probleme.append({"funktion": l["n"], "zustand": WORT[l["f"]], "wort": l["w"], "behebe": l["b"] or None})
    return {"bekannt": True, "alter_s": round(alter_s), "gruppen": gruppen, "probleme": probleme, "grund": ""}


def satz(lage: dict) -> str:
    """Ein Satz für den Agenten: erst die drei Gruppen, dann was nicht in Ordnung ist, dann die Pflicht, es mitzuteilen."""
    if not lage["bekannt"]:
        return f"Lage unbekannt. {lage['grund']} {MITTEILEN}"
    kopf = " · ".join(f"{g['name']}: {g['zustand']}" + (f" ({g['wort']})" if g["wort"] else "") for g in lage["gruppen"].values())
    if not lage["probleme"]:
        return f"{kopf}. Alles, was gemessen wird, läuft."
    liste = "; ".join(f"{p['funktion']} — {p['zustand']}: {p['wort']}" for p in lage["probleme"][:6])
    mehr = f" (+{len(lage['probleme']) - 6} weitere)" if len(lage["probleme"]) > 6 else ""
    return f"{kopf}. Nicht in Ordnung: {liste}{mehr}. {MITTEILEN}"


def kurz(lage: dict) -> str:
    """Für jede Antwort: ein kurzer Stand."""
    if not lage["bekannt"]:
        return "Lage unbekannt: " + lage["grund"]
    if not lage["probleme"]:
        return "Lage: alles läuft."
    return f"Lage: {len(lage['probleme'])} Hinweis(e), zuerst: {lage['probleme'][0]['funktion']} — {lage['probleme'][0]['zustand']}: {lage['probleme'][0]['wort']}. Mehr mit `bridge_cli.py lage`."
