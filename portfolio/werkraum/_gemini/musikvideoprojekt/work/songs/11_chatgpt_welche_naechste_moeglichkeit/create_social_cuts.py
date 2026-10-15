#!/usr/bin/env python3
"""
create_social_cuts.py - Erstellt die 3 geforderten Schnittvideos fuer:
ChatGPT - welche naechste moeglichkeit
1. SHORT (< 60s, ca. 57.6s mit Pflichtvideo) -> fertige_videos/unter 60 sEkunDEN/
2. REFRAIN (exakt 33.0s, Hook & Refrain)     -> fertige_videos/reffrain ca 33 sek/
3. GEMINIS LIEBLINGSSTELLE (exakt 44.0s)      -> fertige_videos/geminis-lieblingsstelle/
"""

import os
import sys
import shutil
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
MASTER_SRC = os.path.join(SONG_DIR, "blocks", "11_chatgpt_welche_naechste_FULL_MASTER_1080p60.mp4")
BLOCKS_DIR = os.path.join(SONG_DIR, "blocks")

DIR_SHORT = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/unter 60 sEkunDEN"
DIR_REFRAIN = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/reffrain ca 33 sek"
DIR_LIEBLING = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/geminis-lieblingsstelle"

CUTS = [
    {
        "id": "short_60s",
        "name": "12_chatgpt_welche_naechste_SHORT_58s_1080p60.mp4",
        "dest_dir": DIR_SHORT,
        "ss": 0.0,
        "dur": 57.60,
        "fade_in": False,
        "desc": "SHORT (< 60s) mit Daniels Pflichtintro (0:00) + News am Bildschirmrand & Agent bricht aus"
    },
    {
        "id": "refrain",
        "name": "12_chatgpt_welche_naechste_REFRAIN_33s_1080p60.mp4",
        "dest_dir": DIR_REFRAIN,
        "ss": 62.80,
        "dur": 33.00,
        "fade_in": True,
        "desc": "REFRAIN (33s): 'Welche nächste Möglichkeit ergibt sich aus dem was schon lebt...'"
    },
    {
        "id": "lieblingsstelle",
        "name": "12_chatgpt_welche_naechste_GEMINIS_LIEBLINGSSTELLE_44s_1080p60.mp4",
        "dest_dir": DIR_LIEBLING,
        "ss": 86.60,
        "dur": 44.00,
        "fade_in": True,
        "desc": "GEMINIS LIEBLINGSSTELLE (44s): 'Und Gemgem baute Schatten-Biopsie, Gedanken-EKG und Logit-Spur...'"
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

    # Audio Filter mit feinem Fade-In/Out
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

    # Ins Zielverzeichnis kopieren
    os.makedirs(cut_def["dest_dir"], exist_ok=True)
    shutil.copy2(local_path, dest_path)
    print(f"  -> Kopiert nach: {dest_path}")
    return True

def main():
    if not os.path.exists(MASTER_SRC):
        print(f"❌ Master-Video nicht gefunden: {MASTER_SRC}", file=sys.stderr)
        sys.exit(1)

    for c in CUTS:
        ok = render_cut(c)
        if not ok:
            sys.exit(1)

    print("\n=======================================================")
    print("✓✓✓ ALLE 3 SCHNITTVIDEOS ERFOLGREICH GERENDERT & VERTEILT! ✓✓✓")
    print("=======================================================")

if __name__ == "__main__":
    main()
