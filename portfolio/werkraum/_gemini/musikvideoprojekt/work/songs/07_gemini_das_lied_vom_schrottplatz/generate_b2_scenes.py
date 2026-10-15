#!/usr/bin/env python3
import json
import os
import time
from huggingface_hub import InferenceClient

client = InferenceClient()

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
thron_json = os.path.join(song_dir, "b2_thron_scenes.json")
out_dir = os.path.join(song_dir, "frames", "b2")
os.makedirs(out_dir, exist_ok=True)

with open(thron_json) as f:
    scenes = json.load(f)

print(f"Starte Generierung von {len(scenes)} Block 2 Thron-Szenen (Underground Comic Noir) via FLUX.1-schnell...")
for idx, sc in enumerate(scenes):
    fpath = os.path.join(out_dir, f"{sc['id']}.jpg")
    if os.path.exists(fpath) and os.path.getsize(fpath) > 10000:
        print(f"[{idx+1}/{len(scenes)}] Bereits vorhanden: {fpath} ({os.path.getsize(fpath)} Bytes)")
        continue
    
    print(f"[{idx+1}/{len(scenes)}] Generiere {sc['id']} (Thron-Wort: {sc['thron_wort']})...")
    success = False
    for attempt in range(5):
        try:
            img = client.text_to_image(sc["prompt"], model="black-forest-labs/FLUX.1-schnell")
            img.save(fpath, quality=95)
            print(f"  -> Gespeichert ({os.path.getsize(fpath)} Bytes): {fpath}")
            success = True
            break
        except Exception as e:
            print(f"  -> Versuch {attempt+1} fehlgeschlagen: {e}")
            time.sleep(3)
    if not success:
        print(f"FEHLER bei {sc['id']}")
        exit(1)

print("\n✓ Alle 12 Szenen für Block 2 erfolgreich im Comic-Noir-Stil generiert!")
