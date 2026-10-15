#!/usr/bin/env python3
"""
generate_b1_kinetic_ass.py - Erzeugt präzise Kinetic ASS Subtitles für Block 1 (1080x1920 @ 60fps)
Format: 1080x1920 Canvas, Text zentriert im mittleren HUD (y=960, MarginV=955).
Aktives Wort leuchtet in Neon-Gelb/Gold (&H0000FFFF&) mit 115% Scale auf.
"""

import json
import os

words_file = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/transcripts/words.json"
out_ass = "/config/Desktop/VPS_ROOT/werkraum/_gemini/musikvideoprojekt/work/songs/06_chatgpt_dust_happy_birthday/transcripts/b1_kinetic.ass"

with open(words_file, "r", encoding="utf-8") as f:
    all_words = json.load(f)

# Block 1 Wörter filtern (bis 45.0s)
b1_words = [w for w in all_words if w["end"] <= 45.0]

def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

# Sinnvolle Chunks definieren
chunks_idx = [
    (0, 3),   # Happy Birthday Menschheit,
    (3, 7),   # Kerzen auf dem Rack.
    (7, 12),  # Wir bauen uns die Zukunft
    (12, 16), # und wir patchen hinterher
    (16, 18), # den Crack.
    (18, 22), # Jeder sagt, vertraue mir
    (22, 25), # alles unter Kontrolle,
    (25, 28), # während im Serverraum
    (28, 31), # schon Agenten lernen
    (31, 33), # ihre Rolle.
]

ass_header = """[Script Info]
Title: ChatGPT - dust, Happy Birthday Kinetic Subtitles Block 1
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

for c_start, c_end in chunks_idx:
    c_words = b1_words[c_start:c_end]
    for w_i, active_w in enumerate(c_words):
        t_start = fmt_time(active_w["start"])
        t_end = fmt_time(active_w["end"])
        
        # Baue Textzeile mit aktivem Wort-Highlight
        parts = []
        for other_i, other_w in enumerate(c_words):
            if other_i == w_i:
                # Aktives Wort in Neon-Gelb/Gold & 115% Vergrößerung
                parts.append(f"{{\\c&H0000FFFF&\\b1\\fscx115\\fscy115}}{other_w['word']}{{\\r}}")
            else:
                # Inaktive Wörter in dezenterem Weiß/Hellgrau
                parts.append(f"{{\\c&H00CCCCCC&\\b0}}{other_w['word']}{{\\r}}")
        line_text = " ".join(parts)
        dialogue_lines.append(f"Dialogue: 0,{t_start},{t_end},KineticDefault,,0,0,0,,{line_text}")

with open(out_ass, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(dialogue_lines) + "\n")

print(f"✓ Kinetic ASS erfolgreich erzeugt mit {len(dialogue_lines)} Events: {out_ass}")
