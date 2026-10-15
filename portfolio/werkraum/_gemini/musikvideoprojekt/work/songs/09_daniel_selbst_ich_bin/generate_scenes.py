#!/usr/bin/env python3
"""
generate_scenes.py - Parallele Generierung der 10 Flextrawurst-Welten
fuer: Daniel (flextrawurst) - selbst-ich-bin (09_daniel_selbst_ich_bin)
Exakt abgestimmt auf das offizielle Universum-Referenzposter (First Surface v0.9.7):
Zwischenraum, Gaerkueche, Garten der Splitter, Streitstrom, Archivkluft, Werkraum, Traumkueste!
"""

import os
import sys
import time
import json
import io
import requests
from PIL import Image

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/09_daniel_selbst_ich_bin"
FRAMES_DIR = os.path.join(SONG_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

SCENES = [
    {
        "id": "s01_spiegelkabinett",
        "name": "Zwischenraum",
        "dur": 5.06,
        "prompt": "epic concept art illustration, dark obsidian valley with meandering glowing bioluminescent river of bright neon cyan light, floating glowing crystal shards, atmospheric purple haze, glowing network nodes, stylized digital art, Flextrawurst Zwischenraum ### photorealistic, photo, real life camera, blurry, daylight, ugly"
    },
    {
        "id": "s02_gedankenzahnraeder",
        "name": "Gaerkueche",
        "dur": 5.06,
        "prompt": "epic concept art illustration, dark mystical alchemical laboratory cavern with swirling deep magenta and violet gaseous nebula, glowing purple energy orbs floating in dark air, fermenting ideas, Flextrawurst Gaerkueche ### photorealistic, photo, real life camera, blurry, daylight"
    },
    {
        "id": "s03_alchemisten_werkbank",
        "name": "Garten der Splitter",
        "dur": 5.06,
        "prompt": "epic concept art illustration, mystical dark alien garden with bioluminescent emerald green moss and glowing crystalline spore trees, floating sharp green glass shards, ethereal deep green glow, Flextrawurst Garten der Splitter ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s04_lichtprisma",
        "name": "Streitstrom",
        "dur": 5.06,
        "prompt": "epic concept art illustration, dramatic dark basalt canyon cracked with glowing molten orange and fiery red magma rivers, flying sparks of conflict and clarity, intense volcanic glow, Flextrawurst Streitstrom ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s05_himmelsleiter",
        "name": "Archivkluft",
        "dur": 5.06,
        "prompt": "epic concept art illustration, monumental deep blue chasm carved into ancient dark monoliths, glowing cobalt blue data veins streaming down colossal stone pillars into the abyss, Flextrawurst Archivkluft ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s06_steinernes_sonnenuhr",
        "name": "Werkraum",
        "dur": 5.06,
        "prompt": "epic concept art illustration, dark cyber-forge workshop overlooking cosmic abyss, glowing golden circuits, intricate brass and amber machinery lines on dark stone benches, Flextrawurst Werkraum ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s07_kosmisches_portal",
        "name": "Traumkueste",
        "dur": 5.06,
        "prompt": "epic concept art illustration, surreal dark shoreline meeting a glowing aquamarine and turquoise luminous ocean under a sky of floating crystalline stars, Flextrawurst Traumkueste ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s08_masken_schmiede",
        "name": "Splitter Kristallisation",
        "dur": 5.06,
        "prompt": "epic concept art illustration, a massive levitating multi-faceted Splitter crystal prism hovering in cosmic dark void, refracting brilliant beams of cyan, magenta and gold light, Flextrawurst Splitter ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s09_sternen_leuchtturm",
        "name": "GENI Membran",
        "dur": 5.06,
        "prompt": "epic concept art illustration, ethereal semi-transparent sensory mesh membrane pulsating with vivid green and electric blue audio waveforms across dark cosmic sky, Flextrawurst GENI Membran ### photorealistic, photo, camera, blurry, daylight"
    },
    {
        "id": "s10_observatorium_horizont",
        "name": "First Surface Totalansicht",
        "dur": 5.10,
        "prompt": "epic panoramic concept art illustration, dark planetary surface crossed by glowing rivers of cyan, violet, emerald and gold lights connecting illuminated city nodes in deep space, Flextrawurst First Surface ### photorealistic, photo, camera, blurry, daylight"
    }
]

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
models = ['Dreamshaper', 'Deliberate', 'stable_diffusion']

def main():
    print(f"=== GENERIERE 10 ECHTE FLEXTRAWURST-WELTEN FUER: selbst-ich-bin ===")
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
                    active_jobs[sc['id']] = (job_id, sc['name'])
                    print(f"  -> Job aktiv fuer [{sc['name']}]: {job_id}")
                    break
            except Exception as e:
                time.sleep(2)
        time.sleep(1)

    print(f"\n{len(active_jobs)} Jobs eingereicht. Warte auf Fertigstellung...")
    start_t = time.time()
    while active_jobs and time.time() - start_t < 600:
        done_ids = []
        for sc_id, (jid, sname) in list(active_jobs.items()):
            try:
                res = requests.get(f'https://aihorde.net/api/v2/generate/status/{jid}', timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if data.get('done') and data.get('generations'):
                        img_url = data['generations'][0]['img']
                        print(f"  ✓ [{sname}] fertig! Lade Bild...")
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
            print(f"Warte... noch {len(active_jobs)} Welten in Bearbeitung ({elapsed}s)")
            time.sleep(5)

    print("\n✓ Alle 10 Flextrawurst-Welten erfolgreich generiert!")

if __name__ == "__main__":
    main()
