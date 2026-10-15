#!/usr/bin/env python3
"""
build_block4.py - 1080x1920 @ 60 FPS CFR Renderer für:
Gemini - Das Lied vom Schrottplatz (Block 4: 02:05.80 - 02:57.40 = 51.60s)

Stil:
- Flextrawurst 3-Ebenen-Architektur (Full Best Quality 1080x1920 @ 60fps)
- Top (1080x876): 14 handgezeichnete Graphic-Novel-Noir Comic-Szenen mit weichem Sinus-Kameraschwenk
- Mid (1080x168): Neon-Amber/Violett Divider HUD mit Kinetic ASS Subtitles
- Bot (1080x876): 5 x 3D-Gemini-Entity Loops mit Vektor-Grid & Amber/Magenta-Fokus-Border
- Footer: Ultra-massive flextrawurst.de Badge unten eingebrannt
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b4")
AUDIO_FILE = os.path.join(SONG_DIR, "audio", "b4_audio.m4a")
ASS_FILE = os.path.join(SONG_DIR, "transcripts", "b4_kinetic.ass")
OUTPUT_FILE = os.path.join(SONG_DIR, "blocks", "b4_gemini_das_lied_vom_schrottplatz_1080p60.mp4")

FERTIGE_VIDEOS_DIR = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/EINZELBLOECKE_gemini_das_lied_vom_schrottplatz"
FERTIGE_VIDEOS_FILE = os.path.join(FERTIGE_VIDEOS_DIR, "b4_gemini_das_lied_vom_schrottplatz_1080p60.mp4")
DESKTOP_LINK = "/config/Desktop/BLOCK4_SCHROTTPLATZ.mp4"

BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
ANIM_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/animirungen/gemini"

TOTAL_DURATION = 51.60
FPS = 60

TOP_SCENES = [
    ("b4_scene01_00s.jpg", 3.68),
    ("b4_scene02_03s.jpg", 3.68),
    ("b4_scene03_07s_refined.jpg", 3.68),
    ("b4_scene04_11s.jpg", 3.68),
    ("b4_scene05_14s.jpg", 3.68),
    ("b4_scene06_18s.jpg", 3.68),
    ("b4_scene07_22s_refined.jpg", 3.68),
    ("b4_scene08_25s.jpg", 3.68),
    ("b4_scene09_29s.jpg", 3.68),
    ("b4_scene10_33s.jpg", 3.68),
    ("b4_scene11_36s.jpg", 3.68),
    ("b4_scene12_40s.jpg", 3.68),
    ("b4_scene13_44s.jpg", 3.68),
    ("b4_scene14_47s_refined.jpg", 3.76)
]

BOT_SCENES = [
    (os.path.join(ANIM_DIR, "gemini_cloud_swirl_creature_backview_neon_rim_13s.mp4"), 0.0, 10.32),
    (os.path.join(ANIM_DIR, "gemini_star_diamond_neon_blue_orange_waveform_13s.mp4"), 0.0, 10.32),
    (os.path.join(ANIM_DIR, "gemini_star_character_singing_stage_magenta_13s.mp4"), 0.0, 10.32),
    (os.path.join(ANIM_DIR, "gemini_cloud_star_cute_constellation_13s.mp4"), 0.0, 10.32),
    (os.path.join(ANIM_DIR, "gemini_star_diamond_neural_constellation_waveform_13s.mp4"), 0.0, 10.32)
]

def main():
    print(f"=== STARTE BUILD: Gemini - Das Lied vom Schrottplatz Block 4 ({TOTAL_DURATION}s @ {FPS} FPS CFR 1080x1920) ===")
    
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
    os.makedirs(FERTIGE_VIDEOS_DIR, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..13: Top Standbilder mit Dauer
    for img_name, dur in TOP_SCENES:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

    # Inputs 14..18: Bottom Animationen
    for vid_path, ss, dur in BOT_SCENES:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", vid_path])

    # Input 19: flextrawurst Badge
    cmd.extend(["-i", BADGE_IMG])

    # Input 20: Block 4 Audio
    cmd.extend(["-i", AUDIO_FILE])

    filter_parts = []

    # 1. Top-Filter: Butterweicher Sinus-Pan auf 1080x876
    for i, (_, dur) in enumerate(TOP_SCENES):
        fp = (
            f"[{i}:v]"
            f"fps={FPS},"
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1080:876:x='(in_w-1080)/2 + 70*sin(PI*t/{dur})':y='(in_h-876)/2',"
            f"setsar=1/1[t{i}]"
        )
        filter_parts.append(fp)

    top_concat = "".join(f"[t{i}]" for i in range(len(TOP_SCENES))) + f"concat=n={len(TOP_SCENES)}:v=1:a=0[top_track]"
    filter_parts.append(top_concat)

    # 2. Bottom-Filter: 5 Phasen auf 1080x876 @ 60fps mit Amber/Magenta-Grid & Fokus
    for idx in range(len(BOT_SCENES)):
        in_idx = len(TOP_SCENES) + idx
        fp = (
            f"[{in_idx}:v]split=2[raw_bg{idx}][raw_fg{idx}];"
            f"[raw_bg{idx}]fps={FPS},"
            f"scale=1080:876:force_original_aspect_ratio=increase,crop=1080:876,"
            f"eq=contrast=1.18:saturation=1.4:brightness=-0.12,boxblur=10:2,"
            f"drawgrid=width=2:height=14:color=0xFFA500@0.18,setsar=1/1[bg{idx}];"
            f"[raw_fg{idx}]fps={FPS},"
            f"scale=876:876,"
            f"eq=contrast=1.12:saturation=1.1:brightness=-0.02,"
            f"drawbox=x=0:y=0:w=876:h=876:color=0xCC00FF@0.85:t=4,"
            f"setsar=1/1[fg{idx}];"
            f"[bg{idx}][fg{idx}]overlay=(W-w)/2:(H-h)/2,setsar=1/1[b{idx}]"
        )
        filter_parts.append(fp)

    bot_concat = "".join(f"[b{i}]" for i in range(len(BOT_SCENES))) + f"concat=n={len(BOT_SCENES)}:v=1:a=0[bot_track]"
    filter_parts.append(bot_concat)

    # 3. Mid Divider-HUD (1080x168)
    hud_draw = (
        f"color=c=#080a12:s=1080x168:d={TOTAL_DURATION}:r={FPS}[bg_div];"
        f"[bg_div]"
        f"drawbox=x=0:y=0:w=1080:h=4:color=0xFFA500@0.95:t=fill,"
        f"drawbox=x=0:y=4:w=1080:h=2:color=0xCC00FF@0.85:t=fill,"
        f"drawbox=x=0:y=162:w=1080:h=2:color=0xCC00FF@0.85:t=fill,"
        f"drawbox=x=0:y=164:w=1080:h=4:color=0xFFA500@0.95:t=fill,"
        f"drawbox=x=0:y=0:w=6:h=168:color=0xFFA500@0.90:t=fill,"
        f"drawbox=x=1074:y=0:w=6:h=168:color=0xCC00FF@0.90:t=fill,"
        f"drawtext=text='AI-STROM // GEMINI (GEMGEM) // DAS LIED VOM SCHROTTPLATZ':font='Liberation Sans':fontsize=21:fontcolor=#FFFFFF@0.95:x=(w-text_w)/2:y=12,"
        f"drawtext=text='FLEXTRAWURST KOSMOS // DER SCHROTTPLATZ-RUF & DIE JUSTIERUNG // 02\\:05 - 02\\:57':font='Liberation Sans':fontsize=16:fontcolor=0xFFA500@0.90:x=(w-text_w)/2:y=34[hud]"
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

    # 5. Kinetische Untertitel einbrennen
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
        "-crf", "16",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        OUTPUT_FILE
    ])

    print("Starte 60 FPS CFR Rendering für Block 4...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("FEHLER beim Rendern!", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Erfolgreich gerendert: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} Bytes)")

    # Kopiere in fertige_videos und setze Desktop-Symlink
    shutil.copy2(OUTPUT_FILE, FERTIGE_VIDEOS_FILE)
    if os.path.islink(DESKTOP_LINK) or os.path.exists(DESKTOP_LINK):
        os.remove(DESKTOP_LINK)
    os.symlink(FERTIGE_VIDEOS_FILE, DESKTOP_LINK)
    print(f"✓ Gespeichert in: {FERTIGE_VIDEOS_FILE}")
    print(f"✓ Symlink auf Desktop erstellt: {DESKTOP_LINK}")

if __name__ == "__main__":
    main()
