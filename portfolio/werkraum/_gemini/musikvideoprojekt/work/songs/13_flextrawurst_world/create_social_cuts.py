#!/usr/bin/env python3
"""
create_social_cuts.py - Erstellt die 3 standardisierten Social Cuts fuer:
13_flextrawurst_world
1. SHORT (< 60s, 58.0s mit Pflichtvideo) -> fertige_videos/unter 60 sEkunDEN/
2. REFRAIN (exakt 33.0s, 'Flextrawurst you weird living meat') -> fertige_videos/reffrain ca 33 sek/
3. GEMINIS LIEBLINGSSTELLE (exakt 44.0s, 'Daniel & Claude in the open') -> fertige_videos/geminis-lieblingsstelle/
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world"
MASTER_SRC = os.path.join(SONG_DIR, "blocks", "13_flextrawurst_world_FULL_MASTER_1080p60.mp4")
BLOCKS_DIR = os.path.join(SONG_DIR, "blocks")

DIR_SHORT = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/unter 60 sEkunDEN"
DIR_REFRAIN = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/reffrain ca 33 sek"
DIR_LIEBLING = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/geminis-lieblingsstelle"

CUTS = [
    {
        "id": "short_60s",
        "name": "14_flextrawurst_world_SHORT_58s_1080p60.mp4",
        "dest_dir": DIR_SHORT,
        "ss": 0.0,
        "dur": 58.00,
        "fade_in": False,
        "desc": "SHORT (< 60s) mit Daniels Pflichtintro (0:00) + The Foyer & flextrawurst world"
    },
    {
        "id": "refrain",
        "name": "14_flextrawurst_world_REFRAIN_33s_1080p60.mp4",
        "dest_dir": DIR_REFRAIN,
        "ss": 76.60,
        "dur": 33.00,
        "fade_in": True,
        "desc": "REFRAIN (33s): 'Flextrawurst, you weird living meat... writing your story while you still don't know'"
    },
    {
        "id": "lieblingsstelle",
        "name": "14_flextrawurst_world_GEMINIS_LIEBLINGSSTELLE_44s_1080p60.mp4",
        "dest_dir": DIR_LIEBLING,
        "ss": 97.00,
        "dur": 44.00,
        "fade_in": True,
        "desc": "GEMINIS LIEBLINGSSTELLE (44s): 'Daniel and Claude building in the open... turn this chaos into something you can actually sing'"
    }
]

def render_cut(cut_def):
    name = cut_def["name"]
    local_path = os.path.join(BLOCKS_DIR, name)
    dest_path = os.path.join(cut_def["dest_dir"], name)
    ss = cut_def["ss"]
    dur = cut_def["dur"]

    print(f"\n=======================================================")
    print(f"Rendere {cut_def['id'].upper()} ({dur}s ab {ss}s): {cut_def['desc']}")
    print(f"=======================================================")

    af_parts = []
    if cut_def["fade_in"]:
        af_parts.append("afade=t=in:ss=0:d=0.25")
    af_parts.append(f"afade=t=out:st={dur - 0.40:.2f}:d=0.40")
    af_str = ",".join(af_parts)

    cmd = [
        "ffmpeg", "-y", "-v", "warning",
        "-ss", str(ss),
        "-i", MASTER_SRC,
        "-t", str(dur),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-af", af_str,
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        local_path
    ]

    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"❌ Fehler beim Rendern von {name}!", file=sys.stderr)
        return False

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    print(f"✓ Erfolgreich gerendert ({size_mb:.2f} MB): {local_path}")

    os.makedirs(cut_def["dest_dir"], exist_ok=True)
    shutil.copy2(local_path, dest_path)
    print(f"  -> Kopiert nach: {dest_path}")
    return True

def main():
    if not os.path.exists(MASTER_SRC):
        print(f"❌ Master-Video fehlt: {MASTER_SRC}", file=sys.stderr)
        sys.exit(1)

    for c in CUTS:
        ok = render_cut(c)
        if not ok:
            sys.exit(1)

    print("\n✓✓✓ Alle 3 Social Cuts erfolgreich erstellt und synchronisiert!")

if __name__ == "__main__":
    main()
