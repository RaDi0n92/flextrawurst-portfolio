"""Fenstergerüst des Körpers: Nachrichtenschleife, Fensterklasse, Zeichenfläche und Schrift über Win32/GDI.

Jedes Fenster des Körpers ist eine Unterklasse von `Fenster`. Alle Fenster leben im GUI-Thread; andere Threads reichen Arbeit
über `Anwendung.post` herein.
"""

from __future__ import annotations

import ctypes
import queue
from collections.abc import Callable
from typing import Any

from . import win32 as w
from .win32 import POINT, RECT

WM_AUH_POST = w.WM_APP + 1


class Schrift:
    """Eine GDI-Schrift mit gemessener Zellgröße (für Zeichengitter) oder Zeilenhöhe (für Text)."""

    def __init__(self, hdc, name: str, hoehe_px: int, *, fett: bool = False, fest: bool = True):
        w.require_windows()
        pitch = (w.FIXED_PITCH | w.FF_MODERN) if fest else (w.DEFAULT_PITCH | w.FF_DONTCARE)
        self.handle = w.gdi32.CreateFontW(-abs(hoehe_px), 0, 0, 0, w.FW_BOLD if fett else w.FW_NORMAL, 0, 0, 0,
                                         w.DEFAULT_CHARSET, w.OUT_TT_PRECIS, w.CLIP_DEFAULT_PRECIS, w.CLEARTYPE_QUALITY,
                                         pitch, name)
        old = w.gdi32.SelectObject(hdc, self.handle)
        metrics = w.TEXTMETRICW()
        w.gdi32.GetTextMetricsW(hdc, ctypes.byref(metrics))
        gesucht = ctypes.create_unicode_buffer(64)
        w.gdi32.GetTextFaceW(hdc, 64, gesucht)
        w.gdi32.SelectObject(hdc, old)
        self.name = name
        self.tatsaechlich = gesucht.value
        self.zellbreite = max(1, metrics.tmAveCharWidth)
        self.zellhoehe = max(1, metrics.tmHeight + metrics.tmExternalLeading)
        self.ascent = metrics.tmAscent

    def hat_glyphen(self, hdc, zeichen: str) -> list[bool]:
        """Für jedes Zeichen: besitzt diese Schrift ein Glyph dafür (statt des Ersatzkästchens)?"""
        anzahl = len(zeichen)
        felder = (w.wintypes.WORD * anzahl)()
        old = w.gdi32.SelectObject(hdc, self.handle)
        ergebnis = w.gdi32.GetGlyphIndicesW(hdc, zeichen, anzahl, felder, w.GGI_MARK_NONEXISTING_GLYPHS)
        w.gdi32.SelectObject(hdc, old)
        if ergebnis == 0xFFFFFFFF:
            return [True] * anzahl
        return [felder[i] != 0xFFFF for i in range(anzahl)]

    def breite(self, hdc, text: str) -> int:
        old = w.gdi32.SelectObject(hdc, self.handle)
        size = w.SIZE()
        w.gdi32.GetTextExtentPoint32W(hdc, text, len(text), ctypes.byref(size))
        w.gdi32.SelectObject(hdc, old)
        return size.cx

    def freigeben(self) -> None:
        if self.handle:
            w.gdi32.DeleteObject(self.handle)
            self.handle = None


class Leinwand:
    """Hintergrundpuffer (DIB, 32 Bit, von oben nach unten), auf den ein Fenster zeichnet und der dann auf den Schirm kopiert wird."""

    def __init__(self, breite: int, hoehe: int):
        w.require_windows()
        self.breite, self.hoehe = max(1, breite), max(1, hoehe)
        screen = w.user32.GetDC(None)
        self.hdc = w.gdi32.CreateCompatibleDC(screen)
        info = w.BITMAPINFO()
        info.bmiHeader.biSize = ctypes.sizeof(w.BITMAPINFOHEADER)
        info.bmiHeader.biWidth = self.breite
        info.bmiHeader.biHeight = -self.hoehe
        info.bmiHeader.biPlanes = 1
        info.bmiHeader.biBitCount = 32
        info.bmiHeader.biCompression = w.BI_RGB
        bits = ctypes.c_void_p()
        self.bitmap = w.gdi32.CreateDIBSection(screen, ctypes.byref(info), w.DIB_RGB_COLORS, ctypes.byref(bits), None, 0)
        w.user32.ReleaseDC(None, screen)
        self._bits = bits
        self._alt = w.gdi32.SelectObject(self.hdc, self.bitmap)
        w.gdi32.SetBkMode(self.hdc, w.TRANSPARENT)
        self._pinsel: dict[int, int] = {}

    def _pinsel_fuer(self, farbe: int) -> int:
        pinsel = self._pinsel.get(farbe)
        if pinsel is None:
            pinsel = self._pinsel[farbe] = w.gdi32.CreateSolidBrush(farbe)
        return pinsel

    def bgr_zeichnen(self, bgr: bytes, bild_b: int, bild_h: int, x: int, y: int, breite: int, hoehe: int, *, spiegeln: bool = False) -> bool:
        """Ein Kamerabild (BGR, Zeile für Zeile von oben nach unten) auf die Fläche (x, y, breite, hoehe) skaliert zeichnen, ggf. seitenverkehrt."""
        if breite < 1 or hoehe < 1 or bild_b < 1 or bild_h < 1 or len(bgr) < bild_b * bild_h * 3:
            return False
        zeile = bild_b * 3
        if zeile % 4:  # DIB-Zeilen sind auf 4 Byte ausgerichtet
            auffuellung = bytes(4 - zeile % 4)
            bgr = b"".join(bgr[i * zeile:(i + 1) * zeile] + auffuellung for i in range(bild_h))
        info = w.BITMAPINFO()
        info.bmiHeader.biSize = ctypes.sizeof(w.BITMAPINFOHEADER)
        info.bmiHeader.biWidth = bild_b
        info.bmiHeader.biHeight = -bild_h
        info.bmiHeader.biPlanes = 1
        info.bmiHeader.biBitCount = 24
        info.bmiHeader.biCompression = w.BI_RGB
        w.gdi32.SetStretchBltMode(self.hdc, w.HALFTONE)
        ziel_x, ziel_b = (x + breite, -breite) if spiegeln else (x, breite)
        puffer = ctypes.create_string_buffer(bgr, len(bgr))
        return bool(w.gdi32.StretchDIBits(self.hdc, ziel_x, y, ziel_b, hoehe, 0, 0, bild_b, bild_h, puffer, ctypes.byref(info),
                                          w.DIB_RGB_COLORS, w.SRCCOPY))

    def fuellen(self, farbe: int, links: int = 0, oben: int = 0, rechts: int | None = None, unten: int | None = None) -> None:
        rect = RECT(links, oben, self.breite if rechts is None else rechts, self.hoehe if unten is None else unten)
        w.user32.FillRect(self.hdc, ctypes.byref(rect), self._pinsel_fuer(farbe))

    def text(self, x: int, y: int, text: str, farbe: int, schrift: Schrift, *, hintergrund: int | None = None,
             zellbreite: int | None = None, breiten: list[int] | None = None) -> None:
        """Text ab (x, y). Mit `zellbreite` bekommt jedes Zeichen genau diese Breite (Zeichengitter), mit `breiten` je Zeichen eine eigene."""
        if not text:
            return
        old = w.gdi32.SelectObject(self.hdc, schrift.handle)
        w.gdi32.SetTextColor(self.hdc, farbe)
        options = 0
        rect = None
        abstaende = breiten if breiten is not None else ([zellbreite] * len(text) if zellbreite else None)
        if hintergrund is not None:
            w.gdi32.SetBkColor(self.hdc, hintergrund)
            options |= w.ETO_OPAQUE
            breite = sum(abstaende) if abstaende else schrift.breite(self.hdc, text)
            rect = RECT(x, y, x + breite, y + schrift.zellhoehe)
        dx = (ctypes.c_int * len(text))(*abstaende) if abstaende else None
        w.gdi32.ExtTextOutW(self.hdc, x, y, options, ctypes.byref(rect) if rect is not None else None, text, len(text), dx)
        w.gdi32.SelectObject(self.hdc, old)

    def polygon(self, punkte: list[tuple[int, int]], fuellfarbe: int, randfarbe: int | None = None, randbreite: int = 1) -> None:
        array = (POINT * len(punkte))(*[POINT(x, y) for x, y in punkte])
        pinsel = self._pinsel_fuer(fuellfarbe)
        alt_pinsel = w.gdi32.SelectObject(self.hdc, pinsel)
        stift = w.gdi32.CreatePen(w.PS_SOLID, randbreite, randfarbe) if randfarbe is not None else w.gdi32.GetStockObject(w.NULL_PEN)
        alt_stift = w.gdi32.SelectObject(self.hdc, stift)
        w.gdi32.Polygon(self.hdc, array, len(punkte))
        w.gdi32.SelectObject(self.hdc, alt_stift)
        w.gdi32.SelectObject(self.hdc, alt_pinsel)
        if randfarbe is not None:
            w.gdi32.DeleteObject(stift)

    def linie(self, x1: int, y1: int, x2: int, y2: int, farbe: int, breite: int = 1) -> None:
        stift = w.gdi32.CreatePen(w.PS_SOLID, breite, farbe)
        alt = w.gdi32.SelectObject(self.hdc, stift)
        w.gdi32.MoveToEx(self.hdc, x1, y1, None)
        w.gdi32.LineTo(self.hdc, x2, y2)
        w.gdi32.SelectObject(self.hdc, alt)
        w.gdi32.DeleteObject(stift)

    def rahmen(self, links: int, oben: int, rechts: int, unten: int, farbe: int, breite: int = 1) -> None:
        for i in range(breite):
            self.fuellen(farbe, links + i, oben + i, rechts - i, oben + i + 1)
            self.fuellen(farbe, links + i, unten - i - 1, rechts - i, unten - i)
            self.fuellen(farbe, links + i, oben + i, links + i + 1, unten - i)
            self.fuellen(farbe, rechts - i - 1, oben + i, rechts - i, unten - i)

    def auf(self, hdc, x: int = 0, y: int = 0) -> None:
        w.gdi32.BitBlt(hdc, x, y, self.breite, self.hoehe, self.hdc, 0, 0, w.SRCCOPY)

    def bgra(self) -> bytes:
        w.gdi32.GdiFlush()
        return ctypes.string_at(self._bits, self.breite * self.hoehe * 4)

    def freigeben(self) -> None:
        if self.hdc:
            w.gdi32.SelectObject(self.hdc, self._alt)
            w.gdi32.DeleteObject(self.bitmap)
            w.gdi32.DeleteDC(self.hdc)
            for pinsel in self._pinsel.values():
                w.gdi32.DeleteObject(pinsel)
            self._pinsel.clear()
            self.hdc = None


_fenster: dict[int, "Fenster"] = {}
_aus_dem_bild = False  # True: die Fenster der Bridge sind in der Bildschirmaufnahme (und damit im Bild der Agenten) nicht zu sehen


def bild_ausnahme_setzen(ausnehmen: bool) -> int:
    """Alle Fenster der Bridge (auch später entstehende) aus der Bildschirmaufnahme ausnehmen oder wieder aufnehmen lassen. Daniel sieht sie weiter.
    Liefert, bei wie vielen vorhandenen Fenstern Windows es angenommen hat (Windows 10 ab Version 2004)."""
    global _aus_dem_bild
    _aus_dem_bild = ausnehmen
    return sum(1 for fenster in list(_fenster.values()) if fenster.aufnahme_ausnehmen(ausnehmen))
_entstehend: list["Fenster"] = []
_klassen: set[str] = set()
_wndproc_ref: Any = None


def _wndproc(hwnd, msg, wparam, lparam):
    fenster = _fenster.get(hwnd)
    if fenster is None and _entstehend:
        fenster = _entstehend[-1]
        fenster.hwnd = hwnd
        _fenster[hwnd] = fenster
    if fenster is not None:
        try:
            result = fenster.nachricht(msg, wparam, lparam)
        except Exception as fehler:  # ein Handler darf die Nachrichtenschleife nie beenden
            Anwendung.fehler("fenster", fehler)
            result = None
        if result is not None:
            return result
        if msg == w.WM_DESTROY:
            _fenster.pop(hwnd, None)
    return w.user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def _klasse_registrieren(name: str, klassenstil: int) -> None:
    global _wndproc_ref
    if name in _klassen:
        return
    if _wndproc_ref is None:
        _wndproc_ref = w.WNDPROC(_wndproc)
    instance = w.kernel32.GetModuleHandleW(None)
    klasse = w.WNDCLASSEXW()
    klasse.cbSize = ctypes.sizeof(w.WNDCLASSEXW)
    klasse.style = klassenstil
    klasse.lpfnWndProc = _wndproc_ref
    klasse.hInstance = instance
    klasse.hCursor = w.user32.LoadCursorW(None, w.IDC_ARROW)
    klasse.hbrBackground = None
    klasse.lpszClassName = name
    if not w.user32.RegisterClassExW(ctypes.byref(klasse)):
        raise OSError(f"RegisterClassExW fehlgeschlagen: {w.last_error()}")
    _klassen.add(name)


class Fenster:
    """Basis aller Fenster des Körpers. Unterklassen überschreiben `zeichnen` und die `bei_*`-Handler."""

    klasse = "AuHFenster"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW
    klassenstil = w.CS_DBLCLKS

    def __init__(self, x: int, y: int, breite: int, hoehe: int, *, titel: str = "", deckkraft: int | None = None,
                 durchklickbar: bool = False, nicht_aktivieren: bool = False):
        w.require_windows()
        self.hwnd: int | None = None
        self.titel = titel
        self.breite, self.hoehe = breite, hoehe
        self.deckkraft = deckkraft
        self.leinwand: Leinwand | None = None
        self._timer: dict[int, Callable[[], None]] = {}
        exstil = self.exstil | (w.WS_EX_LAYERED if deckkraft is not None else 0)
        if durchklickbar:
            exstil |= w.WS_EX_TRANSPARENT | w.WS_EX_LAYERED
        if nicht_aktivieren:
            exstil |= w.WS_EX_NOACTIVATE
        _klasse_registrieren(self.klasse, self.klassenstil)
        _entstehend.append(self)
        try:
            hwnd = w.user32.CreateWindowExW(exstil, self.klasse, titel, self.fensterstil, x, y, breite, hoehe, None, None,
                                            w.kernel32.GetModuleHandleW(None), None)
        finally:
            _entstehend.pop()
        if not hwnd:
            raise OSError(f"CreateWindowExW fehlgeschlagen: {w.last_error()}")
        self.hwnd = hwnd
        _fenster[hwnd] = self
        if _aus_dem_bild:
            self.aufnahme_ausnehmen(True)
        if deckkraft is not None or durchklickbar:
            self.setze_deckkraft(255 if deckkraft is None else deckkraft)
        self.leinwand_anpassen()

    def aufnahme_ausnehmen(self, ausnehmen: bool) -> bool:
        if w.user32 is None or w.user32.SetWindowDisplayAffinity is None or not self.hwnd:
            return False
        return bool(w.user32.SetWindowDisplayAffinity(self.hwnd, w.WDA_EXCLUDEFROMCAPTURE if ausnehmen else w.WDA_NONE))

    # ---- Zustand -----------------------------------------------------------------------------------------------------
    def rechteck(self) -> tuple[int, int, int, int]:
        rect = RECT()
        w.user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def clientgroesse(self) -> tuple[int, int]:
        rect = RECT()
        w.user32.GetClientRect(self.hwnd, ctypes.byref(rect))
        return rect.right - rect.left, rect.bottom - rect.top

    def leinwand_anpassen(self) -> None:
        breite, hoehe = self.clientgroesse()
        if breite <= 0 or hoehe <= 0:
            return
        if self.leinwand is None or (self.leinwand.breite, self.leinwand.hoehe) != (breite, hoehe):
            if self.leinwand is not None:
                self.leinwand.freigeben()
            self.leinwand = Leinwand(breite, hoehe)

    def setze_deckkraft(self, alpha: int) -> None:
        self.deckkraft = max(0, min(255, int(alpha)))
        w.user32.SetLayeredWindowAttributes(self.hwnd, 0, self.deckkraft, w.LWA_ALPHA)

    def deckkraft_lesen(self) -> int | None:
        farbe, alpha, flags = w.COLORREF(), w.wintypes.BYTE(), w.wintypes.DWORD()
        if not w.user32.GetLayeredWindowAttributes(self.hwnd, ctypes.byref(farbe), ctypes.byref(alpha), ctypes.byref(flags)):
            return None
        return alpha.value

    def setze_form(self, punkte: list[tuple[int, int]] | None) -> None:
        """Fensterform (Region) aus einem Polygon in Fensterkoordinaten; None entfernt die Form."""
        if punkte is None:
            w.user32.SetWindowRgn(self.hwnd, None, True)
            return
        array = (POINT * len(punkte))(*[POINT(x, y) for x, y in punkte])
        region = w.gdi32.CreatePolygonRgn(array, len(punkte), w.WINDING)
        w.user32.SetWindowRgn(self.hwnd, region, True)  # das System besitzt die Region ab jetzt

    def verschiebe(self, x: int, y: int, breite: int | None = None, hoehe: int | None = None) -> None:
        if breite is None or hoehe is None:
            links, oben, rechts, unten = self.rechteck()
            breite = rechts - links if breite is None else breite
            hoehe = unten - oben if hoehe is None else hoehe
        w.user32.SetWindowPos(self.hwnd, None, x, y, breite, hoehe, w.SWP_NOZORDER | w.SWP_NOACTIVATE)

    fokus_weg = ""  # welcher Weg den Fokus zuletzt geholt hat (für Fehlersuche), "" = keiner

    def fokus_erzwingen(self) -> bool:
        """Dieses Fenster nach vorn und mit der Tastatur, auch wenn ein anderes Programm sie gerade hat.

        Windows verweigert SetForegroundWindow oft (Vordergrundsperre). Darum eine Kette, jeweils mit Prüfung, ob es geklappt hat:
        1. direkt; 2. an den Eingabefaden des Vordergrundfensters anhängen; 3. ein Alt-Tastendruck (entsperrt den Wechsel), danach noch einmal;
        4. SwitchToThisWindow. Liefert, ob das Fenster danach wirklich vorn steht; `fokus_weg` nennt den Weg."""
        self.fokus_weg = ""
        if w.user32.GetForegroundWindow() == self.hwnd:
            self.fokus_weg = "schon vorn"
            return True

        def vorn() -> bool:
            return w.user32.GetForegroundWindow() == self.hwnd

        def setzen() -> None:
            w.user32.BringWindowToTop(self.hwnd)
            w.user32.SetForegroundWindow(self.hwnd)
            w.user32.SetFocus(self.hwnd)

        w.user32.AllowSetForegroundWindow(0xFFFFFFFF)
        setzen()
        if vorn():
            self.fokus_weg = "direkt"
            return True
        fremder_fenster = w.user32.GetForegroundWindow()
        eigener = w.kernel32.GetCurrentThreadId()
        fremder = w.user32.GetWindowThreadProcessId(fremder_fenster, None) if fremder_fenster else 0
        if fremder and fremder != eigener and w.user32.AttachThreadInput(eigener, fremder, True):
            try:
                setzen()
            finally:
                w.user32.AttachThreadInput(eigener, fremder, False)
            if vorn():
                self.fokus_weg = "Eingabefaden angehängt"
                return True
        w.user32.keybd_event(0x12, 0, 0, 0)  # Alt drücken und loslassen: danach darf das Programm den Vordergrund wechseln
        w.user32.keybd_event(0x12, 0, 2, 0)
        setzen()
        if vorn():
            self.fokus_weg = "Alt-Tastendruck"
            return True
        w.user32.SwitchToThisWindow(self.hwnd, True)
        if vorn():
            self.fokus_weg = "SwitchToThisWindow"
            return True
        return False

    def durchklick_setzen(self, an: bool) -> None:
        """Klicks fallen durch das Fenster (an) oder werden von ihm angenommen (aus); braucht ein Layered Window."""
        alt = w.user32.GetWindowLongPtrW(self.hwnd, w.GWL_EXSTYLE)
        neu = (alt | w.WS_EX_TRANSPARENT) if an else (alt & ~w.WS_EX_TRANSPARENT)
        if neu != alt:
            w.user32.SetWindowLongPtrW(self.hwnd, w.GWL_EXSTYLE, neu)

    def oben(self) -> None:
        w.user32.SetWindowPos(self.hwnd, w.HWND_TOPMOST, 0, 0, 0, 0, w.SWP_NOMOVE | w.SWP_NOSIZE | w.SWP_NOACTIVATE)

    def zeige(self, aktivieren: bool = True) -> None:
        w.user32.ShowWindow(self.hwnd, w.SW_SHOW if aktivieren else w.SW_SHOWNOACTIVATE)
        self.neu_zeichnen()

    def verberge(self) -> None:
        w.user32.ShowWindow(self.hwnd, w.SW_HIDE)

    def sichtbar(self) -> bool:
        return bool(w.user32.IsWindowVisible(self.hwnd))

    def neu_zeichnen(self) -> None:
        w.user32.InvalidateRect(self.hwnd, None, False)

    def mauszeiger(self, art: int) -> None:
        w.user32.SetCursor(w.user32.LoadCursorW(None, art))

    def erfasse_maus(self) -> None:
        w.user32.SetCapture(self.hwnd)

    def gib_maus_frei(self) -> None:
        w.user32.ReleaseCapture()

    def starte_timer(self, ident: int, ms: int, aufruf: Callable[[], None] | None = None) -> None:
        if aufruf is not None:
            self._timer[ident] = aufruf
        w.user32.SetTimer(self.hwnd, ident, ms, None)

    def stoppe_timer(self, ident: int) -> None:
        w.user32.KillTimer(self.hwnd, ident)
        self._timer.pop(ident, None)

    def schliessen(self) -> None:
        if self.hwnd:
            w.user32.DestroyWindow(self.hwnd)

    def maus_position(self) -> tuple[int, int]:
        punkt = POINT()
        w.user32.GetCursorPos(ctypes.byref(punkt))
        return punkt.x, punkt.y

    # ---- Nachrichtenverteilung ---------------------------------------------------------------------------------------
    def nachricht(self, msg: int, wparam: int, lparam: int) -> int | None:
        if msg == w.WM_PAINT:
            self._paint()
            return 0
        if msg == w.WM_ERASEBKGND:
            return 1
        if msg == w.WM_SIZE:
            self.leinwand_anpassen()
            self.bei_groesse(*self.clientgroesse())
            return None
        if msg == w.WM_TIMER:
            aufruf = self._timer.get(wparam)
            if aufruf is not None:
                aufruf()
            else:
                self.bei_timer(wparam)
            return 0
        if msg == w.WM_DESTROY:
            self.bei_zerstoert()
            if self.leinwand is not None:
                self.leinwand.freigeben()
                self.leinwand = None
            return None
        if msg == w.WM_LBUTTONDOWN:
            return self.bei_maus_runter(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_LBUTTONUP:
            return self.bei_maus_hoch(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_LBUTTONDBLCLK:
            return self.bei_doppelklick(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_RBUTTONUP:
            return self.bei_rechtsklick(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_MOUSEMOVE:
            return self.bei_maus_bewegt(w.signed_loword(lparam), w.signed_hiword(lparam), wparam)
        if msg == w.WM_MOUSEWHEEL:
            delta = w.signed_hiword(wparam)
            return self.bei_rad(delta, w.signed_loword(lparam), w.signed_hiword(lparam), w.loword(wparam))
        if msg in (w.WM_KEYDOWN, w.WM_SYSKEYDOWN):
            return self.bei_taste(wparam, lparam, msg == w.WM_SYSKEYDOWN)
        if msg in (w.WM_CHAR, w.WM_SYSCHAR):
            return self.bei_zeichen(wparam, msg == w.WM_SYSCHAR)
        if msg == w.WM_HOTKEY:
            return self.bei_hotkey(wparam)
        if msg == w.WM_KILLFOCUS:
            self.bei_fokus(False)
            return None
        if msg == w.WM_SETFOCUS:
            self.bei_fokus(True)
            return None
        if msg == w.WM_NCHITTEST:
            treffer = self.treffer(w.signed_loword(lparam), w.signed_hiword(lparam))
            return treffer
        if msg == w.WM_CAPTURECHANGED:
            self.bei_maus_verloren()
            return None
        if msg == w.WM_DPICHANGED:
            self.bei_dpi(w.hiword(wparam))
            return None
        return self.bei_nachricht(msg, wparam, lparam)

    def _paint(self) -> None:
        paint = w.PAINTSTRUCT()
        hdc = w.user32.BeginPaint(self.hwnd, ctypes.byref(paint))
        try:
            if self.leinwand is not None:
                self.zeichnen(self.leinwand)
                self.leinwand.auf(hdc)
        finally:
            w.user32.EndPaint(self.hwnd, ctypes.byref(paint))

    # ---- Überschreibbare Handler -------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        leinwand.fuellen(0)

    def treffer(self, x: int, y: int) -> int | None:
        return None

    def bei_groesse(self, breite: int, hoehe: int) -> None: ...
    def bei_zerstoert(self) -> None: ...
    def bei_timer(self, ident: int) -> None: ...
    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_doppelklick(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None: return None
    def bei_rad(self, delta: int, x: int, y: int, flags: int) -> int | None: return None
    def bei_taste(self, vk: int, lparam: int, syskey: bool) -> int | None: return None
    def bei_zeichen(self, code: int, syskey: bool) -> int | None: return None
    def bei_hotkey(self, ident: int) -> int | None: return None
    def bei_fokus(self, hat_fokus: bool) -> None: ...
    def bei_maus_verloren(self) -> None: ...
    def bei_dpi(self, dpi: int) -> None: ...
    def bei_nachricht(self, msg: int, wparam: int, lparam: int) -> int | None: return None


class Zentrale(Fenster):
    """Unsichtbares Fenster: nimmt Hotkeys, Timer und Aufträge aus anderen Threads entgegen."""

    klasse = "AuHZentrale"
    exstil = w.WS_EX_TOOLWINDOW

    def __init__(self, anwendung: "Anwendung"):
        super().__init__(0, 0, 1, 1, titel="Augen und Hände (Zentrale)")
        self.anwendung = anwendung
        self.hotkeys: dict[int, Callable[[], None]] = {}

    def nachricht(self, msg: int, wparam: int, lparam: int) -> int | None:
        if msg == WM_AUH_POST:
            self.anwendung.abarbeiten()
            return 0
        if msg == w.WM_HOTKEY:
            aufruf = self.hotkeys.get(wparam)
            if aufruf is not None:
                aufruf()
            return 0
        return super().nachricht(msg, wparam, lparam)


class Anwendung:
    """Die Nachrichtenschleife des GUI-Threads und die Brücke für Aufträge aus anderen Threads."""

    _aktuell: "Anwendung | None" = None
    fehler_aufruf: Callable[[str, BaseException], None] | None = None

    def __init__(self):
        w.require_windows()
        Anwendung._aktuell = self
        self._aufgaben: queue.SimpleQueue[Callable[[], None]] = queue.SimpleQueue()
        self.zentrale: Zentrale | None = None
        self._hotkey_zaehler = 0
        self._hotkey_namen: dict[str, tuple[int, int, int]] = {}
        self.beendet = False

    @classmethod
    def fehler(cls, wo: str, fehler: BaseException) -> None:
        if cls.fehler_aufruf is not None:
            cls.fehler_aufruf(wo, fehler)

    def dpi_bewusst(self) -> bool:
        if w.user32.SetProcessDpiAwarenessContext is None:
            return False
        return bool(w.user32.SetProcessDpiAwarenessContext(w.DPI_AWARENESS_PER_MONITOR_V2))

    def starten(self) -> None:
        self.zentrale = Zentrale(self)

    def post(self, aufgabe: Callable[[], None]) -> None:
        """Aus jedem Thread erlaubt: führt `aufgabe` im GUI-Thread aus."""
        self._aufgaben.put(aufgabe)
        if self.zentrale is not None and self.zentrale.hwnd:
            w.user32.PostMessageW(self.zentrale.hwnd, WM_AUH_POST, 0, 0)

    def abarbeiten(self) -> None:
        while True:
            try:
                aufgabe = self._aufgaben.get_nowait()
            except queue.Empty:
                return
            try:
                aufgabe()
            except Exception as fehler:
                Anwendung.fehler("post", fehler)

    def hotkey(self, modifikatoren: int, vk: int, aufruf: Callable[[], None]) -> bool:
        assert self.zentrale is not None
        self._hotkey_zaehler += 1
        ident = self._hotkey_zaehler
        if not w.user32.RegisterHotKey(self.zentrale.hwnd, ident, modifikatoren | w.MOD_NOREPEAT, vk):
            return False
        self.zentrale.hotkeys[ident] = aufruf
        return True

    def hotkey_setzen(self, name: str, modifikatoren: int, vk: int, aufruf: Callable[[], None]) -> bool:
        """Hotkey unter einem Namen (neu oder ersetzend). Schlägt die neue Kombination fehl (belegt), bleibt die alte."""
        assert self.zentrale is not None
        alt = self._hotkey_namen.get(name)
        if alt is not None and alt[1:] == (modifikatoren, vk):
            self.zentrale.hotkeys[alt[0]] = aufruf
            return True
        self._hotkey_zaehler += 1
        ident = self._hotkey_zaehler
        if not w.user32.RegisterHotKey(self.zentrale.hwnd, ident, modifikatoren | w.MOD_NOREPEAT, vk):
            return False
        self.zentrale.hotkeys[ident] = aufruf
        if alt is not None:
            w.user32.UnregisterHotKey(self.zentrale.hwnd, alt[0])
            self.zentrale.hotkeys.pop(alt[0], None)
        self._hotkey_namen[name] = (ident, modifikatoren, vk)
        return True

    def hotkey_loeschen(self, name: str) -> None:
        alt = self._hotkey_namen.pop(name, None)
        if alt is not None and self.zentrale is not None:
            w.user32.UnregisterHotKey(self.zentrale.hwnd, alt[0])
            self.zentrale.hotkeys.pop(alt[0], None)

    def schleife(self) -> int:
        nachricht = w.MSG()
        while w.user32.GetMessageW(ctypes.byref(nachricht), None, 0, 0) > 0:
            w.user32.TranslateMessage(ctypes.byref(nachricht))
            w.user32.DispatchMessageW(ctypes.byref(nachricht))
        self.beendet = True
        return int(nachricht.wParam)

    def pumpen(self, maximal_ms: int = 0) -> None:
        """Für Tests: verarbeitet die anstehenden Nachrichten, ohne zu blockieren."""
        import time as _time

        ende = _time.monotonic() + maximal_ms / 1000
        nachricht = w.MSG()
        while True:
            while w.user32.PeekMessageW(ctypes.byref(nachricht), None, 0, 0, w.PM_REMOVE):
                if nachricht.message == w.WM_QUIT:
                    self.beendet = True
                    return
                w.user32.TranslateMessage(ctypes.byref(nachricht))
                w.user32.DispatchMessageW(ctypes.byref(nachricht))
            if _time.monotonic() >= ende:
                return
            _time.sleep(0.005)

    def beenden(self, code: int = 0) -> None:
        w.user32.PostQuitMessage(code)


def _linux_einhaengen() -> None:
    """Mit BRIDGE_BACKEND=linux gelten für alle, die `fenster` importieren, die GTK-Fassungen derselben Namen."""
    from .plattform import ist_linux

    if ist_linux():
        from . import fenster_linux as fl

        g = globals()
        for name in ("Schrift", "Leinwand", "Fenster", "Zentrale", "Anwendung", "bild_ausnahme_setzen"):
            g[name] = getattr(fl, name)


_linux_einhaengen()
