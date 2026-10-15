"""Die Raute: der Sprechort eines Agenten (R023) — ein kleines, rautenförmiges, schwebendes Fenster (R118).

Nach `ERLEBEN.md`: Klicks fallen physikalisch durch die Raute hindurch, damit sie nie versehentlich den Fokus
aus Spiel oder Programm nimmt. Sprechen tut der Agent, nicht Daniel: die Raute hat keinen Klick-Zweck. Bedient wird
sie nur mit gedrückter Modifikatortaste (Standard Strg), und nur zum Einrichten: ziehen (verschieben) und mit
Rechtsklick das Menü (Transparenz, Größe, Schließen). Der Rand zeigt den Verbindungsstatus (PLAN.md G02).

Banner und Ticker (`nachricht_fenster.py`) und der gemeinsame Chat (`chat_fenster.py`) sind eigene kleine Fenster;
`sagen()` meldet eine Nachricht nur an den Besitzer weiter.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift

GROESSE = 52  # Höhe der Raute in Pixeln; die Breite ergibt sich aus der Beschriftung (keine gleichseitige Raute)
GROESSE_MIN, GROESSE_MAX, GROESSE_SCHRITT = 28, 144, 12
NAME_MAX = 14
ZIEH_SCHWELLE = 4  # Pixel Mausbewegung, bevor ein Runterdrücken als Ziehen statt als Klick zählt
TIMER_MODIFIKATOR = 1
MODIFIKATOR_TAKT_MS = 80

STATUS_FARBEN = {
    "offline": stil.FARBE_TEXT_GEDAEMPFT,
    "verbindet": stil.FARBE_WARNUNG,
    "verbunden": stil.FARBE_OK,
    "beendet": stil.FARBE_FEHLER,
    "fehler": stil.FARBE_FEHLER,
    "notaus": stil.FARBE_FEHLER,
}
STATUS_TEXT = {
    "offline": "offline",
    "verbindet": "verbindet …",
    "verbunden": "verbunden",
    "beendet": "beendet",
    "fehler": "Fehler",
    "notaus": "Not-Aus",
}


def status_farbe(status: str) -> int:
    return STATUS_FARBEN.get(status, stil.FARBE_FEHLER)


def beschriftung(name: str, hotkey: str | None) -> str:
    """Die Beschriftung aus ERLEBEN.md: »◆ Codex [F14]« (Fenstertitel)."""
    return f"◆ {name} [{hotkey}]" if hotkey else f"◆ {name}"


def raute_text(name: str, hotkey: str | None) -> str:
    """Was in der Raute steht: der Name und die Tastenkombination zum Ansprechen, immer sichtbar."""
    kurz = name if len(name) <= NAME_MAX else name[:NAME_MAX - 1] + "…"
    return f"{kurz} [{hotkey}]" if hotkey else kurz


def abmessung(groesse: int, textbreite: int, texthoehe: int) -> tuple[int, int]:
    """(Breite, Höhe) einer Raute, in die der Text mittig passt: ein Textkasten passt in eine Raute, wenn
    Textbreite/Breite + Texthöhe/Höhe <= 1 ist; dazu ein kleiner Rand."""
    anteil = min(texthoehe / groesse, 0.75)
    breite = int(textbreite / (1 - anteil) * 1.12) + 4
    return max(breite, int(groesse * 1.8)), groesse


def exstil_fuer(exstil: int, bedienbar: bool) -> int:
    """Klickdurchlässig heißt WS_EX_TRANSPARENT; bedienbar nimmt genau dieses Bit weg und lässt den Rest stehen."""
    return exstil & ~w.WS_EX_TRANSPARENT if bedienbar else exstil | w.WS_EX_TRANSPARENT


class RauteFenster(Fenster):
    klasse = "AuHRaute"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW
    _erzwungen_bis = 0.0  # Standard auf Klassenebene: auch eine ohne __init__ gebaute Raute (Tests) kennt das Attribut; __init__ und erzwingen() setzen es je Instanz

    def __init__(self, x: int, y: int, *, name: str, farbe_hex: str | None = None, kuerzel: str | None = None,
                 hotkey: str | None = None, deckkraft_prozent: int = stil.DECKKRAFT_START_PROZENT,
                 modifikator_vk: int = w.VK_CONTROL,
                 modifikator: Callable[[], bool] | None = None,  # z. B. Bedientaste.gedrueckt; sonst modifikator_vk
                 klick_gewuenscht: Callable[[], None] = lambda: None,  # ungenutzt: die Raute gehört dem Agenten
                 menue_gewuenscht: Callable[[int, int], None] = lambda x, y: None,
                 verschoben: Callable[[int, int], None] = lambda x, y: None,
                 nachricht_gesendet: Callable[[str], None] = lambda text: None):
        w.require_windows()
        self.name = name
        self.farbe_hex = farbe_hex or stil.agentenfarbe(name)
        self.farbe = w.rgb_hex(self.farbe_hex)
        self.kuerzel = kuerzel or stil.kuerzel_aus_name(name)
        self.hotkey = hotkey
        self.status = "offline"
        self._modifikator_vk = modifikator_vk
        self._modifikator = modifikator
        self._klick = klick_gewuenscht
        self._menue = menue_gewuenscht
        self._verschoben = verschoben
        self._nachricht_gesendet = nachricht_gesendet
        self.letzte_nachricht = ""
        self.bedienbar = False
        self._erzwungen_bis = 0.0  # die Hände eines Agenten bedienen diese Raute: bis dahin gilt sie wie bei gehaltener Bedientaste
        self.groesse = GROESSE
        self.breite = GROESSE
        self._ziehanker: tuple[int, int] | None = None
        self._fenster_anker: tuple[int, int] | None = None
        self._ziehen = False
        self.f_kuerzel: Schrift | None = None
        super().__init__(x, y, GROESSE, GROESSE, titel=beschriftung(name, hotkey),
                         deckkraft=stil.deckkraft_alpha(deckkraft_prozent), durchklickbar=True, nicht_aktivieren=True)
        self._schrift_bauen()
        self._neu_bemessen()
        self.starte_timer(TIMER_MODIFIKATOR, MODIFIKATOR_TAKT_MS)

    @staticmethod
    def umriss(breite: int = GROESSE, hoehe: int | None = None) -> list[tuple[int, int]]:
        """Die vier Ecken der Raute (oben, rechts, unten, links) in Fensterkoordinaten; ohne Höhe gleichseitig."""
        hoehe = breite if hoehe is None else hoehe
        return [(breite // 2, 0), (breite, hoehe // 2), (breite // 2, hoehe), (0, hoehe // 2)]

    def text(self) -> str:
        return raute_text(self.name, self.hotkey)

    def _kuerzel_hoehe(self) -> int:
        return max(9, stil.skaliert(14, self.groesse / GROESSE))

    def _textbreite(self) -> int:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            return self.f_kuerzel.breite(hdc, self.text())
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def _neu_bemessen(self) -> None:
        """Fenstergröße und Form an Höhe und Beschriftung anpassen; die linke obere Ecke bleibt stehen."""
        if self.f_kuerzel is None:
            return
        breite, hoehe = abmessung(self.groesse, self._textbreite(), self.f_kuerzel.zellhoehe)
        links, oben, _r, _u = self.rechteck()
        self.breite = breite
        self.verschiebe(links, oben, breite, hoehe)
        self.setze_form(self.umriss(breite, hoehe))
        self._verschoben(links, oben)
        self.neu_zeichnen()

    def groesse_setzen(self, groesse: int) -> None:
        """Höhe der Raute in Pixeln, auf die Grenzen geklemmt; Breite, Form und Schrift folgen."""
        groesse = max(GROESSE_MIN, min(GROESSE_MAX, groesse))
        if groesse == self.groesse:
            return
        self.groesse = groesse
        if self.f_kuerzel is not None:
            self.f_kuerzel.freigeben()
        self._schrift_bauen()
        self._neu_bemessen()

    def setze_identitaet(self, name: str | None = None, farbe_hex: str | None = None) -> None:
        """Neuer Name und/oder neue Farbe (R024): die Raute misst sich neu, Titel und Anzeige folgen sofort."""
        if name:
            self.name = name
            self.kuerzel = stil.kuerzel_aus_name(name)
        if farbe_hex:
            self.farbe_hex = farbe_hex
            self.farbe = w.rgb_hex(farbe_hex)
        w.user32.SetWindowTextW(self.hwnd, beschriftung(self.name, self.hotkey))
        self._neu_bemessen()

    def setze_hotkey(self, hotkey: str | None) -> None:
        """Neue Tastenkombination: die Beschriftung der Raute ändert sich sofort (R024)."""
        if hotkey == self.hotkey:
            return
        self.hotkey = hotkey
        w.user32.SetWindowTextW(self.hwnd, beschriftung(self.name, hotkey))
        self._neu_bemessen()

    def deckkraft_prozent(self) -> int:
        return stil.alpha_prozent(self.deckkraft or 255)

    def deckkraft_weiter(self) -> None:
        self.setze_deckkraft(stil.deckkraft_alpha(stil.naechste_stufe(self.deckkraft_prozent())))
        self.neu_zeichnen()

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_kuerzel = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], self._kuerzel_hoehe(), fett=True, fest=False)
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    # ---- Status ----------------------------------------------------------------------------------------------------
    def setze_status(self, status: str) -> None:
        if status != self.status:
            self.status = status
            self.neu_zeichnen()

    # ---- Klickdurchlässig oder bedienbar ---------------------------------------------------------------------------
    def erzwingen(self, sekunden: float) -> None:
        """Die Hände eines Agenten bedienen diese Raute: für diese Zeit gilt sie wie bei gehaltener Bedientaste (klickbar). `0` hebt es auf."""
        self._erzwungen_bis = time.monotonic() + sekunden if sekunden > 0 else 0.0

    def modifikator_gedrueckt(self) -> bool:
        if time.monotonic() < self._erzwungen_bis:
            return True
        if self._modifikator is not None:
            return self._modifikator()
        return bool(w.user32.GetAsyncKeyState(self._modifikator_vk) & 0x8000)

    def bedienbar_setzen(self, bedienbar: bool) -> None:
        if bedienbar == self.bedienbar:
            return
        self.bedienbar = bedienbar
        alt = w.user32.GetWindowLongPtrW(self.hwnd, w.GWL_EXSTYLE)
        w.user32.SetWindowLongPtrW(self.hwnd, w.GWL_EXSTYLE, exstil_fuer(alt, bedienbar))
        self.neu_zeichnen()

    def bei_timer(self, ident: int) -> None:
        if ident != TIMER_MODIFIKATOR:
            return
        # Während eines Zugs bleibt die Raute bedienbar, auch wenn die Taste zwischendurch losgelassen wird.
        self.bedienbar_setzen(self.modifikator_gedrueckt() or self._ziehanker is not None)

    # ---- Zeichnen ------------------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        leinwand.fuellen(0)
        rand = stil.FARBE_TEXT if self.bedienbar else status_farbe(self.status)
        leinwand.polygon(self.umriss(self.breite, self.groesse), fuellfarbe=self.farbe, randfarbe=rand, randbreite=3)
        if self.f_kuerzel is not None:
            text = self.text()
            breite = self.f_kuerzel.breite(leinwand.hdc, text)
            leinwand.text(self.breite // 2 - breite // 2, self.groesse // 2 - self.f_kuerzel.zellhoehe // 2, text,
                          stil.FARBE_GRUND, self.f_kuerzel)

    def treffer(self, x: int, y: int) -> int | None:
        # Klick und Zug werden selbst unterschieden (siehe bei_maus_*), kein System-Fensterzug über HTCAPTION.
        return w.HTCLIENT

    # ---- Ziehen, Klicken, Menü -----------------------------------------------------------------------------------
    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        if not self.bedienbar:
            return 0
        self.erfasse_maus()
        self._ziehanker = self.maus_position()
        links, oben, _, _ = self.rechteck()
        self._fenster_anker = (links, oben)
        self._ziehen = False
        return 0

    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None:
        if self._ziehanker is None or not flags & 0x0001:
            return 0
        schirm_x, schirm_y = self.maus_position()
        dx, dy = schirm_x - self._ziehanker[0], schirm_y - self._ziehanker[1]
        if not self._ziehen and (abs(dx) > ZIEH_SCHWELLE or abs(dy) > ZIEH_SCHWELLE):
            self._ziehen = True
        if self._ziehen and self._fenster_anker is not None:
            neu_x, neu_y = self._fenster_anker[0] + dx, self._fenster_anker[1] + dy
            self.verschiebe(neu_x, neu_y)
            self._verschoben(neu_x, neu_y)
        return 0

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        if self._ziehanker is None:
            return 0
        self.gib_maus_frei()
        war_ziehen = self._ziehen
        self._ziehanker = None
        self._fenster_anker = None
        self._ziehen = False
        if not war_ziehen:
            self._klick()
        return 0

    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None:
        if self.bedienbar:
            links, oben, _, _ = self.rechteck()
            self._menue(links + x, oben + y)
        return 0

    def bei_maus_verloren(self) -> None:
        self._ziehanker = None
        self._fenster_anker = None
        self._ziehen = False

    # ---- Sprechen --------------------------------------------------------------------------------------------------
    def sagen(self, text: str) -> None:
        """Merkt sich die Nachricht und meldet sie dem Besitzer, der Banner, Ticker und Chat bedient."""
        self.letzte_nachricht = text
        self._nachricht_gesendet(text)

    def bei_zerstoert(self) -> None:
        if self.f_kuerzel is not None:
            self.f_kuerzel.freigeben()
            self.f_kuerzel = None
