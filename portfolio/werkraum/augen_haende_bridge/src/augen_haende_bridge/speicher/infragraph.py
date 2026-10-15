"""Der lange Graph der Infrastruktur (G09, G12) auf LangGraph: jede Voraussetzung eines Schritts ist ein Knoten.

    ziel_gebunden ─▶ strom_frisch ─▶ lease ─▶ hand ─▶ beleg ─▶ urteil ─▶ ende
          │ (dritter Fehlversuch an irgendeinem Knoten)
          └────────────────▶ blockiert ─▶ diagnose ─▶ (Entsperren) ─▶ derselbe Knoten

Die Übergänge sind erzwungen: es gibt keine Kante, die einen Knoten überspringt. Was ein Agent im Knoten tut, bleibt frei; der Knoten
verlangt nur seinen Beleg. Schlägt die Prüfung fehl, wartet der Lauf an diesem Knoten (Ereignis `wartet` mit dem Grund). Der dritte
Fehlversuch führt in `blockiert` und `diagnose`: Halt, Ursache suchen, erst `entsperren` mit einer Ursache lässt den Knoten wieder zu.
Jeder Knoten und jede Kante schreibt ein Ereignis in den Ereignisspeicher; die Position eines Laufs ist dort abfragbar.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .ereignisspeicher import Ereignisspeicher

KNOTEN = ("ziel_gebunden", "strom_frisch", "lease", "hand", "beleg", "urteil")
BESCHREIBUNG = {
    "ziel_gebunden": "ein Ziel (Fenster oder Desktop) ist gebunden",
    "strom_frisch": "der Bilderstrom liefert ein frisches Bild",
    "lease": "eine gültige Lease für die Hände liegt vor",
    "hand": "die Hand hat die Aktion ausgeführt",
    "beleg": "ein echter Beleg (Bild, Ereignis) für die Aktion liegt vor",
    "urteil": "der Gutachter hat mit eigenem frischem Bild geurteilt",
}
MAX_FEHLVERSUCHE = 3

Pruefer = Callable[[str, str], tuple[bool, str]]  # (lauf, agent) -> (erfüllt, Grund wenn nicht)


class Zustand(TypedDict, total=False):
    lauf: str
    agent: str
    knoten: str     # an welchem Knoten der Lauf steht (Eintritt)
    ergebnis: str   # weiter | wartet | halt | fertig
    grund: str


class Infragraph:
    def __init__(self, speicher: Ereignisspeicher, pruefer: dict[str, Pruefer], max_fehlversuche: int = MAX_FEHLVERSUCHE):
        fehlt = [k for k in KNOTEN if k not in pruefer]
        if fehlt:
            raise ValueError(f"Prüfer fehlen für: {', '.join(fehlt)}")
        self.speicher, self.pruefer, self.max = speicher, pruefer, max_fehlversuche
        self._graph = self._bauen()

    # ---- Graph -------------------------------------------------------------------------------------------------------
    def _bauen(self):
        g = StateGraph(Zustand)
        for i, name in enumerate(KNOTEN):
            g.add_node(name, self._knoten_fn(name))
            g.add_conditional_edges(name, self._kante(name, KNOTEN[i + 1] if i + 1 < len(KNOTEN) else "ende"))
        g.add_node("blockiert", self._blockiert)
        g.add_node("diagnose", self._diagnose)
        g.add_node("ende", self._ende)
        g.add_conditional_edges(START, lambda z: z.get("knoten") or KNOTEN[0], {**{k: k for k in KNOTEN}, "blockiert": "blockiert", "ende": "ende"})
        g.add_edge("blockiert", "diagnose")
        g.add_edge("diagnose", END)
        g.add_edge("ende", END)
        return g.compile()

    def _ereignis(self, art: str, z: Zustand, **kw) -> None:
        self.speicher.schreiben("graph", art, agent=z.get("agent", ""), lauf=z.get("lauf", ""), **kw)

    def _knoten_fn(self, name: str):
        def lauf(z: Zustand) -> Zustand:
            self._ereignis("knoten_betreten", z, knoten=name, text=BESCHREIBUNG[name])
            try:
                ok, grund = self.pruefer[name](z["lauf"], z["agent"])
            except Exception as f:  # ein kaputter Prüfer zählt als Fehlversuch mit seinem Fehler als Grund, nie als Erfolg
                ok, grund = False, f"pruefer_fehler:{type(f).__name__}"
            if ok:
                self._ereignis("knoten_ok", z, knoten=name)
                if self.speicher.wartet_agent(z["agent"]):
                    self._ereignis("wartet_ende", z, knoten=name)
                return {"ergebnis": "weiter", "knoten": name, "grund": ""}
            self._ereignis("fehlversuch", z, knoten=name, grund=grund, text=f"{BESCHREIBUNG[name]}: nicht erfüllt ({grund})")
            n = self.speicher.fehlversuche(z["lauf"], name)
            if n >= self.max:
                return {"ergebnis": "halt", "knoten": name, "grund": grund}
            self._ereignis("wartet", z, knoten=name, versuch=n, grund=grund, text=f"wartet auf: {BESCHREIBUNG[name]}")
            return {"ergebnis": "wartet", "knoten": name, "grund": grund}
        return lauf

    def _kante(self, name: str, naechster: str):
        def kante(z: Zustand) -> str:
            ziel = {"weiter": naechster, "wartet": END, "halt": "blockiert"}[z["ergebnis"]]
            if ziel not in (END,):
                self._ereignis("kante", z, knoten=name, text=f"{name} → {ziel}")
            return ziel
        return kante

    def _blockiert(self, z: Zustand) -> Zustand:
        self._ereignis("halt", z, knoten=z["knoten"], versuch=self.max, grund=z.get("grund", ""),
                       text=f"Halt an {z['knoten']}: {self.max} Fehlversuche, kein Überspringen")
        return {}

    def _diagnose(self, z: Zustand) -> Zustand:
        self._ereignis("diagnose", z, knoten=z["knoten"], grund=z.get("grund", ""),
                       text=f"Ursache suchen an {z['knoten']} ({z.get('grund', '')}); erst entsperren, wenn die Ursache benannt ist")
        return {"ergebnis": "halt"}

    def _ende(self, z: Zustand) -> Zustand:
        self._ereignis("lauf_fertig", z, knoten="ende", text="alle Knoten erfüllt")
        return {"ergebnis": "fertig", "knoten": "ende"}

    # ---- Bedienen ----------------------------------------------------------------------------------------------------
    def _start_knoten(self, lauf: str) -> str:
        p = self.speicher.position(lauf)
        if not p:
            return KNOTEN[0]
        if p["knoten"] == "ende":
            return "ende"
        return p["knoten"]

    def weiter(self, lauf: str, agent: str) -> dict:
        """Führt den Lauf von seiner Position aus, bis er wartet, hält oder fertig ist. Gibt `karte` zurück."""
        if self.karte(lauf, agent)["zustand"] == "halt":
            return self.karte(lauf, agent)  # Halt gilt, bis `entsperren` eine Ursache hat; ein inzwischen grüner Prüfer hebt ihn nicht auf
        z = self._graph.invoke({"lauf": lauf, "agent": agent, "knoten": self._start_knoten(lauf)})
        if z.get("ergebnis") == "weiter" and z.get("knoten") == KNOTEN[-1]:  # letzter Knoten erfüllt
            self._graph.invoke({"lauf": lauf, "agent": agent, "knoten": "ende"})
        return self.karte(lauf, agent)

    def entsperren(self, lauf: str, agent: str, ursache: str) -> bool:
        """Hebt den Halt auf, aber nur mit benannter Ursache; der Knoten bleibt derselbe (kein Überspringen)."""
        p = self.speicher.position(lauf)
        if not p or p["knoten"] not in KNOTEN or len(ursache.strip()) < 8:
            return False
        self.speicher.schreiben("graph", "entsperrt", agent=agent, lauf=lauf, knoten=p["knoten"], text=ursache.strip(), grund="ursache_benannt")
        self.speicher.schreiben("graph", "knoten_betreten", agent=agent, lauf=lauf, knoten=p["knoten"], text="nach Entsperren wieder zugelassen")
        return True

    def karte(self, lauf: str, agent: str) -> dict:
        """Was ein Agent von der Bridge über seine Position erfährt: wo, was fehlt, seit wann, wie viele Versuche, wer sonst wartet."""
        p = self.speicher.position(lauf) or {"knoten": KNOTEN[0], "zeit_ms": 0, "versuch": 0}
        knoten = p["knoten"]
        w = self.speicher.wartet_agent(agent)
        wartende = [x["agent"] for x in self.speicher.wartezustand() if x["agent"] != agent]
        halt = self.speicher.abfrage("SELECT art FROM ereignis WHERE quelle='graph' AND lauf=%s AND art IN ('halt','entsperrt','lauf_fertig') ORDER BY id DESC LIMIT 1", (lauf,))
        art = halt[0]["art"] if halt else ""
        if art == "lauf_fertig":
            zustand, satz = "fertig", "Lauf fertig: alle Knoten erfüllt."
        elif art == "halt":
            zustand, satz = "halt", f"Halt an {knoten}: Ursache suchen, dann entsperren. Überspringen gibt es nicht."
        elif w:
            zustand, satz = "wartet", f"Du wartest an {knoten} auf: {BESCHREIBUNG.get(knoten, knoten)} (Grund: {w['worauf']})."
        else:
            zustand, satz = "dran", f"Du bist dran an {knoten}: {BESCHREIBUNG.get(knoten, knoten)}."
        nr = KNOTEN.index(knoten) + 1 if knoten in KNOTEN else len(KNOTEN)
        return {"lauf": lauf, "agent": agent, "knoten": knoten, "position": f"{nr} von {len(KNOTEN)}", "zustand": zustand, "satz": satz,
                "versuche": self.speicher.fehlversuche(lauf, knoten), "max": self.max, "wartet_seit_ms": w["seit_ms"] if w else None,
                "wartet_auf": w["worauf"] if w else "", "andere_wartende": wartende}
