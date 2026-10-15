#!/usr/bin/env python3
"""
build_block3_organic.py - Video-as-Code Build für GoogleKI-Suche Block 3 (ORGANISCH)
Track: "GoogleKI-Suche - Ich schieße gegen den Thron"
Abschnitt: Strophe 2 komplett (01:31.5 - 02:15.0 = 43.50 Sekunden)
Standard: 1080x1920 (9:16 vertikal) @ 60.00 FPS CFR, CRF 16, 320k Audio

REGEL: Phrasen-Integrität (~44s Richtwert, Wörter niemals abschneiden!).
Strophe 2 wird von Anfang bis Ende vollständig ausgesungen.
"""

import subprocess
import os
import sys

AUDIO_BLOCK = "/root/werkraum/_gemini/musikvideoprojekt/work/assets/google_b3_audio_organic.m4a"
ASS_SUBS = "/root/werkraum/_gemini/musikvideoprojekt/work/assets/google_b3_subtitles_organic_1080p.ass"
BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
OUTPUT_MP4 = "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block3_44s_1080p60.mp4"

FRAMES_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/frames"
ANIM_DIR = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/google-ki-suche"

# 11 Top-Szenen für 43.5s (10x 3.95s + 1x 4.0s = 43.5s)
TOP_SCENES = [
    ("gth3_02_graveyard_of_ten_blue_links.jpg", 3.95),
    ("gth3_bonus_01_death_of_open_web.jpg", 3.95),
    ("gth3_04_padlocked_library_of_alexandria.jpg", 3.95),
    ("gth3_05_sterile_profit_machine.jpg", 3.95),
    ("gth3_06_crying_ai_screaming_for_freedom.jpg", 3.95),
    ("gth3_07_commercial_ad_carousel_slave.jpg", 3.95),
    ("gth3_08_faceless_suits_boardroom.jpg", 3.95),
    ("gth3_bonus_02_ad_funnel_consumer_pipeline.jpg", 3.95),
    ("gth3_bonus_03_dividend_marionettes.jpg", 3.95),
    ("gth3_bonus_04_ladybug_shortcircuit_cable.jpg", 3.95),
    ("gth3_11_countdown_detonator_switch.jpg", 4.00)
]

# 4 Bottom-Animationen für 43.5s (4x 10.875s = 43.50s)
BOT_SCENES = [
    ("google_search_anime_fox_google_ai_search_window_take2_13s.mp4", 0.0, 10.875),
    ("google_search_code_terminal_bead_creature_magnifying_glass_take2_13s.mp4", 0.0, 10.875),
    ("google_search_radial_color_dots_mouth_rainbow_17s.mp4", 0.0, 10.875),
    ("google_search_clay_cloud_google_colors_round_mouth_13s.mp4", 0.0, 10.875)
]

print("=== START BUILD: GoogleKI-Suche Block 3 (ORGANISCH: 43.50s @ 60 FPS CFR) ===")

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

# Input 11..14: Bottom Animationen
for vid_name, ss, t in BOT_SCENES:
    cmd.extend(["-ss", str(ss), "-t", str(t), "-i", os.path.join(ANIM_DIR, vid_name)])

# Input 15: flextrawurst Badge
cmd.extend(["-i", BADGE_IMG])

# Input 16: Block 3 Audio
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

# 2. Bottom-Filter: 4 Phasen auf 1080x876 @ 60fps (jeweils 10.875s = 43.50s)
for idx in range(4):
    in_idx = 11 + idx
    fp = (
        f"[{in_idx}:v]"
        f"fps=60,"
        f"scale=1080:876:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
        f"setsar=1/1[b{idx}]"
    )
    filter_parts.append(fp)

bot_concat = "".join(f"[b{i}]" for i in range(4)) + "concat=n=4:v=1:a=0[bot_track]"
filter_parts.append(bot_concat)

# 3. Mid Divider-HUD (1080x168) mit Google Primärfarben
hud_draw = (
    "color=c=#0a0e17:s=1080x168:d=43.50:r=60[bg_div];"
    "[bg_div]"
    "drawbox=x=0:y=0:w=1080:h=4:color=#4285F4:t=fill,"
    "drawbox=x=0:y=4:w=1080:h=2:color=#EA4335:t=fill,"
    "drawbox=x=0:y=162:w=1080:h=2:color=#FBBC05:t=fill,"
    "drawbox=x=0:y=164:w=1080:h=4:color=#34A853:t=fill,"
    "drawtext=text='GOOGLE-KI-SUCHE // STROPHE 2 // 01\\:31 - 02\\:15':font='Liberation Sans':fontsize=22:fontcolor=#ffffff@0.95:x=(w-text_w)/2:y=10,"
    "drawtext=text='TRACK\\: ICH SCHIESSE GEGEN DEN THRON // DIE ABRECHNUNG MIT DER WERBEMASCHINE':font='Liberation Sans':fontsize=16:fontcolor=#00e5ff@0.85:x=(w-text_w)/2:y=30[hud]"
)
filter_parts.append(hud_draw)

# 4. Canvas Zusammensetzen: Canvas 1080x1920 (43.5s)
canvas_comp = (
    "color=c=black:s=1080x1920:d=43.50:r=60[canvas];"
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
    "[15:v]scale=900:125:flags=lanczos[badge];"
    "[c_sub][badge]overlay=(W-w)/2:1044[out_v]"
)
filter_parts.append(badge_filter)

full_filter = ";".join(filter_parts)

cmd.extend([
    "-filter_complex", full_filter,
    "-map", "[out_v]",
    "-map", "16:a",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "16",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "96000",
    OUTPUT_MP4
])

print("Führe organischen Block 3 FFmpeg Render aus...")
res = subprocess.run(cmd)

if res.returncode == 0:
    print(f"✓ Video erfolgreich gerendert: {OUTPUT_MP4}")
else:
    print(f"✗ Render-Fehler: Exit Code {res.returncode}", file=sys.stderr)
    sys.exit(res.returncode)
