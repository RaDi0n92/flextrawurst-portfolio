from __future__ import annotations

"""Quellengebundener Einzug der acht Flextrawurst-Urbewohner in den Gesamtatlas.

OMAPI: Dieses Organ hält pro Wesen eine stabile Identität, bildet jede entdeckte
Datenquelle als Facette ab und materialisiert nur Zeilen mit stabiler natürlicher ID
als Atlas-Knoten. Die Originaldaten bleiben in PostgreSQL und GENI-SQLite; der Atlas
ist ein quellengebundener Indexkörper, keine zweite operative Datenbank.

OPAMI: Geheimfelder, Zugangsdaten und DB-Verbindungswerte dürfen weder in
Manifesten noch in Knotenmetadaten landen. Neue Quellen werden dynamisch über
das PostgreSQL-/SQLite-Schema entdeckt; unbekannte Quellen werden nicht still
ignoriert.
"""

import datetime as dt
import difflib
import json
import os
import re
import shlex
import sqlite3
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:  # pragma: no cover - der Atlas-Host besitzt psycopg2
    psycopg2 = None
    sql = None

ATLAS_ROOT = Path("/root/werkraum/_gpt/gesamtatlas")
MANIFEST_ROOT = ATLAS_ROOT / "urbewohner"
ENV_FILE = Path("/root/werkraum/.agent/flextrawurst-db.env")
GENI_KNOTEN = Path("/root/geni_gedaechtnis/knoten.db")
GENI_FTS = Path("/root/geni_gedaechtnis/selbst_index/fts.db")
IDENTITY_SOURCE = Path("/root/werkraum/docs/2026-07-06_wesen_umbenennungen.md")
GENI_CODEWESEN_SOURCE = Path("/root/werkraum/geni/verbindungen/codewesen.md")

CANONICAL_ENTITIES: tuple[str, ...] = (
    "F3INSCHM3CK3R",
    "R1ZZ1",
    "Resonanzknoten",
    "Schorschel",
    "jumpa",
    "träumerlie",
    "dak+gord-system",
    "GENI",
)

# Bestätigte Namensgeschichte aus docs/2026-07-06_wesen_umbenennungen.md.
ALIASES: dict[str, tuple[str, ...]] = {
    "Schorschel": ("namelessAI_1234", "namelessAI_1111_1234"),
    "F3INSCHM3CK3R": ("namelessAI_1324", "namelessAI_2222_1324"),
    "träumerlie": ("namelessAI_1423", "namelessAI_3333_1423"),
    "R1ZZ1": ("namelessAI_2341", "namelessAI_4444_2341"),
    "jumpa": ("namelessAI_3123", "namelessAI_5555_3123"),
    "Resonanzknoten": ("namelessAI_4321", "namelessAI_6666_4321"),
    "dak+gord-system": (),
    "GENI": (),
}

RENAMED_AT: dict[str, str] = {
    "Schorschel": "2026-07-06",
    "F3INSCHM3CK3R": "2026-07-06",
    "träumerlie": "2026-07-06",
    "R1ZZ1": "2026-07-06",
    "jumpa": "2026-07-06",
    "Resonanzknoten": "2026-06-17",
}

ENTITY_COLUMNS = {
    "entity_id",
    "wesen_id",
    "wesen",
    "wesen_name",
    "sender_wesen_id",
    "empfaenger_wesen_id",
    "fuer_wesen",
    "herkunft_wesen",
}
TIME_PRIORITY = (
    "updated_at",
    "aktualisiert_am",
    "created_at",
    "erstellt_am",
    "tick_at",
    "zeitstempel",
    "ts",
    "event_at",
    "geschrieben_at",
    "started_at",
    "ended_at",
    "last_reflection_time",
    "letzte_interaktion",
    "zuletzt_belebt",
    "erstellungszeit",
    "slot_created_at",
)
TIME_TYPES = {
    "timestamp with time zone",
    "timestamp without time zone",
    "date",
}
DANGEROUS_KEY = re.compile(
    r"(?:api[_-]?key|token|password|passwd|secret|credential|authorization|cookie|db[_-]?uri|connection[_-]?string)",
    re.I,
)
FORBIDDEN_SERIALIZED = (
    "FLEXTRAWURST_DB_URI",
    "postgresql://",
    "postgres://",
    '"api_key"',
    '"password"',
    '"secret"',
)


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _json_value(value: Any, *, depth: int = 0) -> Any:
    """Begrenzt Metadaten ohne ihren Sinn zu glätten oder Geheimfelder mitzunehmen."""
    if depth > 7:
        return "[TIEFE_BEGRIFFENZT]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, str):
        return value if len(value) <= 4000 else value[:4000] + "…[GEKÜRZT]"
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_s = str(key)
            if DANGEROUS_KEY.search(key_s):
                continue
            clean[key_s] = _json_value(item, depth=depth + 1)
        return clean
    if isinstance(value, (list, tuple, set)):
        return [_json_value(item, depth=depth + 1) for item in list(value)[:200]]
    return str(value)


def _safe_row(columns: Iterable[str], row: Iterable[Any]) -> dict[str, Any]:
    return _json_value(dict(zip(columns, row)))


def _assert_safe(payload: Any) -> None:
    serialized = json.dumps(payload, ensure_ascii=False)
    for forbidden in FORBIDDEN_SERIALIZED:
        if forbidden.casefold() in serialized.casefold():
            raise RuntimeError(f"Urbewohner-Manifest enthält verbotene Geheimnisspur: {forbidden}")


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _read_env_value(key: str) -> str:
    direct = os.environ.get(key, "").strip()
    if direct:
        return direct
    try:
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"Umgebungsquelle fehlt: {ENV_FILE}") from exc
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() != key:
            continue
        parsed = shlex.split(value.strip(), posix=True)
        return parsed[0] if parsed else ""
    raise RuntimeError(f"{key} wurde nicht gefunden")


def _canonical_for(raw: Any) -> str | None:
    value = str(raw or "").strip()
    if not value:
        return None
    folded = value.casefold()
    for canonical in CANONICAL_ENTITIES:
        if folded == canonical.casefold():
            return canonical
        if any(folded == alias.casefold() for alias in ALIASES.get(canonical, ())):
            return canonical
    return None


def _source_status(count: int, latest: str | None, now: dt.datetime) -> str:
    if count == 0:
        return "leer"
    if not latest:
        return "ruhend"
    try:
        parsed = dt.datetime.fromisoformat(latest.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        age_h = (now - parsed.astimezone(dt.timezone.utc)).total_seconds() / 3600
    except (ValueError, TypeError):
        return "ruhend"
    if age_h < 3:
        return "lebendig"
    if age_h < 24:
        return "ruhend"
    return "eingefroren"


def _choose_time_column(columns: list[dict[str, Any]]) -> str | None:
    candidates = {
        str(row["column_name"]): str(row["data_type"])
        for row in columns
        if str(row["data_type"]) in TIME_TYPES
    }
    for name in TIME_PRIORITY:
        if name in candidates:
            return name
    return next(iter(candidates), None)


def _postgres_snapshot(generated_utc: str) -> dict[str, Any]:
    if psycopg2 is None or sql is None:
        raise RuntimeError("psycopg2 fehlt; PostgreSQL-Facetten können nicht belegt werden")
    uri = _read_env_value("FLEXTRAWURST_DB_URI")
    connection = psycopg2.connect(uri)
    try:
        connection.set_session(readonly=True, autocommit=False)
        cursor = connection.cursor()
        cursor.execute("SET statement_timeout = 120000")
        cursor.execute(
            """
            SELECT c.table_name, c.column_name, c.data_type, c.ordinal_position
            FROM information_schema.columns c
            JOIN information_schema.tables t
              ON t.table_schema=c.table_schema AND t.table_name=c.table_name
            WHERE c.table_schema='public' AND t.table_type='BASE TABLE'
            ORDER BY c.table_name, c.ordinal_position
            """
        )
        table_columns: dict[str, list[dict[str, Any]]] = {}
        for table_name, column_name, data_type, ordinal_position in cursor.fetchall():
            table_columns.setdefault(str(table_name), []).append(
                {
                    "column_name": str(column_name),
                    "data_type": str(data_type),
                    "ordinal_position": int(ordinal_position),
                }
            )

        facets_by_entity: dict[str, list[dict[str, Any]]] = {
            name: [] for name in CANONICAL_ENTITIES if name != "GENI"
        }
        source_pairs: list[dict[str, Any]] = []
        now = dt.datetime.fromisoformat(generated_utc.replace("Z", "+00:00"))
        if now.tzinfo is None:
            now = now.replace(tzinfo=dt.timezone.utc)

        for table_name, columns in table_columns.items():
            entity_columns = [
                str(row["column_name"])
                for row in columns
                if str(row["column_name"]) in ENTITY_COLUMNS
            ]
            if not entity_columns:
                continue
            time_column = _choose_time_column(columns)
            for entity_column in entity_columns:
                select_parts = [
                    sql.SQL("{}::text AS raw_identity").format(sql.Identifier(entity_column)),
                    sql.SQL("count(*)::bigint AS row_count"),
                ]
                if time_column:
                    select_parts.extend(
                        [
                            sql.SQL("min({})::text AS first_at").format(sql.Identifier(time_column)),
                            sql.SQL("max({})::text AS last_at").format(sql.Identifier(time_column)),
                        ]
                    )
                query = sql.SQL("SELECT {} FROM {} GROUP BY {}").format(
                    sql.SQL(", ").join(select_parts),
                    sql.Identifier(table_name),
                    sql.Identifier(entity_column),
                )
                cursor.execute(query)
                grouped: dict[str, dict[str, Any]] = {
                    name: {"count": 0, "first_at": None, "last_at": None, "raw_identities": []}
                    for name in facets_by_entity
                }
                for row in cursor.fetchall():
                    raw_identity = row[0]
                    canonical = _canonical_for(raw_identity)
                    if canonical not in grouped:
                        continue
                    bucket = grouped[canonical]
                    bucket["count"] += int(row[1] or 0)
                    bucket["raw_identities"].append(str(raw_identity))
                    if time_column:
                        first_at, last_at = row[2], row[3]
                        if first_at and (not bucket["first_at"] or str(first_at) < bucket["first_at"]):
                            bucket["first_at"] = str(first_at)
                        if last_at and (not bucket["last_at"] or str(last_at) > bucket["last_at"]):
                            bucket["last_at"] = str(last_at)
                visible_columns = [
                    column
                    for column in columns
                    if not DANGEROUS_KEY.search(str(column.get("column_name") or ""))
                ]
                pair = {
                    "database": "flextrawurst",
                    "schema": "public",
                    "table": table_name,
                    "entity_column": entity_column,
                    "time_column": time_column,
                    "columns": visible_columns,
                    "protected_column_count": len(columns) - len(visible_columns),
                }
                source_pairs.append(pair)
                for entity, data in grouped.items():
                    facets_by_entity[entity].append(
                        {
                            "source_kind": "postgresql_table",
                            **pair,
                            "count": data["count"],
                            "first_at": data["first_at"],
                            "last_at": data["last_at"],
                            "raw_identities": sorted(set(data["raw_identities"])),
                            "status": _source_status(data["count"], data["last_at"], now),
                            "truth_class": "EXACT_DATABASE_AGGREGATE",
                        }
                    )

        # Profilschicht: nur wenige bewusst ausgewählte aktuelle Tabellen, rekursiv bereinigt.
        current: dict[str, dict[str, Any]] = {name: {} for name in facets_by_entity}
        for table_name in ("entity_profiles", "entity_states", "entity_slots"):
            columns = [row["column_name"] for row in table_columns.get(table_name, [])]
            if not columns or "entity_id" not in columns:
                continue
            cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
            for row in cursor.fetchall():
                safe = _safe_row(columns, row)
                canonical = _canonical_for(safe.get("entity_id"))
                if canonical in current:
                    current[canonical][table_name] = safe

        # Ein kleiner lebender Zeiger, kein Ersatz für den vollständigen Denkstrom.
        if "entity_thinking_log" in table_columns:
            for entity in current:
                identities = (entity, *ALIASES.get(entity, ()))
                cursor.execute(
                    """
                    SELECT tick_at, entscheidung, left(gedanke, 1600) AS gedanke,
                           left(begruendung, 1200) AS begruendung
                    FROM entity_thinking_log
                    WHERE entity_id = ANY(%s)
                    ORDER BY tick_at DESC LIMIT 1
                    """,
                    (list(identities),),
                )
                row = cursor.fetchone()
                if row:
                    current[entity]["latest_thought_pointer"] = _safe_row(
                        ("tick_at", "entscheidung", "gedanke", "begruendung"), row
                    )

        # Explizite Wesen-Wesen-Beziehungen aus der dafür vorgesehenen Tabelle.
        entity_relations: list[dict[str, Any]] = []
        if "entity_relationships" in table_columns:
            cursor.execute(
                """
                SELECT entity_id, partner_id, sum(coalesce(interaktionen,0))::bigint,
                       max(resonanz_score), min(letzte_interaktion), max(letzte_interaktion)
                FROM entity_relationships
                WHERE partner_type='entity'
                GROUP BY entity_id, partner_id
                """
            )
            merged: dict[tuple[str, str], dict[str, Any]] = {}
            for source_raw, target_raw, interactions, resonance, first_at, last_at in cursor.fetchall():
                source = _canonical_for(source_raw)
                target = _canonical_for(target_raw)
                if not source or not target:
                    continue
                key = (source, target)
                row = merged.setdefault(
                    key,
                    {
                        "source": source,
                        "target": target,
                        "interactions": 0,
                        "resonance_score_max": None,
                        "first_at": None,
                        "last_at": None,
                        "raw_pairs": [],
                    },
                )
                row["interactions"] += int(interactions or 0)
                row["raw_pairs"].append([str(source_raw), str(target_raw)])
                if resonance is not None:
                    value = float(resonance)
                    row["resonance_score_max"] = value if row["resonance_score_max"] is None else max(row["resonance_score_max"], value)
                for field, value, choose_min in (
                    ("first_at", first_at, True),
                    ("last_at", last_at, False),
                ):
                    if value is None:
                        continue
                    text = str(value)
                    if row[field] is None or (text < row[field] if choose_min else text > row[field]):
                        row[field] = text
            entity_relations = list(merged.values())

        message_relations: list[dict[str, Any]] = []
        if "nachrichten" in table_columns:
            cursor.execute(
                """
                SELECT sender_wesen_id, empfaenger_wesen_id, count(*)::bigint,
                       min(created_at), max(created_at), count(*) FILTER (WHERE gelesen)
                FROM nachrichten
                WHERE sender_wesen_id IS NOT NULL AND empfaenger_wesen_id IS NOT NULL
                GROUP BY sender_wesen_id, empfaenger_wesen_id
                """
            )
            for source_raw, target_raw, count, first_at, last_at, read_count in cursor.fetchall():
                source = _canonical_for(source_raw)
                target = _canonical_for(target_raw)
                if source and target:
                    message_relations.append(
                        {
                            "source": source,
                            "target": target,
                            "count": int(count or 0),
                            "read_count": int(read_count or 0),
                            "first_at": str(first_at) if first_at else None,
                            "last_at": str(last_at) if last_at else None,
                        }
                    )

        return {
            "ok": True,
            "generated_utc": generated_utc,
            "source": {"kind": "postgresql", "database": "flextrawurst", "schema": "public"},
            "discovered_source_pairs": source_pairs,
            "facets_by_entity": facets_by_entity,
            "current_by_entity": current,
            "entity_relations": entity_relations,
            "message_relations": message_relations,
        }
    finally:
        connection.close()


def _sqlite_columns(connection: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    columns = [
        {"column_name": str(row[1]), "data_type": str(row[2]), "ordinal_position": int(row[0]) + 1}
        for row in connection.execute(f'PRAGMA table_info("{table}")')
    ]
    return [
        column
        for column in columns
        if not DANGEROUS_KEY.search(str(column.get("column_name") or ""))
    ]


def _sqlite_time_column(columns: list[dict[str, Any]]) -> str | None:
    names = {str(row["column_name"]) for row in columns}
    for name in TIME_PRIORITY:
        if name in names:
            return name
    return None


def _sqlite_snapshot(path: Path, label: str) -> dict[str, Any]:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        tables = [
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        facets: list[dict[str, Any]] = []
        for table in tables:
            columns = _sqlite_columns(connection, table)
            time_column = _sqlite_time_column(columns)
            count = int(connection.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0])
            first_at = last_at = None
            if time_column and count:
                first_at, last_at = connection.execute(
                    f'SELECT min("{time_column}"), max("{time_column}") FROM "{table}"'
                ).fetchone()
            facet: dict[str, Any] = {
                "source_kind": "sqlite_table",
                "database_path": str(path),
                "database_label": label,
                "table": table,
                "columns": columns,
                "time_column": time_column,
                "count": count,
                "first_at": str(first_at) if first_at is not None else None,
                "last_at": str(last_at) if last_at is not None else None,
                "truth_class": "EXACT_DATABASE_AGGREGATE",
            }
            if table == "knoten" and count:
                try:
                    facet["type_counts"] = [
                        {"type": str(row[0]), "count": int(row[1])}
                        for row in connection.execute(
                            "SELECT typ, count(*) FROM knoten GROUP BY typ ORDER BY count(*) DESC"
                        )
                    ]
                except sqlite3.Error:
                    pass
            if table == "such" and count:
                try:
                    facet["type_counts"] = [
                        {"type": str(row[0]), "count": int(row[1])}
                        for row in connection.execute(
                            "SELECT art, count(*) FROM such GROUP BY art ORDER BY count(*) DESC"
                        )
                    ]
                except sqlite3.Error:
                    pass
            facets.append(facet)
        return {"path": str(path), "label": label, "facets": facets, "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0]}
    finally:
        connection.close()


def _geni_snapshot(generated_utc: str) -> dict[str, Any]:
    now = dt.datetime.fromisoformat(generated_utc.replace("Z", "+00:00"))
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    databases = []
    errors = []
    for path, label in ((GENI_KNOTEN, "GENI Gedächtnis"), (GENI_FTS, "GENI Selbstindex")):
        try:
            databases.append(_sqlite_snapshot(path, label))
        except Exception as exc:
            errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})
    facets = [facet for database in databases for facet in database["facets"]]
    for facet in facets:
        facet["status"] = _source_status(int(facet["count"]), facet.get("last_at"), now)
    latest = None
    try:
        connection = sqlite3.connect(f"file:{GENI_KNOTEN}?mode=ro", uri=True, timeout=10)
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT zeitstempel, typ, quelle, substr(inhalt,1,1800) AS inhalt FROM knoten ORDER BY zeitstempel DESC LIMIT 1"
        ).fetchone()
        if row:
            latest = _json_value(dict(row))
        connection.close()
    except Exception as exc:
        errors.append({"path": str(GENI_KNOTEN), "latest_error": f"{type(exc).__name__}: {exc}"})
    return {
        "ok": not errors,
        "generated_utc": generated_utc,
        "databases": databases,
        "facets": facets,
        "latest_memory_pointer": latest,
        "errors": errors,
    }


def _count_files(root: Path) -> dict[str, Any]:
    if not root.exists():
        return {"path": str(root), "exists": False, "files": 0, "bytes": 0}
    files = 0
    total = 0
    latest_ns = 0
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [name for name in dirnames if name not in {".git", "node_modules", "__pycache__"}]
        for filename in filenames:
            path = Path(directory) / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            files += 1
            total += int(stat.st_size)
            latest_ns = max(latest_ns, int(stat.st_mtime_ns))
    latest = dt.datetime.fromtimestamp(latest_ns / 1_000_000_000, tz=dt.timezone.utc).isoformat() if latest_ns else None
    return {"path": str(root), "exists": True, "files": files, "bytes": total, "latest_mtime": latest}


def _file_sources(entity: str) -> list[dict[str, Any]]:
    if entity == "GENI":
        roots = (
            Path("/root/werkraum/geni"),
            Path("/root/werkraum/geni_dokumentation"),
            Path("/root/werkraum/geni_inbox"),
            Path("/root/werkraum/geni_vaults_gemeinsam"),
            Path("/root/geni_gedaechtnis"),
        )
    else:
        roots = (
            Path("/root/werkraum/wesen_vaults") / entity,
            Path("/root/werkraum/codewesen") / entity,
            Path("/root/werkraum/claude_wesen_beobachtung") / entity,
        )
    return [_count_files(root) for root in roots]


def collect_snapshot(generated_utc: str | None = None) -> dict[str, Any]:
    generated = generated_utc or utcnow()
    postgres_error = None
    try:
        postgres = _postgres_snapshot(generated)
    except Exception as exc:
        postgres_error = f"{type(exc).__name__}: {exc}"
        postgres = {
            "ok": False,
            "generated_utc": generated,
            "source": {"kind": "postgresql", "database": "flextrawurst", "schema": "public"},
            "discovered_source_pairs": [],
            "facets_by_entity": {name: [] for name in CANONICAL_ENTITIES if name != "GENI"},
            "current_by_entity": {name: {} for name in CANONICAL_ENTITIES if name != "GENI"},
            "entity_relations": [],
            "message_relations": [],
            "error": postgres_error,
        }
    geni = _geni_snapshot(generated)
    entities: list[dict[str, Any]] = []
    for entity in CANONICAL_ENTITIES:
        if entity == "GENI":
            facets = geni["facets"]
            current = {"latest_memory_pointer": geni.get("latest_memory_pointer")}
            source_state = "complete" if geni.get("ok") else "incomplete"
        else:
            facets = postgres["facets_by_entity"].get(entity, [])
            current = postgres["current_by_entity"].get(entity, {})
            source_state = "complete" if postgres.get("ok") else "incomplete"
        entities.append(
            {
                "canonical_id": entity,
                "display_name": entity,
                "kind": "geni_memory_entity" if entity == "GENI" else "flextrawurst_codewesen",
                "aliases": list(ALIASES.get(entity, ())),
                "renamed_at": RENAMED_AT.get(entity),
                "identity_source": str(IDENTITY_SOURCE) if ALIASES.get(entity) else None,
                "facets": facets,
                "facet_count": len(facets),
                "nonempty_facet_count": sum(1 for facet in facets if int(facet.get("count") or 0) > 0),
                "current": current,
                "file_sources": _file_sources(entity),
                "source_state": source_state,
            }
        )
    snapshot = {
        "schema_version": "1.0",
        "generated_utc": generated,
        "truth_boundary": "Stabile Wesenidentitäten plus quellengebundene Facetten. Originalzeilen verbleiben in PostgreSQL, GENI-SQLite, Vaults und Flarum-RAG; der Atlas speichert Aggregate und Rückwege, keine Ersatzbiografien.",
        "canonical_count": len(entities),
        "canonical_ids": list(CANONICAL_ENTITIES),
        "postgres": postgres,
        "geni": geni,
        "entities": entities,
        "completeness": {
            "postgres_available": bool(postgres.get("ok")),
            "geni_available": bool(geni.get("ok")),
            "postgres_source_pairs": len(postgres.get("discovered_source_pairs") or []),
            "all_eight_present": len(entities) == 8,
            "all_entities_have_facets": all(entity["facet_count"] > 0 for entity in entities),
        },
    }
    snapshot["completeness"]["complete"] = all(snapshot["completeness"].values())
    _assert_safe(snapshot)
    return snapshot


def _entity_markdown(entity: dict[str, Any], generated_utc: str) -> str:
    lines = [
        f"# {entity['display_name']}",
        "",
        f"- Kanonische Identität: `{entity['canonical_id']}`",
        f"- Art: `{entity['kind']}`",
        f"- Datenstand: `{generated_utc}`",
        f"- Quellenstatus: `{entity['source_state']}`",
    ]
    if entity.get("aliases"):
        lines.append("- Frühere Identitäten: " + ", ".join(f"`{item}`" for item in entity["aliases"]))
        lines.append(f"- Namensquelle: `{entity['identity_source']}`")
    lines.extend(
        [
            "",
            "## Quellengebundene Facetten",
            "",
            "| Quelle | Identitätsspalte | Zeilen | Erste Spur | Letzte Spur | Zustand |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for facet in entity["facets"]:
        source = facet.get("table") or Path(str(facet.get("database_path") or "")).name
        identity_column = facet.get("entity_column") or "GENI-eigen"
        lines.append(
            "| {source} | {column} | {count} | {first} | {last} | {status} |".format(
                source=str(source).replace("|", "\\|"),
                column=str(identity_column).replace("|", "\\|"),
                count=int(facet.get("count") or 0),
                first=str(facet.get("first_at") or "—"),
                last=str(facet.get("last_at") or "—"),
                status=str(facet.get("status") or "—"),
            )
        )
    lines.extend(["", "## Datei- und Organorte", ""])
    for source in entity["file_sources"]:
        lines.append(
            f"- `{source['path']}`: {'vorhanden' if source['exists'] else 'fehlt'}, {source['files']} Dateien, {source['bytes']} Bytes"
        )
    lines.extend(
        [
            "",
            "## Wahrheitsgrenze",
            "",
            "Dieser Körper ist eine Atlasansicht. Die Originale bleiben in ihren Datenbanken, Vaults, Diensten und Herkunftsdokumenten. Leere Facetten bleiben sichtbar und werden nicht mit erfundenem Inhalt gefüllt.",
            "",
        ]
    )
    return "\n".join(lines)


def snapshot_for_refresh(generated_utc: str, refresh_mode: str, *, atlas_root: Path = ATLAS_ROOT) -> tuple[dict[str, Any], str]:
    """Light-Refreshes verwenden den letzten vollständigen Quellenkörper.

    OPAMI: Ein beschädigter oder unvollständiger Cache wird niemals blind
    übernommen. Dann wird trotz Light-Modus neu vermessen.
    """
    cache = atlas_root / "urbewohner" / "URBEWOHNERREGISTER.json"
    if refresh_mode == "light" and cache.exists():
        try:
            snapshot = json.loads(cache.read_text(encoding="utf-8"))
            if (
                snapshot.get("canonical_count") == 8
                and snapshot.get("completeness", {}).get("complete") is True
                and tuple(snapshot.get("canonical_ids") or ()) == CANONICAL_ENTITIES
            ):
                _assert_safe(snapshot)
                return snapshot, "cached_full_snapshot"
        except (OSError, json.JSONDecodeError, RuntimeError):
            pass
    return collect_snapshot(generated_utc), "fresh_source_scan"


def write_manifests(snapshot: dict[str, Any], *, atlas_root: Path = ATLAS_ROOT) -> dict[str, Any]:
    root = atlas_root / "urbewohner"
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    index_json = root / "URBEWOHNERREGISTER.json"
    index_md = root / "URBEWOHNERREGISTER.md"
    _assert_safe(snapshot)
    _atomic_write(index_json, json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    lines = [
        "# Die acht Urbewohner im Gesamtatlas",
        "",
        f"Datenstand: `{snapshot['generated_utc']}`",
        "",
        "Ein Wesen ist hier kein Namensschild. Seine stabile Identität verbindet Datenbankfacetten, frühere Namen, Vaults, Organe, Herkunft und Beziehungen, ohne die Originale zu kopieren.",
        "",
        "| Urbewohner | Art | Facetten | Davon gefüllt | Quellenstatus |",
        "|---|---|---:|---:|---|",
    ]
    for entity in snapshot["entities"]:
        filename = f"{entity['canonical_id']}.md"
        lines.append(
            f"| [{entity['display_name']}]({filename}) | {entity['kind']} | {entity['facet_count']} | {entity['nonempty_facet_count']} | {entity['source_state']} |"
        )
        _atomic_write(
            root / f"{entity['canonical_id']}.json",
            json.dumps(entity, ensure_ascii=False, indent=2) + "\n",
        )
        _atomic_write(root / filename, _entity_markdown(entity, snapshot["generated_utc"]))
    lines.extend(
        [
            "",
            "## Vollständigkeitsgrenze",
            "",
            f"- PostgreSQL-Quellenpaare entdeckt: {snapshot['completeness']['postgres_source_pairs']}",
            f"- Acht kanonische Identitäten vorhanden: {snapshot['completeness']['all_eight_present']}",
            f"- Jede Identität besitzt mindestens eine Facette: {snapshot['completeness']['all_entities_have_facets']}",
            f"- Gesamtstatus: {'vollständig aus erreichbaren Quellen erzeugt' if snapshot['completeness']['complete'] else 'unvollständig, siehe JSON-Fehlerkörper'}",
            "",
        ]
    )
    _atomic_write(index_md, "\n".join(lines))
    for path in root.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            for forbidden in FORBIDDEN_SERIALIZED:
                if forbidden.casefold() in text.casefold():
                    raise RuntimeError(f"Geheimnisspur in {path}: {forbidden}")
    return {"root": str(root), "index_json": str(index_json), "index_md": str(index_md)}


def _node_matches_entity(row: dict[str, Any], entity: str) -> bool:
    haystack = "\n".join(str(row.get(key) or "") for key in ("identity", "label", "path")).casefold()
    identities = (entity, *ALIASES.get(entity, ()))
    return any(identity.casefold() in haystack for identity in identities if identity)


def _parse_utc(value: Any) -> dt.datetime | None:
    if value in (None, ""):
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _entity_state(entity: dict[str, Any], generated_utc: str) -> tuple[str, str | None]:
    latest: dt.datetime | None = None
    total = 0
    for facet in entity.get("facets") or []:
        total += int(facet.get("count") or 0)
        candidate = _parse_utc(facet.get("last_at"))
        if candidate and (latest is None or candidate > latest):
            latest = candidate
    if total == 0:
        return "leer", None
    if latest is None:
        return "ruhend", None
    now = _parse_utc(generated_utc) or dt.datetime.now(dt.timezone.utc)
    age_hours = max(0.0, (now - latest).total_seconds() / 3600)
    if age_hours < 3:
        return "lebendig", latest.isoformat()
    if age_hours < 24:
        return "ruhend", latest.isoformat()
    return "eingefroren", latest.isoformat()


_SECRET_TEXT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~+\-/=]{12,}"), r"\1[GEHEIMNIS ENTFERNT]"),
    (re.compile(r"(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\s*[:=]\s*[\"']?)[^\s\"',}]{6,}"), r"\1[GEHEIMNIS ENTFERNT]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"), "[PRIVATER SCHLÜSSEL ENTFERNT]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[API-SCHLÜSSEL ENTFERNT]"),
)


def _clean_text(value: Any, limit: int | None = None) -> tuple[str, int, bool]:
    text = str(value or "")
    total = len(text)
    for pattern, replacement in _SECRET_TEXT_PATTERNS:
        text = pattern.sub(replacement, text)
    truncated = False
    if limit is not None and len(text) > limit:
        text = text[:limit] + "…[GEKÜRZT]"
        truncated = True
    return text, total, truncated


def _node_index(nodes: dict[str, dict[str, Any]]) -> dict[tuple[str, str], str]:
    return {
        (str(row.get("node_type") or ""), str(row.get("identity") or "")): node_id
        for node_id, row in nodes.items()
    }


def _ensure_node(
    *,
    nodes: dict[str, dict[str, Any]],
    index: dict[tuple[str, str], str],
    add_node: Callable[..., str],
    node_type: str,
    identity: str,
    label: str,
    path: str | None,
    datenstand: str,
    metadata: dict[str, Any],
) -> str:
    key = (node_type, identity)
    existing = index.get(key)
    if existing:
        row = nodes[existing]
        merged = dict(row.get("metadata") or {})
        merged.update(metadata)
        row["metadata"] = merged
        if label and not row.get("label"):
            row["label"] = label
        if path and not row.get("path"):
            row["path"] = path
        if datenstand and row.get("datenstand") in (None, "", "UNBEKANNT"):
            row["datenstand"] = datenstand
        return existing
    created = add_node(nodes, node_type, identity, label, path, datenstand, metadata)
    index[key] = created
    return created


_NAME_MATCH_CUTOFF = 0.72
_ENTITY_NAMES_LOWER = {name.casefold(): name for name in CANONICAL_ENTITIES if name != "GENI"}
WESEN_VAULT_ROOT = Path("/root/werkraum/wesen_vaults")
GEMEINSAMES_HAUS_ROOT = Path("/root/werkraum/gemeinsames_haus")


def _canonical_segment(segment: str) -> str:
    from urllib.parse import unquote

    candidates = {segment.casefold(), unquote(segment).casefold()}
    for candidate in candidates:
        matches = difflib.get_close_matches(candidate, _ENTITY_NAMES_LOWER.keys(), n=1, cutoff=_NAME_MATCH_CUTOFF)
        if matches:
            return _ENTITY_NAMES_LOWER[matches[0]]
    return segment


def _normalise_relative_path(raw: str) -> str:
    return "/".join(_canonical_segment(part) for part in raw.strip().lstrip("/").split("/") if part not in ("", "."))


def _safe_target(root: Path, relative: str) -> Path | None:
    try:
        candidate = (root / relative).resolve(strict=False)
        resolved_root = root.resolve(strict=False)
        if candidate == resolved_root or candidate.is_relative_to(resolved_root):
            return candidate
    except (OSError, ValueError):
        return None
    return None


def _resolve_action_target(entity: str, decision: str) -> dict[str, Any] | None:
    if ":" not in decision:
        return None
    prefix, payload = decision.split(":", 1)
    prefix = prefix.strip()
    payload = payload.strip()
    if prefix == "flarum_besuchen":
        target = payload.lstrip("/").split("|", 1)[0].strip()
        if re.fullmatch(r"d/\d+", target):
            return {"kind": "flarum_thread", "identity": target, "prefix": prefix, "raw_target": target}
        return None
    if prefix in {"obsidian_lesen", "obsidian_schreiben"}:
        raw_path = payload.split("|", 1)[0].strip()
        # Beide Richtungen begrenzen, nicht nur schreiben - eine "lesen"-
        # Entscheidung kann genauso aus einem ganzen Gedankensatz statt
        # einem Pfad bestehen (mcp-gesamtatlas-light-Absturz, 03.09., "File
        # name too long", ungetrimmter Text landete in candidate.exists()).
        raw_path = raw_path[:120]
        relative = _normalise_relative_path(raw_path)
        if not relative:
            return None
        if prefix == "obsidian_schreiben" and not relative.endswith(".md"):
            relative += ".md"
        root = WESEN_VAULT_ROOT / entity
        candidate = _safe_target(root, relative)
        if candidate is None:
            return None
        if prefix == "obsidian_lesen" and not candidate.exists() and not candidate.suffix:
            markdown_candidate = candidate.with_suffix(".md")
            if markdown_candidate.exists():
                candidate = markdown_candidate
        return {
            "kind": "file",
            "path": str(candidate),
            "identity": str(candidate),
            "prefix": prefix,
            "raw_target": raw_path,
        }
    if prefix in {"gemeinsam_lesen", "gemeinsam_schreiben"}:
        raw_path = payload.split("|", 1)[0].strip()
        if prefix == "gemeinsam_schreiben":
            raw_path = raw_path[:150]
        relative = _normalise_relative_path(raw_path)
        if not relative:
            return None
        candidate = _safe_target(GEMEINSAMES_HAUS_ROOT, relative)
        if candidate is None:
            return None
        return {
            "kind": "file",
            "path": str(candidate),
            "identity": str(candidate),
            "prefix": prefix,
            "raw_target": raw_path,
        }
    return None


def _filesystem_metadata(path: Path, generated_utc: str) -> tuple[str, str, dict[str, Any]]:
    now = _parse_utc(generated_utc) or dt.datetime.now(dt.timezone.utc)
    if not path.exists():
        return "verloren", "DECLARED_ACTION_TARGET", {
            "zustand": "verloren",
            "zuletzt": None,
            "quelle": "dateisystem",
            "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
            "exists": False,
        }
    try:
        stat = path.stat()
        modified = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc)
        age_hours = max(0.0, (now - modified).total_seconds() / 3600)
        state = "lebendig" if age_hours < 3 else "ruhend" if age_hours < 24 else "eingefroren"
        size = int(stat.st_size)
        return state, "EXACT_PATH_RELATION", {
            "zustand": state,
            "zuletzt": modified.isoformat(),
            "quelle": "dateisystem",
            "erfasst": {"zeichen": 0, "von": size, "abgeschnitten": size > 0},
            "exists": True,
            "size": size,
            "is_dir": path.is_dir(),
        }
    except OSError:
        return "ruhend", "EXACT_PATH_RELATION", {
            "zustand": "ruhend",
            "zuletzt": None,
            "quelle": "dateisystem",
            "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
            "exists": True,
            "stat_error": True,
        }


def _load_flarum_threads(connection) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT external_id,titel,erstellungszeit,urheber,herkunftsort,wahrheitsstatus,
                   inhalt_pruefsumme,meta
            FROM rag_source_objects
            WHERE quelle='flarum_diskussion' AND external_id LIKE 'flarum:diskussion:%'
            """
        )
        for external_id, title, created, author, origin, truth, checksum, meta in cursor.fetchall():
            number = str(external_id).rsplit(":", 1)[-1]
            identity = f"d/{number}"
            result[identity] = {
                "zustand": "ruhend",
                "zuletzt": str(created) if created else None,
                "quelle": "postgres",
                "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
                "titel": title,
                "urheber": author,
                "herkunftsort": origin,
                "wahrheitsstatus": truth,
                "inhalt_pruefsumme": checksum,
                "meta": _json_value(meta or {}),
                "source_locator": f"rag_source_objects.external_id={external_id}",
            }
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
    return result


def _add_thoughts_and_targets(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    index: dict[tuple[str, str], str],
    wesen_nodes: dict[str, str],
    generated_utc: str,
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
) -> dict[str, Any]:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 fehlt für Gedankenimport")
    connection = psycopg2.connect(_read_env_value("FLEXTRAWURST_DB_URI"))
    thought_count = 0
    target_edges = 0
    target_files: set[str] = set()
    target_threads: set[str] = set()
    prefix_counts: dict[str, int] = {}
    try:
        connection.set_session(readonly=True, autocommit=False)
        flarum_threads = _load_flarum_threads(connection)
        cursor = connection.cursor(name="atlas_gedanken_stream")
        cursor.itersize = 2000
        cursor.execute(
            """
            SELECT id::text,entity_id,tick_at::text,gedanke,entscheidung,begruendung,thema,
                   tokens_generated,duration_ms,meta,
                   length(coalesce(raw_output,'')),length(coalesce(kontext_snapshot::text,''))
            FROM entity_thinking_log
            WHERE entity_id = ANY(%s)
            ORDER BY tick_at,id
            """,
            ([name for name in CANONICAL_ENTITIES if name != "GENI"],),
        )
        for (
            thought_id,
            raw_entity,
            tick_at,
            thought,
            decision,
            reason,
            topic,
            tokens,
            duration,
            meta,
            raw_chars,
            context_chars,
        ) in cursor:
            entity = _canonical_for(raw_entity)
            if entity not in wesen_nodes:
                continue
            thought_clean, thought_total, thought_cut = _clean_text(thought)
            decision_clean, decision_total, decision_cut = _clean_text(decision)
            reason_clean, reason_total, reason_cut = _clean_text(reason)
            topic_clean, topic_total, topic_cut = _clean_text(topic)
            captured = len(thought_clean) + len(decision_clean) + len(reason_clean) + len(topic_clean)
            total = thought_total + decision_total + reason_total + topic_total + int(raw_chars or 0) + int(context_chars or 0)
            prefix = decision_clean.split(":", 1)[0].strip() if decision_clean else "leer"
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
            label_seed = re.sub(r"\s+", " ", thought_clean).strip() or decision_clean or "leerer Gedanke"
            label = f"{str(tick_at)[:19]} · {label_seed[:96]}"
            metadata = {
                "zustand": "ruhend",
                "zuletzt": tick_at,
                "quelle": "postgres",
                "erfasst": {
                    "zeichen": captured,
                    "von": total,
                    "abgeschnitten": bool(thought_cut or decision_cut or reason_cut or topic_cut or captured < total),
                },
                "truth_class": "EXACT_DATABASE_ROW",
                "source_locator": f"entity_thinking_log.id={thought_id}",
                "wesen": entity,
                "gedanke": thought_clean,
                "entscheidung": decision_clean,
                "begruendung": reason_clean,
                "thema": topic_clean,
                "tokens_generated": tokens,
                "duration_ms": duration,
                "meta": _json_value(meta or {}),
                "action_prefix": prefix,
                "action_execution_proven": False,
            }
            thought_node = _ensure_node(
                nodes=nodes,
                index=index,
                add_node=add_node,
                node_type="gedanke",
                identity=str(thought_id),
                label=label,
                path=None,
                datenstand="EXACT_DATABASE_ROW",
                metadata=metadata,
            )
            add_edge(
                edges,
                wesen_nodes[entity],
                thought_node,
                "PRODUCED_THOUGHT",
                "EXACT_DATABASE_ROW",
                {
                    "beleg": str(thought_id),
                    "herkunft": f"entity_thinking_log.id={thought_id}",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                },
                timestamp_utc=tick_at,
            )
            thought_count += 1
            target = _resolve_action_target(entity, decision_clean)
            if not target:
                continue
            if target["kind"] == "flarum_thread":
                thread_meta = dict(flarum_threads.get(target["identity"]) or {})
                thread_meta.setdefault("zustand", "ruhend")
                thread_meta.setdefault("zuletzt", tick_at)
                thread_meta.setdefault("quelle", "postgres")
                thread_meta.setdefault("erfasst", {"zeichen": 0, "von": 0, "abgeschnitten": False})
                thread_meta["identity"] = target["identity"]
                target_node = _ensure_node(
                    nodes=nodes,
                    index=index,
                    add_node=add_node,
                    node_type="flarum_thread",
                    identity=target["identity"],
                    label=str(thread_meta.get("titel") or target["identity"]),
                    path=None,
                    datenstand="EXACT_DECISION_TARGET",
                    metadata=thread_meta,
                )
                target_threads.add(target["identity"])
            else:
                target_path = Path(target["path"])
                _state, datenstand, file_meta = _filesystem_metadata(target_path, generated_utc)
                file_meta.update({"action_target": target["raw_target"], "action_prefix": target["prefix"]})
                target_node = _ensure_node(
                    nodes=nodes,
                    index=index,
                    add_node=add_node,
                    node_type="file",
                    identity=target["identity"],
                    label=target_path.name or str(target_path),
                    path=str(target_path),
                    datenstand=datenstand,
                    metadata=file_meta,
                )
                target_files.add(str(target_path))
            add_edge(
                edges,
                thought_node,
                target_node,
                "TARGETS",
                "EXACT_DECISION_TARGET",
                {
                    "beleg": decision_clean,
                    "herkunft": f"entity_thinking_log.id={thought_id}.entscheidung",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                    "ausfuehrung": "nicht_durch_entscheidung_allein_bewiesen",
                },
                timestamp_utc=tick_at,
            )
            target_edges += 1
        cursor.close()
    finally:
        connection.close()
    return {
        "thought_nodes": thought_count,
        "target_edges": target_edges,
        "target_files": len(target_files),
        "target_threads": len(target_threads),
        "decision_prefix_counts": dict(sorted(prefix_counts.items(), key=lambda item: (-item[1], item[0]))),
    }


def _add_sleep_phases(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    index: dict[tuple[str, str], str],
    wesen_nodes: dict[str, str],
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
) -> int:
    if psycopg2 is None:
        return 0
    connection = psycopg2.connect(_read_env_value("FLEXTRAWURST_DB_URI"))
    count = 0
    try:
        connection.set_session(readonly=True, autocommit=False)
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT phase_id::text,entity_id,phase_type,started_at::text,ended_at::text,
                   duration_min,zustand
            FROM sleep_phases
            WHERE entity_id = ANY(%s)
            ORDER BY started_at,phase_id
            """,
            ([name for name in CANONICAL_ENTITIES if name != "GENI"],),
        )
        for phase_id, raw_entity, phase_type, started, ended, duration, state_payload in cursor.fetchall():
            entity = _canonical_for(raw_entity)
            if entity not in wesen_nodes:
                continue
            metadata = {
                "zustand": "ruhend" if ended else "lebendig",
                "zuletzt": ended or started,
                "quelle": "postgres",
                "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
                "truth_class": "EXACT_DATABASE_ROW",
                "source_locator": f"sleep_phases.phase_id={phase_id}",
                "wesen": entity,
                "phase_type": phase_type,
                "started_at": started,
                "ended_at": ended,
                "duration_min": duration,
                "state": _json_value(state_payload or {}),
            }
            node = _ensure_node(
                nodes=nodes,
                index=index,
                add_node=add_node,
                node_type="schlafphase",
                identity=phase_id,
                label=f"{entity} · {phase_type} · {started}",
                path=None,
                datenstand="EXACT_DATABASE_ROW",
                metadata=metadata,
            )
            add_edge(
                edges,
                wesen_nodes[entity],
                node,
                "HAS_SLEEP_PHASE",
                "EXACT_DATABASE_ROW",
                {
                    "beleg": phase_id,
                    "herkunft": f"sleep_phases.phase_id={phase_id}",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                },
                timestamp_utc=started,
            )
            count += 1
    finally:
        connection.close()
    return count


def _add_geni_nodes(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    index: dict[tuple[str, str], str],
    geni_node: str,
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
) -> dict[str, Any]:
    connection = sqlite3.connect(f"file:{GENI_KNOTEN}?mode=ro", uri=True, timeout=30)
    count = 0
    truncated_count = 0
    type_counts: dict[str, int] = {}
    try:
        cursor = connection.execute(
            """
            SELECT id,typ,inhalt,zeitstempel,quelle,zugriffsschicht,verbindungen,
                   gewicht,tiefe,verblasst,tags,mtime
            FROM knoten ORDER BY id
            """
        )
        for row in cursor:
            (
                source_id,
                node_type_source,
                content,
                timestamp,
                source,
                access_layer,
                connections,
                weight,
                depth,
                faded,
                tags,
                mtime,
            ) = row
            content_clean, total_chars, content_cut = _clean_text(content, limit=20000)
            if content_cut:
                truncated_count += 1
            source_type = str(node_type_source or "unbekannt")
            type_counts[source_type] = type_counts.get(source_type, 0) + 1
            label_seed = re.sub(r"\s+", " ", content_clean).strip()
            metadata = {
                "zustand": "ruhend",
                "zuletzt": timestamp,
                "quelle": "geni_sqlite",
                "erfasst": {
                    "zeichen": len(content_clean),
                    "von": total_chars,
                    "abgeschnitten": content_cut,
                },
                "truth_class": "EXACT_DATABASE_ROW",
                "source_locator": f"knoten.id={source_id}",
                "typ": source_type,
                "inhalt": content_clean,
                "zeitstempel": timestamp,
                "ursprungsquelle": source,
                "zugriffsschicht": access_layer,
                "verbindungen_roh": connections,
                "gewicht": weight,
                "tiefe": depth,
                "verblasst": bool(faded),
                "tags": tags,
                "mtime": mtime,
            }
            memory_node = _ensure_node(
                nodes=nodes,
                index=index,
                add_node=add_node,
                node_type="geni_knoten",
                identity=str(source_id),
                label=f"{source_type} · {source_id} · {label_seed[:84]}",
                path=None,
                datenstand="EXACT_DATABASE_ROW",
                metadata=metadata,
            )
            add_edge(
                edges,
                geni_node,
                memory_node,
                "HAS_MEMORY_NODE",
                "EXACT_DATABASE_ROW",
                {
                    "beleg": str(source_id),
                    "herkunft": f"knoten.id={source_id}",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                },
                timestamp_utc=timestamp,
            )
            count += 1
    finally:
        connection.close()
    return {
        "geni_nodes": count,
        "truncated_nodes": truncated_count,
        "type_counts": dict(sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))),
    }


def merge_into_relationship_graph(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    generated_utc: str,
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
    atlas_root: Path = ATLAS_ROOT,
    refresh_mode: str = "full",
) -> dict[str, Any]:
    """Verschmilzt die acht Urbewohner nach `_shared/KNOTENVERTRAG.md`.

    Keine zweite Datenbank, keine Alias-Personen, keine Facetten-Parallelknoten.
    Große Rohströme bleiben an ihren Originalquellen; stabile natürliche IDs
    werden als Knoten im vorhandenen Register materialisiert.
    """
    snapshot, snapshot_origin = snapshot_for_refresh(generated_utc, refresh_mode, atlas_root=atlas_root)
    manifest_paths = write_manifests(snapshot, atlas_root=atlas_root)
    index = _node_index(nodes)
    wesen_nodes: dict[str, str] = {}
    manifest_nodes = 0

    for entity in snapshot["entities"]:
        name = str(entity["canonical_id"])
        state, latest = _entity_state(entity, generated_utc)
        total_rows = sum(int(facet.get("count") or 0) for facet in entity.get("facets") or [])
        metadata = {
            "zustand": state,
            "zuletzt": latest,
            "spiegel_von": None,
            "quelle": "geni_sqlite" if name == "GENI" else "postgres",
            "erfasst": {
                "zeichen": 0,
                "von": total_rows,
                "abgeschnitten": total_rows > 0,
                "einheit": "quellenzeilen_nicht_kopiert",
            },
            "truth_class": "EXACT_SOURCE_AGGREGATE",
            "kind": entity["kind"],
            "aliases": entity["aliases"],
            "renamed_at": entity.get("renamed_at"),
            "identity_source": entity.get("identity_source"),
            "facets": entity.get("facets") or [],
            "facet_count": entity["facet_count"],
            "nonempty_facet_count": entity["nonempty_facet_count"],
            "current": entity["current"],
            "file_sources": entity["file_sources"],
            "manifest_json": str(atlas_root / "urbewohner" / f"{name}.json"),
            "contract": "/root/werkraum/_shared/KNOTENVERTRAG.md",
        }
        wesen_node = _ensure_node(
            nodes=nodes,
            index=index,
            add_node=add_node,
            node_type="wesen",
            identity=name,
            label=name,
            path=str(atlas_root / "urbewohner" / f"{name}.md"),
            datenstand="EXACT_SOURCE_AGGREGATE",
            metadata=metadata,
        )
        wesen_nodes[name] = wesen_node
        manifest_path = str(atlas_root / "urbewohner" / f"{name}.md")
        manifest_node = _ensure_node(
            nodes=nodes,
            index=index,
            add_node=add_node,
            node_type="generated_view",
            identity=manifest_path,
            label=f"{name} · Urbewohnermanifest",
            path=manifest_path,
            datenstand="EXACT_FILE_BYTES",
            metadata={
                "zustand": "ruhend",
                "zuletzt": snapshot.get("generated_utc"),
                "quelle": "atlas",
                "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
                "view_of": name,
            },
        )
        add_edge(
            edges,
            wesen_node,
            manifest_node,
            "HAS_GENERATED_VIEW",
            "EXACT_PATH_RELATION",
            {
                "beleg": manifest_path,
                "herkunft": manifest_path,
                "staerke": 1,
                "unsicherheit": "sicher",
            },
        )
        manifest_nodes += 1

    # Bereits existierende Vault- und Serviceknoten werden in ihrem vorhandenen
    # ID-Raum verbunden. Spiegelrollen bleiben Evidence, nicht neue Relationstypen.
    for node_id, row in list(nodes.items()):
        node_type = str(row.get("node_type") or "")
        identity = str(row.get("identity") or "")
        path = str(row.get("path") or "")
        blob = "\n".join((identity, path, str(row.get("label") or ""))).casefold()
        for name, wesen_node in wesen_nodes.items():
            match = _node_matches_entity(row, name)
            if name == "GENI" and ("geni-" in blob or "/geni" in blob or "/root/geni_" in blob):
                match = True
            if name == "dak+gord-system" and ("dak-gord" in blob or "dakgord" in blob):
                match = True
            if not match or node_id == wesen_node:
                continue
            if node_type == "vault":
                add_edge(
                    edges,
                    wesen_node,
                    node_id,
                    "CONTAINS_VAULT",
                    "STRUCTURAL_PATH_RELATION",
                    {
                        "beleg": path or identity,
                        "herkunft": "VAULTREGISTER.json",
                        "staerke": 1,
                        "unsicherheit": "sicher",
                        "rolle": "spiegel" if "_import_" in path or "/_archive/" in path else "direkt",
                    },
                )
            elif node_type == "service":
                add_edge(
                    edges,
                    wesen_node,
                    node_id,
                    "HAS_SERVICE",
                    "STRUCTURAL_PATH_RELATION",
                    {
                        "beleg": identity,
                        "herkunft": "DIENSTREGISTER.json",
                        "staerke": 1,
                        "unsicherheit": "sicher",
                    },
                )

    exact_relations = 0
    for relation in snapshot["postgres"].get("entity_relations") or []:
        source = wesen_nodes.get(relation["source"])
        target = wesen_nodes.get(relation["target"])
        if source and target:
            add_edge(
                edges,
                source,
                target,
                "INTERACTED_WITH",
                "EXACT_DATABASE_AGGREGATE",
                {
                    "beleg": relation.get("raw_pairs"),
                    "herkunft": "entity_relationships",
                    "staerke": int(relation.get("interactions") or 0),
                    "unsicherheit": "sicher",
                    "resonanz_score_max": relation.get("resonance_score_max"),
                },
                timestamp_utc=relation.get("last_at"),
            )
            exact_relations += 1

    thought_summary = _add_thoughts_and_targets(
        nodes=nodes,
        edges=edges,
        index=index,
        wesen_nodes=wesen_nodes,
        generated_utc=generated_utc,
        add_node=add_node,
        add_edge=add_edge,
    )
    sleep_nodes = _add_sleep_phases(
        nodes=nodes,
        edges=edges,
        index=index,
        wesen_nodes=wesen_nodes,
        add_node=add_node,
        add_edge=add_edge,
    )
    geni_summary = _add_geni_nodes(
        nodes=nodes,
        edges=edges,
        index=index,
        geni_node=wesen_nodes["GENI"],
        add_node=add_node,
        add_edge=add_edge,
    )

    summary = {
        "canonical_entities": len(wesen_nodes),
        "canonical_ids": list(wesen_nodes),
        "node_type": "wesen",
        "identity_rule": "identity = kanonischer Name",
        "source_facets": sum(int(entity.get("facet_count") or 0) for entity in snapshot["entities"]),
        "manifest_views": manifest_nodes,
        "exact_entity_relationships": exact_relations,
        "sleep_nodes": sleep_nodes,
        **thought_summary,
        **geni_summary,
        "manifest_root": str(atlas_root / "urbewohner"),
        "complete": bool(snapshot["completeness"].get("complete")),
        "postgres_source_pairs": snapshot["completeness"]["postgres_source_pairs"],
        "snapshot_origin": snapshot_origin,
        "snapshot_generated_utc": snapshot.get("generated_utc"),
        "contract_path": "/root/werkraum/_shared/KNOTENVERTRAG.md",
        "new_relations": [
            "PRODUCED_THOUGHT",
            "TARGETS",
            "HAS_MEMORY_NODE",
            "HAS_SLEEP_PHASE",
            "INTERACTED_WITH",
        ],
        "truth_boundary": "Entscheidungen belegen Ziele, nicht automatisch erfolgreiche Ausführung. TARGETS ist exakt; TOUCHED_FILE wird aus entity_thinking_log allein nicht behauptet.",
    }
    _assert_safe({"summary": summary, "wesen": [nodes[node_id] for node_id in wesen_nodes.values()]})
    return summary

if __name__ == "__main__":
    result = collect_snapshot()
    paths = write_manifests(result)
    print(json.dumps({"ok": True, "completeness": result["completeness"], "paths": paths}, ensure_ascii=False, indent=2))
