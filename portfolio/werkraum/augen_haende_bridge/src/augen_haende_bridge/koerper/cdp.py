"""Chromium-Browser über das DevTools-Protokoll (CDP) lesen und bedienen (G06.7, R123).

Chrome, Edge und Chromium bieten, wenn sie mit `--remote-debugging-port=<Port>` gestartet wurden, einen Anschluss auf 127.0.0.1, über den sich eine Seite lesen
(Seitenbild, DOM, Baum der Bedienungshilfen) und bedienen (Klick, Eingabe) lässt — unabhängig davon, ob das Fenster verdeckt, klein oder minimiert ist, weil die Seite
selbst gerendert wird und nicht der Bildschirm. Ein Browser ohne diesen Anschluss lässt sich damit nicht erreichen; das wird als „nicht verfügbar“ gemeldet, nie erfunden.

Nur Loopback, nur Lesen und Bedienen von Seiten: keine Dateizugriffe, kein Herunterladen, keine Browser-Einstellungen.
"""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from websockets.sync.client import connect


class CdpFehler(Exception):
    """Der Browser antwortet nicht, lehnt ab oder liefert Unbrauchbares."""


@dataclass
class Ziel:
    id: str
    titel: str
    url: str
    art: str
    ws_url: str


@dataclass
class Knoten:
    """Ein Element der Seite mit Herkunft: `dom` (aus dem DOM) oder `ax` (Baum der Bedienungshilfen)."""

    quelle: str
    rolle: str = ""
    name: str = ""
    wert: str = ""
    rect: tuple[float, float, float, float] | None = None  # in CSS-Pixeln der Seite (links, oben, rechts, unten)
    knoten_id: int | None = None
    selektor: str = ""
    zustaende: dict = field(default_factory=dict)

    def mitte(self) -> tuple[float, float] | None:
        return None if self.rect is None else ((self.rect[0] + self.rect[2]) / 2, (self.rect[1] + self.rect[3]) / 2)


def _http(host: str, port: int, pfad: str, timeout: float):
    try:
        with urllib.request.urlopen(f"http://{host}:{port}{pfad}", timeout=timeout) as antwort:
            return json.loads(antwort.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as fehler:
        raise CdpFehler(f"kein Debug-Anschluss auf {host}:{port} ({fehler.__class__.__name__})") from None


class CdpBrowser:
    def __init__(self, port: int = 9222, host: str = "127.0.0.1", timeout: float = 5.0):
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise CdpFehler("nur_loopback")
        self.host, self.port, self.timeout = host, port, timeout

    def verfuegbar(self) -> bool:
        try:
            _http(self.host, self.port, "/json/version", self.timeout)
            return True
        except CdpFehler:
            return False

    def version(self) -> dict:
        return _http(self.host, self.port, "/json/version", self.timeout)

    def ziele(self) -> list[Ziel]:
        """Die offenen Seiten (nur `page`), mit ihren Verbindungsadressen."""
        liste = _http(self.host, self.port, "/json/list", self.timeout)
        if not isinstance(liste, list):
            raise CdpFehler("ungueltige_zieleliste")
        ergebnis = []
        for eintrag in liste:
            if isinstance(eintrag, dict) and eintrag.get("type") == "page" and eintrag.get("webSocketDebuggerUrl"):
                ergebnis.append(Ziel(str(eintrag.get("id", "")), str(eintrag.get("title", "")), str(eintrag.get("url", "")), "page", str(eintrag["webSocketDebuggerUrl"])))
        return ergebnis

    def verbinden(self, ziel: Ziel | str | None = None) -> "CdpSeite":
        ziele = self.ziele()
        if isinstance(ziel, str):
            ziel = next((z for z in ziele if z.id == ziel), None)
        elif ziel is None:
            ziel = ziele[0] if ziele else None
        if ziel is None:
            raise CdpFehler("kein_ziel")
        if not ziel.ws_url.startswith(f"ws://{self.host}:{self.port}/") and not ziel.ws_url.startswith(f"ws://localhost:{self.port}/"):
            raise CdpFehler("fremde_adresse")  # die Adresse muss zu diesem Anschluss passen
        return CdpSeite(ziel, self.timeout)


class CdpSeite:
    def __init__(self, ziel: Ziel, timeout: float = 5.0):
        self.ziel, self.timeout = ziel, timeout
        self._id = 0
        try:
            self._ws = connect(ziel.ws_url, max_size=32 * 1024 * 1024, open_timeout=timeout, proxy=None)
        except Exception as fehler:
            raise CdpFehler(f"verbinden_fehlgeschlagen ({fehler.__class__.__name__})") from None

    def schliessen(self) -> None:
        try:
            self._ws.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.schliessen()

    def befehl(self, methode: str, **parameter):
        """Ein Protokollbefehl mit Antwort; Ereignisse zwischendurch werden verworfen. CdpFehler bei Fehlerantwort oder Zeitüberschreitung."""
        self._id += 1
        nummer = self._id
        try:
            self._ws.send(json.dumps({"id": nummer, "method": methode, "params": parameter}))
            ende = time.monotonic() + self.timeout
            while True:
                rest = ende - time.monotonic()
                if rest <= 0:
                    raise CdpFehler(f"zeitueberschreitung:{methode}")
                antwort = json.loads(self._ws.recv(timeout=rest))
                if antwort.get("id") == nummer:
                    if "error" in antwort:
                        raise CdpFehler(f"{methode}: {antwort['error'].get('message', 'Fehler')}"[:200])
                    return antwort.get("result", {})
        except CdpFehler:
            raise
        except TimeoutError:
            raise CdpFehler(f"zeitueberschreitung:{methode}") from None
        except Exception as fehler:
            raise CdpFehler(f"verbindung:{fehler.__class__.__name__}") from None

    # ---- Lesen -----------------------------------------------------------------------------------------------------
    def titel(self) -> str:
        return str(self.auswerten("document.title"))

    def auswerten(self, ausdruck: str):
        """Einen JavaScript-Ausdruck in der Seite auswerten (nur lesen — der Aufrufer entscheidet, was er ausführen lässt)."""
        r = self.befehl("Runtime.evaluate", expression=ausdruck, returnByValue=True)
        if "exceptionDetails" in r:
            raise CdpFehler("auswerten: " + str(r["exceptionDetails"].get("text", "Fehler"))[:120])
        return r.get("result", {}).get("value")

    def seitenbild(self) -> tuple[bytes, int, int]:
        """Das Bild der Seite (PNG) in ihrer Fenstergröße; unabhängig davon, was vor dem Fenster liegt."""
        r = self.befehl("Page.captureScreenshot", format="png")
        daten = base64.b64decode(r["data"])
        from PIL import Image
        import io

        with Image.open(io.BytesIO(daten)) as bild:
            return daten, bild.size[0], bild.size[1]

    def fenstermass(self) -> tuple[int, int]:
        """Innere Fenstergröße der Seite in CSS-Pixeln."""
        return int(self.auswerten("window.innerWidth")), int(self.auswerten("window.innerHeight"))

    def ax_baum(self) -> list[Knoten]:
        """Der Baum der Bedienungshilfen (Rolle, Name, Wert): das, was ein Mensch mit Screenreader hören würde. Ohne Geometrie; sie kommt über `dom_knoten`."""
        self.befehl("Accessibility.enable")
        r = self.befehl("Accessibility.getFullAXTree")
        knoten = []
        for k in r.get("nodes", []):
            if k.get("ignored"):
                continue
            rolle = (k.get("role") or {}).get("value", "")
            name = (k.get("name") or {}).get("value", "")
            wert = (k.get("value") or {}).get("value", "")
            zustaende = {p.get("name"): (p.get("value") or {}).get("value") for p in k.get("properties", []) if isinstance(p, dict)}
            knoten.append(Knoten("ax", str(rolle), str(name), str(wert), None, k.get("backendDOMNodeId"), "", zustaende))
        return knoten

    def dom_knoten(self, selektor: str) -> Knoten | None:
        """Das erste Element zu einem CSS-Selektor mit seiner Lage (Box der Seite); None, wenn es nicht auffindbar ist."""
        dok = self.befehl("DOM.getDocument", depth=0)
        gefunden = self.befehl("DOM.querySelector", nodeId=dok["root"]["nodeId"], selector=selektor)
        nummer = gefunden.get("nodeId", 0)
        if not nummer:
            return None
        try:
            box = self.befehl("DOM.getBoxModel", nodeId=nummer)["model"]["border"]
        except CdpFehler:
            return Knoten("dom", selektor=selektor, knoten_id=nummer)  # Element ohne Box (verborgen)
        xs, ys = box[0::2], box[1::2]
        beschreibung = self.befehl("DOM.describeNode", nodeId=nummer).get("node", {})
        wert = self.auswerten(f"(document.querySelector({json.dumps(selektor)}) || {{}}).value ?? ''")
        name = self.auswerten(f"(document.querySelector({json.dumps(selektor)}) || {{}}).innerText ?? ''")
        return Knoten("dom", str(beschreibung.get("nodeName", "")).lower(), str(name or "")[:200], str(wert or "")[:200], (min(xs), min(ys), max(xs), max(ys)), nummer, selektor)

    # ---- Bedienen --------------------------------------------------------------------------------------------------
    def klick(self, selektor: str) -> bool:
        """Klick auf die Mitte des Elements. False, wenn es nicht auffindbar oder nicht sichtbar ist — dann geschieht nichts."""
        knoten = self.dom_knoten(selektor)
        if knoten is None or knoten.mitte() is None:
            return False
        x, y = knoten.mitte()
        for art in ("mouseMoved", "mousePressed", "mouseReleased"):
            self.befehl("Input.dispatchMouseEvent", type=art, x=x, y=y, button="left", buttons=1 if art == "mousePressed" else 0, clickCount=1)
        return True

    def tippen(self, selektor: str, text: str) -> bool:
        """Das Feld fokussieren und Text eingeben. False, wenn das Feld nicht auffindbar ist."""
        knoten = self.dom_knoten(selektor)
        if knoten is None or knoten.knoten_id is None:
            return False
        self.befehl("DOM.focus", nodeId=knoten.knoten_id)
        self.befehl("Input.insertText", text=text)
        return True


# ---- Knoten über ihre Kennung im DOM (G11) ---------------------------------------------------------------------------------------------
def _seite_knoten_mitte(self, backend_id: int) -> tuple[float, float] | None:
    """Mitte des Elements in Seitenkoordinaten; None, wenn es nicht (mehr) da oder nicht sichtbar ist."""
    try:
        box = self.befehl("DOM.getBoxModel", backendNodeId=int(backend_id))["model"]["border"]
    except CdpFehler:
        return None
    xs, ys = box[0::2], box[1::2]
    if max(xs) - min(xs) <= 0 or max(ys) - min(ys) <= 0:
        return None
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def _seite_knoten_vorhanden(self, backend_id: int) -> bool:
    try:
        objekt = self.befehl("DOM.resolveNode", backendNodeId=int(backend_id))["object"]["objectId"]
        r = self.befehl("Runtime.callFunctionOn", objectId=objekt, functionDeclaration="function(){ return !!this.isConnected; }", returnByValue=True)
        return bool(r.get("result", {}).get("value"))  # ein aus dem Dokument entferntes Element lässt sich noch auflösen, ist aber weg
    except CdpFehler:
        return False


def _seite_klick_knoten(self, backend_id: int) -> bool:
    mitte = self.knoten_mitte(backend_id)
    if mitte is None:
        return False
    for art in ("mouseMoved", "mousePressed", "mouseReleased"):
        self.befehl("Input.dispatchMouseEvent", type=art, x=mitte[0], y=mitte[1], button="left", buttons=1 if art == "mousePressed" else 0, clickCount=1)
    return True


def _seite_knoten_wert(self, backend_id: int) -> str | None:
    """Wert (Feld) oder sichtbarer Text des Elements; None, wenn es nicht (mehr) aufzulösen ist."""
    try:
        objekt = self.befehl("DOM.resolveNode", backendNodeId=int(backend_id))["object"]["objectId"]
        r = self.befehl("Runtime.callFunctionOn", objectId=objekt, functionDeclaration="function(){ return (this.value !== undefined && this.value !== null && this.tagName !== 'BUTTON') ? String(this.value) : String(this.innerText || this.textContent || ''); }",
                        returnByValue=True)
        return str(r.get("result", {}).get("value", ""))
    except CdpFehler:
        return None


def _seite_text_in_knoten(self, backend_id: int, text: str) -> bool:
    """Das Feld fokussieren, leeren und den Text eintragen (mit den echten Ereignissen von insertText). False, wenn das Element nicht auflösbar ist."""
    try:
        objekt = self.befehl("DOM.resolveNode", backendNodeId=int(backend_id))["object"]["objectId"]
        self.befehl("DOM.focus", backendNodeId=int(backend_id))
        self.befehl("Runtime.callFunctionOn", objectId=objekt, functionDeclaration="function(){ if (this.select) { this.select(); } }", returnByValue=True)
        self.befehl("Input.insertText", text=text)
        return True
    except CdpFehler:
        return False


CdpSeite.knoten_mitte = _seite_knoten_mitte
CdpSeite.knoten_vorhanden = _seite_knoten_vorhanden
CdpSeite.klick_knoten = _seite_klick_knoten
CdpSeite.knoten_wert = _seite_knoten_wert
CdpSeite.text_in_knoten = _seite_text_in_knoten
