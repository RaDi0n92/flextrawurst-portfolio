#!/usr/bin/env python3
"""
normalize_audio_lufs.py - Lautheits-Normalisierung für Streaming & Social Media
Führt eine professionelle Dual-Pass Lautheits-Korrektur via FFmpeg loudnorm durch:
- Target Integrated Loudness: -14.0 LUFS (Social-Media & YouTube/TikTok/Reels Standard)
  (Hinweis: Das offizielle EBU-R128 Broadcast-Target liegt bei -23.0 LUFS; für Mobile/Web
   wird bewusst das lautere -14.0 LUFS Streaming-Target nach ITU-R BS.1770 Messnorm genutzt)
- Maximum True Peak: -1.0 dBTP / dBFS (Verhindert Inter-Sample Clipping)
- Loudness Range (LRA): 7.0 LU
"""

import argparse
import json
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Dual-Pass Lautheits-Mastering für Streaming & Social Media (-14 LUFS nach BS.1770/EBU-Verfahren).")
    parser.add_argument("--input", "-i", required=True, help="Pfad zur Quell-Audiodatei.")
    parser.add_argument("--target-lufs", type=float, default=-14.0, help="Ziel-Lautheit in LUFS (Standard: -14.0 für Social-Media / -23.0 für EBU Broadcast).")
    parser.add_argument("--true-peak", type=float, default=-1.0, help="Maximaler True Peak in dBTP / dBFS (Standard: -1.0).")
    parser.add_argument("--lra", type=float, default=7.0, help="Loudness Range (Standard: 7.0).")
    parser.add_argument("--output", "-o", default=None, help="Pfad zur normalisierten Ausgabedatei.")
    return parser.parse_args()

def main():
    args = parse_args()
    if not os.path.exists(args.input):
        print(f"Fehler: Datei '{args.input}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
        
    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(args.input)
        out_path = f"{base}_mastered_lufs{ext}"
        
    print(f"[*] Starte Dual-Pass BS.1770/EBU Lautheits-Normalisierung für '{args.input}'...")
    print(f"    Ziel: {args.target_lufs} LUFS (Streaming-Target) | True Peak: {args.true_peak} dBTP")

    # Pass 1: Messung (benötigt -v info, da loudnorm JSON auf info-Ebene loggt)
    cmd_pass1 = [
        "ffmpeg", "-v", "info",
        "-i", args.input,
        "-af", f"loudnorm=I={args.target_lufs}:TP={args.true_peak}:LRA={args.lra}:print_format=json",
        "-f", "null",
        "-"
    ]
    
    proc = subprocess.run(cmd_pass1, capture_output=True, text=True)
    stderr = proc.stderr
    
    # Parse JSON output from stderr
    try:
        json_start = stderr.find("{")
        json_end = stderr.rfind("}") + 1
        stats = json.loads(stderr[json_start:json_end])
    except Exception as e:
        print(f"Fehler beim Parsen der Lautheitsmessung (Pass 1):\n{stderr}", file=sys.stderr)
        sys.exit(1)
        
    measured_i = float(stats.get("input_i", -99))
    measured_tp = float(stats.get("input_tp", -99))
    measured_lra = float(stats.get("input_lra", 0))
    measured_thresh = float(stats.get("input_thresh", -99))
    offset = float(stats.get("target_offset", 0))
    
    print(f"    -> Gemessen: {measured_i} LUFS (Peak: {measured_tp} dBFS, LRA: {measured_lra})")
    
    # Pass 2: Lineare Normalisierung mit gemessenen Werten
    filter_pass2 = (
        f"loudnorm=I={args.target_lufs}:TP={args.true_peak}:LRA={args.lra}:"
        f"measured_I={measured_i}:measured_TP={measured_tp}:"
        f"measured_LRA={measured_lra}:measured_thresh={measured_thresh}:"
        f"offset={offset}:linear=true"
    )
    
    codec_args = ["-c:a", "libmp3lame", "-b:a", "320k"] if out_path.endswith(".mp3") else ["-c:a", "aac", "-b:a", "320k"]
    cmd_pass2 = [
        "ffmpeg", "-y", "-v", "error",
        "-i", args.input,
        "-vn",
        "-af", filter_pass2,
        *codec_args,
        "-ar", "48000",
        out_path
    ]
    
    res2 = subprocess.run(cmd_pass2, capture_output=True, text=True)
    if res2.returncode != 0:
        print(f"Fehler bei Normalisierung (Pass 2):\n{res2.stderr}", file=sys.stderr)
        sys.exit(1)
        
    print(f"✓ Lautheits-Mastering erfolgreich abgeschlossen!")
    print(f"  Ausgabe: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    main()
