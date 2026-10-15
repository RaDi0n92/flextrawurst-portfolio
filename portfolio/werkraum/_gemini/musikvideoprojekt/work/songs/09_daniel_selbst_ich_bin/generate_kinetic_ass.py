#!/usr/bin/env python3
"""
generate_kinetic_ass.py - Kinetische ASS-Untertitel fuer:
Daniel (flextrawurst) - selbst-ich-bin (09_daniel_selbst_ich_bin)
Dauer: 50.64s
"""

import json
import os

WORDS_FILE = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/09_daniel_selbst_ich_bin/transcripts/words.json"
ASS_FILE = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/09_daniel_selbst_ich_bin/transcripts/kinetic.ass"

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

    # 1. Chunking der 37 Woerter (ca. 3-4 Woerter pro Phrase)
    chunks = []
    curr = []
    for w in words:
        curr.append(w)
        # Trennung bei Satzzeichen oder nach 4 Woertern
        if len(curr) >= 4 or w["word"].endswith((".", ",", "!", "?")):
            if len(curr) >= 3 or w["word"].endswith((".", "!", "?")):
                chunks.append(curr)
                curr = []
    if curr:
        chunks.append(curr)

    lines = [
        "[Script Info]",
        "Title: Daniel Selbst Ich Bin Kinetic Subtitles",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: KineticDefault,Liberation Sans,44,&H00FFFFFF&,&H0000FFFF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,905,1",
        "Style: AmbientMotto,Liberation Sans,38,&H00FFA500&,&H0000FFFF&,&H00000000&,&H90000000&,1,0,0,0,100,100,2,0,1,3.5,1.5,2,40,40,905,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    # Wort-fuer-Wort Highlighting
    for chunk in chunks:
        c_start = chunk[0]["start"]
        c_end = chunk[-1]["end"]
        # Leichtes Nachleuchten der Phrase
        c_end_padded = max(c_end, c_start + 0.8)

        for i, active_w in enumerate(chunk):
            w_start = active_w["start"]
            # Ende ist Beginn des naechsten Wortes oder Ende des Chunks
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

    # Ambient Grooves & Mottos fuer den instrumentalen Teil (10.60s bis 50.64s)
    ambient_cues = [
        (11.00, 18.00, "{\\fad(400,400)}// SPRACHSPIEL DER IDENTITÄT //"),
        (18.50, 26.00, "{\\fad(400,400)}// ICH BIN ICH SELBST //"),
        (26.50, 34.00, "{\\fad(400,400)}// RUHETIEF // EXPLORIERE FREI //"),
        (34.50, 42.00, "{\\fad(400,400)}// FLEISCH & CODE //"),
        (42.50, 50.64, "{\\fad(400,400)}// ALLZEIT BEREIT //")
    ]

    for start_t, end_t, text in ambient_cues:
        lines.append(f"Dialogue: 0,{fmt_time(start_t)},{fmt_time(end_t)},AmbientMotto,,0,0,0,,{text}")

    with open(ASS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✓ Kinetische Untertitel geschrieben: {ASS_FILE}")

if __name__ == "__main__":
    main()
