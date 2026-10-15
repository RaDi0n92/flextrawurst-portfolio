"""Läuft innerhalb von `dbus-run-session` unter Xvfb: startet den AT-SPI-Bus und das GTK-Programm und führt den gewünschten Fall aus. Ausgabe: eine JSON-Zeile."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from augen_haende_bridge.koerper import uia

fall = sys.argv[1]
os.environ["GTK_MODULES"] = "gail:atk-bridge"
os.environ.pop("NO_AT_BRIDGE", None)
bus = subprocess.Popen(["/usr/libexec/at-spi-bus-launcher", "--launch-immediately"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
reg = subprocess.Popen(["/usr/libexec/at-spi2-registryd", "--use-gnome-session"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
stand = Path(tempfile.mkdtemp()) / "stand.txt"
app = None
ergebnis: dict = {}


def lies_stand() -> str:
    try:
        return stand.read_text(encoding="utf-8")
    except OSError:
        return ""


try:
    q = uia.AtspiQuelle()
    ergebnis["verfuegbar"] = q.verfuegbar()
    if fall == "ohne_baum":
        # ein reines X11-Fenster ohne jede Bedienungshilfe
        from Xlib import X, display

        d = display.Display()
        f = d.screen().root.create_window(10, 10, 200, 100, 0, d.screen().root_depth, X.InputOutput, X.CopyFromParent, background_pixel=0x336699)
        f.set_wm_name("NurFlaeche")
        f.map()
        d.sync()
        time.sleep(1.0)
        ergebnis["anwendungen"] = [n for n, _ in q.anwendungen()]
        b = q.baum("NurFlaeche")
        ergebnis["baum"] = {"status": b.status, "grund": b.grund, "wurzel": b.wurzel is not None}
    else:
        app = subprocess.Popen([sys.executable, str(Path(__file__).parent / "helfer_atspi_app.py"), str(stand)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ende = time.monotonic() + 20
        name = None
        while time.monotonic() < ende and name is None:
            time.sleep(0.5)
            name = next((n for n, p in q.anwendungen() if p == app.pid), None)
        ergebnis["anwendung_gefunden"] = name is not None
        b = q.baum(app.pid)
        ergebnis["status"], ergebnis["anzahl"] = b.status, b.anzahl
        w = b.wurzel
        knopf = w.finde("button", "Zählen") if w else None
        feld = w.finde("text") if w else None
        etikett = w.finde("label", "Beschriftung eins") if w else None
        ergebnis["rollen"] = sorted({k.rolle for k in w.alle()}) if w else []
        ergebnis["knopf"] = None if knopf is None else {"rect": knopf.rect, "faehig": knopf.faehigkeiten}
        ergebnis["feld"] = None if feld is None else {"rect": feld.rect, "faehig": feld.faehigkeiten}
        ergebnis["etikett"] = None if etikett is None else {"rect": etikett.rect, "faehig": etikett.faehigkeiten}
        if fall == "bedienen":
            ergebnis["klick_knopf"] = [q.klick(knopf) for _ in range(2)]
            time.sleep(0.6)
            ergebnis["nach_klick"] = lies_stand()
            ergebnis["text_setzen"] = q.text_setzen(feld, "Grüße 🌍")
            time.sleep(0.6)
            ergebnis["nach_text"] = lies_stand()
            # ein Knoten ohne diese Fähigkeit löst nichts aus
            ergebnis["klick_etikett"] = q.klick(etikett)
            ergebnis["text_etikett"] = q.text_setzen(etikett, "x")
            ergebnis["klick_feld"] = q.klick(feld)
            time.sleep(0.4)
            ergebnis["nach_verweigert"] = lies_stand()
finally:
    for p in (app, reg, bus):
        if p is not None:
            p.terminate()
print(json.dumps(ergebnis, ensure_ascii=False))
