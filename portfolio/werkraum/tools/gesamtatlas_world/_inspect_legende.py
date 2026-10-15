from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")

anchors_check = [
    '  <div id="legende" class="panel">',
    '  const kugelGeo = new THREE.SphereGeometry(2.4, 32, 24);',
    'let globusGeladen = false;',
]
for a in anchors_check:
    n = text.count(a)
    print(repr(a[:40]), ":", n)

print("--- suche legende block genauer ---")
idx = text.find('id="legende"')
print(text[idx-10:idx+300] if idx >= 0 else "NICHT GEFUNDEN")
