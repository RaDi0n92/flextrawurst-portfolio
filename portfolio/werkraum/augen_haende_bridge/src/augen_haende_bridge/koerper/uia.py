"""Normale Programme über die Bedienungshilfen ihres Systems lesen und bedienen (G06.7, R123): UI Automation unter Windows, AT-SPI unter Linux.

Ein gemeinsamer Baum aus `UiKnoten` (Rolle, Name, Wert, Zustände, Lage, Herkunft, Fähigkeiten) und Aktionen mit Rücklese. Ein Programm, das keine Bedienungshilfen anbietet
(eine rein gezeichnete Fläche), ergibt **keinen Baum** (`kein_baum`), nie einen leeren erfolgreichen. Eine Aktion, die der Knoten nicht kann, löst nichts aus.

Die Windows-Fassung benutzt `comtypes` (UI Automation über COM); fehlt die Bibliothek, meldet sie „nicht verfügbar“. Sie ist nur gegen ein nachgebautes Objektmodell und nicht
nativ geprüft. Die Linux-Fassung läuft gegen echte GTK-Programme mit AT-SPI.
"""

from __future__ import annotations

from dataclasses import dataclass, field

QUELLE_UIA, QUELLE_ATSPI = "uia", "atspi"
MAX_KNOTEN = 2000
MAX_TIEFE = 24


@dataclass
class UiKnoten:
    quelle: str
    rolle: str
    name: str = ""
    wert: str = ""
    rect: tuple[int, int, int, int] | None = None  # Bildschirmkoordinaten (links, oben, rechts, unten)
    zustaende: tuple[str, ...] = ()
    faehigkeiten: tuple[str, ...] = ()  # z. B. klick, text_setzen, auswaehlen
    pfad: tuple[int, ...] = ()  # Stelle im Baum; mit der Anwendung zusammen die Anschrift des Knotens
    kinder: list["UiKnoten"] = field(default_factory=list)
    _griff: object = None  # der plattformeigene Knoten (nicht Teil der Daten)

    def finde(self, rolle: str | None = None, name: str | None = None) -> "UiKnoten | None":
        if (rolle is None or self.rolle == rolle) and (name is None or self.name == name):
            return self
        for k in self.kinder:
            treffer = k.finde(rolle, name)
            if treffer is not None:
                return treffer
        return None

    def alle(self) -> list["UiKnoten"]:
        liste = [self]
        for k in self.kinder:
            liste.extend(k.alle())
        return liste

    def mitte(self) -> tuple[int, int] | None:
        return None if self.rect is None else ((self.rect[0] + self.rect[2]) // 2, (self.rect[1] + self.rect[3]) // 2)


@dataclass
class BaumErgebnis:
    status: str  # ok | kein_baum | nicht_verfuegbar | fehler
    wurzel: UiKnoten | None = None
    grund: str = ""
    anzahl: int = 0


class UiQuelle:
    """Schnittstelle der Plattformen."""

    name = ""

    def verfuegbar(self) -> bool:
        return False

    def anwendungen(self) -> list[tuple[str, int | None]]:
        """(Name, Prozess) der Programme, die Bedienungshilfen anbieten."""
        raise NotImplementedError

    def baum(self, anwendung: str | int) -> BaumErgebnis:
        raise NotImplementedError

    def klick(self, knoten: UiKnoten) -> bool:
        raise NotImplementedError

    def text_setzen(self, knoten: UiKnoten, text: str) -> bool:
        raise NotImplementedError


# ---- Linux: AT-SPI ----------------------------------------------------------------------------------------------------------
class AtspiQuelle(UiQuelle):
    name = QUELLE_ATSPI

    def __init__(self):
        self._atspi = None
        try:
            import gi

            gi.require_version("Atspi", "2.0")
            from gi.repository import Atspi

            Atspi.init()
            self._atspi = Atspi
        except Exception:
            self._atspi = None

    def verfuegbar(self) -> bool:
        if self._atspi is None:
            return False
        try:
            return self._atspi.get_desktop(0) is not None
        except Exception:
            return False

    def anwendungen(self) -> list[tuple[str, int | None]]:
        desktop = self._atspi.get_desktop(0)
        liste = []
        for i in range(desktop.get_child_count()):
            app = desktop.get_child_at_index(i)
            if app is not None:
                try:
                    liste.append((app.get_name() or "", app.get_process_id()))
                except Exception:
                    liste.append((app.get_name() or "", None))
        return liste

    def _anwendung(self, wer: str | int):
        desktop = self._atspi.get_desktop(0)
        for i in range(desktop.get_child_count()):
            app = desktop.get_child_at_index(i)
            if app is None:
                continue
            try:
                if (isinstance(wer, int) and app.get_process_id() == wer) or (isinstance(wer, str) and app.get_name() == wer):
                    return app
            except Exception:
                continue
        return None

    def baum(self, anwendung: str | int) -> BaumErgebnis:
        if not self.verfuegbar():
            return BaumErgebnis("nicht_verfuegbar", grund="kein AT-SPI-Bus")
        app = self._anwendung(anwendung)
        if app is None:
            return BaumErgebnis("kein_baum", grund="das Programm meldet sich nicht bei den Bedienungshilfen")
        zaehler = [0]
        wurzel = self._knoten(app, (), 0, zaehler)
        if zaehler[0] <= 1:
            return BaumErgebnis("kein_baum", wurzel, "das Programm bietet keine Elemente an (nur gezeichnete Fläche)", zaehler[0])
        return BaumErgebnis("ok", wurzel, "", zaehler[0])

    def _knoten(self, a, pfad: tuple[int, ...], tiefe: int, zaehler: list[int]) -> UiKnoten:
        zaehler[0] += 1
        Atspi = self._atspi
        rolle = (a.get_role_name() or "").replace(" ", "_")
        wert = ""
        faehig = []
        try:
            if a.get_text_iface() is not None:  # PyGObject: die Schnittstellen sind statische Funktionen von Atspi.Text usw., nicht Methoden des Knotens
                wert = Atspi.Text.get_text(a, 0, min(Atspi.Text.get_character_count(a), 500))
                if a.get_editable_text_iface() is not None:
                    faehig.append("text_setzen")
        except Exception:
            pass
        try:
            if a.get_action_iface() is not None and Atspi.Action.get_n_actions(a) > 0:
                faehig.append("klick")
        except Exception:
            pass
        rect = None
        try:
            if a.get_component_iface() is not None:
                e = a.get_extents(Atspi.CoordType.SCREEN)
                rect = (e.x, e.y, e.x + e.width, e.y + e.height)
        except Exception:
            pass
        zustaende = []
        try:
            for z in a.get_state_set().get_states():
                zustaende.append(z.value_nick)
        except Exception:
            pass
        knoten = UiKnoten(QUELLE_ATSPI, rolle, a.get_name() or "", wert, rect, tuple(zustaende), tuple(faehig), pfad, [], a)
        if tiefe < MAX_TIEFE and zaehler[0] < MAX_KNOTEN:
            for i in range(a.get_child_count()):
                kind = a.get_child_at_index(i)
                if kind is not None and zaehler[0] < MAX_KNOTEN:
                    knoten.kinder.append(self._knoten(kind, pfad + (i,), tiefe + 1, zaehler))
        return knoten

    def klick(self, knoten: UiKnoten) -> bool:
        if "klick" not in knoten.faehigkeiten or knoten._griff is None:
            return False
        try:
            return bool(self._atspi.Action.do_action(knoten._griff, 0))
        except Exception:
            return False

    def text_setzen(self, knoten: UiKnoten, text: str) -> bool:
        if "text_setzen" not in knoten.faehigkeiten or knoten._griff is None:
            return False
        try:
            return bool(self._atspi.EditableText.set_text_contents(knoten._griff, text))
        except Exception:
            return False


# ---- Windows: UI Automation über comtypes -----------------------------------------------------------------------------------
_STEUERELEMENTE = {50000: "button", 50001: "calendar", 50002: "check_box", 50003: "combo_box", 50004: "edit", 50005: "hyperlink", 50006: "image", 50007: "list_item",
                   50008: "list", 50009: "menu", 50010: "menu_bar", 50011: "menu_item", 50012: "progress_bar", 50013: "radio_button", 50014: "scroll_bar", 50015: "slider",
                   50016: "spinner", 50017: "status_bar", 50018: "tab", 50019: "tab_item", 50020: "text", 50021: "tool_bar", 50022: "tool_tip", 50023: "tree",
                   50024: "tree_item", 50025: "custom", 50026: "group", 50027: "thumb", 50028: "data_grid", 50029: "data_item", 50030: "document", 50031: "split_button",
                   50032: "window", 50033: "pane", 50034: "header", 50035: "header_item", 50036: "table", 50037: "title_bar", 50038: "separator"}


class _ComElement:
    """Ein Element von IUIAutomation mit den Eigenschaften, die der gemeinsame Baum braucht (Muster: Invoke und Value)."""

    UIA_INVOKE, UIA_VALUE = 10000, 10002

    def __init__(self, element, automation, client):
        self.e, self.automation, self.client = element, automation, client

    def _muster(self, kennung, schnittstelle):
        try:
            roh = self.e.GetCurrentPattern(kennung)
            return roh.QueryInterface(getattr(self.client, schnittstelle)) if roh else None
        except Exception:
            return None

    @property
    def name(self) -> str:
        return str(self.e.CurrentName or "")

    @property
    def process_id(self) -> int | None:
        return int(self.e.CurrentProcessId)

    @property
    def rolle(self) -> str:
        return _STEUERELEMENTE.get(int(self.e.CurrentControlType), "unbekannt")

    @property
    def wert(self) -> str:
        muster = self._muster(self.UIA_VALUE, "IUIAutomationValuePattern")
        try:
            return str(muster.CurrentValue) if muster is not None else ""
        except Exception:
            return ""

    @property
    def rect(self):
        r = self.e.CurrentBoundingRectangle
        return (int(r.left), int(r.top), int(r.right), int(r.bottom))

    @property
    def zustaende(self):
        z = []
        if self.e.CurrentIsEnabled:
            z.append("enabled")
        if self.e.CurrentHasKeyboardFocus:
            z.append("focused")
        if self.e.CurrentIsOffscreen:
            z.append("offscreen")
        return tuple(z)

    @property
    def hat_invoke(self) -> bool:
        return self._muster(self.UIA_INVOKE, "IUIAutomationInvokePattern") is not None

    @property
    def hat_value(self) -> bool:
        muster = self._muster(self.UIA_VALUE, "IUIAutomationValuePattern")
        return muster is not None and not muster.CurrentIsReadOnly

    def kinder(self):
        liste = self.e.FindAll(2, self.automation.CreateTrueCondition())  # TreeScope_Children
        return [_ComElement(liste.GetElement(i), self.automation, self.client) for i in range(liste.Length)]

    def invoke(self) -> bool:
        self._muster(self.UIA_INVOKE, "IUIAutomationInvokePattern").Invoke()
        return True

    def wert_setzen(self, text: str) -> bool:
        self._muster(self.UIA_VALUE, "IUIAutomationValuePattern").SetValue(text)
        return True


class _ComModell:
    def __init__(self, automation, client):
        self.automation, self.client = automation, client

    def GetRootElement(self):
        return _ComElement(self.automation.GetRootElement(), self.automation, self.client)


class WindowsUiaQuelle(UiQuelle):
    """UI Automation. `modell` ist für Tests einspeisbar (ein nachgebautes Objektmodell mit denselben Aufrufen wie IUIAutomation)."""

    name = QUELLE_UIA

    def __init__(self, modell=None):
        self._modell = modell
        self._fehler = ""
        if modell is None:
            try:
                import comtypes.client  # noqa: F401

                comtypes.client.GetModule("UIAutomationCore.dll")
                from comtypes.gen import UIAutomationClient as client

                automation = comtypes.client.CreateObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=client.IUIAutomation)
                self._modell = _ComModell(automation, client)
            except Exception as fehler:
                self._fehler = f"{fehler.__class__.__name__}"

    def verfuegbar(self) -> bool:
        return self._modell is not None

    def anwendungen(self) -> list[tuple[str, int | None]]:
        wurzel = self._modell.GetRootElement()
        return [(f.name, f.process_id) for f in wurzel.kinder()]

    def baum(self, anwendung: str | int) -> BaumErgebnis:
        if self._modell is None:
            return BaumErgebnis("nicht_verfuegbar", grund=f"UI Automation nicht verfügbar ({self._fehler or 'comtypes fehlt'})")
        wurzel = self._modell.GetRootElement()
        ziel = next((f for f in wurzel.kinder() if f.name == anwendung or f.process_id == anwendung), None)
        if ziel is None:
            return BaumErgebnis("kein_baum", grund="das Programm bietet keine UI Automation an")
        zaehler = [0]
        knoten = self._knoten(ziel, (), 0, zaehler)
        if zaehler[0] <= 1:
            return BaumErgebnis("kein_baum", knoten, "das Programm bietet keine Elemente an", zaehler[0])
        return BaumErgebnis("ok", knoten, "", zaehler[0])

    def _knoten(self, e, pfad, tiefe, zaehler) -> UiKnoten:
        zaehler[0] += 1
        faehig = tuple(k for k, hat in (("klick", e.hat_invoke), ("text_setzen", e.hat_value)) if hat)
        knoten = UiKnoten(QUELLE_UIA, e.rolle, e.name, e.wert, e.rect, tuple(e.zustaende), faehig, pfad, [], e)
        if tiefe < MAX_TIEFE:
            for i, kind in enumerate(e.kinder()):
                if zaehler[0] < MAX_KNOTEN:
                    knoten.kinder.append(self._knoten(kind, pfad + (i,), tiefe + 1, zaehler))
        return knoten

    def klick(self, knoten: UiKnoten) -> bool:
        return bool("klick" in knoten.faehigkeiten and knoten._griff is not None and knoten._griff.invoke())

    def text_setzen(self, knoten: UiKnoten, text: str) -> bool:
        return bool("text_setzen" in knoten.faehigkeiten and knoten._griff is not None and knoten._griff.wert_setzen(text))
