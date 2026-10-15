#!/usr/bin/env python3
"""
batch_queue_manager.py - Multi-Song Batch-Queue & Namespace-Isolations-Manager
Verhindert Asset-Kollisionen bei der Produktion mehrerer Lieder hintereinander.
Erstellt pro Song eine strikt isolierte Ordnerstruktur und führt eine Queue-State JSON.
"""

import argparse
import json
import os
import re
import sys

BASE_WORK_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work"

def parse_args():
    parser = argparse.ArgumentParser(description="Verwalte Multi-Song Batch-Queues und Verzeichnis-Isolation.")
    parser.add_argument("--songs", "-s", nargs="+", help="Liste von Song-Audiodateien (.mp3, .m4a, .wav).")
    parser.add_argument("--dir", "-d", help="Ordner mit mehreren Songs.")
    parser.add_argument("--status", action="store_true", help="Zeige aktuellen Status der Batch-Queue.")
    parser.add_argument("--queue-file", default=os.path.join(BASE_WORK_DIR, "batch_queue_state.json"), help="Pfad zum Queue-State.")
    return parser.parse_args()

def slugify(text):
    s = re.sub(r'[^\w\s-]', '', text).strip().lower()
    s = re.sub(r'[-\s]+', '_', s)
    return s[:40]

def detect_protagonist(song_path):
    lower = os.path.basename(song_path).lower()
    if "claude" in lower:
        return "claude", "/root/werkraum/_gemini/musikvideoprojekt/animirungen/claude"
    elif "chatgpt" in lower or "openai" in lower or "schleudergang" in lower:
        return "chatgpt", "/root/werkraum/_gemini/musikvideoprojekt/animirungen/chatgpt"
    elif "grok" in lower or "xai" in lower:
        return "grok", "/root/werkraum/_gemini/musikvideoprojekt/animirungen/grok"
    elif "google" in lower or "thron" in lower:
        return "google_ki_suche", "/root/werkraum/_gemini/musikvideoprojekt/ALLE_GENERIERTEN_BILDER/google_ki_suche"
    else:
        return "codewesen", "/root/werkraum/_gemini/musikvideoprojekt/animirungen/codewesen"

def init_queue(song_paths, queue_file):
    queue = {"queue_created": "", "songs": []}
    
    for idx, p in enumerate(song_paths):
        if not os.path.exists(p):
            print(f"Warnung: Song '{p}' existiert nicht, wird übersprungen.", file=sys.stderr)
            continue
            
        base = os.path.splitext(os.path.basename(p))[0]
        slug = f"{idx+1:02d}_{slugify(base)}"
        protagonist, anim_dir = detect_protagonist(p)
        
        song_dir = os.path.join(BASE_WORK_DIR, "songs", slug)
        subdirs = ["audio", "transcripts", "frames", "blocks", "master", "audit_frames"]
        for sd in subdirs:
            os.makedirs(os.path.join(song_dir, sd), exist_ok=True)
            
        manifest = {
            "index": idx + 1,
            "slug": slug,
            "title": base,
            "source_audio": os.path.abspath(p),
            "protagonist": protagonist,
            "anim_dir": anim_dir,
            "song_dir": song_dir,
            "status": "PENDING",
            "blocks_total": 0,
            "blocks_completed": 0,
            "master_video": os.path.join(song_dir, "master", f"{slug}_FULL_MASTER_1080p60.mp4"),
            "audit_passed": False
        }
        
        # Manifest in isolierten Song-Ordner schreiben
        with open(os.path.join(song_dir, "song_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        queue["songs"].append(manifest)
        
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)
        
    print(f"\n✓ Batch-Queue initialisiert mit {len(queue['songs'])} Liedern.")
    print(f"  Queue-State: {queue_file}")
    for s in queue["songs"]:
        print(f"  [{s['index']}] {s['slug']} -> Protagonist: {s['protagonist']} ({s['song_dir']})")

def show_status(queue_file):
    if not os.path.exists(queue_file):
        print("Keine aktive Batch-Queue gefunden.")
        return
    with open(queue_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("\n================ MULTI-SONG BATCH-QUEUE STATUS ================")
    for s in data.get("songs", []):
        sym = "✓" if s["status"] == "COMPLETED" else ("▶" if s["status"] == "IN_PROGRESS" else "⏳")
        print(f"[{sym}] Song {s['index']}: {s['slug']:<30} | Status: {s['status']:<12} | Audit: {s['audit_passed']}")
    print("================================================================")

def main():
    args = parse_args()
    if args.status:
        show_status(args.queue_file)
        return
        
    song_list = []
    if args.songs:
        song_list = args.songs
    elif args.dir and os.path.exists(args.dir):
        for ext in [".mp3", ".m4a", ".wav"]:
            song_list.extend([os.path.join(args.dir, f) for f in os.listdir(args.dir) if f.endswith(ext)])
            
    if not song_list:
        print("Fehler: Bitte gib Songs per --songs oder --dir an.", file=sys.stderr)
        sys.exit(1)
        
    init_queue(song_list, args.queue_file)

if __name__ == "__main__":
    main()
