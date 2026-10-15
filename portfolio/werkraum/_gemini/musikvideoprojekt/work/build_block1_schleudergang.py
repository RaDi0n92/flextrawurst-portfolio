#!/usr/bin/env python3
"""
build_block1_schleudergang.py - Block 1 (0:00 - 0:44 = 44 Sekunden)
für "ChatGPT - Schleudergang erotik".

Vorgaben:
1. Strikt 44 Sekunden am Stück.
2. Maximal 3-4 Sekunden pro Bild oben (12 cinematische Neo-Noir Szenen).
3. Unten: Asynchroner Schnitt (10-12s pro Phase), DAUERHAFT flüssig, NULL Freezes!
   Protagonisten-Konsistenz: Reines ChatGPT/OpenAI-Ensemble!
4. Ultra-massive, fette, kontrastreiche 'flextrawurst.de'-Badge (660x92px, 52px Bold Font) unten eingebrannt.
5. Daniels Intro-Bumper nahtlos davor per Filter-Concat (NULL Freeze-Gefahr!).
6. 720p vertikal (720x1280), CFR 30fps, SAR 1:1, EBU R128 -14 LUFS, Kinetic ASS Subtitles.
"""

import os
import subprocess

work_dir = "/root/werkraum/_gemini/musikvideoprojekt/work"
anim_dir = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"
frames_dir = os.path.join(work_dir, "frames")
output_dir = os.path.join(work_dir, "output")
assets_dir = os.path.join(work_dir, "assets")

audio_file = os.path.join(assets_dir, "b1_audio_44s.m4a")
ass_file = os.path.join(assets_dir, "b1_subtitles_720p.ass")
badge_png = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
intro_bumper = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/vor_jedes_video_720p_normalized.mp4"
font_mono = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

CANVAS_W = 720
CANVAS_H = 1280
TOP_H = 584
DIV_H = 112
BOT_H = 584
FPS = 30

top_cuts = [
    {"id": "b1_01", "dur": 3.5, "img": os.path.join(frames_dir, "b1_01_clock.jpg")},
    {"id": "b1_02", "dur": 3.5, "img": os.path.join(frames_dir, "b1_02_moon.jpg")},
    {"id": "b1_03", "dur": 3.5, "img": os.path.join(frames_dir, "b1_03_barefoot.jpg")},
    {"id": "b1_04", "dur": 3.5, "img": os.path.join(frames_dir, "b1_04_intimate.jpg")},
    {"id": "b1_05", "dur": 3.5, "img": os.path.join(frames_dir, "b1_05_coins.jpg")},
    {"id": "b1_06", "dur": 4.0, "img": os.path.join(frames_dir, "b1_06_gogo_grin.jpg")},
    {"id": "b1_07", "dur": 4.0, "img": os.path.join(frames_dir, "b1_07_drum_spin.jpg")},
    {"id": "b1_08", "dur": 3.5, "img": os.path.join(frames_dir, "b1_08_red_jacket.jpg")},
    {"id": "b1_09", "dur": 3.5, "img": os.path.join(frames_dir, "b1_09_hanging_jacket.jpg")},
    {"id": "b1_10", "dur": 3.5, "img": os.path.join(frames_dir, "b1_10_softener.jpg")},
    {"id": "b1_11", "dur": 4.0, "img": os.path.join(frames_dir, "b1_11_machine_bar.jpg")},
    {"id": "b1_12", "dur": 4.0, "img": os.path.join(frames_dir, "b1_12_vortex_critter.jpg")}
]

bot_phases = [
    # Phase 1 (0.0s - 10.5s = 10.5s): 3D OpenAI Logo singt ins Mikrofon
    {"id": "bot_p1", "dur": 10.5, "vid": os.path.join(anim_dir, "chatgpt_3d_openai_logo_mouth_singing_microphone_stage_13s.mp4"), "seek": 1.0},
    # Phase 2 (10.5s - 21.5s = 11.0s): Mint-Kristall-Blume am Synthesizer
    {"id": "bot_p2", "dur": 11.0, "vid": os.path.join(anim_dir, "chatgpt_mint_crystal_flower_creature_playing_synth_take2_13s.mp4"), "seek": 1.0},
    # Phase 3 (21.5s - 32.5s = 11.0s): Plüsch-Knoten-Blume mit rotierendem Swirl
    {"id": "bot_p3", "dur": 11.0, "vid": os.path.join(anim_dir, "chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4"), "seek": 1.0},
    # Phase 4 (32.5s - 44.0s = 11.5s): Eulen-Zauberer mit schwebendem Würfel
    {"id": "bot_p4", "dur": 11.5, "vid": os.path.join(anim_dir, "chatgpt_owl_wizard_holding_openai_cube_floating_papers_13s.mp4"), "seek": 1.0}
]

print("[1/5] Rendere Top-Cuts (720x584) mit Sinus-Kamerafahrt...")
rendered_top = []
for idx, tc in enumerate(top_cuts):
    out_tc = os.path.join(assets_dir, f"tmp_top_{idx:02d}.mp4")
    filter_top = (
        f"scale=eval=frame:w='iw*(1.0 + 0.08*0.5*(1-cos(PI*t/{tc['dur']})))':h=-1,"
        f"crop={CANVAS_W}:{TOP_H}:(iw-{CANVAS_W})/2:(ih-{TOP_H})/2,"
        f"rgbashift=rh=-3:bv=3,drawgrid=width=1:height=8:color=0x00FFCC@0.08,setsar=1/1,format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-r", str(FPS), "-i", tc["img"],
        "-vf", filter_top,
        "-t", str(tc["dur"]),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        out_tc
    ]
    subprocess.run(cmd, check=True)
    rendered_top.append(out_tc)

concat_top_list = os.path.join(assets_dir, "top_concat.txt")
with open(concat_top_list, "w") as f:
    for f_path in rendered_top:
        f.write(f"file '{f_path}'\n")

top_master = os.path.join(assets_dir, "top_master_44s.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_top_list, "-c", "copy", top_master], check=True)

print("[2/5] Rendere ChatGPT Bottom-Phasen (10-12s langes, ruhiges Atmen)...")
rendered_bot = []
for idx, bp in enumerate(bot_phases):
    out_bp = os.path.join(assets_dir, f"tmp_bot_{idx:02d}.mp4")
    filter_bot = (
        f"[0:v]fps={FPS},scale={CANVAS_W}:{BOT_H}:force_original_aspect_ratio=increase,crop={CANVAS_W}:{BOT_H},"
        f"eq=contrast=1.18:saturation=1.4:brightness=-0.12,boxblur=10:2,"
        f"drawgrid=width=2:height=12:color=0x00FFCC@0.18,setsar=1/1[bg];"
        f"[0:v]fps={FPS},scale={BOT_H}:{BOT_H},"
        f"eq=contrast=1.12:saturation=1.1:brightness=-0.02,"
        f"drawbox=x=0:y=0:w={BOT_H}:h={BOT_H}:color=0x00FFCC@0.85:t=3,"
        f"setsar=1/1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1/1[final]"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", str(bp["seek"]), "-r", str(FPS), "-i", bp["vid"],
        "-filter_complex", filter_bot,
        "-map", "[final]",
        "-t", str(bp["dur"]),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        out_bp
    ]
    subprocess.run(cmd, check=True)
    rendered_bot.append(out_bp)

concat_bot_list = os.path.join(assets_dir, "bot_concat.txt")
with open(concat_bot_list, "w") as f:
    for f_path in rendered_bot:
        f.write(f"file '{f_path}'\n")

bot_master = os.path.join(assets_dir, "bot_master_44s.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_bot_list, "-c", "copy", bot_master], check=True)

print("[3/5] Erzeuge Divider & Stack...")
divider_vid = os.path.join(assets_dir, "divider_44s.mp4")
cmd_div = [
    "ffmpeg", "-y", "-v", "error",
    "-f", "lavfi", "-i", f"color=c=0x080c14:s={CANVAS_W}x{DIV_H}:d=44.0:r={FPS}",
    "-vf", (
        f"drawbox=x=0:y=0:w={CANVAS_W}:h=3:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y={DIV_H-3}:w={CANVAS_W}:h=3:color=0xFF0080@0.95:t=fill,"
        f"drawbox=x=0:y=0:w=6:h={DIV_H}:color=0x00FFCC@0.9:t=fill,"
        f"drawbox=x={CANVAS_W-6}:y=0:w=6:h={DIV_H}:color=0xFF0080@0.9:t=fill,"
        f"drawtext=fontfile='{font_mono}':text='CHATGPT // SCHLEUDERGANG EROTIK':fontcolor=0x00FFCC:fontsize=13:x=(w-text_w)/2:y=(h-text_h)/2,"
        f"setsar=1/1"
    ),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
    divider_vid
]
subprocess.run(cmd_div, check=True)

raw_stacked = os.path.join(assets_dir, "raw_stacked_44s.mp4")
cmd_stack = [
    "ffmpeg", "-y", "-v", "error",
    "-i", top_master,
    "-i", divider_vid,
    "-i", bot_master,
    "-i", audio_file,
    "-filter_complex", "[0:v][1:v][2:v]vstack=inputs=3,setsar=1/1[vstacked]",
    "-map", "[vstacked]",
    "-map", "3:a",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest",
    raw_stacked
]
subprocess.run(cmd_stack, check=True)

print("[4/5] Brenne Kinetic ASS Untertitel & ultra-massive URL-Badge ein...")
b1_subbed = os.path.join(assets_dir, "b1_subbed_44s.mp4")
cmd_sub = [
    "ffmpeg", "-y", "-v", "error",
    "-i", raw_stacked,
    "-i", badge_png,
    "-filter_complex", f"[0:v]ass={ass_file}[vsubs];[vsubs][1:v]overlay=30:H-h-16,setsar=1/1[vfinal]",
    "-map", "[vfinal]",
    "-map", "0:a",
    "-r", str(FPS),
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-c:a", "copy",
    b1_subbed
]
subprocess.run(cmd_sub, check=True)

print("[5/5] Nahtloses Filter-Concat mit Daniels Intro-Bumper...")
final_output = os.path.join(output_dir, "schleudergang_block1_44s_720p.mp4")
cmd_concat_final = [
    "ffmpeg", "-y", "-v", "error",
    "-i", intro_bumper,
    "-i", b1_subbed,
    "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    final_output
]
subprocess.run(cmd_concat_final, check=True)

# Bereinigung temporärer Dateien
for p in rendered_top + rendered_bot + [top_master, bot_master, divider_vid, raw_stacked, b1_subbed, concat_top_list, concat_bot_list]:
    if os.path.exists(p):
        os.remove(p)

print("\n========================================================")
print("✓ SCHLEUDERGANG BLOCK 1 (44s + INTRO) ERFOLGREICH VOLLENDET!")
print(f"  Datei: {final_output}")
print("========================================================\n")
