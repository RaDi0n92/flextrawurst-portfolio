"""Mikrofon-Anbindung des Körpers (G07, erste Fassung für G02/BE03): echte Audioblöcke, Stummschaltung und Push-to-talk.

Wie bei `kamera.py` (V04-MEDIEN-ATTRAPPE) kein bloßer Ein/Aus-Zustand: der Stream liefert echte PCM-Blöcke mit
Alter, Herkunft und Sequenznummer. `sounddevice` wird lazy importiert — in dieser Container-Umgebung fehlt die
native PortAudio-Bibliothek, wodurch schon der Import von `sounddevice` mit `OSError` scheitert (kein `cv2`-artiger
sauberer `ImportError`); das Modul selbst bleibt davon unberührt importierbar. Push-to-talk ist der erste Modus
(R041); VAD ist noch nicht gebaut und wird nicht vorgetäuscht. Kein Dauerstream ohne `einschalten()` (R045).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol

Modus = Literal["push_to_talk", "offen"]


class MikrofonFehler(RuntimeError):
    """Ein erwarteter, benannter Fehlschlag (PortAudio/sounddevice fehlt, kein Gerät) — kein Programmierfehler."""


@dataclass(frozen=True)
class AudioBlock:
    sequenz: int
    aufgenommen_ms: int
    abtastrate: int
    kanaele: int
    pcm: bytes
    quelle: str


EingangsCallback = Callable[[bytes, object], None]


class MikrofonQuelle(Protocol):
    """Das injizierbare Backend. `SounddeviceMikrofonQuelle` ist die echte Implementierung."""

    def oeffnen(self, geraet: int | str | None, abtastrate: int, kanaele: int, eingang: EingangsCallback) -> None: ...
    def schliessen(self) -> None: ...


def eingabegeraete(sd=None) -> list[tuple[int, str]]:
    """Die Eingabegeräte als (Index, Name), je Name einmal und möglichst über MME (sonst erscheint jedes Gerät je Audio-Schnittstelle).
    Leere Liste, wenn sounddevice fehlt oder nichts findet."""
    try:
        if sd is None:
            import sounddevice as sd
        geraete = sd.query_devices()
        schnittstellen = sd.query_hostapis()
    except Exception:
        return []
    bevorzugt = next((i for i, h in enumerate(schnittstellen) if "MME" in str(h.get("name", ""))), None)
    ergebnis: list[tuple[int, str]] = []
    gesehen: set[str] = set()
    for index, geraet in enumerate(geraete):
        if geraet.get("max_input_channels", 0) <= 0:
            continue
        if bevorzugt is not None and geraet.get("hostapi") != bevorzugt:
            continue
        name = str(geraet.get("name", f"Gerät {index}"))
        if name not in gesehen:
            gesehen.add(name)
            ergebnis.append((index, name))
    return ergebnis


def geraet_index(name: str | None, sd=None) -> int | str | None:
    """Der Index des Eingabegeräts mit diesem Namen (oder `None` = Standardgerät). Ist der Name nicht (mehr) da, bleibt er als Text stehen,
    damit das Öffnen mit einer klaren Fehlermeldung scheitert statt stillschweigend ein anderes Gerät zu nehmen."""
    if not name:
        return None
    for index, geraetename in eingabegeraete(sd):
        if geraetename == name:
            return index
    return name


class SounddeviceMikrofonQuelle:
    """Echtes Backend über `sounddevice.RawInputStream`. `sounddevice` wird erst bei `oeffnen()` importiert."""

    def __init__(self) -> None:
        self._strom = None

    def oeffnen(self, geraet: int | str | None, abtastrate: int, kanaele: int, eingang: EingangsCallback) -> None:
        try:
            import sounddevice as sd
        except (ImportError, OSError) as fehler:
            # OSError: z.B. "PortAudio library not found" — sounddevice scheitert unter Linux schon beim Import,
            # wenn die native Bibliothek fehlt, nicht erst beim Oeffnen eines Geraets.
            raise MikrofonFehler("sounddevice_nicht_verfuegbar") from fehler

        def _weiterleiten(indata, frames, zeit, status) -> None:
            eingang(bytes(indata), status)

        try:
            self._strom = sd.RawInputStream(device=geraet, samplerate=abtastrate, channels=kanaele, dtype="int16",
                                            callback=_weiterleiten)
            self._strom.start()
        except Exception as fehler:  # sd.PortAudioError und Verwandte: kein Geraet, falsche Abtastrate, belegt
            self._strom = None
            raise MikrofonFehler(f"mikrofon_geraet_fehlgeschlagen:{fehler}") from fehler

    def schliessen(self) -> None:
        if self._strom is not None:
            self._strom.stop()
            self._strom.close()
            self._strom = None


class Mikrofon:
    """Zustand, Stummschaltung, Push-to-talk und Sequenzierung eines Mikrofons (R041)."""

    def __init__(self, *, quelle: MikrofonQuelle | None = None, jetzt_ms: Callable[[], int] | None = None,
                 block_empfangen: Callable[[AudioBlock], None] | None = None) -> None:
        self._quelle = quelle if quelle is not None else SounddeviceMikrofonQuelle()
        self._jetzt_ms = jetzt_ms or (lambda: int(time.monotonic() * 1000))
        self._block_empfangen = block_empfangen or (lambda block: None)
        self.aktiv = False
        self.stumm = False
        self.sprechtaste_gedrueckt = False
        self.modus: Modus = "push_to_talk"
        self.letzter_fehler: str | None = None
        self._geraet: int | str | None = None
        self._abtastrate = 0
        self._kanaele = 0
        self._sequenz = 0

    def einschalten(self, geraet: int | str | None = None, *, abtastrate: int = 16000, kanaele: int = 1) -> bool:
        if self.aktiv:
            return True
        try:
            self._quelle.oeffnen(geraet, abtastrate, kanaele, self._eingang)
        except MikrofonFehler as fehler:
            self.letzter_fehler = str(fehler)
            return False
        self.aktiv = True
        self.letzter_fehler = None
        self._geraet, self._abtastrate, self._kanaele = geraet, abtastrate, kanaele
        self._sequenz = 0
        return True

    def ausschalten(self) -> None:
        if self.aktiv:
            self._quelle.schliessen()
        self.aktiv = False

    def stummschalten(self, stumm: bool = True) -> None:
        self.stumm = stumm

    def modus_setzen(self, modus: Modus) -> None:
        self.modus = modus

    def sprechtaste(self, gedrueckt: bool) -> None:
        self.sprechtaste_gedrueckt = gedrueckt

    def _darf_senden(self) -> bool:
        if not self.aktiv or self.stumm:
            return False
        if self.modus == "push_to_talk":
            return self.sprechtaste_gedrueckt
        return True

    def _eingang(self, pcm: bytes, status: object) -> None:
        """Callback des Streams: läuft im Audio-Thread der Quelle; Aufrufer entscheiden selbst über Thread-Wechsel."""
        if status:
            self.letzter_fehler = str(status)
        if not self._darf_senden():
            return
        self._sequenz += 1
        block = AudioBlock(sequenz=self._sequenz, aufgenommen_ms=self._jetzt_ms(), abtastrate=self._abtastrate,
                            kanaele=self._kanaele, pcm=pcm, quelle=f"sounddevice:{self._geraet}")
        self._block_empfangen(block)
