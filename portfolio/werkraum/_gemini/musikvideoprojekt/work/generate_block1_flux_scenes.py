#!/usr/bin/env python3
"""
generate_block1_flux_scenes.py - Generiert alle 12 Szenen für Block 1
mit FLUX.1-schnell über die freie HuggingFace Inference API!

Stil: Stylized Graphic Novel / Comic Noir / Wesen & Entitäten im Waschsalon.
Absolut keine generischen Plastik-Fotos, sondern echte hand-geinkte Kunstwerke!
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
        "id": "b1_01_clock",
        "prompt": "stylized graphic novel comic art, retro laundromat interior at 3:17 AM, a large digital clock glowing 03:17 in neon cyan on the wall, a small shadow creature with glowing eyes peeking over the clock, rainy window in background, heavy inked lines, noir comic style, not a photo"
    },
    {
        "id": "b1_02_hallway",
        "prompt": "stylized comic illustration of a deserted laundromat hallway at midnight, rows of metallic washing machines, wet floor reflecting turquoise and magenta neon lights, an eccentric horned demon creature sitting in the center, heavy shadows, graphic novel noir art, not a photo"
    },
    {
        "id": "b1_03_machine_four",
        "prompt": "stylized graphic novel art, a quirky hooded creature with bare feet sitting on top of an industrial washing machine labeled number 4, dangling its feet, smirking, neon cyan lighting, dramatic comic ink, not a photo"
    },
    {
        "id": "b1_04_intimate",
        "prompt": "intense close-up portrait of a stylized mythical creature in a neon laundromat, piercing glowing magenta eyes, electric static sparks in its fur and claws, dramatic chiaroscuro shadow, comic novel illustration, not a photo"
    },
    {
        "id": "b1_05_coin_slot",
        "prompt": "stylized comic art of a mechanical coin slot with glowing red error LED, two metal coins held by a clawed monster hand, dark industrial laundromat, graphic novel style, bold ink, not a photo"
    },
    {
        "id": "b1_06_grin",
        "prompt": "stylized graphic novel close-up of a mischievous monster grin with sharp white teeth, vivid cyan electric lightning bolts jumping between its fingertips, comic art style, high contrast, not a photo"
    },
    {
        "id": "b1_07_drum_vortex",
        "prompt": "stylized surreal comic illustration looking into the round glass door of a spinning washing machine drum, a swirling whirlpool of turquoise water and cosmic energy vortex, bold comic lines, not a photo"
    },
    {
        "id": "b1_08_red_jacket",
        "prompt": "stylized comic art, through a round washing machine porthole window, a bright red jacket is caught in a violent water spin cycle, glowing bubbles, heavy inking, graphic novel aesthetic, not a photo"
    },
    {
        "id": "b1_09_hanging_jacket",
        "prompt": "stylized graphic novel scene, a dark jacket hanging from industrial ceiling pipes, in the rafters above perches a small winged chimera creature watching, neon signs, moody shadows, comic art, not a photo"
    },
    {
        "id": "b1_10_softener",
        "prompt": "stylized comic art, a glass bottle tipping over on a steel washing machine, pouring glowing neon cyan liquid detergent, a curious little goblin creature touching the puddle, graphic novel style, not a photo"
    },
    {
        "id": "b1_11_machine_bar",
        "prompt": "stylized comic illustration, washing machine number 7 transformed into a speakeasy bar with two whiskey glasses and ice cubes on top, warm amber and neon purple light, a strange creature sitting next to it, graphic novel art, not a photo"
    },
    {
        "id": "b1_12_flickering_moon",
        "prompt": "stylized graphic novel comic art, looking out the laundromat window at a cracked neon billboard shaped like a broken moon, heavy rain pouring down, silhouette of a horned creature looking out into the sleeping city, noir comic, not a photo"
    }
]

print("Starte FLUX.1 Generierung der 12 Szenen...")
for idx, sc in enumerate(scenes):
    out_file = os.path.join(output_dir, f"{sc['id']}.jpg")
    print(f"[{idx+1}/12] Generiere '{sc['id']}' mit FLUX.1...")
    try:
        img = client.text_to_image(sc["prompt"], model="black-forest-labs/FLUX.1-schnell")
        # Zentrierter 16:9 Beschnitt auf 1280x720
        # img ist standardmäßig 1024x1024 -> wir schneiden vertikal auf 1024x576 und skalieren auf 1280x720
        w, h = img.size
        target_h = int(w * (720 / 1280))
        top = (h - target_h) // 2
        cropped = img.crop((0, top, w, top + target_h)).resize((1280, 720), Image.Resampling.LANCZOS)
        cropped.save(out_file, quality=95)
        print(f"  ✓ Gespeichert: {out_file} (1280x720)")
    except Exception as e:
        print(f"  Fehler bei {sc['id']}: {e}")
    time.sleep(1.0)

print("\n✓ Alle 12 FLUX.1 Szenen fertig generiert!")
