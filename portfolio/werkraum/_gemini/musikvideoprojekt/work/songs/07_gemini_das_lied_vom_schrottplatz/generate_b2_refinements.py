#!/usr/bin/env python3
import json
import os
import time
import requests
import io
from PIL import Image

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
swaps_json = os.path.join(song_dir, "b2_refinement_swaps.json")
out_dir = os.path.join(song_dir, "frames", "b2")

with open(swaps_json) as f:
    swaps = json.load(f)

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
models = ['Dreamshaper', 'Deliberate', 'stable_diffusion']

active_jobs = {}
for sc in swaps:
    ref_id = f"{sc['id']}_refined"
    fpath = os.path.join(out_dir, f"{ref_id}.jpg")
    if os.path.exists(fpath) and os.path.getsize(fpath) > 10000:
        print(f"Bereits vorhanden: {fpath}")
        continue
    prompt = f"{sc['prompt']} ### photorealistic, photo, 3d render, blurry, deformed"
    payload = {
        'prompt': prompt,
        'params': {
            'width': 512,
            'height': 512,
            'steps': 22,
            'cfg_scale': 7.0
        },
        'models': models
    }
    r = requests.post('https://aihorde.net/api/v2/generate/async', headers=headers, json=payload, timeout=15)
    if r.status_code == 202:
        job_id = r.json().get('id')
        active_jobs[ref_id] = job_id
        print(f"Job fuer {ref_id} gestartet: {job_id}")
    time.sleep(1)

start_t = time.time()
while active_jobs and time.time() - start_t < 300:
    done_ids = []
    for sc_id, jid in list(active_jobs.items()):
        try:
            res = requests.get(f'https://aihorde.net/api/v2/generate/status/{jid}', timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('done') and data.get('generations'):
                    img_url = data['generations'][0]['img']
                    img_data = requests.get(img_url, timeout=15).content
                    img = Image.open(io.BytesIO(img_data))
                    out_path = os.path.join(out_dir, f"{sc_id}.jpg")
                    img.save(out_path, quality=95)
                    print(f"  ✓ {sc_id} gespeichert ({os.path.getsize(out_path)} Bytes): {out_path}")
                    done_ids.append(sc_id)
        except Exception:
            pass
        time.sleep(1)
    for did in done_ids:
        del active_jobs[did]
    if active_jobs:
        print(f"Verbleibende Veredelungs-Jobs: {len(active_jobs)} | {int(time.time() - start_t)}s")
        time.sleep(5)

print("Veredelungs-Generierung beendet!")
