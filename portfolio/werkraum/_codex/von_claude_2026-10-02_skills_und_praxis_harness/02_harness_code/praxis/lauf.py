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
import re
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from ..harness import HarnessEdge, HarnessGraph, HarnessNode, HarnessRun, NodeKind

SZENARIO_STANDARD = Path(__file__).with_name("szenario_menschlich.json")
LESEZEIT_MIN_S = 4.0
LESEZEIT_PRO_ZEICHEN_S = 1 / 25  # grob: eine Zeile in Ruhe lesen
MAX_ANSAGE = 300
MIN_TEXT = 8
MAX_TEXT = 600
MAX_KLAERRUNDEN = 2
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
    if isinstance(s, dict) and s.get("rollen", "wechselnd") not in ROLLEN:
        raise PraxisFehler("rollen_ungueltig")
    if not isinstance(schritte, list) or not schritte or len(schritte) > 200:
        raise PraxisFehler("szenario_ungueltig")
    for i, st in enumerate(schritte, 1):
        if not isinstance(st, dict) or st.get("nr") != i or any(not isinstance(st.get(k), str) or not st[k] for k in ("teil", "ziel", "titel", "pruefe", "mache", "erwarte")):
            raise PraxisFehler(f"schritt_{i}_ungueltig")
        ev = st.get("evidenz", [])
        if not isinstance(ev, list) or any(e not in EVIDENZ_ARTEN for e in ev):
            raise PraxisFehler(f"schritt_{i}_evidenz_ungueltig")
        if not isinstance(st.get("kuer", ""), str) or not isinstance(st.get("braucht", ""), str):
            raise PraxisFehler(f"schritt_{i}_ungueltig")
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
                 raute: Callable[[str, str], bool] = lambda tid, text: True, ledger: Callable[[dict], None] = lambda zeile: None, jetzt: Callable[[], float] = time.monotonic,
                 jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000), menue_freigabe: bool = False, ab: int = 1, lauf_id: str | None = None):
        if a == b:
            raise PraxisFehler("zwei_verschiedene_agenten")
        self.szenario, self.a, self.b = szenario, a, b
        self.namen = {a: (namen or {}).get(a, a), b: (namen or {}).get(b, b)}
        self._evidenz, self._raute, self._ledger, self._jetzt, self._jetzt_ms = evidenz, raute, ledger, jetzt, jetzt_ms
        self.menue_freigabe = menue_freigabe
        self.id = lauf_id or f"p-{uuid.uuid4().hex[:8]}"
        self.graph = baue_graph(szenario)
        self.run = HarnessRun(self.id, self.graph, current_node_id=kn(max(1, ab), "ansage"))
        self.run.start()
        self.n = len(szenario["schritte"])
        self.zeilen: list[dict] = []
        self.entdeckungen: list[dict] = []
        self.gestartet_ms = jetzt_ms()
        self._neu_betreten()
        self._ueberspringen_wenn_noetig()

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
            return
        self.z = {"ansage": "", "t_ansage": 0.0, "t_ansage_ms": 0, "lese_bis": 0.0, "t_lesen_ms": 0, "getan": "", "t_getan_ms": 0, "gesehen": "", "urteil": "", "zuschauer": "", "zuschauer_urteil": "",
                  "klaerrunden": 0, "notizen": [], "plaene": [], "wiederholung": getattr(self, "z", {}).get("wiederholung", 0) if getattr(self, "z", None) and self.z.get("nr") == self.nr else 0, "nr": self.nr}
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
        zeile = {"zeit_ms": self._jetzt_ms(), **zeile}
        self.zeilen.append(zeile)
        try:
            self._ledger(zeile)
        except Exception:
            pass

    # ---- Karte: was jetzt ----------------------------------------------------------------------------------------------------------------------------------
    def _lesezeit_rest(self) -> float:
        return max(0.0, self.z["lese_bis"] - self._jetzt())

    def karte(self, agent: str) -> dict:
        self._vor()
        if self.knoten == "ende":
            return {"ok": True, "ende": True, "sage": "Alle Schritte sind durch. Danke euch beiden — schreibt jetzt jeder, wo es sich wie für einen Menschen anfühlte und wo nicht (mit „test entdeckung“)."}
        st, art, wer = self.schritt(), self.art, agent
        rolle = "handelnder" if wer == self.handelnder() else "zuschauer"
        k = {"ok": True, "schritt": st["nr"], "von": self.n, "teil": st["teil"], "titel": st["titel"], "ziel": st["ziel"], "du": rolle, "handelnder": self._name(self.handelnder()), "zuschauer": self._name(self.zuschauer_von()),
             "knoten": art, "pruefe": st["pruefe"], "mache": st["mache"], "erwarte": st["erwarte"], "kuer": st.get("kuer", ""),
             "ansage_vorlage": f"Schritt {st['nr']} · Prüfe: {st['pruefe']} · Mache: {st['mache']} · Erwarte: {st['erwarte']}"[:MAX_ANSAGE]}
        if art == "ansage":
            k["tu_jetzt"] = ("Sag den Schritt in deiner Raute an: `bridge_cli.py test ansage \"Schritt N · Prüfe: … · Mache: … · Erwarte: …\"`. Dann bekommt Daniel Zeit zum Lesen." if rolle == "handelnder"
                             else f"{self._name(self.handelnder())} sagt den Schritt gleich in der Raute an. Schau zu — du bestätigst danach mit deinem eigenen Bild.")
        elif art == "lesen":
            k["tu_jetzt"] = f"Noch {self._lesezeit_rest():.0f} Sekunden: lass Daniel in Ruhe lesen, dann geht es los."
        elif art == "handeln":
            k["tu_jetzt"] = ("Jetzt bist du dran: führe den Schritt genau so aus, wie angesagt (Zeiger, Klicks, Tasten). Danach: `bridge_cli.py test getan \"was ich getan habe\"`." if rolle == "handelnder"
                             else "Schau aufmerksam zu; deine Aufgabe kommt gleich.")
        elif art == "sehen":
            k["tu_jetzt"] = ("Hol ein neues Bild (`see`) und sag, was du siehst: `bridge_cli.py test gesehen \"…\" ok|anders|fehler`." if rolle == "handelnder" else "Warte, bis die Beobachtung da ist; dann bestätigst du.")
        elif art == "zuschauer":
            k["tu_jetzt"] = (f"Du bist dran: hol dein eigenes Bild (`see`) und sag, was du siehst: `bridge_cli.py test zuschauer \"…\" bestaetigt|widerspruch`." if rolle == "zuschauer"
                             else f"Gleich bestätigt {self._name(self.zuschauer_von())}.")
        return k

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
        return self.z["t_ansage_ms"] if "sehen" in self.schritt().get("evidenz", []) else (self.z["t_getan_ms"] or self.z["t_ansage_ms"])

    def _evidenz_fehlt(self, agent: str, arten: list[str], seit_ms: int) -> list[str]:
        return [a for a in arten if self._evidenz(agent, a, seit_ms) < 1]

    # ---- Befehle ----------------------------------------------------------------------------------------------------------------------------------------------------
    def ansage(self, agent: str, text: str) -> dict:
        self._vor()
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
        if not self._raute(agent, text):
            return {"ok": False, "reason": "raute_nicht_erreichbar", "sage": "Die Raute hat die Ansage nicht angenommen (Körper offline?). Prüfe mit `bridge_cli.py agenten`, ob dein Körper verbunden ist — dann nochmal."}
        self.z.update(ansage=text, t_ansage=self._jetzt(), t_ansage_ms=self._jetzt_ms(), lese_bis=self._jetzt() + max(LESEZEIT_MIN_S, len(text) * LESEZEIT_PRO_ZEICHEN_S))
        self.run.step("always")
        return {"ok": True, "lesezeit_s": round(self.z["lese_bis"] - self._jetzt(), 1), "sage": f"Ansage steht in deiner Raute. Warte {self.z['lese_bis'] - self._jetzt():.0f} Sekunden, damit Daniel mitlesen kann — danach handelst du genau so."}

    def planaenderung(self, agent: str, text: str) -> dict:
        self._vor()
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
            return {"ok": False, "reason": "spur_fehlt", "fehlt": fehlt, "sage": (f"Ich sehe im Protokoll noch {' und '.join(wo[f] for f in fehlt)} seit deiner Ansage — "
                                                                              f"dabei kann Daniel dir noch nicht zuschauen. Führe den Schritt jetzt aus: {st['mache']}. Danach melde dich hier.")}
        self.z.update(getan=text.strip()[:MAX_TEXT], t_getan_ms=self._jetzt_ms())
        self.run.step("always")
        return {"ok": True, "sage": "Das sehe ich im Protokoll — gut. Jetzt hinsehen: hol ein neues Bild (`see`) und sag, was du siehst."}

    def gesehen(self, agent: str, text: str, urteil: str) -> dict:
        self._vor()
        if self.art != "sehen":
            return self._falscher_knoten("sehen")
        if agent != self.handelnder():
            return self._nicht_dran(agent, self.handelnder(), "das Hinsehen")
        if urteil not in URTEILE:
            return {"ok": False, "reason": "urteil_ungueltig", "sage": "Das Urteil ist ein Wort: ok, anders (als erwartet) oder fehler."}
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Beschreibe, was du auf dem Bild wirklich siehst — nicht, was du erwartet hast."}
        if self._evidenz_fehlt(agent, ["sehen"], self._seit_blick()):
            return {"ok": False, "reason": "spur_fehlt", "fehlt": ["sehen"], "sage": "Ich sehe noch kein neues Bild von dir seit dem Handeln. Hol erst eins (`bridge_cli.py see`), schau hin und berichte dann — so wie Daniel es täte."}
        self.z.update(gesehen=text.strip()[:MAX_TEXT], urteil=urteil)
        self._raute(agent, f"Schritt {self.nr} · Gesehen: {text.strip()[:160]} · Urteil: {urteil}")
        self.run.step("always")  # sehen → urteil
        self.run.step("always")  # urteil → zuschauer
        return {"ok": True, "sage": f"Danke. Jetzt schaut {self._name(self.zuschauer_von())} auf sein eigenes Bild und bestätigt oder widerspricht."}

    def zuschauer(self, agent: str, text: str, urteil: str) -> dict:
        self._vor()
        if self.art != "zuschauer":
            return self._falscher_knoten("zuschauer")
        if agent != self.zuschauer_von():
            return {"ok": False, "reason": "nicht_dein_zug", "sage": f"Die Bestätigung gehört {self._name(self.zuschauer_von())}: sie oder er schaut auf das eigene Bild und urteilt."}
        if urteil not in ZUSCHAUER_URTEILE:
            return {"ok": False, "reason": "urteil_ungueltig", "sage": "Das Urteil ist ein Wort: bestaetigt oder widerspruch."}
        if not isinstance(text, str) or len(text.strip()) < MIN_TEXT:
            return {"ok": False, "reason": "text_zu_kurz", "sage": "Sag, was du auf deinem eigenen Bild siehst (ein, zwei Sätze)."}
        if self._evidenz_fehlt(agent, ["sehen"], self._seit_blick()):
            return {"ok": False, "reason": "spur_fehlt", "fehlt": ["sehen"], "sage": "Hol erst ein eigenes Bild (`bridge_cli.py see`) — eine Bestätigung ohne eigenen Blick zählt nicht."}
        self._raute(agent, f"Schritt {self.nr} · {'Bestätigt' if urteil == 'bestaetigt' else 'Widerspruch'}: {text.strip()[:170]}")
        self.z.update(zuschauer=text.strip()[:MAX_TEXT], zuschauer_urteil=urteil)
        nr, st = self.nr, self.schritt()
        if urteil == "widerspruch" and self.z["klaerrunden"] < MAX_KLAERRUNDEN:
            self.z["klaerrunden"] += 1
            self.run.step("widerspruch")  # → klären
            self._vor()  # klären → sehen
            return {"ok": True, "sage": f"Danke fürs ehrliche Hinsehen. Klärt es kurz im Chat; {self._name(self.handelnder())} schaut noch einmal hin (`test gesehen`)."}
        streit = urteil == "widerspruch"
        self._zeile({"nr": nr, "titel": st["titel"], "status": "offen_streit" if streit else ("ok" if self.z["urteil"] == "ok" else self.z["urteil"]), "handelnder": self._name(self.handelnder()),
                     "zuschauer": self._name(agent), "ansage": self.z["ansage"], "getan": self.z["getan"], "gesehen": self.z["gesehen"], "urteil": self.z["urteil"], "zuschauer_text": self.z["zuschauer"],
                     "zuschauer_urteil": urteil, "klaerrunden": self.z["klaerrunden"], "plaene": self.z["plaene"], "notizen": self.z["notizen"], "wiederholung": self.z["wiederholung"]})
        self.run.step("bestaetigt")
        self._neu_betreten()
        self._ueberspringen_wenn_noetig()
        lob = LOB[nr % len(LOB)]
        if self.knoten == "ende":
            return {"ok": True, "ende": True, "sage": f"{lob} Das war der letzte Schritt — alle {self.n} sind durch."}
        return {"ok": True, "sage": f"{lob} Weiter mit Schritt {self.nr}: {self.schritt()['titel']} — {self._name(self.handelnder())} sagt ihn an."}

    def nochmal(self, agent: str) -> dict:
        """Den aktuellen Schritt von vorn: der Verlauf bleibt erhalten (Zweig der Harness), der Zustand des Schritts beginnt neu."""
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

    def status(self) -> dict:
        self._vor()
        return {"id": self.id, "schritt": min(self.nr, self.n), "von": self.n, "knoten": self.art, "handelnder": self._name(self.handelnder()) if self.knoten != "ende" else "",
                "fertig": [z["nr"] for z in self.zeilen if z.get("status") in ("ok", "anders", "fehler", "offen_streit")], "zurueckgestellt": [z["nr"] for z in self.zeilen if z.get("status") == "zurueckgestellt"],
                "entdeckungen": len(self.entdeckungen), "harness": self.run.status.value, "trace": len(self.run.trace)}
