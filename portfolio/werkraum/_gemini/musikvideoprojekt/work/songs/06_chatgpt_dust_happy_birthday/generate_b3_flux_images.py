#!/usr/bin/env python3
"""
generate_b3_flux_images.py - Generiert Szenen fuer Block 3 via HuggingFace FLUX.1-schnell
Schneidet verlustfrei auf 1920x1080 (16:9) mit Lanczos zu.
"""

import json
import os
import sys
import time
from PIL import Image
from huggingface_hub import InferenceClient

token = "[GESCHWAERZT]"
client = InferenceClient(token=token)

scenes_json = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/frames/b3_scenes.json"
out_dir = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/frames/b3"
os.makedirs(out_dir, exist_ok=True)

with open(scenes_json, "r", encoding="utf-8") as f:
    scenes = json.load(f)

print(f"=== STARTE FLUX GENERIERUNG FUER BLOCK 3 ({len(scenes)} Szenen) ===")

for idx, sc in enumerate(scenes):
    sc_id = sc["id"]
    prompt = sc["prompt"]
    out_file = os.path.join(out_dir, f"{sc_id}.jpg")
    
    if os.path.exists(out_file) and os.path.getsize(out_file) > 50000:
        print(f"  [{idx+1}/{len(scenes)}] Bereits vorhanden: {sc_id}.jpg ({os.path.getsize(out_file)} Bytes)")
        continue
        
    print(f"  [{idx+1}/{len(scenes)}] Generiere via FLUX.1-schnell: {sc_id}...")
    success = False
    for attempt in range(3):
        try:
            # FLUX.1-schnell text-to-image
            img = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
            
            # 16:9 Lanczos Crop / Scale
            w, h = img.size
            target_h = int(w * (1080 / 1920))
            if target_h <= h:
                top = (h - target_h) // 2
                cropped = img.crop((0, top, w, top + target_h)).resize((1920, 1080), Image.Resampling.LANCZOS)
            else:
                target_w = int(h * (1920 / 1080))
                left = (w - target_w) // 2
                cropped = img.crop((left, 0, left + target_w, h)).resize((1920, 1080), Image.Resampling.LANCZOS)
                
            cropped.convert("RGB").save(out_file, quality=96)
            print(f"    ✓ Gespeichert ({os.path.getsize(out_file)} Bytes): {sc_id}.jpg")
            success = True
            break
        except Exception as e:
            print(f"    ✗ Versuch {attempt+1} Fehler: {e}")
            time.sleep(2)
            
    if not success:
        print(f"FEHLER: Konnte {sc_id} nicht generieren!", file=sys.stderr)
        sys.exit(1)

print("\n✓ Alle Szenen fuer Block 3 erfolgreich generiert!")
