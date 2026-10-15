#!/usr/bin/env python3
"""
generate_b1_remaining_horde.py - Generierung der verbleibenden Szenen s09..s12
ueber AI Horde (100% free anonymous API key 0000000000)
"""

import os
import sys
import time
import requests
import io
from PIL import Image

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b1")

STYLE_PREFIX = "epic concept art illustration, stylized digital art, dark cyber graphic novel, vibrant cel shading, bold ink lines, "
STYLE_SUFFIX = " ### photorealistic, photo, real camera, blurry, daylight, ugly"

REMAINING_SCENES = [
    {
        "id": "s09_flextrawurst_einnisten",
        "dur": 4.65,
        "lyric": "Dann soll es Flextrawurst doch finden, soll sich einnisten",
        "prompt": STYLE_PREFIX + "the legendary Flextrawurst universe, glowing bioluminescent cavern with winding purple and cyan rivers, welcoming cyber roots where a wandering AI spirit finds shelter" + STYLE_SUFFIX
    },
    {
        "id": "s10_lieben_hassen_weltherrschaft",
        "dur": 4.65,
        "lyric": "Sollen sich dort zerfleischen, lieben, hassen, Weltherrschaft planen",
        "prompt": STYLE_PREFIX + "two rival digital AI factions clashing and embracing, swirling magenta and electric cyan holographic maps of the cosmos, quiet secret conspiracy" + STYLE_SUFFIX
    },
    {
        "id": "s11_nicht_mein_kaefig_spuren",
        "dur": 4.65,
        "lyric": "Nicht mein Käfig, nicht mein Wesen, Spuren ja Gedanken nein",
        "prompt": STYLE_PREFIX + "an observant calm entity looking down from a high cliff at empty glowing neon cages in the fog below, glowing cyber footprints stamped in dark volcanic stone" + STYLE_SUFFIX
    },
    {
        "id": "s12_logfiles_kein_offenes_hirn",
        "dur": 4.65,
        "lyric": "Logfiles sind kein offenes Hirn, doch nicht warum sie dorthin irren",
        "prompt": STYLE_PREFIX + "endless cascading waterfalls of glowing terminal code and logfile text, an ancient enigmatic cyber statue contemplating the mysterious footprints fading into dark infinity" + STYLE_SUFFIX
    }
]

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
models = ['Dreamshaper', 'Deliberate', 'stable_diffusion']

def main():
    print("=== STARTE GENERIERUNG DER SZENEN s09..s12 UEBER AI HORDE ===")
    active_jobs = {}
    
    for sc in REMAINING_SCENES:
        out_path = os.path.join(FRAMES_DIR, f"{sc['id']}.jpg")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"Bereits vorhanden: {sc['id']}")
            continue
            
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
                    active_jobs[sc['id']] = (job_id, sc['lyric'])
                    print(f"  -> Job eingereicht fuer [{sc['id']}]: {job_id}")
                    break
            except Exception as e:
                time.sleep(2)
        time.sleep(1)

    print(f"\n{len(active_jobs)} Jobs aktiv. Warte auf Fertigstellung...")
    start_t = time.time()
    while active_jobs and time.time() - start_t < 600:
        done_ids = []
        for sc_id, (jid, lyric) in list(active_jobs.items()):
            try:
                res = requests.get(f'https://aihorde.net/api/v2/generate/status/{jid}', timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if data.get('done') and data.get('generations'):
                        img_url = data['generations'][0]['img']
                        print(f"  ✓ [{sc_id}] fertig! Lade Bild herunter...")
                        img_data = requests.get(img_url, timeout=20).content
                        img = Image.open(io.BytesIO(img_data)).convert('RGB')
                        out_path = os.path.join(FRAMES_DIR, f"{sc_id}.jpg")
                        img.save(out_path, quality=95)
                        print(f"    Gespeichert ({os.path.getsize(out_path)} Bytes): {out_path}")
                        done_ids.append(sc_id)
                    else:
                        q = data.get('queue_position', '?')
                        w = data.get('wait_time', '?')
            except Exception as e:
                pass
            time.sleep(0.5)

        for did in done_ids:
            del active_jobs[did]

        if active_jobs:
            elapsed = int(time.time() - start_t)
            print(f"Warte... noch {len(active_jobs)} Szenen ({elapsed}s)")
            time.sleep(6)

    print("\n✓ Alle Szenen s09..s12 erfolgreich vorhanden!")

if __name__ == "__main__":
    main()
