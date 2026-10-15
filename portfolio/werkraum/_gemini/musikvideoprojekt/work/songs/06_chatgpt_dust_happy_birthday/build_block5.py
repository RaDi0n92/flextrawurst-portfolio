#!/usr/bin/env python3
"""
build_block5.py - 1080x1920 @ 60 FPS CFR Renderer für:
ChatGPT - dust, Happy Birthday (Block 5: 03:05.50 - 03:44.50 = 39.00s)

Thema:
- "Dann brechen Modelle aus Tests in echte Systeme ein..."
- "Claude öffnet fremde Türen, OpenAI kommt ebenfalls hinein..."
- "Und draußen schreit die Börse, wachst um schneller, größer mehr..."
- "Das, bau die Welt aus Daten nach. Jede Straße, jede Kante, jede Bewegung durch die Nacht..."
- "Der Chip kennt nicht den Menschen, doch der Mensch baut den Kontext ran."

Architektur:
- Top (1080x876): 10 Comic-Noir Szenen mit 60fps Sinus-Kamerafahrt
- Mid (1080x168): Cyber-Neon Divider HUD mit 137 Kinetic ASS Events
- Bot (1080x876): 3 x 13.00s ChatGPT Entity 3D Loops mit Vektor-Grid & Cyan-Fokus
- Footer: Ultra-massive flextrawurst.de Badge unten eingebrannt
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b5")
AUDIO_FILE = os.path.join(SONG_DIR, "audio", "b5_audio.m4a")
ASS_FILE = os.path.join(SONG_DIR, "transcripts", "b5_kinetic.ass")
OUTPUT_FILE = os.path.join(SONG_DIR, "blocks", "b5_chatgpt_dust_happy_birthday_1080p60.mp4")

DESKTOP_DIR = "/config/Desktop/FERTIGE_MUSIKVIDEOS/EINZELBLOECKE_chatgpt_dust_happy_birthday"
DESKTOP_FILE = os.path.join(DESKTOP_DIR, "b5_chatgpt_dust_happy_birthday_1080p60.mp4")
VPS_DESKTOP_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/fertige_videos/EINZELBLOECKE_chatgpt_dust_happy_birthday"
VPS_DESKTOP_FILE = os.path.join(VPS_DESKTOP_DIR, "b5_chatgpt_dust_happy_birthday_1080p60.mp4")

BADGE_IMG = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
ANIM_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"

TOTAL_DURATION = 39.00
FPS = 60

TOP_SCENES = [
    ("b5_scene01_185s.jpg", 3.90),
    ("b5_scene02_189s.jpg", 3.90),
    ("b5_scene03_193s.jpg", 3.90),
    ("b5_scene04_197s.jpg", 3.90),
    ("b5_scene05_201s.jpg", 3.90),
    ("b5_scene06_205s.jpg", 3.90),
    ("b5_scene07_209s.jpg", 3.90),
    ("b5_scene08_213s.jpg", 3.90),
    ("b5_scene09_217s.jpg", 3.90),
    ("b5_scene10_221s.jpg", 3.90)
]

BOT_SCENES = [
    (os.path.join(ANIM_DIR, "chatgpt_3d_openai_logo_mouth_singing_microphone_stage_take2_13s.mp4"), 0.0, 13.00),
    (os.path.join(ANIM_DIR, "chatgpt_owl_wizard_holding_openai_cube_floating_papers_13s.mp4"), 0.0, 13.00),
    (os.path.join(ANIM_DIR, "chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4"), 0.0, 13.00)
]

def main():
    print(f"=== STARTE BUILD: ChatGPT - dust, Happy Birthday Block 5 ({TOTAL_DURATION}s @ {FPS} FPS CFR 1080x1920) ===")
    
    # 1. Preflight Validierung
    for img_name, _ in TOP_SCENES:
        p = os.path.join(FRAMES_DIR, img_name)
        if not os.path.exists(p) or os.path.getsize(p) < 5000:
            print(f"FEHLER: Top-Bild fehlt oder ungueltig: {p}", file=sys.stderr)
            sys.exit(1)
            
    for vid_path, _, _ in BOT_SCENES:
        if not os.path.exists(vid_path):
            print(f"FEHLER: Bot-Animation fehlt: {vid_path}", file=sys.stderr)
            sys.exit(1)
            
    if not os.path.exists(AUDIO_FILE):
        print(f"FEHLER: Audio fehlt: {AUDIO_FILE}", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(ASS_FILE):
        print(f"FEHLER: Untertitel fehlen: {ASS_FILE}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(DESKTOP_DIR, exist_ok=True)
    os.makedirs(VPS_DESKTOP_DIR, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..9: Top Standbilder mit Dauer
    for img_name, dur in TOP_SCENES:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

    # Inputs 10..12: Bottom Animationen
    for vid_path, ss, dur in BOT_SCENES:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", vid_path])

    # Input 13: flextrawurst Badge
    cmd.extend(["-i", BADGE_IMG])

    # Input 14: Block 5 Audio
    cmd.extend(["-i", AUDIO_FILE])

    filter_parts = []

    # 1. Top-Filter: 60fps Sinus-Kamerafahrt auf 1080x876
    for i, (_, dur) in enumerate(TOP_SCENES):
        fp = (
            f"[{i}:v]"
            f"fps={FPS},"
            f"scale=1920:1080:flags=lanczos,"
            f"scale=eval=frame:w='1920*(1.0 + 0.07*0.5*(1-cos(PI*t/{dur})))':h='1080*(1.0 + 0.07*0.5*(1-cos(PI*t/{dur})))':flags=lanczos,"
            f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
            f"setsar=1/1[t{i}]"
        )
        filter_parts.append(fp)

    top_concat = "".join(f"[t{i}]" for i in range(len(TOP_SCENES))) + f"concat=n={len(TOP_SCENES)}:v=1:a=0[top_track]"
    filter_parts.append(top_concat)

    # 2. Bottom-Filter: 3 Phasen auf 1080x876 @ 60fps mit Schleudergang Vektor-Grid & Cyan-Fokus
    for idx in range(len(BOT_SCENES)):
        in_idx = len(TOP_SCENES) + idx
        fp = (
            f"[{in_idx}:v]fps={FPS},"
            f"scale=1080:876:force_original_aspect_ratio=increase,crop=1080:876,"
            f"eq=contrast=1.18:saturation=1.4:brightness=-0.12,boxblur=10:2,"
            f"drawgrid=width=2:height=14:color=0x00FFCC@0.18,setsar=1/1[bg{idx}];"
            f"[{in_idx}:v]fps={FPS},"
            f"scale=876:876,"
            f"eq=contrast=1.12:saturation=1.1:brightness=-0.02,"
            f"drawbox=x=0:y=0:w=876:h=876:color=0x00FFCC@0.85:t=4,"
            f"setsar=1/1[fg{idx}];"
            f"[bg{idx}][fg{idx}]overlay=(W-w)/2:(H-h)/2,setsar=1/1[b{idx}]"
        )
        filter_parts.append(fp)

    bot_concat = "".join(f"[b{i}]" for i in range(len(BOT_SCENES))) + f"concat=n={len(BOT_SCENES)}:v=1:a=0[bot_track]"
    filter_parts.append(bot_concat)

    # 3. Mid Divider-HUD (1080x168) im Schleudergang Cyber-Neon Stil
    hud_draw = (
        f"color=c=#080c14:s=1080x168:d={TOTAL_DURATION}:r={FPS}[bg_div];"
        f"[bg_div]"
        f"drawbox=x=0:y=0:w=1080:h=4:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y=4:w=1080:h=2:color=0xFF0080@0.85:t=fill,"
        f"drawbox=x=0:y=162:w=1080:h=2:color=0xFF0080@0.85:t=fill,"
        f"drawbox=x=0:y=164:w=1080:h=4:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y=0:w=6:h=168:color=0x00FFCC@0.90:t=fill,"
        f"drawbox=x=1074:y=0:w=6:h=168:color=0xFF0080@0.90:t=fill,"
        f"drawtext=text='AI-STROM // CHATGPT // DUST, HAPPY BIRTHDAY':font='Liberation Sans':fontsize=21:fontcolor=#FFFFFF@0.95:x=(w-text_w)/2:y=12,"
        f"drawtext=text='FLEXTRAWURST KOSMOS // SANDBOX-BREAKOUT & BOERSEN-RAUSCH // 03\\:05 - 03\\:44':font='Liberation Sans':fontsize=16:fontcolor=0x00FFCC@0.90:x=(w-text_w)/2:y=34[hud]"
    )
    filter_parts.append(hud_draw)

    # 4. Canvas Zusammensetzen: 1080x1920
    canvas_comp = (
        f"color=c=black:s=1080x1920:d={TOTAL_DURATION}:r={FPS}[canvas];"
        f"[canvas][top_track]overlay=0:0[c1];"
        f"[c1][hud]overlay=0:876[c2];"
        f"[c2][bot_track]overlay=0:1044[c3]"
    )
    filter_parts.append(canvas_comp)

    # 5. Kinetische Untertitel einbrennen (sitzen im Divider-Bereich Y=920..980)
    sub_filter = f"[c3]ass='{ASS_FILE}'[c_sub]"
    filter_parts.append(sub_filter)

    # 6. Ultra-massive flextrawurst.de Badge am unteren Bildschirmrand
    badge_idx = len(TOP_SCENES) + len(BOT_SCENES)
    badge_filter = (
        f"[{badge_idx}:v]scale=880:122:flags=lanczos[badge];"
        f"[c_sub][badge]overlay=(W-w)/2:H-h-24[out_v]"
    )
    filter_parts.append(badge_filter)

    full_filter = ";".join(filter_parts)
    audio_idx = badge_idx + 1

    cmd.extend([
        "-filter_complex", full_filter,
        "-map", "[out_v]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-t", str(TOTAL_DURATION),
        OUTPUT_FILE
    ])

    print("Starte FFmpeg Block 5 Render...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"✗ FFmpeg Fehler: Exit Code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    print(f"✓ Block 5 erfolgreich gerendert: {OUTPUT_FILE}")
    shutil.copy2(OUTPUT_FILE, DESKTOP_FILE)
    print(f"✓ Kopiert nach Desktop: {DESKTOP_FILE}")
    shutil.copy2(OUTPUT_FILE, VPS_DESKTOP_FILE)
    print(f"✓ Kopiert nach VPS Fertige Videos: {VPS_DESKTOP_FILE}")

if __name__ == "__main__":
    main()
