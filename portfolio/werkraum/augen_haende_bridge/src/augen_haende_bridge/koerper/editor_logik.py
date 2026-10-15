"""Die Bedienlogik des Zeichen-Editors (G08), unabhängig von Windows oder Linux: Werkzeuge, Auswahl, Ziehen, Skalieren, Gummiband, Text, Tasten.

Das Fenster leitet nur Maus und Tastatur weiter und zeigt `rendern()`. Alle Koordinaten in Pixeln im Editorfenster (= Gate); das Dokument rechnet in Gate-Koordinaten 0 bis 1.
Jede Änderung geht über die Befehle des Dokuments und ist damit rückgängig zu machen.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image, ImageDraw

from .objekte import MAX_TEXT, Dokument, Objekt, neue_id
from .zeichnen_render import hex_zu_rgba, rendern, text_grenzen

WERKZEUGE = ("auswahl", "text", "freihand", "marker", "linie", "pfeil", "rechteck", "kreis", "radierer")
DECKKRAEFTE = (100, 75, 50, 25)
FARBNAMEN = ("Rot", "Gelb", "Grün", "Cyan", "Blau", "Violett", "Weiß", "Schwarz")
FARBEN = ("#FF0055", "#FFD600", "#00E676", "#00E5FF", "#2979FF", "#B388FF", "#FFFFFF", "#101010")
STAERKEN = (2, 4, 8, 14)
GRIFF_PX = 9
MIN_ZIEHEN_PX = 3  # unter dieser Strecke gilt ein Klick, kein Ziehen
VK_ESC, VK_RETURN, VK_BACK, VK_DELETE, VK_PRIOR, VK_NEXT = 0x1B, 0x0D, 0x08, 0x2E, 0x21, 0x22


@dataclass
class Aktion:
    art: str  # zeichnen, ziehen, skalieren, gummiband, form
    start: tuple[float, float] = (0, 0)
    letzt: tuple[float, float] = (0, 0)
    temp: Objekt | None = None
    anker: tuple[float, float] = (0, 0)  # Skalieren: der gegenüberliegende Punkt (Gate-Koordinaten)
    original: dict = field(default_factory=dict)
    bewegt: bool = False


class Editor:
    def __init__(self, dokument: Dokument, groesse, bei_aenderung=lambda: None, bei_beenden=lambda: None, agenten=lambda: []):
        self.dok = dokument
        self._groesse = groesse  # () -> (Breite, Höhe) in Pixeln
        self._geaendert = bei_aenderung
        self._beenden = bei_beenden
        self._agenten = agenten  # () -> [(tid, name)]: wer in diesem Gate sitzt
        self.werkzeug = "auswahl"
        self.farbe = FARBEN[0]
        self.staerke = STAERKEN[1]
        self.schriftgroesse = 28
        self.fett = self.kursiv = self.unterstrichen = False
        self.deckkraft = 100
        self.radiert: set[str] = set()  # beim Ziehen mit dem Radierer berührt (gelöscht wird beim Loslassen, als EIN Befehl)
        self.kontext_menue = lambda px, py: None  # das Fenster zeigt das Menü (Rechtsklick)
        self.auswahl: set[str] = set()
        self.aktion: Aktion | None = None
        self.text_objekt: Objekt | None = None  # Text, der gerade getippt wird (noch nicht im Dokument), oder ein bearbeiteter
        self.text_bearbeitet_id: str | None = None
        self.neu_bildschirm = True
        self.neu_empfaenger: tuple[str, ...] = ()
        self.hinweis = ""

    # ---- Hilfen ----------------------------------------------------------------------------------------------------
    def _gate(self, px: float, py: float) -> tuple[float, float]:
        b, h = self._groesse()
        return px / max(1, b), py / max(1, h)

    def _px(self, x: float, y: float) -> tuple[float, float]:
        b, h = self._groesse()
        return x * b, y * h

    def _neu(self, art: str, punkte, **kw) -> Objekt:
        return Objekt(neue_id(), art, list(punkte), farbe=self.farbe, staerke=self.staerke, schriftgroesse=self.schriftgroesse,
                      bildschirm=self.neu_bildschirm, empfaenger=self.neu_empfaenger, deckkraft=self.deckkraft, fett=self.fett,
                      kursiv=self.kursiv, unterstrichen=self.unterstrichen, **kw)

    def werkzeug_setzen(self, name: str) -> None:
        if name in WERKZEUGE:
            self._text_abbrechen()
            self.werkzeug = name
            if name != "auswahl":
                self.auswahl.clear()
            self._geaendert()

    def farbe_setzen(self, farbe: str) -> None:
        self.farbe = farbe
        if self.auswahl:
            self.dok.aendern(self.auswahl, farbe=farbe)
        if self.text_objekt is not None:
            self.text_objekt.farbe = farbe
        self._geaendert()

    def staerke_setzen(self, staerke: int) -> None:
        self.staerke = max(1, min(60, staerke))
        if self.auswahl:
            self.dok.aendern(self.auswahl, staerke=self.staerke)
        self._geaendert()

    def schriftgroesse_aendern(self, delta: int) -> None:
        self.schriftgroesse = max(10, min(120, self.schriftgroesse + delta))
        if self.text_objekt is not None:
            self.text_objekt.schriftgroesse = self.schriftgroesse
        auswahl_texte = [i for i in self.auswahl if self.dok.objekte[i].art == "text"]
        if auswahl_texte:
            self.dok.aendern(auswahl_texte, schriftgroesse=self.schriftgroesse)
        self._geaendert()

    def _ziel_ids(self, art: str | None = None) -> list[str]:
        return [i for i in self.auswahl if i in self.dok.objekte and (art is None or self.dok.objekte[i].art == art)]

    def stil_umschalten(self, name: str) -> None:
        """Fett, Kursiv oder Unterstrichen: für den Text im Entstehen, die ausgewählten Texte und alles, was danach geschrieben wird."""
        if name not in ("fett", "kursiv", "unterstrichen"):
            return
        texte = self._ziel_ids("text")
        if texte:
            neu = not all(getattr(self.dok.objekte[i], name) for i in texte)
        elif self.text_objekt is not None:
            neu = not getattr(self.text_objekt, name)
        else:
            neu = not getattr(self, name)
        setattr(self, name, neu)
        if self.text_objekt is not None:
            setattr(self.text_objekt, name, neu)
        if texte:
            self.dok.aendern(texte, **{name: neu})
        self._geaendert()

    def deckkraft_setzen(self, prozent: int) -> None:
        self.deckkraft = max(5, min(100, prozent))
        if self.text_objekt is not None:
            self.text_objekt.deckkraft = self.deckkraft
        if self._ziel_ids():
            self.dok.aendern(self._ziel_ids(), deckkraft=self.deckkraft)
        self._geaendert()

    def groesser(self, faktor: float) -> None:
        """Die Auswahl größer (Faktor > 1) oder kleiner machen."""
        if self._ziel_ids():
            self.dok.groesse_aendern(self._ziel_ids(), faktor)
            self._geaendert()

    # ---- Rechtsklick: Menü für Gemaltes und für die Voreinstellungen -------------------------------------------------
    def rechtsklick(self, px: float, py: float) -> None:
        """Rechtsklick auf ein Objekt wählt es (falls noch nicht gewählt) und öffnet das Menü dafür; auf leerer Fläche das Menü der Voreinstellungen."""
        self._text_festschreiben() if self.text_objekt is not None else None
        x, y = self._gate(px, py)
        treffer = self.dok.treffer(x, y, toleranz=max(0.008, GRIFF_PX / max(1, self._groesse()[0])))
        if treffer is not None:
            mitglieder = set(self.dok.mitglieder(treffer))
            if not mitglieder <= self.auswahl:
                self.auswahl = mitglieder
        elif self.werkzeug == "auswahl":
            self.auswahl.clear()
        self._geaendert()
        self.kontext_menue(int(px), int(py))

    def kontext_eintraege(self) -> list:
        """Das Rechtsklick-Menü als Liste (schluessel, Text, angehakt); None trennt. Gilt für die Auswahl, sonst für neue Objekte."""
        auswahl = self._ziel_ids()
        objs = [self.dok.objekte[i] for i in auswahl]
        texte = [o for o in objs if o.art == "text"]
        e: list = []
        if objs:
            e += [("loeschen", "Löschen", False), ("duplizieren", "Doppeln", False), None,
                  ("gross", "Größer", False), ("klein", "Kleiner", False), ("dick", "Strich dicker", False), ("duenn", "Strich dünner", False), None]
        else:
            e += [(None, "Voreinstellung für neue Objekte", None), None]
        e += [(f"deck:{p}", f"Deckkraft {p} %", (objs[0].deckkraft if objs else self.deckkraft) == p) for p in DECKKRAEFTE] + [None]
        if texte or not objs:
            gesetzt = (lambda n: all(getattr(o, n) for o in texte)) if texte else (lambda n: getattr(self, n))
            e += [("fett", "Fett", gesetzt("fett")), ("kursiv", "Kursiv", gesetzt("kursiv")), ("unterstrichen", "Unterstrichen", gesetzt("unterstrichen")),
                  ("schrift+", "Schrift größer", False), ("schrift-", "Schrift kleiner", False), None]
        e += [(f"farbe:{i}", f"Farbe {name}", False) for i, name in enumerate(FARBNAMEN)] + [None]
        if objs:
            e += [("vor", "Nach vorn", False), ("zurueck", "Nach hinten", False), ("aus", "Ausblenden", False)]
        return e

    def kontext_ausfuehren(self, schluessel: str) -> None:
        if schluessel == "loeschen":
            self.loeschen()
        elif schluessel == "duplizieren":
            self.duplizieren()
        elif schluessel == "gross":
            self.groesser(1.25)
        elif schluessel == "klein":
            self.groesser(0.8)
        elif schluessel == "dick":
            self.staerke_setzen(min(60, self.staerke + 2) if not self._ziel_ids() else min(60, self.dok.objekte[self._ziel_ids()[0]].staerke + 2))
        elif schluessel == "duenn":
            self.staerke_setzen(max(1, self.staerke - 2) if not self._ziel_ids() else max(1, self.dok.objekte[self._ziel_ids()[0]].staerke - 2))
        elif schluessel.startswith("deck:"):
            self.deckkraft_setzen(int(schluessel[5:]))
        elif schluessel in ("fett", "kursiv", "unterstrichen"):
            self.stil_umschalten(schluessel)
        elif schluessel == "schrift+":
            self.schriftgroesse_aendern(4)
        elif schluessel == "schrift-":
            self.schriftgroesse_aendern(-4)
        elif schluessel.startswith("farbe:"):
            self.farbe_setzen(FARBEN[int(schluessel[6:])])
        elif schluessel in ("vor", "zurueck"):
            self.ordnung(schluessel)
        elif schluessel == "aus":
            self.ausblenden()

    # ---- Empfänger der Auswahl und neuer Objekte -----------------------------------------------------------------------
    def empfaenger_umschalten(self, tid: str) -> None:
        """Agent in die Empfängerliste der Auswahl (oder der neuen Objekte) aufnehmen oder entfernen."""
        ziele = [self.dok.objekte[i] for i in self.auswahl] if self.auswahl else None
        if ziele:
            alle_drin = all(tid in o.empfaenger for o in ziele)
            for o in ziele:
                neu = tuple(e for e in o.empfaenger if e != tid) if alle_drin else tuple(dict.fromkeys((*o.empfaenger, tid)))
                self.dok.aendern([o.id], empfaenger=neu)
        else:
            self.neu_empfaenger = (tuple(e for e in self.neu_empfaenger if e != tid) if tid in self.neu_empfaenger
                                   else (*self.neu_empfaenger, tid))
        self._geaendert()

    def bildschirm_umschalten(self) -> None:
        ziele = [self.dok.objekte[i] for i in self.auswahl]
        if ziele:
            neu = not all(o.bildschirm for o in ziele)
            self.dok.aendern(self.auswahl, bildschirm=neu)
        else:
            self.neu_bildschirm = not self.neu_bildschirm
        self._geaendert()

    def empfaenger_stand(self) -> tuple[bool, tuple[str, ...]]:
        """Was die Auswahl (sonst die neuen Objekte) gerade ist: (auf dem Bildschirm, Empfänger, die ALLE haben)."""
        if self.auswahl:
            ziele = [self.dok.objekte[i] for i in self.auswahl]
            gemeinsam = set(ziele[0].empfaenger)
            for o in ziele[1:]:
                gemeinsam &= set(o.empfaenger)
            return all(o.bildschirm for o in ziele), tuple(sorted(gemeinsam))
        return self.neu_bildschirm, self.neu_empfaenger

    # ---- Maus ------------------------------------------------------------------------------------------------------
    def maus_runter(self, px: float, py: float, umschalt: bool = False, doppelt: bool = False) -> None:
        x, y = self._gate(px, py)
        if self.text_objekt is not None:
            self._text_festschreiben()
        if self.werkzeug == "auswahl":
            self._auswahl_runter(px, py, x, y, umschalt, doppelt)
        elif self.werkzeug == "radierer":
            self.radiert = set()
            self.aktion = Aktion("radieren", (x, y), (x, y))
            self._radieren_bei(x, y)
            self._geaendert()
        elif self.werkzeug == "text":
            self.text_objekt = self._neu("text", [(x, y)], text="")
            self.text_bearbeitet_id = None
            self._geaendert()
        elif self.werkzeug in ("freihand", "marker"):
            temp = self._neu(self.werkzeug, [(x, y)])
            self.aktion = Aktion("zeichnen", (x, y), (x, y), temp)
            self._geaendert()
        else:  # linie, pfeil, rechteck, kreis: Anfangs- und Endpunkt
            temp = self._neu(self.werkzeug, [(x, y), (x, y)])
            self.aktion = Aktion("form", (x, y), (x, y), temp)
            self._geaendert()

    def _radieren_bei(self, x: float, y: float) -> None:
        treffer = self.dok.treffer(x, y, toleranz=max(0.008, GRIFF_PX / max(1, self._groesse()[0])))
        if treffer is not None:
            self.radiert |= set(self.dok.mitglieder(treffer))

    def _griff_bei(self, px: float, py: float) -> tuple[float, float] | None:
        """Der Anker (gegenüberliegende Ecke), wenn ein Skaliergriff der Einzelauswahl getroffen wird."""
        if len(self.auswahl) != 1:
            return None
        o = self.dok.objekte[next(iter(self.auswahl))]
        if o.art in ("freihand", "marker", "text"):
            return None  # nur Formen und Bilder haben Griffe
        l, t, r, u = o.grenzen()
        for ecke_x, ecke_y, anker in ((l, t, (r, u)), (r, t, (l, u)), (l, u, (r, t)), (r, u, (l, t))):
            ex, ey = self._px(ecke_x, ecke_y)
            if abs(px - ex) <= GRIFF_PX and abs(py - ey) <= GRIFF_PX:
                return anker
        return None

    def _auswahl_runter(self, px, py, x, y, umschalt, doppelt) -> None:
        anker = self._griff_bei(px, py)
        if anker is not None:
            ids = list(self.auswahl)
            self.aktion = Aktion("skalieren", (x, y), (x, y), anker=anker, original=self.dok._stand(self.dok._mit_gruppen(ids)))
            return
        treffer = self.dok.treffer(x, y, toleranz=max(0.008, GRIFF_PX / max(1, self._groesse()[0])))
        if doppelt and treffer and self.dok.objekte[treffer].art == "text":
            self._text_bearbeiten(treffer)
            return
        if treffer is None:
            if not umschalt:
                self.auswahl.clear()
            self.aktion = Aktion("gummiband", (x, y), (x, y))
            self._geaendert()
            return
        mitglieder = set(self.dok.mitglieder(treffer))
        if umschalt:
            self.auswahl = self.auswahl - mitglieder if mitglieder <= self.auswahl else self.auswahl | mitglieder
        elif not mitglieder <= self.auswahl:
            self.auswahl = mitglieder
        self.aktion = Aktion("ziehen", (x, y), (x, y), original=self.dok._stand(self.dok._mit_gruppen(self.auswahl)))
        self._geaendert()

    def maus_bewegt(self, px: float, py: float) -> None:
        a = self.aktion
        if a is None:
            return
        x, y = self._gate(px, py)
        a.letzt = (x, y)
        if a.art == "zeichnen" and a.temp is not None:
            if (x, y) != a.temp.punkte[-1]:
                a.temp.punkte.append((x, y))
            a.bewegt = True
        elif a.art == "form" and a.temp is not None:
            a.temp.punkte[-1] = (x, y)
            a.bewegt = True
        elif a.art == "ziehen":
            a.bewegt = a.bewegt or abs(px - self._px(*a.start)[0]) + abs(py - self._px(*a.start)[1]) >= MIN_ZIEHEN_PX
        elif a.art == "skalieren":
            a.bewegt = True
        elif a.art == "radieren":
            self._radieren_bei(x, y)
            a.bewegt = True
        self._geaendert()

    def maus_hoch(self, px: float, py: float) -> None:
        a, self.aktion = self.aktion, None
        if a is None:
            return
        x, y = self._gate(px, py)
        if a.art in ("zeichnen", "form") and a.temp is not None:
            if a.art == "zeichnen" and len(a.temp.punkte) < 2:
                a.temp.punkte.append((x, y))  # ein Klick ergibt einen Punkt
            if a.art == "form":
                if abs(x - a.start[0]) * self._groesse()[0] + abs(y - a.start[1]) * self._groesse()[1] < MIN_ZIEHEN_PX:
                    self._geaendert()
                    return  # ein Klick ohne Ziehen malt keine Form
                a.temp.punkte[-1] = (x, y)
            self.dok.hinzufuegen(a.temp)
            self.auswahl = set()
        elif a.art == "ziehen" and a.bewegt:
            dx, dy = x - a.start[0], y - a.start[1]
            ids = list(a.original)
            self.dok._anwenden(a.original)  # zurück auf den Stand vor dem Ziehen, dann als EIN Befehl verschieben
            self.dok.verschieben(ids, dx, dy)
        elif a.art == "skalieren":
            ids = list(a.original)
            self.dok._anwenden(a.original)
            ax, ay = a.anker
            sx, sy = a.start[0] - ax, a.start[1] - ay
            fx = (x - ax) / sx if abs(sx) > 1e-6 else 1.0
            fy = (y - ay) / sy if abs(sy) > 1e-6 else 1.0
            if fx > 0.02 and fy > 0.02:
                self.dok.skalieren(ids, fx, fy, a.anker)
        elif a.art == "radieren":
            if self.radiert:
                self.dok.entfernen(self.radiert)  # alles, was berührt wurde, in einem Schritt (ein Strg+Z holt es zurück)
            self.radiert = set()
            self.auswahl &= set(self.dok.objekte)
        elif a.art == "gummiband":
            l, t, r, u = min(a.start[0], x), min(a.start[1], y), max(a.start[0], x), max(a.start[1], y)
            if (r - l) * self._groesse()[0] + (u - t) * self._groesse()[1] >= MIN_ZIEHEN_PX:
                gefunden = set(self.dok.im_rechteck(l, t, r, u))
                self.auswahl = (self.auswahl | gefunden) if self.auswahl else gefunden
                self.auswahl = set(self.dok._mit_gruppen(self.auswahl))
        self._geaendert()

    # ---- Text ------------------------------------------------------------------------------------------------------
    def _text_bearbeiten(self, objekt_id: str) -> None:
        o = self.dok.objekte[objekt_id]
        self.text_objekt = o.kopie()  # der Editor zeigt solange die Arbeitskopie statt des Objekts
        self.text_bearbeitet_id = objekt_id
        self.auswahl = {objekt_id}
        self._geaendert()

    def zeichen(self, code: int) -> None:
        """Ein getipptes Zeichen (WM_CHAR); nur wenn gerade ein Text entsteht."""
        if self.text_objekt is None:
            return
        if code == 0x0D:
            self._text_festschreiben()
        elif code == 0x08:
            self.text_objekt.text = self.text_objekt.text[:-1]
        elif code == 0x0A:
            self.text_objekt.text += "\n"
        elif code >= 0x20 and len(self.text_objekt.text) < MAX_TEXT:
            self.text_objekt.text += chr(code)
        self._geaendert()

    def _text_festschreiben(self) -> None:
        o, self.text_objekt = self.text_objekt, None
        bearbeitet, self.text_bearbeitet_id = self.text_bearbeitet_id, None
        if o is None:
            return
        if bearbeitet is not None and bearbeitet in self.dok.objekte:
            if o.text.strip():
                self.dok.aendern([bearbeitet], text=o.text)
            else:
                self.dok.entfernen([bearbeitet])  # leer gemacht = gelöscht
        elif o.text.strip():
            self.dok.hinzufuegen(o)
        self._geaendert()

    def _text_abbrechen(self) -> None:
        bearbeitet, self.text_bearbeitet_id = self.text_bearbeitet_id, None
        self.text_objekt = None

    # ---- Tasten ----------------------------------------------------------------------------------------------------
    def taste(self, vk: int, strg: bool = False, umschalt: bool = False) -> bool:
        """Liefert, ob die Taste verbraucht wurde."""
        if vk == VK_ESC:
            if self.text_objekt is not None:
                self._text_abbrechen()
                self._geaendert()
            elif self.aktion is not None:
                self.aktion = None
                self._geaendert()
            elif self.auswahl:
                self.auswahl.clear()
                self._geaendert()
            else:
                self._beenden()  # nichts mehr abzubrechen: Esc verlässt den Zeichenmodus
            return True
        if self.text_objekt is not None:
            return False  # Tasten gehören dem Text (WM_CHAR liefert die Zeichen)
        if strg and vk == ord("Z"):
            self.rueckgaengig()
        elif strg and vk == ord("Y"):
            self.wiederholen()
        elif strg and vk == ord("G"):
            self.aufloesen() if umschalt else self.gruppieren()
        elif strg and vk == ord("D"):
            self.duplizieren()
        elif strg and vk == ord("A"):
            self.auswahl = set(self.dok.objekte)
            self._geaendert()
        elif vk == VK_DELETE:
            self.loeschen()
        elif vk == VK_PRIOR:
            self.ordnung("ganz_vor" if strg else "vor")
        elif vk == VK_NEXT:
            self.ordnung("ganz_zurueck" if strg else "zurueck")
        else:
            return False
        return True

    # ---- Befehle auf die Auswahl ---------------------------------------------------------------------------------
    def rueckgaengig(self) -> None:
        self._text_abbrechen()
        if self.dok.rueckgaengig():
            self.auswahl &= set(self.dok.objekte)
            self._geaendert()

    def wiederholen(self) -> None:
        if self.dok.wiederholen():
            self.auswahl &= set(self.dok.objekte)
            self._geaendert()

    def loeschen(self) -> None:
        if self.auswahl:
            self.dok.entfernen(self.dok._mit_gruppen(self.auswahl))
            self.auswahl.clear()
            self._geaendert()

    def gruppieren(self) -> None:
        if len(self.auswahl) >= 2:
            self.dok.gruppieren(self.auswahl)
            self._geaendert()

    def aufloesen(self) -> None:
        if self.auswahl:
            self.dok.aufloesen(self.auswahl)
            self._geaendert()

    def duplizieren(self) -> None:
        if self.auswahl:
            self.auswahl = set(self.dok.duplizieren(self.auswahl))
            self._geaendert()

    def ordnung(self, wie: str) -> None:
        if self.auswahl:
            self.dok.ordnung(self.auswahl, wie)
            self._geaendert()

    def ausblenden(self) -> None:
        """Ausgewählte Objekte ausblenden (sie bleiben gespeichert und lassen sich über „alle einblenden“ zurückholen)."""
        if self.auswahl:
            self.dok.aendern(self.auswahl, sichtbar=False)
            self.auswahl.clear()
            self._geaendert()

    def alle_einblenden(self) -> None:
        versteckt = [i for i, o in self.dok.objekte.items() if not o.sichtbar]
        if versteckt:
            self.dok.aendern(versteckt, sichtbar=True)
            self._geaendert()

    def bild_einfuegen(self, png: bytes, bild_breite: int, bild_hoehe: int) -> str | None:
        """Ein Bild (PNG-Bytes) in die Mitte des Gates, höchstens halb so groß wie das Gate, mit dem Seitenverhältnis des Bildes."""
        gb, gh = self._groesse()
        faktor = min(0.5 * gb / max(1, bild_breite), 0.5 * gh / max(1, bild_hoehe), 1.0)
        b, h = bild_breite * faktor / gb, bild_hoehe * faktor / gh
        o = self._neu("bild", [(0.5 - b / 2, 0.5 - h / 2), (0.5 + b / 2, 0.5 + h / 2)], bild=png)
        neu_id = self.dok.hinzufuegen(o)
        if neu_id:
            self.auswahl = {neu_id}
            self._geaendert()
        return neu_id

    # ---- Anzeige ---------------------------------------------------------------------------------------------------
    def vorschau_objekte(self) -> list[Objekt]:
        """Alles, was der Editor zeigt: das Dokument (ohne das gerade bearbeitete Objekt), das, was gerade gezeichnet wird, und der Text im Entstehen."""
        objekte = [o for o in self.dok.sortiert() if o.sichtbar and o.id != self.text_bearbeitet_id]
        if self.aktion is not None and self.aktion.temp is not None:
            objekte.append(self.aktion.temp)
        if self.aktion is not None and self.aktion.art in ("ziehen", "skalieren") and self.aktion.bewegt:
            objekte = self._mit_bewegung(objekte)
        if self.text_objekt is not None:
            objekte.append(self.text_objekt)
        return objekte

    def _mit_bewegung(self, objekte: list[Objekt]) -> list[Objekt]:
        a = self.aktion
        x, y = a.letzt
        ergebnis = []
        for o in objekte:
            if o.id in a.original and a.original[o.id] is not None:
                kopie = o.kopie()
                if a.art == "ziehen":
                    dx, dy = x - a.start[0], y - a.start[1]
                    kopie.punkte = [(px_ + dx, py_ + dy) for px_, py_ in a.original[o.id].punkte]
                else:
                    ax, ay = a.anker
                    sx, sy = a.start[0] - ax, a.start[1] - ay
                    fx = (x - ax) / sx if abs(sx) > 1e-6 else 1.0
                    fy = (y - ay) / sy if abs(sy) > 1e-6 else 1.0
                    if fx > 0.02 and fy > 0.02:
                        kopie.punkte = [(ax + (px_ - ax) * fx, ay + (py_ - ay) * fy) for px_, py_ in a.original[o.id].punkte]
                ergebnis.append(kopie)
            else:
                ergebnis.append(o)
        return ergebnis

    def rendern(self, breite: int, hoehe: int) -> Image.Image:
        """Das Bild des Editors: alle Objekte (Objekte nur für Agenten leicht abgeblendet) plus Auswahlrahmen, Griffe, Gummiband, Textrahmen."""
        objekte = self.vorschau_objekte()
        bild = Image.new("RGBA", (max(1, breite), max(1, hoehe)), (0, 0, 0, 0))
        privat = [o for o in objekte if not o.bildschirm]
        sichtbar_physisch = [o for o in objekte if o.bildschirm]
        bild.alpha_composite(rendern(sichtbar_physisch, breite, hoehe))
        if privat:  # nur für Agenten bestimmte Objekte: Daniel sieht sie hier etwas blasser (sie stehen nicht auf dem Bildschirm)
            ebene = rendern(privat, breite, hoehe)
            ebene.putalpha(ebene.getchannel("A").point(lambda v: int(v * 0.72)))
            bild.alpha_composite(ebene)
        z = ImageDraw.Draw(bild)
        for i in self.auswahl:
            o = next((x for x in objekte if x.id == i), None)
            if o is None:
                continue
            l, t, r, u = o.grenzen()
            l, t, r, u = l * breite, t * hoehe, r * breite, u * hoehe
            if o.art == "text":
                tb, th = text_grenzen(o.text, o.schriftgroesse, breite, hoehe, o.fett, o.kursiv)
                r, u = l + tb * breite, t + th * hoehe
            pad = 4
            z.rectangle((l - pad, t - pad, r + pad, u + pad), outline=(255, 255, 255, 230), width=1)
            z.rectangle((l - pad - 1, t - pad - 1, r + pad + 1, u + pad + 1), outline=(0, 0, 0, 160), width=1)
            if len(self.auswahl) == 1 and o.art not in ("freihand", "marker", "text"):
                for gx, gy in ((l, t), (r, t), (l, u), (r, u)):
                    z.rectangle((gx - 4, gy - 4, gx + 4, gy + 4), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        for i in self.radiert:  # berührt: roter Rahmen, gleich weg
            o = next((x for x in objekte if x.id == i), None)
            if o is not None:
                l, t, r, u = (v * f for v, f in zip(o.grenzen(), (breite, hoehe, breite, hoehe)))
                z.rectangle((l - 5, t - 5, r + 5, u + 5), outline=(255, 60, 60, 255), width=2)
        a = self.aktion
        if a is not None and a.art == "gummiband":
            (x1, y1), (x2, y2) = self._px(*a.start), self._px(*a.letzt)
            z.rectangle((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)), outline=(120, 200, 255, 255), fill=(120, 200, 255, 40))
        if self.text_objekt is not None:
            x, y = self._px(*self.text_objekt.punkte[0])
            tb, th = text_grenzen(self.text_objekt.text + "|", self.text_objekt.schriftgroesse, breite, hoehe, self.text_objekt.fett, self.text_objekt.kursiv)
            z.rectangle((x - 3, y - 3, x + tb * breite + 6, y + th * hoehe + 6), outline=hex_zu_rgba(self.text_objekt.farbe, 200), width=1)
            z.line((x + max(0, tb * breite - 2), y, x + max(0, tb * breite - 2), y + th * hoehe), fill=(255, 255, 255, 255), width=2)
        return bild
