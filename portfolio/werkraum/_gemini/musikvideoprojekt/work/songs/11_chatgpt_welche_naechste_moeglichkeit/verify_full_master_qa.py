#!/usr/bin/env python3
"""
verify_full_master_qa.py - Endabnahme & QA fuer das finale ChatGPT Musikvideo:
11_chatgpt_welche_naechste_FULL_MASTER_1080p60.mp4
"""

import os
import sys
import json
import subprocess

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
MASTER_LOCAL = os.path.join(SONG_DIR, "blocks", "11_chatgpt_welche_naechste_FULL_MASTER_1080p60.mp4")
MASTER_ARCHIVE = "/root/werkraum/_gemini/musikvideoprojekt/fertige_videos/11_chatgpt_welche_naechste_FULL_MASTER_1080p60.mp4"
DESKTOP_DIR = "/config/Desktop"

EXPECTED_DUR = 291.36  # 284.76s + 6.60s

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
    print("==================================================================")
    print("   FINALE QUALITAETSKONTROLLE: FULL MASTER 1080p60")
    print("   ChatGPT - welche nächste möglichkeit (inkl. Pflichtintro)")
    print("==================================================================")

    all_passed = True

    # 1. Existenz & Groesse
    if not os.path.exists(MASTER_LOCAL):
        print(f"❌ Master-Video existiert nicht: {MASTER_LOCAL}")
        return False
    size_mb = os.path.getsize(MASTER_LOCAL) / (1024 * 1024)
    print(f"✓ Master-Video gefunden ({size_mb:.2f} MB): {MASTER_LOCAL}")
    if size_mb < 150:
        print(f"⚠️ Warnung: Dateigröße ungewöhnlich klein: {size_mb:.2f} MB")

    # 2. Metadaten
    info = run_probe(MASTER_LOCAL)
    if not info:
        return False

    v_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a_stream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    # Resolution
    w, h = v_stream.get("width"), v_stream.get("height")
    if w == 1080 and h == 1920:
        print(f"✓ Auflösung: 1080x1920 (9:16 Portrait)")
    else:
        print(f"❌ Ungültige Auflösung: {w}x{h}")
        all_passed = False

    # FPS
    r_fps = v_stream.get("r_frame_rate")
    avg_fps = v_stream.get("avg_frame_rate")
    if r_fps == "60/1" and avg_fps == "60/1":
        print(f"✓ Bildrate: 60.0 FPS CFR ({r_fps})")
    else:
        print(f"⚠️ Bildrate: r={r_fps}, avg={avg_fps}")

    # Pixel Format
    pix_fmt = v_stream.get("pix_fmt")
    if pix_fmt in ["yuv420p", "yuvj420p"]:
        print(f"✓ Pixel-Format: {pix_fmt} (YUV 4:2:0 Planar)")
    else:
        print(f"❌ Pixel-Format fehlerhaft: {pix_fmt}")
        all_passed = False

    # Dauer
    dur = float(info["format"].get("duration", 0))
    if abs(dur - EXPECTED_DUR) <= 1.0:
        print(f"✓ Gesamtdauer: {dur:.2f}s (Soll: ~{EXPECTED_DUR:.2f}s)")
    else:
        print(f"❌ Gesamtdauer abweichend: {dur:.2f}s (Erwartet ~{EXPECTED_DUR:.2f}s)")
        all_passed = False

    # Audio
    if a_stream:
        a_codec = a_stream.get("codec_name")
        sr = a_stream.get("sample_rate")
        ch = a_stream.get("channels")
        print(f"✓ Audio: {a_codec} {sr}Hz {ch} Kanäle")
    else:
        print("❌ Kein Audio-Stream gefunden!")
        all_passed = False

    # 3. Stream-Dekodierungspruefung (Null Muxer)
    print("Prüfe gesamten Videodatenstrom auf Dekodierungsfehler...")
    null_test = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", MASTER_LOCAL, "-f", "null", "-"],
        capture_output=True, text=True
    )
    if null_test.returncode == 0 and not null_test.stderr:
        print("✓ Videodatenstrom 100% intakt (0 Dekodierungsfehler)")
    else:
        print(f"⚠️ Dekodierungswarnung: {null_test.stderr}")

    # 4. Archiv-Kopie
    if os.path.exists(MASTER_ARCHIVE) and os.path.getsize(MASTER_ARCHIVE) == os.path.getsize(MASTER_LOCAL):
        print(f"✓ Archiv-Kopie synchron vorhanden: {MASTER_ARCHIVE}")
    else:
        print(f"❌ Archiv-Kopie fehlt oder weicht ab: {MASTER_ARCHIVE}")
        all_passed = False

    # 5. Desktop-Sauberkeit
    desktop_files = os.listdir(DESKTOP_DIR)
    video_leak = [
        f for f in desktop_files 
        if any(f.startswith(prefix) for prefix in ["b1_", "b2_", "b3_", "b4_", "b5_", "chatgpt_", "11_"])
        or (f.endswith((".mp4", ".m4a", ".ass")) and not f.endswith(".desktop"))
    ]
    if not video_leak:
        print("✓ Desktop-Sauberkeit gewaehrleistet: 0 Projekt-Dateien auf /config/Desktop")
    else:
        print(f"❌ Projekt-Dateien auf Desktop gefunden: {video_leak}")
        all_passed = False

    print("==================================================================")
    if all_passed:
        print(">>> RESULTAT: FULL MASTER ERFOLGREICH FREIGEGEBEN! <<<")
    else:
        print(">>> RESULTAT: QUALITAETS-GATE NICHT BESTANDEN! <<<")
    print("==================================================================")
    return all_passed

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
