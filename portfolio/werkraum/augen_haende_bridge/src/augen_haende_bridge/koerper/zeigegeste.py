"""Zeigegesten (G11, R052–R054): „das hier“ — mit dem gemeinten Ort, dem Ziel und dem Bild, auf dem gezeigt wurde.

Eine Geste hält fest, **worauf** gezeigt wurde (der WorldDOM-Knoten unter dem Punkt, wenn es einen gibt: Inhaltshaftung), **wo** (Punkt im Bild, Anteil im Fenster) und **auf welchem Bild**.
Danach gilt, was die Aufgabe verlangt: ändert sich das Layout, warnt die Geste oder löst sich neu auf — sie führt nie blind zum alten Pixel.

* Gültig bleibt sie bei gleicher Fenstergröße (das Fenster darf wandern: die Lage im Fenster bleibt `fensterbindung`, der verständliche Fallback).
* Hat sich die Größe geändert, wird neu aufgelöst, wenn die Geste an einem Inhalt haftet und der Knoten frisch gefunden wird; sonst ist sie `veraltet`.
* Ist das Bild zu alt oder das Fenster ein anderes, ist sie `veraltet`.

**Darstellung und Einfügung sind zwei Wege mit zwei Ergebnissen.** `praesentieren` legt ein Zeichen in die gemeinsame Arbeitsfläche (G08): Daniel und die gewählten Agenten sehen es, die Anwendung
merkt nichts. `einfuegen` führt eine echte Handlung in der Anwendung aus (über den WorldDOM-Knoten oder, ohne Inhalt, als Klick auf den neu berechneten Punkt über die Hände) und bringt einen eigenen Beleg.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from .eingabe_adapter import Bildbezug, ZielStand, bild_zu_schirm
from .weltdom import Knoten, WeltDom

MAX_GESTE_ALTER_MS = 60_000


@dataclass(frozen=True)
class Zeigegeste:
    id: str
    ziel: str
    urheber: str
    punkt: tuple[int, int]  # Bildkoordinaten
    bezug: Bildbezug
    schirm: tuple[int, int]  # damals berechneter Bildschirmpunkt
    relativ: tuple[float, float]  # Anteil im Fenster
    knoten_id: str | None  # der Inhalt unter dem Punkt (WorldDOM), wenn es einen gab
    knoten_name: str
    erzeugt_ms: int

    def zu_dict(self) -> dict:
        return {"id": self.id, "ziel": self.ziel, "urheber": self.urheber, "punkt": list(self.punkt), "bild_seq": self.bezug.seq, "schirm": list(self.schirm), "relativ": [round(v, 4) for v in self.relativ],
                "knoten_id": self.knoten_id, "knoten_name": self.knoten_name, "erzeugt_ms": self.erzeugt_ms}


@dataclass
class Pruefung:
    status: str  # gueltig | fensterbindung | neu_aufgeloest | veraltet
    grund: str = ""
    schirm: tuple[int, int] | None = None  # der Punkt, den man jetzt benutzen darf; bei „veraltet“ immer None
    knoten: Knoten | None = None
    warnung: str = ""

    @property
    def benutzbar(self) -> bool:
        return self.status != "veraltet" and self.schirm is not None

    def zu_dict(self) -> dict:
        return {"status": self.status, "grund": self.grund, "schirm": list(self.schirm) if self.schirm else None, "knoten_id": self.knoten.id if self.knoten else None, "warnung": self.warnung}


def erzeugen(ziel: str, punkt: tuple[int, int], bezug: Bildbezug, urheber: str, welt: WeltDom, jetzt_ms: int) -> Zeigegeste:
    """Der Punkt im Bild bekommt, wenn es einen gibt, den kleinsten WorldDOM-Knoten darunter als Inhalt (echte vor erschlossenen, nie erfundene)."""
    schirm = bild_zu_schirm(punkt, bezug)
    kandidaten = [k for k in welt.liste(ziel, nur_aktuell=True, jetzt_ms=jetzt_ms) if k.herkunft in ("real", "inferred") and k.rect and k.rect[0] <= schirm[0] < k.rect[2] and k.rect[1] <= schirm[1] < k.rect[3]]
    # Bedienbares vor bloßem Text (das Etikett im Knopf ist nicht der Knopf), echte vor erschlossenen, dann das Kleinste
    kandidaten.sort(key=lambda k: (0 if {"klick", "text_setzen", "klick_koordinate"} & set(k.faehigkeiten) and k.herkunft == "real" else 1, 0 if k.herkunft == "real" else 1,
                                   (k.rect[2] - k.rect[0]) * (k.rect[3] - k.rect[1])))
    k = kandidaten[0] if kandidaten else None
    r = bezug.rect
    rel = ((schirm[0] - r[0]) / max(1, r[2] - r[0]), (schirm[1] - r[1]) / max(1, r[3] - r[1]))
    return Zeigegeste(f"z-{uuid.uuid4().hex[:8]}", ziel, urheber, punkt, bezug, schirm, rel, k.id if k else None, k.name if k else "", jetzt_ms)


def pruefen(g: Zeigegeste, stand: ZielStand | None, jetzt_ms: int, welt: WeltDom, neu_aufloesen: Callable[[Knoten], Knoten | None] = lambda k: None,
            max_alter_ms: int = MAX_GESTE_ALTER_MS) -> Pruefung:
    if stand is None or not stand.vorhanden or stand.rect is None:
        return Pruefung("veraltet", "ziel_weg", warnung="das Fenster gibt es nicht mehr")
    if stand.minimiert:
        return Pruefung("veraltet", "ziel_minimiert", warnung="das Fenster ist minimiert")
    if stand.generation is not None and g.bezug.generation is not None and stand.generation != g.bezug.generation:
        return Pruefung("veraltet", "ziel_ersetzt", warnung="unter diesem Ziel liegt jetzt ein anderes Fenster")
    if jetzt_ms - g.erzeugt_ms > max_alter_ms:
        return Pruefung("veraltet", "geste_zu_alt", warnung="die Geste ist zu alt; bitte neu zeigen")
    alt = g.bezug.rect
    gleich_gross = (stand.rect[2] - stand.rect[0], stand.rect[3] - stand.rect[1]) == (alt[2] - alt[0], alt[3] - alt[1])
    if stand.rect == alt and (stand.dpi is None or g.bezug.dpi is None or abs(stand.dpi - g.bezug.dpi) < 1e-6):
        return Pruefung("gueltig", "", g.schirm)
    if gleich_gross and (stand.dpi is None or g.bezug.dpi is None or abs(stand.dpi - g.bezug.dpi) < 1e-6):
        punkt = (stand.rect[0] + round(g.relativ[0] * (stand.rect[2] - stand.rect[0])), stand.rect[1] + round(g.relativ[1] * (stand.rect[3] - stand.rect[1])))
        return Pruefung("fensterbindung", "fenster_verschoben", punkt, warnung="das Fenster wurde verschoben; die Geste folgt dem Fenster (nicht dem Inhalt)")
    # Größe oder Maßstab haben sich geändert: das Layout kann sich verschoben haben
    if g.knoten_id is not None:
        alt_knoten = welt.finde(g.knoten_id)
        neu = neu_aufloesen(alt_knoten) if alt_knoten is not None else None
        if neu is not None and neu.rect is not None and neu.herkunft == "real":
            mitte = ((neu.rect[0] + neu.rect[2]) // 2, (neu.rect[1] + neu.rect[3]) // 2)
            return Pruefung("neu_aufgeloest", "inhalt_neu_gefunden", mitte, neu, warnung="das Layout hat sich geändert; die Geste wurde am Inhalt neu aufgelöst")
    return Pruefung("veraltet", "layout_geaendert", warnung="das Layout hat sich geändert und der gemeinte Inhalt ließ sich nicht neu finden — nicht auf den alten Pixel geklickt")


# ---- Zwei getrennte Wege ------------------------------------------------------------------------------------------------------------
def praesentieren(g: Zeigegeste, pruefung: Pruefung, stand: ZielStand | None, overlay_setzen: Callable[[str, tuple[float, float], str], str | None]) -> dict:
    """Ein Zeichen in der gemeinsamen Arbeitsfläche. Die Anwendung wird nicht berührt: das Ergebnis sagt es ausdrücklich. Eine veraltete Geste darf gezeigt werden, aber nur an der alten
    Stelle im Fenster und mit der Warnung (sie behauptet nichts über den jetzigen Inhalt)."""
    if pruefung.benutzbar and stand is not None and stand.rect is not None:
        r = stand.rect
        rel = ((pruefung.schirm[0] - r[0]) / max(1, r[2] - r[0]), (pruefung.schirm[1] - r[1]) / max(1, r[3] - r[1]))
    else:
        rel = g.relativ
    objekt_id = overlay_setzen(g.ziel, rel, f"{g.urheber}: {g.knoten_name or 'hier'}")
    return {"status": "praesentiert" if objekt_id else "fehler", "wirkung_in_anwendung": False, "overlay_objekt": objekt_id, "warnung": pruefung.warnung, "relativ": [round(v, 4) for v in rel],
            "pruefung": pruefung.status}


def einfuegen(g: Zeigegeste, pruefung: Pruefung, *, aktion: str, text: str | None, dienst, haende_klick: Callable[[str, tuple[int, int]], dict] | None) -> dict:
    """Eine echte Handlung in der Anwendung. Veraltete Gesten werden abgelehnt (mit der Warnung), nie auf den alten Pixel ausgeführt."""
    if not pruefung.benutzbar:
        return {"status": "abgelehnt", "grund": pruefung.grund, "wirkung_in_anwendung": False, "warnung": pruefung.warnung}
    knoten_id = pruefung.knoten.id if pruefung.knoten is not None else g.knoten_id
    if knoten_id is not None and dienst is not None and dienst.welt.finde(knoten_id) is not None:
        r = dienst.ausfuehren(g.ziel, knoten_id, aktion, text)
        return {"status": "eingefuegt" if r["status"] == "ausgefuehrt" else r["status"], "grund": r["grund"], "wirkung_in_anwendung": r["status"] == "ausgefuehrt", "beleg": r, "pruefung": pruefung.status}
    if aktion != "klick" or haende_klick is None:
        return {"status": "abgelehnt", "grund": "kein_inhalt_und_nur_klick", "wirkung_in_anwendung": False, "warnung": "ohne Inhalt unter der Geste gibt es nur den Klick auf den Punkt"}
    h = haende_klick(g.ziel, pruefung.schirm)
    return {"status": "eingefuegt" if h.get("status") == "ausgefuehrt" else "abgelehnt", "grund": h.get("grund", ""), "wirkung_in_anwendung": h.get("status") == "ausgefuehrt", "beleg": h, "pruefung": pruefung.status}
