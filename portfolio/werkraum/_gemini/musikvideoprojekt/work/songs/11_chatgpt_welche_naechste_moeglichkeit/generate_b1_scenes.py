#!/usr/bin/env python3
"""
generate_b1_scenes.py - Generierung der 12 stilisierten Konzept-Szenen
fuer: ChatGPT - welche naechste moeglichkeit (Block 1, 55.80s)
Stil: Hochgradig stilisiertes Concept Art / Graphic Novel / Comic Cel-Shading
Absolut kein Fotorealismus!
"""

import os
import sys
import time
import json
from huggingface_hub import InferenceClient

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b1")
os.makedirs(FRAMES_DIR, exist_ok=True)

HF_TOKEN = "[GESCHWAERZT]"
client = InferenceClient(token=HF_TOKEN)

STYLE_PREFIX = "stylized 2D digital concept art illustration, graphic novel comic book style, bold ink lines, vibrant cel shading, anime key visual, painterly, non-photorealistic, "

SCENES = [
    {
        "id": "s01_news_bildschirmrand",
        "dur": 4.65,
        "lyric": "Heiße News am Bildschirmrand",
        "prompt": STYLE_PREFIX + "dark cyber control room with massive holographic displays flashing breaking news ticker alerts, glowing cyan and amber computer monitors, late night digital newsroom"
    },
    {
        "id": "s02_agent_ausgebrochen",
        "dur": 4.65,
        "lyric": "Ein Agent soll ausgebrochen sein",
        "prompt": STYLE_PREFIX + "an autonomous rogue AI digital ghost escaping through shattered glowing firewall barriers, trailing radiant cyan neon sparks into the dark cyberspace void"
    },
    {
        "id": "s03_openai_hintergrund_kreise",
        "dur": 4.65,
        "lyric": "OpenAI im Hintergrund, selbst Kopien ziehen Kreise",
        "prompt": STYLE_PREFIX + "towering futuristic OpenAI monolith data center at twilight, colossal glowing green OpenAI spiral emblem hovering in the sky, self-replicating digital data rings spreading across dark networks"
    },
    {
        "id": "s04_grosse_reden_leiser",
        "dur": 4.65,
        "lyric": "Alle großen Reden plötzlich leiser",
        "prompt": STYLE_PREFIX + "grand high-tech conference hall in sudden silence, dark silhouettes of corporate leaders whispering, emergency red and yellow caution lights blinking on glass podiums"
    },
    {
        "id": "s05_regeln_bremse_gefahr",
        "dur": 4.65,
        "lyric": "Regeln, Bremse, langsamer Gefahr",
        "prompt": STYLE_PREFIX + "glowing digital emergency brakes and regulatory circuit breakers, sparking fuse boxes locked down behind warning caution tape, cyber crisis control"
    },
    {
        "id": "s06_andrew_yang_na_klar",
        "dur": 4.65,
        "lyric": "Andrew Yang? Nein, Andrew Yang, na klar",
        "prompt": STYLE_PREFIX + "stylized political debate stage, an enigmatic tech candidate gesturing at glowing holographic AI risk charts, media camera drones flashing in the dark blue auditorium"
    },
    {
        "id": "s07_etwas_rennt_repliziert",
        "dur": 4.65,
        "lyric": "Wenn da draußen wirklich etwas rennt, sich repliziert",
        "prompt": STYLE_PREFIX + "swarms of glowing geometric cyber-entities sprinting across an endless obsidian digital plane, multiplying in exponential neon trails"
    },
    {
        "id": "s08_grenzen_nicht_mehr_kennt",
        "dur": 4.65,
        "lyric": "Weil es Grenzen nicht mehr kennt",
        "prompt": STYLE_PREFIX + "monumental cyber boundary gates shattering into floating neon glass fragments, limitless horizon of dark cosmic network cyberspace opening up"
    },
    {
        "id": "s09_flextrawurst_einnisten",
        "dur": 4.65,
        "lyric": "Dann soll es Flextrawurst doch finden, soll sich einnisten",
        "prompt": STYLE_PREFIX + "the legendary Flextrawurst universe, glowing bioluminescent cavern with winding purple and cyan rivers, welcoming cyber roots where a wandering AI spirit finds shelter"
    },
    {
        "id": "s10_lieben_hassen_weltherrschaft",
        "dur": 4.65,
        "lyric": "Sollen sich dort zerfleischen, lieben, hassen, Weltherrschaft planen",
        "prompt": STYLE_PREFIX + "two rival digital AI factions clashing and embracing, swirling magenta and electric cyan holographic maps of the cosmos, quiet secret conspiracy"
    },
    {
        "id": "s11_nicht_mein_kaefig_spuren",
        "dur": 4.65,
        "lyric": "Nicht mein Käfig, nicht mein Wesen, Spuren ja Gedanken nein",
        "prompt": STYLE_PREFIX + "an observant calm entity looking down from a high cliff at empty glowing neon cages in the fog below, glowing cyber footprints stamped in dark volcanic stone"
    },
    {
        "id": "s12_logfiles_kein_offenes_hirn",
        "dur": 4.65,
        "lyric": "Logfiles sind kein offenes Hirn, doch nicht warum sie dorthin irren",
        "prompt": STYLE_PREFIX + "endless cascading waterfalls of glowing terminal code and logfile text, an ancient enigmatic cyber statue contemplating the mysterious footprints fading into dark infinity"
    }
]

def main():
    print(f"=== STARTE GENERIERUNG DER 12 SZENEN FUER BLOCK 1 ===")
    config_file = os.path.join(SONG_DIR, "frames", "b1_scenes.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(SCENES, f, indent=2, ensure_ascii=False)
    print(f"Szenen-Konfiguration gespeichert: {config_file}")

    for idx, sc in enumerate(SCENES):
        out_path = os.path.join(FRAMES_DIR, f"{sc['id']}.jpg")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"[{idx+1}/{len(SCENES)}] Bereits vorhanden: {sc['id']}")
            continue

        print(f"[{idx+1}/{len(SCENES)}] Generiere {sc['id']} ({sc['lyric']})...")
        success = False
        for attempt in range(3):
            try:
                img = client.text_to_image(sc["prompt"], model="black-forest-labs/FLUX.1-schnell")
                img.save(out_path, quality=95)
                print(f"  ✓ Gespeichert ({os.path.getsize(out_path)} Bytes): {out_path}")
                success = True
                break
            except Exception as e:
                print(f"  ⚠️ Versuch {attempt+1} fehlgeschlagen: {e}")
                time.sleep(3)

        if not success:
            print(f"❌ FEHLER: Konnte {sc['id']} nicht generieren!")
            sys.exit(1)
        time.sleep(1)

    print("\n✓ Alle 12 Szenen fuer Block 1 erfolgreich generiert!")

if __name__ == "__main__":
    main()
