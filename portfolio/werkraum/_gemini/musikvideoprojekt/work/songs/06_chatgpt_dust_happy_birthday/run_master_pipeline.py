#!/usr/bin/env python3
"""
run_master_pipeline.py - Vollautomatischer End-to-End Orchestrator fuer:
ChatGPT - dust, Happy Birthday (06_chatgpt_dust_happy_birthday)

Fuehrt alle verbleibenden Schritte autonom und deterministisch aus:
1. Block 3 Fertigstellung & Rendern & Audits
2. Block 4 Bildgenerierung & Rendern & Audits
3. Block 5 Bildgenerierung & Rendern & Audits
4. Block 6 Bildgenerierung & Rendern & Audits
5. Master-Concat aller 6 Bloecke (1080p60 CFR) gemaess Daniels Verfassung
6. Bereitstellung auf Desktop & VPS und Extraktion aller Kontrollframes
"""

import os
import sys
import time
import shutil
import subprocess

SONG_DIR = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday"
AUDIT_DIR = "/config/Desktop/KONTROLLBILDER_CHATGPT_HAPPY_BIRTHDAY"
DESKTOP_MASTER_DIR = "/config/Desktop/FERTIGE_MUSIKVIDEOS"
DESKTOP_BLOCKS_DIR = os.path.join(DESKTOP_MASTER_DIR, "EINZELBLOECKE_chatgpt_dust_happy_birthday")
GEN_SCRIPT = "/root/werkraum/_gemini/skills/code-video-roadmap/scripts/generate_horde_images.py"

def run_cmd(cmd, desc):
    print(f"\n>>> [ORCHESTRATOR] {desc}...")
    t0 = time.time()
    res = subprocess.run(cmd, shell=isinstance(cmd, str))
    if res.returncode != 0:
        print(f"✗ FEHLER bei '{desc}': Exit Code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)
    print(f"✓ '{desc}' erfolgreich abgeschlossen in {time.time()-t0:.1f}s")

def extract_audits(video_path, prefix, timestamps):
    os.makedirs(AUDIT_DIR, exist_ok=True)
    for ts in timestamps:
        out_name = f"{prefix}_audit_{int(ts):02d}s.jpg"
        out_path = os.path.join(AUDIT_DIR, out_name)
        c = ["ffmpeg", "-y", "-v", "error", "-ss", str(ts), "-i", video_path, "-frames:v", "1", "-q:v", "2", out_path]
        subprocess.run(c)
        if os.path.exists(out_path):
            print(f"  ✓ Audit: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

def main():
    print("==================================================================")
    print("   FLEXTRAWURST KOSMOS // MASTER PIPELINE ORCHESTRATOR")
    print("   SONG: ChatGPT - dust, Happy Birthday (271.30s @ 1080p60 CFR)")
    print("==================================================================")

    # 1. Block 3
    b3_scenes_json = os.path.join(SONG_DIR, "frames", "b3_scenes.json")
    b3_frames_dir = os.path.join(SONG_DIR, "frames", "b3")
    run_cmd(f"python3 {GEN_SCRIPT} -s {b3_scenes_json} -o {b3_frames_dir}", "Block 3 Bildgenerierung (Vervollstaendigung)")
    run_cmd(f"python3 {os.path.join(SONG_DIR, 'build_block3.py')}", "Block 3 Video Render (1080p60)")
    b3_video = os.path.join(DESKTOP_BLOCKS_DIR, "b3_chatgpt_dust_happy_birthday_1080p60.mp4")
    extract_audits(b3_video, "b3", [5.0, 15.0, 28.0, 42.0])

    # 2. Block 4
    b4_scenes_json = os.path.join(SONG_DIR, "frames", "b4_scenes.json")
    b4_frames_dir = os.path.join(SONG_DIR, "frames", "b4")
    run_cmd(f"python3 {GEN_SCRIPT} -s {b4_scenes_json} -o {b4_frames_dir}", "Block 4 Bildgenerierung")
    run_cmd(f"python3 {os.path.join(SONG_DIR, 'build_block4.py')}", "Block 4 Video Render (1080p60)")
    b4_video = os.path.join(DESKTOP_BLOCKS_DIR, "b4_chatgpt_dust_happy_birthday_1080p60.mp4")
    extract_audits(b4_video, "b4", [5.0, 15.0, 28.0, 42.0])

    # 3. Block 5
    b5_scenes_json = os.path.join(SONG_DIR, "frames", "b5_scenes.json")
    b5_frames_dir = os.path.join(SONG_DIR, "frames", "b5")
    run_cmd(f"python3 {GEN_SCRIPT} -s {b5_scenes_json} -o {b5_frames_dir}", "Block 5 Bildgenerierung")
    run_cmd(f"python3 {os.path.join(SONG_DIR, 'build_block5.py')}", "Block 5 Video Render (1080p60)")
    b5_video = os.path.join(DESKTOP_BLOCKS_DIR, "b5_chatgpt_dust_happy_birthday_1080p60.mp4")
    extract_audits(b5_video, "b5", [5.0, 15.0, 25.0, 35.0])

    # 4. Block 6
    b6_scenes_json = os.path.join(SONG_DIR, "frames", "b6_scenes.json")
    b6_frames_dir = os.path.join(SONG_DIR, "frames", "b6")
    run_cmd(f"python3 {GEN_SCRIPT} -s {b6_scenes_json} -o {b6_frames_dir}", "Block 6 Bildgenerierung")
    run_cmd(f"python3 {os.path.join(SONG_DIR, 'build_block6.py')}", "Block 6 Video Render (1080p60)")
    b6_video = os.path.join(DESKTOP_BLOCKS_DIR, "b6_chatgpt_dust_happy_birthday_1080p60.mp4")
    extract_audits(b6_video, "b6", [5.0, 15.0, 25.0, 40.0])

    # 5. Master-Concat
    run_cmd(f"python3 {os.path.join(SONG_DIR, 'build_full_master.py')}", "Vollstaendiger Master-Concat & Endverifikation")

    print("\n==================================================================")
    print("   ✓✓✓ ALLE BLOECKE UND VOLLSTAENDIGER MASTER FERTIGGESTELLT! ✓✓✓")
    print("==================================================================")

if __name__ == "__main__":
    main()
