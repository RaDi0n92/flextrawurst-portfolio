#!/usr/bin/env python3
"""
build_block2.py - 1080x1920 @ 60 FPS CFR Renderer fuer:
Daniel (flextrawurst) - Sei allzeit bereit und ganz bei mir
Block 2: 00:49.40 - 01:44.80 (55.40s)

Architektur:
- Full Best Quality 1080x1920 @ 60fps CFR
- Top (1080x876): 10 handgefertigte tactile Szenen mit Sinus-Kamerafahrt
- Mid (1080x168): Neon-Gold / Violett Divider HUD mit Kinetic ASS Subtitles
- Bot (1080x876): 6 x 9.233s animierte Daniel-Clips (Fullbody Cosmic Vortex & Closeup SAVAGE Mug)
- Footer: flextrawurst.de Massive Badge unten eingebrannt
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/08_daniel_sei_allzeit_bereit_und_ganz_bei_mir"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b2")
AUDIO_FILE = os.path.join(SONG_DIR, "audio", "b2_audio.m4a")
ASS_FILE = os.path.join(SONG_DIR, "transcripts", "b2_kinetic.ass")
OUTPUT_FILE = os.path.join(SONG_DIR, "blocks", "b2_daniel_sei_allzeit_bereit_1080p60.mp4")

ARCHIV_DIR = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/EINZELBLOECKE_DANIEL"
ARCHIV_FILE = os.path.join(ARCHIV_DIR, "b2_daniel_sei_allzeit_bereit_1080p60.mp4")

BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
ANIM_DIR = os.path.join(SONG_DIR, "anim_muted")
ANIM_CLOSEUP = os.path.join(ANIM_DIR, "daniel_closeup_muted.mp4")
ANIM_FULLBODY = os.path.join(ANIM_DIR, "daniel_fullbody_muted.mp4")

TOTAL_DURATION = 55.40
FPS = 60

TOP_SCENES = [
    ("b2_scene01_00s.jpg", 5.54),
    ("b2_scene02_05s.jpg", 5.54),
    ("b2_scene03_11s.jpg", 5.54),
    ("b2_scene04_16s.jpg", 5.54),
    ("b2_scene05_22s.jpg", 5.54),
    ("b2_scene06_27s.jpg", 5.54),
    ("b2_scene07_33s.jpg", 5.54),
    ("b2_scene08_38s.jpg", 5.54),
    ("b2_scene09_44s.jpg", 5.54),
    ("b2_scene10_49s.jpg", 5.54)
]

BOT_SCENES = [
    (ANIM_FULLBODY, 0.0, 9.233),
    (ANIM_CLOSEUP, 0.0, 9.233),
    (ANIM_FULLBODY, 0.0, 9.233),
    (ANIM_CLOSEUP, 0.0, 9.233),
    (ANIM_FULLBODY, 0.0, 9.233),
    (ANIM_CLOSEUP, 0.0, 9.235)
]

def main():
    print(f"=== STARTE BUILD: Daniel - Sei allzeit bereit Block 2 ({TOTAL_DURATION}s @ {FPS} FPS CFR 1080x1920) ===")
    
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
    os.makedirs(ARCHIV_DIR, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..9: Top Standbilder mit Dauer
    for img_name, dur in TOP_SCENES:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

    # Inputs 10..15: Bottom Animationen
    for vid_path, ss, dur in BOT_SCENES:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", vid_path])

    # Input 16: flextrawurst Badge
    cmd.extend(["-i", BADGE_IMG])

    # Input 17: Block 2 Audio
    cmd.extend(["-i", AUDIO_FILE])

    filter_parts = []

    # 1. Top-Filter: 60fps Sinus-Kamerafahrt auf 1080x876
    for i, (_, dur) in enumerate(TOP_SCENES):
        fp = (
            f"[{i}:v]"
            f"fps={FPS},"
            f"scale=1920:1080:flags=lanczos,"
            f"scale=eval=frame:w='1920*(1.0 + 0.06*0.5*(1-cos(PI*t/{dur})))':h='1080*(1.0 + 0.06*0.5*(1-cos(PI*t/{dur})))':flags=lanczos,"
            f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
            f"setsar=1/1[t{i}]"
        )
        filter_parts.append(fp)

    top_concat = "".join(f"[t{i}]" for i in range(len(TOP_SCENES))) + f"concat=n={len(TOP_SCENES)}:v=1:a=0[top_track]"
    filter_parts.append(top_concat)

    # 2. Bottom-Filter: 6 Phasen auf 1080x876 @ 60fps mit zentriertem Daniel + geblurt/gegridetem Hintergrund
    for idx in range(len(BOT_SCENES)):
        in_idx = len(TOP_SCENES) + idx
        fp = (
            f"[{in_idx}:v]fps={FPS},"
            f"scale=1080:876:force_original_aspect_ratio=increase,crop=1080:876,"
            f"eq=contrast=1.15:saturation=1.3:brightness=-0.12,boxblur=15:3,"
            f"drawgrid=width=2:height=14:color=0xCC00FF@0.15,setsar=1/1[bg{idx}];"
            f"[{in_idx}:v]fps={FPS},"
            f"scale=492:876:flags=lanczos,"
            f"eq=contrast=1.08:saturation=1.1:brightness=0.0,"
            f"drawbox=x=0:y=0:w=492:h=876:color=0xFFA500@0.70:t=3,"
            f"setsar=1/1[fg{idx}];"
            f"[bg{idx}][fg{idx}]overlay=294:0,setsar=1/1[b{idx}]"
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
        f"drawtext=text='FLEISCH & CODE // DANIEL (FLEXTRAWURST) // SEI ALLZEIT BEREIT':font='Liberation Sans':fontsize=21:fontcolor=#FFFFFF@0.95:x=(w-text_w)/2:y=12,"
        f"drawtext=text='BLOCK 2 // VON ZANKERN BIS ALLZEITBEREIT // 00\\:49 - 01\\:44':font='Liberation Sans':fontsize=16:fontcolor=0xFFA500@0.90:x=(w-text_w)/2:y=34[hud]"
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

    # 6. Massive flextrawurst.de Badge am unteren Bildschirmrand
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
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-shortest",
        OUTPUT_FILE
    ])

    print("Starte 60fps Full Best Quality Rendering fuer Block 2 (CRF 16)...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("FEHLER beim Rendering!", file=sys.stderr)
        sys.exit(res.returncode)

    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\n✓ BLOCK 2 ERFOLGREICH GERENDERT ({file_size_mb:.1f} MB): {OUTPUT_FILE}")

    # Ins Archiv kopieren
    shutil.copy2(OUTPUT_FILE, ARCHIV_FILE)
    print(f"  -> Kopiert ins Archiv: {ARCHIV_FILE}")

    # Kontrollframes fuer QA Audit extrahieren (nur intern im Song-Ordner!)
    audits_dir = os.path.join(SONG_DIR, "audits", "b2_frames")
    os.makedirs(audits_dir, exist_ok=True)
    check_times = [6.0, 18.0, 32.0, 48.0]
    for ct in check_times:
        c_out = os.path.join(audits_dir, f"audit_{int(ct):02d}s.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-v", "warning",
            "-ss", str(ct),
            "-i", OUTPUT_FILE,
            "-vframes", "1",
            "-q:v", "2",
            c_out
        ])
        if os.path.exists(c_out):
            print(f"  -> Kontrollframe extrahiert ({ct}s): {c_out}")

if __name__ == "__main__":
    main()
