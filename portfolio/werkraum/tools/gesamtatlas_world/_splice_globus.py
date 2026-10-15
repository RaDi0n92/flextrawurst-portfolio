from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
NEUER_JS = Path("/root/werkraum/tools/gesamtatlas_world/_globus_js_v2.txt").read_text(encoding="utf-8")

text = APP.read_text(encoding="utf-8")
start_marker = "function globusRendern(daten) {"
end_marker = "  globusState = { scene, camera, renderer };\n}"

si = text.find(start_marker)
ei = text.find(end_marker)
if si == -1 or ei == -1:
    raise SystemExit(f"abbruch: marker nicht gefunden si={si} ei={ei}")
ei_end = ei + len(end_marker)

alt_block = text[si:ei_end]
print("alter Block Laenge:", len(alt_block))

text = text[:si] + NEUER_JS.strip() + text[ei_end:]
APP.write_text(text, encoding="utf-8")
print("GLOBUSRENDERN ERSETZT")
