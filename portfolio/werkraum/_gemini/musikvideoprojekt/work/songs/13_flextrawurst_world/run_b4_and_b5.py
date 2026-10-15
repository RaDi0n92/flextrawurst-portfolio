#!/usr/bin/env python3
"""
run_b4_and_b5.py - Automatische Generierung, Rendering & QA fuer Block 4 und Block 5
"""

import subprocess
import sys

def run_step(cmd, desc):
    print(f"\n==================================================")
    print(f"   STARTE: {desc}")
    print(f"==================================================")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"❌ FEHLER bei: {desc} (Exit {res.returncode})")
        sys.exit(res.returncode)
    print(f"✓ ERFOLGREICH: {desc}\n")

def main():
    # 1. Block 4 Szenen
    run_step(
        ["python3", "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/generate_block_scenes_horde.py",
         "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/frames/b4_scenes.json",
         "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/frames/b4",
         "BLOCK 4"],
        "AI Horde Generierung fuer Block 4"
    )

    # 2. Block 4 Render
    run_step(
        ["python3", "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/build_block_generic.py", "b4"],
        "Rendering Block 4"
    )

    # 3. Block 4 QA
    run_step(
        ["python3", "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/verify_video_qa.py", "b4"],
        "QA-Audit Block 4"
    )

    # 4. Block 5 Szenen
    run_step(
        ["python3", "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/generate_block_scenes_horde.py",
         "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/frames/b5_scenes.json",
         "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/frames/b5",
         "BLOCK 5"],
        "AI Horde Generierung fuer Block 5"
    )

    # 5. Block 5 Render
    run_step(
        ["python3", "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/build_block_generic.py", "b5"],
        "Rendering Block 5"
    )

    # 6. Block 5 QA
    run_step(
        ["python3", "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world/verify_video_qa.py", "b5"],
        "QA-Audit Block 5"
    )

    print("\n==================================================")
    print("   >>> BLOCK 4 UND BLOCK 5 VOLLSTAENDIG FERTIG! <<<")
    print("==================================================")

if __name__ == "__main__":
    main()
