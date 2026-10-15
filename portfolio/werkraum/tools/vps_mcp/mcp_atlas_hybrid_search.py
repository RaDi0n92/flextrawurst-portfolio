#!/usr/bin/env python3
"""
Hybrid-Suche (Volltext + Vektor) fuer den Gesamtatlas-Eingang, angelehnt an das
qmd-Konzept (github.com/tobi/qmd, genutzt von github.com/ZeroDot1/LLMWikiNG als
Such-Backend): BM25-Volltextsuche und semantische Vektorsuche parallel ausfuehren,
per Reciprocal Rank Fusion (RRF) kombinieren. Bewusst OHNE Query-Expansion und
LLM-Reranking -- das braeuchte eine eigene Toolchain (node-llama-cpp, ein
Reranker-Modell), RRF allein liefert schon einen echten Hybrid-Effekt.

BM25-Seite: nutzt den bereits bestehenden BEGRIFFSINDEX.sqlite-FTS5-Index (siehe
mcp_atlas.py::find()) -- deckt den GESAMTEN, bereits indizierten Gesamtatlas ab.

Vektor-Seite: bewusst NUR ueber den neuen AI_STROEME/-Bestand (OKF-Dateien aus
atlas.stream_file_write) -- eine Vollindizierung der ~120.000 Bestandsdokumente
haette Stunden CPU-Zeit gekostet. Waechst organisch mit, sobald Stroeme ueber OKF
schreiben. Gleiche Embedding-Infrastruktur wie _claude/tools/semantische_suche.py
(chromadb, lokale ONNX-MiniLM-Einbettung, kein Drittanbieter-Hook, keine neue
Abhaengigkeit -- chromadb war schon im System installiert).
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

import chromadb

ATLAS_ROOT = Path("/root/werkraum/_gpt/gesamtatlas")
CONCEPT_DB = ATLAS_ROOT / "BEGRIFFSINDEX.sqlite"
VEKTOR_INDEX_PFAD = ATLAS_ROOT / "vektorindex"
VEKTOR_COLLECTION_NAME = "gesamtatlas_ai_stroeme"
MANUAL_READ_COLLECTION_NAME = "portfolio_manual_reads"

_chroma_client = None
_chroma_collection = None
_manual_read_collection = None


def _hole_collection():
    global _chroma_client, _chroma_collection
    if _chroma_collection is None:
        VEKTOR_INDEX_PFAD.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(VEKTOR_INDEX_PFAD))
        _chroma_collection = _chroma_client.get_or_create_collection(VEKTOR_COLLECTION_NAME)
    return _chroma_collection


def _hole_manual_read_collection():
    global _chroma_client, _manual_read_collection
    if _manual_read_collection is None:
        VEKTOR_INDEX_PFAD.mkdir(parents=True, exist_ok=True)
        if _chroma_client is None:
            _chroma_client = chromadb.PersistentClient(path=str(VEKTOR_INDEX_PFAD))
        _manual_read_collection = _chroma_client.get_or_create_collection(MANUAL_READ_COLLECTION_NAME)
    return _manual_read_collection


def manual_read_index_aktualisieren(*, pfad: str, text: str, metadaten: dict[str, Any] | None = None) -> None:
    """Indiziert ausschliesslich Material, das bereits durch einen echten manuellen
    Lesezugriff gelaufen ist. Kein Crawler, kein Batch, kein Hintergrundlauf. Das
    RAG lernt also nur dort semantisch dazu, wo wir wirklich gewesen sind."""
    if not pfad or not text:
        return
    try:
        coll = _hole_manual_read_collection()
        meta = dict(metadaten or {})
        meta.setdefault("titel", Path(pfad).name)
        meta["manual_read"] = True
        coll.upsert(ids=[pfad], documents=[text[:12000]], metadatas=[meta])
    except Exception:
        # Semantische Erinnerung ist Zusatzfunktion; ein Fehler darf niemals den
        # echten Lesevorgang oder den MCP-Werkzeugkoerper blockieren.
        pass


def vektor_index_aktualisieren(*, pfad: str, text: str, metadaten: dict[str, Any]) -> None:
    """Fuegt/aktualisiert ein Dokument im Vektor-Index. Wird von
    atlas.stream_file_write nach jedem erfolgreichen Schreiben aufgerufen -- kein
    separater Batch-Lauf noetig, der Index waechst mit jeder neuen OKF-Datei."""
    try:
        coll = _hole_collection()
        coll.upsert(ids=[pfad], documents=[text[:8000]], metadatas=[metadaten])
    except Exception:
        # Vektor-Indizierung ist eine Zusatzfunktion -- ein Fehler dabei darf das
        # eigentliche Schreiben der Datei (atlas.stream_file_write) nicht verhindern.
        pass


def _bm25_suche(query: str, limit: int) -> list[dict[str, Any]]:
    if not CONCEPT_DB.exists():
        return []
    terms = [term for term in re.findall(r"[\wäöüßÄÖÜ-]+", query) if len(term) >= 2]
    match = " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms[:12])
    if not match:
        return []
    conn = sqlite3.connect(CONCEPT_DB)
    conn.row_factory = sqlite3.Row
    ergebnis: list[dict[str, Any]] = []
    try:
        table_sql = conn.execute("SELECT sql FROM sqlite_master WHERE name='documents'").fetchone()
        if not (table_sql and "VIRTUAL TABLE" in str(table_sql[0]).upper()):
            return []
        for row in conn.execute(
            "SELECT path, title, snippet(documents,3,'[',']',' … ',24) AS snippet, "
            "bm25(documents) AS rang FROM documents WHERE documents MATCH ? ORDER BY rang LIMIT ?",
            (match, limit),
        ):
            ergebnis.append({"pfad": row["path"], "titel": row["title"], "ausschnitt": row["snippet"], "quelle": "bm25"})
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()
    return ergebnis


def _vektor_suche(query: str, limit: int) -> list[dict[str, Any]]:
    try:
        coll = _hole_collection()
        if coll.count() == 0:
            return []
        treffer = coll.query(query_texts=[query], n_results=min(limit, coll.count()))
    except Exception:
        return []
    ergebnis: list[dict[str, Any]] = []
    ids = (treffer.get("ids") or [[]])[0]
    dokumente = (treffer.get("documents") or [[]])[0]
    metadaten = (treffer.get("metadatas") or [[]])[0]
    for pfad, doc, meta in zip(ids, dokumente, metadaten):
        ergebnis.append({
            "pfad": pfad,
            "titel": (meta or {}).get("titel") or Path(pfad).name,
            "ausschnitt": (doc or "")[:200],
            "quelle": "vektor",
        })
    return ergebnis


def _manual_vektor_suche(query: str, limit: int) -> list[dict[str, Any]]:
    """Semantische Suche nur ueber Quellen, die tatsaechlich manuell gelesen wurden."""
    try:
        coll = _hole_manual_read_collection()
        if coll.count() == 0:
            return []
        treffer = coll.query(query_texts=[query], n_results=min(limit, coll.count()))
    except Exception:
        return []
    ergebnis: list[dict[str, Any]] = []
    ids = (treffer.get("ids") or [[]])[0]
    dokumente = (treffer.get("documents") or [[]])[0]
    metadaten = (treffer.get("metadatas") or [[]])[0]
    for chunk_id, doc, meta in zip(ids, dokumente, metadaten):
        meta = meta or {}
        source_path = meta.get("source_path") or chunk_id
        ergebnis.append({
            "pfad": source_path,
            "chunk_id": chunk_id,
            "titel": meta.get("titel") or Path(source_path).name,
            "ausschnitt": (doc or "")[:240],
            "quelle": "manual_vektor",
            "manual_read": True,
            # Alte Chunks ohne expliziten Zustand werden konservativ nur als Teilread
            # behandelt; erst DB-Provenienz oder neue Metadaten duerfen "read" behaupten.
            "read_state": meta.get("read_state") or "read_partial",
            "read_range": meta.get("read_range"),
        })
    return ergebnis


def hybrid_suche(query: str, limit: int = 10, rrf_k: int = 60) -> dict[str, Any]:
    """Kombiniert BM25- und Vektor-Trefferlisten per Reciprocal Rank Fusion
    (score = summe 1/(rrf_k + rang), rrf_k=60 wie bei qmd). Kein LLM-Reranking,
    keine Query-Expansion -- bewusst einfacher Kern statt Nachbau der vollen
    qmd-Pipeline."""
    if not query or not query.strip():
        return {"ok": False, "error": "query fehlt"}
    bm25_treffer = _bm25_suche(query, limit * 2)
    vektor_treffer = _vektor_suche(query, limit * 2)
    manual_treffer = _manual_vektor_suche(query, limit * 2)

    rrf_scores: dict[str, float] = {}
    quellen_info: dict[str, dict[str, Any]] = {}
    for rang, eintrag in enumerate(bm25_treffer, start=1):
        pfad = eintrag["pfad"]
        rrf_scores[pfad] = rrf_scores.get(pfad, 0.0) + 1.0 / (rrf_k + rang)
        quellen_info.setdefault(pfad, eintrag)
        quellen_info[pfad].setdefault("bm25_rang", rang)
    for rang, eintrag in enumerate(vektor_treffer, start=1):
        pfad = eintrag["pfad"]
        rrf_scores[pfad] = rrf_scores.get(pfad, 0.0) + 1.0 / (rrf_k + rang)
        if pfad not in quellen_info:
            quellen_info[pfad] = eintrag
        quellen_info[pfad].setdefault("vektor_rang", rang)
    seen_manual_paths: set[str] = set()
    for rang, eintrag in enumerate(manual_treffer, start=1):
        pfad = eintrag["pfad"]
        if pfad in seen_manual_paths:
            continue
        seen_manual_paths.add(pfad)
        # Mehrere gelesene Chunks derselben Datei duerfen deren Rang nicht mehrfach aufblasen.
        # Manuell gelesen bedeutet Erinnerung, nicht Autoritaetsbonus.
        rrf_scores[pfad] = rrf_scores.get(pfad, 0.0) + 1.0 / (rrf_k + rang)
        if pfad not in quellen_info:
            quellen_info[pfad] = eintrag
        else:
            quellen_info[pfad]["manual_read"] = True
            quellen_info[pfad].setdefault("read_range", eintrag.get("read_range"))
        quellen_info[pfad].setdefault("manual_vektor_rang", rang)

    sortiert = sorted(rrf_scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    ergebnisse = []
    for pfad, score in sortiert:
        eintrag = dict(quellen_info[pfad])
        eintrag["rrf_score"] = round(score, 6)
        eintrag["gefunden_ueber"] = sorted({
            "bm25" if "bm25_rang" in eintrag else None,
            "vektor" if "vektor_rang" in eintrag else None,
            "manual_vektor" if "manual_vektor_rang" in eintrag else None,
        } - {None})
        ergebnisse.append(eintrag)

    return {
        "ok": True,
        "query": query,
        "bm25_treffer_gesamt": len(bm25_treffer),
        "vektor_treffer_gesamt": len(vektor_treffer),
        "manual_vektor_treffer_gesamt": len(manual_treffer),
        "ergebnisse": ergebnisse,
        "einschraenkung": (
            "BM25 deckt den indizierten Gesamtatlas ab; der alte Vektorindex deckt AI_STROEME ab; "
            "portfolio_manual_reads waechst ausschliesslich aus echten manuellen Lesezugriffen. "
            "Retrieval ist Wegweiser, niemals Beweis, Vollstaendigkeitsgarantie oder Ersatz fuer Originallekture."
        ),
    }
