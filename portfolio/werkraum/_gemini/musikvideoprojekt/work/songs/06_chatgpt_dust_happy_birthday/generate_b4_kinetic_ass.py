#!/usr/bin/env python3
"""
generate_b4_kinetic_ass.py - Erzeugt präzise Kinetic ASS Subtitles für Block 4 (1080x1920 @ 60fps)
Zeitbereich Block 4: 137.00s - 185.50s (Dauer: 48.50s)
Format: 1080x1920 Canvas, Text zentriert im mittleren HUD (y=960, MarginV=955).
Aktives Wort leuchtet in Neon-Gelb/Gold (&H0000FFFF&) mit 115% Scale auf.
"""

import json
import os

words_file = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/transcripts/words.json"
out_ass = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/transcripts/b4_kinetic.ass"

BLOCK_START = 137.00
BLOCK_END = 185.50

with open(words_file, "r", encoding="utf-8") as f:
    all_words = json.load(f)

# Block 4 Wörter filtern und relative Zeiten berechnen
b4_words = []
for w in all_words:
    if BLOCK_START <= w["start"] < BLOCK_END:
        rel_start = max(0.0, round(w["start"] - BLOCK_START, 3))
        rel_end = min(round(BLOCK_END - BLOCK_START, 3), round(w["end"] - BLOCK_START, 3))
        b4_words.append({
            "word": w["word"],
            "start": rel_start,
            "end": rel_end
        })

print(f"Block 4 Wörter gefunden: {len(b4_words)}")

def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

# Chunking-Logik
chunks = []
current_chunk = []

for i, w in enumerate(b4_words):
    current_chunk.append(w)
    text = w["word"]
    is_punct = any(p in text for p in [".", ",", ";", "!", "?"])
    pause_after = False
    if i < len(b4_words) - 1:
        pause_after = (b4_words[i+1]["start"] - w["end"]) > 0.45
        
    if len(current_chunk) >= 4 or (len(current_chunk) >= 2 and is_punct) or pause_after or (len(current_chunk) >= 5):
        chunks.append(current_chunk)
        current_chunk = []

if current_chunk:
    chunks.append(current_chunk)

print(f"In {len(chunks)} Chunks aufgeteilt.")

ass_header = """[Script Info]
Title: ChatGPT - dust, Happy Birthday Kinetic Subtitles Block 4
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticDefault,Liberation Sans,38,&H00FFFFFF&,&H0000FFFF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,955,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

dialogue_lines = []

for c_words in chunks:
    for w_i, active_w in enumerate(c_words):
        t_start = fmt_time(active_w["start"])
        t_end = fmt_time(active_w["end"])
        
        parts = []
        for other_i, other_w in enumerate(c_words):
            if other_i == w_i:
                parts.append(f"{{\\c&H0000FFFF&\\b1\\fscx115\\fscy115}}{other_w['word']}{{\\r}}")
            else:
                parts.append(f"{{\\c&H00CCCCCC&\\b0}}{other_w['word']}{{\\r}}")
        line_text = " ".join(parts)
        dialogue_lines.append(f"Dialogue: 0,{t_start},{t_end},KineticDefault,,0,0,0,,{line_text}")

with open(out_ass, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(dialogue_lines) + "\n")

print(f"✓ Kinetic ASS für Block 4 erfolgreich erzeugt mit {len(dialogue_lines)} Events: {out_ass}")
