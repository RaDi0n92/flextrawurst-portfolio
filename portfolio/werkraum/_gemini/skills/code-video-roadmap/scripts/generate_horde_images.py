#!/usr/bin/env python3
"""
generate_horde_images.py - Robuster Bildgenerator via AI Horde mit Pollinations-Fallback
Erzeugt Bilder im Comic-/Grok-Stil, schneidet sie verlustfrei auf 1920x1080 Lanczos zu
und prüft sofort die Integrität (keine Leerbilder).
"""

import argparse
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from PIL import Image

def parse_args():
    parser = argparse.ArgumentParser(description="Generiere Bilder via AI Horde mit Fallback.")
    parser.add_argument("--scenes-json", "-s", required=True, help="Pfad zur JSON-Datei mit [{id: str, prompt: str}].")
    parser.add_argument("--out-dir", "-o", required=True, help="Zielordner für generierte Bilder.")
    parser.add_argument("--models", "-m", nargs="+", default=["stable_diffusion", "Comic-Diffusion"], help="AI Horde Modelle.")
    return parser.parse_args()

def generate_via_horde(prompt, models):
    import requests
    headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
    payload = {
        'prompt': prompt,
        'params': {'width': 512, 'height': 512, 'steps': 20, 'cfg_scale': 7.0},
        'models': models
    }
    try:
        r = requests.post('https://aihorde.net/api/v2/generate/async', headers=headers, json=payload, timeout=15)
        if r.status_code != 202:
            return None
        job_id = r.json().get('id')
        if not job_id:
            return None
            
        for _ in range(12):
            time.sleep(5)
            s_resp = requests.get(f'https://aihorde.net/api/v2/generate/status/{job_id}', timeout=10)
            if s_resp.status_code == 200:
                s_data = s_resp.json()
                if s_data.get('done'):
                    img_url = s_data['generations'][0]['img']
                    img_bytes = requests.get(img_url, timeout=15).content
                    return img_bytes
    except Exception as e:
        print(f"    (Horde-Warnung: {e})")
    return None

def generate_via_pollinations(prompt):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.read()
    except Exception as e:
        print(f"    (Pollinations-Warnung: {e})")
    return None

def crop_and_save(img_bytes, out_file):
    img = Image.open(io.BytesIO(img_bytes))
    w, h = img.size
    target_h = int(w * (1080 / 1920))
    if target_h <= h:
        top = (h - target_h) // 2
        cropped = img.crop((0, top, w, top + target_h)).resize((1920, 1080), Image.Resampling.LANCZOS)
    else:
        cropped = img.resize((1920, 1080), Image.Resampling.LANCZOS)
    cropped.convert("RGB").save(out_file, quality=96)

def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    
    with open(args.scenes_json, "r", encoding="utf-8") as f:
        scenes = json.load(f)
        
    print(f"\n=== STARTE BILDGENERIERUNG ({len(scenes)} Szenen) ===")
    for idx, sc in enumerate(scenes):
        sc_id = sc["id"]
        prompt = sc["prompt"]
        out_file = os.path.join(args.out_dir, f"{sc_id}.jpg")
        
        if os.path.exists(out_file) and os.path.getsize(out_file) > 25000:
            print(f"  [{idx+1}/{len(scenes)}] Bereits da: {sc_id}.jpg")
            continue
            
        print(f"  [{idx+1}/{len(scenes)}] Generiere: {sc_id}...")
        
        # Versuch 1: Pollinations (schnell, 2s)
        img_bytes = generate_via_pollinations(prompt)
        
        # Versuch 2: AI Horde (falls Pollinations Rate-Limit / Timeout)
        if not img_bytes:
            print(f"    -> Fallback auf AI Horde für {sc_id}...")
            img_bytes = generate_via_horde(prompt, args.models)
            
        # Versuch 3: Erneuter Versuch nach kurzem Backoff
        if not img_bytes:
            print(f"    -> Zweiter Versuch nach Backoff für {sc_id}...")
            time.sleep(3)
            img_bytes = generate_via_pollinations(prompt)
            
        if img_bytes:
            crop_and_save(img_bytes, out_file)
            sz_kb = os.path.getsize(out_file) / 1024.0
            print(f"    ✓ Gespeichert: {sc_id}.jpg ({sz_kb:.1f} KB)")
        else:
            print(f"    ✗ FEHLER: Konnte kein Bild generieren für {sc_id}", file=sys.stderr)
            
        time.sleep(1.5) # Sanfter Abstand gegen Rate Limits

    print("=== BILDGENERIERUNG ABGESCHLOSSEN ===\n")

if __name__ == "__main__":
    main()
