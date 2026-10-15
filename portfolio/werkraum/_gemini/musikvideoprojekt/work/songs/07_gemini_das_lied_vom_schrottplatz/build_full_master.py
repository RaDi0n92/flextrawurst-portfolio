#!/usr/bin/env python3
"""
build_full_master.py - Nahtloser 1080p60 Master-Concatenator fuer:
Gemini - Das Lied vom Schrottplatz (07_gemini_das_lied_vom_schrottplatz)

Fuegt alle 5 gerenderten Einzelbloecke nahtlos zusammen:
- Block 1: 00:00.00 - 00:44.40 (44.40s)
- Block 2: 00:44.40 - 01:28.16 (43.76s)
- Block 3: 01:28.16 - 02:05.80 (37.64s)
- Block 4: 02:05.80 - 02:57.40 (51.60s)
- Block 5: 02:57.40 - 03:50.00 (52.60s)
Gesamtdauer Song: 230.00s (03:50.00)

Verknuepft Daniels Pflicht-Intro (6.60s) an Position 0:00:
Gesamtdauer Master: 236.60s (03:56.60)

Speichert das fertige Master-Video an den vorgeschriebenen Orten:
- /root/werkraum/_gemini/musikvideoprojekt/fertige_videos/full-videos/07_gemini_das_lied_vom_schrottplatz_FULL_MASTER_1080p60.mp4
- /root/werkraum/_gemini/musikvideoprojekt/fertige_videos/07_gemini_das_lied_vom_schrottplatz_FULL_MASTER_1080p60.mp4
- Symlink auf Desktop: /config/Desktop/07_GEMINI_DAS_LIED_VOM_SCHROTTPLATZ_FULL_MASTER_1080p60.mp4
Und raeumt die 5 temporaeren Einzelblock-Symlinks vom Desktop auf!
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
BLOCKS_DIR = os.path.join(BASE_DIR, "blocks")

BLOCKS = [
    os.path.join(BLOCKS_DIR, "b1_gemini_das_lied_vom_schrottplatz_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b2_gemini_das_lied_vom_schrottplatz_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b3_gemini_das_lied_vom_schrottplatz_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b4_gemini_das_lied_vom_schrottplatz_1080p60.mp4"),
    os.path.join(BLOCKS_DIR, "b5_gemini_das_lied_vom_schrottplatz_1080p60.mp4")
]

PFLICHT_INTRO = "/root/werkraum/_gemini/musikvideoprojekt/pflichtanfangsvideo/daniel_intro_20260918_1080p60_normalized.mp4"
if not os.path.exists(PFLICHT_INTRO):
    PFLICHT_INTRO = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/pflichtanfangsvideo/daniel_intro_20260918_1080p60_normalized.mp4"

SONG_CLEAN_LOCAL = os.path.join(BLOCKS_DIR, "gemini_das_lied_vom_schrottplatz_SONG_CLEAN_NO_INTRO_1080p60.mp4")
MASTER_LOCAL = os.path.join(BLOCKS_DIR, "07_gemini_das_lied_vom_schrottplatz_FULL_MASTER_1080p60.mp4")
MASTER_ARCHIV = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/full-videos/07_gemini_das_lied_vom_schrottplatz_FULL_MASTER_1080p60.mp4"
MASTER_VPS = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/07_gemini_das_lied_vom_schrottplatz_FULL_MASTER_1080p60.mp4"
MASTER_DESKTOP = "/config/Desktop/07_GEMINI_DAS_LIED_VOM_SCHROTTPLATZ_FULL_MASTER_1080p60.mp4"

def main():
    print("=== STARTE MASTER-CONCAT MIT DANIELS PFLICHTVIDEO: Gemini - Das Lied vom Schrottplatz ===")
    
    # 1. Pruefe Pflichtvideo
    if not os.path.exists(PFLICHT_INTRO):
        print(f"FEHLER: Daniels Pflicht-Intro fehlt: {PFLICHT_INTRO}", file=sys.stderr)
        sys.exit(1)
    intro_sz = os.path.getsize(PFLICHT_INTRO) / (1024*1024)
    print(f"  ✓ Daniels Pflicht-Intro verifiziert ({intro_sz:.1f} MB): {PFLICHT_INTRO}")

    # 2. Pruefe alle 5 Song-Bloecke
    for idx, b in enumerate(BLOCKS, 1):
        if not os.path.exists(b):
            print(f"FEHLER: Block {idx} fehlt: {b}", file=sys.stderr)
            sys.exit(1)
        sz = os.path.getsize(b)
        print(f"  ✓ Block {idx} verifiziert ({sz / (1024*1024):.1f} MB): {b}")

    # 3. Baue zuerst das saubere ungeschnittene Song-Video aus Bloecken 1-5 (Stream-Copy)
    concat_list_file = os.path.join(BLOCKS_DIR, "concat_master.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for b in BLOCKS:
            f.write(f"file '{b}'\n")

    MASTER_AUDIO = os.path.join(BASE_DIR, "audio", "das_lied_vom_schrottplatz_14lufs.m4a")
    print(f"\nConcat-Liste geschrieben: {concat_list_file}")
    print("Erstelle sauberen Song-Track mit kontinuierlichem Studio-Master Audio...")
    cmd_song = [
        "ffmpeg", "-y", "-v", "warning",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-i", MASTER_AUDIO,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "copy",
        "-t", "230.00",
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
    print(f"✓ Master-Gesamtdauer verifiziert: {dur:.2f}s (Pflichtvideo 6.60s + Song 230.00s = ~236.60s)")

    # 6. Verteilung an Zielorte
    os.makedirs(os.path.dirname(MASTER_ARCHIV), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_VPS), exist_ok=True)

    shutil.copy2(MASTER_LOCAL, MASTER_ARCHIV)
    print(f"✓ Kopiert nach full-videos: {MASTER_ARCHIV}")

    shutil.copy2(MASTER_LOCAL, MASTER_VPS)
    print(f"✓ Kopiert nach VPS fertige_videos: {MASTER_VPS}")

    # 7. Bereinige etwaige temporaere Symlinks vom Desktop
    print("\nRaeume temporaere Einzelbloecke vom Desktop auf...")
    for i in range(1, 6):
        dsk_block = f"/config/Desktop/BLOCK{i}_SCHROTTPLATZ.mp4"
        if os.path.islink(dsk_block) or os.path.exists(dsk_block):
            try:
                os.remove(dsk_block)
                print(f"  ✓ Entfernt: {dsk_block}")
            except Exception as e:
                print(f"  ✗ Konnte {dsk_block} nicht entfernen: {e}")

    print("\n=== MASTER-BUILD VOLLSTAENDIG MIT PFLICHTVIDEO ABGESCHLOSSEN! ===")

if __name__ == "__main__":
    main()
