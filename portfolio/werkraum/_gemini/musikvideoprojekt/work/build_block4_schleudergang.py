#!/usr/bin/env python3
"""
build_block4_schleudergang.py - Block 4: Das große Finale & Outro
(132.0s bis 207.80s = 75.80 Sekunden) für "ChatGPT - Schleudergang erotik".

Vorgaben:
1. Strikt 75.80 Sekunden (genau bis zum Song-Ende!).
2. Oben: 18 stimmungsgewaltige Schnitte, die die Geschichte zu Ende erzählen
   (Roter Spitzenhandschuh, Unwuchtmodus, fallende 2-Euro-Münze, Lippenstift am Kragen,
    der erstaunte Besitzer am Morgen, Maschine 4 ohne Wäsche, friedlicher Ausklang).
3. Unten: 6 flüssige Phasen des ChatGPT/OpenAI-Ensembles (12-13s pro Phase), NULL Freezes!
4. Eingebrannte massive 'flextrawurst.de'-Badge.
5. 720p vertikal (720x1280), CFR 30fps, SAR 1:1, EBU R128 -14 LUFS, Kinetic ASS Subtitles.
"""

import os
import subprocess

work_dir = "/root/werkraum/_gemini/musikvideoprojekt/work"
anim_dir = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"
frames_dir = os.path.join(work_dir, "frames")
output_dir = os.path.join(work_dir, "output")
assets_dir = os.path.join(work_dir, "assets")

audio_file = os.path.join(assets_dir, "b4_audio_75s.m4a")
ass_file = os.path.join(assets_dir, "b4_subtitles_720p.ass")
badge_png = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
font_mono = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

CANVAS_W = 720
CANVAS_H = 1280
TOP_H = 584
DIV_H = 112
BOT_H = 584
FPS = 30

top_cuts = [
    {"id": "b4_01", "dur": 4.0, "img": os.path.join(frames_dir, "b4_01_putting_on_glove.jpg"), "hud": "RED LACE GLOVE // DU ZIEHST IHN AN // GEHOERT ER DIR?"},
    {"id": "b4_02", "dur": 4.0, "img": os.path.join(frames_dir, "b4_02_since_about_now.jpg"), "hud": "SEIT UNGEFAEHR JETZT // MIDNIGHT SMILE"},
    {"id": "b4_03", "dur": 3.5, "img": os.path.join(frames_dir, "b4_03_flicker_warm_air.jpg"), "hud": "FLACKERLICHT // WARME LUFT // NEON SHIMMER"},
    {"id": "b4_04", "dur": 4.0, "img": os.path.join(frames_dir, "b4_04_hands_on_metal.jpg"), "hud": "METALL UNTER DEINEN HAENDEN // VIBRATION"},
    {"id": "b4_05", "dur": 4.0, "img": os.path.join(frames_dir, "b2_09_vibration_ripples.jpg"), "hud": "UNWUCHTMODUS // VIER MASCHINEN TANZEN"},
    {"id": "b4_06", "dur": 4.0, "img": os.path.join(frames_dir, "b1_05_coin_slot.jpg"), "hud": "UND IRGENDWO FAELLT SEHR LANGSAM..."},
    {"id": "b4_07", "dur": 4.5, "img": os.path.join(frames_dir, "b1_05_coins.jpg"), "hud": "EINE ZWEI-EURO-MUENZE UM // SLOW MOTION"},
    {"id": "b4_08", "dur": 4.0, "img": os.path.join(frames_dir, "b2_01_schleudergang_vortex.jpg"), "hud": "SCHLEUDERGANG // FINAL SPIN VORTEX"},
    {"id": "b4_09", "dur": 4.0, "img": os.path.join(frames_dir, "b3_05_schleudergang_tilt.jpg"), "hud": "JETZT DREHT ES DER BODEN ENTLANG"},
    {"id": "b4_10", "dur": 4.0, "img": os.path.join(frames_dir, "b1_08_red_jacket.jpg"), "hud": "DEIN LIPPENSTIFT // SITZT AUF MEINEM KRAGEN SCHIEF"},
    {"id": "b4_11", "dur": 4.0, "img": os.path.join(frames_dir, "b3_06_socket_surge.jpg"), "hud": "MASCHINE RIEF NACH NOTDIENST // OVERHEAT"},
    {"id": "b4_12", "dur": 4.0, "img": os.path.join(frames_dir, "b3_07_water_splash.jpg"), "hud": "WASCH MICH NICHT SAUBER // LASS FLECKEN ZURUECK"},
    {"id": "b4_13", "dur": 4.0, "img": os.path.join(frames_dir, "b1_10_softener.jpg"), "hud": "EIN BISSCHEN WASCHMITTEL // EIN BISSCHEN GLUECK"},
    {"id": "b4_14", "dur": 4.5, "img": os.path.join(frames_dir, "b1_02_moon.jpg"), "hud": "MORGENS FRAGT DER BESITZER SICH DANN..."},
    {"id": "b4_15", "dur": 4.5, "img": os.path.join(frames_dir, "b1_03_machine_four.jpg"), "hud": "WARUM LAEUFT MASCHINE VIER?"},
    {"id": "b4_16", "dur": 5.0, "img": os.path.join(frames_dir, "b1_03_barefoot.jpg"), "hud": "SEIT SECHS STUNDEN OHNE WAESCHE DARIN"},
    {"id": "b4_17", "dur": 4.5, "img": os.path.join(frames_dir, "b1_12_vortex_critter.jpg"), "hud": "WASCHSALON ATMET AUS // CHATGPT OUTRO"},
    {"id": "b4_18", "dur": 5.3, "img": os.path.join(frames_dir, "b1_01_clock.jpg"), "hud": "03:17 // DAS SYSTEM SCHWEIGT // ENDE"}
]

bot_phases = [
    # Phase 1 (0.0s - 12.0s = 12.0s): 3D Logo singt ins Mikrofon
    {"id": "bot_p1", "dur": 12.0, "vid": os.path.join(anim_dir, "chatgpt_3d_openai_logo_mouth_singing_microphone_stage_take2_13s.mp4"), "seek": 0.5},
    # Phase 2 (12.0s - 24.5s = 12.5s): Mint-Kristall-Blume am Synthesizer
    {"id": "bot_p2", "dur": 12.5, "vid": os.path.join(anim_dir, "chatgpt_mint_crystal_flower_creature_playing_synth_take3_13s.mp4"), "seek": 0.5},
    # Phase 3 (24.5s - 37.0s = 12.5s): Plüsch-Knoten-Blume mit OpenAI Swirl
    {"id": "bot_p3", "dur": 12.5, "vid": os.path.join(anim_dir, "chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4"), "seek": 0.5},
    # Phase 4 (37.0s - 50.0s = 13.0s): Kuttenträger mit leuchtendem Swirl
    {"id": "bot_p4", "dur": 13.0, "vid": os.path.join(anim_dir, "chatgpt_mint_hooded_monk_holding_glowing_openai_swirl_13s.mp4"), "seek": 0.0},
    # Phase 5 (50.0s - 63.0s = 13.0s): Geflügelte Kreatur mit OpenAI Stirnabzeichen
    {"id": "bot_p5", "dur": 13.0, "vid": os.path.join(anim_dir, "chatgpt_mythical_winged_beast_openai_forehead_badge_17s.mp4"), "seek": 2.0},
    # Phase 6 (63.0s - 75.8s = 12.8s): Eulen-Zauberer hält den schwebenden Würfel
    {"id": "bot_p6", "dur": 12.8, "vid": os.path.join(anim_dir, "chatgpt_owl_wizard_holding_openai_cube_floating_papers_13s.mp4"), "seek": 0.2}
]

print("[1/5] Rendere Top-Cuts (720x584) für das Finale (75.8s)...")
rendered_top = []
for idx, tc in enumerate(top_cuts):
    out_tc = os.path.join(assets_dir, f"tmp_b4_top_{idx:02d}.mp4")
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

top_concat_txt = os.path.join(assets_dir, "b4_top_concat.txt")
with open(top_concat_txt, "w") as f:
    for tc_path in rendered_top:
        f.write(f"file '{tc_path}'\n")

top_track = os.path.join(assets_dir, "b4_full_top_75s.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "concat", "-safe", "0", "-i", top_concat_txt,
    "-c", "copy", top_track
], check=True)
print("  ✓ Top-Track fertig (75.8s)")

print("[2/5] Rendere Bottom-Phasen (720x584, DAUERHAFT flüssig, NULL Freezes)...")
rendered_bot = []
for idx, bp in enumerate(bot_phases):
    out_bp = os.path.join(assets_dir, f"tmp_b4_bot_{idx:02d}.mp4")
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

bot_concat_txt = os.path.join(assets_dir, "b4_bot_concat.txt")
with open(bot_concat_txt, "w") as f:
    for bp_path in rendered_bot:
        f.write(f"file '{bp_path}'\n")

bot_track = os.path.join(assets_dir, "b4_full_bot_75s.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "concat", "-safe", "0", "-i", bot_concat_txt,
    "-c", "copy", bot_track
], check=True)
print("  ✓ Bottom-Track fertig (75.8s)")

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
    f"color=c=0x080812:s={CANVAS_W}x{DIV_H}:r={FPS}:d=75.80[mid_bg];"
    f"[mid_bg]{hud_chain}[mid];"
    f"[top][mid][bot]vstack=inputs=3[stack];"
    f"[stack][2:v]overlay=(W-w)/2:H-h-24[v_badged]"
)

stacked_raw = os.path.join(assets_dir, "b4_stacked_raw.mp4")
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
subbed_b4 = os.path.join(output_dir, "schleudergang_block4_finale_75s_720p.mp4")
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
    subbed_b4
]
subprocess.run(cmd_mux, check=True)
print(f"  ✓ Block 4 Finale Master fertig: {subbed_b4}")

print("[5/5] QA & Verification...")
res = subprocess.run([
    "python3", "/config/.agents/skills/code-video-roadmap/scripts/verify_video_qa.py",
    "--video", subbed_b4,
    "--expected-fps", "30"
], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

for f in rendered_top + rendered_bot + [stacked_raw, top_track, bot_track]:
    if os.path.exists(f):
        os.remove(f)

print("🎉 BLOCK 4 FINALE ERFOLGREICH ABGESCHLOSSEN!")
