#!/usr/bin/env python3
import json
import os
import time
import requests
import io
from PIL import Image

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
swaps_json = os.path.join(song_dir, "b3_refinement_swaps.json")
out_dir = os.path.join(song_dir, "frames", "b3")

with open(swaps_json) as f:
    swaps = json.load(f)

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
models = ['Dreamshaper', 'Deliberate', 'stable_diffusion', 'iCoMix', 'Western Animation Diffusion']

active_jobs = {}
for sw in swaps:
    sc_id = sw['id']
    out_file = os.path.join(out_dir, f"{sc_id}_refined.jpg")
    prompt = f"{sw['new_prompt']} ### photorealistic, photo, 3d render, deformed, blurry"
    payload = {
        'prompt': prompt,
        'params': {
            'width': 512,
            'height': 512,
            'steps': 24,
            'cfg_scale': 7.5
        },
        'models': models
    }
    for attempt in range(3):
        try:
            r = requests.post('https://aihorde.net/api/v2/generate/async', headers=headers, json=payload, timeout=15)
            if r.status_code == 202:
                job_id = r.json().get('id')
                active_jobs[sc_id] = (job_id, out_file)
                print(f"  -> Job gestartet für {sc_id}_refined ({sw['thron_wort']}): {job_id}")
                break
        except Exception as e:
            print(f"  Fehler bei Submit: {e}")
            time.sleep(2)
    time.sleep(1)

print(f"\n{len(active_jobs)} Refinement-Jobs laufen auf AI Horde. Warte auf Fertigstellung...")

start_t = time.time()
while active_jobs and time.time() - start_t < 600:
    done_ids = []
    for sc_id, (jid, out_file) in list(active_jobs.items()):
        try:
            res = requests.get(f'https://aihorde.net/api/v2/generate/status/{jid}', timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('done') and data.get('generations'):
                    img_url = data['generations'][0]['img']
                    model_used = data['generations'][0].get('model', '?')
                    print(f"  ✓ {sc_id}_refined fertig via {model_used}! Lade Bild...")
                    img_data = requests.get(img_url, timeout=15).content
                    img = Image.open(io.BytesIO(img_data))
                    img.save(out_file, quality=95)
                    print(f"    Gespeichert ({os.path.getsize(out_file)} Bytes): {out_file}")
                    done_ids.append(sc_id)
        except Exception as e:
            pass
        time.sleep(1)
        
    for did in done_ids:
        del active_jobs[did]
        
    if active_jobs:
        print(f"Verbleibende Refinement-Jobs: {len(active_jobs)} | Zeit: {int(time.time() - start_t)}s")
        time.sleep(5)

if active_jobs:
    print(f"WARNUNG: {len(active_jobs)} Refinement-Jobs nicht fertig!")
    exit(1)
else:
    print("\n✓ Alle 3 Refinement-Bilder erfolgreich generiert!")
