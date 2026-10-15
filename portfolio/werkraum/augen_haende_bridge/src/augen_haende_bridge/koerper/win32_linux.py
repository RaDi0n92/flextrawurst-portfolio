"""Windows-Funktionen, die die Fenster des Körpers direkt aufrufen, in der Linux-Fassung (X11, GTK).

Der Körper ruft an wenigen Stellen `w.user32.…`, `w.gdi32.…` auf (Schrift messen, Tastenzustand, Fenstertitel, Fokus, Arbeitsbereich, Zustand fremder
Fenster, Stil eines Fensters). Unter Linux stehen hier dieselben Namen mit derselben Wirkung. Namen, die es nicht gibt, ergeben wie bei älteren Windows
`None` — der Körper prüft dort ohnehin auf `None`. Fremde Fenster werden über ihre X-Kennung angesprochen.
"""

from __future__ import annotations

from . import win32 as w


class _Tabelle:
    """Namensraum wie `win32._Table`: fehlende Funktionen ergeben None."""

    def __getattr__(self, name: str):
        return None


def _fenster(hwnd):
    from . import fenster_linux as fl

    return fl._fenster.get(int(hwnd or 0))


class _User32(_Tabelle):
    # Gerätekontexte gibt es nicht; die Linux-Schrift und -Leinwand nehmen sie nur der Form halber an.
    def GetDC(self, hwnd):
        return 1

    def ReleaseDC(self, hwnd, hdc):
        return 1

    # Tastenzustand
    def GetKeyState(self, vk):
        from . import tasten_x11

        return 0x8000 if tasten_x11.taste_unten(int(vk)) else 0

    GetAsyncKeyState = GetKeyState

    # eigene Fenster
    def SetWindowTextW(self, hwnd, text):
        f = _fenster(hwnd)
        if f is not None:
            f._win.set_title(str(text))
        return 1

    def SetFocus(self, hwnd):
        f = _fenster(hwnd)
        if f is not None:
            f._win.present_with_time(0)
        return hwnd

    def GetWindowLongPtrW(self, hwnd, index):
        f = _fenster(hwnd)
        return f._exstil if f is not None and index == w.GWL_EXSTYLE else 0

    def SetWindowLongPtrW(self, hwnd, index, wert):
        f = _fenster(hwnd)
        if f is None or index != w.GWL_EXSTYLE:
            return 0
        alt = f._exstil
        f._exstil = int(wert)
        if bool(alt & w.WS_EX_TRANSPARENT) != bool(wert & w.WS_EX_TRANSPARENT):
            f.durchklick_setzen(bool(wert & w.WS_EX_TRANSPARENT))
        if bool(alt & w.WS_EX_NOACTIVATE) != bool(wert & w.WS_EX_NOACTIVATE):
            f._win.set_accept_focus(not (wert & w.WS_EX_NOACTIVATE))
        return alt

    def GetDpiForSystem(self):
        from gi.repository import Gdk

        aufloesung = Gdk.Screen.get_default().get_resolution()
        return int(aufloesung) if aufloesung and aufloesung > 0 else 96

    def GetDpiForWindow(self, hwnd):
        return self.GetDpiForSystem()

    def SystemParametersInfoW(self, aktion, uparam, ziel, flags):
        """Nur SPI_GETWORKAREA: der Desktop ohne Leisten."""
        if aktion != w.SPI_GETWORKAREA:
            return 0
        from . import x11_helfer as x

        rect = getattr(ziel, "_obj", ziel)
        rect.left, rect.top, rect.right, rect.bottom = x.arbeitsbereich()
        return 1

    # fremde Fenster (X-Kennung)
    def IsWindow(self, hwnd):
        from . import x11_helfer as x

        return 1 if x.fenster_existiert(int(hwnd)) else 0

    def IsIconic(self, hwnd):
        from . import x11_helfer as x

        return 1 if x.fenster_minimiert(int(hwnd)) else 0

    def IsWindowVisible(self, hwnd):
        from . import x11_helfer as x

        return 1 if x.fenster_sichtbar(int(hwnd)) else 0

    def GetWindowRect(self, hwnd, ziel):
        from . import x11_helfer as x

        rect = getattr(ziel, "_obj", ziel)
        geo = x.fenster_rechteck(int(hwnd))
        if geo is None:
            return 0
        rect.left, rect.top, rect.right, rect.bottom = geo
        return 1

    def GetForegroundWindow(self):
        from . import x11_helfer as x

        return x.vordergrund() or 0


class _Gdi32(_Tabelle):
    def CreateCompatibleDC(self, hdc):
        return 1

    def DeleteDC(self, hdc):
        return 1


user32, gdi32, kernel32 = _User32(), _Gdi32(), _Tabelle()
