#!/usr/bin/env python3
"""
tools_seed_relations.py — befuellt DAS KANONISCHE BEZIEHUNGSREGISTER.sqlite direkt
(kein Overlay, keine zweite Datenbank) mit zwei neuen Kantenarten, gemaess dem
Knotenvertrag (/root/werkraum/_shared/KNOTENVERTRAG.md):

  "Kein neues Schema. Keine zweite Datenbank. Keine neuen ID-Raeume."
  "Neue Arten nur, wenn keine bestehende passt."
  evidence_json verbindlich: {beleg, herkunft, staerke, unsicherheit}

WICHTIGE EINSCHRAENKUNG DES ATLAS (atlas_health, 2026-08-14): "Nur belegte Pfad-,
Deklarations-, History- und exakte Erwaehnungsbeziehungen werden als Kanten
gespeichert. Semantische Naehe allein erzeugt keine Kante." SIMILAR_TO ist reine
semantische Naehe -- deshalb IMMER unsicherheit=vermutet, nie sicher/abgeleitet,
und ausdruecklich nur gebaut, weil Daniel es explizit angefordert hat (Design- und
Auftragstreue-Regel: neue Bedeutungen nur auf ausdrueckliche Anforderung).

  SIMILAR_TO   — automatisch, gewichtete Kombination aus
                 (a) Begriffsueberlappung via BEGRIFFSINDEX.sqlite (FTS5, bm25)
                 (b) Typ-/Pfadnaehe (gleicher node_type + gemeinsamer Pfad-Praefix)
                 score = 0.6 * text_score_norm + 0.4 * pfad_typ_score
                 datenstand = 'MODELLIERT_AEHNLICHKEIT'

  OPPOSES — HALBAUTOMATISCH: nur Kandidaten, nie direkt scharf. Erkennung ueber
                 ein kuratiertes Gegensatzpaar-Vokabular (deutsch). Bestaetigung/
                 Verwerfung wird zusaetzlich in einem separaten, kleinen
                 Bestaetigungs-Log gefuehrt (BESTAETIGUNGSLOG.json), weil
                 Nutzerentscheidungen einen periodischen Rebuild des Registers
                 ueberleben muessen -- das Log ist die Quelle der Wahrheit fuer
                 den Bestaetigungsstatus, die Kante im Register wird danach neu
                 ausgerichtet.
                 datenstand = 'MODELLIERT_GEGENSATZ_KANDIDAT' bis bestaetigt,
                 danach 'MODELLIERT_GEGENSATZ_BESTAETIGT'.

WIEDERHERSTELLUNG NACH ATLAS-REFRESH: atlas_refresh baut das Register aus
kanonischen Adaptern neu auf; unsere beiden Arten haben keinen Adapter und
ueberleben das nicht automatisch. Ein systemd-Timer (siehe
gesamtatlas-relations-reseed.timer) ruft dieses Skript alle 10 Minuten inkrementell
auf, damit die Kanten binnen kurzer Zeit wiederhergestellt sind. Idempotent:
edge_id ist deterministisch (INSERT OR IGNORE), bereits verarbeitete Quell-Knoten
werden uebersprungen.

Nutzung:
  python3 tools_seed_relations.py similar   --limit 500
  python3 tools_seed_relations.py gegensatz --limit 500
  python3 tools_seed_relations.py similar   --limit 0     # 0 = alle restlichen
  python3 tools_seed_relations.py reseed-inkrementell     # fuer den Timer: kurze Haeppchen beider Arten + Bestaetigungslog anwenden
  python3 tools_seed_relations.py stats
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ATLAS_ROOT = Path("/root/werkraum/_gpt/gesamtatlas")
REL_DB = ATLAS_ROOT / "BEZIEHUNGSREGISTER.sqlite"          # DAS kanonische Register -- hier wird jetzt direkt geschrieben
BEGRIFF_DB = ATLAS_ROOT / "BEGRIFFSINDEX.sqlite"
BESTAETIGUNGSLOG = ATLAS_ROOT / "GEGENSATZ_BESTAETIGUNGSLOG.json"  # ueberlebt Register-Rebuilds, kleine JSON-Datei, kein neues Schema

STOPWORDS = set("""
der die das den dem des ein eine einer eines einem und oder aber wenn dann
als auch nicht nur noch schon sehr viel viele mehr weniger fuer von mit bei
nach vor ueber unter zwischen durch gegen ohne um an auf in im zu zum zur
ist sind war waren wird werden wurde wurden hat haben hatte hatten kann
koennen konnte sich es ich du er sie wir ihr man dass ob wie was wer
wo wann warum self none true false import def class return print from
""".split())

TERM_RE = re.compile(r"[a-zA-ZäöüÄÖÜß_][a-zA-ZäöüÄÖÜß0-9_]{3,}")

GEGENSATZPAARE = [
    ("aktiv", "blockiert"), ("aktiv", "deaktiviert"), ("aktiv", "archiviert"),
    ("bestaetigt", "widerlegt"), ("bestätigt", "widerlegt"),
    ("wahr", "falsch"), ("verifiziert", "unverifiziert"),
    ("geplant", "verworfen"), ("erfolgreich", "fehlgeschlagen"),
    ("gestartet", "gestoppt"), ("offen", "geschlossen"),
    ("freigegeben", "gesperrt"), ("live", "archiviert"),
    ("konsens", "konflikt"), ("stabil", "instabil"),
    ("bestaetigt", "kandidat"), ("fertig", "abgebrochen"),
]


def db_connect(path):
    conn = sqlite3.connect(str(path), timeout=30)
    conn.execute("PRAGMA busy_timeout=15000")
    conn.row_factory = sqlite3.Row
    return conn


def make_edge_id(source, target, relation):
    raw = f"{source}|{target}|{relation}".encode("utf-8")
    return "edge:" + hashlib.sha1(raw).hexdigest()[:20]  # gleicher ID-Raum/-Stil wie bestehende edge_id


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def top_terms(text, n=12):
    if not text:
        return []
    words = [w.lower() for w in TERM_RE.findall(text)]
    words = [w for w in words if w not in STOPWORDS]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(n)]


def fts_query_from_terms(terms):
    parts = [f'"{t}"' for t in terms if t]
    return " OR ".join(parts)


def path_type_score(path_a, path_b, type_a, type_b):
    if type_a != type_b:
        return 0.0
    if not path_a or not path_b:
        return 0.2
    pa, pb = Path(path_a).parts, Path(path_b).parts
    common = 0
    for x, y in zip(pa, pb):
        if x == y:
            common += 1
        else:
            break
    depth = max(len(pa), len(pb), 1)
    return min(1.0, common / depth)


def _lade_bestaetigungslog():
    if not BESTAETIGUNGSLOG.exists():
        return {}
    try:
        return json.loads(BESTAETIGUNGSLOG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _speichere_bestaetigungslog(daten):
    BESTAETIGUNGSLOG.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")


def seed_similar(limit, verbose=True):
    if not REL_DB.exists() or not BEGRIFF_DB.exists():
        return {"ok": False, "error": "REL_DB oder BEGRIFF_DB fehlt"}

    rel_conn = db_connect(REL_DB)
    begriff_conn = db_connect(BEGRIFF_DB)

    already_done = {
        r["source_node_id"]
        for r in rel_conn.execute(
            "SELECT DISTINCT source_node_id FROM edges WHERE relation='SIMILAR_TO' AND datenstand='MODELLIERT_AEHNLICHKEIT'"
        ).fetchall()
    }

    all_rows = rel_conn.execute(
        "SELECT node_id, node_type, label, path FROM nodes WHERE node_type='file' AND path IS NOT NULL"
    ).fetchall()
    rows = [r for r in all_rows if r["node_id"] not in already_done]
    if limit > 0:
        rows = rows[:limit]

    path_to_node = {r["path"]: r for r in all_rows}

    written = 0
    skipped_no_body = 0
    t0 = time.time()

    for i, row in enumerate(rows):
        node_id, node_type, label, path = row["node_id"], row["node_type"], row["label"], row["path"]

        body_row = begriff_conn.execute(
            "SELECT body FROM documents WHERE path = ? LIMIT 1", (path,)
        ).fetchone()
        if not body_row or not body_row["body"]:
            skipped_no_body += 1
            continue

        terms = top_terms(body_row["body"], n=10)
        if not terms:
            continue
        fts_q = fts_query_from_terms(terms)
        if not fts_q:
            continue

        try:
            hits = begriff_conn.execute(
                "SELECT path, bm25(documents) as score FROM documents "
                "WHERE documents MATCH ? ORDER BY score LIMIT 15",
                (fts_q,),
            ).fetchall()
        except sqlite3.OperationalError:
            continue

        if not hits:
            continue

        scores = [h["score"] for h in hits if h["path"] != path]
        if not scores:
            continue
        worst, best = max(scores), min(scores)
        span = (worst - best) or 1.0

        candidates = []
        for h in hits:
            other_path = h["path"]
            if other_path == path:
                continue
            other_node = path_to_node.get(other_path)
            if not other_node:
                continue
            text_score_norm = 1.0 - ((h["score"] - best) / span)
            pt_score = path_type_score(path, other_path, node_type, other_node["node_type"])
            combined = round(0.6 * text_score_norm + 0.4 * pt_score, 4)
            candidates.append((other_node["node_id"], other_path, combined, text_score_norm, pt_score))

        candidates.sort(key=lambda c: c[2], reverse=True)
        for target_id, target_path, score, text_score_norm, pt_score in candidates[:5]:
            if score < 0.15:
                continue
            eid = make_edge_id(node_id, target_id, "SIMILAR_TO")
            # Knotenvertrag-Format: beleg/herkunft/staerke/unsicherheit. Immer
            # 'vermutet', weil semantische Naehe allein laut Atlas-Regel keine
            # belegte Kante ist -- hier bewusst und sichtbar als Modell markiert.
            evidence = json.dumps({
                "beleg": f"FTS5-Begriffsueberlappung ({round(text_score_norm,3)}) + Pfad-/Typnaehe ({round(pt_score,3)})",
                "herkunft": "BEGRIFFSINDEX.sqlite bm25 + BEZIEHUNGSREGISTER.sqlite Pfadvergleich",
                "staerke": round(score, 4),
                "unsicherheit": "vermutet",
            }, ensure_ascii=False)
            rel_conn.execute(
                "INSERT OR IGNORE INTO edges "
                "(edge_id, source_node_id, target_node_id, relation, datenstand, evidence_json, first_utc, last_utc) "
                "VALUES (?, ?, ?, 'SIMILAR_TO', 'MODELLIERT_AEHNLICHKEIT', ?, ?, ?)",
                (eid, node_id, target_id, evidence, now_iso(), now_iso()),
            )
            written += 1

        if i % 50 == 0 and i > 0:
            rel_conn.commit()
        if verbose and i % 200 == 0 and i > 0:
            elapsed = time.time() - t0
            print(f"[similar] {i}/{len(rows)} verarbeitet, {written} Kanten geschrieben, {elapsed:.1f}s", flush=True)

    rel_conn.commit()
    rel_conn.close()
    begriff_conn.close()
    return {"ok": True, "processed": len(rows), "edges_written": written, "skipped_no_body": skipped_no_body}


def seed_gegensatz_kandidaten(limit, verbose=True):
    if not REL_DB.exists():
        return {"ok": False, "error": "REL_DB fehlt"}

    rel_conn = db_connect(REL_DB)

    rows = rel_conn.execute(
        "SELECT node_id, node_type, label, path, metadata_json FROM nodes "
        "WHERE node_type NOT IN ('geni_knoten', 'gedanke')"
        + ("" if limit <= 0 else f" LIMIT {int(limit)}")
    ).fetchall()

    def node_text(r):
        parts = [r["label"] or "", r["path"] or "", (r["metadata_json"] or "")[:2000]]
        return " ".join(parts).lower()

    by_word = {}
    for r in rows:
        t = node_text(r)
        for a, b in GEGENSATZPAARE:
            if a in t:
                by_word.setdefault(a, []).append(r)
            if b in t:
                by_word.setdefault(b, []).append(r)

    written = 0
    checked_pairs = 0
    for a, b in GEGENSATZPAARE:
        left = by_word.get(a, [])
        right = by_word.get(b, [])
        for lr in left:
            for rr in right:
                if lr["node_id"] == rr["node_id"]:
                    continue
                if lr["node_type"] != rr["node_type"]:
                    continue
                pscore = path_type_score(lr["path"] or "", rr["path"] or "", lr["node_type"], rr["node_type"])
                if pscore < 0.15:
                    continue
                checked_pairs += 1
                eid = make_edge_id(lr["node_id"], rr["node_id"], "OPPOSES")
                evidence = json.dumps({
                    "beleg": f"Gegensatzpaar-Vokabular ({a} / {b}) in Label/Pfad/Metadaten",
                    "herkunft": "kuratierte Gegensatzpaar-Liste, halbautomatischer Abgleich",
                    "staerke": round(pscore, 4),
                    "unsicherheit": "vermutet",
                }, ensure_ascii=False)
                rel_conn.execute(
                    "INSERT OR IGNORE INTO edges "
                    "(edge_id, source_node_id, target_node_id, relation, datenstand, evidence_json, first_utc, last_utc) "
                    "VALUES (?, ?, ?, 'OPPOSES', 'MODELLIERT_GEGENSATZ_KANDIDAT', ?, ?, ?)",
                    (eid, lr["node_id"], rr["node_id"], evidence, now_iso(), now_iso()),
                )
                written += 1

    rel_conn.commit()
    rel_conn.close()
    if verbose:
        print(f"[gegensatz] {checked_pairs} Paare geprueft, {written} Kandidaten-Kanten geschrieben")
    return {"ok": True, "processed": len(rows), "candidates_written": written}


def bestaetigungslog_anwenden(verbose=True):
    """Wendet den dauerhaften Bestaetigungs-Log auf das (evtl. gerade frisch
    wiederhergestellte) Register an -- macht bestaetigte/verworfene OPPOSES-
    Kanten nach einem Rebuild wieder sichtbar, ohne dass der Nutzer erneut
    bestaetigen muss."""
    log = _lade_bestaetigungslog()
    if not log:
        return {"ok": True, "angewendet": 0}
    conn = db_connect(REL_DB)
    angewendet = 0
    for edge_id, eintrag in log.items():
        status = eintrag.get("status")
        row = conn.execute("SELECT edge_id FROM edges WHERE edge_id = ?", (edge_id,)).fetchone()
        if not row:
            continue  # Kante noch nicht wiederhergestellt -- naechster Reseed-Lauf holt sie nach
        if status == "verworfen":
            conn.execute("DELETE FROM edges WHERE edge_id = ?", (edge_id,))
            angewendet += 1
        elif status == "bestaetigt":
            conn.execute(
                "UPDATE edges SET datenstand = 'MODELLIERT_GEGENSATZ_BESTAETIGT' WHERE edge_id = ?",
                (edge_id,),
            )
            angewendet += 1
    conn.commit()
    conn.close()
    if verbose:
        print(f"[bestaetigungslog] {angewendet} Eintraege angewendet")
    return {"ok": True, "angewendet": angewendet}


def reseed_inkrementell():
    """Fuer den systemd-Timer: kurze Haeppchen, damit ein einzelner Lauf nie
    lange blockiert. Reihenfolge: erst Kandidaten/Aehnlichkeit nachziehen,
    dann den Bestaetigungslog anwenden."""
    r1 = seed_similar(400, verbose=False)
    r2 = seed_gegensatz_kandidaten(3000, verbose=False)
    r3 = bestaetigungslog_anwenden(verbose=False)
    print(json.dumps({"similar": r1, "gegensatz": r2, "bestaetigungslog": r3}, ensure_ascii=False))


def stats():
    conn = db_connect(REL_DB)
    rows = conn.execute(
        "SELECT relation, datenstand, COUNT(*) c FROM edges WHERE relation IN ('SIMILAR_TO','OPPOSES') GROUP BY relation, datenstand ORDER BY c DESC"
    ).fetchall()
    conn.close()
    out = [dict(r) for r in rows]
    for r in out:
        print(r["relation"], "|", r["datenstand"], "|", r["c"])
    return {"ok": True, "rows": out}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("modus", choices=["similar", "gegensatz", "reseed-inkrementell", "bestaetigungslog-anwenden", "stats"])
    ap.add_argument("--limit", type=int, default=200)
    args = ap.parse_args()

    if args.modus == "similar":
        print(seed_similar(args.limit))
    elif args.modus == "gegensatz":
        print(seed_gegensatz_kandidaten(args.limit))
    elif args.modus == "reseed-inkrementell":
        reseed_inkrementell()
    elif args.modus == "bestaetigungslog-anwenden":
        print(bestaetigungslog_anwenden())
    else:
        stats()
