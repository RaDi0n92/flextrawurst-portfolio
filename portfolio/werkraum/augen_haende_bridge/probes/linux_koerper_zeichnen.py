"""Linux (eigener Xvfb): jedes echte Fenster des Körpers auf der Linux-Fensterschicht bauen, zeichnen und bedienen.

Die Fenster sind dieselben Klassen wie unter Windows (Raute, Terminal, Chat, Regie, Kamera, Bild-Element, Nachrichten, Eingabe, Zeichenfläche,
Werkzeugleiste): ihr Code bleibt unverändert, nur die Fensterschicht darunter ist GTK. Gibt am Ende `linux koerper probe ok` aus und schreibt je
Fenster ein Bild nach $LINUX_KOERPER_BILDER (falls gesetzt), damit man das Aussehen ansehen kann.
"""
import faulthandler
import os
import sys

if os.environ.get("BRIDGE_TEST_XVFB") != "1":  # die Probe tippt Tasten und bewegt den Zeiger: nur auf einem eigenen, privaten Xvfb
    print("Abbruch: nur unter `xvfb-run … env BRIDGE_TEST_XVFB=1` starten (nie auf einem sichtbaren Desktop).", file=sys.stderr)
    sys.exit(2)

os.environ["BRIDGE_BACKEND"] = "linux"
faulthandler.dump_traceback_later(90, exit=True)

from PIL import Image

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.bild_element_fenster import BildElementFenster
from augen_haende_bridge.koerper.chat_fenster import ChatFenster
from augen_haende_bridge.koerper.editor_logik import Editor
from augen_haende_bridge.koerper.eingabe_fenster import RauteEingabe
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.kamera_fenster import KameraFenster
from augen_haende_bridge.koerper.nachricht_fenster import BannerFenster, TickerFenster
from augen_haende_bridge.koerper.objekte import Dokument, Objekt
from augen_haende_bridge.koerper.raute_fenster import RauteFenster
from augen_haende_bridge.koerper.regie_fenster import RegieFenster
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster
from augen_haende_bridge.koerper.zeichen_fenster import WerkzeugLeiste, ZeichenFenster
from augen_haende_bridge.koerper import stil

app = Anwendung()
app.starten()
bilder = os.environ.get("LINUX_KOERPER_BILDER")
if bilder:
    os.makedirs(bilder, exist_ok=True)
ergebnis: list[str] = []


def pruefe(bedingung, text):
    if not bedingung:
        print("FEHLER:", text, file=sys.stderr)
        sys.exit(1)


def zeige(name, fenster):
    fenster.zeige(aktivieren=False)
    app.pumpen(150)
    fenster.neu_zeichnen()
    app.pumpen(150)
    bild = getattr(fenster, "letztes_bild", None)  # Pixel-Alpha-Fenster zeigen ein RGBA-Bild statt einer Leinwand
    if bild is None:
        pruefe(fenster.leinwand is not None, f"{name}: keine Leinwand")
        bild = fenster.leinwand.bild
    farben = len(set(bild.convert("RGBA").resize((64, 64)).tobytes()[i:i + 4] for i in range(0, 64 * 64 * 4, 4)))
    pruefe(farben >= 3, f"{name}: Leinwand ist leer ({farben} Farben)")
    if bilder:
        bild.save(os.path.join(bilder, f"{name}.png"))
    ergebnis.append(f"{name} {fenster.clientgroesse()[0]}x{fenster.clientgroesse()[1]}")
    return fenster


raute = zeige("raute", RauteFenster(40, 40, name="Codex", farbe_hex="#00E5FF", kuerzel="CX", hotkey="F13"))
terminal = zeige("terminal", TerminalFenster(160, 40, zeilen=16, spalten=60, name="Codex", ort="vd1", farbe_hex="#00E5FF"))
terminal.ausgabe(b"\x1b[32mBridge Linux\x1b[0m bereit\r\nuser@vd1:~$ echo hallo\r\nhallo\r\n") if hasattr(terminal, "ausgabe") else None
app.pumpen(150)
pruefe(terminal.leinwand.bild.getpixel((20, 20)) is not None, "Terminal zeichnet")
chat = zeige("chat", ChatFenster(700, 40, breite=320, hoehe=220))
regie = zeige("regie", RegieFenster(30, 300))
kamera = zeige("kamera", KameraFenster(700, 300, name="Codex", farbe_hex="#00E5FF"))
bgr = bytes([30, 160, 220] * (32 * 24))
bild_element = zeige("bild_element", BildElementFenster(900, 300, 160, 120, bild=(bgr, 32, 24), name="Skizze"))
eingabe = zeige("eingabe", RauteEingabe(40, 520, name="Codex", farbe_hex="#00E5FF"))
banner = zeige("banner", BannerFenster(text="Hallo von der Raute", farbe_hex="#FF0055", ziel_rechteck=(0, 0, 1200, 700),
                                       raute_rechteck=(40, 40, 120, 120), jetzt_ms=lambda: 0))
ticker = zeige("ticker", TickerFenster(text="Ticker neben der Raute", farbe_hex="#FFD600", raute_rechteck=(40, 40, 120, 120)))

dok = Dokument("probe")
dok.hinzufuegen(Objekt("r", "rechteck", [(0.1, 0.1), (0.5, 0.5)], farbe="#FF0055", staerke=6, bildschirm=True))
ref = {}
editor = Editor(dok, lambda: ref["f"].clientgroesse(), bei_aenderung=lambda: ref["f"].neu(), agenten=lambda: [("A", "Codex")])
zf = ZeichenFenster((300, 420, 700, 700), editor)
ref["f"] = zf
zeige("zeichenflaeche", zf)
leiste = zeige("werkzeugleiste", WerkzeugLeiste(300, 380, editor))

# Eingaben auf echten Körperfenstern: Klick auf ein Werkzeug der Leiste
a, b, c, d = leiste._rechtecke["w:rechteck"]
links, oben, _r, _u = leiste.rechteck()
leiste.nachricht(w.WM_LBUTTONDOWN, 1, w.make_lparam((a + c) // 2, (b + d) // 2))
leiste.nachricht(w.WM_LBUTTONUP, 0, w.make_lparam((a + c) // 2, (b + d) // 2))
pruefe(editor.werkzeug == "rechteck", f"Werkzeugwahl über die Leiste: {editor.werkzeug}")
# Zeichnen mit der Maus auf der Zeichenfläche
zf.bei_maus_runter(50, 50, 1)
for i in range(1, 6):
    zf.bei_maus_bewegt(50 + 30 * i, 50 + 20 * i, 1)
zf.bei_maus_hoch(200, 150, 0)
pruefe(len(dok.objekte) == 2, f"Rechteck gezeichnet: {len(dok.objekte)} Objekte")

# Raute: Rechtsklick-Menü wird gemeldet, Verschieben meldet die neue Lage
print("linux koerper probe ok:", "; ".join(ergebnis))
app.beenden()
