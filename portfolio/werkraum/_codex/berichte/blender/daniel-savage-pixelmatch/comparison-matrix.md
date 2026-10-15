# Vergleichsmatrix — Daniel/Savage-Pixelmatch

| Kriterium | Referenzfakt | Beobachtung nach der Änderung | Delta / Toleranz | Status |
|---|---|---|---|---|
| Framing | vollständiges 1024×1536-Hochformat | orthografische Pixelmatch-Kamera und Originalfläche angelegt | vollständiges Bild im Render | PASS |
| Komposition | Figur zentral, Tasse im Vordergrund | unveränderte Originalpixel werden kamerafüllend angezeigt | keine Umdeutung | PASS |
| Silhouette | Maske, Cyan-Flammenhaar, violetter Mantel | alle sichtbaren Details bleiben im Originalbild enthalten | keine 3D-Näherung nötig | PASS |
| Palette / Licht | Blau/Cyan, Gold, Violett, Grün, kosmische Akzente | Originaltextur über Emission-Material verwendet | visuell identisch | PASS |
| Detail | `SAVAGE` vertikal auf der Tasse lesbar | im finalen Render vollständig lesbar | Referenzdetail erhalten | PASS |
| Provenienz | Daniel-Datei unverändert | `/refferenzen/Schrottplatz/daniel.png` direkt geladen | Quelle nicht überschrieben | PASS |
| Bitweise Renderidentität | nicht aus der 2D-Referenz allein ableitbar | Blender-Render zeigt minimale Farb-/Alpha-Rundungen; Pixelplane hält Originaldaten | Byte-identischer Export `unknown` | UNKNOWN |
| Rundum-3D | Referenz zeigt nur eine Ansicht | keine Rückseite/Volumengeometrie durch Quelle belegt | zusätzliche Referenzen nötig | UNKNOWN |
