"""Vom Begriff zur Handlung (G11): einen WorldDOM-Knoten auflösen, die Aktion ausführen und die Wirkung zurücklesen.

Der Auftrag heißt nicht „klicke bei x=430, y=280“, sondern „klicke den Knoten `rea-cdp-…`“. Die Auflösung entscheidet je Herkunft, womit gehandelt wird:

* `cdp` (Browser): der Knoten wird über das DOM frisch gesucht (Kennung, sonst eindeutig Rolle und Name); geklickt und getippt wird über die Seite selbst.
* `atspi` / `uia` (Programme mit Bedienungshilfen): der Baum wird frisch gelesen, der Knoten über Pfad oder eindeutig Rolle und Name wiedergefunden; ausgelöst wird über die Bedienungshilfen.
* `koordinate` (aus dem Bild erschlossen, bewusst angelegt): nur über die Hände (G10) mit allem, was dazugehört — Lease, Käfig, Bild; nur Klick.
* `virtuell` (erfundene Knoten ohne Ort, projizierte): kein Effekt in der Anwendung; das Ergebnis sagt es.

Ein Knoten, der nicht aufzulösen ist (verschwunden, mehrdeutig, veraltet, ohne die Fähigkeit), löst **nichts** aus; die Hände bekommen dann nie einen geratenen Punkt.
Das Ergebnis trennt `status`, `methode` und `ruecklese` (vorher, nachher, `bestaetigt` als True/False/None — None heißt: nicht nachprüfbar, ausdrücklich nicht „ok“).
"""

from __future__ import annotations

import time
from collections.abc import Callable

from .weltdom import Knoten, WeltDom

STATUS = ("ausgefuehrt", "unaufloesbar", "veraltet", "abgelehnt", "fehler", "virtuell")
AKTIONEN = ("klick", "text_setzen", "lesen")
RUECKLESE_WARTEN_S = 1.0


def ergebnis(status: str, grund: str = "", methode: str = "", knoten: Knoten | None = None, ruecklese: dict | None = None, **extra) -> dict:
    d = {"status": status, "grund": grund, "methode": methode, "knoten": knoten.zu_dict() if knoten is not None else None, "ruecklese": ruecklese or {"art": "keine", "bestaetigt": None}}
    d.update(extra)
    return d


class AktionsDienst:
    """Löst Knoten auf und handelt. Die Quellen kommen als Funktionen herein (und sind damit austauschbar und prüfbar)."""

    def __init__(self, welt: WeltDom, *, cdp_seite: Callable[[str], object | None] = lambda ziel: None, ui_quelle: Callable[[str], tuple[object, object] | None] = lambda ziel: None,
                 koordinaten_klick: Callable[[str, Knoten], dict] | None = None, bild_holen: Callable[[str, tuple[int, int, int, int]], tuple[bytes, int, int] | None] | None = None,
                 jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000), schlafen: Callable[[float], None] = time.sleep):
        self.welt = welt
        self._cdp_seite, self._ui_quelle, self._koordinaten_klick, self._bild_holen = cdp_seite, ui_quelle, koordinaten_klick, bild_holen
        self._jetzt_ms, self._schlafen = jetzt_ms, schlafen

    # ---- Haupteingang --------------------------------------------------------------------------------------------------------------
    def ausfuehren(self, ziel: str, knoten_id: str, aktion: str, text: str | None = None, erwartung: str | None = None) -> dict:
        k = self.welt.knoten(ziel, knoten_id)
        if k is None:
            return ergebnis("unaufloesbar", "knoten_unbekannt")
        if aktion not in AKTIONEN:
            return ergebnis("abgelehnt", "aktion_unbekannt", knoten=k)
        if k.herkunft == "projected":
            return ergebnis("abgelehnt", "projiziert_nie_ausfuehrbar", k.aufloesung, k)
        if k.veraltet(self._jetzt_ms()):
            return ergebnis("veraltet", "neu_messen", k.aufloesung, k, hinweis=f"gemessen vor {k.alter_ms(self._jetzt_ms())} ms, gilt {k.ttl_ms} ms")
        if k.aufloesung in ("virtuell", "keine"):
            return ergebnis("virtuell", "kein_effekt_in_der_anwendung", "virtuell", k, hinweis="ein erfundener Knoten ohne Ort: es wurde nichts in der Anwendung getan")
        if aktion == "text_setzen" and (not isinstance(text, str) or not 0 <= len(text) <= 500):
            return ergebnis("abgelehnt", "text_ungueltig", k.aufloesung, k)
        if aktion not in k.faehigkeiten and not (aktion == "klick" and "klick_koordinate" in k.faehigkeiten and k.aufloesung == "koordinate"):
            return ergebnis("abgelehnt", "faehigkeit_fehlt", k.aufloesung, k, hinweis=f"dieser Knoten kann: {', '.join(k.faehigkeiten) or 'nichts'}")
        try:
            if k.aufloesung == "cdp":
                return self._cdp(ziel, k, aktion, text, erwartung)
            if k.aufloesung in ("atspi", "uia"):
                return self._ui(ziel, k, aktion, text, erwartung)
            if k.aufloesung == "koordinate":
                return self._koordinate(ziel, k, aktion, erwartung)
            return ergebnis("virtuell", "kein_effekt_in_der_anwendung", "virtuell", k, hinweis="ein erfundener Knoten ohne Ort: es wurde nichts in der Anwendung getan")
        except Exception as fehler:
            return ergebnis("fehler", "ausfuehrung_fehlgeschlagen", k.aufloesung, k, fehler=repr(fehler)[:120])

    # ---- Browser ----------------------------------------------------------------------------------------------------------------------
    def _cdp_aufloesen(self, seite, k: Knoten) -> tuple[int | None, str]:
        """(Kennung im DOM, Grund). Erst die gemerkte Kennung; ist sie ungültig, genau ein Element mit derselben Rolle und demselben Namen."""
        bid = k.anker.get("backend_id")
        if bid is not None and seite.knoten_vorhanden(bid):
            return int(bid), ""
        passend = [a for a in seite.ax_baum() if a.rolle == k.anker.get("rolle") and a.name == k.anker.get("name") and a.knoten_id is not None]
        if len(passend) == 1:
            return int(passend[0].knoten_id), ""
        return None, "knoten_weg" if not passend else "mehrdeutig"

    def _cdp(self, ziel: str, k: Knoten, aktion: str, text: str | None, erwartung: str | None) -> dict:
        seite = self._cdp_seite(ziel)
        if seite is None:
            return ergebnis("unaufloesbar", "quelle_nicht_verfuegbar", "cdp", k)
        bid, grund = self._cdp_aufloesen(seite, k)
        if bid is None:
            return ergebnis("unaufloesbar", grund, "cdp", k)
        vorher = seite.knoten_wert(bid)
        if aktion == "lesen":
            return ergebnis("ausgefuehrt", "", "cdp", k, {"art": "wert", "vorher": vorher, "nachher": vorher, "bestaetigt": None}, gelesen=vorher)
        if aktion == "klick":
            if not seite.klick_knoten(bid):
                return ergebnis("unaufloesbar", "nicht_sichtbar", "cdp", k)
            self._schlafen(0.3)
            nachher = seite.knoten_wert(bid)
            rl = {"art": "wert", "vorher": vorher, "nachher": nachher, "bestaetigt": None}
            if erwartung is not None:
                rl["erwartung"] = erwartung
                rl["bestaetigt"] = bool(self._erwartung_in_seite(seite, erwartung, nachher))
            return ergebnis("ausgefuehrt", "", "cdp", k, rl)
        if not seite.text_in_knoten(bid, text or ""):
            return ergebnis("unaufloesbar", "knoten_weg", "cdp", k)
        nachher = seite.knoten_wert(bid)
        return ergebnis("ausgefuehrt", "", "cdp", k, {"art": "wert", "vorher": vorher, "nachher": nachher, "erwartung": text, "bestaetigt": nachher == text})

    @staticmethod
    def _erwartung_in_seite(seite, erwartung: str, nachher: str | None) -> bool:
        try:
            gesamt = str(seite.auswerten("document.body ? document.body.innerText : ''"))
        except Exception:
            gesamt = ""
        return erwartung in gesamt or (nachher is not None and erwartung in nachher)

    # ---- Bedienungshilfen --------------------------------------------------------------------------------------------------------------
    def _ui_finden(self, wurzel, k: Knoten):
        """Der Knoten im frischen Baum: erst derselbe Pfad mit gleicher Rolle und Name, sonst eindeutig Rolle und Name."""
        pfad = tuple(k.anker.get("pfad", ()))
        knoten = wurzel
        try:
            for i in pfad:
                knoten = knoten.kinder[i]
            if knoten.rolle == k.anker.get("rolle") and knoten.name == k.anker.get("name"):
                return knoten, ""
        except IndexError:
            pass
        passend = [x for x in wurzel.alle() if x.rolle == k.anker.get("rolle") and x.name == k.anker.get("name")]
        if len(passend) == 1:
            return passend[0], ""
        return None, "knoten_weg" if not passend else "mehrdeutig"

    def _ui(self, ziel: str, k: Knoten, aktion: str, text: str | None, erwartung: str | None) -> dict:
        q = self._ui_quelle(ziel)
        if q is None:
            return ergebnis("unaufloesbar", "quelle_nicht_verfuegbar", k.aufloesung, k)
        quelle, pid = q
        baum = quelle.baum(k.anker.get("pid", pid))
        if baum.status != "ok" or baum.wurzel is None:
            return ergebnis("unaufloesbar", baum.status if baum.status != "ok" else "kein_baum", k.aufloesung, k)
        n, grund = self._ui_finden(baum.wurzel, k)
        if n is None:
            return ergebnis("unaufloesbar", grund, k.aufloesung, k)
        vorher = n.wert
        if aktion == "lesen":
            return ergebnis("ausgefuehrt", "", k.aufloesung, k, {"art": "wert", "vorher": vorher, "nachher": vorher, "bestaetigt": None}, gelesen=vorher)
        if aktion == "klick":
            if not quelle.klick(n):
                return ergebnis("abgelehnt", "faehigkeit_fehlt", k.aufloesung, k, hinweis="das Programm bietet für diesen Knoten keine Auslösung an")
            rl = {"art": "text", "vorher": None, "nachher": None, "bestaetigt": None}
            if erwartung is not None:
                rl["erwartung"] = erwartung
                rl["bestaetigt"] = self._ui_wartet_auf(quelle, k, pid, lambda w: any(erwartung in (x.name + " " + x.wert) for x in w.alle()))
            return ergebnis("ausgefuehrt", "", k.aufloesung, k, rl)
        if not quelle.text_setzen(n, text or ""):
            return ergebnis("abgelehnt", "faehigkeit_fehlt", k.aufloesung, k)
        nachher = []
        bestaetigt = self._ui_wartet_auf(quelle, k, pid, lambda w: (lambda f: f is not None and f.wert == (text or ""))(self._ui_finden(w, k)[0]), nachher)
        return ergebnis("ausgefuehrt", "", k.aufloesung, k, {"art": "wert", "vorher": vorher, "nachher": nachher[-1] if nachher else None, "erwartung": text, "bestaetigt": bestaetigt})

    def _ui_wartet_auf(self, quelle, k: Knoten, pid, bedingung, nachher: list | None = None) -> bool:
        ende = time.monotonic() + RUECKLESE_WARTEN_S
        while True:
            baum = quelle.baum(k.anker.get("pid", pid))
            if baum.status == "ok" and baum.wurzel is not None:
                if nachher is not None:
                    gefunden, _ = self._ui_finden(baum.wurzel, k)
                    if gefunden is not None:
                        nachher.append(gefunden.wert)
                if bedingung(baum.wurzel):
                    return True
            if time.monotonic() >= ende:
                return False
            self._schlafen(0.1)

    # ---- Koordinaten (nur über die Hände) ----------------------------------------------------------------------------------------------
    def _koordinate(self, ziel: str, k: Knoten, aktion: str, erwartung: str | None) -> dict:
        if aktion != "klick":
            return ergebnis("abgelehnt", "faehigkeit_fehlt", "koordinate", k, hinweis="ein erschlossener oder erfundener Knoten kennt nur den Klick auf seine Lage")
        if self._koordinaten_klick is None:
            return ergebnis("unaufloesbar", "haende_nicht_verfuegbar", "koordinate", k)
        vorher = self._bild_holen(ziel, k.rect) if self._bild_holen is not None and k.rect else None
        h = self._koordinaten_klick(ziel, k)
        if h.get("status") != "ausgefuehrt":
            return ergebnis("abgelehnt" if h.get("status") == "abgelehnt" else "fehler", h.get("grund", "haende_abgelehnt"), "koordinate", k, haende=h)
        self._schlafen(0.3)
        nachher = self._bild_holen(ziel, k.rect) if self._bild_holen is not None and k.rect else None
        if vorher is not None and nachher is not None and vorher[1:] == nachher[1:]:
            geaendert = vorher[0] != nachher[0]
            rl = {"art": "pixel", "vorher": None, "nachher": None, "bestaetigt": True if geaendert else None, "hinweis": "Pixel haben sich geändert" if geaendert else "keine Pixeländerung messbar (kein Beleg, kein Gegenbeleg)"}
        else:
            rl = {"art": "keine", "bestaetigt": None, "hinweis": "für Koordinaten-Klicks gibt es ohne Bild keine Rücklese"}
        return ergebnis("ausgefuehrt", "", "koordinate", k, rl, haende=h)
