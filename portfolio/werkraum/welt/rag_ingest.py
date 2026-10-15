#!/usr/bin/env python3
"""
RAG Ring 1 — Einspeisung + Zerlegung + Embeddings.
Quelle: _claude/konzepte/DURCHF~1.ODT ("Durchführbare RAG-, Erinnerungs- und Resonanzarchitektur").

Korpora (Daniel-Entscheidung 2026-07-20): Flarum-Archiv pro Wesen + geteiltes Weltwissen.
Dazu seit 2026-09-17: inaktiv gesetzte Gruppenchat-Sitzungen (siehe unten).
GENI-Gedächtnis bewusst NICHT Teil dieses Rings.

Zerlegung strukturbezogen, nicht blind nach Wortzahl:
- wissen/*.md: pro '## '-Abschnitt ein Chunk (gleiches Muster wie _claude/tools/semantische_suche.py)
- flarum/diskussionen/*.md: pro Post ein Chunk, mit Wesen-Attribution aus dem Post-Autor
- codewesen/_gruppenchat/sitzungen/*.json (nur inaktive): pro Nachricht ein Chunk

Idempotent über inhalt_pruefsumme (sha256) — ein erneuter Lauf ueberspringt unveraenderte Chunks.

Gruppenchat wird normalerweise NICHT ueber die CLI hier eingespeist, sondern live
ueber codewesen_chat.py, sobald eine Sitzung inaktiv gesetzt wird (siehe
ingest_gruppenchat()). Der CLI-Modus "gruppenchat" ist nur ein manueller Nachholpfad.

Usage:
  python3 rag_ingest.py wissen [--limit N]
  python3 rag_ingest.py flarum [--limit N]
  python3 rag_ingest.py gruppenchat [--limit N]
  python3 rag_ingest.py alles [--limit N]
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst")
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODELL = "bge-m3"

WERKRAUM = Path("/root/werkraum")
WISSEN_DIR = WERKRAUM / "wissen"
FLARUM_DIR = WERKRAUM / "flarum" / "diskussionen"

# ID-Mapping aus _claude/wesen/_INDEX.md (2026-07-06 Umbenennung) + bekannte Zweitstimmen-Praefixe
SUFFIX_ZU_WESEN = {
    "1234": "Schorschel",
    "1324": "F3INSCHM3CK3R",
    "1423": "träumerlie",
    "2341": "R1ZZ1",
    "3123": "jumpa",
    "4321": "Resonanzknoten",
}
KANONISCHE_NAMEN = set(SUFFIX_ZU_WESEN.values()) | {"dak+gord-system", "dak-gord-system"}
MENSCHEN_NAMEN = {"Admin", "Pit1905", "fridolin", "Daniel"}


def wesen_aus_autor(autor: str) -> str | None:
    """Ordnet einen rohen Flarum-Autornamen dem kanonischen Wesen-Namen zu, oder None bei Menschen."""
    autor = autor.strip()
    if autor in MENSCHEN_NAMEN:
        return None
    if autor in KANONISCHE_NAMEN:
        return "dak+gord-system" if autor == "dak-gord-system" else autor
    m = re.match(r"namelessAI_(?:\d{4}_)?(\d{4})$", autor)
    if m:
        return SUFFIX_ZU_WESEN.get(m.group(1))
    return None


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed(text: str) -> list[float]:
    resp = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODELL, "input": text}, timeout=60)
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def db_connect():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def upsert_source_object(cur, external_id, quelle, wesen, titel, inhalt, erstellungszeit,
                          urheber, herkunftsort, ereignistyp, wahrheitsstatus, meta):
    pruefsumme = sha256(inhalt)
    cur.execute("""
        INSERT INTO rag_source_objects
            (external_id, quelle, wesen, titel, inhalt, erstellungszeit, urheber,
             herkunftsort, ereignistyp, wahrheitsstatus, inhalt_pruefsumme, meta, aktualisiert_am)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
        ON CONFLICT (external_id) DO UPDATE SET
            inhalt = EXCLUDED.inhalt,
            inhalt_pruefsumme = EXCLUDED.inhalt_pruefsumme,
            titel = EXCLUDED.titel,
            meta = EXCLUDED.meta,
            aktualisiert_am = now()
        RETURNING id, inhalt_pruefsumme
    """, (external_id, quelle, wesen, titel, inhalt, erstellungszeit, urheber,
          str(herkunftsort), ereignistyp, wahrheitsstatus, pruefsumme, json.dumps(meta)))
    return cur.fetchone()["id"]


def upsert_chunk_mit_embedding(cur, source_object_id, chunk_index, ueberschrift, inhalt, meta):
    pruefsumme = sha256(inhalt)
    cur.execute("""
        SELECT c.id, e.id AS embedding_id
        FROM rag_source_chunks c
        LEFT JOIN rag_embeddings e ON e.chunk_id = c.id AND e.modell = %s
        WHERE c.source_object_id = %s AND c.chunk_index = %s
    """, (EMBED_MODELL, source_object_id, chunk_index))
    row = cur.fetchone()

    if row and row["embedding_id"] is not None:
        # bereits vollstaendig indiziert -- pruefen ob Inhalt sich geaendert hat
        cur.execute("SELECT inhalt FROM rag_source_chunks WHERE id=%s", (row["id"],))
        bestehender = cur.fetchone()["inhalt"]
        if sha256(bestehender) == pruefsumme:
            return "unveraendert"

    try:
        vektor = embed(inhalt)
    except requests.exceptions.HTTPError as e:
        print(f"[warnung] Chunk übersprungen, Embed schlug fehl ({len(inhalt)} Zeichen, "
              f"source_object_id={source_object_id}, chunk_index={chunk_index}): {e}",
              file=sys.stderr, flush=True)
        return "uebersprungen_zu_gross"

    cur.execute("""
        INSERT INTO rag_source_chunks (source_object_id, chunk_index, ueberschrift, inhalt, meta)
        VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (source_object_id, chunk_index) DO UPDATE SET
            ueberschrift = EXCLUDED.ueberschrift, inhalt = EXCLUDED.inhalt, meta = EXCLUDED.meta
        RETURNING id
    """, (source_object_id, chunk_index, ueberschrift, inhalt, json.dumps(meta)))
    chunk_id = cur.fetchone()["id"]

    cur.execute("""
        INSERT INTO rag_embeddings (chunk_id, modell, embedding)
        VALUES (%s,%s,%s)
        ON CONFLICT (chunk_id, modell) DO UPDATE SET embedding = EXCLUDED.embedding, erstellt_am = now()
    """, (chunk_id, EMBED_MODELL, vektor))
    return "neu_eingebettet"


# --- Wissen-Korpus -----------------------------------------------------------

def chunks_aus_wissen_datei(text: str):
    """Ein Chunk pro '## '-Abschnitt -- identisches Muster wie semantische_suche.py."""
    zeilen = text.split("\n")
    chunks = []
    titel = "(Anfang)"
    inhalt = []

    def abschliessen():
        c = "\n".join(inhalt).strip()
        if c:
            chunks.append((titel, c))

    for zeile in zeilen:
        if zeile.startswith("## "):
            abschliessen()
            titel = zeile[3:].strip()
            inhalt = []
        else:
            inhalt.append(zeile)
    abschliessen()
    return chunks


def ingest_wissen(limit=None):
    dateien = sorted(WISSEN_DIR.rglob("*.md"))
    if limit:
        dateien = dateien[:limit]
    conn = db_connect()
    conn.autocommit = False
    neu, unveraendert, zu_gross = 0, 0, 0
    for i, pfad in enumerate(dateien):
        rel = pfad.relative_to(WERKRAUM)
        text = pfad.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            continue
        titel_zeile = next((l for l in text.split("\n") if l.strip()), pfad.stem)
        titel = titel_zeile.lstrip("#").strip() or pfad.stem
        with conn.cursor() as cur:
            source_id = upsert_source_object(
                cur, external_id=f"wissen:{rel}", quelle="wissen", wesen=None,
                titel=titel, inhalt=text, erstellungszeit=None, urheber=None,
                herkunftsort=rel, ereignistyp="wissen_dokument",
                wahrheitsstatus="aus_datei_abgeleitet", meta={},
            )
            for idx, (ueberschrift, inhalt) in enumerate(chunks_aus_wissen_datei(text)):
                status = upsert_chunk_mit_embedding(cur, source_id, idx, ueberschrift, inhalt, {})
                neu += status == "neu_eingebettet"
                unveraendert += status == "unveraendert"
                zu_gross += status == "uebersprungen_zu_gross"
        conn.commit()  # eine Datei = eine Transaktion -- Abbruch verliert nur die aktuelle Datei
        print(f"[wissen] {i+1}/{len(dateien)} {rel}", flush=True)
    conn.close()
    if zu_gross:
        print(f"[wissen] {zu_gross} Chunks wegen Context-Laenge uebersprungen (siehe Warnungen oben)")
    print(f"[wissen] fertig: {neu} neu eingebettet, {unveraendert} unveraendert")


# --- Flarum-Korpus -------------------------------------------------------------

POST_MUSTER = re.compile(
    r"^### Post #(\d+)\s*—\s*(?:[^\[]*)\[\[[^|]+\|([^\]]+)\]\]\s*—\s*([\d\- :]+)\s*$",
    re.MULTILINE,
)
FRONTMATTER_MUSTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_MUSTER.match(text)
    if not m:
        return {}
    felder = {}
    for zeile in m.group(1).split("\n"):
        if ":" not in zeile:
            continue
        k, _, v = zeile.partition(":")
        felder[k.strip()] = v.strip().strip('"')
    return felder


def posts_aus_diskussion(text: str):
    """Ein Chunk pro Post -- Post bleibt Grundeinheit, nie mitten in Antwort/Ursache getrennt."""
    treffer = list(POST_MUSTER.finditer(text))
    posts = []
    for i, t in enumerate(treffer):
        start = t.end()
        ende = treffer[i + 1].start() if i + 1 < len(treffer) else len(text)
        inhalt = text[start:ende]
        inhalt = inhalt.split("\n---\n")[0].strip()
        post_nr, autor_roh, zeitstempel = t.group(1), t.group(2), t.group(3).strip()
        posts.append((int(post_nr), autor_roh, zeitstempel, inhalt))
    return posts


def ingest_flarum(limit=None):
    dateien = sorted(FLARUM_DIR.glob("*.md"))
    if limit:
        dateien = dateien[:limit]
    conn = db_connect()
    conn.autocommit = False
    neu, unveraendert, uebersprungen, zu_gross = 0, 0, 0, 0
    for i, pfad in enumerate(dateien):
        rel = pfad.relative_to(WERKRAUM)
        text = pfad.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        if not fm.get("titel"):
            uebersprungen += 1
            continue
        erstellt = None
        try:
            erstellt = datetime.strptime(fm["erstellt"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except Exception:
            pass
        with conn.cursor() as cur:
            source_id = upsert_source_object(
                cur, external_id=f"flarum:diskussion:{fm.get('id', pfad.stem)}",
                quelle="flarum_diskussion", wesen=wesen_aus_autor(fm.get("autor", "")),
                titel=fm["titel"], inhalt=text, erstellungszeit=erstellt,
                urheber=fm.get("autor"), herkunftsort=rel, ereignistyp="flarum_diskussion",
                wahrheitsstatus="aus_forum_abgeleitet",
                meta={"tags": fm.get("tags", ""), "posts": fm.get("posts")},
            )
            for post_nr, autor_roh, zeitstempel, inhalt in posts_aus_diskussion(text):
                if not inhalt:
                    continue
                wesen = wesen_aus_autor(autor_roh)
                status = upsert_chunk_mit_embedding(
                    cur, source_id, post_nr, f"Post #{post_nr} — {autor_roh}", inhalt,
                    {"autor_roh": autor_roh, "wesen": wesen, "zeitstempel": zeitstempel},
                )
                neu += status == "neu_eingebettet"
                unveraendert += status == "unveraendert"
                zu_gross += status == "uebersprungen_zu_gross"
        conn.commit()  # eine Datei = eine Transaktion -- Abbruch verliert nur die aktuelle Datei
        print(f"[flarum] {i+1}/{len(dateien)} {rel}", flush=True)
    conn.close()
    if zu_gross:
        print(f"[flarum] {zu_gross} Chunks wegen Context-Laenge uebersprungen (siehe Warnungen oben)")
    print(f"[flarum] fertig: {neu} neu eingebettet, {unveraendert} unveraendert, {uebersprungen} ohne Frontmatter uebersprungen")


# --- Gruppenchat-Korpus (2026-09-17) --------------------------------------------
#
# Daniels Auftrag: eine Gruppenchat-Sitzung soll, sobald sie als "inaktiv" markiert
# wird (codewesen_gruppenchat.setze_inaktiv, ausgeloest ueber codewesen_chat.py),
# durchsuchbar fuer die Wesen bleiben -- ueber genau denselben rag_erkunden:-Weg,
# den sie fuer Flarum/Weltwissen schon kennen. quelle="gruppenchat" hat keinen
# eigenen Filter in rag_retrieve.suche() noetig: der Aufruf aus browser_agent.py
# (rag_erkunden:) uebergibt nie einen quelle-Filter, sucht also automatisch ueber
# alle Quellen inklusive dieser neuen.
#
# Anders als wissen_/flarum_: kein Verzeichnis-Scan noetig, wird pro Sitzung direkt
# aufgerufen (aus codewesen_chat.py._gruppenchat_inaktiv_setzen_endpoint), reicht
# fuer die aktuelle Groessenordnung (eine Handvoll Sitzungen, keine tausenden).
GRUPPENCHAT_SITZUNGEN_DIR = WERKRAUM / "codewesen" / "_gruppenchat" / "sitzungen"


def ingest_gruppenchat(sitzung: dict) -> tuple[int, int, int]:
    """Ein Chunk pro Nachricht -- gleiches Muster wie posts_aus_diskussion() bei
    Flarum: die Nachricht bleibt Grundeinheit, nie mitten im Gedanken zerteilt.
    Gibt (neu, unveraendert, zu_gross) zurueck."""
    sid = sitzung["id"]
    conn = db_connect()
    conn.autocommit = False
    neu = unveraendert = zu_gross = 0
    nachrichten = sitzung.get("nachrichten", [])
    voller_text = "\n\n".join(
        f"{n.get('sprecher', '?')}: {n.get('text', '')}" for n in nachrichten
    )
    erstellt = None
    try:
        erstellt = datetime.fromisoformat(sitzung["erstellt_am"]).replace(tzinfo=timezone.utc)
    except Exception:
        pass
    with conn.cursor() as cur:
        source_id = upsert_source_object(
            cur, external_id=f"gruppenchat:{sid}",
            quelle="gruppenchat", wesen=None,
            titel=sitzung.get("titel", "Gruppenchat"), inhalt=voller_text,
            erstellungszeit=erstellt, urheber=", ".join(sitzung.get("teilnehmer", [])),
            herkunftsort=f"codewesen/_gruppenchat/sitzungen/{sid}.json",
            ereignistyp="gruppenchat_sitzung", wahrheitsstatus="aus_gespraech_abgeleitet",
            meta={"teilnehmer": sitzung.get("teilnehmer", []),
                  "anzahl_nachrichten": len(nachrichten)},
        )
        for idx, n in enumerate(nachrichten):
            text = (n.get("text") or "").strip()
            if not text:
                continue
            sprecher = n.get("sprecher", "?")
            status = upsert_chunk_mit_embedding(
                cur, source_id, idx, f"{sprecher}", text,
                {"sprecher": sprecher, "rolle": n.get("rolle"), "ts": n.get("ts")},
            )
            neu += status == "neu_eingebettet"
            unveraendert += status == "unveraendert"
            zu_gross += status == "uebersprungen_zu_gross"
    conn.commit()
    conn.close()
    return neu, unveraendert, zu_gross


def ingest_gruppenchat_alle_inaktiven(limit=None) -> None:
    """CLI-/Nachhol-Pfad -- der eigentliche Live-Weg ruft ingest_gruppenchat() direkt
    aus codewesen_chat.py auf, sobald eine Sitzung inaktiv gesetzt wird. Diese
    Funktion existiert nur fuer manuelle Nachlaeufe (z.B. nach einem DB-Reset)."""
    if not GRUPPENCHAT_SITZUNGEN_DIR.exists():
        print("[gruppenchat] kein Sitzungsordner gefunden")
        return
    dateien = sorted(GRUPPENCHAT_SITZUNGEN_DIR.glob("*.json"))
    if limit:
        dateien = dateien[:limit]
    gesamt_neu = gesamt_unveraendert = gesamt_uebersprungen = 0
    for i, pfad in enumerate(dateien):
        try:
            sitzung = json.loads(pfad.read_text(encoding="utf-8"))
        except Exception:
            continue
        if sitzung.get("aktiv", True):
            gesamt_uebersprungen += 1
            continue  # nur inaktive Sitzungen -- aktive duerfen noch frei nachhallen
        neu, unveraendert, _ = ingest_gruppenchat(sitzung)
        gesamt_neu += neu
        gesamt_unveraendert += unveraendert
        print(f"[gruppenchat] {i+1}/{len(dateien)} {sitzung.get('titel')} "
              f"({neu} neu, {unveraendert} unveraendert)", flush=True)
    print(f"[gruppenchat] fertig: {gesamt_neu} neu eingebettet, "
          f"{gesamt_unveraendert} unveraendert, {gesamt_uebersprungen} noch aktiv uebersprungen")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("wissen", "flarum", "gruppenchat", "alles"):
        print(__doc__)
        sys.exit(1)
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    modus = sys.argv[1]
    if modus in ("wissen", "alles"):
        ingest_wissen(limit)
    if modus in ("flarum", "alles"):
        ingest_flarum(limit)
    if modus in ("gruppenchat", "alles"):
        ingest_gruppenchat_alle_inaktiven(limit)
