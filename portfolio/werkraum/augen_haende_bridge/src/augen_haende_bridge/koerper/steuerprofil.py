"""Steuerprofile der Hände (G10): wie ein Agent ein Ziel bedient, und was davon die Maschine hergibt.

* `hintergrund`: nichts Physisches. Der Agent bedient über Bedienungshilfen und Browser-Anschluss (UI Automation, AT-SPI, CDP — siehe `uia.py`, `cdp.py`, G11) und stört weder Daniels Zeiger noch seine
  Tastatur. Koordinaten-Aktionen (Klick, Ziehen, Tippen, Tasten, Rad) sind in diesem Profil nicht erlaubt.
* `geteilte_maus`: die echten Zeiger- und Tastaturereignisse des Desktops (XTEST/SendInput). Der Agent und Daniel teilen sich Maus und Tastatur; Daniels Eingabe hat Vorrang (`uebernahme.py`).
* `controller`: ein virtueller Spielcontroller. Das braucht einen Treiber (Windows: ViGEmBus; Linux: uinput). **Nichts davon wird ohne Daniels Wort installiert.** Hier wird nur erkannt, was da ist, und
  das Ziel von bis zu vier Controllern sichtbar gehalten.
* `hybrid`: geteilte Maus und Controller zugleich (Spiel mit Controller, daneben Maus für Menüs).

Das Profil wählt Daniel je Agent; ohne Wahl gilt `geteilte_maus`, wirksam nur, wenn die Hände des Agenten erlaubt sind.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

MAX_CONTROLLER = 4
KOORDINATEN_AKTIONEN = frozenset({"klick", "doppelklick", "ziehen", "tippen", "taste", "rad", "menue"})  # „menue“ ist ein echter Mausklick im Menü des Körpers
PROFILE = ("hintergrund", "geteilte_maus", "controller", "hybrid")
STANDARD = "geteilte_maus"


@dataclass(frozen=True)
class Profil:
    name: str
    zeiger_geteilt: bool
    tastatur_geteilt: bool
    controller: bool
    text: str

    def erlaubt(self, aktion_art: str) -> bool:
        """Darf dieses Profil die Aktion ausführen? Physische Aktionen nur mit geteilter Maus/Tastatur."""
        if aktion_art in KOORDINATEN_AKTIONEN:
            return self.zeiger_geteilt or self.tastatur_geteilt
        return aktion_art == "controller" and self.controller

    def zu_dict(self) -> dict:
        return {"profil": self.name, "zeiger_geteilt": self.zeiger_geteilt, "tastatur_geteilt": self.tastatur_geteilt, "controller": self.controller, "text": self.text}


_PROFILE = {
    "hintergrund": Profil("hintergrund", False, False, False, "Bedienung über Bedienungshilfen und Browser-Anschluss, ohne Daniels Zeiger und Tastatur"),
    "geteilte_maus": Profil("geteilte_maus", True, True, False, "echte Maus und Tastatur, geteilt mit Daniel (er hat Vorrang)"),
    "controller": Profil("controller", False, False, True, "virtueller Controller (braucht einen Treiber)"),
    "hybrid": Profil("hybrid", True, True, True, "geteilte Maus und Tastatur plus virtueller Controller"),
}


def profil(name: object) -> Profil:
    """Unbekannte Namen ergeben das vorsichtigste Profil (`hintergrund`), nie ein weiter gehendes."""
    return _PROFILE.get(name, _PROFILE["hintergrund"]) if isinstance(name, str) else _PROFILE["hintergrund"]


def controller_zustand(*, plattform: str | None = None, existiert=os.path.exists, schreibbar=lambda p: os.access(p, os.W_OK), joysticks=None, vigem=None) -> dict:
    """Was die Maschine für virtuelle Controller hergibt — nur erkennen, nichts installieren oder öffnen.

    `unterstuetzt` ist erst True, wenn der Treiber da **und** nutzbar ist; auch dann erzeugt dieses Modul keinen Controller (das ist ein eigener, von Daniel freizugebender Schritt)."""
    plattform = plattform or ("windows" if os.name == "nt" else "linux")
    ergebnis = {"ziel": MAX_CONTROLLER, "plattform": plattform, "treiber": None, "treiber_vorhanden": False, "nutzbar": False, "erkannte_geraete": [], "freigabe_noetig": True}
    if plattform == "windows":
        vorhanden = _vigem_vorhanden() if vigem is None else vigem
        ergebnis.update(treiber="ViGEmBus", treiber_vorhanden=bool(vorhanden), nutzbar=bool(vorhanden))
        ergebnis["text"] = "ViGEmBus ist installiert" if vorhanden else "ViGEmBus ist nicht installiert; die Installation braucht Daniels Wort"
    else:
        uinput = next((p for p in ("/dev/uinput", "/dev/input/uinput") if existiert(p)), None)
        ergebnis.update(treiber="uinput", treiber_vorhanden=uinput is not None, nutzbar=uinput is not None and schreibbar(uinput))
        if uinput is None:
            ergebnis["text"] = "uinput ist auf diesem Rechner nicht vorhanden"
        elif not ergebnis["nutzbar"]:
            ergebnis["text"] = "uinput ist da, aber nicht beschreibbar (fehlende Rechte); Rechte ändern braucht Daniels Wort"
        else:
            ergebnis["text"] = "uinput ist beschreibbar"
    liste = joysticks() if joysticks is not None else _joysticks_linux()
    ergebnis["erkannte_geraete"] = list(liste)[:MAX_CONTROLLER]
    return ergebnis


def _joysticks_linux() -> list[str]:
    try:
        return sorted(f"/dev/input/{n}" for n in os.listdir("/dev/input") if n.startswith("js"))
    except OSError:
        return []


def _vigem_vorhanden() -> bool:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\ViGEmBus"):
            return True
    except (ImportError, OSError):
        return False


def zustand(name: object, **kw) -> dict:
    """Alles, was die Oberfläche und der Agent über die Steuerung wissen sollen."""
    p = profil(name)
    z = p.zu_dict()
    z["controller_zustand"] = controller_zustand(**kw)
    z["controller_nutzbar"] = bool(p.controller and z["controller_zustand"]["nutzbar"])
    return z
