import json
import subprocess
import os

song_dir = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/01_grok_flextrawurst_usesunocom_1"
audio_master = os.path.join(song_dir, "audio", "grok_audio_14lufs.m4a")
plan_file = os.path.join(song_dir, "transcripts", "grok_block_plan.json")
words_file = os.path.join(song_dir, "transcripts", "grok_flextrawurst_words.json")

with open(plan_file, "r") as f:
    plan = json.load(f)

with open(words_file, "r") as f:
    all_words = json.load(f)

for b in plan:
    b_num = b["block_num"]
    start = b["start"]
    dur = b["duration"]
    end = b["end"]
    
    # 1. Slice Audio (AAC 320k 96kHz)
    out_audio = os.path.join(song_dir, "audio", f"grok_b{b_num}_audio.m4a")
    cmd = [
        "ffmpeg", "-y", "-v", "warning",
        "-ss", str(start),
        "-t", str(dur),
        "-i", audio_master,
        "-c:a", "aac", "-b:a", "320k", "-ar", "96000",
        out_audio
    ]
    subprocess.run(cmd, check=True)
    print(f"✓ Audio Block {b_num} geschnitten: {out_audio} ({dur}s)")
    
    # 2. Slice Words & re-base timestamps relative to block start
    block_words = []
    for w in all_words:
        if w["start"] >= start - 0.2 and w["end"] <= end + 0.3:
            rel_start = max(0.0, round(w["start"] - start, 3))
            rel_end = max(0.1, round(w["end"] - start, 3))
            block_words.append({
                "word": w["word"],
                "start": rel_start,
                "end": rel_end,
                "start_ms": int(rel_start * 1000),
                "end_ms": int(rel_end * 1000)
            })
            
    out_words = os.path.join(song_dir, "transcripts", f"grok_b{b_num}_words.json")
    with open(out_words, "w", encoding="utf-8") as f:
        json.dump(block_words, f, indent=2, ensure_ascii=False)
    print(f"✓ Words Block {b_num} ({len(block_words)} Wörter): {out_words}")

