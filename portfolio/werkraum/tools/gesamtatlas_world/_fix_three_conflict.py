from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")
old = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n</head>'
n = text.count(old)
print("anchor:", n)
if n != 1:
    raise SystemExit("abbruch")
# Eigene Three.js-Kopie entfernen -- kollidierte mit der von 3d-force-graph
# mitgelieferten Instanz (sichtbar am Fehler "ForceGraph3D is not defined").
# globusRendern() prueft zur Laufzeit selbst, ob THREE schon global verfuegbar
# ist (siehe naechster Patch), sonst laedt es nichts falsch Doppeltes mehr.
text = text.replace(old, "</head>", 1)
APP.write_text(text, encoding="utf-8")
print("DOPPELTE THREE.JS-KOPIE ENTFERNT")
