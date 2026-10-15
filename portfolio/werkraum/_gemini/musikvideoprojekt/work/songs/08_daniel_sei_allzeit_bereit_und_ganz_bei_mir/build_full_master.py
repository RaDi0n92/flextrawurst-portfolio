#!/usr/bin/env python3
"""
build_full_master.py - Nahtloser 1080p60 Master-Concatenator fuer:
Daniel (flextrawurst) - sei-allzeit-bereit-und-ganz-bei-mir (08_daniel_sei_allzeit_bereit_und_ganz_bei_mir)

Fuegt alle 2 gerenderten Einzelbloecke nahtlos zusammen:
- Block 1: 00:00.00 - 00:49.40 (49.40s)
- Block 2: 00:49.40 - 01:44.80 (55.40s)
Gesamtdauer: 104.80s (01:44.80)

WICHTIGE ANWEISUNGEN:
- Kein Introvideo vor dem Song (Daniel: 'ohne introvideo davor')
- Kein Muell auf den Desktop! Alle Dateien bleiben strikt in VPS_ROOT / root/werkraum.
- Speichert das fertige Master-Video an den vorgeschriebenen Archiv-Orten:
  1. /root/werkraum/_gemini/musikvideoprojekt/work/songs/08_daniel_sei_allzeit_bereit_und_ganz_bei_mir/blocks/08_daniel_sei_allzeit_bereit_FULL_MASTER_1080p60.mp4
  2. /root/werkraum/_gemini/musikvideoprojekt/fertige_videos/full-videos/08_daniel_sei_allzeit_bereit_FULL_MASTER_1080p60.mp4
  3. /root/werkraum/_gemini/musikvideoprojekt/fertige_videos/08_daniel_sei_allzeit_bereit_FULL_MASTER_1080p60.mp4
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/08_daniel_sei_allzeit_bereit_und_ganz_bei_mir"
BLOCKS_DIR = os.path.join(BASE_DIR, "blocks")

BLOCKS = [
    os.path.join(BLOCKS_DIR, "b1_daniel_sei_allzeit_bereit_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b2_daniel_sei_allzeit_bereit_1080p60.mp4")
]

MASTER_AUDIO = os.path.join(BASE_DIR, "audio", "daniel_sei_allzeit_bereit_14lufs.m4a")
MASTER_LOCAL = os.path.join(BLOCKS_DIR, "08_daniel_sei_allzeit_bereit_FULL_MASTER_1080p60.mp4")
MASTER_ARCHIV_FULL = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/full-videos/08_daniel_sei_allzeit_bereit_FULL_MASTER_1080p60.mp4"
MASTER_ARCHIV_ROOT = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/08_daniel_sei_allzeit_bereit_FULL_MASTER_1080p60.mp4"

AUDIT_LOCAL = os.path.join(BASE_DIR, "audits", "master_audit_frames")

def main():
    print("=== STARTE MASTER-CONCAT FUER: Daniel - sei allzeit bereit und ganz bei mir ===")
    
    # 1. Pruefe Bloecke
    for idx, b in enumerate(BLOCKS, 1):
        if not os.path.exists(b):
            print(f"FEHLER: Block {idx} fehlt: {b}", file=sys.stderr)
            sys.exit(1)
        sz = os.path.getsize(b)
        print(f"  ✓ Block {idx} verifiziert ({sz / (1024*1024):.1f} MB): {b}")

    if not os.path.exists(MASTER_AUDIO):
        print(f"FEHLER: Master-Audio fehlt: {MASTER_AUDIO}", file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ Master Audio verifiziert: {MASTER_AUDIO}")

    # 2. Concat-Liste schreiben
    concat_list_file = os.path.join(BLOCKS_DIR, "concat_master.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for b in BLOCKS:
            f.write(f"file '{b}'\n")
    print(f"\nConcat-Liste geschrieben: {concat_list_file}")

    # 3. Stream-Copy Concat mit durchgehendem Studio-Master-Audio (-14 LUFS)
    print("Fuehre verlustfreien Stream-Copy Concat durch...")
    cmd_master = [
        "ffmpeg", "-y", "-v", "warning",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-i", MASTER_AUDIO,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "copy",
        "-t", "104.80",
        MASTER_LOCAL
    ]
    res = subprocess.run(cmd_master)
    if res.returncode != 0:
        print(f"✗ Fehler beim Master-Concat: Exit Code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    master_sz = os.path.getsize(MASTER_LOCAL) / (1024*1024)
    print(f"✓ Master-Video erfolgreich erstellt: {MASTER_LOCAL} ({master_sz:.1f} MB)")

    # 4. Dauer & Frames pruefen
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", MASTER_LOCAL]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    print(f"✓ Master-Gesamtdauer: {dur:.2f}s (Soll: 104.80s)")

    # 5. Verteilung an Archiv-Orte (NIEMALS AUF DEN DESKTOP!)
    os.makedirs(os.path.dirname(MASTER_ARCHIV_FULL), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_ARCHIV_ROOT), exist_ok=True)

    shutil.copy2(MASTER_LOCAL, MASTER_ARCHIV_FULL)
    print(f"✓ Kopiert nach: {MASTER_ARCHIV_FULL}")

    shutil.copy2(MASTER_LOCAL, MASTER_ARCHIV_ROOT)
    print(f"✓ Kopiert nach: {MASTER_ARCHIV_ROOT}")

    # 6. Kontrollbilder extrahieren (im audits-Ordner des Songs)
    os.makedirs(AUDIT_LOCAL, exist_ok=True)
    audit_points = [
        ("master_audit_01_b1_start_002s.jpg", 2.0),
        ("master_audit_02_b1_mid_025s.jpg", 25.0),
        ("master_audit_03_seam_before_049s.jpg", 49.0),
        ("master_audit_04_seam_after_050s.jpg", 50.0),
        ("master_audit_05_b2_mid_075s.jpg", 75.0),
        ("master_audit_06_b2_outro_103s.jpg", 103.0)
    ]

    print(f"\nExtrahiere {len(audit_points)} Master-Kontrollbilder...")
    for name, ss in audit_points:
        loc_path = os.path.join(AUDIT_LOCAL, name)
        c = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-i", MASTER_LOCAL, "-frames:v", "1", "-q:v", "2", loc_path]
        subprocess.run(c)
        if os.path.exists(loc_path):
            print(f"  ✓ Frame @ {ss:5.1f}s -> {loc_path}")

    # Aufraeumen von temporaeren Testdateien
    test_file = os.path.join(BLOCKS_DIR, "test_master.mp4")
    if os.path.exists(test_file):
        os.remove(test_file)
    test_concat = os.path.join(BLOCKS_DIR, "concat_test.txt")
    if os.path.exists(test_concat):
        os.remove(test_concat)

    print("\n=== MASTER-BUILD FUER DANIEL VOLLSTAENDIG ERFOLGREICH ABGESCHLOSSEN! ===")

if __name__ == "__main__":
    main()
