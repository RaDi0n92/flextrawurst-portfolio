"""Der erste Körper eines Agenten zusammengesetzt: Raute, Terminal, Banner, Ticker und der Fensterscanner
als ein gemeinsam laufendes Ganzes (BE03/G02).

Reine Verdrahtung — die Fenster und der Fensterscanner sind einzeln gebaut und getestet; hier werden nur ihre
Callbacks aneinandergehängt:

* `RauteFenster.sagen()` (der Agent spricht) → Banner (3,3 s, im Zielbereich, blendet aus) und Ticker (6,6 s, an der
  Raute) gleichzeitig, plus `gesprochen(name, text)` an den Besitzer, der es im gemeinsamen Chat einträgt (R026).
* `zeige_ticker()`: Hinweise der Bridge an der Raute (Box neben der Raute, 9,9 s).
* `zeige_daniel()`: Daniels Worte (Chat, Regie) als Box neben der Raute wie jeder Hinweis (9,9 s); das frühere Raum-Banner mit Fade ist entfernt (Daniel, 2026-10-04).
* Die Raute hat keinen Klick-Zweck; Mit gehaltener Bedientaste (Standard Strg+Alt) verschiebt Ziehen sie und ein Rechtsklick öffnet das
  Menü (Status, Transparenz, Größe, Tastenkombination, Terminal, Not-Aus, Beenden). Raute verschoben → Ticker folgt.
* Scanner-Knopf des Terminals → `scanner_anbindung.mache_scanner_callback()`.
* Nichts davon tippt ins Terminal; das Terminal gehört Daniel allein.

Die Verbindung zum Relay hält der Besitzer (`koerper/anwendung.py`); hier kommt sie nur als `terminal_senden`,
`agent_beenden` und `bridge_beenden` an. Die Fensterklassen sind injizierbar, damit die Verdrahtung ohne Windows
testbar bleibt.
"""

from __future__ import annotations

import re
import ctypes
import time
from collections.abc import Callable

from augen_haende_bridge.harness import HarnessRun
from augen_haende_bridge.windows_capture import WindowsScreenCapture
from augen_haende_bridge.windows_scanner import WindowsWindowScanner

from . import menue, offene_menues, stil, ziele
from . import win32 as w
from .eingabe_fenster import RauteEingabe, feld_position
from .nachricht_fenster import BannerFenster, TickerFenster
from .notaus import NotAus
from . import raute_fenster
from .raute_fenster import STATUS_TEXT, RauteFenster
from .scanner_anbindung import Bindung, mache_scanner_callback
from .ziel_halter import fenster_zustand
from .terminal_fenster import TerminalFenster

(MENUE_TERMINAL, MENUE_AGENT_BEENDEN, MENUE_BRIDGE_BEENDEN, MENUE_STATUS, MENUE_NOTAUS,
 MENUE_TRANSPARENZ, MENUE_GROESSER, MENUE_KLEINER, MENUE_RAUTE_REGEL, MENUE_TERMINAL_REGEL, MENUE_TERMINAL_DURCHKLICK, MENUE_HOTKEY, MENUE_HAENDE, MENUE_BILDER,
 MENUE_NAME, MENUE_FARBE, MENUE_NUR_TERMINAL, MENUE_ORT, MENUE_BILD_DATEI, MENUE_BILDFOLGE, MENUE_PLAETZE, MENUE_ZEICHNEN, MENUE_BILD_ELEMENT, MENUE_ANZEIGEORT, MENUE_PAUSE, MENUE_PROFIL, MENUE_AUSNAHME) = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28

Rechteck = tuple[int, int, int, int]


def arbeitsflaeche() -> Rechteck:
    """Der Desktop ohne Taskleiste — das Standardziel, solange nichts gebunden ist (R120)."""
    rect = w.RECT()
    w.user32.SystemParametersInfoW(w.SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right, rect.bottom


def _jetzt_ms() -> int:
    return int(time.monotonic() * 1000)


class ErsterKoerper:
    """Eine Instanz pro gestartetem Agenten (R119): hält Raute, Terminal und die dazwischen entstehenden
    Banner- und Ticker-Fenster zusammen."""

    def __init__(self, *, name: str, ort: str, farbe_hex: str | None = None, hotkey: str | None = None,
                 gesprochen: Callable[[str, str], None] = lambda name, text: None,
                 meldungen_zeigen: Callable[[], bool] = lambda: True,
                 regel_menue: Callable[[str, int, int], None] = lambda element, x, y: None,
                 regeltext: Callable[[str], str] = lambda element: "immer sichtbar",
                 durchklick_text: Callable[[str], str] = lambda element: "aus",
                 bedientaste_text: Callable[[], str] = lambda: "Strg",
                 modifikator: Callable[[], bool] | None = None,
                 hotkey_festlegen: Callable[[], None] = lambda: None,
                 name_aendern: Callable[[], None] = lambda: None,
                 augen_an: Callable[[], bool] = lambda: True,
                 nur_terminal_umschalten: Callable[[], None] = lambda: None,
                 ort_menue: Callable[[int, int], None] = lambda x, y: None,
                 bild_datei: Callable[[], None] = lambda: None,
                 bildfolge_menue: Callable[[int, int], None] = lambda x, y: None,
                 plaetze_menue: Callable[[int, int], None] = lambda x, y: None,
                 zeichnen: Callable[[], None] = lambda: None,
                 bild_element: Callable[[], None] = lambda: None,
                 anzeigeort_menue: Callable[[int, int], None] = lambda x, y: None,
                 farbe_waehlen: Callable[[int, int], None] = lambda x, y: None,
                 haende_text: Callable[[], str] = lambda: "aus",
                 bilder_text: Callable[[], str] = lambda: "kein Ziel gebunden",
                 bilder_umschalten: Callable[[], None] = lambda: None,
                 haende_umschalten: Callable[[], None] = lambda: None,
                 durchklick_umschalten: Callable[[str], None] = lambda element: None,
                 raute_position: tuple[int, int] = (100, 100),
                 terminal_position: tuple[int, int] = (220, 100),
                 terminal_senden: Callable[[bytes], None] = lambda daten: None,
                 terminal_groesse: Callable[[int, int], None] = lambda zeilen, spalten: None,
                 agent_beenden: Callable[[], None] = lambda: None,
                 agent_pause: Callable[[], None] = lambda: None,
                 agent_pausiert: Callable[[], bool] = lambda: False,
                 profil_text: Callable[[], str] = lambda: "geteilte_maus",
                 profil_wechseln: Callable[[], None] = lambda: None,
                 ausnahme_text: Callable[[], str] = lambda: "aus",
                 ausnahme_umschalten: Callable[[], None] = lambda: None,
                 bridge_beenden: Callable[[], None] = lambda: None,
                 scanner: WindowsWindowScanner | None = None,
                 capture: WindowsScreenCapture | None = None,
                 ziel_rechteck: Callable[[], Rechteck] = arbeitsflaeche,
                 ziel_gebunden: Callable[[Bindung], None] = lambda bindung: None,
                 ziel_geloest: Callable[[], None] = lambda: None,
                 jetzt_ms: Callable[[], int] = _jetzt_ms,
                 menue_anzeigen: Callable[..., int] = menue.zeige_menue,
                 not_aus: NotAus | None = None,
                 raute_klasse: type[RauteFenster] = RauteFenster,
                 terminal_klasse: type[TerminalFenster] = TerminalFenster,
                 banner_klasse: type[BannerFenster] = BannerFenster,
                 ticker_klasse: type[TickerFenster] = TickerFenster,
                 eingabe_klasse: type[RauteEingabe] = RauteEingabe,
                 bildschirm: Callable[[], Rechteck] = arbeitsflaeche):
        self.name = name
        self.farbe_hex = farbe_hex or stil.agentenfarbe(name)
        self._name_aendern, self._farbe_waehlen = name_aendern, farbe_waehlen
        self._augen_an, self._nur_terminal_umschalten, self._ort_menue = augen_an, nur_terminal_umschalten, ort_menue
        self._bild_datei, self._bildfolge_menue, self._plaetze_menue = bild_datei, bildfolge_menue, plaetze_menue
        self._zeichnen = zeichnen
        self._bild_element = bild_element
        self._anzeigeort_menue = anzeigeort_menue
        self._scanner_quelle = scanner if scanner is not None else WindowsWindowScanner()
        self._capture_quelle = capture if capture is not None else WindowsScreenCapture()
        self.ziel_rechteck = ziel_rechteck
        self._jetzt_ms = jetzt_ms
        self._banner_klasse = banner_klasse
        self._ticker_klasse = ticker_klasse
        self._eingabe_klasse = eingabe_klasse
        self._bildschirm = bildschirm
        self.eingabe: RauteEingabe | None = None
        self._gesprochen = gesprochen
        self._meldungen_zeigen = meldungen_zeigen
        self._regel_menue = regel_menue
        self._regeltext = regeltext
        self._durchklick_text = durchklick_text
        self._bedientaste_text = bedientaste_text
        self._hotkey_festlegen = hotkey_festlegen
        self._haende_text = haende_text
        self._bilder_text = bilder_text
        self._bilder_umschalten = bilder_umschalten
        self._haende_umschalten = haende_umschalten
        self._durchklick_umschalten = durchklick_umschalten
        self.terminal_ausgeblendet = False  # von Daniel ausgeblendet: die Sichtbarkeitsregel bringt es nicht von selbst zurück
        self._menue_anzeigen = menue_anzeigen
        self.not_aus = not_aus if not_aus is not None else NotAus()
        self._agent_beenden = agent_beenden
        self._ausnahme_text, self._ausnahme_umschalten = ausnahme_text, ausnahme_umschalten
        self._profil_text, self._profil_wechseln = profil_text, profil_wechseln  # G10: Steuerprofil der Hände
        self._agent_pause, self._agent_pausiert = agent_pause, agent_pausiert  # G09: Prozessgruppe anhalten/fortsetzen
        self._bridge_beenden = bridge_beenden
        self.banner: BannerFenster | None = None
        self.ticker: TickerFenster | None = None

        self.bindung: Bindung | None = None
        self.letzter_scanner_lauf: HarnessRun | None = None
        self._arbeitsflaeche = ziel_rechteck
        self._ziel_gebunden_melden = ziel_gebunden
        self._ziel_geloest_melden = ziel_geloest

        self.terminal = terminal_klasse(*terminal_position, name=name, ort=ort, farbe_hex=self.farbe_hex,
                                        senden=terminal_senden, groesse_gemeldet=terminal_groesse,
                                        # R114: Ausblenden lässt die Sitzung laufen; beendet wird nur über das Raute-Menü.
                                        schliessen_gewuenscht=self._terminal_ausblenden,
                                        verbergen_gewuenscht=self._terminal_ausblenden,
                                        ort_gewuenscht=ort_menue, augen_umschalten=nur_terminal_umschalten)
        self.terminal.scanner_verbinden(mache_scanner_callback(
            self.terminal, scanner=self._scanner_quelle, capture=self._capture_quelle, agent_id=name,
            menue_anzeigen=menue_anzeigen, gebunden=self._ziel_gebunden, geloest=self._ziel_geloest,
            lauf_beendet=lambda lauf: setattr(self, "letzter_scanner_lauf", lauf)))

        self.raute = raute_klasse(*raute_position, name=name, farbe_hex=self.farbe_hex, hotkey=hotkey,
                                  modifikator=modifikator,
                                  menue_gewuenscht=self._raute_menue,
                                  verschoben=self._raute_verschoben,
                                  nachricht_gesendet=self._raute_hat_gesprochen)

    # ---- Raute spricht: Banner und Ticker gleichzeitig, der Besitzer trägt es in den gemeinsamen Chat ---------------
    def _terminal_ausblenden(self) -> None:
        self.terminal_ausgeblendet = True
        self.terminal.verberge()

    def _raute_hat_gesprochen(self, text: str) -> None:
        if not self._augen_an():
            return  # „nur Terminal“: kein Rautenchat, kein Banner, keine Box (ohne Bilder gibt es kein Gegenlesen)
        self._gesprochen(self.name, text)
        if not self._meldungen_zeigen():
            return  # die Raute ist gerade wegen ihrer Sichtbarkeitsregel unsichtbar: kein Banner, kein Ticker
        for alt in (self.banner, self.ticker):
            if alt is not None:
                alt.schliessen()
        # nur die Box neben der Raute (Daniel 2026-10-04: kein zweites, größeres Textfeld im Bild; es bleiben ein Text neben der Raute und das Chatfenster)
        self.ticker = self._ticker_klasse(text=text, farbe_hex=self.farbe_hex, raute_rechteck=self.raute.rechteck(),
                                          geschlossen=self._ticker_geschlossen, grenzen=self._bildschirm,
                                          meiden=self._banner_rechtecke)
        self.ticker.zeige(aktivieren=False)

    # ---- Scanner hat gebunden: gebundenes Fenster wird Zielbereich (R027), Besitzer schickt das Bild -------------
    def _ziel_gebunden(self, bindung: Bindung) -> None:
        self.bindung = bindung
        rect = bindung.item.rect
        kennung = ziele.fenster_kennung(str(getattr(bindung.item, "target_id", "")))
        if rect is not None and kennung is not None:
            hwnd, letzte = kennung, [rect]

            def fenster_rect(hwnd=hwnd, letzte=letzte) -> Rechteck:
                """Das Zielfenster, wo es gerade steht (Banner und Selbstbild folgen ihm); ist es weg oder minimiert, das zuletzt bekannte Rechteck."""
                try:
                    existiert, minimiert, aktuell = fenster_zustand(hwnd)
                except Exception:
                    return letzte[0]
                if existiert and not minimiert and aktuell is not None:
                    letzte[0] = aktuell
                return letzte[0]

            self.ziel_rechteck = fenster_rect
        else:
            self.ziel_rechteck = (lambda r=rect: r) if rect is not None else self._arbeitsflaeche
        self._ziel_gebunden_melden(bindung)

    def _ziel_geloest(self) -> None:
        """Daniel hat die Bindung gelöst: wieder der ganze Desktop als Zielbereich, nichts mehr gebunden."""
        self.bindung = None
        self.ziel_rechteck = self._arbeitsflaeche
        self._ziel_geloest_melden()

    def _ticker_rechtecke(self) -> list:
        """Wo gerade die Box neben der Raute steht (dem weicht das Banner aus)."""
        return [self.ticker.rechteck()] if self.ticker is not None else []

    def _banner_rechtecke(self) -> list:
        return [self.banner.rechteck()] if self.banner is not None else []

    def _banner_geschlossen(self) -> None:
        self.banner = None

    def _ticker_geschlossen(self) -> None:
        self.ticker = None

    def _raute_verschoben(self, _x: int, _y: int) -> None:
        if self.ticker is not None:
            self.ticker.an_raute(self.raute.rechteck())

    # ---- Tastenkombination: das Eingabefeld an der Raute (der Agent drückt sie und schreibt) -------------------------
    def eingabe_oeffnen(self, titel: str | None = None, gesendet: Callable[[str], None] | None = None) -> None:
        """Das Eingabefeld an der Raute. Ohne Angaben ist es das Sprechfeld des Agenten (sein Text ist seine Rede); mit `titel` und
        `gesendet` dient es Daniel als Texteingabe (z. B. neuer Name)."""
        if self.eingabe is not None:
            self.eingabe.aktivieren()
            return
        feld = self._eingabe_klasse(0, 0, name=titel or self.name, farbe_hex=self.farbe_hex,
                                    gesendet=gesendet or self.raute.sagen, geschlossen=self._eingabe_geschlossen)
        _l, oben, _r, unten = feld.rechteck()
        x, y = feld_position(self.raute.rechteck(), unten - oben, self._bildschirm())
        feld.verschiebe(x, y)
        self.eingabe = feld
        feld.aktivieren()

    def augen_setzen(self, an: bool) -> None:
        """„Nur Terminal“ ein/aus: der Knopf „A+H“ im Terminal zeigt es; laufende Banner und Boxen verschwinden, wenn es ausgeschaltet wird."""
        self.terminal.setze_augen(an)
        if not an:
            for alt in (self.banner, self.ticker):
                if alt is not None:
                    alt.schliessen()

    def setze_identitaet(self, name: str | None = None, farbe_hex: str | None = None) -> None:
        """Daniel hat Name oder Farbe des Agenten geändert: Raute, Terminal und spätere Banner und Boxen folgen."""
        if name:
            self.name = name
        if farbe_hex:
            self.farbe_hex = farbe_hex
        self.raute.setze_identitaet(name, farbe_hex)
        self.terminal.setze_identitaet(name, farbe_hex)

    def _eingabe_geschlossen(self) -> None:
        self.eingabe = None

    def eingabe_hwnd(self) -> int | None:
        """Das Fenster des offenen Eingabefelds (vom Hände-Faden gelesen, darum nur ein Attribut-Lesen)."""
        feld = self.eingabe
        return feld.hwnd if feld is not None else None

    def eingabe_schliessen(self) -> None:
        if self.eingabe is not None:
            self.eingabe.schliessen()

    # ---- Hinweise der Bridge an der Raute (Tastenkombination, Hände, Sprache …): die Box neben der Raute, 9,9 s ----------
    def zeige_ticker(self, text: str, farbe_hex: str) -> None:
        if not self._meldungen_zeigen() or not self._augen_an():
            return
        if self.ticker is not None:
            self.ticker.schliessen()
        self.ticker = self._ticker_klasse(text=text, farbe_hex=farbe_hex, raute_rechteck=self.raute.rechteck(),
                                          geschlossen=self._ticker_geschlossen, grenzen=self._bildschirm,
                                          meiden=self._banner_rechtecke)
        self.ticker.zeige(aktivieren=False)

    # ---- Daniels Worte: wie alle Hinweise als Box neben der Raute (9,9 s), in Daniels Farbe; das Raum-Banner mit Fade gibt es nicht mehr -------
    def zeige_daniel(self, text: str, farbe_hex: str) -> None:
        self.zeige_ticker(text, farbe_hex)

    # ---- Menü der Raute (Strg + Rechtsklick): Status oben, Schließen erreichbar ----------------------------------
    def menue_eintraege(self) -> list[menue.Eintrag]:
        return [
            (MENUE_STATUS, f"{self.name} · {STATUS_TEXT.get(self.raute.status, self.raute.status)}", menue.ABGEBLENDET),
            None,
            (MENUE_TRANSPARENZ, f"Raute: Deckkraft {self.raute.deckkraft_prozent()} % → nächste Stufe", 0),
            (MENUE_GROESSER, "Raute größer", 0),
            (MENUE_KLEINER, "Raute kleiner", 0),
            (MENUE_RAUTE_REGEL, f"Raute: {self._regeltext('raute')} …", 0),
            (MENUE_TERMINAL_REGEL, f"Terminal: {self._regeltext('terminal')} …", 0),
            (MENUE_TERMINAL_DURCHKLICK,
             f"Terminal: durchklickbar, {self._bedientaste_text()} zum Bedienen — {self._durchklick_text('terminal')}", 0),
            (MENUE_NAME, f"Name ändern … (jetzt {self.name})", 0),
            (MENUE_FARBE, "Farbe wählen …", 0),
            (MENUE_NUR_TERMINAL, f"Nur Terminal (Augen und Hände aus): {'aus' if self._augen_an() else 'an'}", 0),
            (MENUE_ORT, "Ort der Elemente (Desktop oder Zielfenster) …", 0),
            (MENUE_ANZEIGEORT, "Anzeigeort und Ziel (Desktops) …", 0),
            (MENUE_HOTKEY, f"Tastenkombination festlegen … (jetzt {self.raute.hotkey or 'keine'})", 0),
            (MENUE_HAENDE, f"Hände (Agent drückt seine Tastenkombination und tippt): {self._haende_text()}", 0),
            (MENUE_BILDER, f"Bilder an den Agenten (alle paar Sekunden, nach der Bindung): {self._bilder_text()}", 0),
            (MENUE_BILD_DATEI, "Bilddatei an den Agenten senden …", 0),
            (MENUE_BILDFOLGE, "Bildfolge (Ordner) an den Agenten …", 0),
            (MENUE_PLAETZE, "Terminal-Platz tauschen …", 0),
            (MENUE_ZEICHNEN, "Zeichnen im Ziel (Objekte, Text, Bilder) …", 0),
            (MENUE_BILD_ELEMENT, "Bild einblenden (schwebend, Größe und Deckkraft einstellbar) …", 0),
            (MENUE_TERMINAL, "Terminal ausblenden" if self.terminal.sichtbar() else "Terminal einblenden", 0),
            (MENUE_NOTAUS, "Not-Aus aufheben" if self.not_aus.aktiv else "Not-Aus (F12)", 0),
            None,
            (MENUE_AUSNAHME, f"Meine Eingabe unterbricht die Hände nicht (Ausnahme): {self._ausnahme_text()}", 0),
            (MENUE_PROFIL, f"Steuerprofil der Hände: {self._profil_text()} (Klick wechselt)", 0),
            (MENUE_PAUSE, f"{self.name} fortsetzen" if self._agent_pausiert() else f"{self.name} pausieren (Prozess anhalten)", 0),
            (MENUE_AGENT_BEENDEN, f"{self.name} beenden", 0),
            (MENUE_BRIDGE_BEENDEN, "Bridge beenden", 0),
        ]

    def _raute_menue(self, x: int, y: int) -> None:
        with offene_menues.menue_art("raute"):  # nur dieses Menü kann ein Agent (mit Freigabe) bedienen
            gewaehlt = self._menue_anzeigen(self.raute.hwnd, self.menue_eintraege(), x, y)
        if gewaehlt == MENUE_TRANSPARENZ:
            self.raute.deckkraft_weiter()
        elif gewaehlt == MENUE_GROESSER:
            self.raute.groesse_setzen(self.raute.groesse + raute_fenster.GROESSE_SCHRITT)
        elif gewaehlt == MENUE_KLEINER:
            self.raute.groesse_setzen(self.raute.groesse - raute_fenster.GROESSE_SCHRITT)
        elif gewaehlt == MENUE_RAUTE_REGEL:
            self._regel_menue("raute", x, y)
        elif gewaehlt == MENUE_TERMINAL_REGEL:
            self._regel_menue("terminal", x, y)
        elif gewaehlt == MENUE_TERMINAL_DURCHKLICK:
            self._durchklick_umschalten("terminal")
        elif gewaehlt == MENUE_NUR_TERMINAL:
            self._nur_terminal_umschalten()
        elif gewaehlt == MENUE_ORT:
            self._ort_menue(x, y)
        elif gewaehlt == MENUE_ANZEIGEORT:
            self._anzeigeort_menue(x, y)
        elif gewaehlt == MENUE_NAME:
            self._name_aendern()
        elif gewaehlt == MENUE_FARBE:
            self._farbe_waehlen(x, y)
        elif gewaehlt == MENUE_HOTKEY:
            self._hotkey_festlegen()
        elif gewaehlt == MENUE_HAENDE:
            self._haende_umschalten()
        elif gewaehlt == MENUE_BILDER:
            self._bilder_umschalten()
        elif gewaehlt == MENUE_BILD_DATEI:
            self._bild_datei()
        elif gewaehlt == MENUE_BILDFOLGE:
            self._bildfolge_menue(x, y)
        elif gewaehlt == MENUE_PLAETZE:
            self._plaetze_menue(x, y)
        elif gewaehlt == MENUE_ZEICHNEN:
            self._zeichnen()
        elif gewaehlt == MENUE_BILD_ELEMENT:
            self._bild_element()
        elif gewaehlt == MENUE_TERMINAL:
            if self.terminal.sichtbar():
                self._terminal_ausblenden()
            else:
                self.terminal_ausgeblendet = False
                self.terminal.zeige()
        elif gewaehlt == MENUE_NOTAUS:
            self.not_aus.freigeben() if self.not_aus.aktiv else self.not_aus.ausloesen("Menü")
        elif gewaehlt == MENUE_AUSNAHME:
            self._ausnahme_umschalten()
        elif gewaehlt == MENUE_PROFIL:
            self._profil_wechseln()
        elif gewaehlt == MENUE_PAUSE:
            self._agent_pause()
        elif gewaehlt == MENUE_AGENT_BEENDEN:
            self._agent_beenden()
        elif gewaehlt == MENUE_BRIDGE_BEENDEN:
            self._bridge_beenden()

    def setze_hotkey(self, hotkey: str | None) -> None:
        self.raute.setze_hotkey(hotkey)

    def setze_status(self, status: str) -> None:
        """Verbindungsstatus an der Raute; der Sitzungszustand des Terminals wird getrennt gesetzt."""
        self.raute.setze_status(status)

    # ---- Lebenszyklus ----------------------------------------------------------------------------------------------
    def zeigen(self) -> None:
        self.terminal.zeige()
        self.raute.zeige(aktivieren=False)

    def schliessen(self) -> None:
        for fenster in (self.banner, self.ticker, self.eingabe):
            if fenster is not None:
                fenster.schliessen()
        self.raute.schliessen()
        self.terminal.schliessen()
