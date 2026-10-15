"""Die schwebenden Bild-Elemente (G08) eines Gates: je Objekt ein eigenes, direkt anfassbares Fenster, das mit dem Dokument im Gleichklang bleibt.

Das Dokument ist die Wahrheit. Der Takt gleicht beides ab:
* Dokument → Fenster: Ort, Größe und Deckkraft aus den Gate-Koordinaten (das Fenster folgt dem Gate, verschwindet mit ihm beim Minimieren oder Schließen);
* Fenster → Dokument: hat Daniel das Fenster verschoben oder in der Größe geändert und es steht still, wird das als EIN Befehl ins Dokument geschrieben
  (mit dem Seitenverhältnis des Bildes), damit Rückgängig, Speichern und Komposition für Agenten dasselbe wissen.
Objekte nur für Agenten (`bildschirm=False`) dürfen als Fenster nur stehen, wo Windows das Fenster aus der Aufnahme ausnehmen kann, sonst bleiben sie unsichtbar
(bearbeitbar im Zeichenmodus): so sickert nichts in das Basisbild anderer Agenten.
"""

from __future__ import annotations

import io
from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image

from . import stil
from .objekte import Dokument, Objekt

Rechteck = tuple[int, int, int, int]
MIN_B, MIN_H = 64, 48


def bild_bgr(png: bytes) -> tuple[bytes, int, int] | None:
    try:
        with Image.open(io.BytesIO(png)) as roh:
            roh = roh.convert("RGBA")
        grund = Image.new("RGBA", roh.size, (28, 28, 28, 255))
        grund.alpha_composite(roh)
        rgb = grund.convert("RGB")
        return rgb.tobytes("raw", "BGR"), rgb.size[0], rgb.size[1]
    except Exception:
        return None


def objekt_rechteck(o: Objekt, gate: Rechteck) -> Rechteck:
    gb, gh = gate[2] - gate[0], gate[3] - gate[1]
    xs, ys = [p[0] for p in o.punkte], [p[1] for p in o.punkte]
    links, oben = gate[0] + round(min(xs) * gb), gate[1] + round(min(ys) * gh)
    rechts, unten = gate[0] + round(max(xs) * gb), gate[1] + round(max(ys) * gh)
    return links, oben, max(rechts, links + MIN_B), max(unten, oben + MIN_H)


@dataclass
class _Stand:
    fenster: object
    schluessel: str
    gesetzt: Rechteck
    zuletzt: Rechteck
    deckkraft: int
    bild_b: int
    bild_h: int
    schutz: bool = True
    ausnahme: bool | None = None


class BildElemente:
    def __init__(self, fenster_bauen: Callable[..., object], menue: Callable[[str, str, int, int], None] = lambda oid, schluessel, x, y: None,
                 modifikator: Callable[[], bool] | None = None):
        """`fenster_bauen(x, y, b, h, bild=(bgr, b, h), name=…, bei_deckkraft=…, bei_ausblenden=…, bei_menue=…, modifikator=…)`."""
        self._bauen, self._menue, self._modifikator = fenster_bauen, menue, modifikator
        self.stand: dict[str, _Stand] = {}

    def tick(self, schluessel: str, dok: Dokument, da: bool, rect: Rechteck | None, editor_offen: bool) -> None:
        vorhanden = set()
        for o in dok.schwebende():
            vorhanden.add(o.id)
            if not self._soll(o, da, rect, editor_offen):
                self._verbergen(o.id)
                continue
            st = self.stand.get(o.id)
            if st is None:
                st = self._neu(o, schluessel, dok, rect)
                if st is None:
                    continue
            self._abgleichen(o, st, dok, rect)
        for oid in [i for i, st in self.stand.items() if st.schluessel == schluessel and i not in vorhanden]:
            self._schliessen(oid)

    def _soll(self, o: Objekt, da: bool, rect, editor_offen: bool) -> bool:
        if not (o.sichtbar and da and rect is not None and not editor_offen):
            return False
        gb, gh = rect[2] - rect[0], rect[3] - rect[1]
        return gb >= 8 and gh >= 8

    def _neu(self, o: Objekt, schluessel: str, dok: Dokument, rect: Rechteck) -> _Stand | None:
        bgr = bild_bgr(o.bild or b"")
        if bgr is None:
            return None
        ziel = objekt_rechteck(o, rect)
        fenster = self._bauen(ziel[0], ziel[1], ziel[2] - ziel[0], ziel[3] - ziel[1], bild=bgr, name="Bild",
                              bei_deckkraft=lambda p, i=o.id, d=dok: self._deckkraft_aus_fenster(d, i, p),
                              bei_ausblenden=lambda i=o.id, d=dok: d.aendern([i], sichtbar=False),
                              bei_menue=lambda x, y, i=o.id, s=schluessel: self._menue(i, s, x, y),
                              modifikator=self._modifikator)
        st = _Stand(fenster, schluessel, fenster.rechteck(), fenster.rechteck(), -1, bgr[1], bgr[2])
        self.stand[o.id] = st
        return st

    def _deckkraft_aus_fenster(self, dok: Dokument, oid: str, prozent: int) -> None:
        st = self.stand.get(oid)
        if st is not None:
            st.deckkraft = prozent
        dok.aendern([oid], deckkraft=prozent)

    def _abgleichen(self, o: Objekt, st: _Stand, dok: Dokument, rect: Rechteck) -> None:
        f = st.fenster
        # Schutz vor der Aufnahme: nur-für-Agenten-Bilder dürfen nur stehen, wo Windows das Fenster ausnimmt
        if st.ausnahme != (not o.bildschirm):
            st.ausnahme = not o.bildschirm
            st.schutz = bool(f.aufnahme_ausnehmen(st.ausnahme)) or o.bildschirm
        if not o.bildschirm and not st.schutz:
            f.verberge()
            return
        cur = f.rechteck()
        if cur != st.gesetzt:  # Daniel hat das Fenster angefasst: wenn es stillsteht, ins Dokument schreiben
            if cur != st.zuletzt:
                st.zuletzt = cur
                return
            b = max(MIN_B, cur[2] - cur[0])
            h = max(MIN_H, round(b * st.bild_h / max(1, st.bild_b)))  # Seitenverhältnis des Bildes bleibt
            if (cur[2] - cur[0], cur[3] - cur[1]) != (b, h):
                f.verschiebe(cur[0], cur[1], b, h)
                cur = f.rechteck()
            gb, gh = rect[2] - rect[0], rect[3] - rect[1]
            punkte = [((cur[0] - rect[0]) / gb, (cur[1] - rect[1]) / gh), ((cur[2] - rect[0]) / gb, (cur[3] - rect[1]) / gh)]
            dok.aendern([o.id], punkte=punkte)
            st.gesetzt = st.zuletzt = cur
        else:
            ziel = objekt_rechteck(o, rect)
            if ziel != cur:
                f.verschiebe(ziel[0], ziel[1], ziel[2] - ziel[0], ziel[3] - ziel[1])
                st.gesetzt = st.zuletzt = f.rechteck()
        if st.deckkraft != o.deckkraft:
            f.prozent_setzen(o.deckkraft)
            st.deckkraft = o.deckkraft
        if not f.sichtbar():
            f.zeige(aktivieren=False)

    def _verbergen(self, oid: str) -> None:
        st = self.stand.get(oid)
        if st is not None and st.fenster.sichtbar():
            st.fenster.verberge()

    def _schliessen(self, oid: str) -> None:
        st = self.stand.pop(oid, None)
        if st is not None:
            st.fenster.schliessen()

    def schliessen(self) -> None:
        for oid in list(self.stand):
            self._schliessen(oid)
