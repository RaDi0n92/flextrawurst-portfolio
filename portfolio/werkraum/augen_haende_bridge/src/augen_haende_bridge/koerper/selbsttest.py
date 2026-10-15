"""Selbsttest der Bridge auf dem echten Windows: prüft, was unter Wine nicht zu beweisen war, und schreibt einen Bericht.

Aufruf: `AugenUndHaendeBridge.exe --selbsttest` (oder `selbsttest.bat`). Der Test öffnet kurz eigene Testfenster, drückt ein paar Testtasten
(Strg+Alt, F13, Strg+Alt+F5), nimmt einmal den Bildschirm auf und öffnet kurz Kamera und Mikrofon. Er sendet nichts ins Netz, tippt nichts in
fremde Programme (nur in ein eigenes Testfeld) und verändert nichts dauerhaft. Bericht: `%LOCALAPPDATA%\\AugenUndHaendeBridge\\selbsttest.json` und
`selbsttest.txt`. Jede Prüfung meldet ok, warnung, fehler oder unbekannt samt Grund; Kamera und Mikrofon laufen in einem eigenen Prozess, damit ein
Absturz der Bibliotheken den Test nicht mitreißt (und selbst ein Befund ist).
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import traceback
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

OK, WARNUNG, FEHLER, UNBEKANNT = "ok", "warnung", "fehler", "unbekannt"
Pruefung = Callable[[], tuple[str, str]]


@dataclass
class Ergebnis:
    name: str
    status: str
    detail: str
    dauer_ms: int


def ausfuehren(pruefungen: list[tuple[str, Pruefung]], uhr: Callable[[], float] = time.monotonic) -> list[Ergebnis]:
    """Jede Prüfung für sich; eine Ausnahme ist ein Befund, kein Abbruch."""
    ergebnisse = []
    for name, pruefung in pruefungen:
        start = uhr()
        try:
            status, detail = pruefung()
        except Exception as fehler:
            status, detail = FEHLER, f"Ausnahme {fehler!r}: {traceback.format_exc(limit=3)}"[:600]
        ergebnisse.append(Ergebnis(name, status, detail, int((uhr() - start) * 1000)))
    return ergebnisse


def zusammenfassung(ergebnisse: list[Ergebnis]) -> dict[str, int]:
    zaehler = {OK: 0, WARNUNG: 0, FEHLER: 0, UNBEKANNT: 0}
    for e in ergebnisse:
        zaehler[e.status] = zaehler.get(e.status, 0) + 1
    return zaehler


def als_text(ergebnisse: list[Ergebnis], kopf: dict) -> str:
    zeilen = [f"Selbsttest der Augen-und-Hände-Bridge {kopf.get('version', '?')}", f"Rechner: {kopf.get('system', '?')}",
              f"Zeit: {kopf.get('zeit', '?')}", ""]
    zeichen = {OK: "[ OK ]", WARNUNG: "[WARN]", FEHLER: "[FEHL]", UNBEKANNT: "[ ?? ]"}
    for e in ergebnisse:
        zeilen.append(f"{zeichen.get(e.status, '[ ?? ]')} {e.name}  ({e.dauer_ms} ms)")
        zeilen.append(f"       {e.detail}")
    z = zusammenfassung(ergebnisse)
    zeilen += ["", f"Zusammenfassung: {z[OK]} ok, {z[WARNUNG]} Warnung(en), {z[FEHLER]} Fehler, {z[UNBEKANNT]} unbekannt"]
    return "\n".join(zeilen) + "\n"


def bericht_schreiben(ergebnisse: list[Ergebnis], kopf: dict, ordner: Path) -> tuple[Path, Path]:
    ordner.mkdir(parents=True, exist_ok=True)
    json_pfad, text_pfad = ordner / "selbsttest.json", ordner / "selbsttest.txt"
    json_pfad.write_text(json.dumps({"kopf": kopf, "zusammenfassung": zusammenfassung(ergebnisse),
                                     "ergebnisse": [asdict(e) for e in ergebnisse]}, ensure_ascii=False, indent=1), encoding="utf-8")
    text_pfad.write_text(als_text(ergebnisse, kopf), encoding="utf-8")
    return json_pfad, text_pfad


# ---- Geräteprüfung im eigenen Prozess -------------------------------------------------------------------------------
MAX_MIK_GERAETE = 8
GERAET_TIMEOUT_S = {"kamera": 90.0, "mikrofon": 90.0}


def _teil_schreiben(zielpfad: Path, detail: str) -> None:
    """Zwischenstand der Geräteprüfung: bleibt stehen, falls das Gerät später hängt und der Kindprozess abgebrochen wird."""
    try:
        Path(zielpfad).write_text(json.dumps({"status": "teil", "detail": detail}), encoding="utf-8")
    except OSError:
        pass


def geraet_pruefen(art: str, zielpfad: Path) -> None:
    """Läuft im Kindprozess (`--selbsttest-geraet kamera|mikrofon <datei>`): Ergebnis als JSON in die Datei."""
    ergebnis: dict
    try:
        if art == "kamera":
            import cv2

            gefunden = []
            for index in range(4):
                kamera = cv2.VideoCapture(index)
                if kamera.isOpened():
                    ok, bild = kamera.read()
                    gefunden.append({"index": index, "bild": list(bild.shape) if ok and bild is not None else None})
                kamera.release()
                _teil_schreiben(zielpfad, f"Kameras bis Index {index}: {gefunden or 'keine'}")
            ergebnis = {"status": OK if any(g["bild"] for g in gefunden) else WARNUNG,
                        "detail": f"opencv {cv2.__version__}; Kameras: {gefunden or 'keine gefunden'}"}
        elif art == "mikrofon":
            import sounddevice

            from .mikrofon import eingabegeraete

            geraete = eingabegeraete(sounddevice)
            if not geraete:
                ergebnis = {"status": WARNUNG, "detail": "keine Eingabegeräte gefunden"}
            else:
                try:
                    standard_name = sounddevice.query_devices(kind="input")["name"]
                except Exception:
                    standard_name = "?"
                messwerte = {}
                for index, name in geraete[:MAX_MIK_GERAETE]:
                    try:
                        aufnahme = sounddevice.rec(int(0.3 * 16000), samplerate=16000, channels=1, dtype="int16", device=index)
                        sounddevice.wait()
                        messwerte[name] = int(abs(aufnahme.astype("int32")).mean())
                    except Exception as fehler:
                        messwerte[name] = f"Fehler: {type(fehler).__name__}"
                    _teil_schreiben(zielpfad, "Messwerte bis hierher (Amplitude, 0 = Stille): "
                                    + "; ".join(f"{n}: {p}" for n, p in messwerte.items()))
                lebendig = [n for n, p in messwerte.items() if isinstance(p, int) and p > 0]
                text = "; ".join(f"{n}: {p}" for n, p in messwerte.items())
                detail = f"Standardgerät von Windows: {standard_name}. Mittlere Amplitude je Gerät (0 = digitale Stille): {text}"
                if not lebendig:
                    ergebnis = {"status": WARNUNG, "detail": detail + " — überall Stille: stumm geschaltet oder Datenschutz (Einstellungen → Datenschutz → Mikrofon)"}
                elif messwerte.get(standard_name) == 0 or standard_name not in messwerte:
                    ergebnis = {"status": WARNUNG, "detail": detail + f" — das Standardgerät ist still, Signal haben: {lebendig}; "
                                "in der Bridge unter Regie → Mikrofon-Gerät das passende wählen"}
                else:
                    ergebnis = {"status": OK, "detail": detail}
        else:
            ergebnis = {"status": FEHLER, "detail": f"unbekannte Geräteart {art}"}
    except Exception as fehler:
        ergebnis = {"status": FEHLER, "detail": f"{type(fehler).__name__}: {fehler}"[:300]}
    Path(zielpfad).write_text(json.dumps(ergebnis), encoding="utf-8")


def _teilstand(datei: Path) -> str:
    try:
        daten = json.loads(datei.read_text(encoding="utf-8"))
        if daten.get("status") == "teil":
            return f" — Zwischenstand: {daten['detail']}"
    except (OSError, ValueError, KeyError):
        pass
    return ""


def geraet_im_kindprozess(art: str, befehl_basis: list[str], timeout_s: float | None = None) -> tuple[str, str]:
    """Startet sich selbst für die Geräteprüfung; Absturz oder Zeitüberschreitung des Kindes werden zum Befund."""
    datei = Path(tempfile.mkdtemp(prefix="selbsttest-")) / f"{art}.json"
    if timeout_s is None:
        timeout_s = GERAET_TIMEOUT_S.get(art, 60.0)
    try:
        lauf = subprocess.run([*befehl_basis, "--selbsttest-geraet", art, str(datei)], timeout=timeout_s,
                              capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except subprocess.TimeoutExpired:
        return FEHLER, f"{art}: Zeitüberschreitung nach {timeout_s:.0f} s (Prozess hängt)" + _teilstand(datei)
    except OSError as fehler:
        return UNBEKANNT, f"{art}: Kindprozess nicht startbar: {fehler!r}"
    if datei.exists():
        try:
            daten = json.loads(datei.read_text(encoding="utf-8"))
            if daten["status"] != "teil":
                return daten["status"], daten["detail"]
            return FEHLER, f"{art}: Prozess vor dem Ende abgebrochen — Zwischenstand: {daten['detail']}"
        except (ValueError, KeyError):
            pass
    return FEHLER, f"{art}: Prozess ohne Ergebnis beendet (Exitcode {lauf.returncode}) — die Bibliothek ist abgestürzt oder fehlt"


def kopf_bauen(version: str) -> dict:
    return {"version": version, "system": platform.platform(), "python": sys.version.split()[0],
            "zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "frozen": bool(getattr(sys, "frozen", False))}
