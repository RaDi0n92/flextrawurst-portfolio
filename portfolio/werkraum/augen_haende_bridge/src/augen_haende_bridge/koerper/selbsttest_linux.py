"""Der Selbsttest des Linux-Körpers: prüft einzeln, ob alles da ist, was der Körper auf diesem Desktop braucht, und verändert nichts.

Jede Zeile heißt `ok`, `fehlt` (der Körper würde damit nicht oder nur eingeschränkt laufen) oder `Hinweis` (läuft, aber mit einer bekannten Grenze, z. B. kein
Compositor für Durchsichtigkeit). Der Rückgabewert ist 0, wenn nichts fehlt.
"""

from __future__ import annotations

import os
import socket
import sys
import time
from pathlib import Path

Zeile = tuple[str, str, str]  # (Stufe, Name, Einzelheit)


def _pruefen(name: str, aufruf) -> Zeile:
    try:
        stufe, text = aufruf()
        return stufe, name, text
    except Exception as fehler:
        return "fehlt", name, f"{type(fehler).__name__}: {fehler}"[:160]


def pruefungen(ort: str, url: str, token_datei: Path | None) -> list[Zeile]:
    from . import fenster_linux as fl
    from . import linux_adapter as la
    from . import x11_helfer as x

    zeilen: list[Zeile] = []

    def anzeige():
        b, h = x.bildschirmgroesse()
        return "ok", f"{os.environ.get('DISPLAY', '?')} {b}x{h}"

    def fenster():
        f = fl.Fenster(-300, -300, 8, 8, titel="Selbsttest", nicht_aktivieren=True)
        try:
            f.zeige(aktivieren=False)
            fl.Anwendung().pumpen(100)
            ok = x.fenster_existiert(f.hwnd) and f.sichtbar()
        finally:
            f.schliessen()
        return ("ok", "GTK-Fenster lassen sich anlegen und zeigen") if ok else ("fehlt", "ein Fenster erscheint nicht")

    def aufnahme():
        api = la.LinuxCaptureApi()
        daten = api.capture_bgra((0, 0, 64, 64))
        if len(daten) != 64 * 64 * 4:
            return "fehlt", "die Aufnahme liefert die falsche Größe"
        if api.umleitung_moeglich:
            return "ok", "Aufnahme ok; Fenster der Bridge lassen sich auslassen, verdeckte Fenster vollständig lesen (XComposite)"
        if api.fensterbild_moeglich:
            return "ok", "Aufnahme ok; ein Compositor läuft: das Bild eines Fensters kommt über dessen benannte Pixmap, auch verdeckt; Bridge-Fenster stehen im Desktopbild"
        return "Hinweis", "Aufnahme ok, aber XComposite ist nicht verfügbar: Bridge-Fenster stehen im Bild, verdeckte Fenster zeigen fremde Pixel"

    def sitzung():
        art = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if os.environ.get("WAYLAND_DISPLAY") and art == "wayland" and not os.environ.get("DISPLAY"):
            return "fehlt", "Wayland ohne X11: XTEST, XComposite und XRecord gibt es dort nicht (Eingabe nur über libei/Portal, Aufnahme über PipeWire mit Zustimmung); dieser Körper läuft nur unter X11/XWayland"
        if art == "wayland" or os.environ.get("WAYLAND_DISPLAY"):
            return "Hinweis", "Wayland-Sitzung mit XWayland: nur X11-Fenster sind erreichbar, native Wayland-Fenster sehen und bedienen die Hände nicht"
        return "ok", f"X11-Sitzung ({art or 'Sitzungsart unbekannt, kein Wayland erkennbar'})"

    def eingabe():
        d = x.anzeige()
        if not d.has_extension("XTEST"):
            return "fehlt", "XTEST fehlt: die Hände können keine Tasten drücken"
        return "ok", "XTEST (Tasten und Maus senden)"

    def notaus():
        from .notaus import NotAus

        hook = la.LinuxNotAusHook(NotAus())
        if not hook.start(timeout=3.0):
            return "fehlt", f"F12-Not-Aus nicht verfügbar: {hook.fehler}"
        hook.stop()
        return "ok", "F12-Not-Aus über XRecord"

    def hotkeys():
        from .tasten_x11 import HotkeyFaden

        faden = HotkeyFaden(lambda f: None)
        belegbar = faden.eintragen(0x87, 0, lambda: None)  # F24: eine Taste, die kaum jemand belegt
        faden.loeschen(0x87, 0)
        faden.beenden()
        return ("ok", "globale Tastenkombinationen lassen sich abfangen") if belegbar else ("Hinweis", "F24 ließ sich nicht abfangen (belegt?)")

    def schriften():
        namen = [fl._schriftdatei(n, False)[0] for n in ("Consolas", "Segoe UI", "Courier New")]
        if not all(namen):
            return "fehlt", "für eine der Windows-Schriften gibt es keinen Ersatz auf diesem Rechner"
        return "ok", ", ".join(Path(n).name for n in namen)

    def compositor():
        from gi.repository import Gdk

        zusammengesetzt = Gdk.Screen.get_default().is_composited()
        return ("ok", "Compositor läuft: Durchsichtigkeit der Fenster möglich") if zusammengesetzt else (
            "Hinweis", "kein Compositor: Fenster sind undurchsichtig, Objekte werden mit Formmaske und Raster gezeigt")

    def relay():
        adresse = url.replace("ws://", "").split("/")[0]
        host, _, port = adresse.partition(":")
        with socket.create_connection((host, int(port or 80)), timeout=3):
            pass
        if token_datei is None or not token_datei.exists():
            return "fehlt", f"Zugangsdaten fehlen (BRIDGE_TOKEN oder {token_datei})"
        if len(token_datei.read_text().strip()) < 32:
            return "fehlt", "die Zugangsdaten sind zu kurz"
        return "ok", f"{adresse} erreichbar, Zugangsdaten für {ort} gelesen"

    for name, aufruf in (("Anzeige", anzeige), ("Sitzung", sitzung), ("Fensterschicht", fenster), ("Aufnahme", aufnahme), ("Eingabe", eingabe), ("Not-Aus (F12)", notaus),
                         ("Hotkeys", hotkeys), ("Schriften", schriften), ("Compositor", compositor), ("Relay", relay)):
        zeilen.append(_pruefen(name, aufruf))
    return zeilen


def lauf(version: str, ort: str, url: str, token_datei: Path | None, still: bool = False) -> int:
    ausgabe = [f"Augen & Hände Bridge {version} — Selbsttest Linux, Ort {ort}", ""]
    zeilen = pruefungen(ort, url, token_datei)
    for stufe, name, text in zeilen:
        ausgabe.append(f"{stufe:>7}  {name}: {text}")
    fehlt = [z for z in zeilen if z[0] == "fehlt"]
    ausgabe += ["", "Ergebnis: alles da" if not fehlt else f"Ergebnis: {len(fehlt)} fehlt"]
    if not still:
        print("\n".join(ausgabe))
    return 0 if not fehlt else 1
