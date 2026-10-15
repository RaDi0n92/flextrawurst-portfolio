"""Daniel übernimmt (G10): der physische Override der Hände.

Bedient Daniel selbst Maus oder Tastatur, während ein Agent Eingaben schickt, hören die Hände des Agenten auf (Auftrag abgebrochen, alles losgelassen) und bleiben für `PAUSE_S` Sekunden
gesperrt. Zwei Quellen sagen, was nicht vom Agenten kommt:

* **Windows**: Low-Level-Hooks (`WH_MOUSE_LL`, `WH_KEYBOARD_LL`) tragen ein Merkmal „injiziert“. Eingaben der Hände (SendInput) sind injiziert, Daniels Hardware nicht — das ist eindeutig.
* **X11**: XRecord sieht jede Eingabe, auch die der Hände (XTEST), ohne Merkmal. Darum wird gezählt: Zeigerereignisse, die die Engine selbst gesendet hat, werden abgezogen; ein Überschuss
  (`TOLERANZ`) oder jede Eingabe, während die Hände ruhen, ist Daniel. Das ist eine Näherung und nur mit einer zweiten Eingabequelle (nicht mit echter Hardware) geprüft.

Daniels bewusst gewählte **Ausnahme** (`ausnahme()` liefert True): die Hände des Agenten laufen auch bei Daniels Eingabe weiter. Der Not-Aus (F12) bleibt in beiden Fällen unberührt, er ist ein
eigener Weg (`notaus.py`).
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

PAUSE_S = 3.0
TOLERANZ = 3  # so viele Zeigerereignisse mehr als gesendet gelten noch als Rauschen
RUHE_GNADE_S = 0.12  # nach der letzten Sendung der Engine gelten Ereignisse noch als ihre eigenen (Verzögerung der Aufzeichnung)


class Uebernahme:
    """Entscheidet, ob eine beobachtete Eingabe Daniels ist, und hält die Hände dann an."""

    def __init__(self, engine, *, ausnahme: Callable[[], bool] = lambda: False, uhr: Callable[[], float] = time.monotonic, pause_s: float = PAUSE_S):
        self.engine, self._ausnahme, self._uhr, self.pause_s = engine, ausnahme, uhr, pause_s
        self.bis = 0.0
        self.beobachtet_zeiger = 0
        self._korrektur = 0  # Zeigerereignisse, die die Hände gesendet haben, ohne dass der Server eines meldete (Bewegung an dieselbe Stelle): damit sie spätere fremde nicht verdecken
        self.erkannt = 0
        self.letzte_eingabe: float | None = None  # wann Daniel zuletzt tippte oder klickte (ohne Zeigerrauschen: Selkies sendet den Zeiger alle 0,8 s)
        self.ignoriert = 0  # Daniels Eingabe bei gesetzter Ausnahme
        self._sperre = threading.Lock()
        engine.beobachter = self

    # ---- von der Engine ------------------------------------------------------------------------------------------------------
    def _saldo(self, abgleichen: bool = False) -> int:
        """Beobachtete minus gesendete Zeigerereignisse. Fehlen beobachtete (Bewegung an dieselbe Stelle erzeugt keines), wird das nur in Ruhe ausgeglichen (`abgleichen`): währenddessen sind es
        meist bloß noch nicht eingetroffene Ereignisse der Aufzeichnung, und ein Ausgleich würde sie später als fremd erscheinen lassen."""
        s = self.beobachtet_zeiger - self.engine.zeiger_gesendet + self._korrektur
        if s < 0 and abgleichen:
            self._korrektur -= s
            s = 0
        return max(s, 0)

    def auftrag_beginnt(self) -> None:
        with self._sperre:
            self._saldo(abgleichen=self._uhr() - self.engine.letzte_sendung > RUHE_GNADE_S)
            if self.engine.daniel_uebernimmt and self._uhr() >= self.bis:
                self.engine.daniel_uebernimmt = False  # die Pause ist vorbei

    def tick(self) -> None:
        if self.engine.daniel_uebernimmt and self._uhr() >= self.bis:
            self.engine.daniel_uebernimmt = False

    # ---- Quellen ----------------------------------------------------------------------------------------------------------------
    def physisch(self, art: str = "") -> bool:
        """Eine Eingabe, die sicher nicht von den Händen stammt (Windows: nicht injiziert). True, wenn die Hände angehalten wurden."""
        with self._sperre:
            self._korrektur -= self._saldo()  # was als fremd erkannt (oder wegen der Ausnahme ignoriert) wurde, ist erledigt und zählt nicht noch einmal
        if self._ausnahme():
            self.ignoriert += 1
            return False
        self.erkannt += 1
        self.bis = self._uhr() + self.pause_s
        self.engine.daniel_uebernimmt = True
        self.engine.abbrechen("daniel_uebernimmt")
        return True

    def ruhig_seit(self) -> float:
        """Sekunden seit Daniels letztem Tippen oder Klicken (unendlich, wenn noch keines gesehen wurde)."""
        return float("inf") if self.letzte_eingabe is None else self._uhr() - self.letzte_eingabe

    def _von_daniel(self) -> bool:
        return not self.engine.busy and self._uhr() - self.engine.letzte_sendung > RUHE_GNADE_S

    def ereignis_x11(self, art: str) -> None:
        """Eine von XRecord gesehene Eingabe (`zeiger`, `klick` oder `taste`); ohne Merkmal, darum die Zuordnung über Zählen und Ruhe."""
        if art == "klick":  # eine gedrückte Maustaste (zusätzlich zum `zeiger`-Ereignis): wer klickt, hat das Feld gewählt, in das er gleich tippt
            if self._von_daniel():
                self.letzte_eingabe = self._uhr()
            return
        if art == "taste" and self._von_daniel():
            self.letzte_eingabe = self._uhr()
        if art == "zeiger":
            with self._sperre:
                self.beobachtet_zeiger += 1
                ueberschuss = self._saldo()
            if self.engine.busy and ueberschuss > TOLERANZ:
                self.physisch(art)
            elif not self.engine.busy and self._uhr() - self.engine.letzte_sendung > RUHE_GNADE_S:
                self.physisch(art)
        elif art == "taste":
            if not self.engine.busy and self._uhr() - self.engine.letzte_sendung > RUHE_GNADE_S:
                self.physisch(art)


class X11Aufzeichnung:
    """XRecord für Zeiger und Tasten (eigener Faden, eigene Verbindung)."""

    def __init__(self, bei_ereignis: Callable[[str], None]):
        self.bei_ereignis = bei_ereignis
        self.installiert = False
        self.fehler: str | None = None
        self._faden: threading.Thread | None = None
        self._bereit = threading.Event()
        self._kontext = None
        self._steuer = None

    def start(self, timeout: float = 5.0) -> bool:
        self._faden = threading.Thread(target=self._lauf, name="uebernahme-xrecord", daemon=True)
        self._faden.start()
        self._bereit.wait(timeout)
        return self.installiert

    def _lauf(self) -> None:
        from Xlib import X, display
        from Xlib.ext import record
        from Xlib.protocol import rq

        try:
            daten, steuer = display.Display(), display.Display()
            if not daten.has_extension("RECORD"):
                self.fehler = "XRecord fehlt"
                self._bereit.set()
                return
            kontext = daten.record_create_context(0, [record.AllClients], [{
                "core_requests": (0, 0), "core_replies": (0, 0), "ext_requests": (0, 0, 0, 0), "ext_replies": (0, 0, 0, 0),
                "delivered_events": (0, 0), "device_events": (X.KeyPress, X.MotionNotify), "errors": (0, 0), "client_started": False, "client_died": False}])
        except Exception as fehler:
            self.fehler = f"XRecord nicht verfügbar: {fehler!r}"
            self._bereit.set()
            return
        self._kontext, self._steuer = kontext, steuer

        def rueckruf(antwort) -> None:
            if antwort.category != record.FromServer or antwort.client_swapped or not antwort.data:
                return
            rest = antwort.data
            while len(rest):
                ereignis, rest = rq.EventField(None).parse_binary_value(rest, daten.display, None, None)
                if ereignis.type in (X.ButtonPress, X.ButtonRelease, X.MotionNotify):
                    self.bei_ereignis("zeiger")
                    if ereignis.type == X.ButtonPress:
                        self.bei_ereignis("klick")
                elif ereignis.type in (X.KeyPress, X.KeyRelease):
                    self.bei_ereignis("taste")

        self.installiert = True
        self._bereit.set()
        try:
            daten.record_enable_context(kontext, rueckruf)
        except Exception as fehler:
            self.fehler = f"XRecord beendet: {fehler!r}"
        finally:
            self.installiert = False
            try:
                daten.record_free_context(kontext)
            except Exception:
                pass

    def stop(self) -> None:
        if self._kontext is not None and self._steuer is not None:
            try:
                self._steuer.record_disable_context(self._kontext)
                self._steuer.flush()
            except Exception:
                pass
        if self._faden is not None:
            self._faden.join(timeout=3.0)


class WindowsHooks:
    """WH_MOUSE_LL und WH_KEYBOARD_LL in einem eigenen Faden: nicht injizierte Eingabe ist Daniels (LLMHF_INJECTED / LLKHF_INJECTED)."""

    def __init__(self, uebernahme: Uebernahme):
        self.uebernahme = uebernahme
        self.installiert = False
        self.fehler: str | None = None
        self.gesehen = {"injiziert": 0, "physisch": 0}
        self._faden: threading.Thread | None = None
        self._faden_id = 0
        self._bereit = threading.Event()
        self._refs: list = []

    def start(self, timeout: float = 5.0) -> bool:
        self._faden = threading.Thread(target=self._lauf, name="uebernahme-hooks", daemon=True)
        self._faden.start()
        self._bereit.wait(timeout)
        return self.installiert

    def _lauf(self) -> None:
        import ctypes
        from ctypes import wintypes

        u = ctypes.WinDLL("user32", use_last_error=True)
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        self._faden_id = int(k.GetCurrentThreadId())
        LRESULT = ctypes.c_ssize_t
        HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

        class MSLL(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long), ("mouseData", wintypes.DWORD), ("flags", wintypes.DWORD), ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]

        class KBLL(ctypes.Structure):
            _fields_ = [("vk", wintypes.DWORD), ("scan", wintypes.DWORD), ("flags", wintypes.DWORD), ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]

        u.CallNextHookEx.argtypes, u.CallNextHookEx.restype = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM], LRESULT
        u.SetWindowsHookExW.argtypes, u.SetWindowsHookExW.restype = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD], ctypes.c_void_p
        k.GetModuleHandleW.argtypes, k.GetModuleHandleW.restype = [wintypes.LPCWSTR], wintypes.HMODULE

        def maus(n, wp, lp):
            if n == 0:
                info = ctypes.cast(lp, ctypes.POINTER(MSLL)).contents
                if wp != 0x0200 or True:
                    self._gesehen(bool(info.flags & 0x1), "zeiger")
            return u.CallNextHookEx(None, n, wp, lp)

        def tastatur(n, wp, lp):
            if n == 0:
                info = ctypes.cast(lp, ctypes.POINTER(KBLL)).contents
                self._gesehen(bool(info.flags & 0x10), "taste")
            return u.CallNextHookEx(None, n, wp, lp)

        proc_m, proc_k = HOOKPROC(maus), HOOKPROC(tastatur)
        self._refs += [proc_m, proc_k]
        modul = k.GetModuleHandleW(None)
        hm = u.SetWindowsHookExW(14, proc_m, modul, 0)
        hk = u.SetWindowsHookExW(13, proc_k, modul, 0)
        if not hm or not hk:
            self.fehler = f"Hook nicht installiert (Fehler {ctypes.get_last_error()})"
            self._bereit.set()
            return
        self.installiert = True
        self._bereit.set()
        msg = wintypes.MSG()
        u.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        while u.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            u.TranslateMessage(ctypes.byref(msg))
            u.DispatchMessageW(ctypes.byref(msg))
        u.UnhookWindowsHookEx(ctypes.c_void_p(hm))
        u.UnhookWindowsHookEx(ctypes.c_void_p(hk))
        self.installiert = False

    def _gesehen(self, injiziert: bool, art: str) -> None:
        if injiziert:
            self.gesehen["injiziert"] += 1
        else:
            self.gesehen["physisch"] += 1
            self.uebernahme.physisch(art)

    def stop(self) -> None:
        if self._faden is not None and self._faden.is_alive() and self._faden_id:
            import ctypes

            ctypes.WinDLL("user32").PostThreadMessageW(self._faden_id, 0x0012, 0, 0)
            self._faden.join(timeout=3.0)
