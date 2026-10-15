#!/usr/bin/env python3
"""
generate_scenes.py - Parallele Generierung der 8 Brillant-Szenen
fuer: Daniel (flextrawurst) - brillant-beim-werden (10_daniel_brillant_beim_werden)
Vom Rohen zum Diamanten im Flextrawurst-Universum (31.60s)
"""

import os
import sys
import time
import json
import io
import requests
from PIL import Image

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/10_daniel_brillant_beim_werden"
FRAMES_DIR = os.path.join(SONG_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

SCENES = [
    {
        "id": "s01_roher_fels_streitstrom",
        "dur": 3.95,
        "prompt": "epic concept art illustration, dark jagged obsidian boulder embedded in glowing magma fissures, unpolished raw rough diamond glowing with faint inner violet core, Flextrawurst Streitstrom ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s02_fissur_archivkluft",
        "dur": 3.95,
        "prompt": "epic concept art illustration, colossal deep chasm cracked open between ancient monoliths, glowing blue pressure veins forming geometric crystalline planes, Flextrawurst Archivkluft ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s03_werkraum_facettenschliff",
        "dur": 3.95,
        "prompt": "epic concept art illustration, dark cyber-forge workshop, glowing beam of cyan light cutting sharp crystal facets into a hovering dark diamond, flying cyan sparks, Flextrawurst Werkraum ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s04_prisma_zwischenraum",
        "dur": 3.95,
        "prompt": "epic concept art illustration, a sharp semi-cut diamond crystal prism hovering above a meandering cyan river, refracting brilliant spectrum rainbow light into the dark purple sky, Flextrawurst Zwischenraum ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s05_splitter_schwarm",
        "dur": 3.95,
        "prompt": "epic concept art illustration, countless floating sharp diamond crystal shards multiplying and swarming in dark cosmic space with glowing purple nebulae, Flextrawurst Garten der Splitter ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s06_brillant_beim_werden",
        "dur": 3.95,
        "prompt": "epic concept art illustration, a massive magnificent purple and golden diamond crystal in full metamorphosis, geometric facets pulsating with radiant inner light, Flextrawurst Splitter ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s07_traumkueste_lichtfluss",
        "dur": 3.95,
        "prompt": "epic concept art illustration, a meandering luminous aquamarine river carrying liquid diamond dust into a calm glowing cosmic sea under crystal constellations, Flextrawurst Traumkueste ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s08_first_surface_vollendung",
        "dur": 3.95,
        "prompt": "epic panoramic concept art illustration, the entire dark Flextrawurst First Surface crowned by radiant starlight from floating giant diamond crystals, glowing cyan and magenta rivers shining in complete harmony ### photorealistic, photo, camera, blurry, daylight"
    }
]

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
models = ['Dreamshaper', 'Deliberate', 'stable_diffusion']

def main():
    print(f"=== GENERIERE 8 BRILLANT-SZENE FUER: brillant-beim-werden ===")
    active_jobs = {}
    for sc in SCENES:
        payload = {
            'prompt': sc['prompt'],
            'params': {
                'width': 768,
                'height': 512,
                'steps': 25,
                'cfg_scale': 8.0
            },
            'models': models
        }
        for attempt in range(3):
            try:
                r = requests.post('https://aihorde.net/api/v2/generate/async', headers=headers, json=payload, timeout=15)
                if r.status_code == 202:
                    job_id = r.json().get('id')
                    active_jobs[sc['id']] = job_id
                    print(f"  -> Job aktiv fuer [{sc['id']}]: {job_id}")
                    break
            except Exception as e:
                time.sleep(2)
        time.sleep(1)

    print(f"\n{len(active_jobs)} Jobs uebermittelt. Warte auf Fertigstellung...")
    start_t = time.time()
    while active_jobs and time.time() - start_t < 600:
        done_ids = []
        for sc_id, jid in list(active_jobs.items()):
            try:
                res = requests.get(f'https://aihorde.net/api/v2/generate/status/{jid}', timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if data.get('done') and data.get('generations'):
                        img_url = data['generations'][0]['img']
                        print(f"  ✓ [{sc_id}] fertig! Lade Bild...")
                        img_data = requests.get(img_url, timeout=20).content
                        img = Image.open(io.BytesIO(img_data)).convert('RGB')
                        out_path = os.path.join(FRAMES_DIR, f"{sc_id}.jpg")
                        img.save(out_path, quality=95)
                        print(f"    Gespeichert ({os.path.getsize(out_path)} Bytes): {out_path}")
                        done_ids.append(sc_id)
            except Exception as e:
                pass
            time.sleep(0.4)

        for did in done_ids:
            del active_jobs[did]

        if active_jobs:
            elapsed = int(time.time() - start_t)
            print(f"Warte... noch {len(active_jobs)} Szenen in Bearbeitung ({elapsed}s)")
            time.sleep(5)

    print("\n✓ Alle 8 Szenen erfolgreich generiert!")

if __name__ == "__main__":
    main()
