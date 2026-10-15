#!/usr/bin/env python3
import subprocess
import os

video = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/12_codewesen_der_erste_takt/blocks/b1_codewesen_der_erste_takt_1080p60.mp4"
audit_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/12_codewesen_der_erste_takt/audits"
os.makedirs(audit_dir, exist_ok=True)

for sec in [15, 35, 50]:
    out_img = os.path.join(audit_dir, f"b1_frame_{sec:02d}s.jpg")
    cmd = ["ffmpeg", "-y", "-ss", str(sec), "-i", video, "-frames:v", "1", "-q:v", "2", out_img]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(out_img):
        print(f"✓ Snapshot bei {sec}s: {out_img}")
