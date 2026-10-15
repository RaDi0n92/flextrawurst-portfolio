#!/usr/bin/env python3
"""
Migration knoten/ (31,6 Mio. Einzeldateien, ~122G Blockgroessen-Overhead auf
ext4 bei Ø 384 echten Bytes/Datei) -> knoten.db (SQLite, eine Zeile pro Knoten).

Kein Knoten wird geloescht -- alte Dateien bleiben bis zur expliziten Freigabe
unangetastet, dieses Skript liest nur.

Resumable/checkpointed nach demselben Muster wie muster.py lade_alle_knoten()
(siehe docs/systemdoku/31_llm_kontention_dienste_aufraeumung.md) -- bei
31,6 Mio. Dateien darf ein Abbruch (SIGTERM/OOM) nicht wieder bei Null anfangen.

Aufruf:
  python3 migration_knoten_sqlite.py --shard 092        # ein Shard (Test)
  python3 migration_knoten_sqlite.py --alle              # alle 1001 Shards
  python3 migration_knoten_sqlite.py --alle --weiter      # nach Abbruch fortsetzen
"""
import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

GENI_ROOT = Path("/root/werkraum/geni")
KNOTEN_DIR = GENI_ROOT / "gedaechtnis" / "knoten"
DB_PATH = GENI_ROOT / "gedaechtnis" / "knoten.db"
FORTSCHRITT_DATEI = GENI_ROOT / "gedaechtnis" / "_migration_fortschritt.json"

SCHEMA = """
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
"""

CHECKPOINT_INTERVALL_SEK = 20


def db_verbinden() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def fortschritt_laden() -> set:
    try:
        return set(json.loads(FORTSCHRITT_DATEI.read_text()).get("erledigte_shards", []))
    except Exception:
        return set()


def fortschritt_speichern(erledigt: set) -> None:
    tmp = FORTSCHRITT_DATEI.with_suffix(".tmp")
    tmp.write_text(json.dumps({"erledigte_shards": sorted(erledigt)}), encoding="utf-8")
    tmp.replace(FORTSCHRITT_DATEI)


def zeile_aus_json(pfad: Path) -> tuple | None:
    try:
        k = json.loads(pfad.read_text(encoding="utf-8"))
        mtime = pfad.stat().st_mtime
    except Exception as e:
        print(f"  WARNUNG: {pfad} konnte nicht gelesen werden: {e}", file=sys.stderr)
        return None
    try:
        kid = int(k["id"])
    except Exception:
        print(f"  WARNUNG: {pfad} hat keine gueltige numerische id: {k.get('id')!r}", file=sys.stderr)
        return None
    return (
        kid,
        k.get("typ"),
        k.get("inhalt"),
        k.get("zeitstempel"),
        k.get("quelle"),
        k.get("zugriffsschicht", 0),
        json.dumps(k.get("verbindungen", []), ensure_ascii=False),
        k.get("gewicht", 1.0),
        k.get("tiefe", 0),
        1 if k.get("verblasst") else 0,
        json.dumps(k.get("tags", []), ensure_ascii=False),
        mtime,
    )


def shard_migrieren(conn: sqlite3.Connection, shard_pfad: Path) -> tuple:
    zeilen = []
    fehler = 0
    with os.scandir(shard_pfad) as it:
        for entry in it:
            if not entry.name.endswith(".json") or entry.name == "schema.json":
                continue
            zeile = zeile_aus_json(Path(entry.path))
            if zeile is None:
                fehler += 1
                continue
            zeilen.append(zeile)
    if zeilen:
        conn.executemany(
            """INSERT OR REPLACE INTO knoten
               (id, typ, inhalt, zeitstempel, quelle, zugriffsschicht,
                verbindungen, gewicht, tiefe, verblasst, tags, mtime)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            zeilen,
        )
        conn.commit()
    return len(zeilen), fehler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", help="Einzelnen Shard migrieren (z.B. 092), fuer Testlauf")
    ap.add_argument("--alle", action="store_true", help="Alle Shards migrieren")
    ap.add_argument("--weiter", action="store_true", help="Bereits erledigte Shards ueberspringen")
    ap.add_argument("--catchup-seit", type=float,
                     help="Nur Dateien mit mtime >= diesem Unix-Timestamp migrieren "
                          "(schneller Nachzuegler-Pass fuer Knoten die waehrend der "
                          "Vollmigration von den noch alten Services neu geschrieben wurden)")
    args = ap.parse_args()

    if not args.shard and not args.alle and args.catchup_seit is None:
        ap.error("--shard <name>, --alle oder --catchup-seit <timestamp> angeben")

    conn = db_verbinden()

    if args.catchup_seit is not None:
        # find(1) ist bei 31,6 Mio. Dateien um Groessenordnungen schneller als
        # Python-os.scandir+stat pro Datei -- hier reicht das, weil wir nur die
        # (vermutlich wenigen hundert/tausend) waehrend der Migration neu
        # geschriebenen Dateien brauchen, nicht den kompletten Bestand.
        import subprocess
        t0 = time.monotonic()
        proc = subprocess.run(
            ["find", str(KNOTEN_DIR), "-name", "*.json",
             "-newermt", f"@{args.catchup_seit}"],
            capture_output=True, text=True, check=True,
        )
        pfade = [Path(p) for p in proc.stdout.splitlines() if p.strip()]
        zeilen = []
        fehler = 0
        for p in pfade:
            if p.name == "schema.json":
                continue
            z = zeile_aus_json(p)
            if z is None:
                fehler += 1
            else:
                zeilen.append(z)
        if zeilen:
            conn.executemany(
                """INSERT OR REPLACE INTO knoten
                   (id, typ, inhalt, zeitstempel, quelle, zugriffsschicht,
                    verbindungen, gewicht, tiefe, verblasst, tags, mtime)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                zeilen,
            )
            conn.commit()
        dauer = time.monotonic() - t0
        print(f"Catch-up seit {args.catchup_seit}: {len(pfade)} Dateien gefunden, "
              f"{len(zeilen)} migriert, {fehler} Fehler, {dauer:.2f}s")
        conn.close()
        return

    if args.shard:
        shard_pfad = KNOTEN_DIR / args.shard
        if not shard_pfad.is_dir():
            print(f"Shard-Ordner nicht gefunden: {shard_pfad}", file=sys.stderr)
            sys.exit(1)
        t0 = time.monotonic()
        n, fehler = shard_migrieren(conn, shard_pfad)
        dauer = time.monotonic() - t0
        print(f"Shard {args.shard}: {n} Knoten migriert, {fehler} Fehler, {dauer:.2f}s")
        conn.close()
        return

    # --alle
    erledigt = fortschritt_laden() if args.weiter else set()
    with os.scandir(KNOTEN_DIR) as it:
        alle_shards = sorted(s.name for s in it if s.is_dir())

    gesamt_neu = 0
    gesamt_fehler = 0
    letzter_checkpoint = time.monotonic()
    t_start = time.monotonic()

    for i, shard_name in enumerate(alle_shards, 1):
        if shard_name in erledigt:
            continue
        n, fehler = shard_migrieren(conn, KNOTEN_DIR / shard_name)
        gesamt_neu += n
        gesamt_fehler += fehler
        erledigt.add(shard_name)

        if time.monotonic() - letzter_checkpoint >= CHECKPOINT_INTERVALL_SEK:
            fortschritt_speichern(erledigt)
            letzter_checkpoint = time.monotonic()
            vergangen = time.monotonic() - t_start
            print(f"[{i}/{len(alle_shards)}] Shards, {gesamt_neu} Knoten, "
                  f"{gesamt_fehler} Fehler, {vergangen:.0f}s vergangen", flush=True)

    fortschritt_speichern(erledigt)
    conn.close()
    print(f"FERTIG: {len(erledigt)}/{len(alle_shards)} Shards, "
          f"{gesamt_neu} Knoten migriert, {gesamt_fehler} Fehler.")


if __name__ == "__main__":
    main()
