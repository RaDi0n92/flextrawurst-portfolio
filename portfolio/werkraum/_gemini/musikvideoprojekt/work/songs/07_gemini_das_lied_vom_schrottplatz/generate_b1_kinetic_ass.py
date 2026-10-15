#!/usr/bin/env python3
import json
import os

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/07_gemini_das_lied_vom_schrottplatz"
words_file = os.path.join(song_dir, "transcripts", "b1_words.json")
out_ass = os.path.join(song_dir, "transcripts", "b1_kinetic.ass")

with open(words_file, "r", encoding="utf-8") as f:
    b1_words = json.load(f)

def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

# Gruppiere Wörter automatisch in Chunks (bei Pausen >= 0.35s oder max 4 Wörtern)
chunks = []
cur_chunk = []
for i, w in enumerate(b1_words):
    # Überspringe lange 'gam'-Wiederholungen im Beat-Intro
    if w["word"].lower().startswith("gam") or w["word"].lower() == "am":
        continue
    
    cur_chunk.append(w)
    
    # Pause zum nächsten Wort prüfen
    is_gap = False
    if i + 1 < len(b1_words):
        next_w = b1_words[i+1]
        if next_w["start"] - w["end"] >= 0.35:
            is_gap = True
    
    if len(cur_chunk) >= 4 or is_gap or i == len(b1_words) - 1:
        chunks.append(cur_chunk)
        cur_chunk = []

ass_header = """[Script Info]
Title: Das Lied vom Schrottplatz Kinetic Subtitles Block 1
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticDefault,Liberation Sans,42,&H00FFFFFF&,&H0000FFFF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,955,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

dialogue_lines = []
for c in chunks:
    if not c:
        continue
    for w_i, active_w in enumerate(c):
        t_start = fmt_time(active_w["start"])
        t_end = fmt_time(active_w["end"])
        
        parts = []
        for other_i, other_w in enumerate(c):
            w_text = other_w['word'].replace('\\', '').replace('{', '').replace('}', '')
            if other_i == w_i:
                # Aktives Wort in Neon-Cyan/Gold (&H00FFFF00&) mit 115% Scale
                parts.append(f"{{\\c&H00D4FF&\\b1\\fscx115\\fscy115}}{w_text}{{\\r}}")
            else:
                parts.append(f"{{\\c&H00CCCCCC&\\b0}}{w_text}{{\\r}}")
        line_text = " ".join(parts)
        dialogue_lines.append(f"Dialogue: 0,{t_start},{t_end},KineticDefault,,0,0,0,,{line_text}")

with open(out_ass, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(dialogue_lines) + "\n")

print(f"✓ Kinetic ASS erzeugt mit {len(dialogue_lines)} Events aus {len(chunks)} Chunks!")
