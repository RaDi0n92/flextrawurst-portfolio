"""VPS-Seite des Terminals: startet Agenten in einer Linux-PTY, die die Bridge hält (BE01), und reicht den rohen Strom über das Relay.

Der Desktop kann nur Einträge der Startliste (BE02) starten und liefert nie einen Befehl. Die Relay-Tokens bleiben im Starter;
ein gestarteter Agent bekommt nur eine eigene Terminal-ID, ein eigenes Token und den Pfad seines lokalen Sprech-Sockets.
Bestehende Terminals werden weder gesucht noch angebunden.
"""

from __future__ import annotations

import base64
import collections
import fcntl
import json
import os
import queue
import re
import secrets
import select
import signal
import socketserver
import struct
import subprocess
import termios
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from augen_haende_bridge.koerper import ziele as ziel_schluessel_modul
from augen_haende_bridge.koerper.controller_adapter import ControllerAktion
from augen_haende_bridge.koerper.eingabe_adapter import Aktion, LeaseTabelle
from augen_haende_bridge.koerper import weltdom_befehle
from client_vps.ablauf_dienst import AblaufDienst
from client_vps.kapsel_dienst import KapselDienst
from client_vps.praxis_dienst import PraxisDienst
from client_vps.seed_dienst import SeedDienst
from augen_haende_bridge.koerper.agentenregister import Register, RegisterFehler, Zustellung, strom_von

MAX_RAUTE_TIPPEN = 500
MAX_AUDIO_WARTESCHLANGE = 4  # mehr unbearbeitete Äußerungen werden verworfen (Live-Strom, kein Nachholen)
MAX_SAETZE = 50
MAX_SPRACHE_TEXT = 4_000
IDENT = re.compile(r"[A-Za-z0-9_.:-]{1,96}\Z")
ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "USER", "SHELL", "DOCKER_HOST", "DOCKER_CONFIG")
READ_CHUNK = 16_384
MAX_TERMINALS = 8
HAENDE_WARTEN_S = 15.0  # so lange wartet der Starter auf das Ergebnis eines Hände-Auftrags (das Ziehen dauert höchstens 5 s)
WELTDOM_WARTEN_S = 40.0  # Messen mit Bilderkennung dauert länger als ein Klick
HAENDE_STOPP_GRUENDE = frozenset({"not_aus", "daniel_uebernimmt", "verbindung_weg"})  # danach ist die Lease weg: keine heimliche Wiederaufnahme
KEEP_FRAMES = 10
REPLAY_MAX = 512 * 1024  # so viel der letzten Ausgabe jeder Sitzung merkt sich der Starter für die Wiederaufnahme
REPLAY_STUECK = 32 * 1024
SOCKET_LINE_LIMIT = 65_536
STARTNACHRICHT_RUHE_S = 2.5  # so lange darf die Ausgabe still sein, bevor die Startnachricht getippt wird (TUI ist dann bereit)
STARTNACHRICHT_MAX_S = 45.0  # wartet die Sitzung länger nicht zur Ruhe, wird nichts getippt
STARTNACHRICHT_MAX_LAENGE = 2000
STARTNACHRICHT_BLOCK_MAX_S = 600.0  # steht ein Bestätigungsdialog im Weg, wartet die Startnachricht so lange auf Daniel (statt in den Dialog zu tippen)
STARTNACHRICHT_ENTER_PAUSE_S = 0.6  # zwischen Text und Enter (siehe _startnachricht_senden)


def standard_startnachricht(cli: str) -> str:
    """Was ein Agent über die Bridge wissen muss, als ein Satz ohne Zeilenumbruch (er wird wie eingetippt übergeben)."""
    return (f"Du läufst in der Augen-und-Hände-Bridge auf Daniels Windows-Desktop. Mit deiner Raute sprichst du: "
            f"python3 {cli} say \"Text\" (Banner, Ticker und Chat). Was Daniel dir ins Mikrofon sagt: python3 {cli} hoere. "
            f"Alle Werkzeuge: python3 {cli} hilfe")


class Runtime(Protocol):
    def publish(self, kind: str, payload: dict, *, message_id: str | None = None) -> str: ...


@dataclass(frozen=True)
class StartEntry:
    start_id: str
    name: str
    ort: str
    ordner: str
    programm: str
    startnachricht: str = ""  # "" = keine; "standard" = Hinweis auf die Werkzeuge der Bridge; sonst ein eigener Text ({cli} = Pfad)

    def wire(self) -> dict[str, str]:
        return {"start_id": self.start_id, "name": self.name, "ort": self.ort,
                "ordner": self.ordner, "programm": self.programm}


@dataclass(frozen=True)
class Ort:
    kind: str  # "host" | "docker"
    container: str | None
    mount_from: str | None = None
    mount_to: str | None = None

    def seen(self, host_path: str) -> str:
        """Der Pfad, unter dem der Agent in diesem Ort einen Hostpfad sieht."""
        if self.mount_from and (host_path == self.mount_from or host_path.startswith(self.mount_from + "/")):
            return self.mount_to + host_path[len(self.mount_from):]
        return host_path


def _text(value, limit: int, what: str) -> str:
    if not isinstance(value, str) or not value or len(value) > limit or "\x00" in value or "\n" in value:
        raise ValueError(f"invalid_{what}")
    return value


def load_orte(path: Path) -> dict[str, Ort]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    result: dict[str, Ort] = {}
    for name, spec in data["orte"].items():
        _text(name, 40, "ort")
        kind = spec.get("kind")
        if kind not in ("host", "docker"):
            raise ValueError("invalid_ort_kind")
        container = spec.get("container")
        if kind == "docker":
            _text(container, 120, "container")
        mount_from, mount_to = spec.get("mount_from"), spec.get("mount_to")
        if (mount_from is None) != (mount_to is None):
            raise ValueError("invalid_mount")
        if mount_from is not None:
            _text(mount_from, 512, "mount")
            _text(mount_to, 512, "mount")
        result[name] = Ort(kind, container, mount_from, mount_to)
    return result


def load_starts(path: Path, orte: dict[str, Ort]) -> dict[str, StartEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    result: dict[str, StartEntry] = {}
    for item in data["starts"]:
        start_id = item["start_id"]
        if not IDENT.fullmatch(start_id) or start_id in result:
            raise ValueError("invalid_start_id")
        ordner = _text(item["ordner"], 512, "ordner")
        if not ordner.startswith("/"):
            raise ValueError("invalid_ordner")
        nachricht = item.get("startnachricht", "")
        if not isinstance(nachricht, str) or len(nachricht) > STARTNACHRICHT_MAX_LAENGE or "\x00" in nachricht \
                or "\n" in nachricht:
            raise ValueError("invalid_startnachricht")
        entry = StartEntry(start_id, _text(item["name"], 120, "name"), _text(item["ort"], 40, "ort"),
                           ordner, _text(item["programm"], 512, "programm"), nachricht)
        if entry.ort not in orte:
            raise ValueError("unknown_ort")
        result[start_id] = entry
    return result


def build_command(start: StartEntry, ort: Ort, terminal_id: str, token: str, runtime_dir: Path):
    """Return argv, cwd and env for one start. The child never sees relay tokens."""
    bridge_env = {
        "TERM": "xterm-256color", "COLORTERM": "truecolor",
        "BRIDGE_TERMINAL_ID": terminal_id, "BRIDGE_TERMINAL_TOKEN": token,
        "BRIDGE_RUNTIME_DIR": ort.seen(str(runtime_dir)),
    }
    base = {key: os.environ[key] for key in ENV_ALLOW if key in os.environ}
    env = {**base, **bridge_env}
    if ort.kind == "host":
        return ["bash", "-ic", start.programm], start.ordner, env
    # -e KEY ohne Wert: docker liest den Wert aus der eigenen Umgebung, das Token steht nie in der Prozessliste.
    argv = ["docker", "exec", "-it", "-w", start.ordner]
    for key in bridge_env:
        argv += ["-e", key]
    argv += [ort.container, "bash", "-ic", start.programm]
    return argv, None, env


# docker exec läuft nach dem Ende des Clients im Container weiter. Alle Prozesse des Terminals tragen BRIDGE_TERMINAL_ID
# in der Umgebung; darüber werden sie im Container gefunden und angesprochen.
REMOTE_KILL_SCRIPT = ('for d in /proc/[0-9]*; do { tr "\\0" "\\n" < "$d/environ"; } 2>/dev/null '
                      '| grep -qxF "BRIDGE_TERMINAL_ID=$1" && kill -"$2" "${d#/proc/}" 2>/dev/null; done; true')


def remote_kill(ort: Ort, terminal_id: str, sig: int) -> None:
    if ort.kind != "docker" or not IDENT.fullmatch(terminal_id):
        return
    env = {key: os.environ[key] for key in ENV_ALLOW if key in os.environ}
    try:
        subprocess.run(["docker", "exec", ort.container, "sh", "-c", REMOTE_KILL_SCRIPT, "sh", terminal_id, str(int(sig))],
                       capture_output=True, timeout=10, env=env, check=False)
    except (subprocess.SubprocessError, OSError):
        pass


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


class TerminalSession:
    """One process on a pty the launcher owns. Output goes to a callback; nothing else reads the master."""

    def __init__(self, terminal_id: str, start: StartEntry, token: str, argv, cwd, env, rows: int, cols: int,
                 on_output: Callable[[bytes], None], on_exit: Callable[[int], None],
                 remote_kill: Callable[[int], None] | None = None):
        self.terminal_id, self.entry, self.token = terminal_id, start, token
        self._remote_kill = remote_kill
        self.rows, self.cols = rows, cols
        self.state = "starting"
        self._argv, self._cwd, self._env = argv, cwd, env
        self._on_output, self._on_exit = on_output, on_exit
        self.pid = 0
        self.fd = -1
        self.letzte_ausgabe = 0.0  # time.monotonic() der letzten Ausgabe; 0 = noch keine
        self.gestartet = 0  # time.time() beim Start des Prozesses (Sekunden): zusammen mit der PID die Identität der Sitzung
        self.replay = bytearray()  # die letzte Ausgabe (höchstens REPLAY_MAX Bytes) für die Wiederaufnahme
        self._closing = False
        self.pausiert = False  # G09: Prozessgruppe angehalten (SIGSTOP); die Sitzung lebt, die PTY puffert Eingaben
        self._proc: subprocess.Popen | None = None

    def start(self) -> None:
        # Kein pty.fork(): Der Starter ist mehrfädig, und Python-Code zwischen fork und exec kann dort hängen.
        # Popen forkt sicher; setsid -c macht den Prozess zum Sitzungsführer mit dieser PTY als Steuerterminal.
        master, slave = os.openpty()
        try:
            _set_winsize(slave, self.rows, self.cols)
            self._proc = subprocess.Popen(["setsid", "-c", *self._argv], stdin=slave, stdout=slave, stderr=slave,
                                          cwd=self._cwd, env=self._env, close_fds=True)
        except BaseException:
            os.close(master)
            raise
        finally:
            os.close(slave)
        self.pid, self.fd = self._proc.pid, master
        self.gestartet = int(time.time())
        self.state = "running"
        threading.Thread(target=self._read_loop, name=f"terminal-{self.terminal_id}", daemon=True).start()

    def _read_loop(self) -> None:
        try:
            while True:
                ready, _, _ = select.select([self.fd], [], [], 0.25)
                if not ready:
                    if self._proc.poll() is not None:  # Prozess weg und nichts mehr zu lesen (auch wenn ein Enkel die PTY hält)
                        break
                    continue
                try:
                    data = os.read(self.fd, READ_CHUNK)
                except OSError:
                    break
                if not data:
                    break
                self._on_output(data)
        finally:
            code = self._proc.wait()
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.state = "exited"
            self._on_exit(code)

    def write(self, data: bytes) -> None:
        # Ein einziges os.write kann bei großen Eingaben (langes Einfügen) nur einen Teil annehmen: bis alles drin ist.
        rest = memoryview(data)
        while self.state == "running" and rest:
            try:
                rest = rest[os.write(self.fd, rest):]
            except (BlockingIOError, InterruptedError):
                time.sleep(0.005)

    def resize(self, rows: int, cols: int) -> None:
        if self.state == "running":
            self.rows, self.cols = rows, cols
            _set_winsize(self.fd, rows, cols)

    def pausieren(self) -> bool:
        """Hält die ganze Prozessgruppe an (SIGSTOP; für Docker-Orte auch die Prozesse im Container). True, wenn der Zustand jetzt „pausiert“ ist."""
        if self.state != "running" or self._closing:
            return False
        if not self.pausiert:
            self._signal(signal.SIGSTOP)
            self.pausiert = True
        return True

    def fortsetzen(self) -> bool:
        if self.state != "running" or self._closing:
            return False
        if self.pausiert:
            self._signal(signal.SIGCONT)
            self.pausiert = False
        return True

    def close(self) -> None:
        if self.state != "running" or self._closing:
            return
        self._closing = True
        self._signal(signal.SIGHUP)
        if self.pausiert:  # ein angehaltener Prozess nähme SIGHUP erst nach SIGCONT an
            self._signal(signal.SIGCONT)
            self.pausiert = False
        for delay, sig in ((1.5, signal.SIGTERM), (4.0, signal.SIGKILL)):
            timer = threading.Timer(delay, self._signal, args=(sig,))
            timer.daemon = True
            timer.start()

    def _signal(self, sig) -> None:
        if self._remote_kill is not None:
            self._remote_kill(int(sig))
        if self.state != "running" or self._proc.poll() is not None:
            return
        try:
            os.killpg(self.pid, sig)
        except ProcessLookupError:  # setsid ist noch nicht gelaufen, die Prozessgruppe existiert erst danach
            try:
                self._proc.send_signal(sig)
            except ProcessLookupError:
                pass
        except PermissionError:
            pass


class Launcher:
    def __init__(self, runtime: Runtime, starts: dict[str, StartEntry], orte: dict[str, Ort], runtime_dir: Path,
                 cli_pfad: Path | None = None, transkriber=None, uhr: Callable[[], float] = time.monotonic,
                 schlafen: Callable[[float], None] = time.sleep, verteiler=None):
        self.cli_pfad = Path(cli_pfad) if cli_pfad is not None else Path(__file__).resolve().with_name("bridge_cli.py")
        self._uhr, self._schlafen = uhr, schlafen
        self.transkriber = transkriber  # hat .transkribiere(wav_bytes) -> str und optional .vorladen()
        self._audio_schlange: queue.Queue = queue.Queue()
        self._audio_worker: threading.Thread | None = None
        self.saetze: dict[str, list[dict]] = {}  # je Terminal: erkannte Sätze (ältester zuerst)
        self._gelesen: dict[str, int] = {}
        self.audio_verworfen = 0
        self.transkription_fehler: str | None = None
        self.runtime, self.starts, self.orte = runtime, starts, orte
        # G06: mit Verteiler spricht der Starter mit mehreren Desktops (Anzeigeorten). Laufort (self.orte: Host, vd1, vd2) und Anzeigeort (windows, kde1, kde2) sind
        # verschiedene Dinge. Ohne Verteiler bleibt alles wie vorher: ein Desktop, keine Prüfungen.
        self.verteiler = verteiler
        self.anzeige: dict[str, str] = {}  # terminal_id -> Desktop, auf dem Raute, Terminal und Chat stehen
        self.ziel: dict[str, str] = {}  # terminal_id -> Desktop, auf dem das Arbeitsziel liegt (folgt dem Anzeigeort, bis es ausdrücklich gesetzt wird)
        self.ziel_explizit: set[str] = set()
        self.lage: dict[str, tuple[float, dict]] = {}  # terminal_id -> (Eingangszeit, Meldung des Körpers): das Lagebild des Agenten (lage.py)
        self.ziel_info: dict[str, dict] = {}  # terminal_id -> {"target_id", "zustand", "faehigkeit", "seit_ms"} (vom Ziel-Desktop gemeldet)
        self.faehig: set[str] = set()  # Desktops, die nach den Anzeigeorten gefragt haben und die neuen Meldungen verstehen
        self.abgewiesen: dict[str, int] = {}  # Grund -> Anzahl abgewiesener Nachrichten (sichtbar in der Fehlersuche)
        self.frames_abgewiesen: dict[str, int] = {}
        self.leases = LeaseTabelle()  # G10: wer darf auf welches Ziel Eingaben schicken
        self._haende_wartend: dict[str, dict] = {}
        self._weltdom_wartend: dict[str, dict] = {}
        self.register = Register()  # G09: Agenten, Gruppen, Eltern/Kinder, Aufträge
        self._tipp_sperren: dict[str, threading.Lock] = {}
        self._zustell_sperre = threading.Lock()
        self._zustell_warteschlangen: dict[str, collections.deque] = {}
        self._zustell_laeuft: set[str] = set()
        self._zustand_sperre = threading.Lock()  # „running“ und „exited“ eines Terminals werden nie in vertauschter Reihenfolge gemeldet
        self.runtime_dir = Path(runtime_dir)
        self.ablauf = AblaufDienst(self, self.runtime_dir / "ablauf")  # G12: Abläufe, Modi, Regiesprüche mit Wirkung
        self.kapseln = KapselDienst(self, self.runtime_dir / "g13")  # G13/G14: Protokoll, Kapseln, Scrubber, Mischpult, Beobachtung
        self.seeds = SeedDienst(self, self.runtime_dir / "g15")  # G15: Seeds, Loops, Goals
        self.praxis = PraxisDienst(self, self.runtime_dir / "praxis")  # Praxistest als Graph: Ansage in der Raute, echte Spuren, Zuschauer
        self.frames_dir = self.runtime_dir / "frames"
        self.sessions: dict[str, TerminalSession] = {}
        self._seq: dict[str, int] = {}
        self._lock = threading.Lock()
        self._ausgabe_sperre = threading.RLock()
        self._events: queue.Queue[dict | None] = queue.Queue()
        self._worker: threading.Thread | None = None
        self._beendet = threading.Event()
        self.dropped = 0

    # ---- Relay-Ereignisse vom Desktop -------------------------------------------------
    def start(self) -> None:
        self._worker = threading.Thread(target=self._work, name="launcher-events", daemon=True)
        self._worker.start()
        if self.transkriber is not None:
            self._audio_worker = threading.Thread(target=self._audio_lauf, name="launcher-sprache", daemon=True)
            self._audio_worker.start()
        if self.verteiler is not None:
            threading.Thread(target=self._orte_beobachten, name="launcher-orte", daemon=True).start()

    def _orte_beobachten(self) -> None:
        """Meldet allen fähigen Desktops, wenn ein Desktop kommt oder geht (Menü „Anzeigeort“ zeigt dann den aktuellen Stand)."""
        while not self._beendet.wait(1.0):
            try:
                if self.verteiler.veraenderungen():
                    self.anzeigeorte_senden_alle()
                    self.leases.entziehen_wenn(lambda z: not self.verteiler.online(ziel_schluessel_modul.ort_von(z) or ""))  # ein Desktop weg: seine Leases auch
            except Exception:
                self.dropped += 1

    def on_event(self, event: dict) -> None:
        """Wird vom Empfangs-Thread der Verbindung gerufen; er darf hier nie selbst senden (publish wartet auf ihn)."""
        self._events.put(event)

    def _work(self) -> None:
        while True:
            event = self._events.get()
            if event is None:
                return
            try:
                self.handle(event)
            except Exception:  # ein kaputtes Ereignis darf die Warteschlange nicht anhalten
                self.dropped += 1

    def handle(self, event: dict) -> None:
        if event.get("kind") != "event":
            return
        kind, payload = event.get("event_kind"), event.get("payload")
        if not isinstance(payload, dict):
            return
        ort = event.get("_ort")  # von welchem Desktop das kam (nur mit Verteiler)
        handler = {
            "terminal_list_request": lambda: self.send_list(event.get("id", "unknown"), ort),
            "terminal_start": lambda: self.start_terminal(payload, ort),
            "terminal_input": lambda: self._vom_anzeigeort(payload, ort, lambda: self._with_session(payload, lambda s: s.write(base64.b64decode(payload["data"])))),
            "terminal_resize": lambda: self._vom_anzeigeort(payload, ort, lambda: self._with_session(payload, lambda s: s.resize(payload["rows"], payload["cols"]))),
            "terminal_close": lambda: self._vom_anzeigeort(payload, ort, lambda: self._with_session(payload, lambda s: s.close())),
            "terminal_attach": lambda: self._vom_anzeigeort(payload, ort, lambda: self.attach(payload["terminal_id"])),
            "frame": lambda: self.store_frame(payload, ort),
            "terminal_audio": lambda: self._vom_anzeigeort(payload, ort, lambda: self._audio_annehmen(payload)),
            "anzeigeorte_request": lambda: self.anzeigeorte_request(ort),
            "terminal_umziehen": lambda: self.umziehen(payload, ort),
            "terminal_ziel": lambda: self.ziel_setzen(payload, ort),
            "ziel_zustand": lambda: self.ziel_zustand(payload, ort),
            "lage": lambda: self.lage_annehmen(payload),
            "haende_ergebnis": lambda: self.haende_ergebnis(payload, ort),
            "weltdom_ergebnis": lambda: self.weltdom_ergebnis(payload, ort),
            "raute_tippen_ergebnis": lambda: self.praxis.raute_ergebnis(payload, ort),
            "ablauf_steuern": lambda: self.ablauf_steuern(payload, ort),
            "regie_spruch": lambda: self._vom_anzeigeort(payload, ort, lambda: self.regie_spruch(payload)),
            "terminal_steuern": lambda: self._vom_anzeigeort(payload, ort, lambda: self.steuern(payload["terminal_id"], payload["aktion"])),
        }.get(kind)
        if handler is not None:
            handler()

    # ---- Anzeigeort und Zielort (G06) ---------------------------------------------------------------------------------
    def _abweisen(self, grund: str) -> None:
        self.abgewiesen[grund] = self.abgewiesen.get(grund, 0) + 1

    def _vom_anzeigeort(self, payload: dict, ort: str | None, aktion: Callable[[], None]) -> None:
        """Eingaben, Größe, Schließen, Wiederaufnahme und Sprache gelten nur von dem Desktop, der das Terminal zeigt."""
        if self.verteiler is not None and self.anzeige.get(payload.get("terminal_id", "")) != ort:
            self._abweisen("falscher_anzeigeort")
            return
        aktion()

    def _ort_wire(self, terminal_id: str, aktiv: bool, grund: str = "") -> dict:
        session = self.sessions.get(terminal_id)
        info = self.ziel_info.get(terminal_id, {})
        anzeige = self.anzeige.get(terminal_id, "")
        return {"terminal_id": terminal_id, "laufort": session.entry.ort if session is not None else "unbekannt", "anzeigeort": anzeige or "unbekannt",
                "zielort": self.ziel.get(terminal_id, anzeige) or "unbekannt", "aktiv": aktiv,
                "pid": getattr(session, "pid", 0) or 0, "gestartet": getattr(session, "gestartet", 0) or 0,
                "ziel": {"target_id": info.get("target_id"), "zustand": info.get("zustand", "unbekannt"), "faehigkeit": info.get("faehigkeit", "unbekannt")},
                "grund": grund[:80]}

    def _faehige(self, *orte: str | None) -> list[str]:
        return list(dict.fromkeys(o for o in orte if o and o in self.faehig))

    def _ort_melden(self, terminal_id: str, orte: list[str | None], aktiv_fuer: str | None, grund: str = "") -> None:
        for ort in self._faehige(*orte):
            self._publish("terminal_ort", self._ort_wire(terminal_id, aktiv=(ort == aktiv_fuer), grund=grund), ort=ort,
                          message_id=f"ort-{terminal_id}-{uuid.uuid4().hex[:8]}")

    def anzeigeorte_request(self, ort: str | None) -> None:
        if self.verteiler is None or ort is None:
            return
        self.faehig.add(ort)
        self._publish("anzeigeorte", {"orte": self.verteiler.orte_wire()}, ort=ort, message_id=f"orte-{uuid.uuid4().hex[:8]}")
        self._publish("ablauf_stand", self.ablauf.stand(), ort=ort, message_id=f"ablaufstand-{uuid.uuid4().hex[:8]}")  # der neue Desktop kennt sofort Läufe und offene Freigaben

    def anzeigeorte_senden_alle(self) -> None:
        if self.verteiler is None:
            return
        for ort in list(self.faehig):
            if self.verteiler.online(ort):
                self._publish("anzeigeorte", {"orte": self.verteiler.orte_wire()}, ort=ort, message_id=f"orte-{uuid.uuid4().hex[:8]}")

    def umziehen(self, payload: dict, von: str | None) -> None:
        """Der Körper (Raute, Terminal, Chat) eines Agenten wandert auf einen anderen Desktop. Die Sitzung bleibt unberührt: gleiche ID, gleicher Prozess."""
        if self.verteiler is None:
            return
        terminal_id, neu = payload["terminal_id"], payload["ort"]
        session = self.sessions.get(terminal_id)
        alt = self.anzeige.get(terminal_id)

        def ablehnen(grund: str) -> None:
            self._abweisen(grund)
            if von in self.faehig:
                self._publish("terminal_ort", self._ort_wire(terminal_id, aktiv=(alt == von), grund=grund), ort=von,
                              message_id=f"ort-{terminal_id}-{uuid.uuid4().hex[:8]}")

        if session is None or session.state not in ("starting", "running") or alt is None:
            return ablehnen("terminal_unbekannt")
        if von not in (alt, neu):
            return ablehnen("nicht_beteiligt")  # ein dritter Desktop darf nichts verschieben
        if neu not in self.verteiler.desktops:
            return ablehnen("ort_unbekannt")
        if neu == alt:
            return ablehnen("schon_dort")
        if not self.verteiler.online(neu):
            return ablehnen("ort_offline")
        if neu not in self.faehig or alt not in self.faehig:
            return ablehnen("nicht_unterstuetzt")
        with self._ausgabe_sperre:  # solange wir umstellen, geht keine Ausgabe an den falschen Desktop
            self.anzeige[terminal_id] = neu
            if terminal_id not in self.ziel_explizit:
                self.ziel[terminal_id] = neu  # das Ziel folgt, solange es nie ausdrücklich gewählt wurde
                self.ziel_info.pop(terminal_id, None)
        self._ort_melden(terminal_id, [alt, neu], aktiv_fuer=neu)
        self.send_list(f"umzug-{terminal_id}-{uuid.uuid4().hex[:6]}", neu)  # der neue Desktop baut den Körper aus der Liste und nimmt die Sitzung wieder auf

    def ziel_setzen(self, payload: dict, von: str | None) -> None:
        """Das Arbeitsziel liegt auf einem anderen Desktop als der Körper. Bilder gelten ab jetzt nur von dort."""
        if self.verteiler is None:
            return
        terminal_id, neu = payload["terminal_id"], payload["ort"]
        alt_ziel, anzeige = self.ziel.get(terminal_id), self.anzeige.get(terminal_id)
        if terminal_id not in self.sessions or anzeige is None or neu not in self.verteiler.desktops or von not in (anzeige, neu, alt_ziel):
            self._abweisen("ziel_abgelehnt")
            return
        self.ziel[terminal_id] = neu
        self.ziel_explizit.add(terminal_id)
        if neu != alt_ziel:
            self.ziel_info.pop(terminal_id, None)  # das alte Ziel gilt nicht mehr; ein neues muss ausdrücklich gebunden werden
        self._ort_melden(terminal_id, [anzeige, neu, alt_ziel], aktiv_fuer=anzeige)

    def ziel_zustand(self, payload: dict, von: str | None) -> None:
        """Der Ziel-Desktop meldet, in welchem Zustand das Ziel ist (sichtbar, verdeckt, minimiert, weg …) und was die Aufnahme dann leistet."""
        if self.verteiler is None:
            return
        terminal_id = payload["terminal_id"]
        if self.ziel.get(terminal_id) != von:
            self._abweisen("ziel_zustand_vom_falschen_ort")
            return
        self.ziel_info[terminal_id] = {"target_id": payload["target_id"], "zustand": payload["zustand"], "faehigkeit": payload["faehigkeit"], "seit_ms": payload["seit_ms"]}
        self._ort_melden(terminal_id, [self.anzeige.get(terminal_id), von], aktiv_fuer=self.anzeige.get(terminal_id))

    def lage_annehmen(self, payload: dict) -> None:
        from augen_haende_bridge import lage as lagebild

        if lagebild.gueltig(payload) and payload["terminal_id"] in self.sessions:
            self.lage[payload["terminal_id"]] = (time.monotonic(), payload)

    def lage_von(self, terminal_id: str) -> dict:
        from augen_haende_bridge import lage as lagebild

        eingang = self.lage.get(terminal_id)
        return lagebild.bewerte(eingang[1] if eingang else None, time.monotonic() - eingang[0] if eingang else None)

    def lage_kurz(self, terminal_id: str) -> str:
        from augen_haende_bridge import lage as lagebild

        return lagebild.kurz(self.lage_von(terminal_id))

    def _with_session(self, payload: dict, action: Callable[[TerminalSession], None]) -> None:
        session = self.sessions.get(payload.get("terminal_id", ""))
        if session is not None:
            try:
                action(session)
            except OSError:
                pass

    # ---- Starten und Melden -----------------------------------------------------------
    def _publish(self, kind: str, payload: dict, message_id: str | None = None, ort: str | None = None) -> None:
        try:
            if self.verteiler is not None:
                ziel = ort or self.anzeige.get(payload.get("terminal_id", ""))  # Körper-Nachrichten gehen an den Anzeigeort des Terminals
                if ziel is None:
                    self.dropped += 1
                    return
                self.verteiler.publish(kind, payload, message_id=message_id, ort=ziel)
            else:
                self.runtime.publish(kind, payload, message_id=message_id)
        except Exception:  # Verbindung weg oder Sendezeit überschritten: der Strom ist live, der Leser darf nicht sterben
            self.dropped += 1

    def _state(self, session_or_id, start_id: str, name: str, state: str, exit_code=None, reason: str = "", ort: str | None = None) -> None:
        terminal_id = session_or_id if isinstance(session_or_id, str) else session_or_id.terminal_id
        self.kapseln.erfassen("state", terminal_id, f"{name}: {state}" + (f" ({reason[:80]})" if reason else ""), {"state": state, "exit_code": exit_code})
        self._publish("terminal_state", {"terminal_id": terminal_id, "start_id": start_id, "name": name,
                                         "state": state, "exit_code": exit_code, "reason": reason[:200]},
                      message_id=f"state-{terminal_id}-{uuid.uuid4().hex[:8]}", **({"ort": ort} if ort is not None else {}))

    def send_list(self, request_id: str, ort: str | None = None) -> None:
        terminals = [{"terminal_id": s.terminal_id, "start_id": s.entry.start_id, "name": s.entry.name,
                      "state": "paused" if getattr(s, "pausiert", False) else s.state, "rows": s.rows, "cols": s.cols, "pid": s.pid, "gestartet": s.gestartet}
                     for s in self.sessions.values() if s.state in ("starting", "running")
                     and (self.verteiler is None or self.anzeige.get(s.terminal_id) == ort)]  # jeder Desktop sieht nur, was er zeigt
        self._publish("terminal_list", {"request_id": request_id, "starts": [e.wire() for e in self.starts.values()],
                                        "terminals": terminals}, message_id=f"list-{request_id[-80:]}", **({"ort": ort} if ort is not None else {}))

    def start_terminal(self, payload: dict, ort: str | None = None) -> None:
        start = self.starts.get(payload["start_id"])
        terminal_id = f"t-{uuid.uuid4().hex[:10]}"
        if start is None:
            self._state(terminal_id, payload["start_id"], "unbekannt", "failed", None, "unknown_start_id", ort=ort)
            return
        with self._lock:
            running = [s for s in self.sessions.values() if s.state in ("starting", "running")]
            if len(running) >= MAX_TERMINALS:
                self._state(terminal_id, start.start_id, start.name, "failed", None, "too_many_terminals", ort=ort)
                return
            token = secrets.token_urlsafe(24)
            argv, cwd, env = build_command(start, self.orte[start.ort], terminal_id, token, self.runtime_dir)
            session = TerminalSession(
                terminal_id, start, token, argv, cwd, env, payload["rows"], payload["cols"],
                on_output=lambda data, t=terminal_id: self._output(t, data),
                on_exit=lambda code, t=terminal_id: self._exited(t, code),
                remote_kill=(lambda sig, o=self.orte[start.ort], t=terminal_id: remote_kill(o, t, sig))
                if self.orte[start.ort].kind == "docker" else None,
            )
            self.sessions[terminal_id] = session
            self._seq[terminal_id] = 0
            try:
                self.register.anlegen(terminal_id, start.name, strom=strom_von(start.programm), start_id=start.start_id, laufort=start.ort)
            except RegisterFehler:
                self._abweisen("register_voll")
            if self.verteiler is not None and ort is not None:
                self.anzeige[terminal_id] = ort  # der Desktop, der den Start verlangt hat, zeigt das Terminal
                self.ziel[terminal_id] = ort
        self._state(session, start.start_id, start.name, "starting")
        try:
            session.start()
        except OSError as exc:
            session.state = "exited"
            self.register.zustand_setzen(terminal_id, "failed")
            self._state(session, start.start_id, start.name, "failed", None, repr(exc))
            return
        with self._zustand_sperre:
            if session.state == "running":  # ein Programm, das sofort wieder endet, meldet nur „exited“ (nie „running“ nach „exited“)
                self.register.zustand_setzen(terminal_id, "running")
                self._state(session, start.start_id, start.name, "running")
        self._startnachricht_planen(session)

    # ---- G10: Hände ------------------------------------------------------------------------------------------------------
    def _haende_ziel(self, terminal_id: str, wunsch: str | None) -> tuple[str | None, str]:
        """(Ziel-Schlüssel, Grund). Das Ziel ist das gebundene Fenster auf dem Zielort des Agenten; nie ein Index, nie der ganze Desktop."""
        if self.verteiler is None:
            return None, "haende_brauchen_verteiler"
        ziel = wunsch or self.ziel_info.get(terminal_id, {}).get("target_id")
        if not isinstance(ziel, str) or not ziel_schluessel_modul.ist_fenster(ziel):
            return None, "kein_fenster_ziel"
        if ziel_schluessel_modul.ort_von(ziel) != self.ziel.get(terminal_id):
            return None, "ziel_anderer_ort"
        if self.ziel_info.get(terminal_id, {}).get("target_id") != ziel:
            return None, "ziel_nicht_gebunden"
        return ziel, ""

    def lease_befehl(self, terminal_id: str, request: dict) -> dict:
        aktion = request.get("aktion", "nehmen")
        ziel, grund = self._haende_ziel(terminal_id, request.get("ziel") if isinstance(request.get("ziel"), str) else None)
        if ziel is None:
            return {"ok": False, "reason": grund}
        if aktion == "freigeben":
            return {"ok": self.leases.freigeben(ziel, terminal_id), "ziel": ziel}
        ttl = request.get("ttl_s")
        if ttl is not None and (isinstance(ttl, bool) or not isinstance(ttl, (int, float))):
            return {"ok": False, "reason": "ttl_ungueltig"}
        lease, grund = self.leases.erwerben(ziel, terminal_id, ttl)
        if lease is None:
            return {"ok": False, "reason": grund, "ziel": ziel}
        return {"ok": True, "ziel": ziel, "lease": lease.id, "laeuft_ab_in_s": round(lease.bis - self.leases._uhr(), 1)}

    def haende_befehl(self, terminal_id: str, request: dict) -> dict:
        """Ein Hände-Auftrag des Agenten: Aktion, Lease und Ziel prüfen, an den Desktop des Ziels schicken, auf das Ergebnis warten."""
        roh = request.get("aktion")
        a = ControllerAktion.aus_dict(roh) if isinstance(roh, dict) and roh.get("art") == "controller" else Aktion.aus_dict(roh)
        if a is None:
            return {"ok": False, "reason": "aktion_ungueltig"}
        ziel, grund = self._haende_ziel(terminal_id, None)
        if ziel is None:
            return {"ok": False, "reason": grund}
        lease = self.leases.von(ziel)
        if lease is None:
            return {"ok": False, "reason": "lease_fehlt", "status": "abgelehnt"}
        if lease.halter != terminal_id:
            return {"ok": False, "reason": "lease_fremd", "status": "abgelehnt"}
        if any(w["terminal_id"] == terminal_id for w in self._haende_wartend.values()):
            return {"ok": False, "reason": "haende_laeuft_schon"}
        seq = request.get("seq")
        if seq is None:
            meta = self.latest_frame(terminal_id)
            seq = meta.get("seq") if meta else None
        if seq is not None and (isinstance(seq, bool) or not isinstance(seq, int) or seq < 0):
            return {"ok": False, "reason": "seq_ungueltig"}
        auftrag_id = f"h-{uuid.uuid4().hex[:10]}"
        wartend = {"terminal_id": terminal_id, "ziel": ziel, "event": threading.Event(), "ergebnis": None}
        self._haende_wartend[auftrag_id] = wartend
        try:
            self._publish("haende_auftrag", {"terminal_id": terminal_id, "auftrag_id": auftrag_id, "ziel": ziel, "lease": lease.id, "lease_bis_ms": int((time.time() + (lease.bis - self.leases._uhr())) * 1000),
                                             "seq": seq, "aktion": a.zu_dict()}, ort=self.ziel.get(terminal_id), message_id=f"haende-{auftrag_id}")
            if not wartend["event"].wait(HAENDE_WARTEN_S):
                return {"ok": False, "reason": "keine_antwort", "auftrag_id": auftrag_id, "hinweis": "gesendet, aber der Körper hat nicht geantwortet: ob etwas ankam, ist unbekannt"}
            e = dict(wartend["ergebnis"])
            return {"ok": e["status"] == "ausgefuehrt", "auftrag_id": auftrag_id, **{k: e[k] for k in ("status", "grund", "accepted", "delivered", "observed", "dauer_ms", "audited")}}
        finally:
            self._haende_wartend.pop(auftrag_id, None)

    def haende_ergebnis(self, payload: dict, von: str | None) -> None:
        wartend = self._haende_wartend.get(payload["auftrag_id"])
        if wartend is None or wartend["terminal_id"] != payload["terminal_id"]:
            self._abweisen("haende_ergebnis_unbekannt")
            return
        if self.verteiler is not None and ziel_schluessel_modul.ort_von(wartend["ziel"]) != von:
            self._abweisen("haende_ergebnis_vom_falschen_ort")
            return
        if payload["grund"] in HAENDE_STOPP_GRUENDE:
            self.leases.entziehen_wenn(lambda z: z == wartend["ziel"] or payload["grund"] == "not_aus")  # nach einem Stopp muss der Agent die Lease ausdrücklich neu holen
        wartend["ergebnis"] = payload
        wartend["event"].set()

    # ---- G11: WorldDOM -------------------------------------------------------------------------------------------------------------
    def weltdom_befehl(self, terminal_id: str, request: dict) -> dict:
        """Ein Befehl des Agenten an den WorldDOM seines Zielfensters: Argumente streng prüfen, bei Handlungen die Lease verlangen, an den Desktop des Ziels schicken, auf die Antwort warten."""
        befehl = request.get("befehl")
        args = weltdom_befehle.pruefe_args(befehl, request.get("args", {}))
        if args is None:
            return {"ok": False, "reason": "befehl_ungueltig"}
        ziel, grund = self._haende_ziel(terminal_id, None)
        if ziel is None:
            return {"ok": False, "reason": grund}
        lease = self.leases.von(ziel)
        if weltdom_befehle.braucht_lease(befehl, args):
            if lease is None:
                return {"ok": False, "reason": "lease_fehlt", "status": "abgelehnt"}
            if lease.halter != terminal_id:
                return {"ok": False, "reason": "lease_fremd", "status": "abgelehnt"}
        if any(w["terminal_id"] == terminal_id for w in self._weltdom_wartend.values()):
            return {"ok": False, "reason": "weltdom_laeuft_schon"}
        seq = request.get("seq")
        if seq is None:
            meta = self.latest_frame(terminal_id)
            seq = meta.get("seq") if meta else None
        if seq is not None and (isinstance(seq, bool) or not isinstance(seq, int) or seq < 0):
            return {"ok": False, "reason": "seq_ungueltig"}
        if befehl == "zeige" and args.get("empfaenger"):
            aufgeloest = []
            for name in args["empfaenger"]:
                a = self.register.finde(name)
                if a is None:
                    return {"ok": False, "reason": "empfaenger_unbekannt", "empfaenger": name}
                aufgeloest.append(a.terminal_id)
            args["empfaenger"] = aufgeloest
        if befehl in ("zeige", "anker_neu", "profil_speichern", "profil_laden"):  # der Urheber steht im Knoten bzw. im Zeichen: vom Starter gesetzt, nie vom Agenten selbst
            args["urheber"] = self.register.agenten[terminal_id].name if terminal_id in self.register.agenten else terminal_id
        auftrag_id = f"w-{uuid.uuid4().hex[:10]}"
        wartend = {"terminal_id": terminal_id, "ziel": ziel, "event": threading.Event(), "ergebnis": None}
        self._weltdom_wartend[auftrag_id] = wartend
        try:
            bis = int((time.time() + (lease.bis - self.leases._uhr())) * 1000) if lease is not None and lease.halter == terminal_id else 0
            self._publish("weltdom_auftrag", {"terminal_id": terminal_id, "auftrag_id": auftrag_id, "befehl": befehl, "ziel": ziel, "lease_bis_ms": bis, "seq": seq, "args": args},
                          ort=self.ziel.get(terminal_id), message_id=f"weltdom-{auftrag_id}")
            if not wartend["event"].wait(WELTDOM_WARTEN_S):
                return {"ok": False, "reason": "keine_antwort", "auftrag_id": auftrag_id, "hinweis": "gesendet, aber der Körper hat nicht geantwortet: ob etwas geschah, ist unbekannt"}
            e = wartend["ergebnis"]
            return {"ok": e["status"] in ("ok", "ausgefuehrt", "praesentiert", "eingefuegt", "virtuell"), "auftrag_id": auftrag_id, "status": e["status"], **e["daten"]}
        finally:
            self._weltdom_wartend.pop(auftrag_id, None)

    def weltdom_ergebnis(self, payload: dict, von: str | None) -> None:
        wartend = self._weltdom_wartend.get(payload["auftrag_id"])
        if wartend is None or wartend["terminal_id"] != payload["terminal_id"]:
            self._abweisen("weltdom_ergebnis_unbekannt")
            return
        if self.verteiler is not None and ziel_schluessel_modul.ort_von(wartend["ziel"]) != von:
            self._abweisen("weltdom_ergebnis_vom_falschen_ort")
            return
        grund = payload["daten"].get("grund")
        if isinstance(grund, str) and grund in HAENDE_STOPP_GRUENDE:
            self.leases.entziehen_wenn(lambda z: z == wartend["ziel"] or grund == "not_aus")
        wartend["ergebnis"] = payload
        wartend["event"].set()

    # ---- G12: Abläufe und Regiesprüche ----------------------------------------------------------------------------------------------------------------
    def ablauf_steuern(self, payload: dict, von: str | None) -> None:
        """Daniels Steuerung vom Desktop. Nur Desktops, die die neuen Meldungen verstehen (haben nach den Anzeigeorten gefragt), dürfen steuern."""
        if self.verteiler is not None and von not in self.faehig:
            self._abweisen("ablauf_steuern_unbekannter_desktop")
            return
        self.ablauf.steuern(payload)
        self.ablauf_stand_senden()

    def ablauf_stand_senden(self) -> None:
        stand = self.ablauf.stand()
        if self.verteiler is None:
            self._publish("ablauf_stand", stand, message_id=f"ablaufstand-{uuid.uuid4().hex[:8]}")
            return
        for ort in list(self.faehig):
            if self.verteiler.online(ort):
                self._publish("ablauf_stand", stand, ort=ort, message_id=f"ablaufstand-{uuid.uuid4().hex[:8]}")

    def regie_spruch(self, payload: dict) -> None:
        """In eigenem Faden: „Neu scannen“ wartet auf den Körper, und die Ereigniswarteschlange darf dabei nie stehen."""
        threading.Thread(target=self._regie_spruch_ausfuehren, args=(payload,), daemon=True, name="regie").start()

    def _regie_spruch_ausfuehren(self, payload: dict) -> None:
        tid = payload["terminal_id"]
        r = self.ablauf.regie(tid, payload["spruch"])
        self.kapseln.erfassen("regie", tid, f"Regiespruch: {payload['spruch'][:60]}", {"wirkung": str(r["wirkung"])[:20], "aktion": str(r["aktion"])[:40]})
        self._publish("regie_ergebnis", {"terminal_id": tid, "spruch": r["spruch"][:60], "wirkung": str(r["wirkung"])[:20], "aktion": str(r["aktion"])[:40], "hinweis": str(r["hinweis"])[:400],
                                         "zugestellt": bool(r["zugestellt"])}, message_id=f"regie-{tid}-{uuid.uuid4().hex[:6]}")

    # ---- G09: Pause, Zustellung, Aufträge ----------------------------------------------------------------------------
    def steuern(self, terminal_id: str, aktion: str) -> None:
        """Daniel hält einen Agenten an oder lässt ihn weiterlaufen. Der Zustand „paused“ geht an alle, die das Terminal zeigen."""
        session = self.sessions.get(terminal_id)
        if session is None or session.state != "running":
            self._abweisen("steuern_unbekannt")
            return
        if aktion == "pause":
            ok, neu = session.pausieren(), "paused"
        elif aktion == "fortsetzen":
            ok, neu = session.fortsetzen(), "running"
        else:
            self._abweisen("steuern_aktion")
            return
        if not ok:
            self._abweisen("steuern_nicht_moeglich")
            return
        self.register.zustand_setzen(terminal_id, neu)
        self.register.speichern(self.runtime_dir / "register.json")
        self._state(session, session.entry.start_id, session.entry.name, neu)

    def _tippen(self, session: TerminalSession, text: str) -> None:
        """Eine Zeile Text wie getippt in die Sitzung geben (Text, kurze Pause, Enter) — je Sitzung nacheinander, damit sich zwei Zustellungen nicht vermischen."""
        sperre = self._tipp_sperren.setdefault(session.terminal_id, threading.Lock())
        with sperre:
            try:
                session.write(text.replace("\n", " ").replace("\r", " ").encode("utf-8"))
                self._schlafen(STARTNACHRICHT_ENTER_PAUSE_S)
                session.write(b"\r")
            except OSError:
                pass

    def _zustellen(self, zustellungen) -> None:
        """Je Empfänger eine Warteschlange mit genau einem Arbeiter: Nachrichten kommen in der Reihenfolge an, in der sie gesendet wurden (ein Thread je Nachricht hätte das nicht garantiert)."""
        for z in zustellungen:
            session = self.sessions.get(z.an)
            if session is not None and session.state == "running":
                with self._zustell_sperre:
                    self._zustell_warteschlangen.setdefault(z.an, collections.deque()).append((session, z.text))
                    if z.an not in self._zustell_laeuft:
                        self._zustell_laeuft.add(z.an)
                        threading.Thread(target=self._zustell_lauf, args=(z.an,), daemon=True, name=f"zustellen-{z.an}").start()

    def _zustell_lauf(self, an: str) -> None:
        while True:
            with self._zustell_sperre:
                warteschlange = self._zustell_warteschlangen.get(an)
                if not warteschlange:
                    self._zustell_laeuft.discard(an)
                    return
                session, text = warteschlange.popleft()
            self._tippen(session, text)

    def agenten_liste(self) -> list[dict]:
        liste = []
        for a in self.register.agenten.values():
            d = a.zu_dict()
            d["faehigkeiten"] = a.faehigkeiten()
            d["auftraege_offen"] = sum(1 for x in self.register.auftraege_an(a.terminal_id) if x.status in ("gesendet", "angenommen", "laeuft"))
            liste.append(d)
        return liste

    def _agent_befehl(self, terminal_id: str, command: str, request: dict) -> dict | None:
        """Wie `_agent_befehl_roh`, und zeichnet zusätzlich im Ereignisprotokoll auf (G13): reines Zuhören, ändert nie die Antwort."""
        praxis_kontext = self.praxis.kontext(terminal_id) if command != "test" else {}
        antwort = self._agent_befehl_roh(terminal_id, command, request)
        if antwort is not None:
            self.praxis.befehlspur(terminal_id, command, request, antwort, praxis_kontext)
        if antwort is not None and command not in ("kapsel", "seed", "test"):
            art = {"nachricht": "nachricht", "auftrag": "auftrag", "auftrag_status": "auftrag", "haende": "haende", "weltdom": "weltdom", "lease": "lease", "ablauf": "ablauf"}.get(command)
            if art:
                text = str(request.get("text") or request.get("befehl") or request.get("status") or request.get("an") or "")[:600]
                self.kapseln.erfassen(art, terminal_id, f"{command}: {text}".strip(": "), {"ok": bool(antwort.get("ok")), "reason": antwort.get("reason") or antwort.get("grund", ""), "an": request.get("an") if isinstance(request.get("an"), str) else ""})
        return antwort

    def _agent_befehl_roh(self, terminal_id: str, command: str, request: dict) -> dict | None:
        """Befehle des Agenten an das Register. None = kein solcher Befehl. Jeder Fehler des Registers wird zu einer Antwort mit Grund."""
        r = self.register
        try:
            if command == "lease":
                return self.lease_befehl(terminal_id, request)
            if command == "haende":
                return self.haende_befehl(terminal_id, request)
            if command == "weltdom":
                return self.weltdom_befehl(terminal_id, request)
            if command == "ablauf":
                return self.ablauf.befehl(terminal_id, request)
            if command == "kapsel":
                return self.kapseln.befehl(terminal_id, request)
            if command == "seed":
                return self.seeds.befehl(terminal_id, request)
            if command == "test":
                antwort = self.praxis.befehl(terminal_id, request)
                if isinstance(antwort, dict):
                    antwort["lage"] = self.lage_kurz(terminal_id)  # jeder weiß bei jeder Antwort, was für ihn gerade klappt (lage.py)
                return antwort
            if command == "lage":
                from augen_haende_bridge import lage as lagebild

                lage = self.lage_von(terminal_id)
                return {"ok": True, "ich": terminal_id, "sage": lagebild.satz(lage), **lage}
            if command == "agenten":
                return {"ok": True, "ich": terminal_id, "agenten": self.agenten_liste(), "gruppen": r.gruppen()}
            if command == "gruppe":
                gruppe, aktion = request.get("gruppe"), request.get("aktion")
                if aktion == "beitreten":
                    r.gruppe_beitreten(terminal_id, gruppe)
                elif aktion == "verlassen":
                    r.gruppe_verlassen(terminal_id, gruppe)
                else:
                    return {"ok": False, "reason": "aktion_ungueltig"}
                return {"ok": True, "gruppen": r.gruppen()}
            if command == "nachricht":
                zustellungen, abgelehnt = r.nachricht(terminal_id, request.get("an"), request.get("gruppe"), request.get("text"))
                self._zustellen(zustellungen)
                pausiert = [z.name for z in zustellungen if (self.sessions.get(z.an) is not None and getattr(self.sessions[z.an], "pausiert", False))]
                return {"ok": bool(zustellungen), "zugestellt": [z.name for z in zustellungen], "abgelehnt": abgelehnt, "pausiert": pausiert,
                        **({} if zustellungen else {"reason": "niemand_erreicht"})}
            if command == "auftrag":
                auftrag = r.auftrag_neu(terminal_id, request.get("an"), request.get("text"))
                ziel = r.agenten[auftrag.an]
                cli = self.orte[self.sessions[auftrag.an].entry.ort].seen(str(self.cli_pfad))
                absender = r.agenten[terminal_id].name
                text = (f"[Bridge · Auftrag {auftrag.id} von {absender}] {auftrag.text} — Status melden mit: python3 {cli} auftrag-status {auftrag.id} "
                        f"angenommen|laeuft|fertig|fehler \"Ergebnis\"")
                self._zustellen([Zustellung(ziel.terminal_id, ziel.name, text)])
                return {"ok": True, "auftrag": auftrag.zu_dict(), "hinweis": "gesendet; „fertig“ gilt erst, wenn der Empfänger es selbst meldet"}
            if command == "auftrag_status":
                auftrag = r.auftrag_status(request.get("id"), terminal_id, request.get("status"), request.get("ergebnis", ""), request.get("unsicherheit", ""))
                return {"ok": True, "auftrag": auftrag.zu_dict()}
            if command == "auftraege":
                return {"ok": True, "gesendet": [a.zu_dict() for a in r.auftraege_von(terminal_id)], "erhalten": [a.zu_dict() for a in r.auftraege_an(terminal_id)]}
            if command == "kind":
                kind = r.kind_melden(terminal_id, request.get("name"), request.get("strom", "shell") if isinstance(request.get("strom"), str) else "shell")
                return {"ok": True, "agent": kind.zu_dict(), "hinweis": "gemeldet, nicht steuerbar: die Bridge kann diesen Unteragenten weder ansprechen noch anhalten"}
        except RegisterFehler as fehler:
            return {"ok": False, "reason": str(fehler)}
        return None

    # ---- Sprache: Daniels Äußerungen erkennen ------------------------------------------------------------
    def _audio_annehmen(self, payload: dict) -> None:
        terminal_id = payload.get("terminal_id", "")
        session = self.sessions.get(terminal_id)
        if session is None or session.state != "running" or self.transkriber is None:
            return
        if self._audio_schlange.qsize() >= MAX_AUDIO_WARTESCHLANGE:
            self.audio_verworfen += 1
            return
        self._audio_schlange.put((terminal_id, base64.b64decode(payload["data"]), payload["dauer_ms"]))

    def _audio_lauf(self) -> None:
        vorladen = getattr(self.transkriber, "vorladen", None)
        if vorladen is not None:
            vorladen()
        while True:
            eintrag = self._audio_schlange.get()
            if eintrag is None:
                return
            terminal_id, wav, dauer_ms = eintrag
            try:
                text = self.transkriber.transkribiere(wav)
                self.transkription_fehler = None
            except Exception as fehler:
                self.transkription_fehler = f"{fehler!r}"[:200]
                continue
            if not text:
                continue
            satz = {"text": text, "zeit_ms": int(time.time() * 1000)}
            with self._lock:
                liste = self.saetze.setdefault(terminal_id, [])
                liste.append(satz)
                del liste[:-MAX_SAETZE]
            self._publish("sprache_text", {"terminal_id": terminal_id, "text": text[:MAX_SPRACHE_TEXT], "dauer_ms": int(dauer_ms),
                                           "modell": str(getattr(self.transkriber, "modell", "whisper"))[:60]},
                          message_id=f"sprache-{terminal_id}-{uuid.uuid4().hex[:8]}")

    def neue_saetze(self, terminal_id: str) -> list[dict]:
        """Was Daniel seit dem letzten Aufruf gesagt hat (für den Agenten, `bridge_cli hoere`)."""
        with self._lock:
            liste = self.saetze.get(terminal_id, [])
            gelesen = min(self._gelesen.get(terminal_id, 0), len(liste))
            neu = liste[gelesen:]
            self._gelesen[terminal_id] = len(liste)
        return [dict(s) for s in neu]

    # ---- Startnachricht: dem Agenten sagen, wie er über die Bridge spricht ---------------------------
    def startnachricht_text(self, session: TerminalSession) -> str:
        eintrag = session.entry
        if not eintrag.startnachricht:
            return ""
        cli = self.orte[eintrag.ort].seen(str(self.cli_pfad))
        if eintrag.startnachricht == "standard":
            return standard_startnachricht(cli)
        return eintrag.startnachricht.replace("{cli}", cli)

    def _startnachricht_planen(self, session: TerminalSession) -> None:
        text = self.startnachricht_text(session)
        if text:
            threading.Thread(target=self._startnachricht_senden, args=(session, text), daemon=True,
                             name=f"startnachricht-{session.terminal_id}").start()

    # Bildschirmtexte (ohne Leerzeichen und Groß-/Kleinschreibung, denn die Oberflächen setzen Zeichen einzeln), hinter denen ein Programm auf eine Bestätigung wartet. Ein Enter dort würde die
    # vorgewählte Antwort bestätigen — bei Claude Code „Nein, beenden“.
    BESTAETIGUNGSDIALOGE = ("yes,itrustthisfolder", "isthisaprojectyoucreatedoroneyoutrust", "doyoutrustthefilesinthisfolder", "doyoutrustthisfolder")

    def _wartet_auf_bestaetigung(self, session: TerminalSession) -> bool:
        ende = bytes(getattr(session, "replay", b"")[-3000:])
        roh = re.sub(rb"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()][A-Za-z0-9]", b"", ende)
        text = re.sub(r"\s+", "", roh.decode("utf-8", "replace")).lower()
        return any(m in text for m in self.BESTAETIGUNGSDIALOGE)

    def _startnachricht_senden(self, session: TerminalSession, text: str) -> None:
        """Tippt die Nachricht, sobald die Sitzung zur Ruhe gekommen ist (ihr Programm wartet dann auf Eingabe).

        Text und Enter gehen getrennt hinaus: Oberflächen wie die von Claude Code halten einen schnell eintreffenden Block für Eingefügtes,
        und ein Enter darin wird dort zu einem Zeilenumbruch statt zum Absenden. Mit kurzer Pause danach ist es ein echtes Enter."""
        ende = self._uhr() + STARTNACHRICHT_MAX_S
        blockiert = False
        while self._uhr() < ende and session.state == "running":
            if session.letzte_ausgabe and self._uhr() - session.letzte_ausgabe >= STARTNACHRICHT_RUHE_S and self._wartet_auf_bestaetigung(session):
                if not blockiert:
                    blockiert = True
                    ende = max(ende, self._uhr() + STARTNACHRICHT_BLOCK_MAX_S)
                    self._startnachricht_log(session, "wartet: das Programm fragt nach einer Bestätigung (z. B. Vertrauen für den Ordner) — Daniel muss sie geben; es wird nichts hineingetippt")
            elif session.letzte_ausgabe and self._uhr() - session.letzte_ausgabe >= STARTNACHRICHT_RUHE_S:
                try:
                    session.write(text.encode("utf-8"))
                    self._schlafen(STARTNACHRICHT_ENTER_PAUSE_S)
                    session.write(b"\r")
                    self._startnachricht_log(session, "getippt")
                except OSError:
                    self._startnachricht_log(session, "schreibfehler")
                return
            self._schlafen(0.25)
        self._startnachricht_log(session, f"nicht getippt (Sitzung {session.state}, Ausgabe {'ja' if session.letzte_ausgabe else 'nie'})")

    def _startnachricht_log(self, session: TerminalSession, was: str) -> None:
        """Eine Zeile je Versuch in `startnachricht.log` im Laufzeitordner: damit man sieht, ob und warum eine Startnachricht ausblieb."""
        try:
            with open(self.runtime_dir / "startnachricht.log", "a", encoding="utf-8") as datei:
                datei.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {getattr(session, 'terminal_id', '?')} {was}\n")
        except (OSError, AttributeError):
            pass

    def _output(self, terminal_id: str, data: bytes) -> None:
        self.kapseln.ausgabe(terminal_id, data)
        with self._ausgabe_sperre:  # Ausgabe und Wiederaufnahme dürfen sich nicht vermischen
            session = self.sessions.get(terminal_id)
            if session is not None:
                session.letzte_ausgabe = self._uhr()
                session.replay += data
                if len(session.replay) > REPLAY_MAX:
                    del session.replay[:len(session.replay) - REPLAY_MAX]
                    ende = session.replay.find(b"\n", 0, 4096)  # an einer Zeilengrenze anfangen, damit nicht mitten in einer Zeile begonnen wird
                    if ende >= 0:
                        del session.replay[:ende + 1]
            seq = self._seq[terminal_id]
            self._seq[terminal_id] = seq + 1
            self._publish("terminal_output", {"terminal_id": terminal_id, "seq": seq,
                                              "data": base64.b64encode(data).decode()},
                          message_id=f"o-{terminal_id}-{seq}")

    def attach(self, terminal_id: str) -> None:
        """Wiederaufnahme: die gemerkte Ausgabe noch einmal senden. Das erste Stück trägt "replay": true; die Bridge setzt ihren
        Bildschirm dann zurück und baut Bildschirm und Rückblättern aus diesen Bytes neu auf. Die Sitzung selbst wird nicht berührt."""
        with self._ausgabe_sperre:
            session = self.sessions.get(terminal_id)
            if session is None or session.state != "running" or not session.replay:
                return
            daten = bytes(session.replay)
            for i in range(0, len(daten), REPLAY_STUECK):
                seq = self._seq[terminal_id]
                self._seq[terminal_id] = seq + 1
                nutzlast = {"terminal_id": terminal_id, "seq": seq, "data": base64.b64encode(daten[i:i + REPLAY_STUECK]).decode()}
                if i == 0:
                    nutzlast["replay"] = True
                self._publish("terminal_output", nutzlast, message_id=f"o-{terminal_id}-{seq}")

    def _exited(self, terminal_id: str, code: int) -> None:
        session = self.sessions[terminal_id]
        session.pausiert = False
        with self._zustand_sperre:
            self.register.zustand_setzen(terminal_id, "exited")
            self._state(session, session.entry.start_id, session.entry.name, "exited", code)

    # ---- Bilder je Terminal ---------------------------------------------------------------
    def store_frame(self, payload: dict, ort: str | None = None) -> None:
        terminal_id = payload.get("terminal_id") or "_desktop"
        if not IDENT.fullmatch(terminal_id):
            return
        if self.verteiler is not None and terminal_id in self.sessions:
            # Bilder gelten nur vom Zielort; ein anderer Desktop darf dem Agenten kein Bild unterschieben (R011/R012).
            if self.ziel.get(terminal_id) != ort:
                self.frames_abgewiesen[terminal_id] = self.frames_abgewiesen.get(terminal_id, 0) + 1
                self._abweisen("frame_vom_falschen_ziel")
                return
            if self.ziel_info.get(terminal_id, {}).get("zustand") == "weg":
                self.frames_abgewiesen[terminal_id] = self.frames_abgewiesen.get(terminal_id, 0) + 1
                self._abweisen("frame_ziel_weg")  # das Ziel ist geschlossen: kein Bild eines anderen Fensters, bis ein neues Ziel ausdrücklich gebunden ist
                return
        directory = self.frames_dir / terminal_id
        directory.mkdir(parents=True, exist_ok=True)
        self.kapseln.erfassen("frame", terminal_id, f"Bild {payload.get('width')}×{payload.get('height')} ({payload.get('source')})", {"source": payload.get("source"), "seq": payload.get("seq")})
        ext = "png" if payload["mime"] == "image/png" else "jpg"
        blob = base64.b64decode(payload["data"])
        name = f"frame-{payload['captured_at_ms']}.{ext}"
        target = directory / name
        temp = directory / f".{name}.tmp"
        temp.write_bytes(blob)
        os.replace(temp, target)
        meta = {"file": name, "mime": payload["mime"], "captured_at_ms": payload["captured_at_ms"],
                "received_at_ms": int(time.time() * 1000), "width": payload["width"], "height": payload["height"],
                "sha256": payload.get("sha256"), "source": payload["source"],
                "target_id": self.ziel_info.get(terminal_id, {}).get("target_id")}
        for feld in ("aufnahme", "fallback_grund", "seq"):  # G06.7: Quelle des Bildes (Fenster oder Ausschnitt), Rückfallgrund, Folge je Agent
            if feld in payload:
                meta[feld] = payload[feld]
        meta_temp = directory / ".latest.json.tmp"
        meta_temp.write_text(json.dumps(meta), encoding="utf-8")
        os.replace(meta_temp, directory / "latest.json")
        old = sorted(p for p in directory.glob("frame-*") if p.is_file())
        for path in old[:-KEEP_FRAMES]:
            path.unlink(missing_ok=True)

    SEE_WARTE_S = 4.0

    def frisches_bild(self, terminal_id: str) -> dict | None:
        """`see`: dem Körper sagen, dass jetzt ein frisches Bild gebraucht wird, und kurz auf eines warten, das danach aufgenommen wurde. Kommt keins
        (kein Ziel, Strom aus, Körper weg), gilt das letzte Bild mit seinem wahren Alter; die Belegprüfung entscheidet dann selbst über „frisch“."""
        vor_ms = int(time.time() * 1000)
        self._publish("bild_sofort", {"terminal_id": terminal_id}, message_id=f"bild-{terminal_id}-{uuid.uuid4().hex[:8]}")
        ende = time.monotonic() + self.SEE_WARTE_S
        meta = self.latest_frame(terminal_id)
        while time.monotonic() < ende and not (meta and type(meta.get("captured_at_ms")) is int and meta["captured_at_ms"] >= vor_ms):
            time.sleep(0.1)
            meta = self.latest_frame(terminal_id)
        return meta

    def latest_frame(self, terminal_id: str) -> dict | None:
        meta_path = self.frames_dir / terminal_id / "latest.json"
        if not IDENT.fullmatch(terminal_id) or not meta_path.is_file():
            return None
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["age_ms"] = int(time.time() * 1000) - meta["received_at_ms"]
        meta["relative_path"] = f"frames/{terminal_id}/{meta['file']}"
        return meta

    # ---- Sprech-Socket für die Agenten --------------------------------------------------
    def agent_request(self, request: dict) -> dict:
        if not isinstance(request, dict):
            return {"ok": False, "reason": "invalid_request"}
        terminal_id, token = request.get("terminal_id"), request.get("token")
        session = self.sessions.get(terminal_id) if isinstance(terminal_id, str) else None
        if session is None or not isinstance(token, str) or not secrets.compare_digest(session.token, token):
            return {"ok": False, "reason": "unknown_terminal_or_token"}
        if session.state != "running":
            return {"ok": False, "reason": "terminal_not_running"}
        command = request.get("cmd")
        if command == "say":
            text = request.get("text")
            if not isinstance(text, str) or not 1 <= len(text) <= 8000:
                return {"ok": False, "reason": "invalid_text"}
            self.kapseln.erfassen("raute", terminal_id, f"say: {text[:200]}", {"weg": "say"})
            self._publish("raute_say", {"terminal_id": terminal_id, "text": text},
                          message_id=f"say-{terminal_id}-{uuid.uuid4().hex[:8]}")
            return {"ok": True}
        if command == "schreibe":
            text = request.get("text")
            if not isinstance(text, str) or not 1 <= len(text) <= MAX_RAUTE_TIPPEN:
                return {"ok": False, "reason": "invalid_text"}
            self.kapseln.erfassen("raute", terminal_id, f"schreibe: {text[:200]}", {"weg": "schreibe"})
            self._publish("raute_tippen", {"terminal_id": terminal_id, "text": text},
                          message_id=f"tippen-{terminal_id}-{uuid.uuid4().hex[:8]}")
            return {"ok": True, "hinweis": "gesendet; Daniels Bridge tippt es mit der Tastenkombination deiner Raute (wenn Hände erlaubt sind)"}
        if command == "hoere":
            return {"ok": True, "saetze": self.neue_saetze(terminal_id),
                    "fehler": self.transkription_fehler, "spracherkennung": self.transkriber is not None}
        if command == "see":
            praxis_kontext = self.praxis.kontext(terminal_id)
            meta = self.frisches_bild(terminal_id)
            if meta:
                self.kapseln.erfassen("sehen", terminal_id, f"see: Bild {meta.get('width')}×{meta.get('height')} (Quelle {meta.get('source')}, Alter {meta.get('age_ms')} ms)",
                                     {k: meta.get(k) for k in ("seq", "age_ms", "captured_at_ms", "received_at_ms", "target_id", "source")})
                if praxis_kontext:
                    frisch = (type(meta.get("captured_at_ms")) is int and meta["captured_at_ms"] >= praxis_kontext["since_ms"]
                              and type(meta.get("received_at_ms")) is int and meta["received_at_ms"] >= praxis_kontext["since_ms"]
                              and bool(meta.get("target_id")) and meta["target_id"] == praxis_kontext["target_id"]
                              and meta.get("source") not in (None, "file", "synthetic"))
                    self.kapseln.erfassen("sonstiges", terminal_id, "Praxistest-Bildbeleg", {"praxis": praxis_kontext, "command": "see", "ok": True, "capture_fresh": frisch})
            return {"ok": True, "frame": meta} if meta else {"ok": False, "reason": "no_frame_yet"}
        antwort = self._agent_befehl(terminal_id, command, request)
        if antwort is not None:
            self.register.speichern(self.runtime_dir / "register.json")  # Gruppen und Aufträge überdauern einen Neustart des Starters (als Verlauf, nicht als Sitzung)
            return antwort
        return {"ok": False, "reason": "unknown_command"}

    def serve_agents(self, socket_path: Path) -> socketserver.BaseServer:
        launcher = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                line = self.rfile.readline(SOCKET_LINE_LIMIT + 1)
                try:
                    if len(line) > SOCKET_LINE_LIMIT:
                        raise ValueError("too_long")
                    reply = launcher.agent_request(json.loads(line))
                except (ValueError, TypeError):
                    reply = {"ok": False, "reason": "invalid_request"}
                self.wfile.write((json.dumps(reply) + "\n").encode())

        socket_path = Path(socket_path)
        socket_path.parent.mkdir(parents=True, exist_ok=True)
        socket_path.unlink(missing_ok=True)
        server = socketserver.ThreadingUnixStreamServer(str(socket_path), Handler)
        os.chmod(socket_path, 0o666)
        threading.Thread(target=server.serve_forever, name="agent-socket", daemon=True).start()
        return server

    def shutdown(self) -> None:
        self.seeds.stoppen()  # kein Loop läuft nach dem Ende des Starters weiter
        self._beendet.set()
        self._events.put(None)
        self._audio_schlange.put(None)
        for session in list(self.sessions.values()):
            session.close()
