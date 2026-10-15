"""Koerper-Smoketest unter Wine: baut ein echtes RauteFenster und ein echtes TerminalFenster aus koerper/*.py und
prueft per WindowFromPoint/GetWindowRect/GetLayeredWindowAttributes, ob Form, Deckkraft und Schriftaufbau wirklich so
ankommen wie in raute_fenster.py/terminal_fenster.py programmiert.

Bewusst keine Bildschirmaufnahme: Xvfb ohne Compositor stellt Layered-/geformte Fenster als bildschirmgrosse
X-Fenster dar, ein Pixel-Screenshot waere irrefuehrend (siehe die G01-Entscheidung in window_probe.py, die deshalb
schon auf reine WindowFromPoint-Trefferpruefung umgestiegen ist). Dieser Smoketest bindet GetWindowRgnBox selbst
(kein Teil von koerper/win32.py, weil dort nicht gebraucht) und bleibt sonst bei den ueber koerper/win32.py bereits
gebundenen Funktionen. Druckt eine JSON-Zeile und beendet sich selbst (kein externer Treiber noetig)."""

from __future__ import annotations

import ctypes
import json
import os
import sys
import time

if os.name != "nt":
    print(json.dumps({"status": "unavailable", "reason": "not_windows"}))
    sys.exit(0)

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.erster_koerper import ErsterKoerper
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.erster_koerper import arbeitsflaeche
from augen_haende_bridge.koerper.nachricht_fenster import BannerFenster, TickerFenster
from augen_haende_bridge.koerper.notaus import NotAus, TastaturHook
from augen_haende_bridge.koerper.raute_fenster import GROESSE, RauteFenster
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster

# koerper/win32.py bindet nur, was der Koerper selbst braucht; GetWindowRgnBox ist nur fuer diese Diagnose noetig
# und wird deshalb ueber eine eigene, separate DLL-Anbindung geholt statt die _Table-Kapselung aufzubrechen.
_diagnose_user32 = ctypes.WinDLL("user32", use_last_error=True)
_diagnose_user32.GetWindowRgnBox.argtypes = [w.wintypes.HWND, ctypes.POINTER(w.RECT)]
_diagnose_user32.GetWindowRgnBox.restype = ctypes.c_int
_diagnose_user32.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_uint32, ctypes.c_size_t]
_diagnose_user32.keybd_event.restype = None
KEYEVENTF_KEYUP = 0x0002


def fensterrechteck(hwnd) -> list[int]:
    rect = w.RECT()
    w.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return [rect.left, rect.top, rect.right, rect.bottom]


def main() -> int:
    ergebnis: dict = {}

    # Not-Aus zuerst: der Hook läuft im eigenen Faden; der Haupt-Thread pumpt währenddessen KEINE Nachrichten.
    not_aus = NotAus()
    hook = TastaturHook(not_aus)
    hook_da = hook.start()
    _diagnose_user32.keybd_event(w.VK_F1, 0, 0, 0)  # eine andere Taste darf nichts auslösen
    _diagnose_user32.keybd_event(w.VK_F1, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)
    nach_f1 = not_aus.aktiv
    t_taste = time.monotonic()
    _diagnose_user32.keybd_event(w.VK_F12, 0, 0, 0)
    _diagnose_user32.keybd_event(w.VK_F12, 0, KEYEVENTF_KEYUP, 0)
    for _ in range(100):
        if not_aus.aktiv:
            break
        time.sleep(0.01)
    ergebnis["not_aus"] = {
        "hook_installiert": hook_da, "hook_fehler": hook.fehler,
        "andere_taste_loest_nicht_aus": not nach_f1,
        "f12_loest_aus": not_aus.aktiv, "grund": not_aus.grund,
        "gemessen_bis_flag_ms_nur_hinweis": round((time.monotonic() - t_taste) * 1000),
        "gui_thread_pumpte_nicht": True,
    }
    hook.stop()
    ergebnis["not_aus"]["hook_gestoppt"] = not hook.installiert

    anwendung = Anwendung()
    anwendung.starten()

    raute = RauteFenster(200, 200, name="testagent", farbe_hex="#00E5FF", kuerzel="TA", hotkey="F13")
    raute.zeige()
    anwendung.pumpen(200)

    raute_rect = fensterrechteck(raute.hwnd)
    links, oben = raute_rect[0], raute_rect[1]
    mitte = GROESSE // 2

    alpha = ctypes.c_ubyte(0)
    farbe = w.COLORREF(0)
    flags = w.wintypes.DWORD(0)
    alpha_readback_ok = bool(w.user32.GetLayeredWindowAttributes(raute.hwnd, ctypes.byref(farbe), ctypes.byref(alpha), ctypes.byref(flags)))

    box = w.RECT()
    region_type = int(_diagnose_user32.GetWindowRgnBox(raute.hwnd, ctypes.byref(box)))

    def trifft_raute(dx: int, dy: int) -> bool:
        getroffen = w.user32.WindowFromPoint(w.POINT(links + dx, oben + dy))
        return bool(getroffen) and int(getroffen) == int(raute.hwnd)

    exstil_klickdurchlaessig = int(w.user32.GetWindowLongPtrW(raute.hwnd, w.GWL_EXSTYLE))
    mitte_klickdurchlaessig = trifft_raute(mitte, mitte)
    # Strg wirklich drücken (nur in dieser Probe); der Modifikator-Timer der Raute muss das selbst bemerken.
    _diagnose_user32.keybd_event(w.VK_CONTROL, 0, 0, 0)
    anwendung.pumpen(300)
    exstil_bedienbar = int(w.user32.GetWindowLongPtrW(raute.hwnd, w.GWL_EXSTYLE))
    raute_bedienbar_nach_strg = raute.bedienbar

    ergebnis["raute"] = {
        "rect": raute_rect,
        "erwartete_groesse": [GROESSE, GROESSE],
        "groesse_stimmt": (raute_rect[2] - raute_rect[0], raute_rect[3] - raute_rect[1]) == (GROESSE, GROESSE),
        "alpha_readback_ok": alpha_readback_ok,
        "alpha_wert": int(alpha.value) if alpha_readback_ok else None,
        "alpha_erwartet": raute.deckkraft,
        "region_gesetzt": region_type != 0,  # 0 = NULLREGION/Fehler, >0 = SIMPLEREGION/COMPLEXREGION
        "region_box": [box.left, box.top, box.right, box.bottom],
        "klickdurchlaessig_transparent_bit": bool(exstil_klickdurchlaessig & w.WS_EX_TRANSPARENT),
        "klickdurchlaessig_mitte_faellt_durch": not mitte_klickdurchlaessig,
        "bedienbar_transparent_bit": bool(exstil_bedienbar & w.WS_EX_TRANSPARENT),
        "bedienbar_treffer_mitte": trifft_raute(mitte, mitte),
        "bedienbar_treffer_ecke_oben_links": trifft_raute(1, 1),
        "bedienbar_treffer_ecke_oben_rechts": trifft_raute(GROESSE - 2, 1),
        "bedienbar_treffer_ecke_unten_links": trifft_raute(1, GROESSE - 2),
        "bedienbar_treffer_ecke_unten_rechts": trifft_raute(GROESSE - 2, GROESSE - 2),
        "kuerzel_schrift_aufgebaut": raute.f_kuerzel is not None and bool(raute.f_kuerzel.handle),
        "fenstertitel": raute.titel,
    }
    _diagnose_user32.keybd_event(w.VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    anwendung.pumpen(300)
    ergebnis["raute"]["strg_gedrueckt_bedienbar"] = raute_bedienbar_nach_strg
    ergebnis["raute"]["strg_losgelassen_wieder_klickdurchlaessig"] = (
        not raute.bedienbar and bool(int(w.user32.GetWindowLongPtrW(raute.hwnd, w.GWL_EXSTYLE)) & w.WS_EX_TRANSPARENT))
    ergebnis["raute"]["strg_losgelassen_mitte_faellt_durch"] = not trifft_raute(mitte, mitte)

    # Banner und Ticker in echter Zeit: beide entstehen gleichzeitig, das Banner blendet aus, der Ticker bleibt länger.
    ziel = arbeitsflaeche()
    geschlossen = {"banner_ms": None, "ticker_ms": None}
    t0 = int(time.monotonic() * 1000)
    jetzt = lambda: int(time.monotonic() * 1000)  # noqa: E731
    banner = BannerFenster(text="Shader kompiliert!", farbe_hex="#00E5FF", ziel_rechteck=ziel,
                           raute_rechteck=tuple(raute_rect), jetzt_ms=jetzt,
                           geschlossen=lambda: geschlossen.__setitem__("banner_ms", jetzt() - t0))
    ticker = TickerFenster(text="Shader kompiliert!", farbe_hex="#00E5FF", raute_rechteck=tuple(raute_rect),
                           geschlossen=lambda: geschlossen.__setitem__("ticker_ms", jetzt() - t0))
    banner.zeige(aktivieren=False)
    ticker.zeige(aktivieren=False)
    banner_rect, ticker_rect = fensterrechteck(banner.hwnd), fensterrechteck(ticker.hwnd)

    def alpha_von(hwnd) -> int | None:
        a, k, f = ctypes.c_ubyte(0), w.COLORREF(0), w.wintypes.DWORD(0)
        ok = w.user32.GetLayeredWindowAttributes(hwnd, ctypes.byref(k), ctypes.byref(a), ctypes.byref(f))
        return int(a.value) if ok else None

    def faellt_durch(rect) -> bool:
        getroffen = w.user32.WindowFromPoint(w.POINT((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2))
        return int(getroffen or 0) not in (int(banner.hwnd or 0), int(ticker.hwnd or 0))

    banner_durchlaessig, ticker_durchlaessig = faellt_durch(banner_rect), faellt_durch(ticker_rect)
    alpha_verlauf = []
    for _ in range(12):  # etwa alle 250 ms bis kurz vor 3,3 s
        anwendung.pumpen(250)
        if geschlossen["banner_ms"] is None and w.user32.IsWindow(banner.hwnd):
            alpha_verlauf.append([jetzt() - t0, alpha_von(banner.hwnd)])
    anwendung.pumpen(900)  # jetzt etwa 3,9-4,1 s
    ticker_da_nach_4_s = geschlossen["ticker_ms"] is None and bool(w.user32.IsWindow(ticker.hwnd))
    anwendung.pumpen(3000)  # jetzt deutlich nach 6,6 s
    werte = [a for _t, a in alpha_verlauf if a is not None]

    ergebnis["banner_ticker"] = {
        "ziel_arbeitsflaeche": list(ziel),
        "banner_rect": banner_rect,
        "ticker_rect": ticker_rect,
        "banner_im_zielbereich": ziel[0] <= banner_rect[0] and banner_rect[2] <= ziel[2]
                                 and ziel[1] <= banner_rect[1] and banner_rect[3] <= ziel[3],
        "banner_zur_raute_gezogen": banner_rect[0] + (banner_rect[2] - banner_rect[0]) // 2 < (ziel[0] + ziel[2]) // 2,
        "ticker_direkt_rechts_an_der_raute": ticker_rect[0] - raute_rect[2] in range(0, 20),
        "banner_klickdurchlaessig": banner_durchlaessig,
        "ticker_klickdurchlaessig": ticker_durchlaessig,
        "alpha_verlauf_ms_wert": alpha_verlauf,
        "alpha_faellt_monoton": all(a >= b for a, b in zip(werte, werte[1:])) and len(set(werte)) >= 5,
        "banner_geschlossen_nach_ms": geschlossen["banner_ms"],
        "ticker_noch_da_nach_4_s": ticker_da_nach_4_s,
        "ticker_geschlossen_nach_ms": geschlossen["ticker_ms"],
    }

    raute.schliessen()
    anwendung.pumpen(100)

    terminal = TerminalFenster(400, 200, zeilen=24, spalten=80, name="testagent", ort="vd1", farbe_hex="#FFD600")
    terminal.zeige()
    anwendung.pumpen(200)
    terminal.ausgabe(b"hallo koerper\r\n")
    anwendung.pumpen(200)

    terminal_rect = fensterrechteck(terminal.hwnd)
    zeilen, spalten = terminal.zeilen_spalten()

    ergebnis["terminal"] = {
        "rect": terminal_rect,
        "angeforderte_zeilen_spalten": [24, 80],
        "tatsaechliche_zeilen_spalten": [zeilen, spalten],
        "zellbreite_px": terminal.zell_b,
        "zellhoehe_px": terminal.zell_h,
        "schriftname_terminal": terminal.f_terminal.tatsaechlich,
        "schriftname_ui": terminal.f_ui.tatsaechlich,
        "modell_geschrieben_zeile_0": terminal.modell.zeile_text(0)[:20],
    }

    terminal.schliessen()
    anwendung.pumpen(100)

    gesendete_texte: list[str] = []
    chat = ChatFenster(600, 200, name="testagent", farbe_hex="#FFD600", gesendet=gesendete_texte.append,
                        jetzt_text=lambda: "12:00")
    chat.zeige()
    chat.empfangen("testagent", "Shader kompiliert!")
    for zeichen in "hi":
        chat.bei_zeichen(ord(zeichen), False)
    chat.bei_zeichen(0x0D, False)  # Enter
    anwendung.pumpen(150)

    chat_rect = fensterrechteck(chat.hwnd)
    ergebnis["chat"] = {
        "rect": chat_rect,
        "verlauf": chat.verlauf,
        "gesendete_texte": gesendete_texte,
        "eingabe_nach_senden_leer": chat.eingabe == "",
        "schrift_aufgebaut": chat.f_text is not None and bool(chat.f_text.handle),
    }
    chat.schliessen()
    anwendung.pumpen(100)

    # ---- ErsterKoerper: die echte Verdrahtung, nicht nur einzelne Fenster --------------------------------------
    empfangene_bytes: list[bytes] = []
    menue_gesehen: list[str] = []

    def auswahl_haken(_hwnd, eintraege, _x, _y) -> int:
        """Ausdrücklicher Test-Haken statt des blockierenden Popup-Menüs: wählt das eigene Terminalfenster."""
        menue_gesehen.extend(text for (_id, text, _f) in (e for e in eintraege if e))
        for befehl, text, _flags in (e for e in eintraege if e):
            if text == "testagent2 · vd1":
                return befehl
        return 0

    koerper = ErsterKoerper(name="testagent2", ort="vd1", farbe_hex="#00E676",
                            raute_position=(900, 200), terminal_position=(1000, 200),
                            terminal_senden=empfangene_bytes.append, menue_anzeigen=auswahl_haken)
    koerper.zeigen()
    anwendung.pumpen(200)

    koerper.raute.sagen("Shader kompiliert!")  # echter Weg: RauteFenster.sagen -> ErsterKoerper._raute_hat_gesprochen
    anwendung.pumpen(150)
    banner_und_ticker_nach_sagen = koerper.banner is not None and koerper.ticker is not None

    koerper.raute._klick()  # echter Weg: derselbe Callback, den ein echter Klick ohne Zug ausloesen wuerde
    anwendung.pumpen(150)
    chat_existiert_nach_klick = koerper.chat is not None

    if koerper.chat is not None:
        for zeichen in "ok":
            koerper.chat.bei_zeichen(ord(zeichen), False)
        koerper.chat.bei_zeichen(0x0D, False)
        anwendung.pumpen(150)

    # Scanner-Knopf des Terminals über denselben Weg wie ein echter Klick darauf; echte Aufnahme, echtes Inventar.
    koerper.terminal._knopf_ausloesen("scanner")
    anwendung.pumpen(150)
    lauf = koerper.letzter_scanner_lauf
    bindung = koerper.bindung
    terminal_fenster_rect = tuple(fensterrechteck(koerper.terminal.hwnd))
    koerper.raute.sagen("nach der Bindung")
    anwendung.pumpen(100)
    banner_nach_bindung = tuple(fensterrechteck(koerper.banner.hwnd)) if koerper.banner is not None else None
    ergebnis["scanner"] = {
        "menue_eintraege": menue_gesehen,
        "beweise": [p for p in ("SCAN_REQUESTED", "FRAME_CAPTURED", "INVENTORY_READ", "TARGET_SELECTED",
                                "IDENTITY_VERIFIED", "BINDING_CREATED", "BINDING_READ_BACK") if lauf and p in lauf.proofs],
        "harness_status": lauf.status.value if lauf else None,
        "gebunden_an": bindung.binding.target_id if bindung else None,
        "generation": bindung.binding.target_generation if bindung else None,
        "rechte": sorted(c.value for c in bindung.binding.capabilities) if bindung else None,
        "gebundenes_rect": list(bindung.item.rect) if bindung else None,
        "echtes_fenster_rect": list(terminal_fenster_rect),
        "rect_stimmt": bool(bindung) and tuple(bindung.item.rect) == terminal_fenster_rect,
        "terminal_zieltext": koerper.terminal.ziel_text,
        "terminal_ziel_gebunden": koerper.terminal.ziel_gebunden,
        "banner_nach_bindung": list(banner_nach_bindung) if banner_nach_bindung else None,
        "banner_im_gebundenen_fenster": bool(banner_nach_bindung) and terminal_fenster_rect[0] <= banner_nach_bindung[0]
            and banner_nach_bindung[2] <= terminal_fenster_rect[2] and terminal_fenster_rect[1] <= banner_nach_bindung[1]
            and banner_nach_bindung[3] <= terminal_fenster_rect[3],
    }

    # Der echte Fensterscanner (kein Fake) unter Wine: findet er die soeben erzeugten echten Fenster wieder?
    frame = koerper._capture_quelle.capture()
    snapshot = koerper._scanner_quelle.scan(frame_ref=frame.frame_ref, frame_hash=frame.frame_hash,
                                            captured_at_ms=frame.captured_at_ms)
    gefundene_titel = [item.label for item in snapshot.items]

    ergebnis["erster_koerper"] = {
        "banner_und_ticker_entstanden_durch_sagen": banner_und_ticker_nach_sagen,
        "chat_entstand_durch_klick": chat_existiert_nach_klick,
        "chat_verlauf": koerper.chat.verlauf if koerper.chat is not None else None,
        "terminal_hat_getipptes_empfangen": b"".join(empfangene_bytes) == b"ok",
        "scanner_frame_breite_hoehe": [frame.width, frame.height],
        "scanner_fand_eigene_fenster": any("testagent2" in titel for titel in gefundene_titel),
        "scanner_anzahl_ziele": len(snapshot.items),
    }

    koerper.schliessen()
    anwendung.pumpen(100)

    # ASCII-Escapes: die Windows-Konsole unter Wine hat cp1252 und kann z. B. »◆« nicht ausgeben.
    print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
