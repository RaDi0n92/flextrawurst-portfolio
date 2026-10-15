"""Der WorldDOM-Dienst des Körpers (G11): misst, löst auf, handelt und zeigt — für die Aufträge der Agenten.

Der Dienst fasst zusammen, was die Bausteine einzeln können: echte Struktur (Browser über CDP, Programme über Bedienungshilfen), aus dem Bild Erschlossenes, bewusst Angelegtes
(`weltdom.py`, `weltdom_quellen.py`), das Handeln mit Rücklese (`weltdom_aktion.py`) und Zeigegesten (`zeigegeste.py`). Alles Plattformabhängige kommt als Funktion herein.

Jede Antwort nennt, woher die Knoten kamen und was **nicht** verfügbar war (`quellen`): kein Browser-Anschluss, keine Bedienungshilfen, kein tesseract — nie eine leere Liste, die nach „nichts da“ aussieht.
Handelnde Befehle (`aktion`, `einfuegen`) brauchen die Hände des Agenten (Daniels Schalter) und, wo Koordinaten ins Spiel kommen, Profil, Käfig und Bild der Hände (G10).
"""

from __future__ import annotations

import time
from collections.abc import Callable

from . import eingabe_adapter as ea
from . import steuerprofil, weltdom_quellen as wq, zeigegeste as zg
from .weltdom import Knoten, WeltDom
from .weltdom_aktion import AktionsDienst

MAX_ANTWORT_KNOTEN = 150
MAX_GESTEN = 100


class WeltdomDienst:
    def __init__(self, welt: WeltDom, *, cdp_seite: Callable[[str], object | None] = lambda ziel: None, ui_quelle: Callable[[str], tuple[object, object] | None] = lambda ziel: None,
                 bild: Callable[[str], tuple[bytes, int, int, tuple[int, int, int, int]] | None] = lambda ziel: None, ziel_stand: Callable[[str], ea.ZielStand | None] = lambda ziel: None,
                 bezug: Callable[[str, str, int | None], ea.Bildbezug | None] = lambda tid, ziel, seq: None, haende: object | None = None,
                 overlay: Callable[[str, str, tuple[float, float], str, tuple[str, ...]], str | None] | None = None, jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000),
                 schlafen: Callable[[float], None] = time.sleep, profile=None):
        self.welt = welt
        self.profile = profile
        self._cdp_seite, self._ui_quelle, self._bild, self._ziel_stand, self._bezug = cdp_seite, ui_quelle, bild, ziel_stand, bezug
        self.haende, self._overlay, self._jetzt, self._schlafen = haende, overlay, jetzt_ms, schlafen
        self.gesten: dict[str, zg.Zeigegeste] = {}
        self._aktuelle_bezuege: dict[tuple[str, str], ea.Bildbezug] = {}

    # ---- Messen ------------------------------------------------------------------------------------------------------------------------
    def messen(self, ziel: str, *, bild_erschliessen: bool = True) -> dict:
        """Eine frische Messung aller verfügbaren Quellen. Liefert, was jede Quelle ergab (`ok`, Anzahl oder der Grund fürs Fehlen)."""
        jetzt = self._jetzt()
        quellen: dict[str, str] = {}
        seite = None
        try:
            seite = self._cdp_seite(ziel)
        except Exception as fehler:
            quellen["cdp"] = f"fehler: {fehler.__class__.__name__}"
        if seite is not None:
            try:
                ks = wq.aus_cdp(ziel, seite, jetzt, inhalt_ursprung=wq.seiten_ursprung(seite))
                self.welt.ersetze(ziel, "real", "cdp", ks)
                quellen["cdp"] = f"ok: {len(ks)} Knoten"
            except Exception as fehler:
                quellen["cdp"] = f"fehler: {fehler.__class__.__name__}"
        elif "cdp" not in quellen:
            quellen["cdp"] = "nicht verfügbar: kein Browser-Anschluss für dieses Fenster"
        try:
            q = self._ui_quelle(ziel)
        except Exception as fehler:
            q = None
            quellen["ui"] = f"fehler: {fehler.__class__.__name__}"
        if q is not None:
            quelle, pid = q
            try:
                baum = quelle.baum(pid)
                if baum.status == "ok" and baum.wurzel is not None:
                    from .weltdom import aus_ui_baum

                    ks = aus_ui_baum(ziel, baum.wurzel, quelle.name, pid, jetzt)
                    self.welt.ersetze(ziel, "real", quelle.name, ks)
                    quellen[quelle.name] = f"ok: {len(ks)} Knoten"
                else:
                    quellen[quelle.name] = f"{baum.status}: {baum.grund}"
            except Exception as fehler:
                quellen[quelle.name] = f"fehler: {fehler.__class__.__name__}"
        elif "ui" not in quellen:
            quellen["ui"] = "nicht verfügbar: keine Bedienungshilfen für dieses Fenster"
        if bild_erschliessen:
            aufnahme = None
            try:
                aufnahme = self._bild(ziel)
            except Exception as fehler:
                quellen["bild"] = f"fehler: {fehler.__class__.__name__}"
            if aufnahme is not None:
                bgra, b, h, bereich = aufnahme
                flaechen, hinweis = wq.flaechen_erschliessen(ziel, bgra, b, h, bereich, None, jetzt)
                hinweis2 = wq.flaechen_benennen(flaechen, bgra, b, h) if flaechen else ""
                texte, hinweis3 = wq.beschriftungen_erschliessen(ziel, bgra, b, h, bereich, None, jetzt)
                self.welt.ersetze(ziel, "inferred", "flaeche", flaechen)
                self.welt.ersetze(ziel, "inferred", "ocr", texte)
                quellen["bild"] = f"ok: {len(flaechen)} Flächen, {len(texte)} Textstellen" + "".join(f"; {x}" for x in (hinweis, hinweis2, hinweis3) if x)
            elif "bild" not in quellen:
                quellen["bild"] = "nicht verfügbar: keine Fensteraufnahme"
        return quellen

    def liste(self, ziel: str, *, herkunft: str | None = None, rolle: str | None = None, text: str | None = None, neu_messen: bool = True) -> dict:
        quellen = self.messen(ziel) if neu_messen else {}
        jetzt = self._jetzt()
        ks = self.welt.liste(ziel, herkunft=herkunft, rolle=rolle, text=text, nur_aktuell=True, jetzt_ms=jetzt, limit=MAX_ANTWORT_KNOTEN)
        return {"status": "ok", "ziel": ziel, "zaehlung": self.welt.zaehlung(ziel), "quellen": quellen, "knoten": [k.zu_dict(jetzt) for k in ks], "gemessen_ms": jetzt,
                "abgeschnitten": len(ks) >= MAX_ANTWORT_KNOTEN}

    # ---- Handeln ---------------------------------------------------------------------------------------------------------------------------
    def _aktionsdienst(self, tid: str, ziel: str, seq: int | None, *, haende_erlaubt: bool, profil: str, lease_grund: str) -> AktionsDienst:
        def koordinaten_klick(z: str, k: Knoten) -> dict:
            b = self._bezug(tid, z, seq)
            if b is None or k.rect is None:
                return {"status": "abgelehnt", "grund": "frame_unbekannt"}
            r = b.bild_rect or b.rect
            mitte = ((k.rect[0] + k.rect[2]) // 2, (k.rect[1] + k.rect[3]) // 2)
            punkt = (int((mitte[0] - r[0]) * b.breite / max(1, r[2] - r[0])), int((mitte[1] - r[1]) * b.hoehe / max(1, r[3] - r[1])))
            if self.haende is None:
                return {"status": "abgelehnt", "grund": "haende_nicht_verfuegbar"}
            e = self.haende.ausfuehren(f"w-{int(time.time() * 1000)}", ea.Aktion("klick", punkt=punkt), ziel=z, bezug=b, lease_grund=lease_grund, haende_erlaubt=haende_erlaubt,
                                       profil_erlaubt=steuerprofil.profil(profil).erlaubt("klick"))
            return e.zu_dict()

        def bild_holen(z: str, rect):
            a = self._bild(z)
            return None if a is None else (a[0], a[1], a[2])

        return AktionsDienst(self.welt, cdp_seite=self._cdp_seite, ui_quelle=self._ui_quelle, koordinaten_klick=koordinaten_klick, bild_holen=bild_holen, jetzt_ms=self._jetzt, schlafen=self._schlafen)

    def aktion(self, tid: str, ziel: str, knoten_id: str, aktion: str, text: str | None, erwartung: str | None, seq: int | None, *, haende_erlaubt: bool, profil: str, lease_grund: str) -> dict:
        """Eine Handlung an einem Knoten. Ohne erlaubte Hände oder ohne Lease geschieht nichts (auch nicht über die Bedienungshilfen); `lesen` braucht beides nicht."""
        if aktion != "lesen":
            if not haende_erlaubt:
                return {"status": "abgelehnt", "grund": "haende_aus"}
            if lease_grund:
                return {"status": "abgelehnt", "grund": lease_grund}
        d = self._aktionsdienst(tid, ziel, seq, haende_erlaubt=haende_erlaubt, profil=profil, lease_grund=lease_grund)
        return d.ausfuehren(ziel, knoten_id, aktion, text, erwartung)

    # ---- Anker --------------------------------------------------------------------------------------------------------------------------------
    def anker_neu(self, tid: str, ziel: str, name: str, punkt: tuple[int, int] | None, seq: int | None, urheber: str, herkunft: str = "authored") -> dict:
        b = self._bezug(tid, ziel, seq)
        if punkt is not None and b is None:
            return {"status": "abgelehnt", "grund": "frame_unbekannt"}
        rect = rel = None
        if punkt is not None:
            schirm = ea.bild_zu_schirm(punkt, b)
            rect = (schirm[0] - 12, schirm[1] - 12, schirm[0] + 12, schirm[1] + 12)
            r = b.rect
            rel = ((schirm[0] - r[0]) / max(1, r[2] - r[0]), (schirm[1] - r[1]) / max(1, r[3] - r[1]), 24 / max(1, r[2] - r[0]), 24 / max(1, r[3] - r[1]))
        try:
            k = self.welt.anker_anlegen(ziel, name, rect, urheber=urheber, jetzt_ms=self._jetzt(), relativ=rel, herkunft=herkunft)
        except ValueError as fehler:
            return {"status": "abgelehnt", "grund": str(fehler)[:60]}
        return {"status": "ok", "knoten": k.zu_dict(self._jetzt())}

    def anker_weg(self, ziel: str, knoten_id: str) -> dict:
        k = self.welt.knoten(ziel, knoten_id)
        if k is None:
            return {"status": "unaufloesbar", "grund": "knoten_unbekannt"}
        if k.herkunft not in ("authored", "projected"):
            return {"status": "abgelehnt", "grund": "nur_eigene_anker_entfernbar"}
        return {"status": "ok" if self.welt.entfernen(ziel, knoten_id) else "unaufloesbar"}

    # ---- Set-of-Mark (G11): ein Bild mit nummerierten Rahmen um die bedienbaren Knoten ----------------------------------------------------------------------
    def markiert(self, ziel: str, *, neu_messen: bool = True) -> dict:
        from .weltdom_markierung import markieren

        quellen = self.messen(ziel) if neu_messen else {}
        aufnahme = self._bild(ziel)
        if aufnahme is None:
            return {"status": "abgelehnt", "grund": "keine_aufnahme", "quellen": quellen}
        bgra, b, h, bereich = aufnahme
        jetzt = self._jetzt()
        ks = [k.zu_dict(jetzt) for k in self.welt.liste(ziel, nur_aktuell=True, jetzt_ms=jetzt, limit=MAX_ANTWORT_KNOTEN * 4)]
        m = markieren(bgra, b, h, bereich, ks)
        return {"status": "ok", "_jpeg": m["jpeg"], "breite": m["breite"], "hoehe": m["hoehe"], "tabelle": m["tabelle"], "weggelassen": m["weggelassen"], "quellen": quellen,
                "hinweis": "Das Bild folgt als Bild des Ziels („see“). Gehandelt wird über die Knoten-Kennung („knoten ID klick“), nicht über Pixel."}

    # ---- Profile (G11): gemeinsam Angelegtes pro Programm, Seite oder Spiel speichern und wieder laden ----------------------------------------------------------------
    def profil_speichern(self, ziel: str, name: str, urheber: str, passt_auf: dict | None, beschreibung: str = "") -> dict:
        return self._profil(lambda: {"status": "ok", **self.profile.speichern(self.welt, ziel, name, urheber=urheber, jetzt_ms=self._jetzt(), passt_auf=passt_auf, beschreibung=beschreibung)})

    def profil_laden(self, tid: str, ziel: str, name: str, seq: int | None, urheber: str, version: int | None = None) -> dict:
        b = self._bezug(tid, ziel, seq)
        rect = tuple(b.rect) if b is not None and b.rect else None
        return self._profil(lambda: {"status": "ok", **self.profile.laden_in(self.welt, ziel, name, rect, urheber=urheber, jetzt_ms=self._jetzt(), version=version),
                                      "fenster_bekannt": rect is not None})

    def profil_liste(self, passt_auf: dict | None, alle: bool = False) -> dict:
        if self.profile is None:
            return {"status": "abgelehnt", "grund": "profile_nicht_verfuegbar"}
        if passt_auf:
            return {"status": "ok", "profile": self.profile.passende(**passt_auf)}
        return {"status": "ok", "profile": self.profile.liste(mit_ausgeblendeten=alle)}

    def profil_weg(self, name: str, aktiv: bool = False) -> dict:
        if self.profile is None:
            return {"status": "abgelehnt", "grund": "profile_nicht_verfuegbar"}
        ok = self.profile.ausblenden(name, aktiv)
        return {"status": "ok" if ok else "unaufloesbar", "hinweis": "ausgeblendet, nicht gelöscht: alle Versionen bleiben" if ok and not aktiv else ""}

    def _profil(self, aufruf) -> dict:
        from .weltdom_profile import ProfilFehler

        if self.profile is None:
            return {"status": "abgelehnt", "grund": "profile_nicht_verfuegbar"}
        try:
            return aufruf()
        except ProfilFehler as f:
            return {"status": "abgelehnt", "grund": str(f)[:60]}

    # ---- Zeigen ------------------------------------------------------------------------------------------------------------------------------------
    def zeige(self, tid: str, ziel: str, punkt: tuple[int, int], seq: int | None, urheber: str, modus: str, empfaenger: tuple[str, ...], *, aktion: str = "klick", text: str | None = None,
              haende_erlaubt: bool = False, profil: str = "hintergrund", lease_grund: str = "lease_fehlt", neu_messen: bool = True) -> dict:
        """Eine Zeigegeste. `modus`: `praesentieren` (nur Zeichen in der Arbeitsfläche) oder `einfuegen` (echte Handlung). Veraltete Gesten warnen und handeln nie am alten Pixel."""
        b = self._bezug(tid, ziel, seq)
        if b is None:
            return {"status": "abgelehnt", "grund": "frame_unbekannt"}
        if neu_messen:
            self.messen(ziel, bild_erschliessen=False)
        jetzt = self._jetzt()
        g = zg.erzeugen(ziel, punkt, b, urheber, self.welt, jetzt)
        if len(self.gesten) >= MAX_GESTEN:
            self.gesten.pop(next(iter(self.gesten)))
        self.gesten[g.id] = g
        stand = self._ziel_stand(ziel)

        def neu_aufloesen(alt: Knoten | None) -> Knoten | None:
            self.messen(ziel, bild_erschliessen=False)
            return next((k for k in self.welt.liste(ziel, herkunft="real") if alt is not None and (k.rolle, k.name) == (alt.rolle, alt.name)), None)

        p = zg.pruefen(g, stand, jetzt, self.welt, neu_aufloesen=neu_aufloesen)
        d = {"geste": g.zu_dict(), "pruefung": p.zu_dict()}
        if modus == "praesentieren":
            if self._overlay is None:
                return {"status": "fehler", "grund": "arbeitsflaeche_nicht_verfuegbar", **d}
            r = zg.praesentieren(g, p, stand, lambda z, rel, t: self._overlay(tid, z, rel, t, empfaenger))
            return {**r, **d}
        if modus != "einfuegen":
            return {"status": "abgelehnt", "grund": "modus_unbekannt", **d}
        if not haende_erlaubt:
            return {"status": "abgelehnt", "grund": "haende_aus", "wirkung_in_anwendung": False, **d}
        if lease_grund:
            return {"status": "abgelehnt", "grund": lease_grund, "wirkung_in_anwendung": False, **d}
        dienst = self._aktionsdienst(tid, ziel, seq, haende_erlaubt=haende_erlaubt, profil=profil, lease_grund=lease_grund)

        def haende_klick(z: str, schirm: tuple[int, int]) -> dict:
            if self.haende is None:
                return {"status": "abgelehnt", "grund": "haende_nicht_verfuegbar"}
            bb = self._bezug(tid, z, None) or b  # der neue Punkt bezieht sich auf das jetzige Fenster: Bildpunkt aus dem aktuellen Rechteck
            r = stand.rect if stand is not None and stand.rect else b.rect
            neu_b = ea.Bildbezug(z, bb.seq, self._jetzt(), r[2] - r[0], r[3] - r[1], r, bb.generation, bb.dpi, r)
            e = self.haende.ausfuehren(f"z-{int(time.time() * 1000)}", ea.Aktion("klick", punkt=(schirm[0] - r[0], schirm[1] - r[1])), ziel=z, bezug=neu_b, lease_grund=lease_grund,
                                       haende_erlaubt=haende_erlaubt, profil_erlaubt=steuerprofil.profil(profil).erlaubt("klick"))
            return e.zu_dict()

        r = zg.einfuegen(g, p, aktion=aktion, text=text, dienst=dienst, haende_klick=haende_klick)
        return {**r, **d}
