#!/usr/bin/env python3
"""
build_video.py - 1080p60 Full Master Renderer fuer:
Daniel (flextrawurst) - brillant-beim-werden (10_daniel_brillant_beim_werden)
Dauer: 31.60s @ 60.00 fps CFR

Layout (1080x1920):
- 0000 - 0876 (876px): Top Track (8 Flextrawurst Brillant-Szenen mit 60fps Sinus-Zoom)
- 0876 - 1044 (168px): Middle HUD mit Trackheader & kinetischen ASS Untertiteln (MarginV: 905)
- 1044 - 1792 (748px / 876px): Daniel Animationen (Muted, 492x876 Fokusbox + Blur-BG)
- 1792 - 1920 (128px): flextrawurst.de Neon-Badge
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/10_daniel_brillant_beim_werden"
FRAMES_DIR = os.path.join(BASE_DIR, "frames")
ANIM_DIR = os.path.join(BASE_DIR, "anim_muted")
AUDIO_FILE = os.path.join(BASE_DIR, "audio", "daniel_brillant_beim_werden_14lufs.m4a")
ASS_FILE = os.path.join(BASE_DIR, "transcripts", "kinetic.ass")
BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"

TOTAL_DURATION = 31.60
FPS = 60

TOP_SCENES = [
    ("s01_roher_fels_streitstrom.jpg", 3.95),
    ("s02_fissur_archivkluft.jpg", 3.95),
    ("s03_werkraum_facettenschliff.jpg", 3.95),
    ("s04_prisma_zwischenraum.jpg", 3.95),
    ("s05_splitter_schwarm.jpg", 3.95),
    ("s06_brillant_beim_werden.jpg", 3.95),
    ("s07_traumkueste_lichtfluss.jpg", 3.95),
    ("s08_first_surface_vollendung.jpg", 3.95)
]

ANIM_FULLBODY = os.path.join(ANIM_DIR, "daniel_fullbody_muted.mp4")
ANIM_CLOSEUP = os.path.join(ANIM_DIR, "daniel_closeup_muted.mp4")

BOT_SCENES = [
    (ANIM_FULLBODY, 0.0, 7.90),
    (ANIM_CLOSEUP, 0.0, 7.90),
    (ANIM_FULLBODY, 0.0, 7.90),
    (ANIM_CLOSEUP, 0.0, 7.90)
]

OUTPUT_LOCAL = os.path.join(BASE_DIR, "blocks", "10_daniel_brillant_beim_werden_FULL_MASTER_1080p60.mp4")
MASTER_ARCHIV_FULL = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/full-videos/10_daniel_brillant_beim_werden_FULL_MASTER_1080p60.mp4"
MASTER_ARCHIV_ROOT = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/10_daniel_brillant_beim_werden_FULL_MASTER_1080p60.mp4"
AUDIT_LOCAL = os.path.join(BASE_DIR, "audits", "master_audit_frames")

def main():
    print(f"=== STARTE RENDER: Daniel - brillant-beim-werden ({TOTAL_DURATION}s @ {FPS} FPS CFR 1080x1920) ===")
    
    # 1. Validierung
    for img_name, _ in TOP_SCENES:
        p = os.path.join(FRAMES_DIR, img_name)
        if not os.path.exists(p) or os.path.getsize(p) < 10000:
            print(f"FEHLER: Bild fehlt oder ungueltig: {p}", file=sys.stderr)
            sys.exit(1)

    for vid_path, _, _ in BOT_SCENES:
        if not os.path.exists(vid_path):
            print(f"FEHLER: Animation fehlt: {vid_path}", file=sys.stderr)
            sys.exit(1)

    if not os.path.exists(AUDIO_FILE):
        print(f"FEHLER: Audio fehlt: {AUDIO_FILE}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(ASS_FILE):
        print(f"FEHLER: Untertitel fehlen: {ASS_FILE}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(BADGE_IMG):
        print(f"FEHLER: Badge fehlt: {BADGE_IMG}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_LOCAL), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_ARCHIV_FULL), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_ARCHIV_ROOT), exist_ok=True)
    os.makedirs(AUDIT_LOCAL, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..7: Top Standbilder mit Dauer
    for img_name, dur in TOP_SCENES:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

    # Inputs 8..11: Bottom Animationen
    for vid_path, ss, dur in BOT_SCENES:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", vid_path])

    # Input 12: flextrawurst Badge
    cmd.extend(["-i", BADGE_IMG])

    # Input 13: Audio
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

    top_concat_in = "".join([f"[t{i}]" for i in range(len(TOP_SCENES))])
    filter_parts.append(f"{top_concat_in}concat=n={len(TOP_SCENES)}:v=1:a=0[top_track]")

    # 2. Bottom-Filter: Daniel Animation in 1080x876 einpassen
    b_offset = len(TOP_SCENES)
    for j, (_, _, dur) in enumerate(BOT_SCENES):
        idx = b_offset + j
        fp_bg = (
            f"[{idx}:v]"
            f"fps={FPS},"
            f"scale=1080:876:force_original_aspect_ratio=increase:flags=bicubic,"
            f"crop=1080:876,"
            f"boxblur=25:5,"
            f"colorchannelmixer=aa=1.0:rr=0.45:gg=0.45:bb=0.45,"
            f"setsar=1/1[bgb{j}]"
        )
        filter_parts.append(fp_bg)

        fp_fg = (
            f"[{idx}:v]"
            f"fps={FPS},"
            f"scale=492:876:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"drawbox=x=0:y=0:w=492:h=876:color=0xFFA500@0.70:t=3,"
            f"setsar=1/1[fgb{j}]"
        )
        filter_parts.append(fp_fg)

        fp_merge = f"[bgb{j}][fgb{j}]overlay=x=294:y=0:shortest=1[b{j}]"
        filter_parts.append(fp_merge)

    bot_concat_in = "".join([f"[b{j}]" for j in range(len(BOT_SCENES))])
    filter_parts.append(f"{bot_concat_in}concat=n={len(BOT_SCENES)}:v=1:a=0[bot_track]")

    # 3. Middle HUD (1080x168) mit Amber-Begrenzungen und Trackheader
    hud_fp = (
        f"color=c=#0A0B10:s=1080x168:d={TOTAL_DURATION}:r={FPS}[hud_raw];"
        f"[hud_raw]"
        f"drawbox=x=0:y=0:w=1080:h=3:color=0xFFA500@0.85:t=fill,"
        f"drawbox=x=0:y=165:w=1080:h=3:color=0xFFA500@0.85:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
        f"text='FLEISCH & CODE // DANIEL (FLEXTRAWURST) // BRILLANT BEIM WERDEN':"
        f"fontcolor=0xFFFFFF@0.95:fontsize=24:x=(w-text_w)/2:y=16,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
        f"text='SPRACHSPIEL & RHETORIK // 00\\:00 - 00\\:31':"
        f"fontcolor=0xFFA500@0.90:fontsize=18:x=(w-text_w)/2:y=48,"
        f"setsar=1/1[mid_hud]"
    )
    filter_parts.append(hud_fp)

    # 4. Badge unten
    badge_idx = b_offset + len(BOT_SCENES)
    audio_idx = badge_idx + 1

    badge_fp = f"[{badge_idx}:v]fps={FPS},scale=1080:128:flags=lanczos,setsar=1/1[badge]"
    filter_parts.append(badge_fp)

    # 5. Vertikaler Stack: Canvas 1080x1920
    stack_fp = (
        f"color=c=black:s=1080x1920:d={TOTAL_DURATION}:r={FPS}[canvas];"
        f"[canvas][top_track]overlay=x=0:y=0[cv1];"
        f"[cv1][mid_hud]overlay=x=0:y=876[cv2];"
        f"[cv2][bot_track]overlay=x=0:y=1044[cv3];"
        f"[cv3][badge]overlay=x=0:y=1792[cv_full];"
        f"[cv_full]subtitles='{ASS_FILE}'[v_out]"
    )
    filter_parts.append(stack_fp)

    full_filter = ";\n".join(filter_parts)

    cmd.extend([
        "-filter_complex", full_filter,
        "-map", "[v_out]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-t", str(TOTAL_DURATION),
        OUTPUT_LOCAL
    ])

    print("Starte FFmpeg Render-Prozess (1080p60 CRF 16)...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"✗ FFmpeg Fehler: Exit Code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    file_size_mb = os.path.getsize(OUTPUT_LOCAL) / (1024 * 1024)
    print(f"\n✓ Video erfolgreich gerendert: {OUTPUT_LOCAL} ({file_size_mb:.1f} MB)")

    # Archivieren
    shutil.copy2(OUTPUT_LOCAL, MASTER_ARCHIV_FULL)
    print(f"✓ Kopiert nach: {MASTER_ARCHIV_FULL}")
    shutil.copy2(OUTPUT_LOCAL, MASTER_ARCHIV_ROOT)
    print(f"✓ Kopiert nach: {MASTER_ARCHIV_ROOT}")

    # Kontrollbilder
    audit_points = [
        ("master_audit_01_start_002s.jpg", 2.0),
        ("master_audit_02_vocal_008s.jpg", 8.0),
        ("master_audit_03_mid_015s.jpg", 15.0),
        ("master_audit_04_peak_022s.jpg", 22.0),
        ("master_audit_05_outro_028s.jpg", 28.0)
    ]
    print(f"\nExtrahiere {len(audit_points)} Kontrollbilder...")
    for name, ss in audit_points:
        loc_path = os.path.join(AUDIT_LOCAL, name)
        c = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-i", OUTPUT_LOCAL, "-frames:v", "1", "-q:v", "2", loc_path]
        subprocess.run(c)
        if os.path.exists(loc_path):
            print(f"  ✓ Frame @ {ss:5.1f}s -> {loc_path}")

    print("\n=== MASTER-BUILD VOLLSTAENDIG ERFOLGREICH ABGESCHLOSSEN! ===")

if __name__ == "__main__":
    main()
