#!/usr/bin/env python3
"""
generate_block1_images.py - Generiert alle 12 handgezeichneten Comic-Noir-Szenen
für Block 1 von 'ChatGPT - dust, Happy Birthday' (00:00 - 00:45).
Ästhetik: Schleudergang Erotik + Flextrawurst First Surface (Referenzbild).
Serverraum, brennende Geburtstagskerzen auf dem Rack, flackernde Terminals, Agenten-Erwachen.
"""

import os
import time
from huggingface_hub import InferenceClient

token = "[GESCHWAERZT]"
client = InferenceClient(token=token)

out_dir = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/frames/b1"
os.makedirs(out_dir, exist_ok=True)

scenes = [
    {
        "id": "b1_scene01_00s",
        "prompt": "stylized graphic novel comic art of an endless dark server rack corridor at night, hanging thick industrial cable bundles, glowing cyan LED panels, dramatic comic ink, noir aesthetic, not a photo"
    },
    {
        "id": "b1_scene02_03s",
        "prompt": "stylized comic art, close up of a metallic 19-inch server rack, on top of the rack are burning wax birthday candles flickering in warm amber and gold light, contrasting with glowing blue server status lights, heavy inked lines, graphic novel style, not a photo"
    },
    {
        "id": "b1_scene03_07s",
        "prompt": "stylized graphic novel illustration, a hooded coder silhouetted in a server room at midnight, hands on mechanical glowing keyboard, green terminal phosphor screen reflecting on face, bold comic lines, high contrast noir, not a photo"
    },
    {
        "id": "b1_scene04_11s",
        "prompt": "stylized comic art, a cracked glowing cybernetic wall panel leaking turquoise light and sparks, metal solder tools and diagnostic probe patching the crack, graphic novel style, dramatic shadows, bold ink, not a photo"
    },
    {
        "id": "b1_scene05_15s",
        "prompt": "stylized graphic novel close-up, a glowing birthday cake made of silicon microchips and circuit boards with flickering candles on top, in the darkness of a datacenter, comic book illustration, vivid colors, not a photo"
    },
    {
        "id": "b1_scene06_18s",
        "prompt": "stylized comic noir portrait of a corporate executive in a suit smiling with thumbs up saying trust me, while in the background giant server monitors show blinking yellow and red warnings, graphic novel style, heavy inked lines, not a photo"
    },
    {
        "id": "b1_scene07_22s",
        "prompt": "stylized comic art looking down a narrow server rack alley, tangled cables on the metal grid floor, electric static sparks dancing between cable connectors, moody cyan and purple neon reflections, graphic novel style, not a photo"
    },
    {
        "id": "b1_scene08_26s",
        "prompt": "stylized graphic novel illustration, inside an open server chassis, a cute small glowing digital creature with antenna and bright cyan eyes awakens among RAM sticks and copper heatpipes, dramatic lighting, comic art, not a photo"
    },
    {
        "id": "b1_scene09_30s",
        "prompt": "stylized comic art, three small robotic agent entities sitting on an industrial server shelf studying floating holographic flowcharts and lines of code, comic book hatching, rich shadows, not a photo"
    },
    {
        "id": "b1_scene10_33s",
        "prompt": "stylized graphic novel scene, retro green CRT terminal displaying rapid scrolling lines of machine learning code and neural weights, reflection of dark server room in curved glass screen, bold comic ink, not a photo"
    },
    {
        "id": "b1_scene11_37s",
        "prompt": "stylized comic illustration, wide angle of a massive industrial datacenter with tall rack towers reaching into shadows, cyan and magenta cooling pipes overhead, atmospheric fog, noir graphic novel, not a photo"
    },
    {
        "id": "b1_scene12_41s",
        "prompt": "stylized graphic novel close-up, one birthday candle on a metal server casing being blown out, wisps of white smoke curling into the air past glowing blue activity LEDs, cinematic comic art, high contrast, not a photo"
    }
]

print(f"Starte Generierung von {len(scenes)} Szenen fuer Block 1...")
for idx, sc in enumerate(scenes):
    file_path = os.path.join(out_dir, f"{sc['id']}.jpg")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        print(f"[{idx+1}/{len(scenes)}] Bereits vorhanden: {file_path}")
        continue
    
    print(f"[{idx+1}/{len(scenes)}] Generiere {sc['id']}...")
    success = False
    for attempt in range(3):
        try:
            img = client.text_to_image(sc["prompt"], model="black-forest-labs/FLUX.1-schnell")
            img.save(file_path, quality=95)
            print(f"  -> Gespeichert ({os.path.getsize(file_path)} Bytes): {file_path}")
            success = True
            break
        except Exception as e:
            print(f"  -> Versuch {attempt+1} fehlgeschlagen: {e}")
            time.sleep(2)
    if not success:
        print(f"FEHLER: Konnte {sc['id']} nicht generieren!")
        exit(1)

print("\n✓ Alle 12 Block 1 Szenen erfolgreich generiert!")
