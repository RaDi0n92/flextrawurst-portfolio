#!/usr/bin/env python3
"""
Windows-Diktat — lokale, kostenlose Sprache-zu-Text-Eingabe fuer JEDES Fenster
================================================================================

Haelt die HOTKEY-Taste gedrueckt -> nimmt Mikrofon auf. Loslassen -> transkribiert
lokal (faster-whisper, komplett offline, keine Kosten, kein Account) und tippt den
Text direkt in das Fenster, das gerade den Fokus hat -- egal welches, egal wie viele
andere offen sind. Kein Umweg ueber den VPS, keine Cloud, keine Wartezeit durchs Netz.

Daniels Auftrag (2026-08-13): "gibt es auch ne moeglichkeit wie ich direkt in dein
terminal sprechen kann ... auch wenn ich mehrere offen habe? so in der art wie
voicely oder so?" -- wollte nichts Bezahlpflichtiges (Voicy/Wispr Flow), Win+H
funktionierte bei ihm nicht.

SETUP (einmalig, in einer Windows-Eingabeaufforderung/PowerShell):
    pip install faster-whisper sounddevice numpy keyboard

  Erster Start laedt automatisch das Whisper-Modell herunter (bei MODELL_GROESSE
  "small" ca. 150-250 MB, einmalig, danach komplett offline).

STARTEN:
    python windows_diktat.py

  Zum Testen erst OHNE pythonw starten -- die Konsole zeigt jede Transkription an,
  bevor sie getippt wird, so siehst du sofort ob was schiefgeht.

AUTOSTART (optional, erst wenn's laeuft):
  Verknuepfung zu "pythonw windows_diktat.py" in den Startup-Ordner legen
  (Windows-Taste+R -> shell:startup) -- dann laeuft es ohne sichtbares
  Konsolenfenster im Hintergrund.

BEDIENUNG:
  HOTKEY (Standard: rechte Strg-Taste) gedrueckt halten, sprechen, loslassen.
  Der Text erscheint nach kurzer Verarbeitungszeit im gerade fokussierten Fenster.
"""

# ── KONFIGURATION ──────────────────────────────────────────────────────────

HOTKEY = "right ctrl"          # gedrueckt halten zum Aufnehmen. Alternativen: "f9", "right alt", ...
SPRACHE = "de"                  # feste Sprache -- schneller und treffsicherer als Auto-Erkennung.
                                 # None setzen fuer automatische Spracherkennung (langsamer).
MODELL_GROESSE = "small"        # tiny/base/small/medium/large-v3 -- groesser = genauer, aber langsamer.
                                 # "small" ist ein guter Mittelweg auf einem normalen PC ohne GPU.
SAMPLERATE = 16000               # Whisper erwartet 16kHz, nicht aendern.
NACHSATZ_LEERZEICHEN = True     # haengt ein Leerzeichen an, damit aufeinanderfolgende
                                 # Diktate nicht ohne Trennung zusammenlaufen.

# ── IMPLEMENTIERUNG ─────────────────────────────────────────────────────────

import sys
import queue
import threading

import numpy as np
import sounddevice as sd
import keyboard
from faster_whisper import WhisperModel

print(f"Lade Whisper-Modell '{MODELL_GROESSE}' (beim ersten Mal wird es heruntergeladen)...")
modell = WhisperModel(MODELL_GROESSE, device="cpu", compute_type="int8")
print("Modell geladen. Bereit.")
print(f"Hotkey: '{HOTKEY}' gedrueckt halten zum Diktieren, loslassen zum Tippen.")
print("Strg+C in diesem Fenster beendet das Programm.")

_aufnahme_frames: list[np.ndarray] = []
_aufnahme_aktiv = False
_stream: sd.InputStream | None = None


def _audio_callback(indata, frames, time_info, status):
    if _aufnahme_aktiv:
        _aufnahme_frames.append(indata.copy())


def _aufnahme_starten():
    global _aufnahme_aktiv, _stream, _aufnahme_frames
    if _aufnahme_aktiv:
        return
    _aufnahme_frames = []
    _aufnahme_aktiv = True
    _stream = sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="float32",
                              callback=_audio_callback)
    _stream.start()
    print("… höre zu")


def _aufnahme_stoppen_und_tippen():
    global _aufnahme_aktiv, _stream
    if not _aufnahme_aktiv:
        return
    _aufnahme_aktiv = False
    _stream.stop()
    _stream.close()
    _stream = None

    if not _aufnahme_frames:
        return
    audio = np.concatenate(_aufnahme_frames, axis=0).flatten()
    dauer_s = len(audio) / SAMPLERATE
    if dauer_s < 0.3:
        print("(zu kurz, verworfen)")
        return

    print(f"… transkribiere ({dauer_s:.1f}s Audio)")
    segmente, _info = modell.transcribe(audio, language=SPRACHE, beam_size=5)
    text = "".join(segment.text for segment in segmente).strip()

    if not text:
        print("(nichts erkannt)")
        return

    if NACHSATZ_LEERZEICHEN:
        text += " "

    print(f"-> \"{text.strip()}\"")
    keyboard.write(text)


keyboard.on_press_key(HOTKEY, lambda _e: _aufnahme_starten())
keyboard.on_release_key(HOTKEY, lambda _e: _aufnahme_stoppen_und_tippen())

try:
    keyboard.wait()  # blockiert, bis das Programm beendet wird (Strg+C)
except KeyboardInterrupt:
    sys.exit(0)
