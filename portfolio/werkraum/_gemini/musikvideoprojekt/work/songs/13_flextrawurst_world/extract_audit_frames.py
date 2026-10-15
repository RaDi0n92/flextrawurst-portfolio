#!/usr/bin/env python3
"""
extract_audit_frames.py - Extrahiert Audit-Snapshots aus Block 1 Video
"""

import os
import sys
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world"

def extract_frames(block_id="b1"):
    video_path = os.path.join(SONG_DIR, "blocks", f"{block_id}_flextrawurst_world_1080p60.mp4")
    out_dir = os.path.join(SONG_DIR, "audits", block_id)
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(video_path):
        print(f"Video existiert nicht: {video_path}")
        return False

    timestamps = [
        ("05s", 5.0),
        ("12s", 12.0),
        ("21s", 21.0),
        ("27s", 27.0),
        ("33s", 33.0),
        ("39s", 39.0),
        ("44s", 44.0)
    ]

    for label, ts in timestamps:
        out_jpg = os.path.join(out_dir, f"{block_id}_snapshot_{label}.jpg")
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-ss", str(ts),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            out_jpg
        ]
        subprocess.run(cmd)
        if os.path.exists(out_jpg):
            print(f"✓ Snapshot {label} bei {ts}s extrahiert: {out_jpg}")

    return True

if __name__ == "__main__":
    b = sys.argv[1] if len(sys.argv) > 1 else "b1"
    extract_frames(b)
