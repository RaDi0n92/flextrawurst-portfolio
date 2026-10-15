"""Virtuelle Spielcontroller (G10): bis zu vier Geräte, Knöpfe, Sticks, Trigger — mit denselben Sperren wie die Hände.

Ein Controller ist eine Eingabe wie jede andere: ohne Lease, ohne Profil „controller“ oder „hybrid“, bei Not-Aus, bei Daniels Übernahme oder bei fehlender Verbindung geschieht **nichts**, und nach jedem Auftrag (auch nach einem Fehler) ist alles losgelassen.
Ein Knopf wird höchstens `MAX_HALTEN_MS` gehalten.

Backends — der Treiber wird nie von hier aus installiert, nur erkannt (`steuerprofil.controller_zustand`):
* `UinputBackend` (Linux): ein virtuelles Gerät über `/dev/uinput` (Python-Paket `evdev`), das wie ein Xbox-Controller auftritt. Kein zusätzlicher Treiber, aber das Gerät muss beschreibbar sein.
* `VigemBackend` (Windows): über das Paket `vgamepad` und den Treiber ViGEmBus. Ohne beides meldet `verfuegbar()` den Grund.
* `AttrappenBackend`: für Tests und Proben; merkt sich nur, was gesendet wurde.
Was ein Spiel mit dem Gerät macht, sieht die Bridge nicht: `delivered` heißt „an das virtuelle Gerät gesendet“, nie „im Spiel angekommen“.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

MAX_CONTROLLER = 4
MAX_HALTEN_MS = 5000
MIN_HALTEN_MS = 20
KNOEPFE = ("a", "b", "x", "y", "lb", "rb", "back", "start", "guide", "ls", "rs", "hoch", "runter", "links", "rechts")
SEITEN = ("links", "rechts")
BEFEHLE = ("knopf", "stick", "trigger", "loslassen")


class ControllerFehler(Exception):
    def __init__(self, grund: str):
        super().__init__(grund)
        self.grund = grund


@dataclass(frozen=True)
class ControllerAktion:
    befehl: str
    index: int = 0
    name: str = ""  # Knopfname oder Seite (links/rechts bei Stick und Trigger)
    wert: tuple[float, float] = (0.0, 0.0)  # Stick: x, y von -1 bis 1; Trigger: x von 0 bis 1
    dauer_ms: int = 150

    @staticmethod
    def aus_dict(d: object) -> "ControllerAktion | None":
        """Streng: unbekannte Felder, falsche Typen und Werte außerhalb der Grenzen ergeben None."""
        if not isinstance(d, dict) or d.get("art") != "controller" or d.get("befehl") not in BEFEHLE or not set(d) <= {"art", "befehl", "index", "name", "wert", "dauer_ms"}:
            return None
        index, name, dauer = d.get("index", 0), d.get("name", ""), d.get("dauer_ms", 150)
        if type(index) is not int or not 0 <= index < MAX_CONTROLLER or not isinstance(name, str) or type(dauer) is not int:
            return None
        wert = d.get("wert", [0, 0])
        if not isinstance(wert, (list, tuple)) or len(wert) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in wert):
            return None
        x, y = float(wert[0]), float(wert[1])
        if d["befehl"] == "knopf" and (name not in KNOEPFE or not MIN_HALTEN_MS <= dauer <= MAX_HALTEN_MS):
            return None
        if d["befehl"] == "stick" and (name not in SEITEN or not (-1.0 <= x <= 1.0 and -1.0 <= y <= 1.0) or not MIN_HALTEN_MS <= dauer <= MAX_HALTEN_MS):
            return None
        if d["befehl"] == "trigger" and (name not in SEITEN or not 0.0 <= x <= 1.0 or not MIN_HALTEN_MS <= dauer <= MAX_HALTEN_MS):
            return None
        return ControllerAktion(d["befehl"], index, name, (x, y), dauer)

    def zu_dict(self) -> dict:
        d = {"art": "controller", "befehl": self.befehl, "index": self.index}
        if self.name:
            d["name"] = self.name
        if self.befehl in ("stick", "trigger"):
            d["wert"] = list(self.wert)
        if self.befehl != "loslassen":
            d["dauer_ms"] = self.dauer_ms
        return d


# ---- Backends -----------------------------------------------------------------------------------------------------------
class AttrappenBackend:
    name = "attrappe"

    def __init__(self):
        self.ereignisse: list[tuple] = []
        self.offen: set[int] = set()
        self.zustand: dict[int, dict] = {}

    def verfuegbar(self) -> tuple[bool, str]:
        return True, ""

    def oeffnen(self, i: int) -> None:
        self.offen.add(i)
        self.zustand.setdefault(i, {"knoepfe": set(), "sticks": {"links": (0.0, 0.0), "rechts": (0.0, 0.0)}, "trigger": {"links": 0.0, "rechts": 0.0}})

    def knopf(self, i: int, name: str, gedrueckt: bool) -> None:
        self.ereignisse.append(("knopf", i, name, gedrueckt))
        (self.zustand[i]["knoepfe"].add if gedrueckt else self.zustand[i]["knoepfe"].discard)(name)

    def stick(self, i: int, seite: str, x: float, y: float) -> None:
        self.ereignisse.append(("stick", i, seite, x, y))
        self.zustand[i]["sticks"][seite] = (x, y)

    def trigger(self, i: int, seite: str, wert: float) -> None:
        self.ereignisse.append(("trigger", i, seite, wert))
        self.zustand[i]["trigger"][seite] = wert

    def schliessen(self, i: int) -> None:
        self.offen.discard(i)


class UinputBackend:
    """Linux: ein virtuelles Gerät mit den Fähigkeiten eines Xbox-Controllers, über /dev/uinput."""

    name = "uinput"

    def __init__(self, pfad: str = "/dev/uinput"):
        self.pfad = pfad
        self._geraete: dict[int, object] = {}

    def verfuegbar(self) -> tuple[bool, str]:
        import os

        try:
            import evdev  # noqa: F401
        except ImportError:
            return False, "paket_evdev_fehlt"
        if not os.path.exists(self.pfad):
            return False, "uinput_nicht_vorhanden"
        if not os.access(self.pfad, os.W_OK):
            return False, "uinput_nicht_beschreibbar"
        return True, ""

    def _codes(self):
        from evdev import ecodes as e

        knoepfe = {"a": e.BTN_SOUTH, "b": e.BTN_EAST, "x": e.BTN_NORTH, "y": e.BTN_WEST, "lb": e.BTN_TL, "rb": e.BTN_TR, "back": e.BTN_SELECT, "start": e.BTN_START, "guide": e.BTN_MODE,
                   "ls": e.BTN_THUMBL, "rs": e.BTN_THUMBR}
        return e, knoepfe

    def oeffnen(self, i: int) -> None:
        if i in self._geraete:
            return
        from evdev import AbsInfo, UInput

        e, knoepfe = self._codes()
        achse = AbsInfo(0, -32768, 32767, 16, 128, 0)
        trigger = AbsInfo(0, 0, 255, 0, 0, 0)
        hut = AbsInfo(0, -1, 1, 0, 0, 0)
        faehig = {e.EV_KEY: list(knoepfe.values()), e.EV_ABS: [(e.ABS_X, achse), (e.ABS_Y, achse), (e.ABS_RX, achse), (e.ABS_RY, achse), (e.ABS_Z, trigger), (e.ABS_RZ, trigger),
                                                              (e.ABS_HAT0X, hut), (e.ABS_HAT0Y, hut)]}
        self._geraete[i] = UInput(faehig, name=f"Bridge virtueller Controller {i + 1}", vendor=0x045E, product=0x028E, version=1)

    def knopf(self, i: int, name: str, gedrueckt: bool) -> None:
        e, knoepfe = self._codes()
        g = self._geraete[i]
        if name in knoepfe:
            g.write(e.EV_KEY, knoepfe[name], 1 if gedrueckt else 0)
        else:
            achse, wert = {"hoch": (e.ABS_HAT0Y, -1), "runter": (e.ABS_HAT0Y, 1), "links": (e.ABS_HAT0X, -1), "rechts": (e.ABS_HAT0X, 1)}[name]
            g.write(e.EV_ABS, achse, wert if gedrueckt else 0)
        g.syn()

    def stick(self, i: int, seite: str, x: float, y: float) -> None:
        e, _ = self._codes()
        g = self._geraete[i]
        ax, ay = (e.ABS_X, e.ABS_Y) if seite == "links" else (e.ABS_RX, e.ABS_RY)
        g.write(e.EV_ABS, ax, round(x * 32767))
        g.write(e.EV_ABS, ay, round(y * 32767))
        g.syn()

    def trigger(self, i: int, seite: str, wert: float) -> None:
        e, _ = self._codes()
        g = self._geraete[i]
        g.write(e.EV_ABS, e.ABS_Z if seite == "links" else e.ABS_RZ, round(wert * 255))
        g.syn()

    def schliessen(self, i: int) -> None:
        g = self._geraete.pop(i, None)
        if g is not None:
            g.close()


class VigemBackend:
    """Windows: über das Paket `vgamepad` und den Treiber ViGEmBus. Ohne beides meldet `verfuegbar()` den Grund — es wird nichts installiert."""

    name = "vigem"

    def __init__(self):
        self._geraete: dict[int, object] = {}

    def verfuegbar(self) -> tuple[bool, str]:
        try:
            import vgamepad  # noqa: F401
        except ImportError:
            return False, "paket_vgamepad_fehlt"
        except Exception:
            return False, "treiber_vigembus_fehlt"
        try:
            import vgamepad as vg

            pad = vg.VX360Gamepad()
            del pad
        except Exception:
            return False, "treiber_vigembus_fehlt"
        return True, ""

    def oeffnen(self, i: int) -> None:
        if i not in self._geraete:
            import vgamepad as vg

            self._geraete[i] = vg.VX360Gamepad()

    def _tasten(self):
        import vgamepad as vg

        b = vg.XUSB_BUTTON
        return {"a": b.XUSB_GAMEPAD_A, "b": b.XUSB_GAMEPAD_B, "x": b.XUSB_GAMEPAD_X, "y": b.XUSB_GAMEPAD_Y, "lb": b.XUSB_GAMEPAD_LEFT_SHOULDER, "rb": b.XUSB_GAMEPAD_RIGHT_SHOULDER,
                "back": b.XUSB_GAMEPAD_BACK, "start": b.XUSB_GAMEPAD_START, "guide": b.XUSB_GAMEPAD_GUIDE, "ls": b.XUSB_GAMEPAD_LEFT_THUMB, "rs": b.XUSB_GAMEPAD_RIGHT_THUMB,
                "hoch": b.XUSB_GAMEPAD_DPAD_UP, "runter": b.XUSB_GAMEPAD_DPAD_DOWN, "links": b.XUSB_GAMEPAD_DPAD_LEFT, "rechts": b.XUSB_GAMEPAD_DPAD_RIGHT}

    def knopf(self, i: int, name: str, gedrueckt: bool) -> None:
        g = self._geraete[i]
        (g.press_button if gedrueckt else g.release_button)(button=self._tasten()[name])
        g.update()

    def stick(self, i: int, seite: str, x: float, y: float) -> None:
        g = self._geraete[i]
        (g.left_joystick_float if seite == "links" else g.right_joystick_float)(x_value_float=x, y_value_float=-y)  # vgamepad: oben ist positiv; hier ist unten positiv wie bei evdev
        g.update()

    def trigger(self, i: int, seite: str, wert: float) -> None:
        g = self._geraete[i]
        (g.left_trigger_float if seite == "links" else g.right_trigger_float)(value_float=wert)
        g.update()

    def schliessen(self, i: int) -> None:
        self._geraete.pop(i, None)


def waehle_backend(plattform: str | None = None):
    import os

    plattform = plattform or ("windows" if os.name == "nt" else "linux")
    return VigemBackend() if plattform == "windows" else UinputBackend()


# ---- Engine -----------------------------------------------------------------------------------------------------------------
@dataclass
class ControllerErgebnis:
    auftrag_id: str
    status: str  # ausgefuehrt | abgelehnt | abgebrochen | fehler
    grund: str = ""
    delivered: int = 0
    observed: dict = field(default_factory=dict)
    dauer_ms: int = 0

    def zu_dict(self) -> dict:
        return {"auftrag_id": self.auftrag_id, "status": self.status, "grund": self.grund, "accepted": self.status == "ausgefuehrt", "delivered": self.delivered, "observed": self.observed,
                "dauer_ms": self.dauer_ms, "audited": False}


class ControllerEngine:
    def __init__(self, backend, *, not_aus=lambda: False, daniel_uebernimmt=lambda: False, verbindung=lambda: True, schlafen=time.sleep, uhr=time.monotonic):
        self.backend, self._not_aus, self._daniel, self._verbindung, self._schlafen, self._uhr = backend, not_aus, daniel_uebernimmt, verbindung, schlafen, uhr
        self._sperre = threading.RLock()
        self._abbruch = threading.Event()
        self._offen: set[int] = set()
        self._belegt: dict[int, set] = {}  # index -> {("knopf", name), ("stick", seite), ("trigger", seite)}

    def zustand(self) -> dict:
        ok, grund = self.backend.verfuegbar()
        return {"backend": self.backend.name, "verfuegbar": ok, "grund": grund, "geraete": sorted(self._offen), "max": MAX_CONTROLLER, "hinweis": "„delivered“ heißt: an das virtuelle Gerät gesendet, nicht: im Spiel angekommen"}

    def abbrechen(self) -> None:
        """Not-Aus und Übernahme rufen das: ein laufender Auftrag bricht ab, und alles wird losgelassen."""
        self._abbruch.set()
        self.alles_loslassen()

    def alles_loslassen(self) -> int:
        n = 0
        with self._sperre:
            for i, belegt in list(self._belegt.items()):
                for art, name in list(belegt):
                    try:
                        if art == "knopf":
                            self.backend.knopf(i, name, False)
                        elif art == "stick":
                            self.backend.stick(i, name, 0.0, 0.0)
                        else:
                            self.backend.trigger(i, name, 0.0)
                        belegt.discard((art, name))
                        n += 1
                    except Exception:
                        pass
        return n

    def schliessen(self) -> None:
        self.alles_loslassen()
        for i in list(self._offen):
            try:
                self.backend.schliessen(i)
            except Exception:
                pass
            self._offen.discard(i)

    def _grund(self, lease_grund: str, haende_erlaubt: bool, profil_erlaubt: bool) -> str:
        if self._not_aus():
            return "not_aus"
        if not self._verbindung():
            return "verbindung_weg"
        if self._daniel():
            return "daniel_uebernimmt"
        if not haende_erlaubt:
            return "haende_aus"
        if not profil_erlaubt:
            return "profil_erlaubt_nicht"
        return lease_grund

    def ausfuehren(self, auftrag_id: str, a: ControllerAktion, *, lease_grund: str, haende_erlaubt: bool, profil_erlaubt: bool) -> ControllerErgebnis:
        t0 = self._uhr()
        grund = self._grund(lease_grund, haende_erlaubt, profil_erlaubt)
        if grund:
            return ControllerErgebnis(auftrag_id, "abgelehnt", grund)
        ok, warum = self.backend.verfuegbar()
        if not ok:
            return ControllerErgebnis(auftrag_id, "abgelehnt", "controller_" + warum)
        e = ControllerErgebnis(auftrag_id, "ausgefuehrt")
        with self._sperre:
            self._abbruch.clear()
            try:
                if a.index not in self._offen:
                    self.backend.oeffnen(a.index)
                    self._offen.add(a.index)
                belegt = self._belegt.setdefault(a.index, set())
                if a.befehl == "loslassen":
                    e.delivered = self.alles_loslassen()
                else:
                    if a.befehl == "knopf":
                        self.backend.knopf(a.index, a.name, True)
                        belegt.add(("knopf", a.name))
                    elif a.befehl == "stick":
                        self.backend.stick(a.index, a.name, a.wert[0], a.wert[1])
                        belegt.add(("stick", a.name))
                    else:
                        self.backend.trigger(a.index, a.name, a.wert[0])
                        belegt.add(("trigger", a.name))
                    e.delivered = 1
                    bis = self._uhr() + a.dauer_ms / 1000
                    while self._uhr() < bis:
                        if self._abbruch.is_set() or self._not_aus() or self._daniel():
                            e.status, e.grund = "abgebrochen", "not_aus" if self._not_aus() else ("daniel_uebernimmt" if self._daniel() else "abgebrochen")
                            break
                        self._schlafen(min(0.02, max(0.0, bis - self._uhr())))
            except Exception as f:
                e.status, e.grund = "fehler", "backend_fehler"
                e.observed["fehler"] = repr(f)[:120]
            finally:
                e.observed["losgelassen"] = self.alles_loslassen() if a.befehl != "loslassen" else e.delivered
        e.dauer_ms = int((self._uhr() - t0) * 1000)
        return e
