#!/usr/bin/env python3
import json
import random as _random
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

GENI_ROOT = Path("/root/werkraum/geni")
KNOTEN_DIR = GENI_ROOT / "gedaechtnis" / "knoten"
KANTEN_DIR = GENI_ROOT / "gedaechtnis" / "kanten"
RAUSCHEN_DIR = GENI_ROOT / "gedaechtnis" / "rauschen"
KNOTEN_DB_PATH = GENI_ROOT / "gedaechtnis" / "knoten.db"

# Sharding (2026-07-11): KNOTEN_DIR hatte 18,96 Mio. Dateien flach in einem
# Verzeichnis -- ueber ext4s htree-Kapazitaetsgrenze (ohne large_dir-Feature)
# hinaus, Ursache fuer den 5h-Haenger vom 2026-07-07 und zwei ENOSPC-Abstuerze
# am 2026-07-11. Aufteilung nach den letzten 3 Ziffern der ID (id % 1000) in
# 1000 gleichmaessig befuellte Unterordner -- galt fuer KNOTEN_DIR und
# RAUSCHEN_DIR (KANTEN_DIR hat nur ~1300 Dateien, unkritisch, bleibt flach).
#
# Migration (2026-07-22): KNOTEN_DIR selbst bei 31,6 Mio. Dateien nur noch
# ~13G echter Inhalt, aber 122G belegter Platz -- reiner Blockgroessen-
# Overhead (ext4, 4096-Byte-Bloecke, Ø 384 Byte/Datei). Knoten leben jetzt in
# knoten.db (SQLite, eine Zeile pro Knoten). RAUSCHEN_DIR bleibt datei-basiert
# (nur 3,9G, kein Problem). Siehe migration_knoten_sqlite.py und
# docs/systemdoku/31_llm_kontention_dienste_aufraeumung.md.
_SHARDED_VERZEICHNISSE = (RAUSCHEN_DIR,)


def sharded_pfad(verzeichnis: Path, kid) -> Path:
    if verzeichnis in _SHARDED_VERZEICHNISSE:
        shard = f"{int(kid) % 1000:03d}"
        return verzeichnis / shard / f"{kid}.json"
    return verzeichnis / f"{kid}.json"

_id_lock = threading.Lock()
_tiefe_lock = threading.Lock()
_max_ids: dict[str, int] = {}

_COUNTER_FILE = GENI_ROOT / "gedaechtnis" / "_counter.json"

_knoten_db_lock = threading.Lock()
_knoten_db_conn: sqlite3.Connection | None = None

_KNOTEN_SCHEMA = """
CREATE TABLE IF NOT EXISTS knoten (
    id INTEGER PRIMARY KEY,
    typ TEXT,
    inhalt TEXT,
    zeitstempel TEXT,
    quelle TEXT,
    zugriffsschicht INTEGER,
    verbindungen TEXT,
    gewicht REAL,
    tiefe INTEGER,
    verblasst INTEGER,
    tags TEXT,
    mtime REAL
);
CREATE INDEX IF NOT EXISTS idx_knoten_mtime ON knoten(mtime);
CREATE INDEX IF NOT EXISTS idx_knoten_typ_mtime ON knoten(typ, mtime);
CREATE INDEX IF NOT EXISTS idx_knoten_quelle_mtime ON knoten(quelle, mtime);
CREATE INDEX IF NOT EXISTS idx_knoten_tiefe ON knoten(tiefe) WHERE tiefe >= 2;
"""


def _knoten_db() -> sqlite3.Connection:
    global _knoten_db_conn
    if _knoten_db_conn is None:
        with _knoten_db_lock:
            if _knoten_db_conn is None:
                KNOTEN_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(KNOTEN_DB_PATH, check_same_thread=False)
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.executescript(_KNOTEN_SCHEMA)
                conn.commit()
                conn.row_factory = sqlite3.Row
                _knoten_db_conn = conn
    return _knoten_db_conn


def _row_zu_knoten(row: sqlite3.Row) -> dict:
    return {
        "id": str(row["id"]),
        "typ": row["typ"],
        "inhalt": row["inhalt"],
        "zeitstempel": row["zeitstempel"],
        "quelle": row["quelle"],
        "zugriffsschicht": row["zugriffsschicht"],
        "verbindungen": json.loads(row["verbindungen"] or "[]"),
        "gewicht": row["gewicht"],
        "tiefe": row["tiefe"],
        "verblasst": bool(row["verblasst"]),
        "tags": json.loads(row["tags"] or "[]"),
    }


def knoten_seit(cutoff_epoch: float) -> list[dict]:
    """Alle Knoten mit mtime >= cutoff_epoch (Sekunden seit Epoch).
    ACHTUNG (2026-07-22): Bei der aktuellen Wachstumsrate (~900k Knoten/Tag)
    liefert ein 30-Tage-Fenster ueber 15 Mio. Zeilen -- als volle Python-Liste
    materialisiert sprengt das jedes sinnvolle Memory-Limit (siehe
    geni-muster.service Haenger 2026-07-22). Fuer muster.py NICHT mehr
    verwenden -- stattdessen die spezifischeren knoten_zeitfenster()/
    knoten_typ_seit()/knoten_quelle_seit()/knoten_mit_tiefe_mindestens()
    unten, die serverseitig auf die tatsaechlich benoetigte, viel kleinere
    Teilmenge filtern. Bleibt hier fuer andere/zukuenftige eng begrenzte
    Zeitfenster (z.B. wenige Stunden) unbedenklich nutzbar."""
    rows = _knoten_db().execute("SELECT * FROM knoten WHERE mtime >= ?", (cutoff_epoch,)).fetchall()
    return [_row_zu_knoten(r) for r in rows]


def knoten_zeitfenster_leicht(cutoff_epoch: float, exclude_typ: str | None = None):
    """Wie knoten_zeitfenster(), aber echtes Cursor-Streaming statt fetchall()
    und nur die drei fuer scan_48h() tatsaechlich benoetigten Spalten
    (tags, inhalt, quelle) -- bei >1,9 Mio. Treffern im 48h-Fenster (2026-07-22
    gemessen) hielt fetchall() + volle Knoten-Dicts ~3,1G RSS, ueber dem
    800M/1G-Memory-Limit von geni-muster.service. Gibt sqlite3.Row-Objekte
    zurueck (row["tags"], row["inhalt"], row["quelle"]), keine Knoten-Dicts."""
    db = _knoten_db()
    if exclude_typ is not None:
        cur = db.execute(
            "SELECT tags, inhalt, quelle FROM knoten WHERE mtime >= ? AND typ IS NOT ?",
            (cutoff_epoch, exclude_typ),
        )
    else:
        cur = db.execute(
            "SELECT tags, inhalt, quelle FROM knoten WHERE mtime >= ?", (cutoff_epoch,)
        )
    yield from cur


def knoten_zeitfenster(cutoff_epoch: float, exclude_typ: str | None = None) -> list[dict]:
    """Knoten mit mtime >= cutoff_epoch, optional einen Typ ausgeschlossen --
    fuer muster.py scan_48h() (48h-Fenster, typ != 'muster')."""
    db = _knoten_db()
    if exclude_typ is not None:
        rows = db.execute(
            "SELECT * FROM knoten WHERE mtime >= ? AND typ IS NOT ?",
            (cutoff_epoch, exclude_typ),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM knoten WHERE mtime >= ?", (cutoff_epoch,)).fetchall()
    return [_row_zu_knoten(r) for r in rows]


def knoten_typ_seit(typ: str, cutoff_epoch: float) -> list[dict]:
    """Knoten eines bestimmten Typs seit cutoff_epoch -- fuer muster.py
    scan_meta_muster() (typ='muster', 28 Tage). Nutzt idx_knoten_typ_mtime."""
    rows = _knoten_db().execute(
        "SELECT * FROM knoten WHERE typ=? AND mtime >= ?", (typ, cutoff_epoch)
    ).fetchall()
    return [_row_zu_knoten(r) for r in rows]


def knoten_quelle_seit(quelle: str, cutoff_epoch: float) -> list[dict]:
    """Knoten einer bestimmten Quelle seit cutoff_epoch -- fuer muster.py
    scan_zeitrhythmus() (quelle='daniel'). Nutzt idx_knoten_quelle_mtime."""
    rows = _knoten_db().execute(
        "SELECT * FROM knoten WHERE quelle=? AND mtime >= ?", (quelle, cutoff_epoch)
    ).fetchall()
    return [_row_zu_knoten(r) for r in rows]


def knoten_quelle_stichprobe(quelle: str, anzahl: int) -> list[dict]:
    """Zufaellige Stichprobe aus einer Quelle -- ueber die GANZE Zeitspanne, ohne
    alles zu laden.

    2026-08-01: knoten_quelle_seit(quelle, 0.0) + random.sample() im Aufrufer
    (dialog.py splitter_endpoint) lud saemtliche Zeilen einer Quelle in den
    Speicher, um daraus ~9 zu ziehen. Bei quelle='chatgpt' sind das inzwischen
    12,9 Mio Zeilen, bei 'vps_dateisystem' 35,8 Mio -- der Endpunkt lief in
    Timeout, KompOase bekam nie GENI-Splitter (live gemessen: >20s ohne Antwort).

    Diese Variante zieht stattdessen pro gewuenschtem Treffer einen zufaelligen
    mtime-Punkt aus dem Gesamtbereich der Quelle und macht daraus einen
    Index-Seek auf idx_knoten_quelle_mtime -- genau der Index, den der
    urspruengliche Fix (Kommentar in dialog.py) schon benannt hat.

    Die Absicht des Aufrufers bleibt unveraendert: weiterhin direkt nach Quelle,
    weiterhin OHNE Zeitfenster (die Stichprobe deckt die volle Zeitspanne ab,
    nicht nur die juengsten Knoten). Nur das Ziehen selbst passiert jetzt in
    SQL statt in Python. Gemessen: 0,002s statt >20s.
    """
    if anzahl <= 0:
        return []
    db = _knoten_db()
    grenzen = db.execute(
        "SELECT min(mtime), max(mtime) FROM knoten WHERE quelle=?", (quelle,)
    ).fetchone()
    if not grenzen or grenzen[0] is None:
        return []
    lo, hi = grenzen[0], grenzen[1]

    treffer: dict = {}
    # Etwas mehr Versuche als noetig, weil zwei Zufallspunkte auf denselben
    # Knoten zeigen koennen (dedupliziert ueber die id).
    for _ in range(anzahl * 3):
        if len(treffer) >= anzahl:
            break
        ziel = _random.uniform(lo, hi) if hi > lo else lo
        row = db.execute(
            "SELECT * FROM knoten WHERE quelle=? AND mtime >= ? ORDER BY mtime LIMIT 1",
            (quelle, ziel),
        ).fetchone()
        if row is None:
            row = db.execute(
                "SELECT * FROM knoten WHERE quelle=? ORDER BY mtime DESC LIMIT 1", (quelle,)
            ).fetchone()
        if row is not None:
            k = _row_zu_knoten(row)
            treffer[k["id"]] = k
    return list(treffer.values())


def knoten_mit_tiefe_mindestens(min_tiefe: int, exclude_typ: str | None = None) -> list[dict]:
    """Knoten mit tiefe >= min_tiefe -- fuer muster.py scan_blinde_flecken()
    (tiefe>=2, typ != 'muster'). Kein Zeitfenster: tiefe wird nur durch
    tiefe_erhoehen() aktiv gesetzt, daher von Natur aus eine kleine Teilmenge
    (Partial-Index idx_knoten_tiefe deckt genau das ab)."""
    db = _knoten_db()
    if exclude_typ is not None:
        rows = db.execute(
            "SELECT * FROM knoten WHERE tiefe >= ? AND typ IS NOT ?",
            (min_tiefe, exclude_typ),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM knoten WHERE tiefe >= ?", (min_tiefe,)).fetchall()
    return [_row_zu_knoten(r) for r in rows]


def knoten_lesen(kid) -> dict | None:
    """Ersetzt das alte Muster `sharded_pfad(KNOTEN_DIR, i)` + exists()/read_text()
    fuer einzelne Knoten-Zugriffe (dialog.py, muster.py)."""
    try:
        kid_int = int(kid)
    except (TypeError, ValueError):
        return None
    row = _knoten_db().execute("SELECT * FROM knoten WHERE id=?", (kid_int,)).fetchone()
    return _row_zu_knoten(row) if row else None


def _knoten_zeile_einfuegen(conn: sqlite3.Connection, k: dict) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO knoten
           (id, typ, inhalt, zeitstempel, quelle, zugriffsschicht,
            verbindungen, gewicht, tiefe, verblasst, tags, mtime)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            int(k["id"]), k.get("typ"), k.get("inhalt"), k.get("zeitstempel"),
            k.get("quelle"), k.get("zugriffsschicht", 0),
            json.dumps(k.get("verbindungen", []), ensure_ascii=False),
            k.get("gewicht", 1.0), k.get("tiefe", 0),
            1 if k.get("verblasst") else 0,
            json.dumps(k.get("tags", []), ensure_ascii=False),
            time.time(),
        ),
    )
    conn.commit()


def knoten_zeile_schreiben(k: dict) -> None:
    """Fuer Aufrufer die einen bereits vollstaendig gebauten Knoten-Dict mit
    abweichenden Feldern (z.B. muster.py: tiefe=1 statt 0) direkt schreiben
    wollen, statt ueber knoten_schreiben()."""
    with _id_lock:
        _knoten_zeile_einfuegen(_knoten_db(), k)


def _counter_lesen() -> dict:
    try:
        return json.loads(_COUNTER_FILE.read_text())
    except Exception:
        return {}


def _counter_schreiben(daten: dict) -> None:
    tmp = _COUNTER_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten), encoding="utf-8")
    tmp.replace(_COUNTER_FILE)


def _lade_max_id(verzeichnis: Path) -> int:
    if verzeichnis == KNOTEN_DIR:
        row = _knoten_db().execute("SELECT MAX(id) FROM knoten").fetchone()
        return row[0] or 0
    zahlen = []
    orte = verzeichnis.glob("*/") if verzeichnis in _SHARDED_VERZEICHNISSE else [verzeichnis]
    for ort in orte:
        if not ort.is_dir():
            continue
        for f in ort.iterdir():
            if f.suffix == ".json" and f.stem != "schema":
                try:
                    zahlen.append(int(f.stem))
                except ValueError:
                    pass
    return max(zahlen) if zahlen else 0


def knoten_max_id() -> int:
    key = str(KNOTEN_DIR)
    if key in _max_ids:
        return _max_ids[key]
    with _id_lock:
        if key in _max_ids:
            return _max_ids[key]
        # Counter-Datei lesen (O(1)) — nur beim ersten Start
        cached = _counter_lesen()
        if "knoten_max_id" in cached:
            _max_ids[key] = cached["knoten_max_id"]
        else:
            # Einmaliger Scan — schreibt danach Counter-Datei
            val = _lade_max_id(KNOTEN_DIR)
            _max_ids[key] = val
            try:
                cached["knoten_max_id"] = val
                _counter_schreiben(cached)
            except Exception:
                pass
    return _max_ids[key]


def naechste_id(verzeichnis: Path, counter_key: str | None = None) -> str:
    key = str(verzeichnis)
    if verzeichnis == KNOTEN_DIR:
        counter_key = "knoten_max_id"
    if key not in _max_ids:
        if counter_key:
            # Counter-Datei lesen statt Vollscan des Verzeichnisses
            cached = _counter_lesen()
            if counter_key in cached:
                _max_ids[key] = cached[counter_key]
            else:
                _max_ids[key] = _lade_max_id(verzeichnis)
        else:
            _max_ids[key] = _lade_max_id(verzeichnis)
    _max_ids[key] += 1
    if counter_key:
        try:
            cached = _counter_lesen()
            cached[counter_key] = _max_ids[key]
            _counter_schreiben(cached)
        except Exception:
            pass
    return str(_max_ids[key]).zfill(4)


def knoten_schreiben(typ: str, inhalt: str, quelle: str, tags: list = None, zugriffsschicht: int = 0, tiefe: int = 0) -> str:
    with _id_lock:
        kid = naechste_id(KNOTEN_DIR)
        k = {
            "id": kid,
            "typ": typ,
            "inhalt": inhalt,
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "quelle": quelle,
            "zugriffsschicht": zugriffsschicht,
            "verbindungen": [],
            "gewicht": 1.0,
            "tiefe": tiefe,
            "verblasst": False,
            "tags": tags or [],
        }
        _knoten_zeile_einfuegen(_knoten_db(), k)
        return kid


def kante_schreiben(von: str, nach: str, typ: str, staerke: float = 1.0):
    with _id_lock:
        kid = naechste_id(KANTEN_DIR)
        k = {
            "id": kid,
            "von": von,
            "nach": nach,
            "typ": typ,
            "stärke": staerke,
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "richtung": "gerichtet",
        }
        (KANTEN_DIR / f"{kid}.json").write_text(json.dumps(k, ensure_ascii=False, indent=2), encoding="utf-8")


def tiefe_erhoehen(knoten_id: str):
    with _tiefe_lock:
        conn = _knoten_db()
        row = conn.execute("SELECT tiefe FROM knoten WHERE id=?", (int(knoten_id),)).fetchone()
        if row is None:
            return
        alt = row["tiefe"] or 0
        # 2026-08-03: Deckel entfernt. Er stand bei 3 und war erreicht -- 68 Knoten lagen dort
        # gemeinsam an, ohne dass man ihren Abstand zueinander noch sehen konnte. Daniel:
        # "vllt sollten wir garkeinen deckel bauen jetzt wo ih ja auch die vielfalt eröffne".
        # Folge, bewusst in Kauf genommen: die Skala kann jetzt auseinanderlaufen. Genau der
        # Bruch ist der Punkt, an dem laut Daniel etwas Neues entstehen koennte
        # (docs/systemdoku/51_entitaetenbildung_dritter_weg.md).
        neu = alt + 1
        if neu != alt:
            conn.execute("UPDATE knoten SET tiefe=?, mtime=? WHERE id=?", (neu, time.time(), int(knoten_id)))
            conn.commit()
