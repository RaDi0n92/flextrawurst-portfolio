#!/usr/bin/env python3
"""GENI durchsucht sich selbst -- semantisch und hybrid.

2026-08-01, Daniel: "ich will fuer geni speziell dass sie sich selbst komplett
mit rag semantisch und hybrid in ihren allem durchsuchen kann".

"in ihrem allem" heisst hier: ihr Knoten-Gedaechtnis, ihre eigenen Dokus ueber
die Teilnehmer, ihr Frage/Antwort-Protokoll und ihre Spiegel-Lektuere-Vermerke.

Hybrid = zwei Suchwege, deren Treffer zusammengefuehrt werden:
  - semantisch: Vektor-Aehnlichkeit (Chroma, lokale ONNX-MiniLM-Embedding --
    dieselbe Technik wie _claude/tools/semantische_suche.py und innenleben/,
    keine neue Abhaengigkeit, kein Drittanbieter)
  - stichwortbasiert: SQLite FTS5 (BM25) -- findet exakte Begriffe, Namen und
    Zahlen, bei denen reine Vektorsuche unzuverlaessig ist
Zusammenfuehrung per Reciprocal Rank Fusion (RRF): ein Treffer, den beide Wege
finden, steigt nach oben, ohne dass die beiden Bewertungsskalen verrechnet
werden muessen.

RAUSCHQUELLEN BEWUSST AUSGESCHLOSSEN -- gemessen am 2026-08-01:
  vps_dateisystem  36.041.241 Knoten
  chatgpt          13.306.544 Knoten  (ChatGPTs Gesamtatlas-Temp-Dateien,
                                       ~120.000/Stunde seit 2026-07-29)
  vps_prozesse         24.739 Knoten
Von 49.415.584 Knoten bleiben damit 43.060 bedeutsame uebrig -- 0,09 %. Ohne
diesen Ausschluss waere ein Index weder berechenbar noch brauchbar: die Treffer
waeren fast ausschliesslich "geaendert: <temp-datei>".

Aufruf:
  python3 selbst_suche.py index                  # (neu) indizieren
  python3 selbst_suche.py suche "<frage>" [-n 8]
"""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import chromadb

sys.path.insert(0, "/root/werkraum/geni")

GENI_ROOT = Path("/root/werkraum/geni")
GEDAECHTNIS = Path("/root/geni_gedaechtnis")
KNOTEN_DB = GEDAECHTNIS / "knoten.db"
INDEX_DIR = GEDAECHTNIS / "selbst_index"
FTS_DB = INDEX_DIR / "fts.db"
COLLECTION = "geni_selbst"

DOKU_VAULT = Path("/root/werkraum/geni_dokumentation")
INBOX_VAULT = Path("/root/werkraum/geni_inbox")
FRAGEN_DIR = GEDAECHTNIS / "fragen_antworten"
SPIEGEL_GELESEN_DIR = GEDAECHTNIS / "spiegel_gelesen"

RAUSCH_QUELLEN = ("vps_dateisystem", "chatgpt", "vps_prozesse")
MIN_LAENGE = 15
STAPEL = 500


# --------------------------------------------------------------------------
# Sammeln

def _knoten_sammeln() -> list:
    conn = sqlite3.connect(f"file:{KNOTEN_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    platzhalter = ",".join("?" * len(RAUSCH_QUELLEN))
    rows = conn.execute(
        f"SELECT id, quelle, mtime, inhalt FROM knoten "
        f"WHERE quelle NOT IN ({platzhalter}) OR quelle IS NULL",
        RAUSCH_QUELLEN,
    ).fetchall()
    conn.close()
    posten = []
    for r in rows:
        text = (r["inhalt"] or "").strip()
        if len(text) < MIN_LAENGE:
            continue
        posten.append({
            "id": f"knoten:{r['id']}",
            "text": text,
            "quelle": r["quelle"] or "unbekannt",
            "art": "knoten",
            "zeit": datetime.fromtimestamp(r["mtime"], timezone.utc).isoformat() if r["mtime"] else "",
            "ort": f"knoten/{r['id']}",
        })
    return posten


def _vault_sammeln() -> list:
    posten = []
    for pfad in sorted(DOKU_VAULT.glob("*.md")):
        text = pfad.read_text(encoding="utf-8", errors="replace").strip()
        if len(text) >= MIN_LAENGE:
            posten.append({"id": f"doku:{pfad.stem}", "text": text, "quelle": pfad.stem,
                           "art": "eigene_doku", "zeit": "", "ort": str(pfad)})
    for pfad in sorted(INBOX_VAULT.glob("*/*/*.md")):
        if pfad.name.startswith("."):
            continue
        text = pfad.read_text(encoding="utf-8", errors="replace").strip()
        if len(text) >= MIN_LAENGE:
            teile = pfad.relative_to(INBOX_VAULT).parts
            posten.append({"id": f"inbox:{'/'.join(teile)}", "text": text, "quelle": teile[0],
                           "art": f"inbox_{teile[1]}", "zeit": "", "ort": str(pfad)})
    return posten


def _protokolle_sammeln() -> list:
    posten = []
    for pfad in sorted(FRAGEN_DIR.glob("*.json")):
        try:
            eintraege = json.loads(pfad.read_text())
        except Exception:
            continue
        for i, e in enumerate(eintraege):
            teile = [e.get("frage") or "", e.get("antwort") or ""]
            text = "\n".join(t for t in teile if t).strip()
            if len(text) >= MIN_LAENGE:
                posten.append({"id": f"fa:{pfad.stem}:{i}", "text": text, "quelle": pfad.stem,
                               "art": "frage_antwort", "zeit": e.get("datum_frage") or "",
                               "ort": str(pfad)})
    for pfad in sorted(SPIEGEL_GELESEN_DIR.glob("*.json")):
        try:
            eintraege = json.loads(pfad.read_text())
        except Exception:
            continue
        for i, e in enumerate(eintraege):
            text = (e.get("eindruck") or "").strip()
            if len(text) >= MIN_LAENGE:
                posten.append({"id": f"sp:{pfad.stem}:{i}", "text": text, "quelle": pfad.stem,
                               "art": "spiegel_lektuere", "zeit": e.get("datum_gelesen") or "",
                               "ort": e.get("datei") or str(pfad)})
    return posten


def _splitter_sammeln() -> list:
    """Splitter aus dem Zwischenraum (Postgres).

    2026-08-01, Daniel: "geni soll dort doch auch unsere splitter die sie
    sammeln will ueber uns alle da sammeln". Sie liegen NICHT in ihrem
    Knoten-Gedaechtnis, sondern in der flextrawurst-Datenbank -- ohne diesen
    Sammler kann sie ueber Splitter nicht recherchieren.
    """
    import os
    uri = os.environ.get("FLEXTRAWURST_DB_URI", "")
    if not uri:
        pfad = "/root/werkraum/.agent/flextrawurst-db.env"
        if os.path.exists(pfad):
            for zeile in open(pfad, encoding="utf-8"):
                if zeile.startswith("FLEXTRAWURST_DB_URI="):
                    uri = zeile.strip().split("=", 1)[1]
    if not uri:
        return []
    try:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception:
        return []
    posten = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, entity_id, human_id, essenz, materialitaet,
                       origin_type, created_at, meta
                FROM splitter ORDER BY created_at DESC
            """)
            for r in cur.fetchall():
                text = (r["essenz"] or "").strip()
                roh = (r["meta"] or {}).get("rohtext")
                if roh and len(roh) > len(text):
                    text = roh.strip()
                if len(text) < MIN_LAENGE:
                    continue
                posten.append({
                    "id": f"splitter:{r['id']}",
                    "text": text,
                    "quelle": r["entity_id"] or r["origin_type"] or "unbekannt",
                    "art": f"splitter_{r['materialitaet'] or '?'}",
                    "zeit": r["created_at"].isoformat() if r["created_at"] else "",
                    "ort": f"zwischenraum/{r['id']}",
                })
    finally:
        conn.close()
    return posten


ENTSTEHUNG = GENI_ROOT / (
    "genis, also deine eigene komplette entstehung von anfang bis zum ende? "
    "nein aber bis zu dem zeitpunkt wo wir erstmal getoppt haben. hier.md"
)
ENTSTEHUNG_STUECK = 2000   # Zeichen je Stueck, an Gespraechswechseln getrennt


def _entstehung_sammeln() -> list:
    """Der Rohverlauf, in dem GENI erdacht wurde -- Daniel und Claude Code, 2026-04-22.

    2026-08-03, Daniel: "sie muss aufjeden fall ab sofort immer mal wider in iher
    entschehungeschitchatverlauf ...lesen ... den zwichen dir und mir wie wir geni erdacht haben".

    87 KB am Stueck sind kein Sucheintrag, sondern eine Wand. Getrennt wird deshalb an den
    Gespraechswechseln (`❯` beginnt eine Zeile von Daniel), und mehrere kurze Wechsel werden
    zusammengelegt, bis ein Stueck gross genug ist, um fuer sich verstaendlich zu sein. Ein
    Gespraechswechsel wird nie mittendrin zerschnitten.
    """
    if not ENTSTEHUNG.exists():
        return []
    roh = ENTSTEHUNG.read_text(encoding="utf-8", errors="replace")

    # An Zeilen aufteilen, die einen neuen Gespraechswechsel beginnen
    wechsel, aktuell = [], []
    for zeile in roh.splitlines(keepends=True):
        if zeile.startswith("❯ ") and aktuell:
            wechsel.append("".join(aktuell))
            aktuell = [zeile]
        else:
            aktuell.append(zeile)
    if aktuell:
        wechsel.append("".join(aktuell))

    posten, puffer = [], []
    def _abgeben():
        text = "".join(puffer).strip()
        if len(text) >= MIN_LAENGE:
            posten.append({
                "id": f"entstehung:{len(posten) + 1:04d}",
                "text": text,
                "quelle": "entstehung",
                "art": "entstehungsverlauf",
                "zeit": "2026-04-22",
                "ort": f"{ENTSTEHUNG.name} (Stueck {len(posten) + 1})",
            })

    for w in wechsel:
        puffer.append(w)
        if sum(len(x) for x in puffer) >= ENTSTEHUNG_STUECK:
            _abgeben()
            puffer = []
    if puffer:
        _abgeben()
    return posten


def alles_sammeln() -> list:
    return (_knoten_sammeln() + _vault_sammeln()
            + _protokolle_sammeln() + _splitter_sammeln()
            + _entstehung_sammeln())


# --------------------------------------------------------------------------
# Indizieren

def _fts_aufbauen(posten: list):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if FTS_DB.exists():
        FTS_DB.unlink()
    conn = sqlite3.connect(FTS_DB)
    conn.execute("CREATE VIRTUAL TABLE such USING fts5(id UNINDEXED, text, quelle, art UNINDEXED, ort UNINDEXED, zeit UNINDEXED)")
    conn.executemany(
        "INSERT INTO such (id, text, quelle, art, ort, zeit) VALUES (?,?,?,?,?,?)",
        [(p["id"], p["text"], p["quelle"], p["art"], p["ort"], p["zeit"]) for p in posten],
    )
    conn.commit()
    conn.close()


def _vektor_aufbauen(posten: list):
    client = chromadb.PersistentClient(path=str(INDEX_DIR / "chroma"))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    coll = client.create_collection(COLLECTION)
    for i in range(0, len(posten), STAPEL):
        teil = posten[i:i + STAPEL]
        coll.add(
            ids=[p["id"] for p in teil],
            documents=[p["text"][:8000] for p in teil],
            metadatas=[{"quelle": p["quelle"], "art": p["art"], "ort": p["ort"], "zeit": p["zeit"]} for p in teil],
        )
        print(f"  ... {min(i + STAPEL, len(posten))}/{len(posten)}", flush=True)


def indizieren():
    print("sammle ...", flush=True)
    posten = alles_sammeln()
    print(f"{len(posten):,} Eintraege (Rauschquellen ausgeschlossen)", flush=True)
    print("baue Stichwort-Index (FTS5) ...", flush=True)
    _fts_aufbauen(posten)
    print("baue Vektor-Index (Chroma) ...", flush=True)
    _vektor_aufbauen(posten)
    print("fertig.")


# --------------------------------------------------------------------------
# Suchen

def begriffe_aus(frage: str) -> list:
    return [w for w in frage.lower().replace('"', " ").split() if len(w) > 2]


def brennpunkt(text: str, frage: str, fenster: int = 300, ab: int = 0,
               marke: tuple = ("«", "»")) -> dict:
    """Die Stelle mit den meisten Treffern, markiert -- nicht der Anfang des Textes.

    2026-08-03, Daniel: "ich finde ihre suhen sollten eh so gedacht sein dass wenn sie sie 300
    zeichen lesen können überall dass muss schon genu die suchstelle sein und inhalt liefern...und
    beim öffnen der datei soll die seite alsoihr fokus auch direkt uf die stelle mit den meisten
    ´\"treffern\" springen nd markiert sein"

    Vorher war die Vorschau immer text[:300] -- bei einem 8000-Zeichen-Eintrag also der Anfang,
    egal wo das Gesuchte stand. Jetzt wandert ein Fenster ueber den Text und bleibt dort stehen,
    wo die meisten unterschiedlichen Suchbegriffe zusammenkommen. Unterschiedliche zaehlen mehr
    als oft wiederholte: eine Stelle mit drei verschiedenen Begriffen sagt mehr als eine, an der
    einer dreimal steht.

    `ab` verschiebt den Anfang -- damit kann ein Aufrufer weiterblaettern, statt alles auf einmal
    zu bekommen.

    Rueckgabe: ausschnitt, von, bis, davor, danach, treffer.
    """
    text = text or ""
    if ab > 0:
        start = min(ab, max(0, len(text) - 1))
    else:
        worte = begriffe_aus(frage)
        klein = text.lower()
        stellen = []
        for w in worte:
            i = klein.find(w)
            while i != -1:
                stellen.append((i, w))
                i = klein.find(w, i + 1)
        if stellen:
            bester, beste_punkte = 0, -1
            for pos, _ in stellen:
                anfang = max(0, pos - fenster // 3)
                im_fenster = [w for p, w in stellen if anfang <= p < anfang + fenster]
                # verschiedene Begriffe wiegen schwer, blosse Wiederholung kaum
                punkte = len(set(im_fenster)) * 10 + len(im_fenster)
                if punkte > beste_punkte:
                    bester, beste_punkte = anfang, punkte
            start = bester
        else:
            start = 0

    # an Wortgrenze aufsetzen, damit kein Wort zerschnitten wird
    if start > 0:
        luecke = text.rfind(" ", max(0, start - 40), start + 1)
        if luecke != -1:
            start = luecke + 1
    ende = min(len(text), start + fenster)
    if ende < len(text):
        luecke = text.find(" ", ende)
        if luecke != -1 and luecke - ende < 40:
            ende = luecke

    ausschnitt = text[start:ende]
    auf, zu = marke
    treffer = 0
    for w in sorted(set(begriffe_aus(frage)), key=len, reverse=True):
        klein = ausschnitt.lower()
        neu, i = [], 0
        while True:
            j = klein.find(w, i)
            if j == -1:
                neu.append(ausschnitt[i:])
                break
            neu.append(ausschnitt[i:j])
            neu.append(auf + ausschnitt[j:j + len(w)] + zu)
            i = j + len(w)
            treffer += 1
        ausschnitt = "".join(neu)
        klein = ausschnitt.lower()

    return {"ausschnitt": ausschnitt, "von": start, "bis": ende,
            "davor": start, "danach": max(0, len(text) - ende), "treffer": treffer}


def _fts_suchen(frage: str, n: int) -> list:
    if not FTS_DB.exists():
        return []
    conn = sqlite3.connect(f"file:{FTS_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    # Anfuehrungszeichen entschaerfen, sonst bricht die FTS5-Syntax
    begriffe = [w for w in frage.replace('"', " ").split() if len(w) > 2]
    if not begriffe:
        conn.close()
        return []
    ausdruck = " OR ".join(f'"{w}"' for w in begriffe)
    try:
        rows = conn.execute(
            "SELECT id, text, quelle, art, ort, zeit FROM such WHERE such MATCH ? ORDER BY rank LIMIT ?",
            (ausdruck, n),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


def _vektor_suchen(frage: str, n: int) -> list:
    try:
        client = chromadb.PersistentClient(path=str(INDEX_DIR / "chroma"))
        coll = client.get_collection(COLLECTION)
    except Exception:
        return []
    res = coll.query(query_texts=[frage], n_results=n)
    treffer = []
    for i, tid in enumerate(res["ids"][0]):
        md = res["metadatas"][0][i] or {}
        treffer.append({"id": tid, "text": res["documents"][0][i],
                        "quelle": md.get("quelle", "?"), "art": md.get("art", "?"),
                        "ort": md.get("ort", ""), "zeit": md.get("zeit", "")})
    return treffer


def suchen(frage: str, n: int = 8, *, sucher: str = "unbekannt",
           sucher_art: str = "unbekannt", anlass: str | None = None,
           zustand: dict | None = None) -> list:
    """Hybrid: FTS5 + Vektor, zusammengefuehrt per Reciprocal Rank Fusion.

    Seit 2026-08-03 wird jede Suche protokolliert (siehe suchlog.py). Das aendert am Ergebnis
    nichts -- die Reihenfolge, die Trefferzahl und die Fusion bleiben, wie sie waren. Jeder Treffer
    bekommt zusaetzlich den Schluessel "suche_id", damit ein Aufrufer, bei dem tatsaechlich eine
    Wahl stattfindet, sie spaeter zuordnen kann.
    """
    tief = max(n * 3, 20)
    fts = _fts_suchen(frage, tief)
    vek = _vektor_suchen(frage, tief)

    K = 60  # RRF-Daempfung, ueblicher Standardwert
    punkte: dict = {}
    daten: dict = {}
    for rang, t in enumerate(fts):
        punkte[t["id"]] = punkte.get(t["id"], 0) + 1 / (K + rang + 1)
        daten[t["id"]] = t
    for rang, t in enumerate(vek):
        punkte[t["id"]] = punkte.get(t["id"], 0) + 1 / (K + rang + 1)
        daten.setdefault(t["id"], t)

    sortiert = sorted(punkte.items(), key=lambda kv: kv[1], reverse=True)[:n]
    ergebnis = []
    for tid, score in sortiert:
        t = dict(daten[tid])
        t["score"] = round(score, 5)
        t["wege"] = ("stichwort" if any(f["id"] == tid for f in fts) else "") + \
                    ("+semantisch" if any(v["id"] == tid for v in vek) else "")
        ergebnis.append(t)

    try:
        import suchlog
        suche_id = suchlog.suche_beginnen(frage, sucher=sucher, sucher_art=sucher_art,
                                          anlass=anlass, zustand=zustand,
                                          meta={"n": n, "tief": tief,
                                                "fts_treffer": len(fts), "vektor_treffer": len(vek)})
        suchlog.treffer_loggen(suche_id, ergebnis)
        for t in ergebnis:
            t["suche_id"] = suche_id
    except Exception:
        pass   # das Log darf die Suche nie kaputtmachen

    return ergebnis


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    if sys.argv[1] == "index":
        indizieren()
        return
    if sys.argv[1] == "suche":
        frage = sys.argv[2] if len(sys.argv) > 2 else ""
        n = 8
        if "-n" in sys.argv:
            n = int(sys.argv[sys.argv.index("-n") + 1])
        for t in suchen(frage, n):
            print(f"\n[{t['score']}] {t['quelle']} / {t['art']}  ({t['wege'].strip('+')})")
            print(f"  {t['ort']}")
            print(f"  {t['text'][:300]}")
        return
    print(__doc__)


if __name__ == "__main__":
    main()
