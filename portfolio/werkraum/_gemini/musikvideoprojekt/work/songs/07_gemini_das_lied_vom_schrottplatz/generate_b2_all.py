#!/usr/bin/env python3
import json
import os
import time
import io
import urllib.parse
import urllib.request
from PIL import Image

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
thron_json = os.path.join(song_dir, "b2_thron_scenes.json")
out_dir = os.path.join(song_dir, "frames", "b2")
os.makedirs(out_dir, exist_ok=True)

with open(thron_json) as f:
    scenes = json.load(f)

print(f"Starte Generierung der verbleibenden Block 2 Szenen ({len(scenes)} gesamt)...")

for idx, sc in enumerate(scenes):
    fpath = os.path.join(out_dir, f"{sc['id']}.jpg")
    if os.path.exists(fpath) and os.path.getsize(fpath) > 30000:
        print(f"[{idx+1}/{len(scenes)}] Bereits vorhanden: {sc['id']} ({os.path.getsize(fpath)} Bytes)")
        continue
    
    print(f"[{idx+1}/{len(scenes)}] Generiere {sc['id']} (Thron-Wort: {sc['thron_wort']})...")
    encoded = urllib.parse.quote(sc["prompt"])
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux"
    
    success = False
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=50) as resp:
                data = resp.read()
            
            img = Image.open(io.BytesIO(data))
            # Wasserzeichen unten sauber abschneiden (untere 35 Pixel)
            w, h = img.size
            cropped = img.crop((0, 0, w, h - 35))
            cropped.save(fpath, quality=95)
            print(f"  -> Gespeichert ({os.path.getsize(fpath)} Bytes, {cropped.size}): {fpath}")
            success = True
            time.sleep(1)
            break
        except Exception as e:
            print(f"  -> Versuch {attempt+1} fehlgeschlagen: {e}")
            time.sleep(3)
            
    if not success:
        print(f"FEHLER bei {sc['id']}")
        exit(1)

print("\n✓ Alle 12 Szenen fuer Block 2 erfolgreich generiert!")
