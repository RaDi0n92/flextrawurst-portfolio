#!/usr/bin/env python3
"""
generate_all_kinetic_ass.py - Generiert kinetische ASS-Dateien fuer
Bloecke 2, 3, 4, 5 von: ChatGPT - welche naechste moeglichkeit
"""

import json
import os

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
WORDS_FILE = os.path.join(SONG_DIR, "transcripts", "full_words.json")

BLOCKS = [
    {
        "id": "b2",
        "start": 55.80,
        "end": 112.00,
        "ass": os.path.join(SONG_DIR, "transcripts", "b2_kinetic.ass"),
        "words_out": os.path.join(SONG_DIR, "transcripts", "b2_words.json")
    },
    {
        "id": "b3",
        "start": 112.00,
        "end": 169.00,
        "ass": os.path.join(SONG_DIR, "transcripts", "b3_kinetic.ass"),
        "words_out": os.path.join(SONG_DIR, "transcripts", "b3_words.json")
    },
    {
        "id": "b4",
        "start": 169.00,
        "end": 215.60,
        "ass": os.path.join(SONG_DIR, "transcripts", "b4_kinetic.ass"),
        "words_out": os.path.join(SONG_DIR, "transcripts", "b4_words.json")
    },
    {
        "id": "b5",
        "start": 215.60,
        "end": 284.76,
        "ass": os.path.join(SONG_DIR, "transcripts", "b5_kinetic.ass"),
        "words_out": os.path.join(SONG_DIR, "transcripts", "b5_words.json")
    }
]

def fmt_time(t):
    hrs = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = int(t % 60)
    cs = int(round((t - int(t)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

def generate_ass_for_block(b_info, full_words):
    b_start = b_info["start"]
    b_end = b_info["end"]

    # Filter words and shift time
    b_words = []
    for w in full_words:
        if w["start"] >= b_start and w["start"] < b_end:
            # Ignore automated post-song whisper hallucinations (e.g. "Untertitel im Auftrag des ZDF")
            if "untertitel" in w["word"].lower() or "zdf" in w["word"].lower():
                continue
            b_words.append({
                "word": w["word"],
                "start": round(max(0.0, w["start"] - b_start), 2),
                "end": round(max(0.1, w["end"] - b_start), 2)
            })

    with open(b_info["words_out"], "w", encoding="utf-8") as f:
        json.dump(b_words, f, indent=2, ensure_ascii=False)

    # Chunking: 3-4 Woerter pro Phrase
    chunks = []
    curr = []
    for w in b_words:
        curr.append(w)
        if len(curr) >= 4 or w["word"].endswith((".", ",", "!", "?", ":", ";")):
            if len(curr) >= 3 or w["word"].endswith((".", "!", "?")):
                chunks.append(curr)
                curr = []
    if curr:
        chunks.append(curr)

    lines = [
        "[Script Info]",
        f"Title: ChatGPT Welche Naechste Moeglichkeit Kinetic Subtitles {b_info['id'].upper()}",
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

    with open(b_info["ass"], "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✓ {b_info['id'].upper()}: {len(b_words)} Woerter in {len(chunks)} Chunks -> {b_info['ass']}")

def main():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        full_words = json.load(f)

    for b in BLOCKS:
        generate_ass_for_block(b, full_words)

if __name__ == "__main__":
    main()
