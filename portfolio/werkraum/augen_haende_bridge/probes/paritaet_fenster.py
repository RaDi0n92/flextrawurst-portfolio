"""Windows-Fassung und Linux-Fassung zeichnen dieselben Fenster: dieses Programm läuft in beiden (unter Wine mit GDI, unter Linux mit GTK/Pillow), baut dieselben Fenster mit
denselben Eingaben und schreibt je Fenster ein PNG und die Größe in einen Ordner, damit beide verglichen werden können.

Aufruf: `paritaet_fenster.py <Ausgabeordner>`; die Umgebung wählt die Fassung (unter Linux BRIDGE_BACKEND=linux und BRIDGE_TEST_XVFB=1)."""
import json
import os
import sys

if os.name != "nt" and os.environ.get("BRIDGE_TEST_XVFB") != "1":
    print("Abbruch: unter Linux nur auf einem eigenen Xvfb (BRIDGE_TEST_XVFB=1)", file=sys.stderr)
    sys.exit(2)

ziel = sys.argv[1]
os.makedirs(ziel, exist_ok=True)

from PIL import Image

from augen_haende_bridge.koerper.bild_element_fenster import BildElementFenster
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.editor_logik import Editor
from augen_haende_bridge.koerper.eingabe_fenster import RauteEingabe
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.kamera_fenster import KameraFenster
from augen_haende_bridge.koerper.objekte import Dokument
from augen_haende_bridge.koerper.raute_fenster import RauteFenster
from augen_haende_bridge.koerper.regie_fenster import RegieFenster
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster
from augen_haende_bridge.koerper.zeichen_fenster import WerkzeugLeiste

app = Anwendung()
app.starten()
groessen = {}


def festhalten(name, fenster):
    fenster.zeige(aktivieren=False)
    app.pumpen(150)
    leinwand = fenster.leinwand
    fenster.zeichnen(leinwand)  # frisch zeichnen, unabhängig davon, wann das System das Neuzeichnen verlangt hat
    breite, hoehe = leinwand.breite, leinwand.hoehe
    bgra = leinwand.bgra()
    Image.frombuffer("RGBA", (breite, hoehe), bgra, "raw", "BGRA", 0, 1).convert("RGB").save(os.path.join(ziel, f"{name}.png"))
    groessen[name] = [breite, hoehe]


festhalten("raute", RauteFenster(40, 40, name="Codex", farbe_hex="#00E5FF", kuerzel="CX", hotkey="F13"))
terminal = TerminalFenster(160, 40, zeilen=16, spalten=60, name="Codex", ort="vd1", farbe_hex="#00E5FF")
terminal.ausgabe(b"\x1b[32mBridge\x1b[0m bereit\r\nuser@vd1:~$ ls\r\nkarte  notizen  spiegel\r\n")
festhalten("terminal", terminal)
festhalten("chat", ChatFenster(700, 40, breite=320, hoehe=220))
festhalten("regie", RegieFenster(30, 300))
festhalten("kamera", KameraFenster(700, 300, name="Codex", farbe_hex="#00E5FF"))
festhalten("bild_element", BildElementFenster(900, 300, 160, 120, bild=(bytes([30, 160, 220] * (32 * 24)), 32, 24), name="Skizze"))
festhalten("eingabe", RauteEingabe(40, 520, name="Codex", farbe_hex="#00E5FF"))
editor = Editor(Dokument("p"), lambda: (600, 400))
festhalten("werkzeugleiste", WerkzeugLeiste(300, 380, editor))
with open(os.path.join(ziel, "groessen.json"), "w") as datei:
    json.dump(groessen, datei)
print("paritaet probe ok", len(groessen))
app.beenden()
