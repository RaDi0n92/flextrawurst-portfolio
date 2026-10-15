"""Das Ereignisprotokoll des Starters (G13): was zwischen den Agenten, Daniel und den Zielen geschah — Zeit, Quelle, Agent, Ziel, Art — ohne ein einziges Modell.

Hier laufen die Spuren zusammen, aus denen Momentkapseln, der Zeit-Scrubber und die Beobachtung durch Hauhaucs gebaut werden: Nachrichten, Aufträge, Regiesprüche, Zustände der Terminals, Zielmeldungen, Hände- und WorldDOM-Ergebnisse, Ablauf-Ereignisse und
die Ausgabe der Terminals (als zeitgestempelte Stücke). Aufzeichnen ist reines Skript: keine Inferenz, keine Bildverarbeitung.

Begrenzt und ehrlich: Das Protokoll hält die letzten `MAX_EREIGNISSE` im Speicher und schreibt jede Zeile zusätzlich in eine Datei (bei 20 MB wird sie einmal umbenannt, nie gelöscht). Von der Terminalausgabe bleiben je Terminal die letzten
`MAX_AUSGABE_BYTES`; was darüber hinaus liegt, fehlt — und die Auswertung sagt, **dass** es fehlt (`luecke`), statt so zu tun, als wäre es da.
"""

from __future__ import annotations

import codecs
import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

MAX_EREIGNISSE = 20_000
MAX_AUSGABE_BYTES = 512 * 1024
MAX_TEXT = 2000
DATEI_MAX_BYTES = 20 * 1024 * 1024
ARTEN = ("nachricht", "auftrag", "regie", "state", "ziel", "haende", "weltdom", "ablauf", "frame", "lease", "kapsel", "beobachtung", "sehen", "raute", "sonstiges")


@dataclass
class Ereignis:
    id: str
    zeit_ms: int
    art: str
    agent: str = ""
    ziel: str = ""
    text: str = ""
    daten: dict = field(default_factory=dict)

    def zu_dict(self) -> dict:
        return {"id": self.id, "zeit_ms": self.zeit_ms, "art": self.art, "agent": self.agent, "ziel": self.ziel, "text": self.text, "daten": self.daten}

    @staticmethod
    def aus_dict(d: object) -> "Ereignis | None":
        if not isinstance(d, dict):
            return None
        try:
            return Ereignis(str(d["id"])[:40], int(d["zeit_ms"]), str(d["art"])[:20], str(d.get("agent", ""))[:96], str(d.get("ziel", ""))[:160], str(d.get("text", ""))[:MAX_TEXT], dict(d.get("daten", {})))
        except (KeyError, TypeError, ValueError):
            return None


class Ereignisprotokoll:
    def __init__(self, ordner: Path | None = None, jetzt_ms=lambda: int(time.time() * 1000)):
        self.ordner = Path(ordner) if ordner else None
        self._jetzt = jetzt_ms
        self._sperre = threading.RLock()
        self._ereignisse: deque[Ereignis] = deque(maxlen=MAX_EREIGNISSE)
        self._ausgabe: dict[str, deque] = {}  # agent -> deque[(zeit_ms, text)]
        self._ausgabe_bytes: dict[str, int] = {}
        self._ausgabe_verworfen: dict[str, int] = {}
        self._zerleger: dict[str, object] = {}
        self._nr = 0
        self.fehler = ""
        self._abonnenten: list = []
        if self.ordner:
            self._laden()

    # ---- Schreiben ---------------------------------------------------------------------------------------------------------------------
    def erfassen(self, art: str, agent: str = "", text: str = "", daten: dict | None = None, ziel: str = "") -> str:
        if art not in ARTEN:
            art = "sonstiges"
        with self._sperre:
            self._nr += 1
            e = Ereignis(f"e-{self._nr}", self._jetzt(), art, agent[:96], ziel[:160], str(text)[:MAX_TEXT], _klein(daten or {}))
            self._ereignisse.append(e)
            self._schreiben(e)
            abos = list(self._abonnenten)
        for a in abos:
            try:
                a(e)
            except Exception:
                pass  # ein kaputter Zuhörer hält das Aufzeichnen nie an
        return e.id

    def abonnieren(self, aufruf) -> None:
        """Wer jedes neue Ereignis sofort sehen will (Beobachtung, Scrubber); Fehler in der Funktion bleiben dort."""
        with self._sperre:
            self._abonnenten.append(aufruf)

    def ausgabe(self, agent: str, daten: bytes) -> None:
        """Ein Stück Terminalausgabe (als Text) mit Zeitstempel; älteres wird verworfen und gezählt."""
        with self._sperre:
            zerleger = self._zerleger.get(agent)
            if zerleger is None:
                zerleger = self._zerleger[agent] = codecs.getincrementaldecoder("utf-8")("replace")  # ein Zeichen, das über zwei Lesestücke geht, bleibt ganz
            text = zerleger.decode(daten)
            if not text:
                return  # nur der Anfang eines Mehrbyte-Zeichens: kommt mit dem nächsten Stück
        with self._sperre:
            q = self._ausgabe.setdefault(agent, deque())
            q.append((self._jetzt(), text))
            self._ausgabe_bytes[agent] = self._ausgabe_bytes.get(agent, 0) + len(text.encode("utf-8"))
            while self._ausgabe_bytes[agent] > MAX_AUSGABE_BYTES and len(q) > 1:
                _, alt = q.popleft()
                self._ausgabe_bytes[agent] -= len(alt.encode("utf-8"))
                self._ausgabe_verworfen[agent] = self._ausgabe_verworfen.get(agent, 0) + 1

    def _schreiben(self, e: Ereignis) -> None:
        if self.ordner is None:
            return
        try:
            datei = self.ordner / "ereignisse.jsonl"
            self.ordner.mkdir(parents=True, exist_ok=True)
            if datei.exists() and datei.stat().st_size > DATEI_MAX_BYTES:
                datei.replace(datei.with_suffix(".jsonl.1"))
            with open(datei, "a", encoding="utf-8") as f:
                f.write(json.dumps(e.zu_dict(), ensure_ascii=False) + "\n")
        except OSError as f:
            self.fehler = f"Protokoll nicht geschrieben: {f!r}"[:200]

    def _laden(self) -> None:
        datei = self.ordner / "ereignisse.jsonl"
        if not datei.exists():
            return
        try:
            for zeile in datei.read_text(encoding="utf-8").splitlines()[-MAX_EREIGNISSE:]:
                try:
                    e = Ereignis.aus_dict(json.loads(zeile))
                except ValueError:
                    continue
                if e is not None:
                    self._ereignisse.append(e)
                    if e.id.startswith("e-") and e.id[2:].isdigit():
                        self._nr = max(self._nr, int(e.id[2:]))
        except OSError:
            self.fehler = "Ereignisdatei unlesbar"

    # ---- Lesen -----------------------------------------------------------------------------------------------------------------------------
    def ereignis(self, eid: str) -> Ereignis | None:
        with self._sperre:
            return next((e for e in reversed(self._ereignisse) if e.id == eid), None)

    def zeitraum(self, von_ms: int = 0, bis_ms: int | None = None, agenten=None, arten=None, limit: int = 5000) -> list[Ereignis]:
        bis = bis_ms if bis_ms is not None else 2**62
        with self._sperre:
            treffer = [e for e in self._ereignisse if von_ms <= e.zeit_ms <= bis and (not agenten or e.agent in agenten or not e.agent) and (not arten or e.art in arten)]
        return treffer[-limit:]

    def letzte(self, n: int = 50, agenten=None) -> list[Ereignis]:
        with self._sperre:
            liste = [e for e in self._ereignisse if not agenten or e.agent in agenten or not e.agent]
        return liste[-n:]

    def ausgabe_bis(self, agent: str, zeit_ms: int | None = None, max_zeichen: int = 20_000) -> tuple[str, dict]:
        """Terminaltext bis zu einem Zeitpunkt (letzte `max_zeichen`) und was fehlt: `{"verworfene_stuecke": n, "abgeschnitten": bool}`."""
        with self._sperre:
            q = list(self._ausgabe.get(agent, []))
            verworfen = self._ausgabe_verworfen.get(agent, 0)
        text = "".join(t for z, t in q if zeit_ms is None or z <= zeit_ms)
        abgeschnitten = len(text) > max_zeichen
        return text[-max_zeichen:], {"verworfene_stuecke": verworfen, "abgeschnitten": abgeschnitten, "stuecke": len(q)}

    def zaehler(self, agenten=None) -> dict[str, int]:
        with self._sperre:
            z: dict[str, int] = {}
            for e in self._ereignisse:
                if not agenten or e.agent in agenten:
                    z[e.agent or "_system"] = z.get(e.agent or "_system", 0) + 1
            return z

    def anzahl(self) -> int:
        with self._sperre:
            return len(self._ereignisse)


def _klein(d: dict, tiefe: int = 0) -> dict:
    """Daten begrenzen: Zeichenketten kürzen, Tiefe und Größe beschränken, nie ein Absturz wegen unserialisierbarer Werte."""
    if tiefe > 3:
        return {}
    ergebnis = {}
    for k, v in list(d.items())[:30]:
        k = str(k)[:40]
        if isinstance(v, (int, float, bool)) or v is None:
            ergebnis[k] = v
        elif isinstance(v, str):
            ergebnis[k] = v[:400]
        elif isinstance(v, dict):
            ergebnis[k] = _klein(v, tiefe + 1)
        elif isinstance(v, (list, tuple)):
            ergebnis[k] = [(_klein(x, tiefe + 1) if isinstance(x, dict) else (x if isinstance(x, (int, float, bool)) or x is None else str(x)[:200])) for x in list(v)[:20]]
        else:
            ergebnis[k] = str(v)[:200]
    return ergebnis
