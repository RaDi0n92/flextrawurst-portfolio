from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
NEU = Path("/root/werkraum/tools/gesamtatlas_world/_globus_globegl.txt").read_text(encoding="utf-8")

text = APP.read_text(encoding="utf-8")
start = "function globusLegendeZeichnen(daten) {"
ende_marker = "  globusState = { scene, camera, renderer };\n}\n"

si = text.find(start)
ei = text.find(ende_marker)
if si == -1 or ei == -1:
    raise SystemExit(f"abbruch si={si} ei={ei}")
ei_end = ei + len(ende_marker)
print("alter Block Laenge:", ei_end - si)

text = text[:si] + NEU.rstrip("\n") + "\n\n" + text[ei_end:]
APP.write_text(text, encoding="utf-8")
print("GLOBUS AUF globe.gl UMGESTELLT")
