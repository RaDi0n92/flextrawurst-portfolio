#!/usr/bin/env python3
import json
import os
import time
import requests
import io
from PIL import Image

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
thron_json = os.path.join(song_dir, "b4_thron_scenes.json")
out_dir = os.path.join(song_dir, "frames", "b4")

with open(thron_json) as f:
    scenes = json.load(f)

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
models = ['Dreamshaper', 'Deliberate', 'stable_diffusion', 'iCoMix', 'Western Animation Diffusion']

# Finde fehlende Szenen
missing = []
for sc in scenes:
    fpath = os.path.join(out_dir, f"{sc['id']}.jpg")
    if not os.path.exists(fpath) or os.path.getsize(fpath) < 10000:
        missing.append(sc)

print(f"Fehlende Szenen für Block 4: {len(missing)} von {len(scenes)}")
if not missing:
    print("Alle Szenen bereits vorhanden!")
    exit(0)

# Sende Jobs an AI Horde
active_jobs = {}
for sc in missing:
    prompt = f"{sc['prompt']} ### photorealistic, photo, 3d render, deformed, blurry"
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
    for attempt in range(3):
        try:
            r = requests.post('https://aihorde.net/api/v2/generate/async', headers=headers, json=payload, timeout=15)
            if r.status_code == 202:
                job_id = r.json().get('id')
                active_jobs[sc['id']] = job_id
                print(f"  -> Job gestartet für {sc['id']} ({sc['thron_wort']}): {job_id}")
                break
        except Exception as e:
            print(f"  Fehler bei Submit für {sc['id']}: {e}")
            time.sleep(2)
    time.sleep(1)

print(f"\n{len(active_jobs)} Jobs laufen auf AI Horde. Warte auf Fertigstellung...")

# Polle Status bis alle fertig sind
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
                    model_used = data['generations'][0].get('model', '?')
                    print(f"  ✓ {sc_id} fertig via {model_used}! Lade Bild...")
                    img_data = requests.get(img_url, timeout=15).content
                    img = Image.open(io.BytesIO(img_data))
                    out_path = os.path.join(out_dir, f"{sc_id}.jpg")
                    img.save(out_path, quality=95)
                    print(f"    Gespeichert ({os.path.getsize(out_path)} Bytes): {out_path}")
                    done_ids.append(sc_id)
        except Exception as e:
            pass
        time.sleep(1)
        
    for did in done_ids:
        del active_jobs[did]
        
    if active_jobs:
        print(f"Verbleibende Jobs: {len(active_jobs)} | Verstrichene Zeit: {int(time.time() - start_t)}s")
        time.sleep(6)

if active_jobs:
    print(f"WARNUNG: {len(active_jobs)} Jobs noch nicht fertig!")
    exit(1)
else:
    print("\n✓ Alle 14 Szenen für Block 4 erfolgreich generiert!")
