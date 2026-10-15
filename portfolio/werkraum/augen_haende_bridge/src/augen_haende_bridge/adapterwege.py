"""Welche Wege es zu welchem Agentenstrom gibt und was davon wirklich geprüft ist (G09, C9).

Die Bridge erreicht jeden Strom über dieselbe PTY-Sitzung: sie startet das Programm der Startliste in einer Pseudoterminal-Sitzung und tippt Text hinein (Zustellung, Aufträge, Startnachricht).
Dass das *für den jeweiligen echten Agenten* klappt, hängt von seiner Oberfläche ab (Vertrauensdialog, Neuzeichnen, Eingabefeld). Darum steht hier je Strom, was am echten Programm gemessen wurde —
mit Datum und Messweise — und was offen ist. „offen“ heißt nicht „geht nicht“, sondern „nicht gemessen“.

Gemessen wird mit `probes/adapterweg_tui.py`: das echte Programm startet über den echten Starter in einer PTY, die Probe wartet auf Ruhe, tippt eine Marke OHNE Enter (es entsteht keine Anfrage an ein
Modell) und sucht sie in der Ausgabe. Kopfloser Weg (kein Terminal, ein Aufruf mit Eingabetext) steht nur, wenn die Hilfe des Programms ihn nennt; er wurde nicht ausgeführt, weil jeder Lauf eine echte
Modell-Anfrage auf Daniels Konto wäre.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field

BELEGT, ZERSTUECKELT, DIALOG, OFFEN, FEHLT = "belegt", "ankommt_zerstueckelt", "vertrauensdialog_im_weg", "offen", "nicht_installiert"
STAND = "2026-10-02"


@dataclass(frozen=True)
class Weg:
    strom: str
    programm: str  # Name auf dem PATH
    version_argumente: tuple[str, ...] = ("--version",)
    version_muster: str = r"\d+(?:\.\d+)+"
    pty_tippen: str = OFFEN  # Ergebnis der TUI-Probe
    pty_bemerkung: str = ""
    kopflos: str = ""  # der Aufruf, den die Hilfe nennt (nicht ausgeführt)
    kopflos_ausgefuehrt: bool = False
    orte: tuple[str, ...] = ()  # wo er in der Startliste vorkommt
    messung: dict = field(default_factory=dict)


WEGE: dict[str, Weg] = {
    "claude": Weg("claude", "claude", pty_tippen=DIALOG,
                  pty_bemerkung="Im Probelauf (Ordner /tmp und /config, Umgebung des Starters) stand der Ordner-Vertrauensdialog; Tippen kam dort nicht an. Nach dem Bestätigen des Dialogs nicht gemessen.",
                  kopflos="claude -p \"Text\"", orte=("claude-vd1", "anthropic-claude-vd2", "haiku-host", "claude-host")),
    "codex": Weg("codex", "codex", pty_tippen=BELEGT, pty_bemerkung="Marke erscheint im Eingabefeld (Ordner /config).", kopflos="codex exec \"Text\"", orte=("codex-vd1", "codex-host")),
    "gemini": Weg("gemini", "agy", pty_tippen=ZERSTUECKELT,
                  pty_bemerkung="Marke erreicht die Eingabe, die Anzeige mischt die Statuszeile hinein (ZQXmar…Gke7391); als Text im Ausgabestrom nicht zusammenhängend zu finden.",
                  kopflos="agy -p \"Text\" (Hilfe nennt Druckmodus mit stream-json)", orte=("gemgem-vd1", "gravity-vd2", "gemgem-host")),
    "opencode": Weg("opencode", "opencode", pty_tippen=BELEGT, pty_bemerkung="Marke erscheint im Eingabefeld (Ordner /config).", kopflos="opencode run \"Text\"", orte=("opencode-vd1",)),
    "kimi": Weg("kimi", "kimi", pty_tippen=OFFEN, pty_bemerkung="Auf diesem Rechner nicht installiert (steht nur auf dem Host, Eintrag nicht von Daniel bestätigt).", orte=("kimi-host",)),
    "glm": Weg("glm", "glm", pty_tippen=OFFEN, pty_bemerkung="Auf diesem Rechner nicht installiert (nur Host, Eintrag nicht bestätigt).", orte=("glm-host",)),
}


def pruefe(strom: str, ausfuehren=subprocess.run, suchen=shutil.which) -> dict:
    """Prüft jetzt: ist das Programm da, und nennt es eine Version? Der Rest (PTY-Tippen) ist die gemessene Spalte der Tabelle."""
    weg = WEGE[strom]
    pfad = suchen(weg.programm)
    ergebnis = {"strom": strom, "programm": weg.programm, "pfad": pfad, "installiert": pfad is not None, "version": None, "pty_tippen": weg.pty_tippen, "pty_bemerkung": weg.pty_bemerkung,
                "kopflos": weg.kopflos or None, "kopflos_ausgefuehrt": weg.kopflos_ausgefuehrt, "gemessen_am": STAND}
    if pfad is None:
        ergebnis["status"] = FEHLT
        return ergebnis
    try:
        lauf = ausfuehren([pfad, *weg.version_argumente], capture_output=True, text=True, timeout=25)
        treffer = re.search(weg.version_muster, (lauf.stdout or "") + (lauf.stderr or ""))
        ergebnis["version"] = treffer.group(0) if treffer else None
    except (subprocess.SubprocessError, OSError):
        pass
    ergebnis["status"] = weg.pty_tippen
    return ergebnis


def uebersicht(**kw) -> list[dict]:
    return [pruefe(strom, **kw) for strom in WEGE]
