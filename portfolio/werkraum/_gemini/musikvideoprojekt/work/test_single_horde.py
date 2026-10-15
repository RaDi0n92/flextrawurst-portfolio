#!/usr/bin/env python3
import requests
import json
import time
import io
from PIL import Image

prompt = "gothic cyberpunk winged gargoyle creature with glowing purple slit eyes and dark metallic horns, perched on rainy iron parapet at night, staring through glowing transparent energy dome into a massive bioluminescent cyberpunk city below, dark comic book art style, glowing neon cyan and purple, cinematic lighting, highly detailed digital illustration"
negative_prompt = "photorealistic human, real person, selfie, stock photo, bearded man, smiling woman, park, sunlight, blurry, ugly, distorted, deformed, text, watermark"

headers = {'Content-Type': 'application/json', 'apikey': '0000000000'}
payload = {
    'prompt': f"{prompt} ### {negative_prompt}",
    'params': {
        'width': 512,
        'height': 512,
        'steps': 25,
        'cfg_scale': 7.5
    },
    'models': ['stable_diffusion', 'Comic-Diffusion', 'Deliberate']
}

print("Sende Test-Request an AI Horde...")
r = requests.post('https://aihorde.net/api/v2/generate/async', headers=headers, json=payload, timeout=15)
if r.status_code != 202:
    print(f"Fehler bei Anfrage: {r.status_code} {r.text}")
    exit(1)

job_id = r.json().get('id')
print(f"Job ID: {job_id}. Warte auf Worker...")

for i in range(25):
    time.sleep(3)
    s_resp = requests.get(f'https://aihorde.net/api/v2/generate/status/{job_id}', timeout=10)
    if s_resp.status_code == 200:
        s_data = s_resp.json()
        if s_data.get('done'):
            img_url = s_data['generations'][0]['img']
            print(f"Fertig! Lade Bild von {img_url}...")
            img_bytes = requests.get(img_url, timeout=15).content
            img = Image.open(io.BytesIO(img_bytes))
            # Crop to 16:9
            w, h = img.size
            target_h = int(w * (1080 / 1920))
            top = (h - target_h) // 2
            cropped = img.crop((0, top, w, top + target_h)).resize((1920, 1080), Image.Resampling.LANCZOS)
            out_file = "/root/werkraum/_gemini/musikvideoprojekt/work/test_grok_style.jpg"
            cropped.convert("RGB").save(out_file, quality=96)
            print(f"✓ Gespeichert: {out_file}")
            exit(0)
        else:
            print(f"  Warte... Position in Queue: {s_data.get('queue_position', '?')}")

print("Timeout bei Generierung.")
exit(1)
