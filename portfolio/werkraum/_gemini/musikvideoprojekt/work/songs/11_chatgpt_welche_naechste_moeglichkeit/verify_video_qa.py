#!/usr/bin/env python3
"""
verify_video_qa.py - Umfassende Qualitaetskontrolle fuer Block 1
ChatGPT - welche naechste moeglichkeit
"""

import os
import sys
import json
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
VIDEO_PATH = os.path.join(SONG_DIR, "blocks", "b1_chatgpt_welche_naechste_1080p60.mp4")
ARCHIVE_PATH = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/EINZELBLOECKE_CHATGPT/b1_chatgpt_welche_naechste_1080p60.mp4"
DESKTOP_DIR = "/config/Desktop"

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

def main():
    print("==================================================")
    print("   QUALITAETS-GATE & AUDIT: CHATGPT BLOCK 1       ")
    print("==================================================")

    all_passed = True

    # 1. Existenz des Block-Videos
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video existiert nicht: {VIDEO_PATH}")
        return False
    size_mb = os.path.getsize(VIDEO_PATH) / (1024 * 1024)
    print(f"✓ Video gefunden ({size_mb:.2f} MB): {VIDEO_PATH}")

    # 2. FFprobe Metadaten-Check
    info = run_probe(VIDEO_PATH)
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
    if 55.70 <= dur <= 55.95:
        print(f"✓ Dauer: {dur:.2f}s (Soll: ~55.80s)")
    else:
        print(f"❌ Dauer abweichend: {dur:.2f}s")
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
        ["ffmpeg", "-v", "error", "-i", VIDEO_PATH, "-f", "null", "-"],
        capture_output=True, text=True
    )
    if null_test.returncode == 0 and not null_test.stderr:
        print("✓ Datenstrom intakt, 0 Dekodierungsfehler")
    else:
        print(f"⚠️ Warnung beim Dekodieren: {null_test.stderr}")

    # 4. Archiv-Kopie Pruefung
    if os.path.exists(ARCHIVE_PATH) and os.path.getsize(ARCHIVE_PATH) == os.path.getsize(VIDEO_PATH):
        print(f"✓ Archiv-Kopie vorhanden und synchron: {ARCHIVE_PATH}")
    else:
        print(f"❌ Archiv-Kopie fehlt oder weicht ab: {ARCHIVE_PATH}")
        all_passed = False

    # 5. Desktop Sauberkeit (Keine Video-Projektdateien / Symlinks auf dem Desktop)
    desktop_files = os.listdir(DESKTOP_DIR)
    # Finde Projekt-bezogene Dateien (z.B. b1_*, chatgpt_*, mp4, m4a, ass, json aus dem Projekt)
    video_leak = [
        f for f in desktop_files 
        if any(f.startswith(prefix) for prefix in ["b1_", "chatgpt_", "daniel_", "08_", "09_", "10_", "11_"])
        or (f.endswith((".mp4", ".m4a", ".ass")) and not f.endswith(".desktop"))
    ]
    if not video_leak:
        print("✓ Desktop-Sauberkeit gewaehrleistet: 0 Projekt-Dateien / Leaks auf /config/Desktop")
    else:
        print(f"❌ Projekt-Dateien auf Desktop gefunden: {video_leak}")
        all_passed = False

    print("==================================================")
    if all_passed:
        print(">>> RESULTAT: QUALITAETS-GATE ERFOLGREICH PASSIERT! <<<")
    else:
        print(">>> RESULTAT: FEHLER IM QUALITAETS-GATE! <<<")
    print("==================================================")
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
