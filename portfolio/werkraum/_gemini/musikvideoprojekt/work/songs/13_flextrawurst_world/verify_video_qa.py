#!/usr/bin/env python3
"""
verify_video_qa.py - Qualitaetskontrolle fuer Flextrawurst-World Bloecke
"""

import os
import sys
import json
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world"
DESKTOP_DIR = "/config/Desktop"

EXPECTED_DURS = {
    "b1": (49.00, 48.80, 49.20),
    "b2": (59.00, 58.80, 59.20),
    "b3": (60.00, 59.80, 60.20),
    "b4": (30.00, 29.80, 30.20),
    "b5": (27.00, 26.80, 27.20),
}

def run_probe(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,sample_rate,channels,pix_fmt",
        "-of", "json",
        path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ ffprobe Fehler: {res.stderr}")
        return None
    return json.loads(res.stdout)

def main(block_id="b1"):
    print("==================================================")
    print(f"   QUALITAETS-GATE & AUDIT: FLEXTRAWURST-WORLD {block_id.upper()}     ")
    print("==================================================")

    video_filename = f"{block_id}_flextrawurst_world_1080p60.mp4"
    video_path = os.path.join(SONG_DIR, "blocks", video_filename)

    all_passed = True

    # 1. Existenz des Block-Videos
    if not os.path.exists(video_path):
        print(f"❌ Video existiert nicht: {video_path}")
        return False
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"✓ Video gefunden ({size_mb:.2f} MB): {video_path}")

    # 2. FFprobe Metadaten-Check
    info = run_probe(video_path)
    if not info:
        return False

    v_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a_stream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    # Resolution
    w, h = v_stream.get("width"), v_stream.get("height")
    if w == 1080 and h == 1920:
        print(f"✓ Aufloesung: 1080x1920 (9:16 Portrait)")
    else:
        print(f"❌ Ungueltige Aufloesung: {w}x{h} (Erwartet 1080x1920)")
        all_passed = False

    # FPS
    r_fps = v_stream.get("r_frame_rate")
    avg_fps = v_stream.get("avg_frame_rate")
    if r_fps == "60/1" and avg_fps == "60/1":
        print(f"✓ Bildrate: 60.0 FPS CFR ({r_fps})")
    else:
        print(f"⚠️ Bildrate abweichend: r={r_fps}, avg={avg_fps}")

    # Pix Fmt
    pix_fmt = v_stream.get("pix_fmt")
    if pix_fmt in ["yuv420p", "yuvj420p"]:
        print(f"✓ Pixel-Format: {pix_fmt} (YUV 4:2:0 Planar)")
    else:
        print(f"❌ Pixel-Format: {pix_fmt} (Erwartet yuv420p / yuvj420p)")
        all_passed = False

    # Duration
    dur = float(info["format"].get("duration", 0))
    target_dur, min_dur, max_dur = EXPECTED_DURS.get(block_id, (30.0, 25.0, 35.0))
    if min_dur <= dur <= max_dur:
        print(f"✓ Dauer: {dur:.2f}s (Soll: ~{target_dur:.2f}s)")
    else:
        print(f"❌ Dauer abweichend: {dur:.2f}s (Erwartet: {min_dur}s - {max_dur}s)")
        all_passed = False

    # Audio
    if a_stream:
        a_codec = a_stream.get("codec_name")
        sr = a_stream.get("sample_rate")
        ch = a_stream.get("channels")
        print(f"✓ Audio Stream: {a_codec} {sr}Hz {ch}ch")
    else:
        print(f"❌ Kein Audio-Stream gefunden!")
        all_passed = False

    # 3. Stream-Dekodierungspruefung (Null Muxer)
    print("Pruefe Videodatenstrom auf Korruption...")
    null_test = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", video_path, "-f", "null", "-"],
        capture_output=True, text=True
    )
    if null_test.returncode == 0 and not null_test.stderr:
        print("✓ Stream-Integritaet: 100% sauber, 0 Dekodierungsfehler!")
    else:
        print(f"❌ Dekodierungsfehler festgestellt: {null_test.stderr}")
        all_passed = False

    # 4. Desktop-Sauberkeits-Check
    desktop_files = [f for f in os.listdir(DESKTOP_DIR) if f.endswith((".mp4", ".m4a", ".jpg", ".png", ".ass"))]
    if not desktop_files:
        print("✓ Desktop-Sauberkeit: 100% sauber, keine Artefakte auf /config/Desktop")
    else:
        print(f"⚠️ Warnung: Dateien auf Desktop gefunden: {desktop_files}")

    print("==================================================")
    if all_passed:
        print(f"   >>> {block_id.upper()} QA STATUS: 100% BESTANDEN <<<")
    else:
        print(f"   >>> {block_id.upper()} QA STATUS: FEHLERHAFT <<<")
    print("==================================================")
    return all_passed

if __name__ == "__main__":
    b = sys.argv[1] if len(sys.argv) > 1 else "b1"
    success = main(b)
    sys.exit(0 if success else 1)
