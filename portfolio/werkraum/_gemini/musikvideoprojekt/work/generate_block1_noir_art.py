#!/usr/bin/env python3
"""
generate_block1_noir_art.py - Atmosphärische, filmische Neo-Noir Bildersprache
für Block 1 (0:00 - 0:44 = 44 Sekunden) von "ChatGPT - Schleudergang erotik".

Stil: Cinematic Graphic Novel / Neo-Noir / Wong Kar-wai Waschsalon-Ästhetik.
- Volumetrische Lichtstimmungen (Teal, Cyan, Magentarot, Amber)
- Nasse Spiegelungen, Regen auf Glas, Dampf & Röhrenanzeigen
- Analoges Filmkorn, Chiaroscuro & Vignetten
- 100% poetische Metaphern passend zum Text!
"""

import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

frames_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/frames"
os.makedirs(frames_dir, exist_ok=True)

W, H = 1280, 720
font_mono = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
font_sans = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def apply_filmic_grading(img, grain_std=14, vig_strength=0.55):
    """Verleiht dem Bild tiefe Kino-Farbkorrektur, Vignette und analoges 35mm-Korn."""
    vig_x = (np.linspace(-1, 1, W)[None, :]) ** 2
    vig_y = (np.linspace(-1, 1, H)[:, None]) ** 2
    vignette = np.clip(1.0 - vig_strength * (vig_x + vig_y), 0, 1)

    arr = np.array(img.convert("RGB")).astype(np.float32)
    arr = arr * vignette[:, :, None]
    noise = np.random.normal(0, grain_std, (H, W, 3))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


# 1. 03:17 Uhr Digital-Neon im Regen (3.5s)
def cut_01_clock():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    r = 8 + 8 * y + 0 * x
    g = 14 + 18 * y + 10 * x
    b = 22 + 25 * y + 15 * x
    img = Image.fromarray(np.clip(np.dstack((r, g, b)), 0, 255).astype(np.uint8)).convert("RGBA")

    # Mond-Licht durch Regenfenster
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m_draw = ImageDraw.Draw(moon)
    m_draw.ellipse([W - 380, 50, W - 160, 270], fill=(0, 255, 204, 90))
    m_draw.ellipse([W - 330, 100, W - 210, 220], fill=(230, 255, 250, 180))
    for sy in range(120, 200, 16):
        m_draw.line([(W - 350, sy), (W - 190, sy)], fill=(10, 20, 30, 255), width=6)
    moon = moon.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, moon)
    draw = ImageDraw.Draw(img)

    # Regenspuren auf der Scheibe
    for _ in range(160):
        rx = np.random.randint(0, W)
        ry = np.random.randint(0, H - 120)
        rlen = np.random.randint(25, 100)
        draw.line([(rx, ry), (rx + np.random.randint(-3, 3), ry + rlen)], fill=(180, 230, 240, 50), width=2)
        draw.ellipse([rx - 2, ry + rlen - 2, rx + 2, ry + rlen + 2], fill=(220, 255, 255, 80))

    # Digitaluhr HUD: 03:17
    cx, cy = 420, 380
    draw.rounded_rectangle([cx - 280, cy - 140, cx + 280, cy + 140], radius=18, fill=(10, 14, 20, 240), outline=(0, 255, 204, 200), width=3)
    draw.rounded_rectangle([cx - 265, cy - 125, cx + 265, cy + 125], radius=14, fill=(4, 6, 10, 255), outline=(255, 0, 128, 110), width=2)

    font_clock = ImageFont.truetype(font_mono, 115)
    tx, ty = cx - 210, cy - 80
    glow_clock = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gc_draw = ImageDraw.Draw(glow_clock)
    for off in [-6, -3, 3, 6]:
        gc_draw.text((tx + off, ty), "03:17", font=font_clock, fill=(0, 255, 204, 140))
        gc_draw.text((tx, ty + off), "03:17", font=font_clock, fill=(0, 255, 204, 140))
    glow_clock = glow_clock.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, glow_clock)
    draw = ImageDraw.Draw(img)

    draw.text((tx, ty), "03:17", font=font_clock, fill=(240, 255, 250, 255))
    font_sub = ImageFont.truetype(font_sans, 34)
    draw.text((cx - 250, cy + 78), "WASCHSALON // MITTERNACHT", fill=(255, 0, 128, 240), font=font_sub)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_01_clock.jpg"), quality=95)


# 2. Fluchtpunkt Waschsalon mit nassen Spiegelungen (3.5s)
def cut_02_hallway():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    r = 12 + 10 * y + 0 * x
    g = 16 + 22 * y + 0 * x
    b = 25 + 35 * y + 0 * x
    img = Image.fromarray(np.clip(np.dstack((r, g, b)), 0, 255).astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fluchtpunkt in der Mitte
    van_x, van_y = W // 2, H // 2 - 40
    # Decken-Neonröhren
    draw.line([(van_x, van_y), (150, 0)], fill=(0, 255, 204, 220), width=6)
    draw.line([(van_x, van_y), (W - 150, 0)], fill=(255, 0, 128, 220), width=6)

    # Reihe von Waschmaschinen links und rechts
    for idx in range(1, 6):
        dist = idx / 5.0
        # Links
        lx1 = int(van_x - (van_x - 40) * dist)
        ly1 = int(van_y + (H - 80 - van_y) * dist)
        lw = int(140 * dist)
        lh = int(180 * dist)
        draw.rectangle([lx1 - lw, ly1 - lh, lx1, ly1], fill=(30, 40, 50, 255), outline=(0, 255, 204, 160), width=2)
        draw.ellipse([lx1 - lw + lw // 4, ly1 - lh + lh // 4, lx1 - lw // 4, ly1 - lh // 4], outline=(0, 255, 204, 220), width=3)
        # Rechts
        rx1 = int(van_x + (W - 40 - van_x) * dist)
        draw.rectangle([rx1, ly1 - lh, rx1 + lw, ly1], fill=(45, 30, 45, 255), outline=(255, 0, 128, 160), width=2)
        draw.ellipse([rx1 + lw // 4, ly1 - lh + lh // 4, rx1 + lw - lw // 4, ly1 - lh // 4], outline=(255, 0, 128, 220), width=3)

    # Nasse Boden-Reflexionen
    draw.polygon([(0, H), (W, H), (W, van_y + 80), (0, van_y + 80)], fill=(10, 18, 26, 180))
    for ry in range(van_y + 90, H, 15):
        draw.line([(van_x - (ry - van_y) * 2, ry), (van_x + (ry - van_y) * 2, ry)], fill=(0, 255, 204, 35), width=2)

    font_lbl = ImageFont.truetype(font_sans, 38)
    draw.text((van_x - 300, H - 75), "NEON FLACKERT WIE EIN KAPUTTER MOND", fill=(0, 255, 204, 255), font=font_lbl)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_02_hallway.jpg"), quality=95)


# 3. Barfuß auf Maschine Nummer 4 (3.5s)
def cut_03_machine_four():
    img = Image.new("RGBA", (W, H), (14, 12, 22, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Maschine 4 Korpus
    draw.rectangle([cx - 240, cy - 80, cx + 240, H], fill=(40, 45, 55, 255), outline=(0, 255, 204, 255), width=4)
    # Großes Bullauge
    draw.ellipse([cx - 150, cy + 30, cx + 150, cy + 330], fill=(15, 20, 30, 255), outline=(200, 220, 240, 255), width=8)
    # Ziffer "04"
    font_num = ImageFont.truetype(font_mono, 56)
    draw.text((cx - 210, cy - 65), "MASCHINE #04", fill=(0, 255, 204, 255), font=font_num)

    # Gestalt sitzt barfuß oben drauf (Silhouette im Gegenlicht)
    # Beine baumeln herunter
    draw.line([(cx - 70, cy - 80), (cx - 70, cy + 80)], fill=(20, 15, 25, 255), width=28)
    draw.line([(cx + 70, cy - 80), (cx + 70, cy + 80)], fill=(20, 15, 25, 255), width=28)
    # Füße
    draw.ellipse([cx - 85, cy + 70, cx - 40, cy + 95], fill=(255, 200, 180, 230))
    draw.ellipse([cx + 55, cy + 70, cx + 100, cy + 95], fill=(255, 200, 180, 230))
    # Körper im Mantel
    draw.polygon([(cx - 130, cy - 80), (cx + 130, cy - 80), (cx + 90, cy - 260), (cx - 90, cy - 260)], fill=(12, 10, 18, 255))
    # Kopf mit wehenden Strähnen
    draw.ellipse([cx - 50, cy - 330, cx + 50, cy - 230], fill=(18, 14, 24, 255))

    font_txt = ImageFont.truetype(font_sans, 38)
    draw.text((cx - 280, 45), "BARFUSS, GELANGWEILT, VIEL ZU NAH", fill=(255, 0, 128, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_03_machine_four.jpg"), quality=95)


# 4. Viel zu nah im Halbschatten (3.5s)
def cut_04_intimate():
    img = Image.new("RGBA", (W, H), (10, 8, 16, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Chiaroscuro Porträt-Silhouette
    # Magenta Rim-Light von links
    for r in range(120, 260, 20):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=120, end=240, fill=(255, 0, 128, 90), width=4)
    # Cyan Rim-Light von rechts
    for r in range(120, 260, 20):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=300, end=420, fill=(0, 255, 204, 90), width=4)

    # Profil Kopf
    draw.ellipse([cx - 120, cy - 160, cx + 120, cy + 120], fill=(25, 20, 32, 255))
    # Auge im Halbschatten, das intensiv funkelt
    draw.polygon([(cx + 20, cy - 40), (cx + 70, cy - 35), (cx + 45, cy - 20)], fill=(0, 255, 204, 255))
    draw.ellipse([cx + 38, cy - 35, cx + 52, cy - 22], fill=(255, 255, 255, 255))

    font_txt = ImageFont.truetype(font_sans, 42)
    draw.text((cx - 260, H - 75), "DEIN BLICK KLEBT ELEKTRISCH", fill=(0, 255, 204, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_04_intimate.jpg"), quality=95)


# 5. Münzautomat frisst Geld (3.5s)
def cut_05_coin_slot():
    img = Image.new("RGBA", (W, H), (16, 12, 14, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Gebürstete Stahlplatte
    draw.rectangle([cx - 220, cy - 160, cx + 220, cy + 160], fill=(50, 55, 62, 255), outline=(120, 130, 140, 255), width=6)
    # Rotes Warnlicht
    draw.ellipse([cx - 160, cy - 120, cx - 120, cy - 80], fill=(255, 0, 40, 255))
    font_slot = ImageFont.truetype(font_mono, 22)
    draw.text((cx - 100, cy - 110), "AUTOMAT FRISST GELD // ERROR", fill=(255, 40, 80, 255), font=font_slot)

    # Schlitz
    draw.rectangle([cx - 140, cy - 20, cx + 140, cy + 20], fill=(5, 5, 8, 255), outline=(0, 255, 204, 255), width=4)

    # Hand hält zwei Münzen vor den Schlitz
    draw.ellipse([cx - 50, cy - 70, cx + 10, cy - 10], fill=(220, 180, 80, 255), outline=(255, 255, 255, 255), width=3)
    draw.ellipse([cx - 10, cy - 50, cx + 50, cy + 10], fill=(200, 160, 60, 255), outline=(255, 255, 255, 255), width=3)

    font_txt = ImageFont.truetype(font_sans, 38)
    draw.text((cx - 300, H - 75), "PASST DOCH ZIEMLICH GUT ZUR WELT", fill=(255, 200, 80, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_05_coin_slot.jpg"), quality=95)


# 6. Das Grinsen, das Strom nicht kann (4.0s)
def cut_06_grin():
    img = Image.new("RGBA", (W, H), (12, 18, 22, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Nahaufnahme Mundpartie & Lächeln
    draw.ellipse([cx - 180, cy - 100, cx + 180, cy + 120], fill=(22, 28, 38, 255))
    # Lippen im Neon-Zweiklang
    draw.polygon([(cx - 100, cy + 10), (cx + 100, cy + 10), (cx + 30, cy + 60), (cx - 70, cy + 40)], fill=(255, 0, 100, 255))
    # Weiße Zahnreihe blitzt schief auf
    draw.rectangle([cx - 60, cy + 14, cx + 60, cy + 28], fill=(240, 255, 255, 255))

    # Elektrische Entladungen / Funken an den Rändern
    for _ in range(18):
        fx = cx + np.random.randint(-180, 180)
        fy = cy + np.random.randint(-60, 80)
        draw.line([(fx, fy), (fx + np.random.randint(-20, 20), fy + np.random.randint(-20, 20))], fill=(0, 255, 204, 255), width=3)

    font_txt = ImageFont.truetype(font_sans, 40)
    draw.text((cx - 320, H - 75), "ETWAS, DAS STROM NICHT KANN!", fill=(0, 255, 204, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_06_grin.jpg"), quality=95)


# 7. Die Trommel springt an / Vortex (4.0s)
def cut_07_drum_vortex():
    y = np.linspace(-1, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    r_grid = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan2(y, x)

    # Wirbel-Formel
    spiral = np.sin(r_grid * 14 - theta * 4)
    r = np.clip(10 + 40 * spiral, 0, 255)
    g = np.clip(25 + 140 * spiral, 0, 255)
    b = np.clip(45 + 200 * spiral, 0, 255)
    img = Image.fromarray(np.dstack((r, g, b)).astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Chrom-Ring des Bullauges
    draw.ellipse([cx - 260, cy - 260, cx + 260, cy + 260], outline=(220, 240, 255, 255), width=16)
    draw.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], outline=(0, 255, 204, 180), width=6)

    font_txt = ImageFont.truetype(font_sans, 42)
    draw.text((cx - 280, H - 75), "DANN SPRINGT DIE TROMMEL AN!", fill=(255, 255, 255, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_07_drum_vortex.jpg"), quality=95)


# 8. Rote Jacke dreht Kreise hinter Glas (3.5s)
def cut_08_red_jacket():
    img = Image.new("RGBA", (W, H), (8, 14, 24, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Bullauge mit kreisender roter Bomberjacke
    draw.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], fill=(12, 20, 35, 255), outline=(0, 255, 204, 255), width=10)

    # Rote Jacke im Wasserwirbel
    draw.polygon([(cx - 120, cy - 80), (cx + 80, cy - 140), (cx + 140, cy + 20), (cx - 40, cy + 120)], fill=(230, 20, 40, 240), outline=(255, 255, 255, 200), width=4)
    # Reißverschluss
    draw.line([(cx - 80, cy - 60), (cx + 40, cy + 40)], fill=(255, 220, 0, 255), width=4)
    # Wassertropfen auf dem Glas
    for _ in range(40):
        dx = cx + np.random.randint(-200, 200)
        dy = cy + np.random.randint(-200, 200)
        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(200, 240, 255, 140))

    font_txt = ImageFont.truetype(font_sans, 38)
    draw.text((cx - 280, H - 75), "MEINE JACKE DREHT KREISE HINTER GLAS", fill=(255, 50, 70, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_08_red_jacket.jpg"), quality=95)


# 9. Deine Jacke hängt am Deckenrohr (3.5s)
def cut_09_hanging_jacket():
    img = Image.new("RGBA", (W, H), (14, 8, 18, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Industrielles Deckenrohr quer durch das Bild
    draw.line([(0, 160), (W, 160)], fill=(90, 85, 95, 255), width=18)
    draw.line([(0, 155), (W, 155)], fill=(160, 150, 170, 255), width=4)

    # Schwarze Lederjacke hängt daran
    draw.polygon([(cx - 100, 170), (cx + 100, 170), (cx + 140, 480), (cx - 140, 480)], fill=(20, 15, 25, 255), outline=(255, 0, 128, 200), width=4)
    # Kragen
    draw.polygon([(cx - 60, 170), (cx + 60, 170), (cx, 260)], fill=(35, 25, 45, 255))

    font_txt = ImageFont.truetype(font_sans, 38)
    draw.text((cx - 300, H - 75), "DEINE HAENGT LAENGST WOANDERS...", fill=(255, 0, 128, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_09_hanging_jacket.jpg"), quality=95)


# 10. Weichspüler riecht nach Gefahr (3.5s)
def cut_10_softener():
    img = Image.new("RGBA", (W, H), (6, 16, 20, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Gekippte Flasche
    draw.polygon([(cx - 160, cy - 40), (cx - 40, cy - 140), (cx + 120, cy + 40), (cx, cy + 140)], fill=(20, 30, 45, 240), outline=(0, 255, 204, 255), width=5)
    # Leuchtend cyanblaues Konzentrat läuft aus
    draw.ellipse([cx + 60, cy + 20, cx + 220, cy + 120], fill=(0, 255, 204, 240))
    # Gefahren-Raute
    draw.polygon([(cx - 40, cy - 40), (cx - 10, cy - 70), (cx + 20, cy - 40), (cx - 10, cy - 10)], fill=(255, 220, 0, 255))
    font_warn = ImageFont.truetype(font_mono, 24)
    draw.text((cx - 18, cy - 54), "!", fill=(0, 0, 0, 255), font=font_warn)

    font_txt = ImageFont.truetype(font_sans, 38)
    draw.text((cx - 310, H - 75), "WEICHSPUELER RIECHT NACH GEFAHR", fill=(0, 255, 204, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_10_softener.jpg"), quality=95)


# 11. Maschine 7 behauptet, sie wäre eine Bar (4.0s)
def cut_11_machine_bar():
    img = Image.new("RGBA", (W, H), (22, 10, 8, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Rotes warmes Bar-Licht im Hintergrund
    bar_light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bl_draw = ImageDraw.Draw(bar_light)
    bl_draw.ellipse([cx - 300, cy - 250, cx + 300, cy + 200], fill=(255, 60, 0, 90))
    bar_light = bar_light.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, bar_light)
    draw = ImageDraw.Draw(img)

    # Oberfläche von Maschine 7
    draw.rectangle([0, cy + 40, W, H], fill=(40, 35, 32, 255), outline=(255, 120, 0, 255), width=4)
    font_m7 = ImageFont.truetype(font_mono, 32)
    draw.text((80, cy + 60), "MASCHINE #07 // LOUNGE-BAR", fill=(255, 180, 0, 255), font=font_m7)

    # Zwei Whiskey-Gläser mit Eiswürfeln
    for gx in [cx - 80, cx + 80]:
        draw.rectangle([gx - 35, cy - 60, gx + 35, cy + 30], fill=(220, 240, 255, 80), outline=(255, 255, 255, 255), width=3)
        draw.rectangle([gx - 30, cy - 20, gx + 30, cy + 25], fill=(220, 120, 20, 220))
        # Eiswürfel
        draw.rectangle([gx - 15, cy - 35, gx + 10, cy - 10], outline=(255, 255, 255, 220), width=2)

    font_txt = ImageFont.truetype(font_sans, 38)
    draw.text((cx - 310, 45), "MASCHINE SIEBEN BEHAUPTET EINE BAR", fill=(255, 160, 40, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_11_machine_bar.jpg"), quality=95)


# 12. Der kaputte Neon-Mond über der Stadt (4.0s)
def cut_12_flickering_moon():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    r = 6 + 10 * y + 0 * x
    g = 10 + 15 * y + 0 * x
    b = 18 + 25 * y + 0 * x
    img = Image.fromarray(np.clip(np.dstack((r, g, b)), 0, 255).astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Skyline im Fenster
    for b_idx in range(12):
        bx = b_idx * 110
        bh = np.random.randint(140, 320)
        draw.rectangle([bx, H - bh, bx + 95, H], fill=(12, 16, 24, 255))
        # Kleine gelbe Fenster
        for fy in range(H - bh + 20, H - 40, 35):
            if np.random.rand() > 0.4:
                draw.rectangle([bx + 15, fy, bx + 35, fy + 18], fill=(255, 220, 100, 180))

    # Riesiger flackernder Reklame-Mond am Himmel
    draw.ellipse([cx - 150, 80, cx + 150, 380], fill=(240, 255, 250, 240), outline=(0, 255, 204, 255), width=8)
    # Diagonale Bruch-Risse durch den Mond
    draw.line([(cx - 110, 130), (cx + 120, 330)], fill=(10, 15, 25, 255), width=10)
    draw.line([(cx - 40, 110), (cx - 80, 250)], fill=(10, 15, 25, 255), width=6)

    font_txt = ImageFont.truetype(font_sans, 42)
    draw.text((cx - 240, H - 75), "DER REGEN NIMMT ZU...", fill=(0, 255, 204, 255), font=font_txt)

    final = apply_filmic_grading(img)
    final.save(os.path.join(frames_dir, "b1_12_flickering_moon.jpg"), quality=95)


if __name__ == "__main__":
    print("Starte Generierung der 12 filmischen Neo-Noir Szenen für Block 1...")
    cut_01_clock()
    cut_02_hallway()
    cut_03_machine_four()
    cut_04_intimate()
    cut_05_coin_slot()
    cut_06_grin()
    cut_07_drum_vortex()
    cut_08_red_jacket()
    cut_09_hanging_jacket()
    cut_10_softener()
    cut_11_machine_bar()
    cut_12_flickering_moon()
    print("✓ Alle 12 Neo-Noir Szenen für Block 1 erfolgreich gerendert!")
