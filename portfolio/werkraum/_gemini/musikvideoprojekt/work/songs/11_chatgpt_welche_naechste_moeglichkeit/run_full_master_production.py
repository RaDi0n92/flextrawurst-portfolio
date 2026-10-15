#!/usr/bin/env python3
"""
run_full_master_production.py - Vollautomatischer Master-Produktionsablauf fuer:
ChatGPT - welche naechste moeglichkeit (284.76s + 6.60s Pflichtvideo = 291.36s)

Fuehrt vollstaendig und autonom aus:
1. Block 2 Generierung & Render
2. Block 3 Generierung & Render
3. Block 4 Generierung & Render
4. Block 5 Generierung & Render
5. Nahtloser Master-Concat mit Pflichtintro (0:00)
6. Vollstaendige Endkontrolle & Audit-Frame-Extraktion
"""

import os
import sys
import time
import shutil
import subprocess
import json

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
PFLICHT_VIDEO = "/root/werkraum/_gemini/musikvideoprojekt/pflichtanfangsvideo/daniel_intro_20260918_1080p60_normalized.mp4"
BLOCKS_DIR = os.path.join(SONG_DIR, "blocks")
AUDITS_DIR = os.path.join(SONG_DIR, "audits", "master_audit_frames")

FINAL_MASTER_LOCAL = os.path.join(BLOCKS_DIR, "11_chatgpt_welche_naechste_FULL_MASTER_1080p60.mp4")
FINAL_MASTER_ARCHIVE = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/11_chatgpt_welche_naechste_FULL_MASTER_1080p60.mp4"

GEN_SCRIPT = os.path.join(SONG_DIR, "generate_block_scenes_horde.py")
BUILD_SCRIPT = os.path.join(SONG_DIR, "build_block_generic.py")

from generate_block_scenes_horde import generate_scenes
from build_block_generic import render_block

def run_step(step_name, fn):
    print(f"\n=======================================================")
    print(f">>> STARTE SCHRITT: {step_name}")
    print(f"=======================================================")
    t0 = time.time()
    ok = fn()
    if not ok:
        print(f"❌ FEHLER in Schritt: {step_name}!", file=sys.stderr)
        sys.exit(1)
    print(f"✓✓✓ SCHRITT ERFOLGREICH: {step_name} in {time.time()-t0:.1f}s\n")

def process_block(b_id):
    cfg_file = os.path.join(SONG_DIR, "frames", f"{b_id}_scenes.json")
    frames_dir = os.path.join(SONG_DIR, "frames", b_id)
    with open(cfg_file) as f:
        scenes = json.load(f)

    # 1. Bilder generieren
    if not generate_scenes(scenes, frames_dir, b_id.upper()):
        return False

    # 2. Block rendern
    if not render_block(b_id):
        return False

    return True

def build_full_master():
    print("\n=======================================================")
    print(">>> ERSTELLE FULL MASTER MIT PFLICHTVIDEO AN 0:00")
    print("=======================================================")

    block_files = [
        PFLICHT_VIDEO,
        os.path.join(BLOCKS_DIR, "b1_chatgpt_welche_naechste_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b2_chatgpt_welche_naechste_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b3_chatgpt_welche_naechste_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b4_chatgpt_welche_naechste_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b5_chatgpt_welche_naechste_1080p60.mp4")
    ]

    for p in block_files:
        if not os.path.exists(p) or os.path.getsize(p) < 1000000:
            print(f"❌ Fehler: Blockdatei fehlt oder ist zu klein: {p}", file=sys.stderr)
            return False

    concat_list = os.path.join(BLOCKS_DIR, "master_concat.txt")
    with open(concat_list, "w") as f:
        for p in block_files:
            f.write(f"file '{p}'\n")

    cmd = [
        "ffmpeg", "-y", "-v", "warning",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        FINAL_MASTER_LOCAL
    ]
    print(f"Führe Stream-Copy Master-Concat durch...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("Concat fehlgeschlagen, versuche Re-Encoding Concat...", file=sys.stderr)
        inputs = []
        filter_in = ""
        for i, p in enumerate(block_files):
            inputs.extend(["-i", p])
            filter_in += f"[{i}:v][{i}:a]"
        reencode_cmd = [
            "ffmpeg", "-y", "-v", "warning",
            *inputs,
            "-filter_complex", f"{filter_in}concat=n={len(block_files)}:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            FINAL_MASTER_LOCAL
        ]
        res = subprocess.run(reencode_cmd)
        if res.returncode != 0:
            print("❌ Re-Encoding Concat ebenfalls fehlgeschlagen!", file=sys.stderr)
            return False

    size_mb = os.path.getsize(FINAL_MASTER_LOCAL) / (1024 * 1024)
    print(f"✓ FULL MASTER ERFOLGREICH ERSTELLT ({size_mb:.1f} MB): {FINAL_MASTER_LOCAL}")

    # Archiv-Kopie
    os.makedirs(os.path.dirname(FINAL_MASTER_ARCHIVE), exist_ok=True)
    shutil.copy2(FINAL_MASTER_LOCAL, FINAL_MASTER_ARCHIVE)
    print(f"  -> Kopiert ins Archiv: {FINAL_MASTER_ARCHIVE}")

    # Kontrollframes extrahieren
    os.makedirs(AUDITS_DIR, exist_ok=True)
    check_points = [
        (3.0, "00_pflichtintro"),
        (25.0, "01_block1_intro"),
        (80.0, "02_block2_zensi"),
        (140.0, "03_block3_kompoase"),
        (200.0, "04_block4_claude_rag"),
        (260.0, "05_block5_final_refrain")
    ]
    for ts, name in check_points:
        c_out = os.path.join(AUDITS_DIR, f"master_audit_{name}_{int(ts):03d}s.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-v", "warning",
            "-ss", str(ts),
            "-i", FINAL_MASTER_LOCAL,
            "-vframes", "1",
            "-update", "1",
            "-q:v", "2",
            c_out
        ])
        if os.path.exists(c_out):
            print(f"  ✓ Kontrollframe extrahiert ({ts}s): {c_out}")

    return True

def main():
    print("#######################################################")
    print("   VOLLAUTOMATISCHE PRODUKTION: CHATGPT MUSIKVIDEO")
    print("   SONG: welche-nächste-möglichkeit (284.76s + 6.60s)")
    print("#######################################################")

    # Block 2
    run_step("Block 2 (Zensi & Gemini Labor)", lambda: process_block("b2"))

    # Block 3
    run_step("Block 3 (KompOase & Teilchenwolke)", lambda: process_block("b3"))

    # Block 4
    run_step("Block 4 (Claude & Bedeutungsstaub)", lambda: process_block("b4"))

    # Block 5
    run_step("Block 5 (Finaler Refrain & Vollendung)", lambda: process_block("b5"))

    # Master Concat mit Pflichtvideo
    run_step("Full Master Concat (Pflichtvideo + Bloecke 1..5)", build_full_master)

    print("\n#######################################################")
    print("   ✓✓✓ GESAMTES MUSIKVIDEO VOLLSTAENDIG PRODUZIERT! ✓✓✓")
    print("#######################################################")

if __name__ == "__main__":
    main()
