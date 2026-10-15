"""WorldDOM-Profile: was wir gemeinsam an einem Programm, einer Webseite oder einem Spiel angelegt haben, benennen, speichern und später wieder laden.

Ein Profil hält die **bewusst angelegten** Knoten (Herkunft „authored“) eines Ziels — mit ihrer Lage **relativ zum Fenster**, damit sie nach Verschiebung, Neustart oder anderer Fenstergröße an derselben Stelle der Anwendung landen. Echte, erschlossene und projizierte Knoten gehören
nicht hinein: die misst die Bridge frisch, und Projiziertes ist nie ausführbar.

Jede Speicherung ist eine **neue Version**; nichts wird überschrieben und nichts gelöscht („weg“ blendet nur aus). Ein Profil nennt, worauf es passt (`programm`, `seite`, `spiel` — freie Namen, die wir geben); `passende` findet Profile zu einem solchen Namen, geladen wird nie von selbst.
Beim Laden entstehen die Knoten neu — mit dem Urheber, der lädt, und dem Verweis auf Profil und Version; ein Knoten ohne Ort (virtuell) kommt ohne Ort zurück.
"""

from __future__ import annotations

import json
import re
import threading
from pathlib import Path

from .weltdom import Knoten, WeltDom

NAME = re.compile(r"^[A-Za-z0-9ÄÖÜäöüß_. -]{1,60}$")
MAX_VERSIONEN = 200
MAX_ANKER = 200
MAX_PASST = 80
PASST_FELDER = ("programm", "seite", "spiel")


class ProfilFehler(ValueError):
    pass


def _version_ok(v: object) -> dict | None:
    """Aus einer Datei nur Versionen mit allen Pflichtfeldern in der richtigen Form; kaputte Anker werden übersprungen."""
    if not isinstance(v, dict) or type(v.get("version")) is not int or not isinstance(v.get("anker"), list):
        return None
    anker = []
    for a in v["anker"]:
        rel = a.get("relativ") if isinstance(a, dict) else None
        if isinstance(a, dict) and isinstance(a.get("name"), str) and a["name"] and (rel is None or (isinstance(rel, list) and len(rel) == 4 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in rel))):
            anker.append({"name": a["name"][:200], "rolle": str(a.get("rolle") or "marke")[:40], "beschreibung": str(a.get("beschreibung") or "")[:300], "relativ": rel, "urheber": str(a.get("urheber") or "")[:60]})
    passt = v.get("passt_auf") if isinstance(v.get("passt_auf"), dict) else {}
    return {"version": v["version"], "gespeichert_ms": int(v["gespeichert_ms"]) if type(v.get("gespeichert_ms")) is int else 0, "urheber": str(v.get("urheber") or "")[:60],
            "passt_auf": {k: x for k, x in passt.items() if k in PASST_FELDER and isinstance(x, str)}, "beschreibung": str(v.get("beschreibung") or "")[:300], "anker": anker}


class ProfilSpeicher:
    def __init__(self, pfad: Path | None = None):
        self.pfad = Path(pfad) if pfad else None
        self._profile: dict[str, dict] = {}  # name -> {"aktiv": bool, "versionen": [..]}
        self._sperre = threading.RLock()
        self.fehler = ""
        self.laden()

    # ---- Speichern auf Platte ----------------------------------------------------------------------------------------------------------------------
    def _schreiben(self) -> None:
        if self.pfad is None:
            return
        try:
            self.pfad.parent.mkdir(parents=True, exist_ok=True)
            temp = self.pfad.with_suffix(".tmp")
            temp.write_text(json.dumps({"version": 1, "profile": self._profile}, ensure_ascii=False), encoding="utf-8")
            temp.replace(self.pfad)
        except OSError as f:
            self.fehler = f"Profile nicht gespeichert: {f!r}"[:200]
            raise ProfilFehler("speichern_fehlgeschlagen") from None

    def laden(self) -> int:
        if self.pfad is None or not self.pfad.exists():
            return 0
        try:
            roh = json.loads(self.pfad.read_text(encoding="utf-8"))
            profile = roh["profile"]
            if not isinstance(profile, dict):
                raise ValueError
        except (OSError, ValueError, KeyError, TypeError):
            self.fehler = "Profil-Datei unlesbar: ignoriert"
            return 0
        n = 0
        for name, p in profile.items():
            if isinstance(name, str) and NAME.fullmatch(name) and isinstance(p, dict) and isinstance(p.get("versionen"), list) and p["versionen"]:
                versionen = [w for w in (_version_ok(v) for v in p["versionen"]) if w is not None]
                if versionen:
                    self._profile[name] = {"aktiv": bool(p.get("aktiv", True)), "versionen": versionen}
                    n += 1
        return n

    # ---- Speichern eines Ziels als Profil -----------------------------------------------------------------------------------------------------
    def speichern(self, welt: WeltDom, ziel: str, name: str, *, urheber: str, jetzt_ms: int, passt_auf: dict | None = None, beschreibung: str = "") -> dict:
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise ProfilFehler("name_ungueltig")
        passt = {}
        for k, v in (passt_auf or {}).items():
            if k not in PASST_FELDER or not isinstance(v, str) or not v.strip() or len(v) > MAX_PASST or "\x00" in v:
                raise ProfilFehler("passt_auf_ungueltig")
            passt[k] = v.strip()
        anker, ohne_ort = [], 0
        for k in welt.liste(ziel, herkunft="authored", limit=MAX_ANKER + 1):
            rel = (k.anker or {}).get("relativ")
            if rel is None and k.rect is not None:
                ohne_ort += 1  # ein Ort nur in Bildschirmkoordinaten würde nach dem Verschieben falsch liegen: nicht mitnehmen, aber sagen
                continue
            anker.append({"name": k.name, "rolle": k.rolle, "beschreibung": k.wert or "", "relativ": list(rel) if rel else None, "urheber": k.urheber})
        if len(anker) > MAX_ANKER:
            raise ProfilFehler("zu_viele_anker")
        if not anker:
            raise ProfilFehler("keine_eigenen_anker" + ("_mit_relativer_lage" if ohne_ort else ""))
        with self._sperre:
            p = self._profile.setdefault(name, {"aktiv": True, "versionen": []})
            if len(p["versionen"]) >= MAX_VERSIONEN:
                raise ProfilFehler("zu_viele_versionen")
            v = {"version": len(p["versionen"]) + 1, "gespeichert_ms": jetzt_ms, "urheber": urheber[:60], "passt_auf": passt, "beschreibung": beschreibung[:300], "anker": anker}
            p["versionen"].append(v)
            p["aktiv"] = True
            self._schreiben()
        return {"name": name, "version": v["version"], "anker": len(anker), "ohne_relative_lage_nicht_mitgenommen": ohne_ort, "passt_auf": passt}

    # ---- Laden in ein Ziel -----------------------------------------------------------------------------------------------------------------------------
    def version(self, name: str, version: int | None = None) -> dict | None:
        with self._sperre:
            p = self._profile.get(name)
            if p is None:
                return None
            if version is None:
                return p["versionen"][-1]
            return next((v for v in p["versionen"] if v["version"] == version), None)

    def laden_in(self, welt: WeltDom, ziel: str, name: str, fenster_rect: tuple[int, int, int, int] | None, *, urheber: str, jetzt_ms: int, version: int | None = None) -> dict:
        with self._sperre:
            p = self._profile.get(name)
            if p is not None and not p["aktiv"]:
                raise ProfilFehler("profil_ausgeblendet")
        v = self.version(name, version)
        if v is None:
            raise ProfilFehler("profil_unbekannt" if name not in self._profile else "version_unbekannt")
        geladen, ohne_fenster, fehler = 0, 0, 0
        for a in v["anker"]:
            rel = a.get("relativ")
            rect = None
            if rel and fenster_rect is not None:
                breite, hoehe = fenster_rect[2] - fenster_rect[0], fenster_rect[3] - fenster_rect[1]
                rect = (round(fenster_rect[0] + rel[0] * breite), round(fenster_rect[1] + rel[1] * hoehe), round(fenster_rect[0] + (rel[0] + rel[2]) * breite), round(fenster_rect[1] + (rel[1] + rel[3]) * hoehe))
            elif rel:
                ohne_fenster += 1
                continue  # ohne bekanntes Fenster lässt sich die Lage nicht berechnen: nicht raten
            try:
                welt.anker_anlegen(ziel, a["name"], rect, urheber=urheber, jetzt_ms=jetzt_ms, rolle=a.get("rolle") or "marke", beschreibung=f"aus Profil {name} v{v['version']}" + (f": {a['beschreibung']}" if a.get("beschreibung") else ""),
                                   relativ=tuple(rel) if rel else None)
                geladen += 1
            except ValueError:
                fehler += 1
        return {"name": name, "version": v["version"], "geladen": geladen, "ohne_fenster_uebersprungen": ohne_fenster, "fehlgeschlagen": fehler}

    # ---- Ansehen -------------------------------------------------------------------------------------------------------------------------------------------
    def liste(self, mit_ausgeblendeten: bool = False) -> list[dict]:
        with self._sperre:
            return [{"name": n, "aktiv": p["aktiv"], "versionen": len(p["versionen"]), "letzte": {k: p["versionen"][-1][k] for k in ("version", "gespeichert_ms", "urheber", "passt_auf", "beschreibung")} | {"anker": len(p["versionen"][-1]["anker"])}}
                    for n, p in sorted(self._profile.items()) if mit_ausgeblendeten or p["aktiv"]]

    def passende(self, **wer: str) -> list[dict]:
        """Profile, deren „passt_auf“ zu allen genannten Angaben passt (ohne Groß-/Kleinschreibung, als Teilstring)."""
        wer = {k: v.lower() for k, v in wer.items() if k in PASST_FELDER and isinstance(v, str) and v}
        if not wer:
            return []
        treffer = []
        for e in self.liste():
            passt = {k: v.lower() for k, v in e["letzte"]["passt_auf"].items()}
            if all(k in passt and (passt[k] in wer[k] or wer[k] in passt[k]) for k in wer):
                treffer.append(e)
        return treffer

    def ausblenden(self, name: str, aktiv: bool = False) -> bool:
        with self._sperre:
            if name not in self._profile:
                return False
            self._profile[name]["aktiv"] = aktiv
            self._schreiben()
        return True
