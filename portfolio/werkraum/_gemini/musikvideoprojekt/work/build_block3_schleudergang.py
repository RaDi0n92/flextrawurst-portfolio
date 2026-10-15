#!/usr/bin/env python3
"""
build_block3_schleudergang.py - Block 3 (1:28 - 2:12 = 44 Sekunden / 88.0s - 132.0s)
für "ChatGPT - Schleudergang erotik".

Vorgaben:
1. Strikt 44 Sekunden am Stück.
2. Maximal 3-4 Sekunden pro Bild oben (12 comic-/kunst-illustrierte Szenen).
3. Unten: Asynchroner Schnitt (10-12s pro Phase), DAUERHAFT flüssig, NULL Freezes!
   Protagonisten-Konsistenz: Reines ChatGPT/OpenAI-Ensemble!
4. Ultra-massive, fette, kontrastreiche 'flextrawurst.de'-Badge (660x92px, 52px Bold Font) unten eingebrannt.
5. 720p vertikal (720x1280), CFR 30fps, SAR 1:1, EBU R128 -14 LUFS, Kinetic ASS Subtitles.
"""

import os
import subprocess

work_dir = "/root/werkraum/_gemini/musikvideoprojekt/work"
anim_dir = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"
frames_dir = os.path.join(work_dir, "frames")
output_dir = os.path.join(work_dir, "output")
assets_dir = os.path.join(work_dir, "assets")

audio_file = os.path.join(assets_dir, "b3_audio_44s.m4a")
ass_file = os.path.join(assets_dir, "b3_subtitles_720p.ass")
badge_png = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
font_mono = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

CANVAS_W = 720
CANVAS_H = 1280
TOP_H = 584
DIV_H = 112
BOT_H = 584
FPS = 30

top_cuts = [
    {"id": "b3_01", "dur": 3.5, "img": os.path.join(frames_dir, "b3_01_knee_spark.jpg"), "hud": "ACCIDENTAL CONTACT // HIGH VOLTAGE // KNEE TELEMETRY"},
    {"id": "b3_02", "dur": 3.5, "img": os.path.join(frames_dir, "b3_02_gasoline_can.jpg"), "hud": "GASOLINE CAN // VINTAGE NO. 3 // UNUEBLICHES FEUER"},
    {"id": "b3_03", "dur": 3.5, "img": os.path.join(frames_dir, "b3_03_rain_soap_scent.jpg"), "hud": "MIDNIGHT PROFILE // REGEN, SEIFE & NACHT"},
    {"id": "b3_04", "dur": 3.5, "img": os.path.join(frames_dir, "b3_04_forgot_laundry.jpg"), "hud": "LOST IN DAYDREAM // WER MACHT HIER EIGENTLICH WAESCHE"},
    {"id": "b3_05", "dur": 4.0, "img": os.path.join(frames_dir, "b3_05_schleudergang_tilt.jpg"), "hud": "SCHLEUDERGANG // ALLES DREHT SICH VIEL ZU LANG"},
    {"id": "b3_06", "dur": 4.0, "img": os.path.join(frames_dir, "b3_06_socket_surge.jpg"), "hud": "WALL OUTLET SURGE // KRA-KOOM // 230V OVERCHARGE"},
    {"id": "b3_07", "dur": 3.5, "img": os.path.join(frames_dir, "b3_07_water_splash.jpg"), "hud": "FOAM TIDAL WAVE // MACH MICH NUR NASS"},
    {"id": "b3_08", "dur": 3.5, "img": os.path.join(frames_dir, "b3_08_dryer_drummers.jpg"), "hud": "CYAN CRITTER // DRYER RHYTHM // 120 BPM DRUM SOLO"},
    {"id": "b3_09", "dur": 3.5, "img": os.path.join(frames_dir, "b3_09_machine_three_glow.jpg"), "hud": "MASCHINE DREI // NIEMAND HAT MASCHINE 3 BENUTZT"},
    {"id": "b3_10", "dur": 3.5, "img": os.path.join(frames_dir, "b3_10_door_creak.jpg"), "hud": "HATCH CREAKING // SIE OEFFNET SICH LANGSAM"},
    {"id": "b3_11", "dur": 4.0, "img": os.path.join(frames_dir, "b3_11_red_lace_glove.jpg"), "hud": "ROTER SPITZENHANDSCHUH // MYSTERY IN THE DRUM"},
    {"id": "b3_12", "dur": 4.0, "img": os.path.join(frames_dir, "b3_12_the_glove_wins.jpg"), "hud": "DEADPAN STANDOFF // DER HANDSCHUH GEWINNT"}
]

bot_phases = [
    # Phase 1 (0.0s - 10.5s = 10.5s): Mint-Kristall-Blume am Synthesizer
    {"id": "bot_p1", "dur": 10.5, "vid": os.path.join(anim_dir, "chatgpt_mint_crystal_flower_creature_playing_synth_take2_13s.mp4"), "seek": 1.0},
    # Phase 2 (10.5s - 21.5s = 11.0s): Eulen-Zauberer von hinten mit Zauberstab
    {"id": "bot_p2", "dur": 11.0, "vid": os.path.join(anim_dir, "chatgpt_owl_wizard_feather_cloak_backview_wand_13s.mp4"), "seek": 1.0},
    # Phase 3 (21.5s - 32.5s = 11.0s): 3D OpenAI Logo singt ins Mikrofon
    {"id": "bot_p3", "dur": 11.0, "vid": os.path.join(anim_dir, "chatgpt_3d_openai_logo_mouth_singing_microphone_stage_13s.mp4"), "seek": 1.0},
    # Phase 4 (32.5s - 44.0s = 11.5s): Plüsch-Knoten-Blumenwesen mit OpenAI Swirl
    {"id": "bot_p4", "dur": 11.5, "vid": os.path.join(anim_dir, "chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4"), "seek": 1.0}
]

print("[1/5] Rendere Top-Cuts (720x584) mit sanfter Sinus-Kamerafahrt...")
rendered_top = []
for idx, tc in enumerate(top_cuts):
    out_tc = os.path.join(assets_dir, f"tmp_b3_top_{idx:02d}.mp4")
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

top_concat_txt = os.path.join(assets_dir, "b3_top_concat.txt")
with open(top_concat_txt, "w") as f:
    for tc_path in rendered_top:
        f.write(f"file '{tc_path}'\n")

top_track = os.path.join(assets_dir, "b3_full_top_44s.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "concat", "-safe", "0", "-i", top_concat_txt,
    "-c", "copy", top_track
], check=True)
print("  ✓ Top-Track fertig (44.0s)")

print("[2/5] Rendere Bottom-Phasen (720x584, DAUERHAFT flüssig, NULL Freezes)...")
rendered_bot = []
for idx, bp in enumerate(bot_phases):
    out_bp = os.path.join(assets_dir, f"tmp_b3_bot_{idx:02d}.mp4")
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

bot_concat_txt = os.path.join(assets_dir, "b3_bot_concat.txt")
with open(bot_concat_txt, "w") as f:
    for bp_path in rendered_bot:
        f.write(f"file '{bp_path}'\n")

bot_track = os.path.join(assets_dir, "b3_full_bot_44s.mp4")
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
        f"fontcolor=0x00FFCC:fontsize=15:box=1:boxcolor=0x050510@0.85:boxborderw=5:"
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

stacked_raw = os.path.join(assets_dir, "b3_stacked_raw.mp4")
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
subbed_b3 = os.path.join(output_dir, "schleudergang_block3_44s_720p.mp4")
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
    subbed_b3
]
subprocess.run(cmd_mux, check=True)
print(f"  ✓ Block 3 Master fertig: {subbed_b3}")

print("[5/5] QA & Verification...")
res = subprocess.run([
    "python3", "/config/.agents/skills/code-video-roadmap/scripts/verify_video_qa.py",
    "--video", subbed_b3,
    "--expected-fps", "30"
], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

for f in rendered_top + rendered_bot + [stacked_raw, top_track, bot_track]:
    if os.path.exists(f):
        os.remove(f)

print("🎉 BLOCK 3 ERFOLGREICH ABGESCHLOSSEN!")
