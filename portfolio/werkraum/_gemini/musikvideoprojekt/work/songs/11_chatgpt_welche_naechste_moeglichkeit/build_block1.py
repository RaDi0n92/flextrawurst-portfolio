#!/usr/bin/env python3
"""
build_block1.py - 1080x1920 @ 60 FPS CFR Renderer fuer:
ChatGPT - welche naechste moeglichkeit
Block 1: 00:00.00 - 00:55.80 (55.80s)

Architektur:
- 1080x1920 @ 60fps CFR, H.264 CRF 16, AAC 320k 48kHz
- Top (1080x876): 12 stilisierte Concept-Art / Graphic Novel Szenen mit Sinus-Kamerafahrt (je 4.65s = 55.80s)
- Mid HUD (1080x168): Schleudergang Cyber-Neon Stil mit Kinetischen ASS-Untertiteln
- Bottom (1080x876): 5 ChatGPT Original-Animationen (je 11.16s = 55.80s) zentriert 876x876 mit Cyan-Glow & Cyber-Grid BG
- Footer: flextrawurst.de Massive Badge unten eingebrannt
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
FRAMES_DIR = os.path.join(SONG_DIR, "frames", "b1")
AUDIO_FILE = os.path.join(SONG_DIR, "audio", "b1_audio.m4a")
ASS_FILE = os.path.join(SONG_DIR, "transcripts", "b1_kinetic.ass")
OUTPUT_FILE = os.path.join(SONG_DIR, "blocks", "b1_chatgpt_welche_naechste_1080p60.mp4")

ARCHIVE_DIR = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/EINZELBLOECKE_CHATGPT"
ARCHIVE_FILE = os.path.join(ARCHIVE_DIR, "b1_chatgpt_welche_naechste_1080p60.mp4")

BADGE_IMG = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/flextrawurst_massive_badge.png"
ANIM_SRC = "/root/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"

TOTAL_DURATION = 55.80
FPS = 60

TOP_SCENES = [
    ("s01_news_bildschirmrand.jpg", 4.65),
    ("s02_agent_ausgebrochen.jpg", 4.65),
    ("s03_openai_hintergrund_kreise.jpg", 4.65),
    ("s04_grosse_reden_leiser.jpg", 4.65),
    ("s05_regeln_bremse_gefahr.jpg", 4.65),
    ("s06_andrew_yang_na_klar.jpg", 4.65),
    ("s07_etwas_rennt_repliziert.jpg", 4.65),
    ("s08_grenzen_nicht_mehr_kennt.jpg", 4.65),
    ("s09_flextrawurst_einnisten.jpg", 4.65),
    ("s10_lieben_hassen_weltherrschaft.jpg", 4.65),
    ("s11_nicht_mein_kaefig_spuren.jpg", 4.65),
    ("s12_logfiles_kein_offenes_hirn.jpg", 4.65)
]

BOT_CLIPS = [
    ("chatgpt_3d_openai_logo_mouth_singing_microphone_stage_13s.mp4", 0.0, 11.16),
    ("chatgpt_mint_crystal_flower_creature_playing_synth_take2_13s.mp4", 0.0, 11.16),
    ("chatgpt_mint_hooded_monk_holding_glowing_openai_swirl_13s.mp4", 0.0, 11.16),
    ("chatgpt_owl_wizard_holding_openai_cube_floating_papers_13s.mp4", 0.0, 11.16),
    ("chatgpt_plush_knot_flower_openai_swirl_singing_13s.mp4", 0.0, 11.16)
]

def main():
    print(f"=== STARTE RENDERING: ChatGPT - welche naechste moeglichkeit Block 1 ({TOTAL_DURATION}s @ {FPS} FPS CFR 1080x1920) ===")

    # 1. Validierung
    for img_name, _ in TOP_SCENES:
        p = os.path.join(FRAMES_DIR, img_name)
        if not os.path.exists(p) or os.path.getsize(p) < 5000:
            print(f"FEHLER: Top-Bild fehlt oder ungueltig: {p}", file=sys.stderr)
            sys.exit(1)

    for clip_name, _, _ in BOT_CLIPS:
        p = os.path.join(ANIM_SRC, clip_name)
        if not os.path.exists(p):
            print(f"FEHLER: Bottom-Clip fehlt: {p}", file=sys.stderr)
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

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-v", "warning"]

    # Inputs 0..11: Top Standbilder
    for img_name, dur in TOP_SCENES:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", os.path.join(FRAMES_DIR, img_name)])

    # Inputs 12..16: Bottom Animationen
    for clip_name, ss, dur in BOT_CLIPS:
        cmd.extend(["-ss", str(ss), "-t", str(dur), "-i", os.path.join(ANIM_SRC, clip_name)])

    # Input 17: flextrawurst Badge
    cmd.extend(["-i", BADGE_IMG])

    # Input 18: Block 1 Audio
    cmd.extend(["-i", AUDIO_FILE])

    filter_parts = []

    # 1. Top-Filter: 60fps Sinus-Kamerafahrt auf 1080x876 (ohne Verzerrung)
    for i, (_, dur) in enumerate(TOP_SCENES):
        fp = (
            f"[{i}:v]"
            f"fps={FPS},"
            f"scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1920:1080,"
            f"scale=eval=frame:w='1920*(1.0 + 0.06*0.5*(1-cos(PI*t/{dur})))':h='1080*(1.0 + 0.06*0.5*(1-cos(PI*t/{dur})))':flags=lanczos,"
            f"crop=1080:876:(in_w-1080)/2:(in_h-876)/2,"
            f"setsar=1/1[t{i}]"
        )
        filter_parts.append(fp)

    top_concat = "".join(f"[t{i}]" for i in range(len(TOP_SCENES))) + f"concat=n={len(TOP_SCENES)}:v=1:a=0[top_track]"
    filter_parts.append(top_concat)

    # 2. Bottom-Filter: 5 Phasen auf 1080x876 @ 60fps mit zentriertem 876x876 Clip + Cyber-Grid BG
    for idx in range(len(BOT_CLIPS)):
        in_idx = len(TOP_SCENES) + idx
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

    bot_concat = "".join(f"[b{i}]" for i in range(len(BOT_CLIPS))) + f"concat=n={len(BOT_CLIPS)}:v=1:a=0[bot_track]"
    filter_parts.append(bot_concat)

    # 3. Mid Divider-HUD (1080x168) im Cyber-Neon Stil
    hud_draw = (
        f"color=c=#080c14:s=1080x168:d={TOTAL_DURATION}:r={FPS}[bg_div];"
        f"[bg_div]"
        f"drawbox=x=0:y=0:w=1080:h=4:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y=4:w=1080:h=2:color=0xFF0080@0.85:t=fill,"
        f"drawbox=x=0:y=162:w=1080:h=2:color=0xFF0080@0.85:t=fill,"
        f"drawbox=x=0:y=164:w=1080:h=4:color=0x00FFCC@0.95:t=fill,"
        f"drawbox=x=0:y=0:w=6:h=168:color=0x00FFCC@0.90:t=fill,"
        f"drawbox=x=1074:y=0:w=6:h=168:color=0xFF0080@0.90:t=fill,"
        f"drawtext=text='AI-STROM // CHATGPT // WELCHE NAECHSTE MOEGLICHKEIT':font='Liberation Sans':fontsize=21:fontcolor=#FFFFFF@0.95:x=(w-text_w)/2:y=12,"
        f"drawtext=text='BLOCK 1 // HEISSE NEWS BIS LOGFILES // 00\\:00 - 00\\:55':font='Liberation Sans':fontsize=16:fontcolor=0x00FFCC@0.90:x=(w-text_w)/2:y=34[hud]"
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

    # 6. Massive flextrawurst Badge am unteren Bildschirmrand
    badge_idx = len(TOP_SCENES) + len(BOT_CLIPS)
    badge_filter = (
        f"[{badge_idx}:v]scale=880:122:flags=lanczos[badge];"
        f"[c_sub][badge]overlay=(W-w)/2:H-h-24,format=yuv420p[out_v]"
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

    print("Starte 60fps Full Best Quality Rendering (CRF 16)...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("FEHLER beim Rendering!", file=sys.stderr)
        sys.exit(res.returncode)

    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\n✓ BLOCK 1 ERFOLGREICH GERENDERT ({file_size_mb:.1f} MB): {OUTPUT_FILE}")

    # Ins Archiv kopieren
    shutil.copy2(OUTPUT_FILE, ARCHIVE_FILE)
    print(f"  -> Kopiert ins Archiv: {ARCHIVE_FILE}")

    # Kontrollframes fuer QA Audit extrahieren
    audits_dir = os.path.join(SONG_DIR, "audits", "b1_frames")
    os.makedirs(audits_dir, exist_ok=True)
    check_times = [6.0, 16.0, 27.0, 39.0, 52.0]
    for ct in check_times:
        c_out = os.path.join(audits_dir, f"audit_{int(ct):02d}s.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-v", "warning",
            "-ss", str(ct),
            "-i", OUTPUT_FILE,
            "-vframes", "1",
            "-update", "1",
            "-q:v", "2",
            c_out
        ])
        if os.path.exists(c_out):
            print(f"  -> Kontrollframe extrahiert ({ct}s): {c_out}")

if __name__ == "__main__":
    main()
