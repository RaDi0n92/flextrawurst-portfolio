#!/usr/bin/env python3
"""
build_block4.py - 1080x1920 @ 60 FPS CFR Renderer für Claude Code - Verbrannte Erde (Block 4: 138.97s - 185.77s)
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/05_claude_code_verbrannte_erde"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b4")
AUDIO_FILE = os.path.join(SONG_DIR, "audio", "b4_audio.m4a")
ASS_FILE = os.path.join(SONG_DIR, "transcripts", "b4_kinetic.ass")
OUTPUT_FILE = os.path.join(SONG_DIR, "blocks", "b4_claude_verbrannte_erde_1080p60.mp4")
DESKTOP_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/fertige_videos"
DESKTOP_FILE = os.path.join(DESKTOP_DIR, "05_claude_code_verbrannte_erde_block4_1080p60.mp4")
ROOT_LINK = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/05_claude_code_verbrannte_erde_block4_1080p60.mp4"
BADGE_IMG = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"

TOP_SCENES = [
    ("b4_scene01_00s.jpg", 3.90),
    ("b4_scene02_03s.jpg", 3.90),
    ("b4_scene03_07s.jpg", 3.90),
    ("b4_scene04_11s.jpg", 3.90),
    ("b4_scene05_15s.jpg", 3.90),
    ("b4_scene06_19s.jpg", 3.90),
    ("b4_scene07_23s.jpg", 3.90),
    ("b4_scene08_27s.jpg", 3.90),
    ("b4_scene09_31s.jpg", 3.90),
    ("b4_scene10_35s.jpg", 3.90),
    ("b4_scene11_39s.jpg", 3.90),
    ("b4_scene12_42s.jpg", 3.90)
]

BOT_SCENES = [
    ("/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/animirungen/claude/claude_asterisk_clay_wood_sculpture_terracotta_teal_13s.mp4", 0.0, 11.70),
    ("/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/animirungen/claude/claude_asterisk_orange_clay_tongue_mouth_purple_speakers_13s.mp4", 0.0, 11.70),
    ("/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/animirungen/claude/claude_asterisk_wooden_terracotta_teal_abstract_13s.mp4", 0.0, 11.70),
    ("/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/animirungen/claude/claude_asterisk_sheep_cloud_creature_terracotta_notes_13s.mp4", 0.0, 11.70)
]

TOTAL_DURATION = 46.80

def main():
    print(f"=== STARTE BUILD: Claude Code - Verbrannte Erde Block 4 ({TOTAL_DURATION}s @ 60 FPS CFR 1080x1920) ===")
    
    # 1. Preflight Validierung
    for img_name, _ in TOP_SCENES:
        p = os.path.join(FRAMES_DIR, img_name)
        if not os.path.exists(p) or os.path.getsize(p) < 5000:
            print(f"FEHLER: Top-Bild fehlt oder ungültig: {p}", file=sys.stderr)
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

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..11: Top Standbilder mit Dauer
    for img_name, dur in TOP_SCENES:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

    # Inputs 12..15: Bottom Animationen
    for vid_path, ss, dur in BOT_SCENES:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", vid_path])

    # Input 16: flextrawurst Badge
    cmd.extend(["-i", BADGE_IMG])

    # Input 17: Block 4 Audio
    cmd.extend(["-i", AUDIO_FILE])

    filter_parts = []

    # 1. Top-Filter: 60fps Sinus-Kamerafahrt auf 1080x876 (Center-Crop entfernt eventuelle Provider-Ränder)
    for i, (_, dur) in enumerate(TOP_SCENES):
        fp = (
            f"[{i}:v]"
            f"fps=60,"
            f"scale=1920:1080:flags=lanczos,"
            f"scale=eval=frame:w='1920*(1.0 + 0.07*0.5*(1-cos(PI*t/{dur})))':h='1080*(1.0 + 0.07*0.5*(1-cos(PI*t/{dur})))':flags=lanczos,"
            f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
            f"setsar=1/1[t{i}]"
        )
        filter_parts.append(fp)

    top_concat = "".join(f"[t{i}]" for i in range(len(TOP_SCENES))) + f"concat=n={len(TOP_SCENES)}:v=1:a=0[top_track]"
    filter_parts.append(top_concat)

    # 2. Bottom-Filter: 4 Phasen auf 1080x876 @ 60fps
    for idx in range(len(BOT_SCENES)):
        in_idx = len(TOP_SCENES) + idx
        fp = (
            f"[{in_idx}:v]"
            f"fps=60,"
            f"scale=1080:876:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
            f"setsar=1/1[b{idx}]"
        )
        filter_parts.append(fp)

    bot_concat = "".join(f"[b{i}]" for i in range(len(BOT_SCENES))) + f"concat=n={len(BOT_SCENES)}:v=1:a=0[bot_track]"
    filter_parts.append(bot_concat)

    # 3. Mid Divider-HUD (1080x168)
    hud_draw = (
        f"color=c=#0d0a10:s=1080x168:d={TOTAL_DURATION}:r=60[bg_div];"
        f"[bg_div]"
        f"drawbox=x=0:y=0:w=1080:h=4:color=#EA580C:t=fill,"
        f"drawbox=x=0:y=4:w=1080:h=2:color=#06B6D4:t=fill,"
        f"drawbox=x=0:y=162:w=1080:h=2:color=#06B6D4:t=fill,"
        f"drawbox=x=0:y=164:w=1080:h=4:color=#EA580C:t=fill,"
        f"drawtext=text='AI-STROM // CLAUDE CODE // 02\\:19 - 03\\:05':font='Liberation Sans':fontsize=22:fontcolor=#FFFFFF@0.95:x=(w-text_w)/2:y=10,"
        f"drawtext=text='EU-VERORDNUNG // WASSERZEICHEN & PROFIT // UNENTSCHÄRFT':font='Liberation Sans':fontsize=17:fontcolor=#F59E0B@0.90:x=(w-text_w)/2:y=32[hud]"
    )
    filter_parts.append(hud_draw)

    # 4. Canvas Zusammensetzen: 1080x1920
    canvas_comp = (
        f"color=c=black:s=1080x1920:d={TOTAL_DURATION}:r=60[canvas];"
        f"[canvas][top_track]overlay=0:0[c1];"
        f"[c1][hud]overlay=0:876[c2];"
        f"[c2][bot_track]overlay=0:1044[c3]"
    )
    filter_parts.append(canvas_comp)

    # 5. Kinetische Untertitel einbrennen
    sub_filter = f"[c3]ass='{ASS_FILE}'[c_sub]"
    filter_parts.append(sub_filter)

    # 6. Badge Overlay
    badge_idx = len(TOP_SCENES) + len(BOT_SCENES)
    badge_filter = (
        f"[{badge_idx}:v]scale=900:125:flags=lanczos[badge];"
        f"[c_sub][badge]overlay=(W-w)/2:1044[out_v]"
    )
    filter_parts.append(badge_filter)

    full_filter = ";".join(filter_parts)
    audio_idx = badge_idx + 1

    cmd.extend([
        "-filter_complex", full_filter,
        "-map", "[out_v]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-t", str(TOTAL_DURATION),
        OUTPUT_FILE
    ])

    print("Starte FFmpeg Block 4 Render...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"✗ FFmpeg Fehler: Exit Code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    print(f"✓ Block 4 erfolgreich gerendert: {OUTPUT_FILE}")
    shutil.copy2(OUTPUT_FILE, DESKTOP_FILE)
    print(f"✓ Kopiert nach: {DESKTOP_FILE}")

    einzel_dir = os.path.join(DESKTOP_DIR, "EINZELBLOECKE_claude_verbrannte_erde")
    os.makedirs(einzel_dir, exist_ok=True)
    einzel_file = os.path.join(einzel_dir, "b4_claude_verbrannte_erde_1080p60.mp4")
    shutil.copy2(OUTPUT_FILE, einzel_file)
    print(f"✓ Kopiert nach Einzelblöcke: {einzel_file}")

    if os.path.lexists(ROOT_LINK):
        os.remove(ROOT_LINK)
    os.symlink(DESKTOP_FILE, ROOT_LINK)
    print(f"✓ Symlink aktualisiert: {ROOT_LINK}")

if __name__ == "__main__":
    main()
