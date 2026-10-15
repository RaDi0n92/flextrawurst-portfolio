"""Wine-Probe der Sichtbarkeitsregeln mit echten Fenstern und echten fremden Programmen (notepad, regedit).

Prüft: Programmliste, Vordergrund-Erkennung, dass ein Fenster mit Regel „nur bei notepad.exe“ echt erscheint und
verschwindet, Speichern/Wiederherstellen von Ort und Deckkraft. Ausgabe: eine JSON-Zeile.
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from augen_haende_bridge.koerper import einstellungen as einst
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.raute_fenster import RauteFenster
from augen_haende_bridge.koerper.sichtbarkeit import Sichtbarkeit, WindowsQuelle, programm_regel

_u = ctypes.WinDLL("user32", use_last_error=True)
_u.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
_u.FindWindowW.restype = w.wintypes.HWND
_u.SetForegroundWindow.argtypes = [w.wintypes.HWND]
_u.IsWindowVisible.argtypes = [w.wintypes.HWND]
_u.ShowWindow.argtypes = [w.wintypes.HWND, ctypes.c_int]
_u.BringWindowToTop.argtypes = [w.wintypes.HWND]
_u.SetWindowPos.argtypes = [w.wintypes.HWND, w.wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]


def nach_vorn(klasse: str) -> bool:
    for _ in range(50):
        hwnd = _u.FindWindowW(klasse, None)
        if hwnd:
            _u.ShowWindow(hwnd, 5)
            _u.BringWindowToTop(hwnd)
            _u.SetForegroundWindow(hwnd)
            return True
        time.sleep(0.1)
    return False


def main() -> int:
    anwendung = Anwendung()
    quelle = WindowsQuelle()
    ergebnis: dict = {}
    programme = quelle.offene_programme(os.getpid())
    ergebnis["programmliste_typ_ok"] = all(hasattr(p, "programm") and hasattr(p, "titel") for p in programme)

    notepad = subprocess.Popen(["notepad.exe"])
    regedit = subprocess.Popen(["regedit.exe"])
    time.sleep(2.0)
    anwendung.pumpen(100)
    namen = [p.programm for p in quelle.offene_programme(os.getpid())]
    ergebnis["fremde_programme_gefunden"] = {"notepad.exe": "notepad.exe" in namen, "regedit.exe": "regedit.exe" in namen}

    raute = RauteFenster(600, 200, name="Simi", farbe_hex="#00E5FF")
    raute.zeige(aktivieren=False)
    anwendung.pumpen(50)
    sicht = Sichtbarkeit(quelle, eigene_pid=os.getpid())
    sicht.registrieren("raute", raute, programm_regel("notepad.exe"))

    vorn_notepad = nach_vorn("Notepad")
    anwendung.pumpen(300)
    v1 = quelle.vordergrund()
    sicht.tick()
    sichtbar_bei_notepad = bool(_u.IsWindowVisible(raute.hwnd))
    vorn_regedit = nach_vorn("RegEdit_RegEdit")
    anwendung.pumpen(300)
    v2 = quelle.vordergrund()
    sicht.tick()
    sichtbar_bei_regedit = bool(_u.IsWindowVisible(raute.hwnd))
    nach_vorn("Notepad")
    anwendung.pumpen(300)
    sicht.tick()
    wieder_sichtbar = bool(_u.IsWindowVisible(raute.hwnd))
    ergebnis["vordergrund"] = {
        "notepad_nach_vorn_gefunden": vorn_notepad, "erkannt_1": v1.programm if v1 else None,
        "regedit_nach_vorn_gefunden": vorn_regedit, "erkannt_2": v2.programm if v2 else None,
    }
    ergebnis["raute_regel_notepad"] = {"sichtbar_bei_notepad": sichtbar_bei_notepad,
                                        "sichtbar_bei_regedit": sichtbar_bei_regedit,
                                        "wieder_sichtbar_bei_notepad": wieder_sichtbar}

    pfad = Path(tempfile.mkdtemp()) / "einstellungen.json"
    e = einst.Einstellungen(pfad)
    raute.verschiebe(321, 222)
    raute.groesse_setzen(72)
    raute.setze_deckkraft(128)
    daten = einst.erfassen(raute, "raute")
    daten["regel"] = programm_regel("notepad.exe").zu_dict()
    e.setzen("raute:Simi", daten)
    e.speichern()
    raute.schliessen()
    anwendung.pumpen(50)
    neu = RauteFenster(10, 10, name="Simi", farbe_hex="#00E5FF")
    neu.zeige(aktivieren=False)
    anwendung.pumpen(50)
    e2 = einst.Einstellungen(pfad)
    e2.laden()
    einst.anwenden(neu, e2.element("raute:Simi"), "raute", quelle.bildschirm)
    anwendung.pumpen(50)
    l, o, r, u = neu.rechteck()
    ergebnis["wiederhergestellt"] = {"ort": [l, o], "groesse": r - l, "deckkraft": neu.deckkraft_lesen()}
    neu.schliessen()
    for prozess in (notepad, regedit):
        prozess.kill()
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
