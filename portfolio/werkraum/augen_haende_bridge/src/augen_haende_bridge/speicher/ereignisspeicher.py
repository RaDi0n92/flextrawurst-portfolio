"""Ereignisspeicher in PostgreSQL (G13): was in der Bridge geschieht, bleibt für immer und ist abfragbar.

Eigene Datenbank (Adresse in `BRIDGE_DB_URL`), nicht `flextrawurst`. Die Tabellen sind append-only (Trigger in `schema.sql`).
Einlesen aus Ereignisprotokoll und Praxis-Ledger ist wiederholbar: `(quelle, extern_id)` ist eindeutig, ein zweiter Lauf schreibt nichts doppelt.
Wartezustand, Position eines Laufs und Fehlversuche sind Sichten über denselben Strom, kein zweiter Speicher.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")
MAX_TEXT = 4000


HEIM = Path(os.environ.get("BRIDGE_SPEICHER_HEIM", "/root/bridge_speicher"))


def adresse() -> str:
    """`BRIDGE_DB_URL`, sonst die Adresse der eigenen Datenbank in `<HEIM>/db_url` (leer, wenn es keine gibt)."""
    if os.environ.get("BRIDGE_DB_URL"):
        return os.environ["BRIDGE_DB_URL"]
    try:
        return (HEIM / "db_url").read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _psycopg():
    try:
        import psycopg
    except ImportError:  # der Starter läuft im System-Python; psycopg liegt in der venv des Speichers
        import sys

        for ordner in sorted((HEIM / "venv" / "lib").glob("python3.*/site-packages")):
            if str(ordner) not in sys.path:
                sys.path.append(str(ordner))
        import psycopg
    from psycopg.rows import dict_row

    return psycopg, dict_row


def datenbank_starten() -> bool:
    """Startet die eigene Datenbank (`<HEIM>/start.sh`), falls sie nicht läuft; True, wenn das Skript ohne Fehler zurückkam."""
    import subprocess

    try:
        return subprocess.run(["sh", str(HEIM / "start.sh")], capture_output=True, timeout=60).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class Ereignisspeicher:
    def __init__(self, dsn: str | None = None, jetzt_ms=lambda: int(time.time() * 1000)):
        self.dsn = dsn or adresse()
        if not self.dsn:
            raise ValueError("keine Datenbankadresse (BRIDGE_DB_URL)")
        self._jetzt = jetzt_ms
        psycopg, dict_row = _psycopg()
        try:
            self._verbindung = psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row)
        except psycopg.OperationalError:
            if not (dsn is None and not os.environ.get("BRIDGE_DB_URL") and datenbank_starten()):
                raise
            self._verbindung = psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row)

    def schliessen(self) -> None:
        self._verbindung.close()

    def schema_anlegen(self) -> None:
        self._verbindung.execute(SCHEMA.read_text(encoding="utf-8"))

    # ---- Schreiben ---------------------------------------------------------------------------------------------------
    def schreiben(self, quelle: str, art: str, *, agent: str = "", lauf: str = "", knoten: str = "", versuch: int = 0, grund: str = "",
                  text: str = "", daten: dict | None = None, extern_id: str | None = None, zeit_ms: int | None = None) -> int | None:
        """Hängt ein Ereignis an; gibt die Id zurück, bei schon bekannter `extern_id` None."""
        zeile = self._verbindung.execute(
            "INSERT INTO ereignis (zeit_ms, quelle, extern_id, art, agent, lauf, knoten, versuch, grund, text, daten) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT DO NOTHING RETURNING id",
            (zeit_ms if zeit_ms is not None else self._jetzt(), quelle, extern_id, art, agent, lauf, knoten, versuch, grund,
             str(text)[:MAX_TEXT], json.dumps(daten or {}, ensure_ascii=False, default=str))).fetchone()
        return zeile["id"] if zeile else None

    def einlesen_protokoll(self, datei: Path) -> tuple[int, int]:
        """`ereignisse.jsonl` des Starters. Gibt (neu, schon_bekannt) zurück; kaputte Zeilen zählen nirgends mit und stehen nicht im Ergebnis."""
        neu = bekannt = 0
        with open(datei, encoding="utf-8") as f:
            for zeile in f:
                try:
                    e = json.loads(zeile)
                    i = self.schreiben("protokoll", str(e["art"]), agent=str(e.get("agent", "")), text=str(e.get("text", "")),
                                       grund=str((e.get("daten") or {}).get("reason", "")), daten={**(e.get("daten") or {}), "ziel": e.get("ziel", "")}, zeit_ms=int(e["zeit_ms"]),
                                       extern_id=f"{e['id']}@{e['zeit_ms']}")
                except (ValueError, KeyError, TypeError):
                    continue
                neu, bekannt = (neu + 1, bekannt) if i else (neu, bekannt + 1)
        return neu, bekannt

    def einlesen_ledger(self, datei: Path) -> tuple[int, int]:
        """Ein Ledger des Praxis-Harness (`<lauf>.jsonl`): jede Zeile ein Ereignis des Laufs."""
        neu = bekannt = 0
        with open(datei, encoding="utf-8") as f:
            for zeile in f:
                try:
                    i = self.schreibe_ledgerzeile(json.loads(zeile))
                except (ValueError, KeyError, TypeError):
                    continue
                neu, bekannt = (neu + 1, bekannt) if i else (neu, bekannt + 1)
        return neu, bekannt

    def schreibe_ledgerzeile(self, e: dict) -> int | None:
        """Eine Ledger-Zeile als Ereignis; die Kennung folgt aus dem Inhalt, dieselbe Zeile steht also nie zweimal da."""
        kennung = hashlib.sha1(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        return self.schreiben("ledger", str(e["status"]), agent=str(e.get("von", "")), lauf=str(e["lauf_id"]), knoten=f"s{e.get('nr', 0)}",
                              text=str(e.get("text", "")), daten={k: v for k, v in e.items() if k not in ("text", "status", "von", "lauf_id", "zeit_ms")},
                              zeit_ms=int(e["zeit_ms"]), extern_id=f"{e['lauf_id']}:{kennung}")

    # ---- Lesen -------------------------------------------------------------------------------------------------------
    def zaehlen(self, quelle: str | None = None) -> int:
        if quelle:
            return self._verbindung.execute("SELECT count(*) AS n FROM ereignis WHERE quelle=%s", (quelle,)).fetchone()["n"]
        return self._verbindung.execute("SELECT count(*) AS n FROM ereignis").fetchone()["n"]

    def lauf(self, lauf: str, grenze: int = 200) -> list[dict]:
        return self._verbindung.execute("SELECT * FROM ereignis WHERE lauf=%s ORDER BY zeit_ms, id LIMIT %s", (lauf, grenze)).fetchall()

    def position(self, lauf: str) -> dict | None:
        return self._verbindung.execute("SELECT * FROM lauf_position WHERE lauf=%s", (lauf,)).fetchone()

    def wartezustand(self) -> list[dict]:
        return self._verbindung.execute("SELECT * FROM wartezustand ORDER BY seit_ms").fetchall()

    def wartet_agent(self, agent: str) -> dict | None:
        return self._verbindung.execute("SELECT * FROM wartezustand WHERE agent=%s", (agent,)).fetchone()

    def fehlversuche(self, lauf: str, knoten: str) -> int:
        z = self._verbindung.execute("SELECT anzahl FROM fehlversuche WHERE lauf=%s AND knoten=%s", (lauf, knoten)).fetchone()
        return int(z["anzahl"]) if z else 0

    def abfrage(self, sql: str, parameter: tuple = ()) -> list[dict]:
        return self._verbindung.execute(sql, parameter).fetchall()
