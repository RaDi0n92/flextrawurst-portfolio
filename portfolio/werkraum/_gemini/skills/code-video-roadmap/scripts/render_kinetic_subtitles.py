#!/usr/bin/env python3
"""
render_kinetic_subtitles.py - Deterministischer Kinetic Typography Generator
Unterstützt 1080x1920 Full-HD Standard, dynamische Silben-Hervorhebung,
Safe-Zone Schutz (keine Kollision mit flextrawurst Badge bei Y=1010)
und automatische Skalierung bei überlangen deutschen Wörtern (>16 Zeichen).
"""

import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Erzeuge stylische Kinetic ASS-Untertitel aus Wort-Timings.")
    parser.add_argument("--words", "-w", required=True, help="Pfad zur JSON-Datei mit Wort-Timings.")
    parser.add_argument("--output", "-o", default="kinetic_subtitles.ass", help="Pfad zur Ausgabe-ASS-Datei.")
    parser.add_argument("--width", type=int, default=1080, help="Videobreite (Standard: 1080).")
    parser.add_argument("--height", type=int, default=1920, help="Videohöhe (Standard: 1920).")
    parser.add_argument("--font", default="Liberation Sans", help="Schriftart (Standard: Liberation Sans).")
    parser.add_argument("--fontsize", type=int, default=42, help="Schriftgröße (Standard: 42).")
    parser.add_argument("--accent-color", default="&H00FFCC&", help="ASS BGR-Farbe für aktives Wort (z.B. &H00FFCC& für Cyan, &H00A5FF& für Orange).")
    parser.add_argument("--inactive-color", default="&HCCCCCC&", help="ASS BGR-Farbe für inaktive Wörter.")
    parser.add_argument("--chunk-size", type=int, default=3, help="Maximalwörter pro Zeile/Event.")
    parser.add_argument("--margin-v", type=int, default=920, help="Vertikaler Abstand von unten (Standard: 920px für 1080x1920 Safe-Zone).")
    return parser.parse_args()

def to_ms(item, key_ms, key_sec):
    if key_ms in item:
        return int(item[key_ms])
    elif key_sec in item:
        return int(float(item[key_sec]) * 1000)
    return 0

def ms_to_ass_time(ms):
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    centiseconds = (ms % 1000) // 10
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

def clean_word(w):
    return w.replace("\\", "").replace("{", "").replace("}", "").strip()

def main():
    args = parse_args()
    if not os.path.exists(args.words):
        print(f"Fehler: Datei '{args.words}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
        
    with open(args.words, "r", encoding="utf-8") as f:
        raw = json.load(f)
        
    # Extrahiere Liste von Wörtern
    raw_words = []
    if isinstance(raw, list):
        raw_words = raw
    elif isinstance(raw, dict):
        raw_words = raw.get("words", [])
        if not raw_words and "segments" in raw:
            for s in raw["segments"]:
                raw_words.extend(s.get("words", []))
                
    normalized = []
    for w in raw_words:
        txt = clean_word(w.get("word") or w.get("text") or "")
        if not txt:
            continue
        s_ms = to_ms(w, "start_ms", "start")
        e_ms = to_ms(w, "end_ms", "end")
        if e_ms <= s_ms:
            e_ms = s_ms + 300
        normalized.append({"word": txt, "start_ms": s_ms, "end_ms": e_ms})
        
    if not normalized:
        print("Fehler: Keine gültigen Wörter gefunden.", file=sys.stderr)
        sys.exit(1)
        
    # Chunks gruppieren (2 bis 3 Wörter)
    chunks = []
    for i in range(0, len(normalized), args.chunk_size):
        chunks.append(normalized[i:i + args.chunk_size])
        
    ass_header = f"""[Script Info]
Title: Kinetic Subtitles 1080p
ScriptType: v4.00+
PlayResX: {args.width}
PlayResY: {args.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticDefault,{args.font},{args.fontsize},&H00FFFFFF&,{args.accent_color},&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,5.0,3.0,2,40,40,{args.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for c_idx, chunk in enumerate(chunks):
        chunk_start = chunk[0]["start_ms"]
        # Nächster Chunk Start (falls vorhanden) um Überlappung strikt zu verhindern!
        next_chunk_start = chunks[c_idx+1][0]["start_ms"] if c_idx + 1 < len(chunks) else chunk[-1]["end_ms"] + 250
        chunk_end = min(chunk[-1]["end_ms"] + 150, next_chunk_start)
        if chunk_end <= chunk_start:
            chunk_end = chunk_start + 200
        
        for idx, active in enumerate(chunk):
            w_start = active["start_ms"]
            # Ende ist Start des nächsten Wortes oder Chunk-Ende
            if idx + 1 < len(chunk):
                w_end = min(chunk[idx+1]["start_ms"], chunk_end)
            else:
                w_end = chunk_end
            if w_end <= w_start:
                w_end = w_start + 150
                
            line_parts = []
            for j, item in enumerate(chunk):
                word_str = item["word"]
                # Schrumpfe überlange Wörter dynamisch
                scale_mod = "\\fscx85\\fscy85" if len(word_str) > 15 else ""
                
                if j == idx:
                    # Aktives Wort: Akzentfarbe + Pop-up Zoom
                    line_parts.append(f"{{\\c{args.accent_color}\\b1\\fscx115\\fscy115{scale_mod}}}{word_str}{{\\r}}")
                else:
                    # Inaktives Wort: Dezent gedimmt
                    line_parts.append(f"{{\\c{args.inactive_color}\\b0{scale_mod}}}{word_str}{{\\r}}")
                    
            text_line = " ".join(line_parts)
            events.append(f"Dialogue: 0,{ms_to_ass_time(w_start)},{ms_to_ass_time(w_end)},KineticDefault,,0,0,0,,{text_line}")
            
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
        
    print(f"✓ Kinetic ASS Untertitel generiert: {args.output} ({len(events)} Timing-Events)")

if __name__ == "__main__":
    main()
