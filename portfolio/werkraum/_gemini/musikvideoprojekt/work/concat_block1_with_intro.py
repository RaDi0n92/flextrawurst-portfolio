#!/usr/bin/env python3
import subprocess
import os

intro = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/vor_jedes_video_1080p60_normalized.mp4"
b1 = "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block1_44s_1080p60.mp4"
out = "/root/werkraum/_gemini/musikvideoprojekt/work/output/google_thron_block1_mit_pflichtintro_1080p60.mp4"

concat_txt = "/root/werkraum/_gemini/musikvideoprojekt/work/assets/concat_b1_intro.txt"
with open(concat_txt, "w") as f:
    f.write(f"file '{intro}'\n")
    f.write(f"file '{b1}'\n")

cmd = ["ffmpeg", "-y", "-v", "warning", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", out]
subprocess.run(cmd, check=True)
print(f"✓ Block 1 mit Pflichtstartvideo erstellt: {out}")
