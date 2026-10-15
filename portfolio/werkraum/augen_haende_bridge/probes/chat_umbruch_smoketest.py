"""Wine/Windows: echtes ChatFenster mit langer Nachricht: Umbruch mit echter Schriftmessung, nichts breiter als das Fenster, Bildlauf."""
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper.chat_fenster import PAD, ChatFenster
from augen_haende_bridge.koerper.fenster import Anwendung

gui = Anwendung()
f = ChatFenster(100, 100, breite=260, hoehe=200)
text = "Das ist eine sehr lange Nachricht von einem Agenten, die in einem kleinen Chatfenster nicht in eine Zeile passt und deshalb umbrechen muss. " * 3
f.empfangen("Claude", text)
f.empfangen("Claude", "kurz")
f.empfangen("Claude", "x" * 120)
gui.pumpen(200)
zeilen = f.anzeigezeilen()
breite, _ = f.clientgroesse()
breiten = [(f._messen_kopf(k + " ") if k else 0) + f._messen(t) for _, k, t in zeilen]
f.bei_rad(120, 100 + PAD, 100 + 60, 0)
f.bei_rad(120, 100 + PAD, 100 + 60, 0)
gui.pumpen(100)
ergebnis = {"zeilen": len(zeilen), "max_breite": max(breiten), "fenster": breite, "kopf": zeilen[0][1], "erste": zeilen[0][2], "zweite": zeilen[1][2], "zeilenhoehe": f._zeilenhoehe(),
            "versatz": f._bildlauf_versatz}
griff = f._griff()
f.springen(True)
ergebnis["griff"] = griff
ergebnis["versatz_nach_sprung"] = f._bildlauf_versatz
ergebnis["anfaenge"] = f._umbruch_anfaenge[:4]
f.neu_zeichnen()
gui.pumpen(100)
f.verschiebe(100, 100, 600, 200)
gui.pumpen(100)
ergebnis["zeilen_breit"] = len(f.anzeigezeilen())
f.schliessen()
print(json.dumps({"status": "ok", **ergebnis}, ensure_ascii=False))
