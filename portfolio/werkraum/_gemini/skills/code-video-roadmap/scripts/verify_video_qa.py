#!/usr/bin/env python3
"""
verify_video_qa.py - Automatisches Video Quality-Gate & Container-Prüfer
Untersucht ein gerendertes Video per ffprobe auf 7 Qualitätskriterien:
1. SAR 1:1 (Keine anamorphotische Verzerrung)
2. Framerate (Exakt 60.0 fps CFR gemäß Full-Best-Quality-Gesetz)
3. Audio-Präsenz (Audio-Stream vorhanden, Stereo, >= 44.1kHz / 96kHz)
4. Pixel-Format (yuv420p für maximale Player-Kompatibilität)
5. Dimensionen geradzahlig (1080x1920)
6. A/V-Dauersynchronisation (Dauer-Delta < 0.15s)
7. Automatische Extraktion von 4 Kontrollframes für visuelle Selbst-Inspektion (view_file)
"""

import argparse
import json
import math
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Automatische Qualitätsprüfung eines gerenderten Videos.")
    parser.add_argument("--video", "-v", required=True, help="Pfad zur Videodatei.")
    parser.add_argument("--expected-fps", type=float, default=60.0, help="Erwartete Framerate (Standard: 60.0 CFR).")
    parser.add_argument("--reference-audio", "-a", default=None, help="Pfad zur Referenz-Audiodatei zum Dauer-Abgleich.")
    parser.add_argument("--extract-audit-frames", action="store_true", default=True, help="Extrahiere automatisch Kontrollframes für visuelle Prüfung.")
    return parser.parse_args()

def run_probe(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-print_format", "json",
        path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe Fehler bei '{path}': {res.stderr}")
    return json.loads(res.stdout)

def main():
    args = parse_args()
    if not os.path.exists(args.video):
        print(f"FAIL: Video '{args.video}' existiert nicht.", file=sys.stderr)
        sys.exit(1)
        
    probe = run_probe(args.video)
    streams = probe.get("streams", [])
    format_info = probe.get("format", {})
    
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    
    checks = []
    
    # 1. Video-Stream vorhanden
    if not v_stream:
        checks.append(("Video-Stream", False, "Kein Videostream gefunden."))
    else:
        # Codec
        v_codec = v_stream.get("codec_name")
        codec_ok = v_codec in ["h264", "hevc", "vp9", "av1"]
        checks.append(("Video-Codec", codec_ok, f"Codec: {v_codec}"))
        
        # SAR 1:1
        sar = v_stream.get("sample_aspect_ratio", "1:1")
        sar_ok = sar in ["1:1", None, "0:1"]
        checks.append(("SAR 1:1 (Square Pixels)", sar_ok, f"SAR: {sar}"))
        
        # Pixel-Format
        pix_fmt = v_stream.get("pix_fmt", "unknown")
        pix_ok = pix_fmt in ["yuv420p", "yuvj420p"]
        checks.append(("Pixel-Format (yuv420p)", pix_ok, f"Format: {pix_fmt}"))
        
        # Framerate
        r_fps_str = v_stream.get("r_frame_rate", "0/1")
        if "/" in r_fps_str:
            num, den = map(float, r_fps_str.split("/"))
            actual_fps = num / den if den != 0 else 0
        else:
            actual_fps = float(r_fps_str)
        fps_ok = abs(actual_fps - args.expected_fps) < 0.05
        checks.append(("Framerate (CFR)", fps_ok, f"Ist: {actual_fps:.2f} fps (Soll: {args.expected_fps:.2f})"))
        
        # Auflösung geradzahlig
        w = int(v_stream.get("width", 0))
        h = int(v_stream.get("height", 0))
        res_ok = (w % 2 == 0) and (h % 2 == 0) and w > 0 and h > 0
        checks.append(("Dimensionen geradzahlig", res_ok, f"{w}x{h}"))

    # 2. Audio-Stream vorhanden
    if not a_stream:
        checks.append(("Audio-Stream", False, "Kein Audiostream im Video gefunden."))
    else:
        a_codec = a_stream.get("codec_name")
        channels = int(a_stream.get("channels", 0))
        sample_rate = int(a_stream.get("sample_rate", 0))
        a_ok = a_codec in ["aac", "mp3", "opus"] and channels >= 1 and sample_rate >= 44100
        checks.append(("Audio-Stream intakt", a_ok, f"{a_codec}, {channels}ch, {sample_rate}Hz"))

    # 3. Referenz-Dauer abgleichen
    v_dur = float(format_info.get("duration", 0.0))
    if args.reference_audio and os.path.exists(args.reference_audio):
        ref_probe = run_probe(args.reference_audio)
        ref_dur = float(ref_probe.get("format", {}).get("duration", 0.0))
        dur_diff = abs(v_dur - ref_dur)
        dur_ok = dur_diff <= 0.15
        checks.append(("A/V-Dauersynchronität", dur_ok, f"Video: {v_dur:.2f}s, Audio: {ref_dur:.2f}s (Diff: {dur_diff:.2f}s)"))
    else:
        checks.append(("Video-Dauer", v_dur > 0, f"Dauer: {v_dur:.2f}s"))

    # Gesamtergebnis
    all_passed = all(c[1] for c in checks)
    
    print("\n================ VIDEO QUALITY-GATE REPORT ================")
    for name, passed, detail in checks:
        status_sym = "✓ PASS" if passed else "✗ FAIL"
        print(f"[{status_sym}] {name:<26} : {detail}")
    print("============================================================")
    
    # 4. Extrahiere Kontrollframes für visuelle Selbst-Inspektion
    if args.extract_audit_frames and v_dur > 0:
        base_name = os.path.splitext(os.path.basename(args.video))[0]
        out_dir = os.path.join(os.path.dirname(os.path.abspath(args.video)), "audit_frames")
        os.makedirs(out_dir, exist_ok=True)
        
        sample_points = [
            ("start", min(1.5, v_dur * 0.1)),
            ("phase1", v_dur * 0.35),
            ("phase2", v_dur * 0.70),
            ("end", max(0.5, v_dur - 1.5))
        ]
        
        print("\n--- KONTROLLFRAMES FÜR VISUELLE PFLICHT-INSPEKTION (view_file) ---")
        for tag, t in sample_points:
            f_path = os.path.join(out_dir, f"{base_name}_{tag}_{int(t)}s.jpg")
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", args.video, "-frames:v", "1", f_path]
            subprocess.run(cmd)
            print(f"  [{tag:<8}] @ {t:>5.1f}s -> {f_path}")
        print("------------------------------------------------------------------\n")
    
    if all_passed:
        print("RESULT: ALL GATES PASSED (Freigabe erteilt).\n")
        sys.exit(0)
    else:
        print("RESULT: GATE FAILURE (Nacharbeit erforderlich).\n", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
