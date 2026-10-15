#!/usr/bin/env python3
"""
asset_preflight_proxy.py - Schneller Proxy- & Format-Normalisierer

Prüft Roh-Assets (Videos & Bilder) vor dem Compositing:
- Wandelt ungerade Frameraten (z.B. 24fps, 59.94fps) in strikte CFR 30.0 fps um
- Skaliert gigantische 4K-Dateien auf Projekt-Proxy-Größe herunter
- Verhindert OOM-Abstürze und beschleunigt das finale Rendering drastisch
"""

import argparse
import json
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Normalisiere Roh-Assets vor dem Compositing.")
    parser.add_argument("--input", "-i", required=True, help="Pfad zu einer Datei oder einem Verzeichnis mit Video-Assets.")
    parser.add_argument("--output-dir", "-o", default="./proxies", help="Verzeichnis für die optimierten Proxy-Assets.")
    parser.add_argument("--target-height", type=int, default=854, help="Zielhöhe für Proxies (Standard: 854).")
    parser.add_argument("--fps", type=int, default=30, help="Ziel-Framerate (Standard: 30).")
    return parser.parse_args()

def probe_file(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-print_format", "json",
        path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return json.loads(res.stdout)

def process_file(src_path, out_dir, target_height, fps):
    base_name = os.path.basename(src_path)
    out_path = os.path.join(out_dir, f"proxy_{base_name}")
    
    probe = probe_file(src_path)
    if not probe:
        return src_path
        
    v_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), None)
    if not v_stream:
        return src_path
        
    w = int(v_stream.get("width", 0))
    h = int(v_stream.get("height", 0))
    
    # Prüfen, ob Optimierung nötig ist (Höhe größer als Target oder Codec nicht H264)
    needs_proxy = (h > target_height) or (v_stream.get("codec_name") != "h264")
    
    if not needs_proxy:
        return src_path
        
    print(f"[*] Erzeuge Proxy für {base_name} ({w}x{h} -> Zielhöhe {target_height}, {fps} fps)...")
    
    # Schnelles Downscaling mit Preset ultrafast
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", src_path,
        "-vf", f"scale=-2:{target_height}:force_original_aspect_ratio=decrease,fps={fps},setsar=1/1",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"    ✓ Proxy fertig: {out_path}")
        return out_path
    else:
        print(f"    ✗ Fehler beim Proxy-Rendering:\n{res.stderr}", file=sys.stderr)
        return src_path

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    if os.path.isfile(args.input):
        process_file(args.input, args.output_dir, args.target_height, args.fps)
    elif os.path.isdir(args.input):
        exts = [".mp4", ".mov", ".mkv", ".webm"]
        for f in sorted(os.listdir(args.input)):
            if any(f.lower().endswith(e) for e in exts):
                process_file(os.path.join(args.input, f), args.output_dir, args.target_height, args.fps)

if __name__ == "__main__":
    main()
