"""Das Register der Agenten (G09): wer läuft, in welcher Gruppe, als Kind von wem, mit welchen Aufträgen und was die jeweilige Runtime wirklich kann.

Reine Logik ohne Prozesse und Netz: der Starter (`client_vps/terminal_launcher.py`) füllt es und handelt danach. Vier Dinge sind getrennt:
* **Sitzung** (Terminal-ID): die laufende PTY-Sitzung, vom Starter gestartet. Mehrere Sitzungen desselben Stroms (zweimal Codex) sind verschiedene Agenten.
* **Beziehung**: Gruppen (beliebig viele je Agent) und Eltern/Kind. Ein Kind ist entweder **steuerbar** (der Starter hat dafür eine eigene Sitzung gestartet) oder nur **gemeldet**
  (ein Unteragent, der im Prozess des Eltern-Agenten läuft; die Bridge kann ihn weder ansprechen noch anhalten und kennzeichnet ihn so).
* **Auftrag**: etwas, das ein Agent einem anderen aufgibt, mit Status, Ergebnis und Unsicherheit. Der Status steigt nur, wenn der Empfänger ihn meldet; nichts wird erfunden.
* **Fähigkeiten** je Strom (Ansprechen, Beobachten, Pausieren, Beenden): aus dem, was die echte Runtime (PTY und Prozessgruppe) hergibt; „nicht unterstützt“ heißt nicht „ausgeführt“.

Bestehende fremde Sitzungen werden nicht angebunden (BE01): jeder Agent hier ist eine Sitzung, die die Bridge selbst gestartet hat.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

NAME = re.compile(r"[^\x00-\x1f]{1,40}\Z")
GRUPPE = re.compile(r"[A-Za-z0-9_.-]{1,32}\Z")
ZUSTAENDE = ("starting", "running", "paused", "exited", "failed")
AUFTRAG_STATUS = ("gesendet", "angenommen", "laeuft", "fertig", "fehler", "abgebrochen")
AUFTRAG_REIHENFOLGE = {"gesendet": 0, "angenommen": 1, "laeuft": 2, "fertig": 3, "fehler": 3, "abgebrochen": 3}
MAX_AGENTEN, MAX_AUFTRAEGE, MAX_TEXT, MAX_GRUPPEN_JE_AGENT = 64, 500, 4000, 16
RATE_FENSTER_S, RATE_MAX = 10.0, 10  # höchstens 10 Nachrichten je Absender in 10 Sekunden
DUBLETTEN_S = 5.0

# Welcher Strom hinter einem Programmnamen steckt (für die Anzeige und die Fähigkeiten); alles Unbekannte ist `shell`.
STROEME = {"claude": "claude", "codex": "codex", "gemini": "gemini", "agy": "gemini", "kimi": "kimi", "glm": "glm", "opencode": "opencode", "gpt": "gpt", "haiku": "claude"}

# Was die Runtime bei einer von der Bridge gehaltenen PTY-Sitzung hergibt (für alle Ströme gleich, weil es die PTY ist, nicht das Modell):
PTY_FAEHIGKEITEN = {"ansprechen": "Text in die Sitzung tippen (PTY)", "beobachten": "Ausgabe mitlesen (PTY), Bilder je Ziel", "pausieren": "Prozessgruppe anhalten (SIGSTOP/SIGCONT)",
                    "beenden": "Sitzung schließen (SIGHUP, dann SIGKILL)", "delegieren": "Auftrag in die Sitzung tippen; Ergebnis meldet der Empfänger"}
FAEHIGKEITEN = {strom: dict(PTY_FAEHIGKEITEN) for strom in set(STROEME.values()) | {"shell"}}
FAEHIGKEITEN["shell"].pop("delegieren")  # eine bloße Shell nimmt keine Aufträge an und meldet nichts zurück
KEINE = {"ansprechen": None, "beobachten": None, "pausieren": None, "beenden": None, "delegieren": None}  # ein nur gemeldetes Kind


def strom_von(programm: str) -> str:
    erstes = programm.strip().split()[0].rsplit("/", 1)[-1].lower() if programm.strip() else ""
    return STROEME.get(erstes, "shell")


class RegisterFehler(ValueError):
    pass


@dataclass
class Agent:
    terminal_id: str
    name: str
    strom: str = "shell"
    start_id: str = ""
    laufort: str = ""
    zustand: str = "starting"
    gruppen: set[str] = field(default_factory=set)
    eltern_id: str | None = None
    kinder: list[str] = field(default_factory=list)
    steuerbar: bool = True
    seit: float = field(default_factory=time.time)

    def faehigkeiten(self) -> dict:
        return dict(FAEHIGKEITEN.get(self.strom, FAEHIGKEITEN["shell"])) if self.steuerbar else dict(KEINE)

    def zu_dict(self) -> dict:
        return {"terminal_id": self.terminal_id, "name": self.name, "strom": self.strom, "start_id": self.start_id, "laufort": self.laufort, "zustand": self.zustand,
                "gruppen": sorted(self.gruppen), "eltern_id": self.eltern_id, "kinder": list(self.kinder), "steuerbar": self.steuerbar, "seit": self.seit}


@dataclass
class Auftrag:
    id: str
    von: str
    an: str
    text: str
    status: str = "gesendet"
    ergebnis: str = ""
    unsicherheit: str = ""
    verlauf: list[tuple[float, str, str]] = field(default_factory=list)  # (Zeit, Status, Bemerkung)
    erzeugt: float = field(default_factory=time.time)

    def zu_dict(self) -> dict:
        return {"id": self.id, "von": self.von, "an": self.an, "text": self.text, "status": self.status, "ergebnis": self.ergebnis, "unsicherheit": self.unsicherheit,
                "verlauf": [list(v) for v in self.verlauf], "erzeugt": self.erzeugt}


@dataclass
class Zustellung:
    an: str  # terminal_id
    name: str
    text: str


class Register:
    def __init__(self, uhr=time.monotonic):
        self.agenten: dict[str, Agent] = {}
        self.auftraege: dict[str, Auftrag] = {}
        self._uhr = uhr
        self._gesendet: dict[str, list[float]] = {}  # Absender -> Zeiten
        self._zuletzt: dict[tuple, float] = {}

    # ---- Agenten ----------------------------------------------------------------------------------------------------
    def anlegen(self, terminal_id: str, name: str, *, strom: str = "shell", start_id: str = "", laufort: str = "", eltern_id: str | None = None,
                zustand: str = "starting") -> Agent:
        if terminal_id in self.agenten:
            return self.agenten[terminal_id]
        if len(self.agenten) >= MAX_AGENTEN:
            raise RegisterFehler("zu_viele_agenten")
        if eltern_id is not None and eltern_id not in self.agenten:
            raise RegisterFehler("eltern_unbekannt")
        agent = Agent(terminal_id, self._eindeutiger_name(name), strom, start_id, laufort, zustand, eltern_id=eltern_id)
        self.agenten[terminal_id] = agent
        if eltern_id is not None:
            self.agenten[eltern_id].kinder.append(terminal_id)
        return agent

    def _eindeutiger_name(self, name: str) -> str:
        """Zwei Sitzungen desselben Stroms bleiben unterscheidbar: „Codex“, „Codex 2“, … (wie in der Oberfläche)."""
        if not NAME.fullmatch(name or ""):
            raise RegisterFehler("name_ungueltig")
        benutzt = {a.name for a in self.agenten.values()}
        if name not in benutzt:
            return name
        n = 2
        while f"{name} {n}" in benutzt:
            n += 1
        return f"{name} {n}"

    def zustand_setzen(self, terminal_id: str, zustand: str) -> None:
        if zustand not in ZUSTAENDE:
            raise RegisterFehler("zustand_ungueltig")
        if terminal_id in self.agenten:
            self.agenten[terminal_id].zustand = zustand

    def finde(self, wer: str) -> Agent | None:
        """Per Terminal-ID oder Anzeigename (ohne Beachtung der Groß-/Kleinschreibung)."""
        if wer in self.agenten:
            return self.agenten[wer]
        return next((a for a in self.agenten.values() if a.name.lower() == wer.lower()), None)

    def kind_melden(self, eltern_id: str, name: str, strom: str = "shell") -> Agent:
        """Ein Unteragent, der im Prozess des Eltern-Agenten läuft: bekannt, aber nicht steuerbar (kein Ansprechen, Anhalten oder Beenden)."""
        if eltern_id not in self.agenten:
            raise RegisterFehler("eltern_unbekannt")
        kennung = f"k-{uuid.uuid4().hex[:8]}"
        agent = self.anlegen(kennung, name, strom=strom, eltern_id=eltern_id, zustand="running")
        agent.steuerbar = False
        return agent

    def entfernen_wenn_beendet(self, terminal_id: str) -> None:
        a = self.agenten.get(terminal_id)
        if a is not None and a.zustand in ("exited", "failed"):
            a.zustand = a.zustand  # beendete Agenten bleiben im Register (Verlauf, Aufträge), bis sie ausdrücklich entfernt werden

    # ---- Gruppen ----------------------------------------------------------------------------------------------------
    def gruppe_beitreten(self, terminal_id: str, gruppe: str) -> None:
        if not GRUPPE.fullmatch(gruppe or ""):
            raise RegisterFehler("gruppe_ungueltig")
        agent = self.agenten.get(terminal_id)
        if agent is None:
            raise RegisterFehler("agent_unbekannt")
        if len(agent.gruppen) >= MAX_GRUPPEN_JE_AGENT and gruppe not in agent.gruppen:
            raise RegisterFehler("zu_viele_gruppen")
        agent.gruppen.add(gruppe)

    def gruppe_verlassen(self, terminal_id: str, gruppe: str) -> None:
        if terminal_id in self.agenten:
            self.agenten[terminal_id].gruppen.discard(gruppe)

    def mitglieder(self, gruppe: str, nur_steuerbare: bool = False) -> list[Agent]:
        return [a for a in self.agenten.values() if gruppe in a.gruppen and a.zustand in ("starting", "running", "paused") and (a.steuerbar or not nur_steuerbare)]

    def gruppen(self) -> dict[str, list[str]]:
        ergebnis: dict[str, list[str]] = {}
        for a in self.agenten.values():
            for g in a.gruppen:
                ergebnis.setdefault(g, []).append(a.name)
        return {g: sorted(n) for g, n in sorted(ergebnis.items())}

    # ---- Nachrichten ------------------------------------------------------------------------------------------------
    def nachricht(self, von: str, an: str | None, gruppe: str | None, text: str, jetzt: float | None = None) -> tuple[list[Zustellung], list[dict]]:
        """Wer bekommt diese Nachricht? Liefert (Zustellungen, abgelehnt mit Grund). Schutz vor Endlosschleifen: nie an sich selbst, nie an nur gemeldete Kinder, Dubletten und
        eine Rate je Absender werden abgewiesen; eine Zustellung löst von selbst nichts aus (Antworten sind neue, ausdrückliche Nachrichten)."""
        jetzt = self._uhr() if jetzt is None else jetzt
        absender = self.agenten.get(von)
        if absender is None:
            raise RegisterFehler("absender_unbekannt")
        if not isinstance(text, str) or not 1 <= len(text) <= MAX_TEXT:
            raise RegisterFehler("text_ungueltig")
        if (an is None) == (gruppe is None):
            raise RegisterFehler("entweder_an_oder_gruppe")
        zeiten = [t for t in self._gesendet.get(von, []) if jetzt - t < RATE_FENSTER_S]
        if len(zeiten) >= RATE_MAX:
            raise RegisterFehler("zu_schnell")
        schluessel = (von, an or "", gruppe or "", text)
        if jetzt - self._zuletzt.get(schluessel, -1e9) < DUBLETTEN_S:
            raise RegisterFehler("dublette")
        if an is not None:
            ziel = self.finde(an)
            if ziel is None:
                raise RegisterFehler("empfaenger_unbekannt")
            empfaenger = [ziel]
        else:
            empfaenger = self.mitglieder(gruppe)
            if not empfaenger:
                raise RegisterFehler("gruppe_leer")
        zustellungen, abgelehnt = [], []
        for e in empfaenger:
            if e.terminal_id == von:
                abgelehnt.append({"an": e.name, "grund": "selbst"})  # kein Selbst-Echo
            elif not e.steuerbar:
                abgelehnt.append({"an": e.name, "grund": "nicht_steuerbar"})
            elif e.zustand not in ("running", "paused"):
                abgelehnt.append({"an": e.name, "grund": f"zustand_{e.zustand}"})
            else:
                zustellungen.append(Zustellung(e.terminal_id, e.name, f"[Bridge · von {absender.name}] {text}"))
        self._gesendet[von] = zeiten + [jetzt]
        self._zuletzt[schluessel] = jetzt
        return zustellungen, abgelehnt

    # ---- Aufträge ---------------------------------------------------------------------------------------------------
    def auftrag_neu(self, von: str, an: str, text: str) -> Auftrag:
        absender, ziel = self.agenten.get(von), self.finde(an)
        if absender is None:
            raise RegisterFehler("absender_unbekannt")
        if ziel is None:
            raise RegisterFehler("empfaenger_unbekannt")
        if ziel.terminal_id == von:
            raise RegisterFehler("an_sich_selbst")
        if not ziel.steuerbar:
            raise RegisterFehler("nicht_steuerbar")
        if "delegieren" not in ziel.faehigkeiten():
            raise RegisterFehler("nimmt_keine_auftraege")
        if not isinstance(text, str) or not 1 <= len(text) <= MAX_TEXT:
            raise RegisterFehler("text_ungueltig")
        if len(self.auftraege) >= MAX_AUFTRAEGE:
            raise RegisterFehler("zu_viele_auftraege")
        a = Auftrag(f"a-{uuid.uuid4().hex[:8]}", von, ziel.terminal_id, text)
        a.verlauf.append((time.time(), "gesendet", ""))
        self.auftraege[a.id] = a
        return a

    def auftrag_status(self, auftrag_id: str, wer: str, status: str, ergebnis: str = "", unsicherheit: str = "") -> Auftrag:
        """Nur der Empfänger (oder der Auftraggeber zum Abbrechen) darf den Status ändern; er steigt nur, geht nie zurück."""
        a = self.auftraege.get(auftrag_id)
        if a is None:
            raise RegisterFehler("auftrag_unbekannt")
        if status not in AUFTRAG_STATUS or status == "gesendet":
            raise RegisterFehler("status_ungueltig")
        wer_id = (self.finde(wer).terminal_id if self.finde(wer) else wer)
        if status == "abgebrochen":
            if wer_id not in (a.von, a.an):
                raise RegisterFehler("nicht_beteiligt")
        elif wer_id != a.an:
            raise RegisterFehler("nur_der_empfaenger")
        if AUFTRAG_REIHENFOLGE[a.status] >= 3:
            raise RegisterFehler("schon_abgeschlossen")
        if AUFTRAG_REIHENFOLGE[status] < AUFTRAG_REIHENFOLGE[a.status]:
            raise RegisterFehler("status_geht_nicht_zurueck")
        a.status = status
        if status in ("fertig", "fehler"):
            a.ergebnis = (ergebnis or "")[:MAX_TEXT]
        a.unsicherheit = (unsicherheit or a.unsicherheit)[:500]
        a.verlauf.append((time.time(), status, (ergebnis or "")[:120]))
        return a

    def auftraege_von(self, terminal_id: str) -> list[Auftrag]:
        return [a for a in self.auftraege.values() if a.von == terminal_id]

    def auftraege_an(self, terminal_id: str) -> list[Auftrag]:
        return [a for a in self.auftraege.values() if a.an == terminal_id]

    # ---- Speichern --------------------------------------------------------------------------------------------------
    def zu_dict(self) -> dict:
        return {"version": 1, "agenten": [a.zu_dict() for a in self.agenten.values()], "auftraege": [a.zu_dict() for a in self.auftraege.values()]}

    def speichern(self, pfad: Path) -> bool:
        try:
            pfad.parent.mkdir(parents=True, exist_ok=True)
            temp = pfad.with_suffix(".tmp")
            temp.write_text(json.dumps(self.zu_dict(), ensure_ascii=False), encoding="utf-8")
            temp.replace(pfad)
            return True
        except OSError:
            return False

    @staticmethod
    def laden(pfad: Path) -> "Register":
        """Tolerant: eine fehlende oder kaputte Datei ergibt ein leeres Register. Geladene Agenten gelten als beendet (die Sitzungen leben im Starter, nicht in der Datei)."""
        r = Register()
        try:
            roh = json.loads(pfad.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return r
        for d in roh.get("agenten", []) if isinstance(roh, dict) else []:
            try:
                a = Agent(str(d["terminal_id"]), str(d["name"])[:40], str(d.get("strom", "shell")), str(d.get("start_id", "")), str(d.get("laufort", "")), "exited",
                          set(d.get("gruppen", [])), d.get("eltern_id"), list(d.get("kinder", [])), bool(d.get("steuerbar", True)), float(d.get("seit", 0)))
                r.agenten[a.terminal_id] = a
            except (KeyError, TypeError, ValueError):
                continue
        for d in roh.get("auftraege", []) if isinstance(roh, dict) else []:
            try:
                a = Auftrag(str(d["id"]), str(d["von"]), str(d["an"]), str(d["text"])[:MAX_TEXT], str(d.get("status", "gesendet")), str(d.get("ergebnis", "")),
                            str(d.get("unsicherheit", "")), [tuple(v) for v in d.get("verlauf", [])], float(d.get("erzeugt", 0)))
                if a.status in AUFTRAG_STATUS:
                    r.auftraege[a.id] = a
            except (KeyError, TypeError, ValueError):
                continue
        return r
