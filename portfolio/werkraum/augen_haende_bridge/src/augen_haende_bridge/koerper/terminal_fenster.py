"""Das Terminalfenster: schwebend, immer oben, einzeln verschiebbar, größenänderbar, ein- und ausblendbar (R114).

Es zeichnet, was das Terminalmodell aus dem Strom der von der Bridge gehaltenen Sitzung hält, und schickt Tasten, Einfügen und
Größenänderungen dorthin zurück. Unten rechts sitzt der Fensterscanner dieses Terminals (R015), links daneben „A+H“ (Augen und Hände an oder „nur Terminal“, R122)
und „Ort“ (jedes Element auf dem Desktop oder im Zielfenster, R121).
"""

from __future__ import annotations

import ctypes
from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift
from .menue import ABGEBLENDET, text_aus_zwischenablage, text_in_zwischenablage, zeige_menue
from .terminal_modell import STANDARD_BG, TerminalModell, einfuegen_zu_bytes, taste_zu_bytes, zeichen_zu_bytes

TIMER_ZEICHNEN, TIMER_CURSOR, TIMER_GROESSE, TIMER_AUTOSCROLL = 1, 2, 3, 4
RAD_ZEILEN = 3  # Zeilen je Rasten des Mausrads
# Schriftgröße des Terminals in Pixeln bei 96 dpi. War 16; Daniel (2026-10-01): „so wie bei vd1“. Gemessen am Screenshot: Zeile 27 statt 19 px,
# Zeichenbreite 11,9 statt 8,5 px, also etwa 0,71 des alten Werts.
SCHRIFT_PX = 12
GRUNDDPI = 96
GRUND = w.rgb(*STANDARD_BG)


def _wahl_schrift(hdc, namen: tuple[str, ...], hoehe: int, **optionen) -> Schrift:
    erste = None
    for name in namen:
        schrift = Schrift(hdc, name, hoehe, **optionen)
        if schrift.tatsaechlich.lower() == name.lower():
            return schrift
        if erste is None:
            erste = schrift
        else:
            schrift.freigeben()
    return erste


class TerminalFenster(Fenster):
    klasse = "AuHTerminal"
    fensterstil = w.WS_POPUP | w.WS_THICKFRAME
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW
    _balken_ziehen: int | None = None
    _maus_y = 0
    rollbalken_b = 0  # Breite des Rollbalkens rechts; wird mit den Schriften skaliert gesetzt

    def __init__(self, x: int, y: int, *, zeilen: int = 30, spalten: int = 100, name: str, ort: str, farbe_hex: str,
                 deckkraft_prozent: int = stil.DECKKRAFT_START_PROZENT,
                 senden: Callable[[bytes], None] = lambda daten: None,
                 groesse_gemeldet: Callable[[int, int], None] = lambda zeilen, spalten: None,
                 schliessen_gewuenscht: Callable[[], None] = lambda: None,
                 verbergen_gewuenscht: Callable[[], None] = lambda: None,
                 scanner_gewuenscht: Callable[[int, int], None] = lambda x, y: None,
                 ort_gewuenscht: Callable[[int, int], None] = lambda x, y: None,
                 augen_umschalten: Callable[[], None] = lambda: None,
                 layout_geaendert: Callable[[], None] = lambda: None,
                 antwort: Callable[[bytes], None] | None = None):
        w.require_windows()
        self.name, self.ort, self.farbe_hex = name, ort, farbe_hex
        self.farbe = w.rgb_hex(farbe_hex)
        self.zustand = "startet…"
        self.ziel_text, self.ziel_gebunden = "Ziel: Desktop (ungebunden)", False
        self._senden, self._groesse_gemeldet = senden, groesse_gemeldet
        self._schliessen, self._verbergen, self._scanner = schliessen_gewuenscht, verbergen_gewuenscht, scanner_gewuenscht
        self._ort, self._augen = ort_gewuenscht, augen_umschalten
        self.augen_an = True  # False = „nur Terminal“: Bilder, Hände, Kamera und Rautenchat dieses Agenten sind aus
        self.ort_text = "Ort"
        self._layout_geaendert = layout_geaendert
        self.modell = TerminalModell(zeilen, spalten, antwort=antwort or senden)
        self._gemeldet = (zeilen, spalten)
        self._hat_fokus = False
        self._cursor_phase = True
        self._zeichnen_geplant = False
        self._char_unterdruecken = False
        self._hohes_ersatzzeichen = 0
        self._auswahl_anker: tuple[int, int] | None = None
        self._ziehen = False
        self._ersatz: dict[str, Schrift | None] = {}
        self._knopf_unten: str | None = None
        self._balken_ziehen: int | None = None  # Abstand des Griffpunkts zum Anfang des Griffs, solange am Rollbalken gezogen wird
        self._maus_y = 0
        self.dpi = self._system_dpi()
        self._schriften_bauen(self.dpi / GRUNDDPI)
        breite = 2 * (self.rand + self.pad) + spalten * self.zell_b + self.rollbalken_b
        hoehe = self.titel_h + self.unten_h + 2 * self.pad + zeilen * self.zell_h
        super().__init__(x, y, breite, hoehe, titel=f"{name} · {ort}", deckkraft=stil.deckkraft_alpha(deckkraft_prozent))
        self.dpi = self._fenster_dpi()
        self.starte_timer(TIMER_CURSOR, 530)

    # ---- Maße und Schriften ------------------------------------------------------------------------------------------
    @staticmethod
    def _system_dpi() -> int:
        return int(w.user32.GetDpiForSystem()) if w.user32.GetDpiForSystem is not None else GRUNDDPI

    def _fenster_dpi(self) -> int:
        if w.user32.GetDpiForWindow is None:
            return self.dpi
        return int(w.user32.GetDpiForWindow(self.hwnd)) or self.dpi

    def _schriften_bauen(self, faktor: float) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_terminal = _wahl_schrift(hdc, stil.SCHRIFT_TERMINAL, stil.skaliert(SCHRIFT_PX, faktor))
            self.f_fett = _wahl_schrift(hdc, (self.f_terminal.name,), stil.skaliert(SCHRIFT_PX, faktor), fett=True)
            self.f_ui = _wahl_schrift(hdc, stil.SCHRIFT_OBERFLAECHE, stil.skaliert(13, faktor), fest=False)
            self.f_ersatz = []
            for name in stil.SCHRIFT_ERSATZ:
                kandidat = Schrift(hdc, name, stil.skaliert(SCHRIFT_PX, faktor))
                if kandidat.tatsaechlich.lower() == name.lower():
                    self.f_ersatz.append(kandidat)
                else:
                    kandidat.freigeben()
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)
        self.zell_b, self.zell_h = self.f_terminal.zellbreite, self.f_terminal.zellhoehe
        self.titel_h = stil.skaliert(28, faktor)
        self.unten_h = stil.skaliert(26, faktor)
        self.rand = stil.skaliert(5, faktor)
        self.pad = stil.skaliert(4, faktor)
        self.knopf = stil.skaliert(20, faktor)
        self.rollbalken_b = stil.skaliert(10, faktor)
        self._ersatz.clear()

    def gitter_rechteck(self) -> tuple[int, int, int, int]:
        breite, hoehe = self.clientgroesse()
        return (self.rand + self.pad, self.titel_h + self.pad, breite - self.rand - self.pad - self.rollbalken_b,
                hoehe - self.unten_h - self.pad)

    def rollbalken_rechteck(self) -> tuple[int, int, int, int]:
        breite, hoehe = self.clientgroesse()
        return (breite - self.rand - self.pad - self.rollbalken_b, self.titel_h + self.pad, breite - self.rand, hoehe - self.unten_h - self.pad)

    def griff_rechteck(self) -> tuple[int, int, int, int] | None:
        """Der Griff im Rollbalken; None, solange es keinen Verlauf zum Blättern gibt."""
        verlauf = self.modell.verlauf_laenge()
        if verlauf <= 0 or self.modell.bildschirm.alternativ:
            return None
        links, oben, rechts, unten = self.rollbalken_rechteck()
        hoehe = unten - oben
        sichtbar = self.modell.zeilen
        griff_h = max(stil.skaliert(24, self.dpi / GRUNDDPI), hoehe * sichtbar // (sichtbar + verlauf))
        griff_h = min(griff_h, hoehe)
        anteil = 1 - self.modell.verlauf_versatz() / verlauf  # 1 = ganz unten (Gegenwart)
        anfang = oben + round((hoehe - griff_h) * anteil)
        return links + 2, anfang, rechts - 1, anfang + griff_h

    def _versatz_fuer(self, y: int, griff_abstand: int) -> int:
        """Versatz vom Ende, wenn der Griff mit seinem Ankerpunkt auf Höhe y steht."""
        links, oben, rechts, unten = self.rollbalken_rechteck()
        griff = self.griff_rechteck()
        griff_h = (griff[3] - griff[1]) if griff else 0
        spielraum = max(1, (unten - oben) - griff_h)
        anteil = max(0.0, min(1.0, (y - griff_abstand - oben) / spielraum))
        return round((1 - anteil) * self.modell.verlauf_laenge())

    def zeilen_spalten(self) -> tuple[int, int]:
        links, oben, rechts, unten = self.gitter_rechteck()
        return max(1, (unten - oben) // self.zell_h), max(1, (rechts - links) // self.zell_b)

    def knopf_rechtecke(self) -> dict[str, tuple[int, int, int, int]]:
        breite, _ = self.clientgroesse()
        k, luecke = self.knopf, stil.skaliert(4, self.dpi / GRUNDDPI)
        oben = (self.titel_h - k) // 2
        schliessen = (breite - self.rand - k, oben, breite - self.rand, oben + k)
        verbergen = (schliessen[0] - luecke - k, oben, schliessen[0] - luecke, oben + k)
        deckkraft_b = stil.skaliert(46, self.dpi / GRUNDDPI)
        deckkraft = (verbergen[0] - luecke - deckkraft_b, oben, verbergen[0] - luecke, oben + k)
        return {"schliessen": schliessen, "verbergen": verbergen, "deckkraft": deckkraft}

    def scanner_rechteck(self) -> tuple[int, int, int, int]:
        breite, hoehe = self.clientgroesse()
        k = self.knopf
        oben = hoehe - self.unten_h + (self.unten_h - k) // 2
        return (breite - self.rand - k - 2, oben, breite - self.rand - 2, oben + k)

    def leiste_knopf_rechtecke(self) -> dict[str, tuple[int, int, int, int]]:
        """Die zwei Knöpfe links neben dem Scanner: „Ort“ (Element auf dem Desktop oder im Zielfenster) und „A+H“ (Augen und Hände an/aus)."""
        a, b, c, d = self.scanner_rechteck()
        breite_knopf, luecke = stil.skaliert(40, self.dpi / GRUNDDPI), stil.skaliert(4, self.dpi / GRUNDDPI)
        augen = (a - luecke - breite_knopf, b, a - luecke, d)
        ort = (augen[0] - luecke - breite_knopf, b, augen[0] - luecke, d)
        return {"ort": ort, "augen": augen}

    def setze_augen(self, an: bool) -> None:
        if an != self.augen_an:
            self.augen_an = an
            self.neu_zeichnen()

    def setze_ort_text(self, text: str) -> None:
        if text != self.ort_text:
            self.ort_text = text
            self.neu_zeichnen()

    # ---- Zustand nach außen ------------------------------------------------------------------------------------------
    def setze_identitaet(self, name: str | None = None, farbe_hex: str | None = None) -> None:
        """Neuer Name und/oder neue Farbe des Agenten: Titel und Rahmen folgen sofort."""
        if name:
            self.name = name
            w.user32.SetWindowTextW(self.hwnd, f"{name} · {self.ort}")
        if farbe_hex:
            self.farbe_hex, self.farbe = farbe_hex, w.rgb_hex(farbe_hex)
        self.neu_zeichnen()

    def setze_zustand(self, text: str) -> None:
        self.zustand = text
        self.neu_zeichnen()

    def setze_ziel(self, text: str, gebunden: bool) -> None:
        self.ziel_text, self.ziel_gebunden = text, gebunden
        self.neu_zeichnen()

    def scanner_verbinden(self, scanner_gewuenscht: Callable[[int, int], None]) -> None:
        """Ersetzt den Scanner-Callback nachträglich — der echte Callback (`scanner_anbindung.py`) braucht das
        bereits gebaute Fenster selbst (`terminal.hwnd`, `terminal.setze_ziel`), ist zur Konstruktionszeit also
        noch nicht verfügbar."""
        self._scanner = scanner_gewuenscht

    def deckkraft_prozent(self) -> int:
        return stil.alpha_prozent(self.deckkraft or 255)

    def ausgabe(self, daten: bytes) -> None:
        """Neue Bytes der Sitzung. Gezeichnet wird gebündelt, höchstens etwa 60-mal je Sekunde."""
        self.modell.einspeisen(daten)
        if not self._zeichnen_geplant:
            self._zeichnen_geplant = True
            self.starte_timer(TIMER_ZEICHNEN, 16)

    def text_aller_zeilen(self) -> list[str]:
        return self.modell.bildschirm.display

    # ---- Zeichnen ----------------------------------------------------------------------------------------------------
    def _ersatz_schrift(self, leinwand: Leinwand, zeichen: str) -> Schrift | None:
        if ord(zeichen[0]) < 0x100:
            return None
        if zeichen in self._ersatz:
            return self._ersatz[zeichen]
        gewaehlt = None
        if not self.f_terminal.hat_glyphen(leinwand.hdc, zeichen)[0]:
            for kandidat in self.f_ersatz:
                if kandidat.hat_glyphen(leinwand.hdc, zeichen)[0]:
                    gewaehlt = kandidat
                    break
        self._ersatz[zeichen] = gewaehlt
        return gewaehlt

    def zeichnen(self, leinwand: Leinwand) -> None:
        breite, hoehe = leinwand.breite, leinwand.hoehe
        leinwand.fuellen(GRUND)
        self._zeichne_titel(leinwand, breite)
        self._zeichne_gitter(leinwand)
        self._zeichne_leiste(leinwand, breite, hoehe)
        rahmen = 2 if self._hat_fokus else 1
        leinwand.rahmen(0, 0, breite, hoehe, self.farbe, rahmen)

    def _zeichne_titel(self, l: Leinwand, breite: int) -> None:
        l.fuellen(stil.FARBE_TITEL, 0, 0, breite, self.titel_h)
        quadrat = stil.skaliert(12, self.dpi / GRUNDDPI)
        y = (self.titel_h - quadrat) // 2
        l.fuellen(self.farbe, self.rand + 2, y, self.rand + 2 + quadrat, y + quadrat)
        text_x = self.rand + 2 + quadrat + stil.skaliert(8, self.dpi / GRUNDDPI)
        text_y = (self.titel_h - self.f_ui.zellhoehe) // 2
        l.text(text_x, text_y, f"{self.name} · {self.ort}", stil.FARBE_TEXT, self.f_ui)
        name_breite = self.f_ui.breite(l.hdc, f"{self.name} · {self.ort}")
        rechtes_ende = min(rect[0] for rect in self.knopf_rechtecke().values()) - 8
        zustand_x = text_x + name_breite + stil.skaliert(12, self.dpi / GRUNDDPI)
        if zustand_x < rechtes_ende:
            farbe = stil.FARBE_TEXT_GEDAEMPFT
            if self.zustand.startswith(("fehl", "beendet")):
                farbe = stil.FARBE_FEHLER
            elif self.zustand.startswith("läuft"):
                farbe = stil.FARBE_OK
            l.text(zustand_x, text_y, self.zustand, farbe, self.f_ui)
        rechtecke = self.knopf_rechtecke()
        for schluessel, (a, b, c, d) in rechtecke.items():
            l.fuellen(stil.FARBE_KNOPF_AKTIV if self._knopf_unten == schluessel else stil.FARBE_KNOPF, a, b, c, d)
            mitte_x, mitte_y, r = (a + c) // 2, (b + d) // 2, stil.skaliert(4, self.dpi / GRUNDDPI)
            if schluessel == "schliessen":
                l.linie(mitte_x - r, mitte_y - r, mitte_x + r + 1, mitte_y + r + 1, stil.FARBE_TEXT, 2)
                l.linie(mitte_x - r, mitte_y + r, mitte_x + r + 1, mitte_y - r - 1, stil.FARBE_TEXT, 2)
            elif schluessel == "verbergen":
                l.linie(mitte_x - r, mitte_y + r // 2, mitte_x + r + 1, mitte_y + r // 2, stil.FARBE_TEXT, 2)
            else:
                text = f"{self.deckkraft_prozent()}%"
                l.text(a + (c - a - self.f_ui.breite(l.hdc, text)) // 2, b + (d - b - self.f_ui.zellhoehe) // 2, text, stil.FARBE_TEXT, self.f_ui)

    def _zeichne_leiste(self, l: Leinwand, breite: int, hoehe: int) -> None:
        l.fuellen(stil.FARBE_LEISTE, 0, hoehe - self.unten_h, breite, hoehe)
        a, b, c, d = self.scanner_rechteck()
        l.fuellen(stil.FARBE_KNOPF_AKTIV if self._knopf_unten == "scanner" else stil.FARBE_KNOPF, a, b, c, d)
        mitte_x, mitte_y = (a + c) // 2, (b + d) // 2
        r = (c - a) // 2 - 4
        l.rahmen(mitte_x - r, mitte_y - r, mitte_x + r + 1, mitte_y + r + 1, stil.FARBE_TEXT, 1)
        l.linie(mitte_x - r - 3, mitte_y, mitte_x + r + 4, mitte_y, stil.FARBE_TEXT, 1)
        l.linie(mitte_x, mitte_y - r - 3, mitte_x, mitte_y + r + 4, stil.FARBE_TEXT, 1)
        if self.ziel_gebunden:
            l.fuellen(stil.FARBE_OK, c - 5, b, c, b + 5)
        text_y = hoehe - self.unten_h + (self.unten_h - self.f_ui.zellhoehe) // 2
        l.text(self.rand + 4, text_y, self.ziel_text, stil.FARBE_OK if self.ziel_gebunden else stil.FARBE_TEXT_GEDAEMPFT, self.f_ui)
        for name, (ka, kb, kc, kd) in self.leiste_knopf_rechtecke().items():
            gedrueckt = self._knopf_unten == name
            if name == "augen":
                text, farbe = ("A+H", stil.FARBE_OK) if self.augen_an else ("nur T", stil.FARBE_WARNUNG)
            else:
                text, farbe = self.ort_text, stil.FARBE_TEXT
            l.fuellen(stil.FARBE_KNOPF_AKTIV if gedrueckt else stil.FARBE_KNOPF, ka, kb, kc, kd)
            l.rahmen(ka, kb, kc, kd, farbe, 1)
            l.text(ka + (kc - ka - self.f_ui.breite(l.hdc, text)) // 2, kb + (kd - kb - self.f_ui.zellhoehe) // 2, text, farbe, self.f_ui)
        if self.modell.im_verlauf():
            marke = "↑ Verlauf"
            l.text(self.leiste_knopf_rechtecke()["ort"][0] - self.f_ui.breite(l.hdc, marke) - 12, text_y, marke, stil.FARBE_WARNUNG, self.f_ui)

    def _zeichne_gitter(self, l: Leinwand) -> None:
        links, oben, rechts, unten = self.gitter_rechteck()
        zeilen, spalten = self.zeilen_spalten()
        modell = self.modell
        zeilen, spalten = min(zeilen, modell.zeilen), min(spalten, modell.spalten)
        cursor_z, cursor_s, cursor_sichtbar = modell.cursor()
        zeige_cursor = cursor_sichtbar and not modell.im_verlauf()
        zw, zh = self.zell_b, self.zell_h
        for z in range(zeilen):
            y = oben + z * zh
            lauf: list | None = None  # [text, breiten, vordergrund, hintergrund, fett, unterstrichen, durchgestrichen, x]
            s = 0
            while s < spalten:
                zelle = modell.zelle(z, s)
                if zelle.stumm:
                    s += 1
                    continue
                vorn, hinten = zelle.vordergrund, zelle.hintergrund
                if modell.ist_ausgewaehlt(z, s):
                    hinten = (38, 79, 120)
                cursor_hier = zeige_cursor and z == cursor_z and s == cursor_s
                if cursor_hier and self._hat_fokus and self._cursor_phase:
                    vorn, hinten = hinten, vorn
                breite = zw * (2 if zelle.breit else 1)
                ersatz = self._ersatz_schrift(l, zelle.zeichen) if zelle.zeichen != " " else None
                schluessel = (w.rgb(*vorn), w.rgb(*hinten), zelle.fett, zelle.unterstrichen, zelle.durchgestrichen)
                if ersatz is not None or lauf is None or lauf[2:7] != list(schluessel):
                    if lauf is not None:
                        self._lauf_zeichnen(l, lauf, y)
                        lauf = None
                if ersatz is not None:
                    l.fuellen(schluessel[1], links + s * zw, y, links + s * zw + breite, y + zh)
                    l.text(links + s * zw, y, zelle.zeichen, schluessel[0], ersatz, breiten=[breite])
                else:
                    if lauf is None:
                        lauf = ["", [], *schluessel, links + s * zw]
                    lauf[0] += zelle.zeichen
                    lauf[1].append(breite)
                if cursor_hier and not self._hat_fokus:
                    l.rahmen(links + s * zw, y, links + s * zw + breite, y + zh, w.rgb(*zelle.vordergrund), 1)
                s += 2 if zelle.breit else 1
            if lauf is not None:
                self._lauf_zeichnen(l, lauf, y)
        # Rest rechts und unten neben dem Zeichengitter
        l.fuellen(GRUND, links + spalten * zw, oben, rechts, unten)
        l.fuellen(GRUND, links, oben + zeilen * zh, rechts, unten)
        self._zeichne_rollbalken(l)

    def _zeichne_rollbalken(self, l: Leinwand) -> None:
        a, b, c, d = self.rollbalken_rechteck()
        l.fuellen(stil.farbe_hell(GRUND, 1.4), a, b, c, d)
        griff = self.griff_rechteck()
        if griff is not None:
            gedrueckt = self._balken_ziehen is not None
            l.fuellen(stil.FARBE_TEXT if gedrueckt else stil.FARBE_TEXT_GEDAEMPFT, *griff)

    def _lauf_zeichnen(self, l: Leinwand, lauf: list, y: int) -> None:
        text, breiten, vorn, hinten, fett, unterstrichen, durchgestrichen, x = lauf
        schrift = self.f_fett if fett else self.f_terminal
        l.text(x, y, text, vorn, schrift, hintergrund=hinten, breiten=breiten)
        gesamt = sum(breiten)
        if unterstrichen:
            l.linie(x, y + self.zell_h - 2, x + gesamt, y + self.zell_h - 2, vorn, 1)
        if durchgestrichen:
            l.linie(x, y + self.zell_h // 2, x + gesamt, y + self.zell_h // 2, vorn, 1)

    # ---- Treffer, Maus -----------------------------------------------------------------------------------------------
    def _client_punkt(self, x_schirm: int, y_schirm: int) -> tuple[int, int]:
        links, oben, _, _ = self.rechteck()
        return x_schirm - links, y_schirm - oben

    @staticmethod
    def _in(rect: tuple[int, int, int, int], x: int, y: int) -> bool:
        return rect[0] <= x < rect[2] and rect[1] <= y < rect[3]

    def treffer(self, x: int, y: int) -> int | None:
        cx, cy = self._client_punkt(x, y)
        breite, hoehe = self.clientgroesse()
        kante = self.rand
        links, rechts, oben, unten = cx < kante, cx >= breite - kante, cy < kante, cy >= hoehe - kante
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
        if cy < self.titel_h and not any(self._in(r, cx, cy) for r in self.knopf_rechtecke().values()):
            return w.HTCAPTION
        return w.HTCLIENT

    def zelle_bei(self, x: int, y: int) -> tuple[int, int]:
        links, oben, _, _ = self.gitter_rechteck()
        zeilen, spalten = self.zeilen_spalten()
        return (max(0, min(self.modell.zeilen - 1, (y - oben) // self.zell_h)),
                max(0, min(self.modell.spalten - 1, (x - links) // self.zell_b)))

    def _im_gitter(self, x: int, y: int) -> bool:
        return self._in(self.gitter_rechteck(), x, y)

    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        w.user32.SetFocus(self.hwnd)
        for schluessel, rect in self.knopf_rechtecke().items():
            if self._in(rect, x, y):
                self._knopf_unten = schluessel
                self.erfasse_maus()
                self.neu_zeichnen()
                return 0
        if self._in(self.scanner_rechteck(), x, y):
            self._knopf_unten = "scanner"
            self.erfasse_maus()
            self.neu_zeichnen()
            return 0
        for schluessel, rect in self.leiste_knopf_rechtecke().items():
            if self._in(rect, x, y):
                self._knopf_unten = schluessel
                self.erfasse_maus()
                self.neu_zeichnen()
                return 0
        if self._in(self.rollbalken_rechteck(), x, y):
            self._rollbalken_druecken(y)
            return 0
        if self._im_gitter(x, y):
            self._auswahl_anker = self.zelle_bei(x, y)
            self._ziehen = False
            self.modell.auswahl_setzen(None)
            self.erfasse_maus()
            self.neu_zeichnen()
        return 0

    def _rollbalken_druecken(self, y: int) -> None:
        griff = self.griff_rechteck()
        if griff is None:
            return
        if griff[1] <= y < griff[3]:
            self._balken_ziehen = y - griff[1]  # am Griff packen, ohne dass er springt
        else:
            self._balken_ziehen = (griff[3] - griff[1]) // 2  # in die Leiste geklickt: Griff dorthin setzen
            self._balken_zu(y)
        self.erfasse_maus()
        self.neu_zeichnen()

    def _balken_zu(self, y: int) -> None:
        if self.modell.zu_versatz(self._versatz_fuer(y, self._balken_ziehen or 0)):
            self.neu_zeichnen()

    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None:
        self._maus_y = y
        if self._balken_ziehen is not None and flags & 0x0001:
            self._balken_zu(y)
            return 0
        if self._auswahl_anker is not None and flags & 0x0001:
            aktuell = self.zelle_bei(x, y)
            self._ziehen = self._ziehen or aktuell != self._auswahl_anker
            self._auswahl_erweitern(aktuell)
            _, oben, _, unten = self.gitter_rechteck()
            if y < oben or y >= unten:
                self.starte_timer(TIMER_AUTOSCROLL, 60)  # über den Rand hinaus gezogen: weiterblättern, auch ohne Mausbewegung
            else:
                self.stoppe_timer(TIMER_AUTOSCROLL)
        return 0

    def _autoscroll(self) -> None:
        """Beim Markieren über den oberen/unteren Rand hinaus: weiterblättern, die Auswahl wächst mit."""
        if self._auswahl_anker is None:
            self.stoppe_timer(TIMER_AUTOSCROLL)
            return
        _, oben, _, unten = self.gitter_rechteck()
        if oben <= self._maus_y < unten:
            self.stoppe_timer(TIMER_AUTOSCROLL)
            return
        schritt = RAD_ZEILEN if self._maus_y < oben else -RAD_ZEILEN
        bewegt = self.modell.blaettern_zeilen(schritt)
        zeile, spalte = self._auswahl_anker
        self._auswahl_anker = (max(0, min(self.modell.zeilen - 1, zeile + bewegt)), spalte)
        rand_zeile = 0 if self._maus_y < oben else self.modell.zeilen - 1
        mitte = self.zelle_bei(self.gitter_rechteck()[0], oben + rand_zeile * self.zell_h)
        self._auswahl_erweitern((rand_zeile, mitte[1]))

    def _auswahl_erweitern(self, aktuell: tuple[int, int]) -> None:
        anker = self._auswahl_anker
        if aktuell >= anker:
            self.modell.auswahl_setzen(anker, (aktuell[0], aktuell[1] + 1))
        else:
            self.modell.auswahl_setzen(aktuell, (anker[0], anker[1] + 1))
        self.neu_zeichnen()

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        gedrueckt, self._knopf_unten = self._knopf_unten, None
        self.gib_maus_frei()
        self.stoppe_timer(TIMER_AUTOSCROLL)
        if self._balken_ziehen is not None:
            self._balken_ziehen = None
            self.neu_zeichnen()
            return 0
        if gedrueckt is not None:
            if gedrueckt == "scanner":
                rect = self.scanner_rechteck()
            else:
                rect = self.leiste_knopf_rechtecke().get(gedrueckt) or self.knopf_rechtecke()[gedrueckt]
            if self._in(rect, x, y):
                self._knopf_ausloesen(gedrueckt)
            self.neu_zeichnen()
            return 0
        if self._auswahl_anker is not None:
            if not self._ziehen:
                self.modell.auswahl_setzen(None)
            self._auswahl_anker = None
            self.neu_zeichnen()
        return 0

    def bei_maus_verloren(self) -> None:
        self._knopf_unten = None
        self._auswahl_anker = None
        self._balken_ziehen = None
        self.stoppe_timer(TIMER_AUTOSCROLL)

    def _knopf_ausloesen(self, knopf: str) -> None:
        if knopf == "schliessen":
            self._schliessen()
        elif knopf == "verbergen":
            self._verbergen()
        elif knopf == "deckkraft":
            self.setze_deckkraft(stil.deckkraft_alpha(stil.naechste_stufe(self.deckkraft_prozent())))
            self._layout_geaendert()
        elif knopf == "augen":
            self._augen()
        elif knopf == "ort":
            a, b, c, d = self.leiste_knopf_rechtecke()["ort"]
            links, oben, _, _ = self.rechteck()
            self._ort(links + a, oben + d)
        elif knopf == "scanner":
            a, b, c, d = self.scanner_rechteck()
            links, oben, _, _ = self.rechteck()
            self._scanner(links + a, oben + b)

    def bei_doppelklick(self, x: int, y: int, flags: int) -> int | None:
        if self._im_gitter(x, y):
            zeile, spalte = self.zelle_bei(x, y)
            anfang, ende = self.modell.wort_bei(zeile, spalte)
            self.modell.auswahl_setzen(anfang, ende)
            self.neu_zeichnen()
        return 0

    MENUE_KOPIEREN, MENUE_EINFUEGEN, MENUE_ALLES, MENUE_AUFHEBEN = 1, 2, 3, 4

    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None:
        """Wie ein gewohntes Terminal: ein Menü mit Kopieren, Einfügen, Alles markieren und Auswahl aufheben."""
        if not self._im_gitter(x, y):
            return 0
        hat_auswahl = self.modell.auswahl is not None
        links, oben, _, _ = self.rechteck()  # x, y sind Fensterkoordinaten, das Menü braucht Bildschirmkoordinaten
        befehl = zeige_menue(self.hwnd, [
            (self.MENUE_KOPIEREN, "Kopieren", 0 if hat_auswahl else ABGEBLENDET),
            (self.MENUE_EINFUEGEN, "Einfügen", 0),
            None,
            (self.MENUE_ALLES, "Alles markieren", 0),
            (self.MENUE_AUFHEBEN, "Auswahl aufheben", 0 if hat_auswahl else ABGEBLENDET),
        ], links + x, oben + y)
        if befehl == self.MENUE_KOPIEREN:
            self.kopieren()
        elif befehl == self.MENUE_EINFUEGEN:
            self.einfuegen()
        elif befehl == self.MENUE_ALLES:
            self.modell.alles_markieren()
        elif befehl == self.MENUE_AUFHEBEN:
            self.modell.auswahl_setzen(None)
        if befehl:
            self.neu_zeichnen()
        return 0

    def bei_rad(self, delta: int, x: int, y: int, flags: int) -> int | None:
        client_x, client_y = self._client_punkt(x, y)
        if client_y < self.titel_h:
            prozent = max(10, min(100, self.deckkraft_prozent() + (5 if delta > 0 else -5)))
            self.setze_deckkraft(stil.deckkraft_alpha(prozent))
            self.neu_zeichnen()
            self._layout_geaendert()
            return 0
        if self._im_gitter(client_x, client_y):
            zeile, spalte = self.zelle_bei(client_x, client_y)
            meldung = self.modell.rad_meldung(delta > 0, zeile, spalte)
            if meldung is not None:  # das Programm will das Rad selbst (z. B. Vollbild-Oberfläche): ihm geben, nicht selbst blättern
                self._senden(meldung * RAD_ZEILEN)
                return 0
        self.modell.blaettern_zeilen(RAD_ZEILEN if delta > 0 else -RAD_ZEILEN)
        self.neu_zeichnen()
        return 0

    def bei_nachricht(self, msg: int, wparam: int, lparam: int) -> int | None:
        if msg == w.WM_SETCURSOR and w.loword(lparam) == w.HTCLIENT:
            punkt = self.maus_position()
            links, oben, _, _ = self.rechteck()
            art = w.IDC_IBEAM if self._im_gitter(punkt[0] - links, punkt[1] - oben) else w.IDC_ARROW
            self.mauszeiger(art)
            return 1
        if msg == w.WM_NCCALCSIZE and wparam:
            return 0
        if msg == w.WM_GETMINMAXINFO:
            info = ctypes.cast(lparam, ctypes.POINTER(w.MINMAXINFO)).contents
            info.ptMinTrackSize.x = 2 * (self.rand + self.pad) + 20 * self.zell_b
            info.ptMinTrackSize.y = self.titel_h + self.unten_h + 2 * self.pad + 4 * self.zell_h
            return 0
        if msg == w.WM_MOUSEACTIVATE:
            return w.MA_ACTIVATE
        if msg in (w.WM_MOVE, w.WM_EXITSIZEMOVE):
            self._layout_geaendert()
        return None

    # ---- Tastatur ----------------------------------------------------------------------------------------------------
    def _umschalter(self) -> tuple[bool, bool, bool]:
        gedrueckt = lambda vk: bool(w.user32.GetKeyState(vk) & 0x8000)  # noqa: E731
        return gedrueckt(w.VK_SHIFT), gedrueckt(w.VK_MENU), gedrueckt(w.VK_CONTROL)

    def bei_taste(self, vk: int, lparam: int, syskey: bool) -> int | None:
        if vk in (w.VK_SHIFT, w.VK_CONTROL, w.VK_MENU):
            return 0
        umschalt, alt, strg = self._umschalter()
        if strg and umschalt and vk == ord("C"):
            self._char_unterdruecken = True
            self.kopieren()
            return 0
        if (strg and umschalt and vk == ord("V")) or (umschalt and not strg and vk == w.VK_INSERT):
            self._char_unterdruecken = True
            self.einfuegen()
            return 0
        altgr = strg and alt
        daten = taste_zu_bytes(vk, umschalt=umschalt, alt=alt and not altgr, strg=strg and not altgr,
                               anwendungs_cursor=self.modell.anwendungs_cursor())
        if daten is not None:
            if vk in (w.VK_TAB, 0x20):
                self._char_unterdruecken = True
            self._eingabe(daten)
            return 0
        return 0 if syskey else None

    def bei_zeichen(self, code: int, syskey: bool) -> int | None:
        if self._char_unterdruecken:
            self._char_unterdruecken = False
            return 0
        if 0xD800 <= code <= 0xDBFF:
            self._hohes_ersatzzeichen = code
            return 0
        if 0xDC00 <= code <= 0xDFFF and self._hohes_ersatzzeichen:
            ganz = 0x10000 + ((self._hohes_ersatzzeichen - 0xD800) << 10) + (code - 0xDC00)
            self._hohes_ersatzzeichen = 0
            self._eingabe(chr(ganz).encode("utf-8"))
            return 0
        daten = zeichen_zu_bytes(code, alt=syskey)
        if daten is not None:
            self._eingabe(daten)
        return 0

    def _eingabe(self, daten: bytes) -> None:
        if self.modell.im_verlauf():
            self.modell.blaettern(-1000)
            self.neu_zeichnen()
        self._senden(daten)

    def zuruecksetzen(self) -> None:
        """Wiederaufnahme einer laufenden Sitzung: der Starter schickt ihre letzte Ausgabe noch einmal, der Bildschirm baut sich daraus neu auf."""
        self.modell.zuruecksetzen()
        self.neu_zeichnen()

    def tippe(self, text: str) -> None:
        """Text wie eingegeben (für Chat und Regie): zeichenweise als Eingabe an die Sitzung."""
        self._eingabe(text.encode("utf-8"))

    def kopieren(self) -> bool:
        text = self.modell.auswahl_text()
        return bool(text) and text_in_zwischenablage(self.hwnd, text)

    def einfuegen(self) -> None:
        text = text_aus_zwischenablage(self.hwnd)
        if text:
            self._eingabe(einfuegen_zu_bytes(text, self.modell.eingeklammertes_einfuegen()))

    def bei_fokus(self, hat_fokus: bool) -> None:
        self._hat_fokus = hat_fokus
        self.neu_zeichnen()

    # ---- Größe, Zeit -------------------------------------------------------------------------------------------------
    def bei_groesse(self, breite: int, hoehe: int) -> None:
        if not hasattr(self, "modell"):
            return
        zeilen, spalten = self.zeilen_spalten()
        if self.modell.groesse_setzen(zeilen, spalten):
            self.starte_timer(TIMER_GROESSE, 150)
        self._layout_geaendert()

    def bei_dpi(self, dpi: int) -> None:
        self.dpi = dpi
        self._schriften_bauen(dpi / GRUNDDPI)
        self.neu_zeichnen()

    def bei_timer(self, ident: int) -> None:
        if ident == TIMER_ZEICHNEN:
            self.stoppe_timer(TIMER_ZEICHNEN)
            self._zeichnen_geplant = False
            self.neu_zeichnen()
        elif ident == TIMER_CURSOR:
            self._cursor_phase = not self._cursor_phase
            if self._hat_fokus and self.modell.cursor()[2]:
                self.neu_zeichnen()
        elif ident == TIMER_AUTOSCROLL:
            self._autoscroll()
        elif ident == TIMER_GROESSE:
            self.stoppe_timer(TIMER_GROESSE)
            groesse = (self.modell.zeilen, self.modell.spalten)
            if groesse != self._gemeldet:
                self._gemeldet = groesse
                self._groesse_gemeldet(*groesse)

    def bei_zerstoert(self) -> None:
        for schrift in (self.f_terminal, self.f_fett, self.f_ui, *self.f_ersatz):
            schrift.freigeben()
