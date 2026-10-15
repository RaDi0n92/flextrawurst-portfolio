"""Kamera und Mikrofon je Agent zuschalten (R040, R041, R045): echte Geräte, nichts läuft ohne ausdrückliches Einschalten.

* Bei der Kamera liest ein Lesefaden je eingeschalteter Kamera im `takt_s`-Abstand einen echten Frame und reicht ihn weiter
  (sparsam, kein Dauerstrom, R045). Ohne Gerät bleibt der Zustand „fehler“ mit dem benannten Grund.
* Beim Mikrofon werden echte Audioblöcke erfasst und zu einzelnen Äußerungen geschnitten (`sprachaufnahme.py`): im Standard nur, solange
  die Sprechtaste gehalten wird, oder bei offenem Mikrofon per Energieerkennung. Jede Äußerung geht als WAV an `audio_weitergeben`
  (Relay → VPS → Spracherkennung). Ohne Rückruf bleibt `audio_uebertragung` False und nichts verlässt den Rechner.
* Der Not-Aus stoppt alles sofort; eine Äußerung, die dabei fertig wird, wird verworfen.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from .kamera import Kamera, KameraFrame
from .mikrofon import AudioBlock, Mikrofon, geraet_index
from .notaus import NotAus
from .sprachaufnahme import MODUS_SPRECHTASTE, Segmentierer, wav_bytes
from .tastenkombi import taste_gehalten


@dataclass
class AgentMedien:
    kamera: Kamera
    mikrofon: Mikrofon
    bloecke: int = 0
    segment: Segmentierer | None = None
    startet: bool = False  # die Kamera wird gerade geöffnet
    aeusserungen: int = 0
    frames_gesendet: int = 0
    faden: threading.Thread | None = None
    stopp: threading.Event = field(default_factory=threading.Event)


STANDARD_SPRECHTASTE = 0x77  # F8
VORSCHAU_S = 0.2  # Abstand der Bilder im Selbstbild-Fenster (zum Agenten geht weiter nur jedes `takt_s`-te)


class Medien:
    def __init__(self, *, frame_weitergeben: Callable[[str, KameraFrame], None], not_aus: NotAus,
                 melden: Callable[[], None] = lambda: None, takt_s: float = 1.0,
                 kamera_bauen: Callable[[], Kamera] = Kamera, mikrofon_bauen: Callable[..., Mikrofon] = Mikrofon,
                 audio_weitergeben: Callable[[str, bytes, int], None] | None = None,
                 taste: Callable[[int], bool] = taste_gehalten):
        self._weitergeben, self._melden, self._takt_s = frame_weitergeben, melden, takt_s
        self._vorschau: Callable[[str, KameraFrame], None] | None = None  # jedes gelesene Bild, für Daniels Selbstbild-Fenster
        self._audio = audio_weitergeben
        self._taste = taste
        self.modus = MODUS_SPRECHTASTE  # oder "offen"
        self.sprechtaste_vk = STANDARD_SPRECHTASTE
        self.mik_geraet: str | None = None  # Name des Eingabegeräts; None = Standardgerät von Windows
        self._kamera_bauen, self._mikrofon_bauen = kamera_bauen, mikrofon_bauen
        self.not_aus = not_aus
        self._agenten: dict[str, AgentMedien] = {}
        not_aus.bei_ausloesen(lambda grund: self.alles_stoppen())

    def fuer(self, agent_id: str) -> AgentMedien:
        eintrag = self._agenten.get(agent_id)
        if eintrag is None:
            eintrag = AgentMedien(self._kamera_bauen(), None)  # type: ignore[arg-type]
            eintrag.segment = Segmentierer(lambda pcm, dauer_ms, a=agent_id: self._aeusserung(a, pcm, dauer_ms),
                                           modus=lambda: self.modus,
                                           sprechtaste_gehalten=lambda: self._taste(self.sprechtaste_vk))
            eintrag.mikrofon = self._mikrofon_bauen(block_empfangen=lambda block, e=eintrag: self._block(e, block))
            self._agenten[agent_id] = eintrag
        return eintrag

    @property
    def audio_uebertragung(self) -> bool:
        return self._audio is not None

    def audio_verbinden(self, audio_weitergeben: Callable[[str, bytes, int], None]) -> None:
        self._audio = audio_weitergeben

    @staticmethod
    def _block(eintrag: AgentMedien, block: AudioBlock) -> None:
        eintrag.bloecke += 1
        if eintrag.segment is not None:
            eintrag.segment.block(block.pcm, block.abtastrate)

    def _aeusserung(self, agent_id: str, pcm: bytes, dauer_ms: int) -> None:
        if self._audio is None or self.not_aus.aktiv:
            return
        self._agenten[agent_id].aeusserungen += 1
        self._audio(agent_id, wav_bytes(pcm), dauer_ms)

    # ---- Kamera ----------------------------------------------------------------------------------------------------
    def kamera_umschalten(self, agent_id: str) -> str:
        """Ein- oder ausschalten. Das Öffnen geschieht im Kamera-Faden (es kann nativ 10 bis 20 s dauern); bis dahin ist der Zustand „startet“."""
        eintrag = self.fuer(agent_id)
        if eintrag.kamera.aktiv or eintrag.startet:
            self._kamera_stoppen(eintrag)
        elif not self.not_aus.aktiv:
            eintrag.stopp.clear()
            eintrag.startet = True
            eintrag.faden = threading.Thread(target=self._kamera_lauf, args=(agent_id, eintrag), daemon=True,
                                             name=f"kamera-{agent_id}")
            eintrag.faden.start()
        self._melden()
        return self.kamera_zustand(agent_id)

    def _kamera_lauf(self, agent_id: str, eintrag: AgentMedien) -> None:
        try:
            geoeffnet = eintrag.kamera.einschalten()
        finally:
            eintrag.startet = False
        if geoeffnet and (eintrag.stopp.is_set() or self.not_aus.aktiv):
            eintrag.kamera.ausschalten()  # in der Zwischenzeit ausgeschaltet oder Not-Aus: das gerade geöffnete Gerät gleich wieder zu
            geoeffnet = False
        self._melden()
        if geoeffnet:
            self._lesen(agent_id, eintrag)

    def _lesen(self, agent_id: str, eintrag: AgentMedien) -> None:
        letzter_versand = None
        while not eintrag.stopp.is_set() and not self.not_aus.aktiv:
            frame = eintrag.kamera.frame_lesen()
            if frame is not None:
                if self._vorschau is not None:
                    self._vorschau(agent_id, frame)
                jetzt = time.monotonic()
                if letzter_versand is None or jetzt - letzter_versand >= self._takt_s - 0.01:
                    letzter_versand = jetzt
                    self._weitergeben(agent_id, frame)
                    eintrag.frames_gesendet += 1
            schritt = min(self._takt_s, VORSCHAU_S) if self._vorschau is not None else self._takt_s
            if eintrag.stopp.wait(schritt):
                break

    def _kamera_stoppen(self, eintrag: AgentMedien) -> None:
        eintrag.stopp.set()
        if eintrag.faden is not None and eintrag.faden is not threading.current_thread():
            eintrag.faden.join(timeout=3.0)
        eintrag.faden = None
        eintrag.kamera.ausschalten()

    def kamera_zustand(self, agent_id: str) -> str:
        eintrag = self.fuer(agent_id)
        kamera = eintrag.kamera
        if eintrag.startet:
            return "startet"
        return "ein" if kamera.aktiv else ("fehler" if kamera.letzter_fehler else "aus")

    # ---- Mikrofon --------------------------------------------------------------------------------------------------
    def mikrofon_umschalten(self, agent_id: str) -> str:
        eintrag = self.fuer(agent_id)
        if eintrag.mikrofon.aktiv:
            eintrag.mikrofon.ausschalten()
            eintrag.segment.zuruecksetzen()
        elif not self.not_aus.aktiv:
            eintrag.mikrofon.modus_setzen("offen")  # ausdrückliches Einschalten durch Daniel
            eintrag.mikrofon.einschalten(geraet_index(self.mik_geraet))
        self._melden()
        return self.mikrofon_zustand(agent_id)

    def mikrofon_zustand(self, agent_id: str) -> str:
        mikrofon = self.fuer(agent_id).mikrofon
        return "ein" if mikrofon.aktiv else ("fehler" if mikrofon.letzter_fehler else "aus")

    def fehlertext(self, agent_id: str) -> str:
        eintrag = self.fuer(agent_id)
        teile = []
        if eintrag.kamera.letzter_fehler and not eintrag.kamera.aktiv:
            teile.append(f"Kamerafehler {eintrag.kamera.letzter_fehler}")
        if eintrag.mikrofon.letzter_fehler and not eintrag.mikrofon.aktiv:
            teile.append(f"Mikrofonfehler {eintrag.mikrofon.letzter_fehler}")
        return "; ".join(teile)

    # ---- Stoppen ---------------------------------------------------------------------------------------------------
    def stoppen(self, agent_id: str) -> None:
        eintrag = self._agenten.get(agent_id)
        if eintrag is not None:
            self._kamera_stoppen(eintrag)
            eintrag.mikrofon.ausschalten()
            eintrag.segment.zuruecksetzen()

    def alles_stoppen(self) -> None:
        for agent_id in list(self._agenten):
            self.stoppen(agent_id)
        self._melden()
