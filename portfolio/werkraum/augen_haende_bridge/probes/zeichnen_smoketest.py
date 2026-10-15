"""Wine/Windows: echte Zeichenfenster: Pixel-Alpha-Fenster, Editor mit Mausereignissen, Werkzeugleiste, Anzeige der Bildschirmobjekte."""
import json
import os
import sys

if os.name != "nt":
    print(json.dumps({"status": "unavailable"}))
    sys.exit(0)

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.arbeitsflaechen_anzeige import ArbeitsflaechenAnzeige
from augen_haende_bridge.koerper.editor_logik import Editor
from augen_haende_bridge.koerper.fenster import Anwendung
from augen_haende_bridge.koerper.komposition import Arbeitsflaechen
from augen_haende_bridge.koerper.objekte import Dokument, Objekt
from augen_haende_bridge.koerper.pixel_fenster import PixelFenster
from augen_haende_bridge.koerper.zeichen_fenster import WerkzeugLeiste, ZeichenFenster

gui = Anwendung()
dok = Dokument("t")
ref = {}
ed = Editor(dok, lambda: ref["f"].clientgroesse(), bei_aenderung=lambda: ref["f"].neu(), agenten=lambda: [("A", "Codex")])
f = ZeichenFenster((100, 100, 500, 400), ed)
ref["f"] = f
f.zeige(aktivieren=False)
leiste = WerkzeugLeiste(100, 20, ed)
leiste.zeige(aktivieren=False)
gui.pumpen(150)
ergebnis = {"fenster_groesse": f.clientgroesse(), "pixel_angenommen": f.angenommen, "leck_schutz": f.leck_schutz,
            "leiste_groesse": leiste.clientgroesse()}
# Palette: Werkzeug Rechteck waehlen (Klick auf den Knopf)
a, b, c, d = leiste._rechtecke["w:rechteck"]
leiste.bei_maus_runter((a + c) // 2, (b + d) // 2, 1)
leiste.bei_maus_hoch((a + c) // 2, (b + d) // 2, 0)
ergebnis["werkzeug"] = ed.werkzeug
# 0.9.1: Stil, Deckkraft, Radierer ueber Knoepfe der Leiste
for schluessel in ("t:fett", "d:50", "w:radierer"):
    a, b, c, d = leiste._rechtecke[schluessel]
    leiste.bei_maus_runter((a + c) // 2, (b + d) // 2, 1)
    leiste.bei_maus_hoch((a + c) // 2, (b + d) // 2, 0)
ergebnis["neu_in_leiste"] = {"fett": ed.fett, "deckkraft": ed.deckkraft, "werkzeug": ed.werkzeug}
a, b, c, d = leiste._rechtecke["w:rechteck"]
leiste.bei_maus_runter((a + c) // 2, (b + d) // 2, 1)
leiste.bei_maus_hoch((a + c) // 2, (b + d) // 2, 0)
ed.deckkraft_setzen(100)
ed.stil_umschalten("fett")
# Rechteck ziehen ueber die Fensterereignisse
f.bei_maus_runter(40, 40, 1)
for i in range(1, 6):
    f.bei_maus_bewegt(40 + 40 * i, 40 + 20 * i, 1)
f.bei_maus_hoch(240, 140, 0)
ergebnis["objekte"] = [o.art for o in dok.sortiert()]
gui.pumpen(100)
bild = f.letztes_bild
ergebnis["editor_hat_pixel"] = bool(bild is not None and bild.getbbox())
ergebnis["rand_pixel_alpha"] = bild.getpixel((1, 1))[3] if bild is not None else None
ergebnis["mitte_alpha"] = bild.getpixel((200, 200))[3] if bild is not None else None  # fast durchsichtig, aber nicht 0 (faengt Klicks)
# Strg+Z ueber die Tastenbehandlung
w.user32.keybd_event(w.VK_CONTROL, 0, 0, 0)
f.bei_taste(ord("Z"), 0, False)
w.user32.keybd_event(w.VK_CONTROL, 0, 2, 0)
ergebnis["nach_rueckgaengig"] = len(dok.objekte)
# Anzeige der Bildschirmobjekte
dok.hinzufuegen(Objekt("s", "kreis", [(0.2, 0.2), (0.8, 0.8)], bildschirm=True, farbe="#FF0000", staerke=6))
arbeit = Arbeitsflaechen()
arbeit.dokumente["desktop"] = dok
anzeige = ArbeitsflaechenAnzeige(arbeit, lambda r: PixelFenster(r[0], r[1], r[2] - r[0], r[3] - r[1], titel="Objekte"), lambda k: (True, False, None),
                                 lambda: (600, 100, 900, 300))
anzeige.tick()
gui.pumpen(100)
fenster = anzeige.fenster.get("desktop")
ergebnis["anzeige_da"] = fenster is not None
ergebnis["anzeige_groesse"] = fenster.clientgroesse() if fenster else None
ergebnis["anzeige_angenommen"] = bool(fenster and fenster.angenommen)
ergebnis["anzeige_durchklickbar"] = bool(fenster and (w.user32.GetWindowLongPtrW(fenster.hwnd, w.GWL_EXSTYLE) & w.WS_EX_TRANSPARENT)) if hasattr(w, "GWL_EXSTYLE") else None
print(json.dumps({"status": "ok", **ergebnis}))
for x in (leiste, f, *anzeige.fenster.values()):
    x.schliessen()
