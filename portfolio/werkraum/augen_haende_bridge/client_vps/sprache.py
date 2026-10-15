"""Sprache zu Text auf dem VPS: Daniels Äußerungen (vom Mikrofon der Bridge) werden mit Whisper (faster-whisper, CPU) erkannt.

Läuft in einem eigenen Faden, eine Äußerung nach der anderen, das Modell wird beim Start vorgeladen. Das Audio bleibt im Speicher und wird
nie gespeichert. Einstellbar über die Umgebung des Dienstes: BRIDGE_WHISPER_MODELL (Standard large-v3; kleiner und schneller: medium, small), BRIDGE_WHISPER_SPRACHE (Standard de),
BRIDGE_WHISPER_THREADS (Standard 8), BRIDGE_WHISPER_VOKABULAR (Wörter, die oft falsch erkannt werden, als Hinweis an das Modell).
"""

from __future__ import annotations

import io
import os
import re
import threading
from collections.abc import Callable

STANDARD_MODELL = "large-v3"  # gemessen (PLAN_G02_Y): bei gleicher Laufzeit wie medium die wenigsten Fehler bei Namen und Tastennamen
STANDARD_VOKABULAR = "Claude, Codex, Gemgem, Gemini, Flextrawurst, Raute, Bridge, Terminal, Chat, Strg, Alt, Durchklicken"
# Bekannte Phantom-Sätze, die Whisper bei Stille oder Rauschen erfindet
PHANTOME = ("untertitel", "amara.org", "vielen dank fürs zuschauen", "vielen dank für's zuschauen", "copyright", "www.", "abonniert")
MAX_NO_SPEECH = 0.6
MIN_LOGPROB = -1.2


def ist_phantom(text: str) -> bool:
    klein = text.lower()
    return any(p in klein for p in PHANTOME)


def bereinigen(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class WhisperTranskriber:
    """`faktor` ist einspeisbar (Tests): ruft mit (modellname, threads) ein Objekt mit `.transcribe(datei, **optionen)` auf."""

    def __init__(self, modell: str | None = None, sprache: str | None = None, threads: int | None = None,
                 vokabular: str | None = None, faktor: Callable[[str, int], object] | None = None):
        self.modell = modell or os.environ.get("BRIDGE_WHISPER_MODELL") or STANDARD_MODELL
        self.sprache = sprache or os.environ.get("BRIDGE_WHISPER_SPRACHE") or "de"
        self.threads = threads or int(os.environ.get("BRIDGE_WHISPER_THREADS") or 8)
        self.vokabular = vokabular if vokabular is not None else os.environ.get("BRIDGE_WHISPER_VOKABULAR", STANDARD_VOKABULAR)
        self._faktor = faktor or self._echtes_modell
        self._modell = None
        self._sperre = threading.Lock()
        self.fehler: str | None = None

    @staticmethod
    def _echtes_modell(name: str, threads: int):
        from faster_whisper import WhisperModel

        return WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=threads)

    def vorladen(self) -> bool:
        """Modell laden (dauert einige Sekunden); meldet, ob es geklappt hat."""
        with self._sperre:
            if self._modell is not None:
                return True
            try:
                self._modell = self._faktor(self.modell, self.threads)
                self.fehler = None
                return True
            except Exception as fehler:  # fehlende Bibliothek, fehlendes Modell, kein Speicher
                self.fehler = f"{fehler!r}"[:200]
                return False

    def transkribiere(self, wav: bytes) -> str:
        """Der erkannte Text der Äußerung ('' bei Stille oder wenn nichts Brauchbares erkannt wurde)."""
        if not self.vorladen():
            raise RuntimeError(f"whisper_nicht_verfuegbar: {self.fehler}")
        segmente, _info = self._modell.transcribe(
            io.BytesIO(wav), language=self.sprache, beam_size=5, vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500}, initial_prompt=self.vokabular or None,
            condition_on_previous_text=False)
        teile = []
        for s in segmente:
            if getattr(s, "no_speech_prob", 0.0) > MAX_NO_SPEECH and getattr(s, "avg_logprob", 0.0) < MIN_LOGPROB:
                continue
            teile.append(s.text)
        text = bereinigen(" ".join(teile))
        return "" if ist_phantom(text) else text
