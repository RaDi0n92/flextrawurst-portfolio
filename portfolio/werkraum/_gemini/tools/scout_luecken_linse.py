import json
import sqlite3
import re
from collections import Counter, defaultdict
from pathlib import Path

history_path = Path("/root/werkraum/_gpt/session_history.jsonl")
path_db = Path("/root/werkraum/_gpt/gesamtatlas/PFADINDEX.sqlite")

conn = sqlite3.connect(path_db)
known_paths = set(row[0] for row in conn.execute("SELECT path FROM paths"))
conn.close()

PATH_REGEX = re.compile(r"/(?:[a-zA-Z0-9_\.\-]+/)+[a-zA-Z0-9_\.\-]+")

path_mentions = Counter()
path_sessions = defaultdict(set)
path_events = defaultdict(set)

with history_path.open("r", encoding="utf-8") as f:
    for line in f:
        try:
            ev = json.loads(line)
        except Exception:
            continue
        session_id = str(ev.get("session_id") or "")
        event_id = str(ev.get("event_id") or "")
        blob = str(ev.get("target") or "") + "\n" + json.dumps(ev.get("details") or {}, ensure_ascii=False)
        for p in PATH_REGEX.findall(blob):
            p_clean = p.rstrip(".,:;)]}\"'\"")
            path_mentions[p_clean] += 1
            if session_id:
                path_sessions[p_clean].add(session_id)
            if event_id:
                path_events[p_clean].add(event_id)

missing_paths = [p for p in path_mentions if p not in known_paths]

categories = {
    "laufzeit_tmp": [],
    "temporaer_test": [],
    "pfadfragment_fehler": [],
    "geloeschter_projektpfad": [],
    "system_oder_externe_ref": []
}

for p in missing_paths:
    low = p.lower()
    if p.startswith("/tmp") or p.startswith("/proc") or p.startswith("/dev") or "/.system_generated/" in p:
        categories["laufzeit_tmp"].append(p)
    elif "test" in low or "scratch" in low or "tmp" in low or "draft" in low or "temp" in low or "dummy" in low or "selftest" in low:
        categories["temporaer_test"].append(p)
    elif p.endswith("...") or len(Path(p).suffix) > 8 or "backup-" in p:
        categories["pfadfragment_fehler"].append(p)
    elif p.startswith("/root/werkraum") or p.startswith("/root/flextrawurst") or p.startswith("/root/zensi") or p.startswith("/root/werkraum_"):
        categories["geloeschter_projektpfad"].append(p)
    else:
        categories["system_oder_externe_ref"].append(p)

print(f"Gesamt-Erwaehnungen von unvollstaendigen/fehlenden Pfaden: {len(missing_paths)}")
print("=" * 70)
for cat, items in categories.items():
    total_mentions = sum(path_mentions[p] for p in items)
    multi_session = sum(1 for p in items if len(path_sessions[p]) > 1)
    multi_event = sum(1 for p in items if len(path_events[p]) >= 3)
    print(f"Kategorie: {cat:25s} | Anzahl: {len(items):4d} | Mentions: {total_mentions:5d} | >1 Sessions: {multi_session:3d} | >=3 Events: {multi_event:3d}")

print("=" * 70)
vis_worthy = [p for p in categories["geloeschter_projektpfad"] + categories["temporaer_test"] if len(path_events[p]) >= 3 or len(path_sessions[p]) > 1]
print(f"VISUALISIERUNGSWÜRDIGE LÜCKEN-KNOTEN (In Projektpfaden mit >=3 Events oder >1 Session): {len(vis_worthy)}")
for p in vis_worthy[:8]:
    print(f"  * {p} | Mentions: {path_mentions[p]} | Events: {len(path_events[p])} | Sessions: {len(path_sessions[p])}")
