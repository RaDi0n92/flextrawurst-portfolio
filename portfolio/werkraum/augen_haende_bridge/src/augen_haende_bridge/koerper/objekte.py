"""Objekte der gemeinsamen Arbeitsfläche (G08): Bilder, Texte, Freihand, Marker, Linien, Pfeile, Rechtecke und Kreise in einem Gate.

Ein **Gate** ist das gebundene Ziel (ein Fenster oder der ganze Desktop). Objekte liegen im Gate, nie auf einem anderen: ein Agentenwechsel verschiebt sie
nicht ungefragt in ein anderes Gate (R051). Alle Punkte sind **relativ zum Gate** (0 bis 1, links oben ist (0, 0)), so wandern sie mit und skalieren mit dem Fenster.

Jedes Objekt hat zwei voneinander unabhängige Einstellungen (R113, R043):

* `bildschirm`: steht physisch auf Daniels Bildschirm (und ist damit auch im Basisbild jedes Agenten, der diesen Bereich sieht);
* `empfaenger`: in den Bildern genau dieser Agenten wird es komponiert — und nirgends sonst (nicht auf dem Bildschirm, nicht im Bild anderer Agenten, nicht im Chat).

Das Dokument kennt Auswahl-unabhängige Befehle mit Rückgängig und Wiederholen: jeder Befehl merkt Zustand davor und danach der betroffenen Objekte.
"""

from __future__ import annotations

import base64
import copy
import itertools
import uuid
from dataclasses import dataclass, field

ARTEN = ("bild", "text", "freihand", "marker", "linie", "pfeil", "rechteck", "kreis")
MAX_UNDO = 200
MAX_OBJEKTE = 500
MAX_PUNKTE = 5000
MAX_TEXT = 2000
MAX_BILD_BYTES = 4_000_000
Punkt = tuple[float, float]


@dataclass
class Objekt:
    id: str
    art: str
    punkte: list[Punkt]
    farbe: str = "#FF0055"
    staerke: int = 4
    text: str = ""
    schriftgroesse: int = 28
    bild: bytes | None = None  # PNG-Bytes eines eingefügten Bildes
    z: int = 0
    gruppe: str | None = None
    sichtbar: bool = True
    bildschirm: bool = False
    empfaenger: tuple[str, ...] = ()
    deckkraft: int = 100  # 5 bis 100 Prozent
    fett: bool = False
    kursiv: bool = False
    unterstrichen: bool = False
    schwebend: bool = False  # ein Bild-Element: eigenes Fenster, direkt anfassbar (verschieben, Größe, Deckkraft), nicht Teil der durchklickbaren Anzeige

    def kopie(self) -> "Objekt":
        return copy.copy(self)

    def grenzen(self) -> tuple[float, float, float, float]:
        """(links, oben, rechts, unten) in Gate-Koordinaten (ohne Strichstärke)."""
        xs = [p[0] for p in self.punkte] or [0.0]
        ys = [p[1] for p in self.punkte] or [0.0]
        return min(xs), min(ys), max(xs), max(ys)

    def zu_dict(self) -> dict:
        d = {"id": self.id, "art": self.art, "punkte": [[round(x, 5), round(y, 5)] for x, y in self.punkte], "farbe": self.farbe,
             "staerke": self.staerke, "text": self.text, "schriftgroesse": self.schriftgroesse, "z": self.z, "gruppe": self.gruppe,
             "sichtbar": self.sichtbar, "bildschirm": self.bildschirm, "empfaenger": list(self.empfaenger),
             "deckkraft": self.deckkraft, "fett": self.fett, "kursiv": self.kursiv, "unterstrichen": self.unterstrichen, "schwebend": self.schwebend}
        if self.bild is not None:
            d["bild"] = base64.b64encode(self.bild).decode()
        return d

    @staticmethod
    def aus_dict(d: object) -> "Objekt | None":
        """Tolerant: kaputte oder fremde Daten ergeben None statt eines Absturzes."""
        try:
            if not isinstance(d, dict) or d.get("art") not in ARTEN:
                return None
            punkte = [(min(1.5, max(-0.5, float(p[0]))), min(1.5, max(-0.5, float(p[1])))) for p in d.get("punkte", [])][:MAX_PUNKTE]
            if not punkte:
                return None
            bild = base64.b64decode(d["bild"], validate=True) if d.get("bild") else None
            if bild is not None and len(bild) > MAX_BILD_BYTES:
                return None
            farbe = d.get("farbe") if isinstance(d.get("farbe"), str) and len(d["farbe"]) == 7 and d["farbe"].startswith("#") else "#FF0055"
            return Objekt(str(d.get("id") or uuid.uuid4().hex[:10]), d["art"], punkte, farbe, max(1, min(60, int(d.get("staerke", 4)))),
                          str(d.get("text", ""))[:MAX_TEXT], max(8, min(200, int(d.get("schriftgroesse", 28)))), bild, int(d.get("z", 0)),
                          d.get("gruppe") if isinstance(d.get("gruppe"), str) else None, bool(d.get("sichtbar", True)),
                          bool(d.get("bildschirm", False)), tuple(str(e) for e in d.get("empfaenger", [])[:32]),
                          max(5, min(100, int(d.get("deckkraft", 100)))), bool(d.get("fett", False)), bool(d.get("kursiv", False)),
                          bool(d.get("unterstrichen", False)), bool(d.get("schwebend", False)))
        except (TypeError, ValueError, KeyError, IndexError):
            return None


def neue_id() -> str:
    return uuid.uuid4().hex[:10]


class Dokument:
    """Die Objekte eines Gates mit Rückgängig und Wiederholen."""

    def __init__(self, ziel_schluessel: str = ""):
        self.ziel_schluessel = ziel_schluessel
        self.objekte: dict[str, Objekt] = {}
        self._undo: list[tuple[dict, dict]] = []
        self._redo: list[tuple[dict, dict]] = []
        self._z = itertools.count(1)
        self.version = 0  # steigt bei jeder Änderung (auch Rückgängig): Bilder werden dann neu komponiert

    # ---- Lesen ------------------------------------------------------------------------------------------------------
    def sortiert(self) -> list[Objekt]:
        return sorted(self.objekte.values(), key=lambda o: (o.z, o.id))

    def fuer_empfaenger(self, tid: str) -> list[Objekt]:
        """Was in das Bild dieses Agenten komponiert wird: sichtbar und er steht in der Empfängerliste (alles andere nicht)."""
        return [o for o in self.sortiert() if o.sichtbar and tid in o.empfaenger]

    def auf_dem_bildschirm(self) -> list[Objekt]:
        """Was die durchklickbare Anzeige zeichnet; schwebende Bild-Elemente haben ihr eigenes Fenster."""
        return [o for o in self.sortiert() if o.sichtbar and o.bildschirm and not o.schwebend]

    def schwebende(self) -> list[Objekt]:
        return [o for o in self.sortiert() if o.schwebend and o.art == "bild"]

    def mitglieder(self, objekt_id: str) -> list[str]:
        """Das Objekt und alle seiner Gruppe."""
        o = self.objekte.get(objekt_id)
        if o is None:
            return []
        if o.gruppe is None:
            return [objekt_id]
        return [i for i, x in self.objekte.items() if x.gruppe == o.gruppe]

    def treffer(self, x: float, y: float, toleranz: float = 0.01) -> str | None:
        """Das oberste Objekt an dieser Stelle (Gate-Koordinaten), oder None. Nur sichtbare zählen."""
        for o in reversed(self.sortiert()):
            if not o.sichtbar:
                continue
            l, t, r, u = o.grenzen()
            if o.art in ("rechteck", "kreis", "bild", "text") and l - toleranz <= x <= r + toleranz and t - toleranz <= y <= u + toleranz:
                return o.id
            if o.art in ("linie", "pfeil", "freihand", "marker") and self._nahe_am_strich(o, x, y, max(toleranz, o.staerke / 1500)):
                return o.id
        return None

    @staticmethod
    def _nahe_am_strich(o: Objekt, x: float, y: float, toleranz: float) -> bool:
        pts = o.punkte
        for (ax, ay), (bx, by) in zip(pts, pts[1:] or pts):
            dx, dy = bx - ax, by - ay
            laenge2 = dx * dx + dy * dy
            t = 0.0 if laenge2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / laenge2))
            if (x - (ax + t * dx)) ** 2 + (y - (ay + t * dy)) ** 2 <= toleranz ** 2:
                return True
        return False

    def im_rechteck(self, l: float, t: float, r: float, u: float) -> list[str]:
        """Objekte, die vollständig im Rechteck liegen (Gummiband-Auswahl)."""
        ergebnis = []
        for o in self.sortiert():
            if not o.sichtbar:
                continue
            ol, ot, orr, ou = o.grenzen()
            if ol >= l and ot >= t and orr <= r and ou <= u:
                ergebnis.append(o.id)
        return ergebnis

    # ---- Befehle ----------------------------------------------------------------------------------------------------
    def _buchen(self, vorher: dict, nachher: dict) -> None:
        if vorher == nachher:
            return
        self._undo.append((vorher, nachher))
        del self._undo[:-MAX_UNDO]
        self._redo.clear()
        self.version += 1

    def _anwenden(self, zustand: dict) -> None:
        for i, o in zustand.items():
            if o is None:
                self.objekte.pop(i, None)
            else:
                self.objekte[i] = o.kopie()

    def _stand(self, ids) -> dict:
        return {i: (self.objekte[i].kopie() if i in self.objekte else None) for i in ids}

    def hinzufuegen(self, objekt: Objekt) -> str | None:
        if len(self.objekte) >= MAX_OBJEKTE or objekt.art not in ARTEN or not objekt.punkte:
            return None
        objekt.punkte = objekt.punkte[:MAX_PUNKTE]
        objekt.text = objekt.text[:MAX_TEXT]
        objekt.z = next(self._z)
        vorher = {objekt.id: None}
        self.objekte[objekt.id] = objekt
        self._buchen(vorher, self._stand([objekt.id]))
        return objekt.id

    def entfernen(self, ids) -> int:
        ids = [i for i in ids if i in self.objekte]
        if not ids:
            return 0
        vorher = self._stand(ids)
        for i in ids:
            del self.objekte[i]
        self._buchen(vorher, {i: None for i in ids})
        return len(ids)

    def aendern(self, ids, **felder) -> int:
        """Felder mehrerer Objekte setzen (Farbe, Stärke, Text, Sichtbarkeit, Empfänger, …)."""
        ids = [i for i in ids if i in self.objekte]
        if not ids:
            return 0
        erlaubt = {"farbe", "staerke", "text", "schriftgroesse", "sichtbar", "bildschirm", "empfaenger", "punkte", "deckkraft", "fett", "kursiv",
                   "unterstrichen", "schwebend"}
        felder = {k: v for k, v in felder.items() if k in erlaubt}
        vorher = self._stand(ids)
        for i in ids:
            for k, v in felder.items():
                setattr(self.objekte[i], k, tuple(v) if k == "empfaenger" else v)
        self._buchen(vorher, self._stand(ids))
        return len(ids)

    def verschieben(self, ids, dx: float, dy: float) -> int:
        ids = [i for i in self._mit_gruppen(ids) if i in self.objekte]
        if not ids:
            return 0
        vorher = self._stand(ids)
        for i in ids:
            o = self.objekte[i]
            o.punkte = [(x + dx, y + dy) for x, y in o.punkte]
        self._buchen(vorher, self._stand(ids))
        return len(ids)

    def skalieren(self, ids, faktor_x: float, faktor_y: float, ankerpunkt: Punkt) -> int:
        """Größe ändern um einen festen Punkt (die gegenüberliegende Ecke beim Ziehen eines Griffs)."""
        ids = [i for i in self._mit_gruppen(ids) if i in self.objekte]
        if not ids or faktor_x <= 0 or faktor_y <= 0:
            return 0
        vorher = self._stand(ids)
        ax, ay = ankerpunkt
        for i in ids:
            o = self.objekte[i]
            o.punkte = [(ax + (x - ax) * faktor_x, ay + (y - ay) * faktor_y) for x, y in o.punkte]
        self._buchen(vorher, self._stand(ids))
        return len(ids)

    def groesse_aendern(self, ids, faktor: float) -> int:
        """Größer oder kleiner um die Mitte der gemeinsamen Umrandung (Rechtsklick-Menü). Texte ändern ihre Schriftgröße, nicht die Punkte."""
        ids = [i for i in self._mit_gruppen(ids) if i in self.objekte]
        if not ids or faktor <= 0:
            return 0
        vorher = self._stand(ids)
        grenzen = [self.objekte[i].grenzen() for i in ids if self.objekte[i].art != "text"]
        if grenzen:
            mx = (min(g[0] for g in grenzen) + max(g[2] for g in grenzen)) / 2
            my = (min(g[1] for g in grenzen) + max(g[3] for g in grenzen)) / 2
        for i in ids:
            o = self.objekte[i]
            if o.art == "text":
                o.schriftgroesse = max(8, min(200, round(o.schriftgroesse * faktor)))
            else:
                o.punkte = [(mx + (x - mx) * faktor, my + (y - my) * faktor) for x, y in o.punkte]
        self._buchen(vorher, self._stand(ids))
        return len(ids)

    def _mit_gruppen(self, ids) -> list[str]:
        ergebnis: list[str] = []
        for i in ids:
            for m in self.mitglieder(i):
                if m not in ergebnis:
                    ergebnis.append(m)
        return ergebnis

    def ordnung(self, ids, wie: str) -> int:
        """Z-Ordnung: „ganz_vor“, „ganz_zurueck“, „vor“ (eins höher), „zurueck“ (eins tiefer)."""
        ids = [i for i in self._mit_gruppen(ids) if i in self.objekte]
        if not ids or wie not in ("ganz_vor", "ganz_zurueck", "vor", "zurueck"):
            return 0
        folge = [o.id for o in self.sortiert()]
        gewaehlt = [i for i in folge if i in ids]
        rest = [i for i in folge if i not in ids]
        if wie == "ganz_vor":
            neu = rest + gewaehlt
        elif wie == "ganz_zurueck":
            neu = gewaehlt + rest
        else:
            neu = list(folge)
            schritte = range(len(neu) - 2, -1, -1) if wie == "vor" else range(1, len(neu))
            for pos in schritte:
                a, b = (pos, pos + 1) if wie == "vor" else (pos, pos - 1)
                if neu[a] in ids and neu[b] not in ids:
                    neu[a], neu[b] = neu[b], neu[a]
        if neu == folge:
            return 0
        vorher = self._stand(folge)
        for nr, i in enumerate(neu, start=1):
            self.objekte[i].z = nr
        self._z = itertools.count(len(neu) + 1)
        self._buchen(vorher, self._stand(folge))
        return len(ids)

    def gruppieren(self, ids) -> str | None:
        ids = [i for i in ids if i in self.objekte]
        if len(ids) < 2:
            return None
        gruppe = "g-" + neue_id()
        vorher = self._stand(ids)
        for i in ids:
            self.objekte[i].gruppe = gruppe
        self._buchen(vorher, self._stand(ids))
        return gruppe

    def aufloesen(self, ids) -> int:
        ids = [i for i in self._mit_gruppen(ids) if i in self.objekte and self.objekte[i].gruppe is not None]
        if not ids:
            return 0
        vorher = self._stand(ids)
        for i in ids:
            self.objekte[i].gruppe = None
        self._buchen(vorher, self._stand(ids))
        return len(ids)

    def duplizieren(self, ids, versatz: float = 0.02) -> list[str]:
        ids = [i for i in self._mit_gruppen(ids) if i in self.objekte]
        neue: list[str] = []
        zuordnung: dict[str, str] = {}
        vorher: dict = {}
        for i in sorted(ids, key=lambda k: self.objekte[k].z):
            if len(self.objekte) >= MAX_OBJEKTE:
                break
            o = self.objekte[i].kopie()
            o.id = neue_id()
            o.punkte = [(x + versatz, y + versatz) for x, y in o.punkte]
            o.z = next(self._z)
            if o.gruppe is not None:
                zuordnung.setdefault(o.gruppe, "g-" + neue_id())
                o.gruppe = zuordnung[o.gruppe]
            self.objekte[o.id] = o
            vorher[o.id] = None
            neue.append(o.id)
        if neue:
            self._buchen(vorher, self._stand(neue))
        return neue

    # ---- Rückgängig, Wiederholen ----------------------------------------------------------------------------------
    def rueckgaengig(self) -> bool:
        if not self._undo:
            return False
        vorher, nachher = self._undo.pop()
        self._anwenden(vorher)
        self._redo.append((vorher, nachher))
        self.version += 1
        return True

    def wiederholen(self) -> bool:
        if not self._redo:
            return False
        vorher, nachher = self._redo.pop()
        self._anwenden(nachher)
        self._undo.append((vorher, nachher))
        self.version += 1
        return True

    @property
    def kann_rueckgaengig(self) -> bool:
        return bool(self._undo)

    @property
    def kann_wiederholen(self) -> bool:
        return bool(self._redo)

    # ---- Speichern -------------------------------------------------------------------------------------------------
    def zu_dict(self) -> dict:
        return {"ziel": self.ziel_schluessel, "objekte": [o.zu_dict() for o in self.sortiert()]}

    @staticmethod
    def aus_dict(d: object, ziel_schluessel: str = "") -> "Dokument":
        dok = Dokument(ziel_schluessel)
        liste = d.get("objekte", []) if isinstance(d, dict) else []
        for roh in liste[:MAX_OBJEKTE] if isinstance(liste, list) else []:
            o = Objekt.aus_dict(roh)
            if o is not None and o.id not in dok.objekte:
                o.z = next(dok._z)  # die Reihenfolge der Datei bleibt, die Zahlen werden neu vergeben
                dok.objekte[o.id] = o
        return dok
