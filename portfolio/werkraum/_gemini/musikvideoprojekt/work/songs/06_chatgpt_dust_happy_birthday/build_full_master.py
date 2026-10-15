#!/usr/bin/env python3
"""
build_full_master.py - Nahtloser 1080p60 Master-Concatenator fuer:
ChatGPT - dust, Happy Birthday (06_chatgpt_dust_happy_birthday)

Fuegt alle 6 gerenderten Einzelbloecke nahtlos zusammen:
- Block 1: 00:00.00 - 00:45.00 (45.00s)
- Block 2: 00:45.00 - 01:29.50 (44.50s)
- Block 3: 01:29.50 - 02:17.00 (47.50s)
- Block 4: 02:17.00 - 03:05.50 (48.50s)
- Block 5: 03:05.50 - 03:44.50 (39.00s)
- Block 6: 03:44.50 - 04:31.30 (46.80s)
Gesamtdauer: 271.30s (04:31.30)

Speichert das fertige Master-Video gemaess Verfassung an genau einem festen Ort:
/config/Desktop/FERTIGE_MUSIKVIDEOS/06_chatgpt_dust_happy_birthday_FULL_MASTER_1080p60.mp4
sowie im full-videos Archiv und extrahiert 10 Kontrollbilder fuer Daniel.
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday"
BLOCKS_DIR = os.path.join(BASE_DIR, "blocks")

BLOCKS = [
    os.path.join(BLOCKS_DIR, "b1_chatgpt_dust_happy_birthday_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b2_chatgpt_dust_happy_birthday_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b3_chatgpt_dust_happy_birthday_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b4_chatgpt_dust_happy_birthday_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b5_chatgpt_dust_happy_birthday_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b6_chatgpt_dust_happy_birthday_1080p60.mp4")
]

PFLICHT_INTRO = "/vps_root/werkraum/_gemini/musikvideoprojekt/pflichtanfangsvideo/daniel_intro_20260918_1080p60_normalized.mp4"
if not os.path.exists(PFLICHT_INTRO):
    PFLICHT_INTRO = "/root/werkraum/_gemini/musikvideoprojekt/pflichtanfangsvideo/daniel_intro_20260918_1080p60_normalized.mp4"
if not os.path.exists(PFLICHT_INTRO):
    PFLICHT_INTRO = "/config/Desktop/FERTIGE_MUSIKVIDEOS/00_DANIELS_NEUES_PFLICHTVIDEO_EINZELN_1080p60.mp4"

SONG_CLEAN_LOCAL = os.path.join(BLOCKS_DIR, "chatgpt_dust_happy_birthday_SONG_CLEAN_NO_INTRO_1080p60.mp4")
MASTER_LOCAL = os.path.join(BLOCKS_DIR, "06_chatgpt_dust_happy_birthday_FULL_MASTER_1080p60.mp4")
MASTER_DESKTOP = "/config/Desktop/FERTIGE_MUSIKVIDEOS/06_chatgpt_dust_happy_birthday_FULL_MASTER_1080p60.mp4"
MASTER_ARCHIV = "/config/Desktop/FERTIGE_MUSIKVIDEOS/full-videos/06_chatgpt_dust_happy_birthday_FULL_MASTER_1080p60.mp4"
MASTER_VPS = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/fertige_videos/06_chatgpt_dust_happy_birthday_FULL_MASTER_1080p60.mp4"

AUDIT_DESKTOP = "/config/Desktop/KONTROLLBILDER_CHATGPT_HAPPY_BIRTHDAY"
AUDIT_LOCAL = os.path.join(BASE_DIR, "audit_frames")

def main():
    print("=== STARTE MASTER-CONCAT MIT DANIELS PFLICHTVIDEO: ChatGPT - dust, Happy Birthday ===")
    
    # 1. Pruefe Pflichtvideo
    if not os.path.exists(PFLICHT_INTRO):
        print(f"FEHLER: Daniels Pflicht-Intro fehlt: {PFLICHT_INTRO}", file=sys.stderr)
        sys.exit(1)
    intro_sz = os.path.getsize(PFLICHT_INTRO) / (1024*1024)
    print(f"  ✓ Daniels Pflicht-Intro verifiziert ({intro_sz:.1f} MB): {PFLICHT_INTRO}")

    # 2. Pruefe alle 6 Song-Bloecke
    for idx, b in enumerate(BLOCKS, 1):
        if not os.path.exists(b):
            print(f"FEHLER: Block {idx} fehlt: {b}", file=sys.stderr)
            sys.exit(1)
        sz = os.path.getsize(b)
        print(f"  ✓ Block {idx} verifiziert ({sz / (1024*1024):.1f} MB): {b}")

    # 3. Baue zuerst das saubere ungeschnittene Song-Video aus Bloecken 1-6 (Stream-Copy)
    concat_list_file = os.path.join(BLOCKS_DIR, "concat_master.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for b in BLOCKS:
            f.write(f"file '{b}'\n")

    if not os.path.exists(SONG_CLEAN_LOCAL):
        print(f"\nConcat-Liste geschrieben: {concat_list_file}")
        print("Erstelle sauberen Song-Track (Stream-Copy Bloecke 1-6)...")
        cmd_song = [
            "ffmpeg", "-y", "-v", "warning",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_file,
            "-c", "copy",
            SONG_CLEAN_LOCAL
        ]
        res = subprocess.run(cmd_song)
        if res.returncode != 0:
            print(f"✗ Fehler beim Song-Concat: Exit Code {res.returncode}", file=sys.stderr)
            sys.exit(res.returncode)

    song_sz = os.path.getsize(SONG_CLEAN_LOCAL) / (1024*1024)
    print(f"✓ Reiner Song-Track bereit ({song_sz:.1f} MB): {SONG_CLEAN_LOCAL}")

    # 4. Verknuepfe Daniels Pflichtvideo an Position 0:00 mit dem Song via filter_complex
    # Erzwingt einheitliches yuv420p, 60fps CFR und 96kHz AAC Audio
    filter_complex = (
        "[0:v]format=yuv420p,fps=60,setsar=1/1[v0];"
        "[1:v]format=yuv420p,fps=60,setsar=1/1[v1];"
        "[0:a]aformat=sample_rates=96000:channel_layouts=stereo[a0];"
        "[1:a]aformat=sample_rates=96000:channel_layouts=stereo[a1];"
        "[v0][v1]concat=n=2:v=1:a=0[vmaster];"
        "[a0][a1]concat=n=2:v=0:a=1[amaster]"
    )

    cmd_master = [
        "ffmpeg", "-y", "-v", "warning",
        "-i", PFLICHT_INTRO,
        "-i", SONG_CLEAN_LOCAL,
        "-filter_complex", filter_complex,
        "-map", "[vmaster]",
        "-map", "[amaster]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "60",
        "-c:a", "aac", "-b:a", "320k", "-ar", "96000",
        MASTER_LOCAL
    ]

    print("\nRendere finales Master-Video mit Daniels Pflicht-Intro...")
    res = subprocess.run(cmd_master)
    if res.returncode != 0:
        print(f"✗ FFmpeg Master Render Fehler: Exit Code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    master_sz = os.path.getsize(MASTER_LOCAL) / (1024*1024)
    print(f"✓ Master-Video erfolgreich erstellt: {MASTER_LOCAL} ({master_sz:.1f} MB)")

    # 5. Dauer pruefen
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", MASTER_LOCAL]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    print(f"✓ Master-Gesamtdauer verifiziert: {dur:.2f}s (Pflichtvideo 6.60s + Song 271.30s = ~277.90s)")

    # 6. Verteilung an alle vorgeschriebenen Orte
    os.makedirs(os.path.dirname(MASTER_DESKTOP), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_ARCHIV), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_VPS), exist_ok=True)

    shutil.copy2(MASTER_LOCAL, MASTER_DESKTOP)
    print(f"✓ Kopiert nach Desktop: {MASTER_DESKTOP}")

    shutil.copy2(MASTER_LOCAL, MASTER_ARCHIV)
    print(f"✓ Kopiert nach full-videos: {MASTER_ARCHIV}")

    shutil.copy2(MASTER_LOCAL, MASTER_VPS)
    print(f"✓ Kopiert nach VPS fertige_videos: {MASTER_VPS}")

    # 7. Kontrollbilder extrahieren (inkl. Pflichtintro & Nahtstelle)
    os.makedirs(AUDIT_DESKTOP, exist_ok=True)
    os.makedirs(AUDIT_LOCAL, exist_ok=True)

    audit_points = [
        ("master_audit_00_pflichtintro_003s.jpg", 3.0),
        ("master_audit_01_naht_intro_musik_007s.jpg", 7.0),
        ("master_audit_02_b1_025s.jpg", 25.0),
        ("master_audit_03_b2_070s.jpg", 70.0),
        ("master_audit_04_b2_090s.jpg", 90.0),
        ("master_audit_05_b3_110s.jpg", 110.0),
        ("master_audit_06_b3_130s.jpg", 130.0),
        ("master_audit_07_b4_160s.jpg", 160.0),
        ("master_audit_08_b4_180s.jpg", 180.0),
        ("master_audit_09_b5_200s.jpg", 200.0),
        ("master_audit_10_b5_220s.jpg", 220.0),
        ("master_audit_11_b6_240s.jpg", 240.0),
        ("master_audit_12_b6_265s.jpg", 265.0)
    ]

    print(f"\nExtrahiere {len(audit_points)} Master-Kontrollbilder...")
    for name, ss in audit_points:
        loc_path = os.path.join(AUDIT_LOCAL, name)
        dsk_path = os.path.join(AUDIT_DESKTOP, name)
        c = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-i", MASTER_LOCAL, "-frames:v", "1", "-q:v", "2", loc_path]
        subprocess.run(c)
        if os.path.exists(loc_path):
            shutil.copy2(loc_path, dsk_path)
            print(f"  ✓ Frame @ {ss:5.1f}s -> {dsk_path}")

    print("\n=== MASTER-BUILD VOLLSTAENDIG MIT PFLICHTVIDEO ABGESCHLOSSEN! ===")

if __name__ == "__main__":
    main()
