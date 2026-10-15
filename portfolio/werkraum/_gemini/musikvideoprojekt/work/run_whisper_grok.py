import json
from faster_whisper import WhisperModel

audio_file = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/01_grok_flextrawurst_usesunocom_1/audio/grok_audio_14lufs.m4a"
out_json = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/01_grok_flextrawurst_usesunocom_1/transcripts/grok_flextrawurst_words.json"

print("Lade faster-whisper Model (small / cpu / int8)...")
model = WhisperModel("small", device="cpu", compute_type="int8")

print("Transkribiere mit word_timestamps=True...")
segments, info = model.transcribe(audio_file, language="de", word_timestamps=True)

words_list = []
for segment in segments:
    for word in segment.words:
        words_list.append({
            "word": word.word.strip(),
            "start": round(word.start, 3),
            "end": round(word.end, 3),
            "start_ms": int(word.start * 1000),
            "end_ms": int(word.end * 1000),
            "probability": round(word.probability, 3)
        })

print(f"Fertig! {len(words_list)} Wörter extrahiert.")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(words_list, f, indent=2, ensure_ascii=False)

print(f"Gespeichert in: {out_json}")
