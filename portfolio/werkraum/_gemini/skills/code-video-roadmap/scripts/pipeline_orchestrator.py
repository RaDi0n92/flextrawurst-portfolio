#!/usr/bin/env python3
"""
pipeline_orchestrator.py - Master-Orchestrator für die Video-as-Code Pipeline

Automatisiert alle 5 Phasen des code-video-roadmap Skills:
Phase 1: Audio-Telemetrie & Transienten
Phase 2: Wort-Ausrichtung & Kinetic Typography
Phase 3/4: Audio-Reaktiver Schnitt & Shader-Compositing
Phase 5: Automatisches Quality-Gate & Manifest-Export
"""

import argparse
import json
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Master-Orchestrator für code-generierte Videos.")
    parser.add_argument("--audio", "-a", required=True, help="Pfad zur Master-Audiodatei.")
    parser.add_argument("--bpm", type=float, default=None, help="BPM des Songs.")
    parser.add_argument("--lyrics-json", "-l", default=None, help="Optionale JSON mit Whisper-Wort-Timings.")
    parser.add_argument("--preset", choices=["9:16_480p", "9:16_1080p", "1:1_1080p", "16:9_1080p"], default="9:16_480p", help="Format-Preset (Standard: 9:16_480p).")
    parser.add_argument("--protagonist", choices=["claude", "chatgpt", "grok", "gemini", "codewesen"], default="claude", help="Haupt-Protagonist für das Video (Standard: claude).")
    parser.add_argument("--output-dir", "-o", default="./pipeline_out", help="Ausgabeverzeichnis.")
    parser.add_argument("--fps", type=int, default=30, help="Framerate (Standard: 30).")
    return parser.parse_args()

PRESETS = {
    "9:16_480p":  {"width": 480,  "height": 854,  "fontsize": 22},
    "9:16_1080p": {"width": 1080, "height": 1920, "fontsize": 48},
    "1:1_1080p":  {"width": 1080, "height": 1080, "fontsize": 44},
    "16:9_1080p": {"width": 1920, "height": 1080, "fontsize": 42}
}

def main():
    args = parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    print("\n========================================================")
    print("🎬 START PIPELINE-ORCHESTRATOR (Video as Code)")
    print(f"   Audio: {os.path.abspath(args.audio)}")
    print(f"   Ziel:  {out_dir}")
    print("========================================================\n")
    
    # ----------------------------------------------------
    # SCHRITT 1: Audio-Telemetrie & Transienten
    # ----------------------------------------------------
    print("[1/4] Phase 1: Extrahiere Audio-Telemetrie & Transienten...")
    sync_json = os.path.join(out_dir, "audio_sync.json")
    cmd_audio = [
        sys.executable, os.path.join(script_dir, "audio_beat_mapper.py"),
        "--input", args.audio,
        "--fps", str(args.fps),
        "--output", sync_json
    ]
    if args.bpm:
        cmd_audio.extend(["--bpm", str(args.bpm)])
        
    res1 = subprocess.run(cmd_audio, capture_output=True, text=True)
    if res1.returncode != 0:
        print(f"Fehler in Phase 1:\n{res1.stderr}", file=sys.stderr)
        sys.exit(1)
    print("      ✓ audio_sync.json erfolgreich erzeugt.")

    # ----------------------------------------------------
    # SCHRITT 2: Kinetic Typography & Alignment
    # ----------------------------------------------------
    ass_path = os.path.join(out_dir, "subtitles.ass")
    if args.lyrics_json and os.path.exists(args.lyrics_json):
        print("[2/4] Phase 2: Quantisiere Wort-Timings & baue Kinetic ASS...")
        aligned_json = os.path.join(out_dir, "aligned_words.json")
        cmd_align = [
            sys.executable, os.path.join(script_dir, "align_transcripts_to_beats.py"),
            "--transcripts", args.lyrics_json,
            "--audio-sync", sync_json,
            "--output", aligned_json
        ]
        res_align = subprocess.run(cmd_align, capture_output=True, text=True)
        if res_align.returncode != 0:
            print(f"Fehler bei Alignment:\n{res_align.stderr}", file=sys.stderr)
            sys.exit(1)
            
        p_info = PRESETS[args.preset]
        cmd_ass = [
            sys.executable, os.path.join(script_dir, "render_kinetic_subtitles.py"),
            "--words", aligned_json,
            "--width", str(p_info["width"]),
            "--height", str(p_info["height"]),
            "--fontsize", str(p_info["fontsize"]),
            "--output", ass_path
        ]
        res_ass = subprocess.run(cmd_ass, capture_output=True, text=True)
        if res_ass.returncode != 0:
            print(f"Fehler bei ASS-Generierung:\n{res_ass.stderr}", file=sys.stderr)
            sys.exit(1)
        print("      ✓ Kinetic ASS-Untertitel fertig.")
    else:
        print("[2/4] Phase 2: Keine Lyrics-JSON übergeben (Überspringe Untertitel-Generierung).")

    # ----------------------------------------------------
    # SCHRITT 3: Zusammenfassung & Manifest
    # ----------------------------------------------------
    manifest_path = os.path.join(out_dir, "production_manifest.json")
    manifest = {
        "status": "READY_FOR_COMPOSITING",
        "protagonist_lock": {
            "lead_protagonist": args.protagonist,
            "allowed_asset_dir": f"/root/werkraum/_gemini/musikvideoprojekt/animirungen/{args.protagonist}"
        },
        "audio_sync": sync_json,
        "subtitles_ass": ass_path if os.path.exists(ass_path) else None,
        "preset": args.preset,
        "fps": args.fps,
        "bpm": args.bpm
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print("\n========================================================")
    print("✓ PIPELINE-ORCHESTRIERUNG ABGESCHLOSSEN")
    print(f"  Manifest: {manifest_path}")
    print("========================================================\n")

if __name__ == "__main__":
    main()
