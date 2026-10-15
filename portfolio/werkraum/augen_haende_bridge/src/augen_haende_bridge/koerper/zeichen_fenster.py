"""Die Fenster des Zeichenmodus (G08): die Editorfläche über dem Gate und die Werkzeugleiste.

Beide sind aus der Bildschirmaufnahme ausgenommen, wo Windows das kann: so stehen Daniels Entwürfe und die nur für Agenten bestimmten Objekte nicht in
den Bildern der Agenten. Kann Windows es nicht, zeigt die Editorfläche die nur für Agenten bestimmten Objekte nicht (sonst würden sie durchsickern)
und sagt das. Die Bedienung selbst steckt in `editor_logik.py`; hier wird nur Maus und Tastatur weitergereicht und gezeigt.
"""

from __future__ import annotations

from collections.abc import Callable

from PIL import Image, ImageDraw

from . import stil
from . import win32 as w
from .editor_logik import DECKKRAEFTE, FARBEN, STAERKEN, WERKZEUGE, Editor
from .fenster import Fenster, Leinwand, Schrift
from .pixel_fenster import PixelFenster

MK_LBUTTON, MK_SHIFT = 0x0001, 0x0004
WERKZEUG_TEXT = {"auswahl": "Wahl", "text": "Text", "freihand": "Stift", "marker": "Marker", "linie": "Linie", "pfeil": "Pfeil",
                 "rechteck": "Rechteck", "kreis": "Kreis", "radierer": "Radierer"}
STIL_TEXT = {"fett": "F", "kursiv": "K", "unterstrichen": "U", "schrift-": "A−", "schrift+": "A+"}
ICON_B = 18
PAD, KNOPF_H, LUECKE = 6, 24, 4


class ZeichenFenster(PixelFenster):
    """Die Fläche, auf der Daniel zeichnet. Leicht abgedunkelt (damit sie jeden Klick fängt und man den Modus sieht), mit farbigem Rand."""

    klasse = "AuHZeichnen"

    def __init__(self, rechteck: tuple[int, int, int, int], editor: Editor, *, farbe_hex: str = "#00E5FF", privat_zeigen: Callable[[], bool] = lambda: True,
                 modifikator: Callable[[], bool] | None = None):
        links, oben, rechts, unten = rechteck
        self.editor = editor
        self._farbe = farbe_hex
        self._privat_zeigen = privat_zeigen
        self._modifikator = modifikator  # die Bedientaste (Strg+Alt): Rechtsklick öffnet das Menü nur mit ihr, wie bei allen Bridge-Elementen
        self.hinweis = ""
        super().__init__(links, oben, max(40, rechts - links), max(40, unten - oben), titel="Zeichnen", durchklickbar=False, nicht_aktivieren=False)
        self.leck_schutz = self.aufnahme_ausnehmen(True)  # nur dann dürfen nur-für-Agenten-Objekte hier erscheinen
        self.neu()

    def neu(self) -> None:
        b, h = self.clientgroesse()
        if b <= 0 or h <= 0:
            return
        grund = Image.new("RGBA", (b, h), (0, 0, 0, 5))
        ebene = self.editor.rendern(b, h) if self.leck_schutz else self._ohne_privates(b, h)
        grund.alpha_composite(ebene)
        z = ImageDraw.Draw(grund)
        z.rectangle((0, 0, b - 1, h - 1), outline=ImageDraw.ImageColor.getrgb(self._farbe) + (230,), width=3)  # Rand: der Zeichenmodus ist an
        if not self.leck_schutz:
            z.text((12, 8), "Windows nimmt die Ausnahme aus der Aufnahme nicht an: Objekte nur für Agenten werden hier nicht gezeigt", fill=(255, 220, 120, 255))
        if self.hinweis:
            z.text((12, 28 if not self.leck_schutz else 8), self.hinweis, fill=(255, 235, 150, 255))
        self.setze_rgba(grund)

    def _ohne_privates(self, b: int, h: int) -> Image.Image:
        """Editorbild ohne die Objekte, die nur für Agenten bestimmt sind (sie dürfen nicht im Bildschirmbild stehen)."""
        dok = self.editor.dok
        versteckt = [o for o in dok.objekte.values() if not o.bildschirm and o.sichtbar]
        for o in versteckt:
            o.sichtbar = False
        try:
            return self.editor.rendern(b, h)
        finally:
            for o in versteckt:
                o.sichtbar = True

    def _umschalt(self) -> bool:
        return bool(w.user32.GetKeyState(w.VK_SHIFT) & 0x8000)

    def _strg(self) -> bool:
        return bool(w.user32.GetKeyState(w.VK_CONTROL) & 0x8000)

    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        self.erfasse_maus()
        if self.hinweis:
            self.hinweis = ""
        self.editor.maus_runter(x, y, umschalt=bool(flags & MK_SHIFT))
        return 0

    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None:
        if self._modifikator is None or self._modifikator():
            self.hinweis = ""
            self.editor.rechtsklick(x, y)
        else:
            self.hinweis = "Rechtsklick-Menü: Bedientaste halten (Strg+Alt) und rechtsklicken"
            self.neu()
        return 0

    def bei_doppelklick(self, x: int, y: int, flags: int) -> int | None:
        self.erfasse_maus()
        self.editor.maus_runter(x, y, umschalt=bool(flags & MK_SHIFT), doppelt=True)
        return 0

    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None:
        if flags & MK_LBUTTON:
            self.editor.maus_bewegt(x, y)
        return 0

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        self.gib_maus_frei()
        self.editor.maus_hoch(x, y)
        return 0

    def bei_taste(self, vk: int, lparam: int, syskey: bool) -> int | None:
        if vk in (w.VK_SHIFT, w.VK_CONTROL, w.VK_MENU):
            return 0
        self.editor.taste(vk, strg=self._strg(), umschalt=self._umschalt())
        return 0  # nichts geht an die Programme darunter

    def bei_zeichen(self, code: int, syskey: bool) -> int | None:
        self.editor.zeichen(code)
        return 0

    def bei_nachricht(self, msg: int, wparam: int, lparam: int) -> int | None:
        if msg == w.WM_SETCURSOR and w.loword(lparam) == w.HTCLIENT:
            self.mauszeiger(w.IDC_IBEAM if self.editor.werkzeug == "text" else w.IDC_ARROW)
            return 1
        return None


class WerkzeugLeiste(Fenster):
    """Werkzeuge, Farben, Stärken, Befehle und „Sichtbar für …“. Nimmt nie den Fokus (die Tastatur bleibt bei der Zeichenfläche)."""

    klasse = "AuHWerkzeuge"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    BEFEHLE = (("rueck", "Rückg."), ("wied", "Wied."), ("loesch", "Löschen"), ("dupl", "Doppeln"), ("gruppe", "Gruppe"), ("aufloes", "Trennen"),
               ("gross", "Größer"), ("klein", "Kleiner"),
               ("vor", "Nach vorn"), ("zurueck", "Nach hinten"), ("aus", "Ausblenden"), ("ein", "Alle ein"), ("bild", "Bild …"),
               ("sicht", "Sichtbar für …"), ("ziel", "Ziel …"), ("fertig", "Fertig"))

    def __init__(self, x: int, y: int, editor: Editor, *, bild_waehlen: Callable[[], None] = lambda: None,
                 sichtbar_menue: Callable[[int, int], None] = lambda x, y: None, ziel_menue: Callable[[int, int], None] = lambda x, y: None,
                 fertig: Callable[[], None] = lambda: None):
        w.require_windows()
        self.editor = editor
        self._bild, self._sichtbar, self._ziel, self._fertig = bild_waehlen, sichtbar_menue, ziel_menue, fertig
        self._unten: str | None = None
        self.f_text: Schrift | None = None
        self._schrift_bauen()
        self._rechtecke = self._layout()
        breite = max(r[2] for r in self._rechtecke.values()) + PAD
        hoehe = max(r[3] for r in self._rechtecke.values()) + PAD
        super().__init__(x, y, breite, hoehe, titel="Werkzeuge", deckkraft=stil.deckkraft_alpha(96), nicht_aktivieren=True)
        self.aufnahme_ausnehmen(True)

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_text = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(12, 1.0), fest=False)
            self._text_breiten = {n: self.f_text.breite(hdc, t) for n, t in [*WERKZEUG_TEXT.items(), *self.BEFEHLE, *STIL_TEXT.items()]}
            self._text_breiten.update({f"d{p}": self.f_text.breite(hdc, f"{p}%") for p in DECKKRAEFTE})
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def _layout(self) -> dict[str, tuple[int, int, int, int]]:
        """Drei Zeilen: Werkzeuge; Farben und Stärken; Befehle. Rechtecke in Fensterkoordinaten, Name → (l, o, r, u)."""
        r: dict[str, tuple[int, int, int, int]] = {}
        x, y = PAD, PAD
        for name in WERKZEUGE:
            b = self._text_breiten[name] + 16 + ICON_B
            r[f"w:{name}"] = (x, y, x + b, y + KNOPF_H)
            x += b + LUECKE
        breite_zeile1 = x
        x, y = PAD, y + KNOPF_H + LUECKE
        for i, _f in enumerate(FARBEN):
            r[f"f:{i}"] = (x, y, x + KNOPF_H, y + KNOPF_H)
            x += KNOPF_H + LUECKE
        x += 8
        for i, s in enumerate(STAERKEN):
            r[f"s:{i}"] = (x, y, x + KNOPF_H + 6, y + KNOPF_H)
            x += KNOPF_H + 6 + LUECKE
        breite_zeile2 = x
        x, y = PAD, y + KNOPF_H + LUECKE  # Zeile 3: Text-Stil, Schriftgröße, Deckkraft
        for name in STIL_TEXT:
            b = max(KNOPF_H, self._text_breiten[name] + 14)
            r[f"t:{name}"] = (x, y, x + b, y + KNOPF_H)
            x += b + LUECKE
        x += 8
        for p in DECKKRAEFTE:
            b = self._text_breiten[f"d{p}"] + 14
            r[f"d:{p}"] = (x, y, x + b, y + KNOPF_H)
            x += b + LUECKE
        x, y = PAD, y + KNOPF_H + LUECKE
        for name, text in self.BEFEHLE:
            b = self._text_breiten[name] + 14
            if x + b > max(breite_zeile1, breite_zeile2, 560):
                x, y = PAD, y + KNOPF_H + LUECKE
            r[f"b:{name}"] = (x, y, x + b, y + KNOPF_H)
            x += b + LUECKE
        return r

    # ---- Zeichnen -----------------------------------------------------------------------------------------------------
    def zeichnen(self, l: Leinwand) -> None:
        breite, hoehe = l.breite, l.hoehe
        l.fuellen(stil.FARBE_LEISTE)
        l.rahmen(0, 0, breite, hoehe, stil.FARBE_TEXT_GEDAEMPFT, 1)
        ed = self.editor
        for schluessel, (a, b, c, d) in self._rechtecke.items():
            art, _, name = schluessel.partition(":")
            aktiv = ((art == "w" and ed.werkzeug == name) or (art == "f" and FARBEN[int(name)] == ed.farbe) or (art == "s" and STAERKEN[int(name)] == ed.staerke)
                     or (art == "t" and self._stil_an(name)) or (art == "d" and int(name) == ed.deckkraft))
            if art == "f":
                l.fuellen(w.rgb_hex(FARBEN[int(name)]), a, b, c, d)
                l.rahmen(a, b, c, d, stil.FARBE_TEXT if aktiv else stil.FARBE_GRUND, 3 if aktiv else 1)
                continue
            gedrueckt = self._unten == schluessel
            l.fuellen(stil.FARBE_KNOPF_AKTIV if (aktiv or gedrueckt) else stil.FARBE_KNOPF, a, b, c, d)
            if art == "s":
                dicke = STAERKEN[int(name)]
                mitte_y = (b + d) // 2
                l.fuellen(stil.FARBE_TEXT, a + 6, mitte_y - min(dicke, 14) // 2, c - 6, mitte_y + (min(dicke, 14) + 1) // 2)
                continue
            if art == "t":
                text = STIL_TEXT[name]
            elif art == "d":
                text = f"{name}%"
            else:
                text = WERKZEUG_TEXT[name] if art == "w" else dict(self.BEFEHLE)[name]
            breite_text = self._text_breiten[name if art != "d" else f"d{name}"]
            icon_platz = ICON_B if art == "w" else 0
            if art == "w":
                self._icon(l, name, a + 5, b + (d - b - 14) // 2)
            ausgegraut = (art == "b" and ((name == "rueck" and not ed.dok.kann_rueckgaengig) or (name == "wied" and not ed.dok.kann_wiederholen)))
            l.text(a + icon_platz + (c - a - icon_platz - breite_text) // 2, b + (d - b - self.f_text.zellhoehe) // 2, text,
                   stil.FARBE_TEXT_GEDAEMPFT if ausgegraut else stil.FARBE_TEXT, self.f_text)

    def _stil_an(self, name: str) -> bool:
        ed = self.editor
        if name.startswith("schrift"):
            return False
        texte = [ed.dok.objekte[i] for i in ed.auswahl if i in ed.dok.objekte and ed.dok.objekte[i].art == "text"]
        if texte:
            return all(getattr(o, name) for o in texte)
        return bool((ed.text_objekt or ed).__dict__.get(name, False))

    def _icon(self, l: Leinwand, art: str, x: int, y: int) -> None:
        """Ein kleines Symbol (14×14) links im Werkzeugknopf, damit man die Werkzeuge ohne Lesen erkennt."""
        f, g = stil.FARBE_TEXT, stil.FARBE_TEXT_GEDAEMPFT
        if art == "auswahl":  # Mauszeiger
            l.polygon([(x + 1, y), (x + 1, y + 12), (x + 4, y + 9), (x + 7, y + 14), (x + 9, y + 13), (x + 6, y + 8), (x + 11, y + 8)], f, g, 1)
        elif art == "text":
            l.fuellen(f, x + 1, y + 1, x + 13, y + 4)
            l.fuellen(f, x + 6, y + 1, x + 9, y + 14)
        elif art == "freihand":
            for (a, b), (c, d) in zip([(0, 11), (4, 4), (8, 11), (12, 3)], [(4, 4), (8, 11), (12, 3), (14, 6)]):
                l.linie(x + a, y + b, x + c, y + d, f, 2)
        elif art == "marker":
            l.fuellen(w.rgb_hex("#FFD600"), x, y + 4, x + 14, y + 11)
            l.rahmen(x, y + 4, x + 14, y + 11, g, 1)
        elif art == "linie":
            l.linie(x + 1, y + 13, x + 13, y + 1, f, 2)
        elif art == "pfeil":
            l.linie(x + 1, y + 13, x + 12, y + 2, f, 2)
            l.polygon([(x + 14, y), (x + 5, y + 2), (x + 12, y + 9)], f)
        elif art == "rechteck":
            l.rahmen(x + 1, y + 2, x + 14, y + 13, f, 2)
        elif art == "kreis":
            import math
            l.polygon([(round(x + 7 + 6 * math.cos(i * math.pi / 8)), round(y + 7 + 6 * math.sin(i * math.pi / 8))) for i in range(16)], stil.FARBE_KNOPF, f, 2)
        elif art == "radierer":
            l.polygon([(x + 1, y + 9), (x + 8, y + 1), (x + 14, y + 6), (x + 8, y + 13), (x + 4, y + 13)], w.rgb_hex("#FF8A80"), f, 1)

    def treffer(self, x: int, y: int) -> int | None:
        links, oben, _r, _u = self.rechteck()
        cx, cy = x - links, y - oben
        if any(a <= cx < c and b <= cy < d for a, b, c, d in self._rechtecke.values()):
            return w.HTCLIENT
        return w.HTCAPTION  # an den Rändern lässt sich die Leiste verschieben

    def _knopf_bei(self, x: int, y: int) -> str | None:
        for schluessel, (a, b, c, d) in self._rechtecke.items():
            if a <= x < c and b <= y < d:
                return schluessel
        return None

    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        self._unten = self._knopf_bei(x, y)
        if self._unten is not None:
            self.erfasse_maus()
            self.neu_zeichnen()
        return 0

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        gedrueckt, self._unten = self._unten, None
        self.gib_maus_frei()
        if gedrueckt is not None and self._knopf_bei(x, y) == gedrueckt:
            self._ausfuehren(gedrueckt)
        self.neu_zeichnen()
        return 0

    def bei_maus_verloren(self) -> None:
        self._unten = None

    def _ausfuehren(self, schluessel: str) -> None:
        art, _, name = schluessel.partition(":")
        ed = self.editor
        if art == "w":
            ed.werkzeug_setzen(name)
        elif art == "f":
            ed.farbe_setzen(FARBEN[int(name)])
        elif art == "s":
            ed.staerke_setzen(STAERKEN[int(name)])
        elif art == "t":
            if name.startswith("schrift"):
                ed.schriftgroesse_aendern(4 if name.endswith("+") else -4)
            else:
                ed.stil_umschalten(name)
        elif art == "d":
            ed.deckkraft_setzen(int(name))
        elif name == "gross":
            ed.groesser(1.25)
        elif name == "klein":
            ed.groesser(0.8)
        elif name == "ziel":
            links, oben, _r, _u = self.rechteck()
            a, b, c, d = self._rechtecke["b:ziel"]
            self._ziel(links + a, oben + d)
        elif name == "rueck":
            ed.rueckgaengig()
        elif name == "wied":
            ed.wiederholen()
        elif name == "loesch":
            ed.loeschen()
        elif name == "dupl":
            ed.duplizieren()
        elif name == "gruppe":
            ed.gruppieren()
        elif name == "aufloes":
            ed.aufloesen()
        elif name == "vor":
            ed.ordnung("vor")
        elif name == "zurueck":
            ed.ordnung("zurueck")
        elif name == "aus":
            ed.ausblenden()
        elif name == "ein":
            ed.alle_einblenden()
        elif name == "bild":
            self._bild()
        elif name == "sicht":
            links, oben, _r, _u = self.rechteck()
            a, b, c, d = self._rechtecke[f"b:{name}"]
            self._sichtbar(links + a, oben + d)
        elif name == "fertig":
            self._fertig()

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
