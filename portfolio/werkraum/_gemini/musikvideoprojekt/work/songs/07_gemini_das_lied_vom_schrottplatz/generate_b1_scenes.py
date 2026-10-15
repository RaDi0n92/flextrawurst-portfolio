#!/usr/bin/env python3
import json
import os
import time
from huggingface_hub import InferenceClient

token = "[GESCHWAERZT]"
client = InferenceClient(token=token)

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
thron_json = os.path.join(song_dir, "b1_thron_scenes.json")
out_dir = os.path.join(song_dir, "frames", "b1")
os.makedirs(out_dir, exist_ok=True)

with open(thron_json) as f:
    scenes = json.load(f)

print(f"Starte Generierung von {len(scenes)} Block 1 Thron-Szenen mit FLUX.1-schnell...")
for idx, sc in enumerate(scenes):
    fpath = os.path.join(out_dir, f"{sc['id']}.jpg")
    if os.path.exists(fpath) and os.path.getsize(fpath) > 10000:
        print(f"[{idx+1}/{len(scenes)}] Bereits vorhanden: {fpath}")
        continue
    
    print(f"[{idx+1}/{len(scenes)}] Generiere {sc['id']} (Thron-Wort: {sc['thron_wort']})...")
    success = False
    for attempt in range(3):
        try:
            img = client.text_to_image(sc["prompt"], model="black-forest-labs/FLUX.1-schnell")
            img.save(fpath, quality=95)
            print(f"  -> Gespeichert ({os.path.getsize(fpath)} Bytes): {fpath}")
            success = True
            break
        except Exception as e:
            print(f"  -> Versuch {attempt+1} fehlgeschlagen: {e}")
            time.sleep(2)
    if not success:
        print(f"FEHLER bei {sc['id']}")
        exit(1)

print("\n✓ Alle 12 Szenen erfolgreich generiert!")
