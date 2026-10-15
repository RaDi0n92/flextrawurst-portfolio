"""Läuft in `dbus-run-session` unter Xvfb: AT-SPI-Bus, ein echtes GTK-Programm, dann der gewünschte WorldDOM-Fall. Ausgabe: eine JSON-Zeile."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from augen_haende_bridge.koerper import uia, weltdom as wd
from augen_haende_bridge.koerper.weltdom_aktion import AktionsDienst

fall = sys.argv[1]
os.environ["GTK_MODULES"] = "gail:atk-bridge"
os.environ.pop("NO_AT_BRIDGE", None)
bus = subprocess.Popen(["/usr/libexec/at-spi-bus-launcher", "--launch-immediately"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
reg = subprocess.Popen(["/usr/libexec/at-spi2-registryd", "--use-gnome-session"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
stand = Path(tempfile.mkdtemp()) / "stand.txt"
app = subprocess.Popen([sys.executable, str(Path(__file__).parent / "helfer_atspi_app.py"), str(stand)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ZIEL = "kde1:window:4242"
ergebnis: dict = {}


def lies() -> str:
    try:
        return stand.read_text(encoding="utf-8")
    except OSError:
        return ""


try:
    q = uia.AtspiQuelle()
    ende = time.monotonic() + 20
    while time.monotonic() < ende and not any(p == app.pid for _, p in q.anwendungen()):
        time.sleep(0.4)
    jetzt = [int(time.time() * 1000)]
    welt = wd.WeltDom()
    baum = q.baum(app.pid)
    knoten = wd.aus_ui_baum(ZIEL, baum.wurzel, "atspi", app.pid, jetzt[0])
    welt.ersetze(ZIEL, "real", "atspi", knoten)
    ergebnis["knoten"] = [k.zu_dict(jetzt[0]) for k in welt.liste(ZIEL)]
    dienst = AktionsDienst(welt, ui_quelle=lambda z: (q, app.pid), jetzt_ms=lambda: jetzt[0], schlafen=time.sleep)
    knopf = next((k for k in knoten if k.rolle == "button"), None)
    feld = next((k for k in knoten if k.rolle == "text"), None)
    etikett = next((k for k in knoten if k.rolle == "label"), None)
    if fall == "aktion":
        r1 = dienst.ausfuehren(ZIEL, knopf.id, "klick", erwartung=None)
        time.sleep(0.5)
        ergebnis["klick"] = {"status": r1["status"], "methode": r1["methode"], "ruecklese": r1["ruecklese"], "stand": lies()}
        r2 = dienst.ausfuehren(ZIEL, feld.id, "text_setzen", "Grüße 🌍")
        time.sleep(0.5)
        ergebnis["text"] = {"status": r2["status"], "ruecklese": r2["ruecklese"], "stand": lies()}
        r3 = dienst.ausfuehren(ZIEL, etikett.id, "klick")
        r4 = dienst.ausfuehren(ZIEL, etikett.id, "text_setzen", "x")
        r5 = dienst.ausfuehren(ZIEL, etikett.id, "lesen")
        ergebnis["etikett"] = {"klick": [r3["status"], r3["grund"]], "text": [r4["status"], r4["grund"]], "lesen": [r5["status"], r5.get("gelesen")], "stand": lies()}
        # ein Knoten, den es nicht mehr gibt (Anker zeigt auf anderen Namen), löst nichts aus
        falsch = wd.Knoten("rea-atspi-weg", ZIEL, "real", "atspi", "button", "Gibt es nicht", "", None, 1.0, jetzt[0], 5000, None, ("klick",), "atspi",
                           {"pid": app.pid, "pfad": [9, 9], "rolle": "button", "name": "Gibt es nicht"})
        welt.ersetze(ZIEL, "real", "atspi", knoten + [falsch])
        vorher = lies()
        r6 = dienst.ausfuehren(ZIEL, falsch.id, "klick")
        ergebnis["weg"] = {"status": r6["status"], "grund": r6["grund"], "stand_gleich": lies() == vorher}
        jetzt[0] += 60_000  # alles veraltet
        r7 = dienst.ausfuehren(ZIEL, knopf.id, "klick")
        ergebnis["veraltet"] = {"status": r7["status"], "grund": r7["grund"], "stand_gleich": lies() == vorher}
        # zwei gleichnamige Knoten: mehrdeutig
        zwilling = wd.Knoten("rea-atspi-zwilling", ZIEL, "real", "atspi", "button", knopf.name, "", None, 1.0, jetzt[0], 5000, None, ("klick",), "atspi",
                             {"pid": app.pid, "pfad": [9, 9], "rolle": "button", "name": knopf.name})
        # (nur ein echter Knopf im Programm: der Zwilling mit falschem Pfad findet ihn über Rolle und Name, eindeutig)
        welt.ersetze(ZIEL, "real", "atspi", [zwilling])
        r8 = dienst.ausfuehren(ZIEL, zwilling.id, "klick")
        time.sleep(0.5)
        ergebnis["umgefunden"] = {"status": r8["status"], "stand": lies()}
finally:
    for p in (app, reg, bus):
        p.terminate()
print(json.dumps(ergebnis, ensure_ascii=False))
