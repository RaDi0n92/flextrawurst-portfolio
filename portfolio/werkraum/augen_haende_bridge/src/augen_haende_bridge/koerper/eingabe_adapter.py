"""Die Hände (G10): Klicken, Ziehen, Tippen, Tastenkombinationen und Mausrad auf einem Ziel — hinter einem Käfig, mit Lease und echten Plattformaufrufen.

Drei Schichten, getrennt:

1. **Käfig** (`pruefe`, reine Logik): entscheidet, ob eine Aktion überhaupt ausgeführt werden darf. Er kennt nur Daten, keine Plattform: Not-Aus, Hände-Schalter, Lease, Ziel (da, minimiert,
   dasselbe wie beim Sehen), das Bild, auf das sich der Agent bezieht (Alter, Geometrie, DPI), und ob der Punkt innerhalb des Ziels liegt. Jede Ablehnung hat einen festen Grund aus `GRUENDE`.
   Eingaben gehen nie auf bloße Modell-IDs oder Listenindizes: die Aktion nennt einen Ziel-Schlüssel (`ziele.py`) und das Bild (Folgenummer), das der Agent gesehen hat.
2. **Engine** (`HaendeEngine`): führt eine erlaubte Aktion über ein `Backend` aus, Schritt für Schritt, und prüft vor jedem Schritt erneut Not-Aus, Abbruch und Ziel. Sie merkt sich, was gedrückt
   ist, und lässt in jedem Fall wieder los (auch bei Abbruch, Fehler und Not-Aus). Das Ergebnis trennt `accepted` (der Käfig hat zugelassen), `delivered` (Ereignisse an das System übergeben, wie
   viele) und `observed` (nachgemessene Wirkung, wo es sie gibt: Zeigerposition). `audited` ist der Eintrag im Protokoll.
3. **Backend** (`X11Backend`, `WindowsBackend`): die Plattformaufrufe (XTEST, SendInput). Austauschbar, damit der Käfig und die Engine ohne Plattform prüfbar sind; die Backends selbst werden gegen
   echte Fenster geprüft.

Nicht hier: virtuelle Controller (brauchen einen Treiber, nur nach Daniels Wort, siehe `steuerprofil.py`) und semantische Aktionen auf Knoten (G11).
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from . import menue_freigabe, offene_menues

Rechteck = tuple[int, int, int, int]

TASTEN = ("links", "rechts", "mitte")
ARTEN = ("klick", "doppelklick", "ziehen", "tippen", "taste", "rad", "menue")
MAX_TEXT = 500
MAX_MENUE_TEXT = 120
MAX_ZIEHEN_MS, MIN_ZIEHEN_MS = 5000, 50
SCHRITT_MS = 15
MAX_RAD = 20
MAX_BILD_ALTER_MS = 15_000  # ein älteres Bild ist keine Grundlage mehr für Koordinaten
TEXT_STUECK = 8

GRUENDE = {
    "not_aus": "Not-Aus aktiv",
    "haende_aus": "Daniel hat die Hände dieses Agenten nicht erlaubt",
    "profil_erlaubt_nicht": "das Steuerprofil erlaubt diese Aktion nicht",
    "aktion_ungueltig": "die Aktion ist unvollständig oder hat unzulässige Werte",
    "kein_ziel": "kein Ziel gebunden",
    "ziel_weg": "das Ziel gibt es nicht mehr",
    "ziel_ersetzt": "unter dem Ziel-Schlüssel liegt jetzt ein anderes Fenster",
    "ziel_minimiert": "das Ziel ist minimiert",
    "lease_fehlt": "der Agent hat keine Lease auf dieses Ziel",
    "lease_abgelaufen": "die Lease ist abgelaufen",
    "lease_fremd": "die Lease gehört einem anderen Agenten",
    "frame_unbekannt": "das Bild, auf das sich der Agent bezieht, ist dem Körper nicht bekannt",
    "frame_veraltet": "das Bild, auf das sich der Agent bezieht, ist zu alt",
    "frame_anderes_ziel": "das Bild gehört zu einem anderen Ziel",
    "geometrie_geaendert": "das Ziel wurde seit dem Bild verschoben, in der Größe oder im DPI-Maßstab verändert",
    "ausserhalb": "der Punkt liegt außerhalb des Ziels",
    "punkt_verdeckt": "an diesem Punkt liegt ein anderes Fenster vor dem Ziel",
    "fokus_verloren": "das Ziel hat die Tastatur nicht (mehr)",
    "fokus_nicht_erreichbar": "die Tastatur ließ sich dem Ziel nicht geben",
    "notaus_taste": "diese Taste ist der Not-Aus des Körpers",
    "systemtaste": "diese Tastenkombination ist gesperrt",
    "daniel_uebernimmt": "Daniel bedient gerade selbst",
    "verbindung_weg": "die Verbindung zum Starter ist abgebrochen",
    "abgebrochen": "abgebrochen",
    "backend_fehler": "das System hat die Eingabe nicht angenommen",
    "menue_nicht_freigegeben": "Menü-Fenster der Bridge sind für die Hände nicht freigegeben",
    "menue_nicht_offen": "es ist kein Menü offen, das der Körper kennt",
    "menue_eintrag_unbekannt": "das offene Menü hat keinen Eintrag mit diesem Namen",
    "menue_eintrag_unklar": "der Name passt auf mehrere Einträge des Menüs",
    "menue_eintrag_gesperrt": "dieser Menüeintrag ist für Agenten gesperrt",
    "menue_eintrag_abgeblendet": "dieser Menüeintrag ist abgeblendet",
}


# ---- Daten --------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Aktion:
    art: str
    punkt: tuple[int, int] | None = None  # Bildkoordinaten des Bildes, auf das sich der Agent bezieht
    bis: tuple[int, int] | None = None
    taste: str = "links"
    text: str = ""
    kombi: str = ""
    dauer_ms: int = 300
    dy: int = 0  # Mausrad: positiv = nach unten, in Rastern

    @staticmethod
    def aus_dict(d: object) -> "Aktion | None":
        """Streng: unbekannte Felder, falsche Typen und unzulässige Werte ergeben None."""
        if not isinstance(d, dict) or d.get("art") not in ARTEN:
            return None
        erlaubt = {"art", "punkt", "bis", "taste", "text", "kombi", "dauer_ms", "dy"}
        if not set(d) <= erlaubt:
            return None

        def punkt(v):
            if v is None:
                return None
            if isinstance(v, (list, tuple)) and len(v) == 2 and all(type(c) is int and -100_000 <= c <= 100_000 for c in v):
                return (v[0], v[1])
            raise ValueError

        try:
            a = Aktion(d["art"], punkt(d.get("punkt")), punkt(d.get("bis")), d.get("taste", "links"), d.get("text", ""), d.get("kombi", ""), d.get("dauer_ms", 300), d.get("dy", 0))
        except ValueError:
            return None
        if a.taste not in TASTEN or not isinstance(a.text, str) or not isinstance(a.kombi, str) or type(a.dauer_ms) is not int or type(a.dy) is not int:
            return None
        if a.art in ("klick", "doppelklick") and a.punkt is None:
            return None
        if a.art == "ziehen" and (a.punkt is None or a.bis is None or not MIN_ZIEHEN_MS <= a.dauer_ms <= MAX_ZIEHEN_MS):
            return None
        if a.art == "tippen" and not 1 <= len(a.text) <= MAX_TEXT:
            return None
        if a.art == "taste" and not 1 <= len(a.kombi) <= 60:
            return None
        if a.art == "rad" and (a.dy == 0 or abs(a.dy) > MAX_RAD or a.punkt is None):
            return None
        if a.art == "menue" and (not 1 <= len(a.text) <= MAX_MENUE_TEXT or a.punkt is not None or a.bis is not None):
            return None  # ein Menüeintrag wird beim Namen genannt; Koordinaten nimmt der Körper dafür nie an
        return a

    def zu_dict(self) -> dict:
        d = {"art": self.art}
        for feld, standard in (("punkt", None), ("bis", None), ("taste", "links"), ("text", ""), ("kombi", ""), ("dauer_ms", 300), ("dy", 0)):
            wert = getattr(self, feld)
            if wert != standard:
                d[feld] = list(wert) if isinstance(wert, tuple) else wert
        return d


@dataclass(frozen=True)
class Bildbezug:
    """Das Bild, das der Agent gesehen hat — vom Körper beim Senden festgehalten."""

    ziel: str
    seq: int
    captured_at_ms: int
    breite: int
    hoehe: int
    rect: Rechteck  # Fensterrechteck in Bildschirmkoordinaten zur Aufnahmezeit
    generation: object = None  # Identität des Fensters zur Aufnahmezeit
    dpi: float | None = None
    bild_rect: Rechteck | None = None  # der Bildschirmbereich, den das Bild zeigt (bei einem teils außerhalb liegenden Fenster kleiner als `rect`); Vorgabe: `rect`


@dataclass(frozen=True)
class ZielStand:
    """Der jetzige Zustand des Ziels, frisch gelesen."""

    vorhanden: bool
    rect: Rechteck | None = None
    minimiert: bool = False
    generation: object = None
    dpi: float | None = None


@dataclass
class Entscheidung:
    ok: bool
    grund: str = ""
    start: tuple[int, int] | None = None  # Bildschirmpunkte, wenn ok
    ende: tuple[int, int] | None = None


@dataclass
class Ergebnis:
    auftrag_id: str
    status: str  # ausgefuehrt | abgelehnt | abgebrochen | fehler
    grund: str = ""
    accepted: bool = False
    delivered: int = 0
    observed: dict = field(default_factory=dict)
    dauer_ms: int = 0
    audited: bool = False

    def zu_dict(self) -> dict:
        return {"auftrag_id": self.auftrag_id, "status": self.status, "grund": self.grund, "accepted": self.accepted, "delivered": self.delivered,
                "observed": self.observed, "dauer_ms": self.dauer_ms, "audited": self.audited, "text": GRUENDE.get(self.grund, "")}


# ---- Lease --------------------------------------------------------------------------------------------------------------
@dataclass
class Lease:
    id: str
    ziel: str
    halter: str
    bis: float


class LeaseTabelle:
    """Wer darf auf dieses Ziel Eingaben schicken? Höchstens einer zugleich, zeitlich begrenzt; ein anderer kann sie nicht an sich reißen, nur nach Ablauf oder Freigabe haben."""

    def __init__(self, uhr: Callable[[], float] = time.monotonic, standard_ttl_s: float = 30.0, max_ttl_s: float = 300.0):
        self._uhr, self.standard_ttl_s, self.max_ttl_s = uhr, standard_ttl_s, max_ttl_s
        self._leases: dict[str, Lease] = {}
        self._sperre = threading.Lock()
        self._zaehler = 0

    def _abgelaufen_entfernen(self) -> None:
        jetzt = self._uhr()
        for ziel in [z for z, l in self._leases.items() if l.bis <= jetzt]:
            del self._leases[ziel]

    def erwerben(self, ziel: str, halter: str, ttl_s: float | None = None) -> tuple[Lease | None, str]:
        ttl = min(float(ttl_s if ttl_s is not None else self.standard_ttl_s), self.max_ttl_s)
        if ttl <= 0:
            return None, "ttl_ungueltig"
        with self._sperre:
            self._abgelaufen_entfernen()
            vorhanden = self._leases.get(ziel)
            if vorhanden is not None and vorhanden.halter != halter:
                return None, "belegt"
            self._zaehler += 1
            lease = vorhanden or Lease(f"l-{self._zaehler}-{int(self._uhr() * 1000) % 100000}", ziel, halter, 0.0)
            lease.bis = self._uhr() + ttl  # derselbe Halter verlängert
            self._leases[ziel] = lease
            return lease, ""

    def freigeben(self, ziel: str, halter: str) -> bool:
        with self._sperre:
            lease = self._leases.get(ziel)
            if lease is None or lease.halter != halter:
                return False
            del self._leases[ziel]
            return True

    def alle_entziehen(self) -> int:
        with self._sperre:
            n = len(self._leases)
            self._leases.clear()
            return n

    def pruefen(self, lease_id: str | None, ziel: str, halter: str) -> str:
        """'' wenn gültig, sonst der Grund."""
        with self._sperre:
            lease = self._leases.get(ziel)
            if lease is None:
                return "lease_fehlt"
            if lease.bis <= self._uhr():
                del self._leases[ziel]
                return "lease_abgelaufen"
            if lease.halter != halter:
                return "lease_fremd"
            if lease_id != lease.id:
                return "lease_fehlt"
            return ""

    def entziehen_wenn(self, bedingung: Callable[[str], bool]) -> int:
        """Entzieht alle Leases, deren Ziel-Schlüssel die Bedingung erfüllt (z. B. alle eines Desktops, der offline gegangen ist)."""
        with self._sperre:
            weg = [z for z in self._leases if bedingung(z)]
            for z in weg:
                del self._leases[z]
            return len(weg)

    def von(self, ziel: str) -> Lease | None:
        with self._sperre:
            self._abgelaufen_entfernen()
            return self._leases.get(ziel)


# ---- Käfig --------------------------------------------------------------------------------------------------------------
def bild_zu_schirm(punkt: tuple[int, int], bezug: Bildbezug) -> tuple[int, int]:
    """Ein Punkt im Bild des Agenten auf den Bildschirm: Fensterursprung plus Punkt, skaliert um das Verhältnis Fenster zu Bild."""
    r = bezug.bild_rect or bezug.rect
    breite, hoehe = r[2] - r[0], r[3] - r[1]
    return (r[0] + int(punkt[0] * breite / bezug.breite), r[1] + int(punkt[1] * hoehe / bezug.hoehe))


def _pruefe_menue(aktion: Aktion, freigegeben: bool, offen: "offene_menues.OffenesMenue | None") -> Entscheidung:
    """Die Menü-Aktion: nur mit Freigabe, nur im Menü, das der Körper selbst offen hält, nur ein erlaubter Eintrag, der Name muss eindeutig sein."""
    if not freigegeben:
        return Entscheidung(False, "menue_nicht_freigegeben")
    if offen is None:
        return Entscheidung(False, "menue_nicht_offen")
    name = aktion.text.strip().casefold()
    if name in menue_freigabe.SCHLIESSEN_NAMEN:
        return Entscheidung(True) if offen.schliessen is not None else Entscheidung(False, "menue_eintrag_unbekannt")
    treffer = [e for e in offen.eintraege if e.text.casefold() == name] or [e for e in offen.eintraege if e.text.casefold().startswith(name)]
    if not treffer:
        return Entscheidung(False, "menue_eintrag_unbekannt")
    if len(treffer) > 1:
        return Entscheidung(False, "menue_eintrag_unklar")
    eintrag = treffer[0]
    grund = menue_freigabe.pruefe_eintrag(offen.art, eintrag.befehl)
    if grund:
        return Entscheidung(False, grund)
    if not eintrag.aktiv:
        return Entscheidung(False, "menue_eintrag_abgeblendet")
    return Entscheidung(True, "", eintrag.mitte, None)


def pruefe(aktion: Aktion, *, ziel: str, bezug: Bildbezug | None, stand: ZielStand | None, lease_grund: str, not_aus: bool, haende_erlaubt: bool, profil_erlaubt: bool,
           jetzt_ms: int, max_alter_ms: int = MAX_BILD_ALTER_MS, daniel_uebernimmt: bool = False, verbindung: bool = True,
           menue_freigabe_an: bool = False, menue_offen: "offene_menues.OffenesMenue | None" = None) -> Entscheidung:
    """Der Käfig. Die Reihenfolge ist Absicht: erst, was alles stoppt, dann Rechte, dann das Ziel, dann das Bild, zuletzt die Punkte."""
    if not_aus:
        return Entscheidung(False, "not_aus")
    if not verbindung:
        return Entscheidung(False, "verbindung_weg")
    if daniel_uebernimmt:
        return Entscheidung(False, "daniel_uebernimmt")
    if not haende_erlaubt:
        return Entscheidung(False, "haende_aus")
    if not profil_erlaubt:
        return Entscheidung(False, "profil_erlaubt_nicht")
    if not ziel or ziel == "desktop":
        return Entscheidung(False, "kein_ziel")  # Eingaben gehen nur auf ein bestimmtes Fenster, nie auf „den Bildschirm“
    if lease_grund:
        return Entscheidung(False, lease_grund)
    if stand is None or not stand.vorhanden:
        return Entscheidung(False, "ziel_weg")
    if stand.minimiert:
        return Entscheidung(False, "ziel_minimiert")
    if stand.rect is None:
        return Entscheidung(False, "ziel_weg")
    if aktion.art == "menue":
        return _pruefe_menue(aktion, menue_freigabe_an, menue_offen)
    if aktion.art in ("tippen", "taste"):
        # Die Tastatur braucht keinen Bildpunkt und kein Bild; ob das Ziel die Tastatur hat, wird beim Ausführen vor jedem Stück geprüft.
        if aktion.art == "taste" and "f12" in [t.strip().lower() for t in aktion.kombi.split("+")]:
            return Entscheidung(False, "notaus_taste")
        if aktion.art == "taste" and _gesperrt(aktion.kombi):
            return Entscheidung(False, "systemtaste")
        return Entscheidung(True)
    if bezug is None:
        return Entscheidung(False, "frame_unbekannt")
    if bezug.ziel != ziel:
        return Entscheidung(False, "frame_anderes_ziel")
    if jetzt_ms - bezug.captured_at_ms > max_alter_ms:
        return Entscheidung(False, "frame_veraltet")
    if stand.generation is not None and bezug.generation is not None and stand.generation != bezug.generation:
        return Entscheidung(False, "ziel_ersetzt")
    if stand.rect != bezug.rect or (stand.dpi is not None and bezug.dpi is not None and abs(stand.dpi - bezug.dpi) > 1e-6):
        return Entscheidung(False, "geometrie_geaendert")
    if aktion.punkt is None:
        return Entscheidung(True, "", None, None)
    punkte = [aktion.punkt] + ([aktion.bis] if aktion.bis is not None else [])
    schirm = []
    for p in punkte:
        if not (0 <= p[0] < bezug.breite and 0 <= p[1] < bezug.hoehe):
            return Entscheidung(False, "ausserhalb")
        schirm.append(bild_zu_schirm(p, bezug))
    for x, y in schirm:
        if not (stand.rect[0] <= x < stand.rect[2] and stand.rect[1] <= y < stand.rect[3]):
            return Entscheidung(False, "ausserhalb")
    return Entscheidung(True, "", schirm[0], schirm[1] if len(schirm) > 1 else None)


def _gesperrt(kombi: str) -> bool:
    teile = {t.strip().lower() for t in kombi.split("+")}
    return {"alt"} <= teile and bool(teile & {"strg", "ctrl"}) and bool(teile & {"entf", "delete", "del"})  # Strg+Alt+Entf


# ---- Tastenkombinationen in Windows-Tastencodes (die Sprache des Körpers) ------------------------------------------------------
_MODS = {"strg": 0x11, "ctrl": 0x11, "alt": 0x12, "umschalt": 0x10, "shift": 0x10, "win": 0x5B, "super": 0x5B, "meta": 0x5B}
_BENANNT = {"enter": 0x0D, "return": 0x0D, "tab": 0x09, "esc": 0x1B, "escape": 0x1B, "leertaste": 0x20, "space": 0x20, "entf": 0x2E, "delete": 0x2E, "del": 0x2E,
            "pos1": 0x24, "home": 0x24, "ende": 0x23, "end": 0x23, "bildauf": 0x21, "pageup": 0x21, "bildab": 0x22, "pagedown": 0x22, "links": 0x25, "left": 0x25,
            "hoch": 0x26, "up": 0x26, "rechts": 0x27, "right": 0x27, "runter": 0x28, "down": 0x28, "rueckschritt": 0x08, "backspace": 0x08, "einfg": 0x2D, "insert": 0x2D}


def kombi_zu_vk(text: str) -> tuple[list[int], int] | None:
    """„Strg+Umschalt+S“ → ([0x11, 0x10], 0x53). None, wenn etwas nicht zu benennen ist. Buchstaben, Ziffern, F1–F24 und die benannten Tasten sind erlaubt."""
    teile = [t.strip().lower() for t in text.split("+") if t.strip()]
    if not teile:
        return None
    mods = []
    for t in teile[:-1]:
        if t not in _MODS:
            return None
        mods.append(_MODS[t])
    letzte = teile[-1]
    if letzte in _BENANNT:
        vk = _BENANNT[letzte]
    elif len(letzte) == 1 and letzte.isalpha() and letzte.isascii():
        vk = ord(letzte.upper())
    elif len(letzte) == 1 and letzte.isdigit():
        vk = ord(letzte)
    elif letzte.startswith("f") and letzte[1:].isdigit() and 1 <= int(letzte[1:]) <= 24:
        vk = 0x6F + int(letzte[1:])
    elif letzte in _MODS:
        vk, mods = _MODS[letzte], mods
    else:
        return None
    return mods, vk


# ---- Backends -----------------------------------------------------------------------------------------------------------
class Backend:
    """Die Plattformaufrufe. Jeder liefert True/die Zahl, wenn das System die Eingabe angenommen hat."""

    name = ""

    def maus_bewegen(self, x: int, y: int) -> bool: ...
    def maus_taste(self, taste: str, runter: bool) -> bool: ...
    def rad(self, dy: int) -> bool: ...
    def rad_ereignisse(self, dy: int) -> int:
        return 1  # so viele Zeigerereignisse erzeugt ein Radschritt-Auftrag beim Beobachter
    def taste(self, vk: int, runter: bool) -> bool: ...
    def text(self, text: str) -> int: ...
    def maus_position(self) -> tuple[int, int]: ...
    def fenster_am_punkt(self, x: int, y: int) -> int | None: ...
    def tastatur_fokus(self) -> int | None: ...
    def fokus_geben(self, kennung: int) -> bool: ...

    def gleich(self, oben: int | None, ziel: int | None) -> bool:
        """Ist `oben` (Fenster der obersten Ebene am Punkt oder mit Tastaturfokus) das Ziel oder enthält es? Unter X11 liegt das Ziel oft in einem Rahmen der Fensterverwaltung."""
        return oben is not None and ziel is not None and int(oben) == int(ziel)


def _unter_schloss(f):
    """Methoden des X11-Backends laufen unter dem Schloss der Verbindung."""
    import functools

    @functools.wraps(f)
    def innen(self, *a, **k):
        with self._sperre:
            return f(self, *a, **k)

    return innen


class X11Backend(Backend):
    """XTEST für Zeiger, Tasten und Rad; eigene Verbindung (nur aus dem Faden der Engine benutzen)."""

    name = "x11"

    def __init__(self):
        from Xlib import X, display
        from Xlib.ext import xtest

        self._X, self._xtest = X, xtest
        self._d = display.Display()
        self._sperre = threading.RLock()  # alles Loslassen kommt auch aus anderen Fäden (Not-Aus, Übernahme): eine Verbindung darf nie gleichzeitig benutzt werden
        self._wurzel = self._d.screen().root
        if not self._d.has_extension("XTEST"):
            raise RuntimeError("XTEST fehlt")

    def _fake(self, art: int, detail: int = 0, x: int = 0, y: int = 0, wurzel=None) -> None:
        self._xtest.fake_input(self._d, art, detail, 0, wurzel if wurzel is not None else self._X.NONE, x, y)

    @_unter_schloss
    def maus_bewegen(self, x: int, y: int) -> bool:
        self._xtest.fake_input(self._d, self._X.MotionNotify, 0, 0, self._wurzel, int(x), int(y))
        self._d.sync()
        return True

    _TASTEN = {"links": 1, "mitte": 2, "rechts": 3}

    @_unter_schloss
    def maus_taste(self, taste: str, runter: bool) -> bool:
        self._xtest.fake_input(self._d, self._X.ButtonPress if runter else self._X.ButtonRelease, self._TASTEN[taste])
        self._d.sync()
        return True

    @_unter_schloss
    def rad(self, dy: int) -> bool:
        knopf = 5 if dy > 0 else 4
        for _ in range(abs(dy)):
            self._xtest.fake_input(self._d, self._X.ButtonPress, knopf)
            self._xtest.fake_input(self._d, self._X.ButtonRelease, knopf)
        self._d.sync()
        return True

    def rad_ereignisse(self, dy: int) -> int:
        return 2 * abs(dy)  # X11: je Raster ein Drücken und ein Loslassen

    @_unter_schloss
    def taste(self, vk: int, runter: bool) -> bool:
        from . import linux_adapter as la

        return la.xtest_senden([(vk, 0, 0 if runter else 0x0002)]) == 1

    @_unter_schloss
    def text(self, text: str) -> int:
        from . import linux_adapter as la
        from .tasten_senden import text_ereignisse

        return la.xtest_senden(text_ereignisse(text))

    @_unter_schloss
    def maus_position(self) -> tuple[int, int]:
        d = self._wurzel.query_pointer()
        return d.root_x, d.root_y

    @_unter_schloss
    def fenster_am_punkt(self, x: int, y: int) -> int | None:
        """Das oberste sichtbare Fenster der obersten Ebene an diesem Punkt (Stapelreihenfolge: das letzte Kind liegt oben)."""
        from Xlib import X, error
        from Xlib.ext import shape

        try:
            for kind in reversed(self._wurzel.query_tree().children):
                try:
                    attr = kind.get_attributes()
                    if attr.map_state != X.IsViewable or attr.win_class == X.InputOnly:
                        continue
                    geo = kind.get_geometry()
                except error.XError:
                    continue
                if geo.x <= x < geo.x + geo.width and geo.y <= y < geo.y + geo.height:
                    try:
                        if self._d.has_extension("SHAPE"):
                            sr = kind.shape_get_rectangles(shape.SK.Input)
                            if sr is not None and len(sr.rectangles) == 0:
                                continue
                    except Exception:
                        pass
                    return int(kind.id)
        except error.XError:
            return None
        return None

    @_unter_schloss
    def tastatur_fokus(self) -> int | None:
        """Das Fenster der obersten Ebene, das die Tastatur hat (vom Fokusfenster zur Wurzel hinauf)."""
        from Xlib import error

        try:
            fenster = self._d.get_input_focus().focus
            while hasattr(fenster, "id") and fenster.id > 1:
                eltern = fenster.query_tree().parent
                if not hasattr(eltern, "id") or eltern.id == self._wurzel.id:  # die Wurzel selbst hat als Elternteil „keines“ (eine Zahl, kein Fenster)
                    return int(fenster.id)
                fenster = eltern
        except error.XError:
            return None
        return None

    @_unter_schloss
    def fokus_geben(self, kennung: int) -> bool:
        from Xlib import X, error

        try:
            fenster = self._d.create_resource_object("window", int(kennung))
            fenster.configure(stack_mode=X.Above)
            self._d.set_input_focus(fenster, X.RevertToParent, X.CurrentTime)
            self._d.sync()
            return True
        except error.XError:
            return False

    @_unter_schloss
    def gleich(self, oben, ziel) -> bool:
        if oben is None or ziel is None:
            return False
        if int(oben) == int(ziel):
            return True
        from Xlib import error

        try:  # das Ziel kann im Rahmen der Fensterverwaltung stecken: bis drei Ebenen tief suchen
            ebene = [self._d.create_resource_object("window", int(oben))]
            for _ in range(3):
                kinder = []
                for f in ebene:
                    kinder.extend(f.query_tree().children)
                if any(int(k.id) == int(ziel) for k in kinder):
                    return True
                ebene = kinder
        except error.XError:
            return False
        return False

    def schliessen(self) -> None:
        try:
            self._d.close()
        except Exception:
            pass


class WindowsBackend(Backend):
    """SendInput für Maus und Tasten (Windows oder Wine); der Zeiger wird mit SetCursorPos gesetzt."""

    name = "windows"
    _MOUSEEVENTF = {("links", True): 0x0002, ("links", False): 0x0004, ("rechts", True): 0x0008, ("rechts", False): 0x0010, ("mitte", True): 0x0020, ("mitte", False): 0x0040}
    MOUSEEVENTF_WHEEL = 0x0800

    def __init__(self):
        import ctypes
        from ctypes import wintypes

        self._ct, self._wt = ctypes, wintypes
        self._u = ctypes.WinDLL("user32", use_last_error=True)
        self._u.SetCursorPos.argtypes, self._u.SetCursorPos.restype = [ctypes.c_int, ctypes.c_int], ctypes.c_int
        self._u.GetSystemMetrics.argtypes, self._u.GetSystemMetrics.restype = [ctypes.c_int], ctypes.c_int
        self._u.GetCursorPos.argtypes, self._u.GetCursorPos.restype = [ctypes.POINTER(wintypes.POINT)], ctypes.c_int
        self._u.WindowFromPoint.argtypes, self._u.WindowFromPoint.restype = [wintypes.POINT], ctypes.c_void_p
        self._u.GetAncestor.argtypes, self._u.GetAncestor.restype = [ctypes.c_void_p, ctypes.c_uint], ctypes.c_void_p
        self._u.GetForegroundWindow.restype = ctypes.c_void_p
        self._u.SetForegroundWindow.argtypes, self._u.SetForegroundWindow.restype = [ctypes.c_void_p], ctypes.c_int
        self._u.GetWindowRect.argtypes, self._u.GetWindowRect.restype = [ctypes.c_void_p, ctypes.POINTER(wintypes.RECT)], ctypes.c_int

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_int32), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]

        class INPUT(ctypes.Structure):
            class _U(ctypes.Union):
                _fields_ = [("mi", MOUSEINPUT)]
            _anonymous_ = ("u",)
            _fields_ = [("type", ctypes.c_uint32), ("u", _U)]

        self._MOUSEINPUT, self._INPUT = MOUSEINPUT, INPUT
        self._u.SendInput.argtypes, self._u.SendInput.restype = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int], ctypes.c_uint

    def _maus(self, flags: int, daten: int = 0) -> bool:
        eintrag = self._INPUT(0, self._INPUT._U(mi=self._MOUSEINPUT(0, 0, daten, flags, 0, 0)))
        return self._u.SendInput(1, self._ct.byref(eintrag), self._ct.sizeof(self._INPUT)) == 1

    def maus_bewegen(self, x: int, y: int) -> bool:
        """Über SendInput (absolut, über den ganzen virtuellen Desktop): so trägt die Bewegung das Merkmal „injiziert“ und ist für die Übernahme-Erkennung als Eingabe der Hände erkennbar
        (SetCursorPos tut das unter Wine nicht)."""
        vx, vy, vb, vh = (self._u.GetSystemMetrics(m) for m in (76, 77, 78, 79))
        if vb <= 1 or vh <= 1:
            return bool(self._u.SetCursorPos(int(x), int(y)))
        nx, ny = ((int(x) - vx) * 65536 + vb - 1) // vb, ((int(y) - vy) * 65536 + vh - 1) // vh
        eintrag = self._INPUT(0, self._INPUT._U(mi=self._MOUSEINPUT(nx, ny, 0, 0x0001 | 0x8000 | 0x4000, 0, 0)))  # MOVE | ABSOLUTE | VIRTUALDESK
        return self._u.SendInput(1, self._ct.byref(eintrag), self._ct.sizeof(self._INPUT)) == 1

    def maus_taste(self, taste: str, runter: bool) -> bool:
        return self._maus(self._MOUSEEVENTF[(taste, runter)])

    def rad(self, dy: int) -> bool:
        return self._maus(self.MOUSEEVENTF_WHEEL, -120 * dy)  # positiv (nach unten) = Rad zum Nutzer = negative Daten

    def taste(self, vk: int, runter: bool) -> bool:
        from .tasten_senden import windows_sendinput

        return windows_sendinput([(vk, 0, 0 if runter else 0x0002)]) == 1

    def text(self, text: str) -> int:
        from .tasten_senden import text_ereignisse, windows_sendinput

        return windows_sendinput(text_ereignisse(text))

    def maus_position(self) -> tuple[int, int]:
        p = self._wt.POINT()
        self._u.GetCursorPos(self._ct.byref(p))
        return p.x, p.y

    def fenster_am_punkt(self, x: int, y: int) -> int | None:
        h = self._u.WindowFromPoint(self._wt.POINT(int(x), int(y)))
        if not h:
            return None
        wurzel = self._u.GetAncestor(h, 2)  # GA_ROOT
        return int(wurzel or h)

    def tastatur_fokus(self) -> int | None:
        h = self._u.GetForegroundWindow()
        return int(h) if h else None

    def fokus_geben(self, kennung: int) -> bool:
        """Windows verweigert den Vordergrundwechsel oft (Foreground-Lock). Erst der einfache Versuch; hilft er nicht, einmal die Eingabewarteschlange des Vordergrund-Threads teilen
        (AttachThreadInput), erneut versuchen und sofort wieder lösen. Das Ergebnis zählt erst, wenn das Ziel danach wirklich vorn steht."""
        ziel = int(kennung)
        if self._u.SetForegroundWindow(ziel) and self.tastatur_fokus() == ziel:
            return True
        ct = self._ct
        k = ct.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentThreadId.restype = ct.c_uint32
        self._u.GetWindowThreadProcessId.argtypes, self._u.GetWindowThreadProcessId.restype = [ct.c_void_p, ct.c_void_p], ct.c_uint32
        self._u.AttachThreadInput.argtypes, self._u.AttachThreadInput.restype = [ct.c_uint32, ct.c_uint32, ct.c_int], ct.c_int
        vorn = self._u.GetForegroundWindow()
        eigener, fremder = k.GetCurrentThreadId(), (self._u.GetWindowThreadProcessId(vorn, None) if vorn else 0)
        angehaengt = bool(fremder and fremder != eigener and self._u.AttachThreadInput(eigener, fremder, 1))
        try:
            self._u.SetForegroundWindow(ziel)
        finally:
            if angehaengt:
                self._u.AttachThreadInput(eigener, fremder, 0)
        return self.tastatur_fokus() == ziel


# ---- Engine -------------------------------------------------------------------------------------------------------------
class HaendeEngine:
    def __init__(self, backend: Backend, *, not_aus=None, ziel_stand: Callable[[str], ZielStand | None], ziel_kennung: Callable[[str], int | None],
                 uhr: Callable[[], float] = time.monotonic, jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000), schlafen: Callable[[float], None] = time.sleep,
                 protokoll: Callable[[dict], None] | None = None, notaus_vk: int = 0x7B):
        self.backend, self.not_aus = backend, not_aus
        self._ziel_stand, self._ziel_kennung = ziel_stand, ziel_kennung
        self._uhr, self._jetzt_ms, self._schlafen, self._protokoll = uhr, jetzt_ms, schlafen, protokoll
        self.notaus_vk = notaus_vk
        self.gedrueckt: set[tuple[str, object]] = set()  # ("maus", taste) und ("taste", vk), die die Engine gedrückt hält
        self._abbruch = threading.Event()
        self._sperre = threading.RLock()
        self.verbindung = True
        self.daniel_uebernimmt = False
        self.gesendet_ereignisse = 0
        self.zeiger_gesendet = 0  # Zeiger- und Tastenereignisse der Maus, die diese Engine gesendet hat (Gegenstück für den Beobachter der Übernahme)
        self.letzte_sendung = 0.0
        self.busy = False
        self.beobachter = None  # `uebernahme.Uebernahme`, wenn Daniels Eingabe beobachtet wird
        self.menue_freigabe = False  # nur Daniels Wort schaltet das an (Relay); aus = jede Menü-Aktion wird abgelehnt
        self.menue_offen: Callable[[], "offene_menues.OffenesMenue | None"] = offene_menues.REGISTER.aktuell
        self.loslassen_dauer_ms: list[float] = []
        if self.not_aus is not None:
            self.not_aus.bei_ausloesen(lambda grund: self.abbrechen("not_aus"))

    # ---- Abbruch und Loslassen -----------------------------------------------------------------------------------------------
    def abbrechen(self, grund: str = "abgebrochen") -> None:
        """Von jedem Faden aus: der laufende Auftrag hört beim nächsten Schritt auf; alles Gedrückte wird sofort losgelassen."""
        self._abbruch.set()
        self.alles_loslassen()

    def alles_loslassen(self) -> int:
        t0 = self._uhr()
        n = 0
        for art, wert in list(self.gedrueckt):
            try:
                ok = self.backend.maus_taste(wert, False) if art == "maus" else self.backend.taste(int(wert), False)
            except Exception:
                ok = False
            if ok:
                self.gedrueckt.discard((art, wert))
                n += 1
        self.loslassen_dauer_ms.append((self._uhr() - t0) * 1000)
        return n

    def verbindung_verloren(self) -> None:
        self.verbindung = False
        self.abbrechen("verbindung_weg")

    def verbindung_da(self) -> None:
        self.verbindung = True

    def _stopp(self) -> str:
        if self._abbruch.is_set():
            if self.daniel_uebernimmt:
                return "daniel_uebernimmt"
            return "not_aus" if self.not_aus is not None and self.not_aus.aktiv else ("verbindung_weg" if not self.verbindung else "abgebrochen")
        if self.not_aus is not None and self.not_aus.aktiv:
            return "not_aus"
        if not self.verbindung:
            return "verbindung_weg"
        if self.daniel_uebernimmt:
            return "daniel_uebernimmt"
        return ""

    # ---- Ausführen --------------------------------------------------------------------------------------------------------------
    def ausfuehren(self, auftrag_id: str, aktion: Aktion, *, ziel: str, bezug: Bildbezug | None, lease_grund: str, haende_erlaubt: bool, profil_erlaubt: bool = True) -> Ergebnis:
        t0 = self._uhr()
        with self._sperre:
            if not (self.not_aus is not None and self.not_aus.aktiv) and self.verbindung:
                self._abbruch.clear()  # ein neuer Auftrag beginnt frisch, solange nichts Grundsätzliches stoppt
            if self.beobachter is not None:
                self.beobachter.auftrag_beginnt()
            stand = self._ziel_stand(ziel)
            entscheidung = pruefe(aktion, ziel=ziel, bezug=bezug, stand=stand, lease_grund=lease_grund, not_aus=bool(self.not_aus is not None and self.not_aus.aktiv),
                                  haende_erlaubt=haende_erlaubt, profil_erlaubt=profil_erlaubt, jetzt_ms=self._jetzt_ms(), daniel_uebernimmt=self.daniel_uebernimmt,
                                  verbindung=self.verbindung, menue_freigabe_an=self.menue_freigabe, menue_offen=self.menue_offen())
            if not entscheidung.ok:
                return self._fertig(Ergebnis(auftrag_id, "abgelehnt", entscheidung.grund), aktion, ziel, t0)
            ergebnis = Ergebnis(auftrag_id, "ausgefuehrt", accepted=True)
            self.busy = True
            try:
                self._ausfuehren(aktion, ziel, entscheidung, ergebnis, stand)
            except _Abbruch as stopp:
                ergebnis.status, ergebnis.grund = "abgebrochen", stopp.grund
            except Exception as fehler:
                ergebnis.status, ergebnis.grund = "fehler", "backend_fehler"
                ergebnis.observed["fehler"] = repr(fehler)[:120]
            finally:
                self.alles_loslassen()  # in jedem Fall: nichts bleibt gedrückt
                self.busy = False
                self.letzte_sendung = self._uhr()
            return self._fertig(ergebnis, aktion, ziel, t0)

    def _fertig(self, e: Ergebnis, aktion: Aktion, ziel: str, t0: float) -> Ergebnis:
        e.dauer_ms = int((self._uhr() - t0) * 1000)
        if self._protokoll is not None:
            try:
                self._protokoll({"zeit_ms": self._jetzt_ms(), "ziel": ziel, "aktion": aktion.zu_dict(), "ergebnis": e.zu_dict()})
                e.audited = True
            except Exception:
                e.audited = False
        return e

    def _schritt(self) -> None:
        grund = self._stopp()
        if grund:
            raise _Abbruch(grund)

    def _senden(self, aufruf, ergebnis: Ergebnis, n: int = 1, zeiger: int = 0) -> None:
        """Ruft die Plattformeingabe auf. Die erwartete Zahl eigener Zeigerereignisse wird VOR dem Aufruf gezählt: der Beobachter der Übernahme sieht die Ereignisse sonst früher als den Zähler."""
        self.letzte_sendung = self._uhr()
        self.zeiger_gesendet += zeiger  # zählt auch, wenn das System „nein“ sagt: vorsichtshalber
        ok = aufruf()
        self.letzte_sendung = self._uhr()
        if not ok:
            raise RuntimeError("system hat die eingabe nicht angenommen")
        ergebnis.delivered += n
        self.gesendet_ereignisse += n

    def _am_punkt_ist_ziel(self, ziel: str, punkt: tuple[int, int]) -> bool:
        return self.backend.gleich(self.backend.fenster_am_punkt(*punkt), self._ziel_kennung(ziel))

    def _fokus_sichern(self, ziel: str) -> str:
        kennung = self._ziel_kennung(ziel)
        if kennung is None:
            return "ziel_weg"
        if not self.backend.gleich(self.backend.tastatur_fokus(), kennung):
            if not self.backend.fokus_geben(int(kennung)):
                return "fokus_nicht_erreichbar"
            self._schlafen(0.05)
            if not self.backend.gleich(self.backend.tastatur_fokus(), kennung):
                return "fokus_nicht_erreichbar"
        return ""

    def _ausfuehren(self, a: Aktion, ziel: str, entscheidung: Entscheidung, ergebnis: Ergebnis, stand: ZielStand) -> None:
        if a.art == "menue" and a.text.strip().casefold() in menue_freigabe.SCHLIESSEN_NAMEN:
            offen = self.menue_offen()
            if offen is None or offen.schliessen is None:
                raise _Abbruch("menue_nicht_offen")
            self._schritt()
            offen.schliessen()  # der Körper schließt sein eigenes Menü; es wird keine Taste simuliert
            ergebnis.delivered += 1
            ergebnis.observed["menue"] = "geschlossen"
            return
        if a.art == "menue":
            offen = self.menue_offen()  # noch einmal frisch: das Menü kann sich seit der Prüfung geschlossen haben
            if offen is None or not self.backend.gleich(self.backend.fenster_am_punkt(*entscheidung.start), offen.kennung):
                raise _Abbruch("punkt_verdeckt")
            self._schritt()
            self._senden(lambda: self.backend.maus_bewegen(*entscheidung.start), ergebnis, zeiger=1)
            self.gedrueckt.add(("maus", "links"))
            self._senden(lambda: self.backend.maus_taste("links", True), ergebnis, zeiger=1)
            self._senden(lambda: self.backend.maus_taste("links", False), ergebnis, zeiger=1)
            self.gedrueckt.discard(("maus", "links"))
            self._schlafen(0.03)
            ergebnis.observed["zeiger"] = list(self.backend.maus_position())
            return
        if a.art in ("klick", "doppelklick", "ziehen", "rad"):
            if not self._am_punkt_ist_ziel(ziel, entscheidung.start):
                raise _Abbruch("punkt_verdeckt")
        if a.art in ("klick", "doppelklick"):
            for _ in range(2 if a.art == "doppelklick" else 1):
                self._schritt()
                self._senden(lambda: self.backend.maus_bewegen(*entscheidung.start), ergebnis, zeiger=1)
                self.gedrueckt.add(("maus", a.taste))  # vor dem Senden eintragen: auch wenn das System „nein“ sagt, wird beim Aufräumen losgelassen
                self._senden(lambda: self.backend.maus_taste(a.taste, True), ergebnis, zeiger=1)
                self._senden(lambda: self.backend.maus_taste(a.taste, False), ergebnis, zeiger=1)
                self.gedrueckt.discard(("maus", a.taste))
                self._schlafen(0.03)
            ergebnis.observed["zeiger"] = list(self.backend.maus_position())
        elif a.art == "rad":
            self._schritt()
            self._senden(lambda: self.backend.maus_bewegen(*entscheidung.start), ergebnis, zeiger=1)
            self._senden(lambda: self.backend.rad(a.dy), ergebnis, abs(a.dy), zeiger=self.backend.rad_ereignisse(a.dy))
            ergebnis.observed["zeiger"] = list(self.backend.maus_position())
        elif a.art == "ziehen":
            if entscheidung.ende is not None and not self._am_punkt_ist_ziel(ziel, entscheidung.ende):
                raise _Abbruch("punkt_verdeckt")
            self._schritt()
            self._senden(lambda: self.backend.maus_bewegen(*entscheidung.start), ergebnis, zeiger=1)
            self.gedrueckt.add(("maus", a.taste))
            self._senden(lambda: self.backend.maus_taste(a.taste, True), ergebnis, zeiger=1)
            schritte = max(2, a.dauer_ms // SCHRITT_MS)
            (x0, y0), (x1, y1) = entscheidung.start, entscheidung.ende
            for i in range(1, schritte + 1):
                self._schritt()
                neu = self._ziel_stand(ziel)  # wird das Ziel mitten im Ziehen verschoben, hört das Ziehen auf
                if neu is None or not neu.vorhanden or neu.rect != stand.rect:
                    raise _Abbruch("geometrie_geaendert")
                self._senden(lambda: self.backend.maus_bewegen(x0 + (x1 - x0) * i // schritte, y0 + (y1 - y0) * i // schritte), ergebnis, zeiger=1)
                self._schlafen(SCHRITT_MS / 1000)
            self._senden(lambda: self.backend.maus_taste(a.taste, False), ergebnis, zeiger=1)
            self.gedrueckt.discard(("maus", a.taste))
            ergebnis.observed["zeiger"] = list(self.backend.maus_position())
            ergebnis.observed["erwartet"] = [x1, y1]
        elif a.art == "tippen":
            self._schritt()
            fehler = self._fokus_sichern(ziel)
            if fehler:
                raise _Abbruch(fehler)
            text = a.text.replace("\r", " ").replace("\n", " ")
            for i in range(0, len(text), TEXT_STUECK):
                self._schritt()
                if not self.backend.gleich(self.backend.tastatur_fokus(), self._ziel_kennung(ziel)):
                    raise _Abbruch("fokus_verloren")
                stueck = text[i:i + TEXT_STUECK]
                n = self.backend.text(stueck)
                if n < 1:
                    raise RuntimeError("text nicht angenommen")
                ergebnis.delivered += n
                self.gesendet_ereignisse += n
            ergebnis.observed["zeichen"] = len(text)
        elif a.art == "taste":
            teile = kombi_zu_vk(a.kombi)
            if teile is None:
                raise _Abbruch("aktion_ungueltig")
            mods, vk = teile
            if vk == self.notaus_vk:
                raise _Abbruch("notaus_taste")
            self._schritt()
            fehler = self._fokus_sichern(ziel)
            if fehler:
                raise _Abbruch(fehler)
            for m in mods:
                self._schritt()
                self.gedrueckt.add(("taste", m))
                self._senden(lambda: self.backend.taste(m, True), ergebnis)
            self._schritt()
            self.gedrueckt.add(("taste", vk))
            self._senden(lambda: self.backend.taste(vk, True), ergebnis)
            self._senden(lambda: self.backend.taste(vk, False), ergebnis)
            self.gedrueckt.discard(("taste", vk))
            for m in reversed(mods):
                self._senden(lambda: self.backend.taste(m, False), ergebnis)
                self.gedrueckt.discard(("taste", m))
            ergebnis.observed["kombi"] = a.kombi


class _Abbruch(Exception):
    def __init__(self, grund: str):
        super().__init__(grund)
        self.grund = grund
