#!/usr/bin/env python3
"""
concat_full_google_thron.py - Nahtlose Zusammenführung aller Blöcke inkl. Daniels Pflichtstartvideo
Track: "GoogleKI-Suche - Ich schieße gegen den Thron"
Dauer: ca. 05:31 Min (Pflicht-Intro + voller Song)
Qualität: 1080x1920 @ 60.00 FPS CFR, H.264 CRF 16, 320 kbps AAC Stereo 96 kHz
"""

import subprocess
import os
import sys

OUTPUT_FULL = "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_FULL_MASTER_1080p60.mp4"
CONCAT_TXT = "/root/werkraum/_gemini/musikvideoprojekt/work/assets/google_thron_concat_list.txt"

BLOCKS = [
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block1_mit_pflichtintro_1080p60.mp4",
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block2_44s_1080p60.mp4",
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block3_44s_1080p60.mp4",
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block4_45s_1080p60.mp4",
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block5_44s_1080p60.mp4",
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block6_52s_1080p60.mp4",
    "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block7_51s_1080p60.mp4",
]

print("=== START CONCATENATION: GoogleKI-Suche Full Master mit Daniels Pflicht-Intro ===")

with open(CONCAT_TXT, "w") as f:
    for b in BLOCKS:
        if not os.path.exists(b):
            print(f"Fehler: Block fehlt: {b}", file=sys.stderr)
            sys.exit(1)
        sz_mb = os.path.getsize(b) / (1024 * 1024)
        print(f"  Gefunden: {os.path.basename(b)} ({sz_mb:.1f} MB)")
        f.write(f"file '{b}'\n")

print(f"Concat-Liste geschrieben: {CONCAT_TXT}")

# Filter-Concat für 100% lückenlosen, perfekten Übergang
# Alle 7 Inputs concatten:
inputs = []
filter_v = []
filter_a = []
for i, b in enumerate(BLOCKS):
    inputs.extend(["-i", b])
    filter_v.append(f"[{i}:v]")
    filter_a.append(f"[{i}:a]")

filter_complex = "".join(filter_v) + f"concat=n={len(BLOCKS)}:v=1:a=0[v];" + "".join(filter_a) + f"concat=n={len(BLOCKS)}:v=0:a=1[a]"

cmd = [
    "ffmpeg", "-y", "-v", "warning",
    *inputs,
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "60",
    "-c:a", "aac", "-b:a", "320k", "-ar", "96000",
    OUTPUT_FULL
]

print("Führe Master-Concat aus...")
res = subprocess.run(cmd)

if res.returncode == 0:
    print(f"✓ Master-Gesamtvideo mit Pflicht-Intro erfolgreich erstellt: {OUTPUT_FULL}")
    sz_mb = os.path.getsize(OUTPUT_FULL) / (1024 * 1024)
    print(f"  Dateigröße: {sz_mb:.1f} MB")
else:
    print(f"✗ Fehler bei Concat: Exit Code {res.returncode}", file=sys.stderr)
    sys.exit(res.returncode)
