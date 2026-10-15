"""Der laufende Bilderstrom an die Agenten (R045 sparsam, R120: nur nach der Bindung).

Sobald ein Agent ein Ziel gebunden hat (Desktop, Fenster, Spiel), bekommt er in festen Abständen ein frisches Bild genau dieses Ziels:
alle `takt_s` Sekunden ein Bildschirmfoto, je Agent auf sein Ziel zugeschnitten (bei einem Fenster folgt der Ausschnitt dem Fenster),
als JPEG über das Relay. Ein Bild, das sich seit dem letzten nicht verändert hat, wird nicht noch einmal gesendet, nur alle
`keepalive_s` Sekunden ein Lebenszeichen. Damit sehen die Agenten auch Daniels Worte (Ticker), die Banner und den Chat, die als Fenster auf
dem Bildschirm stehen. Not-Aus stoppt alles. Je Agent abschaltbar.
"""

from __future__ import annotations

import base64
import hashlib
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from . import bild
from .fensteraufnahme import AUFNAHME_AUSSCHNITT, AUFNAHME_FENSTER, FensterAufnahme

Rechteck = tuple[int, int, int, int]
TAKT_S, KEEPALIVE_S = 2.0, 5.0  # Keepalive deutlich unter dem Höchstalter des Bezugsbilds im Käfig (MAX_BILD_ALTER_MS = 15 s): bei gleicher Länge wäre ein unverändertes Fenster regelmäßig „veraltet“
STUMM_MELDUNG_S, HERZSCHLAG_S = 60.0, 60.0  # Log-Drossel je Grund; Lebenszeichen des Fadens


VERLAUF = 16  # so viele zuletzt gesendete Bilder je Agent merkt sich der Körper (für die Hände: auf welchem Bild hat der Agent gezielt?)


@dataclass(frozen=True)
class Gesendet:
    """Was zu einem gesendeten Bild gehört: damit Koordinaten des Agenten später auf den Bildschirm zurückgerechnet werden können."""

    seq: int
    captured_at_ms: int
    breite: int  # Pixel des gesendeten Bildes
    hoehe: int
    fenster_rect: Rechteck | None  # das Fensterrechteck zur Aufnahmezeit (None bei einem Desktop-Ziel)
    bild_rect: Rechteck  # der Bildschirmbereich, den das Bild zeigt
    hwnd: int | None


@dataclass
class Ziel:
    hwnd: int | None  # None = der ganze Bildschirm (oder `rect`)
    rect: Rechteck | None = None
    an: bool = True
    letzter_hash: bytes | None = None
    letzte_zeit: float = -1e9
    gesendet: int = 0
    seq: int = 0  # Folge je Ziel: beginnt mit jedem neuen Binden bei 0 und steigt mit jedem gesendeten Bild
    uebersprungen: int = 0


def ausschnitt_hash(raw: bytes, breite: int, ausschnitt: Rechteck) -> bytes:
    """Kurzer Fingerabdruck nur des Ausschnitts (Zeile für Zeile, ohne den ganzen Frame zu kopieren)."""
    links, oben, rechts, unten = ausschnitt
    h = hashlib.blake2b(digest_size=8)
    ansicht = memoryview(raw)
    for y in range(oben, unten):
        anfang = (y * breite + links) * 4
        h.update(ansicht[anfang:anfang + (rechts - links) * 4])
    return h.digest()


class Bilderstrom:
    def __init__(self, *, erfassen: Callable[[], tuple[bytes, int, int]], bildschirm: Callable[[], Rechteck],
                 fenster_rect: Callable[[int], Rechteck | None],
                 senden: Callable[[str, dict], bool],
                 kodieren: Callable[[bytes, int, int, Rechteck], tuple[bytes, int, int]] = bild.bgra_zu_jpeg,
                 gesperrt: Callable[[], bool] = lambda: False,
                 ziel_verschwunden: Callable[[str], None] = lambda tid: None,
                 komposit: Callable[[str, Rechteck, Rechteck], object] | None = None,
                 fehler: Callable[[str], None] = lambda text: None,
                 fenster_bild: Callable[[int], tuple[bytes, int, int] | None] | None = None,
                 ziel_sichtbar: Callable[[int], bool] = lambda hwnd: True,
                 uhr: Callable[[], float] = time.monotonic, jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000),
                 takt_s: float = TAKT_S, keepalive_s: float = KEEPALIVE_S):
        self._erfassen, self._bildschirm, self._fenster_rect, self._senden = erfassen, bildschirm, fenster_rect, senden
        self._kodieren, self._gesperrt = kodieren, gesperrt
        self._ziel_verschwunden, self._fehler = ziel_verschwunden, fehler
        self._komposit = komposit  # (Agent, Gate, Ausschnitt in Bildschirmkoordinaten) → Komposit | None: Objekte nur für diesen Agenten (G08)
        self._uhr, self._jetzt_ms = uhr, jetzt_ms
        self.aufnahme = FensterAufnahme(fenster_bild)  # G06.7: Bild genau dieses Fensters, auch verdeckt; sonst sichtbarer Rückfall
        self._ziel_sichtbar = ziel_sichtbar  # minimierte Ziele werden nicht gefordert und bekommen keine Bilder
        self.takt_s, self.keepalive_s = takt_s, keepalive_s
        self.ziele: dict[str, Ziel] = {}
        self.verlauf: dict[str, deque[Gesendet]] = {}
        self._sperre = threading.Lock()
        self._takt_sperre = threading.RLock()  # ein Durchlauf zur Zeit: der Takt-Faden und `sofort_senden` (aus anderen Fäden) teilen sich Folgenummern und Verlauf
        self._stop = threading.Event()
        self._stumm_zuletzt: dict[tuple[str, str], float] = {}  # (Agent, Grund) → letztes Auftreten, für die Ampel
        self._stumm_gemeldet: dict[tuple[str, str], float] = {}  # (Agent, Grund) → letzte Meldung; keine Flut, aber auch keine Stille
        self._herzschlag_zeit = 0.0
        self._herzschlag_takte = 0

    # ---- Verwalten -------------------------------------------------------------------------------------------------
    def binden(self, tid: str, hwnd: int | None, rect: Rechteck | None = None) -> None:
        """Neues Ziel für diesen Agenten (ersetzt ein altes); das erste Bild kommt beim nächsten Takt."""
        with self._sperre:
            alt = self.ziele.get(tid)
            self.ziele[tid] = Ziel(hwnd, rect, alt.an if alt is not None else True)
            self.verlauf.pop(tid, None)  # ein neues Ziel: alte Bilder sind keine Grundlage mehr für Koordinaten

    def loesen(self, tid: str) -> None:
        with self._sperre:
            self.ziele.pop(tid, None)
            self.verlauf.pop(tid, None)

    def bezug(self, tid: str, seq: int | None) -> Gesendet | None:
        """Das gesendete Bild mit dieser Folgenummer (None = das letzte); None, wenn es nicht (mehr) gemerkt ist."""
        with self._sperre:
            liste = self.verlauf.get(tid)
            if not liste:
                return None
            if seq is None:
                return liste[-1]
            return next((g for g in reversed(liste) if g.seq == seq), None)

    def an(self, tid: str) -> bool:
        ziel = self.ziele.get(tid)
        return bool(ziel and ziel.an)

    def auffrischen(self, tid: str) -> bool:
        """Behebe-Knopf „Bilder neu starten“: Strom an, nächstes Bild sofort, alte Bezüge verwerfen. False, wenn es kein Ziel gibt."""
        with self._sperre:
            ziel = self.ziele.get(tid)
            if ziel is None:
                return False
            ziel.an, ziel.letzter_hash, ziel.letzte_zeit = True, None, -1e9
            self._stumm_gemeldet = {k: v for k, v in self._stumm_gemeldet.items() if k[0] != tid}  # neue Gründe sofort wieder melden
            return True

    def sofort(self, tid: str) -> bool:
        """Ein Agent fragt per `see` nach einem frischen Bild: beim nächsten Takt wird gesendet, auch wenn sich nichts verändert hat (statt auf den
        Keepalive zu warten). Der Strom bleibt sonst, wie er ist; False, wenn es kein Ziel gibt."""
        with self._sperre:
            ziel = self.ziele.get(tid)
            if ziel is None or not ziel.an:
                return False
            ziel.letzte_zeit = -1e9
            return True

    def probleme(self, tid: str, innerhalb_s: float = 8.0) -> frozenset:
        """Gründe, aus denen dieses Ziel in den letzten Sekunden kein Bild bekam (der Takt ist 2 s, der Grund wird bei jedem Takt gesetzt)."""
        jetzt = self._uhr()
        return frozenset(g for (t, g), zeit in list(self._stumm_zuletzt.items()) if t == tid and jetzt - zeit <= innerhalb_s)

    def stand(self, tid: str) -> dict | None:
        """Für die Ampel: ist ein Ziel gebunden, ist der Strom an, und wie alt ist das letzte gesendete Bild (None = noch keins)."""
        with self._sperre:
            ziel = self.ziele.get(tid)
            if ziel is None:
                return None
            alter = None if ziel.letzte_zeit < -1e8 else max(0.0, self._uhr() - ziel.letzte_zeit)
            return {"an": ziel.an, "hwnd": ziel.hwnd, "alter_s": alter, "gesendet": ziel.gesendet}

    def umschalten(self, tid: str) -> bool:
        with self._sperre:
            ziel = self.ziele.get(tid)
            if ziel is None:
                return False
            ziel.an = not ziel.an
            ziel.letzter_hash = None  # beim Wiedereinschalten sofort ein frisches Bild
            return ziel.an

    # ---- Keine stillen Zweige --------------------------------------------------------------------------------------
    def _stumm(self, tid: str, grund: str, detail: str = "") -> None:
        """Ein Ziel bekommt gerade kein Bild: Grund ins Log, je Agent und Grund höchstens einmal pro Minute."""
        jetzt = self._uhr()
        self._stumm_zuletzt[(tid, grund)] = jetzt
        if jetzt - self._stumm_gemeldet.get((tid, grund), -1e9) >= STUMM_MELDUNG_S:
            self._stumm_gemeldet[(tid, grund)] = jetzt
            self._fehler(f"Bilderstrom: kein Bild für {tid}: {grund}{(' (' + detail + ')') if detail else ''}"[:200])

    def _herzschlag(self) -> None:
        """Alle 60 Sekunden eine Lebenszeichen-Zeile: Fehlt sie im Log, hängt der Faden selbst."""
        self._herzschlag_takte += 1
        jetzt = self._uhr()
        if jetzt - self._herzschlag_zeit < HERZSCHLAG_S:
            return
        self._herzschlag_zeit = jetzt
        with self._sperre:
            ziele = {tid: ("an" if z.an else "AUS", z.hwnd, z.gesendet, z.uebersprungen) for tid, z in self.ziele.items()}
        self._fehler(f"Bilderstrom lebt: Takte={self._herzschlag_takte}, Ziele={ziele}"[:200])
        self._herzschlag_takte = 0

    # ---- Ein Takt --------------------------------------------------------------------------------------------------
    def tick(self) -> int:
        """Ein Durchlauf; liefert, wie viele Bilder gesendet wurden."""
        with self._takt_sperre:
            return self._tick()

    def sofort_senden(self, tids: list[str]) -> int:
        """Ohne Wenn und Aber: jedem dieser Agenten **jetzt** ein frisches Bild senden, auch bei unverändertem Fenster und ohne auf den Takt zu warten.
        Für „ein Agent hat in seine Raute gesendet, alle anderen im selben Gate sehen sofort hin“. Agenten ohne Ziel oder mit ausgeschaltetem Strom
        bekommen nichts (sie haben keine Augen an); die Anzahl der gesendeten Bilder kommt zurück."""
        with self._takt_sperre:
            nur = set()
            with self._sperre:
                for tid in tids:
                    ziel = self.ziele.get(tid)
                    if ziel is not None and ziel.an:
                        ziel.letzter_hash, ziel.letzte_zeit = None, -1e9
                        nur.add(tid)
            return self._tick(nur=nur) if nur else 0

    def _tick(self, nur: set[str] | None = None) -> int:
        self._herzschlag()
        if self._gesperrt():
            self._stumm("alle", "gesperrt", "Not-Aus aktiv")
            return 0
        with self._sperre:
            aktive = [(tid, ziel) for tid, ziel in self.ziele.items() if ziel.an and (nur is None or tid in nur)]
            ausgeschaltet = [tid for tid, ziel in self.ziele.items() if not ziel.an]
        for tid in ausgeschaltet:
            self._stumm(tid, "ziel_aus", "an=False: per Knopf (Augen aus)")
        if not aktive:
            return 0
        raw, breite, hoehe = self._erfassen()
        ursprung = self._bildschirm()[:2]
        gesendet = 0
        for tid, ziel in aktive:
            rect = self._fenster_rect(ziel.hwnd) if ziel.hwnd is not None else (ziel.rect or self._bildschirm())
            if rect is None:
                # Die Augen dürfen nie ausfallen: Ist das Fenster weg, geht der Strom sofort auf den ganzen
                # Desktop. Der Knopf-Zustand `an` bleibt unberührt; ein verschwundenes Fenster schaltet nichts mehr aus.
                self._stumm(tid, "fenster_weg", f"hwnd={ziel.hwnd}, Bilder kommen jetzt vom ganzen Desktop")
                ziel.hwnd, ziel.rect, ziel.letzter_hash = None, None, None
                with self._sperre:
                    self.verlauf.pop(tid, None)  # Koordinaten des alten Fensters taugen nicht mehr als Bezug
                self._ziel_verschwunden(tid)
                continue
            if ziel.hwnd is not None and not self._ziel_sichtbar(ziel.hwnd):
                self._stumm(tid, "ziel_unsichtbar", f"hwnd={ziel.hwnd} minimiert oder nicht eingeblendet")
                continue
            quelle, grund = AUFNAHME_AUSSCHNITT, ""
            bgra_, b_, h_, ausschnitt = raw, breite, hoehe, bild.ausschnitt_im_frame(rect, ursprung, breite, hoehe)
            if ziel.hwnd is not None:
                fb = self.aufnahme.holen(ziel.hwnd)
                if fb is not None:
                    quelle, bgra_, b_, h_, ausschnitt = AUFNAHME_FENSTER, fb.bgra, fb.breite, fb.hoehe, (0, 0, fb.breite, fb.hoehe)
                else:
                    grund = self.aufnahme.letzter_grund
                    self._stumm(tid, "aufnahme_rueckfall", f"{grund or 'kein Fensterbild'}; Bildschirmausschnitt statt Fensterbild")
            if ausschnitt is None:
                self._stumm(tid, "ausschnitt_leer", f"rect={rect}")
                continue
            kompo = None
            if self._komposit is not None:
                if quelle == AUFNAHME_FENSTER:
                    ausschnitt_schirm = rect
                else:
                    ausschnitt_schirm = (ausschnitt[0] + ursprung[0], ausschnitt[1] + ursprung[1], ausschnitt[2] + ursprung[0], ausschnitt[3] + ursprung[1])
                kompo = self._komposit(tid, rect, ausschnitt_schirm)
            fingerabdruck = ausschnitt_hash(bgra_, b_, ausschnitt) + (kompo.token if kompo is not None else b"") + quelle.encode()
            jetzt = self._uhr()
            if fingerabdruck == ziel.letzter_hash and jetzt - ziel.letzte_zeit < self.keepalive_s:
                ziel.uebersprungen += 1
                continue
            if kompo is not None:
                daten, b, h = self._kodieren(bgra_, b_, h_, ausschnitt, nachbearbeiten=kompo.anwenden)
            else:
                daten, b, h = self._kodieren(bgra_, b_, h_, ausschnitt)
            payload = {"mime": "image/jpeg", "data": base64.b64encode(daten).decode(), "source": "capture",
                       "captured_at_ms": self._jetzt_ms(), "width": b, "height": h, "terminal_id": tid,
                       "aufnahme": quelle, "seq": ziel.seq}
            if grund:
                payload["fallback_grund"] = grund
            if self._senden(tid, payload):
                bildbereich = rect if quelle == AUFNAHME_FENSTER else (ausschnitt[0] + ursprung[0], ausschnitt[1] + ursprung[1], ausschnitt[2] + ursprung[0], ausschnitt[3] + ursprung[1])
                with self._sperre:
                    self.verlauf.setdefault(tid, deque(maxlen=VERLAUF)).append(
                        Gesendet(ziel.seq, payload["captured_at_ms"], b, h, rect if ziel.hwnd is not None else None, bildbereich, ziel.hwnd))
                ziel.letzter_hash, ziel.letzte_zeit = fingerabdruck, jetzt
                ziel.gesendet += 1
                ziel.seq += 1
                gesendet += 1
            else:
                self._stumm(tid, "senden_abgelehnt", "strom_senden gab False: Sender fehlt, Status nicht verbunden, Nur-Terminal oder Warteschlange voll")
        return gesendet

    # ---- Faden -----------------------------------------------------------------------------------------------------
    def starten(self) -> None:
        def lauf() -> None:
            while not self._stop.wait(self.takt_s):
                try:
                    self.tick()
                except Exception as fehler:  # ein Aussetzer (Aufnahme scheitert kurz) darf den Strom nicht beenden
                    self._fehler(f"Bilderstrom: {fehler!r}"[:200])

        threading.Thread(target=lauf, name="bilderstrom", daemon=True).start()

    def stoppen(self) -> None:
        self._stop.set()
