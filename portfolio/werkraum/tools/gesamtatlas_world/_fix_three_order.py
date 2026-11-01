from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")
old = '<script src="[Adresse entfernt]"></script>'
n = text.count(old)
print("anchor:", n)
if n != 1:
    raise SystemExit("abbruch")
text = text.replace(
    old,
    old + '\n<script src="[Adresse entfernt]"></script>',
    1,
)
APP.write_text(text, encoding="utf-8")
print("THREE.JS NACH 3d-force-graph GELADEN")
