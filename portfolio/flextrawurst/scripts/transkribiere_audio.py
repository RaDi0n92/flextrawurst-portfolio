import sys
import json
from faster_whisper import WhisperModel

def main():
    pfad = sys.argv[1]
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(pfad)
    text = " ".join(s.text.strip() for s in segments)
    print(json.dumps({
        "text": text.strip(),
        "sprache": info.language,
        "sprache_wahrscheinlichkeit": round(info.language_probability, 2),
    }))

if __name__ == "__main__":
    main()
