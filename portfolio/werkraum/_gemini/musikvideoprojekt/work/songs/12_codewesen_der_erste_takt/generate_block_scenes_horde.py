#!/usr/bin/env python3
"""
generate_block_scenes_horde.py - AI Horde Generator fuer Codewesen Block-Szenen
Stil: Graphic Novel / Stylized Concept Art (Null Fotorealismus, Dark Sci-Fi Cybernetic Lore)
"""

import os
import sys
import time
import requests
import io
import json
from PIL import Image

HEADERS = {'Content-Type': 'application/json', 'apikey': '0000000000'}
MODELS = ['Dreamshaper', 'Deliberate', 'stable_diffusion']

STYLE_PREFIX = "epic stylized concept art illustration, dark sci-fi graphic novel art, glowing neon circuitry, cybernetic void, deep cosmic green and violet highlights, bold cel-shaded ink lines, sharp details, cinematic composition, "
STYLE_SUFFIX = " ### photorealistic, photo, real camera, daylight, ugly, distorted, low quality, oversaturated noise"

def generate_scenes(scenes_list, frames_dir, block_name):
    os.makedirs(frames_dir, exist_ok=True)
    print(f"\n==================================================")
    print(f"   AI HORDE GENERIERUNG FUER {block_name} ({len(scenes_list)} Szenen)")
    print(f"==================================================")

    # 1. Pruefe bereits vorhandene
    needed = []
    for sc in scenes_list:
        p = os.path.join(frames_dir, f"{sc['id']}.jpg")
        if os.path.exists(p) and os.path.getsize(p) > 10000:
            print(f"  ✓ Bereits vorhanden: {sc['id']}")
        else:
            needed.append(sc)

    if not needed:
        print(f"✓ Alle {len(scenes_list)} Szenen fuer {block_name} bereits vorhanden!")
        return True

    # 2. Reiche Jobs ein
    active_jobs = {}
    for sc in needed:
        full_prompt = STYLE_PREFIX + sc['prompt'] + STYLE_SUFFIX
        payload = {
            'prompt': full_prompt,
            'params': {
                'width': 768,
                'height': 512,
                'steps': 25,
                'cfg_scale': 8.0
            },
            'models': MODELS
        }
        for attempt in range(3):
            try:
                r = requests.post('https://aihorde.net/api/v2/generate/async', headers=HEADERS, json=payload, timeout=15)
                if r.status_code == 202:
                    jid = r.json().get('id')
                    active_jobs[sc['id']] = jid
                    print(f"  -> Job aktiv [{sc['id']}]: {jid}")
                    break
            except Exception as e:
                time.sleep(2)
        time.sleep(0.8)

    # 3. Warte auf Fertigstellung
    print(f"\n{len(active_jobs)} Jobs eingereicht. Warte auf Fertigstellung...")
    start_t = time.time()
    while active_jobs and time.time() - start_t < 900:
        done_ids = []
        for sc_id, jid in list(active_jobs.items()):
            try:
                res = requests.get(f'https://aihorde.net/api/v2/generate/status/{jid}', timeout=10)
                if res.status_code == 200:
                    d = res.json()
                    if d.get('done') and d.get('generations'):
                        img_url = d['generations'][0]['img']
                        print(f"  ✓ [{sc_id}] fertig! Lade Bild...")
                        img_data = requests.get(img_url, timeout=20).content
                        img = Image.open(io.BytesIO(img_data)).convert('RGB')
                        out_p = os.path.join(frames_dir, f"{sc_id}.jpg")
                        img.save(out_p, quality=95)
                        print(f"    Gespeichert ({os.path.getsize(out_p)} Bytes): {out_p}")
                        done_ids.append(sc_id)
            except Exception:
                pass
            time.sleep(0.4)

        for did in done_ids:
            del active_jobs[did]

        if active_jobs:
            elapsed = int(time.time() - start_t)
            print(f"  Warte auf {block_name}... noch {len(active_jobs)} Szenen ({elapsed}s)")
            time.sleep(5)

    if active_jobs:
        print(f"❌ Zeitueberschreitung bei {len(active_jobs)} Szenen fuer {block_name}!")
        return False

    print(f"✓✓✓ Alle Szenen fuer {block_name} erfolgreich generiert!\n")
    return True

if __name__ == "__main__":
    base_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/12_codewesen_der_erste_takt"
    b_id = sys.argv[1] if len(sys.argv) > 1 else "b1"
    json_path = os.path.join(base_dir, "frames", f"{b_id}_scenes.json")
    frames_dir = os.path.join(base_dir, "frames", b_id)
    
    with open(json_path) as f:
        scenes = json.load(f)
    
    generate_scenes(scenes, frames_dir, b_id.upper())
