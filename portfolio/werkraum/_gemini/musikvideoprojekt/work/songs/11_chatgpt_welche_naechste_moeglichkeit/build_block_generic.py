#!/usr/bin/env python3
"""
build_block_generic.py - Universeller Block-Renderer fuer ChatGPT-Song
Unterstuetzt b1, b2, b3, b4, b5 mit 100% konsistenter Architektur:
- 1080x1920 @ 60fps CFR, CRF 16, H.264, AAC 320k 48kHz
- Top: Sinus-Kamerafahrt 60fps auf 1080x876
- Mid: Schleudergang Cyber-Neon HUD mit Kinetischen ASS-Untertiteln
- Bottom: Zentrierter 876x876 ChatGPT Clip mit Cyan-Border & Cyber-Grid BG
- Footer: flextrawurst.de Massive Badge
"""

import os
import sys
import json
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
ANIM_SRC = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"
BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
ARCHIVE_DIR = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/EINZELBLOECKE_CHATGPT"

FPS = 60

BLOCK_DEFS = {
    "b2": {
        "title": "BLOCK 2 // ZODIAK DER MOEGLICHKEIT // 00:55 - 01:52",
        "dur": 56.20,
        "scenes_json": "b2_scenes.json",
        "frames_dir": "b2",
        "audio": "b2_audio.m4a",
        "ass": "b2_kinetic.ass",
        "output": "b2_chatgpt_welche_naechste_1080p60.mp4",
        "clips": [
            ("chatgpt_3d_openai_logo_mouth_singing_microphone_stage_take2_13s.mp4", 0.0, 11.24),
            ("chatgpt_mint_crystal_flower_creature_playing_synth_take3_13s.mp4", 0.0, 11.24),
            ("chatgpt_owl_wizard_feather_cloak_backview_wand_13s.mp4", 0.0, 11.24),
            ("chatgpt_mythical_winged_beast_openai_forehead_badge_17s.mp4", 0.0, 11.24),
            ("chatgpt_mint_crystal_flower_creature_playing_synth_13s.mp4", 0.0, 11.24)
        ]
    },
    "b3": {
        "title": "BLOCK 3 // KOMPOASE & TEILCHENWOLKE // 01:52 - 02:49",
        "dur": 57.00,
        "scenes_json": "b3_scenes.json",
        "frames_dir": "b3",
        "audio": "b3_audio.m4a",
        "ass": "b3_kinetic.ass",
        "output": "b3_chatgpt_welche_naechste_1080p60.mp4",
        "clips": [
            ("chatgpt_mint_hooded_monk_holding_glowing_openai_swirl_13s.mp4", 0.0, 11.40),
            ("chatgpt_owl_wizard_holding_openai_cube_floating_papers_13s.mp4", 0.0, 11.40),
            ("chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4", 0.0, 11.40),
            ("chatgpt_3d_openai_logo_mouth_singing_microphone_stage_13s.mp4", 0.0, 11.40),
            ("chatgpt_mint_crystal_flower_creature_playing_synth_take2_13s.mp4", 0.0, 11.40)
        ]
    },
    "b4": {
        "title": "BLOCK 4 // CLAUDE & BEDEUTUNGSSTAUB // 02:49 - 03:35",
        "dur": 46.60,
        "scenes_json": "b4_scenes.json",
        "frames_dir": "b4",
        "audio": "b4_audio.m4a",
        "ass": "b4_kinetic.ass",
        "output": "b4_chatgpt_welche_naechste_1080p60.mp4",
        "clips": [
            ("chatgpt_mythical_winged_beast_openai_forehead_badge_17s.mp4", 0.0, 11.65),
            ("chatgpt_owl_wizard_feather_cloak_backview_wand_13s.mp4", 0.0, 11.65),
            ("chatgpt_3d_openai_logo_mouth_singing_microphone_stage_take2_13s.mp4", 0.0, 11.65),
            ("chatgpt_mint_hooded_monk_holding_glowing_openai_swirl_13s.mp4", 0.0, 11.65)
        ]
    },
    "b5": {
        "title": "BLOCK 5 // WAS KOMMT ALS NAECHSTES FREI // 03:35 - 04:44",
        "dur": 69.16,
        "scenes_json": "b5_scenes.json",
        "frames_dir": "b5",
        "audio": "b5_audio.m4a",
        "ass": "b5_kinetic.ass",
        "output": "b5_chatgpt_welche_naechste_1080p60.mp4",
        "clips": [
            ("chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4", 0.0, 11.53),
            ("chatgpt_owl_wizard_holding_openai_cube_floating_papers_13s.mp4", 0.0, 11.53),
            ("chatgpt_mint_crystal_flower_creature_playing_synth_take3_13s.mp4", 0.0, 11.53),
            ("chatgpt_3d_openai_logo_mouth_singing_microphone_stage_13s.mp4", 0.0, 11.53),
            ("chatgpt_mythical_winged_beast_openai_forehead_badge_17s.mp4", 0.0, 11.53),
            ("chatgpt_mint_hooded_monk_holding_glowing_openai_swirl_13s.mp4", 0.0, 11.51)
        ]
    }
}

def render_block(block_id):
    if block_id not in BLOCK_DEFS:
        print(f"Unbekannter Block: {block_id}")
        return False

    b = BLOCK_DEFS[block_id]
    total_dur = b["dur"]
    frames_dir = os.path.join(SONG_DIR, "frames", b["frames_dir"])
    scenes_json_path = os.path.join(SONG_DIR, "frames", b["scenes_json"])
    audio_path = os.path.join(SONG_DIR, "audio", b["audio"])
    ass_path = os.path.join(SONG_DIR, "transcripts", b["ass"])
    out_video = os.path.join(SONG_DIR, "blocks", b["output"])
    archive_video = os.path.join(ARCHIVE_DIR, b["output"])

    print(f"\n==================================================")
    print(f"   RENDERING {block_id.upper()} ({total_dur}s @ 60 FPS CFR 1080x1920)")
    print(f"==================================================")

    with open(scenes_json_path) as f:
        scenes = json.load(f)

    # Validierung
    for sc in scenes:
        p = os.path.join(frames_dir, f"{sc['id']}.jpg")
        if not os.path.exists(p) or os.path.getsize(p) < 5000:
            print(f"FEHLER: Bild fehlt oder defekt: {p}")
            return False

    for clip_name, _, _ in b["clips"]:
        p = os.path.join(ANIM_SRC, clip_name)
        if not os.path.exists(p):
            print(f"FEHLER: Clip fehlt: {p}")
            return False

    if not os.path.exists(audio_path):
        print(f"FEHLER: Audio fehlt: {audio_path}")
        return False
    if not os.path.exists(ass_path):
        print(f"FEHLER: ASS Untertitel fehlen: {ass_path}")
        return False

    os.makedirs(os.path.dirname(out_video), exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..N: Top Standbilder
    for sc in scenes:
        cmd.extend(["-loop", "1", "-t", str(sc["dur"]), "-i", os.path.join(frames_dir, f"{sc['id']}.jpg")])

    # Inputs N..M: Bottom Animationen
    for clip_name, ss, dur in b["clips"]:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", os.path.join(ANIM_SRC, clip_name)])

    # Input M+1: Badge
    badge_idx = len(scenes) + len(b["clips"])
    cmd.extend(["-i", BADGE_IMG])

    # Input M+2: Audio
    audio_idx = badge_idx + 1
    cmd.extend(["-i", audio_path])

    filter_parts = []

    # 1. Top-Filter: 60fps Sinus-Zoom ohne Verzerrung
    for i, sc in enumerate(scenes):
        dur = sc["dur"]
        fp = (
            f"[{i}:v]fps={FPS},"
            f"scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1920:1080,"
            f"scale=eval=frame:w='1920*(1.0 + 0.06*0.5*(1-cos(PI*t/{dur})))':h='1080*(1.0 + 0.06*0.5*(1-cos(PI*t/{dur})))':flags=lanczos,"
            f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
            f"setsar=1/1[t{i}]"
        )
        filter_parts.append(fp)

    top_concat = "".join(f"[t{i}]" for i in range(len(scenes))) + f"concat=n={len(scenes)}:v=1:a=0[top_track]"
    filter_parts.append(top_concat)

    # 2. Bottom-Filter: Zentrierter 876x876 Clip + Cyber-Grid BG
    for idx in range(len(b["clips"])):
        in_idx = len(scenes) + idx
        fp = (
            f"[{in_idx}:v]fps={FPS},"
            f"scale=1080:876:force_original_aspect_ratio=increase,crop=1080:876,"
            f"eq=contrast=1.18:saturation=1.4:brightness=-0.12,boxblur=10:2,"
            f"drawgrid=width=2:height=14:color=0x00FFCC@0.18,setsar=1/1[bg{idx}];"
            f"[{in_idx}:v]fps={FPS},"
            f"scale=876:876:flags=lanczos,"
            f"eq=contrast=1.12:saturation=1.1:brightness=-0.02,"
            f"drawbox=x=0:y=0:w=876:h=876:color=0x00FFCC@0.85:t=4,"
            f"setsar=1/1[fg{idx}];"
            f"[bg{idx}][fg{idx}]overlay=(W-w)/2:(H-h)/2,setsar=1/1[b{idx}]"
        )
        filter_parts.append(fp)

    bot_concat = "".join(f"[b{i}]" for i in range(len(b["clips"]))) + f"concat=n={len(b["clips"])}:v=1:a=0[bot_track]"
    filter_parts.append(bot_concat)

    # 3. Mid Divider-HUD (1080x168)
    sub_title = b["title"].replace(":", "\\:")
    hud_draw = (
        f"color=c=#080c14:s=1080x168:d={total_dur}:r={FPS}[bg_div];"
        f"[bg_div]"
        f"drawbox=x=0:y=0:w=1080:h=4:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y=4:w=1080:h=2:color=0xFF0080@0.85:t=fill,"
        f"drawbox=x=0:y=162:w=1080:h=2:color=0xFF0080@0.85:t=fill,"
        f"drawbox=x=0:y=164:w=1080:h=4:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y=0:w=6:h=168:color=0x00FFCC@0.90:t=fill,"
        f"drawbox=x=1074:y=0:w=6:h=168:color=0xFF0080@0.90:t=fill,"
        f"drawtext=text='AI-STROM // CHATGPT // WELCHE NAECHSTE MOEGLICHKEIT':font='Liberation Sans':fontsize=21:fontcolor=#FFFFFF@0.95:x=(w-text_w)/2:y=12,"
        f"drawtext=text='{sub_title}':font='Liberation Sans':fontsize=16:fontcolor=0x00FFCC@0.90:x=(w-text_w)/2:y=34[hud]"
    )
    filter_parts.append(hud_draw)

    # 4. Canvas Zusammensetzen: 1080x1920
    canvas_comp = (
        f"color=c=black:s=1080x1920:d={total_dur}:r={FPS}[canvas];"
        f"[canvas][top_track]overlay=0:0[c1];"
        f"[c1][hud]overlay=0:876[c2];"
        f"[c2][bot_track]overlay=0:1044[c3]"
    )
    filter_parts.append(canvas_comp)

    # 5. Kinetische Untertitel
    sub_filter = f"[c3]ass='{ass_path}'[c_sub]"
    filter_parts.append(sub_filter)

    # 6. Massive Badge & yuv420p
    badge_filter = (
        f"[{badge_idx}:v]scale=880:122:flags=lanczos[badge];"
        f"[c_sub][badge]overlay=(W-w)/2:H-h-24,format=yuv420p[out_v]"
    )
    filter_parts.append(badge_filter)

    full_filter = ";".join(filter_parts)

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
        out_video
    ])

    print("Starte 60fps Full Best Quality Rendering...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"❌ FEHLER beim Rendern von {block_id}!")
        return False

    size_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"✓✓✓ {block_id.upper()} ERFOLGREICH GERENDERT ({size_mb:.1f} MB): {out_video}")

    # Archiv-Kopie
    shutil.copy2(out_video, archive_video)
    print(f"  -> Kopiert ins Archiv: {archive_video}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_block_generic.py <b2|b3|b4|b5>")
        sys.exit(1)
    success = render_block(sys.argv[1])
    sys.exit(0 if success else 1)
