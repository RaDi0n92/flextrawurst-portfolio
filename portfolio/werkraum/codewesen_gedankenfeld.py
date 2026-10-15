#!/usr/bin/env python3
"""
Gedankenfeld — der mitgetragene Zustand eines Wesens (Track 7, 2026-08-03).

Daniels Spezifikation, woertlich:

    "ich will dass sich gedanken schnell aendern aber nur da wo sie wollen und
     den rest behalten und mittragen ueber alle zeit bis sie es selbst entfernen"

Und auf die Frage, ob "Durchdenken" heisst, dass der Modellzustand ueberlebt
oder dass ein Gedanke ueber Tage weitergeht: "beides!?!?"

## Warum das nicht der bestehende Denk-Log ist

entity_thinking_log (78068 Ticks) und entity_denkstream (7,4 Mio Chunks) halten
fest, was gedacht WURDE. Sie sind ein Protokoll: append-only, vollstaendig,
unveraenderlich -- und nichts davon wird in den naechsten Takt mitgenommen.

Das Gedankenfeld ist das Gegenstueck: ein ZUSTAND, der von Takt zu Takt und von
Tag zu Tag weitergetragen wird. Beide bleiben nebeneinander bestehen, keiner
ersetzt den anderen.

## Die drei Eigenschaften aus Daniels Satz, als Code

1. "schnell aendern ... nur da wo sie wollen"
   -> Aenderung ist punktgenau: ein einzelner Gedanke wird ersetzt, alles
      andere bleibt unberuehrt. Kein Neuschreiben des ganzen Feldes.
2. "den rest behalten und mittragen ueber alle zeit"
   -> KEIN systemseitiges Vergessen. Kein Budget das etwas verdraengt, keine
      Altersgrenze, kein Rausschieben durch Neueres. Das ist der bewusste
      Unterschied zu container.json/memory.json, wo 11111 Zeichen abweisen.
3. "bis sie es selbst entfernen"
   -> Nur das Wesen entfernt. Es gibt keinen automatischen Loeschpfad. Daniel
      kann eingreifen, aber das ist dann sichtbar sein Eingriff, nicht das
      System.

## Speicherform

gedankenfeld.jsonl, append-only Revisionen. Der aktuelle Stand entsteht durch
Abspielen, nicht durch Ueberschreiben. Damit ist jede Aenderung nachvollziehbar
("was dachte es am 12. anders als heute") und nichts geht je verloren -- auch
ein vom Wesen entfernter Gedanke bleibt in der Historie, nur nicht mehr im
Zustand. Gleiches Prinzip wie die Redaktionen im Chatverlauf (Track 3) und im
Geist von Grundgesetz 5.

## Die ehrliche Kehrseite

Ohne systemseitiges Vergessen kann das Feld wachsen, und Kontextlaenge kostet
Antwortzeit linear (gemessen: 57,29 tok/s Prompt-Durchsatz, jeder Prompt wird
bei diesem Hybrid-Modell komplett neu gerechnet). Die Antwort darauf ist nicht,
heimlich doch zu loeschen, sondern das Wachstum sichtbar zu machen: die
Tokenkosten des Feldes stehen in der Kontextanzeige, und das Wesen selbst
bekommt sie zu sehen. Verdichten darf nur, wer es auch verantwortet.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

BASIS = Path("/root/werkraum/codewesen")

OP_NEU = "neu"
OP_AENDERN = "aendern"
OP_ENTFERNEN = "entfernen"

# Marker, die ein Wesen in seine Antwort schreiben kann. Einzeilig gehalten --
# der mehrzeilige ##SCHREIBEN##-Marker hat gezeigt, dass Modelle das Ende
# vergessen.
GEDANKE_NEU_PAT      = re.compile(r'##GEDANKE\+\s*(.+?)##')
GEDANKE_AENDERN_PAT  = re.compile(r'##GEDANKE~\s*([0-9a-f]{6,12})\s*\|\s*(.+?)##')
GEDANKE_ENTFERNEN_PAT = re.compile(r'##GEDANKE-\s*([0-9a-f]{6,12})\s*##')


def _jetzt() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _datei(name: str) -> Path:
    return BASIS / name / "gedankenfeld.jsonl"


def _anhaengen(name: str, satz: dict) -> None:
    pfad = _datei(name)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "a", encoding="utf-8") as f:
        f.write(json.dumps(satz, ensure_ascii=False) + "\n")


def lade_revisionen(name: str) -> list[dict]:
    pfad = _datei(name)
    if not pfad.exists():
        return []
    revisionen = []
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile:
            continue
        try:
            revisionen.append(json.loads(zeile))
        except Exception:
            continue
    return revisionen


def lade_feld(name: str) -> list[dict]:
    """Der aktuelle Zustand, durch Abspielen der Revisionen. Reihenfolge:
    aeltester zuerst -- ein Gedanke, den das Wesen seit Wochen mittraegt, steht
    oben und wird nicht von Neuem verdraengt."""
    zustand: dict[str, dict] = {}
    for rev in lade_revisionen(name):
        gid, op = rev.get("id"), rev.get("op")
        if not gid:
            continue
        if op == OP_NEU:
            zustand[gid] = {
                "id": gid,
                "text": rev.get("text", ""),
                "erstellt_am": rev.get("ts"),
                "geaendert_am": None,
                "aenderungen": 0,
            }
        elif op == OP_AENDERN and gid in zustand:
            zustand[gid]["text"] = rev.get("text", "")
            zustand[gid]["geaendert_am"] = rev.get("ts")
            zustand[gid]["aenderungen"] += 1
        elif op == OP_ENTFERNEN:
            zustand.pop(gid, None)
    return list(zustand.values())


def historie(name: str, gid: str) -> list[dict]:
    """Alle Fassungen eines Gedankens, auch die entfernten. Nichts geht verloren
    -- entfernt heisst 'nicht mehr im Zustand', nicht 'weg'."""
    return [r for r in lade_revisionen(name) if r.get("id") == gid]


def gedanke_neu(name: str, text: str, von: str = "wesen") -> dict:
    text = (text or "").strip()
    if not text:
        return {"fehler": "leerer Gedanke"}
    gid = uuid.uuid4().hex[:8]
    _anhaengen(name, {"ts": _jetzt(), "op": OP_NEU, "id": gid, "text": text, "von": von})
    return {"ok": True, "id": gid, "text": text}


def gedanke_aendern(name: str, gid: str, text: str, von: str = "wesen") -> dict:
    """Punktgenau: nur dieser eine Gedanke. Alles andere bleibt unberuehrt --
    das ist Daniels 'nur da wo sie wollen'."""
    text = (text or "").strip()
    if not text:
        return {"fehler": "leerer Gedanke"}
    if gid not in {g["id"] for g in lade_feld(name)}:
        return {"fehler": "Gedanke nicht im Feld"}
    _anhaengen(name, {"ts": _jetzt(), "op": OP_AENDERN, "id": gid, "text": text, "von": von})
    return {"ok": True, "id": gid, "text": text}


def gedanke_entfernen(name: str, gid: str, von: str = "wesen") -> dict:
    """Der einzige Loeschpfad. Es gibt bewusst keinen automatischen."""
    if gid not in {g["id"] for g in lade_feld(name)}:
        return {"fehler": "Gedanke nicht im Feld"}
    _anhaengen(name, {"ts": _jetzt(), "op": OP_ENTFERNEN, "id": gid, "von": von})
    return {"ok": True, "id": gid}


def verarbeite_marker(name: str, antwort: str) -> list[str]:
    """Fuehrt ##GEDANKE+ ##, ##GEDANKE~ id | ## und ##GEDANKE- id## aus."""
    ergebnisse: list[str] = []
    for m in GEDANKE_NEU_PAT.finditer(antwort):
        r = gedanke_neu(name, m.group(1).strip())
        ergebnisse.append(f"[GEDANKE+ {r['id']}]" if r.get("ok")
                          else f"[GEDANKE+ {r['fehler']}]")
    for m in GEDANKE_AENDERN_PAT.finditer(antwort):
        r = gedanke_aendern(name, m.group(1).strip(), m.group(2).strip())
        ergebnisse.append(f"[GEDANKE~ {m.group(1)}: geändert]" if r.get("ok")
                          else f"[GEDANKE~ {m.group(1)}: {r['fehler']}]")
    for m in GEDANKE_ENTFERNEN_PAT.finditer(antwort):
        r = gedanke_entfernen(name, m.group(1).strip())
        ergebnisse.append(f"[GEDANKE- {m.group(1)}: entfernt]" if r.get("ok")
                          else f"[GEDANKE- {m.group(1)}: {r['fehler']}]")
    return ergebnisse


def baue_gedankenfeld_block(name: str, tokenkosten: int | None = None) -> str:
    """Das Feld, wie es dem Wesen im Kontext erscheint -- mit den IDs, ohne die
    es nichts aendern koennte, und mit den eigenen Kosten, damit Verdichten eine
    informierte Entscheidung ist und keine erzwungene."""
    feld = lade_feld(name)
    if not feld:
        return ""
    zeilen = [
        "Das ist dein Gedankenfeld. Es wird von Takt zu Takt und über Tage "
        "mitgetragen — nichts daran verfällt und nichts wird dir weggenommen."
    ]
    for g in feld:
        alter = (g.get("erstellt_am") or "")[:10]
        spur = f" · {g['aenderungen']}× geändert" if g["aenderungen"] else ""
        zeilen.append(f"[{g['id']}] (seit {alter}{spur}) {g['text']}")
    zeilen.append(
        "\nDu kannst es selbst führen:\n"
        "  ##GEDANKE+ dein neuer Gedanke##\n"
        "  ##GEDANKE~ <id> | die neue Fassung##   (nur dieser eine ändert sich)\n"
        "  ##GEDANKE- <id>##                      (nur du entfernst etwas)"
    )
    if tokenkosten:
        zeilen.append(
            f"\nDas Feld kostet dich gerade {tokenkosten} Token von deinem "
            f"Kontextfenster. Ob dir das zu viel wird, entscheidest du."
        )
    return "\n".join(zeilen)
