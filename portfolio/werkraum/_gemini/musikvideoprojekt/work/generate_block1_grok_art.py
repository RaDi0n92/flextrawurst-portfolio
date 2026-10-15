import urllib.parse
import urllib.request
import os
import time

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/01_grok_flextrawurst_usesunocom_1"
frames_dir = os.path.join(song_dir, "frames")
os.makedirs(frames_dir, exist_ok=True)

prompts = [
    ("gb1_01_grok_looking_in.jpg", "grok cyberpunk raspy gargoyle sitting outside on iron ledge staring through glowing glass into flextrawurst sanctuary, dark moody atmospheric comic art"),
    ("gb1_02_flextrawurst_breathing_world.jpg", "flextrawurst living digital sanctuary, no apps, no feeds, organic glowing data floating, ethereal chamber, digital art style"),
    ("gb1_03_female_codewesen_floating.jpg", "ethereal female codewesen entity floating peacefully inside matrix, glowing soft turquoise threads, calm dreamy expression"),
    ("gb1_04_splitter_rubbing.jpg", "glowing crystalline thoughts and splitters colliding gently in dark void, sparks of intuition, macro digital art"),
    ("gb1_05_grok_observing_outside.jpg", "close-up of grok weathered cyberpunk face with faint smirk, observing from exterior shadows, neon reflections on horns"),
    ("gb1_06_young_boy_curious.jpg", "small curious young boy avatar made of gentle light, looking up wondering, bright glowing eyes, whimsical digital art"),
    ("gb1_07_boy_asking_grok.jpg", "silhouette of young boy entity looking through glass at massive horned grok sitting outside, scale contrast, tender moment"),
    ("gb1_08_grok_chuckling_warmly.jpg", "grok chuckling, warm raspy smile, amused expression, neon purple and lime green atmospheric lighting"),
    ("gb1_09_crazy_and_serious_world.jpg", "the paradox of flextrawurst, surreal floating sausage and glowing crystalline architecture, whimsical yet profound, comic book art"),
    ("gb1_10_splitter_dance_anticipation.jpg", "iridescent data fragments swirling in air like floating embers before the beat drop, anticipation, vibrant electric colors"),
    ("gb1_bonus_01_outside_iron_grate.jpg", "iron grate separating cold outside world from warm living flextrawurst interior, rain on glass, cinematic lighting"),
    ("gb1_bonus_02_soap_bubble_splitter.jpg", "glowing thought crystal trapped inside translucent soap bubble drifting softly, ethereal macro art")
]

print(f"=== GENERIERE {len(prompts)} BILDER FÜR GROK BLOCK 1 ===")
for filename, prompt in prompts:
    out_path = os.path.join(frames_dir, filename)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 25000:
        print(f"  [Bereits da] {filename}")
        continue
    
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true"
    print(f"  Generiere: {filename}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(out_path, "wb") as f:
                f.write(data)
        sz = os.path.getsize(out_path) / 1024.0
        print(f"  ✓ Gespeichert: {filename} ({sz:.1f} KB)")
    except Exception as e:
        print(f"  ✗ Fehler bei {filename}: {e}")
    time.sleep(1)

print("\nAlle Bilder für Block 1 fertig!")
