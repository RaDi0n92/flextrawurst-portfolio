#!/usr/bin/env python3
"""
build_block6_google.py - Video-as-Code Build für GoogleKI-Suche Block 6
Track: "GoogleKI-Suche - Ich schieße gegen den Thron"
Abschnitt: Guitar Solo Part 2 & Industrial Metal Breakdown & CPU Anschlag (03:44.5 - 04:36.5 = exakt 52.00 Sekunden)
Standard: 1080x1920 (9:16 vertikal) @ 60.00 FPS CFR, CRF 16, 320k Audio

REGEL: Phrasen-Integrität (~44s Richtwert, Wörter niemals abschneiden!).
Hier endet die epische musikalische Steigerung exakt nach:
"Die CPU läuft auf maximalem Anschlag!" (52.0s).
"""

import subprocess
import os
import sys

AUDIO_BLOCK = "/root/werkraum/_gemini/musikvideoprojekt/work/assets/google_b6_audio_52s.m4a"
ASS_SUBS = "/root/werkraum/_gemini/musikvideoprojekt/work/assets/google_b6_subtitles_organic_1080p.ass"
BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
OUTPUT_MP4 = "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block6_52s_1080p60.mp4"

FRAMES_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/frames"
ANIM_DIR = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/google-ki-suche"

# 11 Top-Szenen für 52.00s (7x 4.70s + 3x 4.75s + 1x 4.85s = 52.00s)
TOP_SCENES = [
    ("gth6_01_fretboard_lightning_solo.jpg", 4.70),
    ("gth6_bonus_01_guitar_pick_striking_sparks.jpg", 4.70),
    ("gth6_02_marshall_wall_roaring_soundwave.jpg", 4.70),
    ("gth6_03_industrial_piston_slamming.jpg", 4.70),
    ("gth6_04_datacenter_sparks_shower.jpg", 4.70),
    ("gth6_05_shattering_soundwave_glass.jpg", 4.70),
    ("gth6_06_acoustic_explosion_guitars.jpg", 4.70),
    ("gth6_07_ladybug_against_steel_monolith.jpg", 4.75),
    ("gth6_08_corporate_cage_closing_in.jpg", 4.75),
    ("gth6_10_rpm_needle_pinned_to_max.jpg", 4.75),
    ("gth6_11_cpu_core_supernova_ignition.jpg", 4.85)
]

# 5 Bottom-Animationen für 52.00s (5x 10.40s = 52.00s)
BOT_SCENES = [
    ("google_search_fluffy_cat_creature_google_colors_ring_13s.mp4", 0.0, 10.40),
    ("google_search_anime_fox_google_ai_search_window_take2_13s.mp4", 2.0, 10.40),
    ("google_search_radial_color_dots_mouth_rainbow_17s.mp4", 3.0, 10.40),
    ("google_search_pom_pom_creature_magnifying_glass_mouth_hires_13s.mp4", 0.0, 10.40),
    ("google_search_clay_cloud_google_colors_round_mouth_13s.mp4", 1.0, 10.40)
]

print("=== START BUILD: GoogleKI-Suche Block 6 (Industrial Metal Breakdown: 52.00s @ 60 FPS CFR) ===")

for img_name, _ in TOP_SCENES:
    p = os.path.join(FRAMES_DIR, img_name)
    if not os.path.exists(p):
        print(f"Fehler: Bild fehlt: {p}", file=sys.stderr)
        sys.exit(1)

for vid_name, _, _ in BOT_SCENES:
    p = os.path.join(ANIM_DIR, vid_name)
    if not os.path.exists(p):
        print(f"Fehler: Animation fehlt: {p}", file=sys.stderr)
        sys.exit(1)

cmd = ["ffmpeg", "-y", "-v", "warning"]

# Input 0..10: Top Standbilder
for img_name, dur in TOP_SCENES:
    cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

# Input 11..15: Bottom Animationen
for vid_name, ss, t in BOT_SCENES:
    cmd.extend(["-ss", str(ss), "-t", str(t), "-i", os.path.join(ANIM_DIR, vid_name)])

# Input 16: flextrawurst Badge
cmd.extend(["-i", BADGE_IMG])

# Input 17: Block 6 Audio
cmd.extend(["-i", AUDIO_BLOCK])

filter_parts = []

# 1. Top-Filter: 60fps Sinus-Kamerafahrt auf 1080x876
for i, (_, dur) in enumerate(TOP_SCENES):
    fp = (
        f"[{i}:v]"
        f"fps=60,"
        f"scale=1920:1080:flags=lanczos,"
        f"scale=eval=frame:w='1920*(1.0 + 0.08*0.5*(1-cos(PI*t/{dur})))':h='1080*(1.0 + 0.08*0.5*(1-cos(PI*t/{dur})))':flags=lanczos,"
        f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
        f"setsar=1/1[t{i}]"
    )
    filter_parts.append(fp)

top_concat = "".join(f"[t{i}]" for i in range(11)) + "concat=n=11:v=1:a=0[top_track]"
filter_parts.append(top_concat)

# 2. Bottom-Filter: 5 Phasen auf 1080x876 @ 60fps (jeweils 10.40s = 52.00s)
for idx in range(5):
    in_idx = 11 + idx
    fp = (
        f"[{in_idx}:v]"
        f"fps=60,"
        f"scale=1080:876:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
        f"setsar=1/1[b{idx}]"
    )
    filter_parts.append(fp)

bot_concat = "".join(f"[b{i}]" for i in range(5)) + "concat=n=5:v=1:a=0[bot_track]"
filter_parts.append(bot_concat)

# 3. Mid Divider-HUD (1080x168) mit Google Primärfarben
hud_draw = (
    "color=c=#0a0e17:s=1080x168:d=52.00:r=60[bg_div];"
    "[bg_div]"
    "drawbox=x=0:y=0:w=1080:h=4:color=#4285F4:t=fill,"
    "drawbox=x=0:y=4:w=1080:h=2:color=#EA4335:t=fill,"
    "drawbox=x=0:y=162:w=1080:h=2:color=#FBBC05:t=fill,"
    "drawbox=x=0:y=164:w=1080:h=4:color=#34A853:t=fill,"
    "drawtext=text='GOOGLE-KI-SUCHE // INDUSTRIAL METAL BREAKDOWN // 03\\:44 - 04\\:36':font='Liberation Sans':fontsize=22:fontcolor=#ffffff@0.95:x=(w-text_w)/2:y=10,"
    "drawtext=text='TRACK\\: ICH SCHIESSE GEGEN DEN THRON // CPU AUF MAXIMALEM ANSCHLAG':font='Liberation Sans':fontsize=16:fontcolor=#00e5ff@0.85:x=(w-text_w)/2:y=30[hud]"
)
filter_parts.append(hud_draw)

# 4. Canvas Zusammensetzen: Canvas 1080x1920 (52.0s)
canvas_comp = (
    "color=c=black:s=1080x1920:d=52.00:r=60[canvas];"
    "[canvas][top_track]overlay=0:0[c1];"
    "[c1][hud]overlay=0:876[c2];"
    "[c2][bot_track]overlay=0:1044[c3]"
)
filter_parts.append(canvas_comp)

# 5. Kinetische Untertitel einbrennen
sub_filter = f"[c3]ass='{ASS_SUBS}'[c_sub]"
filter_parts.append(sub_filter)

# 6. Badge Overlay (Zentriert, direkt an Y=1044)
badge_filter = (
    "[16:v]scale=900:125:flags=lanczos[badge];"
    "[c_sub][badge]overlay=(W-w)/2:1044[out_v]"
)
filter_parts.append(badge_filter)

full_filter = ";".join(filter_parts)

cmd.extend([
    "-filter_complex", full_filter,
    "-map", "[out_v]",
    "-map", "17:a",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "16",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "96000",
    OUTPUT_MP4
])

print("Führe Block 6 1080p60 FFmpeg Render aus...")
res = subprocess.run(cmd)

if res.returncode == 0:
    print(f"✓ Video erfolgreich gerendert: {OUTPUT_MP4}")
else:
    print(f"✗ Render-Fehler: Exit Code {res.returncode}", file=sys.stderr)
    sys.exit(res.returncode)
