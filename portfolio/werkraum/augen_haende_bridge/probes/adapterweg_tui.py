"""Probe: kommt getippter Text (ohne Enter, es entsteht keine Anfrage) im echten TUI eines Agenten an? Startet das Programm über den echten Starter in einer PTY,
wartet auf Ruhe, tippt eine Marke und sucht sie in der Ausgabe. Ausgabe: eine JSON-Zeile je Programm. Aufruf: adapterweg_tui.py programm [programm ...]"""
import base64
import json
import re
import sys
import tempfile
import time
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent.parent / "src"), str(Path(__file__).resolve().parent.parent)]
from client_vps.terminal_launcher import Launcher, Ort, StartEntry

MARKE = "ZQXmarke7391"


class Rt:
    def __init__(self):
        self.gesendet = []

    def publish(self, kind, payload, *, message_id=None):
        self.gesendet.append((kind, payload))
        return "x"


def lauf(programm: str) -> dict:
    rt = Rt()
    name = programm.split()[0]
    l = Launcher(rt, {"p": StartEntry("p", name, "Host", __import__("os").environ.get("PROBE_ORDNER", "/tmp"), programm)}, {"Host": Ort("host", None)}, Path(tempfile.mkdtemp()))
    l.start()
    l.start_terminal({"start_id": "p", "rows": 40, "cols": 120})
    tid, s = next(iter(l.sessions.items()))
    t0 = time.monotonic()
    while time.monotonic() - t0 < 40 and not (s.letzte_ausgabe and time.monotonic() - s.letzte_ausgabe > 3.0):
        time.sleep(0.25)
    def aus() -> str:
        return b"".join(base64.b64decode(p["data"]) for k, p in rt.gesendet if k == "terminal_output").decode("utf-8", "replace")
    vorher = len(aus())
    ruhig = bool(s.letzte_ausgabe) and time.monotonic() - s.letzte_ausgabe > 3.0
    s.write(MARKE.encode())
    t1 = time.monotonic()
    while time.monotonic() - t1 < 6 and MARKE not in aus()[vorher:]:
        time.sleep(0.2)
    def glatt(t: str) -> str:  # TUIs zeichnen mit Cursorsprüngen: Steuerzeichen und Zwischenräume weg, die Zeichenfolge bleibt
        return re.sub(r"[^A-Za-z0-9]", "", re.sub(r"\x1b\[[0-9;?>]*[ -/]*[@-~]|\x1b\][^\x07]*\x07|\x1b[()][A-Z0-9]", "", t))
    angekommen = MARKE in glatt(aus()[vorher:])
    ende = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07", "", aus())[-300:].replace("\n", " ")
    l.shutdown()
    time.sleep(2)
    return {"programm": programm, "lief": s.state in ("running", "exited"), "ausgabe_bytes": vorher, "ruhig": ruhig, "marke_im_tui": angekommen, "zuletzt_sichtbar": ende[-160:]}


for p in sys.argv[1:]:
    print(json.dumps(lauf(p), ensure_ascii=False), flush=True)
