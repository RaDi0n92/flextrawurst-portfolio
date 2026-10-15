"""Aus dem Mikrofonstrom einzelne Äußerungen schneiden (für die Spracherkennung auf dem VPS).

Zwei Betriebsarten:
* `sprechtaste` (Standard, datenschutzfreundlich): aufgenommen wird nur, solange die Sprechtaste gehalten wird.
* `offen`: eine einfache Energieerkennung schneidet Äußerungen aus dem laufenden Strom (alles, was das Mikrofon hört, wird erkannt und gesendet).
Jede fertige Äußerung kommt als 16-kHz-Mono-PCM zurück; `wav_bytes` verpackt sie für das Relay.
"""

from __future__ import annotations

import array
import struct
from collections.abc import Callable

RATE = 16_000
BYTES_PRO_SEKUNDE = RATE * 2
MODUS_SPRECHTASTE, MODUS_OFFEN = "sprechtaste", "offen"
STANDARD_SCHWELLE = 500.0  # mittlere Amplitude (von 32768), ab der „Sprache“ beginnt
MIN_S, MAX_S, NACHLAUF_S, VORLAUF_S = 0.4, 28.0, 0.8, 0.3


def wav_bytes(pcm: bytes, rate: int = RATE, kanaele: int = 1) -> bytes:
    """Ein WAV mit 44-Byte-Kopf (PCM, 16 Bit)."""
    return (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, kanaele, rate, rate * kanaele * 2,
                                                                                       kanaele * 2, 16) + b"data" + struct.pack("<I", len(pcm)) + pcm)


def mittlere_amplitude(pcm: bytes) -> float:
    if len(pcm) < 2:
        return 0.0
    werte = array.array("h")
    werte.frombytes(pcm[: len(pcm) // 2 * 2])
    return sum(abs(v) for v in werte) / len(werte)


class Segmentierer:
    def __init__(self, fertig: Callable[[bytes, int], None], *, modus: Callable[[], str] = lambda: MODUS_SPRECHTASTE,
                 sprechtaste_gehalten: Callable[[], bool] = lambda: False, schwelle: float = STANDARD_SCHWELLE,
                 rate: int = RATE):
        self._fertig, self._modus, self._taste = fertig, modus, sprechtaste_gehalten
        self.schwelle, self._rate = schwelle, rate
        self._puffer = bytearray()
        self._vorlauf = bytearray()
        self._sprechend = False
        self._stille_s = 0.0
        self._laut_bloecke = 0

    def _sekunden(self, daten: bytes) -> float:
        return len(daten) / (self._rate * 2)

    def block(self, pcm: bytes, rate: int | None = None) -> None:
        if rate is not None and rate != self._rate:
            return  # nur 16 kHz wird erkannt; andere Raten werden nicht still falsch behandelt
        if self._modus() == MODUS_OFFEN:
            self._offen(pcm)
        else:
            self._taste_halten(pcm)

    # ---- Sprechtaste -----------------------------------------------------------------------------------------------
    def _taste_halten(self, pcm: bytes) -> None:
        if self._taste():
            self._puffer += pcm
            self._sprechend = True
            if self._sekunden(self._puffer) >= MAX_S:
                self._abschliessen()
                self._sprechend = True  # Taste noch gehalten: die nächste Äußerung beginnt sofort
        elif self._sprechend:
            self._abschliessen()

    # ---- Offenes Mikrofon ------------------------------------------------------------------------------------------
    def _offen(self, pcm: bytes) -> None:
        laut = mittlere_amplitude(pcm) >= self.schwelle
        dauer = self._sekunden(pcm)
        if not self._sprechend:
            self._vorlauf += pcm
            self._vorlauf = self._vorlauf[-int(VORLAUF_S * self._rate * 2):]
            self._laut_bloecke = self._laut_bloecke + 1 if laut else 0
            if self._laut_bloecke >= 2:  # zwei laute Blöcke hintereinander: Sprache beginnt
                self._puffer = bytearray(self._vorlauf)
                self._sprechend, self._stille_s = True, 0.0
            return
        self._puffer += pcm
        self._stille_s = 0.0 if laut else self._stille_s + dauer
        if self._stille_s >= NACHLAUF_S or self._sekunden(self._puffer) >= MAX_S:
            self._abschliessen()

    def _abschliessen(self) -> None:
        daten = bytes(self._puffer)
        self._puffer = bytearray()
        self._vorlauf = bytearray()
        self._sprechend, self._stille_s, self._laut_bloecke = False, 0.0, 0
        if self._sekunden(daten) >= MIN_S:
            self._fertig(daten, int(self._sekunden(daten) * 1000))

    def zuruecksetzen(self) -> None:
        """Mikrofon aus: nichts Angefangenes wird mehr gesendet."""
        self._puffer = bytearray()
        self._vorlauf = bytearray()
        self._sprechend, self._stille_s, self._laut_bloecke = False, 0.0, 0
