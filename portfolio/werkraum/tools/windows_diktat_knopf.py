#!/usr/bin/env python3
"""
Windows-Diktat mit Knopf -- lokale, kostenlose, UNZENSIERTE Sprache-zu-Text-Eingabe
=====================================================================================

Zweiter Anlauf, nachdem der erste Versuch (windows_diktat.py, globaler Tastatur-Hook per
"keyboard"-Bibliothek) bei Daniel auch als Administrator nicht auf Tastendruecke reagierte
(Ursache nicht abschliessend geklaert). Diesmal kein Hook: ein simples Fenster mit einem
Knopf zum Klicken.

Zweiter, eigener Grund fuer diesen Ansatz: der Diktat-Tab in der Toolbox
(flextrawurst.de/toolbox) nutzt Googles Spracherkennungsdienst -- der zensiert
Kraftausdruecke serverseitig (Chrome zeigt dann z.B. "s****" statt des echten Wortes), ohne
dass eine Webseite das offiziell abschalten koennte (kein maskProfanity-Parameter in der
Web-Speech-API-Spezifikation). faster-whisper laeuft komplett lokal und filtert nichts.

SETUP (einmalig, in einer Windows-Eingabeaufforderung):
    pip install faster-whisper sounddevice numpy

  ("keyboard" wird NICHT mehr gebraucht -- kein globaler Hook mehr noetig, nur ein Knopf im
  Fenster. tkinter ist in normalen Windows-Python-Installationen bereits eingebaut, kein
  extra pip install noetig.)

STARTEN:
    python windows_diktat_knopf.py

BEDIENUNG:
  Knopf klicken zum Aufnahme-Start, nochmal klicken zum Stopp -- der Text wird transkribiert
  und ins Feld darunter geschrieben (haengt an, ueberschreibt nichts Vorheriges). Dort frei
  editierbar -- korrigieren, ergaenzen, loeschen, ganz normal wie in jedem Textfeld.
  "Kopieren" legt den aktuellen kompletten Feldinhalt in die Zwischenablage.
"""

# ── KONFIGURATION ──────────────────────────────────────────────────────────

SPRACHE = "de"                  # feste Sprache -- schneller und treffsicherer als Auto-Erkennung.
MODELL_GROESSE = "small"        # tiny/base/small/medium/large-v3 -- groesser = genauer, langsamer.
SAMPLERATE = 16000               # Whisper erwartet 16kHz, nicht aendern.

# ── IMPLEMENTIERUNG ─────────────────────────────────────────────────────────

import queue
import threading
import tkinter as tk
from tkinter import scrolledtext

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

modell = None
aufnahme_aktiv = False
aufnahme_frames: list[np.ndarray] = []
stream: sd.InputStream | None = None
ergebnis_queue: queue.Queue = queue.Queue()


def modell_laden():
    global modell
    print("[Diktat] Lade Whisper-Modell ...", flush=True)
    try:
        modell = WhisperModel(MODELL_GROESSE, device="cpu", compute_type="int8")
        print("[Diktat] Modell geladen.", flush=True)
        ergebnis_queue.put(("bereit", None))
    except Exception as exc:
        print(f"[Diktat] FEHLER beim Laden des Modells: {exc}", flush=True)
        ergebnis_queue.put(("fehler", str(exc)))


def audio_callback(indata, frames, time_info, status):
    if aufnahme_aktiv:
        aufnahme_frames.append(indata.copy())


def aufnahme_starten():
    global aufnahme_aktiv, stream, aufnahme_frames
    aufnahme_frames = []
    aufnahme_aktiv = True
    stream = sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="float32",
                             callback=audio_callback)
    stream.start()
    btn.config(text="⏹ Aufnahme stoppen", bg="#c0392b")
    status_label.config(text="Nimmt auf …")


def aufnahme_stoppen_und_transkribieren():
    global aufnahme_aktiv, stream
    aufnahme_aktiv = False
    stream.stop()
    stream.close()
    stream = None
    btn.config(text="🎤 Aufnahme starten", bg="#2d6a4f", state="disabled")
    status_label.config(text="Transkribiere …")

    def hintergrund():
        if not aufnahme_frames:
            ergebnis_queue.put(("text", ""))
            return
        audio = np.concatenate(aufnahme_frames, axis=0).flatten()
        if len(audio) / SAMPLERATE < 0.3:
            ergebnis_queue.put(("text", ""))
            return
        segmente, _info = modell.transcribe(audio, language=SPRACHE, beam_size=5)
        text = "".join(s.text for s in segmente).strip()
        ergebnis_queue.put(("text", text))

    threading.Thread(target=hintergrund, daemon=True).start()


def auf_knopf_klick():
    if aufnahme_aktiv:
        aufnahme_stoppen_und_transkribieren()
    else:
        aufnahme_starten()


def kopieren():
    root.clipboard_clear()
    root.clipboard_append(textfeld.get("1.0", tk.END).strip())
    status_label.config(text="Kopiert.")


def leeren():
    textfeld.delete("1.0", tk.END)


def queue_pruefen():
    try:
        while True:
            art, wert = ergebnis_queue.get_nowait()
            if art == "bereit":
                status_label.config(text="Bereit.")
                btn.config(state="normal")
            elif art == "fehler":
                status_label.config(text=f"FEHLER: {wert}")
            elif art == "text":
                if wert:
                    textfeld.insert(tk.END, wert + " ")
                btn.config(state="normal")
                status_label.config(text="Bereit.")
    except queue.Empty:
        pass
    root.after(150, queue_pruefen)


print("[Diktat] Baue Fenster auf ...", flush=True)
root = tk.Tk()
root.title("Diktat (lokal, unzensiert)")
root.geometry("560x420")

status_label = tk.Label(root, text="Lade Modell (beim ersten Mal wird es heruntergeladen) …",
                         font=("Segoe UI", 10))
status_label.pack(pady=(10, 4))

btn = tk.Button(root, text="🎤 Aufnahme starten", command=auf_knopf_klick,
                 font=("Segoe UI", 12), bg="#2d6a4f", fg="white", height=2, state="disabled")
btn.pack(fill="x", padx=10, pady=6)

textfeld = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 11))
textfeld.pack(fill="both", expand=True, padx=10, pady=6)

knopf_reihe = tk.Frame(root)
knopf_reihe.pack(fill="x", padx=10, pady=(0, 10))
tk.Button(knopf_reihe, text="Kopieren", command=kopieren).pack(side="left", expand=True, fill="x", padx=(0, 4))
tk.Button(knopf_reihe, text="Leeren", command=leeren).pack(side="left", expand=True, fill="x", padx=(4, 0))

# Wichtig: Fenster JETZT schon einmal wirklich zeichnen, BEVOR das (moeglicherweise
# GIL-blockierende) Modell-Laden im Hintergrund-Thread beginnt -- sonst kann es passieren,
# dass das Fenster erst nach dem Laden ueberhaupt zum ersten Mal sichtbar wird (genau das
# Symptom, das bei Daniel auftrat: 10 Minuten, kein Fenster, obwohl das Modell schon
# heruntergeladen war).
root.update_idletasks()
root.update()
print("[Diktat] Fenster sichtbar. Starte Modell-Ladevorgang im Hintergrund ...", flush=True)

threading.Thread(target=modell_laden, daemon=True).start()
root.after(150, queue_pruefen)
root.mainloop()
