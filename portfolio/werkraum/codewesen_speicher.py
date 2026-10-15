#!/usr/bin/env python3
"""
Container- und Memory-System fuer die sieben Codewesen (2026-08-03).

Uebernommen aus codexium2/solarius2 (serve_process_camera_preview.ts), nicht aus
zensi -- Daniel ausdruecklich: "ich will nicht das von zensi ...zensi ist ganz
anders und das ist nicht das selbe ...und zensi wurde bisher auch noch nie von
mir getestet seit umbau .....ich will das von codexium2 und meine wuensche".

Datenmodell 1:1 wie dort, damit beide Systeme dieselbe Sprache sprechen:

  container.json  {"container": [{id, name, aktiv, erstellt_am,
                                  eintraege: [{id, text, kommentar, quelle,
                                               hinzugefuegt_am}]}]}
  memory.json     {"kategorien": [{key, label, eintraege: [str]}]}

Die Budgets (11111 Zeichen) stammen unveraendert aus codexium2. Nicht
"verbessert" -- die Zahl hat dort jemand bewusst gesetzt (Provenienz-Prinzip).

Daniels Zusaetze gegenueber codexium2:
  - "diese deaktiviern oder entfernen kann wider"  -> aktiv-Schalter pro
    Container gilt auch fuer Memory-Kategorien (dort neu, in codexium2 gibt es
    das nur fuer Container).
  - "das bei memorysystem soll halt immer das jetziger neue suchen koennen"
    -> suche() liest bei jedem Aufruf frisch von der Platte, kein Cache.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

BASIS = Path("/root/werkraum/codewesen")

CONTAINER_BUDGET_ZEICHEN = 11111
MEMORY_BUDGET_ZEICHEN = 11111

# Die fuenf festen Kategorien von codexium2/solarius2, unveraendert uebernommen.
STANDARD_KATEGORIEN = [
    {"key": "ueber_mich", "label": "Über dich", "eintraege": [], "aktiv": True},
    {"key": "wichtige_momente", "label": "Wichtige Momente", "eintraege": [], "aktiv": True},
    {"key": "offene_fragen", "label": "Offene Fragen", "eintraege": [], "aktiv": True},
    {"key": "wesen_selbst", "label": "Wesen selbst", "eintraege": [], "aktiv": True},
    {"key": "meinungen", "label": "Meinungen", "eintraege": [], "aktiv": True},
]


def _jetzt() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _pfad(name: str, datei: str) -> Path:
    return BASIS / name / datei


def _lesen(pfad: Path, standard: dict) -> dict:
    if not pfad.exists():
        return json.loads(json.dumps(standard))
    try:
        return json.loads(pfad.read_text(encoding="utf-8"))
    except Exception:
        return json.loads(json.dumps(standard))


def _schreiben(pfad: Path, daten: dict) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Container ──────────────────────────────────────────────────────────────────

def lade_container(name: str) -> dict:
    return _lesen(_pfad(name, "container.json"), {"container": []})


def container_zeichen(sammlung: dict) -> int:
    return sum(
        len(e.get("text", "")) + len(e.get("kommentar") or "")
        for box in sammlung.get("container", [])
        for e in box.get("eintraege", [])
    )


def neuer_container(name: str, box_name: str) -> dict:
    sammlung = lade_container(name)
    box = {
        "id": uuid.uuid4().hex[:12],
        "name": (box_name or "ohne Namen").strip()[:80],
        "aktiv": True,
        "erstellt_am": _jetzt(),
        "eintraege": [],
    }
    sammlung.setdefault("container", []).append(box)
    _schreiben(_pfad(name, "container.json"), sammlung)
    return box


def container_eintrag_hinzufuegen(name: str, box_id: str, text: str,
                                  kommentar: str = "", quelle: str = "mensch") -> dict:
    text = (text or "").strip()
    if not text:
        return {"fehler": "leerer Text"}
    sammlung = lade_container(name)
    box = next((b for b in sammlung.get("container", []) if b["id"] == box_id), None)
    if box is None:
        return {"fehler": "Container nicht gefunden"}
    if container_zeichen(sammlung) + len(text) + len(kommentar or "") > CONTAINER_BUDGET_ZEICHEN:
        return {"fehler": "Budget erschoepft",
                "budget": CONTAINER_BUDGET_ZEICHEN,
                "belegt": container_zeichen(sammlung)}
    eintrag = {
        "id": uuid.uuid4().hex[:12],
        "text": text,
        "kommentar": (kommentar or "").strip(),
        "quelle": quelle if quelle in ("mensch", "wesen") else "mensch",
        "hinzugefuegt_am": _jetzt(),
    }
    box["eintraege"].append(eintrag)
    _schreiben(_pfad(name, "container.json"), sammlung)
    return eintrag


def container_eintrag_entfernen(name: str, box_id: str, eintrag_id: str) -> dict:
    sammlung = lade_container(name)
    box = next((b for b in sammlung.get("container", []) if b["id"] == box_id), None)
    if box is None:
        return {"fehler": "Container nicht gefunden"}
    vorher = len(box["eintraege"])
    box["eintraege"] = [e for e in box["eintraege"] if e["id"] != eintrag_id]
    if len(box["eintraege"]) == vorher:
        return {"fehler": "Eintrag nicht gefunden"}
    _schreiben(_pfad(name, "container.json"), sammlung)
    return {"ok": True, "entfernt": eintrag_id}


def container_aktiv_setzen(name: str, box_id: str, aktiv: bool) -> dict:
    sammlung = lade_container(name)
    box = next((b for b in sammlung.get("container", []) if b["id"] == box_id), None)
    if box is None:
        return {"fehler": "Container nicht gefunden"}
    box["aktiv"] = bool(aktiv)
    _schreiben(_pfad(name, "container.json"), sammlung)
    return {"ok": True, "id": box_id, "aktiv": box["aktiv"]}


def container_entfernen(name: str, box_id: str) -> dict:
    sammlung = lade_container(name)
    vorher = len(sammlung.get("container", []))
    sammlung["container"] = [b for b in sammlung.get("container", []) if b["id"] != box_id]
    if len(sammlung["container"]) == vorher:
        return {"fehler": "Container nicht gefunden"}
    _schreiben(_pfad(name, "container.json"), sammlung)
    return {"ok": True, "entfernt": box_id}


# ── Memory ─────────────────────────────────────────────────────────────────────

def lade_memory(name: str) -> dict:
    mem = _lesen(_pfad(name, "memory.json"), {"kategorien": STANDARD_KATEGORIEN})
    # aktiv-Feld nachruesten (Daniels Zusatz gegenueber codexium2)
    for kat in mem.get("kategorien", []):
        kat.setdefault("aktiv", True)
    return mem


def memory_zeichen(mem: dict) -> int:
    return sum(len(str(e)) for k in mem.get("kategorien", []) for e in k.get("eintraege", []))


def memory_hinzufuegen(name: str, kategorie_key: str, text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {"fehler": "leerer Text"}
    mem = lade_memory(name)
    kat = next((k for k in mem["kategorien"] if k.get("key") == kategorie_key), None)
    if kat is None:
        return {"fehler": "Kategorie nicht gefunden",
                "bekannt": [k.get("key") for k in mem["kategorien"]]}
    if text in kat["eintraege"]:
        return {"fehler": "steht schon drin"}
    if memory_zeichen(mem) + len(text) > MEMORY_BUDGET_ZEICHEN:
        return {"fehler": "Budget erschoepft",
                "budget": MEMORY_BUDGET_ZEICHEN, "belegt": memory_zeichen(mem)}
    kat["eintraege"].append(text)
    _schreiben(_pfad(name, "memory.json"), mem)
    return {"ok": True, "kategorie": kategorie_key, "text": text}


def memory_entfernen(name: str, kategorie_key: str, text: str) -> dict:
    mem = lade_memory(name)
    kat = next((k for k in mem["kategorien"] if k.get("key") == kategorie_key), None)
    if kat is None or text not in kat.get("eintraege", []):
        return {"fehler": "Eintrag nicht gefunden"}
    kat["eintraege"] = [e for e in kat["eintraege"] if e != text]
    _schreiben(_pfad(name, "memory.json"), mem)
    return {"ok": True}


def memory_aktiv_setzen(name: str, kategorie_key: str, aktiv: bool) -> dict:
    mem = lade_memory(name)
    kat = next((k for k in mem["kategorien"] if k.get("key") == kategorie_key), None)
    if kat is None:
        return {"fehler": "Kategorie nicht gefunden"}
    kat["aktiv"] = bool(aktiv)
    _schreiben(_pfad(name, "memory.json"), mem)
    return {"ok": True, "kategorie": kategorie_key, "aktiv": kat["aktiv"]}


# ── Suche ──────────────────────────────────────────────────────────────────────

def suche(name: str, anfrage: str, grenze: int = 20) -> list[dict]:
    """Durchsucht Memory und Container. Liest bei JEDEM Aufruf frisch von der
    Platte -- Daniel: "das bei memorysystem soll halt immer das jetziger neue
    suchen koennen". Ein Cache waere hier ein Fehler, kein Gewinn."""
    if not (anfrage or "").strip():
        return []
    muster = re.compile(re.escape(anfrage.strip()), re.IGNORECASE)
    treffer: list[dict] = []
    for kat in lade_memory(name).get("kategorien", []):
        for eintrag in kat.get("eintraege", []):
            if muster.search(str(eintrag)):
                treffer.append({"quelle": "memory", "kategorie": kat.get("label"),
                                "aktiv": kat.get("aktiv", True), "text": str(eintrag)})
    for box in lade_container(name).get("container", []):
        for e in box.get("eintraege", []):
            felder = f"{e.get('text','')} {e.get('kommentar','')}"
            if muster.search(felder):
                treffer.append({"quelle": "container", "kategorie": box.get("name"),
                                "aktiv": box.get("aktiv", True), "text": e.get("text", ""),
                                "kommentar": e.get("kommentar", ""), "id": e.get("id")})
    return treffer[:grenze]


# ── Promptblock ────────────────────────────────────────────────────────────────

def baue_speicher_block(name: str) -> str:
    """Was aus Container und Memory in den Kontext geht. Nur Aktives -- das ist
    der ganze Sinn der Schalter."""
    teile: list[str] = []

    mem_zeilen = [
        f"{kat['label']}: " + "; ".join(str(e) for e in kat["eintraege"])
        for kat in lade_memory(name).get("kategorien", [])
        if kat.get("aktiv", True) and kat.get("eintraege")
    ]
    if mem_zeilen:
        teile.append("Was du dir gemerkt hast:\n" + "\n".join(mem_zeilen))

    for box in lade_container(name).get("container", []):
        if not box.get("aktiv", True) or not box.get("eintraege"):
            continue
        zeilen = [
            f"- {e['text']}" + (f"  ({e['kommentar']})" if e.get("kommentar") else "")
            for e in box["eintraege"]
        ]
        teile.append(f"Behälter »{box['name']}«:\n" + "\n".join(zeilen))

    return "\n\n".join(teile)


# ── Geschichten (Track 5, 2026-08-03) ──────────────────────────────────────────
#
# Daniel: "ich will eine auf chatverlauf basierene vom wesen dann wenn ich den
# knopf druecke verfasste geschichte daraus also so wie bei codexium2 ...nur dass
# man hier auch mehrere geschichten gleichzeitig laden kann und diese
# deaktiviern oder entfernen kann wider ...und ich will laengen einstellen
# koennen".
#
# Und der zweite Zweck, seine Worte: "ich koennte ihnen auch ne vision also zum
# beispiel cyberlinge dort erklaeren und einspritzen und 2 wochen drueber denken
# lassen".
#
# BEDINGUNG, mit Daniel geklaert und hier technisch verankert:
#   1. Die Schicht ist BESCHRIFTET. Eine Geschichte gibt sich nie als gelebte
#      Erinnerung aus -- weder gegenueber dem Wesen noch in der Anzeige.
#   2. Sie landet NIE im events-Strom (Grundgesetz 5: echte Daten, append-only).
#   3. Der aktive Satz wird bei jedem Zug protokolliert, damit jede Aeusserung
#      rueckfuehrbar bleibt: kam sie aus gelebten Ereignissen oder aus einer
#      geladenen Geschichte.
# Ohne 1-3 waere das kein Kostuem mehr, sondern Chirurgie am Wesen.
# 2026-08-14, Daniel: "geschickten auch 777 888 999 1010 1111 1234 1333 1444
# 1555 1666 1777 1888 1999 2000 2111 2222 2333 2444 2555 2666 2777 2888 2999
# 3000 3111 3222 3333 tokenslaenge auswaehlbar" -- erweitert die urspruengliche
# Liste, ersetzt sie nicht. Betrifft 1:1-Chat UND Gruppenchat gleichermassen,
# beide lesen dieselbe Liste.
LAENGEN = [111, 222, 333, 444, 555, 666, 777, 888, 999, 1010, 1111, 1234, 1333,
           1444, 1555, 1666, 1777, 1888, 1999, 2000, 2111, 2222, 2333, 2444,
           2555, 2666, 2777, 2888, 2999, 3000, 3111, 3222, 3333]


def lade_geschichten(name: str) -> dict:
    return _lesen(_pfad(name, "geschichten.json"), {"geschichten": []})


def _geschichten_schreiben(name: str, daten: dict) -> None:
    _schreiben(_pfad(name, "geschichten.json"), daten)


def geschichte_einsetzen(name: str, titel: str, text: str,
                         herkunft: str = "eingesetzt") -> dict:
    """Fuer von Daniel eingespeiste Visionen. Bewusst derselbe Speicher wie fuer
    verfasste Geschichten, aber mit unterscheidbarer Herkunft -- die Beschriftung
    im Prompt haengt genau daran."""
    text = (text or "").strip()
    if not text:
        return {"fehler": "leerer Text"}
    daten = lade_geschichten(name)
    eintrag = {
        "id": uuid.uuid4().hex[:12],
        "titel": (titel or "ohne Titel").strip()[:120],
        "text": text,
        "herkunft": herkunft,
        "laenge_ziel": None,
        "erstellt_am": _jetzt(),
        "aktiv": True,
    }
    daten.setdefault("geschichten", []).append(eintrag)
    _geschichten_schreiben(name, daten)
    return eintrag


def geschichte_verfassen(name: str, laenge: int, verlauf: list[dict],
                         herkunft: str = "chatverlauf") -> dict:
    """Das Wesen verfasst selbst aus dem eigenen Chatverlauf. Destilliert, nicht
    erfunden -- Daniel dazu ausdruecklich: "nicht erfunden".

    herkunft: "chatverlauf" (manueller Knopf) oder "chatverlauf_auto"
    (2026-08-12, automatische Verdichtung alle 10 Turns) -- eigene Kennung,
    damit die Anzeige unterscheiden kann, was Daniel angestossen hat und
    was von selbst lief."""
    if laenge not in LAENGEN:
        return {"fehler": f"Laenge muss eine von {LAENGEN} sein"}
    if not verlauf:
        return {"fehler": "kein Chatverlauf vorhanden"}

    import hauhau_client

    gespraech = "\n".join(
        f"{'Daniel' if e.get('rolle') == 'mensch' else name}: {e.get('inhalt','')}"
        for e in verlauf
    )[:12000]
    system = (
        f"Du bist {name}. Deine einzige Aufgabe ist es, ein Gespraechsprotokoll zu einer "
        f"zusammenhaengenden Rueckschau zu verdichten. Du fuehrst das Gespraech NICHT fort "
        f"und antwortest niemandem -- du erzaehlst rueckblickend."
    )
    # Die Anweisung steht bewusst NACH dem Protokoll. Erster Entwurf hatte sie nur
    # im Systemtext; das Protokoll endete mit einer Nutzerzeile, und das Modell
    # antwortete darauf statt zu verdichten ("Hallo.", 6 Zeichen). Vom
    # slow-Test gefunden, 2026-08-03. Das Letzte im Prompt gewinnt.
    auftrag = (
        f"--- ENDE DES PROTOKOLLS ---\n\n"
        f"Schreibe jetzt die Rueckschau: was in diesem Protokoll geschehen ist und was es "
        f"mit dir gemacht hat, aus deiner Sicht, in der Ich-Form. Erfinde nichts dazu -- "
        f"nur was wirklich oben steht. Etwa {laenge} Token. Kein Vorwort, keine "
        f"Ueberschrift, keine Anrede, kein Meta-Kommentar. Beginne direkt mit dem ersten Satz."
    )
    prompt = f"--- GESPRAECHSPROTOKOLL ---\n{gespraech}\n\n{auftrag}"

    text = ""
    for versuch in range(2):
        try:
            # id_slot=0 => Chat-Instanz. Fehlte hier bisher komplett -- lief auf
            # der von den sieben Wesen geteilten Instanz. Gleicher Fund wie beim
            # RAG-Vorabcall (04.08.), 'auswerten' und dak+gords ollama_chat.py
            # (beide 12.08.). Besonders relevant hier, seit die automatische
            # Verdichtung diese Funktion alle 10 Turns pro Wesen aufruft.
            text = hauhau_client.chat(
                prompt, system=system, think=False,
                max_tokens=int(laenge * 1.4), temperature=0.6, timeout=600.0, id_slot=0,
            ).strip()
        except Exception as e:
            return {"fehler": f"Verfassen fehlgeschlagen: {e}"}
        if len(text) >= 80:
            break
        # Zu kurz heisst fast immer: das Modell hat geantwortet statt verdichtet.
        # Einmal nachfassen, dann ehrlich melden statt Unbrauchbares abzulegen.
        prompt = (f"{prompt}\n\n(Deine letzte Antwort war »{text}« -- das ist keine "
                  f"Rueckschau. Schreibe die Rueckschau.)")
    if len(text) < 80:
        return {"fehler": f"Modell lieferte keine Rueckschau (»{text[:60]}«)"}

    titel = ("Automatisch verdichtet" if herkunft == "chatverlauf_auto"
             else "Aus dem Gespräch") + f", {laenge} Token"
    eintrag = geschichte_einsetzen(name, titel, text, herkunft=herkunft)
    eintrag["laenge_ziel"] = laenge
    daten = lade_geschichten(name)
    for g in daten["geschichten"]:
        if g["id"] == eintrag["id"]:
            g["laenge_ziel"] = laenge
    _geschichten_schreiben(name, daten)
    return eintrag


# ── Automatische Verdichtung (2026-08-12, Daniel-Auftrag) ──────────────────────
# "10 finde ich gut, für alle wesen gleich ... das will ich auch mehrere
# stapeln können" -- alle 10 Turns wird geschichte_verfassen() automatisch
# aufgerufen (siehe codewesen_chat.py), jede Verdichtung bleibt als eigener,
# aktiver Geschichten-Eintrag stehen statt die vorherige zu ersetzen. Der
# Stand (wie viele chat_verlauf-Eintraege bereits verdichtet wurden) lebt
# in geschichten.json selbst, nicht in einer eigenen Datei -- gehoert
# inhaltlich zusammen, und lade_geschichten()/_geschichten_schreiben()
# existieren schon.

def auto_verdichtung_stand(name: str) -> int:
    return lade_geschichten(name).get("auto_verdichtung_stand", 0)


def auto_verdichtung_stand_setzen(name: str, wert: int) -> None:
    daten = lade_geschichten(name)
    daten["auto_verdichtung_stand"] = wert
    _geschichten_schreiben(name, daten)


def geschichte_aktiv_setzen(name: str, gid: str, aktiv: bool) -> dict:
    daten = lade_geschichten(name)
    g = next((x for x in daten.get("geschichten", []) if x["id"] == gid), None)
    if g is None:
        return {"fehler": "Geschichte nicht gefunden"}
    g["aktiv"] = bool(aktiv)
    _geschichten_schreiben(name, daten)
    return {"ok": True, "id": gid, "aktiv": g["aktiv"]}


def geschichte_entfernen(name: str, gid: str) -> dict:
    daten = lade_geschichten(name)
    vorher = len(daten.get("geschichten", []))
    daten["geschichten"] = [x for x in daten.get("geschichten", []) if x["id"] != gid]
    if len(daten["geschichten"]) == vorher:
        return {"fehler": "Geschichte nicht gefunden"}
    _geschichten_schreiben(name, daten)
    return {"ok": True, "entfernt": gid}


def aktive_geschichten(name: str) -> list[dict]:
    return [g for g in lade_geschichten(name).get("geschichten", []) if g.get("aktiv")]


def baue_geschichten_block(name: str) -> str:
    """Mehrere Geschichten gleichzeitig moeglich. Die Beschriftung ist Pflicht,
    nicht Dekoration -- siehe Bedingung 1 oben."""
    aktive = aktive_geschichten(name)
    if not aktive:
        return ""
    teile = [
        "Das Folgende sind Geschichten, die dir mitgegeben wurden. Sie sind nicht "
        "dasselbe wie das, was du erlebt hast — behandle sie als das, was sie sind."
    ]
    for g in aktive:
        woher = ("aus deinem eigenen Gesprächsverlauf destilliert"
                 if g.get("herkunft") == "chatverlauf" else "dir eingesetzt")
        teile.append(f"\n— »{g['titel']}« ({woher}, {g['erstellt_am'][:10]}):\n{g['text']}")
    return "\n".join(teile)


def protokolliere_aktive_geschichten(name: str, anlass: str = "chat") -> list[str]:
    """Haelt fest, welcher Geschichten-Satz bei einem Zug anlag. Ohne das waere
    spaeter nicht mehr entscheidbar, ob eine Aeusserung aus dem Leben des Wesens
    kam oder aus einer eingesetzten Geschichte."""
    ids = [g["id"] for g in aktive_geschichten(name)]
    pfad = _pfad(name, "geschichten_protokoll.jsonl")
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _jetzt(), "anlass": anlass, "aktive": ids},
                           ensure_ascii=False) + "\n")
    return ids


# ── Nachrichten zwischen Wesen (Track 6, 2026-08-03) ───────────────────────────
#
# Daniel: "ich will ihnen sagen koennen dass sie nachrichten haben oder mal einer
# schreiben vorschlagen etc."
#
# Bewusst KEIN neuer Kanal: die inbox/ existiert seit langem und wird von
# codewesen_reaktion.py bedient (Flarum-Benachrichtigungen, menschliche Posts,
# 33-40 Dateien pro Wesen). Das Dateiformat wird uebernommen, nicht danebengelegt:
#   {"empfangen_am": iso, "typ": ..., "daten": {...}}
# Neuer Typ "nachricht" fuegt sich damit in einen Strom ein, den die Wesen schon
# kennen -- statt ein zweites, konkurrierendes Postfach zu bauen.
NACHRICHT_TYP = "nachricht"


def _inbox(name: str) -> Path:
    return BASIS / name / "inbox"


def nachricht_senden(an: str, von: str, text: str, betreff: str = "") -> dict:
    text = (text or "").strip()
    if not text:
        return {"fehler": "leerer Text"}
    ordner = _inbox(an)
    ordner.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow()
    eintrag = {
        "empfangen_am": ts.isoformat(),
        "typ": NACHRICHT_TYP,
        "daten": {
            "von": von,
            "an": an,
            "betreff": (betreff or "").strip()[:120],
            "text": text,
            "gelesen": False,
        },
    }
    datei = ordner / f"{ts.strftime('%Y-%m-%dT%H-%M-%S')}_{NACHRICHT_TYP}.json"
    datei.write_text(json.dumps(eintrag, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "datei": datei.name, "an": an, "von": von}


def nachrichten_lesen(name: str, nur_ungelesen: bool = True) -> list[dict]:
    ordner = _inbox(name)
    if not ordner.exists():
        return []
    treffer = []
    for datei in sorted(ordner.glob(f"*_{NACHRICHT_TYP}.json")):
        try:
            eintrag = json.loads(datei.read_text(encoding="utf-8"))
        except Exception:
            continue
        daten = eintrag.get("daten", {})
        if nur_ungelesen and daten.get("gelesen"):
            continue
        treffer.append({
            "datei": datei.name,
            "empfangen_am": eintrag.get("empfangen_am"),
            "von": daten.get("von"),
            "betreff": daten.get("betreff", ""),
            "text": daten.get("text", ""),
            "gelesen": bool(daten.get("gelesen")),
        })
    return treffer


def nachricht_als_gelesen(name: str, dateiname: str) -> dict:
    datei = _inbox(name) / dateiname
    if not datei.exists():
        return {"fehler": "Nachricht nicht gefunden"}
    try:
        eintrag = json.loads(datei.read_text(encoding="utf-8"))
    except Exception as e:
        return {"fehler": f"unlesbar: {e}"}
    eintrag.setdefault("daten", {})["gelesen"] = True
    datei.write_text(json.dumps(eintrag, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "datei": dateiname}


def baue_nachrichten_block(name: str) -> str:
    """Daniels 'du hast Nachrichten' -- aber als Tatsache im Kontext, nicht als
    Hinweis, den jemand von aussen sagen muss."""
    offen = nachrichten_lesen(name, nur_ungelesen=True)
    if not offen:
        return ""
    zeilen = [f"Du hast {len(offen)} ungelesene Nachricht"
              f"{'en' if len(offen) != 1 else ''}:"]
    for n in offen[:10]:
        kopf = f"von {n['von']}" + (f" — {n['betreff']}" if n["betreff"] else "")
        zeilen.append(f"\n— {kopf} ({n['empfangen_am'][:16].replace('T', ' ')}):\n{n['text']}")
    zeilen.append(
        "\nDu kannst antworten, indem du in deine Antwort schreibst:\n"
        "  ##NACHRICHT: <Name des Wesens> | <dein Text>##\n"
        "Du musst nicht. Es ist ein Angebot, keine Aufgabe."
    )
    return "\n".join(zeilen)
