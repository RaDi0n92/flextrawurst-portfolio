#!/usr/bin/env python3
"""
generate_b1_kinetic_ass.py - Kinetische ASS-Untertitel fuer:
ChatGPT - welche naechste moeglichkeit (Block 1)
Dauer: 55.80s
"""

import json
import os

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
WORDS_FILE = os.path.join(SONG_DIR, "transcripts", "b1_words.json")
ASS_FILE = os.path.join(SONG_DIR, "transcripts", "b1_kinetic.ass")

def fmt_time(t):
    hrs = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = int(t % 60)
    cs = int(round((t - int(t)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

def main():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = json.load(f)

    # 1. Chunking der 117 Woerter (ca. 3-4 Woerter pro Phrase)
    chunks = []
    curr = []
    for w in words:
        curr.append(w)
        if len(curr) >= 4 or w["word"].endswith((".", ",", "!", "?", ":", ";")):
            if len(curr) >= 3 or w["word"].endswith((".", "!", "?")):
                chunks.append(curr)
                curr = []
    if curr:
        chunks.append(curr)

    lines = [
        "[Script Info]",
        "Title: ChatGPT Welche Naechste Moeglichkeit Kinetic Subtitles Block 1",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: KineticDefault,Liberation Sans,44,&H00FFFFFF&,&H0000FFFF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,905,1",
        "Style: AmbientMotto,Liberation Sans,38,&H0000FFCC&,&H0000FFFF&,&H00000000&,&H90000000&,1,0,0,0,100,100,2,0,1,3.5,1.5,2,40,40,905,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    for chunk in chunks:
        c_start = chunk[0]["start"]
        c_end = chunk[-1]["end"]
        c_end_padded = max(c_end, c_start + 0.6)

        for i, active_w in enumerate(chunk):
            w_start = active_w["start"]
            if i + 1 < len(chunk):
                w_end = chunk[i+1]["start"]
            else:
                w_end = c_end_padded

            if w_end <= w_start:
                w_end = w_start + 0.2

            parts = []
            for j, w in enumerate(chunk):
                text = w["word"]
                if j == i:
                    parts.append(f"{{\\c&H002BF7FF&\\b1\\fscx118\\fscy118}}{text}{{\\r}}")
                else:
                    parts.append(f"{{\\c&H00D0D0D0&\\b0}}{text}{{\\r}}")

            full_line = " ".join(parts)
            lines.append(f"Dialogue: 0,{fmt_time(w_start)},{fmt_time(w_end)},KineticDefault,,0,0,0,,{full_line}")

    with open(ASS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✓ Kinetische Untertitel geschrieben: {ASS_FILE}")

if __name__ == "__main__":
    main()
