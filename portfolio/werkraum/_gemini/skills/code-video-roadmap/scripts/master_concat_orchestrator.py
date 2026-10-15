#!/usr/bin/env python3
"""
master_concat_orchestrator.py - Automatischer Master-Video-Verketter mit Daniels Pflicht-Intro
Führt alle Blöcke 1 bis N zusammen, erzwingt Daniels Intro an Position 0:00,
beseitigt Pixel-Format-Mismatches (yuv420p vs yuvj420p) per Filter-Graph
und führt sofort das Quality-Gate sowie die Frame-Extraktion für den Voll-Audit aus.
"""

import argparse
import glob
import json
import os
import subprocess
import sys

DEFAULT_INTRO = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/vor_jedes_video_1080p60_normalized.mp4"
RAW_INTRO = "/root/werkraum/_gemini/musikvideoprojekt/assets_shared/vor-jedes-video.mp4"

def parse_args():
    parser = argparse.ArgumentParser(description="Verkette Videoblöcke nahtlos mit Daniels Pflicht-Intro.")
    parser.add_argument("--blocks", "-b", nargs="+", required=True, help="Liste von Block-Videodateien in korrekter Reihenfolge.")
    parser.add_argument("--output", "-o", required=True, help="Pfad zum finalen Master-Video.")
    parser.add_argument("--intro", "-i", default=DEFAULT_INTRO, help="Pfad zum Pflicht-Intro (Standard: vor_jedes_video_1080p60_normalized.mp4).")
    parser.add_argument("--crf", type=int, default=16, help="H.264 CRF (Standard: 16).")
    parser.add_argument("--preset", default="veryfast", help="H.264 Preset (Standard: veryfast).")
    return parser.parse_args()

def ensure_normalized_intro(intro_path):
    if os.path.exists(intro_path):
        return intro_path
    if not os.path.exists(RAW_INTRO):
        raise FileNotFoundError(f"Weder '{intro_path}' noch '{RAW_INTRO}' gefunden!")
    print(f"Normalisiere Pflicht-Intro '{RAW_INTRO}' -> '{intro_path}'...")
    cmd = [
        "ffmpeg", "-y", "-v", "warning",
        "-i", RAW_INTRO,
        "-vf", "fps=60,scale=1080:1920:flags=lanczos,setsar=1/1,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "96000",
        intro_path
    ]
    subprocess.run(cmd, check=True)
    print("✓ Pflicht-Intro normalisiert (1080x1920 @ 60fps CFR, 96kHz).")
    return intro_path

def probe_file(path):
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-print_format", "json", path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe Fehler bei '{path}': {res.stderr}")
    return json.loads(res.stdout)

def main():
    args = parse_args()
    
    # 1. Prüfe Pflicht-Intro
    intro_file = ensure_normalized_intro(args.intro)
    
    # 2. Prüfe alle Blöcke
    input_files = [intro_file]
    for b in args.blocks:
        if not os.path.exists(b):
            print(f"Fehler: Block-Datei '{b}' existiert nicht!", file=sys.stderr)
            sys.exit(1)
        input_files.append(b)
        
    print(f"\n=== MASTER CONCAT ORCHESTRATION ({len(input_files)} Segmente) ===")
    for idx, f in enumerate(input_files):
        sz = os.path.getsize(f) / (1024 * 1024)
        tag = "PFLICHT-INTRO" if idx == 0 else f"BLOCK {idx}"
        print(f"  [{idx}] {tag:<14}: {os.path.basename(f)} ({sz:.1f} MB)")
        
    # 3. Baue sicheren Filter-Graph (Erzwingt yuv420p und CFR 60fps für alle Inputs)
    inputs_cmd = []
    filter_v = []
    filter_a = []
    for i, f in enumerate(input_files):
        inputs_cmd.extend(["-i", f])
        filter_v.append(f"[{i}:v]format=yuv420p,fps=60,setsar=1/1[v{i}];")
        filter_a.append(f"[{i}:a]aformat=sample_rates=96000:channel_layouts=stereo[a{i}];")
        
    concat_v_in = "".join(f"[v{i}]" for i in range(len(input_files)))
    concat_a_in = "".join(f"[a{i}]" for i in range(len(input_files)))
    
    filter_complex = (
        "".join(filter_v) +
        "".join(filter_a) +
        f"{concat_v_in}concat=n={len(input_files)}:v=1:a=0[vmaster];" +
        f"{concat_a_in}concat=n={len(input_files)}:v=0:a=1[amaster]"
    )
    
    cmd = [
        "ffmpeg", "-y", "-v", "warning",
        *inputs_cmd,
        "-filter_complex", filter_complex,
        "-map", "[vmaster]",
        "-map", "[amaster]",
        "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf), "-pix_fmt", "yuv420p", "-r", "60",
        "-c:a", "aac", "-b:a", "320k", "-ar", "96000",
        args.output
    ]
    
    print("\nRendere Master-Video...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Fehler beim Master-Rendering (Exit {res.returncode})", file=sys.stderr)
        sys.exit(res.returncode)
        
    sz_mb = os.path.getsize(args.output) / (1024 * 1024)
    print(f"\n✓ Master-Video erfolgreich erstellt: {args.output} ({sz_mb:.1f} MB)")
    
    # 4. Automatischer Quality-Gate Aufruf
    script_dir = os.path.dirname(os.path.abspath(__file__))
    qa_script = os.path.join(script_dir, "verify_video_qa.py")
    if os.path.exists(qa_script):
        print("\nFühre Quality-Gate Verifikation aus...")
        subprocess.run(["python3", qa_script, "--video", args.output, "--expected-fps", "60.0"], check=True)
        
    # 5. Extrahiere 4 Audit-Frames für visuelle Selbst-Inspektion
    probe = probe_file(args.output)
    dur = float(probe.get("format", {}).get("duration", 0.0))
    audit_times = [
        ("01_intro", 2.0),
        ("02_naht_block1", 6.5),
        ("03_mitte", max(7.0, dur * 0.5)),
        ("04_outro", max(7.0, dur - 3.0))
    ]
    
    out_dir = os.path.dirname(args.output)
    audit_dir = os.path.join(out_dir, "audit_frames_master")
    os.makedirs(audit_dir, exist_ok=True)
    
    print("\n--- MASTER AUDIT-FRAMES (Inaugenscheinnahme via view_file) ---")
    for tag, t in audit_times:
        if t < dur:
            frame_path = os.path.join(audit_dir, f"master_audit_{tag}_{int(t)}s.jpg")
            cmd_frame = ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", args.output, "-frames:v", "1", frame_path]
            subprocess.run(cmd_frame)
            print(f"  [{tag:<15}] @ {t:>6.1f}s -> {frame_path}")
    print("---------------------------------------------------------------\n")

if __name__ == "__main__":
    main()
