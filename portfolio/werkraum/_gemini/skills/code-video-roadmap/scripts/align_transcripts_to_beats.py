#!/usr/bin/env python3
"""
align_transcripts_to_beats.py - Transienten-Quantizer für Kinetic Typography

Nimmt Whisper-Wort-Timings und quantisiert/snappt ungenaue Wort-Anfänge
magnetisch an die nächstgelegenen Audio-Transienten (Kicks, Snares, Vokal-Onsets).
Verhindert Timing-Drift und Asynchronität bei gesungenem Text.
"""

import argparse
import json
import math
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Quantisiere Whisper-Wort-Timings an Audio-Transienten.")
    parser.add_argument("--transcripts", "-t", required=True, help="Pfad zur JSON-Datei mit Whisper-Wörtern.")
    parser.add_argument("--audio-sync", "-a", required=True, help="Pfad zur audio_sync.json aus audio_beat_mapper.py.")
    parser.add_argument("--tolerance-ms", type=float, default=120.0, help="Maximales Snap-Fenster in ms (Standard: 120ms).")
    parser.add_argument("--output", "-o", default="aligned_words.json", help="Pfad für die kalibrierten Wort-Timings.")
    return parser.parse_args()

def snap_to_transients(words, transient_times_sec, tolerance_sec, fps):
    aligned = []
    snapped_count = 0
    
    for item in words:
        orig_start_sec = item["start_ms"] / 1000.0
        orig_end_sec = item["end_ms"] / 1000.0
        
        # Finde nächsten Transienten
        best_transient = None
        min_dist = float("inf")
        
        for t_sec in transient_times_sec:
            dist = abs(t_sec - orig_start_sec)
            if dist < min_dist:
                min_dist = dist
                best_transient = t_sec
                
        # Wenn innerhalb der Toleranz: magnetisch einrasten
        if best_transient is not None and min_dist <= tolerance_sec:
            new_start_sec = best_transient
            drift_ms = round((new_start_sec - orig_start_sec) * 1000.0, 1)
            snapped_count += 1
        else:
            new_start_sec = orig_start_sec
            drift_ms = 0.0
            
        new_start_frame = int(round(new_start_sec * fps))
        new_end_frame = int(round(orig_end_sec * fps))
        if new_end_frame <= new_start_frame:
            new_end_frame = new_start_frame + 1
            
        aligned.append({
            "word": item["word"],
            "start_ms": int(round(new_start_sec * 1000.0)),
            "end_ms": int(round(orig_end_sec * 1000.0)),
            "start_frame": new_start_frame,
            "end_frame": new_end_frame,
            "snapped": drift_ms != 0.0,
            "drift_corrected_ms": drift_ms
        })
        
    return aligned, snapped_count

def main():
    args = parse_args()
    if not os.path.exists(args.transcripts):
        print(f"Fehler: '{args.transcripts}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.audio_sync):
        print(f"Fehler: '{args.audio_sync}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
        
    with open(args.transcripts, "r", encoding="utf-8") as f:
        raw_words = json.load(f)
    with open(args.audio_sync, "r", encoding="utf-8") as f:
        audio_sync = json.load(f)
        
    fps = audio_sync["meta"]["fps"]
    
    # Kombiniere Kicks und Snares als Snap-Ziele
    transients = sorted(list(set(
        audio_sync["stats"]["kick_times_sec"] + audio_sync["stats"]["snare_times_sec"]
    )))
    
    tolerance_sec = args.tolerance_ms / 1000.0
    aligned, snapped_count = snap_to_transients(raw_words, transients, tolerance_sec, fps)
    
    out_data = {
        "meta": {
            "source_transcripts": os.path.abspath(args.transcripts),
            "source_audio_sync": os.path.abspath(args.audio_sync),
            "fps": fps,
            "tolerance_ms": args.tolerance_ms,
            "total_words": len(raw_words),
            "snapped_words": snapped_count
        },
        "words": aligned
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)
        
    print(f"✓ Transienten-Quantisierung abgeschlossen:")
    print(f"  Gesamt-Wörter: {len(raw_words)}")
    print(f"  An Transienten eingerastet: {snapped_count} Wörter ({snapped_count/len(raw_words)*100:.1f}%)")
    print(f"  Gespeichert in: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
