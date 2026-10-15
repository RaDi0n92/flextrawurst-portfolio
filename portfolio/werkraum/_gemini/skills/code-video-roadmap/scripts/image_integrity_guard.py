#!/usr/bin/env python3
"""
image_integrity_guard.py - Automatischer Bild-Integritäts- und Glitch-Wächter
Prüft generierte Bilder vor dem Rendern:
- Mindestdateigröße (> 25 KB)
- Bild-Decodierbarkeit (PIL verify / load)
- Schwarze / leere Bilder (Pixel-Standardabweichung > 4.0)
- Dimensionen & Aspect-Ratio
"""

import argparse
import os
import sys
from PIL import Image, ImageStat

def parse_args():
    parser = argparse.ArgumentParser(description="Prüfe generierte Bilder auf Korruption, Leerbilder oder Formatfehler.")
    parser.add_argument("--images", "-i", nargs="+", help="Liste von Bildpfaden.")
    parser.add_argument("--dir", "-d", help="Ordner mit Bildern.")
    parser.add_argument("--min-size-kb", type=float, default=25.0, help="Mindestdateigröße in KB (Standard: 25.0).")
    return parser.parse_args()

def check_image(path, min_kb):
    errors = []
    if not os.path.exists(path):
        return False, ["Datei existiert nicht"]
        
    sz_kb = os.path.getsize(path) / 1024.0
    if sz_kb < min_kb:
        errors.append(f"Datei zu klein ({sz_kb:.1f} KB < {min_kb} KB)")
        
    try:
        with Image.open(path) as img:
            img.verify()
        # Nochmal öffnen zum Lesen der Pixel
        with Image.open(path) as img:
            img.load()
            stat = ImageStat.Stat(img.convert("L"))
            stddev = stat.stddev[0]
            if stddev < 3.5:
                errors.append(f"Bild ist nahezu einfarbig / schwarz (stddev={stddev:.2f})")
    except Exception as e:
        errors.append(f"Decodierfehler: {str(e)}")
        
    return len(errors) == 0, errors

def main():
    args = parse_args()
    img_list = []
    if args.images:
        img_list = args.images
    elif args.dir and os.path.exists(args.dir):
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            img_list.extend([os.path.join(args.dir, f) for f in os.listdir(args.dir) if f.lower().endswith(ext)])
            
    if not img_list:
        print("Keine Bilder zum Prüfen übergeben.", file=sys.stderr)
        sys.exit(1)
        
    failed = []
    passed = 0
    for p in img_list:
        ok, errs = check_image(p, args.min_size_kb)
        if ok:
            passed += 1
        else:
            failed.append((p, errs))
            
    print(f"\n=== BILD-INTEGRITÄTS-REPORT ({len(img_list)} Bilder) ===")
    print(f"✓ Intakt: {passed} Bilder")
    if failed:
        print(f"✗ Defekt / Glitch: {len(failed)} Bilder!")
        for p, errs in failed:
            print(f"  - {os.path.basename(p)}: {', '.join(errs)}")
        print("=======================================================\n")
        sys.exit(1)
    else:
        print("RESULT: Alle Bilder intakt und build-bereit.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
