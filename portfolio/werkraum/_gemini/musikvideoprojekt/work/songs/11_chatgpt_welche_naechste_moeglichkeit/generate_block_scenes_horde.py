#!/usr/bin/env python3
"""
generate_block_scenes_horde.py - Robuster AI Horde Generator fuer Block-Szenen
Stil: Graphic Novel / Stylized Concept Art (Null Fotorealismus)
"""

import os
import sys
import time
import requests
import io
from PIL import Image

HEADERS = {'Content-Type': 'application/json', 'apikey': '0000000000'}
MODELS = ['Dreamshaper', 'Deliberate', 'stable_diffusion']

STYLE_PREFIX = "epic concept art illustration, stylized digital art, dark cyber graphic novel, vibrant cel shading, bold ink lines, "
STYLE_SUFFIX = " ### photorealistic, photo, real camera, blurry, daylight, ugly"

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
    if len(sys.argv) < 3:
        print("Usage: generate_block_scenes_horde.py <scenes.json> <out_dir>")
        sys.exit(1)
    import json
    with open(sys.argv[1]) as f:
        scenes = json.load(f)
    generate_scenes(scenes, sys.argv[2], "CLI")
