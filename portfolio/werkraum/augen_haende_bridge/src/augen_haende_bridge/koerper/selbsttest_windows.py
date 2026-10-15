"""Die Windows-Prüfungen des Selbsttests (siehe selbsttest.py). Nur auf Windows lauffähig; unter Wine zeigt der Lauf, was dort geht."""

from __future__ import annotations

import ctypes
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from . import selbsttest as st
from . import win32 as w
from .bilderstrom import Bilderstrom
from .chat_fenster import ChatFenster
from .durchklick import DurchklickVerwalter
from .einstellungen import Einstellungen
from .fenster import Anwendung
from .raute_fenster import RauteFenster
from .regie_fenster import RegieFenster
from .eingabe_fenster import RauteEingabe
from .sichtbarkeit import WindowsQuelle
from .tasten_senden import Haende, kombination_ereignisse, windows_sendinput
from .tastenkombi import Bedientaste, Kombination
from .terminal_fenster import TerminalFenster

OK, WARNUNG, FEHLER, UNBEKANNT = st.OK, st.WARNUNG, st.FEHLER, st.UNBEKANNT
CYAN = (0, 229, 255)


def _punkt_fenster(x: int, y: int) -> int:
    dll = ctypes.WinDLL("user32", use_last_error=True)
    dll.WindowFromPoint.argtypes = [w.POINT]
    dll.WindowFromPoint.restype = w.wintypes.HWND
    return int(dll.WindowFromPoint(w.POINT(x, y)) or 0)


def _rect(hwnd: int) -> tuple[int, int, int, int]:
    r = w.RECT()
    ctypes.WinDLL("user32").GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom


def _mitte(hwnd: int) -> tuple[int, int]:
    l, o, r, u = _rect(hwnd)
    return (l + r) // 2, (o + u) // 2


class _Fehlt:
    ok, grund = False, "haende_nicht_fertig"


st_ergebnis_fehlt = _Fehlt()


def _fenster_beschreibung(hwnd: int) -> str:
    if not hwnd:
        return "keins"
    titel = ctypes.create_unicode_buffer(120)
    klasse = ctypes.create_unicode_buffer(80)
    w.user32.GetWindowTextW(hwnd, titel, 120)
    w.user32.GetClassNameW(hwnd, klasse, 80)
    return f"Fenster {hwnd} Klasse {klasse.value!r} Titel {titel.value!r}"


def _vordergrund() -> int:
    return int(w.user32.GetForegroundWindow() or 0)


def _pumpen_bis(gui: Anwendung, bedingung, sekunden: float) -> bool:
    ende = time.monotonic() + sekunden
    while time.monotonic() < ende:
        gui.pumpen(30)
        if bedingung():
            return True
    return bool(bedingung())


FUNKTIONSTASTEN = [Kombination(0, vk) for vk in range(0x7C, 0x88)]  # F13 bis F24
STRG_ALT = [Kombination(w.MOD_CONTROL | w.MOD_ALT, vk) for vk in (0x74, 0x75, 0x76, 0x77, 0x78, 0x79)]  # Strg+Alt+F5 bis F10


def erste_anmeldbare(gui: Anwendung, name: str, kandidaten: list[Kombination], aufruf) -> tuple[Kombination | None, list[str]]:
    """Meldet die erste Kombination an, die frei ist; die belegten werden mit aufgezählt (Belegung ist selbst ein Befund)."""
    belegt = []
    for kombi in kandidaten:
        if gui.hotkey_setzen(name, kombi.modifikatoren, kombi.vk, aufruf):
            return kombi, belegt
        belegt.append(kombi.text())
    return None, belegt


def pruefungen(gui: Anwendung, befehl_basis: list[str]) -> list[tuple[str, st.Pruefung]]:
    api = None
    try:
        from augen_haende_bridge.windows_capture import Win32CaptureApi

        api = Win32CaptureApi()
    except Exception:
        pass
    quelle = WindowsQuelle()
    fenster: dict[str, object] = {}

    def system() -> tuple[str, str]:
        dpi = None
        try:
            dpi = ctypes.WinDLL("user32").GetDpiForSystem()
        except (OSError, AttributeError):
            pass
        rect = quelle.bildschirm()
        breite, hoehe = rect[2] - rect[0], rect[3] - rect[1]
        monitore = int(w.user32.GetSystemMetrics(80))
        gesetzt = gui.dpi_bewusst()
        awareness = None
        try:
            a = ctypes.c_int(-1)
            if ctypes.WinDLL("shcore").GetProcessDpiAwareness(ctypes.WinDLL("kernel32").GetCurrentProcess(), ctypes.byref(a)) == 0:
                awareness = {0: "nicht DPI-bewusst", 1: "systemweit DPI-bewusst", 2: "pro Monitor DPI-bewusst"}.get(a.value, a.value)
        except (OSError, AttributeError):
            pass
        detail = (f"virtueller Bildschirm {breite}x{hoehe} ab ({rect[0]},{rect[1]}), {monitore} Monitor(e), System-DPI {dpi}, "
                  f"Prozess: {awareness} (per-monitor-v2 selbst gesetzt: {gesetzt})")
        from augen_haende_bridge.windows_capture import MAX_CAPTURE_PIXELS
        if breite * hoehe > MAX_CAPTURE_PIXELS:
            return FEHLER, f"{detail}; ZU GROSS für die Aufnahme (Grenze {MAX_CAPTURE_PIXELS} Pixel): der Bilderstrom würde scheitern"
        return OK, detail

    def fenster_anlegen() -> tuple[str, str]:
        fenster["raute"] = RauteFenster(200, 200, name="Selbsttest", farbe_hex="#00E5FF", hotkey="F13")
        fenster["chat"] = ChatFenster(200, 400)
        fenster["regie"] = RegieFenster(700, 200)
        fenster["terminal"] = TerminalFenster(700, 400, zeilen=8, spalten=30, name="Selbsttest", ort="Test", farbe_hex="#00E5FF")
        for f in fenster.values():
            f.zeige(aktivieren=False)
        gui.pumpen(300)
        unsichtbar = [n for n, f in fenster.items() if not w.user32.IsWindowVisible(f.hwnd)]
        if unsichtbar:
            return FEHLER, f"nicht sichtbar: {unsichtbar}"
        raute = _rect(fenster["raute"].hwnd)
        return OK, f"Raute, Chat, Regieleiste und Terminal angelegt; Raute {raute[2] - raute[0]}x{raute[3] - raute[1]} px"

    def durchklick() -> tuple[str, str]:
        if "chat" not in fenster:
            return UNBEKANNT, "Testfenster fehlen"
        bedientaste = Bedientaste()
        if not _pumpen_bis(gui, lambda: not bedientaste.gedrueckt(), 3.0):
            return UNBEKANNT, "Strg/Alt waren schon vor dem Test gedrückt (Tastatur in Benutzung?) — Prüfung übersprungen, bitte ohne Tastendruck wiederholen"
        verwalter = DurchklickVerwalter(strg=bedientaste.gedrueckt)
        for name in ("chat", "regie", "terminal"):
            verwalter.registrieren(name, fenster[name], aktiv=True)
        gui.pumpen(100)
        ohne = {n: _punkt_fenster(*_mitte(fenster[n].hwnd)) == fenster[n].hwnd for n in ("chat", "regie", "terminal")}
        senden = windows_sendinput
        runter = [(0x11, 0, 0), (0x12, 0, 0)]
        hoch = [(0x12, 0, 2), (0x11, 0, 2)]
        angenommen = senden(runter)
        try:
            gehalten = _pumpen_bis(gui, bedientaste.gedrueckt, 1.0)
            verwalter.tick()
            gui.pumpen(100)
            mit = {n: _punkt_fenster(*_mitte(fenster[n].hwnd)) == fenster[n].hwnd for n in ("chat", "regie", "terminal")}
        finally:
            senden(hoch)
        gui.pumpen(150)
        verwalter.tick()
        gui.pumpen(100)
        danach = {n: _punkt_fenster(*_mitte(fenster[n].hwnd)) == fenster[n].hwnd for n in ("chat", "regie", "terminal")}
        detail = (f"SendInput nahm {angenommen} von 2 Ereignissen an; Bedientaste erkannt: {gehalten}; "
                  f"ohne Tasten trifft das Fenster: {ohne}; mit Strg+Alt: {mit}; danach: {danach}")
        if angenommen < 2 or not gehalten:
            return FEHLER, detail + " — Windows hat die Testtasten nicht angenommen oder nicht gemeldet"
        if any(ohne.values()) or not all(mit.values()) or any(danach.values()):
            return FEHLER, detail
        return OK, detail

    def hotkey() -> tuple[str, str]:
        berichte, treffer = {}, []
        for art, kandidaten in (("Funktionstaste", FUNKTIONSTASTEN), ("Strg+Alt+Taste", STRG_ALT)):
            kombi, belegt = erste_anmeldbare(gui, f"selbsttest-{art}", kandidaten, lambda a=art: treffer.append(a))
            zusatz = f" (belegt: {', '.join(belegt)})" if belegt else ""
            if kombi is None:
                berichte[art] = f"alle Kandidaten belegt{zusatz}"
                continue
            angenommen = windows_sendinput(kombination_ereignisse(kombi))
            ausgeloest = _pumpen_bis(gui, lambda a=art: a in treffer, 1.5)
            berichte[art] = (f"{kombi.text()} ausgelöst{zusatz}" if ausgeloest
                             else f"{kombi.text()} NICHT ausgelöst (SendInput nahm {angenommen} Ereignisse an){zusatz}")
            gui.hotkey_loeschen(f"selbsttest-{art}")
        detail = "; ".join(f"{n}: {b}" for n, b in berichte.items())
        if all("ausgelöst" in b and "NICHT" not in b for b in berichte.values()):
            return OK, detail
        if any("NICHT ausgelöst" in b for b in berichte.values()):
            return FEHLER, detail
        return WARNUNG, detail

    def eingabefeld_mit_fremdprogramm() -> tuple[str, str]:
        gesendet, felder = [], []

        aufgerufen: list = []

        def oeffnen() -> None:
            aufgerufen.append(1)
            feld = RauteEingabe(0, 0, name="Selbsttest", farbe_hex="#00E5FF", gesendet=gesendet.append, geschlossen=lambda: felder.clear())
            feld.verschiebe(300, 300)
            felder.append(feld)
            feld.aktivieren()

        kombi, belegt = erste_anmeldbare(gui, "selbsttest-feld", STRG_ALT + FUNKTIONSTASTEN, oeffnen)
        if kombi is None:
            return UNBEKANNT, f"keine freie Tastenkombination gefunden (belegt: {', '.join(belegt)}), Feld nicht prüfbar"
        fremd = subprocess.Popen(["notepad.exe"])
        try:
            time.sleep(1.5)
            gui.pumpen(100)
            dll = ctypes.WinDLL("user32", use_last_error=True)
            dll.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
            dll.FindWindowW.restype = w.wintypes.HWND
            dll.SetForegroundWindow.argtypes = [w.wintypes.HWND]
            notepad = dll.FindWindowW("Notepad", None)
            if notepad:
                dll.SetForegroundWindow(notepad)
                time.sleep(0.4)
            fremd_vorn = bool(notepad) and _vordergrund() == int(notepad)
            haende = Haende()
            ergebnisse: list = []

            def lauf() -> None:  # wie in der Bridge: die Hände laufen in einem eigenen Faden, die Oberfläche bleibt frei
                ergebnisse.append(haende.schreiben(
                    "Test äöü 123", kombi, feld_hat_fokus=lambda: bool(felder) and _vordergrund() == felder[0].hwnd,
                    gesperrt=lambda: False, feld_schliessen=lambda: gui.post(lambda: [f.schliessen() for f in list(felder)])))

            import threading
            faden = threading.Thread(target=lauf, daemon=True)
            faden.start()
            _pumpen_bis(gui, lambda: not faden.is_alive(), 15.0)
            ergebnis = ergebnisse[0] if ergebnisse else st_ergebnis_fehlt
            gui.pumpen(300)
            ok = ergebnis.ok and gesendet == ["Test äöü 123"]
            vorn_jetzt = _fenster_beschreibung(_vordergrund())
            feld_info = (f"Feld offen: {bool(felder)}" + (f", Fokusweg: {felder[0].fokus_weg or 'keiner hat geklappt'}" if felder else "")
                         + f"; Vordergrund danach: {vorn_jetzt}; Hotkey ausgelöst: {aufgerufen}")
            detail = (f"Notepad war vorn: {fremd_vorn}; Hände: {ergebnis}; im Feld angekommen: {gesendet}; {feld_info}")
            if ok:
                return OK, detail
            if ergebnis.grund == "feld_nicht_geoeffnet" and felder:
                return FEHLER, detail + " — das Feld öffnet sich, bekommt aber die Tastatur nicht (Vordergrundsperre von Windows)"
            return FEHLER, detail
        finally:
            gui.hotkey_loeschen("selbsttest-feld")
            for f in list(felder):
                f.schliessen()
            fremd.kill()
            try:
                fremd.wait(5)
            except subprocess.TimeoutExpired:
                pass
            gui.pumpen(200)

    def aufnahme_layered() -> tuple[str, str]:
        """Steht die Raute (ein Layered Window mit Deckkraft) im Bildschirmbild? Verglichen wird die Aufnahme mit sichtbarer gegen versteckte Raute,
        unabhängig von Deckkraft und Farbe."""
        if api is None or "raute" not in fenster:
            return UNBEKANNT, "Aufnahme oder Raute nicht verfügbar"
        from augen_haende_bridge import windows_capture

        raute = fenster["raute"]
        virtuell = api.virtual_screen_rect()
        l, o, r, u = _rect(raute.hwnd)
        x, y = (l + r) // 2, o + 9  # oben in der Raute: über dem Text, innerhalb des Randes
        breite = virtuell[2] - virtuell[0]
        ausgabe = {}
        for name, flag in (("mit CAPTUREBLT", windows_capture.CAPTUREBLT), ("ohne CAPTUREBLT", 0)):
            alt = windows_capture.CAPTUREBLT
            windows_capture.CAPTUREBLT = flag
            try:
                start = time.monotonic()
                mit = api.capture_bgra(virtuell)
                dauer = int((time.monotonic() - start) * 1000)
                raute.verberge()
                gui.pumpen(250)
                ohne = api.capture_bgra(virtuell)
            finally:
                windows_capture.CAPTUREBLT = alt
                raute.zeige(aktivieren=False)
                gui.pumpen(250)
            i = ((y - virtuell[1]) * breite + (x - virtuell[0])) * 4
            p_mit, p_ohne = tuple(mit[i:i + 3]), tuple(ohne[i:i + 3])
            unterschied = max(abs(a - b) for a, b in zip(p_mit, p_ohne))
            ausgabe[name] = (p_mit[::-1], p_ohne[::-1], unterschied >= 12, dauer)
        detail = "; ".join(f"{n}: Pixel mit Raute {v[0]}, ohne {v[1]} → {'Raute im Bild' if v[2] else 'Raute NICHT im Bild'} ({v[3]} ms)"
                           for n, v in ausgabe.items())
        if ausgabe["mit CAPTUREBLT"][2]:
            return OK, detail + ("" if ausgabe["ohne CAPTUREBLT"][2] else " — das Flag ist hier nötig und wirkt")
        return FEHLER, detail + " — Layered Windows (Raute, Ticker, Chat) fehlen im Bild: Agenten würden sie nicht sehen"

    def aufnahme_ausnehmbar() -> tuple[str, str]:
        """Lassen sich die Fenster der Bridge aus der Bildschirmaufnahme ausnehmen (Windows 10 ab 2004)? Verglichen: Aufnahme mit der Raute (normal),
        mit der Raute (ausgenommen) und ohne die Raute (versteckt). Ausgenommen muss wie versteckt aussehen."""
        if api is None or "raute" not in fenster:
            return UNBEKANNT, "Aufnahme oder Raute nicht verfügbar"
        raute = fenster["raute"]
        virtuell = api.virtual_screen_rect()
        l, o, r, u = _rect(raute.hwnd)
        x, y = (l + r) // 2, o + 9
        breite = virtuell[2] - virtuell[0]
        i = ((y - virtuell[1]) * breite + (x - virtuell[0])) * 4

        def pixel(bild_):
            return tuple(bild_[i:i + 3])

        mit = pixel(api.capture_bgra(virtuell))
        angenommen = raute.aufnahme_ausnehmen(True)
        gui.pumpen(250)
        ausgenommen = pixel(api.capture_bgra(virtuell))
        raute.aufnahme_ausnehmen(False)
        raute.verberge()
        gui.pumpen(250)
        ohne = pixel(api.capture_bgra(virtuell))
        raute.zeige(aktivieren=False)
        gui.pumpen(250)
        weg = lambda a, b: max(abs(p - q) for p, q in zip(a, b))  # noqa: E731
        detail = (f"Pixel normal {mit[::-1]}, ausgenommen {ausgenommen[::-1]}, ohne Raute {ohne[::-1]}; Windows nahm die Einstellung "
                  f"{'an' if angenommen else 'NICHT an'}")
        if not angenommen:
            return WARNUNG, detail + " — „Bridge-Fenster im Bild: aus“ geht hier nicht"
        if weg(mit, ohne) < 12:
            return UNBEKANNT, detail + " — Raute war schon normal nicht im Bild, Vergleich nicht möglich"
        return (OK, detail + " — ausgenommene Fenster fehlen im Bild, wie gewollt") if weg(ausgenommen, ohne) < 12 else (
            WARNUNG, detail + " — die Fenster sind trotz Einstellung im Bild: „Bridge-Fenster im Bild: aus“ wirkt hier nicht")

    def bilderstrom() -> tuple[str, str]:
        if api is None:
            return UNBEKANNT, "Aufnahme nicht verfügbar"
        gesendet = []
        virtuell = api.virtual_screen_rect()
        strom = Bilderstrom(
            erfassen=lambda: (api.capture_bgra(virtuell), virtuell[2] - virtuell[0], virtuell[3] - virtuell[1]),
            bildschirm=lambda: virtuell, fenster_rect=lambda h: _rect(h),
            senden=lambda tid, p: gesendet.append(p) or True)
        strom.binden("selbsttest", None)
        start = time.monotonic()
        n = strom.tick()
        dauer = int((time.monotonic() - start) * 1000)
        if not n:
            return FEHLER, "kein Bild erzeugt"
        groesse = len(gesendet[0]["data"]) * 3 // 4
        detail = f"ein Bild {gesendet[0]['width']}x{gesendet[0]['height']}, {groesse // 1024} KB JPEG, Aufnahme plus Kodierung {dauer} ms"
        return (WARNUNG if dauer > 1500 else OK), detail + (" — langsam, der Bilderstrom-Takt sollte größer sein" if dauer > 1500 else "")

    def programme() -> tuple[str, str]:
        vorn = quelle.vordergrund()
        liste = quelle.offene_programme(os.getpid())
        detail = f"Vordergrund: {vorn.programm if vorn else None}; {len(liste)} offene Programme, z. B. {[p.programm for p in liste[:5]]}"
        if not liste:
            return WARNUNG, detail + " — Programmliste leer (Programme mit Adminrechten sind ohne Adminrechte nicht lesbar)"
        return OK, detail

    def einstellungen() -> tuple[str, str]:
        ordner = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP", ".")) / "AugenUndHaendeBridge"
        e = Einstellungen(ordner / "selbsttest-einstellungen.json")
        e.setzen("test", {"x": 1})
        if not e.speichern():
            return FEHLER, f"nicht schreibbar: {e.fehler}"
        e2 = Einstellungen(ordner / "selbsttest-einstellungen.json")
        e2.laden()
        (ordner / "selbsttest-einstellungen.json").unlink(missing_ok=True)
        return (OK, f"schreiben und lesen in {ordner}") if e2.element("test") == {"x": 1} else (FEHLER, "gelesen ≠ geschrieben")

    def relay() -> tuple[str, str]:
        url = os.environ.get("BRIDGE_URL")
        if not url:
            return UNBEKANNT, "BRIDGE_URL nicht gesetzt (nur mit dem Startskript und Tunnel prüfbar)"
        ziel = urlparse(url)
        try:
            with socket.create_connection((ziel.hostname, ziel.port or 80), timeout=3):
                return OK, f"{ziel.hostname}:{ziel.port} erreichbar"
        except OSError as fehler:
            return WARNUNG, f"{ziel.hostname}:{ziel.port} nicht erreichbar: {fehler}"

    def aufraeumen() -> tuple[str, str]:
        for f in fenster.values():
            try:
                f.schliessen()
            except Exception:
                pass
        gui.pumpen(100)
        return OK, "Testfenster geschlossen"

    return [
        ("System, Bildschirm, DPI", system),
        ("Testfenster anlegen", fenster_anlegen),
        ("Durchklicken: Klicks fallen durch, mit Strg+Alt nicht", durchklick),
        ("Tastenkombinationen (Hotkeys) per echtem Tastendruck", hotkey),
        ("Bildschirmaufnahme enthält die Fenster der Bridge (Layered Windows)", aufnahme_layered),
        ("Bridge-Fenster lassen sich aus der Aufnahme ausnehmen", aufnahme_ausnehmbar),
        ("Bilderstrom: ein Takt (Aufnahme + JPEG)", bilderstrom),
        ("Offene Programme und Vordergrund", programme),
        ("Einstellungen schreiben und lesen", einstellungen),
        ("Relay erreichbar", relay),
        ("Eingabefeld und Hände, während ein Fremdprogramm vorn ist", eingabefeld_mit_fremdprogramm),
        ("Kamera (eigener Prozess)", lambda: st.geraet_im_kindprozess("kamera", befehl_basis)),
        ("Mikrofon (eigener Prozess)", lambda: st.geraet_im_kindprozess("mikrofon", befehl_basis)),
        ("Aufräumen", aufraeumen),
    ]


def befehl_basis() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, "-m", "augen_haende_bridge.koerper.haupt"]


def auswaehlen(liste: list[tuple[str, st.Pruefung]], nur: list[str], ohne: list[str]) -> list[tuple[str, st.Pruefung]]:
    """Prüfungen nach Stichworten (Teil des Namens, Groß/Klein egal) eingrenzen; Aufräumen läuft immer mit."""
    def passt(name: str, stichworte: list[str]) -> bool:
        return any(s.lower() in name.lower() for s in stichworte)

    ergebnis = []
    for name, pruefung in liste:
        if name == "Aufräumen" or ((not nur or passt(name, nur)) and not (ohne and passt(name, ohne))):
            ergebnis.append((name, pruefung))
    return ergebnis


def lauf(version: str, still: bool = False, nur: list[str] | None = None, ohne: list[str] | None = None) -> int:
    """Der ganze Selbsttest; Rückgabe: 0 wenn kein Fehler, sonst 1."""
    w.require_windows()
    gui = Anwendung()
    gui.dpi_bewusst()
    gui.starten()
    ergebnisse = st.ausfuehren(auswaehlen(pruefungen(gui, befehl_basis()), nur or [], ohne or []))
    ordner = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP", ".")) / "AugenUndHaendeBridge"
    json_pfad, text_pfad = st.bericht_schreiben(ergebnisse, st.kopf_bauen(version), ordner)
    z = st.zusammenfassung(ergebnisse)
    if still:
        return 1 if z[FEHLER] else 0
    try:
        ctypes.windll.user32.MessageBoxW(
            None, f"Selbsttest fertig: {z[OK]} ok, {z[WARNUNG]} Warnung(en), {z[FEHLER]} Fehler, {z[UNBEKANNT]} unbekannt.\n\nBericht:\n{text_pfad}",
            "Augen & Hände Bridge — Selbsttest", 0x40 if not z[FEHLER] else 0x30)
    except Exception:
        pass
    return 1 if z[FEHLER] else 0
