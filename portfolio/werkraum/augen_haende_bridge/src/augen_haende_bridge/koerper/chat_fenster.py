"""Der gemeinsame Chat (R026): ein kleines Fenster für alle Agenten und für Daniel, dauerhaft, mit dem ganzen Verlauf.

Die Agenten schreiben über ihre Raute (`bridge_cli say` → `raute_say`); `KoerperAnwendung` speist das hier über
`empfangen()` ein, mit der Farbe des Agenten (`farbe_setzen`). Daniel schreibt hier selbst (Eingabezeile) oder über
die Regie. Beides geht **nicht** ins Terminal: `gesendet` bekommt den Text, der Besitzer zeigt ihn im Chat und
6,6 s auf dem Bildschirm, damit der Agent ihn im Bild sieht. Oben steht, an wen Daniel gerade schreibt
(„An: Name“); ein Klick darauf wechselt zum nächsten Agenten.

Das Fenster lässt sich am Kopf verschieben, an den Kanten vergrößern und über den Prozent-Knopf transparenter
machen. Lange Nachrichten werden an der Fensterbreite umgebrochen (an Wortgrenzen, zu lange Wörter zeichenweise), der Bildlauf zählt
die umgebrochenen Zeilen.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift

TIMER_CURSOR = 1
PAD = 6
EINGABE_HOEHE_ZUSCHLAG = 10
KOPF_H = 24
RAND = 5
KNOPF_BREITE = 44
KOPF_SCHRIFT_PX = 18  # Zeit und Name vor der Nachricht; der Text dahinter ist 13 px (Daniel 2026-10-01: „viel größer“)
TEXT_NUANCE = 0.45  # so weit ist der Nachrichtentext von der Farbe des Absenders zur Textfarbe hin gemischt
SPRUNG_B = 22  # Breite der Sprungknöpfe ▲ ▼ im Kopf
ROLLBALKEN_B = 10
MIN_GRIFF = 20

Rechteck = tuple[int, int, int, int]


def verlauf_anhaengen(verlauf: list[tuple[str, str, str]], sender: str, text: str, zeit: str,
                       maximal: int) -> list[tuple[str, str, str]]:
    """Neuer Eintrag ans Ende; älteste fallen weg, sobald `maximal` überschritten wird (R045: kein unbegrenztes Wachstum)."""
    neu = [*verlauf, (sender, text, zeit)]
    return neu[-maximal:] if maximal > 0 else neu


def sichtbare_zeilen(verlauf: list[tuple[str, str, str]], anzahl: int, versatz: int) -> list[tuple[str, str, str]]:
    """`anzahl` Zeilen; `versatz` 0 zeigt das Ende des Verlaufs, größerer Versatz blättert zurück."""
    ende = max(0, len(verlauf) - versatz)
    anfang = max(0, ende - anzahl)
    return verlauf[anfang:ende]


def maximaler_versatz(gesamt: int, anzahl: int) -> int:
    return max(0, gesamt - anzahl)


def umbrechen(text: str, max_breite: int, messen: Callable[[str], int], folge_breite: int | None = None) -> list[str]:
    """`text` in Zeilen, die höchstens `max_breite` breit sind (gemessen mit `messen`); alle Zeilen nach der ersten höchstens
    `folge_breite` (für einen Einzug). Umbruch an Leerzeichen; ein einzelnes Wort, das allein nicht passt, wird zeichenweise
    getrennt. Ein leerer Text ergibt eine leere Zeile."""
    folge = max_breite if folge_breite is None else folge_breite
    zeilen: list[str] = []

    def grenze() -> int:
        return max_breite if not zeilen else folge

    for absatz in text.split("\n"):
        aktuell = ""
        for wort in absatz.split(" "):
            kandidat = wort if not aktuell else f"{aktuell} {wort}"
            if messen(kandidat) <= grenze():
                aktuell = kandidat
                continue
            if aktuell:
                zeilen.append(aktuell)
                aktuell = ""
            while wort and messen(wort) > grenze():  # zu langes Wort: so viele Zeichen, wie passen (mindestens eines)
                n = len(wort)
                while n > 1 and messen(wort[:n]) > grenze():
                    n -= 1
                zeilen.append(wort[:n])
                wort = wort[n:]
            aktuell = wort
        zeilen.append(aktuell)
    return zeilen


def kopf_rechtecke(breite: int) -> dict[str, Rechteck]:
    """Die Knöpfe im Kopf: Deckkraft ganz rechts, davor ▼ und ▲ (zur nächsten/vorigen Nachricht), „An: Name“ davor."""
    deckkraft = (breite - RAND - KNOPF_BREITE, 2, breite - RAND, KOPF_H - 2)
    runter = (deckkraft[0] - 4 - SPRUNG_B, 2, deckkraft[0] - 4, KOPF_H - 2)
    hoch = (runter[0] - 2 - SPRUNG_B, 2, runter[0] - 2, KOPF_H - 2)
    empfaenger = (breite // 3, 2, max(breite // 3 + 10, hoch[0] - 4), KOPF_H - 2)
    return {"empfaenger": empfaenger, "hoch": hoch, "runter": runter, "deckkraft": deckkraft}


def rollbalken_rechteck(breite: int, hoehe: int, eingabe_hoehe: int) -> Rechteck:
    """Der Streifen für den Rollbalken rechts, zwischen Kopf und Eingabezeile."""
    return breite - RAND - ROLLBALKEN_B, KOPF_H, breite - RAND, hoehe - eingabe_hoehe


def griff_rechteck(gesamt: int, sichtbar: int, versatz: int, bereich: Rechteck) -> Rechteck | None:
    """Der Griff im Rollbalken (Fensterkoordinaten); None, solange alles auf einmal sichtbar ist. Versatz 0 = unten (Gegenwart)."""
    if gesamt <= sichtbar:
        return None
    links, oben, rechts, unten = bereich
    hoehe = unten - oben
    griff_h = min(hoehe, max(MIN_GRIFF, hoehe * sichtbar // gesamt))
    anteil = 1 - min(versatz, gesamt - sichtbar) / (gesamt - sichtbar)
    anfang = oben + round((hoehe - griff_h) * anteil)
    return links + 2, anfang, rechts - 1, anfang + griff_h


def versatz_fuer(y: int, abstand: int, gesamt: int, sichtbar: int, bereich: Rechteck) -> int:
    """Versatz, wenn der Griff mit seinem Ankerpunkt (`abstand` unter seiner Oberkante) auf Höhe y steht."""
    _l, oben, _r, unten = bereich
    griff_h = min(unten - oben, max(MIN_GRIFF, (unten - oben) * sichtbar // max(1, gesamt)))
    anteil = max(0.0, min(1.0, (y - abstand - oben) / max(1, (unten - oben) - griff_h)))
    return round((1 - anteil) * max(0, gesamt - sichtbar))


def sprung_versatz(anfaenge: list[int], gesamt: int, sichtbar: int, versatz: int, hoch: bool) -> int:
    """Neuer Versatz, wenn die vorige (hoch) bzw. nächste Nachricht mit ihrem Anfang oben im Fenster stehen soll.
    Hinter der letzten Nachricht endet es ganz unten (Versatz 0)."""
    maximal = max(0, gesamt - sichtbar)
    oben = max(0, gesamt - versatz - sichtbar)  # Index der obersten sichtbaren Zeile
    if hoch:
        davor = [a for a in anfaenge if a < oben]
        ziel = davor[-1] if davor else 0
    else:
        danach = [a for a in anfaenge if a > oben]
        if not danach:
            return 0
        ziel = danach[0]
    return max(0, min(maximal, gesamt - ziel - sichtbar))


def kante_bei(x: int, y: int, breite: int, hoehe: int, rand: int = RAND) -> int | None:
    """Fenstersystem-Trefferwert für die Kanten (Größenänderung); None im Inneren."""
    links, rechts, oben, unten = x < rand, x >= breite - rand, y < rand, y >= hoehe - rand
    if oben and links:
        return w.HTTOPLEFT
    if oben and rechts:
        return w.HTTOPRIGHT
    if unten and links:
        return w.HTBOTTOMLEFT
    if unten and rechts:
        return w.HTBOTTOMRIGHT
    if oben:
        return w.HTTOP
    if unten:
        return w.HTBOTTOM
    if links:
        return w.HTLEFT
    if rechts:
        return w.HTRIGHT
    return None


def _in(rechteck: Rechteck, x: int, y: int) -> bool:
    return rechteck[0] <= x < rechteck[2] and rechteck[1] <= y < rechteck[3]


def _uhrzeit_text() -> str:
    return time.strftime("%H:%M")


class ChatFenster(Fenster):
    klasse = "AuHChat"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    MAX_VERLAUF = 500

    def __init__(self, x: int, y: int, *, breite: int = 380, hoehe: int = 240,
                 gesendet: Callable[[str], None] = lambda text: None,
                 empfaenger_wechseln: Callable[[], None] = lambda: None,
                 jetzt_text: Callable[[], str] | None = None):
        w.require_windows()
        self._gesendet = gesendet
        self._empfaenger_wechseln = empfaenger_wechseln
        self._jetzt_text = jetzt_text or _uhrzeit_text
        self.verlauf: list[tuple[str, str, str]] = []
        self.farben: dict[str, int] = {}
        self.empfaenger = "kein Agent"
        self.empfaenger_farbe = stil.FARBE_TEXT_GEDAEMPFT
        self.eingabe = ""
        self._bildlauf_versatz = 0
        self._cursor_phase = True
        self._hat_fokus = False
        self.f_text: Schrift | None = None
        self.f_kopf: Schrift | None = None  # größer und fett: „[Zeit] Name:“ vor jeder Nachricht
        self._mess_hdc = None
        self._umbruch_stand: tuple | None = None
        self._umbruch_zeilen: list[tuple[str, str]] = []
        self._umbruch_anfaenge: list[int] = []
        self._balken_ziehen: int | None = None
        super().__init__(x, y, breite, hoehe, titel="Chat", deckkraft=255)
        self._schrift_bauen()
        self.starte_timer(TIMER_CURSOR, 530)

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_text = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(13, 1.0), fest=False)
            self.f_kopf = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(KOPF_SCHRIFT_PX, 1.0), fest=False, fett=True)
            self._mess_hdc = hdc  # bleibt für das Messen beim Umbrechen; wird in bei_zerstoert freigegeben
        finally:
            w.user32.ReleaseDC(None, screen)

    # ---- Nachrichten -----------------------------------------------------------------------------------------------
    def farbe_setzen(self, sender: str, farbe: int) -> None:
        self.farben[sender] = farbe

    def empfaenger_setzen(self, name: str, farbe: int) -> None:
        self.empfaenger, self.empfaenger_farbe = name, farbe
        self.neu_zeichnen()

    def empfangen(self, sender: str, text: str) -> None:
        self.verlauf = verlauf_anhaengen(self.verlauf, sender, text, self._jetzt_text(), self.MAX_VERLAUF)
        self._bildlauf_versatz = 0
        self.neu_zeichnen()

    def senden(self) -> None:
        text = self.eingabe.strip()
        if not text:
            return
        self.eingabe = ""
        self._gesendet(text)  # der Besitzer trägt ihn (mit Empfänger) in den Verlauf ein und zeigt ihn auf dem Bildschirm
        self.neu_zeichnen()

    def deckkraft_prozent(self) -> int:
        return stil.alpha_prozent(self.deckkraft or 255)

    # ---- Umbruch ---------------------------------------------------------------------------------------------------
    def _messen(self, text: str) -> int:
        return self.f_text.breite(self._mess_hdc, text)

    def _messen_kopf(self, text: str) -> int:
        return self.f_kopf.breite(self._mess_hdc, text)

    def _zeilenhoehe(self) -> int:
        """Alle Zeilen sind so hoch wie die größere Schrift (Zeit und Name), damit sich beim Blättern nichts verschiebt."""
        text = self.f_text.zellhoehe if self.f_text is not None else 16
        kopf = self.f_kopf.zellhoehe if self.f_kopf is not None else 0
        return max(text, kopf)

    def anzeigezeilen(self) -> list[tuple[str, str, str]]:
        """Der ganze Verlauf als Zeilen, die in die Fensterbreite passen: (Absender, Kopf, Text). Nur die erste Zeile eines Eintrags trägt den
        Kopf „[Zeit] Absender:“ (größer, in der Farbe des Absenders), die folgenden sind eingerückt. Das Ergebnis wird gemerkt, solange
        Verlauf und Breite gleich bleiben."""
        breite, _ = self.clientgroesse()
        stand = (len(self.verlauf), self.verlauf[-1] if self.verlauf else None, breite)
        if stand == self._umbruch_stand:
            return self._umbruch_zeilen
        platz = max(20, breite - 2 * PAD - 2 - ROLLBALKEN_B - 2)
        einzug = "    "
        folge = max(10, platz - self._messen(einzug))
        zeilen: list[tuple[str, str, str]] = []
        anfaenge: list[int] = []
        for sender, text, zeit in self.verlauf:
            kopf = f"[{zeit}] {sender}:"
            erste = max(20, platz - self._messen_kopf(kopf + " "))
            teile = umbrechen(text, erste, self._messen, folge)
            anfaenge.append(len(zeilen))
            zeilen.append((sender, kopf, teile[0]))
            zeilen.extend((sender, "", einzug + rest) for rest in teile[1:])
        self._umbruch_stand, self._umbruch_zeilen, self._umbruch_anfaenge = stand, zeilen, anfaenge
        return zeilen

    # ---- Geometrie ---------------------------------------------------------------------------------------------------
    def _eingabe_hoehe(self) -> int:
        return (self.f_text.zellhoehe if self.f_text is not None else 16) + EINGABE_HOEHE_ZUSCHLAG

    def zeilen_sichtbar(self) -> int:
        _, hoehe = self.clientgroesse()
        return max(1, (hoehe - KOPF_H - self._eingabe_hoehe() - PAD) // self._zeilenhoehe())

    def treffer(self, x: int, y: int) -> int | None:
        links, oben, rechts, unten = self.rechteck()
        cx, cy = x - links, y - oben
        breite, hoehe = rechts - links, unten - oben
        kante = kante_bei(cx, cy, breite, hoehe)
        if kante is not None:
            return kante
        if cy < KOPF_H and not any(_in(r, cx, cy) for r in kopf_rechtecke(breite).values()):
            return w.HTCAPTION
        return w.HTCLIENT

    # ---- Maus ------------------------------------------------------------------------------------------------------
    def _balken_bereich(self) -> Rechteck:
        breite, hoehe = self.clientgroesse()
        return rollbalken_rechteck(breite, hoehe, self._eingabe_hoehe())

    def _griff(self) -> Rechteck | None:
        return griff_rechteck(len(self.anzeigezeilen()), self.zeilen_sichtbar(), self._bildlauf_versatz, self._balken_bereich())

    def _balken_zu(self, y: int) -> None:
        neu = versatz_fuer(y, self._balken_ziehen or 0, len(self.anzeigezeilen()), self.zeilen_sichtbar(), self._balken_bereich())
        if neu != self._bildlauf_versatz:
            self._bildlauf_versatz = neu
            self.neu_zeichnen()

    def springen(self, hoch: bool) -> None:
        """Zum Anfang der vorigen bzw. nächsten Nachricht: sie steht dann oben im Fenster."""
        gesamt = len(self.anzeigezeilen())  # füllt auch die Nachrichtenanfänge
        self._bildlauf_versatz = sprung_versatz(self._umbruch_anfaenge, gesamt, self.zeilen_sichtbar(), self._bildlauf_versatz, hoch)
        self.neu_zeichnen()

    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        breite, _ = self.clientgroesse()
        rechtecke = kopf_rechtecke(breite)
        if _in(rechtecke["deckkraft"], x, y):
            self.setze_deckkraft(stil.deckkraft_alpha(stil.naechste_stufe(self.deckkraft_prozent())))
            self.neu_zeichnen()
        elif _in(rechtecke["hoch"], x, y):
            self.springen(True)
        elif _in(rechtecke["runter"], x, y):
            self.springen(False)
        elif _in(rechtecke["empfaenger"], x, y):
            self._empfaenger_wechseln()
        elif _in(self._balken_bereich(), x, y):
            griff = self._griff()
            if griff is not None:
                if griff[1] <= y < griff[3]:
                    self._balken_ziehen = y - griff[1]  # am Griff packen, ohne dass er springt
                else:
                    self._balken_ziehen = (griff[3] - griff[1]) // 2  # in die Leiste geklickt: Griff dorthin setzen
                    self._balken_zu(y)
                self.erfasse_maus()
                self.neu_zeichnen()
        return 0

    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None:
        if self._balken_ziehen is not None and flags & 0x0001:
            self._balken_zu(y)
        return 0

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        if self._balken_ziehen is not None:
            self._balken_ziehen = None
            self.gib_maus_frei()
            self.neu_zeichnen()
        return 0

    def bei_maus_verloren(self) -> None:
        self._balken_ziehen = None

    def bei_rad(self, delta: int, x: int, y: int, flags: int) -> int | None:
        maximal = maximaler_versatz(len(self.anzeigezeilen()), self.zeilen_sichtbar())
        self._bildlauf_versatz = max(0, min(maximal, self._bildlauf_versatz + (1 if delta > 0 else -1)))
        self.neu_zeichnen()
        return 0

    def bei_groesse(self, breite: int, hoehe: int) -> None:
        self.neu_zeichnen()

    # ---- Tastatur --------------------------------------------------------------------------------------------------
    def bei_zeichen(self, code: int, syskey: bool) -> int | None:
        if code == 0x0D:
            self.senden()
            return 0
        if code == 0x08:
            self.eingabe = self.eingabe[:-1]
            self.neu_zeichnen()
            return 0
        if code < 0x20 or 0xD800 <= code <= 0xDFFF:
            return 0
        self.eingabe += chr(code)
        self.neu_zeichnen()
        return 0

    def bei_fokus(self, hat_fokus: bool) -> None:
        self._hat_fokus = hat_fokus
        self.neu_zeichnen()

    def bei_timer(self, ident: int) -> None:
        if ident == TIMER_CURSOR:
            self._cursor_phase = not self._cursor_phase
            if self._hat_fokus:
                self.neu_zeichnen()

    # ---- Zeichnen --------------------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        breite, hoehe = leinwand.breite, leinwand.hoehe
        leinwand.fuellen(stil.FARBE_GRUND)
        leinwand.fuellen(stil.FARBE_LEISTE, 0, 0, breite, KOPF_H)
        kopf_y = (KOPF_H - self.f_text.zellhoehe) // 2
        leinwand.text(PAD, kopf_y, "Chat", stil.FARBE_TEXT, self.f_text)
        rechtecke = kopf_rechtecke(breite)
        empfaenger = f"An: {self.empfaenger}"[:24]
        platz = rechtecke["empfaenger"][2] - rechtecke["empfaenger"][0]
        while len(empfaenger) > 4 and self.f_text.breite(leinwand.hdc, empfaenger) > platz:
            empfaenger = empfaenger[:-2] + "…"
        leinwand.text(rechtecke["empfaenger"][0], kopf_y, empfaenger, self.empfaenger_farbe, self.f_text)
        for name, nach_oben in (("hoch", True), ("runter", False)):
            a, b, c, d = rechtecke[name]
            leinwand.rahmen(a, b, c, d, stil.FARBE_TEXT_GEDAEMPFT, 1)
            mx, my = (a + c) // 2, (b + d) // 2
            punkte = [(mx - 4, my + 3), (mx + 4, my + 3), (mx, my - 3)] if nach_oben else [(mx - 4, my - 3), (mx + 4, my - 3), (mx, my + 3)]
            leinwand.polygon(punkte, stil.FARBE_TEXT)
        d_links, d_oben, d_rechts, d_unten = rechtecke["deckkraft"]
        leinwand.rahmen(d_links, d_oben, d_rechts, d_unten, stil.FARBE_TEXT_GEDAEMPFT, 1)
        prozent = f"{self.deckkraft_prozent()}%"
        leinwand.text(d_links + (d_rechts - d_links - self.f_text.breite(leinwand.hdc, prozent)) // 2, kopf_y,
                      prozent, stil.FARBE_TEXT, self.f_text)
        eingabe_h = self._eingabe_hoehe()
        zellhoehe = self._zeilenhoehe()
        zeilen = sichtbare_zeilen(self.anzeigezeilen(), self.zeilen_sichtbar(), self._bildlauf_versatz)
        y = hoehe - eingabe_h - PAD - len(zeilen) * zellhoehe
        for sender, kopf, text in zeilen:
            farbe = self.farben.get(sender, stil.FARBE_TEXT)
            x = PAD
            if kopf:
                leinwand.text(x, y + (zellhoehe - self.f_kopf.zellhoehe) // 2, kopf, farbe, self.f_kopf)
                x += self.f_kopf.breite(leinwand.hdc, kopf + " ")
            leinwand.text(x, y + zellhoehe - self.f_text.zellhoehe - 1, text, stil.mischen(farbe, stil.FARBE_TEXT, TEXT_NUANCE), self.f_text)
            y += zellhoehe
        leinwand.fuellen(stil.FARBE_LEISTE, 0, hoehe - eingabe_h, breite, hoehe)
        cursor = "▏" if (self._hat_fokus and self._cursor_phase) else ""
        leinwand.text(PAD, hoehe - eingabe_h + EINGABE_HOEHE_ZUSCHLAG // 2, self.eingabe + cursor, stil.FARBE_TEXT,
                      self.f_text)
        balken = rollbalken_rechteck(breite, hoehe, eingabe_h)
        leinwand.fuellen(stil.farbe_hell(stil.FARBE_GRUND, 1.4), *balken)
        griff = griff_rechteck(len(self.anzeigezeilen()), self.zeilen_sichtbar(), self._bildlauf_versatz, balken)
        if griff is not None:
            leinwand.fuellen(stil.FARBE_TEXT if self._balken_ziehen is not None else stil.FARBE_TEXT_GEDAEMPFT, *griff)
        leinwand.rahmen(0, 0, breite, hoehe, self.empfaenger_farbe, 1)

    def bei_zerstoert(self) -> None:
        if self._mess_hdc is not None:
            w.gdi32.DeleteDC(self._mess_hdc)
            self._mess_hdc = None
        if self.f_kopf is not None:
            self.f_kopf.freigeben()
            self.f_kopf = None
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
