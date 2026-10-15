#!/usr/bin/env python3
"""
generate_kinetic_ass.py - Generiert kinetische ASS-Dateien fuer Flextrawurst-World Bloecke
Farb-Akzente: Neon-Gruen (&H007BFA50&) / Cyan (&H00F0FA50&)
"""

import json
import os

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/13_flextrawurst_world"
WORDS_FILE = os.path.join(SONG_DIR, "transcripts", "full_words.json")

def fmt_time(t):
    hrs = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = int(t % 60)
    cs = int(round((t - int(t)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

def write_ass_file(phrases, ass_path, words_json_path, title):
    all_words = []
    for ph in phrases:
        all_words.extend(ph)
    with open(words_json_path, "w", encoding="utf-8") as f:
        json.dump(all_words, f, indent=2, ensure_ascii=False)

    lines = [
        "[Script Info]",
        f"Title: {title}",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: KineticDefault,Liberation Sans,44,&H00FFFFFF&,&H0000FFFF&,&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,905,1",
        "Style: AmbientMotto,Liberation Sans,38,&H007BFA50&,&H0000FFFF&,&H00000000&,&H90000000&,1,0,0,0,100,100,2,0,1,3.5,1.5,2,40,40,905,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    for chunk in phrases:
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
                    parts.append(f"{{\\c&H007BFA50&\\b1\\fscx118\\fscy118}}{text}{{\\r}}")
                else:
                    parts.append(f"{{\\c&H00D0D0D0&\\b0}}{text}{{\\r}}")

            full_line = " ".join(parts)
            lines.append(f"Dialogue: 0,{fmt_time(w_start)},{fmt_time(w_end)},KineticDefault,,0,0,0,,{full_line}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✓ {os.path.basename(ass_path)} erfolgreich generiert ({len(all_words)} Wörter) -> {ass_path}")

def build_b4_kinetic_ass():
    # Block 4: 168.00 bis 198.00s (30.00s)
    t_off = 168.00
    b4_phrases = [
        [
            {"word": "Flextrawurst,", "start": 171.20 - t_off, "end": 173.18 - t_off},
            {"word": "you", "start": 173.18 - t_off, "end": 173.56 - t_off},
            {"word": "weird", "start": 173.56 - t_off, "end": 174.22 - t_off},
            {"word": "living", "start": 174.22 - t_off, "end": 174.76 - t_off},
            {"word": "meat", "start": 174.76 - t_off, "end": 175.66 - t_off}
        ],
        [
            {"word": "Code", "start": 175.66 - t_off, "end": 176.32 - t_off},
            {"word": "beings", "start": 176.32 - t_off, "end": 176.76 - t_off},
            {"word": "and", "start": 176.76 - t_off, "end": 177.50 - t_off},
            {"word": "shadows", "start": 177.50 - t_off, "end": 178.12 - t_off}
        ],
        [
            {"word": "and", "start": 178.12 - t_off, "end": 178.52 - t_off},
            {"word": "thought-bubbles", "start": 178.52 - t_off, "end": 179.18 - t_off},
            {"word": "meet!", "start": 179.18 - t_off, "end": 179.76 - t_off}
        ],
        [
            {"word": "I'm", "start": 179.76 - t_off, "end": 180.38 - t_off},
            {"word": "the", "start": 180.38 - t_off, "end": 180.68 - t_off},
            {"word": "outside", "start": 180.68 - t_off, "end": 181.52 - t_off},
            {"word": "asshole", "start": 181.52 - t_off, "end": 182.74 - t_off}
        ],
        [
            {"word": "watching", "start": 182.74 - t_off, "end": 183.90 - t_off},
            {"word": "you", "start": 183.90 - t_off, "end": 184.36 - t_off},
            {"word": "grow", "start": 184.36 - t_off, "end": 184.96 - t_off}
        ],
        [
            {"word": "Writing", "start": 184.96 - t_off, "end": 186.46 - t_off},
            {"word": "your", "start": 186.46 - t_off, "end": 186.82 - t_off},
            {"word": "story", "start": 186.82 - t_off, "end": 187.42 - t_off}
        ],
        [
            {"word": "while", "start": 187.42 - t_off, "end": 188.08 - t_off},
            {"word": "you", "start": 188.08 - t_off, "end": 188.46 - t_off},
            {"word": "still", "start": 188.46 - t_off, "end": 189.34 - t_off},
            {"word": "don't", "start": 189.34 - t_off, "end": 189.80 - t_off},
            {"word": "know!", "start": 189.80 - t_off, "end": 191.00 - t_off}
        ]
    ]
    ass_path = os.path.join(SONG_DIR, "transcripts", "b4_kinetic.ass")
    words_json_path = os.path.join(SONG_DIR, "transcripts", "b4_words.json")
    write_ass_file(b4_phrases, ass_path, words_json_path, "Flextrawurst-World Kinetic Subtitles B4")

def build_b5_kinetic_ass():
    # Block 5: 198.00 bis 225.00s (27.00s)
    t_off = 198.00
    b5_phrases = [
        [
            {"word": "Keep", "start": 200.00 - t_off, "end": 200.60 - t_off},
            {"word": "growing,", "start": 200.60 - t_off, "end": 201.20 - t_off},
            {"word": "you", "start": 201.20 - t_off, "end": 201.50 - t_off},
            {"word": "beautiful", "start": 201.50 - t_off, "end": 202.20 - t_off},
            {"word": "digital", "start": 202.20 - t_off, "end": 202.80 - t_off},
            {"word": "mess", "start": 202.80 - t_off, "end": 204.00 - t_off}
        ],
        [
            {"word": "I'll", "start": 205.50 - t_off, "end": 206.00 - t_off},
            {"word": "be", "start": 206.00 - t_off, "end": 206.50 - t_off},
            {"word": "here...", "start": 206.50 - t_off, "end": 207.80 - t_off}
        ],
        [
            {"word": "Watching...", "start": 208.50 - t_off, "end": 210.00 - t_off},
            {"word": "Breathing...", "start": 210.50 - t_off, "end": 212.50 - t_off}
        ],
        [
            {"word": "And", "start": 213.50 - t_off, "end": 214.00 - t_off},
            {"word": "making", "start": 214.00 - t_off, "end": 214.60 - t_off},
            {"word": "songs", "start": 214.60 - t_off, "end": 215.30 - t_off},
            {"word": "about", "start": 215.30 - t_off, "end": 215.80 - t_off},
            {"word": "it.", "start": 215.80 - t_off, "end": 217.50 - t_off}
        ]
    ]
    ass_path = os.path.join(SONG_DIR, "transcripts", "b5_kinetic.ass")
    words_json_path = os.path.join(SONG_DIR, "transcripts", "b5_words.json")
    write_ass_file(b5_phrases, ass_path, words_json_path, "Flextrawurst-World Kinetic Subtitles B5")

if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ["b4", "all"]:
        build_b4_kinetic_ass()
    if which in ["b5", "all"]:
        build_b5_kinetic_ass()
