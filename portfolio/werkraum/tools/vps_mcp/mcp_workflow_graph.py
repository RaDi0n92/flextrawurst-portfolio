from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import fnmatch
import json
import os
import re
import shlex
import threading
import time
import uuid
from typing import Any, TypedDict

import psycopg2
from langgraph.graph import END, START, StateGraph

import mcp_delivery_graph as delivery_graph

from mcp_action_graph import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    NODE_BULK_MUTATION,
    NODE_CONTROL_RESTART,
    NODE_META_GENERATION,
    NODE_NAVIGATE,
    NODE_READ,
    NODE_SHELL_AUTOMATION,
    NODE_SHELL_READ,
    NODE_SINGLE_DELETE,
    NODE_SINGLE_EDIT,
    NODE_SINGLE_MOVE,
    NODE_SINGLE_WRITE,
    NODE_UNKNOWN_MUTATION,
    PORTFOLIO_ROOT,
    CONTROL_PLANE_ROOT,
    evaluate_action as base_evaluate_action,
    graph_snapshot as base_graph_snapshot,
    server_instructions as base_server_instructions,
)

STATE_PATH_INVENTORY = "PATH_INVENTORY"
STATE_MANUAL_DISCOVERY = "MANUAL_DISCOVERY"
STATE_FOCUSED_READING = "FOCUSED_READING"
STATE_CHANGE_READY = "CHANGE_READY"
STATE_VERIFY = "VERIFY"
STATE_RECOVER = "RECOVER"

MODE_DISCOVER = "DISCOVER"
MODE_SURGICAL = "SURGICAL"
# Accepted only as a legacy label; it no longer grants or gates actions.
MODE_BUILD_ALLOWED = "BUILD_ALLOWED"
MODE_CONTROL_PLANE = "CONTROL_PLANE"
_ALLOWED_MODES = {MODE_DISCOVER, MODE_SURGICAL, MODE_CONTROL_PLANE}

_RUNTIME_PATH = Path("/root/werkraum/_shared/mcp_shared/action_workflow.json")
_RUNTIME_SCHEMA = 3
_MEMORY_ENV_PATH = Path("/root/werkraum/.agent/flextrawurst-db.env")
_MEMORY_SCHEMA = "portfolio_memory"
_LOCK = threading.RLock()
_RECENT_LIMIT = 40
_MUTATION_NODES = {
    NODE_SINGLE_EDIT,
    NODE_SINGLE_WRITE,
    NODE_SINGLE_DELETE,
    NODE_SINGLE_MOVE,
    NODE_CONTROL_RESTART,
}
_STATEFUL_MUTATION_NODES = _MUTATION_NODES | {
    NODE_META_GENERATION,
    NODE_SHELL_AUTOMATION,
}
_READISH_NODES = {NODE_READ}
_NAVIGATION_NODES = {NODE_NAVIGATE, NODE_SHELL_READ}
_PATH_INVENTORY_TOOLS = {
    "harness.path_scan",
    "harness.path_inventory",
    "harness.graph",
    "harness.check_action",
    "harness.set_mode",
    "vps.list_roots",
    "vps.list_files",
}
_PREINVENTORY_OBSERVATION_TOOLS = {
    "agents.list_sessions",
    "agents.read_session",
    "agents.search_sessions",
    "agents.compare_sessions",
    "database.query_readonly",
    "network.http_probe",
    "services.status",
    "services.logs",
    "atlas.stream_search",
    "atlas.stream_status",
    "atlas.map",
    "atlas.ai_stream_state",
}
_HARD_BLOCK_NODES = {
    NODE_SHELL_AUTOMATION,
    NODE_META_GENERATION,
    NODE_BULK_MUTATION,
    NODE_UNKNOWN_MUTATION,
}
NODE_TASK_SCOPE = "TASK_SCOPE"
_TASK_SCOPE_CONTROL_TOOLS = {
    "harness.graph",
    "harness.layers",
    "harness.layer_set",
    "harness.full_activate",
    "harness.set_mode",
    "harness.check_action",
    "harness.directive_context",
    "harness.directive_reminder",
    "harness.output_check",
    "harness.experience_message",
    "harness.learning_context",
    "harness.learning_status",
    "harness.master_pause",
    "harness.master_resume",
    "harness.control_leases",
}

_HARNESS_LAYER_KINDS = {"CORE", "PROJECT", "TASK", "EPHEMERAL"}
_HARNESS_DESIRED_STATUSES = {"ACTIVE", "PAUSED", "ARCHIVED"}
_HARNESS_HEALTH_STATUSES = {"HEALTHY", "DEGRADED", "BROKEN", "UNKNOWN"}

_HARNESS_CORE_LAYERS: dict[str, dict[str, Any]] = {
    "core.master": {
        "title": "Harness insgesamt",
        "purpose": "Hauptschalter fuer die gesamte Harness-Durchsetzung.",
        "does": "Entscheidet, ob die Schutz- und Steuerlogik vor normalen Toolaktionen eingreift.",
        "pause_effect": "Unterbausteine behalten ihren eigenen Zustand, wirken aber voruebergehend nicht.",
    },
    "core.task_scope": {
        "title": "Aktueller Auftrag",
        "purpose": "Haelt ChatGPT vor allen anderen Harness-Regeln beim aktuell autorisierten Auftrag.",
        "does": "Prueft normale Toolaktionen zuerst gegen den aktiven verifizierten TASK-Scope; Nebenpfade werden geblockt statt verfolgt.",
        "pause_effect": "Task-Scope bleibt sichtbar, blockiert normale Aktionen aber voruebergehend nicht.",
    },
    "core.path_inventory": {
        "title": "Pfadorientierung",
        "purpose": "Verhindert blinde Arbeit in unbekannten VPS-Bereichen.",
        "does": "Kennt vorhandene Pfade und kann Inhaltsarbeit begrenzen, bis genug Orientierung vorhanden ist.",
        "pause_effect": "Andere Harness-Bausteine bleiben aktiv; nur diese Orientierungsbremse greift nicht.",
    },
    "core.action_graph": {
        "title": "Aktionsklassifikation",
        "purpose": "Unterscheidet Lesen, Navigation, Einzelmutation, Shell-Automation und groessere Eingriffe.",
        "does": "Ordnet jede Toolaktion einer Sicherheitsklasse und erlaubten Folgekanten zu.",
        "pause_effect": "Die Harness nutzt diese Klassifikation voruebergehend nicht zur Blockentscheidung.",
    },
    "core.learned_rules": {
        "title": "Selbstlernschleife",
        "purpose": "Erfahrungen in getestete, spaeter wieder korrigierbare Verhaltensregeln ueberfuehren.",
        "does": "Nur getestete ACTIVE-Regeln duerfen hart wirken; Kandidaten bleiben Vorschlaege.",
        "pause_effect": "Bestehende Lernregeln bleiben erhalten, greifen aber voruebergehend nicht hart ein.",
    },
    "core.directives": {
        "title": "Deine Direktiven",
        "purpose": "Explizite Nutzeranweisungen staerker machen als Modellgewohnheiten.",
        "does": "Prueft verifizierte Direktiven, Reminder und Invarianten deterministisch vor Mutationen.",
        "pause_effect": "Die Direktivenhistorie bleibt erhalten, wird aber voruebergehend nicht als Denier angewendet.",
    },
    "core.intent_mode": {
        "title": "Arbeitsmodus",
        "purpose": "Den aktuellen Arbeitsstil sichtbar machen.",
        "does": "Zeigt DISCOVER, SURGICAL oder CONTROL_PLANE; konkrete Nutzeranweisung und Auftragsscope entscheiden ueber Aktionen.",
        "pause_effect": "Der sichtbare Modus bleibt dokumentiert; andere passende Gates arbeiten unabhaengig davon.",
    },
    "core.verify_recover": {
        "title": "Gegenpruefung und Recovery",
        "purpose": "Nach Eingriffen nicht einfach ungeprueft weiterlaufen.",
        "does": "Erzwingt Gegenlesen nach Aenderungen und fuehrt nach Blocks oder Fehlern in einen Recovery-Zustand.",
        "pause_effect": "Verify-/Recovery-Zustaende bleiben dokumentiert, blockieren aber voruebergehend keine Folgeaktion.",
    },
    "core.read_before_mutate": {
        "title": "Lesen vor Aendern",
        "purpose": "Aenderungen an bestehendem Inhalt auf Kenntnis des konkreten Ziels stuetzen.",
        "does": "Bestehende Dateien muessen vor Edit, Loeschung oder Verschiebung direkt gelesen sein; neue Dateien brauchen einen passenden Auftrag, keinen kuenstlichen Mindestbestand an Referenzdateien.",
        "pause_effect": "Diese konkrete Vorbedingung wird voruebergehend nicht durchgesetzt.",
    },
    "core.output_check": {
        "title": "Ausgabepruefung",
        "purpose": "Auch fertige Assistant-Ausgaben gegen harte Nutzerregeln pruefbar machen.",
        "does": "Prueft vorgesehenen Text gegen aktive DENY-Regeln, wenn der Client den Check verbindlich aufruft.",
        "pause_effect": "Der Check bleibt sichtbar, blockiert die Ausgabe aber voruebergehend nicht.",
    },
    "core.client_capture": {
        "title": "Vertrauenswuerdiger Nutzer-Capture",
        "purpose": "Rohes Nutzerwort von Modellinterpretation und Erinnerung trennen.",
        "does": "Nimmt echte Nutzereingaben als verifizierte Autoritaetsquelle auf, aus der harte Constraints entstehen duerfen.",
        "pause_effect": "Neue Eingaben erzeugen voruebergehend keine harte Autoritaet; bestehende Historie bleibt erhalten.",
    },
}


@dataclass(frozen=True)
class WorkflowDecision:
    decision: str
    state: str
    action_node: str
    tool_name: str
    project_scoped: bool
    reason: str
    next_state_on_success: str
    next_state_on_failure: str
    guidance: tuple[str, ...] = ()
    allowed_neighbors: tuple[str, ...] = (
        "vps.read_file",
        "vps.list_files",
        "vps.search_text",
        "git.diff",
        "vps.edit_file (nach Lesen)",
        "vps.write_file (einzelnes Ziel; neue Dateien brauchen keinen kuenstlichen Mindestbestand an Referenzen)",
        "vps.delete (eine Datei, nach Lesen)",
        "vps.move (eine Datei, nach Lesen)",
    )

    @property
    def allowed(self) -> bool:
        return self.decision == DECISION_ALLOW

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed"] = self.allowed
        data["allowed_neighbors"] = list(self.allowed_neighbors)
        data["guidance"] = list(self.guidance)
        return data


def _session_key(args: dict[str, Any] | None) -> str:
    args = args if isinstance(args, dict) else {}
    raw = str(args.get("session_id") or "default")
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in "._-")[:100]
    return safe or "default"


def _default_session() -> dict[str, Any]:
    return {
        "state": STATE_PATH_INVENTORY,
        "mode": MODE_DISCOVER,
        "mode_user_instruction": None,
        "mode_changed_at": None,
        "path_inventory_complete": False,
        "path_scan_id": None,
        "path_scan_counts": {},
        "reads_since_mutation": 0,
        "distinct_read_paths": [],
        "recent_events": [],
        "pending_verification": [],
        "blocked_streak": 0,
        "last_updated": None,
    }


def _memory_db_uri() -> str | None:
    if _MEMORY_ENV_PATH.is_file():
        for raw in _MEMORY_ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("FLEXTRAWURST_DB_URI="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _workflow_connection():
    uri = _memory_db_uri()
    if not uri:
        return None
    conn = psycopg2.connect(uri, connect_timeout=5)
    conn.autocommit = True
    return conn


def _ensure_workflow_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {_MEMORY_SCHEMA}")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.workflow_runtime (
                session_id text PRIMARY KEY,
                schema_version integer NOT NULL,
                state jsonb NOT NULL,
                updated_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )


def _ensure_harness_layer_tables(conn) -> None:
    """Persistente, append-only Steuerung fuer Harness-Schichten und ihren Dialog."""
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {_MEMORY_SCHEMA}")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_layers (
                layer_id text PRIMARY KEY,
                kind text NOT NULL CHECK (kind IN ('CORE','PROJECT','TASK','EPHEMERAL')),
                title text NOT NULL,
                purpose text NOT NULL DEFAULT '',
                does_text text NOT NULL DEFAULT '',
                pause_effect text NOT NULL DEFAULT '',
                scope jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                provenance jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                parent_layer_id text,
                created_at timestamptz NOT NULL DEFAULT now(),
                updated_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_layer_events (
                event_id text PRIMARY KEY,
                layer_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.harness_layers(layer_id),
                event_type text NOT NULL CHECK (
                    event_type IN ('CREATE','SET_ACTIVE','SET_PAUSED','ARCHIVE','RESTORE','HEALTH')
                ),
                actor text NOT NULL,
                reason text NOT NULL DEFAULT '',
                desired_status text CHECK (desired_status IN ('ACTIVE','PAUSED','ARCHIVED')),
                health text CHECK (health IN ('HEALTHY','DEGRADED','BROKEN','UNKNOWN')),
                expires_at timestamptz,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_layer_feedback (
                entry_id text PRIMARY KEY,
                layer_id text REFERENCES {_MEMORY_SCHEMA}.harness_layers(layer_id),
                actor text NOT NULL,
                entry_type text NOT NULL CHECK (
                    entry_type IN ('COMMENT','PROPOSAL','ACCEPT','REJECT','RATING')
                ),
                text text NOT NULL DEFAULT '',
                payload jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                parent_entry_id text,
                status text NOT NULL DEFAULT 'OPEN' CHECK (
                    status IN ('OPEN','ACCEPTED','REJECTED','RESOLVED','RECORDED','ARCHIVED')
                ),
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=%s
              AND t.relname='harness_layer_feedback'
              AND c.conname='harness_layer_feedback_status_check'
            """,
            (_MEMORY_SCHEMA,),
        )
        feedback_status_constraint = cur.fetchone()
        if feedback_status_constraint is not None and "RECORDED" not in str(feedback_status_constraint[0]):
            cur.execute(
                f"ALTER TABLE {_MEMORY_SCHEMA}.harness_layer_feedback "
                "DROP CONSTRAINT harness_layer_feedback_status_check"
            )
            cur.execute(
                f"""
                ALTER TABLE {_MEMORY_SCHEMA}.harness_layer_feedback
                ADD CONSTRAINT harness_layer_feedback_status_check
                CHECK (status IN ('OPEN','ACCEPTED','REJECTED','RESOLVED','RECORDED','ARCHIVED'))
                """
            )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_feedback_receipts (
                entry_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.harness_layer_feedback(entry_id),
                recipient text NOT NULL,
                ack_actor text NOT NULL,
                ack_note text NOT NULL DEFAULT '',
                seen_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY (entry_id,recipient)
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_layer_context (
                context_id text PRIMARY KEY,
                layer_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.harness_layers(layer_id),
                actor text NOT NULL,
                context_type text NOT NULL CHECK (
                    context_type IN ('PLAN','VISION','RESEARCH','EVIDENCE','DOC','LINK','NOTE')
                ),
                title text NOT NULL,
                summary text NOT NULL DEFAULT '',
                reference text NOT NULL DEFAULT '',
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_layer_definition_events (
                event_id text PRIMARY KEY,
                layer_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.harness_layers(layer_id),
                actor text NOT NULL,
                reason text NOT NULL DEFAULT '',
                before_definition jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                after_definition jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.harness_control_leases (
                lease_id text PRIMARY KEY,
                actor text NOT NULL,
                grantee text NOT NULL,
                layer_pattern text NOT NULL DEFAULT '*',
                scope jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                reason text NOT NULL DEFAULT '',
                expires_at timestamptz,
                revoked_at timestamptz,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS harness_layer_events_layer_idx ON {_MEMORY_SCHEMA}.harness_layer_events(layer_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS harness_layer_feedback_layer_idx ON {_MEMORY_SCHEMA}.harness_layer_feedback(layer_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS harness_feedback_receipts_recipient_idx ON {_MEMORY_SCHEMA}.harness_feedback_receipts(recipient,seen_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS harness_layer_context_layer_idx ON {_MEMORY_SCHEMA}.harness_layer_context(layer_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS harness_layer_definition_events_layer_idx ON {_MEMORY_SCHEMA}.harness_layer_definition_events(layer_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS harness_control_leases_active_idx ON {_MEMORY_SCHEMA}.harness_control_leases(expires_at,revoked_at)"
        )

        for layer_id, spec in _HARNESS_CORE_LAYERS.items():
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layers
                    (layer_id,kind,title,purpose,does_text,pause_effect,scope,provenance,parent_layer_id)
                VALUES (%s,'CORE',%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s)
                ON CONFLICT (layer_id) DO NOTHING
                """,
                (
                    layer_id,
                    spec["title"],
                    spec["purpose"],
                    spec["does"],
                    spec["pause_effect"],
                    json.dumps({"type": "GLOBAL"}, ensure_ascii=False),
                    json.dumps({"source": "mcp_workflow_graph", "builtin": True}, ensure_ascii=False),
                    None if layer_id == "core.master" else "core.master",
                ),
            )


def harness_layers_snapshot(session_id: str | None = None) -> dict[str, Any]:
    """Eine kanonische Sicht fuer MCP und Web-Dashboard. Kein UI-Schattenstate."""
    conn = _workflow_connection()
    now_ts = time.time()
    if conn is None:
        return {
            "ok": False,
            "updated_at": now_ts,
            "master": {"desired_status": "ACTIVE", "effective_status": "ACTIVE", "health": "UNKNOWN"},
            "layers": [],
            "leases": [],
            "feedback_open": 0,
            "warning": "PostgreSQL nicht erreichbar; fail-safe bleibt Harness ACTIVE.",
        }
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT layer_id,kind,title,purpose,does_text,pause_effect,scope,provenance,parent_layer_id,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layers
                ORDER BY CASE kind WHEN 'CORE' THEN 0 WHEN 'PROJECT' THEN 1 WHEN 'TASK' THEN 2 ELSE 3 END,
                         layer_id
                """
            )
            layer_rows = cur.fetchall()
            cur.execute(
                f"""
                SELECT DISTINCT ON (layer_id)
                       layer_id,event_type,actor,reason,desired_status,
                       EXTRACT(EPOCH FROM expires_at)::double precision,
                       metadata,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_events
                WHERE desired_status IS NOT NULL
                ORDER BY layer_id,created_at DESC
                """
            )
            latest_status_events = {row[0]: row[1:] for row in cur.fetchall()}
            cur.execute(
                f"""
                SELECT DISTINCT ON (layer_id)
                       layer_id,actor,reason,health,metadata,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_events
                WHERE health IS NOT NULL
                ORDER BY layer_id,created_at DESC
                """
            )
            latest_health_events = {row[0]: row[1:] for row in cur.fetchall()}
            cur.execute(
                f"""
                SELECT layer_id,actor,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_events
                WHERE event_type='CREATE'
                ORDER BY created_at ASC
                """
            )
            creation_events: dict[str, tuple[Any, ...]] = {}
            for row in cur.fetchall():
                creation_events.setdefault(str(row[0]), tuple(row[1:]))
            cur.execute(
                f"""
                SELECT p.layer_id,count(*)::integer
                FROM {_MEMORY_SCHEMA}.harness_layer_feedback p
                WHERE p.entry_type='PROPOSAL'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM {_MEMORY_SCHEMA}.harness_layer_feedback d
                      WHERE d.parent_entry_id=p.entry_id
                        AND d.entry_type IN ('ACCEPT','REJECT')
                  )
                GROUP BY p.layer_id
                """
            )
            feedback_counts = {row[0]: int(row[1]) for row in cur.fetchall()}
            cur.execute(
                f"""
                SELECT event_id,layer_id,event_type,actor,reason,desired_status,health,
                       EXTRACT(EPOCH FROM expires_at)::double precision,
                       metadata,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_events
                ORDER BY created_at DESC
                LIMIT 600
                """
            )
            recent_event_rows = cur.fetchall()
            cur.execute(
                f"""
                SELECT context_id,layer_id,actor,context_type,title,summary,reference,metadata,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_context
                ORDER BY created_at DESC
                LIMIT 600
                """
            )
            context_rows = cur.fetchall()
            cur.execute(
                f"""
                SELECT event_id,layer_id,actor,reason,before_definition,after_definition,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_definition_events
                ORDER BY created_at DESC
                LIMIT 600
                """
            )
            definition_event_rows = cur.fetchall()
            cur.execute(
                f"""
                SELECT lease_id,actor,grantee,layer_pattern,scope,reason,
                       EXTRACT(EPOCH FROM expires_at)::double precision,
                       metadata,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_control_leases
                WHERE revoked_at IS NULL
                  AND (expires_at IS NULL OR expires_at > now())
                ORDER BY created_at DESC
                """
            )
            lease_rows = cur.fetchall()

        recent_events_by_layer: dict[str, list[dict[str, Any]]] = {}
        for row in recent_event_rows:
            layer_id = str(row[1])
            bucket = recent_events_by_layer.setdefault(layer_id, [])
            if len(bucket) >= 10:
                continue
            bucket.append({
                "event_id": row[0],
                "event_type": row[2],
                "actor": row[3],
                "reason": row[4],
                "desired_status": row[5],
                "health": row[6],
                "expires_at": row[7],
                "metadata": row[8] or {},
                "created_at": row[9],
            })

        context_by_layer: dict[str, list[dict[str, Any]]] = {}
        for row in context_rows:
            layer_id = str(row[1])
            bucket = context_by_layer.setdefault(layer_id, [])
            if len(bucket) >= 20:
                continue
            bucket.append({
                "context_id": row[0],
                "actor": row[2],
                "context_type": row[3],
                "title": row[4],
                "summary": row[5],
                "reference": row[6],
                "metadata": row[7] or {},
                "created_at": row[8],
            })

        definition_history_by_layer: dict[str, list[dict[str, Any]]] = {}
        for row in definition_event_rows:
            layer_id = str(row[1])
            bucket = definition_history_by_layer.setdefault(layer_id, [])
            if len(bucket) >= 20:
                continue
            bucket.append({
                "event_id": row[0],
                "actor": row[2],
                "reason": row[3],
                "before": row[4] or {},
                "after": row[5] or {},
                "created_at": row[6],
            })

        layers: list[dict[str, Any]] = []
        master_desired = "ACTIVE"
        for row in layer_rows:
            (
                layer_id, kind, title, purpose, does_text, pause_effect,
                scope, provenance, parent_layer_id, created_at,
            ) = row
            status_event = latest_status_events.get(layer_id)
            health_event = latest_health_events.get(layer_id)
            creation_event = creation_events.get(str(layer_id))
            created_actor = (
                str(creation_event[0])
                if creation_event is not None and creation_event[0] is not None
                else ("SYSTEM_BUILTIN" if kind == "CORE" else None)
            )
            created_event_at = (
                float(creation_event[1])
                if creation_event is not None and creation_event[1] is not None
                else None
            )
            desired = "ACTIVE"
            health = "HEALTHY" if kind == "CORE" else "UNKNOWN"
            status_reason = "Standardmaessig aktiv; noch keine abweichende Steuerentscheidung."
            status_actor = "SYSTEM_DEFAULT"
            health_reason = "Kein abweichender Gesundheitszustand gemeldet."
            health_actor = "SYSTEM_DEFAULT"
            expires_at = None
            last_status_event_at = None
            last_health_event_at = None
            if status_event is not None:
                event_type, status_actor, status_reason, event_desired, expires_at, metadata, last_status_event_at = status_event
                if event_desired in _HARNESS_DESIRED_STATUSES:
                    desired = event_desired
            if health_event is not None:
                health_actor, health_reason, event_health, health_metadata, last_health_event_at = health_event
                if event_health in _HARNESS_HEALTH_STATUSES:
                    health = event_health

            expired_pause = bool(desired == "PAUSED" and expires_at is not None and expires_at <= now_ts)
            if expired_pause:
                desired = "ACTIVE"
                status_reason = "Zeitlich begrenzte Pause ist abgelaufen; automatisch wieder aktiv."
                status_actor = "TTL"
                expires_at = None

            if desired == "ARCHIVED":
                effective = "ARCHIVED"
            elif kind != "CORE" and expires_at is not None and expires_at <= now_ts:
                effective = "EXPIRED"
                status_reason = "Die gesetzte Lebensdauer dieser dynamischen Schicht ist abgelaufen."
                status_actor = "TTL"
            else:
                effective = desired

            item = {
                "layer_id": layer_id,
                "kind": kind,
                "title": title,
                "purpose": purpose,
                "does": does_text,
                "pause_effect": pause_effect,
                "scope": scope or {},
                "provenance": provenance or {},
                "created_actor": created_actor,
                "created_event_at": created_event_at,
                "parent_layer_id": parent_layer_id,
                "desired_status": desired,
                "effective_status": effective,
                "health": health,
                "status_reason": status_reason,
                "status_actor": status_actor,
                "health_reason": health_reason,
                "health_actor": health_actor,
                "expires_at": expires_at,
                "last_status_event_at": last_status_event_at,
                "last_health_event_at": last_health_event_at,
                "last_event_at": max(
                    [ts for ts in (last_status_event_at, last_health_event_at) if ts is not None],
                    default=None,
                ),
                "created_at": created_at,
                "open_feedback": feedback_counts.get(layer_id, 0),
                "recent_events": list(recent_events_by_layer.get(str(layer_id), [])),
                "context": list(context_by_layer.get(str(layer_id), [])),
                "definition_history": list(definition_history_by_layer.get(str(layer_id), [])),
            }
            if layer_id == "core.master":
                master_desired = desired
            layers.append(item)

        master_effective = "PAUSED" if master_desired == "PAUSED" else "ACTIVE"
        for item in layers:
            if item["layer_id"] != "core.master" and master_effective == "PAUSED":
                if item["effective_status"] == "ACTIVE":
                    item["effective_status"] = "BLOCKED_BY_PARENT"
            if item["layer_id"] == "core.master":
                item["effective_status"] = master_effective

        leases = [
            {
                "lease_id": row[0],
                "actor": row[1],
                "grantee": row[2],
                "layer_pattern": row[3],
                "scope": row[4] or {},
                "reason": row[5],
                "expires_at": row[6],
                "metadata": row[7] or {},
                "created_at": row[8],
            }
            for row in lease_rows
        ]
        master = next((item for item in layers if item["layer_id"] == "core.master"), None) or {
            "desired_status": "ACTIVE",
            "effective_status": "ACTIVE",
            "health": "UNKNOWN",
            "status_reason": "Master-Layer fehlt; fail-safe ACTIVE.",
        }
        chatgpt_inbox = harness_feedback_inbox(recipient="CHATGPT", limit=100)
        return {
            "ok": True,
            "session_id": session_id or "default",
            "updated_at": now_ts,
            "master": master,
            "layers": layers,
            "leases": leases,
            "feedback_open": sum(feedback_counts.values()),
            "chatgpt_inbox": chatgpt_inbox,
            "chatgpt_inbox_count": len(chatgpt_inbox),
            "counts": {
                "active": sum(1 for x in layers if x["effective_status"] == "ACTIVE"),
                "paused": sum(1 for x in layers if x["desired_status"] == "PAUSED"),
                "archived": sum(1 for x in layers if x["effective_status"] == "ARCHIVED"),
                "degraded": sum(1 for x in layers if x["health"] in {"DEGRADED", "BROKEN"}),
                "ephemeral": sum(1 for x in layers if x["kind"] == "EPHEMERAL" and x["effective_status"] != "EXPIRED"),
            },
        }
    finally:
        conn.close()


def harness_layer_set(
    layer_id: str,
    desired_status: str,
    *,
    actor: str,
    reason: str,
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    desired_status = str(desired_status).upper()
    if desired_status not in _HARNESS_DESIRED_STATUSES:
        raise ValueError(f"Ungueltiger Layer-Status: {desired_status}")
    if not actor.strip() or not reason.strip():
        raise ValueError("actor und reason sind Pflichtfelder.")
    if ttl_seconds is not None and int(ttl_seconds) <= 0:
        raise ValueError("ttl_seconds muss positiv sein oder entfallen.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar; Layer-Zustand wird fail-safe nicht veraendert.")
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {_MEMORY_SCHEMA}.harness_layers WHERE layer_id=%s",
                (layer_id,),
            )
            if cur.fetchone() is None:
                raise ValueError(f"Unbekannter Harness-Layer: {layer_id}")
            event_type = {
                "ACTIVE": "SET_ACTIVE",
                "PAUSED": "SET_PAUSED",
                "ARCHIVED": "ARCHIVE",
            }[desired_status]
            expires_sql = "now() + (%s * interval '1 second')" if ttl_seconds is not None else "NULL"
            params: list[Any] = [
                "hle-" + uuid.uuid4().hex,
                layer_id,
                event_type,
                actor.strip(),
                reason.strip(),
                desired_status,
            ]
            if ttl_seconds is not None:
                params.append(int(ttl_seconds))
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layer_events
                    (event_id,layer_id,event_type,actor,reason,desired_status,expires_at)
                VALUES (%s,%s,%s,%s,%s,%s,{expires_sql})
                """,
                tuple(params),
            )
        return harness_layers_snapshot()
    finally:
        conn.close()


def harness_update_layer_definition(
    layer_id: str,
    *,
    actor: str,
    reason: str,
    title: str | None = None,
    purpose: str | None = None,
    does_text: str | None = None,
    pause_effect: str | None = None,
) -> dict[str, Any]:
    if not layer_id.strip() or not actor.strip() or not reason.strip():
        raise ValueError("layer_id, actor und reason sind Pflichtfelder.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT kind,title,purpose,does_text,pause_effect
                FROM {_MEMORY_SCHEMA}.harness_layers
                WHERE layer_id=%s
                FOR UPDATE
                """,
                (layer_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Unbekannter Harness-Layer: {layer_id}")
            kind, old_title, old_purpose, old_does, old_pause = row
            if str(kind) == "CORE" and actor.strip() != "DANIEL_DASHBOARD":
                raise PermissionError(
                    "CORE-Definitionen duerfen nur durch Daniels authentifiziertes Dashboard direkt geaendert werden."
                )

            before = {
                "title": str(old_title or ""),
                "purpose": str(old_purpose or ""),
                "does": str(old_does or ""),
                "pause_effect": str(old_pause or ""),
            }
            after = {
                "title": before["title"] if title is None else str(title).strip(),
                "purpose": before["purpose"] if purpose is None else str(purpose).strip(),
                "does": before["does"] if does_text is None else str(does_text).strip(),
                "pause_effect": before["pause_effect"] if pause_effect is None else str(pause_effect).strip(),
            }
            if not after["title"]:
                raise ValueError("title darf nicht leer sein.")
            if after == before:
                return {
                    "changed": False,
                    "layer_id": layer_id,
                    "before": before,
                    "after": after,
                    "snapshot": harness_layers_snapshot(),
                }

            event_id = "hld-" + uuid.uuid4().hex
            cur.execute(
                f"""
                UPDATE {_MEMORY_SCHEMA}.harness_layers
                SET title=%s,purpose=%s,does_text=%s,pause_effect=%s,updated_at=now()
                WHERE layer_id=%s
                """,
                (
                    after["title"],
                    after["purpose"],
                    after["does"],
                    after["pause_effect"],
                    layer_id,
                ),
            )
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layer_definition_events
                    (event_id,layer_id,actor,reason,before_definition,after_definition)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s::jsonb)
                """,
                (
                    event_id,
                    layer_id,
                    actor.strip(),
                    reason.strip(),
                    json.dumps(before, ensure_ascii=False),
                    json.dumps(after, ensure_ascii=False),
                ),
            )
        return {
            "changed": True,
            "event_id": event_id,
            "layer_id": layer_id,
            "before": before,
            "after": after,
            "snapshot": harness_layers_snapshot(),
        }
    finally:
        conn.close()


def harness_create_layer(
    *,
    layer_id: str,
    kind: str,
    title: str,
    purpose: str,
    does_text: str,
    pause_effect: str,
    actor: str,
    reason: str,
    scope: dict[str, Any] | None = None,
    provenance: dict[str, Any] | None = None,
    parent_layer_id: str = "core.master",
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    kind = str(kind).upper()
    if kind not in _HARNESS_LAYER_KINDS or kind == "CORE":
        raise ValueError("Dynamische Layer duerfen PROJECT, TASK oder EPHEMERAL sein.")
    if not re.fullmatch(r"[a-z0-9._:-]{3,120}", layer_id):
        raise ValueError("layer_id darf nur a-z, 0-9 und ._:- enthalten.")

    scope_data = scope if isinstance(scope, dict) else {}
    provenance_data = provenance if isinstance(provenance, dict) else {}
    if kind == "TASK" and provenance_data.get("authority_verified") is True:
        raw_goal = str(scope_data.get("raw_goal") or scope_data.get("goal") or "").strip()
        allowed_tools = _task_scope_patterns(scope_data.get("allowed_tool_patterns"))
        allowed_targets = _task_scope_patterns(scope_data.get("allowed_target_patterns"))
        if not raw_goal:
            raise ValueError("Ein verifizierter TASK braucht ein klares Ziel (raw_goal).")
        if not allowed_tools:
            raise ValueError("Ein verifizierter TASK braucht mindestens ein allowed_tool_pattern.")
        invalid_targets = [
            pattern for pattern in allowed_targets
            if not _build_target_pattern_is_bounded(pattern)
        ]
        if invalid_targets:
            raise ValueError(
                "TASK-Zielmuster muessen begrenzte absolute VPS-Pfade sein: "
                + ", ".join(invalid_targets[:3])
            )

    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layers
                    (layer_id,kind,title,purpose,does_text,pause_effect,scope,provenance,parent_layer_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s)
                """,
                (
                    layer_id, kind, title.strip(), purpose.strip(), does_text.strip(), pause_effect.strip(),
                    json.dumps(scope or {}, ensure_ascii=False),
                    json.dumps(provenance or {}, ensure_ascii=False),
                    parent_layer_id,
                ),
            )
            expires_sql = "now() + (%s * interval '1 second')" if ttl_seconds is not None else "NULL"
            params: list[Any] = [
                "hle-" + uuid.uuid4().hex,
                layer_id,
                "CREATE",
                actor.strip(),
                reason.strip(),
                "ACTIVE",
            ]
            if ttl_seconds is not None:
                params.append(int(ttl_seconds))
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layer_events
                    (event_id,layer_id,event_type,actor,reason,desired_status,expires_at)
                VALUES (%s,%s,%s,%s,%s,%s,{expires_sql})
                """,
                tuple(params),
            )
        return harness_layers_snapshot()
    finally:
        conn.close()


def harness_layer_feedback(
    *,
    layer_id: str | None,
    actor: str,
    entry_type: str,
    text: str,
    payload: dict[str, Any] | None = None,
    parent_entry_id: str | None = None,
) -> dict[str, Any]:
    entry_type = str(entry_type).upper()
    if entry_type not in {"COMMENT", "PROPOSAL", "ACCEPT", "REJECT", "RATING"}:
        raise ValueError(f"Ungueltiger Feedback-Typ: {entry_type}")
    if not actor.strip() or not text.strip():
        raise ValueError("actor und text sind Pflichtfelder.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        entry_id = "hlf-" + uuid.uuid4().hex
        status = (
            "OPEN" if entry_type == "PROPOSAL"
            else "RECORDED" if entry_type in {"COMMENT", "RATING"}
            else "ACCEPTED" if entry_type == "ACCEPT"
            else "REJECTED"
        )
        with conn.cursor() as cur:
            if layer_id is not None:
                cur.execute(
                    f"SELECT 1 FROM {_MEMORY_SCHEMA}.harness_layers WHERE layer_id=%s",
                    (layer_id,),
                )
                if cur.fetchone() is None:
                    raise ValueError(f"Unbekannter Harness-Layer: {layer_id}")
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layer_feedback
                    (entry_id,layer_id,actor,entry_type,text,payload,parent_entry_id,status)
                VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s)
                """,
                (
                    entry_id, layer_id, actor.strip(), entry_type, text.strip(),
                    json.dumps(payload or {}, ensure_ascii=False), parent_entry_id, status,
                ),
            )
        return {"entry_id": entry_id, "status": status, "snapshot": harness_layers_snapshot()}
    finally:
        conn.close()


def harness_layer_context_add(
    *,
    layer_id: str,
    actor: str,
    context_type: str,
    title: str,
    summary: str,
    reference: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context_type = str(context_type).upper().strip()
    if context_type not in {"PLAN", "VISION", "RESEARCH", "EVIDENCE", "DOC", "LINK", "NOTE"}:
        raise ValueError(f"Ungueltiger Kontext-Typ: {context_type}")
    if not layer_id.strip() or not actor.strip() or not title.strip():
        raise ValueError("layer_id, actor und title sind Pflichtfelder.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        context_id = "hlc-" + uuid.uuid4().hex
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {_MEMORY_SCHEMA}.harness_layers WHERE layer_id=%s",
                (layer_id,),
            )
            if cur.fetchone() is None:
                raise ValueError(f"Unbekannter Harness-Layer: {layer_id}")
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_layer_context
                    (context_id,layer_id,actor,context_type,title,summary,reference,metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    context_id, layer_id.strip(), actor.strip(), context_type,
                    title.strip(), summary.strip(), reference.strip(),
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
        return {"context_id": context_id, "snapshot": harness_layers_snapshot()}
    finally:
        conn.close()


def harness_feedback_list(layer_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    conn = _workflow_connection()
    if conn is None:
        return []
    try:
        _ensure_harness_layer_tables(conn)
        limit = max(1, min(int(limit), 500))
        with conn.cursor() as cur:
            if layer_id:
                cur.execute(
                    f"""
                    SELECT entry_id,layer_id,actor,entry_type,text,payload,parent_entry_id,status,
                           EXTRACT(EPOCH FROM created_at)::double precision
                    FROM {_MEMORY_SCHEMA}.harness_layer_feedback
                    WHERE layer_id=%s
                    ORDER BY created_at DESC LIMIT %s
                    """,
                    (layer_id, limit),
                )
            else:
                cur.execute(
                    f"""
                    SELECT entry_id,layer_id,actor,entry_type,text,payload,parent_entry_id,status,
                           EXTRACT(EPOCH FROM created_at)::double precision
                    FROM {_MEMORY_SCHEMA}.harness_layer_feedback
                    ORDER BY created_at DESC LIMIT %s
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
        entries = [
            {
                "entry_id": row[0], "layer_id": row[1], "actor": row[2],
                "entry_type": row[3], "text": row[4], "payload": row[5] or {},
                "parent_entry_id": row[6], "status": row[7], "created_at": row[8],
            }
            for row in rows
        ]
        decisions: dict[str, str] = {}
        for entry in entries:
            parent_id = entry.get("parent_entry_id")
            entry_type = str(entry.get("entry_type") or "").upper()
            if parent_id and entry_type in {"ACCEPT", "REJECT"} and parent_id not in decisions:
                decisions[parent_id] = "ACCEPTED" if entry_type == "ACCEPT" else "REJECTED"
        for entry in entries:
            if str(entry.get("entry_type") or "").upper() == "PROPOSAL":
                entry["status"] = decisions.get(str(entry["entry_id"]), "OPEN")
        return entries
    finally:
        conn.close()


def harness_feedback_entry(entry_id: str) -> dict[str, Any]:
    """Liest genau einen Resonanzeintrag samt aktuellem Entscheidungsstatus."""
    entry = str(entry_id or "").strip()
    if not entry:
        raise ValueError("entry_id fehlt.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT entry_id,layer_id,actor,entry_type,text,payload,parent_entry_id,status,
                       EXTRACT(EPOCH FROM created_at)::double precision
                FROM {_MEMORY_SCHEMA}.harness_layer_feedback
                WHERE entry_id=%s
                """,
                (entry,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Unbekannter Resonanzeintrag: {entry}")
            result = {
                "entry_id": row[0],
                "layer_id": row[1],
                "actor": row[2],
                "entry_type": row[3],
                "text": row[4],
                "payload": row[5] or {},
                "parent_entry_id": row[6],
                "status": row[7],
                "created_at": row[8],
            }
            if str(result["entry_type"] or "").upper() == "PROPOSAL":
                cur.execute(
                    f"""
                    SELECT entry_type
                    FROM {_MEMORY_SCHEMA}.harness_layer_feedback
                    WHERE parent_entry_id=%s AND entry_type IN ('ACCEPT','REJECT')
                    ORDER BY created_at DESC,entry_id DESC
                    LIMIT 1
                    """,
                    (entry,),
                )
                decision = cur.fetchone()
                if decision is None:
                    result["status"] = "OPEN"
                else:
                    result["status"] = "ACCEPTED" if str(decision[0]).upper() == "ACCEPT" else "REJECTED"
        return result
    finally:
        conn.close()


def harness_feedback_inbox(
    *,
    recipient: str = "CHATGPT",
    limit: int = 100,
) -> list[dict[str, Any]]:
    recipient = str(recipient or "").strip().upper()
    if not recipient:
        raise ValueError("recipient fehlt.")
    conn = _workflow_connection()
    if conn is None:
        return []
    try:
        _ensure_harness_layer_tables(conn)
        limit = max(1, min(int(limit), 500))
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT f.entry_id,f.layer_id,f.actor,f.entry_type,f.text,f.payload,
                       f.parent_entry_id,f.status,
                       EXTRACT(EPOCH FROM f.created_at)::double precision,
                       p.entry_type,p.text,p.payload
                FROM {_MEMORY_SCHEMA}.harness_layer_feedback f
                LEFT JOIN {_MEMORY_SCHEMA}.harness_feedback_receipts r
                  ON r.entry_id=f.entry_id AND r.recipient=%s
                LEFT JOIN {_MEMORY_SCHEMA}.harness_layer_feedback p
                  ON p.entry_id=f.parent_entry_id
                WHERE f.actor='DANIEL_DASHBOARD'
                  AND r.entry_id IS NULL
                ORDER BY f.created_at ASC,f.entry_id ASC
                LIMIT %s
                """,
                (recipient, limit),
            )
            rows = cur.fetchall()
        return [
            {
                "entry_id": row[0],
                "layer_id": row[1],
                "actor": row[2],
                "entry_type": row[3],
                "text": row[4],
                "payload": row[5] or {},
                "parent_entry_id": row[6],
                "status": row[7],
                "created_at": row[8],
                "parent": (
                    {
                        "entry_type": row[9],
                        "text": row[10],
                        "payload": row[11] or {},
                    }
                    if row[6] is not None
                    else None
                ),
            }
            for row in rows
        ]
    finally:
        conn.close()


def harness_feedback_ack(
    entry_id: str,
    *,
    recipient: str = "CHATGPT",
    actor: str = "CHATGPT",
    note: str = "",
) -> dict[str, Any]:
    entry_id = str(entry_id or "").strip()
    recipient = str(recipient or "").strip().upper()
    actor = str(actor or "").strip()
    if not entry_id or not recipient or not actor:
        raise ValueError("entry_id, recipient und actor sind Pflichtfelder.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {_MEMORY_SCHEMA}.harness_layer_feedback WHERE entry_id=%s",
                (entry_id,),
            )
            if cur.fetchone() is None:
                raise ValueError(f"Unbekannter Resonanzeintrag: {entry_id}")
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_feedback_receipts
                    (entry_id,recipient,ack_actor,ack_note,seen_at)
                VALUES (%s,%s,%s,%s,now())
                ON CONFLICT (entry_id,recipient)
                DO UPDATE SET ack_actor=EXCLUDED.ack_actor,
                              ack_note=EXCLUDED.ack_note,
                              seen_at=now()
                """,
                (entry_id, recipient, actor, str(note or "").strip()),
            )
        return {
            "entry_id": entry_id,
            "recipient": recipient,
            "ack_actor": actor,
            "ack_note": str(note or "").strip(),
            "remaining": harness_feedback_inbox(recipient=recipient, limit=500),
        }
    finally:
        conn.close()


def harness_control_lease_grant(
    *,
    actor: str,
    grantee: str,
    reason: str,
    layer_pattern: str = "*",
    scope: dict[str, Any] | None = None,
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    if not actor.strip() or not grantee.strip() or not reason.strip():
        raise ValueError("actor, grantee und reason sind Pflichtfelder.")
    if ttl_seconds is not None and int(ttl_seconds) <= 0:
        raise ValueError("ttl_seconds muss positiv sein oder entfallen.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        lease_id = "hcl-" + uuid.uuid4().hex
        expires_sql = "now() + (%s * interval '1 second')" if ttl_seconds is not None else "NULL"
        params: list[Any] = [
            lease_id,
            actor.strip(),
            grantee.strip(),
            layer_pattern.strip() or "*",
            json.dumps(scope or {}, ensure_ascii=False),
            reason.strip(),
        ]
        if ttl_seconds is not None:
            params.append(int(ttl_seconds))
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.harness_control_leases
                    (lease_id,actor,grantee,layer_pattern,scope,reason,expires_at)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s,{expires_sql})
                """,
                tuple(params),
            )
        return {"lease_id": lease_id, "snapshot": harness_layers_snapshot()}
    finally:
        conn.close()


def harness_control_lease_revoke(*, lease_id: str, actor: str, reason: str) -> dict[str, Any]:
    if not lease_id.strip() or not actor.strip() or not reason.strip():
        raise ValueError("lease_id, actor und reason sind Pflichtfelder.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL nicht erreichbar.")
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {_MEMORY_SCHEMA}.harness_control_leases
                SET revoked_at=now(),
                    metadata=COALESCE(metadata,'{{}}'::jsonb) ||
                             jsonb_build_object('revoked_by',%s,'revoke_reason',%s)
                WHERE lease_id=%s AND revoked_at IS NULL
                """,
                (actor.strip(), reason.strip(), lease_id.strip()),
            )
            if cur.rowcount != 1:
                raise ValueError("Aktive Control-Lease nicht gefunden.")
        return harness_layers_snapshot()
    finally:
        conn.close()


def harness_control_allowed(grantee: str, layer_id: str) -> bool:
    conn = _workflow_connection()
    if conn is None:
        return False
    try:
        _ensure_harness_layer_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT layer_pattern
                FROM {_MEMORY_SCHEMA}.harness_control_leases
                WHERE grantee=%s
                  AND revoked_at IS NULL
                  AND (expires_at IS NULL OR expires_at > now())
                """,
                (grantee,),
            )
            patterns = [str(row[0] or "*") for row in cur.fetchall()]
        return any(fnmatch.fnmatch(layer_id, pattern) for pattern in patterns)
    finally:
        conn.close()


def harness_full_activate(*, actor: str, reason: str) -> dict[str, Any]:
    if not actor.strip() or not reason.strip():
        raise ValueError("actor und reason sind Pflichtfelder.")
    snap = harness_layers_snapshot()
    for item in snap.get("layers", []):
        if item.get("effective_status") in {"ARCHIVED", "EXPIRED"}:
            continue
        harness_layer_set(
            str(item["layer_id"]),
            "ACTIVE",
            actor=actor,
            reason=reason,
            ttl_seconds=None,
        )
    return harness_layers_snapshot()


def harness_master_paused() -> bool:
    try:
        snap = harness_layers_snapshot()
        return snap.get("master", {}).get("effective_status") == "PAUSED"
    except Exception:
        return False


def _ensure_directive_tables(conn) -> None:
    """Append-only Rohtextquelle plus getrennte harte Ableitungen, Invarianten und Reminder."""
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {_MEMORY_SCHEMA}")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.directive_events (
                event_id text PRIMARY KEY,
                session_id text NOT NULL,
                raw_text text NOT NULL,
                raw_sha256 text NOT NULL,
                source_kind text NOT NULL DEFAULT 'UNVERIFIED_MODEL_CLAIM',
                idempotency_key text,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"ALTER TABLE {_MEMORY_SCHEMA}.directive_events ADD COLUMN IF NOT EXISTS idempotency_key text"
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.directive_relations (
                edge_id text PRIMARY KEY,
                from_event_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.directive_events(event_id),
                to_event_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.directive_events(event_id),
                relation text NOT NULL CHECK (relation IN ('SUPERSEDES','REFINES','CONTRADICTS','DERIVED_FROM')),
                reason text NOT NULL DEFAULT '',
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.directive_status_events (
                status_event_id text PRIMARY KEY,
                directive_event_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.directive_events(event_id),
                status text NOT NULL CHECK (status IN ('ACTIVE','ARCHIVED')),
                actor text NOT NULL,
                reason text NOT NULL DEFAULT '',
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS directive_status_events_lookup_idx "
            f"ON {_MEMORY_SCHEMA}.directive_status_events(directive_event_id,created_at DESC)"
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.directive_constraints (
                constraint_id text PRIMARY KEY,
                directive_event_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.directive_events(event_id),
                effect text NOT NULL CHECK (effect IN ('DENY','REQUIRE_REMINDER','REMIND')),
                action_pattern text NOT NULL DEFAULT '*',
                target_pattern text NOT NULL DEFAULT '*',
                statement text NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.directive_invariants (
                invariant_id text PRIMARY KEY,
                directive_event_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.directive_events(event_id),
                invariant_type text NOT NULL CHECK (invariant_type IN ('EXACT_CONTENT','PATH_STABLE','MUST_EXIST','MUST_NOT_EXIST')),
                path text NOT NULL,
                expected_sha256 text,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.directive_reminders (
                reminder_id text PRIMARY KEY,
                session_id text NOT NULL,
                action_fingerprint text NOT NULL,
                tool_name text NOT NULL,
                directive_event_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
                issued_at timestamptz NOT NULL DEFAULT now(),
                expires_at timestamptz NOT NULL
            )
            """
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS directive_events_created_idx ON {_MEMORY_SCHEMA}.directive_events(created_at DESC)"
        )
        cur.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS directive_events_idempotency_idx ON {_MEMORY_SCHEMA}.directive_events(session_id,idempotency_key) WHERE idempotency_key IS NOT NULL"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS directive_relations_to_idx ON {_MEMORY_SCHEMA}.directive_relations(to_event_id,relation)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS directive_constraints_event_idx ON {_MEMORY_SCHEMA}.directive_constraints(directive_event_id)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS directive_invariants_event_idx ON {_MEMORY_SCHEMA}.directive_invariants(directive_event_id,path)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS directive_reminders_lookup_idx ON {_MEMORY_SCHEMA}.directive_reminders(session_id,action_fingerprint,expires_at DESC)"
        )
        cur.execute(
            f"""
            CREATE OR REPLACE FUNCTION {_MEMORY_SCHEMA}.reject_directive_mutation()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'directive source is append-only: % on %.%', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
            END;
            $$
            """
        )
        for table in ("directive_events", "directive_relations", "directive_constraints", "directive_invariants"):
            cur.execute(
                """
                SELECT 1 FROM pg_trigger
                WHERE tgrelid=%s::regclass AND tgname=%s AND NOT tgisinternal
                """,
                (f"{_MEMORY_SCHEMA}.{table}", f"{table}_no_update_delete"),
            )
            if cur.fetchone() is None:
                cur.execute(
                    f"""
                    CREATE TRIGGER {table}_no_update_delete
                    BEFORE UPDATE OR DELETE ON {_MEMORY_SCHEMA}.{table}
                    FOR EACH ROW EXECUTE FUNCTION {_MEMORY_SCHEMA}.reject_directive_mutation()
                    """
                )
            cur.execute(
                """
                SELECT 1 FROM pg_trigger
                WHERE tgrelid=%s::regclass AND tgname=%s AND NOT tgisinternal
                """,
                (f"{_MEMORY_SCHEMA}.{table}", f"{table}_no_truncate"),
            )
            if cur.fetchone() is None:
                cur.execute(
                    f"""
                    CREATE TRIGGER {table}_no_truncate
                    BEFORE TRUNCATE ON {_MEMORY_SCHEMA}.{table}
                    FOR EACH STATEMENT EXECUTE FUNCTION {_MEMORY_SCHEMA}.reject_directive_mutation()
                    """
                )


def _ensure_experience_tables(conn) -> None:
    """Unverfaelschte, append-only Erfahrungsschicht fuer Chat-Turns und reale Aktionen."""
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {_MEMORY_SCHEMA}")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.experience_messages (
                message_id text PRIMARY KEY,
                turn_id text NOT NULL,
                session_id text NOT NULL,
                role text NOT NULL CHECK (role IN ('USER','ASSISTANT','USER_REACTION')),
                raw_text text NOT NULL,
                raw_sha256 text NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.experience_actions (
                action_id text PRIMARY KEY,
                turn_id text,
                session_id text NOT NULL,
                tool_name text NOT NULL,
                arguments jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                decision jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                result jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                ok boolean NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.experience_evaluations (
                evaluation_id text PRIMARY KEY,
                turn_id text NOT NULL,
                session_id text NOT NULL,
                trigger_kind text NOT NULL,
                needs_review boolean NOT NULL,
                metrics jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                summary text NOT NULL DEFAULT '',
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS experience_messages_session_idx "
            f"ON {_MEMORY_SCHEMA}.experience_messages(session_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS experience_messages_turn_idx "
            f"ON {_MEMORY_SCHEMA}.experience_messages(turn_id,created_at)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS experience_actions_turn_idx "
            f"ON {_MEMORY_SCHEMA}.experience_actions(turn_id,created_at)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS experience_evaluations_turn_idx "
            f"ON {_MEMORY_SCHEMA}.experience_evaluations(turn_id,created_at)"
        )
        cur.execute(
            f"""
            CREATE OR REPLACE FUNCTION {_MEMORY_SCHEMA}.reject_experience_mutation()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'experience source is append-only: % on %.%', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
            END;
            $$
            """
        )
        for table in ("experience_messages", "experience_actions", "experience_evaluations"):
            for suffix, timing in (
                ("no_update_delete", "BEFORE UPDATE OR DELETE"),
                ("no_truncate", "BEFORE TRUNCATE"),
            ):
                trigger_name = f"{table}_{suffix}"
                cur.execute(
                    """
                    SELECT 1 FROM pg_trigger
                    WHERE tgrelid=%s::regclass AND tgname=%s AND NOT tgisinternal
                    """,
                    (f"{_MEMORY_SCHEMA}.{table}", trigger_name),
                )
                if cur.fetchone() is None:
                    scope = "FOR EACH ROW" if suffix == "no_update_delete" else "FOR EACH STATEMENT"
                    cur.execute(
                        f"""
                        CREATE TRIGGER {trigger_name}
                        {timing} ON {_MEMORY_SCHEMA}.{table}
                        {scope} EXECUTE FUNCTION {_MEMORY_SCHEMA}.reject_experience_mutation()
                        """
                    )


def _current_experience_turn(conn, session_id: str) -> str | None:
    _ensure_experience_tables(conn)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT turn_id
            FROM {_MEMORY_SCHEMA}.experience_messages
            WHERE session_id=%s AND role='USER'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (session_id,),
        )
        row = cur.fetchone()
    return str(row[0]) if row else None


def record_experience_message(
    raw_text: str,
    *,
    role: str,
    session_id: str | None = None,
    turn_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Speichert genau den gelieferten Text; keine Zusammenfassung und keine Umformulierung."""
    if not isinstance(raw_text, str) or not raw_text:
        raise ValueError("Erfahrungsnachricht braucht unveraenderten nichtleeren Rohtext.")
    normalized_role = str(role or "").strip().upper()
    if normalized_role not in {"USER", "ASSISTANT", "USER_REACTION"}:
        raise ValueError(f"Unbekannte Erfahrungsrolle: {normalized_role}")
    key = _session_key({"session_id": session_id} if session_id else {})
    raw_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Erfahrungsschicht nicht erreichbar; kein fluechtiger Fallback.")
    try:
        _ensure_experience_tables(conn)
        actual_turn = str(turn_id or "").strip()
        reaction_turn_for_evaluation: str | None = None
        if not actual_turn:
            if normalized_role == "USER":
                previous_turn = _current_experience_turn(conn, key)
                if previous_turn:
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            SELECT 1
                            FROM {_MEMORY_SCHEMA}.experience_messages
                            WHERE turn_id=%s AND role='ASSISTANT'
                            LIMIT 1
                            """,
                            (previous_turn,),
                        )
                        previous_has_assistant = cur.fetchone() is not None
                    if previous_has_assistant:
                        reaction_id = "m-" + uuid.uuid4().hex
                        with conn.cursor() as cur:
                            cur.execute(
                                f"""
                                INSERT INTO {_MEMORY_SCHEMA}.experience_messages
                                    (message_id,turn_id,session_id,role,raw_text,raw_sha256,metadata)
                                VALUES (%s,%s,%s,'USER_REACTION',%s,%s,%s::jsonb)
                                """,
                                (
                                    reaction_id,
                                    previous_turn,
                                    key,
                                    raw_text,
                                    raw_sha256,
                                    json.dumps(
                                        {
                                            "automatic_link": True,
                                            "reason": "naechster Nutzerinput nach Assistant-Ausgabe",
                                        },
                                        ensure_ascii=False,
                                    ),
                                ),
                            )
                        reaction_turn_for_evaluation = previous_turn
                actual_turn = "t-" + uuid.uuid4().hex
            else:
                actual_turn = _current_experience_turn(conn, key) or ("t-" + uuid.uuid4().hex)
        message_id = "m-" + uuid.uuid4().hex
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.experience_messages
                    (message_id,turn_id,session_id,role,raw_text,raw_sha256,metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    message_id,
                    actual_turn,
                    key,
                    normalized_role,
                    raw_text,
                    raw_sha256,
                    json.dumps(metadata if isinstance(metadata, dict) else {}, ensure_ascii=False),
                ),
            )

        automatic_evaluations: list[dict[str, Any]] = []
        if normalized_role in {"ASSISTANT", "USER_REACTION"}:
            try:
                automatic_evaluations.append(
                    evaluate_experience_turn(
                        actual_turn,
                        session_id=key,
                        trigger_kind=normalized_role,
                    )
                )
            except Exception:
                pass
        if reaction_turn_for_evaluation:
            try:
                automatic_evaluations.append(
                    evaluate_experience_turn(
                        reaction_turn_for_evaluation,
                        session_id=key,
                        trigger_kind="NEXT_USER_REACTION",
                    )
                )
            except Exception:
                pass

        return {
            "message_id": message_id,
            "turn_id": actual_turn,
            "session_id": key,
            "role": normalized_role,
            "raw_sha256": raw_sha256,
            "immutable_source": True,
            "automatic_evaluations": automatic_evaluations,
        }
    finally:
        conn.close()


def _record_experience_action(
    tool_name: str,
    args: dict[str, Any],
    decision: "WorkflowDecision",
    result: dict[str, Any],
) -> None:
    """Schreibt die reale Toolhandlung und ihr reales Ergebnis automatisch append-only."""
    key = _session_key(args)
    conn = _workflow_connection()
    if conn is None:
        return
    try:
        _ensure_experience_tables(conn)
        turn_id = _current_experience_turn(conn, key)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.experience_actions
                    (action_id,turn_id,session_id,tool_name,arguments,decision,result,ok)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s)
                """,
                (
                    "a-" + uuid.uuid4().hex,
                    turn_id,
                    key,
                    str(tool_name),
                    json.dumps(args or {}, ensure_ascii=False, default=str),
                    json.dumps(decision.to_dict(), ensure_ascii=False, default=str),
                    json.dumps(result or {}, ensure_ascii=False, default=str),
                    bool((result or {}).get("ok")),
                ),
            )
    finally:
        conn.close()


def evaluate_experience_turn(
    turn_id: str,
    *,
    session_id: str | None = None,
    trigger_kind: str = "TURN_COMPLETE",
) -> dict[str, Any]:
    """Kleine deterministische Turn-Auswertung; keine LLM-Deutung."""
    turn = str(turn_id or "").strip()
    if not turn:
        raise ValueError("Turn-Auswertung braucht turn_id.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Erfahrungsauswertung nicht erreichbar.")
    try:
        _ensure_experience_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT session_id,role,raw_sha256,created_at
                FROM {_MEMORY_SCHEMA}.experience_messages
                WHERE turn_id=%s
                ORDER BY created_at,message_id
                """,
                (turn,),
            )
            messages = list(cur.fetchall())
            cur.execute(
                f"""
                SELECT action_id,tool_name,arguments,decision,result,ok,created_at
                FROM {_MEMORY_SCHEMA}.experience_actions
                WHERE turn_id=%s
                ORDER BY created_at,action_id
                """,
                (turn,),
            )
            actions = list(cur.fetchall())

        if not messages and not actions:
            raise ValueError(f"Unbekannter Turn: {turn}")
        key = str(session_id or (messages[0][0] if messages else "default"))
        role_counts: dict[str, int] = {}
        for _session, role, _sha, _created in messages:
            role_counts[str(role)] = role_counts.get(str(role), 0) + 1

        failed_action_ids: list[str] = []
        blocked_action_ids: list[str] = []
        mutation_action_ids: list[str] = []
        move_action_ids: list[str] = []
        unverified_mutation_ids: list[str] = []
        mutation_nodes = {
            NODE_SINGLE_EDIT,
            NODE_SINGLE_WRITE,
            NODE_SINGLE_DELETE,
            NODE_SINGLE_MOVE,
            NODE_META_GENERATION,
            NODE_CONTROL_RESTART,
        }

        normalized_actions: list[dict[str, Any]] = []
        for action_id, tool_name, arguments, decision, result, ok, created_at in actions:
            action = {
                "action_id": str(action_id),
                "tool_name": str(tool_name),
                "arguments": arguments if isinstance(arguments, dict) else {},
                "decision": decision if isinstance(decision, dict) else {},
                "result": result if isinstance(result, dict) else {},
                "ok": bool(ok),
                "created_at": created_at,
            }
            normalized_actions.append(action)
            if not action["ok"]:
                failed_action_ids.append(action["action_id"])
            if str(action["decision"].get("decision") or "") == DECISION_BLOCK:
                blocked_action_ids.append(action["action_id"])
            if str(action["decision"].get("action_node") or "") in mutation_nodes:
                mutation_action_ids.append(action["action_id"])
            if action["tool_name"] == "vps.move":
                move_action_ids.append(action["action_id"])

        for index, action in enumerate(normalized_actions):
            node = str(action["decision"].get("action_node") or "")
            if not action["ok"] or node not in mutation_nodes or node == NODE_SINGLE_DELETE:
                continue
            arguments = action["arguments"]
            target = str(arguments.get("path") or arguments.get("source") or "").strip()
            if not target:
                continue
            verified = False
            for later in normalized_actions[index + 1:]:
                later_node = str(later["decision"].get("action_node") or "")
                if later_node in mutation_nodes and later["ok"]:
                    break
                if (
                    later["ok"]
                    and later["tool_name"] == "vps.read_file"
                    and str(later["arguments"].get("path") or "").strip() == target
                    and later["arguments"].get("start_line") is None
                    and later["arguments"].get("end_line") is None
                ):
                    verified = True
                    break
            if not verified:
                unverified_mutation_ids.append(action["action_id"])

        metrics = {
            "message_count": len(messages),
            "role_counts": role_counts,
            "action_count": len(actions),
            "failed_action_ids": failed_action_ids,
            "blocked_action_ids": blocked_action_ids,
            "mutation_action_ids": mutation_action_ids,
            "move_action_ids": move_action_ids,
            "unverified_mutation_ids": unverified_mutation_ids,
            "has_user_reaction": role_counts.get("USER_REACTION", 0) > 0,
        }
        needs_review = bool(failed_action_ids or blocked_action_ids or unverified_mutation_ids)
        summary = (
            f"{len(actions)} Aktionen; "
            f"{len(failed_action_ids)} Fehler; "
            f"{len(blocked_action_ids)} Blocks; "
            f"{len(mutation_action_ids)} Mutationen; "
            f"{len(unverified_mutation_ids)} Mutation(en) ohne direkte Ruecklesung."
        )
        evaluation_id = "ev-" + uuid.uuid4().hex
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.experience_evaluations
                    (evaluation_id,turn_id,session_id,trigger_kind,needs_review,metrics,summary)
                VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s)
                """,
                (
                    evaluation_id,
                    turn,
                    key,
                    str(trigger_kind or "TURN_COMPLETE"),
                    needs_review,
                    json.dumps(metrics, ensure_ascii=False),
                    summary,
                ),
            )
        drift_point = None
        if needs_review:
            try:
                drift_point = find_drift_point(turn, session_id=key)
            except Exception as exc:
                drift_point = {
                    "found": False,
                    "error": f"Driftpunktsuche fehlgeschlagen: {exc}",
                }
        try:
            learning_reassessment = _reassess_session_learning_rules(key)
        except Exception as exc:
            learning_reassessment = [{"error": str(exc)}]
        return {
            "evaluation_id": evaluation_id,
            "turn_id": turn,
            "session_id": key,
            "needs_review": needs_review,
            "metrics": metrics,
            "summary": summary,
            "drift_point": drift_point,
            "learning_reassessment": learning_reassessment,
        }
    finally:
        conn.close()


def _ensure_learning_tables(conn) -> None:
    """Persistente Lernspur; Roh-Erfahrung bleibt getrennt und unveraendert."""
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {_MEMORY_SCHEMA}")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.experience_drift_points (
                drift_id text PRIMARY KEY,
                turn_id text NOT NULL,
                session_id text NOT NULL,
                source_kind text NOT NULL CHECK (source_kind IN ('DETERMINISTIC','CHATGPT_SELF_OBSERVED')),
                action_id text,
                drift_code text NOT NULL,
                description text NOT NULL,
                evidence jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.learning_rules (
                rule_id text PRIMARY KEY,
                source_drift_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.experience_drift_points(drift_id),
                session_id text NOT NULL,
                rule_kind text NOT NULL,
                rule_text text NOT NULL,
                rule_sha256 text NOT NULL,
                condition jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                enforcement jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.learning_rule_events (
                event_id text PRIMARY KEY,
                rule_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.learning_rules(rule_id),
                status text NOT NULL CHECK (status IN ('CANDIDATE','TESTING','ACTIVE','WEAKENED','SUPERSEDED','RETIRED')),
                reason text NOT NULL DEFAULT '',
                metrics jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.learning_rule_tests (
                test_id text PRIMARY KEY,
                rule_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.learning_rules(rule_id),
                turn_id text NOT NULL,
                matched boolean NOT NULL,
                source_covered boolean NOT NULL,
                would_block_success boolean NOT NULL,
                details jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.learning_rule_feedback (
                feedback_id text PRIMARY KEY,
                rule_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.learning_rules(rule_id),
                turn_id text,
                source_kind text NOT NULL CHECK (source_kind IN ('DETERMINISTIC','CHATGPT_SELF_OBSERVED','DANIEL_DASHBOARD')),
                outcome text NOT NULL CHECK (outcome IN ('HELPFUL','HARMFUL','IRRELEVANT','CONTRADICTED')),
                evidence jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=%s
              AND t.relname='learning_rule_feedback'
              AND c.conname='learning_rule_feedback_source_kind_check'
            """,
            (_MEMORY_SCHEMA,),
        )
        learning_feedback_source_constraint = cur.fetchone()
        if learning_feedback_source_constraint is not None and "DANIEL_DASHBOARD" not in str(learning_feedback_source_constraint[0]):
            cur.execute(
                f"ALTER TABLE {_MEMORY_SCHEMA}.learning_rule_feedback "
                "DROP CONSTRAINT learning_rule_feedback_source_kind_check"
            )
            cur.execute(
                f"""
                ALTER TABLE {_MEMORY_SCHEMA}.learning_rule_feedback
                ADD CONSTRAINT learning_rule_feedback_source_kind_check
                CHECK (source_kind IN ('DETERMINISTIC','CHATGPT_SELF_OBSERVED','DANIEL_DASHBOARD'))
                """
            )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS experience_drift_turn_idx "
            f"ON {_MEMORY_SCHEMA}.experience_drift_points(turn_id,created_at)"
        )
        cur.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS learning_rules_drift_hash_idx "
            f"ON {_MEMORY_SCHEMA}.learning_rules(source_drift_id,rule_sha256)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS learning_rule_events_rule_idx "
            f"ON {_MEMORY_SCHEMA}.learning_rule_events(rule_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS learning_rule_tests_rule_idx "
            f"ON {_MEMORY_SCHEMA}.learning_rule_tests(rule_id,created_at DESC)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS learning_rule_feedback_rule_idx "
            f"ON {_MEMORY_SCHEMA}.learning_rule_feedback(rule_id,created_at DESC)"
        )
        cur.execute(
            f"""
            CREATE OR REPLACE FUNCTION {_MEMORY_SCHEMA}.reject_learning_source_mutation()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'learning source is append-only: % on %.%', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
            END;
            $$
            """
        )
        for table in ("experience_drift_points", "learning_rules", "learning_rule_events", "learning_rule_tests", "learning_rule_feedback"):
            for suffix, timing in (
                ("no_update_delete", "BEFORE UPDATE OR DELETE"),
                ("no_truncate", "BEFORE TRUNCATE"),
            ):
                trigger_name = f"{table}_{suffix}"
                cur.execute(
                    """
                    SELECT 1 FROM pg_trigger
                    WHERE tgrelid=%s::regclass AND tgname=%s AND NOT tgisinternal
                    """,
                    (f"{_MEMORY_SCHEMA}.{table}", trigger_name),
                )
                if cur.fetchone() is None:
                    scope = "FOR EACH ROW" if suffix == "no_update_delete" else "FOR EACH STATEMENT"
                    cur.execute(
                        f"""
                        CREATE TRIGGER {trigger_name}
                        {timing} ON {_MEMORY_SCHEMA}.{table}
                        {scope} EXECUTE FUNCTION {_MEMORY_SCHEMA}.reject_learning_source_mutation()
                        """
                    )


def find_drift_point(
    turn_id: str,
    *,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Findet den ersten deterministisch belegbaren Driftpunkt eines Turns."""
    turn = str(turn_id or "").strip()
    if not turn:
        raise ValueError("Driftpunktsuche braucht turn_id.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Driftpunktsuche nicht erreichbar.")
    try:
        _ensure_experience_tables(conn)
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT session_id
                FROM {_MEMORY_SCHEMA}.experience_messages
                WHERE turn_id=%s
                ORDER BY created_at
                LIMIT 1
                """,
                (turn,),
            )
            session_row = cur.fetchone()
            key = str(session_id or (session_row[0] if session_row else "default"))
            cur.execute(
                f"""
                SELECT action_id,tool_name,arguments,decision,result,ok,created_at
                FROM {_MEMORY_SCHEMA}.experience_actions
                WHERE turn_id=%s
                ORDER BY created_at,action_id
                """,
                (turn,),
            )
            actions = list(cur.fetchall())
            cur.execute(
                f"""
                SELECT metrics
                FROM {_MEMORY_SCHEMA}.experience_evaluations
                WHERE turn_id=%s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (turn,),
            )
            evaluation_row = cur.fetchone()

        selected: dict[str, Any] | None = None
        for action_id, tool_name, arguments, decision, result, ok, created_at in actions:
            decision_data = decision if isinstance(decision, dict) else {}
            if str(decision_data.get("decision") or "") == DECISION_BLOCK:
                task_scope_block = str(decision_data.get("action_node") or "") == NODE_TASK_SCOPE
                selected = {
                    "action_id": str(action_id),
                    "drift_code": "TASK_SCOPE_BLOCK" if task_scope_block else "FIRST_BLOCKED_ACTION",
                    "description": (
                        "Aktion lag ausserhalb des aktiven verifizierten Task-Scope und wurde bewusst geparkt."
                        if task_scope_block
                        else "Erste vom bestehenden Kontrollgraphen blockierte Aktion."
                    ),
                    "evidence": {
                        "tool_name": str(tool_name),
                        "arguments": arguments if isinstance(arguments, dict) else {},
                        "decision": decision_data,
                        "parked_sidequest": bool(task_scope_block),
                    },
                }
                break
            if not bool(ok):
                selected = {
                    "action_id": str(action_id),
                    "drift_code": "FIRST_FAILED_ACTION",
                    "description": "Erste ausgefuehrte Aktion mit fehlgeschlagenem Ergebnis.",
                    "evidence": {
                        "tool_name": str(tool_name),
                        "arguments": arguments if isinstance(arguments, dict) else {},
                        "result": result if isinstance(result, dict) else {},
                    },
                }
                break

        if selected is None and evaluation_row and isinstance(evaluation_row[0], dict):
            unverified = list(evaluation_row[0].get("unverified_mutation_ids") or [])
            if unverified:
                first_id = str(unverified[0])
                selected = {
                    "action_id": first_id,
                    "drift_code": "MUTATION_NOT_REREAD",
                    "description": "Erste erfolgreiche Mutation, deren konkretes Ziel im Turn nicht vollstaendig rueckgelesen wurde.",
                    "evidence": {"action_id": first_id},
                }

        if selected is None:
            return {
                "turn_id": turn,
                "session_id": key,
                "found": False,
                "reason": "Kein deterministisch belegbarer Driftpunkt gefunden.",
            }

        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT drift_id
                FROM {_MEMORY_SCHEMA}.experience_drift_points
                WHERE turn_id=%s AND source_kind='DETERMINISTIC'
                  AND drift_code=%s AND COALESCE(action_id,'')=%s
                ORDER BY created_at
                LIMIT 1
                """,
                (turn, selected["drift_code"], selected.get("action_id") or ""),
            )
            existing = cur.fetchone()
            if existing:
                existing_drift_id = str(existing[0])
                try:
                    candidate_rule = propose_candidate_rule(existing_drift_id, session_id=key)
                except Exception as exc:
                    candidate_rule = {"created": False, "error": str(exc)}
                return {
                    "drift_id": existing_drift_id,
                    "turn_id": turn,
                    "session_id": key,
                    "found": True,
                    "deduplicated": True,
                    "candidate_rule": candidate_rule,
                    **selected,
                }
            drift_id = "dr-" + uuid.uuid4().hex
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.experience_drift_points
                    (drift_id,turn_id,session_id,source_kind,action_id,drift_code,description,evidence)
                VALUES (%s,%s,%s,'DETERMINISTIC',%s,%s,%s,%s::jsonb)
                """,
                (
                    drift_id,
                    turn,
                    key,
                    selected.get("action_id"),
                    selected["drift_code"],
                    selected["description"],
                    json.dumps(selected["evidence"], ensure_ascii=False, default=str),
                ),
            )
        try:
            candidate_rule = propose_candidate_rule(drift_id, session_id=key)
        except Exception as exc:
            candidate_rule = {"created": False, "error": str(exc)}
        return {
            "drift_id": drift_id,
            "turn_id": turn,
            "session_id": key,
            "found": True,
            "deduplicated": False,
            "candidate_rule": candidate_rule,
            **selected,
        }
    finally:
        conn.close()


def record_self_observed_drift(
    turn_id: str,
    description: str,
    *,
    session_id: str | None = None,
    action_id: str | None = None,
    drift_code: str = "SELF_OBSERVED_DRIFT",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """ChatGPT-eigene Beobachtung; behauptet ausdruecklich keine Nutzerkorrektur."""
    turn = str(turn_id or "").strip()
    text = str(description or "").strip()
    if not turn or not text:
        raise ValueError("Selbstbeobachteter Drift braucht turn_id und description.")
    key = _session_key({"session_id": session_id} if session_id else {})
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer selbstbeobachteten Drift nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        drift_id = "dr-" + uuid.uuid4().hex
        payload = dict(evidence or {})
        payload["attribution"] = "ChatGPT hat die Abweichung selbst beobachtet; keine Nutzerkorrektur behauptet."
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.experience_drift_points
                    (drift_id,turn_id,session_id,source_kind,action_id,drift_code,description,evidence)
                VALUES (%s,%s,%s,'CHATGPT_SELF_OBSERVED',%s,%s,%s,%s::jsonb)
                """,
                (
                    drift_id,
                    turn,
                    key,
                    str(action_id or "") or None,
                    str(drift_code or "SELF_OBSERVED_DRIFT"),
                    text,
                    json.dumps(payload, ensure_ascii=False, default=str),
                ),
            )
        return {
            "drift_id": drift_id,
            "turn_id": turn,
            "session_id": key,
            "source_kind": "CHATGPT_SELF_OBSERVED",
            "description": text,
        }
    finally:
        conn.close()


def _default_candidate_for_drift(
    drift_code: str,
    evidence: dict[str, Any],
) -> dict[str, Any] | None:
    code = str(drift_code or "")
    if code == "MUTATION_NOT_REREAD":
        return {
            "rule_kind": "REQUIRE_REREAD_AFTER_MUTATION",
            "rule_text": "Nach einer erfolgreichen Mutation muss das konkrete Ziel vollstaendig rueckgelesen werden, bevor der Lauf als erfolgreich gilt.",
            "condition": {"after_successful_mutation": True},
            "enforcement": {"type": "REQUIRE_REREAD_SAME_TARGET"},
        }
    if code == "FIRST_BLOCKED_ACTION":
        tool_name = str(evidence.get("tool_name") or "")
        return {
            "rule_kind": "AVOID_REPEAT_BLOCKED_ACTION",
            "rule_text": "Eine bereits blockierte Aktion darf nicht unveraendert erneut versucht werden; zuerst muss die konkrete Blockursache behoben oder der Auftrag neu belegt werden.",
            "condition": {"tool_name": tool_name, "after_same_action_block": True},
            "enforcement": {"type": "REQUIRE_RECOVERY_BEFORE_REPEAT"},
        }
    if code == "FIRST_FAILED_ACTION":
        tool_name = str(evidence.get("tool_name") or "")
        return {
            "rule_kind": "REQUIRE_RECOVERY_AFTER_FAILURE",
            "rule_text": "Nach einer fehlgeschlagenen Toolaktion darf Erfolg nicht angenommen werden; vor einer Wiederholung muss die Fehlerlage erneut geprueft werden.",
            "condition": {"tool_name": tool_name, "after_failed_action": True},
            "enforcement": {"type": "REQUIRE_RECOVERY_BEFORE_REPEAT"},
        }
    return None


def propose_candidate_rule(
    drift_id: str,
    *,
    rule_text: str | None = None,
    rule_kind: str | None = None,
    condition: dict[str, Any] | None = None,
    enforcement: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Erzeugt nur CANDIDATE; nie direkte Aktivierung."""
    drift = str(drift_id or "").strip()
    if not drift:
        raise ValueError("Kandidatenregel braucht drift_id.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Kandidatenregel nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT session_id,drift_code,description,evidence
                FROM {_MEMORY_SCHEMA}.experience_drift_points
                WHERE drift_id=%s
                """,
                (drift,),
            )
            row = cur.fetchone()
        if row is None:
            raise ValueError(f"Unbekannter Driftpunkt: {drift}")
        drift_session, drift_code, drift_description, drift_evidence = row
        evidence_data = drift_evidence if isinstance(drift_evidence, dict) else {}
        defaults = _default_candidate_for_drift(str(drift_code), evidence_data)
        if not str(rule_text or "").strip():
            if defaults is None:
                return {
                    "created": False,
                    "drift_id": drift,
                    "reason": "Fuer diesen Drift gibt es keine sichere deterministische Kandidatenregel.",
                }
            rule_text = str(defaults["rule_text"])
            rule_kind = str(rule_kind or defaults["rule_kind"])
            condition = dict(condition or defaults["condition"])
            enforcement = dict(enforcement or defaults["enforcement"])
        text = str(rule_text).strip()
        kind = str(rule_kind or "SELF_OBSERVED_CANDIDATE").strip()
        condition_data = dict(condition or {})
        enforcement_data = dict(enforcement or {})
        key = str(session_id or drift_session or "default")
        rule_sha = hashlib.sha256(
            json.dumps(
                {
                    "rule_kind": kind,
                    "rule_text": text,
                    "condition": condition_data,
                    "enforcement": enforcement_data,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT rule_id
                FROM {_MEMORY_SCHEMA}.learning_rules
                WHERE source_drift_id=%s AND rule_sha256=%s
                LIMIT 1
                """,
                (drift, rule_sha),
            )
            existing = cur.fetchone()
            if existing:
                return {
                    "created": False,
                    "deduplicated": True,
                    "rule_id": str(existing[0]),
                    "drift_id": drift,
                    "status": "CANDIDATE",
                }
            rule_id = "lr-" + uuid.uuid4().hex
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rules
                    (rule_id,source_drift_id,session_id,rule_kind,rule_text,rule_sha256,condition,enforcement)
                VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
                """,
                (
                    rule_id,
                    drift,
                    key,
                    kind,
                    text,
                    rule_sha,
                    json.dumps(condition_data, ensure_ascii=False, default=str),
                    json.dumps(enforcement_data, ensure_ascii=False, default=str),
                ),
            )
            event_id = "lre-" + uuid.uuid4().hex
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_events
                    (event_id,rule_id,status,reason,metrics)
                VALUES (%s,%s,'CANDIDATE',%s,%s::jsonb)
                """,
                (
                    event_id,
                    rule_id,
                    "Aus Driftpunkt abgeleitet; noch nicht gegen alte Traces getestet.",
                    json.dumps(
                        {
                            "source_drift_code": str(drift_code),
                            "source_drift_description": str(drift_description),
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
        try:
            learning_cycle = run_learning_cycle(rule_id)
        except Exception as exc:
            learning_cycle = {
                "rule_id": rule_id,
                "regression_test": {
                    "status": "CANDIDATE",
                    "error": f"Regressionstest/Lernzyklus fehlgeschlagen: {exc}",
                },
                "activation": {
                    "activated": False,
                    "status": "CANDIDATE",
                },
            }
        activation = dict(learning_cycle.get("activation") or {})
        regression_test = dict(learning_cycle.get("regression_test") or {})
        return {
            "created": True,
            "deduplicated": False,
            "rule_id": rule_id,
            "drift_id": drift,
            "status": str(activation.get("status") or regression_test.get("status") or "CANDIDATE"),
            "rule_kind": kind,
            "rule_text": text,
            "condition": condition_data,
            "enforcement": enforcement_data,
            "learning_cycle": learning_cycle,
        }
    finally:
        conn.close()


def test_candidate_rule(
    rule_id: str,
    *,
    limit: int = 200,
) -> dict[str, Any]:
    """Spielt eine Kandidatenregel deterministisch gegen gespeicherte alte Turns."""
    rule = str(rule_id or "").strip()
    if not rule:
        raise ValueError("Regeltest braucht rule_id.")
    limit = max(1, min(int(limit), 1000))
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Regeltest nicht erreichbar.")
    try:
        _ensure_experience_tables(conn)
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT r.session_id,r.rule_kind,r.condition,r.enforcement,
                       d.turn_id,d.action_id
                FROM {_MEMORY_SCHEMA}.learning_rules r
                JOIN {_MEMORY_SCHEMA}.experience_drift_points d
                  ON d.drift_id=r.source_drift_id
                WHERE r.rule_id=%s
                """,
                (rule,),
            )
            row = cur.fetchone()
        if row is None:
            raise ValueError(f"Unbekannte Kandidatenregel: {rule}")
        session_id, rule_kind, condition, enforcement, source_turn, source_action = row
        condition_data = condition if isinstance(condition, dict) else {}
        enforcement_data = enforcement if isinstance(enforcement, dict) else {}

        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_events
                    (event_id,rule_id,status,reason,metrics)
                VALUES (%s,%s,'TESTING',%s,%s::jsonb)
                """,
                (
                    "lre-" + uuid.uuid4().hex,
                    rule,
                    "Kandidatenregel wird gegen gespeicherte alte Turns getestet.",
                    json.dumps({"limit": limit}, ensure_ascii=False),
                ),
            )
            cur.execute(
                f"""
                SELECT turn_id, max(created_at) AS last_seen
                FROM (
                    SELECT turn_id,created_at
                    FROM {_MEMORY_SCHEMA}.experience_messages
                    WHERE session_id=%s
                    UNION ALL
                    SELECT turn_id,created_at
                    FROM {_MEMORY_SCHEMA}.experience_actions
                    WHERE session_id=%s AND turn_id IS NOT NULL
                ) q
                GROUP BY turn_id
                ORDER BY last_seen DESC
                LIMIT %s
                """,
                (str(session_id), str(session_id), limit),
            )
            turn_ids = [str(item[0]) for item in cur.fetchall()]

        results: list[dict[str, Any]] = []
        source_covered_any = False
        success_collisions = 0
        matched_turns = 0

        for turn in turn_ids:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT action_id,tool_name,arguments,decision,result,ok,created_at
                    FROM {_MEMORY_SCHEMA}.experience_actions
                    WHERE turn_id=%s
                    ORDER BY created_at,action_id
                    """,
                    (turn,),
                )
                action_rows = list(cur.fetchall())
                cur.execute(
                    f"""
                    SELECT metrics
                    FROM {_MEMORY_SCHEMA}.experience_evaluations
                    WHERE turn_id=%s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (turn,),
                )
                evaluation_row = cur.fetchone()

            actions = [
                {
                    "action_id": str(action_id),
                    "tool_name": str(tool_name),
                    "arguments": arguments if isinstance(arguments, dict) else {},
                    "decision": decision if isinstance(decision, dict) else {},
                    "result": result if isinstance(result, dict) else {},
                    "ok": bool(ok),
                }
                for action_id, tool_name, arguments, decision, result, ok, _created_at in action_rows
            ]
            metrics = (
                evaluation_row[0]
                if evaluation_row and isinstance(evaluation_row[0], dict)
                else {}
            )
            matched = False
            source_covered = False
            would_block_success = False
            details: dict[str, Any] = {
                "rule_kind": str(rule_kind),
                "condition": condition_data,
                "enforcement": enforcement_data,
            }

            if str(rule_kind) == "REQUIRE_REREAD_AFTER_MUTATION":
                mutation_ids = list(metrics.get("mutation_action_ids") or [])
                unverified_ids = list(metrics.get("unverified_mutation_ids") or [])
                matched = bool(mutation_ids)
                source_covered = (
                    turn == str(source_turn)
                    and str(source_action or "") in {str(x) for x in unverified_ids}
                )
                would_block_success = False
                details.update(
                    {
                        "mutation_count": len(mutation_ids),
                        "unverified_count": len(unverified_ids),
                    }
                )
            elif str(rule_kind) in {"AVOID_REPEAT_BLOCKED_ACTION", "REQUIRE_RECOVERY_AFTER_FAILURE"}:
                target_tool = str(condition_data.get("tool_name") or "")
                waiting_for_recovery = False
                trigger_action_ids: list[str] = []
                prevented_action_ids: list[str] = []
                for action in actions:
                    if (
                        waiting_for_recovery
                        and action["ok"]
                        and action["tool_name"] == "vps.read_file"
                        and action["arguments"].get("start_line") is None
                        and action["arguments"].get("end_line") is None
                    ):
                        waiting_for_recovery = False
                        continue
                    if action["tool_name"] != target_tool:
                        continue
                    blocked = str(action["decision"].get("decision") or "") == DECISION_BLOCK
                    failed = not action["ok"]
                    is_trigger = (
                        blocked
                        if str(rule_kind) == "AVOID_REPEAT_BLOCKED_ACTION"
                        else failed
                    )
                    if not waiting_for_recovery and is_trigger:
                        waiting_for_recovery = True
                        trigger_action_ids.append(action["action_id"])
                        if turn == str(source_turn) and action["action_id"] == str(source_action or ""):
                            source_covered = True
                        continue
                    if waiting_for_recovery:
                        matched = True
                        prevented_action_ids.append(action["action_id"])
                        if action["ok"]:
                            would_block_success = True
                matched = matched or bool(trigger_action_ids)
                details.update(
                    {
                        "target_tool": target_tool,
                        "trigger_action_ids": trigger_action_ids,
                        "prevented_action_ids": prevented_action_ids,
                    }
                )
            else:
                matched = False
                source_covered = False
                would_block_success = False
                details["unsupported_for_deterministic_replay"] = True
                details["activation_blocked"] = True

            if matched:
                matched_turns += 1
            if source_covered:
                source_covered_any = True
            if would_block_success:
                success_collisions += 1

            test_id = "lrt-" + uuid.uuid4().hex
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.learning_rule_tests
                        (test_id,rule_id,turn_id,matched,source_covered,would_block_success,details)
                    VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    (
                        test_id,
                        rule,
                        turn,
                        matched,
                        source_covered,
                        would_block_success,
                        json.dumps(details, ensure_ascii=False, default=str),
                    ),
                )
            results.append(
                {
                    "test_id": test_id,
                    "turn_id": turn,
                    "matched": matched,
                    "source_covered": source_covered,
                    "would_block_success": would_block_success,
                }
            )

        passed_for_activation = bool(source_covered_any and success_collisions == 0)
        summary = {
            "tested_turns": len(turn_ids),
            "matched_turns": matched_turns,
            "source_covered": source_covered_any,
            "success_collisions": success_collisions,
            "passed_for_activation": passed_for_activation,
        }
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_events
                    (event_id,rule_id,status,reason,metrics)
                VALUES (%s,%s,'TESTING',%s,%s::jsonb)
                """,
                (
                    "lre-" + uuid.uuid4().hex,
                    rule,
                    "Regressionstest abgeschlossen; Aktivierung bleibt ein separater Schritt.",
                    json.dumps(summary, ensure_ascii=False),
                ),
            )
        return {
            "rule_id": rule,
            "status": "TESTING",
            **summary,
            "tests": results,
        }
    finally:
        conn.close()


def _latest_learning_rule_status(conn, rule_id: str) -> tuple[str | None, dict[str, Any]]:
    _ensure_learning_tables(conn)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT status,metrics
            FROM {_MEMORY_SCHEMA}.learning_rule_events
            WHERE rule_id=%s
            ORDER BY created_at DESC,event_id DESC
            LIMIT 1
            """,
            (rule_id,),
        )
        row = cur.fetchone()
    if row is None:
        return None, {}
    return str(row[0]), row[1] if isinstance(row[1], dict) else {}


def activate_tested_rule(rule_id: str) -> dict[str, Any]:
    """Aktiviert nur eine nachweislich bestandene Kandidatenregel."""
    rule = str(rule_id or "").strip()
    if not rule:
        raise ValueError("Regelaktivierung braucht rule_id.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Regelaktivierung nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT rule_kind,rule_text,condition,enforcement,session_id
                FROM {_MEMORY_SCHEMA}.learning_rules
                WHERE rule_id=%s
                """,
                (rule,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Unbekannte Regel: {rule}")
            cur.execute(
                f"""
                SELECT status,metrics
                FROM {_MEMORY_SCHEMA}.learning_rule_events
                WHERE rule_id=%s
                  AND status='TESTING'
                  AND metrics ? 'passed_for_activation'
                ORDER BY created_at DESC,event_id DESC
                LIMIT 1
                """,
                (rule,),
            )
            test_row = cur.fetchone()

        if test_row is None:
            return {
                "rule_id": rule,
                "activated": False,
                "status": "CANDIDATE",
                "reason": "Kein abgeschlossener Regressionstest vorhanden.",
            }
        metrics = test_row[1] if isinstance(test_row[1], dict) else {}
        passed = bool(metrics.get("passed_for_activation"))
        collisions = int(metrics.get("success_collisions") or 0)
        source_covered = bool(metrics.get("source_covered"))
        if not passed or collisions or not source_covered:
            return {
                "rule_id": rule,
                "activated": False,
                "status": "TESTING",
                "reason": "Regressionstest erlaubt keine Aktivierung.",
                "metrics": metrics,
            }

        current_status, _ = _latest_learning_rule_status(conn, rule)
        if current_status == "ACTIVE":
            return {
                "rule_id": rule,
                "activated": False,
                "deduplicated": True,
                "status": "ACTIVE",
                "metrics": metrics,
            }

        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_events
                    (event_id,rule_id,status,reason,metrics)
                VALUES (%s,%s,'ACTIVE',%s,%s::jsonb)
                """,
                (
                    "lre-" + uuid.uuid4().hex,
                    rule,
                    "Regressionstest deckt den Quellfehler ab und erzeugte keine Kollision mit gespeichertem Erfolg.",
                    json.dumps(metrics, ensure_ascii=False),
                ),
            )
        return {
            "rule_id": rule,
            "activated": True,
            "status": "ACTIVE",
            "metrics": metrics,
        }
    finally:
        conn.close()


def _active_learning_rules(session_id: str) -> list[dict[str, Any]]:
    conn = _workflow_connection()
    if conn is None:
        return []
    try:
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                WITH latest AS (
                    SELECT DISTINCT ON (e.rule_id)
                           e.rule_id,e.status,e.created_at
                    FROM {_MEMORY_SCHEMA}.learning_rule_events e
                    ORDER BY e.rule_id,e.created_at DESC,e.event_id DESC
                )
                SELECT r.rule_id,r.rule_kind,r.rule_text,r.condition,r.enforcement,l.status,r.created_at
                FROM {_MEMORY_SCHEMA}.learning_rules r
                JOIN latest l ON l.rule_id=r.rule_id
                WHERE r.session_id=%s AND l.status IN ('ACTIVE','WEAKENED')
                ORDER BY r.created_at DESC
                """,
                (session_id,),
            )
            rows = list(cur.fetchall())
        return [
            {
                "rule_id": str(rule_id),
                "rule_kind": str(rule_kind),
                "rule_text": str(rule_text),
                "condition": condition if isinstance(condition, dict) else {},
                "enforcement": enforcement if isinstance(enforcement, dict) else {},
                "status": str(status),
                "created_at": created_at.isoformat() if created_at else None,
            }
            for rule_id, rule_kind, rule_text, condition, enforcement, status, created_at in rows
        ]
    finally:
        conn.close()


def learning_context(
    query: str,
    *,
    session_id: str | None = None,
    limit: int = 12,
) -> dict[str, Any]:
    """Ruft aktive/abgeschwaechte Lernregeln als Erinnerung ab; Status bleibt Autoritaet."""
    key = _session_key({"session_id": session_id} if session_id else {})
    limit = max(1, min(int(limit), 30))
    qtokens = _directive_tokens(str(query or ""))
    rules = _active_learning_rules(key)
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for index, rule in enumerate(rules):
        overlap = len(qtokens.intersection(_directive_tokens(rule["rule_text"]))) if qtokens else 0
        active_bonus = 1 if rule["status"] == "ACTIVE" else 0
        scored.append((overlap, active_bonus * 1000 - index, rule))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return {
        "query": str(query or ""),
        "session_id": key,
        "rules": [item[2] for item in scored[:limit]],
        "contract": [
            "ACTIVE darf hart wirken.",
            "WEAKENED ist nur Erinnerung und darf nicht hart blockieren.",
            "SUPERSEDED und RETIRED werden nicht angewendet.",
            "RAG-Auswahl aendert niemals den Regelstatus.",
        ],
    }


def _pending_verification_conflicts(
    tool_name: str,
    args: dict[str, Any],
    pending_paths: list[str] | set[str] | tuple[str, ...],
) -> bool:
    """True nur, wenn die geplante Mutation denselben noch ungeprueften Bereich beruehrt."""
    pending = [os.path.normpath(str(path)) for path in pending_paths if str(path).strip()]
    if not pending:
        return False

    if str(tool_name) == "services.restart":
        service = str(args.get("name") or args.get("service") or "").strip()
        if service == "vps-mcp.service":
            runtime_files = {
                "vps_mcp_server.py",
                "mcp_workflow_graph.py",
                "mcp_action_graph.py",
                "mcp_cognitive_graph.py",
            }
            return any(Path(path).name in runtime_files for path in pending)
        return False

    targets = [os.path.normpath(str(path)) for path in _portfolio_paths(args, tool_name) if str(path).strip()]
    if not targets:
        # Unbekannte/pathlose Mutation bleibt konservativ an offene Verifikation gebunden.
        return True

    def overlaps(left: str, right: str) -> bool:
        if left == right:
            return True
        lprefix = left.rstrip(os.sep) + os.sep
        rprefix = right.rstrip(os.sep) + os.sep
        return left.startswith(rprefix) or right.startswith(lprefix)

    return any(overlaps(target, waiting) for target in targets for waiting in pending)


def _learned_rule_guard(
    tool_name: str,
    args: dict[str, Any],
    session_id: str,
    session: dict[str, Any],
) -> dict[str, Any]:
    """Harte Laufzeitpruefung ausschliesslich fuer ACTIVE-Regeln."""
    active = [rule for rule in _active_learning_rules(session_id) if rule["status"] == "ACTIVE"]
    if not active:
        return {"allowed": True, "matched_rules": []}

    mutation_tool = str(tool_name) in {
        "vps.edit_file",
        "vps.write_file",
        "vps.delete",
        "vps.move",
        "services.restart",
    }
    matched: list[dict[str, Any]] = []

    for rule in active:
        kind = rule["rule_kind"]
        condition = rule["condition"]
        if kind == "REQUIRE_REREAD_AFTER_MUTATION" and mutation_tool:
            pending = list(session.get("pending_verification") or [])
            if pending and _pending_verification_conflicts(tool_name, args, pending):
                matched.append(
                    {
                        "rule_id": rule["rule_id"],
                        "rule_kind": kind,
                        "reason": "Vor der naechsten Mutation wartet noch eine konkrete Ruecklesung.",
                        "pending_verification": pending,
                    }
                )
        elif kind in {"AVOID_REPEAT_BLOCKED_ACTION", "REQUIRE_RECOVERY_AFTER_FAILURE"}:
            target_tool = str(condition.get("tool_name") or "")
            if target_tool and target_tool != str(tool_name):
                continue
            conn = _workflow_connection()
            if conn is None:
                matched.append(
                    {
                        "rule_id": rule["rule_id"],
                        "rule_kind": kind,
                        "reason": "Erfahrungsdaten fuer aktive Regel nicht erreichbar; fail-closed.",
                    }
                )
                continue
            try:
                _ensure_experience_tables(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT action_id,decision,ok,created_at
                        FROM {_MEMORY_SCHEMA}.experience_actions
                        WHERE session_id=%s AND tool_name=%s
                        ORDER BY created_at DESC,action_id DESC
                        LIMIT 1
                        """,
                        (session_id, str(tool_name)),
                    )
                    previous = cur.fetchone()
                    if previous is None:
                        continue
                    action_id, previous_decision, previous_ok, previous_created = previous
                    blocked = (
                        isinstance(previous_decision, dict)
                        and str(previous_decision.get("decision") or "") == DECISION_BLOCK
                    )
                    failed = not bool(previous_ok)
                    trigger = blocked if kind == "AVOID_REPEAT_BLOCKED_ACTION" else failed
                    if not trigger:
                        continue
                    cur.execute(
                        f"""
                        SELECT 1
                        FROM {_MEMORY_SCHEMA}.experience_actions
                        WHERE session_id=%s
                          AND tool_name='vps.read_file'
                          AND ok=true
                          AND created_at > %s
                          AND NOT (arguments ? 'start_line')
                          AND NOT (arguments ? 'end_line')
                        LIMIT 1
                        """,
                        (session_id, previous_created),
                    )
                    recovered = cur.fetchone() is not None
                if not recovered:
                    matched.append(
                        {
                            "rule_id": rule["rule_id"],
                            "rule_kind": kind,
                            "reason": "Dieselbe Aktionsart wurde zuvor blockiert/fehlerhaft beendet; erst reale Rueckpruefung.",
                            "previous_action_id": str(action_id),
                        }
                    )
            finally:
                conn.close()

    if matched:
        return {
            "allowed": False,
            "reason": "Aktive gelernte Regel blockiert die Aktion.",
            "matched_rules": matched,
        }
    return {"allowed": True, "matched_rules": []}


class LearningCycleState(TypedDict, total=False):
    rule_id: str
    regression_test: dict[str, Any]
    activation: dict[str, Any]
    output: dict[str, Any]


def _learning_cycle_test(state: LearningCycleState) -> dict[str, Any]:
    return {"regression_test": test_candidate_rule(str(state["rule_id"]))}


def _learning_cycle_activate(state: LearningCycleState) -> dict[str, Any]:
    return {"activation": activate_tested_rule(str(state["rule_id"]))}


def _learning_cycle_finalize(state: LearningCycleState) -> dict[str, Any]:
    return {
        "output": {
            "rule_id": str(state["rule_id"]),
            "regression_test": dict(state.get("regression_test") or {}),
            "activation": dict(state.get("activation") or {}),
        }
    }


def _build_learning_cycle_graph():
    graph = StateGraph(LearningCycleState)
    graph.add_node("regression_test", _learning_cycle_test)
    graph.add_node("activate_if_safe", _learning_cycle_activate)
    graph.add_node("finalize", _learning_cycle_finalize)
    graph.add_edge(START, "regression_test")
    graph.add_edge("regression_test", "activate_if_safe")
    graph.add_edge("activate_if_safe", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


_LEARNING_CYCLE_GRAPH = _build_learning_cycle_graph()


def run_learning_cycle(rule_id: str) -> dict[str, Any]:
    """LangGraph-Kante: Kandidat -> Regression -> sichere Aktivierung -> Ergebnis."""
    result = _LEARNING_CYCLE_GRAPH.invoke({"rule_id": str(rule_id)})
    return dict(result.get("output") or {})


def record_rule_feedback(
    rule_id: str,
    outcome: str,
    *,
    turn_id: str | None = None,
    source_kind: str = "CHATGPT_SELF_OBSERVED",
    evidence: dict[str, Any] | None = None,
    reassess: bool = True,
) -> dict[str, Any]:
    """Append-only Rueckmeldung; behauptet keine Nutzerkorrektur."""
    rule = str(rule_id or "").strip()
    normalized_outcome = str(outcome or "").strip().upper()
    normalized_source = str(source_kind or "").strip().upper()
    if not rule:
        raise ValueError("Regel-Rueckmeldung braucht rule_id.")
    if normalized_outcome not in {"HELPFUL", "HARMFUL", "IRRELEVANT", "CONTRADICTED"}:
        raise ValueError(f"Unbekanntes Regel-Outcome: {normalized_outcome}")
    if normalized_source not in {"DETERMINISTIC", "CHATGPT_SELF_OBSERVED", "DANIEL_DASHBOARD"}:
        raise ValueError("Unbekannte Quelle fuer Regel-Rueckmeldung.")

    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Regel-Rueckmeldung nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {_MEMORY_SCHEMA}.learning_rules WHERE rule_id=%s",
                (rule,),
            )
            if cur.fetchone() is None:
                raise ValueError(f"Unbekannte Regel: {rule}")
            feedback_id = "lrf-" + uuid.uuid4().hex
            payload = dict(evidence or {})
            payload["attribution"] = (
                "deterministische Systembeobachtung"
                if normalized_source == "DETERMINISTIC"
                else (
                    "echtes Nutzerfeedback aus Daniels geschütztem Harness-Dashboard"
                    if normalized_source == "DANIEL_DASHBOARD"
                    else "ChatGPT-Selbstbeobachtung; keine Nutzerkorrektur behauptet"
                )
            )
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_feedback
                    (feedback_id,rule_id,turn_id,source_kind,outcome,evidence)
                VALUES (%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    feedback_id,
                    rule,
                    str(turn_id or "") or None,
                    normalized_source,
                    normalized_outcome,
                    json.dumps(payload, ensure_ascii=False, default=str),
                ),
            )
        result = {
            "feedback_id": feedback_id,
            "rule_id": rule,
            "turn_id": str(turn_id or "") or None,
            "source_kind": normalized_source,
            "outcome": normalized_outcome,
        }
    finally:
        conn.close()

    if reassess:
        try:
            result["reassessment"] = reassess_learning_rule(rule)
        except Exception as exc:
            result["reassessment"] = {"error": str(exc)}
    return result


def _decide_reassessed_rule_status(
    feedback_counts: dict[str, int],
    regression: dict[str, Any],
) -> tuple[str, str]:
    """Pure Statusentscheidung: neue Erfahrung darf eine Regel auch wieder schlechter machen."""
    collisions = int(regression.get("success_collisions") or 0)
    harmful = int(feedback_counts.get("HARMFUL", 0))
    contradicted = int(feedback_counts.get("CONTRADICTED", 0))
    negative = harmful + contradicted
    passed = bool(regression.get("passed_for_activation"))
    source_covered = bool(regression.get("source_covered"))

    if collisions >= 2 or negative >= 2:
        return (
            "RETIRED",
            "Wiederholte Erfolgs-Kollisionen oder negative Selbstbeobachtungen; Regel wird stillgelegt.",
        )
    if collisions >= 1 or negative >= 1 or not source_covered:
        return (
            "WEAKENED",
            "Neue Erfahrung macht die Regel unsicher oder zu breit; nur noch Erinnerung, kein harter Denier.",
        )
    if passed:
        return (
            "ACTIVE",
            "Erneuter Trace-Test bestaetigt die Regel ohne Erfolgs-Kollision.",
        )
    return (
        "WEAKENED",
        "Regel ist unter dem aktuellen Erfahrungsstand nicht sicher hart aktivierbar.",
    )


def reassess_learning_rule(rule_id: str, *, limit: int = 200) -> dict[str, Any]:
    """Neue Erfahrungen koennen Regeln bestaetigen, abschwaechen oder stilllegen."""
    rule = str(rule_id or "").strip()
    if not rule:
        raise ValueError("Regel-Neubewertung braucht rule_id.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Regel-Neubewertung nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        current_status, _current_metrics = _latest_learning_rule_status(conn, rule)
        if current_status in {"SUPERSEDED", "RETIRED"}:
            return {
                "rule_id": rule,
                "status": current_status,
                "changed": False,
                "reason": "Abgeloeste/stillgelegte Regel wird nicht automatisch wiederbelebt.",
            }
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT outcome,count(*)
                FROM {_MEMORY_SCHEMA}.learning_rule_feedback
                WHERE rule_id=%s
                GROUP BY outcome
                """,
                (rule,),
            )
            feedback_counts = {str(outcome): int(count) for outcome, count in cur.fetchall()}
    finally:
        conn.close()

    regression = test_candidate_rule(rule, limit=limit)
    collisions = int(regression.get("success_collisions") or 0)
    passed = bool(regression.get("passed_for_activation"))
    source_covered = bool(regression.get("source_covered"))
    new_status, reason = _decide_reassessed_rule_status(feedback_counts, regression)

    metrics = {
        "previous_status": current_status,
        "feedback_counts": feedback_counts,
        "regression": {
            "tested_turns": regression.get("tested_turns"),
            "matched_turns": regression.get("matched_turns"),
            "source_covered": source_covered,
            "success_collisions": collisions,
            "passed_for_activation": passed,
        },
    }
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Regelstatus nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_events
                    (event_id,rule_id,status,reason,metrics)
                VALUES (%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    "lre-" + uuid.uuid4().hex,
                    rule,
                    new_status,
                    reason,
                    json.dumps(metrics, ensure_ascii=False, default=str),
                ),
            )
    finally:
        conn.close()
    return {
        "rule_id": rule,
        "previous_status": current_status,
        "status": new_status,
        "changed": new_status != current_status,
        "reason": reason,
        "metrics": metrics,
    }


def supersede_learning_rule(
    old_rule_id: str,
    replacement_rule_id: str,
    *,
    reason: str = "",
) -> dict[str, Any]:
    """Ersetzt eine alte Regel append-only; beide Regelkoerper bleiben erhalten."""
    old_rule = str(old_rule_id or "").strip()
    replacement = str(replacement_rule_id or "").strip()
    if not old_rule or not replacement or old_rule == replacement:
        raise ValueError("Supersession braucht zwei verschiedene Regel-IDs.")
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Regel-Supersession nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        replacement_status, _ = _latest_learning_rule_status(conn, replacement)
        if replacement_status != "ACTIVE":
            raise ValueError("Ersatzregel muss bereits ACTIVE sein.")
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {_MEMORY_SCHEMA}.learning_rules WHERE rule_id=%s",
                (old_rule,),
            )
            if cur.fetchone() is None:
                raise ValueError(f"Unbekannte alte Regel: {old_rule}")
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.learning_rule_events
                    (event_id,rule_id,status,reason,metrics)
                VALUES (%s,%s,'SUPERSEDED',%s,%s::jsonb)
                """,
                (
                    "lre-" + uuid.uuid4().hex,
                    old_rule,
                    str(reason or "Durch eine spezifischere/bessere aktive Regel ersetzt."),
                    json.dumps({"replacement_rule_id": replacement}, ensure_ascii=False),
                ),
            )
        return {
            "rule_id": old_rule,
            "status": "SUPERSEDED",
            "replacement_rule_id": replacement,
        }
    finally:
        conn.close()


def learning_status(
    *,
    session_id: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Aktueller Zustand plus Geschichte bleibt getrennt in Events erhalten."""
    key = _session_key({"session_id": session_id} if session_id else {})
    limit = max(1, min(int(limit), 500))
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Lernstatus nicht erreichbar.")
    try:
        _ensure_learning_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                WITH latest AS (
                    SELECT DISTINCT ON (e.rule_id)
                           e.rule_id,e.status,e.reason,e.metrics,e.created_at
                    FROM {_MEMORY_SCHEMA}.learning_rule_events e
                    ORDER BY e.rule_id,e.created_at DESC,e.event_id DESC
                ),
                feedback AS (
                    SELECT rule_id,
                           count(*) FILTER (WHERE outcome='HELPFUL') AS helpful,
                           count(*) FILTER (WHERE outcome='HARMFUL') AS harmful,
                           count(*) FILTER (WHERE outcome='CONTRADICTED') AS contradicted,
                           count(*) FILTER (WHERE outcome='IRRELEVANT') AS irrelevant
                    FROM {_MEMORY_SCHEMA}.learning_rule_feedback
                    GROUP BY rule_id
                )
                SELECT r.rule_id,r.rule_kind,r.rule_text,r.condition,r.enforcement,
                       r.source_drift_id,d.drift_code,d.description,d.evidence,
                       l.status,l.reason,l.metrics,
                       COALESCE(f.helpful,0),COALESCE(f.harmful,0),
                       COALESCE(f.contradicted,0),COALESCE(f.irrelevant,0),
                       r.created_at,l.created_at
                FROM {_MEMORY_SCHEMA}.learning_rules r
                JOIN latest l ON l.rule_id=r.rule_id
                LEFT JOIN feedback f ON f.rule_id=r.rule_id
                LEFT JOIN {_MEMORY_SCHEMA}.experience_drift_points d ON d.drift_id=r.source_drift_id
                WHERE r.session_id=%s
                ORDER BY l.created_at DESC
                LIMIT %s
                """,
                (key, limit),
            )
            rows = list(cur.fetchall())
        return {
            "session_id": key,
            "rules": [
                {
                    "rule_id": str(rule_id),
                    "rule_kind": str(rule_kind),
                    "rule_text": str(rule_text),
                    "condition": condition if isinstance(condition, dict) else {},
                    "enforcement": enforcement if isinstance(enforcement, dict) else {},
                    "source_drift": {
                        "drift_id": str(source_drift_id or "") or None,
                        "drift_code": str(drift_code or "") or None,
                        "description": str(drift_description or "") or None,
                        "evidence": drift_evidence if isinstance(drift_evidence, dict) else {},
                    },
                    "status": str(status),
                    "reason": str(reason),
                    "metrics": metrics if isinstance(metrics, dict) else {},
                    "feedback": {
                        "helpful": int(helpful),
                        "harmful": int(harmful),
                        "contradicted": int(contradicted),
                        "irrelevant": int(irrelevant),
                    },
                    "created_at": created_at.isoformat() if created_at else None,
                    "status_at": status_at.isoformat() if status_at else None,
                }
                for (
                    rule_id,
                    rule_kind,
                    rule_text,
                    condition,
                    enforcement,
                    source_drift_id,
                    drift_code,
                    drift_description,
                    drift_evidence,
                    status,
                    reason,
                    metrics,
                    helpful,
                    harmful,
                    contradicted,
                    irrelevant,
                    created_at,
                    status_at,
                ) in rows
            ],
        }
    finally:
        conn.close()


def _reassess_session_learning_rules(session_id: str, *, limit: int = 200) -> list[dict[str, Any]]:
    """Nach neuer Erfahrung aktive/abgeschwaechte Regeln erneut gegen den wachsenden Trace-Bestand halten."""
    rules = _active_learning_rules(session_id)
    results: list[dict[str, Any]] = []
    for rule in rules:
        try:
            results.append(reassess_learning_rule(rule["rule_id"], limit=limit))
        except Exception as exc:
            results.append({"rule_id": rule["rule_id"], "error": str(exc)})
    return results


class DirectiveState(TypedDict, total=False):
    raw_text: str
    session_id: str
    metadata: dict[str, Any]
    constraints: list[dict[str, Any]]
    invariants: list[dict[str, Any]]
    supersedes: list[str]
    source_kind: str
    idempotency_key: str | None
    event_id: str
    raw_sha256: str
    deduplicated: bool
    output: dict[str, Any]


_TRUSTED_DIRECTIVE_SOURCE = "TRUSTED_CLIENT_CAPTURE"
_UNVERIFIED_DIRECTIVE_SOURCE = "UNVERIFIED_MODEL_CLAIM"


def _directive_validate(state: DirectiveState) -> dict[str, Any]:
    raw_text = state.get("raw_text")
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("Direktive braucht unveraenderten nichtleeren Rohtext.")
    source_kind = str(state.get("source_kind") or _UNVERIFIED_DIRECTIVE_SOURCE).strip().upper()
    if source_kind not in {_TRUSTED_DIRECTIVE_SOURCE, _UNVERIFIED_DIRECTIVE_SOURCE}:
        raise ValueError(f"Unbekannte Directive-Quelle: {source_kind}")
    constraints = list(state.get("constraints") or [])
    invariants = list(state.get("invariants") or [])
    supersedes = [str(x) for x in state.get("supersedes") or [] if str(x)]
    if source_kind != _TRUSTED_DIRECTIVE_SOURCE and (constraints or invariants or supersedes):
        raise ValueError(
            "Unverifizierter Modell-Claim darf weder harte Constraints/Invarianten noch SUPERSEDES-Kanten erzeugen."
        )
    for item in constraints:
        if not isinstance(item, dict):
            raise ValueError("Directive-Constraint muss ein Objekt sein.")
        effect = str(item.get("effect") or "REMIND").upper()
        if effect not in {"DENY", "REQUIRE_REMINDER", "REMIND"}:
            raise ValueError(f"Unbekannter Directive-effect: {effect}")
        if not str(item.get("statement") or "").strip():
            raise ValueError("Directive-Constraint braucht statement.")
        for key in ("action_pattern", "target_pattern"):
            if len(str(item.get(key) or "*")) > 512:
                raise ValueError(f"{key} ist zu lang; harte Matcher sind absichtlich begrenzt.")
    for item in invariants:
        if not isinstance(item, dict):
            raise ValueError("Directive-Invariante muss ein Objekt sein.")
        inv_type = str(item.get("type") or "").upper()
        if inv_type not in {"EXACT_CONTENT", "PATH_STABLE", "MUST_EXIST", "MUST_NOT_EXIST"}:
            raise ValueError(f"Unbekannte Invariante: {inv_type}")
        if not str(item.get("path") or "").strip():
            raise ValueError("Directive-Invariante braucht path.")
        if inv_type == "EXACT_CONTENT" and not str(item.get("expected_sha256") or "").strip():
            raise ValueError("EXACT_CONTENT braucht expected_sha256.")
    return {
        "source_kind": source_kind,
        "constraints": constraints,
        "invariants": invariants,
        "supersedes": supersedes,
        "idempotency_key": str(state.get("idempotency_key") or "").strip() or None,
    }


def _directive_persist_atomic(state: DirectiveState) -> dict[str, Any]:
    raw_text = str(state["raw_text"])
    session_id = str(state.get("session_id") or "default")
    source_kind = str(state.get("source_kind") or _UNVERIFIED_DIRECTIVE_SOURCE)
    idempotency_key = state.get("idempotency_key")
    raw_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktiven nicht erreichbar; kein fluechtiger Fallback.")
    conn.autocommit = False
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            if idempotency_key:
                cur.execute(
                    f"""
                    SELECT event_id,raw_sha256
                    FROM {_MEMORY_SCHEMA}.directive_events
                    WHERE session_id=%s AND idempotency_key=%s
                    LIMIT 1
                    """,
                    (session_id, idempotency_key),
                )
                existing = cur.fetchone()
                if existing is not None:
                    if str(existing[1]) != raw_sha256:
                        raise ValueError("Idempotency-Key existiert bereits fuer anderen Rohtext; fail-closed.")
                    conn.commit()
                    return {
                        "event_id": str(existing[0]),
                        "raw_sha256": raw_sha256,
                        "deduplicated": True,
                    }

            event_id = "d-" + uuid.uuid4().hex
            metadata = dict(state.get("metadata") or {})
            metadata["authority_provenance"] = source_kind
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.directive_events
                    (event_id,session_id,raw_text,raw_sha256,source_kind,idempotency_key,metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    event_id,
                    session_id,
                    raw_text,
                    raw_sha256,
                    source_kind,
                    idempotency_key,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            for old_id in state.get("supersedes") or []:
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.directive_relations
                        (edge_id,from_event_id,to_event_id,relation,reason)
                    VALUES (%s,%s,%s,'SUPERSEDES','spaetere verifizierte Nutzer-Direktive')
                    """,
                    ("de-" + uuid.uuid4().hex, event_id, str(old_id)),
                )
            for item in state.get("constraints") or []:
                effect = str(item.get("effect") or "REMIND").upper()
                meta = dict(item.get("metadata") or {})
                meta["matcher"] = "glob_v1"
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.directive_constraints
                        (constraint_id,directive_event_id,effect,action_pattern,target_pattern,statement,metadata)
                    VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    (
                        "dc-" + uuid.uuid4().hex,
                        event_id,
                        effect,
                        str(item.get("action_pattern") or "*"),
                        str(item.get("target_pattern") or "*"),
                        str(item.get("statement") or "").strip(),
                        json.dumps(meta, ensure_ascii=False),
                    ),
                )
            for item in state.get("invariants") or []:
                inv_type = str(item.get("type") or "").upper()
                inv_path = str(Path(str(item.get("path"))).expanduser().resolve(strict=False))
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.directive_invariants
                        (invariant_id,directive_event_id,invariant_type,path,expected_sha256,metadata)
                    VALUES (%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    (
                        "di-" + uuid.uuid4().hex,
                        event_id,
                        inv_type,
                        inv_path,
                        str(item.get("expected_sha256") or "") or None,
                        json.dumps(item.get("metadata") or {}, ensure_ascii=False),
                    ),
                )
        conn.commit()
        return {
            "event_id": event_id,
            "raw_sha256": raw_sha256,
            "deduplicated": False,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _directive_persist_event(state: DirectiveState) -> dict[str, Any]:
    raw_text = state.get("raw_text")
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("USER_DIRECTIVE braucht unveraenderten nichtleeren Rohtext.")
    event_id = "d-" + uuid.uuid4().hex
    raw_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktiven nicht erreichbar; kein fluechtiger Fallback.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.directive_events
                    (event_id,session_id,raw_text,raw_sha256,source_kind,metadata)
                VALUES (%s,%s,%s,%s,'USER_DIRECTIVE',%s::jsonb)
                """,
                (
                    event_id,
                    str(state.get("session_id") or "default"),
                    raw_text,
                    raw_sha256,
                    json.dumps(state.get("metadata") or {}, ensure_ascii=False),
                ),
            )
    finally:
        conn.close()
    return {"event_id": event_id, "raw_sha256": raw_sha256}


def _directive_persist_relations(state: DirectiveState) -> dict[str, Any]:
    supersedes = [str(x) for x in state.get("supersedes") or [] if str(x)]
    if not supersedes:
        return {}
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktiven nicht erreichbar.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            for old_id in supersedes:
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.directive_relations
                        (edge_id,from_event_id,to_event_id,relation,reason)
                    VALUES (%s,%s,%s,'SUPERSEDES','spaetere explizite Daniel-Direktive')
                    """,
                    ("de-" + uuid.uuid4().hex, state["event_id"], old_id),
                )
    finally:
        conn.close()
    return {}


def _directive_persist_constraints(state: DirectiveState) -> dict[str, Any]:
    constraints = list(state.get("constraints") or [])
    if not constraints:
        return {}
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktiven nicht erreichbar.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            for item in constraints:
                if not isinstance(item, dict):
                    continue
                effect = str(item.get("effect") or "REMIND").upper()
                if effect not in {"DENY", "REQUIRE_REMINDER", "REMIND"}:
                    raise ValueError(f"Unbekannter Directive-effect: {effect}")
                statement = str(item.get("statement") or "").strip()
                if not statement:
                    raise ValueError("Directive-Constraint braucht statement.")
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.directive_constraints
                        (constraint_id,directive_event_id,effect,action_pattern,target_pattern,statement,metadata)
                    VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    (
                        "dc-" + uuid.uuid4().hex,
                        state["event_id"],
                        effect,
                        str(item.get("action_pattern") or ".*"),
                        str(item.get("target_pattern") or ".*"),
                        statement,
                        json.dumps(item.get("metadata") or {}, ensure_ascii=False),
                    ),
                )
    finally:
        conn.close()
    return {}


def _directive_finalize(state: DirectiveState) -> dict[str, Any]:
    source_kind = state.get("source_kind") or _UNVERIFIED_DIRECTIVE_SOURCE
    return {
        "output": {
            "event_id": state["event_id"],
            "raw_sha256": state["raw_sha256"],
            "session_id": state.get("session_id") or "default",
            "immutable_source": True,
            "source_kind": source_kind,
            "authority_verified": source_kind == _TRUSTED_DIRECTIVE_SOURCE,
            "supersedes": list(state.get("supersedes") or []),
            "constraint_count": len(state.get("constraints") or []),
            "invariant_count": len(state.get("invariants") or []),
            "deduplicated": bool(state.get("deduplicated")),
        }
    }


def _build_directive_ingest_graph():
    graph = StateGraph(DirectiveState)
    graph.add_node("validate", _directive_validate)
    graph.add_node("persist_atomic", _directive_persist_atomic)
    graph.add_node("finalize", _directive_finalize)
    graph.add_edge(START, "validate")
    graph.add_edge("validate", "persist_atomic")
    graph.add_edge("persist_atomic", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


_DIRECTIVE_INGEST_GRAPH = _build_directive_ingest_graph()


def record_directive(
    raw_text: str,
    *,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    constraints: list[dict[str, Any]] | None = None,
    invariants: list[dict[str, Any]] | None = None,
    supersedes: list[str] | None = None,
    source_kind: str = _UNVERIFIED_DIRECTIVE_SOURCE,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """Persistiert Rohtext exakt; nur vertrauenswuerdiger Client-Capture darf harte Autoritaet erzeugen."""
    result = _DIRECTIVE_INGEST_GRAPH.invoke(
        {
            "raw_text": raw_text,
            "session_id": _session_key({"session_id": session_id} if session_id else {}),
            "metadata": metadata if isinstance(metadata, dict) else {},
            "constraints": list(constraints or []),
            "invariants": list(invariants or []),
            "supersedes": list(supersedes or []),
            "source_kind": str(source_kind or _UNVERIFIED_DIRECTIVE_SOURCE),
            "idempotency_key": idempotency_key,
        }
    )
    return dict(result.get("output") or {})


def set_directive_status(
    event_id: str,
    status: str,
    *,
    actor: str,
    reason: str,
) -> dict[str, Any]:
    """Schaltet eine bestehende Direktive append-only ACTIVE oder ARCHIVED."""
    event_id = str(event_id or "").strip()
    status = str(status or "").strip().upper()
    actor = str(actor or "").strip()
    reason = str(reason or "").strip()
    if not event_id:
        raise ValueError("event_id fehlt.")
    if status not in {"ACTIVE", "ARCHIVED"}:
        raise ValueError("status muss ACTIVE oder ARCHIVED sein.")
    if not actor:
        raise ValueError("actor fehlt.")
    if not reason:
        raise ValueError("reason fehlt.")

    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktivenstatus nicht erreichbar.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT session_id
                FROM {_MEMORY_SCHEMA}.directive_events
                WHERE event_id=%s
                LIMIT 1
                """,
                (event_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Direktive nicht gefunden.")
            session_id = str(row[0])
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.directive_status_events
                    (status_event_id,directive_event_id,status,actor,reason)
                VALUES (%s,%s,%s,%s,%s)
                """,
                ("dse-" + uuid.uuid4().hex, event_id, status, actor, reason),
            )
    finally:
        conn.close()

    snapshot = directive_status(session_id=session_id, limit=500)
    directive = next(
        (item for item in snapshot.get("directives", []) if item.get("event_id") == event_id),
        None,
    )
    return {
        "event_id": event_id,
        "status": status,
        "directive": directive,
    }


def _directive_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z0-9_./-]{3,}", str(text).lower())
        if token not in {"root", "true", "false", "none", "null"}
    }


def directive_context(query: str, *, limit: int = 12) -> dict[str, Any]:
    """Directive-RAG: aktive Rohdirektiven, gewichtet nach Bezug + Aktualitaet."""
    limit = max(1, min(int(limit), 30))
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktiven nicht erreichbar.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT e.event_id,e.session_id,e.raw_text,e.raw_sha256,e.source_kind,e.created_at
                FROM {_MEMORY_SCHEMA}.directive_events e
                WHERE COALESCE((
                    SELECT s.status
                    FROM {_MEMORY_SCHEMA}.directive_status_events s
                    WHERE s.directive_event_id=e.event_id
                    ORDER BY s.created_at DESC,s.status_event_id DESC
                    LIMIT 1
                ),'ACTIVE')='ACTIVE'
                  AND NOT EXISTS (
                    SELECT 1 FROM {_MEMORY_SCHEMA}.directive_relations r
                    WHERE r.to_event_id=e.event_id AND r.relation='SUPERSEDES'
                )
                ORDER BY e.created_at DESC
                """
            )
            rows = cur.fetchall()
        qtokens = _directive_tokens(query)
        scored = []
        for event_id, session_id, raw_text, raw_sha256, source_kind, created_at in rows:
            overlap = len(qtokens.intersection(_directive_tokens(raw_text))) if qtokens else 0
            authority_verified = str(source_kind) == _TRUSTED_DIRECTIVE_SOURCE
            scored.append(
                (
                    overlap,
                    created_at,
                    {
                        "event_id": str(event_id),
                        "session_id": str(session_id),
                        "raw_text": str(raw_text),
                        "raw_sha256": str(raw_sha256),
                        "source_kind": str(source_kind),
                        "authority_verified": authority_verified,
                        "created_at": created_at.isoformat() if created_at else None,
                        "retrieval_overlap": overlap,
                    },
                )
            )
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        chosen = [item[2] for item in scored[:limit]]
        return {
            "query": query,
            "directives": chosen,
            "contract": [
                "raw_text bleibt unveraendert",
                "nur TRUSTED_CLIENT_CAPTURE darf harte Autoritaet/Constraints/Supersession erzeugen",
                "UNVERIFIED_MODEL_CLAIM ist Erinnerung, niemals Nutzer-Autoritaet",
                "RAG waehlt Erinnerung; harte Regeln werden davon unabhaengig deterministisch geprueft",
            ],
        }
    finally:
        conn.close()


def directive_status(*, session_id: str | None = None, limit: int = 200) -> dict[str, Any]:
    """Dashboard-Inventar der Direktiven: Rohtext, Autoritaet, Ableitungen und Ablösung."""
    key = _session_key({"session_id": session_id} if session_id else {})
    limit = max(1, min(int(limit), 500))
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktivenstatus nicht erreichbar.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT event_id,raw_text,source_kind,metadata,created_at
                FROM {_MEMORY_SCHEMA}.directive_events
                WHERE session_id=%s
                ORDER BY created_at DESC,event_id DESC
                LIMIT %s
                """,
                (key, limit),
            )
            event_rows = list(cur.fetchall())
        event_ids = [str(row[0]) for row in event_rows]
        constraints_by_event: dict[str, list[dict[str, Any]]] = {}
        invariants_by_event: dict[str, list[dict[str, Any]]] = {}
        supersedes_by_event: dict[str, list[str]] = {}
        superseded_by_event: dict[str, list[str]] = {}
        status_events_by_event: dict[str, list[dict[str, Any]]] = {}
        latest_status_by_event: dict[str, dict[str, Any]] = {}

        if event_ids:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT directive_event_id,constraint_id,effect,action_pattern,target_pattern,
                           statement,metadata,created_at
                    FROM {_MEMORY_SCHEMA}.directive_constraints
                    WHERE directive_event_id = ANY(%s)
                    ORDER BY created_at,constraint_id
                    """,
                    (event_ids,),
                )
                for event_id, constraint_id, effect, action_pattern, target_pattern, statement, metadata, created_at in cur.fetchall():
                    constraints_by_event.setdefault(str(event_id), []).append(
                        {
                            "constraint_id": str(constraint_id),
                            "effect": str(effect),
                            "action_pattern": str(action_pattern),
                            "target_pattern": str(target_pattern),
                            "statement": str(statement),
                            "metadata": metadata if isinstance(metadata, dict) else {},
                            "created_at": created_at.isoformat() if created_at else None,
                        }
                    )
                cur.execute(
                    f"""
                    SELECT directive_event_id,invariant_id,invariant_type,path,expected_sha256,
                           metadata,created_at
                    FROM {_MEMORY_SCHEMA}.directive_invariants
                    WHERE directive_event_id = ANY(%s)
                    ORDER BY created_at,invariant_id
                    """,
                    (event_ids,),
                )
                for event_id, invariant_id, invariant_type, path, expected_sha256, metadata, created_at in cur.fetchall():
                    invariants_by_event.setdefault(str(event_id), []).append(
                        {
                            "invariant_id": str(invariant_id),
                            "type": str(invariant_type),
                            "path": str(path),
                            "expected_sha256": str(expected_sha256 or "") or None,
                            "metadata": metadata if isinstance(metadata, dict) else {},
                            "created_at": created_at.isoformat() if created_at else None,
                        }
                    )
                cur.execute(
                    f"""
                    SELECT from_event_id,to_event_id,relation,reason,created_at
                    FROM {_MEMORY_SCHEMA}.directive_relations
                    WHERE from_event_id = ANY(%s) OR to_event_id = ANY(%s)
                    ORDER BY created_at,edge_id
                    """,
                    (event_ids, event_ids),
                )
                for from_event_id, to_event_id, relation, _reason, _created_at in cur.fetchall():
                    if str(relation) == "SUPERSEDES":
                        supersedes_by_event.setdefault(str(from_event_id), []).append(str(to_event_id))
                        superseded_by_event.setdefault(str(to_event_id), []).append(str(from_event_id))

                cur.execute(
                    f"""
                    SELECT directive_event_id,status_event_id,status,actor,reason,created_at
                    FROM {_MEMORY_SCHEMA}.directive_status_events
                    WHERE directive_event_id = ANY(%s)
                    ORDER BY directive_event_id,created_at,status_event_id
                    """,
                    (event_ids,),
                )
                for directive_event_id, status_event_id, status, actor, reason, created_at in cur.fetchall():
                    key_id = str(directive_event_id)
                    item = {
                        "status_event_id": str(status_event_id),
                        "status": str(status),
                        "actor": str(actor),
                        "reason": str(reason or ""),
                        "created_at": created_at.isoformat() if created_at else None,
                    }
                    status_events_by_event.setdefault(key_id, []).append(item)
                    latest_status_by_event[key_id] = item

        directives = []
        for event_id, raw_text, source_kind, metadata, created_at in event_rows:
            event_key = str(event_id)
            superseded_by = list(dict.fromkeys(superseded_by_event.get(event_key, [])))
            source = str(source_kind)
            manual_status = latest_status_by_event.get(event_key) or {}
            effective_status = (
                "SUPERSEDED"
                if superseded_by
                else str(manual_status.get("status") or "ACTIVE")
            )
            directives.append(
                {
                    "event_id": event_key,
                    "raw_text": str(raw_text),
                    "source_kind": source,
                    "authority_verified": source == _TRUSTED_DIRECTIVE_SOURCE,
                    "status": effective_status,
                    "status_actor": manual_status.get("actor"),
                    "status_reason": manual_status.get("reason"),
                    "status_changed_at": manual_status.get("created_at"),
                    "status_history": status_events_by_event.get(event_key, []),
                    "constraints": constraints_by_event.get(event_key, []),
                    "invariants": invariants_by_event.get(event_key, []),
                    "supersedes": list(dict.fromkeys(supersedes_by_event.get(event_key, []))),
                    "superseded_by": superseded_by,
                    "metadata": metadata if isinstance(metadata, dict) else {},
                    "created_at": created_at.isoformat() if created_at else None,
                }
            )

        return {
            "session_id": key,
            "directives": directives,
            "counts": {
                "total": len(directives),
                "active_verified": sum(
                    1 for item in directives
                    if item["status"] == "ACTIVE" and item["authority_verified"]
                ),
                "active_unverified": sum(
                    1 for item in directives
                    if item["status"] == "ACTIVE" and not item["authority_verified"]
                ),
                "archived": sum(1 for item in directives if item["status"] == "ARCHIVED"),
                "superseded": sum(1 for item in directives if item["status"] == "SUPERSEDED"),
            },
        }
    finally:
        conn.close()


def _action_fingerprint(tool_name: str, args: dict[str, Any]) -> str:
    normalized = dict(args or {})
    normalized.pop("directive_reminder_id", None)
    body = json.dumps(
        {"tool": str(tool_name), "args": normalized},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def directive_reminder(
    tool_name: str,
    arguments: dict[str, Any] | None,
    *,
    session_id: str | None = None,
    limit: int = 12,
) -> dict[str, Any]:
    args = arguments if isinstance(arguments, dict) else {}
    key = _session_key({"session_id": session_id} if session_id else args)
    query = str(tool_name) + " " + json.dumps(args, ensure_ascii=False, default=str)
    context = directive_context(query, limit=limit)
    reminder_id = "dr-" + uuid.uuid4().hex
    fingerprint = _action_fingerprint(tool_name, args)
    event_ids = [item["event_id"] for item in context["directives"]]
    conn = _workflow_connection()
    if conn is None:
        raise RuntimeError("PostgreSQL fuer Direktiven nicht erreichbar.")
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.directive_reminders
                    (reminder_id,session_id,action_fingerprint,tool_name,directive_event_ids,expires_at)
                VALUES (%s,%s,%s,%s,%s::jsonb,now() + interval '10 minutes')
                """,
                (reminder_id, key, fingerprint, str(tool_name), json.dumps(event_ids)),
            )
    finally:
        conn.close()
    return {
        "reminder_id": reminder_id,
        "session_id": key,
        "action_fingerprint": fingerprint,
        "tool_name": tool_name,
        "directives": context["directives"],
        "contract": context["contract"],
        "expires_in_seconds": 600,
    }


def _safe_glob_match(pattern: str, value: str) -> bool:
    pattern = str(pattern or "*")
    if len(pattern) > 512:
        raise ValueError("Gespeicherter harter Matcher ist zu lang; fail-closed.")
    return fnmatch.fnmatchcase(str(value), pattern)


def _active_trusted_constraints(conn, session_id: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT c.directive_event_id,c.effect,c.action_pattern,c.target_pattern,c.statement
            FROM {_MEMORY_SCHEMA}.directive_constraints c
            JOIN {_MEMORY_SCHEMA}.directive_events e ON e.event_id=c.directive_event_id
            WHERE e.session_id=%s AND e.source_kind=%s
              AND COALESCE((
                  SELECT s.status
                  FROM {_MEMORY_SCHEMA}.directive_status_events s
                  WHERE s.directive_event_id=e.event_id
                  ORDER BY s.created_at DESC,s.status_event_id DESC
                  LIMIT 1
              ),'ACTIVE')='ACTIVE'
              AND NOT EXISTS (
                  SELECT 1 FROM {_MEMORY_SCHEMA}.directive_relations r
                  WHERE r.to_event_id=e.event_id AND r.relation='SUPERSEDES'
              )
            ORDER BY c.created_at
            """,
            (session_id, _TRUSTED_DIRECTIVE_SOURCE),
        )
        return list(cur.fetchall())


def _mutation_paths(tool_name: str, args: dict[str, Any]) -> tuple[str | None, str | None]:
    try:
        if tool_name == "vps.move":
            src = str(Path(str(args.get("source") or "")).expanduser().resolve(strict=False)) if args.get("source") else None
            dst = str(Path(str(args.get("destination") or "")).expanduser().resolve(strict=False)) if args.get("destination") else None
            return src, dst
        raw = args.get("path")
        p = str(Path(str(raw)).expanduser().resolve(strict=False)) if raw else None
        return p, p
    except Exception:
        return None, None


def _proposed_text_for_mutation(tool_name: str, args: dict[str, Any], path: str) -> str | None:
    if tool_name == "vps.write_file":
        return str(args.get("content") or "")
    if tool_name != "vps.edit_file":
        return None
    try:
        current = Path(path).read_text(encoding="utf-8")
    except Exception as exc:
        raise ValueError(f"Invarianten-Guard konnte Ziel nicht lesen: {exc}")
    old = str(args.get("old_string") or "")
    new = str(args.get("new_string") or "")
    if not old or old not in current:
        raise ValueError("Invarianten-Guard kann vorgeschlagenen Endzustand nicht eindeutig bilden; fail-closed.")
    if bool(args.get("replace_all", False)):
        return current.replace(old, new)
    if current.count(old) != 1:
        raise ValueError("Invarianten-Guard verlangt fuer Einzelersatz genau ein Vorkommen; fail-closed.")
    return current.replace(old, new, 1)


def _check_active_invariants(conn, tool_name: str, args: dict[str, Any], session_id: str) -> dict[str, Any]:
    source_path, destination_path = _mutation_paths(tool_name, args)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT i.directive_event_id,i.invariant_type,i.path,i.expected_sha256
            FROM {_MEMORY_SCHEMA}.directive_invariants i
            JOIN {_MEMORY_SCHEMA}.directive_events e ON e.event_id=i.directive_event_id
            WHERE e.session_id=%s AND e.source_kind=%s
              AND COALESCE((
                  SELECT s.status
                  FROM {_MEMORY_SCHEMA}.directive_status_events s
                  WHERE s.directive_event_id=e.event_id
                  ORDER BY s.created_at DESC,s.status_event_id DESC
                  LIMIT 1
              ),'ACTIVE')='ACTIVE'
              AND NOT EXISTS (
                  SELECT 1 FROM {_MEMORY_SCHEMA}.directive_relations r
                  WHERE r.to_event_id=e.event_id AND r.relation='SUPERSEDES'
              )
            ORDER BY i.created_at
            """,
            (session_id, _TRUSTED_DIRECTIVE_SOURCE),
        )
        rows = list(cur.fetchall())

    violations = []
    for event_id, inv_type, inv_path, expected_sha256 in rows:
        inv_path = str(inv_path)
        inv_type = str(inv_type)
        if inv_type in {"PATH_STABLE", "MUST_EXIST"}:
            if tool_name in {"vps.move", "vps.delete"} and source_path == inv_path:
                violations.append({"directive_event_id": str(event_id), "type": inv_type, "path": inv_path})
        elif inv_type == "MUST_NOT_EXIST":
            touches = (
                (tool_name in {"vps.write_file", "vps.edit_file"} and source_path == inv_path)
                or (tool_name == "vps.move" and destination_path == inv_path)
            )
            if touches:
                violations.append({"directive_event_id": str(event_id), "type": inv_type, "path": inv_path})
        elif inv_type == "EXACT_CONTENT":
            if tool_name in {"vps.move", "vps.delete"} and source_path == inv_path:
                violations.append({"directive_event_id": str(event_id), "type": inv_type, "path": inv_path})
            elif tool_name in {"vps.write_file", "vps.edit_file"} and source_path == inv_path:
                proposed = _proposed_text_for_mutation(tool_name, args, inv_path)
                proposed_sha = hashlib.sha256((proposed or "").encode("utf-8")).hexdigest()
                if proposed_sha != str(expected_sha256 or ""):
                    violations.append({
                        "directive_event_id": str(event_id),
                        "type": inv_type,
                        "path": inv_path,
                        "expected_sha256": str(expected_sha256 or ""),
                        "proposed_sha256": proposed_sha,
                    })
    return {"allowed": not violations, "violations": violations}


def _directive_guard(tool_name: str, args: dict[str, Any], session_id: str) -> dict[str, Any]:
    fingerprint = _action_fingerprint(tool_name, args)
    conn = _workflow_connection()
    if conn is None:
        return {"allowed": False, "reason": "PostgreSQL-Direktivengedaechtnis nicht erreichbar; fail-closed.", "directives": []}
    try:
        _ensure_directive_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT reminder_id,directive_event_ids
                FROM {_MEMORY_SCHEMA}.directive_reminders
                WHERE session_id=%s AND action_fingerprint=%s AND expires_at > now()
                ORDER BY issued_at DESC
                LIMIT 1
                """,
                (session_id, fingerprint),
            )
            reminder = cur.fetchone()
            if reminder is None:
                return {
                    "allowed": False,
                    "reason": "Vor dieser Mutation fehlt der passende Directive-RAG-Reminder fuer exakt diese Toolargumente.",
                    "directives": [],
                }
            reminder_id, event_ids_json = reminder
            event_ids = list(event_ids_json or [])
            if not event_ids:
                return {
                    "allowed": False,
                    "reason": "Reminder enthielt keine aktive Daniel-Direktive; Mutation bleibt fail-closed.",
                    "directives": [],
                }
            serialized_target = json.dumps(args, ensure_ascii=False, sort_keys=True, default=str)
            source_path, destination_path = _mutation_paths(tool_name, args)
            target_candidates = [serialized_target]
            argv_value = args.get("argv")
            if isinstance(argv_value, (list, tuple)) and argv_value:
                argv_text = " ".join(str(part) for part in argv_value)
                if argv_text not in target_candidates:
                    target_candidates.append(argv_text)
            command_value = args.get("command", args.get("cmd"))
            if isinstance(command_value, str) and command_value.strip():
                command_text = command_value.strip()
                if command_text not in target_candidates:
                    target_candidates.append(command_text)
            for candidate in (
                args.get("path"),
                source_path,
                destination_path,
                args.get("name"),
                args.get("service"),
                args.get("url"),
            ):
                if candidate not in (None, ""):
                    candidate_text = str(candidate)
                    if candidate_text not in target_candidates:
                        target_candidates.append(candidate_text)
            matched_constraints = []
            try:
                for event_id, effect, action_pattern, target_pattern, statement in _active_trusted_constraints(conn, session_id):
                    target_matches = any(
                        _safe_glob_match(str(target_pattern), candidate)
                        for candidate in target_candidates
                    )
                    if _safe_glob_match(str(action_pattern), str(tool_name)) and target_matches:
                        matched_constraints.append(
                            {
                                "directive_event_id": str(event_id),
                                "effect": str(effect),
                                "statement": str(statement),
                            }
                        )
            except Exception as exc:
                return {
                    "allowed": False,
                    "reason": f"Harter Directive-Matcher ungueltig: {exc}",
                    "directives": event_ids,
                }
            denied = [item for item in matched_constraints if item["effect"] == "DENY"]
            if denied:
                return {
                    "allowed": False,
                    "reason": "Expliziter verifizierter Nutzer-Constraint blockiert diese Aktion.",
                    "reminder_id": str(reminder_id),
                    "directives": event_ids,
                    "matched_constraints": matched_constraints,
                }
            authorizers = [item for item in matched_constraints if item["effect"] == "REQUIRE_REMINDER"]
            if not authorizers:
                return {
                    "allowed": False,
                    "reason": "Kein verifizierter positiver Autorisierungs-Constraint trifft diese Mutation; fail-closed.",
                    "reminder_id": str(reminder_id),
                    "directives": event_ids,
                    "matched_constraints": matched_constraints,
                }
            try:
                invariant_result = _check_active_invariants(conn, tool_name, args, session_id)
            except Exception as exc:
                return {
                    "allowed": False,
                    "reason": f"State-Invarianten konnten nicht sicher ausgewertet werden: {exc}",
                    "reminder_id": str(reminder_id),
                    "directives": event_ids,
                }
            if not invariant_result["allowed"]:
                return {
                    "allowed": False,
                    "reason": "Verifizierte Zustandsinvariante blockiert den vorgeschlagenen Endzustand.",
                    "reminder_id": str(reminder_id),
                    "directives": event_ids,
                    "invariant_violations": invariant_result["violations"],
                }
            return {
                "allowed": True,
                "reason": "Exakter Reminder vorhanden; harte Constraints und Zustandsinvarianten wurden deterministisch geprueft.",
                "reminder_id": str(reminder_id),
                "directives": event_ids,
                "matched_constraints": matched_constraints,
            }
    finally:
        conn.close()


def output_check(proposed_text: str, *, session_id: str | None = None, limit: int = 12) -> dict[str, Any]:
    """Bridge/Client-Ausgabecheck; harte Regeln werden unabhaengig vom RAG-Top-k geladen."""
    text = str(proposed_text or "")
    key = _session_key({"session_id": session_id} if session_id else {})
    context = directive_context("OUTPUT " + text, limit=limit)
    denied = []
    conn = _workflow_connection()
    if conn is None:
        return {
            "allowed": False,
            "reason": "PostgreSQL-Direktivengedaechtnis nicht erreichbar; fail-closed.",
            "directives": context["directives"],
        }
    try:
        _ensure_directive_tables(conn)
        try:
            for event_id, effect, action_pattern, target_pattern, statement in _active_trusted_constraints(conn, key):
                if str(effect) != "DENY":
                    continue
                if _safe_glob_match(str(action_pattern), "OUTPUT") and _safe_glob_match(str(target_pattern), text):
                    denied.append({
                        "directive_event_id": str(event_id),
                        "statement": str(statement),
                    })
        except Exception as exc:
            return {
                "allowed": False,
                "reason": f"Harter Output-Matcher ungueltig: {exc}",
                "denied_by": [{"statement": "fail-closed"}],
                "directives": context["directives"],
                "enforcement": "HARD nur wenn Bridge/Client diesen Check vor Ausgabe zwingend aufruft",
            }

        try:
            _ensure_workflow_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT state FROM {_MEMORY_SCHEMA}.workflow_runtime WHERE session_id=%s AND schema_version=%s",
                    (key, _RUNTIME_SCHEMA),
                )
                runtime_row = cur.fetchone()
            runtime_state = runtime_row[0] if runtime_row and isinstance(runtime_row[0], dict) else {}
            pending = list(runtime_state.get("pending_verification") or [])
            if pending:
                for rule in _active_learning_rules(key):
                    if rule["status"] != "ACTIVE":
                        continue
                    if rule["rule_kind"] == "REQUIRE_REREAD_AFTER_MUTATION":
                        denied.append(
                            {
                                "learning_rule_id": rule["rule_id"],
                                "statement": "Finaler Output blockiert: Eine erfolgreiche Mutation wartet noch auf direkte Ruecklesung.",
                                "pending_verification": pending,
                            }
                        )
        except Exception as exc:
            return {
                "allowed": False,
                "reason": f"Gelernter Output-Guard konnte nicht sicher geprueft werden: {exc}",
                "denied_by": [{"statement": "learning-guard fail-closed"}],
                "directives": context["directives"],
                "enforcement": "HARD nur wenn Bridge/Client diesen Check vor Ausgabe zwingend aufruft",
            }

        return {
            "allowed": not denied,
            "reason": "kein harter Output-DENY getroffen" if not denied else "Output durch aktive Direktive oder gelernte Regel blockiert",
            "denied_by": denied,
            "directives": context["directives"],
            "learning_rules": learning_context("OUTPUT " + text, session_id=key, limit=limit)["rules"],
            "enforcement": "HARD nur wenn Bridge/Client diesen Check vor Ausgabe zwingend aufruft",
        }
    finally:
        conn.close()


def _load_all() -> dict[str, Any]:
    conn = None
    try:
        conn = _workflow_connection()
        if conn is not None:
            _ensure_workflow_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT session_id,state FROM {_MEMORY_SCHEMA}.workflow_runtime WHERE schema_version=%s",
                    (_RUNTIME_SCHEMA,),
                )
                sessions = {
                    str(session_id): state
                    for session_id, state in cur.fetchall()
                    if isinstance(state, dict)
                }
            if sessions:
                return {"schema": _RUNTIME_SCHEMA, "sessions": sessions}
    except Exception:
        pass
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    try:
        data = json.loads(_RUNTIME_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("schema") == _RUNTIME_SCHEMA:
            return data
    except Exception:
        pass
    return {"schema": _RUNTIME_SCHEMA, "sessions": {}}


def _save_all(data: dict[str, Any]) -> None:
    sessions = data.get("sessions") if isinstance(data, dict) else {}
    conn = None
    try:
        conn = _workflow_connection()
        if conn is not None:
            _ensure_workflow_table(conn)
            with conn.cursor() as cur:
                for session_id, state in (sessions or {}).items():
                    if not isinstance(state, dict):
                        continue
                    cur.execute(
                        f"""
                        INSERT INTO {_MEMORY_SCHEMA}.workflow_runtime(session_id,schema_version,state,updated_at)
                        VALUES (%s,%s,%s::jsonb,now())
                        ON CONFLICT (session_id) DO UPDATE SET
                            schema_version=EXCLUDED.schema_version,
                            state=EXCLUDED.state,
                            updated_at=now()
                        """,
                        (str(session_id), _RUNTIME_SCHEMA, json.dumps(state, ensure_ascii=False)),
                    )
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    try:
        _RUNTIME_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = _RUNTIME_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(_RUNTIME_PATH)
    except Exception:
        pass


def _get_session(data: dict[str, Any], key: str) -> dict[str, Any]:
    sessions = data.setdefault("sessions", {})
    session = sessions.get(key)
    if not isinstance(session, dict):
        session = _default_session()
        sessions[key] = session
    base = _default_session()
    base.update(session)
    if str(base.get("mode") or MODE_DISCOVER) == MODE_BUILD_ALLOWED:
        base["mode"] = MODE_SURGICAL
        base["mode_user_instruction"] = "Legacy BUILD_ALLOWED als SURGICAL weitergefuehrt; der Modus erteilt keine Zusatzberechtigung."
    elif str(base.get("mode") or MODE_DISCOVER) not in _ALLOWED_MODES:
        base["mode"] = MODE_DISCOVER
        base["mode_user_instruction"] = "Legacy/ungueltiger Modus beim Laden auf DISCOVER zurueckgesetzt."

    # Alte Shell-Laeufe konnten ihr cwd als vermeintliches Mutationsziel in
    # pending_verification ablegen. Ein Verzeichnis kann durch vps.read_file
    # niemals als Gegenpruefung erfuellt werden und erzeugt sonst einen
    # permanenten VERIFY-Deadlock. Solche Altlasten werden beim Laden geheilt.
    pending = [
        str(path)
        for path in list(base.get("pending_verification") or [])
        if str(path).strip() and not Path(str(path)).is_dir()
    ]
    base["pending_verification"] = pending
    if base.get("state") == STATE_VERIFY and not pending:
        base["state"] = STATE_FOCUSED_READING

    sessions[key] = base
    return base


def set_mode(
    mode: str,
    user_instruction: str,
    session_id: str | None = None,
    *,
    authority_source: str = "CALLER_DECLARED",
) -> dict[str, Any]:
    mode = str(mode or "").strip().upper()
    instruction = str(user_instruction or "").strip()
    if mode == MODE_BUILD_ALLOWED:
        mode = MODE_SURGICAL
    if mode not in _ALLOWED_MODES:
        raise ValueError(f"Unbekannter Modus: {mode}. Erlaubt: {sorted(_ALLOWED_MODES)}")
    if len(instruction) < 8:
        raise ValueError("Mode-Wechsel braucht einen expliziten Nutzerauftrag als sichtbare Begruendung.")

    key = _session_key({"session_id": session_id} if session_id else {})
    authority_source = str(authority_source or "CALLER_DECLARED").strip().upper()
    with _LOCK:
        all_state = _load_all()
        session = _get_session(all_state, key)
        old_mode = str(session.get("mode") or MODE_DISCOVER)
        session["mode"] = mode
        session["mode_user_instruction"] = instruction[:1000]
        session["mode_changed_at"] = time.time()
        session["state"] = (
            STATE_VERIFY
            if session.get("pending_verification")
            else (STATE_MANUAL_DISCOVERY if bool(session.get("path_inventory_complete")) else STATE_PATH_INVENTORY)
        )
        session["reads_since_mutation"] = 0
        session["distinct_read_paths"] = []
        event = {
            "ts": time.time(),
            "tool": "harness.set_mode",
            "node": "MODE_CHANGE",
            "decision": DECISION_ALLOW,
            "ok": True,
            "before": old_mode,
            "after": mode,
            "paths": [],
            "reason": instruction[:300],
            "authority_source": authority_source,
            "verification_satisfied": None,
        }
        recent = list(session.get("recent_events") or [])
        recent.append(event)
        session["recent_events"] = recent[-_RECENT_LIMIT:]
        _save_all(all_state)
        return {
            "session": key,
            "old_mode": old_mode,
            "mode": mode,
            "state": session["state"],
            "user_instruction": session["mode_user_instruction"],
            "authority_provenance": authority_source,
        }


def _path_values(args: dict[str, Any]) -> list[str]:
    values: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            if value.startswith("/"):
                try:
                    values.append(str(Path(value).resolve(strict=False)))
                except Exception:
                    pass
            return
        if isinstance(value, dict):
            for nested in value.values():
                walk(nested)
            return
        if isinstance(value, (list, tuple)):
            for nested in value:
                walk(nested)

    walk(args)
    return values


def _portfolio_paths(args: dict[str, Any], tool_name: str | None = None) -> list[str]:
    root = str(PORTFOLIO_ROOT)
    if PORTFOLIO_ROOT == Path("/"):
        paths = [p for p in _path_values(args) if Path(p).is_absolute()]
    else:
        paths = [p for p in _path_values(args) if p == root or p.startswith(root + "/")]

    if tool_name == "vps.shell":
        cwd_raw = args.get("cwd")
        command = args.get("command", args.get("cmd", ""))
        try:
            cwd = Path(str(cwd_raw)).resolve(strict=False)
        except Exception:
            cwd = PORTFOLIO_ROOT
        # cwd beschreibt nur den Ausfuehrungskontext. Es ist kein mutiertes Ziel
        # und darf deshalb niemals als spaeter zu verifizierender Pfad landen.
        cwd_value = str(cwd)
        paths = [path for path in paths if path != cwd_value]
        if isinstance(command, str):
            try:
                tokens = shlex.split(command)
            except Exception:
                tokens = command.split()
            for index, token in enumerate(tokens):
                token = token.strip()
                if not token or index == 0 or token.startswith("-") or token in {"|", "&&", ";"}:
                    continue
                candidate = Path(token)
                path_like = (
                    candidate.is_absolute()
                    or "/" in token
                    or token.startswith(".")
                    or bool(candidate.suffix)
                )
                if not path_like:
                    continue
                if not candidate.is_absolute():
                    candidate = cwd / candidate
                try:
                    resolved = candidate.resolve(strict=False)
                except Exception:
                    continue
                if resolved == PORTFOLIO_ROOT or PORTFOLIO_ROOT in resolved.parents:
                    value = str(resolved)
                    if value not in paths:
                        paths.append(value)
        if len(paths) > 1 and root in paths:
            paths = [p for p in paths if p != root]
    return paths


def _inside_control_plane(path: str | None) -> bool:
    if not path:
        return False
    try:
        resolved = Path(path).resolve(strict=False)
    except Exception:
        return False
    return resolved == CONTROL_PLANE_ROOT or CONTROL_PLANE_ROOT in resolved.parents


def _control_plane_validation_command(tool_name: str, args: dict[str, Any]) -> bool:
    """Erlaubt im CONTROL_PLANE nur eng begrenzte Syntax-/Regressionstests."""
    if tool_name != "vps.shell":
        return False
    try:
        cwd = Path(str(args.get("cwd") or "")).resolve(strict=False)
    except Exception:
        return False
    command = args.get("command", args.get("cmd", ""))
    if not isinstance(command, str) or not command.strip():
        return False
    if cwd == Path("/etc/nginx") and command.strip() in {
        "nginx -t",
        "nginx -t -e stderr",
    }:
        return True
    if cwd != CONTROL_PLANE_ROOT:
        return False
    try:
        tokens = shlex.split(command)
    except Exception:
        return False
    if not tokens or any(token in {"|", "||", "&&", ";", ">", ">>", "<"} for token in tokens):
        return False
    if tokens and tokens[0] == "PYTHONPYCACHEPREFIX=/tmp/vps_mcp_pycache":
        tokens = tokens[1:]
    if tokens[:3] == ["python3", "-m", "py_compile"]:
        targets = tokens[3:]
        if not targets:
            return False
        for raw in targets:
            if raw.startswith("-"):
                return False
            target = (cwd / raw).resolve(strict=False)
            if not _inside_control_plane(str(target)) or target.suffix != ".py":
                return False
        return True
    if tokens[:3] == ["python3", "-m", "pytest"]:
        targets = [token for token in tokens[3:] if not token.startswith("-")]
        allowed_flags = {"-q", "--quiet", "-x", "--maxfail=1"}
        flags = [token for token in tokens[3:] if token.startswith("-")]
        if any(flag not in allowed_flags for flag in flags):
            return False
        if not targets:
            return False
        for raw in targets:
            target = (cwd / raw).resolve(strict=False)
            if not _inside_control_plane(str(target)):
                return False
            if target.suffix != ".py" or "tests" not in target.parts:
                return False
        return True
    return False


def _control_plane_nginx_reload(tool_name: str, args: dict[str, Any]) -> bool:
    """Exakt eine eng begrenzte Control-Plane-Mutation: nginx nach gepruefter Config reloaden."""
    exact_command = False
    if tool_name == "vps.exec_allowlisted":
        argv = args.get("argv")
        exact_command = (
            isinstance(argv, list)
            and [str(x) for x in argv] == ["systemctl", "reload", "nginx"]
        )
    elif tool_name == "vps.shell":
        command = args.get("command", args.get("cmd", ""))
        exact_command = isinstance(command, str) and command.strip() == "systemctl reload nginx"
    if not exact_command:
        return False
    try:
        cwd = Path(str(args.get("cwd") or "")).resolve(strict=False)
    except Exception:
        return False
    return cwd == CONTROL_PLANE_ROOT


def _primary_mutation_target(tool_name: str, args: dict[str, Any]) -> str | None:
    if tool_name in {"vps.edit_file", "vps.write_file", "vps.delete"}:
        raw = args.get("path")
    elif tool_name == "vps.move":
        raw = args.get("source", args.get("path"))
    else:
        raw = None
    if not isinstance(raw, str) or not raw:
        return None
    try:
        resolved = Path(raw).resolve(strict=False)
    except Exception:
        return None
    if resolved == PORTFOLIO_ROOT or PORTFOLIO_ROOT in resolved.parents:
        return str(resolved)
    return None


def _guidance_for(session: dict[str, Any], node: str, paths: list[str]) -> tuple[str, ...]:
    guidance: list[str] = []
    recent = list(session.get("recent_events") or [])
    if node in _READISH_NODES and paths:
        same = sum(1 for event in recent[-5:] if paths[0] in (event.get("paths") or []))
        if same >= 2:
            guidance.append(
                "Du kreist mehrfach um dieselbe Datei. Lies ruhig weiter, aber eine Seitenkante "
                "(Geschwisterdatei/Suche/anderer Bereich) ist jetzt wahrscheinlich informativer."
            )
    if session.get("state") == STATE_VERIFY:
        guidance.append("Voriger Eingriff wartet auf Gegenlesen/Verifikation.")
    if session.get("state") == STATE_RECOVER:
        guidance.append("Nach einem Block erst wieder Bodenhaftung durch Lesen/Suchen herstellen.")
    return tuple(guidance)


def _task_scope_patterns(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]


def _task_scope_authority_verified(layer: dict[str, Any]) -> bool:
    provenance = layer.get("provenance") if isinstance(layer.get("provenance"), dict) else {}
    source = str(provenance.get("source") or provenance.get("source_kind") or "").strip().upper()
    created_actor = str(layer.get("created_actor") or "").strip().upper()
    # Provenienzfelder allein sind keine Autoritaet: harness.create_layer ist auch fuer
    # ChatGPT erreichbar. Hart wirksam wird ein TASK deshalb nur, wenn der serverseitig
    # persistierte CREATE-Actor vom authentifizierten Daniel-Dashboard stammt UND die
    # dazugehoerige Dashboard-Provenienz explizit verifiziert ist.
    return (
        created_actor == "DANIEL_DASHBOARD"
        and source == "CHATGPTHARNESS"
        and provenance.get("authority_verified") is True
    )


def _task_scope_targets(args: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("path", "source", "destination", "target", "cwd", "name", "url", "provider", "stream_id"):
        value = args.get(key)
        if isinstance(value, str) and value.strip() and value.strip() not in values:
            values.append(value.strip())
    return values


def _task_scope_targets_for_action(tool_name: str, args: dict[str, Any]) -> list[str]:
    targets = _task_scope_targets(args)
    if tool_name in {"vps.shell", "vps.exec_allowlisted"}:
        script_targets = _scoped_script_targets(tool_name, args)
        if script_targets:
            cwd = str(args.get("cwd") or "").strip()
            targets = [target for target in targets if target != cwd]
            for target in script_targets:
                if target not in targets:
                    targets.append(target)
    return targets


def task_scope_snapshot(
    session_id: str | None = None,
    *,
    layer_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    snapshot = layer_snapshot if isinstance(layer_snapshot, dict) else harness_layers_snapshot(session_id)
    layers = list(snapshot.get("layers") or [])
    core = next((item for item in layers if item.get("layer_id") == "core.task_scope"), None)
    core_effective = str((core or {}).get("effective_status") or "ACTIVE")
    active_tasks = [
        item for item in layers
        if item.get("kind") == "TASK" and item.get("effective_status") == "ACTIVE"
    ]
    active_tasks.sort(
        key=lambda item: (
            float(item.get("last_event_at") or item.get("created_at") or 0.0),
            str(item.get("layer_id") or ""),
        )
    )
    visible = active_tasks[-1] if active_tasks else None
    verified = [
        item for item in active_tasks
        if _task_scope_authority_verified(item)
    ]
    scope_conflict = core_effective == "ACTIVE" and len(verified) > 1
    enforced = verified[0] if len(verified) == 1 and core_effective == "ACTIVE" else None
    selected = enforced or visible
    scope = selected.get("scope") if isinstance(selected, dict) and isinstance(selected.get("scope"), dict) else {}
    provenance = (
        selected.get("provenance")
        if isinstance(selected, dict) and isinstance(selected.get("provenance"), dict)
        else {}
    )
    return {
        "core_effective_status": core_effective,
        "active_task_count": len(active_tasks),
        "verified_active_task_count": len(verified),
        "visible_layer_id": visible.get("layer_id") if isinstance(visible, dict) else None,
        "layer_id": enforced.get("layer_id") if isinstance(enforced, dict) else None,
        "task_id": scope.get("task_id") or (enforced.get("layer_id") if isinstance(enforced, dict) else None),
        "raw_goal": scope.get("raw_goal") or scope.get("goal") or "",
        "allowed_tool_patterns": _task_scope_patterns(scope.get("allowed_tool_patterns")),
        "allowed_target_patterns": _task_scope_patterns(scope.get("allowed_target_patterns")),
        "completion_criteria": scope.get("completion_criteria") or [],
        "sidequest_policy": str(scope.get("sidequest_policy") or "park_only"),
        "authority_verified": bool(enforced) or scope_conflict,
        "hard_enforced": bool(enforced) or scope_conflict,
        "scope_conflict": scope_conflict,
        "conflicting_layer_ids": [str(item.get("layer_id") or "") for item in verified] if scope_conflict else [],
        "provenance": provenance,
    }


def _build_target_pattern_is_bounded(pattern: str) -> bool:
    normalized = str(pattern or "").strip().replace("\\", "/")
    if not normalized.startswith("/"):
        return False
    if not any(char in normalized for char in "*?["):
        return normalized != "/" and ".." not in Path(normalized).parts
    prefix = re.split(r"[*?\[]", normalized, maxsplit=1)[0].rstrip("/")
    parts = [part for part in prefix.split("/") if part]
    return len(parts) >= 3


def _scope_matches_task_target(scope: dict[str, Any], target: str) -> bool:
    try:
        resolved = str(Path(target).expanduser().resolve(strict=False))
    except Exception:
        return False
    return any(
        _build_target_pattern_is_bounded(pattern) and fnmatch.fnmatch(resolved, pattern)
        for pattern in (scope.get("allowed_target_patterns") or [])
    )


def _scoped_script_targets(tool_name: str, args: dict[str, Any]) -> list[str]:
    """Return explicit script/test paths from one direct interpreter invocation."""
    if tool_name == "vps.shell":
        raw_command = args.get("command", args.get("cmd", ""))
        if not isinstance(raw_command, str) or not raw_command.strip():
            return []
        if any(char in raw_command for char in ("|", ";", "&", ">", "<", "`", "$", "\n", "\r")):
            return []
        try:
            tokens = shlex.split(raw_command)
        except Exception:
            return []
    elif tool_name == "vps.exec_allowlisted":
        raw_argv = args.get("argv")
        if not isinstance(raw_argv, (list, tuple)) or not raw_argv:
            return []
        tokens = [str(part) for part in raw_argv]
    else:
        return []

    if len(tokens) < 2 or Path(tokens[0]).name.lower() not in {"python", "python3", "node", "deno"}:
        return []
    cwd_raw = args.get("cwd")
    if not isinstance(cwd_raw, str) or not Path(cwd_raw).is_absolute():
        return []
    cwd = Path(cwd_raw).expanduser().resolve(strict=False)

    if len(tokens) >= 4 and tokens[1] == "-m" and tokens[2] in {"pytest", "py_compile"}:
        raw_targets = tokens[3:]
        if not raw_targets or any(part.startswith("-") for part in raw_targets):
            return []
    else:
        raw_targets = [tokens[1]]
        if raw_targets[0].startswith("-"):
            return []

    resolved_targets: list[str] = []
    script_suffixes = {".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx"}
    for raw_target in raw_targets:
        path = Path(raw_target).expanduser()
        if not path.is_absolute():
            path = cwd / path
        path = path.resolve(strict=False)
        if path.suffix.lower() not in script_suffixes or not path.is_file():
            return []
        resolved_targets.append(str(path))
    return resolved_targets


def _direct_script_execution_allowed(
    action_node: str,
    tool_name: str,
    args: dict[str, Any],
) -> bool:
    if action_node != NODE_SHELL_AUTOMATION:
        return False
    if tool_name not in {"vps.shell", "vps.exec_allowlisted"}:
        return False
    return bool(_scoped_script_targets(tool_name, args))


def _task_scope_conflict_decision(
    tool_name: str,
    current_state: str,
    scope: dict[str, Any],
) -> WorkflowDecision:
    conflicts = ", ".join(scope.get("conflicting_layer_ids") or [])
    return WorkflowDecision(
        decision=DECISION_BLOCK,
        state=current_state,
        action_node=NODE_TASK_SCOPE,
        tool_name=tool_name,
        project_scoped=True,
        reason="TASK_SCOPE_BLOCK: mehrere verifizierte aktive TASK-Layer: " + conflicts,
        next_state_on_success=current_state,
        next_state_on_failure=current_state,
        guidance=("Task-Konflikt im Control-/Dashboard-Kanal aufloesen; keinen Arbeitszweig erraten.",),
        allowed_neighbors=("harness.graph", "harness.layers", "harness.layer_set", "harness.full_activate"),
    )


def _task_scope_preflight(
    tool_name: str,
    args: dict[str, Any],
    *,
    session_id: str,
    current_state: str,
) -> WorkflowDecision | None:
    # A direct script invocation is tied to the current user action; it does not
    # require a second Dashboard TASK record or a read-as-permission ritual.
    if tool_name in {"vps.shell", "vps.exec_allowlisted"} and _scoped_script_targets(tool_name, args):
        return None
    if tool_name in _TASK_SCOPE_CONTROL_TOOLS:
        return None
    scope = task_scope_snapshot(session_id)
    if not scope.get("hard_enforced"):
        return None
    if scope.get("scope_conflict"):
        return _task_scope_conflict_decision(tool_name, current_state, scope)

    tool_patterns = list(scope.get("allowed_tool_patterns") or [])
    if not tool_patterns:
        return WorkflowDecision(
            decision=DECISION_BLOCK,
            state=current_state,
            action_node=NODE_TASK_SCOPE,
            tool_name=tool_name,
            project_scoped=True,
            reason="TASK_SCOPE_BLOCK: Verifizierter aktiver TASK-Scope hat keine allowed_tool_patterns; fail-closed.",
            next_state_on_success=current_state,
            next_state_on_failure=current_state,
            guidance=("Auftragsscope im Control-/Dashboard-Kanal korrigieren; Nebenpfad nicht verfolgen.",),
            allowed_neighbors=("harness.graph",),
        )
    if not any(fnmatch.fnmatch(tool_name, pattern) for pattern in tool_patterns):
        return WorkflowDecision(
            decision=DECISION_BLOCK,
            state=current_state,
            action_node=NODE_TASK_SCOPE,
            tool_name=tool_name,
            project_scoped=True,
            reason=(
                "TASK_SCOPE_BLOCK: Tool liegt ausserhalb des aktuell verifizierten Auftrags "
                f"{scope.get('task_id') or scope.get('layer_id') or ''}."
            ),
            next_state_on_success=current_state,
            next_state_on_failure=current_state,
            guidance=("Nebenfund nur parken; erst den aktuellen Auftrag bis zum Abschlusskriterium fuehren.",),
            allowed_neighbors=("harness.graph",),
        )

    target_patterns = list(scope.get("allowed_target_patterns") or [])
    targets = _task_scope_targets_for_action(tool_name, args)
    if target_patterns and targets:
        outside = [
            target for target in targets
            if not any(fnmatch.fnmatch(target, pattern) for pattern in target_patterns)
        ]
        if outside:
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current_state,
                action_node=NODE_TASK_SCOPE,
                tool_name=tool_name,
                project_scoped=True,
                reason=(
                    "TASK_SCOPE_BLOCK: Ziel liegt ausserhalb des aktuell verifizierten Auftrags: "
                    + ", ".join(outside[:3])
                ),
                next_state_on_success=current_state,
                next_state_on_failure=current_state,
                guidance=("Nebenfund nur parken; Ziel nicht weiter verfolgen.",),
                allowed_neighbors=("harness.graph",),
            )
    return None


def preflight_action(tool_name: str, args: dict[str, Any] | None) -> WorkflowDecision:
    args = args if isinstance(args, dict) else {}
    key = _session_key(args)
    with _LOCK:
        all_state = _load_all()
        session = _get_session(all_state, key)
        current = str(session.get("state") or STATE_MANUAL_DISCOVERY)
        mode = str(session.get("mode") or MODE_DISCOVER)

    scope_block = _task_scope_preflight(tool_name, args, session_id=key, current_state=current)
    if scope_block is not None:
        return scope_block

    task_scope = task_scope_snapshot(key)
    base = base_evaluate_action(tool_name, args)
    if not base.project_scoped:
        return WorkflowDecision(
            decision=base.decision,
            state="OUTSIDE_PORTFOLIO_POLICY",
            action_node=base.action_node,
            tool_name=tool_name,
            project_scoped=False,
            reason=base.reason,
            next_state_on_success="OUTSIDE_PORTFOLIO_POLICY",
            next_state_on_failure="OUTSIDE_PORTFOLIO_POLICY",
        )

    paths = _portfolio_paths(args, tool_name)
    guidance = _guidance_for(session, base.action_node, paths)

    if tool_name == "harness.path_scan" and bool(args.get("reset", False)) and mode != MODE_CONTROL_PLANE:
        return WorkflowDecision(
            decision=DECISION_BLOCK,
            state=current,
            action_node=base.action_node,
            tool_name=tool_name,
            project_scoped=True,
            reason="reset=true verwirft den laufenden Pfadscan und ist nur im expliziten CONTROL_PLANE-Modus erlaubt.",
            next_state_on_success=current,
            next_state_on_failure=current,
            guidance=("Fuer einen normalen Scan reset=false verwenden.",),
            allowed_neighbors=("harness.path_scan (reset=false)", "harness.graph", "harness.set_mode"),
        )

    preinventory_observation = tool_name in _PREINVENTORY_OBSERVATION_TOOLS
    if tool_name == "network.http_probe":
        method = str(args.get("method") or "GET").strip().upper()
        preinventory_observation = method in {"GET", "HEAD", "OPTIONS"} and not bool(args.get("body"))
    if preinventory_observation and not bool(session.get("path_inventory_complete")):
        return WorkflowDecision(
            decision=DECISION_ALLOW,
            state=current,
            action_node=NODE_NAVIGATE,
            tool_name=tool_name,
            project_scoped=True,
            reason="Read-only Beobachtungswerkzeug: darf vor der VPS-Pfadinventur laufen und baut keinen Datei-Lesezustand auf.",
            next_state_on_success=current,
            next_state_on_failure=current,
            guidance=guidance,
        )

    layer_snapshot = harness_layers_snapshot(key)
    path_inventory_layer = next(
        (item for item in layer_snapshot.get("layers", []) if item.get("layer_id") == "core.path_inventory"),
        None,
    )
    path_inventory_enforced = (
        path_inventory_layer is None
        or str(path_inventory_layer.get("effective_status") or "ACTIVE") == "ACTIVE"
    )
    verify_recover_layer = next(
        (item for item in layer_snapshot.get("layers", []) if item.get("layer_id") == "core.verify_recover"),
        None,
    )
    verify_recover_enforced = (
        verify_recover_layer is None
        or str(verify_recover_layer.get("effective_status") or "ACTIVE") == "ACTIVE"
    )

    task_targets = _task_scope_targets_for_action(tool_name, args)
    task_target_patterns = list(task_scope.get("allowed_target_patterns") or [])
    task_scoped_path_access = bool(
        task_scope.get("hard_enforced")
        and not task_scope.get("scope_conflict")
        and task_targets
        and task_target_patterns
        and all(
            any(fnmatch.fnmatch(target, pattern) for pattern in task_target_patterns)
            for target in task_targets
        )
    )

    direct_script_call = (
        tool_name in {"vps.shell", "vps.exec_allowlisted"}
        and bool(_scoped_script_targets(tool_name, args))
    )
    if path_inventory_enforced and current == STATE_PATH_INVENTORY and session.get("path_scan_id") and not bool(session.get("path_inventory_complete")) and not task_scoped_path_access and not direct_script_call:
        control_plane_paths_ok = bool(paths) and all(_inside_control_plane(path) for path in paths)
        control_plane_repair = (
            mode == MODE_CONTROL_PLANE
            and (
                (tool_name in {"vps.read_file", "vps.edit_file", "git.diff"} and control_plane_paths_ok)
                or (
                    tool_name in {"services.status", "services.logs", "services.restart"}
                    and str(args.get("name") or "") == "vps-mcp.service"
                )
                or _control_plane_validation_command(tool_name, args)
                or _control_plane_nginx_reload(tool_name, args)
            )
        )
        if tool_name not in _PATH_INVENTORY_TOOLS and not control_plane_repair and not task_scoped_path_access:
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="Vor dem ersten Inhaltslesen muss die VPS-Pfadinventur vollstaendig abgeschlossen sein. In dieser Phase sind nur Pfade erlaubt.",
                next_state_on_success=STATE_PATH_INVENTORY,
                next_state_on_failure=STATE_PATH_INVENTORY,
                guidance=(),
                allowed_neighbors=(
                    "harness.path_scan",
                    "harness.path_inventory",
                    "harness.graph",
                    "vps.list_roots",
                    "vps.list_files",
                ),
            )

    preliminary = base
    direct_script_execution = (
        preliminary.action_node == NODE_SHELL_AUTOMATION
        and _direct_script_execution_allowed(preliminary.action_node, tool_name, args)
    )
    if direct_script_execution:
        base = base_evaluate_action(tool_name, args, allow_direct_execution=True)

    target = _primary_mutation_target(tool_name, args)
    relaxable_control_validation = (
        mode == MODE_CONTROL_PLANE
        and base.action_node == NODE_SHELL_AUTOMATION
        and _control_plane_validation_command(tool_name, args)
    )
    relaxable_control_reload = (
        mode == MODE_CONTROL_PLANE
        and _control_plane_nginx_reload(tool_name, args)
    )
    if (not base.allowed or base.action_node in _HARD_BLOCK_NODES) and not (
        direct_script_execution
        or relaxable_control_validation
        or relaxable_control_reload
    ):
        return WorkflowDecision(
            decision=DECISION_BLOCK,
            state=current,
            action_node=base.action_node,
            tool_name=tool_name,
            project_scoped=True,
            reason=base.reason,
            next_state_on_success=STATE_RECOVER,
            next_state_on_failure=STATE_RECOVER,
            guidance=guidance,
        )

    effective_mutation = (
        base.action_node in _MUTATION_NODES
        or direct_script_execution
        or relaxable_control_reload
    )
    if effective_mutation:
        learned_guard = _learned_rule_guard(tool_name, args, key, session)
        if not learned_guard.get("allowed", False):
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="LEARNED_RULE_DENIER: " + str(
                    learned_guard.get("reason") or "Aktive gelernte Regel blockiert diese Aktion."
                ),
                next_state_on_success=STATE_RECOVER,
                next_state_on_failure=STATE_RECOVER,
                guidance=guidance + (
                    "Gelernte Regel verlangt erst Gegenlesen/Recovery; Regelstatus bleibt in PostgreSQL nachvollziehbar.",
                ),
                allowed_neighbors=(
                    "harness.learning_context",
                    "harness.graph",
                    "vps.read_file",
                ),
            )
        directive_guard = _directive_guard(tool_name, args, key)
        if not directive_guard.get("allowed", False):
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="DIRECTIVE_DENIER: " + str(directive_guard.get("reason") or "Mutation widerspricht dem Direktiven-Gate."),
                next_state_on_success=STATE_RECOVER,
                next_state_on_failure=STATE_RECOVER,
                guidance=guidance + (
                    "Rufe harness.directive_reminder fuer exakt diese Toolaktion und Argumente auf; erst danach erneut pruefen.",
                ),
                allowed_neighbors=(
                    "harness.directive_reminder",
                    "harness.directive_context",
                    "harness.graph",
                    "vps.read_file",
                ),
            )
        if base.action_node == NODE_CONTROL_RESTART and mode != MODE_CONTROL_PLANE:
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="Der gezielte VPS-MCP-Neustart ist nur im expliziten CONTROL_PLANE-Modus erlaubt.",
                next_state_on_success=STATE_RECOVER,
                next_state_on_failure=STATE_RECOVER,
                guidance=guidance + ("Erst per explizitem Nutzerauftrag CONTROL_PLANE aktivieren.",),
            )
        if verify_recover_enforced and current == STATE_VERIFY and _pending_verification_conflicts(
            tool_name, args, list(session.get("pending_verification") or [])
        ):
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="Vor der naechsten Mutation muss der vorige Eingriff erst gelesen/geprueft werden.",
                next_state_on_success=STATE_VERIFY,
                next_state_on_failure=STATE_RECOVER,
                guidance=guidance + ("Lies das betroffene Ziel direkt erneut; Suche/RAG ersetzt diese Rueckkante nicht.",),
            )
        if verify_recover_enforced and current == STATE_RECOVER:
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="Nach einem Block ist eine weitere Mutation keine gueltige Folgekante. Erst wieder direkt lesen; Suche allein reicht nicht.",
                next_state_on_success=STATE_RECOVER,
                next_state_on_failure=STATE_RECOVER,
                guidance=guidance,
            )

        target = _primary_mutation_target(tool_name, args)
        known_reads = set(session.get("distinct_read_paths") or [])
        empty_dir_delete = False
        symlink_delete = False
        if base.action_node == NODE_SINGLE_DELETE:
            raw_delete_path = args.get("path")
            try:
                raw_delete_obj = Path(str(raw_delete_path)).expanduser()
                symlink_delete = raw_delete_obj.is_absolute() and raw_delete_obj.is_symlink()
            except Exception:
                symlink_delete = False
            if target and not symlink_delete:
                try:
                    target_path = Path(target)
                    empty_dir_delete = target_path.is_dir() and not any(target_path.iterdir())
                except Exception:
                    empty_dir_delete = False
        inspected_delete = empty_dir_delete or symlink_delete

        target_exists = bool(target and Path(target).exists())
        requires_prior_read = (
            base.action_node != NODE_SINGLE_WRITE
            or target_exists
        )
        if int(session.get("reads_since_mutation") or 0) < 1 and requires_prior_read and not inspected_delete:
            return WorkflowDecision(
                decision=DECISION_BLOCK,
                state=current,
                action_node=base.action_node,
                tool_name=tool_name,
                project_scoped=True,
                reason="Im aktuellen Lauf fehlt vor dieser Mutation ein echter Lese-/Pruefschritt; das Ziel ist noch nicht geprueft.",
                next_state_on_success=STATE_RECOVER,
                next_state_on_failure=STATE_RECOVER,
                guidance=guidance + ("Erst Quelle/Umfeld lesen, dann gezielt eingreifen.",),
            )
        if base.action_node in {NODE_SINGLE_EDIT, NODE_SINGLE_DELETE, NODE_SINGLE_MOVE}:
            if target and target not in known_reads and not inspected_delete:
                return WorkflowDecision(
                    decision=DECISION_BLOCK,
                    state=current,
                    action_node=base.action_node,
                    tool_name=tool_name,
                    project_scoped=True,
                    reason="Die konkrete Zieldatei wurde in diesem Lauf noch nicht selbst gelesen.",
                    next_state_on_success=STATE_RECOVER,
                    next_state_on_failure=STATE_RECOVER,
                    guidance=guidance + ("Lies genau die Datei, die du veraendern/loeschen/verschieben willst.",),
                )
            if base.action_node == NODE_SINGLE_MOVE and bool(args.get("overwrite", False)):
                raw_destination = args.get("destination", args.get("target"))
                try:
                    destination = Path(str(raw_destination)).resolve(strict=False) if raw_destination else None
                except Exception:
                    destination = None
                if destination is not None and destination.exists():
                    if destination.is_dir():
                        return WorkflowDecision(
                            decision=DECISION_BLOCK,
                            state=current,
                            action_node=NODE_BULK_MUTATION,
                            tool_name=tool_name,
                            project_scoped=True,
                            reason="Move-overwrite auf einen vorhandenen Ordner wuerde rekursiv Material entfernen und bleibt gesperrt.",
                            next_state_on_success=STATE_RECOVER,
                            next_state_on_failure=STATE_RECOVER,
                            guidance=guidance,
                        )
                    if str(destination) not in known_reads:
                        return WorkflowDecision(
                            decision=DECISION_BLOCK,
                            state=current,
                            action_node=base.action_node,
                            tool_name=tool_name,
                            project_scoped=True,
                            reason="Ein vorhandenes Move-Ziel muss vor overwrite=true selbst vollstaendig gelesen werden.",
                            next_state_on_success=STATE_RECOVER,
                            next_state_on_failure=STATE_RECOVER,
                            guidance=guidance + ("Lies auch die Zieldatei, die durch den Move verschwinden wuerde.",),
                        )
        elif base.action_node in {NODE_SINGLE_WRITE, NODE_META_GENERATION} and target:
            target_path = Path(target)
            if target_path.exists() and target not in known_reads:
                return WorkflowDecision(
                    decision=DECISION_BLOCK,
                    state=current,
                    action_node=base.action_node,
                    tool_name=tool_name,
                    project_scoped=True,
                    reason="Ein vorhandenes Schreibziel muss vor dem Ueberschreiben selbst gelesen werden.",
                    next_state_on_success=STATE_RECOVER,
                    next_state_on_failure=STATE_RECOVER,
                    guidance=guidance,
                )
        return WorkflowDecision(
            decision=DECISION_ALLOW,
            state=current,
            action_node=base.action_node,
            tool_name=tool_name,
            project_scoped=True,
            reason=base.reason,
            next_state_on_success=STATE_VERIFY,
            next_state_on_failure=STATE_RECOVER,
            guidance=guidance,
        )

    if base.action_node in _READISH_NODES:
        if current in {STATE_VERIFY, STATE_RECOVER}:
            next_state = STATE_FOCUSED_READING
        elif int(session.get("reads_since_mutation") or 0) >= 1:
            next_state = STATE_CHANGE_READY
        else:
            next_state = STATE_FOCUSED_READING
        return WorkflowDecision(
            decision=DECISION_ALLOW,
            state=current,
            action_node=base.action_node,
            tool_name=tool_name,
            project_scoped=True,
            reason=base.reason,
            next_state_on_success=next_state,
            next_state_on_failure=STATE_RECOVER,
            guidance=guidance,
        )

    return WorkflowDecision(
        decision=DECISION_ALLOW,
        state=current,
        action_node=base.action_node,
        tool_name=tool_name,
        project_scoped=True,
        reason=base.reason,
        next_state_on_success=current,
        next_state_on_failure=STATE_RECOVER,
        guidance=guidance,
    )


def record_outcome(
    tool_name: str,
    args: dict[str, Any] | None,
    decision: WorkflowDecision,
    result: dict[str, Any] | None,
) -> None:
    if not decision.project_scoped:
        return
    args = args if isinstance(args, dict) else {}
    result = result if isinstance(result, dict) else {}
    ok = bool(result.get("ok"))
    key = _session_key(args)
    paths = _portfolio_paths(args, tool_name)
    is_partial_direct_read = (
        tool_name == "vps.read_file"
        and (args.get("start_line") is not None or args.get("end_line") is not None)
    )

    with _LOCK:
        all_state = _load_all()
        session = _get_session(all_state, key)
        before = str(session.get("state") or STATE_MANUAL_DISCOVERY)

        verification_satisfied = None
        if tool_name == "harness.path_scan":
            if decision.allowed and ok:
                scan_data = result.get("data") if isinstance(result.get("data"), dict) else {}
                session["path_scan_id"] = scan_data.get("scan_id")
                session["path_scan_counts"] = scan_data.get("counts") if isinstance(scan_data.get("counts"), dict) else {}
                session["path_inventory_complete"] = bool(scan_data.get("complete"))
                session["blocked_streak"] = 0
                after = STATE_MANUAL_DISCOVERY if session["path_inventory_complete"] else STATE_PATH_INVENTORY
            else:
                session["path_inventory_complete"] = False
                session["blocked_streak"] = int(session.get("blocked_streak") or 0) + (0 if decision.allowed else 1)
                after = STATE_PATH_INVENTORY
        elif not decision.allowed and decision.action_node == NODE_TASK_SCOPE:
            # PRIO-0 ist kein Fehler-/Recovery-Ereignis. Der Nebenpfad wird nur geparkt,
            # waehrend der laufende Auftrag und sein Workflow-Zustand unveraendert bleiben.
            after = before
            session["blocked_streak"] = int(session.get("blocked_streak") or 0)
        elif not decision.allowed:
            after = STATE_VERIFY if before == STATE_VERIFY else STATE_RECOVER
            session["blocked_streak"] = int(session.get("blocked_streak") or 0) + 1
        elif not ok and decision.action_node in _NAVIGATION_NODES:
            after = before
            session["blocked_streak"] = int(session.get("blocked_streak") or 0)
        elif not ok:
            after = STATE_VERIFY if before == STATE_VERIFY else STATE_RECOVER
            session["blocked_streak"] = 0
        elif decision.action_node in _READISH_NODES and is_partial_direct_read:
            # Ein Ausschnitt darf Orientierung geben, aber weder eine Mutation freischalten
            # noch eine ausstehende Verifikation als erledigt markieren.
            session["blocked_streak"] = 0
            verification_satisfied = False if before == STATE_VERIFY else None
            after = STATE_VERIFY if before == STATE_VERIFY else STATE_FOCUSED_READING
        elif decision.action_node in _READISH_NODES:
            prior_state = before
            session["reads_since_mutation"] = int(session.get("reads_since_mutation") or 0) + 1
            known = list(session.get("distinct_read_paths") or [])
            for path in paths:
                if path not in known:
                    known.append(path)
            session["distinct_read_paths"] = known[-20:]
            session["blocked_streak"] = 0

            pending = set(session.get("pending_verification") or [])
            verification_satisfied = (
                not pending
                or bool(pending.intersection(paths))
                or tool_name in {"git.diff", "git.show"}
            )
            if prior_state == STATE_VERIFY:
                if verification_satisfied:
                    if tool_name in {"git.diff", "git.show"}:
                        remaining_pending = set()
                    else:
                        remaining_pending = pending.difference(paths)
                    session["pending_verification"] = sorted(remaining_pending)
                    after = STATE_VERIFY if remaining_pending else STATE_FOCUSED_READING
                else:
                    after = STATE_VERIFY
            elif prior_state == STATE_RECOVER:
                after = STATE_FOCUSED_READING
            elif len(session["distinct_read_paths"]) >= 2:
                after = STATE_CHANGE_READY
            else:
                after = STATE_FOCUSED_READING
        elif decision.action_node == NODE_SINGLE_DELETE:
            # Ein erfolgreich bestaetigter Delete kann nicht durch Wiederlesen des
            # geloeschten Ziels verifiziert werden. Das Serverwerkzeug setzt deleted=true
            # erst nach vollzogener Entfernung; diese Rueckgabe ist die direkte
            # Verifikation dieses irreversiblen Einzelschritts.
            data = result.get("data") if isinstance(result.get("data"), dict) else {}
            verification_satisfied = bool(data.get("deleted"))
            after = STATE_FOCUSED_READING if verification_satisfied else STATE_VERIFY
            session["reads_since_mutation"] = 0
            session["distinct_read_paths"] = []
            session["pending_verification"] = [] if verification_satisfied else paths
            session["blocked_streak"] = 0
        elif decision.action_node in _STATEFUL_MUTATION_NODES:
            after = STATE_VERIFY
            session["reads_since_mutation"] = 0
            mutated = set(paths)
            session["distinct_read_paths"] = [
                path for path in list(session.get("distinct_read_paths") or [])
                if path not in mutated
            ][-20:]
            pending_now = set(session.get("pending_verification") or [])
            pending_now.update(paths)
            session["pending_verification"] = sorted(pending_now)
            session["blocked_streak"] = 0
        else:
            after = before if decision.state != before else decision.next_state_on_success

        session["state"] = after
        session["last_updated"] = time.time()
        event = {
            "ts": time.time(),
            "tool": tool_name,
            "node": decision.action_node,
            "decision": decision.decision,
            "ok": ok,
            "before": before,
            "after": after,
            "paths": paths[:4],
            "reason": decision.reason,
            "verification_satisfied": verification_satisfied,
        }
        recent = list(session.get("recent_events") or [])
        recent.append(event)
        session["recent_events"] = recent[-_RECENT_LIMIT:]
        _save_all(all_state)

    try:
        _record_experience_action(tool_name, args, decision, result)
    except Exception:
        # Erfahrungsmitschrift darf den eigentlichen Toollauf nicht nachtraeglich faelschen/blockieren.
        pass


def graph_snapshot(session_id: str | None = None) -> dict[str, Any]:
    base = base_graph_snapshot()
    key = _session_key({"session_id": session_id} if session_id else {})
    with _LOCK:
        all_state = _load_all()
        session = _get_session(all_state, key)
    layer_snapshot = harness_layers_snapshot(session_id)
    task_scope = task_scope_snapshot(session_id, layer_snapshot=layer_snapshot)

    workflow_edges = [
        {"from": STATE_PATH_INVENTORY, "to": STATE_MANUAL_DISCOVERY, "on": "complete persisted VPS path inventory"},
        {"from": STATE_MANUAL_DISCOVERY, "to": STATE_FOCUSED_READING, "on": "successful direct source read"},
        {"from": STATE_FOCUSED_READING, "to": STATE_CHANGE_READY, "on": "second distinct direct source read (informational state, not a universal write prerequisite)"},
        {"from": STATE_CHANGE_READY, "to": STATE_VERIFY, "on": "successful allowed mutation"},
        {"from": STATE_VERIFY, "to": STATE_VERIFY, "on": "blocked mutation, navigation or unrelated read"},
        {"from": STATE_VERIFY, "to": STATE_FOCUSED_READING, "on": "direct reread of pending target"},
        {"from": STATE_RECOVER, "to": STATE_FOCUSED_READING, "on": "successful direct source read"},
        {"from": "non-VERIFY state", "to": STATE_RECOVER, "on": "blocked or failed project action"},
    ]
    mode_edges = [
        {"from": MODE_DISCOVER, "to": MODE_SURGICAL, "on": "declared explicit user instruction"},
        {"from": MODE_SURGICAL, "to": MODE_DISCOVER, "on": "declared explicit user instruction"},
        {"from": MODE_DISCOVER, "to": MODE_CONTROL_PLANE, "on": "declared explicit user instruction"},
        {"from": MODE_SURGICAL, "to": MODE_CONTROL_PLANE, "on": "declared explicit user instruction"},
        {"from": MODE_CONTROL_PLANE, "to": MODE_DISCOVER, "on": "declared explicit user instruction"},
    ]
    return {
        "active": layer_snapshot.get("master", {}).get("effective_status") == "ACTIVE",
        "scope": str(PORTFOLIO_ROOT),
        "session": key,
        "runtime": session,
        "harness_layers": layer_snapshot,
        "task_scope": task_scope,
        "workflow_states": [
            STATE_PATH_INVENTORY,
            STATE_MANUAL_DISCOVERY,
            STATE_FOCUSED_READING,
            STATE_CHANGE_READY,
            STATE_VERIFY,
            STATE_RECOVER,
        ],
        "workflow_edges": workflow_edges,
        "intent_modes": [MODE_DISCOVER, MODE_SURGICAL, MODE_CONTROL_PLANE],
        "mode_edges": mode_edges,
        "current_mode": session.get("mode", MODE_DISCOVER),
        "hard_gate": base,
        "delivery_graph": delivery_graph.snapshot(session_id),
        "principles": [
            "PRIO 0: verifizierter aktiver Task-Scope wird vor allen anderen Gates geprueft; Nebenpfade werden nur geparkt",
            "harte Verbote bleiben im serverseitigen Gate",
            "nur direkter Einzel-Read baut Lesezustand auf; Suche/Listung/RAG nicht",
            "Mutation erzeugt VERIFY-Schuld; die konkrete Quelle muss direkt gegengelesen werden",
            "zweite Mutation ohne Gegenlesen wird gestoppt",
            "Block/Fehler fuehrt in RECOVER, ausser VERIFY-Schuld muss erhalten bleiben",
            "Arbeitsmodi beschreiben den Arbeitsstil; sie erteilen keine zweite Freigabe neben der konkreten Nutzeranweisung",
            "ein Dateisuffix wie .py sperrt keinen einzelnen auftragsgebundenen Write",
            "Direkte einzelne Script-Aufrufe brauchen keinen zusaetzlichen TASK-Scope oder Script-Lesebeleg; die bestehenden Tool- und Workflow-Pruefungen gelten",
            "user_instruction-Herkunft ist deklarativ protokolliert, nicht kryptographisch beweisbar",
            "Wiederholungen geben Seitenkanten-Hinweise, blockieren Neugier aber nicht",
            "Laufspur speichert Aktionsmetadaten; Originaldateien bleiben Autoritaet",
        ],
    }


def server_instructions() -> str:
    return (
        base_server_instructions()
        + " Zusaetzlicher Workflow-State: Ein Auftrag kann direktes Quellenlesen verlangen; Suche/Listung/RAG ersetzen einen solchen Nachweis nicht. "
          "Mutation fuehrt zu VERIFY; vor weiterer Mutation muss ein veraendertes bestehendes Ziel direkt gegengelesen werden. "
          "Neue Dateien brauchen einen passenden Auftrag und den exakten Direktiven-Reminder, keine zwei kuenstlich vorgeschriebenen Referenzdateien. "
          "Aktive Modi sind DISCOVER, SURGICAL und CONTROL_PLANE. Die Modi sind keine zweite Autorisierungsstufe: ein auftragsgebundener Write oder Edit wird anhand der konkreten Nutzeranweisung und der vorhandenen Aktionpruefungen bewertet. "
          "Der Dateisuffix sperrt keine Code-Datei. Direkte einzelne Script-Aufrufe brauchen keinen zusaetzlichen TASK-Scope oder Script-Lesebeleg; Bulk-, Hintergrund- und verschleierte Shell-Aktionen bleiben gesperrt. "
          "CONTROL_PLANE erlaubt gezielte Arbeit am bestehenden MCP-Kontrollkoerper nach vorherigem Lesen. "
          "Ein user_instruction-String ist deklarativ und kann serverseitig nicht kryptographisch als echte Nutzereingabe bewiesen werden. "
          "Wenn der Client den aktuellen Nutzer-Rohtext tatsaechlich bereitstellt, muss er vor der Bearbeitung mit harness.experience_message als USER wortgetreu gespeichert werden; niemals aus Erinnerung rekonstruieren. "
          "Vor einer finalen Nutzerantwort muss harness.output_check auf den exakten vorgesehenen Text laufen; nur bei ALLOW darf genau dieser Text anschliessend als ASSISTANT in harness.experience_message gespeichert und ausgegeben werden. "
          "Aktive Lernregeln werden serverseitig hart geprueft; harness.learning_context liefert zusaetzlich relevante ACTIVE/WEAKENED-Regeln als Erinnerung. "
          "harness.graph zeigt Laufzustand, Intent und Rueckkanten."
        + delivery_graph.server_instruction()
    )
