"""Den WorldDOM-Dienst an den Körper anschließen (G11): Quellen (Browser, Bedienungshilfen, Fensterbild), Zielzustand und Arbeitsfläche aus der Plattform und der Anwendung.

Der Browser-Anschluss ist freiwillig: ist Chromium mit `--remote-debugging-port=<Port>` gestartet (Port in `BRIDGE_CDP_PORT`, Vorgabe 9222), wird die Seite genutzt, deren Titel zum Fenstertitel passt;
sonst steht „nicht verfügbar“ in der Antwort. Unter Windows fehlt `comtypes` im Paket: UI Automation meldet „nicht verfügbar“, ehrlich.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from . import ziele
from .eingabe_adapter import ZielStand
from .weltdom import WeltDom
from .weltdom_dienst import WeltdomDienst
from .weltdom_profile import ProfilSpeicher


def baue_weltdom(plattform, ort: str, haende_engine, anwendung_ref: list, *, fenster_zustand=None, pfad: Path | None = None, cdp_port: int | None = None, fenster_liste=None) -> WeltdomDienst:
    """`fenster_liste()` liefert `WindowInfo`-ähnliche Einträge (hwnd, title, process_id); Vorgabe: die Fensteraufzählung der Plattform."""
    if fenster_zustand is None:
        from .ziel_halter import fenster_zustand as fz
        fenster_zustand = fz
    welt = WeltDom(pfad)
    welt.laden()
    api = getattr(plattform.quelle, "_api", None)
    liste = fenster_liste or (api.enumerate_windows if api is not None else (lambda: []))
    port = cdp_port or int(os.environ.get("BRIDGE_CDP_PORT", "9222") or 9222)
    zustand: dict = {"atspi": None, "uia": None}
    sperre = threading.Lock()

    def fenster(ziel: str):
        kennung = ziele.fenster_kennung(ziel)
        if kennung is None or ziele.ort_von(ziel) != ort:
            return None
        return next((f for f in liste() if f.hwnd == kennung), None)

    def cdp_seite(ziel: str):
        f = fenster(ziel)
        if f is None:
            return None
        from .cdp import CdpBrowser, CdpFehler

        browser = CdpBrowser(port, timeout=3.0)
        if not browser.verfuegbar():
            return None
        passend = [z for z in browser.ziele() if z.titel and f.title.startswith(z.titel)]
        if len(passend) != 1:  # nur bei eindeutiger Zuordnung: keine geratene Seite
            return None
        try:
            return browser.verbinden(passend[0])
        except CdpFehler:
            return None

    def ui_quelle(ziel: str):
        f = fenster(ziel)
        if f is None or not f.process_id:
            return None
        with sperre:
            if plattform.name == "windows":
                if zustand["uia"] is None:
                    from .uia import WindowsUiaQuelle
                    zustand["uia"] = WindowsUiaQuelle()
                q = zustand["uia"]
            else:
                if zustand["atspi"] is None:
                    from .uia import AtspiQuelle
                    zustand["atspi"] = AtspiQuelle()
                q = zustand["atspi"]
        return (q, f.process_id) if q.verfuegbar() else None

    def bild(ziel: str):
        kennung = ziele.fenster_kennung(ziel)
        if kennung is None or ziele.ort_von(ziel) != ort:
            return None
        vorhanden, minimiert, rect = fenster_zustand(kennung)
        if not vorhanden or minimiert or rect is None:
            return None
        aufnahme = plattform.fenster_bild(kennung) if plattform.fenster_bild is not None else None
        if aufnahme is None:
            bgra = plattform.capture_api.capture_bgra(rect)
            return bgra, rect[2] - rect[0], rect[3] - rect[1], rect
        return aufnahme[0], aufnahme[1], aufnahme[2], rect

    def ziel_stand(ziel: str):
        kennung = ziele.fenster_kennung(ziel)
        if kennung is None or ziele.ort_von(ziel) != ort:
            return None
        vorhanden, minimiert, rect = fenster_zustand(kennung)
        return ZielStand(vorhanden, rect, minimiert, kennung, None)

    def bezug(tid: str, ziel: str, seq):
        a = anwendung_ref[0] if anwendung_ref else None
        b = a._bildbezug(tid, seq) if a is not None else None
        return b if b is not None and b.ziel == ziel else None

    def overlay(tid: str, ziel: str, rel, text: str, empfaenger):
        a = anwendung_ref[0] if anwendung_ref else None
        return a.zeige_overlay(tid, ziel, rel, text, tuple(empfaenger)) if a is not None else None

    return WeltdomDienst(welt, cdp_seite=cdp_seite, ui_quelle=ui_quelle, bild=bild, ziel_stand=ziel_stand, bezug=bezug, haende=haende_engine, overlay=overlay,
                         profile=ProfilSpeicher(pfad.with_name('weltdom_profile.json') if pfad else None))
