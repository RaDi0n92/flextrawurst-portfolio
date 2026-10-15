"""Der Einstiegspunkt der exe: setzt den ersten Körper zusammen und läuft, bis die Bridge beendet wird.

Reine Verdrahtung. Die Bausteine (Fenster, Anwendung, Not-Aus, Medien) sind einzeln gebaut und getestet.

Umgebung: `BRIDGE_URL` und `BRIDGE_TOKEN` (setzt der SSH-Starter); fehlen sie, läuft die Bridge sichtbar offline.
Ausdrückliche Prüfhaken für den Wine-Lauf der exe, im Normalbetrieb nicht gesetzt:
`BRIDGE_TEST_AUTOSTART` (start_id, die einmal gestartet wird), `BRIDGE_TEST_TIPPE` (Text, der nach dem Sitzungsstart
einmal getippt wird), `BRIDGE_TEST_DANIEL_SAGT` (Text, den Daniel nach `BRIDGE_TEST_DANIEL_NACH_S` Sekunden in den Chat schreibt),
`BRIDGE_TEST_AUDIO` (WAV-Datei, die statt des Mikrofons eingespeist wird),
`BRIDGE_TEST_UMZIEHEN` (`ort@sekunden`: schickt den Körper des ersten Agenten nach der Zeit auf diesen Desktop),
`BRIDGE_TEST_BERICHT` (Pfad, in den bei jeder Änderung der Zustandsbericht als JSON geschrieben
wird), `BRIDGE_TEST_ENDE_S` (Bridge beendet sich nach so vielen Sekunden).
Fehler landen in `%LOCALAPPDATA%\\AugenUndHaendeBridge\\bridge.log` (die exe hat kein Konsolenfenster).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.10.0-g02"


def log_pfad() -> Path:
    basis = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    ordner = Path(basis) / "AugenUndHaendeBridge"
    ordner.mkdir(parents=True, exist_ok=True)
    return ordner / "bridge.log"


def _log(text: str) -> None:
    try:
        with open(log_pfad(), "a", encoding="utf-8") as datei:
            datei.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {text}\n")
    except OSError:
        pass


@dataclass
class Plattform:
    """Was sich zwischen Windows und Linux ändert: alles Übrige des Körpers ist dasselbe. Der Ort (windows, kde1, kde2) steht in den Ziel-Schlüsseln."""

    name: str
    ort: str
    pruefen: Callable[[], None]
    hook_bauen: Callable[[object], object]  # Not-Aus-Tastenhaken
    quelle: object  # Sichtbarkeitsregeln: vordergrund(), bildschirm(), offene_programme()
    capture_api: object  # virtual_screen_rect(), capture_bgra(rect)
    datei_waehlen: Callable
    einstellungen_pfad: Path | None
    haende_senden: Callable | None = None
    scanner: object | None = None
    capture: object | None = None
    ziel_faehigkeit: Callable[[str], str] | None = None
    fenster_bild: Callable[[int], tuple[bytes, int, int] | None] | None = None  # Bild genau eines Fensters (G06.7); None = nur Bildschirmausschnitt
    mik_geraete: Callable | None = None
    fenster_vor: Callable[[int], bool] | None = None  # ein fremdes Fenster nach vorn holen (Ampel: „Fenster nach vorn“)
    piepen: Callable[[], None] | None = None  # kurzer Warnton (Ampel)
    anzeigename: str = ""
    nur_info: dict = field(default_factory=dict)


def ziel_verdeckt_pruefer(api, eigene_pid: int):
    """(Kennung) -> liegt ein anderes Fenster (nicht der Bridge) wesentlich vor dem Ziel? Aus der Fensterliste der Plattform (oben zuerst)."""
    def verdeckt(kennung: int) -> bool:
        fenster = api.enumerate_windows()
        ziel = next((f for f in fenster if f.hwnd == kennung), None)
        if ziel is None:
            return False
        flaeche = max(1, (ziel.rect[2] - ziel.rect[0]) * (ziel.rect[3] - ziel.rect[1]))
        for f in fenster:
            if f.hwnd == kennung:
                return False
            if f.process_id == eigene_pid:
                continue
            breite = min(f.rect[2], ziel.rect[2]) - max(f.rect[0], ziel.rect[0])
            hoehe = min(f.rect[3], ziel.rect[3]) - max(f.rect[1], ziel.rect[1])
            if breite > 0 and hoehe > 0 and breite * hoehe >= max(2000, 0.05 * flaeche):
                return True
        return False

    return verdeckt


def plattform_windows() -> Plattform:
    from . import win32 as w
    from .dateiwahl import datei_waehlen
    from .einstellungen import standard_pfad
    from .notaus import TastaturHook
    from .sichtbarkeit import WindowsQuelle
    from augen_haende_bridge.windows_capture import Win32CaptureApi
    from .windows_fenster_bild import fenster_bild

    quelle = WindowsQuelle()
    return Plattform(name="windows", ort="windows", pruefen=w.require_windows, hook_bauen=lambda not_aus: TastaturHook(not_aus), quelle=quelle,
                     capture_api=Win32CaptureApi(), datei_waehlen=datei_waehlen, einstellungen_pfad=standard_pfad(), anzeigename="Windows", fenster_bild=fenster_bild)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--version" in argv:
        print(f"AugenUndHaendeBridge {VERSION}")
        return 0
    if "--selbsttest-geraet" in argv:  # interner Aufruf: Kamera oder Mikrofon in einem eigenen Prozess prüfen
        i = argv.index("--selbsttest-geraet")
        from . import selbsttest

        selbsttest.geraet_pruefen(argv[i + 1], Path(argv[i + 2]))
        return 0
    if "--selbsttest" in argv:
        try:
            from . import selbsttest_windows

            def stichworte(name: str) -> list[str]:
                return [t for arg in argv if arg.startswith(name + "=") for t in arg.split("=", 1)[1].split(",") if t]

            return selbsttest_windows.lauf(VERSION, still="--still" in argv, nur=stichworte("--nur"), ohne=stichworte("--ohne"))
        except Exception:
            _log("Selbsttest abgebrochen:\n" + traceback.format_exc())
            _meldung("Der Selbsttest ist abgebrochen. Einzelheiten stehen in\n" + str(log_pfad()))
            return 1
    try:
        return _lauf()
    except Exception:
        _log("Abbruch:\n" + traceback.format_exc())
        _meldung("Die Bridge ist abgebrochen. Einzelheiten stehen in\n" + str(log_pfad()))
        return 1


def _meldung(text: str) -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, text, "Augen & Hände Bridge", 0x10)
    except Exception:
        pass


def _lauf(plattform: Plattform | None = None) -> int:
    from . import win32 as w
    from .anwendung import KoerperAnwendung
    from .chat_fenster import ChatFenster
    from .kamera_fenster import KameraFenster
    from .ziel_halter import ZielHalter
    from .zeichen_fenster import WerkzeugLeiste, ZeichenFenster
    from .pixel_fenster import PixelFenster
    from .arbeitsflaechen_anzeige import ArbeitsflaechenAnzeige
    from .bild_elemente import BildElemente
    from .bild_element_fenster import BildElementFenster
    from .komposition import Arbeitsflaechen
    from .ziel_halter import fenster_zustand
    from .fenster import bild_ausnahme_setzen
    from .erster_koerper import ErsterKoerper, arbeitsflaeche
    from .fenster import Anwendung
    from .medien import Medien
    from .notaus import NotAus
    from .ampel_fenster import AmpelFenster
    from .regie_fenster import RegieFenster
    from .einstellungen import Einstellungen
    from .sichtbarkeit import Sichtbarkeit
    from .durchklick import DurchklickVerwalter
    from .tastenkombi import Bedientaste
    from .tasten_senden import Haende
    from .mikrofon import eingabegeraete
    from .bilderstrom import Bilderstrom

    if plattform is None:
        plattform = plattform_windows()
    plattform.pruefen()
    _log(f"Start {VERSION} ({plattform.name}, Ort {plattform.ort})")
    gui = Anwendung()
    Anwendung.fehler_aufruf = lambda wo, fehler: _log(f"Fehler in {wo}: {fehler!r}\n{traceback.format_exc()}")
    gui.dpi_bewusst()
    gui.starten()

    not_aus = NotAus()
    hook = plattform.hook_bauen(not_aus)
    hook_da = hook.start()
    quelle = plattform.quelle
    einstellungen = Einstellungen(plattform.einstellungen_pfad)
    einstellungen.laden()
    if einstellungen.fehler:
        _log(einstellungen.fehler)
    sichtbarkeit = Sichtbarkeit(quelle, eigene_pid=os.getpid())
    bedientaste = Bedientaste()
    bedientaste.setzen(einstellungen.element("_global").get("bedientaste"))
    medien = Medien(frame_weitergeben=lambda agent, frame: None, not_aus=not_aus)
    globale = einstellungen.element("_global")
    if globale.get("bridge_im_bild") is False:
        bild_ausnahme_setzen(True)  # vor dem Anlegen der Fenster: sie sind dann gleich aus der Aufnahme ausgenommen
    if globale.get("mik_modus") in ("sprechtaste", "offen"):
        medien.modus = globale["mik_modus"]
    if isinstance(globale.get("mik_geraet"), str) and globale["mik_geraet"]:
        medien.mik_geraet = globale["mik_geraet"]
    if isinstance(globale.get("sprechtaste_vk"), int) and 0x08 <= globale["sprechtaste_vk"] <= 0xFE:
        medien.sprechtaste_vk = globale["sprechtaste_vk"]
    capture_api = plattform.capture_api

    def erfassen() -> tuple[bytes, int, int]:
        rect = capture_api.virtual_screen_rect()
        return capture_api.capture_bgra(rect), rect[2] - rect[0], rect[3] - rect[1]

    def fenster_rect(hwnd: int):
        import ctypes

        r = w.RECT()
        if not w.user32.IsWindow(hwnd) or not w.user32.GetWindowRect(hwnd, ctypes.byref(r)):
            return None
        return r.left, r.top, r.right, r.bottom

    bilderstrom = Bilderstrom(
        erfassen=erfassen, bildschirm=capture_api.virtual_screen_rect, fenster_rect=fenster_rect,
        senden=lambda tid, payload: anwendung.strom_senden(tid, payload), gesperrt=lambda: not_aus.aktiv,
        ziel_verschwunden=lambda tid: anwendung.strom_ziel_verschwunden(tid),
        komposit=lambda tid, gate, ausschnitt: anwendung.komposit_fuer(tid, gate, ausschnitt), fehler=_log,
        fenster_bild=plattform.fenster_bild, ziel_sichtbar=lambda hwnd: not fenster_zustand(hwnd)[1])
    arbeit = Arbeitsflaechen()
    anzeige = ArbeitsflaechenAnzeige(
        arbeit,
        fenster_bauen=lambda rect: PixelFenster(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1], titel="Objekte"),
        gate_zustand=lambda schluessel: fenster_zustand(int(schluessel.rsplit(":", 1)[1])), desktop=arbeitsflaeche,
        editor_offen=lambda: anwendung.editor_offen["schluessel"] if anwendung.editor_offen else None,
        bild_elemente=BildElemente(lambda x, y, b, h, **kw: BildElementFenster(x, y, b, h, **kw),
                                   menue=lambda oid, schluessel, x, y: anwendung.bild_element_menue(oid, schluessel, x, y),
                                   modifikator=bedientaste.gedrueckt))
    def fenster_liste() -> list[tuple[int, str, str]]:
        """Fenster, in die man zeichnen kann („Ziel …“ im Zeichenmodus): sichtbar, mit Titel, nicht von der Bridge selbst, nicht winzig."""
        liste = []
        for f in quelle._api.enumerate_windows():
            if f.process_id == os.getpid() or not f.visible or not (f.title or "").strip():
                continue
            if f.rect[2] - f.rect[0] < 120 or f.rect[3] - f.rect[1] < 80:
                continue
            liste.append((f.hwnd, f.title, f.process_path or ""))
        return liste

    from .haende_anbindung import baue_haende

    anwendung_ref: list = []  # die Anwendung entsteht erst nach den Händen; die Ausnahme Daniels liest sie von dort
    haende_buendel = baue_haende(plattform.name, plattform.ort, not_aus, ausnahme=lambda: bool(anwendung_ref and anwendung_ref[0].daniel_ausnahme),
                                 protokoll_pfad=einstellungen.pfad.with_name("haende_protokoll.jsonl") if einstellungen.pfad else None)
    if haende_buendel.fehler:
        _log(haende_buendel.fehler)
    haende_buendel.starten()
    from .weltdom_anbindung import baue_weltdom

    weltdom_dienst = baue_weltdom(plattform, plattform.ort, haende_buendel.engine, anwendung_ref, pfad=einstellungen.pfad.with_name("weltdom.json") if einstellungen.pfad else None)

    anwendung = KoerperAnwendung(
        url=os.environ.get("BRIDGE_URL"), token=os.environ.get("BRIDGE_TOKEN"), gui=gui,
        ort=plattform.ort, ziel_zustaende=True, ziel_verdeckt=ziel_verdeckt_pruefer(quelle._api, os.getpid()) if hasattr(quelle, "_api") else None,
        ziel_faehigkeit=plattform.ziel_faehigkeit,
        koerper_bauen=lambda **kwargs: ErsterKoerper(**{**({"scanner": plattform.scanner} if plattform.scanner is not None else {}),
                                                         **({"capture": plattform.capture} if plattform.capture is not None else {}), **kwargs}),
        regie_bauen=RegieFenster, ampel_bauen=AmpelFenster, fenster_vor=plattform.fenster_vor, piepen=plattform.piepen, chat_bauen=ChatFenster, kamera_bauen=KameraFenster, ziel_halter=ZielHalter(),
        datei_waehlen=plattform.datei_waehlen, arbeit=arbeit, zeichen_bauen=lambda rect, editor, farbe: ZeichenFenster(rect, editor, farbe_hex=farbe, modifikator=bedientaste.gedrueckt),
        leiste_bauen=lambda x, y, editor, **kw: WerkzeugLeiste(x, y, editor, **kw), anzeige=anzeige, arbeit_pfad=einstellungen.pfad.with_name("arbeitsflaeche.json") if einstellungen.pfad else None,
        medien=medien, fenster_liste=fenster_liste,
        arbeitsflaeche=arbeitsflaeche, not_aus=not_aus,
        sichtbarkeit=sichtbarkeit, durchklick=DurchklickVerwalter(strg=bedientaste.gedrueckt), bedientaste=bedientaste, haende=Haende(senden=plattform.haende_senden) if plattform.haende_senden is not None else Haende(), bilderstrom=bilderstrom, haende_engine=haende_buendel.engine, weltdom_dienst=weltdom_dienst,
        mik_geraete=plattform.mik_geraete or eingabegeraete, einstellungen=einstellungen, bildschirm=quelle.bildschirm,
        programme=lambda: quelle.offene_programme(os.getpid()),
        test_autostart=os.environ.get("BRIDGE_TEST_AUTOSTART"), test_tippe=os.environ.get("BRIDGE_TEST_TIPPE"))
    if globale.get("bridge_im_bild") is False:
        anwendung.bridge_im_bild = False
    anwendung.daniel_ausnahme = globale.get("daniel_ausnahme") is True
    anwendung_ref.append(anwendung)

    letzter = [None]

    def protokollieren() -> None:  # jede Änderung von Status/Hinweis/Agentenzustand landet im Log (Fehlersuche vor Ort)
        zeile = (anwendung.status, anwendung.hinweis, tuple((a.name, a.zustand) for a in anwendung.agenten.values()))
        if zeile != letzter[0]:
            letzter[0] = zeile
            _log(f"Zustand: {zeile}")
    anwendung.beobachter.append(protokollieren)

    anwendung.fehler_haken = Anwendung.fehler
    anwendung.log = _log
    anwendung.notbremse = lambda: (_log("Notbremse beim Beenden: Prozess wird beendet"), os._exit(0))

    bericht_pfad = os.environ.get("BRIDGE_TEST_BERICHT")
    if bericht_pfad:
        def bericht_schreiben() -> None:
            daten = anwendung.bericht()
            daten["f12_hook_installiert"] = hook_da
            Path(bericht_pfad).write_text(json.dumps(daten, ensure_ascii=True, indent=1), encoding="utf-8")
        anwendung.beobachter.append(bericht_schreiben)
    ende_s = os.environ.get("BRIDGE_TEST_ENDE_S")
    if ende_s:
        def testende() -> None:
            if bericht_pfad:  # letzter Bericht, solange die Körper noch stehen
                bericht_schreiben()
                anwendung.beobachter.remove(bericht_schreiben)
            anwendung.beenden()
        threading.Timer(float(ende_s), lambda: gui.post(testende)).start()

    umzug = os.environ.get("BRIDGE_TEST_UMZIEHEN")  # „kde2@12“: nach 12 s den Körper des ersten Agenten auf kde2 schicken (derselbe Weg wie das Menü „Anzeigeort“)
    if umzug and "@" in umzug:
        ziel_ort, sekunden = umzug.split("@", 1)
        threading.Timer(float(sekunden), lambda: gui.post(lambda: anwendung.agenten and anwendung.anzeigeort_wechseln(next(iter(anwendung.agenten)), ziel_ort))).start()
    daniel_text = os.environ.get("BRIDGE_TEST_DANIEL_SAGT")
    if daniel_text:  # Prüfhaken: Daniel schreibt einmal in den Chat, wie eine Eingabe mit Enter
        threading.Timer(float(os.environ.get("BRIDGE_TEST_DANIEL_NACH_S", "8")),
                        lambda: gui.post(lambda: anwendung.daniel_sagt(daniel_text))).start()
    audio_datei = os.environ.get("BRIDGE_TEST_AUDIO")
    if audio_datei:  # Prüfhaken: statt des Mikrofons wird eine WAV-Datei (16 kHz, mono) eingespeist, sobald ein Agent läuft
        gestartet = []

        def audio_einspeisen() -> None:
            import wave

            if gestartet or not anwendung.agenten:
                return
            gestartet.append(True)
            tid = next(iter(anwendung.agenten))
            medien.modus = "offen"

            def lauf() -> None:
                with wave.open(audio_datei, "rb") as datei:
                    pcm = datei.readframes(datei.getnframes())
                segment = medien.fuer(tid).segment
                block = 3200  # 0,1 s
                for i in range(0, len(pcm), block):
                    segment.block(pcm[i:i + block], 16000)
                    time.sleep(0.01)
                for _ in range(15):  # Stille zum Abschluss der Äußerung
                    segment.block(b"\x00" * block, 16000)
                    time.sleep(0.01)

            threading.Thread(target=lauf, daemon=True, name="test-audio").start()

        anwendung.beobachter.append(audio_einspeisen)
    anwendung.starten()
    if not hook_da:
        anwendung.hinweis = f"F12-Not-Aus nicht verfügbar: {hook.fehler}"
        _log(anwendung.hinweis)
    code = gui.schleife()
    _log(f"Schleife beendet ({code})")
    # Notbremse: bleibt beim Aufräumen irgendetwas hängen, endet der Prozess trotzdem nach wenigen Sekunden.
    watchdog = threading.Timer(5.0, lambda: (_log("Notbremse: Prozess wird beendet"), os._exit(code)))
    watchdog.daemon = True
    watchdog.start()
    haende_buendel.stoppen()
    hook.stop()
    medien.alles_stoppen()
    _log(f"Ende {code}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
