#!/usr/bin/env python3
"""
dynamic_phrase_chunker.py - Intelligenter Schnittstellen-Planer für modulare Song-Blöcke
Unterstützt alle gängigen Whisper JSON Formate (ms, s, flat list, segments dict).
Verhindert das Zerschneiden von Wörtern und Gesangsphrasen, indem Schnitte mathematisch
an echten Gesangspausen (Gaps >= 0.5s) im Korridor von min_dur bis max_dur platziert werden.
"""

import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Berechne organische Phrasen-Schnittstellen aus Whisper Word-Level Timestamps.")
    parser.add_argument("--whisper-json", "-w", required=True, help="Pfad zur Whisper JSON mit Segmenten/Wörtern.")
    parser.add_argument("--min-block-dur", type=float, default=38.0, help="Minimale Blockdauer in Sekunden (Standard: 38.0s).")
    parser.add_argument("--max-block-dur", type=float, default=54.0, help="Maximale Blockdauer in Sekunden (Standard: 54.0s).")
    parser.add_argument("--target-dur", type=float, default=44.0, help="Ziel-Blockdauer (Standard: 44.0s).")
    parser.add_argument("--output-json", "-o", default=None, help="Optionaler Ausgabepfad für die generierten Block-Definitionen.")
    return parser.parse_args()

def normalize_words(data):
    raw_list = []
    if isinstance(data, list):
        raw_list = data
    elif isinstance(data, dict):
        if "words" in data:
            raw_list = data["words"]
        elif "segments" in data:
            for seg in data["segments"]:
                if "words" in seg:
                    raw_list.extend(seg["words"])
                else:
                    raw_list.append({
                        "word": seg.get("text", "").strip(),
                        "start": seg.get("start", 0.0),
                        "end": seg.get("end", 0.0)
                    })

    normalized = []
    for item in raw_list:
        word = item.get("word") or item.get("text") or ""
        word = word.strip()
        if not word:
            continue
            
        # Sekunden oder Millisekunden?
        if "start_ms" in item and "end_ms" in item:
            start_sec = float(item["start_ms"]) / 1000.0
            end_sec = float(item["end_ms"]) / 1000.0
        else:
            start_sec = float(item.get("start", 0.0))
            end_sec = float(item.get("end", 0.0))
            
        normalized.append({
            "word": word,
            "start": start_sec,
            "end": end_sec
        })
        
    return sorted(normalized, key=lambda x: x["start"])

def main():
    args = parse_args()
    if not os.path.exists(args.whisper_json):
        print(f"Fehler: Datei '{args.whisper_json}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
        
    with open(args.whisper_json, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    words = normalize_words(raw_data)
    if not words:
        print("Fehler: Keine Wörter in Whisper-Datei gefunden.", file=sys.stderr)
        sys.exit(1)
        
    total_dur = max(w["end"] for w in words)
    print(f"Gesamte erkannte Vokal-Dauer: {total_dur:.2f}s ({len(words)} Wörter)")
    
    blocks = []
    curr_start = 0.0
    word_idx = 0
    num_words = len(words)
    
    block_num = 1
    while curr_start < total_dur:
        target_time = curr_start + args.target_dur
        min_time = curr_start + args.min_block_dur
        max_time = curr_start + args.max_block_dur
        
        # Wenn wir kurz vor dem Ende sind, nehmen wir alles bis zum Schluss
        if total_dur - curr_start <= max_time - curr_start:
            end_time = total_dur
            block_words = [w for w in words if w["start"] >= curr_start and w["end"] <= end_time]
            blocks.append({
                "block_num": block_num,
                "start": round(curr_start, 2),
                "end": round(end_time, 2),
                "duration": round(end_time - curr_start, 2),
                "words_count": len(block_words),
                "first_word": block_words[0]["word"] if block_words else "",
                "last_word": block_words[-1]["word"] if block_words else ""
            })
            break
            
        # Suche nach der besten Lücke (Gap) im Fenster
        best_cut = None
        best_score = -1e9
        next_word_idx = word_idx
        
        for i in range(word_idx, num_words - 1):
            w_cur = words[i]
            w_next = words[i+1]
            
            w_end = w_cur["end"]
            w_next_start = w_next["start"]
            gap = w_next_start - w_end
            
            if w_end < min_time:
                continue
            if w_end > max_time:
                break
                
            dist_penalty = abs(w_end - target_time) * 0.25
            score = (gap * 3.0) - dist_penalty
            
            if score > best_score:
                best_score = score
                best_cut = w_end + (gap / 2.0)
                next_word_idx = i + 1
                
        if best_cut is None:
            candidates = [w for w in words if min_time <= w["end"] <= max_time]
            if candidates:
                best_w = min(candidates, key=lambda w: abs(w["end"] - target_time))
                best_cut = best_w["end"]
                next_word_idx = words.index(best_w) + 1
            else:
                best_cut = target_time
                next_word_idx = word_idx + 10
                
        block_words = [w for w in words if w["start"] >= curr_start and w["end"] <= best_cut]
        blocks.append({
            "block_num": block_num,
            "start": round(curr_start, 2),
            "end": round(best_cut, 2),
            "duration": round(best_cut - curr_start, 2),
            "words_count": len(block_words),
            "first_word": block_words[0]["word"] if block_words else "",
            "last_word": block_words[-1]["word"] if block_words else ""
        })
        
        curr_start = best_cut
        word_idx = next_word_idx
        block_num += 1
        
    print("\n================ PHRASEN-SCHNITTSTELLEN REPORT ================")
    for b in blocks:
        print(f"Block {b['block_num']}: {b['start']:>6.2f}s - {b['end']:>6.2f}s ({b['duration']:>5.2f}s) | "
              f"{b['words_count']:>3} Wörter | Von: »{b['first_word']}« Bis: »{b['last_word']}«")
    print("================================================================")
    
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)
        print(f"Gespeichert in: {args.output_json}")

if __name__ == "__main__":
    main()
