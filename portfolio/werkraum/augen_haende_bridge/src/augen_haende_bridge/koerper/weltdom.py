"""WorldDOM (G11): die Bedeutungsschicht über Bild und Programm — Knoten mit Herkunft, Konfidenz, Aktualität und der Methode, mit der sie aufgelöst werden.

Vier Herkünfte, nie vermischt (`ERLEBEN.md`, WorldDOM):

* `real`: aus einer echten Strukturquelle (Browser über CDP, Bedienungshilfen über AT-SPI oder UI Automation). Konfidenz 1,0 für das Dasein des Knotens; seine Lage kann abgeleitet sein.
* `inferred`: aus dem Bild erschlossen (Flächen und Beschriftungen per Bildverarbeitung und OCR). Konfidenz < 1, Grenzen stehen im Knoten.
* `authored`: bewusst angelegt von Daniel oder einem Agenten (Marke, Label, Bedienfläche). Der Urheber steht im Knoten; er wird gespeichert und überlebt einen Neustart.
* `projected`: ein möglicher künftiger Zustand. Nie ausführbar.

Jeder Knoten sagt, **wann** er gemessen wurde (`gemessen_ms`) und wie lange er gilt (`ttl_ms`); danach ist er `veraltet` und löst keine Aktion mehr aus (siehe `weltdom_aktion.py`).
Eine erfundene Ebene gibt nie vor, native Fähigkeiten zu haben: `faehigkeiten` eines erschlossenen oder erfundenen Knotens sind höchstens `zeigen` und `klick_koordinate`.
"""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path

Rechteck = tuple[int, int, int, int]
HERKUENFTE = ("real", "inferred", "authored", "projected")
AUFLOESUNGEN = ("cdp", "uia", "atspi", "koordinate", "virtuell", "keine")
MAX_KNOTEN_JE_ZIEL = 2000
MAX_NAME, MAX_WERT = 200, 300
TTL_REAL_MS, TTL_INFERRED_MS, TTL_AUTHORED_MS = 5_000, 8_000, 24 * 3600_000
STANDARD_TTL = {"real": TTL_REAL_MS, "inferred": TTL_INFERRED_MS, "authored": TTL_AUTHORED_MS, "projected": TTL_INFERRED_MS}


@dataclass
class Knoten:
    id: str
    ziel: str
    herkunft: str
    quelle: str  # cdp | atspi | uia | flaeche | ocr | hand | projektion
    rolle: str
    name: str = ""
    wert: str = ""
    rect: Rechteck | None = None  # Bildschirmkoordinaten zur Messzeit
    confidence: float = 1.0
    gemessen_ms: int = 0
    ttl_ms: int = TTL_REAL_MS
    bild_seq: int | None = None  # auf welches gesendete Bild sich `rect` bezieht (bei aus dem Bild erschlossenen Knoten)
    faehigkeiten: tuple[str, ...] = ()
    aufloesung: str = "keine"
    anker: dict = field(default_factory=dict)  # womit sich der Knoten später wiederfinden lässt (Selektor, Rolle+Name+Pfad, Lage relativ zum Fenster)
    urheber: str = ""
    grenzen: str = ""  # Was dieser Knoten nicht weiß (nur bei erschlossenen, erfundenen und projizierten)
    geometrie: str = "gemessen"  # gemessen | abgeleitet (aus Fensterlage berechnet, nicht vom Programm genannt)

    def alter_ms(self, jetzt_ms: int) -> int:
        return max(0, jetzt_ms - self.gemessen_ms)

    def veraltet(self, jetzt_ms: int) -> bool:
        return self.alter_ms(jetzt_ms) > self.ttl_ms

    def zu_dict(self, jetzt_ms: int | None = None) -> dict:
        d = {"id": self.id, "ziel": self.ziel, "herkunft": self.herkunft, "quelle": self.quelle, "rolle": self.rolle, "name": self.name, "wert": self.wert,
             "rect": list(self.rect) if self.rect else None, "confidence": round(self.confidence, 3), "gemessen_ms": self.gemessen_ms, "ttl_ms": self.ttl_ms,
             "bild_seq": self.bild_seq, "faehigkeiten": list(self.faehigkeiten), "aufloesung": self.aufloesung, "anker": self.anker, "urheber": self.urheber,
             "grenzen": self.grenzen, "geometrie": self.geometrie}
        if jetzt_ms is not None:
            d["alter_ms"] = self.alter_ms(jetzt_ms)
            d["veraltet"] = self.veraltet(jetzt_ms)
        return d

    @staticmethod
    def aus_dict(d: object) -> "Knoten | None":
        """Streng und tolerant zugleich: aus Dateien nur, was alle Pflichtfelder in der richtigen Form hat."""
        if not isinstance(d, dict):
            return None
        try:
            if d["herkunft"] not in HERKUENFTE or d.get("aufloesung", "keine") not in AUFLOESUNGEN:
                return None
            rect = d.get("rect")
            if rect is not None:
                rect = tuple(int(v) for v in rect)
                if len(rect) != 4:
                    return None
            conf = float(d.get("confidence", 1.0))
            if not 0.0 <= conf <= 1.0:
                return None
            return Knoten(str(d["id"])[:120], str(d["ziel"])[:160], d["herkunft"], str(d["quelle"])[:20], str(d["rolle"])[:40], str(d.get("name", ""))[:MAX_NAME], str(d.get("wert", ""))[:MAX_WERT],
                          rect, conf, int(d.get("gemessen_ms", 0)), int(d.get("ttl_ms", STANDARD_TTL[d["herkunft"]])), d.get("bild_seq"), tuple(str(f) for f in d.get("faehigkeiten", ()))[:10],
                          d.get("aufloesung", "keine"), dict(d.get("anker", {})), str(d.get("urheber", ""))[:60], str(d.get("grenzen", ""))[:200], str(d.get("geometrie", "gemessen")))
        except (KeyError, TypeError, ValueError):
            return None


def knoten_id(ziel: str, herkunft: str, quelle: str, *schluessel) -> str:
    """Stabil über Messungen hinweg: dasselbe Element bekommt dieselbe Kennung (aus Rolle, Name, Pfad), nicht aus der Zeit."""
    h = hashlib.blake2b("|".join(str(s) for s in schluessel).encode("utf-8"), digest_size=6).hexdigest()
    return f"{herkunft[:3]}-{quelle}-{h}"


class WeltDom:
    def __init__(self, pfad: Path | None = None):
        self._knoten: dict[str, dict[str, Knoten]] = {}  # ziel -> id -> Knoten
        self.pfad = Path(pfad) if pfad else None
        self.fehler = ""
        self._sperre = threading.RLock()

    # ---- Schreiben ---------------------------------------------------------------------------------------------------------------
    def ersetze(self, ziel: str, herkunft: str, quelle: str, neu: list[Knoten]) -> tuple[int, int]:
        """Eine Messung ersetzt den Stand dieser Quelle für das Ziel. Liefert (neu_oder_aktualisiert, verschwunden); verschwundene Knoten fliegen raus, nichts wird als noch da behauptet."""
        with self._sperre:
            tabelle = self._knoten.setdefault(ziel, {})
            alt = {i for i, k in tabelle.items() if k.herkunft == herkunft and k.quelle == quelle}
            neu = neu[:MAX_KNOTEN_JE_ZIEL]
            for k in neu:
                if k.ziel != ziel or k.herkunft != herkunft or k.quelle != quelle:
                    raise ValueError("knoten_passt_nicht_zur_messung")
                tabelle[k.id] = k
            weg = alt - {k.id for k in neu}
            for i in weg:
                del tabelle[i]
            return len(neu), len(weg)

    def anker_anlegen(self, ziel: str, name: str, rect: Rechteck | None, *, urheber: str, jetzt_ms: int, rolle: str = "marke", beschreibung: str = "", relativ: tuple[float, float, float, float] | None = None,
                      herkunft: str = "authored", ttl_ms: int | None = None) -> Knoten:
        """Ein bewusst erfundener (oder projizierter) Knoten. `relativ` (Anteile des Fensters) hält ihn bei Verschiebung und Skalierung an derselben Stelle."""
        if herkunft not in ("authored", "projected"):
            raise ValueError("nur_authored_oder_projected")
        if not name or len(name) > MAX_NAME or not urheber:
            raise ValueError("name_oder_urheber_fehlt")
        if rect is None and relativ is None and herkunft == "authored":
            raise ValueError("ort_fehlt")
        anker = {"relativ": list(relativ)} if relativ else {}
        faehig = ("zeigen", "klick_koordinate") if herkunft == "authored" and (rect or relativ) else ("zeigen",)
        k = Knoten(knoten_id(ziel, herkunft, "hand", name, urheber, rect, relativ), ziel, herkunft, "hand" if herkunft == "authored" else "projektion", rolle, name, beschreibung[:MAX_WERT], rect, 1.0 if herkunft == "authored" else 0.5,
                   jetzt_ms, ttl_ms or STANDARD_TTL[herkunft], None, faehig if herkunft == "authored" else ("zeigen",), "koordinate" if herkunft == "authored" and (rect or relativ) else "virtuell", anker, urheber,
                   "bewusst angelegt, nicht Teil der Anwendung" if herkunft == "authored" else "ein möglicher künftiger Zustand, nie ausführbar", "gemessen")
        with self._sperre:
            tabelle = self._knoten.setdefault(ziel, {})
            if len(tabelle) >= MAX_KNOTEN_JE_ZIEL:
                raise ValueError("zu_viele_knoten")
            tabelle[k.id] = k
        self.speichern()
        return k

    def entfernen(self, ziel: str, knoten_id_: str) -> bool:
        with self._sperre:
            weg = self._knoten.get(ziel, {}).pop(knoten_id_, None) is not None
        if weg:
            self.speichern()
        return weg

    # ---- Lesen ---------------------------------------------------------------------------------------------------------------------
    def knoten(self, ziel: str, knoten_id_: str) -> Knoten | None:
        with self._sperre:
            return self._knoten.get(ziel, {}).get(knoten_id_)

    def finde(self, knoten_id_: str) -> Knoten | None:
        with self._sperre:
            for tabelle in self._knoten.values():
                if knoten_id_ in tabelle:
                    return tabelle[knoten_id_]
        return None

    def liste(self, ziel: str, *, herkunft: str | None = None, rolle: str | None = None, text: str | None = None, nur_aktuell: bool = False, jetzt_ms: int = 0, limit: int = 200) -> list[Knoten]:
        with self._sperre:
            treffer = [k for k in self._knoten.get(ziel, {}).values() if (herkunft is None or k.herkunft == herkunft) and (rolle is None or k.rolle == rolle)
                       and (text is None or text.lower() in (k.name + " " + k.wert).lower()) and (not nur_aktuell or not k.veraltet(jetzt_ms))]
        treffer.sort(key=lambda k: (k.rect[1], k.rect[0]) if k.rect else (10**9, 0))
        return treffer[:limit]

    def zaehlung(self, ziel: str) -> dict[str, int]:
        with self._sperre:
            z = {h: 0 for h in HERKUENFTE}
            for k in self._knoten.get(ziel, {}).values():
                z[k.herkunft] += 1
            return z

    def ziel_vergessen(self, ziel: str) -> None:
        """Das Fenster ist weg: seine echten, erschlossenen und projizierten Knoten gelten nicht mehr; erfundene Anker bleiben (Daniel hat sie gesetzt)."""
        with self._sperre:
            tabelle = self._knoten.get(ziel, {})
            for i in [i for i, k in tabelle.items() if k.herkunft != "authored"]:
                del tabelle[i]

    # ---- Speichern: nur das Bewusste ----------------------------------------------------------------------------------------------
    def speichern(self) -> bool:
        if self.pfad is None:
            return True
        try:
            with self._sperre:
                daten = {z: [k.zu_dict() for k in t.values() if k.herkunft == "authored"] for z, t in self._knoten.items()}
            daten = {z: v for z, v in daten.items() if v}
            self.pfad.parent.mkdir(parents=True, exist_ok=True)
            temp = self.pfad.with_suffix(".tmp")
            temp.write_text(json.dumps({"version": 1, "anker": daten}, ensure_ascii=False), encoding="utf-8")
            temp.replace(self.pfad)
            return True
        except OSError as fehler:
            self.fehler = f"WorldDOM nicht gespeichert: {fehler!r}"[:200]
            return False

    def laden(self) -> int:
        """Tolerant: eine kaputte Datei ergibt keinen Absturz, kaputte Einträge werden übersprungen."""
        if self.pfad is None or not self.pfad.exists():
            return 0
        try:
            roh = json.loads(self.pfad.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.fehler = "WorldDOM-Datei unlesbar: ignoriert"
            return 0
        n = 0
        for ziel, liste in (roh.get("anker", {}) if isinstance(roh, dict) else {}).items():
            if not isinstance(liste, list):
                continue
            for d in liste:
                k = Knoten.aus_dict(d)
                if k is not None and k.herkunft == "authored" and k.ziel == ziel:
                    self._knoten.setdefault(ziel, {})[k.id] = k
                    n += 1
        return n


# ---- Echte Strukturquellen in Knoten übersetzen --------------------------------------------------------------------------------------
UI_ROLLEN_FAEHIG = {"button": ("klick",), "push_button": ("klick",), "check_box": ("klick",), "radio_button": ("klick",), "menu_item": ("klick",), "link": ("klick",), "hyperlink": ("klick",),
                    "tab": ("klick",), "tab_item": ("klick",), "list_item": ("klick",), "text": ("text_setzen", "lesen"), "edit": ("text_setzen", "lesen"), "entry": ("text_setzen", "lesen"),
                    "textbox": ("text_setzen", "lesen"), "combo_box": ("klick",), "label": ("lesen",), "heading": ("lesen",), "document": ("lesen",)}


def aus_ui_baum(ziel: str, wurzel, quelle: str, pid, jetzt_ms: int, *, nur_nuetzliche: bool = True) -> list[Knoten]:
    """Ein `uia.UiKnoten`-Baum (AT-SPI oder UI Automation) → real-Knoten. Rolle und Name, Lage und die Fähigkeiten, die der Knoten wirklich hat (nicht die der Rolle)."""
    knoten: list[Knoten] = []

    def gehe(k, pfad: tuple[int, ...]) -> None:
        rolle = k.rolle or "unbekannt"
        if not nur_nuetzliche or rolle in UI_ROLLEN_FAEHIG or k.faehigkeiten:
            faehig = tuple(sorted(set(k.faehigkeiten) | ({"lesen"} if (k.name or k.wert) else set())))
            knoten.append(Knoten(knoten_id(ziel, "real", quelle, pid, pfad, rolle, k.name), ziel, "real", quelle, rolle, k.name[:MAX_NAME], (k.wert or "")[:MAX_WERT], k.rect, 1.0, jetzt_ms,
                                 TTL_REAL_MS, None, faehig, quelle, {"pid": pid, "pfad": list(pfad), "rolle": rolle, "name": k.name[:MAX_NAME]}, "", "", "gemessen" if k.rect else "abgeleitet"))
        for i, kind in enumerate(k.kinder):
            gehe(kind, pfad + (i,))

    gehe(wurzel, ())
    return knoten
