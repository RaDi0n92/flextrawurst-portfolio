#!/usr/bin/env python3
"""
Gruppenchat-Speicherung (2026-08-13) -- reines Speicher-Modul, keine LLM-Logik.

Daniels Auftrag: kollektiver Chat mit mehreren/allen sieben Codewesen gleichzeitig,
manuell gesteuert (kein autonomes Symposium wie bei zensi -- ausdruecklich anders
gewuenscht, analog zur bereits bestehenden Entscheidung bei codewesen_speicher.py:
"ich will nicht das von zensi ... ich will das von codexium2 und meine wuensche").

Eine Sitzung ist eine einzelne JSON-Datei (nicht JSONL): sie traegt veraenderlichen
Zustand (Teilnehmer, Modus, aktiver Sprecher) UND den anhaengenden Nachrichtenverlauf
gemeinsam, deshalb wird bei jeder Aenderung die ganze Datei neu geschrieben statt nur
angehaengt. Sitzungen bleiben klein genug (ein Gespraech, keine Wochen), das ist kein
Performance-Problem.

Zusaetzlich zur Sitzungsdatei schreibt codewesen_chat.py jede Nachricht auch in die
eigene chat_verlauf.jsonl des jeweils sprechenden/angesprochenen Wesens (Daniels
Entscheidung "beides") -- das passiert dort, nicht hier, weil dieses Modul die
Funktionen aus codewesen_chat.py (baue_system_prompt etc.) nicht importieren soll,
um einen Zirkularimport zu vermeiden.
"""
from __future__ import annotations

import json
import secrets
from datetime import datetime
from pathlib import Path

BASE = Path("/root/werkraum/codewesen/_gruppenchat/sitzungen")


def _sitzungen_dir() -> Path:
    BASE.mkdir(parents=True, exist_ok=True)
    return BASE


def _pfad(sid: str) -> Path:
    # sid kommt nur aus neue_id() oder aus vorhandenen Dateinamen -- trotzdem
    # keine Pfadanteile durchlassen, falls es je aus einer URL kommt.
    sid = Path(sid).name
    return _sitzungen_dir() / f"{sid}.json"


def neue_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S_") + secrets.token_hex(3)


def neue_sitzung(titel: str, teilnehmer: list[str]) -> dict:
    sid = neue_id()
    sitzung = {
        "id": sid,
        "titel": (titel or "").strip() or "Gruppenchat",
        "erstellt_am": datetime.utcnow().isoformat(),
        "teilnehmer": list(teilnehmer),
        "modus": "zuhoeren",
        "aktiver_sprecher": None,
        "nachrichten": [],
        "aktiv": True,
    }
    speichere_sitzung(sitzung)
    return sitzung


def ist_aktiv(sitzung: dict) -> bool:
    """Fehlendes Feld = aktiv -- Rueckwaertskompatibilitaet fuer Sitzungen von vor
    2026-09-17 (dieses Feld gab es vorher nicht, alle bestehenden Sitzungen galten
    implizit als aktiv/nachhallend)."""
    return sitzung.get("aktiv", True)


def setze_inaktiv(sid: str) -> dict | None:
    """2026-09-17, Daniels Auftrag: Gruppenchats duerfen erst frei nachhallen (bleiben
    aktiv, wie bisher), aber Daniel soll manuell markieren koennen wann eine Sitzung
    fertig ist -- inaktiv heisst NICHT geloescht oder unsichtbar, nur: taucht nicht mehr
    automatisch im 1:1-Kontext der Wesen auf, ist aber weiter durchsuchbar (siehe
    rag_ingest.ingest_gruppenchat, codewesen_chat._gruppenchat_inaktiv_setzen_endpoint)."""
    sitzung = lade_sitzung(sid)
    if sitzung is None:
        return None
    sitzung["aktiv"] = False
    sitzung["inaktiv_seit"] = datetime.utcnow().isoformat()
    speichere_sitzung(sitzung)
    return sitzung


def setze_aktiv(sid: str) -> dict | None:
    """Umkehrung von setze_inaktiv -- nichts hier ist endgueltig (Grundgesetz 4)."""
    sitzung = lade_sitzung(sid)
    if sitzung is None:
        return None
    sitzung["aktiv"] = True
    sitzung.pop("inaktiv_seit", None)
    speichere_sitzung(sitzung)
    return sitzung


def lade_sitzung(sid: str) -> dict | None:
    pfad = _pfad(sid)
    if not pfad.exists():
        return None
    try:
        return json.loads(pfad.read_text(encoding="utf-8"))
    except Exception:
        return None


def speichere_sitzung(sitzung: dict) -> None:
    pfad = _pfad(sitzung["id"])
    pfad.write_text(json.dumps(sitzung, ensure_ascii=False, indent=2), encoding="utf-8")


def liste_sitzungen() -> list[dict]:
    treffer = []
    for datei in _sitzungen_dir().glob("*.json"):
        try:
            s = json.loads(datei.read_text(encoding="utf-8"))
        except Exception:
            continue
        treffer.append({
            "id": s["id"], "titel": s.get("titel", ""),
            "teilnehmer": s.get("teilnehmer", []),
            "erstellt_am": s.get("erstellt_am"),
            "anzahl_nachrichten": len(s.get("nachrichten", [])),
            "letzte_aktivitaet": (s["nachrichten"][-1]["ts"] if s.get("nachrichten")
                                   else s.get("erstellt_am")),
            "aktiv": ist_aktiv(s),
        })
    treffer.sort(key=lambda x: x["letzte_aktivitaet"] or "", reverse=True)
    return treffer


def fuege_nachricht_hinzu(sitzung: dict, sprecher: str, text: str) -> dict:
    """sprecher == 'Daniel' fuer Menschen-Nachrichten, sonst ein Name aus
    sitzung['teilnehmer']. Gibt den neuen Eintrag zurueck, speichert die
    Sitzung sofort (nicht erst am Ende) -- gleiche Begruendung wie bei
    speichere_chat_eintrag in codewesen_chat.py: bei einem haengenden
    Folgeschritt geht sonst auch die Frage selbst verloren."""
    eintrag = {
        "ts": datetime.utcnow().isoformat(),
        "sprecher": sprecher,
        "rolle": "mensch" if sprecher == "Daniel" else "wesen",
        "text": text,
    }
    sitzung["nachrichten"].append(eintrag)
    speichere_sitzung(sitzung)
    return eintrag
