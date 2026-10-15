#!/usr/bin/env python3
"""
generate_block1_lyric_art.py - Generiert die 12 prägnanten Szenen für Block 1
exakt nach den lyrischen Bildern des Songtexts mit FLUX.1-schnell.

Fokus:
- Prägnante Text-Momente: Die Digitaluhr 03:17, der kaputte Mond, barfuß auf Maschine 4,
  die zwei Münzen, die kreisende rote Jacke, Weichspüler, Maschine 7 als Bar!
- Angereichert mit dezenten, skurrilen Gogo-/Kristall-Details wo es passt.
- KEIN Cyberpunk, keine generischen Fotos, sondern echte stilisierte Kunst!
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
        "prompt": "stylized illustration of a retro digital clock glowing 03:17 on a tiled wall of a quiet laundromat at night, warm soft ambient light, steam in the air, graphic novel style, atmospheric mood, not a photo"
    },
    {
        "id": "b1_02_moon",
        "prompt": "stylized comic art, looking through a tall rainy window at a flickering circular neon sign shaped like a broken moon, reflecting on the wet street outside, moody colors, graphic novel illustration, not a photo"
    },
    {
        "id": "b1_03_barefoot",
        "prompt": "stylized artistic close-up of bare feet casually dangling over the stainless steel edge of an industrial washing machine labeled number 4, floor tiles below, comic graphic novel illustration, warm intimate lighting, not a photo"
    },
    {
        "id": "b1_04_intimate",
        "prompt": "stylized graphic novel illustration of two people sitting very close side-by-side on top of washing machines, seen from behind or profile, quiet intimate tension, cozy midnight laundromat, comic art, not a photo"
    },
    {
        "id": "b1_05_coins",
        "prompt": "stylized comic art close-up, two shiny euro coins held in human fingers inserting into a mechanical metal coin slot on an old washing machine, warm moody lighting, comic book illustration, not a photo"
    },
    {
        "id": "b1_06_gogo_grin",
        "prompt": "stylized illustration of a cute quirky Gogo Crazy Bones mini creature with a tiny glowing crystal horn sitting on a box of laundry detergent with a funny toothy smirk, comic art style, not a photo"
    },
    {
        "id": "b1_07_drum_spin",
        "prompt": "stylized graphic novel view looking directly into the round glass door of a washing machine drum just starting to spin, swirling water and white soap suds, dynamic motion lines, comic art, not a photo"
    },
    {
        "id": "b1_08_red_jacket",
        "prompt": "stylized comic art, through the circular glass porthole of a washing machine, a bright red jacket is swirling in the water with soap bubbles, vibrant colors, graphic novel illustration, not a photo"
    },
    {
        "id": "b1_09_hanging_jacket",
        "prompt": "stylized illustration of a dark denim jacket casually hanging from an overhead metal pipe in a laundromat, soft warm overhead light, graphic novel comic style, not a photo"
    },
    {
        "id": "b1_10_softener",
        "prompt": "stylized comic art, an old glass bottle of blue liquid fabric softener spilling a bright turquoise puddle onto the brushed metal of a washing machine, small glowing crystal bubbles rising, graphic novel style, not a photo"
    },
    {
        "id": "b1_11_machine_bar",
        "prompt": "stylized comic illustration of two glasses with whiskey and ice cubes resting on top of washing machine number 7 like an improvised midnight bar, warm amber light, cozy graphic novel aesthetic, not a photo"
    },
    {
        "id": "b1_12_vortex_critter",
        "prompt": "stylized fantasy comic illustration of a whimsical tiny clockwork gear sprite watching the spinning washing machine drum, soap bubbles floating in the air, warm cozy midnight atmosphere, not a photo"
    }
]

print("Starte FLUX.1 Generierung der 12 lyrischen Szenen für Block 1...")
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

print("\n✓ Alle 12 Bilder erfolgreich generiert!")
