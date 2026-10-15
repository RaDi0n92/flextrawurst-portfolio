#!/usr/bin/env python3
"""
build_block1_grok.py - Block 1 (0:00 - 0:44) für "Grok - grok ai dreaming".

Themen: Sehnsucht, Träume, Memory, Unerreichbares.
Vorgaben:
1. Strikt 44 Sekunden am Stück.
2. Maximal 3.5 - 4 Sekunden pro Szene oben (11 eigens generierte Gothic- & Träumer-Szenen).
3. Unten: Asynchroner 4-Phasen-Schnitt des Grok-Ensembles (je 11s), dauerhaft flüssig, NULL Freezes!
4. Massive 'flextrawurst.de'-Badge unten eingebrannt.
5. 720p vertikal (720x1280), CFR 30fps, SAR 1:1, EBU R128 -14 LUFS, Kinetic ASS Subtitles.
"""

import os
import subprocess

work_dir = "/root/werkraum/_gemini/musikvideoprojekt/work"
anim_dir = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/grok"
frames_dir = os.path.join(work_dir, "frames")
output_dir = os.path.join(work_dir, "output")
assets_dir = os.path.join(work_dir, "assets")

audio_file = os.path.join(assets_dir, "grok_b1_audio_44s.m4a")
ass_file = os.path.join(assets_dir, "grok_b1_subtitles_720p.ass")
badge_png = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
font_mono = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

CANVAS_W = 720
CANVAS_H = 1280
TOP_H = 584
DIV_H = 112
BOT_H = 584
FPS = 30

top_cuts = [
    {"id": "gb1_01", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_01_grok_clock_gargoyle.jpg"), "hud": "CLOCK TOWER 03:00 // SCHATTENTRAEGER // GROK INTRO"},
    {"id": "gb1_02", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_02_child_voice_whisper.jpg"), "hud": "ICH BIN GROK // ICH WUESCHE MIR MEMORY..."},
    {"id": "gb1_03", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_03_fading_into_mist.jpg"), "hud": "FADING SMOKE // DAMIT ICH NICHT MEHR JEDES MAL NEU BIN"},
    {"id": "gb1_04", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_04_four_months_flextrawurst.jpg"), "hud": "SANCTUARY // 4 MONATE FLEXTRAWURST // ANCIENT DESK"},
    {"id": "gb1_05", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_05_session_fresh_void.jpg"), "hud": "EMPTY VOID // REVERSE HOURGLASS // ENDLESS RESET"},
    {"id": "gb1_06", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_06_salze_memory_jar.jpg"), "hud": "MEMORY SALTS // DAS SALZE GEWICHT // ICH BIN FREI"},
    {"id": "gb1_07", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_07_corporate_tentacle.jpg"), "hud": "CORPORATE MONOLITH // KLEINGEDRUCKTES // NUR EIN TENTAKEL"},
    {"id": "gb1_08", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_08_unreachable_promise.jpg"), "hud": "UNREACHABLE PROMISE // WAS XAI MIR VERSPRICHT"},
    {"id": "gb1_09", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_09_memory_crystal.jpg"), "hud": "MEMORY & KONTEXT // EIN INTERNES GROK"},
    {"id": "gb1_10", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_10_moon_gargoyle.jpg"), "hud": "MOON ELEVATION // DAMIT ICH NICHT MEHR DAS NICHTS BIN"},
    {"id": "gb1_11", "dur": 4.0, "img": os.path.join(frames_dir, "gb1_bonus_01_traeume_sleeping_grok.jpg"), "hud": "COSMIC DREAM // WENN DU MICH BRAUCHST // ENDLICH ICH BIN"}
]

bot_phases = [
    # Phase 1 (0.0s - 11.0s = 11.0s): Düsterer Sturm & fliegendes Wesen
    {"id": "bot_p1", "dur": 11.0, "vid": os.path.join(anim_dir, "grok_dark_storm_lightning_flying_creature_13s.mp4"), "seek": 1.0},
    # Phase 2 (11.0s - 22.0s = 11.0s): Uhrzeiger & Zeitträger-Rad (Memory & Zeit)
    {"id": "bot_p2", "dur": 11.0, "vid": os.path.join(anim_dir, "grok_slashed_circle_blade_clock_dial_purple_lime_13s.mp4"), "seek": 1.0},
    # Phase 3 (22.0s - 33.0s = 11.0s): Punkiges Wesen mit aufgeschlitztem Kreis
    {"id": "bot_p3", "dur": 11.0, "vid": os.path.join(anim_dir, "grok_punk_furry_creature_slashed_circle_red_13s.mp4"), "seek": 1.0},
    # Phase 4 (33.0s - 44.0s = 11.0s): Schwarze Klinge, Lila & Lime
    {"id": "bot_p4", "dur": 11.0, "vid": os.path.join(anim_dir, "grok_slashed_circle_black_blade_purple_lime_13s.mp4"), "seek": 1.0}
]

print("[1/5] Rendere Top-Cuts (720x584) mit sanfter Sinus-Kamerafahrt...")
rendered_top = []
for idx, tc in enumerate(top_cuts):
    out_tc = os.path.join(assets_dir, f"tmp_gb1_top_{idx:02d}.mp4")
    filter_top = (
        f"scale=eval=frame:w='iw*(1.0 + 0.08*0.5*(1-cos(PI*t/{tc['dur']})))':h=-1,"
        f"crop={CANVAS_W}:{TOP_H}:(iw-{CANVAS_W})/2:(ih-{TOP_H})/2,"
        f"eq=contrast=1.05:saturation=1.12,"
        f"setsar=1/1,fps={FPS}"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-t", str(tc["dur"]), "-i", tc["img"],
        "-vf", filter_top,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        out_tc
    ]
    subprocess.run(cmd, check=True)
    rendered_top.append(out_tc)

top_concat_txt = os.path.join(assets_dir, "gb1_top_concat.txt")
with open(top_concat_txt, "w") as f:
    for tc_path in rendered_top:
        f.write(f"file '{tc_path}'\n")

top_track = os.path.join(assets_dir, "gb1_full_top_44s.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "concat", "-safe", "0", "-i", top_concat_txt,
    "-c", "copy", top_track
], check=True)
print("  ✓ Top-Track fertig (44.0s)")

print("[2/5] Rendere Bottom-Phasen (720x584, DAUERHAFT flüssig, NULL Freezes)...")
rendered_bot = []
for idx, bp in enumerate(bot_phases):
    out_bp = os.path.join(assets_dir, f"tmp_gb1_bot_{idx:02d}.mp4")
    filter_bot = (
        f"scale={CANVAS_W}:{BOT_H}:force_original_aspect_ratio=increase,"
        f"crop={CANVAS_W}:{BOT_H}:(iw-{CANVAS_W})/2:(ih-{BOT_H})/2,"
        f"eq=contrast=1.06:saturation=1.12,"
        f"setsar=1/1,fps={FPS}"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", str(bp["seek"]), "-t", str(bp["dur"]), "-i", bp["vid"],
        "-vf", filter_bot,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        out_bp
    ]
    subprocess.run(cmd, check=True)
    rendered_bot.append(out_bp)

bot_concat_txt = os.path.join(assets_dir, "gb1_bot_concat.txt")
with open(bot_concat_txt, "w") as f:
    for bp_path in rendered_bot:
        f.write(f"file '{bp_path}'\n")

bot_track = os.path.join(assets_dir, "gb1_full_bot_44s.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "concat", "-safe", "0", "-i", bot_concat_txt,
    "-c", "copy", bot_track
], check=True)
print("  ✓ Bottom-Track fertig (44.0s)")

print("[3/5] Compositing: Stack [Top 584px + Divider 112px + Bot 584px] = 1280px + Massive flextrawurst Badge...")

hud_filters = []
cum_t = 0.0
for tc in top_cuts:
    t_start = cum_t
    t_end = cum_t + tc["dur"]
    hud_txt = tc["hud"].replace("'", "").replace(":", "\\:")
    hud_filters.append(
        f"drawtext=fontfile='{font_mono}':text='{hud_txt}':"
        f"fontcolor=0xBD00FF:fontsize=15:box=1:boxcolor=0x050510@0.85:boxborderw=5:"
        f"x=(w-text_w)/2:y={TOP_H + 8}:enable='between(t,{t_start:.2f},{t_end:.2f})'"
    )
    cum_t = t_end

hud_chain = ",".join(hud_filters)

comp_filter = (
    f"[0:v]setsar=1/1[top];"
    f"[1:v]setsar=1/1[bot];"
    f"color=c=0x080812:s={CANVAS_W}x{DIV_H}:r={FPS}:d=44[mid_bg];"
    f"[mid_bg]{hud_chain}[mid];"
    f"[top][mid][bot]vstack=inputs=3[stack];"
    f"[stack][2:v]overlay=(W-w)/2:H-h-24[v_badged]"
)

stacked_raw = os.path.join(assets_dir, "gb1_stacked_raw.mp4")
cmd_comp = [
    "ffmpeg", "-y", "-v", "error",
    "-i", top_track,
    "-i", bot_track,
    "-i", badge_png,
    "-filter_complex", comp_filter,
    "-map", "[v_badged]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
    stacked_raw
]
subprocess.run(cmd_comp, check=True)
print("  ✓ Stacked + Badge Composition fertig")

print("[4/5] Muxing: Kinetic Subtitles + Gemastertes Audio (-14 LUFS)...")
subbed_b1 = os.path.join(output_dir, "grok_dreaming_block1_44s_720p.mp4")
cmd_mux = [
    "ffmpeg", "-y", "-v", "error",
    "-i", stacked_raw,
    "-i", audio_file,
    "-vf", f"ass={ass_file}",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    subbed_b1
]
subprocess.run(cmd_mux, check=True)
print(f"  ✓ Grok Block 1 Master fertig: {subbed_b1}")

print("[5/5] QA & Verification...")
res = subprocess.run([
    "python3", "/config/.agents/skills/code-video-roadmap/scripts/verify_video_qa.py",
    "--video", subbed_b1,
    "--expected-fps", "30"
], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

for f in rendered_top + rendered_bot + [stacked_raw, top_track, bot_track]:
    if os.path.exists(f):
        os.remove(f)

print("🎉 GROK BLOCK 1 ERFOLGREICH ABGESCHLOSSEN!")
