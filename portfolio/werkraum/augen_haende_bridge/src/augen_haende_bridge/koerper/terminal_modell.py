"""Terminalmodell des Körpers: VT-Zustand (pyte), Alternate Screen, Farben, Tastenkodierung, Auswahl. Reine Logik, läuft unter Linux.

Das Fenster (`terminal_fenster.py`) zeichnet nur, was dieses Modell hält. Der rohe Strom kommt vom Starter auf dem VPS; Antworten,
die das Terminal selbst erzeugt (Geräte- und Cursorabfragen), gehen über `antwort` zurück in dieselbe Sitzung.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

import pyte
from pyte.screens import StaticDefaultDict

ALT_MODI = (47, 1047, 1049)
ANWENDUNGS_CURSOR = 1 << 5  # DECCKM (privater Modus 1)
BRACKETED_PASTE = 2004 << 5
TEXT_CURSOR_SICHTBAR = 25 << 5  # DECTCEM
MAUS_VERFOLGEN = tuple(m << 5 for m in (1000, 1002, 1003))  # das Programm will Mausereignisse haben
MAUS_SGR = 1006 << 5  # ... in der SGR-Schreibweise

# Windows-Terminal-Palette (Campbell); Namen wie pyte sie liefert.
PALETTE_NAMEN = ["black", "red", "green", "brown", "blue", "magenta", "cyan", "white",
                 "brightblack", "brightred", "brightgreen", "brightbrown", "brightblue", "brightmagenta", "brightcyan", "brightwhite"]
PALETTE_RGB = [(12, 12, 12), (197, 15, 31), (19, 161, 14), (193, 156, 0), (0, 55, 218), (136, 23, 152), (58, 150, 221), (204, 204, 204),
               (118, 118, 118), (231, 72, 86), (22, 198, 12), (249, 241, 165), (59, 120, 255), (180, 0, 158), (97, 214, 214), (242, 242, 242)]
STANDARD_FG = (204, 204, 204)
STANDARD_BG = (12, 12, 12)

_NAME_ZU_RGB = dict(zip(PALETTE_NAMEN, PALETTE_RGB))
_NAME_ZU_RGB["brightyellow"] = PALETTE_RGB[11]


def farbe_rgb(name: str, standard: tuple[int, int, int]) -> tuple[int, int, int]:
    """pyte-Farbname oder 6-stelliger Hexwert in (r, g, b) der Palette."""
    if name == "default":
        return standard
    rgb = _NAME_ZU_RGB.get(name)
    if rgb is not None:
        return rgb
    try:
        return int(name[0:2], 16), int(name[2:4], 16), int(name[4:6], 16)
    except (ValueError, IndexError):
        return standard


class Strom(pyte.ByteStream):
    """Bytes immer als UTF-8 lesen, aber den DEC-Linienzeichensatz zulassen: Programme wie mc, dialog oder ncurses-Oberflächen schalten mit
    ESC ( 0 auf Rahmenzeichen (l q k x m j …) um und mit ESC ( B zurück. pyte ignoriert das im UTF-8-Modus, darum liest dieser Strom selbst."""

    def feed(self, data: bytes) -> None:  # type: ignore[override]
        pyte.Stream.feed(self, self.utf8_decoder.decode(data))

    def select_other_charset(self, code: str) -> None:
        pass  # ESC % @ / ESC % G: wir bleiben bei UTF-8


class Bildschirm(pyte.HistoryScreen):
    """pyte-Bildschirm mit Rückblätterverlauf, Alternate Screen (47/1047/1049) und Antworten an die Sitzung."""

    def __init__(self, spalten: int, zeilen: int, *, verlauf: int = 5000, antwort: Callable[[bytes], None] | None = None):
        super().__init__(spalten, zeilen, history=verlauf, ratio=.5)
        self.alternativ = False
        self._haupt: tuple | None = None
        self._antwort = antwort or (lambda _daten: None)

    def write_process_input(self, data: str) -> None:
        self._antwort(data.encode("utf-8"))

    def set_mode(self, *modi: int, **kwargs) -> None:
        if kwargs.get("private"):
            alt = [m for m in modi if m in ALT_MODI]
            rest = [m for m in modi if m not in ALT_MODI]
            if alt:
                self._alternativ_ein(cursor_retten=1049 in alt)
            if rest:
                super().set_mode(*rest, **kwargs)
            return
        super().set_mode(*modi, **kwargs)

    def reset_mode(self, *modi: int, **kwargs) -> None:
        if kwargs.get("private"):
            alt = [m for m in modi if m in ALT_MODI]
            rest = [m for m in modi if m not in ALT_MODI]
            if alt:
                self._alternativ_aus(cursor_zurueck=1049 in alt)
            if rest:
                super().reset_mode(*rest, **kwargs)
            return
        super().reset_mode(*modi, **kwargs)

    def _leerer_puffer(self):
        return defaultdict(lambda: StaticDefaultDict(self.default_char))

    def _alternativ_ein(self, cursor_retten: bool) -> None:  # der Cursor wird immer gesichert; 47/1047 stellen ihn nicht wieder her
        if self.alternativ:
            return
        self._haupt = (self.buffer, pyte.screens.Cursor(self.cursor.x, self.cursor.y, self.cursor.attrs), self.margins)
        self.buffer = self._leerer_puffer()
        self.margins = None
        self.alternativ = True
        self.cursor.x = self.cursor.y = 0
        self.dirty.update(range(self.lines))

    def _alternativ_aus(self, cursor_zurueck: bool) -> None:
        if not self.alternativ or self._haupt is None:
            return
        puffer, cursor, raender = self._haupt
        self.buffer, self.margins = puffer, raender
        if cursor_zurueck:
            self.cursor.x, self.cursor.y, self.cursor.attrs = cursor.x, cursor.y, cursor.attrs
        self._haupt = None
        self.alternativ = False
        self.dirty.update(range(self.lines))

    def index(self) -> None:
        if self.alternativ:  # kein Verlauf im Alternate Screen
            pyte.Screen.index(self)
        else:
            super().index()

    def reverse_index(self) -> None:
        if self.alternativ:
            pyte.Screen.reverse_index(self)
        else:
            super().reverse_index()


@dataclass(frozen=True)
class Zelle:
    zeichen: str
    vordergrund: tuple[int, int, int]
    hintergrund: tuple[int, int, int]
    fett: bool
    kursiv: bool
    unterstrichen: bool
    durchgestrichen: bool
    breit: bool
    stumm: bool  # zweite Hälfte eines breiten Zeichens: nichts zeichnen


class TerminalModell:
    """Alles, was ein Terminalfenster über eine Sitzung weiß: Bildschirm, Größe, Auswahl."""

    def __init__(self, zeilen: int = 30, spalten: int = 100, *, antwort: Callable[[bytes], None] | None = None):
        self.bildschirm = Bildschirm(spalten, zeilen, antwort=antwort)
        self._strom = Strom(self.bildschirm)
        self._strom.use_utf8 = False  # nur für pyte's Parser: so nimmt er Zeichensatzwechsel (ESC ( 0, ESC ( B) an; dekodiert wird in `Strom.feed` immer als UTF-8
        self.auswahl: tuple[tuple[int, int], tuple[int, int]] | None = None
        self.geaendert = True
        self.empfangen = 0

    @property
    def zeilen(self) -> int:
        return self.bildschirm.lines

    @property
    def spalten(self) -> int:
        return self.bildschirm.columns

    def einspeisen(self, daten: bytes) -> None:
        self.empfangen += len(daten)
        self._strom.feed(daten)
        self.geaendert = True

    def groesse_setzen(self, zeilen: int, spalten: int) -> bool:
        if (zeilen, spalten) == (self.zeilen, self.spalten):
            return False
        self.bildschirm.resize(zeilen, spalten)
        self.auswahl = None
        self.geaendert = True
        return True

    def zelle(self, zeile: int, spalte: int) -> Zelle:
        puffer = self.bildschirm.buffer[zeile][spalte]
        vorn, hinten = farbe_rgb(puffer.fg, STANDARD_FG), farbe_rgb(puffer.bg, STANDARD_BG)
        if puffer.reverse:
            vorn, hinten = hinten, vorn
        daten = puffer.data
        return Zelle(daten if daten else " ", vorn, hinten, puffer.bold, puffer.italics, puffer.underscore, puffer.strikethrough,
                     breit=bool(daten) and pyte.screens.wcwidth(daten[0]) == 2, stumm=daten == "")

    def zeile_text(self, zeile: int) -> str:
        return self.bildschirm.display[zeile]

    def cursor(self) -> tuple[int, int, bool]:
        c = self.bildschirm.cursor
        return c.y, c.x, not c.hidden

    def anwendungs_cursor(self) -> bool:
        return ANWENDUNGS_CURSOR in self.bildschirm.mode

    def rad_meldung(self, hoch: bool, zeile: int, spalte: int) -> bytes | None:
        """Mausrad als Mausereignis für das Programm (vollbildige Oberflächen wie Claude Code bringen ihr eigenes Blättern mit
        und wollen das Rad selbst); None, wenn das Programm keine Mausereignisse angefordert hat."""
        modus = self.bildschirm.mode
        if not any(m in modus for m in MAUS_VERFOLGEN):
            return None
        spalte, zeile = spalte + 1, zeile + 1  # Terminal zählt ab 1
        taste = 64 if hoch else 65
        if MAUS_SGR in modus:
            return b"\x1b[<%d;%d;%dM" % (taste, spalte, zeile)
        if spalte > 222 or zeile > 222:
            return None  # die alte Schreibweise reicht nur bis 223
        return b"\x1b[M" + bytes([32 + taste, 32 + spalte, 32 + zeile])

    def eingeklammertes_einfuegen(self) -> bool:
        return BRACKETED_PASTE in self.bildschirm.mode

    # ---- Verlauf -----------------------------------------------------------------------------------------------------
    def blaettern(self, seiten: int) -> None:
        """Positiv: zurück in den Verlauf, negativ: nach vorn. Im Alternate Screen gibt es keinen Verlauf."""
        if self.bildschirm.alternativ:
            return
        for _ in range(abs(seiten)):
            (self.bildschirm.prev_page if seiten > 0 else self.bildschirm.next_page)()
        self.geaendert = True

    def zuruecksetzen(self) -> None:
        """Alles zurück auf leer (Bildschirm, Rückblättern, Auswahl, Alternate-Screen-Zustand): vor dem Wiederaufnehmen einer laufenden
        Sitzung, deren letzte Ausgabe der Starter noch einmal schickt."""
        self.bildschirm.reset()
        self.bildschirm.alternativ = False
        self.bildschirm._haupt = None
        self.auswahl = None
        self.geaendert = True

    def verlauf_laenge(self) -> int:
        """Zeilen oberhalb des sichtbaren Bildes (zurückgeblätterter Verlauf plus der noch darüber)."""
        history = self.bildschirm.history
        return len(history.top) + len(history.bottom)

    def verlauf_versatz(self) -> int:
        """Wie viele Zeilen das Bild gerade vom Ende (der Gegenwart) zurückgeblättert ist; 0 = ganz unten."""
        return len(self.bildschirm.history.bottom)

    def blaettern_zeilen(self, zeilen: int) -> int:
        """Zeilenweise blättern (positiv: zurück in den Verlauf). Eine ausgewählte Stelle wandert mit dem Text mit.
        Liefert, um wie viele Zeilen sich das Bild wirklich bewegt hat (mit Vorzeichen wie `zeilen`)."""
        if self.bildschirm.alternativ or zeilen == 0:
            return 0
        gesamt, vorzeichen, rest = 0, 1 if zeilen > 0 else -1, abs(zeilen)
        while rest > 0:
            schritt = self._blaettern_schritt(vorzeichen * min(rest, self.bildschirm.lines))
            if schritt == 0:
                break
            gesamt += schritt
            rest -= abs(schritt)
        return gesamt

    def _blaettern_schritt(self, zeilen: int) -> int:
        """Höchstens eine Bildhöhe auf einmal (so viel kann der Pufferumbau von pyte)."""
        schirm = self.bildschirm
        history, hoehe = schirm.history, schirm.lines
        if zeilen > 0:
            mid = min(len(history.top), zeilen)
            if mid <= 0:
                return 0
            history.bottom.extendleft(schirm.buffer[y] for y in range(hoehe - 1, hoehe - mid - 1, -1))
            schirm.history = history._replace(position=history.position - mid)
            for y in range(hoehe - 1, mid - 1, -1):
                schirm.buffer[y] = schirm.buffer[y - mid]
            for y in range(mid - 1, -1, -1):
                schirm.buffer[y] = schirm.history.top.pop()
            bewegt = mid
        else:
            mid = min(len(history.bottom), -zeilen)
            if mid <= 0:
                return 0
            history.top.extend(schirm.buffer[y] for y in range(mid))
            schirm.history = history._replace(position=history.position + mid)
            for y in range(hoehe - mid):
                schirm.buffer[y] = schirm.buffer[y + mid]
            for y in range(hoehe - mid, hoehe):
                schirm.buffer[y] = schirm.history.bottom.popleft()
            bewegt = -mid
        schirm.dirty = set(range(hoehe))
        if self.auswahl is not None:
            (z1, s1), (z2, s2) = self.auswahl
            klemmen = lambda z: max(0, min(hoehe - 1, z + bewegt))  # noqa: E731
            self.auswahl = ((klemmen(z1), s1), (klemmen(z2), s2))
        self.geaendert = True
        return bewegt

    def zu_versatz(self, ziel: int) -> int:
        """Auf einen bestimmten Versatz vom Ende blättern (für den Rollbalken)."""
        ziel = max(0, min(self.verlauf_laenge(), ziel))
        return self.blaettern_zeilen(ziel - self.verlauf_versatz())

    def im_verlauf(self) -> bool:
        history = self.bildschirm.history
        return history.position < history.size

    # ---- Auswahl -----------------------------------------------------------------------------------------------------
    def auswahl_setzen(self, start: tuple[int, int] | None, ende: tuple[int, int] | None = None) -> None:
        self.auswahl = None if start is None or ende is None or start == ende else (start, ende)
        self.geaendert = True

    def auswahl_grenzen(self) -> tuple[tuple[int, int], tuple[int, int]] | None:
        if self.auswahl is None:
            return None
        a, b = self.auswahl
        return (a, b) if a <= b else (b, a)

    def ist_ausgewaehlt(self, zeile: int, spalte: int) -> bool:
        grenzen = self.auswahl_grenzen()
        return grenzen is not None and grenzen[0] <= (zeile, spalte) < grenzen[1]

    def auswahl_text(self) -> str:
        grenzen = self.auswahl_grenzen()
        if grenzen is None:
            return ""
        (z1, s1), (z2, s2) = grenzen
        ergebnis = ""
        for z in range(z1, z2 + 1):
            anfang = s1 if z == z1 else 0
            ende = s2 if z == z2 else self.spalten
            text = self.zeile_text(z)[anfang:ende]
            if z < z2 and self._umbruch_am_ende(z):
                ergebnis += text  # weicher Umbruch: dieselbe Zeile geht weiter, kein Zeilenwechsel und keine Leerzeichen weg
            else:
                ergebnis += text.rstrip() + ("\n" if z < z2 else "")
        return ergebnis

    def _umbruch_am_ende(self, zeile: int) -> bool:
        """Läuft die Zeile bis in die letzte Spalte, wurde sie umgebrochen: gleicher Text, keine echte Zeile."""
        text = self.zeile_text(zeile)
        return len(text) >= self.spalten and text[self.spalten - 1] != " "

    def alles_markieren(self) -> None:
        letzte = self.zeilen - 1
        while letzte > 0 and not self.zeile_text(letzte).strip():
            letzte -= 1  # leere Zeilen unten nicht mitnehmen
        self.auswahl_setzen((0, 0), (letzte, self.spalten))

    def wort_bei(self, zeile: int, spalte: int) -> tuple[tuple[int, int], tuple[int, int]]:
        text = self.zeile_text(zeile)
        spalte = max(0, min(len(text) - 1, spalte)) if text else 0
        if not text or text[spalte].isspace():
            return (zeile, spalte), (zeile, spalte + 1)
        anfang = spalte
        while anfang > 0 and not text[anfang - 1].isspace():
            anfang -= 1
        ende = spalte
        while ende < len(text) and not text[ende].isspace():
            ende += 1
        return (zeile, anfang), (zeile, ende)


# ---- Tastenkodierung (Windows-Taste -> Bytes an die Sitzung) -------------------------------------------------------
VK = dict(BACK=0x08, TAB=0x09, RETURN=0x0D, ESCAPE=0x1B, SPACE=0x20, PRIOR=0x21, NEXT=0x22, END=0x23, HOME=0x24, LEFT=0x25, UP=0x26,
          RIGHT=0x27, DOWN=0x28, INSERT=0x2D, DELETE=0x2E, F1=0x70)

_CURSORTASTEN = {VK["UP"]: "A", VK["DOWN"]: "B", VK["RIGHT"]: "C", VK["LEFT"]: "D", VK["HOME"]: "H", VK["END"]: "F"}
_TILDETASTEN = {VK["INSERT"]: 2, VK["DELETE"]: 3, VK["PRIOR"]: 5, VK["NEXT"]: 6}
_FUNKTIONSTILDEN = {5: 15, 6: 17, 7: 18, 8: 19, 9: 20, 10: 21, 11: 23, 12: 24, 13: 25, 14: 26, 15: 28, 16: 29, 17: 31, 18: 32, 19: 33, 20: 34}


def modifikator(umschalt: bool, alt: bool, strg: bool) -> int:
    return 1 + (1 if umschalt else 0) + (2 if alt else 0) + (4 if strg else 0)


def taste_zu_bytes(vk: int, *, umschalt: bool = False, alt: bool = False, strg: bool = False, anwendungs_cursor: bool = False) -> bytes | None:
    """Sondertasten als xterm-Folge; None, wenn die Taste über WM_CHAR als Zeichen ankommt."""
    mod = modifikator(umschalt, alt, strg)
    if vk in _CURSORTASTEN:
        buchstabe = _CURSORTASTEN[vk]
        if mod > 1:
            return f"\x1b[1;{mod}{buchstabe}".encode()
        return (f"\x1bO{buchstabe}" if anwendungs_cursor else f"\x1b[{buchstabe}").encode()
    if vk in _TILDETASTEN:
        nummer = _TILDETASTEN[vk]
        return (f"\x1b[{nummer};{mod}~" if mod > 1 else f"\x1b[{nummer}~").encode()
    if VK["F1"] <= vk <= VK["F1"] + 19:
        nummer = vk - VK["F1"] + 1
        if nummer <= 4:
            buchstabe = "PQRS"[nummer - 1]
            return (f"\x1b[1;{mod}{buchstabe}" if mod > 1 else f"\x1bO{buchstabe}").encode()
        tilde = _FUNKTIONSTILDEN[nummer]
        return (f"\x1b[{tilde};{mod}~" if mod > 1 else f"\x1b[{tilde}~").encode()
    if vk == VK["TAB"] and umschalt and not strg and not alt:
        return b"\x1b[Z"
    if vk == VK["SPACE"] and strg and not alt:
        return b"\x00"
    return None


def zeichen_zu_bytes(code: int, *, alt: bool = False) -> bytes | None:
    """Ein Zeichen aus WM_CHAR/WM_SYSCHAR (UTF-16-Einheit, Ersatzpaare setzt der Aufrufer zusammen)."""
    if code == 0x0D:
        daten = b"\r"
    elif code == 0x08:
        daten = b"\x7f"
    elif code == 0x1B:
        daten = b"\x1b"
    elif code == 0x09:
        daten = b"\t"
    elif code < 0x20 or code == 0x7F:
        daten = bytes([code])
    elif 0xD800 <= code <= 0xDFFF:
        return None
    else:
        daten = chr(code).encode("utf-8")
    return (b"\x1b" + daten) if alt else daten


def einfuegen_zu_bytes(text: str, eingeklammert: bool) -> bytes:
    text = text.replace("\r\n", "\r").replace("\n", "\r")
    daten = text.encode("utf-8")
    return b"\x1b[200~" + daten + b"\x1b[201~" if eingeklammert else daten
