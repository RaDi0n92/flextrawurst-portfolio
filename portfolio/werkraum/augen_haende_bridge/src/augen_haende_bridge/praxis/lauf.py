"""Praxistest als Graph (Knoten, Kanten, Python): ein Lauf führt zwei Agenten Schritt für Schritt durch ein Szenario — freundlich, aber nicht zu umgehen.

**Leitgedanke (Daniel):** Jeder Prüfschritt muss für ihn nachvollziehbar sein. Der Handelnde sagt den Schritt **vorher in seiner Raute an**, wartet, bis man es lesen konnte, tut genau das, sagt danach, was er gesehen hat, und der andere Agent schaut zu und bestätigt oder widerspricht.

**Ein Schritt ist ein kleiner Graph** auf der vorhandenen Harness (`harness.py`):

    ansage ──▶ lesen ──▶ handeln ──▶ sehen ──▶ urteil ──▶ zuschauer ──bestätigt──▶ (nächster Schritt)
       ▲                    │                                  │
       └────Planänderung────┘                                  └──Widerspruch──▶ klären ──▶ sehen

Zusätzlich führt eine Kante „zurückgestellt“ über Schritte hinweg, die auf etwas Fehlendes warten (z. B. die Menü-Freigabe), damit der Lauf nie festhängt.

**Der Lauf glaubt keine Behauptung:** ein Knoten wird erst verlassen, wenn echte Spuren da sind (Hände-Aktionen, Bilder, Befehle im Ereignisprotokoll des Starters). Fehlt etwas, bekommt der Agent keine Strafe, sondern **einen freundlichen, genauen nächsten Schritt**. Kein Knoten blockiert den Lauf endgültig; der Lauf selbst bleibt immer weiterführbar.
Kreativer Spielraum: zu jedem Schritt gibt es eine **Kür** (freiwillig) und jederzeit eine **Entdeckung** (eigene Beobachtung), beides landet im Protokoll.
"""

from __future__ import annotations

import json
import hashlib
import re
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from ..harness import HarnessEdge, HarnessGraph, HarnessNode, HarnessRun, NodeKind
from .belege import validiere as validiere_belege
from . import hilfe

SZENARIO_STANDARD = Path(__file__).with_name("szenario_menschlich.json")
LESEZEIT_MIN_S = 4.0
LESEZEIT_PRO_ZEICHEN_S = 1 / 25  # grob: eine Zeile in Ruhe lesen
MAX_ANSAGE = 300
MIN_TEXT = 8
MAX_TEXT = 600
MAX_KLAERRUNDEN = 2
MAX_FEHLVERSUCHE = 3  # der dritte echte Fehlversuch an einem Schritt hält den Lauf an: kein Überspringen, erst die Ursache
MIN_URSACHE = 20
FEHLVERSUCH_GRUENDE = ("raute_nicht_erreichbar", "spur_fehlt", "schrittbeleg_fehlt")  # echte Hindernisse, keine Tippfehler im Befehl
URTEILE = ("ok", "anders", "fehler")
ZUSCHAUER_URTEILE = ("bestaetigt", "widerspruch")
EVIDENZ_ARTEN = ("sehen", "haende", "haende_abgelehnt", "nachricht", "weltdom", "kapsel", "seed", "loop", "raute")
KNOTEN = ("ansage", "lesen", "handeln", "sehen", "urteil", "zuschauer", "klaeren")

LOB = ("Schön, das war klar und nachvollziehbar.", "Gut gemacht — so kann Daniel mitgehen.", "Sauber. Genau so macht man das auf Augenhöhe.", "Stark, weiter im Takt.", "Das war ein runder Schritt.")


class PraxisFehler(ValueError):
    pass


# ---- Szenario und Graph ------------------------------------------------------------------------------------------------------------------------------
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
ROLLEN = ("wechselnd", "a")  # wechselnd: ungerade Schritte A, gerade B; a: A handelt immer, B schaut immer zu


def szenario_pfad(name: str) -> Path:
    """`szenario_<name>.json` neben diesem Modul; nur schlichte Namen (keine Pfade)."""
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise PraxisFehler("szenario_name_ungueltig")
    pfad = Path(__file__).with_name(f"szenario_{name}.json")
    if not pfad.is_file():
        raise PraxisFehler("szenario_unbekannt")
    return pfad


def szenarien() -> list[dict]:
    ergebnis = []
    for p in sorted(Path(__file__).parent.glob("szenario_*.json")):
        name = p.stem[len("szenario_"):]
        try:
            s = lade_szenario(p)
        except PraxisFehler:
            continue
        ergebnis.append({"name": name, "titel": s.get("titel", name), "schritte": len(s["schritte"]), "rollen": s.get("rollen", "wechselnd")})
    return ergebnis


def lade_szenario(pfad: Path | None = None) -> dict:
    try:
        s = json.loads(Path(pfad or SZENARIO_STANDARD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise PraxisFehler("szenario_unlesbar") from None
    schritte = s.get("schritte") if isinstance(s, dict) else None
    if isinstance(s, dict) and (type(s.get("contract_version", 1)) is not int or s.get("contract_version", 1) not in (1, 2)):
        raise PraxisFehler("contract_version_unbekannt")
    if isinstance(s, dict) and s.get("rollen", "wechselnd") not in ROLLEN:
        raise PraxisFehler("rollen_ungueltig")
    if not isinstance(schritte, list) or not schritte or len(schritte) > 200:
        raise PraxisFehler("szenario_ungueltig")
    for i, st in enumerate(schritte, 1):
        if not isinstance(st, dict) or type(st.get("nr")) is not int or st.get("nr") != i or any(not isinstance(st.get(k), str) or not st[k] for k in ("teil", "ziel", "titel", "pruefe", "mache", "erwarte")):
            raise PraxisFehler(f"schritt_{i}_ungueltig")
        ev = st.get("evidenz")
        if not isinstance(ev, list) or not ev or any(e not in EVIDENZ_ARTEN for e in ev):
            raise PraxisFehler(f"schritt_{i}_evidenz_ungueltig")
        if not isinstance(st.get("kuer", ""), str) or st.get("braucht", "") not in ("", "menue_freigabe"):
            raise PraxisFehler(f"schritt_{i}_ungueltig")
        if s.get("contract_version") == 2:
            try:
                validiere_belege(st.get("belege"))
            except ValueError as exc:
                raise PraxisFehler(f"schritt_{i}_{exc}") from exc
    if s.get("contract_version", 1) not in (1, 2):
        raise PraxisFehler("contract_version_unbekannt")
    return s


def kn(nr: int, art: str) -> str:
    return f"s{nr}.{art}"


def baue_graph(szenario: dict) -> HarnessGraph:
    """Die Knoten und Kanten des ganzen Szenarios. Bedingte Kanten stehen vor der „always“-Kante, damit sie bei ihrem Signal Vorrang haben."""
    n = len(szenario["schritte"])
    knoten: dict[str, HarnessNode] = {}
    kanten: list[HarnessEdge] = []
    arten = {"ansage": NodeKind.STATE, "lesen": NodeKind.STATE, "handeln": NodeKind.ACTION, "sehen": NodeKind.OBSERVATION, "urteil": NodeKind.STATE, "zuschauer": NodeKind.STATE, "klaeren": NodeKind.STATE}
    for st in szenario["schritte"]:
        i = st["nr"]
        for art in KNOTEN:
            knoten[kn(i, art)] = HarnessNode(kn(i, art), arten[art], f"Schritt {i} · {st['titel']} · {art}", metadata={"schritt": i, "art": art})
        weiter = kn(i + 1, "ansage") if i < n else "ende"
        kanten += [HarnessEdge(kn(i, "ansage"), weiter, "zurueckgestellt"), HarnessEdge(kn(i, "ansage"), kn(i, "lesen")), HarnessEdge(kn(i, "lesen"), kn(i, "handeln")),
                   HarnessEdge(kn(i, "handeln"), kn(i, "ansage"), "planaenderung"), HarnessEdge(kn(i, "handeln"), kn(i, "sehen")), HarnessEdge(kn(i, "sehen"), kn(i, "urteil")),
                   HarnessEdge(kn(i, "urteil"), kn(i, "zuschauer")), HarnessEdge(kn(i, "zuschauer"), kn(i, "klaeren"), "widerspruch"), HarnessEdge(kn(i, "zuschauer"), weiter, "bestaetigt"),
                   HarnessEdge(kn(i, "klaeren"), kn(i, "sehen"))]
    knoten["ende"] = HarnessNode("ende", NodeKind.STATE, "Geschafft", metadata={"art": "ende"})
    g = HarnessGraph(f"praxis-{szenario.get('id', 'x')}", kn(1, "ansage"), knoten, tuple(kanten))
    g.validate()
    return g


def _norm(text: str) -> str:
    return text.lower().replace("ü", "ue").replace("ä", "ae").replace("ö", "oe")


class PraxisLauf:
    def __init__(self, szenario: dict, a: str, b: str, *, namen: dict[str, str] | None = None, evidenz: Callable[[str, str, int], int] = lambda tid, art, seit_ms: 0,
                 raute: Callable[[str, str], bool | dict] = lambda tid, text: False, ledger: Callable[[dict], None] = lambda zeile: None, jetzt: Callable[[], float] = time.monotonic,
                 jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000), menue_freigabe: bool = False, ab: int = 1, lauf_id: str | None = None,
                 pruefe_belege: Callable[[object], dict] | None = None):
        if a == b:
            raise PraxisFehler("zwei_verschiedene_agenten")
        if type(ab) is not int or not 1 <= ab <= len(szenario["schritte"]):
            raise PraxisFehler("ab_ungueltig")
        self.szenario, self.a, self.b = json.loads(json.dumps(szenario)), a, b
        self.szenario_sha256 = hashlib.sha256(json.dumps(self.szenario, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.namen = {a: (namen or {}).get(a, a), b: (namen or {}).get(b, b)}
        self._evidenz, self._raute, self._ledger, self._jetzt, self._jetzt_ms = evidenz, raute, ledger, jetzt, jetzt_ms
        self.menue_freigabe = menue_freigabe
        self._pruefe_belege = pruefe_belege
        self.id = lauf_id or f"p-{uuid.uuid4().hex[:8]}"
        self.graph = baue_graph(szenario)
        self.run = HarnessRun(self.id, self.graph, current_node_id=kn(max(1, ab), "ansage"))
        self.run.start()
        self.n = len(szenario["schritte"])
        self.zeilen: list[dict] = []
        self.entdeckungen: list[dict] = []
        self.gestartet_ms = jetzt_ms()
        self.ab = ab
        self.ledger_fehler = ""
        self.fehlversuche: dict[int, int] = {}  # Schrittnummer -> echte Fehlversuche seit der letzten Ursache (überlebt „nochmal“)
        self.halt: dict | None = None  # gesetzt ab dem dritten Fehlversuch: {"nr", "grund", "seit_ms"}
        self.erinnerung: dict = {}  # ähnliche frühere Fälle aus dem Ereignisspeicher (setzt der Dienst nach einem Fehlversuch)
        self._neu_betreten()
        self._ueberspringen_wenn_noetig()

    # ---- Halt statt Überspringen ---------------------------------------------------------------------------------------------------------------
    def _halt_antwort(self) -> dict:
        h = self.halt or {}
        return {"ok": False, "reason": "halt", "halt": dict(h),
                "sage": (f"Halt an Schritt {h.get('nr')}: {MAX_FEHLVERSUCHE} Fehlversuche (zuletzt: {h.get('grund')}). Überspringen und „nicht getestet“ gibt es hier nicht. "
                         f"Suche die Ursache, behebe sie und trag sie ein: `bridge_cli.py test ursache \"…\"` (mindestens {MIN_URSACHE} Zeichen). Danach geht es am selben Schritt weiter.")}

    def _fehlversuch(self, agent: str, antwort: dict) -> dict:
        """Zählt einen echten Fehlversuch (Ledger-Zeile `fehlversuch`); beim dritten wird angehalten (Ledger-Zeile `halt`)."""
        if antwort.get("ok") or antwort.get("reason") not in FEHLVERSUCH_GRUENDE or self.knoten == "ende":
            return antwort
        nr = self.nr
        n = self.fehlversuche[nr] = self.fehlversuche.get(nr, 0) + 1
        grund = antwort["reason"]
        self._zeile({"nr": nr, "titel": self.schritt()["titel"], "status": "fehlversuch", "von": self._name(agent), "grund": grund, "versuch": n,
                     "text": f"Fehlversuch {n} von {MAX_FEHLVERSUCHE} an Schritt {nr}: {grund}"})
        antwort = {**antwort, "fehlversuche": n, "max_fehlversuche": MAX_FEHLVERSUCHE, **hilfe.naechste_handlung(antwort, self.schritt(), {"handelnder": self._name(self.handelnder()), "zuschauer": self._name(self.zuschauer_von())})}
        if n >= MAX_FEHLVERSUCHE:
            self.halt = {"nr": nr, "grund": grund, "seit_ms": self._jetzt_ms()}
            self._zeile({"nr": nr, "status": "halt", "von": self._name(agent), "grund": grund, "text": f"Halt an Schritt {nr} nach {n} Fehlversuchen ({grund})"})
            antwort.update(reason="halt", halt=dict(self.halt), sage=self._halt_antwort()["sage"])
        return antwort

    def ursache(self, agent: str, text: str) -> dict:
        """Die benannte Ursache hebt den Halt auf; der Schritt bleibt derselbe, der Zähler beginnt bei null."""
        if not self.halt:
            return {"ok": False, "reason": "kein_halt", "sage": "Es gibt keinen Halt; mach einfach mit dem Schritt weiter."}
        if not isinstance(text, str) or len(text.strip()) < MIN_URSACHE:
            return {"ok": False, "reason": "ursache_zu_kurz", "sage": f"Beschreibe die Ursache konkret (mindestens {MIN_URSACHE} Zeichen): was hat den Schritt verhindert und was hast du behoben?"}
        nr = self.halt["nr"]
        self._zeile({"nr": nr, "status": "ursache", "von": self._name(agent), "text": text.strip()[:MAX_TEXT], "grund": self.halt.get("grund", "")})
        self.fehlversuche[nr] = 0
        self.halt = None
        return {"ok": True, "sage": f"Ursache steht im Protokoll. Weiter an Schritt {nr}."}

    # ---- Orientierung ------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def knoten(self) -> str:
        return self.run.current_node_id or "ende"

    @property
    def nr(self) -> int:
        return int(self.knoten[1:].split(".")[0]) if self.knoten != "ende" else self.n + 1

    @property
    def art(self) -> str:
        return self.knoten.split(".")[1] if self.knoten != "ende" else "ende"

    def schritt(self, nr: int | None = None) -> dict:
        return self.szenario["schritte"][(nr or self.nr) - 1]

    def handelnder(self, nr: int | None = None) -> str:
        if self.szenario.get("rollen", "wechselnd") == "a":
            return self.a
        return self.a if (nr or self.nr) % 2 == 1 else self.b

    def zuschauer_von(self, nr: int | None = None) -> str:
        return self.b if self.handelnder(nr) == self.a else self.a

    def _name(self, tid: str) -> str:
        return self.namen.get(tid, tid)

    def _neu_betreten(self) -> None:
        """Ein frischer Schritt beginnt: Zustand leeren und einen Haltepunkt setzen (für „nochmal“)."""
        if self.knoten == "ende":
            if self.run.status.value == "running":
                self.run.step()
            return
        self.z = {"ansage": "", "t_ansage": 0.0, "t_ansage_ms": 0, "lese_bis": 0.0, "t_lesen_ms": 0, "getan": "", "t_getan_ms": 0, "gesehen": "", "urteil": "", "zuschauer": "", "zuschauer_urteil": "",
                  "klaerrunden": 0, "t_klaeren_ms": 0, "notizen": [], "plaene": [], "versuch_id": uuid.uuid4().hex,
                  "wiederholung": getattr(self, "z", {}).get("wiederholung", 0) if getattr(self, "z", None) and self.z.get("nr") == self.nr else 0, "nr": self.nr}
        try:
            self.run.checkpoint(f"schritt-{self.nr}")
        except RuntimeError:
            pass

    def _ueberspringen_wenn_noetig(self) -> None:
        while self.knoten != "ende" and self.art == "ansage" and self.schritt().get("braucht") == "menue_freigabe" and not self.menue_freigabe:
            st = self.schritt()
            self._zeile({"nr": st["nr"], "titel": st["titel"], "status": "zurueckgestellt", "grund": "Menü-Fenster der Bridge sind für die Hände noch nicht freigegeben (Daniels Wort für den Käfig fehlt)"})
            self.run.step("zurueckgestellt")
            self._neu_betreten()

    def _zeile(self, zeile: dict) -> None:
        zeile = {"zeit_ms": self._jetzt_ms(), "lauf_id": self.id, "versuch_id": self.z.get("versuch_id"), **zeile}
        try:
            self._ledger(zeile)
        except Exception as exc:
            self.ledger_fehler = type(exc).__name__
            raise PraxisFehler("ledger_nicht_geschrieben") from exc
        self.ledger_fehler = ""
        self.zeilen.append(zeile)

    # ---- Karte: was jetzt ----------------------------------------------------------------------------------------------------------------------------------
    def _lesezeit_rest(self) -> float:
        return max(0.0, self.z["lese_bis"] - self._jetzt())

    def karte(self, agent: str) -> dict:
        self._vor()
        if self.knoten == "ende":
            return {"ok": True, "ende": True, "ergebnis": self.abschluss(), "sage": "Danke euch beiden. Der Lauf ist beendet. Prüft die getrennte Bilanz: durchgeführt, bestätigt, Fehler, Streit und nicht getestet. Entdeckungen bleiben willkommen (`test kuer`)."}
        st, art, wer = self.schritt(), self.art, agent
        rolle = "handelnder" if wer == self.handelnder() else "zuschauer"
        k = {"ok": True, "schritt": st["nr"], "von": self.n, "teil": st["teil"], "titel": st["titel"], "ziel": st["ziel"], "du": rolle, "handelnder": self._name(self.handelnder()), "zuschauer": self._name(self.zuschauer_von()),
             "knoten": art, "pruefe": st["pruefe"], "mache": st["mache"], "erwarte": st["erwarte"], "kuer": st.get("kuer", ""),
             "ansage_vorlage": f"Schritt {st['nr']} · Prüfe: {st['pruefe']} · Mache: {st['mache']} · Erwarte: {st['erwarte']}"[:MAX_ANSAGE]}
        k["belege"] = st.get("belege", [])
        k["wartezustand"] = self.wartezustand(agent)
        k["fehlversuche"] = {"n": self.fehlversuche.get(self.nr, 0), "max": MAX_FEHLVERSUCHE, "halt": dict(self.halt) if self.halt else None}
        k["wirkungspruefung"] = st.get("wirkungspruefung", "Legacy-Szenario: nur Spurarten geprüft, keine konkrete Aktionsfolge.")
        if art == "ansage":
            k["tu_jetzt"] = ("Sag den Schritt in deiner Raute an: `bridge_cli.py test ansage \"Schritt N · Prüfe: … · Mache: … · Erwarte: …\"`. Dann bekommt Daniel Zeit zum Lesen." if rolle == "handelnder"
                             else f"{self._name(self.handelnder())} sagt den Schritt gleich in der Raute an. Schau zu — du bestätigst danach mit deinem eigenen Bild.")
        elif art == "lesen":
            k["tu_jetzt"] = f"Noch {self._lesezeit_rest():.0f} Sekunden: lass Daniel in Ruhe lesen, dann geht es los."
        elif art == "handeln":
            k["tu_jetzt"] = ("Jetzt bist du dran: führe den Schritt genau so aus, wie angesagt (Zeiger, Klicks, Tasten). Danach: `bridge_cli.py test getan \"was ich getan habe\"`." if rolle == "handelnder"
                             else "Schau aufmerksam zu; deine Aufgabe kommt gleich.")
            if rolle == "zuschauer" and any(c.get("role") == "zuschauer" for c in st.get("belege", [])):
                k["tu_jetzt"] = "Dieser Schritt braucht auch deine Handlung: stimmt sie im Chat ab und erfülle deine Belege aus der Karte vor `test getan`. Danach folgt dein eigener Bildvergleich."
        elif art == "sehen":
            k["tu_jetzt"] = ("Hol ein neues Bild (`see`) und sag, was du siehst: `bridge_cli.py test gesehen \"…\" ok|anders|fehler`." if rolle == "handelnder" else "Warte, bis die Beobachtung da ist; dann bestätigst du.")
        elif art == "zuschauer":
            k["tu_jetzt"] = (f"Du bist dran: hol dein eigenes Bild (`see`) und sag, was du siehst: `bridge_cli.py test zuschauer \"…\" bestaetigt|widerspruch`." if rolle == "zuschauer"
                             else f"Gleich bestätigt {self._name(self.zuschauer_von())}.")
        if art == "ansage" and rolle == "handelnder":
            k["vorher_pruefen"] = hilfe.ziel_hinweis(st["ziel"])
        still = hilfe.stillstand(k["wartezustand"]["seit_s"], art, rolle, self._name(self.handelnder()))
        if still and not self.halt:
            k["stillstand"] = still
        if self.erinnerung.get("nr") == self.nr and self.erinnerung.get("faelle"):
            k["erinnerung"] = self.erinnerung
        if self.halt:  # im Halt gilt nur die Ursache, was auch immer der Knoten sonst verlangt
            k["tu_jetzt"] = self._halt_antwort()["sage"]
        return k

    def ziel_gewechselt(self, aktuell: dict[str, str | None]) -> dict | None:
        """Das Ziel wird bei der Ansage festgehalten (die Belege tragen es). Hat sich ein Ziel danach geändert, gilt der Versuch nicht mehr: das ist **kein Fehlversuch**,
        sondern die Antwort „sag neu an“ mit dem genauen Befehl. `aktuell`: Agent -> Ziel-Kennung jetzt. Keine Ansage gemacht oder nichts festgehalten: kein Befund."""
        fest = self.z.get("targets") or {}
        if self.knoten == "ende" or not self.z.get("t_ansage_ms") or not fest or self.schritt().get("aendert_ziel"):
            return None  # (`aendert_ziel`: der Schritt besteht selbst im Binden eines Fensters)
        diff = {t: (fest.get(t), aktuell.get(t)) for t in (self.a, self.b) if fest.get(t) != aktuell.get(t)}
        if not diff:
            return None
        zeilen = "; ".join(f"{self._name(t)}: {alt or 'ungebunden'} → {neu or 'ungebunden'}" for t, (alt, neu) in diff.items())
        return {"ok": False, "reason": "ziel_gewechselt", "ziele": {self._name(t): {"bei_ansage": alt, "jetzt": neu} for t, (alt, neu) in diff.items()},
                "klasse": hilfe.KLASSEN["ziel_gewechselt"],
                "next": {"satz": f"Ziel seit der Ansage geändert ({zeilen}). Die Belege tragen das alte Ziel, darum gilt dieser Versuch nicht (kein Fehlversuch). Beide an das Ziel von Schritt {self.nr} binden, dann `test nochmal` und neu ansagen.",
                         "befehl": "bridge_cli.py test nochmal", "ziel": self.schritt()["ziel"]},
                "sage": f"Dein Ziel hat sich seit der Ansage geändert ({zeilen}). Das ist kein Fehlversuch: Sag den Schritt mit dem jetzigen Ziel neu an (`test nochmal`, dann `test ansage`)."}

    def wartezustand(self, agent: str) -> dict:
        """Worauf wartet `agent` gerade — und wer wartet auf ihn. Die Zeit zählt ab der ersten Beobachtung des Knotens."""
        if self.knoten == "ende":
            return {"wartet": False, "worauf": "", "wer": "", "seit_s": 0, "auf_dich": []}
        marke = (self.knoten, self.z.get("versuch_id"))
        if getattr(self, "_seit_marke", None) != marke:
            self._seit_marke, self._seit_s = marke, self._jetzt()
        handelnd, zuschauend = self.handelnder(), self.zuschauer_von()
        wer_wartet: dict[str, tuple[str, str]] = {}  # tid -> (worauf, auf wen)
        art = self.art
        if art == "ansage":
            wer_wartet[zuschauend] = ("die Ansage des Schritts in der Raute", handelnd)
        elif art == "lesen":
            wer_wartet[handelnd] = ("Daniels Lesezeit", "")
            wer_wartet[zuschauend] = ("Daniels Lesezeit", "")
        elif art == "handeln":
            wer_wartet[zuschauend] = ("die Handlung", handelnd)
        elif art in ("sehen", "urteil"):
            wer_wartet[zuschauend] = ("das Urteil mit eigenem frischem Bild", handelnd)
        elif art == "zuschauer":
            wer_wartet[handelnd] = ("die Bestätigung mit eigenem frischem Bild", zuschauend)
        elif art == "klaeren":
            wer_wartet[handelnd] = ("die Klärung", zuschauend)
            wer_wartet[zuschauend] = ("die Klärung", handelnd)
        worauf, wer = wer_wartet.get(agent, ("", ""))
        return {"wartet": bool(worauf), "worauf": worauf, "wer": self._name(wer) if wer else "", "seit_s": round(max(0.0, self._jetzt() - self._seit_s)),
                "auf_dich": [self._name(t) for t, (_w, auf) in wer_wartet.items() if auf == agent]}

    # ---- Fortschritt prüfen ---------------------------------------------------------------------------------------------------------------------------------
    def _vor(self) -> None:
        """Knoten, die nur auf Zeit oder Klärung warten, laufen von selbst weiter."""
        if self.knoten == "ende":
            return
        if self.art == "lesen" and self._jetzt() >= self.z["lese_bis"]:
            self.z["t_lesen_ms"] = self._jetzt_ms()
            self.run.step("always")
        if self.art == "klaeren":
            self.run.step("always")
        if self.art == "urteil":
            self.run.step("always")

    def _nicht_dran(self, agent: str, wer: str, was: str) -> dict:
        return {"ok": False, "reason": "nicht_dein_zug", "sage": f"Gerade ist {self._name(wer)} dran ({was}). Du schaust zu und bist gleich wieder an der Reihe — dein Bild zählt später."}

    def _falscher_knoten(self, erwartet: str) -> dict:
        hinweis = {"ansage": "erst die Ansage in der Raute", "lesen": f"noch {self._lesezeit_rest():.0f} Sekunden Lesezeit für Daniel", "handeln": "erst handeln, dann berichten", "sehen": "erst hinsehen, dann urteilen",
                   "zuschauer": "der Zuschauer ist an der Reihe", "ende": "alles ist durch"}.get(self.art, "")
        return {"ok": False, "reason": f"jetzt_{self.art}", "sage": f"Fast — gerade steht „{self.art}“ an ({hinweis}). Mit `bridge_cli.py test karte` siehst du, was als Nächstes kommt.", "karte_knoten": self.art}

    def _seit_blick(self) -> int:
        """Ab wann ein Bild als „danach“ zählt: nach dem Handeln — außer der Schritt besteht selbst aus Hinsehen, dann zählt das Bild seit der Ansage."""
        basis = self.z["t_ansage_ms"] if "sehen" in self.schritt().get("evidenz", []) else (self.z["t_getan_ms"] or self.z["t_ansage_ms"])
        return max(basis, self.z["t_klaeren_ms"])

    def _evidenz_fehlt(self, agent: str, arten: list[str], seit_ms: int) -> list[str]:
        return [a for a in arten if self._evidenz(agent, a, seit_ms) < 1]

    # ---- Befehle ----------------------------------------------------------------------------------------------------------------------------------------------------
    def ansage(self, agent: str, text: str) -> dict:
        self._vor()
        if self.halt:
            return self._halt_antwort()
        if self.knoten == "ende":
            return self._falscher_knoten("ansage")
        if self.art != "ansage":
            return self._falscher_knoten("ansage")
        if agent != self.handelnder():
            return self._nicht_dran(agent, self.handelnder(), "die Ansage")
        text = text.strip() if isinstance(text, str) else ""
        n = _norm(text)
        fehlt = [m for m, w in (("Schritt " + str(self.nr), f"schritt {self.nr}"), ("Prüfe:", "pruefe:"), ("Mache:", "mache:"), ("Erwarte:", "erwarte:")) if w not in n]
        if fehlt or not MIN_TEXT <= len(text) <= MAX_ANSAGE:
            return {"ok": False, "reason": "ansage_unvollstaendig", "fehlt": fehlt, "sage": (f"Fast! Eine Ansage braucht {', '.join(fehlt) or 'eine passende Länge (bis 300 Zeichen)'}. "
                                                                                          f"Eine fertige Vorlage: {self.karte(agent)['ansage_vorlage']}")}
        quittung = self._raute(agent, text)
        if not (quittung is True or isinstance(quittung, dict) and quittung.get("ok") is True):
            return self._fehlversuch(agent, {"ok": False, "reason": "raute_nicht_erreichbar", "quittung": quittung,
                                             "sage": "Der Körper hat das Tippen nicht bestätigt. Prüfe Hände, Not-Aus, Fokus und Verbindung; erst danach erneut ansagen."})
        # The body ACK is retained in the run state and the raw capsule
        # protocol.  It is not a second visible step row: the human ledger
        # contains one final row per attempted step.
        self.z.update(ansage=text, ansage_quittung=quittung, t_ansage=self._jetzt(), t_ansage_ms=self._jetzt_ms(), lese_bis=self._jetzt() + max(LESEZEIT_MIN_S, len(text) * LESEZEIT_PRO_ZEICHEN_S))
        self.run.step("always")
        return {"ok": True, "lesezeit_s": round(self.z["lese_bis"] - self._jetzt(), 1), "sage": f"Der Körper hat das Tippen bestätigt. Warte {self.z['lese_bis'] - self._jetzt():.0f} Sekunden, damit Daniel mitlesen kann — danach handelst du genau so."}

    def planaenderung(self, agent: str, text: str) -> dict:
        self._vor()
        if self.halt:
            return self._halt_antwort()
        if self.art not in ("handeln", "lesen") or agent != self.handelnder():
            return self._falscher_knoten("handeln")
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Sag in einem Satz, was sich ändert und warum — dann sagst du den Schritt neu an."}
        self.z["plaene"].append(text.strip()[:MAX_TEXT])
        plaene = list(self.z["plaene"])
        self.run.current_node_id = kn(self.nr, "handeln")
        self.run.step("planaenderung")
        self._neu_betreten()
        self.z["plaene"] = plaene
        return {"ok": True, "sage": "Planänderung notiert. Sag den Schritt bitte neu an (`test ansage`), damit Daniel wieder mitkommt — mit „Planänderung:“ am Anfang geht es schneller."}

    def getan(self, agent: str, text: str) -> dict:
        self._vor()
        if self.halt:
            return self._halt_antwort()
        if self.art != "handeln":
            return self._falscher_knoten("handeln")
        if agent != self.handelnder():
            return self._nicht_dran(agent, self.handelnder(), "das Handeln")
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Beschreibe in ein, zwei Sätzen, was du getan hast (z. B. „Zeiger auf die Schaltfläche, einmal geklickt“)."}
        st = self.schritt()
        fehlt = self._evidenz_fehlt(agent, st.get("evidenz", []), self.z["t_ansage_ms"])
        if fehlt:
            wo = {"haende": "eine Aktion deiner Hände (klick, tippe, taste, ziehe …)", "haende_abgelehnt": "einen abgelehnten Versuch (z. B. Klick außerhalb) im Protokoll", "sehen": "ein Bild (`see`)", "nachricht": "eine Nachricht",
                  "weltdom": "einen WorldDOM-Befehl", "kapsel": "einen Kapsel-Befehl", "seed": "einen Seed", "loop": "einen Loop", "raute": "eine Raute-Eingabe"}
            return self._fehlversuch(agent, {"ok": False, "reason": "spur_fehlt", "fehlt": fehlt, "sage": (f"Ich sehe im Protokoll noch {' und '.join(wo[f] for f in fehlt)} seit deiner Ansage — "
                                                                                                            f"dabei kann Daniel dir noch nicht zuschauen. Führe den Schritt jetzt aus: {st['mache']}. Danach melde dich hier.")})
        if self.szenario.get("contract_version") == 2:
            proof = self._pruefe_belege(self) if self._pruefe_belege else {"ok": False, "missing": ["belegpruefer_fehlt"]}
            self.z["belegpruefung"] = proof
            if not proof.get("ok"):
                return self._fehlversuch(agent, {"ok": False, "reason": "schrittbeleg_fehlt", "belege": proof,
                                                 "sage": "Die konkrete Aktionsfolge ist noch nicht belegt. Prüfe den fehlenden Beleg in der Karte; eine beliebige Spur genügt nicht."})
        self.z.update(getan=text.strip()[:MAX_TEXT], t_getan_ms=self._jetzt_ms())
        self.run.step("always")
        return {"ok": True, "sage": "Das sehe ich im Protokoll — gut. Jetzt hinsehen: hol ein neues Bild (`see`) und sag, was du siehst."}

    def gesehen(self, agent: str, text: str, urteil: str) -> dict:
        self._vor()
        if self.halt:
            return self._halt_antwort()
        if self.art != "sehen":
            return self._falscher_knoten("sehen")
        if agent != self.handelnder():
            return self._nicht_dran(agent, self.handelnder(), "das Hinsehen")
        if urteil not in URTEILE:
            return {"ok": False, "reason": "urteil_ungueltig", "sage": "Das Urteil ist ein Wort: ok, anders (als erwartet) oder fehler."}
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Beschreibe, was du auf dem Bild wirklich siehst — nicht, was du erwartet hast."}
        if self._evidenz_fehlt(agent, ["sehen"], self._seit_blick()):
            return self._fehlversuch(agent, {"ok": False, "reason": "spur_fehlt", "fehlt": ["sehen"], "sage": "Ich sehe noch kein neues Bild von dir seit dem Handeln. Hol erst eins (`bridge_cli.py see`), schau hin und berichte dann — so wie Daniel es täte."})
        self.z.update(gesehen=text.strip()[:MAX_TEXT], urteil=urteil)
        # In der Raute steht nur die Ansage vorher (was auffällt), kein Fazit danach. Das Urteil steht im Ledger.
        self.run.step("always")  # sehen → urteil
        self.run.step("always")  # urteil → zuschauer
        return {"ok": True, "sage": f"Danke. Jetzt schaut {self._name(self.zuschauer_von())} auf sein eigenes Bild und bestätigt oder widerspricht."}

    def zuschauer(self, agent: str, text: str, urteil: str) -> dict:
        self._vor()
        if self.halt:
            return self._halt_antwort()
        if self.art != "zuschauer":
            return self._falscher_knoten("zuschauer")
        if agent != self.zuschauer_von():
            return {"ok": False, "reason": "nicht_dein_zug", "sage": f"Die Bestätigung gehört {self._name(self.zuschauer_von())}: sie oder er schaut auf das eigene Bild und urteilt."}
        if urteil not in ZUSCHAUER_URTEILE:
            return {"ok": False, "reason": "urteil_ungueltig", "sage": "Das Urteil ist ein Wort: bestaetigt oder widerspruch."}
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Sag, was du auf deinem eigenen Bild siehst (ein, zwei Sätze)."}
        if self._evidenz_fehlt(agent, ["sehen"], self._seit_blick()):
            return self._fehlversuch(agent, {"ok": False, "reason": "spur_fehlt", "fehlt": ["sehen"], "sage": "Hol erst ein eigenes Bild (`bridge_cli.py see`) — eine Bestätigung ohne eigenen Blick zählt nicht."})
        self.z.update(zuschauer=text.strip()[:MAX_TEXT], zuschauer_urteil=urteil)
        nr, st = self.nr, self.schritt()
        if urteil == "widerspruch" and self.z["klaerrunden"] < MAX_KLAERRUNDEN:
            self.z["klaerrunden"] += 1
            self.z["t_klaeren_ms"] = self._jetzt_ms() + 1
            self.run.step("widerspruch")  # → klären
            self._vor()  # klären → sehen
            return {"ok": True, "sage": f"Danke fürs ehrliche Hinsehen. Klärt es kurz im Chat; {self._name(self.handelnder())} schaut noch einmal hin (`test gesehen`)."}
        streit = urteil == "widerspruch"
        self._zeile({"nr": nr, "titel": st["titel"], "status": "offen_streit" if streit else ("ok" if self.z["urteil"] == "ok" else self.z["urteil"]), "handelnder": self._name(self.handelnder()),
                     "zuschauer": self._name(agent), "ansage": self.z["ansage"], "getan": self.z["getan"], "gesehen": self.z["gesehen"], "urteil": self.z["urteil"], "zuschauer_text": self.z["zuschauer"],
                     "zuschauer_urteil": urteil, "klaerrunden": self.z["klaerrunden"], "plaene": self.z["plaene"], "notizen": self.z["notizen"], "wiederholung": self.z["wiederholung"],
                     "ansage_quittung": self.z.get("ansage_quittung"),
                     "belegpruefung": self.z.get("belegpruefung"), "wirkungsbeleg": "zwei_agentenurteile"})
        self.run.step("bestaetigt")
        self._neu_betreten()
        self._ueberspringen_wenn_noetig()
        lob = "Beobachtung und Gegenurteil sind protokolliert."
        if self.knoten == "ende":
            return {"ok": True, "ende": True, "ergebnis": self.abschluss(), "sage": f"Danke euch beiden. {lob} Der Lauf ist beendet; die Bilanz nennt auch Fehler und nicht getestete Schritte."}
        return {"ok": True, "sage": f"{lob} Weiter mit Schritt {self.nr}: {self.schritt()['titel']} — {self._name(self.handelnder())} sagt ihn an."}

    def nochmal(self, agent: str) -> dict:
        """Den aktuellen Schritt von vorn: der Verlauf bleibt erhalten (Zweig der Harness), der Zustand des Schritts beginnt neu."""
        if self.halt:
            return self._halt_antwort()
        if self.knoten == "ende":
            return self._falscher_knoten("ansage")
        if agent != self.handelnder():
            return self._nicht_dran(agent, self.handelnder(), "der Neustart des Schritts")
        nr, wdh = self.nr, self.z["wiederholung"] + 1
        zweig = self.run.fork(f"schritt-{nr}", new_run_id=f"{self.id}-w{wdh}")
        zweig.start()
        self.run = zweig
        self._neu_betreten()
        self.z["wiederholung"] = wdh
        return {"ok": True, "sage": f"Gern, Schritt {nr} noch einmal von vorn. Der erste Versuch bleibt im Verlauf stehen. Sag ihn neu an."}

    def nicht_getestet(self, agent: str, grund: str) -> dict:
        if self.halt:
            return self._halt_antwort()  # kein Überspringen im Halt
        if self.knoten == "ende" or agent != self.handelnder():
            return {"ok": False, "reason": "nicht_dein_zug"}
        if not (self.schritt().get("braucht") == "menue_freigabe" and not self.menue_freigabe):
            return {"ok": False, "reason": "kein_ueberspringen",
                    "sage": ("Schritte werden nicht übersprungen. Wenn etwas nicht klappt: den genauen Grund in der Raute sagen, die Ursache suchen und beheben, "
                             "den Schritt mit `test nochmal` wiederholen. Nach dem dritten Fehlversuch hält der Lauf an (`test ursache`). Zurückstellen gibt es nur für Schritte, "
                             "die auf Daniels Freigabe der Bridge-Menüs warten.")}
        if not isinstance(grund, str) or len(grund.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "grund_fehlt"}
        self._zeile({"nr": self.nr, "titel": self.schritt()["titel"], "status": "zurueckgestellt", "grund": grund.strip()[:MAX_TEXT]})
        # Explicitly abandoned attempt; never counted as a successful action or proof.
        self.run.current_node_id = kn(self.nr, "ansage")
        self.run.step("zurueckgestellt")
        self._neu_betreten()
        self._ueberspringen_wenn_noetig()
        return {"ok": True, "sage": "Als nicht getestet protokolliert; kein PASS. Die nächste Karte zeigt den weiteren Schritt.", "ergebnis": self.abschluss()}

    def kuer(self, agent: str, text: str) -> dict:
        """Freiwillig und kreativ: eine Kür-Idee ausprobiert oder eine eigene Entdeckung. Landet im Protokoll, nie als Pflicht."""
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Erzähl in einem Satz, was dir aufgefallen ist."}
        e = {"zeit_ms": self._jetzt_ms(), "von": self._name(agent), "schritt": self.nr if self.knoten != "ende" else self.n, "text": text.strip()[:MAX_TEXT]}
        self.entdeckungen.append(e)
        if self.knoten != "ende" and getattr(self, "z", None):
            self.z["notizen"].append(f"{e['von']}: {e['text']}")
        self._zeile({"nr": e["schritt"], "status": "entdeckung", "von": e["von"], "text": e["text"]})
        return {"ok": True, "sage": "Gute Beobachtung — die steht jetzt im Protokoll. Genau dafür ist Platz."}

    def abschluss(self) -> dict:
        letzte = {z["nr"]: z["status"] for z in self.zeilen if z.get("status") in ("ok", "anders", "fehler", "offen_streit", "zurueckgestellt")}
        gruppen = {s: sorted(n for n, v in letzte.items() if v == s) for s in ("ok", "anders", "fehler", "offen_streit", "zurueckgestellt")}
        ungetestet = sorted(set(range(1, self.n + 1)) - {n for n, s in letzte.items() if s != "zurueckgestellt"})
        status = "ABORTED" if self.run.status.value == "aborted" else ("RUNNING" if self.knoten != "ende" else ("INCOMPLETE_WITH_DEFERRED" if ungetestet else ("COMPLETE_WITH_FINDINGS" if any(gruppen[s] for s in ("anders", "fehler", "offen_streit")) else "COMPLETE")))
        return {"status": status, "bestaetigt": gruppen["ok"], "anders": gruppen["anders"], "fehler": gruppen["fehler"],
                "offen_streit": gruppen["offen_streit"], "nicht_getestet": ungetestet,
                "beweisgrenze": "Maschinelle Aktionsspuren plus zwei Agentenurteile; keine native Produktabnahme."}

    def status(self) -> dict:
        self._vor()
        return {"id": self.id, "schritt": min(self.nr, self.n), "von": self.n, "knoten": self.art, "handelnder": self._name(self.handelnder()) if self.knoten != "ende" else "",
                "fertig": [z["nr"] for z in self.zeilen if z.get("status") in ("ok", "anders", "fehler", "offen_streit")], "zurueckgestellt": [z["nr"] for z in self.zeilen if z.get("status") == "zurueckgestellt"],
                "entdeckungen": len(self.entdeckungen), "harness": self.run.status.value, "trace": len(self.run.trace),
                "ergebnis": self.abschluss(), "ledger_fehler": self.ledger_fehler, "szenario_sha256": self.szenario_sha256}

    def checkpoint(self) -> dict:
        """Recovery evidence only. Restart never silently resumes a physical action."""
        return {"id": self.id, "a": self.a, "b": self.b, "szenario": self.szenario, "szenario_sha256": self.szenario_sha256,
                "knoten": self.knoten, "zustand": self.z, "zeilen": self.zeilen, "entdeckungen": self.entdeckungen,
                "ergebnis": self.abschluss(), "recovery": "NEW_ATTEMPT_REQUIRED_AFTER_RESTART"}
