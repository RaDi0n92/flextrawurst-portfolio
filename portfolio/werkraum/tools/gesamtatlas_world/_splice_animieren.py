from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
NEU = Path("/root/werkraum/tools/gesamtatlas_world/_globus_animieren_v2.txt").read_text(encoding="utf-8")

text = APP.read_text(encoding="utf-8")
start = "  function animieren() {"
ende = "  animieren();\n"

si = text.find(start)
ei = text.find(ende)
if si == -1 or ei == -1:
    raise SystemExit(f"abbruch si={si} ei={ei}")
ei_end = ei + len(ende)
print("alter Block Laenge:", ei_end - si)

text = text[:si] + NEU.rstrip("\n") + "\n" + text[ei_end:]
APP.write_text(text, encoding="utf-8")
print("ANIMIEREN ERSETZT")
