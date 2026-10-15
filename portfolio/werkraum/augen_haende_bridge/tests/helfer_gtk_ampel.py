"""Ein echtes Ampel-Fenster (GTK-Fensterschicht) für den Bedientest: schreibt Klicks, Menüaufrufe und die Fensterlage in eine JSON-Datei."""
import json
import os
import sys

os.environ["BRIDGE_BACKEND"] = "linux"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from augen_haende_bridge.koerper import ampel
from augen_haende_bridge.koerper.fenster import Anwendung  # noqa: E402  (nach BRIDGE_BACKEND=linux ist das die GTK-Schicht)
from augen_haende_bridge.koerper.ampel_fenster import AmpelFenster  # noqa: E402

stand_datei = sys.argv[1]
stand = {"aktionen": [], "menues": []}


def schreibe() -> None:
    f = fenster.rechteck()
    stand["rechteck"] = list(f)
    stand["lampen"] = len(fenster.lampen)
    with open(stand_datei, "w", encoding="utf-8") as datei:
        json.dump(stand, datei)


def daten(name: str) -> list:
    return [ampel.Lampe("bild", "Bilder kommen frisch an", ampel.ROT, "KEIN BILD", blinkt=False, behebe="strom_neu"),
            ampel.Lampe("hand", "Hände insgesamt", ampel.GRUEN, "bereit"),
            ampel.Lampe("bind", "Ziel des Agenten", ampel.GRUEN, "ganzer Desktop")]


def aktion(agent: str, name: str) -> None:
    stand["aktionen"].append([agent, name])
    schreibe()


def menue(agent: str, x: int, y: int) -> None:
    stand["menues"].append([agent, x, y])
    schreibe()


fenster = AmpelFenster(100, 100, name="Testagent", daten=daten, aktion=aktion, menue=menue, farbe=lambda: "#00c0ff")
fenster.zeige(aktivieren=False)

# Durchklick wie im Körper: das Fenster ist klickdurchlässig, solange die Bedientaste nicht gehalten wird. Die Taste liefert hier eine Datei
# (der Test setzt sie), im Körper ist es Strg+Alt über XQueryKeymap.
from augen_haende_bridge.koerper.durchklick import DurchklickVerwalter  # noqa: E402

taste_datei = sys.argv[2] if len(sys.argv) > 2 else None
durchklick = None
if taste_datei:
    def taste_gehalten() -> bool:
        try:
            return open(taste_datei, encoding="utf-8").read().strip() == "1"
        except OSError:
            return False

    durchklick = DurchklickVerwalter(strg=taste_gehalten, takt_s=0.05)
    durchklick.registrieren("ampel:test", fenster, True)
from gi.repository import GLib  # noqa: E402

GLib.timeout_add(200, lambda: (schreibe(), True)[1])
anwendung = Anwendung()
anwendung.starten()
if durchklick is not None:
    durchklick.starten(anwendung.post)

anwendung.schleife()
