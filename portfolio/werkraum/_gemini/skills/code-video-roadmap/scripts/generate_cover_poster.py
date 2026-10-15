#!/usr/bin/env python3
"""
generate_cover_poster.py - Automatischer Cover-Poster & Thumbnail-Generator

Extrahiert den optischen Peak-Frame aus den ersten 3 Sekunden eines Videos,
wendet Schärfung und Farbbrillanz an und exportiert ein fertiges Social-Media-Cover.
"""

import argparse
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Extrahiere ein gestochen scharfes Cover-Poster aus einem Video.")
    parser.add_argument("--video", "-v", required=True, help="Pfad zum gerenderten Video.")
    parser.add_argument("--time-sec", "-t", type=float, default=2.2, help="Zeitpunkt in Sekunden für das Cover (Standard: 2.2s).")
    parser.add_argument("--output", "-o", default="cover_poster.jpg", help="Pfad zum Ausgabebild.")
    return parser.parse_args()

def main():
    args = parse_args()
    if not os.path.exists(args.video):
        print(f"Fehler: Video '{args.video}' existiert nicht.", file=sys.stderr)
        sys.exit(1)
        
    print(f"[*] Extrahiere High-CTR Cover-Poster bei t={args.time_sec}s aus '{args.video}'...")
    
    # Extraktion mit Unsharp-Masking für knackige Details auf mobilen Displays
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", str(args.time_sec),
        "-i", args.video,
        "-vframes", "1",
        "-vf", "unsharp=5:5:0.8:5:5:0.4,eq=contrast=1.05:saturation=1.1",
        "-q:v", "2",
        args.output
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Fehler bei Thumbnail-Generierung:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)
        
    print(f"✓ Cover-Poster erfolgreich erzeugt:")
    print(f"  Datei: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
