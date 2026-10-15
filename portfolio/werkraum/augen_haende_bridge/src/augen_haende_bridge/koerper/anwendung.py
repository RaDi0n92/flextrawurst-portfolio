"""Die Anwendung des ersten Körpers: hält die Verbindung zum Relay und für jeden gestarteten Agenten einen Körper.

* Verbindung nur, wenn `BRIDGE_URL` und `BRIDGE_TOKEN` gesetzt sind (der SSH-Launcher setzt sie); sonst sichtbar
  offline, nie heimlich verbunden.
* Die Agenten startet der Starter auf dem VPS (`client_vps/terminal_launcher.py`) aus der Startliste (BE02); der
  Desktop schickt nur die `start_id`, nie einen Befehl. Ein Körper entsteht erst, wenn die Sitzung wirklich startet
  (R119), und hält sie: Ausgabe, Eingabe, Größe (BE01).
* Transportereignisse kommen im Transport-Thread an und werden mit `post` in den GUI-Thread gereicht. Gesendet
  wird über einen eigenen Sender-Thread, damit ein langsamer Socket die Oberfläche nie anhält.
* Nach einer Scanner-Bindung geht das gebundene Bild an genau diesen Agenten (R120).
"""

from __future__ import annotations

import ntpath
import os

import base64
import queue
import time
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from augen_haende_bridge.transport import MAX_TERMINAL_INPUT

from . import anzeigeort, bild, menue, offene_menues, stil, ziele
from . import win32 as w
from . import einstellungen as einst
from .einstellungen import Einstellungen
from .bilderstrom import Bilderstrom
from .eingabe_adapter import Aktion, Bildbezug
from . import steuerprofil
from .durchklick import DurchklickVerwalter
from .bildfolge import Bildfolgen, bilder_im_ordner
from .komposition import Arbeitsflaechen
from .ziel_halter import ORT_DESKTOP, ORT_ZIEL, ZielHalter, fenster_zustand
from .notaus import NotAus
from .regie_fenster import BREITE as REGIE_BREITE
from .regie_fenster import REGIESPRUECHE, leiste_position
from .scanner_anbindung import Bindung
from .sichtbarkeit import IMMER, Regel, Sichtbarkeit, programm_regel
from .tasten_senden import Haende
from .tastenkombi import BEDIENTASTEN, Bedientaste, Erfasser, Kombination, standard_kombination

VK_F13 = 0x7C
MAX_HOTKEYS = 12  # F13 bis F24
STANDARD_ZEILEN, STANDARD_SPALTEN = 30, 100
SENDE_WARTESCHLANGE = 512
NOTBREMSE_S = 8.0
GESPERRTE_ARTEN = frozenset({"terminal_input", "frame", "terminal_start", "terminal_audio"})  # nichts hinaus, solange Not-Aus gilt

SPRUCH_ID, START_ID, BEENDEN_ID, CHAT_ID = 1, 100, 200, 300  # Befehls-IDs im Regie-Menü
CHAT_REGEL_ID, LEISTE_REGEL_ID = 310, 311
CHAT_DURCHKLICK_ID, LEISTE_DURCHKLICK_ID, KAMERA_DURCHKLICK_ID = 320, 321, 322
BEDIENTASTE_ID, BEDIENTASTE_WAHL_ID = 330, 2000
SPRECHTASTE_ID, MIKMODUS_ID, MIKGERAET_ID, MIKGERAET_WAHL_ID = 340, 341, 342, 3000
REGEL_IMMER_ID, REGEL_PROGRAMM_ID = 1000, 1001  # im Auswahlmenü der Sichtbarkeit
FARBE_WAHL_ID, FARBE_STANDARD_ID = 3200, 3299  # Farbwahl im Raute-Menü
ZURUECKSETZEN_ID, ZURUECKSETZEN_JA_ID, NUR_TERMINAL_ALLE_ID = 350, 351, 352
ORT_WAHL_ID = 3300
BILD_FENSTER_ID = 353
PLATZ_TAUSCH_ID = 3400  # Raute-Menü „Terminal-Platz tauschen mit …“, je anderer Agent eine Nummer
FOLGE_START_ID, FOLGE_PAUSE_ID, FOLGE_STOP_ID = 3500, 3501, 3502
SICHTBAR_BILDSCHIRM_ID, SICHTBAR_AGENT_ID = 3600, 3610
KONTEXT_ID, ZIEL_ID = 3700, 3800
ANZEIGEORT_WECHSEL_ID, ANZEIGEORT_ZIEL_ID = 3900, 3950
ZEICHNEN_ID = 354
MENUE_FREIGABE_ID = 355  # Daniel schaltet hier ein, ob Agenten Bridge-Menüs bedienen dürfen (Aktion „menue“, Praxistest 11 bis 17); nach jedem Start aus
ORT_ELEMENTE = (("raute", "Raute"), ("terminal", "Terminal"), ("kamera", "Selbstbild"), ("ampel", "Ampel"))
FARBNAMEN = ("Cyan", "Gelb", "Pink", "Grün", "Blau", "Orange", "Violett", "Rosa")  # zu stil.AGENTENFARBEN, in derselben Reihenfolge
NAME_MAX = 24
FARBE_HEX = re.compile(r"#[0-9A-Fa-f]{6}")
DANIEL_FARBE_HEX = "#F2F2F2"  # Daniels Farbe im Chat und im Ticker (Agenten haben eigene)
CHAT_AMPEL = "Meldung"  # Absender der Lampenmeldungen im Chat (kein Agent, nicht Daniel; die Symbole ⚠ ✓ ℹ tragen den Zustand)

Rechteck = tuple[int, int, int, int]


AMPEL_ZEILE_ID, AMPEL_DECKKRAFT_ID, AMPEL_DURCHKLICK_ID, AMPEL_GROESSER_ID, AMPEL_KLEINER_ID = 9000, 9500, 9501, 9502, 9503
AMPEL_REGEL_ID, AMPEL_AUSBLENDEN_ID, AMPEL_ALLE_ID = 9504, 9505, 9506  # Befehls-IDs im Ampel-Menü
AMPEL_TAKT_S = 5.0  # alle fünf Sekunden: Lampen berechnen, Dauerfeuer in den Chat, bei neuem Rot piepen


class Gui(Protocol):
    def post(self, aufgabe: Callable[[], None]) -> None: ...
    def hotkey(self, modifikatoren: int, vk: int, aufruf: Callable[[], None]) -> bool: ...
    def hotkey_setzen(self, name: str, modifikatoren: int, vk: int, aufruf: Callable[[], None]) -> bool: ...
    def hotkey_loeschen(self, name: str) -> None: ...
    def beenden(self, code: int = 0) -> None: ...


class Sender:
    """Eigener Thread zwischen GUI und Transport: der GUI-Thread legt nur ab, er wartet nie auf den Socket."""

    def __init__(self, veroeffentlichen: Callable[[str, dict], object], fehler: Callable[[str], None],
                 gesperrt: Callable[[str], bool] = lambda kind: False):
        self._veroeffentlichen = veroeffentlichen
        self._fehler = fehler
        self._gesperrt = gesperrt  # wird im Sender-Faden gefragt: wirkt auch bei hängendem GUI-Thread
        self.verworfen = 0
        self._schlange: queue.Queue = queue.Queue(maxsize=SENDE_WARTESCHLANGE)
        self._faden = threading.Thread(target=self._lauf, name="koerper-sender", daemon=True)
        self._faden.start()

    def senden(self, kind: str, payload: dict) -> bool:
        try:
            self._schlange.put_nowait((kind, payload))
            return True
        except queue.Full:
            self._fehler("Sendewarteschlange voll — Nachricht verworfen")
            return False

    def _lauf(self) -> None:
        while True:
            eintrag = self._schlange.get()
            if eintrag is None:
                return
            kind, payload = eintrag
            if self._gesperrt(kind):
                self.verworfen += 1
                continue
            try:
                self._veroeffentlichen(kind, payload)
            except Exception as fehler:  # Verbindung weg: sichtbar melden, weiterlaufen
                self._fehler(f"{kind}: {fehler!r}"[:200])

    def stop(self) -> None:
        self._schlange.put(None)


def eingabe_stuecke(daten: bytes, groesse: int = MAX_TERMINAL_INPUT) -> list[bytes]:
    """Terminaleingaben in Stücke, die das Relay annimmt (`MAX_TERMINAL_INPUT`)."""
    return [daten[i:i + groesse] for i in range(0, len(daten), groesse)] if daten else []


def platz_fuer(index: int, flaeche: Rechteck) -> tuple[tuple[int, int], tuple[int, int]]:
    """(Raute-Position, Terminal-Position) für den index-ten Körper: Terminals unten versetzt (Skizze), Rauten oben rechts."""
    links, oben, rechts, unten = flaeche
    terminal = (links + 140 + index * 40, max(oben, unten - 640 - index * 30))
    raute = (rechts - 120 - (index % 4) * 60, oben + 80 + (index // 4) * 70 + (index % 4) * 20)
    return raute, terminal


@dataclass
class AgentZustand:
    terminal_id: str
    start_id: str
    name: str
    zustand: str = "starting"
    hotkey: str | None = None
    koerper: object | None = None
    ausgabe_seq: int = -1
    haende: bool = True  # darf der Agent seine Tastenkombination drücken und in sein Eingabefeld tippen lassen
    haende_laufen: bool = False
    steuerprofil: str = "geteilte_maus"  # wie die Hände dieses Agenten bedienen dürfen (steuerprofil.py); wirksam nur bei erlaubten Händen
    beenden_gewuenscht: bool = False  # Daniel hat „beenden“ gewählt: nach dem Ende verschwindet der ganze Körper
    luecken: int = 0
    nur_terminal: bool = False  # „nur Terminal“ (R122): Bilder, Hände, Kamera und Rautenchat aus; Mikrofon und Terminal laufen weiter
    orte_gewuenscht: tuple = ()  # Elemente, die im Zielfenster stehen sollen, sobald ein Fenster gebunden ist (überlebt den Neustart)
    schluessel: str = ""  # fester Name, unter dem die Einstellungen des Agenten gespeichert sind (der angezeigte Name kann geändert werden)
    name_geaendert: bool = False
    farbe_ueberschrieben: str | None = None  # die von Daniel gewählte Farbe; None = Standardfarbe
    pid: int | None = None  # Identität der Sitzung auf dem VPS: Prozess und Startzeit (aus der Terminalliste)
    gestartet: int | None = None
    neue_sitzung: bool = False  # unter derselben ID läuft ein anderer Prozess als vorher


class KoerperAnwendung:
    def __init__(self, *, url: str | None, token: str | None, gui: Gui,
                 koerper_bauen: Callable[..., object],
                 ort: str = "windows",
                 ziel_zustaende: bool = False,
                 ziel_verdeckt: Callable[[int], bool] | None = None,
                 ziel_faehigkeit: Callable[[str], str] | None = None,
                 runtime_bauen: Callable[..., object] | None = None,
                 arbeitsflaeche: Callable[[], Rechteck] = lambda: (0, 0, 1920, 1040),
                 bild_kodieren: Callable[[bytes, int, int, Rechteck], tuple[bytes, int, int]] = bild.bgra_zu_jpeg,
                 sender_bauen: Callable[..., Sender] = Sender,
                 not_aus: NotAus | None = None,
                 regie_bauen: Callable[..., object] | None = None,
                 ampel_bauen: Callable[..., object] | None = None,
                 fenster_vor: Callable[[int], bool] | None = None,
                 piepen: Callable[[], None] | None = None,
                 chat_bauen: Callable[..., object] | None = None,
                 kamera_bauen: Callable[..., object] | None = None,
                 ziel_halter: ZielHalter | None = None,
                 datei_waehlen: Callable[[int], str | None] | None = None,
                 zeichen_bauen: Callable[..., object] | None = None,
                 leiste_bauen: Callable[..., object] | None = None,
                 fenster_liste: Callable[[], list[tuple[int, str, str]]] | None = None,
                 anzeige: object | None = None,
                 arbeit: Arbeitsflaechen | None = None,
                 arbeit_pfad=None,
                 datei_kodieren: Callable[[str], tuple[bytes, int, int]] = bild.datei_zu_jpeg,
                 medien: object | None = None,
                 menue_anzeigen: Callable[..., int] = menue.zeige_menue,
                 sichtbarkeit: Sichtbarkeit | None = None,
                 durchklick: DurchklickVerwalter | None = None,
                 bedientaste: Bedientaste | None = None,
                 haende: Haende | None = None,
                 haende_engine: object | None = None,
                 weltdom_dienst: object | None = None,
                 mik_geraete: Callable[[], list[tuple[int, str]]] | None = None,
                 bilderstrom: Bilderstrom | None = None,
                 vordergrund_hwnd: Callable[[], int] | None = None,
                 erfasser: Erfasser | None = None,
                 einstellungen: Einstellungen | None = None,
                 bildschirm: Callable[[], Rechteck] | None = None,
                 programme: Callable[[], list] = lambda: [],
                 test_autostart: str | None = None, test_tippe: str | None = None):
        self.url, self.token = url, token
        self.gui = gui
        self.ort = ort  # Kennung dieses Arbeitsplatzes in den Ziel-Schlüsseln: windows, kde1, kde2 (ziele.py)
        self.anzeigeorte = anzeigeort.AnzeigeOrteStand(ort)  # welche Desktops es gibt und wo welches Terminal gezeigt wird (G06)
        self._ziel_zustaende_an = ziel_zustaende  # meldet dem Starter, in welchem Zustand die Ziele dieses Desktops sind (läuft nur im echten Betrieb)
        self._ziel_verdeckt = ziel_verdeckt  # (Kennung) -> liegt ein anderes Fenster davor? (plattformabhängig, von haupt geliefert)
        self._ziel_faehigkeit = ziel_faehigkeit or anzeigeort.faehigkeit_standard
        self._ziel_zustand_gemeldet: dict[str, tuple] = {}
        self._ziel_zustand_zeit = 0.0
        self._ziel_stop = threading.Event()
        self.ziel_gaeste: set[str] = set()  # Agenten, deren Körper auf einem anderen Desktop steht und deren Ziel hier liegt
        self._koerper_bauen = koerper_bauen
        self._runtime_bauen = runtime_bauen
        self._arbeitsflaeche = arbeitsflaeche
        self._bild_kodieren = bild_kodieren
        self._sender_bauen = sender_bauen
        self._test_autostart = test_autostart  # ausdrücklicher Test-Haken für den Wine-Lauf der EXE
        self._test_tippe = test_tippe  # ebenso: tippt einmal, sobald die erste Sitzung läuft
        self._regie_bauen = regie_bauen
        self._ampel_bauen, self._fenster_vor, self._piepen = ampel_bauen, fenster_vor, piepen
        self.ampel_ausgeblendet: set[str] = set()  # Agent-IDs, deren Ampel Daniel ausgeblendet hat
        self.ampel_fenster: dict[str, object] = {}  # Agent-ID → sein Ampel-Fenster
        self._chat_bauen = chat_bauen
        self._kamera_bauen = kamera_bauen
        self.ziel_halter = ziel_halter
        self._datei_waehlen, self._datei_kodieren = datei_waehlen, datei_kodieren
        self.arbeit = arbeit if arbeit is not None else Arbeitsflaechen()  # die Objekte der gemeinsamen Arbeitsfläche, je Gate ein Dokument (G08)
        self._zeichen_bauen, self._leiste_bauen, self.anzeige, self._arbeit_pfad = zeichen_bauen, leiste_bauen, anzeige, arbeit_pfad
        self._fenster_liste = fenster_liste or (lambda: [])
        self.editor_offen: dict | None = None  # {"schluessel", "tid", "editor", "fenster", "leiste"} solange der Zeichenmodus an ist
        if arbeit_pfad is not None:
            self.arbeit.laden(arbeit_pfad)
        self.bildfolgen = Bildfolgen(self._folge_bild_senden, fertig=lambda tid: self.gui.post(lambda t=tid: self._folge_beendet(t)))
        self.bridge_im_bild = True  # False: die Fenster der Bridge sind aus der Aufnahme ausgenommen (die Agenten sehen sie nicht)
        self.kamera_fenster: dict[str, object] = {}  # terminal_id → Selbstbild-Fenster
        self._standard: dict[str, tuple] = {}  # Fensterschlüssel → (Rechteck, Deckkraft, Raute-Größe) beim Anlegen, ohne gespeicherte Werte
        self._kamera_verborgen: set[str] = set()  # Daniel hat das Selbstbild per X weggemacht (bis die Kamera aus/an geht)
        self._vorschau_neu: dict[str, object] = {}  # letztes ungezeigtes Bild je Agent (aus dem Kamera-Faden)
        self.sichtbarkeit = sichtbarkeit
        self.durchklick = durchklick
        self.bedientaste = bedientaste
        self._haende = haende
        self.ablauf_stand: dict = {"laeufe": [], "offen": [], "lernen": False, "ablaeufe": []}  # G12: zuletzt vom Starter gemeldet
        self._ablauf_aktionen: dict[int, dict] = {}
        self.daniel_ausnahme = False  # Daniel erlaubt den Händen, bei seiner eigenen Eingabe weiterzuarbeiten (Not-Aus bleibt); Vorgabe: aus
        self.weltdom_dienst = weltdom_dienst  # G11: Knoten messen, auflösen, handeln, zeigen (weltdom_dienst.WeltdomDienst)
        self.haende_engine = haende_engine  # G10: Klicken, Ziehen, Tippen, Tasten, Rad auf dem gebundenen Fenster (eingabe_adapter.HaendeEngine)
        self._mik_geraete = mik_geraete or (lambda: [])
        self.bilderstrom = bilderstrom
        if medien is not None and hasattr(medien, "audio_verbinden"):
            medien.audio_verbinden(self.audio_senden)
        self._vordergrund_hwnd = vordergrund_hwnd or (lambda: int(w.user32.GetForegroundWindow() or 0))
        self._erfasser = erfasser if erfasser is not None else Erfasser()
        self.einstellungen = einstellungen
        self._bildschirm = bildschirm
        self._programme = programme
        self._fenster_art: dict[str, tuple[str, str, object]] = {}  # Regel-Schlüssel -> (Art, Speicherschlüssel, Fenster)
        self.chat_ausgeblendet = False
        self.fehler_haken: Callable[[str, BaseException], None] | None = None
        self.abbau_fehler: list[str] = []
        self.log: Callable[[str], None] = lambda text: None
        self.notbremse: Callable[[], None] | None = None
        self.regie = None
        self.anzeigeort_grund: dict[str, tuple] = {}  # Agent → (Grund, Zeit) des letzten abgelehnten Anzeigeort-Befehls
        self.haende_arten: dict[str, dict] = {}  # Agent → Aktionsart → (Status, Grund, Zeit) der letzten Aktion dieser Art
        self.haende_ziele: dict[str, dict] = {}  # Agent → Name des Ziels → (Status, Grund, Zeit) der letzten Aktion dort
        self.haende_letztes: dict[str, tuple[str, str, float]] = {}  # Agent → (Status, Grund, Zeit) der letzten Hände-Aktion, für die Ampel
        self._dialog_seit: dict[str, tuple[tuple[str, str], float]] = {}  # Agent -> (Dialog, erste Sichtung)
        self._dialog_gemeldet: dict[str, tuple[str, str]] = {}  # Agent -> der Dialog, der schon im Chat steht
        self._lage_zeit: dict[str, float] = {}  # Agent -> wann das Lagebild zuletzt an den Relay ging
        self.haende_gruende: dict[str, dict[str, float]] = {}  # Agent → Ablehnungsgrund → Zeit des letzten Auftretens (monotonic)
        self._ampel_rot: dict = {}  # (Agent, Lampe) → Wort, was gerade rot ist (für „wieder ok“)
        self._ampel_meldezeit: dict = {}  # (Agent, Lampe) → Zeit der letzten Chatzeile
        self._ampel_pieps: dict = {}  # (Agent, Lampe) → letzte Farbe, damit es nur beim Wechsel auf Rot piept
        self.ampel_stand: dict[str, list] = {}  # Agent → aktuelle Lampen, vom Takt gefüllt, von den Ampel-Fenstern gelesen
        self.ziel_weg_seit: dict[str, float] = {}  # Agent → Zeitpunkt, an dem sein Fenster verschwand; endet beim nächsten Binden
        self.chat = None
        self.medien = medien
        self._menue_anzeigen = menue_anzeigen
        self.gewaehlt: str | None = None  # terminal_id des Agenten, für den Regie und Medien gelten
        self.empfaenger: str | None = None  # terminal_id, an die Daniels Chat geht; None = an alle
        self.runtime = None
        self.sender: Sender | None = None
        self.status = "offline"
        self.hinweis = ""
        self.startliste: dict[str, dict] = {}
        self.agenten: dict[str, AgentZustand] = {}
        self.beobachter: list[Callable[[], None]] = []
        self.not_aus = not_aus if not_aus is not None else NotAus()
        self.not_aus.bei_ausloesen(lambda grund: self.gui.post(lambda: self._not_aus_gilt(grund)))
        self.not_aus.bei_freigabe(lambda: self.gui.post(self._not_aus_aufgehoben))
        if medien is not None:
            medien._weitergeben = self._kamera_frame  # Lesefaden des Medienmanagers → Sender
            medien._melden = lambda: self.gui.post(self._medien_gemeldet)
            medien._vorschau = self._kamera_vorschau

    @property
    def eingaben_gesperrt(self) -> bool:
        return self.not_aus.aktiv

    @eingaben_gesperrt.setter
    def eingaben_gesperrt(self, wert: bool) -> None:
        self.not_aus.ausloesen("gesetzt") if wert else self.not_aus.freigeben()

    def _anzeige_status(self) -> str:
        return "notaus" if self.not_aus.aktiv else self.status

    def _not_aus_gilt(self, grund: str) -> None:
        self.bildfolgen.alle_stoppen()
        self.hinweis = f"Not-Aus ({grund}) — keine Eingaben, Bilder oder Starts mehr hinaus"
        self._status_anzeigen()

    def _not_aus_aufgehoben(self) -> None:
        self.hinweis = ""
        self._status_anzeigen()

    def _status_anzeigen(self) -> None:
        for agent in self.agenten.values():
            if agent.koerper is not None and agent.zustand in ("starting", "running"):
                agent.koerper.setze_status(self._anzeige_status())
        self._regie_anzeigen()
        self._melden()

    # ---- Verbinden -------------------------------------------------------------------------------------------------
    def starten(self) -> None:
        self._regie_zeigen()
        if self.sichtbarkeit is not None:
            self.sichtbarkeit.starten(self.gui.post, nebenbei=self.einstellungen_sichern)
        if self.durchklick is not None:
            self.durchklick.starten(self.gui.post)
        if self.ziel_halter is not None:
            self.ziel_halter.starten(self.gui.post)
        if self._ziel_zustaende_an:
            def takt() -> None:
                while not self._ziel_stop.wait(1.0):
                    self.gui.post(self.ziel_zustaende_melden)

            threading.Thread(target=takt, name="ziel-zustand", daemon=True).start()
        def ampel_faden() -> None:
            while not self._ziel_stop.wait(AMPEL_TAKT_S):
                self.gui.post(self.ampel_takt)

        threading.Thread(target=ampel_faden, name="ampel-takt", daemon=True).start()
        if self.anzeige is not None:
            self.anzeige.starten(self.gui.post)
        if self.bilderstrom is not None:
            self.bilderstrom.starten()
        if not self.url or not self.token:
            self._setze_status("offline", "BRIDGE_URL/BRIDGE_TOKEN fehlen — keine Verbindung")
            return
        if self._runtime_bauen is None:
            from augen_haende_bridge.bridge_runtime import BridgeRuntime
            self._runtime_bauen = BridgeRuntime
        self.runtime = self._runtime_bauen(self.url, self.token,
                                           on_event=lambda ereignis: (self._verbindung_schnell(ereignis), self.gui.post(lambda: self.ereignis(ereignis)))[1])
        self.sender = self._sender_bauen(self.runtime.publish,
                                         lambda text: self.gui.post(lambda: self._setze_status(self.status, text)),
                                         lambda kind: self.not_aus.aktiv and kind in GESPERRTE_ARTEN)
        self._setze_status("verbindet", "")
        self.runtime.start()

    def _verbindung_schnell(self, ereignis: dict) -> None:
        """Aus dem Fadens der Verbindung, ohne den GUI-Faden: bricht die Verbindung ab, stoppen die Hände sofort (auch wenn die Oberfläche hängt)."""
        if self.haende_engine is None:
            return
        art = ereignis.get("kind")
        if art == "runtime.failed":
            self.haende_engine.verbindung_verloren()
        elif art == "runtime.connected":
            self.haende_engine.verbindung_da()

    def _setze_status(self, status: str, hinweis: str) -> None:
        self.status, self.hinweis = status, hinweis
        self._status_anzeigen()

    def _melden(self) -> None:
        for beobachter in list(self.beobachter):
            beobachter()

    def _senden(self, kind: str, payload: dict) -> bool:
        if self.sender is None or self.status != "verbunden":
            self._setze_status(self.status, f"nicht verbunden — {kind} nicht gesendet")
            return False
        return self.sender.senden(kind, payload)

    # ---- Ereignisse vom Relay (immer im GUI-Thread) ----------------------------------------------------------------
    def ereignis(self, ereignis: dict) -> None:
        art = ereignis.get("kind")
        if art == "runtime.connected":
            self._setze_status("verbunden", "")
            self._senden("terminal_list_request", {})
            if "anzeigeorte" in (ereignis.get("welcome") or {}).get("capabilities", []):
                self._senden("anzeigeorte_request", {})  # ein älterer Relay kennt das nicht: dann bleibt alles wie bisher
            return
        if art == "runtime.failed":
            self._setze_status("fehler", str(ereignis.get("reason", ""))[:200])
            return
        if art == "error":
            self._setze_status(self.status, f"Relay lehnt ab: {ereignis.get('reason')}")
            return
        if art == "result" and ereignis.get("status") in ("peer_offline", "backpressure", "delivery_unknown"):
            self._setze_status(self.status, f"VPS-Starter: {ereignis.get('status')}")
            return
        if art != "event":
            return
        payload = ereignis.get("payload") or {}
        {
            "terminal_list": self._terminal_liste,
            "terminal_state": self._terminal_zustand,
            "terminal_output": self._terminal_ausgabe,
            "raute_say": self._raute_sagt,
            "raute_tippen": self._raute_tippt,
            "bild_sofort": self._bild_sofort,
            "sprache_text": self._sprache_text,
            "anzeigeorte": self._anzeigeorte_stand,
            "terminal_ort": self._terminal_ort,
            "haende_auftrag": self._haende_auftrag,
            "weltdom_auftrag": self._weltdom_auftrag,
            "ablauf_stand": self._ablauf_stand,
            "regie_ergebnis": self._regie_ergebnis,
        }.get(ereignis.get("event_kind"), lambda _p: None)(payload)

    def _terminal_liste(self, payload: dict) -> None:
        self.startliste = {start["start_id"]: start for start in payload.get("starts", [])}
        for terminal in payload.get("terminals", []):
            tid, pid, gestartet = terminal["terminal_id"], terminal.get("pid"), terminal.get("gestartet")
            agent = self.agenten.get(tid)
            if agent is None:
                agent = self._agent_anlegen(tid, terminal["start_id"], terminal["name"], terminal["state"])
                if terminal["state"] in ("running", "paused"):  # bereits laufende Sitzung wieder aufgenommen
                    agent.koerper.terminal.setze_zustand("pausiert" if terminal["state"] == "paused" else "läuft")
            elif agent.pid is not None and pid is not None and (agent.pid, agent.gestartet) != (pid, gestartet):
                agent.neue_sitzung = True  # derselbe Name, aber ein anderer Prozess: eine neue Shell, nicht die alte Sitzung
                self.log(f"Sitzung {tid}: andere Identität (PID {agent.pid}/{agent.gestartet} → {pid}/{gestartet})")
                self._setze_status(self.status, f"{terminal['name']}: läuft unter derselben ID, aber als neuer Prozess")
            agent.pid, agent.gestartet = pid, gestartet
            if terminal["state"] in ("running", "paused"):
                self._senden("terminal_attach", {"terminal_id": tid})  # der Starter spielt die letzte Ausgabe noch einmal ein
        self._melden()
        if self._test_autostart and self._test_autostart in self.startliste:
            start_id, self._test_autostart = self._test_autostart, None
            self.agent_starten(start_id)

    def _terminal_zustand(self, payload: dict) -> None:
        tid, zustand = payload["terminal_id"], payload["state"]
        agent = self.agenten.get(tid)
        if agent is None:
            if zustand not in ("starting", "running", "paused"):
                self._setze_status(self.status, f"{payload['name']}: {zustand} {payload.get('reason', '')}".strip())
                return
            agent = self._agent_anlegen(tid, payload["start_id"], payload["name"], zustand)
        agent.zustand = zustand
        koerper = agent.koerper
        if agent.beenden_gewuenscht and zustand in ("exited", "failed"):
            self._agent_entfernen(tid)  # Raute, Terminal, Banner und Ticker verschwinden mit dem Agenten
            return
        if zustand == "running":
            koerper.terminal.setze_zustand("läuft")
            koerper.setze_status(self._anzeige_status())
            if self._test_tippe:
                text, self._test_tippe = self._test_tippe, None
                koerper.terminal.tippe(text)
        elif zustand == "paused":
            koerper.terminal.setze_zustand("pausiert (Prozess angehalten)")
            koerper.setze_status("pausiert")
        elif zustand == "exited":
            code = payload.get("exit_code")
            koerper.terminal.setze_zustand(f"beendet (Code {code})" if code is not None else "beendet")
            koerper.setze_status("beendet")
        elif zustand == "failed":
            koerper.terminal.setze_zustand(f"fehlgeschlagen: {payload.get('reason', '')}"[:80])
            koerper.setze_status("fehler")
        self._melden()

    def _terminal_ausgabe(self, payload: dict) -> None:
        agent = self.agenten.get(payload["terminal_id"])
        if agent is None:
            return
        seq = payload["seq"]
        if payload.get("replay"):  # Wiederaufnahme: Bildschirm und Rückblättern aus der gesendeten Ausgabe neu aufbauen
            agent.koerper.terminal.zuruecksetzen()
            agent.ausgabe_seq = seq - 1
        if agent.ausgabe_seq >= 0 and seq != agent.ausgabe_seq + 1:
            agent.luecken += 1  # der Strom ist live und verlustbehaftet gewollt; Lücken werden gezählt, nicht erfunden
        agent.ausgabe_seq = seq
        agent.koerper.terminal.ausgabe(base64.b64decode(payload["data"]))

    HAENDE_GRUENDE = {
        "keine_tastenkombination": "Der Agent hat keine Tastenkombination",
        "gesperrt": "Not-Aus aktiv",
        "feld_nicht_geoeffnet": "Die Tastenkombination hat das Eingabefeld nicht geöffnet",
        "fokus_verloren": "Das Eingabefeld hat die Tastatur verloren, abgebrochen",
        "sendinput_fehlgeschlagen": "Windows hat die Tasten nicht angenommen",
        "leerer_text": "Leerer Text",
        "daniel_uebernimmt": "Daniel tippt oder klickt gerade, nichts gedrückt",
    }
    RAUTE_RUHE_S = 2.0  # so lange darf Daniel nicht getippt oder geklickt haben, bevor ein Agent in seine Raute schreibt

    def _bild_sofort(self, payload: dict) -> None:
        """Der Relay meldet: ein Agent hat `see` gerufen und braucht ein frisches Bild (auch bei unverändertem Fenster)."""
        if self.bilderstrom is not None and payload.get("terminal_id") in self.agenten:
            self.bilderstrom.sofort(payload["terminal_id"])

    def _raute_tippt(self, payload: dict) -> None:
        """Ein Agent will mit seinen Händen schreiben: seine Tastenkombination drücken und in sein Eingabefeld tippen."""
        tid, text = payload["terminal_id"], payload["text"]

        def quittieren(ok: bool, grund: str = "") -> None:
            if ok:
                self._raute_gesendet(tid)  # gesendet: alle anderen Agenten im selben Gate bekommen sofort ein Bild
            if not ok and grund:
                self.haende_gruende.setdefault(tid, {})[f"raute:{grund}"] = time.monotonic()  # für die Ampel
            # Nur der abgeschlossene Körperversuch wird quittiert, nie bloß der Empfang.
            # Alte Aufträge ohne request_id behalten ihren bisherigen Versandweg.
            if payload.get("request_id"):
                self._senden("raute_tippen_ergebnis", {"terminal_id": tid, "request_id": payload["request_id"],
                                                       "ok": ok, "grund": grund[:80]})

        agent = self.agenten.get(tid)
        if agent is None or agent.nur_terminal:  # „nur Terminal“: keine Hände
            quittieren(False, "agent_unbekannt" if agent is None else "nur_terminal")
            return

        def melden(meldung: str) -> None:
            agent.koerper.zeige_ticker(f"Hände: {meldung}", DANIEL_FARBE_HEX)

        if not agent.haende:
            melden(f"aus — {agent.name} wollte schreiben")
            quittieren(False, "haende_aus")
            return
        if self._haende is None:
            melden("nicht verfügbar")
            quittieren(False, "haende_nicht_verfuegbar")
            return
        if self.not_aus.aktiv:
            melden(self.HAENDE_GRUENDE["gesperrt"])
            quittieren(False, "gesperrt")
            return
        if agent.haende_laufen:
            melden("noch beschäftigt")
            quittieren(False, "beschaeftigt")
            return
        agent.haende_laufen = True
        kombi = Kombination.aus_text(agent.hotkey)

        def lauf() -> None:
            try:
                ergebnis = self._haende.schreiben(
                    text, kombi, feld_hat_fokus=lambda: self._feld_hat_fokus(tid), gesperrt=lambda: self.not_aus.aktiv,
                    feld_schliessen=lambda: self.gui.post(lambda: self._feld_schliessen(tid)),
                    ruhig=self._daniel_ist_ruhig, eigene_markieren=self._eigene_tasten_markieren)
            except Exception as fehler:
                meldung = f"Fehler {fehler!r}"[:80]
                self.gui.post(lambda m=meldung: melden(m))
                self.gui.post(lambda: quittieren(False, "schreibfehler"))
                return
            finally:
                agent.haende_laufen = False
            if not ergebnis.ok:
                self.gui.post(lambda: melden(self.HAENDE_GRUENDE.get(ergebnis.grund, ergebnis.grund)))
            self.gui.post(lambda: quittieren(ergebnis.ok, "" if ergebnis.ok else ergebnis.grund))

        threading.Thread(target=lauf, daemon=True, name=f"haende-{tid}").start()

    def _daniel_ist_ruhig(self) -> bool:
        """Daniel hat in den letzten `RAUTE_RUHE_S` weder getippt noch geklickt; ohne Beobachter der Übernahme (z. B. Windows: dort zählt SendInput) gilt Ruhe."""
        beobachter = getattr(getattr(self, "haende_engine", None), "beobachter", None)
        ruhig_seit = getattr(beobachter, "ruhig_seit", None)
        return True if ruhig_seit is None else ruhig_seit() >= self.RAUTE_RUHE_S

    def _eigene_tasten_markieren(self) -> None:
        engine = getattr(self, "haende_engine", None)
        if engine is not None:
            engine.letzte_sendung = time.monotonic()  # die Aufzeichnung sieht diese Tasten kurz danach: sie gehören den Händen, nicht Daniel

    def _feld_hat_fokus(self, tid: str) -> bool:
        agent = self.agenten.get(tid)
        hwnd = agent.koerper.eingabe_hwnd() if agent is not None else None
        return bool(hwnd) and self._vordergrund_hwnd() == hwnd

    def _feld_schliessen(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        if agent is not None:
            agent.koerper.eingabe_schliessen()

    def haende_umschalten(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        if agent is not None:
            agent.haende = not agent.haende
            self.einstellungen_sichern()

    # ---- Sprache: Daniels Mikrofon → VPS (Whisper) → Text im Chat und an der Raute ---------------------------------
    def audio_senden(self, agent_id: str, wav: bytes, dauer_ms: int) -> None:
        """Aus dem Audio-Faden: eine fertige Äußerung an den VPS (threadsicher; Not-Aus sperrt hier und im Sender)."""
        agent = self.agenten.get(agent_id)
        if agent is None or self.not_aus.aktiv or self.sender is None or self.status != "verbunden":
            return
        if self.sender.senden("terminal_audio", {"terminal_id": agent_id, "mime": "audio/wav",
                                                "data": base64.b64encode(wav).decode(), "dauer_ms": dauer_ms}):
            self.gui.post(lambda: agent.koerper.zeige_ticker("Sprache wird erkannt …", DANIEL_FARBE_HEX))

    def _sprache_text(self, payload: dict) -> None:
        """Der erkannte Text von Daniels Äußerung: im Chat und als Ticker an der Raute, wie getippt (Terminal bleibt unberührt)."""
        if payload["terminal_id"] in self.agenten:
            self.daniel_sagt(f"(Sprache) {payload['text']}", payload["terminal_id"], in_session=False)

    def sprechtaste_festlegen(self) -> None:
        if self.medien is None or not hasattr(self.medien, "sprechtaste_vk"):
            return
        self._chat_hinweis("Sprechtaste festlegen: die gewünschte Taste drücken … (Esc bricht ab)")
        self._erfasser.im_hintergrund(lambda kombi: self.gui.post(lambda: self._sprechtaste_erfasst(kombi)))

    def _sprechtaste_erfasst(self, kombi: Kombination | None) -> None:
        if kombi is None:
            self._chat_hinweis("Sprechtaste: keine Änderung")
            return
        self.medien.sprechtaste_vk = kombi.vk
        self._chat_hinweis(f"Sprechtaste: {Kombination(0, kombi.vk).text()} (gedrückt halten zum Sprechen)")
        self.einstellungen_sichern()

    def mik_modus_umschalten(self) -> None:
        if self.medien is None or not hasattr(self.medien, "modus"):
            return
        self.medien.modus = "offen" if self.medien.modus == "sprechtaste" else "sprechtaste"
        self._chat_hinweis("Mikrofon offen: alles, was es hört, wird erkannt und an den VPS gesendet"
                           if self.medien.modus == "offen" else "Mikrofon mit Sprechtaste: nur während die Taste gehalten wird")
        self.einstellungen_sichern()

    def mik_geraet_waehlen(self, x: int, y: int) -> None:
        """Welches Mikrofon die Bridge benutzt: das Standardgerät von Windows oder ein bestimmtes (z. B. wenn das Standardgerät ein virtuelles ist)."""
        if self.medien is None or not hasattr(self.medien, "mik_geraet") or self.regie is None:
            return
        geraete = self._mik_geraete()
        aktuell = self.medien.mik_geraet
        eintraege: list = [(MIKGERAET_WAHL_ID, "Standardgerät von Windows", menue.GEHAKT if aktuell is None else 0), None]
        for i, (_index, name) in enumerate(geraete):
            eintraege.append((MIKGERAET_WAHL_ID + 1 + i, name, menue.GEHAKT if name == aktuell else 0))
        if not geraete:
            eintraege.append((0, "Keine Eingabegeräte gefunden", menue.ABGEBLENDET))
        wahl = self._menue_anzeigen(self.regie.hwnd, eintraege, x, y)
        if wahl == MIKGERAET_WAHL_ID:
            self.medien.mik_geraet = None
        elif MIKGERAET_WAHL_ID < wahl <= MIKGERAET_WAHL_ID + len(geraete):
            self.medien.mik_geraet = geraete[wahl - MIKGERAET_WAHL_ID - 1][1]
        else:
            return
        self._chat_hinweis(f"Mikrofon-Gerät: {self.medien.mik_geraet or 'Standard von Windows'} (gilt beim nächsten Einschalten des Mikrofons)")
        self.einstellungen_sichern()

    def _chat_hinweis(self, text: str) -> None:
        if self.chat is not None:
            self.chat.empfangen("Bridge", text)

    def _sprechtaste_text(self) -> str:
        vk = getattr(self.medien, "sprechtaste_vk", None)
        return Kombination(0, vk).text() if vk else "–"

    def _mikmodus_text(self) -> str:
        return "offen (alles wird erkannt)" if getattr(self.medien, "modus", "sprechtaste") == "offen" else "Sprechtaste"

    def _raute_sagt(self, payload: dict) -> None:
        agent = self.agenten.get(payload["terminal_id"])
        if agent is not None:
            agent.koerper.raute.sagen(payload["text"])
            self._raute_gesendet(payload["terminal_id"])

    RAUTE_BILD_VERZOEGERUNG_S = 0.4  # die Raute zeichnet ihren Text im nächsten Takt der Oberfläche; erst danach ist er im Bild

    def _gate_nachbarn(self, tid: str) -> list[str]:
        """Alle anderen Agenten im selben Gate (gleiches gebundenes Fenster oder gleicher Desktop). Wer nirgends gebunden ist, hat kein Gate."""
        schluessel = self.ziel_schluessel(tid)
        if schluessel is None:
            return []
        return [a.terminal_id for a in self.agenten.values() if a.terminal_id != tid and self.ziel_schluessel(a.terminal_id) == schluessel]

    def _sofortbild(self, empfaenger: list[str], anlass: str) -> None:
        """Ohne Wenn und Aber: jedem dieser Agenten **jetzt** ein frisches Bild (auch bei unverändertem Fenster, ohne auf den Takt zu warten).
        Das Senden läuft im eigenen Faden, nie in der Oberfläche; erst nach einer kurzen Pause, damit der neue Text im Bild steht."""
        if self.bilderstrom is None or not empfaenger:
            return
        namen = ", ".join(self.agenten[t].name for t in empfaenger if t in self.agenten)

        def senden() -> None:
            try:
                n = self.bilderstrom.sofort_senden(empfaenger)
                self.log(f"{anlass}: Sofortbild an {namen} ({n} gesendet)")
            except Exception as fehler:
                self.log(f"Sofortbild ({anlass}): {fehler!r}"[:200])

        timer = threading.Timer(self.RAUTE_BILD_VERZOEGERUNG_S, senden)
        timer.daemon = True
        timer.start()

    def _raute_gesendet(self, tid: str) -> None:
        """Ein Agent hat in seine Raute gesendet (getippt oder gesagt): jeder andere Agent im selben Gate bekommt sofort ein frisches Bild."""
        if tid in self.agenten:
            self._sofortbild(self._gate_nachbarn(tid), f"Raute von {self.agenten[tid].name}")

    def _meldung_posten(self, tid: str | None, text: str) -> None:
        """Eine Meldung im Chat (Absender „Meldung“). Betrifft sie einen Agenten, bekommen er **und** jeder andere Agent im selben Gate sofort ein Bild:
        so sieht jeder, was gemeldet wurde, auch wenn er den Chat nicht liest."""
        if self.chat is not None:
            self.chat.empfangen(CHAT_AMPEL, text)
        if tid in self.agenten:
            self._sofortbild([tid] + self._gate_nachbarn(tid), f"Meldung zu {self.agenten[tid].name}")

    # ---- Körper anlegen --------------------------------------------------------------------------------------------
    def _eindeutiger_name(self, basis: str) -> str:
        """Zwei Sitzungen mit demselben Namen bleiben unterscheidbar: „Codex“, „Codex 2“, … (kleinste freie Nummer)."""
        benutzt = {a.schluessel or a.name for a in self.agenten.values()}
        if basis not in benutzt:
            return basis
        nummer = 2
        while f"{basis} {nummer}" in benutzt:
            nummer += 1
        return f"{basis} {nummer}"

    def _agent_anlegen(self, tid: str, start_id: str, name: str, zustand: str) -> AgentZustand:
        index = len(self.agenten)
        name = self._eindeutiger_name(name)  # ab hier der feste Schlüssel dieses Agenten
        ueber = self.einstellungen.element(f"agent:{name}") if self.einstellungen is not None else {}
        anzeige = ueber.get("name") if isinstance(ueber.get("name"), str) and 1 <= len(ueber["name"]) <= NAME_MAX else name
        farbe = ueber.get("farbe") if isinstance(ueber.get("farbe"), str) and FARBE_HEX.fullmatch(ueber["farbe"]) else None
        kombi = self._hotkey_waehlen(tid, name)
        hotkey = kombi.text() if kombi is not None else None
        start = self.startliste.get(start_id, {})
        raute_pos, terminal_pos = platz_fuer(index, self._arbeitsflaeche())
        agent = AgentZustand(tid, start_id, anzeige, zustand, hotkey)
        agent.schluessel, agent.name_geaendert, agent.farbe_ueberschrieben = name, anzeige != name, farbe
        agent.koerper = self._koerper_bauen(
            name=anzeige, farbe_hex=farbe, ort=start.get("ort", "?"), hotkey=hotkey,
            augen_an=lambda t=tid: not self.agenten[t].nur_terminal if t in self.agenten else True,
            nur_terminal_umschalten=lambda t=tid: self.nur_terminal_umschalten(t),
            ort_menue=lambda x, y, t=tid: self.ort_menue(t, x, y),
            bild_datei=lambda t=tid: self.bild_datei_senden(t),
            bildfolge_menue=lambda x, y, t=tid: self.bildfolge_menue(t, x, y),
            plaetze_menue=lambda x, y, t=tid: self.plaetze_menue(t, x, y),
            zeichnen=lambda t=tid: self.zeichnen_oeffnen(t),
            bild_element=lambda t=tid: self.bild_element_neu(t),
            anzeigeort_menue=lambda x, y, t=tid: self.anzeigeort_menue(t, x, y),
            name_aendern=lambda t=tid: self.name_aendern(t),
            farbe_waehlen=lambda x, y, t=tid: self.farbe_menue(t, x, y),
            raute_position=raute_pos, terminal_position=terminal_pos,
            terminal_senden=lambda daten, t=tid: self.eingabe_senden(t, daten),
            terminal_groesse=lambda zeilen, spalten, t=tid: self._senden(
                "terminal_resize", {"terminal_id": t, "rows": zeilen, "cols": spalten}),
            agent_beenden=lambda t=tid: self.agent_beenden(t),
            agent_pause=lambda t=tid: self.agent_pause_umschalten(t),
            profil_text=lambda t=tid: getattr(self.agenten.get(t), "steuerprofil", steuerprofil.STANDARD),
            profil_wechseln=lambda t=tid: self.agent_profil_wechseln(t),
            ausnahme_text=lambda: "an" if self.daniel_ausnahme else "aus",
            ausnahme_umschalten=self.ausnahme_umschalten,
            agent_pausiert=lambda t=tid: getattr(self.agenten.get(t), "zustand", "") == "paused",
            bridge_beenden=self.beenden,
            ziel_gebunden=lambda bindung, t=tid: self.bild_senden(t, bindung),
            ziel_geloest=lambda t=tid: self.ziel_loesen(t),
            gesprochen=self._agent_hat_gesprochen,
            meldungen_zeigen=lambda t=tid: self.sichtbarkeit is None or self.sichtbarkeit.sichtbar_erlaubt(f"raute:{t}"),
            regel_menue=lambda element, x, y, t=tid: self.regel_menue(f"{element}:{t}", x, y),
            regeltext=lambda element, t=tid: self._regel_text(f"{element}:{t}"),
            durchklick_text=lambda element, t=tid: self._durchklick_text(f"{element}:{t}"),
            durchklick_umschalten=lambda element, t=tid: self.durchklick_umschalten(f"{element}:{t}"),
            bedientaste_text=self._bedientaste_text,
            modifikator=self.bedientaste.gedrueckt if self.bedientaste is not None else None,
            hotkey_festlegen=lambda t=tid: self.hotkey_festlegen(t),
            haende_text=lambda t=tid: "an" if self.agenten[t].haende else "aus",
            haende_umschalten=lambda t=tid: self.haende_umschalten(t),
            bilder_text=lambda t=tid: self._bilder_text(t),
            bilder_umschalten=lambda t=tid: self.bilder_umschalten(t),
            not_aus=self.not_aus,
        )
        if self.einstellungen is not None:
            element = self.einstellungen.element(f"raute:{name}")
            if isinstance(element.get("haende"), bool):
                agent.haende = element["haende"]
            if element.get("steuerprofil") in steuerprofil.PROFILE:
                agent.steuerprofil = element["steuerprofil"]
            if element.get("nur_terminal") is True:
                agent.nur_terminal = True
            orte = element.get("orte")
            if isinstance(orte, list):
                agent.orte_gewuenscht = tuple(o for o in orte if o in {e for e, _ in ORT_ELEMENTE})
        self.agenten[tid] = agent
        agent.koerper.zeigen()
        self._fenster_einrichten(f"raute:{tid}", "raute", f"raute:{name}", agent.koerper.raute)
        self._fenster_einrichten(f"terminal:{tid}", "terminal", f"terminal:{name}", agent.koerper.terminal,
                                 nutzer_verborgen=lambda k=agent.koerper: k.terminal_ausgeblendet)
        agent.koerper.setze_status(self._anzeige_status())
        if agent.nur_terminal:
            agent.koerper.augen_setzen(False)
        elif self.bilderstrom is not None:
            self.bilderstrom.binden(tid, None)  # Augen immer an: ohne Bindung sieht der Agent den ganzen Desktop
        if self.gewaehlt is None:
            self.gewaehlt = tid
        self._regie_zeigen()
        self._ampel_fuer(tid)  # eigenes kleines Fenster je Agent: zeigt, was schiefgeht
        if self.chat is not None:
            self.chat.farbe_setzen(agent.name, w.rgb_hex(agent.koerper.farbe_hex))
        return agent

    # ---- Anzeigeorte (G06): wo der Körper steht, wo das Ziel liegt ------------------------------------------------------
    def _anzeigeorte_stand(self, payload: dict) -> None:
        self.anzeigeorte.setze_orte(payload.get("orte", []))
        self._melden()

    def _terminal_ort(self, payload: dict) -> None:
        info = anzeigeort.TerminalOrt.aus_payload(payload)
        tid = info.terminal_id
        self.anzeigeorte.merke(info)
        if info.grund:
            self.anzeigeort_grund[tid] = (info.grund, time.monotonic())  # für die Ampel
            self._setze_status(self.status, "Anzeigeort: " + anzeigeort.GRUND_TEXT.get(info.grund, info.grund))
        if not info.aktiv and tid in self.agenten and info.anzeigeort != self.ort:
            self._agent_entfernen(tid)  # der Körper ist auf einen anderen Desktop gewandert; die Sitzung läuft weiter und wird dort aufgenommen
        self._ziel_pruefen(info)
        self._melden()

    def _ziel_pruefen(self, info: "anzeigeort.TerminalOrt") -> None:
        """Liegt das Ziel dieses Terminals hier, aber der Körper woanders, ist dieser Desktop „Ziel-Gast“: er sendet seinen ganzen Bildschirm als Bild.
        Liegt es nicht (mehr) hier, endet der Strom (der Starter nähme die Bilder ohnehin nicht an)."""
        tid = info.terminal_id
        if self.bilderstrom is None:
            return
        hier_ziel = info.zielort == self.ort
        if hier_ziel and tid not in self.agenten and tid not in self.bilderstrom.ziele:
            self.bilderstrom.binden(tid, None)
            self.ziel_gaeste.add(tid)
            self._setze_status(self.status, f"{self.anzeigeorte.name(self.ort)} ist jetzt Ziel für ein Terminal auf {self.anzeigeorte.name(info.anzeigeort)} (ganzer Desktop)")
        elif not hier_ziel and tid in self.bilderstrom.ziele and (tid in self.ziel_gaeste or tid in self.agenten):
            self.bilderstrom.loesen(tid)
            self.ziel_gaeste.discard(tid)
        elif not hier_ziel:
            self.ziel_gaeste.discard(tid)

    def ziel_zustand_von(self, ziel) -> str:
        """ok, verdeckt, minimiert oder weg: der Zustand eines gebundenen Ziels (ein ganzer Desktop ist immer ok)."""
        if ziel.hwnd is None:
            return "ok"
        existiert, minimiert, _rect = fenster_zustand(ziel.hwnd)
        if not existiert:
            return "weg"
        if minimiert:
            return "minimiert"
        if self._ziel_verdeckt is not None and self._ziel_verdeckt(ziel.hwnd):
            return "verdeckt"
        return "ok"

    def ziel_zustaende_melden(self) -> None:
        """Dem Starter melden, wenn sich der Zustand eines Ziels dieses Desktops ändert: er gibt es an den Anzeigeort weiter (Menü „Anzeigeort und Ziel“)."""
        if not self.anzeigeorte.unterstuetzt or self.bilderstrom is None or self.status != "verbunden":
            return
        for tid, ziel in list(self.bilderstrom.ziele.items()):
            info = self.anzeigeorte.terminals.get(tid)
            if info is not None and info.zielort and info.zielort != self.ort:
                continue  # das Ziel liegt woanders
            zustand = self.ziel_zustand_von(ziel)
            target_id = ziele.fenster_schluessel(self.ort, ziel.hwnd) if ziel.hwnd is not None else f"{self.ort}:desktop"
            if self._ziel_zustand_gemeldet.get(tid) == (target_id, zustand):
                continue
            self._ziel_zustand_gemeldet[tid] = (target_id, zustand)
            self._senden("ziel_zustand", {"terminal_id": tid, "target_id": target_id, "zustand": zustand, "faehigkeit": self._ziel_faehigkeit(zustand),
                                          "seit_ms": int(time.time() * 1000)})
        for tid in [t for t in self._ziel_zustand_gemeldet if t not in self.bilderstrom.ziele]:
            del self._ziel_zustand_gemeldet[tid]

    def anzeigeort_menue(self, tid: str, x: int, y: int) -> None:
        """Raute-Menü „Anzeigeort und Ziel“: Laufort, Anzeigeort, Sitzung und Ziel getrennt, dazu Wechsel des Anzeigeorts und Wahl des Zielorts."""
        agent = self.agenten.get(tid)
        if agent is None:
            return
        eintraege = self.anzeigeorte.menue_eintraege(tid, ANZEIGEORT_WECHSEL_ID)
        if self.anzeigeorte.unterstuetzt:
            andere = self.anzeigeorte.ziele_fuer_wechsel(tid)
            info = self.anzeigeorte.terminals.get(tid)
            ziel_jetzt = info.zielort if info else self.ort
            ziele = [o for o in self.anzeigeorte.orte if o.get("online") and o["ort"] != ziel_jetzt]
            eintraege.append(None)
            eintraege += [(ANZEIGEORT_ZIEL_ID + i, f"Arbeitsziel auf {o.get('name') or o['ort']} legen (ganzer Desktop) …", 0) for i, o in enumerate(ziele)]
        with offene_menues.menue_art("raute.anzeigeort"):
            gewaehlt = self._menue_anzeigen(agent.koerper.raute.hwnd, eintraege, x, y)
        if not gewaehlt:
            return
        ort = self.anzeigeorte.wahl_zu_ort(tid, ANZEIGEORT_WECHSEL_ID, gewaehlt)
        if ort is not None:
            self.anzeigeort_wechseln(tid, ort)
            return
        i = gewaehlt - ANZEIGEORT_ZIEL_ID
        info = self.anzeigeorte.terminals.get(tid)
        ziel_jetzt = info.zielort if info else self.ort
        ziele = [o for o in self.anzeigeorte.orte if o.get("online") and o["ort"] != ziel_jetzt]
        if 0 <= i < len(ziele):
            self.ziel_legen(tid, ziele[i]["ort"])

    def anzeigeort_wechseln(self, tid: str, ort: str) -> bool:
        """Der Körper dieses Agenten soll auf dem Desktop `ort` stehen (Menü „Anzeigeort“); der Starter entscheidet und meldet das Ergebnis."""
        agent = self.agenten.get(tid)
        if agent is None or not self._senden("terminal_umziehen", {"terminal_id": tid, "ort": ort}):
            return False
        self._setze_status(self.status, f"{agent.name}: Anzeigeort wechselt zu {self.anzeigeorte.name(ort)} …")
        return True

    def ziel_legen(self, tid: str, ort: str) -> bool:
        """Das Arbeitsziel (ganzer Desktop) dieses Agenten soll auf dem Desktop `ort` liegen; der Körper bleibt, wo er ist."""
        agent = self.agenten.get(tid)
        if agent is None or not self._senden("terminal_ziel", {"terminal_id": tid, "ort": ort}):
            return False
        self._setze_status(self.status, f"{agent.name}: Arbeitsziel liegt künftig auf {self.anzeigeorte.name(ort)}")
        return True

    # ---- „Nur Terminal“ (R122) -----------------------------------------------------------------------------------------
    def _nur_terminal(self, tid: str) -> bool:
        agent = self.agenten.get(tid)
        return bool(agent and agent.nur_terminal)

    def nur_terminal_setzen(self, tid: str, an: bool) -> None:
        """Augen und Hände dieses Agenten aus (an=True) oder wieder ein. Mikrofon und Terminal bleiben unberührt; die einzelnen Schalter
        (Hände, Bilder, Kamera) behalten ihre eigenen Werte und gelten nach dem Einschalten wieder."""
        agent = self.agenten.get(tid)
        if agent is None or agent.nur_terminal == an:
            return
        agent.nur_terminal = an
        if an:
            self.bildfolgen.stoppen(tid)
        if an and self.medien is not None and self.medien.kamera_zustand(tid) in ("ein", "startet"):
            self.medien.kamera_umschalten(tid)  # läuft die Kamera, wird sie ausgeschaltet; die Bilder gehen nirgends hin
        agent.koerper.augen_setzen(not an)
        if not an and self.bilderstrom is not None and tid not in self.bilderstrom.ziele:
            self.bilderstrom.binden(tid, None)  # Start im Zustand „nur Terminal“ bindet nichts; beim Einschalten sehen die Augen den ganzen Desktop
        self._kamera_fenster_abgleichen()
        self._setze_status(self.status, f"{agent.name}: {'nur Terminal (Augen und Hände aus)' if an else 'Augen und Hände wieder an'}")
        self._regie_anzeigen()
        self.einstellungen_sichern()

    def nur_terminal_umschalten(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        if agent is not None:
            self.nur_terminal_setzen(tid, not agent.nur_terminal)

    def nur_terminal_alle(self) -> None:
        """Für alle Agenten gleichzeitig: sind nicht alle schon „nur Terminal“, werden alle es; sonst gehen alle wieder auf an."""
        an = not all(a.nur_terminal for a in self.agenten.values())
        for tid in list(self.agenten):
            self.nur_terminal_setzen(tid, an)

    # ---- Ort der Elemente (R121) ---------------------------------------------------------------------------------------
    def _ziel_hwnd(self, tid: str) -> int | None:
        if self.bilderstrom is None:
            return None
        ziel = self.bilderstrom.ziele.get(tid)
        return ziel.hwnd if ziel is not None else None

    def _orte_anwenden(self, tid: str) -> None:
        """Ein Fenster wurde als Ziel gebunden: Elemente, die Daniel im Zielfenster haben will, gehen hinein."""
        agent = self.agenten.get(tid)
        if agent is None or self.ziel_halter is None:
            return
        for element in agent.orte_gewuenscht:
            if f"{element}:{tid}" in self.ziel_halter.elemente:
                self.ziel_halter.setze_ort(f"{element}:{tid}", ORT_ZIEL)

    def ort_menue(self, tid: str, x: int, y: int) -> None:
        agent = self.agenten.get(tid)
        if agent is None or self.ziel_halter is None:
            return
        hat_ziel = self._ziel_hwnd(tid) is not None
        eintraege: list = [(0, f"Ort der Elemente von {agent.name}" if hat_ziel else "Kein einzelnes Fenster als Ziel gebunden — erst im Scanner ein Fenster wählen",
                            menue.ABGEBLENDET), None]
        vorhanden = [(i, e, text) for i, (e, text) in enumerate(ORT_ELEMENTE) if f"{e}:{tid}" in self.ziel_halter.elemente]
        for i, element, text in vorhanden:
            im_ziel = self.ziel_halter.ort(f"{element}:{tid}") == ORT_ZIEL
            eintraege.append((ORT_WAHL_ID + i, f"{text}: {'im Zielfenster → auf den Desktop' if im_ziel else 'auf dem Desktop → ins Zielfenster'}",
                              0 if (hat_ziel or im_ziel) else menue.ABGEBLENDET))
        fenster = agent.koerper.terminal if agent.koerper.terminal.sichtbar() else agent.koerper.raute
        gewaehlt = self._menue_anzeigen(fenster.hwnd, eintraege, x, y)
        for i, element, text in vorhanden:
            if gewaehlt == ORT_WAHL_ID + i:
                self.ort_wechseln(tid, element)

    def ort_wechseln(self, tid: str, element: str) -> None:
        agent = self.agenten.get(tid)
        schluessel = f"{element}:{tid}"
        if agent is None or self.ziel_halter is None or schluessel not in self.ziel_halter.elemente:
            return
        ziel = ORT_DESKTOP if self.ziel_halter.ort(schluessel) == ORT_ZIEL else ORT_ZIEL
        fehler = self.ziel_halter.setze_ort(schluessel, ziel)
        if fehler:
            self._setze_status(self.status, fehler)
            return
        liste = {e for e, _ in ORT_ELEMENTE if self.ziel_halter.ort(f"{e}:{tid}") == ORT_ZIEL}
        agent.orte_gewuenscht = tuple(e for e, _ in ORT_ELEMENTE if e in liste)
        text = dict(ORT_ELEMENTE)[element]
        self._setze_status(self.status, f"{agent.name}: {text} steht jetzt {'im Zielfenster' if ziel == ORT_ZIEL else 'auf dem Desktop'}")
        self.einstellungen_sichern()

    # ---- Name und Farbe je Agent (R024) -------------------------------------------------------------------------------
    def name_aendern(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        if agent is not None:
            agent.koerper.eingabe_oeffnen("Neuer Name", lambda text, t=tid: self.umbenennen(t, text))

    def umbenennen(self, tid: str, text: str) -> bool:
        agent = self.agenten.get(tid)
        neu = " ".join((text or "").split())
        if agent is None or not neu:
            return False
        if len(neu) > NAME_MAX:
            self._setze_status(self.status, f"Name zu lang (höchstens {NAME_MAX} Zeichen)")
            return False
        if any(a.name == neu for a in self.agenten.values() if a is not agent):
            self._setze_status(self.status, f"Der Name „{neu}“ ist schon vergeben")
            return False
        alt, agent.name = agent.name, neu
        agent.name_geaendert = neu != agent.schluessel
        agent.koerper.setze_identitaet(name=neu)
        fenster = self.kamera_fenster.get(tid)
        if fenster is not None:
            fenster.setze_identitaet(name=neu)
        if self.chat is not None:
            self.chat.farbe_setzen(neu, w.rgb_hex(agent.koerper.farbe_hex))
        self._setze_status(self.status, f"„{alt}“ heißt jetzt „{neu}“")
        self._regie_anzeigen()
        self.einstellungen_sichern()
        return True

    def farbe_menue(self, tid: str, x: int, y: int) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        eintraege = [(FARBE_WAHL_ID + i, f"● {FARBNAMEN[i]}", menue.GEHAKT if hex_ == agent.koerper.farbe_hex else 0)
                     for i, hex_ in enumerate(stil.AGENTENFARBEN)]
        eintraege += [None, (FARBE_STANDARD_ID, "Standardfarbe", 0)]
        with offene_menues.menue_art("raute.farbe"):
            gewaehlt = self._menue_anzeigen(agent.koerper.raute.hwnd, eintraege, x, y)
        if FARBE_WAHL_ID <= gewaehlt < FARBE_WAHL_ID + len(stil.AGENTENFARBEN):
            self.farbe_setzen(tid, stil.AGENTENFARBEN[gewaehlt - FARBE_WAHL_ID])
        elif gewaehlt == FARBE_STANDARD_ID:
            self.farbe_setzen(tid, None)

    def farbe_setzen(self, tid: str, farbe_hex: str | None) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        standard = stil.agentenfarbe(agent.schluessel)
        neu = farbe_hex or standard
        agent.farbe_ueberschrieben = neu if neu != standard else None
        agent.koerper.setze_identitaet(farbe_hex=neu)
        fenster = self.kamera_fenster.get(tid)
        if fenster is not None:
            fenster.setze_identitaet(farbe_hex=neu)
        if self.chat is not None:
            self.chat.farbe_setzen(agent.name, w.rgb_hex(neu))
        self._regie_anzeigen()
        self.einstellungen_sichern()

    # ---- Ampel: alles, was schiefgehen kann, sichtbar -----------------------------------------------
    AMPEL_WEG_ANZEIGE_S = 45.0  # so lange gilt "Fenster weg" als rote LED, danach ist der Desktop-Fall der Normalzustand

    def ampel_zustand(self, tid: str):
        """Alles, was der Körper über diesen Agenten misst, als Zustand für den Lampenkatalog."""
        from . import ampel
        jetzt = time.monotonic()
        agent = self.agenten[tid]
        stand = self.bilderstrom.stand(tid) if self.bilderstrom is not None else None
        letztes = self.haende_letztes.get(tid)
        terminal = agent.koerper.terminal
        weg_seit = self.ziel_weg_seit.get(tid)
        gruende = {g: jetzt - t for g, t in self.haende_gruende.get(tid, {}).items()}
        ziel = self.bilderstrom.ziele.get(tid) if self.bilderstrom is not None else None
        ziel_zustand = self.ziel_zustand_von(ziel) if ziel is not None else None
        return ampel.Zustand(
            name=agent.name, an=stand["an"] if stand else True, nur_terminal=agent.nur_terminal, haende_an=agent.haende,
            strom_vorhanden=stand is not None, alter_s=stand["alter_s"] if stand else None, gesperrt=self.eingaben_gesperrt,
            letztes=(letztes[0], letztes[1], jetzt - letztes[2]) if letztes else None, gruende=gruende,
            haende_arten={k: (v[0], v[1], jetzt - v[2]) for k, v in self.haende_arten.get(tid, {}).items()},
            haende_ziele={k: (v[0], v[1], jetzt - v[2]) for k, v in self.haende_ziele.get(tid, {}).items()},
            probleme=self.bilderstrom.probleme(tid) if self.bilderstrom is not None else frozenset(),
            kamera=self.medien.kamera_zustand(tid) if self.medien is not None else "aus",
            ziel_zustand=ziel_zustand, aufnahme=self._ziel_faehigkeit(ziel_zustand) if ziel_zustand is not None else None,
            anzeigeort_grund=(self.anzeigeort_grund[tid][0], jetzt - self.anzeigeort_grund[tid][1]) if tid in self.anzeigeort_grund else None,
            dialog=self._dialog_von(tid, agent, jetzt),
            gebunden=bool(terminal.ziel_gebunden), ziel_text=terminal.ziel_text or "",
            fenster_weg=weg_seit is not None and jetzt - weg_seit <= self.AMPEL_WEG_ANZEIGE_S,
            terminal_draussen=self._terminal_draussen(agent), verbunden=self.status == "verbunden")

    def _terminal_draussen(self, agent) -> bool:
        """Liegt das Terminal oder die Raute des Agenten (auch nur teilweise) außerhalb des Bildschirms? Das passierte, als sich die Auflösung änderte."""
        try:
            links, oben, rechts, unten = self._arbeitsflaeche()
            for fenster in (agent.koerper.terminal, agent.koerper.raute):
                fl, fo, fr, fu = fenster.rechteck()
                if fl < links - 2 or fo < oben - 2 or fr > rechts + 2 or fu > unten + 2:
                    return True
        except Exception:
            return False
        return False

    def ampel_takt(self) -> None:
        """Im GUI-Faden, alle paar Sekunden: Lampen aller Agenten berechnen, Dauerfeuer in den Chat, bei neuem Rot piepen."""
        from . import ampel
        jetzt = time.monotonic()
        zeilen = []
        for tid, agent in list(self.agenten.items()):
            lampen = ampel.lampen(self.ampel_zustand(tid))
            self.ampel_stand[agent.name] = lampen
            self._lage_senden(tid, lampen, jetzt)
            self._dialog_melden(tid, agent, lampen)
            zeilen.append((agent.name, lampen))
            meldungen, self._ampel_rot, self._ampel_meldezeit = ampel.chat_meldungen(self._ampel_rot, self._ampel_meldezeit, jetzt, agent.name, lampen)
            for text in meldungen:
                self._meldung_posten(tid, text)
        for name in [n for n in self.ampel_stand if n not in {a.name for a in self.agenten.values()}]:
            self.ampel_stand.pop(name, None)
        piept, self._ampel_pieps = ampel.neue_pieps(self._ampel_pieps, [(n, [ampel.Led(l.kennung, l.farbe, l.wort, l.blinkt, l.behebe, l.piepen) for l in ls]) for n, ls in zeilen])
        if piept and self._piepen is not None:
            try:
                self._piepen()
            except Exception:
                pass  # ein fehlender Ton darf nichts stören

    LAGE_ALLE_S = 5.0  # der Relay hält das Lagebild nach 20 s ohne Meldung für unbekannt

    def _lage_senden(self, tid: str, lampen: list, jetzt: float) -> None:
        """Jeder Agent soll jederzeit wissen, was für ihn klappt: die Lampen gehen alle 5 s an den Relay (`lage.py`); er gibt sie dem Agenten zurück."""
        from .. import lage
        from . import ampel

        zuletzt = self._lage_zeit.get(tid, 0.0)
        if jetzt - zuletzt < self.LAGE_ALLE_S - 0.5:
            return
        try:
            if self._senden("lage", lage.nutzlast(tid, lampen, ampel.gruppe_von)):
                self._lage_zeit[tid] = jetzt
        except Exception:
            pass  # eine verpasste Lagemeldung merkt der Relay am Alter; sie darf den Takt nie anhalten

    def _dialog_melden(self, tid: str, agent, lampen: list) -> None:
        """Einmal je Dialog in den Chat: Daniel soll wissen, dass ein Agent auf ihn wartet (und der Agent sieht es im Lagebild)."""
        dialog = self._dialog_seit.get(tid)
        if dialog is None:
            self._dialog_gemeldet.pop(tid, None)
            return
        if self._dialog_gemeldet.get(tid) == dialog[0] or self.chat is None:
            return
        self._dialog_gemeldet[tid] = dialog[0]
        art, frage = dialog[0]
        from .ampel import DIALOG_ART
        self._meldung_posten(tid, f"⏳ {agent.name} wartet auf {DIALOG_ART.get(art, 'einen Dialog')} in seinem Programm: {frage}. Beantworte ihn im Terminal von {agent.name}.")
        self.log(f"Dialog: {agent.name} wartet auf {DIALOG_ART.get(art, 'einen Dialog')} ({frage})")

    def _dialog_von(self, tid: str, agent, jetzt: float) -> tuple[str, str, float] | None:
        """Wartet der Agent auf einen Dialog seines Programms? (Art, Frage, Sekunden) aus dem sichtbaren Terminalbild, sonst None; die Zeit läuft ab der ersten Sichtung."""
        from .dialog_erkennung import erkenne

        modell = getattr(agent.koerper.terminal, "modell", None)
        try:
            dialog = erkenne([modell.zeile_text(i) for i in range(modell.zeilen)]) if modell is not None else None
        except Exception:
            dialog = None  # ein unlesbares Terminalbild ist kein Dialog und darf den Takt nicht anhalten
        if dialog is None:
            self._dialog_seit.pop(tid, None)
            return None
        alt = self._dialog_seit.get(tid)
        if alt is None or alt[0] != (dialog.art, dialog.frage):
            alt = self._dialog_seit[tid] = ((dialog.art, dialog.frage), jetzt)
        return dialog.art, dialog.frage, jetzt - alt[1]

    def ampel_lampen(self, agent_name: str) -> list:
        """Für ein Ampel-Fenster: die zuletzt berechneten Lampen dieses Agenten."""
        return list(self.ampel_stand.get(agent_name, []))

    def _ampel_fuer(self, tid: str) -> None:
        """Jeder Agent bekommt sein eigenes, kleines, verschiebbares Ampel-Fenster. Abschalten: BRIDGE_AMPEL=0."""
        if self._ampel_bauen is None or tid in self.ampel_fenster or os.environ.get("BRIDGE_AMPEL") == "0":
            return
        agent = self.agenten.get(tid)
        if agent is None:
            return
        flaeche = self._arbeitsflaeche()
        nr = len(self.ampel_fenster)
        fenster = self._ampel_bauen(flaeche[0] + 12 + nr * 100, flaeche[1] + 12, name=agent.name, daten=self.ampel_lampen, aktion=self.ampel_aktion, menue=self.ampel_menue,
                                      farbe=lambda a=agent: a.koerper.farbe_hex)
        fenster.zeige(aktivieren=False)
        self.ampel_fenster[tid] = fenster
        self._fenster_einrichten(f"ampel:{tid}", "ampel", f"ampel:{agent.name}", fenster, nutzer_verborgen=lambda t=tid: t in self.ampel_ausgeblendet)

    def ampel_aktion(self, agent_name: str, aktion: str) -> None:
        """Ein Klick auf eine Lampe: rote Lampe mit Knopf → beheben; sonst die Lampe im Chat erklären. Immer mit Zeile im Log und im Hinweis."""
        tid = next((t for t, a in self.agenten.items() if a.name == agent_name), None)
        if tid is None:
            return
        from . import ampel as ampel_modul
        agent = self.agenten[tid]
        if aktion.startswith("gruppe:"):
            gruppe = aktion[7:]
            teile = [l for l in self.ampel_stand.get(agent_name, []) if ampel_modul.gruppe_von(l.kennung) == gruppe]
            if self.chat is not None and teile:
                self.chat.empfangen(CHAT_AMPEL, f"ℹ [{agent_name}] {ampel_modul.GRUPPEN_ERKLAERUNG.get(gruppe, gruppe)}")
                for l in teile:
                    self.chat.empfangen(CHAT_AMPEL, "    " + ampel_modul.menue_zeile(l))
            return
        if aktion.startswith("info:"):
            kennung = aktion[5:]
            lampe = next((l for l in self.ampel_stand.get(agent_name, []) if l.kennung == kennung), None)
            if lampe is not None and self.chat is not None:
                self.chat.empfangen(CHAT_AMPEL, f"ℹ [{agent_name}] {ampel_modul.menue_zeile(lampe)}")
            return
        if aktion == "desktop_binden":
            self.ziel_loesen(tid)
            self.gui.post(lambda: agent.koerper.terminal.setze_ziel("Ziel: Desktop (ungebunden)", False))
            text = "ganzer Desktop gebunden"
        elif aktion == "strom_neu":
            ok = self.bilderstrom is not None and self.bilderstrom.auffrischen(tid)
            if not ok and self.bilderstrom is not None:
                self.bilderstrom.binden(tid, None)
            text = "Bilder neu gestartet"
        elif aktion == "fenster_vor":
            stand = self.bilderstrom.stand(tid) if self.bilderstrom is not None else None
            hwnd = stand["hwnd"] if stand else None
            ok = bool(hwnd is not None and self._fenster_vor is not None and self._fenster_vor(hwnd))
            text = "Fenster nach vorn geholt" if ok else "Fenster nicht gefunden (Desktop gebunden?)"
        elif aktion == "terminal_holen":
            self._terminal_zurueckholen(agent)
            text = "Terminal und Raute zurück in den Bildschirm geholt"
        else:
            return
        self.log(f"Ampel-Knopf {aktion} für {agent_name}: {text}")
        self._setze_status(self.status, f"{agent_name}: {text}")
        if self.chat is not None:
            self.chat.empfangen(CHAT_AMPEL, f"▶ {agent_name}: {text}")

    def ampel_menue(self, agent_name: str, x: int, y: int) -> None:
        """Strg+Alt + Rechtsklick auf die Ampel (wie bei der Raute): jede Funktion ausgeschrieben, dahinter in Klammern, wie es ihr geht. Eine Zeile anklicken behebt oder erklärt."""
        from . import ampel
        tid = next((t for t, a in self.agenten.items() if a.name == agent_name), None)
        fenster = self.ampel_fenster.get(tid) if tid else None
        if tid is None or fenster is None:
            return
        lampen = self.ampel_stand.get(agent_name, [])
        eintraege: list = [(0, f"Ampel {agent_name}", menue.ABGEBLENDET)]
        reihenfolge: list = []
        for ueberschrift, teile in ampel.menue_gruppen(lampen):
            eintraege += [None, (0, ueberschrift, menue.ABGEBLENDET)]
            for lampe in teile:
                zeile = ampel.menue_zeile(lampe)
                if lampe.behebe and lampe.farbe != ampel.GRUEN:
                    zeile += f"  →  beheben: {ampel.AKTIONS_TEXT.get(lampe.behebe, lampe.behebe)}"
                eintraege.append((AMPEL_ZEILE_ID + len(reihenfolge), "    " + zeile, 0))
                reihenfolge.append(lampe)
        lampen = reihenfolge
        prozent = stil.alpha_prozent(fenster.deckkraft or 255)
        eintraege += [None,
                      (AMPEL_DECKKRAFT_ID, f"Ampel: Deckkraft {prozent} % → nächste Stufe", 0),
                      (AMPEL_GROESSER_ID, "Ampel größer", 0), (AMPEL_KLEINER_ID, "Ampel kleiner", 0),
                      (AMPEL_REGEL_ID, f"Ampel: {self._regel_text(f'ampel:{tid}')} …", 0),
                      (AMPEL_AUSBLENDEN_ID, "Ampel einblenden" if tid in self.ampel_ausgeblendet else "Ampel ausblenden", 0),
                      (AMPEL_DURCHKLICK_ID, f"Durchklickbar, {self._bedientaste_text()} zum Bedienen — {self._durchklick_text(f'ampel:{tid}')}", 0)]
        gewaehlt = self._menue_anzeigen(fenster.hwnd, eintraege, x, y)
        if AMPEL_ZEILE_ID <= gewaehlt < AMPEL_ZEILE_ID + len(lampen):
            lampe = lampen[gewaehlt - AMPEL_ZEILE_ID]
            self.ampel_aktion(agent_name, lampe.behebe if (lampe.behebe and lampe.farbe != ampel.GRUEN) else f"info:{lampe.kennung}")
        elif gewaehlt == AMPEL_REGEL_ID:
            self.regel_menue(f"ampel:{tid}", x, y)
        elif gewaehlt == AMPEL_AUSBLENDEN_ID:
            if tid in self.ampel_ausgeblendet:
                self.ampel_ausgeblendet.discard(tid)
                fenster.zeige(aktivieren=False)
            else:
                self.ampel_ausgeblendet.add(tid)
                fenster.verberge()
        elif gewaehlt == AMPEL_GROESSER_ID:
            fenster.groesser()
            self.einstellungen_sichern()
        elif gewaehlt == AMPEL_KLEINER_ID:
            fenster.groesser(-0.3)
            self.einstellungen_sichern()
        elif gewaehlt == AMPEL_DECKKRAFT_ID:
            fenster.deckkraft_weiter()
            self.einstellungen_sichern()
        elif gewaehlt == AMPEL_DURCHKLICK_ID:
            self.durchklick_umschalten(f"ampel:{tid}")

    def ampeln_umschalten(self) -> None:
        """Alle Ampeln auf einmal aus- oder einblenden: sind alle ausgeblendet, werden alle sichtbar, sonst werden alle ausgeblendet."""
        alle_aus = bool(self.ampel_fenster) and set(self.ampel_fenster) <= self.ampel_ausgeblendet
        for tid, fenster in self.ampel_fenster.items():
            if alle_aus:
                self.ampel_ausgeblendet.discard(tid)
                fenster.zeige(aktivieren=False)
            else:
                self.ampel_ausgeblendet.add(tid)
                fenster.verberge()

    def _terminal_zurueckholen(self, agent) -> None:
        links, oben, rechts, unten = self._arbeitsflaeche()
        for fenster in (agent.koerper.terminal, agent.koerper.raute):
            fl, fo, fr, fu = fenster.rechteck()
            b, h = fr - fl, fu - fo
            x = max(links, min(fl, rechts - b))
            y = max(oben, min(fo, unten - h))
            if (x, y) != (fl, fo):
                fenster.verschiebe(x, y)

    # ---- Regie- und Medienleiste (unten links, für den gewählten Agenten) ------------------------------------------
    def _regie_zeigen(self) -> None:
        if self._regie_bauen is None:
            return
        if self.regie is None:
            x, y = leiste_position(self._arbeitsflaeche())
            self.regie = self._regie_bauen(
                x, y, agent_wechseln=self.agent_wechseln, mikrofon_umschalten=self.mikrofon_umschalten,
                kamera_umschalten=self.kamera_umschalten, regie_menue=self.regie_menue,
                notaus_umschalten=self.notaus_umschalten)
            self.regie.zeige(aktivieren=False)
            self._fenster_einrichten("regie", "regie", "regie", self.regie)
        if self.chat is None and self._chat_bauen is not None:
            flaeche = self._arbeitsflaeche()
            self.chat = self._chat_bauen(leiste_position(flaeche)[0] + REGIE_BREITE + 12, flaeche[3] - 240 - 12,
                                         gesendet=self.daniel_sagt, empfaenger_wechseln=self.empfaenger_wechseln)
            self.chat.zeige(aktivieren=False)
            self._fenster_einrichten("chat", "chat", "chat", self.chat, nutzer_verborgen=lambda: self.chat_ausgeblendet)
            for agent in self.agenten.values():
                self.chat.farbe_setzen(agent.name, w.rgb_hex(agent.koerper.farbe_hex))
            self.chat.farbe_setzen(CHAT_AMPEL, stil.FARBE_TEXT_GEDAEMPFT)  # die Ampel ist kein Agent und nicht Daniel: gedämpftes Grau, die Zeile nennt den Agenten in eckigen Klammern
        self._regie_anzeigen()

    # ---- Sichtbarkeit und Einstellungen je Fenster -----------------------------------------------------------------
    def _fenster_einrichten(self, schluessel: str, art: str, speicher: str, fenster, nutzer_verborgen=lambda: False) -> None:
        """Gespeicherten Ort/Größe/Deckkraft anwenden und das Fenster mit seiner Sichtbarkeitsregel anmelden."""
        self._fenster_art[schluessel] = (art, speicher, fenster)
        try:  # die Standardwerte merken, bevor Gespeichertes angewendet wird (für „zurücksetzen“)
            self._standard[schluessel] = (fenster.rechteck(), fenster.deckkraft, getattr(fenster, "groesse", None))
        except Exception:
            pass
        regel = IMMER
        gespeichert: dict = {}
        if self.einstellungen is not None:
            gespeichert = self.einstellungen.element(speicher)
        if self.durchklick is not None and art in ("chat", "regie", "terminal", "kamera", "ampel"):
            # Standard: durchklickbar wie die Raute (Strg zum Bedienen); Daniel schaltet es je Fenster ab
            an = gespeichert.get("durchklick")
            self.durchklick.registrieren(schluessel, fenster, an if isinstance(an, bool) else True)
        if self.einstellungen is not None:
            daten = self.einstellungen.element(speicher)
            try:
                einst.anwenden(fenster, daten, art, self._bildschirm)
            except Exception as fehler:
                self.log(f"Einstellungen anwenden ({schluessel}): {fehler!r}"[:200])
            regel = Regel.aus_dict(daten.get("regel"))
        if self.ziel_halter is not None and art in ("raute", "terminal", "kamera", "ampel"):
            tid = schluessel.split(":", 1)[1]
            self.ziel_halter.anmelden(schluessel, fenster, lambda t=tid: self._ziel_hwnd(t), nutzer_verborgen)
            alt = nutzer_verborgen
            nutzer_verborgen = lambda s=schluessel, a=alt: a() or self.ziel_halter.versteckt(s)  # noqa: E731
        if self.sichtbarkeit is not None:
            self.sichtbarkeit.registrieren(schluessel, fenster, regel, nutzer_verborgen)

    def _regel_text(self, schluessel: str) -> str:
        return self.sichtbarkeit.regel(schluessel).text() if self.sichtbarkeit is not None else IMMER.text()

    def einstellungen_sichern(self) -> None:
        self.arbeit_speichern()  # die Objekte der Arbeitsfläche liegen in einer eigenen Datei und brauchen die Einstellungen nicht
        if self.einstellungen is None:
            return
        for schluessel, (art, speicher, fenster) in list(self._fenster_art.items()):
            try:
                daten = einst.erfassen(fenster, art)
            except Exception:
                continue
            daten["regel"] = (self.sichtbarkeit.regel(schluessel) if self.sichtbarkeit is not None else IMMER).zu_dict()
            if self.durchklick is not None and schluessel in self.durchklick.eintraege:
                daten["durchklick"] = self.durchklick.aktiv(schluessel)
            if art == "raute":
                agent = self.agenten.get(schluessel.split(":", 1)[1])
                if agent is not None and agent.hotkey:
                    daten["hotkey"] = agent.hotkey
                if agent is not None:
                    daten["haende"] = agent.haende
                    daten["steuerprofil"] = agent.steuerprofil
                    if agent.nur_terminal:
                        daten["nur_terminal"] = True
                    if agent.orte_gewuenscht:
                        daten["orte"] = list(agent.orte_gewuenscht)
            self.einstellungen.setzen(speicher, daten)
        for agent in self.agenten.values():  # Name und Farbe, die Daniel selbst gewählt hat (sonst nichts speichern)
            if agent.schluessel:
                ueber: dict = {}
                if agent.name_geaendert:
                    ueber["name"] = agent.name
                if agent.farbe_ueberschrieben:
                    ueber["farbe"] = agent.farbe_ueberschrieben
                if ueber or self.einstellungen.element(f"agent:{agent.schluessel}"):  # leer lassen, solange nichts geändert wurde
                    self.einstellungen.setzen(f"agent:{agent.schluessel}", ueber)
        globale = {}
        if self.bedientaste is not None:
            globale["bedientaste"] = self.bedientaste.name
        if self.medien is not None and hasattr(self.medien, "modus") and hasattr(self.medien, "sprechtaste_vk"):
            globale.update({"mik_modus": self.medien.modus, "sprechtaste_vk": self.medien.sprechtaste_vk})
            if getattr(self.medien, "mik_geraet", None):
                globale["mik_geraet"] = self.medien.mik_geraet
        if not self.bridge_im_bild:
            globale["bridge_im_bild"] = False
        if self.daniel_ausnahme:
            globale["daniel_ausnahme"] = True
        if globale or self.einstellungen.element("_global"):  # auch leer schreiben, wenn etwas dastand: ein zurückgenommener Wert muss verschwinden
            self.einstellungen.setzen("_global", globale)
        if not self.einstellungen.speichern():
            self.log(self.einstellungen.fehler or "Einstellungen nicht gespeichert")

    def fenster_zuruecksetzen(self) -> None:
        """Alle Fenster (Raute, Terminal, Chat, Leiste, Selbstbild, Ampel) auf ihre Standardplätze, Standardgrößen und Standardwerte, ohne Neustart.
        Namen und Farben der Agenten gehen auf den Standard zurück. Tastenkombinationen, Mikrofon- und Bedientasten-Einstellungen bleiben."""
        for schluessel, (art, speicher, fenster) in list(self._fenster_art.items()):
            standard = self._standard.get(schluessel)
            if standard is not None:
                (links, oben, rechts, unten), deckkraft, groesse = standard
                if art == "raute" and groesse is not None:
                    fenster.groesse_setzen(groesse)
                if art == "ampel":
                    fenster.faktor_setzen(1.0)  # die Größe der Ampel ist ihr Faktor; Fenstermaße und Faktor gehen zusammen zurück
                fenster.verschiebe(links, oben, rechts - links, unten - oben)
                if deckkraft is not None:
                    fenster.setze_deckkraft(deckkraft)
            if self.durchklick is not None and schluessel in self.durchklick.eintraege:
                self.durchklick.setzen(schluessel, True)
            if self.sichtbarkeit is not None:
                self.sichtbarkeit.regel_setzen(schluessel, IMMER)
        for tid in list(self.ampel_ausgeblendet):
            self.ampel_ausgeblendet.discard(tid)
            fenster = self.ampel_fenster.get(tid)
            if fenster is not None:
                fenster.zeige(aktivieren=False)
        for tid, agent in self.agenten.items():
            if agent.name_geaendert:
                agent.name, agent.name_geaendert = agent.schluessel, False
                agent.koerper.setze_identitaet(name=agent.schluessel)
            if agent.farbe_ueberschrieben:
                self.farbe_setzen(tid, None)
            if self.chat is not None:
                self.chat.farbe_setzen(agent.name, w.rgb_hex(agent.koerper.farbe_hex))
        self._regie_anzeigen()
        self.einstellungen_sichern()
        self._setze_status(self.status, "Fenster auf Standard zurückgesetzt")

    def zuruecksetzen_fragen(self, x: int, y: int) -> None:
        gewaehlt = self._menue_anzeigen(self.regie.hwnd, [
            (0, "Alle Fenster, Namen und Farben auf Standard zurücksetzen?", menue.ABGEBLENDET),
            (ZURUECKSETZEN_JA_ID, "Ja, zurücksetzen", 0), (0, "Abbrechen", 0)], x, y)
        if gewaehlt == ZURUECKSETZEN_JA_ID:
            self.fenster_zuruecksetzen()

    def _fenster_vergessen(self, praefix_tid: str) -> None:
        self.einstellungen_sichern()  # Ort des Fensters merken, bevor es verschwindet
        for schluessel in (f"raute:{praefix_tid}", f"terminal:{praefix_tid}", f"kamera:{praefix_tid}", f"ampel:{praefix_tid}"):
            self._fenster_art.pop(schluessel, None)
            if self.ziel_halter is not None:
                self.ziel_halter.abmelden(schluessel)
            if self.sichtbarkeit is not None:
                self.sichtbarkeit.entfernen(schluessel)
            if self.durchklick is not None:
                self.durchklick.entfernen(schluessel)

    # ---- Tastenkombination je Agent (R024: Hotkey einstellbar, steht in der Raute) --------------------------------
    def _bedientaste_text(self) -> str:
        return self.bedientaste.text() if self.bedientaste is not None else "Strg"

    def _hotkey_anmelden(self, tid: str, kombi: Kombination) -> bool:
        aufruf = lambda t=tid: self.eingabe_oeffnen(t)
        setzen = getattr(self.gui, "hotkey_setzen", None)
        if setzen is not None:
            return bool(setzen(f"agent:{tid}", kombi.modifikatoren, kombi.vk, aufruf))
        return bool(self.gui.hotkey(kombi.modifikatoren, kombi.vk, aufruf))

    def _hotkey_waehlen(self, tid: str, name: str) -> Kombination | None:
        """Gespeicherte Kombination dieses Agenten, sonst die erste freie von F13 bis F24; nur zurück, was sich wirklich anmelden ließ."""
        belegt = {a.hotkey for a in self.agenten.values()}
        kandidaten: list[Kombination] = []
        if self.einstellungen is not None:
            gespeichert = Kombination.aus_text(self.einstellungen.element(f"raute:{name}").get("hotkey"))
            if gespeichert is not None:
                kandidaten.append(gespeichert)
        kandidaten += [k for k in (standard_kombination(i) for i in range(MAX_HOTKEYS)) if k is not None]
        for kombi in kandidaten:
            if kombi.text() in belegt:
                continue
            if self._hotkey_anmelden(tid, kombi):
                return kombi
        return None

    def hotkey_festlegen(self, tid: str) -> None:
        """Raute-Menü: die nächste gedrückte Tastenkombination öffnet künftig das Eingabefeld dieser Raute."""
        agent = self.agenten.get(tid)
        if agent is None:
            return
        agent.koerper.zeige_ticker("Tastenkombination drücken … (Esc bricht ab)", DANIEL_FARBE_HEX)
        self._erfasser.im_hintergrund(lambda kombi, t=tid: self.gui.post(lambda: self._hotkey_erfasst(t, kombi)))

    def _hotkey_erfasst(self, tid: str, kombi: Kombination | None) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        if kombi is None:
            agent.koerper.zeige_ticker("Keine Änderung", DANIEL_FARBE_HEX)
        elif not kombi.zulaessig():
            agent.koerper.zeige_ticker(f"{kombi.text()}: nicht erlaubt (Buchstaben nur mit Modifikator)", DANIEL_FARBE_HEX)
        elif kombi.text() in {a.hotkey for a in self.agenten.values() if a.terminal_id != tid}:
            agent.koerper.zeige_ticker(f"{kombi.text()}: schon bei einem anderen Agenten", DANIEL_FARBE_HEX)
        elif not self._hotkey_anmelden(tid, kombi):
            agent.koerper.zeige_ticker(f"{kombi.text()}: von Windows oder einem anderen Programm belegt", DANIEL_FARBE_HEX)
        else:
            agent.hotkey = kombi.text()
            agent.koerper.setze_hotkey(kombi.text())
            agent.koerper.zeige_ticker(f"Eingabefeld: {kombi.text()}", DANIEL_FARBE_HEX)
            self.einstellungen_sichern()

    def bedientaste_menue(self, x: int, y: int) -> None:
        if self.bedientaste is None or self.regie is None:
            return
        namen = list(BEDIENTASTEN)
        eintraege = [(BEDIENTASTE_WAHL_ID + i, BEDIENTASTEN[n][0], menue.GEHAKT if n == self.bedientaste.name else 0)
                     for i, n in enumerate(namen)]
        wahl = self._menue_anzeigen(self.regie.hwnd, eintraege, x, y)
        if BEDIENTASTE_WAHL_ID <= wahl < BEDIENTASTE_WAHL_ID + len(namen):
            self.bedientaste.setzen(namen[wahl - BEDIENTASTE_WAHL_ID])
            self.einstellungen_sichern()

    def _durchklick_text(self, schluessel: str) -> str:
        return "an" if self.durchklick is not None and self.durchklick.aktiv(schluessel) else "aus"

    def durchklick_umschalten(self, schluessel: str) -> None:
        if self.durchklick is not None and schluessel in self.durchklick.eintraege:
            self.durchklick.umschalten(schluessel)
            self.einstellungen_sichern()

    def regel_menue(self, schluessel: str, x: int, y: int) -> None:
        """Auswahl, wann dieses Fenster zu sehen ist: immer, oder nur bei einem der gerade offenen Programme."""
        if self.sichtbarkeit is None or schluessel not in self._fenster_art:
            return
        aktuell = self.sichtbarkeit.regel(schluessel)
        programme = list(self._programme())
        eintraege: list = [(REGEL_IMMER_ID, "Immer sichtbar (Desktop)", menue.GEHAKT if aktuell == IMMER else 0), None]
        auswahl: list[Regel] = []
        if aktuell != IMMER and aktuell.programm not in [p.programm for p in programme]:
            auswahl.append(aktuell)
            eintraege.append((REGEL_PROGRAMM_ID, f"Nur bei {aktuell.programm} (nicht geöffnet)", menue.GEHAKT))
        for programm in programme:
            auswahl.append(programm_regel(programm.programm, programm.titel))
            eintraege.append((REGEL_PROGRAMM_ID + len(auswahl) - 1, f"Nur bei {programm.programm} — {programm.titel[:40]}",
                              menue.GEHAKT if aktuell.programm == programm.programm else 0))
        if not programme:
            eintraege.append((0, "Keine offenen Programme gefunden", menue.ABGEBLENDET))
        hwnd = self.regie.hwnd if self.regie is not None else self._fenster_art[schluessel][2].hwnd
        wahl = self._menue_anzeigen(hwnd, eintraege, x, y)
        if wahl == REGEL_IMMER_ID:
            regel = IMMER
        elif REGEL_PROGRAMM_ID <= wahl < REGEL_PROGRAMM_ID + len(auswahl):
            regel = auswahl[wahl - REGEL_PROGRAMM_ID]
        else:
            return
        self.sichtbarkeit.regel_setzen(schluessel, regel)
        self.einstellungen_sichern()

    def _regie_anzeigen(self) -> None:
        agent = self.agenten.get(self.gewaehlt) if self.gewaehlt else None
        if self.regie is None:
            return
        medien, tid = self.medien, self.gewaehlt
        if self.chat is not None:
            ziel = self.agenten.get(self.empfaenger) if self.empfaenger else None
            self.chat.empfaenger_setzen(ziel.name if ziel else "alle",
                                        w.rgb_hex(ziel.koerper.farbe_hex) if ziel else stil.FARBE_TEXT)
        self.regie.setze(
            agent_name=agent.name if agent else "kein Agent",
            agent_farbe=w.rgb_hex(agent.koerper.farbe_hex) if agent else stil.FARBE_TEXT_GEDAEMPFT,
            mikrofon=medien.mikrofon_zustand(tid) if medien and agent else "aus",
            kamera=medien.kamera_zustand(tid) if medien and agent else "aus",
            notaus=self.not_aus.aktiv,
            hinweis=medien.fehlertext(tid) if medien and agent else "")

    def agent_wechseln(self) -> None:
        ids = list(self.agenten)
        if not ids:
            return
        self.gewaehlt = ids[(ids.index(self.gewaehlt) + 1) % len(ids)] if self.gewaehlt in ids else ids[0]
        self._regie_anzeigen()

    def empfaenger_wechseln(self) -> None:
        """Klick auf „An: …“ im Chat: alle → erster Agent → … → alle."""
        reihe: list[str | None] = [None, *self.agenten]
        aktuell = self.empfaenger if self.empfaenger in self.agenten else None
        self.empfaenger = reihe[(reihe.index(aktuell) + 1) % len(reihe)]
        self._regie_anzeigen()

    def eingabe_oeffnen(self, tid: str) -> None:
        """Die Tastenkombination einer Raute: an genau dieser Raute öffnet sich das Eingabefeld des Agenten."""
        agent = self.agenten.get(tid)
        if agent is not None:
            agent.koerper.eingabe_oeffnen()

    def chat_umschalten(self) -> None:
        if self.chat is not None:
            if self.chat.sichtbar():
                self.chat_ausgeblendet = True
                self.chat.verberge()
            else:
                self.chat_ausgeblendet = False
                self.chat.zeige()

    def _agent_hat_gesprochen(self, name: str, text: str) -> None:
        """Ein Agent hat an seiner Raute gesprochen: Banner und Ticker hat sein Körper schon, hier kommt der Chat."""
        if self.chat is not None:
            self.chat.empfangen(name, text)

    def daniel_sagt(self, text: str, tid: str | None = None, *, in_session: bool = True) -> None:
        """Daniels Worte (Chat-Eingabe oder Regiespruch): in den Chat, 6,6 s als Banner im Zielbereich jedes Angesprochenen und, wie der Plan
        verlangt (G03, E05: „Daniels Antwort landet nachweisbar in der gewählten Session“), als Eingabe in die laufende Session des Angesprochenen.

        Standard ist „an alle“: jede Raute steht im Ziel ihres Agenten (Desktop, Fenster oder Spiel), also sieht jeder Agent das Banner in seinem
        eigenen Bild. `in_session=False` (erkannte Sprache): nur Chat und Banner, das Terminal bleibt unberührt."""
        ziel = tid if tid is not None else self.empfaenger
        einzeln = self.agenten.get(ziel) if ziel else None
        adressaten = [(ziel, einzeln)] if einzeln is not None else list(self.agenten.items())
        if self.chat is not None:
            an = einzeln.name if einzeln is not None else "alle"
            self.chat.empfangen(f"Daniel → {an}" if adressaten else "Daniel", text)
        for kennung, agent in adressaten:
            agent.koerper.zeige_daniel(f"Daniel: {text}", DANIEL_FARBE_HEX)
            if in_session and getattr(agent, "zustand", "running") == "running":
                self.eingabe_senden(kennung, f"Daniel: {text}\r".encode("utf-8"))  # wie getippt: Text und Eingabetaste; bei Not-Aus sperrt eingabe_senden selbst

    def kamera_umschalten(self) -> None:
        if self.medien is not None and self.gewaehlt in self.agenten:
            if self._nur_terminal(self.gewaehlt):
                self._setze_status(self.status, f"{self.agenten[self.gewaehlt].name}: nur Terminal, die Kamera bleibt aus")
                return
            self.medien.kamera_umschalten(self.gewaehlt)
            self._regie_anzeigen()
            fehler = self.medien.fehlertext(self.gewaehlt)
            if fehler:
                self._setze_status(self.status, fehler)

    def mikrofon_umschalten(self) -> None:
        if self.medien is not None and self.gewaehlt in self.agenten:
            self.medien.mikrofon_umschalten(self.gewaehlt)
            self._regie_anzeigen()
            fehler = self.medien.fehlertext(self.gewaehlt)
            if fehler:
                self._setze_status(self.status, fehler)

    def notaus_umschalten(self) -> None:
        self.not_aus.freigeben() if self.not_aus.aktiv else self.not_aus.ausloesen("Regieleiste")

    def regie_menue(self, x: int, y: int) -> None:
        """Regiesprüche (R029) als Gesprächswunsch an den gewählten Agenten, darunter die Startliste (BE02) und Beenden."""
        if self.regie is None:
            return
        sprueche_frei = bool(self.agenten)
        ziel = self.agenten.get(self.empfaenger) if self.empfaenger else None
        eintraege: list = [(0, f"Sprüche gehen an: {ziel.name if ziel else 'alle Agenten'}" if self.agenten else "Kein Agent gestartet",
                            menue.ABGEBLENDET), None]
        eintraege += [(SPRUCH_ID + i, text, 0 if sprueche_frei else menue.ABGEBLENDET)
                      for i, text in enumerate(REGIESPRUECHE)]
        eintraege.append(None)
        start_frei = self.status == "verbunden" and not self.not_aus.aktiv
        starts = sorted(self.startliste.values(), key=lambda start: start["start_id"])
        for i, start in enumerate(starts):
            eintraege.append((START_ID + i, f"Starten: {start['name']} · {start['ort']}",
                              0 if start_frei else menue.ABGEBLENDET))
        if not starts:
            eintraege.append((0, "Keine Startliste (nicht verbunden)", menue.ABGEBLENDET))
        eintraege += self._ablauf_menueeintraege()
        eintraege += [None, (CHAT_ID, "Chat ein-/ausblenden", 0),
                      (AMPEL_ALLE_ID, "Alle Ampeln: " + ("ausgeblendet" if self.ampel_fenster and set(self.ampel_fenster) <= self.ampel_ausgeblendet else "sichtbar") + " → umschalten",
                       0 if self.ampel_fenster else menue.ABGEBLENDET),
                      (CHAT_REGEL_ID, f"Chat: {self._regel_text('chat')} …", 0),
                      (LEISTE_REGEL_ID, f"Leiste: {self._regel_text('regie')} …", 0),
                      (CHAT_DURCHKLICK_ID,
                       f"Chat: durchklickbar, {self._bedientaste_text()} zum Bedienen — {self._durchklick_text('chat')}", 0),
                      (LEISTE_DURCHKLICK_ID,
                       f"Leiste: durchklickbar, {self._bedientaste_text()} zum Bedienen — {self._durchklick_text('regie')}", 0),
                      *self._kamera_menueeintrag(),
                      (BEDIENTASTE_ID, f"Bedientaste für alle Fenster: {self._bedientaste_text()} …", 0),
                      (SPRECHTASTE_ID, f"Sprechtaste (halten zum Sprechen): {self._sprechtaste_text()} …", 0),
                      (MIKMODUS_ID, f"Mikrofon-Modus: {self._mikmodus_text()} …", 0),
                      (MIKGERAET_ID, f"Mikrofon-Gerät: {getattr(self.medien, 'mik_geraet', None) or 'Standard von Windows'} …", 0),
                      (ZEICHNEN_ID, "Zeichnen im Ziel des gewählten Agenten …" if self.agenten else "Zeichnen (erst einen Agenten starten)",
                       0 if self.agenten else menue.ABGEBLENDET),
                      (BILD_FENSTER_ID, "Bridge-Fenster im Bild der Agenten: " + ("an" if self.bridge_im_bild else "aus (sie sehen deine Banner nicht)"), 0),
                      (NUR_TERMINAL_ALLE_ID, "Nur Terminal für alle Agenten: " + ("aus" if self.agenten and all(a.nur_terminal for a in self.agenten.values()) else "an"),
                       0 if self.agenten else menue.ABGEBLENDET),
                      (MENUE_FREIGABE_ID, "Bridge-Menüs für Agenten bedienbar (Praxistest 11–17): " + ("an, nur erlaubte Einträge" if getattr(self.haende_engine, "menue_freigabe", False)
                                                                                                    else "aus"), 0 if self.haende_engine is not None else menue.ABGEBLENDET),
                      (ZURUECKSETZEN_ID, "Fenster, Namen und Farben zurücksetzen …", 0),
                      (BEENDEN_ID, "Bridge beenden", 0)]
        gewaehlt = self._menue_anzeigen(self.regie.hwnd, eintraege, x, y)
        if SPRUCH_ID <= gewaehlt < SPRUCH_ID + len(REGIESPRUECHE) and sprueche_frei:
            self.regie_spruch(REGIESPRUECHE[gewaehlt - SPRUCH_ID])
        elif gewaehlt in self._ablauf_aktionen:
            self._ablauf_aktion_senden(self._ablauf_aktionen[gewaehlt])
        elif gewaehlt == CHAT_ID:
            self.chat_umschalten()
        elif gewaehlt == AMPEL_ALLE_ID:
            self.ampeln_umschalten()
        elif gewaehlt == CHAT_REGEL_ID:
            self.regel_menue("chat", x, y)
        elif gewaehlt == LEISTE_REGEL_ID:
            self.regel_menue("regie", x, y)
        elif gewaehlt == BEDIENTASTE_ID:
            self.bedientaste_menue(x, y)
        elif gewaehlt == SPRECHTASTE_ID:
            self.sprechtaste_festlegen()
        elif gewaehlt == MIKMODUS_ID:
            self.mik_modus_umschalten()
        elif gewaehlt == MIKGERAET_ID:
            self.mik_geraet_waehlen(x, y)
        elif gewaehlt == CHAT_DURCHKLICK_ID:
            self.durchklick_umschalten("chat")
        elif gewaehlt == LEISTE_DURCHKLICK_ID:
            self.durchklick_umschalten("regie")
        elif gewaehlt == KAMERA_DURCHKLICK_ID and self.gewaehlt:
            self.durchklick_umschalten(f"kamera:{self.gewaehlt}")
        elif START_ID <= gewaehlt < START_ID + len(starts):
            self.agent_starten(starts[gewaehlt - START_ID]["start_id"])
        elif gewaehlt == ZEICHNEN_ID:
            self.zeichnen_oeffnen(self.gewaehlt)
        elif gewaehlt == BILD_FENSTER_ID:
            self.bridge_im_bild_umschalten()
        elif gewaehlt == NUR_TERMINAL_ALLE_ID:
            self.nur_terminal_alle()
        elif gewaehlt == MENUE_FREIGABE_ID:
            self.menue_freigabe_umschalten()
        elif gewaehlt == ZURUECKSETZEN_ID:
            self.zuruecksetzen_fragen(x, y)
        elif gewaehlt == BEENDEN_ID:
            self.beenden()

    def _kamera_frame(self, agent_id: str, frame) -> None:
        """Aus dem Kamera-Lesefaden: kodieren im Faden, Absenden über den Sender (Not-Aus-Sperre im Sender-Faden)."""
        if self.not_aus.aktiv or agent_id not in self.agenten or self._nur_terminal(agent_id):
            return
        daten, breite, hoehe = bild.bgr_zu_jpeg(frame.bgr, frame.breite, frame.hoehe)
        if self.sender is not None and self.status == "verbunden":
            self.sender.senden("frame", {"mime": "image/jpeg", "data": base64.b64encode(daten).decode(),
                                         "source": "capture", "captured_at_ms": frame.aufgenommen_ms,
                                         "width": breite, "height": hoehe, "terminal_id": agent_id})

    # ---- Handlungen aus der Oberfläche -------------------------------------------------------------------------------
    def agent_starten(self, start_id: str) -> bool:
        if start_id not in self.startliste or self.not_aus.aktiv:
            return False
        return self._senden("terminal_start", {"start_id": start_id, "rows": STANDARD_ZEILEN, "cols": STANDARD_SPALTEN})

    def eingabe_senden(self, tid: str, daten: bytes) -> None:
        if self.eingaben_gesperrt:
            self._setze_status(self.status, "Not-Aus aktiv — Eingabe nicht gesendet")
            return
        for stueck in eingabe_stuecke(daten):
            self._senden("terminal_input", {"terminal_id": tid, "data": base64.b64encode(stueck).decode()})

    # ---- G10: Hände auf dem gebundenen Fenster --------------------------------------------------------------------------------
    def _bildbezug(self, tid: str, seq: int | None) -> Bildbezug | None:
        """Das Bild, auf das sich der Agent bezieht, aus dem, was der Bilderstrom gesendet hat (None, wenn es nicht mehr gemerkt ist oder ein Desktop-Ziel war)."""
        g = self.bilderstrom.bezug(tid, seq) if self.bilderstrom is not None else None
        if g is None or g.hwnd is None or g.fenster_rect is None:
            return None
        return Bildbezug(ziele.fenster_schluessel(self.ort, g.hwnd), g.seq, g.captured_at_ms, g.breite, g.hoehe, g.fenster_rect, g.hwnd, None, g.bild_rect)

    def _haende_ergebnis_senden(self, payload: dict, e) -> None:
        d = e.zu_dict()
        self.haende_letztes[payload["terminal_id"]] = (d["status"], d["grund"], time.monotonic())
        jetzt_m = time.monotonic()
        aktion = payload.get("aktion")
        art = aktion.get("art") if isinstance(aktion, dict) else None
        if isinstance(art, str) and art:
            self.haende_arten.setdefault(payload["terminal_id"], {})[art] = (d["status"], d["grund"], jetzt_m)
        agent_hier = self.agenten.get(payload["terminal_id"])
        if agent_hier is not None:
            ziel_name = (agent_hier.koerper.terminal.ziel_text or "").removeprefix("Ziel: ").split("—")[-1].strip() or "Desktop"
            self.haende_ziele.setdefault(payload["terminal_id"], {})[ziel_name[:24]] = (d["status"], d["grund"], jetzt_m)
        if d["status"] != "ausgefuehrt" and d["grund"]:
            self.haende_gruende.setdefault(payload["terminal_id"], {})[d["grund"]] = time.monotonic()
        beobachtet = {k: v for k, v in d["observed"].items() if k in ("zeiger", "erwartet", "zeichen", "kombi", "fehler")}
        if self.sender is not None and self.status == "verbunden":
            self.sender.senden("haende_ergebnis", {"terminal_id": payload["terminal_id"], "auftrag_id": payload["auftrag_id"], "status": d["status"], "grund": d["grund"][:60],
                                                   "accepted": d["accepted"], "delivered": d["delivered"], "observed": beobachtet, "dauer_ms": d["dauer_ms"], "audited": d["audited"]})

    def _haende_auftrag(self, payload: dict) -> None:
        """Im GUI-Thread angekommen; ausgeführt wird im eigenen Faden (die Engine arbeitet nacheinander, ein Auftrag blockiert die Oberfläche nie)."""
        from .eingabe_adapter import Ergebnis

        tid = payload["terminal_id"]
        agent = self.agenten.get(tid)

        def abgelehnt(grund: str) -> None:
            self._haende_ergebnis_senden(payload, Ergebnis(payload["auftrag_id"], "abgelehnt", grund))

        if isinstance(payload["aktion"], dict) and payload["aktion"].get("art") == "controller":
            return self._controller_auftrag(payload)
        aktion = Aktion.aus_dict(payload["aktion"])
        if self.haende_engine is None:
            return abgelehnt("haende_nicht_verfuegbar")
        if aktion is None:
            return abgelehnt("aktion_ungueltig")
        if agent is None:
            return abgelehnt("kein_ziel")
        haende_erlaubt = agent.haende and not agent.nur_terminal
        profil_erlaubt = steuerprofil.profil(agent.steuerprofil).erlaubt(aktion.art)
        lease_grund = "" if int(time.time() * 1000) < payload["lease_bis_ms"] else "lease_abgelaufen"
        bezug = self._bildbezug(tid, payload["seq"])

        def lauf() -> None:
            freigegeben = False if aktion.art == "menue" else self._bridge_fenster_freigeben(payload["ziel"], aktion)  # ein Menüklick trifft das Menü, nicht das Ziel
            try:
                e = self.haende_engine.ausfuehren(payload["auftrag_id"], aktion, ziel=payload["ziel"], bezug=bezug, lease_grund=lease_grund, haende_erlaubt=haende_erlaubt,
                                                  profil_erlaubt=profil_erlaubt)
            except Exception as fehler:
                self.log(f"haende {payload['auftrag_id']}: {fehler!r}"[:300])
                e = Ergebnis(payload["auftrag_id"], "fehler", "backend_fehler")
            finally:
                if freigegeben:
                    self._bridge_fenster_wieder_durchklickbar()
            self._haende_ergebnis_senden(payload, e)

        threading.Thread(target=lauf, daemon=True, name=f"haende-{payload['auftrag_id']}").start()

    def _bridge_fenster_freigeben(self, ziel: str, aktion) -> bool:
        """Ist das Ziel ein Fenster der Bridge (Regieleiste, Chat, Terminal …), das im Normalmodus durchklickbar ist, wäre es für die Hände unerreichbar:
        der Käfig fände das Fenster darunter am Klickpunkt (`punkt_verdeckt`), und ein Klick ginge hindurch. Für die Dauer der Aktion gilt es wie bei gehaltener
        Bedientaste als klickbar; danach ist es wieder durchklickbar. Gibt zurück, ob freigegeben wurde."""
        try:
            hwnd = int(str(ziel).rsplit(":", 1)[-1])
        except ValueError:
            return False
        dauer = (getattr(aktion, "dauer_ms", 0) or 0) / 1000 + 4.0
        raute = next((a.koerper.raute for a in self.agenten.values() if getattr(a.koerper.raute, "hwnd", None) == hwnd), None)
        if raute is not None:  # die Raute regelt ihre Durchklickbarkeit selbst (Bedientaste im Timer), nicht über die Verwaltung
            raute.erzwingen(dauer)
            fertig = threading.Event()
            self.gui.post(lambda: (raute.bedienbar_setzen(True), fertig.set()))
            fertig.wait(1.0)
            time.sleep(0.15)
            return True
        if self.durchklick is None or not self.durchklick.gehoert(hwnd):
            return False
        self.durchklick.erzwingen(dauer)
        fertig = threading.Event()
        self.gui.post(lambda: (self.durchklick.tick(), fertig.set()))
        fertig.wait(1.0)
        time.sleep(0.15)  # der Fenstermanager übernimmt die neue Eingabeform nicht im selben Atemzug
        return True

    def _bridge_fenster_wieder_durchklickbar(self) -> None:
        for agent in list(self.agenten.values()):
            raute = getattr(agent.koerper, "raute", None)
            if raute is not None and hasattr(raute, "erzwingen"):
                raute.erzwingen(0)  # der Timer der Raute stellt „durchklickbar“ beim nächsten Takt wieder her
        if self.durchklick is not None:
            self.durchklick.erzwingen(0)
            self.gui.post(self.durchklick.tick)

    def _controller_auftrag(self, payload: dict) -> None:
        """Ein virtueller Controller (G10): dieselben Sperren wie die Hände; das Gerät entsteht erst beim ersten Auftrag, und nur, wenn Backend und Treiber da sind (nie installiert)."""
        from .controller_adapter import ControllerAktion, ControllerEngine, ControllerErgebnis, waehle_backend

        tid = payload["terminal_id"]
        agent = self.agenten.get(tid)
        a = ControllerAktion.aus_dict(payload["aktion"])

        def melden(e) -> None:
            self._haende_ergebnis_senden(payload, e)

        if self.haende_engine is None:
            return melden(ControllerErgebnis(payload["auftrag_id"], "abgelehnt", "haende_nicht_verfuegbar"))
        if a is None:
            return melden(ControllerErgebnis(payload["auftrag_id"], "abgelehnt", "aktion_ungueltig"))
        if agent is None:
            return melden(ControllerErgebnis(payload["auftrag_id"], "abgelehnt", "kein_ziel"))
        if getattr(self, "controller_engine", None) is None:
            h = self.haende_engine
            self.controller_engine = ControllerEngine(waehle_backend(), not_aus=lambda: bool(h.not_aus is not None and h.not_aus.aktiv), daniel_uebernimmt=lambda: bool(h.daniel_uebernimmt),
                                                      verbindung=lambda: bool(h.verbindung))
        engine = self.controller_engine
        haende_erlaubt = agent.haende and not agent.nur_terminal
        profil_erlaubt = steuerprofil.profil(agent.steuerprofil).erlaubt("controller")
        lease_grund = "" if int(time.time() * 1000) < payload["lease_bis_ms"] else "lease_abgelaufen"

        def lauf() -> None:
            try:
                e = engine.ausfuehren(payload["auftrag_id"], a, lease_grund=lease_grund, haende_erlaubt=haende_erlaubt, profil_erlaubt=profil_erlaubt)
            except Exception as fehler:
                self.log(f"controller {payload['auftrag_id']}: {fehler!r}"[:300])
                e = ControllerErgebnis(payload["auftrag_id"], "fehler", "backend_fehler")
            melden(e)

        threading.Thread(target=lauf, daemon=True, name=f"controller-{payload['auftrag_id']}").start()

    # ---- G11: WorldDOM -------------------------------------------------------------------------------------------------------------
    def zeige_overlay(self, tid: str, ziel: str, rel: tuple[float, float], text: str, empfaenger: tuple[str, ...]) -> str | None:
        """Ein Zeichen in der gemeinsamen Arbeitsfläche (G08): auf Daniels Bildschirm und in den Bildern der gewählten Agenten — die Anwendung selbst wird nicht berührt."""
        import uuid as _uuid
        from .objekte import Objekt

        nachbarn = self._gate_nachbarn(tid)
        # Wer niemanden nennt, zeigt allen im selben Gate (der Sinn einer Zeigegeste); wer Empfänger nennt, zeigt genau diesen (privat, „Sichtbar für …“).
        gesehen_von = tuple(dict.fromkeys((tid, *(empfaenger or nachbarn))))
        o = Objekt(f"zeige-{_uuid.uuid4().hex[:8]}", "marker", [(max(0.0, min(1.0, rel[0])), max(0.0, min(1.0, rel[1])))], farbe="#00B7FF", text=text[:80], bildschirm=True,
                   empfaenger=gesehen_von)
        oid = self.arbeit.dokument(ziel).hinzufuegen(o)
        if oid is not None and self.anzeige is not None:
            self.gui.post(self.anzeige.tick)
        if oid is not None:
            self._sofortbild([t for t in gesehen_von if t != tid], f"Zeigegeste von {self.agenten[tid].name if tid in self.agenten else tid}")
        return oid

    def _weltdom_ergebnis_senden(self, payload: dict, status: str, daten: dict) -> None:
        if self.sender is not None and self.status == "verbunden":
            self.sender.senden("weltdom_ergebnis", {"terminal_id": payload["terminal_id"], "auftrag_id": payload["auftrag_id"], "status": status[:30], "daten": daten})

    def _weltdom_auftrag(self, payload: dict) -> None:
        """Im GUI-Thread angekommen; gemessen, aufgelöst und gehandelt wird im eigenen Faden (Bilderkennung dauert, die Oberfläche bleibt frei)."""
        from .weltdom_befehle import pruefe_args

        tid = payload["terminal_id"]
        agent = self.agenten.get(tid)
        befehl = payload["befehl"]

        def abgelehnt(grund: str) -> None:
            self._weltdom_ergebnis_senden(payload, "abgelehnt", {"grund": grund})

        args = pruefe_args(befehl, payload["args"], intern=True)
        if self.weltdom_dienst is None:
            return abgelehnt("weltdom_nicht_verfuegbar")
        if args is None:
            return abgelehnt("befehl_ungueltig")
        if agent is None:
            return abgelehnt("kein_ziel")
        bis = payload["lease_bis_ms"]
        lease_grund = "lease_fehlt" if not bis else ("" if int(time.time() * 1000) < bis else "lease_abgelaufen")
        haende_erlaubt = agent.haende and not agent.nur_terminal
        ziel, seq, dienst = payload["ziel"], payload["seq"], self.weltdom_dienst
        urheber = args.get("urheber") or agent.name

        def lauf() -> None:
            try:
                if befehl == "liste":
                    r = dienst.liste(ziel, herkunft=args.get("herkunft"), rolle=args.get("rolle"), text=args.get("text"), neu_messen=args.get("neu_messen", True))
                elif befehl == "aktion":
                    r = dienst.aktion(tid, ziel, args["knoten"], args["aktion"], args.get("text"), args.get("erwartung"), seq, haende_erlaubt=haende_erlaubt, profil=agent.steuerprofil, lease_grund=lease_grund)
                elif befehl == "zeige":
                    r = dienst.zeige(tid, ziel, tuple(args["punkt"]), seq, urheber, args["modus"], tuple(args.get("empfaenger", ())), aktion=args.get("aktion", "klick"), text=args.get("text"),
                                     haende_erlaubt=haende_erlaubt, profil=agent.steuerprofil, lease_grund=lease_grund)
                elif befehl == "anker_neu":
                    r = dienst.anker_neu(tid, ziel, args["name"], tuple(args["punkt"]) if args.get("punkt") else None, seq, urheber, args.get("herkunft", "authored"))
                elif befehl == "markiert":
                    r = dienst.markiert(ziel, neu_messen=args.get("neu_messen", True))
                    daten = r.pop("_jpeg", None)
                    if daten is not None:
                        if not self._senden("frame", {"mime": "image/jpeg", "data": base64.b64encode(daten).decode(), "source": "synthetic", "captured_at_ms": int(time.time() * 1000),
                                                      "width": r["breite"], "height": r["hoehe"], "terminal_id": tid, "aufnahme": "markiert"}):
                            r = {"status": "fehler", "grund": "bild_nicht_gesendet"}
                elif befehl == "profil_speichern":
                    r = dienst.profil_speichern(ziel, args["name"], urheber, args.get("passt_auf"), args.get("beschreibung", ""))
                elif befehl == "profil_laden":
                    r = dienst.profil_laden(tid, ziel, args["name"], seq, urheber, args.get("version"))
                elif befehl == "profil_liste":
                    r = dienst.profil_liste(args.get("passt_auf"), bool(args.get("alle")))
                elif befehl == "profil_weg":
                    r = dienst.profil_weg(args["name"], bool(args.get("aktiv", False)))
                else:
                    r = dienst.anker_weg(ziel, args["knoten"])
            except Exception as fehler:
                self.log(f"weltdom {payload['auftrag_id']}: {fehler!r}"[:300])
                r = {"status": "fehler", "grund": "ausfuehrung_fehlgeschlagen"}
            status = str(r.pop("status", "ok"))
            self._weltdom_ergebnis_senden(payload, status, r)

        threading.Thread(target=lauf, daemon=True, name=f"weltdom-{payload['auftrag_id']}").start()

    # ---- G12: Abläufe und Regiesprüche -----------------------------------------------------------------------------------------------------------------
    ABLAUF_ID = 4200

    def regie_spruch(self, spruch: str) -> None:
        """Ein Regiespruch für den gewählten Agenten. Mit neuem Starter entscheidet dieser, ob es eine echte Wirkung gibt (Ablauf pausieren, Frage beantworten …) und meldet es zurück; sonst wie bisher als Banner."""
        tid = self.empfaenger if self.empfaenger in self.agenten else self.gewaehlt
        if tid in self.agenten and self.anzeigeorte.unterstuetzt and self._senden("regie_spruch", {"terminal_id": tid, "spruch": spruch[:60]}):
            return
        self.daniel_sagt(spruch, in_session=False)  # Regiesprüche haben eigene Semantik (R029/R030): Banner oder echte Wirkung, nicht heimlich ins Terminal

    def _regie_ergebnis(self, payload: dict) -> None:
        """Der Starter sagt, was der Spruch bewirkt hat. Gesprächswünsche kommen wie bisher als Banner; echte Wirkungen werden benannt."""
        tid = payload["terminal_id"]
        agent = self.agenten.get(tid)
        if payload["wirkung"] == "gespraech" and payload["zugestellt"]:
            self.daniel_sagt(payload["spruch"], tid, in_session=False)
        if agent is not None:
            etikett = "Wirkung" if payload["wirkung"] == "echt" else ("Gespräch, keine echte Wirkung" if payload["wirkung"] == "gespraech" else "nicht ausgeführt")
            agent.koerper.zeige_ticker(f"Regie „{payload['spruch']}“ — {etikett}: {payload['hinweis']}"[:200], DANIEL_FARBE_HEX)
        self._setze_status(self.status, f"Regie „{payload['spruch']}“: {payload['aktion']}")

    def _ablauf_stand(self, payload: dict) -> None:
        self.ablauf_stand = payload
        self._melden()

    def _ablauf_menueeintraege(self) -> list:
        """Läufe mit ihrer nächsten sinnvollen Aktion, offene Freigaben, Abläufe zum Starten und der Lernschalter — nur, wenn der Starter Abläufe kennt."""
        self._ablauf_aktionen = {}
        st = self.ablauf_stand
        if not self.anzeigeorte.unterstuetzt or not (st["laeufe"] or st["offen"] or st["ablaeufe"] or st.get("seeds")):
            return []
        eintraege: list = [None]
        n = 0

        def neu(text, aktion, flags=0):
            nonlocal n
            self._ablauf_aktionen[self.ABLAUF_ID + n] = aktion
            eintraege.append((self.ABLAUF_ID + n, text, flags))
            n += 1

        for f in st["offen"][:5]:
            neu(f"Freigeben: {f['beschreibung'][:50]}", {"aktion": "freigeben", "frage_id": f["id"]})
            neu(f"Verweigern: {f['beschreibung'][:50]}", {"aktion": "verweigern", "frage_id": f["id"]})
        for l in st["laeufe"][:6]:
            kopf = f"{l['ablauf']} · {l['agent']} · {l['status']}"
            if l["status"] == "running":
                neu(f"Ablauf pausieren: {kopf}", {"aktion": "pausieren", "lauf_id": l["id"]})
            elif l["status"] == "paused":
                neu(f"Ablauf fortsetzen: {kopf}", {"aktion": "fortsetzen", "lauf_id": l["id"]})
            if l["status"] in ("running", "paused", "blocked"):
                neu(f"Ablauf abbrechen: {kopf}", {"aktion": "abbrechen", "lauf_id": l["id"]})
        for x in (st.get("seeds") or [])[:8]:  # G15: aktive Seeds und laufende Loops, von Daniel zurücknehmbar
            if x.get("art") == "loop":
                neu(f"Loop stoppen: {x['titel'][:40]} ({x['zieltyp']})", {"aktion": "loop_stoppen", "loop_id": x["id"]})
            else:
                neu(f"Seed zurückziehen: {x['titel'][:40]} ({x['zieltyp']})", {"aktion": "seed_zurueckziehen", "seed_id": x["id"]})
        tid = self.gewaehlt if self.gewaehlt in self.agenten else None
        if tid:
            for a in st["ablaeufe"][:6]:
                neu(f"Ablauf starten: {a['name']} (v{a['version']}) für {self.agenten[tid].name}", {"aktion": "start", "ablauf_id": a["id"], "terminal_id": tid})
        neu("Lernen aus Abläufen: " + ("an — ausschalten" if st["lernen"] else "aus — einschalten"), {"aktion": "lernen", "an": not st["lernen"]})
        return eintraege

    def _ablauf_aktion_senden(self, aktion: dict) -> None:
        if self._senden("ablauf_steuern", aktion):
            self._setze_status(self.status, f"Ablauf: {aktion['aktion']} gesendet")

    def ausnahme_umschalten(self) -> None:
        self.daniel_ausnahme = not self.daniel_ausnahme
        self.einstellungen_sichern()
        self._setze_status(self.status, "Daniels Eingabe unterbricht die Hände " + ("NICHT mehr (Ausnahme an, Not-Aus bleibt)" if self.daniel_ausnahme else "wieder (Ausnahme aus)"))

    def agent_profil_wechseln(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        namen = steuerprofil.PROFILE
        agent.steuerprofil = namen[(namen.index(agent.steuerprofil) + 1) % len(namen)] if agent.steuerprofil in namen else steuerprofil.STANDARD
        self.einstellungen_sichern()
        self._setze_status(self.status, f"{agent.name}: Steuerprofil {agent.steuerprofil} — {steuerprofil.profil(agent.steuerprofil).text}")

    def agent_pause_umschalten(self, tid: str) -> None:
        """Den Prozess dieses Agenten anhalten oder fortsetzen (der Starter schickt SIGSTOP/SIGCONT an die ganze Prozessgruppe)."""
        agent = self.agenten.get(tid)
        if agent is None or agent.zustand not in ("running", "paused"):
            self._setze_status(self.status, "Pausieren geht nur bei einem laufenden Agenten")
            return
        self._senden("terminal_steuern", {"terminal_id": tid, "aktion": "fortsetzen" if agent.zustand == "paused" else "pause"})

    def agent_beenden(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        if agent.zustand in ("exited", "failed"):
            self._agent_entfernen(tid)  # Sitzung ist schon vorbei: nur die Fenster schließen
            return
        agent.beenden_gewuenscht = True  # sobald die Sitzung endet, verschwindet der Körper
        self._senden("terminal_close", {"terminal_id": tid})

    def _agent_entfernen(self, tid: str) -> None:
        agent = self.agenten.pop(tid, None)
        if agent is None:
            return
        self._fenster_vergessen(tid)
        self.bildfolgen.stoppen(tid)
        fenster = self.kamera_fenster.pop(tid, None)
        if fenster is not None:
            fenster.schliessen()
        self._kamera_verborgen.discard(tid)
        loeschen = getattr(self.gui, "hotkey_loeschen", None)
        if loeschen is not None:
            loeschen(f"agent:{tid}")  # die Tastenkombination wird frei (sonst bliebe sie für den nächsten Agenten belegt)
        if self.bilderstrom is not None:
            self.bilderstrom.loesen(tid)
        ampel = self.ampel_fenster.pop(tid, None)
        if ampel is not None:
            ampel.schliessen()
        agent.koerper.schliessen()
        if self.medien is not None:
            self.medien.stoppen(tid)
        if self.gewaehlt == tid:
            self.gewaehlt = next(iter(self.agenten), None)
        if self.empfaenger == tid:
            self.empfaenger = None
        self._regie_anzeigen()
        self._melden()

    # ---- Selbstbild: Daniels Kamerabild bei jedem Agenten ----------------------------------------------------------
    def _medien_gemeldet(self) -> None:
        self._regie_anzeigen()
        self._kamera_fenster_abgleichen()

    def _kamera_menueeintrag(self) -> list:
        """Regie-Menüpunkt für das Selbstbild des gewählten Agenten (nur, wenn es sein Fenster schon gibt)."""
        schluessel = f"kamera:{self.gewaehlt}"
        if self.durchklick is None or schluessel not in self.durchklick.eintraege:
            return []
        return [(KAMERA_DURCHKLICK_ID,
                 f"Selbstbild: durchklickbar, {self._bedientaste_text()} zum Bedienen — {self._durchklick_text(schluessel)}", 0)]

    def _kamera_vorschau(self, tid: str, frame) -> None:
        """Aus dem Kamera-Faden: nur das jeweils neueste Bild merken und genau einen Auftrag an den GUI-Thread schicken."""
        if self._kamera_bauen is None:
            return
        schon_wartend = tid in self._vorschau_neu
        self._vorschau_neu[tid] = frame
        if not schon_wartend:
            self.gui.post(lambda t=tid: self._vorschau_zeigen(t))

    def _vorschau_zeigen(self, tid: str) -> None:
        frame = self._vorschau_neu.pop(tid, None)
        fenster = self.kamera_fenster.get(tid)
        if frame is not None and fenster is not None and tid not in self._kamera_verborgen:
            fenster.bild_setzen(frame.bgr, frame.breite, frame.hoehe)

    def _kamera_fenster_abgleichen(self) -> None:
        """Pro Agent: Kamera an → Selbstbild-Fenster da; Kamera aus/Fehler → weg."""
        if self._kamera_bauen is None or self.medien is None:
            return
        for tid, agent in self.agenten.items():
            zustand = self.medien.kamera_zustand(tid)
            fenster = self.kamera_fenster.get(tid)
            if zustand in ("ein", "startet") and tid not in self._kamera_verborgen:
                if fenster is None:
                    fenster = self._kamera_fenster_bauen(tid, agent)
                    if fenster is None:
                        continue
                if zustand == "startet":
                    fenster.bild_loeschen()
                if (self.sichtbarkeit is None or self.sichtbarkeit.sichtbar_erlaubt(f"kamera:{tid}")) and not (
                        self.ziel_halter is not None and self.ziel_halter.versteckt(f"kamera:{tid}")):
                    fenster.zeige(aktivieren=False)
            else:
                if zustand not in ("ein", "startet"):
                    self._kamera_verborgen.discard(tid)  # beim nächsten Einschalten wieder zeigen
                if fenster is not None:
                    fenster.verberge()

    def _kamera_fenster_bauen(self, tid: str, agent):
        flaeche = self._arbeitsflaeche()
        nummer = list(self.agenten).index(tid)
        x, y = flaeche[2] - 260 - nummer * 24, flaeche[3] - 210 - nummer * 24
        try:
            fenster = self._kamera_bauen(x, y, name=agent.name, farbe_hex=agent.koerper.farbe_hex,
                                         verbergen_gewuenscht=lambda t=tid: self._kamera_verbergen(t))
        except Exception as fehler:
            self.log(f"Selbstbild-Fenster ({agent.name}): {fehler!r}"[:200])
            return None
        self.kamera_fenster[tid] = fenster
        self._fenster_einrichten(f"kamera:{tid}", "kamera", f"kamera:{agent.schluessel}", fenster,
                                 nutzer_verborgen=lambda t=tid: t in self._kamera_verborgen)
        if "kamera" in agent.orte_gewuenscht and self.ziel_halter is not None and self._ziel_hwnd(tid) is not None:
            self.ziel_halter.setze_ort(f"kamera:{tid}", ORT_ZIEL)
        return fenster

    def _kamera_verbergen(self, tid: str) -> None:
        self._kamera_verborgen.add(tid)
        fenster = self.kamera_fenster.get(tid)
        if fenster is not None:
            fenster.verberge()

    def _bilder_text(self, tid: str) -> str:
        if self.bilderstrom is None or tid not in self.bilderstrom.ziele:
            return "kein Ziel gebunden"
        if self._nur_terminal(tid):
            return "aus (nur Terminal)"
        ziel = self.bilderstrom.ziele[tid]
        zaehler = f", {getattr(ziel, 'gesendet', 0)} gesendet" if isinstance(getattr(ziel, "gesendet", None), int) else ""
        verworfen = getattr(self.sender, "verworfen", 0) if self.sender is not None else 0
        ueberlast = f", Überlast: {verworfen} verworfen" if isinstance(verworfen, int) and verworfen > 0 else ""
        return ("an" if self.bilderstrom.an(tid) else "aus") + zaehler + ueberlast

    def bilder_umschalten(self, tid: str) -> None:
        if self.bilderstrom is not None:
            self.bilderstrom.umschalten(tid)

    def strom_senden(self, tid: str, payload: dict) -> bool:
        """Aus dem Bilderstrom-Faden: ein Bild in die Sendewarteschlange (threadsicher; Not-Aus sperrt im Sender)."""
        if self.sender is None or self.status != "verbunden" or self._nur_terminal(tid):
            return False
        return self.sender.senden("frame", payload)

    def strom_ziel_verschwunden(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        self.ziel_weg_seit[tid] = time.monotonic()
        if agent is not None:
            self.gui.post(lambda: agent.koerper.zeige_ticker("Bilder: das gebundene Fenster ist weg — Bilder jetzt vom ganzen Desktop",
                                                               DANIEL_FARBE_HEX))
            self.gui.post(lambda: agent.koerper.terminal.setze_ziel("Ziel: Desktop (ungebunden)", False))

    def _strom_binden(self, tid: str, bindung: Bindung) -> None:
        """Nach der Bindung bekommt der Agent laufend Bilder seines Ziels (Fenster folgt, Desktop ganz)."""
        if self.bilderstrom is None:
            return
        import re
        self.ziel_weg_seit.pop(tid, None)
        self.bilderstrom.binden(tid, ziele.fenster_kennung(str(getattr(bindung.item, "target_id", ""))))

    # ---- Zeichnen: Objekte im Gate (G08) ---------------------------------------------------------------------------------
    def _arbeit_zuordnen(self, tid: str, bindung) -> None:
        """Beim Binden: das Gate bekommt einen stabilen Namen (Programm), damit gespeicherte Objekte wiederkommen."""
        import ntpath  # Windows-Pfade, auch wenn die Prüfung unter Linux läuft
        pfad = getattr(bindung.item, "process_path", None)
        schluessel = self.ziel_schluessel(tid)
        if schluessel is None:
            return
        self.arbeit.zuordnen(schluessel, "desktop" if schluessel == "desktop" else (ntpath.basename(pfad or "").lower() or schluessel))

    def arbeit_speichern(self) -> None:
        if self._arbeit_pfad is not None:
            self.arbeit.speichern(self._arbeit_pfad)

    def _gate_rechteck(self, schluessel: str):
        from .ziel_halter import fenster_zustand
        if ziele.ist_fenster(schluessel):
            existiert, minimiert, rect = fenster_zustand(ziele.fenster_kennung(schluessel))
            return rect if existiert and not minimiert else None
        return self._arbeitsflaeche()

    def zeichnen_oeffnen(self, tid: str | None = None, ziel: str | None = None, programm: str | None = None) -> bool:
        """Den Zeichenmodus für das Gate dieses Agenten öffnen: Editorfläche auf dem Gate plus Werkzeugleiste. Esc oder „Fertig“ beendet ihn."""
        tid = tid or self.gewaehlt
        agent = self.agenten.get(tid) if tid else None
        if agent is None or self._zeichen_bauen is None or self._leiste_bauen is None:
            return False
        if self.editor_offen is not None:
            self.zeichnen_schliessen()
        schluessel = ziel or self.ziel_schluessel(tid) or "desktop"
        if ziel is not None:  # frei gewähltes Ziel (Menü „Ziel …“): gespeicherte Objekte dieses Programms holen
            self.arbeit.zuordnen(schluessel, "desktop" if schluessel == "desktop" else (programm or schluessel))
        rect = self._gate_rechteck(schluessel)
        if rect is None:
            self._setze_status(self.status, f"{agent.name}: das gebundene Fenster ist nicht sichtbar, zum Zeichnen erst wiederherstellen")
            return False
        from .editor_logik import Editor
        dok = self.arbeit.dokument(schluessel)
        gebunden = self.ziel_schluessel(tid) == schluessel
        ref: dict = {}

        def agenten_im_ziel():
            return self._agenten_im_ziel(schluessel)
        editor = Editor(dok, lambda: ref["fenster"].clientgroesse(), bei_aenderung=lambda: self._editor_neu(), bei_beenden=self.zeichnen_schliessen,
                        agenten=agenten_im_ziel)
        editor.kontext_menue = self._zeichnen_kontext_menue
        if gebunden:
            editor.neu_empfaenger = ()  # Standard: auf dem Bildschirm; „Sichtbar für …“ macht Objekte privat
        fenster = self._zeichen_bauen(rect, editor, agent.koerper.farbe_hex)
        ref["fenster"] = fenster
        leiste = self._leiste_bauen(0, 0, editor, bild_waehlen=self._zeichnen_bild_waehlen, sichtbar_menue=self._zeichnen_sichtbar_menue,
                                    ziel_menue=self._zeichnen_ziel_menue, fertig=self.zeichnen_schliessen)
        links, oben, _r, _u = leiste.rechteck()
        lb, lh = _r - links, _u - oben
        bildschirm = self._arbeitsflaeche()
        x = max(bildschirm[0], min(rect[0], bildschirm[2] - lb))
        y = rect[1] - lh - 6 if rect[1] - lh - 6 >= bildschirm[1] else rect[1] + 10
        leiste.verschiebe(x, y)
        self.editor_offen = {"schluessel": schluessel, "tid": tid, "editor": editor, "fenster": fenster, "leiste": leiste}
        fenster.zeige(aktivieren=True)
        leiste.zeige(aktivieren=False)
        if hasattr(fenster, "fokus_erzwingen"):
            fenster.fokus_erzwingen()
        hinweis = "" if gebunden else " (dieses Ziel ist für den Agenten nicht gebunden: Objekte nur für Agenten erscheinen in seinem Bild erst nach der Bindung)"
        self._setze_status(self.status, f"Zeichnen für {agent.name}: Esc beendet{hinweis}")
        return True

    def _editor_neu(self) -> None:
        if self.editor_offen is not None:
            self.editor_offen["fenster"].neu()
            self.editor_offen["leiste"].neu_zeichnen()

    def zeichnen_schliessen(self) -> None:
        offen, self.editor_offen = self.editor_offen, None
        if offen is None:
            return
        offen["editor"]._text_festschreiben()
        for fenster in (offen["leiste"], offen["fenster"]):
            fenster.schliessen()
        self.arbeit_speichern()
        if self.anzeige is not None:
            self.anzeige.tick()

    def _zeichnen_bild_waehlen(self) -> None:
        offen = self.editor_offen
        if offen is None or self._datei_waehlen is None:
            return
        pfad = self._datei_waehlen(offen["fenster"].hwnd)
        if not pfad:
            return
        try:
            import io
            from PIL import Image
            with Image.open(pfad) as roh:
                roh = roh.convert("RGBA")
                roh.thumbnail((1600, 1600))
                puffer = io.BytesIO()
                roh.save(puffer, format="PNG")
                breite, hoehe = roh.size
            offen["editor"].bild_einfuegen(puffer.getvalue(), breite, hoehe)
        except Exception as fehler:
            self._setze_status(self.status, f"Bild nicht lesbar: {type(fehler).__name__}")

    def _zeichnen_kontext_menue(self, px: int, py: int) -> None:
        """Rechtsklick in der Zeichenfläche: Menü für das Objekt unter dem Zeiger, sonst für die Voreinstellungen."""
        offen = self.editor_offen
        if offen is None:
            return
        editor = offen["editor"]
        links, oben, _r, _u = offen["fenster"].rechteck()
        eintraege = editor.kontext_eintraege()
        menue_eintraege: list = []
        for i, e in enumerate(eintraege):
            if e is None:
                menue_eintraege.append(None)
                continue
            schluessel, text, haken = e
            flags = menue.ABGEBLENDET if schluessel is None else (menue.GEHAKT if haken else 0)
            menue_eintraege.append((KONTEXT_ID + i if schluessel is not None else 0, text, flags))
        gewaehlt = self._menue_anzeigen(offen["fenster"].hwnd, menue_eintraege, links + px, oben + py)
        if gewaehlt >= KONTEXT_ID and gewaehlt - KONTEXT_ID < len(eintraege):
            e = eintraege[gewaehlt - KONTEXT_ID]
            if e is not None and e[0] is not None:
                editor.kontext_ausfuehren(e[0])

    def _zeichnen_ziel_menue(self, x: int, y: int) -> None:
        """„Ziel …“ wie beim Fensterscanner: der ganze Desktop oder eines der offenen Fenster; dort wird gezeichnet."""
        offen = self.editor_offen
        if offen is None:
            return
        fenster = self._fenster_liste()
        eintraege: list = [(0, "Hier zeichnen …", menue.ABGEBLENDET), None, (ZIEL_ID, "Ganzer Desktop", 0), None]
        eintraege += [(ZIEL_ID + 1 + i, f"{titel[:60]}  ({ntpath.basename(pfad)})", 0) for i, (_h, titel, pfad) in enumerate(fenster[:60])]
        if not fenster:
            eintraege.append((0, "Keine Fenster gefunden", menue.ABGEBLENDET))
        gewaehlt = self._menue_anzeigen(offen["leiste"].hwnd, eintraege, x, y)
        tid = offen["tid"]
        if gewaehlt == ZIEL_ID:
            self.zeichnen_oeffnen(tid, ziel="desktop")
        elif ZIEL_ID < gewaehlt <= ZIEL_ID + len(fenster):
            hwnd, _titel, pfad = fenster[gewaehlt - ZIEL_ID - 1]
            self.zeichnen_oeffnen(tid, ziel=ziele.fenster_schluessel(self.ort, hwnd), programm=ntpath.basename(pfad or "").lower() or None)

    def _agenten_im_ziel(self, schluessel: str) -> list[tuple[str, str]]:
        drin = [(a.terminal_id, a.name) for a in self.agenten.values() if self.ziel_schluessel(a.terminal_id) == schluessel]
        return drin or [(a.terminal_id, a.name) for a in self.agenten.values()]  # noch niemand dort gebunden: alle zur Wahl

    def bild_element_neu(self, tid: str | None = None) -> bool:
        """Raute-Menü „Bild einblenden …“: ein Bild als schwebendes Element (eigenes Fenster) im Gate dieses Agenten, sofort direkt anfassbar."""
        tid = tid or self.gewaehlt
        agent = self.agenten.get(tid) if tid else None
        if agent is None or self._datei_waehlen is None:
            return False
        schluessel = self.ziel_schluessel(tid) or "desktop"
        rect = self._gate_rechteck(schluessel)
        if rect is None:
            self._setze_status(self.status, f"{agent.name}: das gebundene Fenster ist nicht sichtbar, zum Einblenden erst wiederherstellen")
            return False
        pfad = self._datei_waehlen(agent.koerper.raute.hwnd)
        if not pfad:
            return False
        try:
            import io
            from PIL import Image
            from .objekte import Objekt, neue_id
            with Image.open(pfad) as roh:
                roh = roh.convert("RGBA")
                roh.thumbnail((1600, 1600))
                puffer = io.BytesIO()
                roh.save(puffer, format="PNG")
                bb, bh = roh.size
        except Exception as fehler:
            self._setze_status(self.status, f"Bild nicht lesbar: {type(fehler).__name__}")
            return False
        gb, gh = rect[2] - rect[0], rect[3] - rect[1]
        faktor = min(0.4 * gb / max(1, bb), 0.4 * gh / max(1, bh), 1.0)
        b, h = bb * faktor / gb, bh * faktor / gh
        dok = self.arbeit.dokument(schluessel)
        versatz = 0.03 * len([o for o in dok.schwebende()])  # mehrere Bilder liegen nicht exakt übereinander
        mx, my = min(0.5 + versatz, 1 - b / 2), min(0.5 + versatz, 1 - h / 2)
        o = Objekt(neue_id(), "bild", [(mx - b / 2, my - h / 2), (mx + b / 2, my + h / 2)], bild=puffer.getvalue(), bildschirm=True, schwebend=True)
        if dok.hinzufuegen(o) is None:
            return False
        self.arbeit_speichern()
        if self.anzeige is not None:
            self.anzeige.tick()
        self._setze_status(self.status, "Bild eingeblendet: am Kopf verschieben, an den Kanten Größe, Mausrad = Deckkraft, Rechtsklick (mit Bedientaste) = Menü")
        return True

    def bild_element_menue(self, oid: str, schluessel: str, x: int, y: int) -> None:
        """Rechtsklick (mit Bedientaste) auf ein schwebendes Bild: Sichtbar für …, Deckkraft, Ausblenden, Entfernen."""
        dok = self.arbeit.dokumente.get(schluessel)
        o = dok.objekte.get(oid) if dok is not None else None
        if o is None or self.anzeige is None:
            return
        agenten = self._agenten_im_ziel(schluessel)
        eintraege: list = [(0, "Sichtbar für …", menue.ABGEBLENDET), (SICHTBAR_BILDSCHIRM_ID, "Auf meinem Bildschirm (jeder, der den Bereich sieht)", menue.GEHAKT if o.bildschirm else 0)]
        eintraege += [(SICHTBAR_AGENT_ID + i, f"Nur im Bild von {name}", menue.GEHAKT if tid in o.empfaenger else 0) for i, (tid, name) in enumerate(agenten)]
        eintraege += [None] + [(KONTEXT_ID + p, f"Deckkraft {p} %", menue.GEHAKT if o.deckkraft == p else 0) for p in (100, 75, 50, 25)]
        eintraege += [None, (KONTEXT_ID + 1, "Ausblenden", 0), (KONTEXT_ID + 2, "Entfernen", 0)]
        st = self.anzeige._bild_elemente.stand.get(oid) if getattr(self.anzeige, "_bild_elemente", None) else None
        hwnd = st.fenster.hwnd if st is not None else (self.regie.hwnd if self.regie else 0)
        gewaehlt = self._menue_anzeigen(hwnd, eintraege, x, y)
        if gewaehlt == SICHTBAR_BILDSCHIRM_ID:
            dok.aendern([oid], bildschirm=not o.bildschirm)
        for i, (tid, _name) in enumerate(agenten):
            if gewaehlt == SICHTBAR_AGENT_ID + i:
                neu = tuple(e for e in o.empfaenger if e != tid) if tid in o.empfaenger else (*o.empfaenger, tid)
                dok.aendern([oid], empfaenger=neu)
        if gewaehlt in (KONTEXT_ID + p for p in (100, 75, 50, 25)):
            dok.aendern([oid], deckkraft=gewaehlt - KONTEXT_ID)
        elif gewaehlt == KONTEXT_ID + 1:
            dok.aendern([oid], sichtbar=False)
        elif gewaehlt == KONTEXT_ID + 2:
            dok.entfernen([oid])
        self.arbeit_speichern()

    def _zeichnen_sichtbar_menue(self, x: int, y: int) -> None:
        """„Sichtbar für …“: auf dem Bildschirm und/oder nur im Bild einzelner Agenten (R043); gilt für die Auswahl, sonst für neue Objekte."""
        offen = self.editor_offen
        if offen is None:
            return
        editor = offen["editor"]
        bildschirm, empfaenger = editor.empfaenger_stand()
        ziele = "die Auswahl" if editor.auswahl else "neue Objekte"
        agenten = editor._agenten()
        eintraege: list = [(0, f"Sichtbar für … ({ziele})", menue.ABGEBLENDET), None,
                           (SICHTBAR_BILDSCHIRM_ID, "Auf meinem Bildschirm (jeder, der den Bereich sieht)", menue.GEHAKT if bildschirm else 0), None]
        eintraege += [(SICHTBAR_AGENT_ID + i, f"Nur im Bild von {name}", menue.GEHAKT if tid in empfaenger else 0) for i, (tid, name) in enumerate(agenten)]
        if not agenten:
            eintraege.append((0, "Kein Agent in diesem Ziel gebunden", menue.ABGEBLENDET))
        gewaehlt = self._menue_anzeigen(offen["leiste"].hwnd, eintraege, x, y)
        if gewaehlt == SICHTBAR_BILDSCHIRM_ID:
            editor.bildschirm_umschalten()
        for i, (tid, name) in enumerate(agenten):
            if gewaehlt == SICHTBAR_AGENT_ID + i:
                editor.empfaenger_umschalten(tid)

    def ziel_schluessel(self, tid: str) -> str | None:
        """Der Schlüssel des Gates dieses Agenten: das gebundene Fenster oder „desktop“; None ohne Bindung."""
        if self.bilderstrom is None or tid not in self.bilderstrom.ziele:
            return None
        hwnd = self.bilderstrom.ziele[tid].hwnd
        return ziele.fenster_schluessel(self.ort, hwnd) if hwnd is not None else "desktop"

    def komposit_fuer(self, tid: str, gate, ausschnitt):
        """Für den Bilderstrom: die Objekte, die nur dieser Agent in seinem Gate sehen soll (sonst None)."""
        if self._nur_terminal(tid):
            return None
        return self.arbeit.komposit(tid, self.ziel_schluessel(tid), gate, ausschnitt)

    def ziel_loesen(self, tid: str) -> None:
        """Daniel hat im Scanner „Bindung lösen“ gewählt: der Agent sieht wieder den ganzen Desktop, seine Elemente stehen wieder auf dem Desktop."""
        self.ziel_weg_seit.pop(tid, None)
        if self.bilderstrom is not None:
            self.bilderstrom.binden(tid, None)  # Lösen heißt: ganzer Desktop, die Bilder reißen nie ab
        if self.ziel_halter is not None:
            self.ziel_halter.tick()  # kein Fenster-Ziel mehr: Elemente gehen auf den Desktop zurück
        agent = self.agenten.get(tid)
        if agent is not None:
            self._setze_status(self.status, f"{agent.name}: Bindung gelöst, Bilder vom ganzen Desktop")

    def bild_datei_senden(self, tid: str) -> bool:
        """Eine Bilddatei an genau diesen Agenten (Quelle „file“, R038): Daniel wählt sie, die Bridge verkleinert sie und sendet ein Bild."""
        agent = self.agenten.get(tid)
        if agent is None or self._datei_waehlen is None:
            return False
        if self.eingaben_gesperrt or self._nur_terminal(tid):
            self._setze_status(self.status, f"{agent.name}: " + ("Not-Aus aktiv" if self.eingaben_gesperrt else "nur Terminal, keine Bilder"))
            return False
        pfad = self._datei_waehlen(agent.koerper.raute.hwnd)
        if not pfad:
            return False
        try:
            daten, breite, hoehe = self._datei_kodieren(pfad)
        except Exception as fehler:
            self._setze_status(self.status, f"Bilddatei nicht lesbar: {type(fehler).__name__}")
            return False
        ok = self._senden("frame", {"mime": "image/jpeg", "data": base64.b64encode(daten).decode(), "source": "file",
                                    "captured_at_ms": int(time.time() * 1000), "width": breite, "height": hoehe, "terminal_id": tid})
        self._setze_status(self.status, f"Bild an {agent.name} gesendet ({breite}×{hoehe})" if ok else "Bild nicht gesendet")
        return ok

    # ---- Bildfolge (R038) ---------------------------------------------------------------------------------------------
    def _folge_bild_senden(self, tid: str, pfad: str) -> bool:
        """Aus dem Folge-Faden: ein Bild der Folge (Not-Aus und „nur Terminal“ sperren; ein unlesbares Bild wird gezählt und übersprungen)."""
        if self.eingaben_gesperrt or self._nur_terminal(tid) or self.sender is None or self.status != "verbunden":
            return False
        try:
            daten, breite, hoehe = self._datei_kodieren(pfad)
        except Exception:
            return False
        return self.sender.senden("frame", {"mime": "image/jpeg", "data": base64.b64encode(daten).decode(), "source": "file",
                                            "captured_at_ms": int(time.time() * 1000), "width": breite, "height": hoehe, "terminal_id": tid})

    def _folge_beendet(self, tid: str) -> None:
        agent = self.agenten.get(tid)
        folge = self.bildfolgen.folgen.get(tid)
        if agent is not None and folge is not None and not folge.laeuft:
            self._setze_status(self.status, f"Bildfolge für {agent.name} zu Ende ({folge.index}/{len(folge.pfade)} gesendet, {folge.fehler} Fehler)")

    def bildfolge_menue(self, tid: str, x: int, y: int) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        folge = self.bildfolgen.folgen.get(tid)
        eintraege: list = [(0, f"Bildfolge für {agent.name}: {self.bildfolgen.text(tid)}", menue.ABGEBLENDET), None,
                           (FOLGE_START_ID, "Bilder eines Ordners nacheinander senden …", 0)]
        if folge is not None and folge.laeuft:
            eintraege += [(FOLGE_PAUSE_ID, "Fortsetzen" if folge.pausiert else "Pausieren", 0), (FOLGE_STOP_ID, "Stoppen", 0)]
        gewaehlt = self._menue_anzeigen(agent.koerper.raute.hwnd, eintraege, x, y)
        if gewaehlt == FOLGE_START_ID:
            self.bildfolge_starten(tid)
        elif gewaehlt == FOLGE_PAUSE_ID and folge is not None:
            self.bildfolgen.pausieren(tid, not folge.pausiert)
        elif gewaehlt == FOLGE_STOP_ID:
            self.bildfolgen.stoppen(tid)
            self._setze_status(self.status, f"Bildfolge für {agent.name} gestoppt")

    def bildfolge_starten(self, tid: str) -> bool:
        """Daniel wählt ein Bild; alle Bilder dieses Ordners (Namensreihenfolge, höchstens 500) gehen nacheinander an den Agenten."""
        agent = self.agenten.get(tid)
        if agent is None or self._datei_waehlen is None:
            return False
        if self.eingaben_gesperrt or self._nur_terminal(tid):
            self._setze_status(self.status, f"{agent.name}: " + ("Not-Aus aktiv" if self.eingaben_gesperrt else "nur Terminal, keine Bilder"))
            return False
        pfad = self._datei_waehlen(agent.koerper.raute.hwnd)
        if not pfad:
            return False
        import os
        pfade = bilder_im_ordner(os.path.dirname(pfad))
        if pfad in pfade:
            pfade = pfade[pfade.index(pfad):]  # ab dem gewählten Bild
        if not self.bildfolgen.starten(tid, pfade):
            self._setze_status(self.status, "Im Ordner liegen keine Bilder")
            return False
        self._setze_status(self.status, f"Bildfolge für {agent.name} gestartet ({len(pfade)} Bilder)")
        return True

    # ---- Plätze tauschen (R020) ---------------------------------------------------------------------------------------
    def plaetze_menue(self, tid: str, x: int, y: int) -> None:
        agent = self.agenten.get(tid)
        if agent is None:
            return
        andere = [(i, a) for i, a in enumerate(self.agenten.values()) if a.terminal_id != tid]
        eintraege: list = [(0, f"Terminal-Platz von {agent.name} tauschen mit:", menue.ABGEBLENDET), None]
        eintraege += [(PLATZ_TAUSCH_ID + i, a.name, 0) for i, a in andere] or [(0, "Kein anderer Agent gestartet", menue.ABGEBLENDET)]
        gewaehlt = self._menue_anzeigen(agent.koerper.raute.hwnd, eintraege, x, y)
        for i, a in andere:
            if gewaehlt == PLATZ_TAUSCH_ID + i:
                self.plaetze_tauschen(tid, a.terminal_id)

    def plaetze_tauschen(self, tid_a: str, tid_b: str) -> bool:
        """Zwei Terminalansichten tauschen Ort und Größe (R020). Jede Sitzung behält ihr Terminal, ihren Namen und ihre Farbe; es ändert sich nur, wo sie stehen."""
        a, b = self.agenten.get(tid_a), self.agenten.get(tid_b)
        if a is None or b is None or tid_a == tid_b:
            return False
        ta, tb = a.koerper.terminal, b.koerper.terminal
        (al, ao, ar, au), (bl, bo, br, bu) = ta.rechteck(), tb.rechteck()
        ta.verschiebe(bl, bo, br - bl, bu - bo)
        tb.verschiebe(al, ao, ar - al, au - ao)
        self._setze_status(self.status, f"Terminal-Plätze von {a.name} und {b.name} getauscht")
        self.einstellungen_sichern()
        return True

    def menue_freigabe_umschalten(self) -> None:
        """Daniel allein schaltet hier ein, ob Agenten die Menüs der Bridge bedienen dürfen (Aktion „menue“: nur Einträge der Erlaubnisliste, nie Beenden, Not-Aus, Pausieren, Hände, Profil).
        Dieses Menü ist selbst nie für Agenten bedienbar (es hat keine Art im Register). Nach jedem Start ist die Freigabe aus."""
        engine = self.haende_engine
        if engine is None:
            return
        engine.menue_freigabe = not getattr(engine, "menue_freigabe", False)
        zustand = "an" if engine.menue_freigabe else "aus"
        self.log(f"menue_freigabe {zustand} (Daniel, Regie-Menü)")
        self._setze_status(self.status, "Agenten dürfen erlaubte Einträge der Bridge-Menüs bedienen" if engine.menue_freigabe else "Agenten können keine Bridge-Menüs bedienen")

    def bridge_im_bild_umschalten(self) -> None:
        """Die Fenster der Bridge aus der Aufnahme ausnehmen (die Agenten sehen dann nur dein Programm, aber auch keine Banner mit deinen Worten)
        oder wieder zeigen. Beobachtung (Bild) und sichtbare Einblendung sind damit getrennt schaltbar (R039)."""
        from . import fenster as fenster_modul

        self.bridge_im_bild = not self.bridge_im_bild
        angenommen = fenster_modul.bild_ausnahme_setzen(not self.bridge_im_bild)
        if not self.bridge_im_bild and angenommen == 0 and self._fenster_art:
            self.bridge_im_bild = True
            fenster_modul.bild_ausnahme_setzen(False)
            self._setze_status(self.status, "Windows nimmt die Ausnahme nicht an (braucht Windows 10 ab Version 2004)")
            return
        self._setze_status(self.status, "Bridge-Fenster sind im Bild der Agenten" if self.bridge_im_bild
                           else "Bridge-Fenster sind aus dem Bild der Agenten ausgenommen")
        self.einstellungen_sichern()

    def bild_senden(self, tid: str, bindung: Bindung) -> None:
        """Das gebundene Ziel als Bild an genau diesen Agenten (R120); danach laufend (Bilderstrom)."""
        if self.eingaben_gesperrt:
            return
        self._strom_binden(tid, bindung)
        self._arbeit_zuordnen(tid, bindung)
        self._orte_anwenden(tid)  # Elemente, die im Zielfenster stehen sollen, kommen jetzt hinein
        if self._nur_terminal(tid):
            return  # „nur Terminal“: der Agent bekommt keine Bilder
        frame = bindung.frame
        desktop = bindung.snapshot.items[0].rect or (0, 0, frame.width, frame.height)
        ziel = bindung.item.rect or desktop
        ausschnitt = bild.ausschnitt_im_frame(ziel, (desktop[0], desktop[1]), frame.width, frame.height)
        if ausschnitt is None:
            self._setze_status(self.status, "gebundenes Ziel liegt außerhalb der Aufnahme")
            return
        kompo = self.arbeit.komposit(tid, self.ziel_schluessel(tid), ziel,
                                     (ausschnitt[0] + desktop[0], ausschnitt[1] + desktop[1], ausschnitt[2] + desktop[0], ausschnitt[3] + desktop[1]))
        if kompo is not None:
            daten, breite, hoehe = self._bild_kodieren(frame.bgra_bytes, frame.width, frame.height, ausschnitt, nachbearbeiten=kompo.anwenden)
        else:
            daten, breite, hoehe = self._bild_kodieren(frame.bgra_bytes, frame.width, frame.height, ausschnitt)
        self._senden("frame", {"mime": "image/jpeg", "data": base64.b64encode(daten).decode(), "source": "capture",
                               "captured_at_ms": frame.captured_at_ms, "width": breite, "height": hoehe,
                               "terminal_id": tid})

    def bericht(self) -> dict:
        """Der beobachtbare Zustand als Daten (für den Wine-Lauf und die Übergabe-Evidence)."""
        return {
            "status": self.status, "hinweis": self.hinweis, "not_aus": self.not_aus.aktiv,
            "eingaben_gesperrt": self.eingaben_gesperrt,
            "chat_verlauf": [list(eintrag) for eintrag in self.chat.verlauf] if self.chat is not None else [],
            "startliste": sorted(self.startliste),
            "agenten": [{
                "terminal_id": a.terminal_id, "start_id": a.start_id, "name": a.name, "zustand": a.zustand,
                "hotkey": a.hotkey, "ausgabe_seq": a.ausgabe_seq, "luecken": a.luecken,
                "raute_status": a.koerper.raute.status,
                "raute_letzte_nachricht": a.koerper.raute.letzte_nachricht,
                "banner_da": a.koerper.banner is not None, "ticker_da": a.koerper.ticker is not None,
                "bilderstrom": (self.bilderstrom.ziele[a.terminal_id].gesendet
                                if self.bilderstrom is not None and a.terminal_id in self.bilderstrom.ziele else None),
                "terminal_zustand": a.koerper.terminal.zustand,
                "terminal_ziel": a.koerper.terminal.ziel_text,
                "terminal_text": [z.rstrip() for z in a.koerper.terminal.text_aller_zeilen() if z.strip()],
            } for a in self.agenten.values()],
        }

    def beenden(self) -> None:
        """Bridge beenden: im GUI-Thread und nicht mitten in einem Mausklick auf ein Fenster, das dabei zerstört wird."""
        if self.notbremse is not None:  # hängt ein Schritt (auch im GUI-Thread), endet der Prozess trotzdem
            bremse = threading.Timer(NOTBREMSE_S, self.notbremse)
            bremse.daemon = True
            bremse.start()
        self.gui.post(self._abbauen)

    def _abbauen(self) -> None:
        """Erst die Fenster (sofort weg), dann alles, was warten kann. Jeder Schritt für sich und im Log: ein Fehler
        oder ein langsamer Schritt darf das Beenden nie aufhalten (sonst bliebe die Bridge halb offen)."""
        def versuche(wo: str, aufruf: Callable[[], object]) -> None:
            self.log(f"beenden: {wo}")
            try:
                aufruf()
            except Exception as fehler:
                self.abbau_fehler.append(f"{wo}: {fehler!r}"[:200])
                self.log(f"beenden: {wo} FEHLER {fehler!r}"[:300])
                if self.fehler_haken is not None:
                    self.fehler_haken(f"beenden/{wo}", fehler)

        self.log("beenden: Anfang")
        self._ziel_stop.set()
        versuche("zeichnen", self.zeichnen_schliessen)  # Objekte speichern, Zeichenfenster zu
        versuche("einstellungen", self.einstellungen_sichern)  # Orte merken, solange die Fenster noch stehen
        if self.anzeige is not None:
            versuche("anzeige", self.anzeige.stoppen)
            versuche("anzeige-fenster", self.anzeige.schliessen)
        self.bildfolgen.alle_stoppen()
        if self.sichtbarkeit is not None:
            versuche("sichtbarkeit", self.sichtbarkeit.stoppen)
        if self.durchklick is not None:
            versuche("durchklick", self.durchklick.stoppen)
        if self.bilderstrom is not None:
            versuche("bilderstrom", self.bilderstrom.stoppen)
        for agent in list(self.agenten.values()):
            versuche(f"koerper {agent.name}", agent.koerper.schliessen)
        self.agenten.clear()
        for name in ("regie", "chat"):
            fenster = getattr(self, name)
            setattr(self, name, None)
            if fenster is not None:
                versuche(name, fenster.schliessen)
        if self.medien is not None:
            versuche("medien", self.medien.alles_stoppen)
        if self.sender is not None:
            versuche("sender", self.sender.stop)
        if self.runtime is not None:
            versuche("runtime", self.runtime.stop)
        self.log("beenden: Ende")
        self.gui.beenden(0)
