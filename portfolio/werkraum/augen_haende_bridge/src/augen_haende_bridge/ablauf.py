"""Abläufe (G12): deklarative, versionierte Graphen, die Agenten selbst entwerfen, speichern und ausführen — auf der vorhandenen Harness (`harness.py`).

Ein Ablauf ist **Daten** (JSON), kein Code. Ein neuer Ablauf braucht deshalb keinen neuen Build, solange er nur Fähigkeiten benutzt, die es schon gibt (R078). Die Harness liefert Zustand, Kanten, Spur,
Checkpoints und Zweige; dieses Modul ergänzt, was ihr fehlte: **Ausführen** (jeder Knoten ruft einen Handler), **Prüfungen** vorher und nachher, **Abweichungen mit Fallback**, **Zustand und Unsicherheit**,
**Versionen** und **Durchläufe, die erhalten bleiben**.

Knotenarten (→ Harness): `beobachten` (OBSERVATION), `handeln` und `delegieren` (ACTION), `pruefen` (OBSERVATION), `tor` (GATE, Daniels Freigabe), `zustand` und `warten` (STATE).
Jeder Knoten, der etwas tut, nennt einen Handler (`weltdom`, `haende`, `lease`, `nachricht`, `auftrag`); der Ausführer ruft ihn und wertet das Ergebnis aus: `ok` oder `abweichung` (Vorher-/Nachher-Prüfung oder Handler
meldet nicht ok) oder `fehler` (Ausnahme). Kanten tragen das Signal (`wenn`); fehlt für eine Abweichung ein Fallback, hält der Lauf ehrlich an (`blocked`), er rät nie weiter.

Bedingungen sind keine Programme: `{"pfad": "liste.knoten", "enthaelt": {"rolle": "button", "name": "OK"}}`. Werte aus früheren Knoten gehen als `{"$ref": "liste.knoten.0.id"}` oder
`{"$suche": {"pfad": "liste.knoten", "wo": {"name": "OK"}, "feld": "id"}}` in spätere Argumente — nichts davon wird ausgewertet (kein `eval`).
"""

from __future__ import annotations

import json
import re
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .harness import HarnessEdge, HarnessGraph, HarnessNode, HarnessRun, NodeKind, RunStatus

SCHEMA = 1
ARTEN = {"beobachten": NodeKind.OBSERVATION, "handeln": NodeKind.ACTION, "delegieren": NodeKind.ACTION, "pruefen": NodeKind.OBSERVATION, "tor": NodeKind.GATE, "zustand": NodeKind.STATE,
         "warten": NodeKind.STATE}
HANDELNDE_ARTEN = frozenset({"handeln", "delegieren"})  # verändern etwas außerhalb des Ablaufs: Shadow führt sie nie aus, das Daniel-Tor fragt vorher
AKTIONEN = ("weltdom", "haende", "lease", "nachricht", "auftrag")
SIGNALE = ("ok", "abweichung", "fehler", "pass", "always")
MAX_KNOTEN, MAX_KANTEN, MAX_SCHRITTE, MAX_NAME, MAX_TEXT = 200, 600, 1000, 120, 2000
ID = re.compile(r"[A-Za-z0-9_.-]{1,64}\Z")
OPERATOREN = ("gleich", "ungleich", "vorhanden", "enthaelt", "mindestens", "hoechstens", "nicht_leer")


class AblaufFehler(ValueError):
    pass


# ---- Werte und Bedingungen -------------------------------------------------------------------------------------------------------------------
def hole(ctx: object, pfad: str):
    """`a.b.0.c` aus verschachtelten Wörterbüchern und Listen; (gefunden, Wert)."""
    wert = ctx
    for teil in pfad.split("."):
        if isinstance(wert, dict) and teil in wert:
            wert = wert[teil]
        elif isinstance(wert, list) and teil.isdigit() and int(teil) < len(wert):
            wert = wert[int(teil)]
        else:
            return False, None
    return True, wert


def _passt(eintrag: object, muster: dict) -> bool:
    return isinstance(eintrag, dict) and all(k in eintrag and eintrag[k] == v for k, v in muster.items())


def bedingung(b: object, ctx: dict) -> bool:
    """Eine einzelne, strukturierte Bedingung. Unbekannte Operatoren und fehlende Pfade sind **falsch**, nie wahr."""
    if not isinstance(b, dict) or not isinstance(b.get("pfad"), str):
        raise AblaufFehler("bedingung_ungueltig")
    ops = [o for o in OPERATOREN if o in b]
    if len(ops) != 1 or set(b) - {"pfad", ops[0]}:
        raise AblaufFehler("bedingung_ungueltig")
    gefunden, wert = hole(ctx, b["pfad"])
    op = ops[0]
    if op == "vorhanden":
        return gefunden == bool(b["vorhanden"])
    if not gefunden:
        return False
    soll = b[op]
    if op == "gleich":
        return wert == soll
    if op == "ungleich":
        return wert != soll
    if op == "nicht_leer":
        return bool(wert) == bool(soll)
    if op == "enthaelt":
        if isinstance(wert, list):
            return any(_passt(e, soll) if isinstance(soll, dict) else e == soll for e in wert)
        return isinstance(wert, str) and isinstance(soll, str) and soll in wert
    if not isinstance(wert, (int, float)) or isinstance(wert, bool) or not isinstance(soll, (int, float)):
        return False
    return wert >= soll if op == "mindestens" else wert <= soll


def alle_bedingungen(liste: list, ctx: dict) -> tuple[bool, str]:
    """(erfüllt, erste nicht erfüllte als Text)."""
    for b in liste:
        if not bedingung(b, ctx):
            return False, json.dumps(b, ensure_ascii=False)[:120]
    return True, ""


def aufloesen(wert: object, ctx: dict, tiefe: int = 0):
    """`$ref` und `$suche` in Argumenten durch Werte aus dem Kontext ersetzen; ein fehlender Wert ist ein Fehler (der Knoten läuft dann nicht mit geratenen Argumenten)."""
    if tiefe > 8:
        raise AblaufFehler("argumente_zu_tief")
    if isinstance(wert, dict):
        if set(wert) == {"$ref"}:
            ok, v = hole(ctx, str(wert["$ref"]))
            if not ok:
                raise AblaufFehler(f"ref_fehlt:{wert['$ref']}"[:100])
            return v
        if set(wert) == {"$suche"}:
            s = wert["$suche"]
            if not isinstance(s, dict) or not {"pfad", "wo", "feld"} <= set(s):
                raise AblaufFehler("suche_ungueltig")
            ok, liste = hole(ctx, str(s["pfad"]))
            treffer = [e for e in liste if _passt(e, s["wo"]) and s["feld"] in e] if ok and isinstance(liste, list) else []
            if len(treffer) != 1:
                raise AblaufFehler(f"suche_{'leer' if not treffer else 'mehrdeutig'}")  # keinen Treffer zu raten ist schlimmer als anzuhalten
            return treffer[0][s["feld"]]
        return {k: aufloesen(v, ctx, tiefe + 1) for k, v in wert.items()}
    if isinstance(wert, list):
        return [aufloesen(v, ctx, tiefe + 1) for v in wert]
    return wert


def fehlende_erwartungen(erwartet, knoten: list[dict]) -> list[dict]:
    """Welche der erwarteten Knoten die frische Messung nicht (mehr) zeigt. Eine Erwartung passt, wenn ein gemessener Knoten alle genannten Felder hat (Rolle und Name gleich, Text als Teilstring von Name oder Wert, ohne Groß-/Kleinschreibung)."""
    def passt(e: dict, k: dict) -> bool:
        ziel = f"{k.get('name', '')} {k.get('wert', '')}".lower()
        return all((e[f].lower() in ziel) if f == "text" else (str(k.get(f, "")).lower() == e[f].lower()) for f in e)

    return [dict(e) for e in erwartet if not any(passt(e, k) for k in knoten if isinstance(k, dict))]


# ---- Der Ablauf selbst (Daten) --------------------------------------------------------------------------------------------------------------------
KNOTEN_FELDER = {"art", "name", "aktion", "args", "speichere", "vorher", "nachher", "fallback", "unsicherheit", "pruefe", "setze", "sekunden", "an", "text", "warte_s", "beschreibung"}


@dataclass(frozen=True)
class Ablauf:
    id: str
    version: int
    name: str
    start: str
    knoten: dict
    kanten: tuple
    max_schritte: int = 200
    beschreibung: str = ""
    urheber: str = ""
    erzeugt_ms: int = 0
    erwartet: tuple = ()  # Knoten, auf die sich der Ablauf beim Entwurf stützte: je {"rolle"?, "name"?, "text"?}; vor dem Start gegen eine frische Messung geprüft

    def zu_dict(self) -> dict:
        d = {"schema": SCHEMA, "id": self.id, "version": self.version, "name": self.name, "start": self.start, "knoten": self.knoten, "kanten": list(self.kanten), "max_schritte": self.max_schritte,
             "beschreibung": self.beschreibung, "urheber": self.urheber, "erzeugt_ms": self.erzeugt_ms}
        if self.erwartet:
            d["erwartet"] = [dict(e) for e in self.erwartet]
        return d

    @staticmethod
    def aus_dict(d: object, *, version: int | None = None, urheber: str = "", jetzt_ms: int = 0) -> "Ablauf":
        """Streng: unbekannte Felder, unbekannte Arten und Handler, hängende Kanten, ungültige Bedingungen und zu große Abläufe werden abgelehnt. Fehler tragen einen festen Code."""
        if not isinstance(d, dict):
            raise AblaufFehler("kein_wörterbuch")
        if not set(d) <= {"schema", "id", "version", "name", "start", "knoten", "kanten", "max_schritte", "beschreibung", "urheber", "erzeugt_ms", "erwartet"}:
            raise AblaufFehler("unbekannte_felder")
        if d.get("schema", SCHEMA) != SCHEMA:
            raise AblaufFehler("schema_unbekannt")
        if not isinstance(d.get("id"), str) or not ID.fullmatch(d["id"]):
            raise AblaufFehler("id_ungueltig")
        name = d.get("name", d["id"])
        if not isinstance(name, str) or not 1 <= len(name) <= MAX_NAME:
            raise AblaufFehler("name_ungueltig")
        knoten = d.get("knoten")
        if not isinstance(knoten, dict) or not 1 <= len(knoten) <= MAX_KNOTEN:
            raise AblaufFehler("knoten_ungueltig")
        for kid, k in knoten.items():
            Ablauf._knoten_pruefen(kid, k)
        start = d.get("start")
        if start not in knoten:
            raise AblaufFehler("start_unbekannt")
        kanten = d.get("kanten", [])
        if not isinstance(kanten, list) or len(kanten) > MAX_KANTEN:
            raise AblaufFehler("kanten_ungueltig")
        sauber = []
        for e in kanten:
            if not isinstance(e, dict) or set(e) - {"von", "nach", "wenn"} or e.get("von") not in knoten or e.get("nach") not in knoten or e.get("wenn", "always") not in SIGNALE:
                raise AblaufFehler("kante_ungueltig")
            wenn = e.get("wenn", "always")
            if knoten[e["von"]].get("art") == "tor" and wenn == "ok":
                wenn = "pass"  # ein Tor öffnet mit „pass“ (so kennt es die Harness); „ok“ ist dieselbe Absicht
            sauber.append({"von": e["von"], "nach": e["nach"], "wenn": wenn})
        for kid, k in knoten.items():  # `fallback` ist eine Kurzschreibweise für eine Abweichungskante
            if "fallback" in k:
                if k["fallback"] not in knoten:
                    raise AblaufFehler("fallback_unbekannt")
                if not any(e["von"] == kid and e["wenn"] == "abweichung" for e in sauber):
                    sauber.append({"von": kid, "nach": k["fallback"], "wenn": "abweichung"})
        mx = d.get("max_schritte", 200)
        if type(mx) is not int or not 1 <= mx <= MAX_SCHRITTE:
            raise AblaufFehler("max_schritte_ungueltig")
        beschr = d.get("beschreibung", "")
        if not isinstance(beschr, str) or len(beschr) > MAX_TEXT:
            raise AblaufFehler("beschreibung_ungueltig")
        v = version if version is not None else d.get("version", 1)
        if type(v) is not int or v < 1:
            raise AblaufFehler("version_ungueltig")
        erwartet = d.get("erwartet", [])
        if not isinstance(erwartet, list) or len(erwartet) > 50 or any(not isinstance(e, dict) or not e or set(e) - {"rolle", "name", "text"} or any(not isinstance(x, str) or not x or len(x) > 120 for x in e.values()) for e in erwartet):
            raise AblaufFehler("erwartet_ungueltig")
        return Ablauf(d["id"], v, name, start, json.loads(json.dumps(knoten)), tuple(sauber), mx, beschr, urheber or str(d.get("urheber", ""))[:60], jetzt_ms or int(d.get("erzeugt_ms", 0)), tuple(dict(e) for e in erwartet))

    @staticmethod
    def _knoten_pruefen(kid: object, k: object) -> None:
        if not isinstance(kid, str) or not ID.fullmatch(kid) or not isinstance(k, dict) or set(k) - KNOTEN_FELDER or k.get("art") not in ARTEN:
            raise AblaufFehler("knoten_ungueltig")
        art = k["art"]
        if art in ("beobachten", "handeln"):
            if k.get("aktion") not in AKTIONEN or not isinstance(k.get("args", {}), dict):
                raise AblaufFehler("aktion_unbekannt")
        elif art == "delegieren":
            if not isinstance(k.get("an"), str) or not isinstance(k.get("text"), str) or not 1 <= len(k["text"]) <= MAX_TEXT or not isinstance(k.get("warte_s", 60), (int, float)) or k.get("warte_s", 60) < 0:
                raise AblaufFehler("delegation_ungueltig")
        elif art == "warten":
            if not isinstance(k.get("sekunden"), (int, float)) or isinstance(k["sekunden"], bool) or not 0 <= k["sekunden"] <= 3600:
                raise AblaufFehler("warten_ungueltig")
        elif art == "zustand":
            if not isinstance(k.get("setze"), dict) or len(json.dumps(k["setze"])) > 2000:
                raise AblaufFehler("zustand_ungueltig")
        elif art in ("pruefen", "tor"):
            if not isinstance(k.get("pruefe", []), list):
                raise AblaufFehler("pruefe_ungueltig")
        for feld in ("vorher", "nachher", "pruefe"):
            if feld in k:
                if not isinstance(k[feld], list) or len(k[feld]) > 20:
                    raise AblaufFehler(f"{feld}_ungueltig")
                for b in k[feld]:
                    try:
                        bedingung(b, {})
                    except AblaufFehler:
                        raise AblaufFehler(f"{feld}_bedingung_ungueltig") from None
        if "unsicherheit" in k and (not isinstance(k["unsicherheit"], str) or len(k["unsicherheit"]) > 300):
            raise AblaufFehler("unsicherheit_ungueltig")
        if "speichere" in k and (not isinstance(k["speichere"], str) or not ID.fullmatch(k["speichere"])):
            raise AblaufFehler("speichere_ungueltig")

    def graph(self) -> HarnessGraph:
        knoten = {kid: HarnessNode(kid, ARTEN[k["art"]], str(k.get("name", kid))[:MAX_NAME], required_capabilities=frozenset({k["aktion"]}) if k.get("aktion") else frozenset())
                  for kid, k in self.knoten.items()}
        return HarnessGraph(f"{self.id}@{self.version}", self.start, knoten, tuple(HarnessEdge(e["von"], e["nach"], e["wenn"]) for e in self.kanten))


# ---- Speicher: Versionen und Durchläufe, nichts wird überschrieben --------------------------------------------------------------------------------
class AblaufSpeicher:
    def __init__(self, ordner: Path | None, uhr: Callable[[], int] = lambda: int(time.time() * 1000)):
        self.ordner = Path(ordner) if ordner else None
        self._uhr = uhr
        self._sperre = threading.RLock()
        self._abl: dict[str, dict[int, Ablauf]] = {}
        self._laeufe: dict[str, dict] = {}
        self.fehler = ""
        if self.ordner:
            self._laden()

    def _pfad(self, *teile: str) -> Path:
        return self.ordner.joinpath(*teile)

    def _laden(self) -> None:
        for datei in sorted((self.ordner / "ablaeufe").glob("*.json")) if (self.ordner / "ablaeufe").is_dir() else []:
            try:
                a = Ablauf.aus_dict(json.loads(datei.read_text(encoding="utf-8")))
                self._abl.setdefault(a.id, {})[a.version] = a
            except (OSError, ValueError):
                self.fehler = f"Ablaufdatei übersprungen: {datei.name}"
        for datei in sorted((self.ordner / "laeufe").glob("*.json")) if (self.ordner / "laeufe").is_dir() else []:
            try:
                d = json.loads(datei.read_text(encoding="utf-8"))
                if isinstance(d, dict) and isinstance(d.get("id"), str):
                    if d.get("status") in ("running", "ready"):
                        d["status"] = "unterbrochen"  # der Prozess, der ihn trug, ist weg: ehrlich so benennen, nicht als laufend ausgeben
                    self._laeufe[d["id"]] = d
            except (OSError, ValueError):
                self.fehler = f"Laufdatei übersprungen: {datei.name}"

    def _schreiben(self, pfad: Path, daten: dict) -> bool:
        try:
            pfad.parent.mkdir(parents=True, exist_ok=True)
            temp = pfad.with_suffix(".tmp")
            temp.write_text(json.dumps(daten, ensure_ascii=False), encoding="utf-8")
            temp.replace(pfad)
            return True
        except OSError as f:
            self.fehler = f"nicht gespeichert: {f!r}"[:200]
            return False

    # ---- Abläufe -------------------------------------------------------------------------------------------------------------------------------
    def speichere(self, d: dict, urheber: str) -> Ablauf:
        """Legt eine **neue Version** an (nie eine bestehende überschreiben). Fehler im Ablauf: AblaufFehler."""
        with self._sperre:
            vorhanden = self._abl.get(d.get("id") if isinstance(d, dict) else None, {})
            neu = Ablauf.aus_dict(d, version=max(vorhanden, default=0) + 1, urheber=urheber, jetzt_ms=self._uhr())
            self._abl.setdefault(neu.id, {})[neu.version] = neu
            if self.ordner:
                self._schreiben(self._pfad("ablaeufe", f"{neu.id}@{neu.version}.json"), neu.zu_dict())
            return neu

    def ablauf(self, ablauf_id: str, version: int | None = None) -> Ablauf | None:
        with self._sperre:
            v = self._abl.get(ablauf_id, {})
            return v.get(version) if version is not None else (v[max(v)] if v else None)

    def versionen(self, ablauf_id: str) -> list[int]:
        with self._sperre:
            return sorted(self._abl.get(ablauf_id, {}))

    def liste(self) -> list[dict]:
        with self._sperre:
            return [{"id": i, "name": v[max(v)].name, "version": max(v), "versionen": sorted(v), "urheber": v[max(v)].urheber} for i, v in sorted(self._abl.items())]

    # ---- Durchläufe ----------------------------------------------------------------------------------------------------------------------------
    def lauf_sichern(self, lauf_dict: dict) -> None:
        with self._sperre:
            self._laeufe[lauf_dict["id"]] = lauf_dict
            if self.ordner:
                self._schreiben(self._pfad("laeufe", f"{lauf_dict['id']}.json"), lauf_dict)

    def lauf(self, lauf_id: str) -> dict | None:
        with self._sperre:
            return self._laeufe.get(lauf_id)

    def laeufe(self, ablauf_id: str | None = None) -> list[dict]:
        with self._sperre:
            return [d for d in self._laeufe.values() if ablauf_id is None or d.get("ablauf_id") == ablauf_id]


# ---- Ein Lauf --------------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Eintrag:
    nr: int
    knoten: str
    art: str
    signal: str
    status: str
    detail: str = ""
    zeit_ms: int = 0
    simuliert: bool = False

    def zu_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class Lauf:
    id: str
    ablauf: Ablauf
    run: HarnessRun
    agent: str = ""  # terminal_id des Agenten, in dessen Namen gehandelt wird
    ctx: dict = field(default_factory=dict)
    zustand: dict = field(default_factory=dict)
    unsicherheit: list = field(default_factory=list)
    modi: tuple = ("free",)
    verlauf: list = field(default_factory=list)
    schritte: int = 0
    grund: str = ""  # warum ein Lauf angehalten hat
    eltern: str | None = None
    zweig_von: str | None = None
    gestartet_ms: int = 0
    beendet_ms: int = 0
    snapshots: dict = field(default_factory=dict)  # Name → (Kontext, Zustand, Unsicherheit, Länge des Verlaufs, Schritte) zum Zeitpunkt des Checkpoints

    @property
    def status(self) -> str:
        return self.run.status.value

    def zu_dict(self) -> dict:
        return {"id": self.id, "ablauf_id": self.ablauf.id, "ablauf_version": self.ablauf.version, "agent": self.agent, "status": self.status, "knoten": self.run.current_node_id, "modi": list(self.modi),
                "schritte": self.schritte, "grund": self.grund, "zustand": self.zustand, "unsicherheit": self.unsicherheit, "ctx": self.ctx, "verlauf": [e.zu_dict() for e in self.verlauf],
                "checkpoints": {n: {"knoten": c.node_id, "verlauf": len(self.verlauf)} for n, c in self.run.checkpoints.items()}, "eltern": self.eltern, "zweig_von": self.zweig_von,
                "gestartet_ms": self.gestartet_ms, "beendet_ms": self.beendet_ms}


def neuer_lauf(ablauf: Ablauf, agent: str, handler: frozenset[str], modi: tuple = ("free",), jetzt_ms: int = 0, lauf_id: str | None = None) -> Lauf:
    run = HarnessRun(lauf_id or f"l-{uuid.uuid4().hex[:8]}", ablauf.graph(), capabilities=frozenset(handler))
    return Lauf(run.id, ablauf, run, agent, modi=tuple(modi), gestartet_ms=jetzt_ms)


class Ausfuehrer:
    """Führt Läufe knotenweise aus. Handler kommen herein (`name → Funktion(spezifikation, kontext) → Ergebnis-Wörterbuch mit `ok`); die Modi (`ablauf_modi.Modi`) entscheiden, ob etwas wirklich geschieht."""

    def __init__(self, handler: dict[str, Callable[[dict, dict], dict]], *, modi=None, speicher: AblaufSpeicher | None = None, jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000),
                 schlafen: Callable[[float], None] = time.sleep):
        self.handler, self.modi, self.speicher, self._jetzt, self._schlafen = handler, modi, speicher, jetzt_ms, schlafen
        self._abbruch: dict[str, threading.Event] = {}
        self._sperre = threading.RLock()

    # ---- Steuern (von Daniel oder dem Agenten) --------------------------------------------------------------------------------------------------
    def starten(self, lauf: Lauf) -> None:
        lauf.run.start()
        lauf.gestartet_ms = lauf.gestartet_ms or self._jetzt()
        self._abbruch[lauf.id] = threading.Event()
        self._sichern(lauf)

    def pausieren(self, lauf: Lauf) -> bool:
        """Hält vor dem nächsten Knoten an; ein gerade laufender Handler wird nicht unterbrochen (Warten und Genehmigungen sind unterbrechbar)."""
        with self._sperre:
            if lauf.run.status != RunStatus.RUNNING:
                return False
            lauf.run.pause()
            lauf.grund = "pausiert"
            self._sichern(lauf)
            return True

    def fortsetzen(self, lauf: Lauf) -> bool:
        with self._sperre:
            if lauf.run.status != RunStatus.PAUSED:
                return False
            lauf.run.start()
            lauf.grund = ""
            self._abbruch[lauf.id] = threading.Event()
            self._sichern(lauf)
            return True

    def abbrechen(self, lauf: Lauf, grund: str = "operator") -> None:
        with self._sperre:
            if lauf.run.status in (RunStatus.COMPLETED, RunStatus.ABORTED):
                return
            lauf.run.abort(grund)
            lauf.grund = f"abgebrochen: {grund}"[:120]
            lauf.beendet_ms = self._jetzt()
            if lauf.id in self._abbruch:
                self._abbruch[lauf.id].set()
            self._sichern(lauf)

    def checkpoint(self, lauf: Lauf, name: str) -> None:
        lauf.run.checkpoint(name)
        lauf.snapshots[name] = (json.loads(json.dumps(lauf.ctx)), json.loads(json.dumps(lauf.zustand)), list(lauf.unsicherheit), len(lauf.verlauf), lauf.schritte)
        self._sichern(lauf)

    def zweig(self, lauf: Lauf, checkpoint: str, neue_id: str | None = None) -> Lauf:
        """Ein neuer Lauf ab einem Beobachtungspunkt des alten. Der alte bleibt unverändert; der neue erbt Kontext und Zustand (Kopie) bis dahin."""
        neu_run = lauf.run.fork(checkpoint, new_run_id=neue_id or f"l-{uuid.uuid4().hex[:8]}")
        ctx, zustand, unsicherheit, verlauf_n, schritte = lauf.snapshots[checkpoint]  # der Stand AM Beobachtungspunkt, nicht der heutige
        zweig = Lauf(neu_run.id, lauf.ablauf, neu_run, lauf.agent, json.loads(json.dumps(ctx)), json.loads(json.dumps(zustand)), list(unsicherheit), lauf.modi,
                     [Eintrag(**e.zu_dict()) for e in lauf.verlauf[:verlauf_n]], schritte, "", lauf.id, checkpoint, self._jetzt(), snapshots=dict(lauf.snapshots))
        self._sichern(zweig)
        return zweig

    # ---- Ausführen ----------------------------------------------------------------------------------------------------------------------------------
    def laufen(self, lauf: Lauf) -> Lauf:
        """Bis zum Ende, Anhalten oder Abbruch. Jeder Schritt prüft vorher, ob jemand gestoppt hat."""
        while lauf.run.status == RunStatus.RUNNING:
            self.schritt(lauf)
        if lauf.run.status in (RunStatus.COMPLETED, RunStatus.BLOCKED, RunStatus.ABORTED):
            lauf.beendet_ms = lauf.beendet_ms or self._jetzt()
        self._sichern(lauf)
        return lauf

    def schritt(self, lauf: Lauf) -> None:
        with self._sperre:
            if lauf.run.status != RunStatus.RUNNING:
                return
        if lauf.schritte >= lauf.ablauf.max_schritte:
            lauf.run.status = RunStatus.BLOCKED
            lauf.grund = f"max_schritte_erreicht:{lauf.ablauf.max_schritte}"
            lauf.run._trace(lauf.run.current_node_id or "", "blocked", lauf.grund)
            return
        kid = lauf.run.current_node_id
        k = lauf.ablauf.knoten[kid]
        lauf.schritte += 1
        signal, status, detail, simuliert = self._knoten_ausfuehren(lauf, kid, k)
        if "unsicherheit" in k and not simuliert and signal in ("ok", "pass") and not any(u["knoten"] == kid for u in lauf.unsicherheit):
            lauf.unsicherheit.append({"knoten": kid, "text": k["unsicherheit"]})  # an jedem Knoten, nicht nur an Handlern: was der Entwerfer als unsicher markiert hat, reist mit
        if lauf.run.status != RunStatus.RUNNING:  # jemand hat währenddessen pausiert oder abgebrochen: dieser Schritt zählt, der nächste Knoten wird nicht betreten
            lauf.verlauf.append(Eintrag(lauf.schritte, kid, k["art"], signal, status, detail, self._jetzt(), simuliert))
            self._sichern(lauf)
            return
        if signal in ("abweichung", "fehler") and not any(e["von"] == kid and e["wenn"] in (signal, "always") for e in lauf.ablauf.kanten):
            lauf.run.status = RunStatus.BLOCKED
            lauf.grund = f"{signal} ohne Fallback an {kid}: {detail}"[:200]
            lauf.run._trace(kid, "blocked", lauf.grund)
        else:
            lauf.run.step("pass" if k["art"] == "tor" else signal)
            if lauf.run.status == RunStatus.BLOCKED and not lauf.grund:
                lauf.grund = lauf.run.trace[-1].detail if lauf.run.trace else "angehalten"
        lauf.verlauf.append(Eintrag(lauf.schritte, kid, k["art"], signal, status, detail, self._jetzt(), simuliert))
        if self.modi is not None:
            self.modi.nach_schritt(lauf, lauf.verlauf[-1])
        self._sichern(lauf)

    def _knoten_ausfuehren(self, lauf: Lauf, kid: str, k: dict) -> tuple[str, str, str, bool]:
        """(Signal, Status, Detail, simuliert)."""
        art = k["art"]
        try:
            ok, was = alle_bedingungen(k.get("vorher", []), lauf.ctx)
            if not ok:
                return "abweichung", "vorher_nicht_erfuellt", was, False
            if art == "zustand":
                lauf.zustand.update(json.loads(json.dumps(k["setze"])))
                return "ok", "zustand_gesetzt", ",".join(sorted(k["setze"])), False
            if art == "warten":
                self._warten(lauf, float(k["sekunden"]))
                return "ok", "gewartet", f"{k['sekunden']} s", False
            if art == "pruefen":
                ok, was = alle_bedingungen(k.get("pruefe", []), lauf.ctx)
                return ("ok", "geprueft", "", False) if ok else ("abweichung", "pruefung_nicht_erfuellt", was, False)
            if art == "tor":
                return self._tor(lauf, kid, k)
            entscheidung = self.modi.vor_handeln(lauf, kid, k) if (self.modi is not None and art in HANDELNDE_ARTEN) else "ausfuehren"
            if entscheidung == "simulieren":
                lauf.ctx[k.get("speichere", kid)] = {"ok": None, "simuliert": True}
                return "ok", "simuliert", "Shadow: nichts ausgeführt", True
            if entscheidung == "abgelehnt":
                lauf.run.status = RunStatus.BLOCKED
                lauf.grund = f"Freigabe verweigert an {kid}" + (f" ({lauf.grund})" if lauf.grund else "")  # der genaue Grund (Zeitablauf, nein, Bereich aus) steht dabei
                lauf.run._trace(kid, "blocked", lauf.grund)
                return "abweichung", "freigabe_verweigert", kid, False
            if art == "delegieren":
                ergebnis = self._delegieren(lauf, k)
            else:
                handler = self.handler.get(k["aktion"])
                if handler is None:
                    lauf.run.status = RunStatus.BLOCKED
                    lauf.grund = f"handler_fehlt:{k['aktion']}"
                    lauf.run._trace(kid, "blocked", lauf.grund)
                    return "fehler", "handler_fehlt", k["aktion"], False
                ergebnis = handler({"aktion": k["aktion"], "args": aufloesen(k.get("args", {}), lauf.ctx), "agent": lauf.agent, "knoten": kid}, {"lauf": lauf.id})
            if not isinstance(ergebnis, dict):
                return "fehler", "ergebnis_ungueltig", type(ergebnis).__name__, False
            lauf.ctx[k.get("speichere", kid)] = json.loads(json.dumps(ergebnis, default=str))
            if isinstance(ergebnis.get("unsicherheit"), str):
                lauf.unsicherheit.append({"knoten": kid, "text": ergebnis["unsicherheit"][:300]})
            if not ergebnis.get("ok", False):
                return "abweichung", "handler_meldet_nicht_ok", str(ergebnis.get("reason") or ergebnis.get("grund") or ergebnis.get("status") or "")[:120], False
            ok, was = alle_bedingungen(k.get("nachher", []), lauf.ctx)
            if not ok:
                return "abweichung", "nachher_nicht_erfuellt", was, False
            return "ok", "ausgefuehrt", "", False
        except AblaufFehler as f:
            return "fehler", "ablauf_fehler", str(f)[:120], False
        except Exception as f:
            return "fehler", "ausnahme", repr(f)[:120], False

    def _tor(self, lauf: Lauf, kid: str, k: dict) -> tuple[str, str, str, bool]:
        ok, was = alle_bedingungen(k.get("pruefe", []), lauf.ctx)
        if not ok:
            lauf.run.status = RunStatus.BLOCKED
            lauf.grund = f"Tor {kid} nicht erfüllt: {was}"[:200]
            lauf.run._trace(kid, "blocked", lauf.grund)
            return "abweichung", "tor_nicht_erfuellt", was, False
        if self.modi is not None and not self.modi.tor_frei(lauf, kid, k):
            lauf.run.status = RunStatus.BLOCKED
            lauf.grund = f"Tor {kid}: keine Freigabe"
            lauf.run._trace(kid, "blocked", lauf.grund)
            return "abweichung", "keine_freigabe", kid, False
        return "pass", "tor_offen", "", False

    def _warten(self, lauf: Lauf, sekunden: float) -> None:
        ende = time.monotonic() + sekunden
        while time.monotonic() < ende and lauf.run.status == RunStatus.RUNNING and not self._abbruch.get(lauf.id, threading.Event()).is_set():
            self._schlafen(min(0.05, max(0.0, ende - time.monotonic())))

    def _delegieren(self, lauf: Lauf, k: dict) -> dict:
        """Ein Teilauftrag an einen anderen Agenten mit Zustand und Unsicherheit; der Handler `auftrag` übernimmt das Senden und Warten."""
        handler = self.handler.get("auftrag")
        if handler is None:
            return {"ok": False, "reason": "handler_fehlt:auftrag"}
        text = k["text"] + f"\n[Ablauf {lauf.ablauf.id}@{lauf.ablauf.version}, Lauf {lauf.id}; Zustand: {json.dumps(lauf.zustand, ensure_ascii=False)[:400]}; offene Unsicherheit: " \
                           f"{'; '.join(u['text'] for u in lauf.unsicherheit[-3:]) or 'keine'}]"
        return handler({"aktion": "auftrag", "args": {"an": k["an"], "text": text[:2000], "warte_s": k.get("warte_s", 60)}, "agent": lauf.agent}, {"lauf": lauf.id})

    def _sichern(self, lauf: Lauf) -> None:
        if self.speichern_aktiv():
            self.speicher.lauf_sichern(lauf.zu_dict())

    def speichern_aktiv(self) -> bool:
        return self.speicher is not None


def wiedergeben(speicher: AblaufSpeicher, lauf_id: str) -> list[dict]:
    """Replay: die gespeicherte Spur eines Durchlaufs — liest nur, ruft **keinen** Handler und führt nichts in einer Anwendung aus."""
    d = speicher.lauf(lauf_id)
    return [] if d is None else [dict(e, replay=True) for e in d.get("verlauf", [])]
