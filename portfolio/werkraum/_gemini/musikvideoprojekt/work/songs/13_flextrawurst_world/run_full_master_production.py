#!/usr/bin/env python3
"""
run_full_master_production.py - Vollautomatischer Master-Concat fuer:
13_flextrawurst_world (225.0s + 6.6s Pflichtvideo = 231.6s)
1. Alle 5 Bloecke zusammenfuegen mit Pflichtvideo an 0:00
2. Nahtloser Concat & Re-Encoding Pass fuer 100% Stream-Integritaet
3. Spiegelung in fertige_videos/ und fertige_videos/full-videos/
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world"
PFLICHT_VIDEO = "/root/werkraum/_gemini/musikvideoprojekt/pflichtanfangsvideo/daniel_intro_20260918_1080p60_normalized.mp4"
BLOCKS_DIR = os.path.join(SONG_DIR, "blocks")

FINAL_MASTER_LOCAL = os.path.join(BLOCKS_DIR, "13_flextrawurst_world_FULL_MASTER_1080p60.mp4")
FINAL_MASTER_ARCHIVE_1 = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/13_flextrawurst_world_FULL_MASTER_1080p60.mp4"
FINAL_MASTER_ARCHIVE_2 = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/full-videos/13_flextrawurst_world_FULL_MASTER_1080p60.mp4"

def build_full_master():
    print("\n=======================================================")
    print(">>> ERSTELLE FULL MASTER MIT PFLICHTVIDEO AN 0:00")
    print("=======================================================")

    block_files = [
        PFLICHT_VIDEO,
        os.path.join(BLOCKS_DIR, "b1_flextrawurst_world_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b2_flextrawurst_world_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b3_flextrawurst_world_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b4_flextrawurst_world_1080p60.mp4"),
        os.path.join(BLOCKS_DIR, "b5_flextrawurst_world_1080p60.mp4")
    ]

    for p in block_files:
        if not os.path.exists(p) or os.path.getsize(p) < 1000000:
            print(f"❌ Fehler: Blockdatei fehlt oder ist zu klein: {p}", file=sys.stderr)
            return False

    print("Starte Concat-Pass mit Re-Encoding fuer 100% perfekte Audio/Video-Synchronisation...")
    inputs = []
    filter_in = ""
    for i, p in enumerate(block_files):
        inputs.extend(["-i", p])
        filter_in += f"[{i}:v][{i}:a]"

    concat_cmd = [
        "ffmpeg", "-y", "-v", "warning",
        *inputs,
        "-filter_complex", f"{filter_in}concat=n={len(block_files)}:v=1:a=1[v][a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        FINAL_MASTER_LOCAL
    ]
    res = subprocess.run(concat_cmd)
    if res.returncode != 0:
        print("❌ Re-Encoding Concat fehlgeschlagen!", file=sys.stderr)
        return False

    size_mb = os.path.getsize(FINAL_MASTER_LOCAL) / (1024 * 1024)
    print(f"✓ FULL MASTER ERFOLGREICH ERSTELLT ({size_mb:.1f} MB): {FINAL_MASTER_LOCAL}")

    # Archiv-Kopien
    os.makedirs(os.path.dirname(FINAL_MASTER_ARCHIVE_1), exist_ok=True)
    shutil.copy2(FINAL_MASTER_LOCAL, FINAL_MASTER_ARCHIVE_1)
    print(f"  -> Kopiert ins Archiv 1: {FINAL_MASTER_ARCHIVE_1}")

    os.makedirs(os.path.dirname(FINAL_MASTER_ARCHIVE_2), exist_ok=True)
    shutil.copy2(FINAL_MASTER_LOCAL, FINAL_MASTER_ARCHIVE_2)
    print(f"  -> Kopiert ins Archiv 2: {FINAL_MASTER_ARCHIVE_2}")

    return True

if __name__ == "__main__":
    success = build_full_master()
    sys.exit(0 if success else 1)
