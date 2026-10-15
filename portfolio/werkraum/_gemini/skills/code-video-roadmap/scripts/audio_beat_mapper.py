#!/usr/bin/env python3
"""
audio_beat_mapper.py - Multi-Band Transienten- und Frequenz-Mapper für Video-as-Code

Extrahiert 3 echte Frequenzbänder (Sub-Bass, Vocals, Highs) via FFmpeg-Filter
sowie framegenaue Transienten-Peaks für deterministisches Motion-Design.
"""

import argparse
import json
import math
import os
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Extrahiere echte Frequenzbänder & Beats für code-generierte Videos.")
    parser.add_argument("--input", "-i", required=True, help="Pfad zur Audiodatei oder Videodatei.")
    parser.add_argument("--fps", type=int, default=30, help="Ziel-Framerate für das spätere Video (Standard: 30).")
    parser.add_argument("--bpm", type=float, default=None, help="BPM des Songs (optional, für Takt-Raster).")
    parser.add_argument("--first-beat-sec", type=float, default=None, help="Zeitpunkt des ersten Downbeats in Sekunden (Takt 1). Wenn weggelassen, wird der erste Kick-Transient verwendet.")
    parser.add_argument("--output", "-o", default="audio_sync.json", help="Pfad für die generierte JSON-Datei.")
    return parser.parse_args()

def get_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Fehler beim Lesen der Dauer: {res.stderr}")
    return float(res.stdout.strip())

def extract_band_rms(audio_path, total_frames, fps, af_filter):
    """Extrahiert RMS-Werte für ein spezifisches Frequenzband über FFmpeg."""
    sample_rate = fps * 100
    samples_per_frame = 100
    bytes_per_sample = 2
    frame_bytes = samples_per_frame * bytes_per_sample

    cmd = [
        "ffmpeg", "-v", "error",
        "-i", audio_path,
        "-af", af_filter,
        "-ac", "1",
        "-ar", str(sample_rate),
        "-f", "s16le",
        "-"
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw_audio, _ = proc.communicate()
    
    energies = []
    max_e = 1e-6
    for f in range(total_frames):
        start_idx = f * frame_bytes
        end_idx = start_idx + frame_bytes
        chunk = raw_audio[start_idx:end_idx]
        if not chunk:
            energies.append(0.0)
            continue
        
        count = len(chunk) // 2
        sum_sq = 0
        for i in range(count):
            val = int.from_bytes(chunk[i*2:(i+1)*2], byteorder="little", signed=True)
            sum_sq += val * val
        rms = math.sqrt(sum_sq / count) if count > 0 else 0.0
        energies.append(rms)
        if rms > max_e:
            max_e = rms
            
    # Normalisieren auf 0.0 - 1.0
    return [round(e / max_e, 4) for e in energies]

def detect_onsets(band_energies, min_energy=0.35, min_delta=0.12):
    """Erkennt Onsets/Peaks basierend auf steilen Energieflanken."""
    onsets = []
    for f in range(1, len(band_energies) - 1):
        delta = band_energies[f] - band_energies[f-1]
        if band_energies[f] >= min_energy and delta >= min_delta:
            if band_energies[f] >= band_energies[f+1]:
                onsets.append(f)
    return onsets

def main():
    args = parse_args()
    if not os.path.exists(args.input):
        print(f"Fehler: Datei '{args.input}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
        
    duration = get_duration(args.input)
    total_frames = int(math.ceil(duration * args.fps))
    
    print(f"[*] Analysiere {duration:.2f}s Audio ({total_frames} Frames @ {args.fps} fps)...")
    
    # 1. Sub-Bass (20 - 130 Hz) -> Echte Kicks und 808
    print("    -> Extrahiere Sub-Bass Band (20 - 130 Hz)...")
    sub_bass = extract_band_rms(args.input, total_frames, args.fps, "highpass=f=20,lowpass=f=130")
    
    # 2. Vocals / Mitten (300 - 3000 Hz) -> Menschliche/Synthetische Gesangsstimme
    print("    -> Extrahiere Vocal / Mitten Band (300 - 3000 Hz)...")
    vocals = extract_band_rms(args.input, total_frames, args.fps, "highpass=f=300,lowpass=f=3000")
    
    # 3. Highs / Transienten (4500 - 16000 Hz) -> Snares, Hi-Hats, Claps
    print("    -> Extrahiere Highs / Snare Band (4500 - 16000 Hz)...")
    highs = extract_band_rms(args.input, total_frames, args.fps, "highpass=f=4500")
    
    # Onset-Erkennung für Kicks und Snares
    kicks = set(detect_onsets(sub_bass, min_energy=0.40, min_delta=0.15))
    snares = set(detect_onsets(highs, min_energy=0.35, min_delta=0.15))
    
    # Takt-Raster Berechnung bei angegebenem BPM
    bar_starts_sec = []
    if args.bpm and args.bpm > 0:
        beat_dur = 60.0 / args.bpm
        bar_dur = beat_dur * 4.0
        # Erster Downbeat
        anchor_sec = args.first_beat_sec
        if anchor_sec is None:
            anchor_sec = sorted(list(kicks))[0] / args.fps if kicks else 0.0
            
        t = anchor_sec
        while t < duration:
            bar_starts_sec.append(round(t, 3))
            t += bar_dur

    bar_starts_frames = [int(round(t * args.fps)) for t in bar_starts_sec]
    bar_set = set(bar_starts_frames)

    frames_data = []
    for f in range(total_frames):
        sb = sub_bass[f] if f < len(sub_bass) else 0.0
        voc = vocals[f] if f < len(vocals) else 0.0
        hi = highs[f] if f < len(highs) else 0.0
        is_k = f in kicks
        is_s = f in snares
        is_b = f in bar_set
        
        frames_data.append({
            "frame": f,
            "time_sec": round(f / args.fps, 3),
            "sub_bass": sb,
            "vocals": voc,
            "highs": hi,
            "is_kick": is_k,
            "is_snare": is_s,
            "is_bar_start": is_b,
            "scale_pulse": round(1.0 + (sb * 0.12 if is_k else 0.0), 3)
        })
        
    out = {
        "meta": {
            "source_file": os.path.abspath(args.input),
            "duration_sec": round(duration, 3),
            "fps": args.fps,
            "total_frames": total_frames,
            "bpm": args.bpm,
            "first_beat_anchor_sec": round(anchor_sec, 3) if args.bpm else None
        },
        "stats": {
            "kick_count": len(kicks),
            "snare_count": len(snares),
            "bar_count": len(bar_starts_sec),
            "bar_starts_sec": bar_starts_sec,
            "kick_frames": sorted(list(kicks)),
            "snare_frames": sorted(list(snares)),
            "kick_times_sec": [round(f / args.fps, 3) for f in sorted(list(kicks))],
            "snare_times_sec": [round(f / args.fps, 3) for f in sorted(list(snares))]
        },
        "frames": frames_data
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        
    print(f"✓ Loop 1 Härtung erfolgreich:")
    print(f"  Gefundene Kicks: {len(kicks)}, Snares: {len(snares)}")
    print(f"  Gespeichert in: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
