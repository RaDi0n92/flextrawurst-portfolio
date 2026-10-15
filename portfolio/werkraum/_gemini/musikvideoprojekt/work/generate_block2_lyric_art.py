#!/usr/bin/env python3
"""
generate_block2_lyric_art.py - Generiert die 12 lyrischen Szenen für Block 2
(0:44 - 1:28 = 44 Sekunden) von "ChatGPT - Schleudergang erotik" mit FLUX.1-schnell.

Vorgaben von Daniel:
- Nicht zu starr, nicht 1:1 kopieren, frei und kreativ variieren!
- Fokus auf die markanten, lebendigen Momente:
  * Schleudergang / Schwindel
  * Steckdose mit Funken
  * Schaumberge & Spaß auf den Trocknern
  * Schlafende Stadt im Regenfenster
  * Die gestohlene Socke als Handpuppe ("Das ist jetzt Kunst!")
  * Der brummende Getränkeautomat & Kaffee statt Cola
  * Geräte, die sich spielerisch "ausziehen" (aufklappen wie Blütenblätter)
- Echte stilisierte Kunstwerke, KEIN Cyberpunk, keine generischen Stockfotos!
"""

import os
import time
from huggingface_hub import InferenceClient
from PIL import Image

output_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/frames"
os.makedirs(output_dir, exist_ok=True)

token = "[GESCHWAERZT]"
client = InferenceClient(token=token)

scenes = [
    {
        "id": "b2_01_schleudergang_vortex",
        "prompt": "stylized graphic novel illustration, dizzy tilted perspective inside a vintage laundromat, floating soap bubbles and laundry spiraling in a gentle motion vortex, warm amber and soft teal lighting, expressive comic art, not a photo"
    },
    {
        "id": "b2_02_steckdose_spark",
        "prompt": "stylized comic art close-up, a vintage wall power socket with delicate glowing electric sparks softly arcing in the air, warm cozy lighting, atmospheric graphic novel style, not a photo"
    },
    {
        "id": "b2_03_foam_overflow",
        "prompt": "stylized whimsical illustration of huge mountains of fluffy white soap bubbles overflowing from a washing machine door onto the floor tiles, playful and funny, colorful comic art, not a photo"
    },
    {
        "id": "b2_04_dryer_party",
        "prompt": "stylized graphic novel scene, two friends sitting on top of warm laundry dryers with bare feet, laughing together, cozy midnight atmosphere, soft warm lamp light, comic book style, not a photo"
    },
    {
        "id": "b2_05_sleeping_city",
        "prompt": "stylized illustration looking out a steamy rainy laundromat window onto a quiet sleeping city skyline at night with distant glowing windows, soft deep blue hues, moody graphic novel art, not a photo"
    },
    {
        "id": "b2_06_rhythm_dryer",
        "prompt": "stylized comic art, an industrial laundry dryer vibrating to a heavy musical beat, floating musical notes and sound wave ripples in the warm air, vibrant illustration, not a photo"
    },
    {
        "id": "b2_07_sock_puppet_art",
        "prompt": "stylized graphic novel close-up, a hand wearing a striped colorful sock like an eccentric sock puppet with sewn button eyes, held up with serious artistic pride, comic book art, not a photo"
    },
    {
        "id": "b2_08_sock_imp",
        "prompt": "stylized whimsical character art, a cute quirky little fluffy creature with big curious eyes wearing a stolen sock over its head like a silly hat, playful cartoon fantasy art, vibrant colors, not a photo"
    },
    {
        "id": "b2_09_vibration_ripples",
        "prompt": "stylized comic book detail, a glass of water resting on top of a vibrating washing machine, heavy concentric ripples on the water surface from the bass thumping, graphic novel inking, not a photo"
    },
    {
        "id": "b2_10_vending_machine",
        "prompt": "stylized illustration of an old retro beverage vending machine glowing in a dim laundromat corner, soft warm humming glow, colorful vintage buttons, comic book aesthetic, not a photo"
    },
    {
        "id": "b2_11_coffee_soda",
        "prompt": "stylized comic art, a finger pressing a cola button on a vending machine but steaming hot dark coffee pours into a paper cup, rising curls of steam, humorous graphic novel style, not a photo"
    },
    {
        "id": "b2_12_machines_undressing",
        "prompt": "whimsical surreal comic illustration, a vintage washing machine playfully opening its front circular door like blooming flower petals, glowing brass gears inside, floating soap bubbles, fairytale humor, not a photo"
    }
]

print("Starte FLUX.1 Generierung der 12 Szenen für Block 2...")
for idx, sc in enumerate(scenes):
    out_file = os.path.join(output_dir, f"{sc['id']}.jpg")
    print(f"[{idx+1}/12] Generiere '{sc['id']}'...")
    try:
        img = client.text_to_image(sc["prompt"], model="black-forest-labs/FLUX.1-schnell")
        w, h = img.size
        target_h = int(w * (720 / 1280))
        top = (h - target_h) // 2
        cropped = img.crop((0, top, w, top + target_h)).resize((1280, 720), Image.Resampling.LANCZOS)
        cropped.save(out_file, quality=95)
        print(f"  ✓ Gespeichert: {out_file} (1280x720)")
    except Exception as e:
        print(f"  Fehler bei {sc['id']}: {e}")
    time.sleep(0.5)

print("\n✓ Alle 12 Bilder für Block 2 erfolgreich generiert!")
