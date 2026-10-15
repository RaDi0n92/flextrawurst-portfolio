"""Der Körper und die Anzeigeorte (G06): welche Desktops es gibt, wo ein Agent gezeigt wird und wie er von einem zum anderen wandert.

Vier Dinge sind getrennt und werden getrennt gemeldet (R011, R012, R115):
* **Laufort** (Host, vd1, vd2): wo das Programm des Agenten läuft;
* **Anzeigeort** (Windows, KDE 1, KDE 2): auf welchem Desktop Raute, Terminal, Chat und Banner stehen;
* **Sitzung**: das konkrete Terminal mit Prozess und Startzeit (eine neue Shell unter demselben Namen ist eine andere Sitzung);
* **Ziel**: das Fenster oder der Desktop, den der Agent sieht und bedient, auf einem beliebigen Desktop, unabhängig vom Anzeigeort.

Dieses Modul hält nur den Stand und baut Menüs und Beschreibungstexte; das Senden und Anwenden steht in `anwendung.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import menue

GRUND_TEXT = {"terminal_unbekannt": "dieses Terminal gibt es nicht (mehr)", "nicht_beteiligt": "dieser Desktop darf es nicht verschieben",
              "ort_unbekannt": "diesen Desktop kennt der Relay nicht", "schon_dort": "dort wird es schon gezeigt", "ort_offline": "dieser Desktop ist nicht verbunden",
              "nicht_unterstuetzt": "dieser Körper kennt Anzeigeorte noch nicht", "ziel_abgelehnt": "das Ziel wurde abgelehnt"}
ZIEL_ZUSTAENDE = ("ok", "verdeckt", "minimiert", "inaktiv", "weg", "unbekannt")
ZIEL_FAEHIGKEITEN = ("frisch", "fremde_pixel", "letztes_bild", "keine_aufnahme", "unbekannt")
ZUSTAND_TEXT = {"ok": "sichtbar", "verdeckt": "verdeckt", "minimiert": "minimiert", "inaktiv": "inaktiv", "weg": "geschlossen", "unbekannt": "unbekannt"}
FAEHIGKEIT_TEXT = {"frisch": "Bild frisch", "fremde_pixel": "Bild mit fremden Fenstern davor", "letztes_bild": "nur das letzte Bild", "keine_aufnahme": "keine Aufnahme", "unbekannt": "Aufnahme unbekannt"}


def faehigkeit_standard(zustand: str) -> str:
    """Was die Aufnahme bei diesem Zustand leistet, wenn sie den Bildschirm ausschneidet (Windows heute): verdeckt zeigt fremde Fenster, minimiert und geschlossen nichts."""
    return {"ok": "frisch", "verdeckt": "fremde_pixel", "minimiert": "keine_aufnahme", "inaktiv": "frisch", "weg": "keine_aufnahme"}.get(zustand, "unbekannt")


def faehigkeit_fensteraufnahme(zustand: str) -> str:
    """Mit Fensteraufnahme (XComposite unter Linux): auch ein verdecktes Fenster kommt vollständig; minimierte und geschlossene nicht."""
    return {"ok": "frisch", "verdeckt": "frisch", "minimiert": "keine_aufnahme", "inaktiv": "frisch", "weg": "keine_aufnahme"}.get(zustand, "unbekannt")


@dataclass
class TerminalOrt:
    """Was der Starter über ein Terminal meldet: `terminal_ort`."""

    terminal_id: str
    laufort: str = ""
    anzeigeort: str = ""
    zielort: str = ""
    aktiv: bool = False
    pid: int = 0
    gestartet: int = 0
    ziel_id: str | None = None
    ziel_zustand: str = "unbekannt"
    ziel_faehigkeit: str = "unbekannt"
    grund: str = ""

    @staticmethod
    def aus_payload(payload: dict) -> "TerminalOrt":
        ziel = payload.get("ziel") or {}
        return TerminalOrt(payload["terminal_id"], str(payload.get("laufort", "")), str(payload.get("anzeigeort", "")), str(payload.get("zielort", "")),
                           bool(payload.get("aktiv")), int(payload.get("pid") or 0), int(payload.get("gestartet") or 0),
                           ziel.get("target_id"), str(ziel.get("zustand", "unbekannt")), str(ziel.get("faehigkeit", "unbekannt")), str(payload.get("grund", "")))


@dataclass
class AnzeigeOrteStand:
    eigener_ort: str = "windows"
    orte: list[dict] = field(default_factory=list)  # [{"ort", "name", "online"}]
    unterstuetzt: bool = False  # hat der Relay (und der Starter) Anzeigeorte gemeldet
    terminals: dict[str, TerminalOrt] = field(default_factory=dict)

    def setze_orte(self, orte: list[dict]) -> None:
        self.orte = [o for o in orte if isinstance(o, dict) and isinstance(o.get("ort"), str)]
        self.unterstuetzt = True

    def name(self, ort: str) -> str:
        return next((o.get("name") or ort for o in self.orte if o["ort"] == ort), ort or "?")

    def merke(self, info: TerminalOrt) -> None:
        self.terminals[info.terminal_id] = info

    def vergessen(self, terminal_id: str) -> None:
        self.terminals.pop(terminal_id, None)

    def ziele_fuer_wechsel(self, terminal_id: str) -> list[dict]:
        """Desktops, auf die der Körper dieses Agenten wandern kann: online, nicht der aktuelle."""
        info = self.terminals.get(terminal_id)
        aktuell = info.anzeigeort if info and info.anzeigeort else self.eigener_ort
        return [o for o in self.orte if o.get("online") and o["ort"] != aktuell]

    # ---- Beschreibung: vier getrennte Angaben -----------------------------------------------------------------------
    def beschreibung(self, terminal_id: str) -> list[str]:
        info = self.terminals.get(terminal_id)
        if info is None:
            return [f"Anzeigeort: {self.name(self.eigener_ort)}"]
        zeilen = [f"Läuft auf: {info.laufort or '?'}", f"Angezeigt auf: {self.name(info.anzeigeort or self.eigener_ort)}"]
        zeilen.append(f"Sitzung: PID {info.pid}" if info.pid else "Sitzung: unbekannt")
        if info.ziel_id:
            zeilen.append(f"Ziel: {self.name(info.zielort or info.anzeigeort)} · {info.ziel_id.rsplit(':', 1)[-1] if ':window:' in info.ziel_id else 'Desktop'} · "
                          f"{ZUSTAND_TEXT.get(info.ziel_zustand, info.ziel_zustand)} · {FAEHIGKEIT_TEXT.get(info.ziel_faehigkeit, info.ziel_faehigkeit)}")
        else:
            zeilen.append(f"Ziel: {self.name(info.zielort or info.anzeigeort or self.eigener_ort)} · Desktop (ungebunden)")
        return zeilen

    # ---- Menü ------------------------------------------------------------------------------------------------------
    def menue_eintraege(self, terminal_id: str, basis_id: int) -> list:
        """Einträge fürs Raute-Menü: die vier Angaben (abgeblendet) und die Desktops, auf die man den Körper schicken kann."""
        eintraege: list = [(0, zeile, menue.ABGEBLENDET) for zeile in self.beschreibung(terminal_id)]
        if not self.unterstuetzt:
            eintraege.append((0, "Anzeigeorte: der Relay meldet keine (noch nicht neu gestartet?)", menue.ABGEBLENDET))
            return eintraege
        eintraege.append(None)
        andere = self.ziele_fuer_wechsel(terminal_id)
        if not andere:
            eintraege.append((0, "Kein anderer Desktop ist verbunden", menue.ABGEBLENDET))
        for i, o in enumerate(andere):
            eintraege.append((basis_id + i, f"Anzeigeort wechseln zu {o.get('name') or o['ort']} …", 0))
        return eintraege

    def wahl_zu_ort(self, terminal_id: str, basis_id: int, gewaehlt: int) -> str | None:
        andere = self.ziele_fuer_wechsel(terminal_id)
        i = gewaehlt - basis_id
        return andere[i]["ort"] if 0 <= i < len(andere) else None
