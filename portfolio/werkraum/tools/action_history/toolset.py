from __future__ import annotations

from typing import Any

from .browser_capture import (
    browser_chat_status as build_browser_chat_status,
    link_browser_turn_to_mcp as build_browser_turn_link,
    list_browser_chats as build_browser_chat_list,
    read_browser_chat as build_browser_chat_read,
    read_browser_turn as build_browser_turn_read,
    read_browser_timeline as build_browser_timeline_read,
    set_browser_chat_alias as build_browser_alias,
    verify_browser_capture as build_browser_verify,
)
from .browser_experiments import (
    apply_browser_experiment_action as build_browser_experiment_action,
    browser_experiment_status as build_browser_experiment_status,
    build_browser_experiment_timeline as build_browser_experiment_timeline,
    create_browser_experiment as build_browser_experiment_create,
    export_browser_experiment as build_browser_experiment_export,
    list_browser_experiments as build_browser_experiment_list,
)
from .file_work import (
    ensure_file_work_constitution,
    load_file_work_protocol,
)
from .history import ActionHistory
from .lifecycle import (
    begin_session_once,
    end_session_once,
    session_action,
    startup_session,
)
from .reporting import build_session_report
from .session_continuity import load_session_continuity_protocol
from .tracked_file_ops import TrackedFileOps
from .time_stream import (
    ensure_temporal_trace,
    load_temporal_protocol,
    query_time_stream,
    rebuild_time_stream,
    record_timeline_marker,
    utc_now_payload,
)
from .ui_visible import (
    load_ui_visible_protocol,
    record_ui_visible_bundle,
    record_ui_visible_message,
    ui_visible_export_status as build_ui_visible_export_status,
)

REQUIRED_TOOLS = (
    "history_begin_session",
    "history_startup",
    "history_recent",
    "history_summary",
    "history_session_report",
    "history_verify",
    "history_capabilities",
    "history_record_action",
    "history_end_session",
    "ui_visible_record_message",
    "ui_visible_record_bundle",
    "ui_visible_export_status",
    "browser_capture_list_chats",
    "browser_capture_chat_status",
    "browser_capture_read_chat",
    "browser_capture_read_turn",
    "browser_capture_read_timeline",
    "browser_capture_set_alias",
    "browser_capture_link_turn_to_mcp",
    "browser_capture_verify",
    "browser_experiment_list",
    "browser_experiment_create",
    "browser_experiment_status",
    "browser_experiment_action",
    "browser_experiment_timeline",
    "browser_experiment_export",
    "file_work_context",
    "timeline_now",
    "timeline_record_marker",
    "timeline_query",
    "timeline_rebuild",
    "tracked_read_file",
    "tracked_write_file",
    "tracked_append_file",
    "tracked_reread_own_file",
)


def register_action_history_tools(
    mcp: Any,
    *,
    history: ActionHistory | None = None,
    files: TrackedFileOps | None = None,
) -> dict[str, Any]:
    """Registriert den Action-History-Körper in einem bestehenden FastMCP-kompatiblen Server."""
    active_history = history or ActionHistory()
    active_files = files or TrackedFileOps(active_history)
    registered: dict[str, Any] = {}

    def register(function):
        decorated = mcp.tool()(function)
        registered[function.__name__] = decorated
        return decorated

    def history_begin_session(
        session_id: str,
        new_session_reason: str,
        supersedes_session_id: str | None = None,
        recent_limit: int = 30,
    ) -> dict[str, Any]:
        """Eröffnet bewusst eine neue Session. Grund ist Pflicht; bestehende offene IDs müssen fortgesetzt werden."""
        return startup_session(
            active_history,
            session_id=session_id,
            recent_limit=recent_limit,
            session_intent="new",
            new_session_reason=new_session_reason,
            supersedes_session_id=supersedes_session_id,
            details={"source_tool": "history_begin_session"},
        )

    def history_startup(
        session_id: str | None = None,
        recent_limit: int = 30,
        session_intent: str = "resume",
        new_session_reason: str | None = None,
        supersedes_session_id: str | None = None,
    ) -> dict[str, Any]:
        """Setzt standardmäßig die angegebene kanonische Session fort. Neue Sessions benötigen intent=new und einen Grund."""
        return startup_session(
            active_history,
            session_id=session_id,
            recent_limit=recent_limit,
            session_intent=session_intent,
            new_session_reason=new_session_reason,
            supersedes_session_id=supersedes_session_id,
            details={"source_tool": "history_startup"},
        )

    def history_recent(
        session_id: str | None = None,
        action: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Liest die letzten protokollierten Aktionen."""
        return active_history.list_events(
            session_id=session_id,
            action=action,
            status=status,
            limit=limit,
        )

    def history_summary(session_id: str | None = None) -> dict[str, Any]:
        """Erzeugt eine kompakte Bilanz ausschließlich aus protokollierten Aktionen."""
        return active_history.summary(session_id=session_id)

    def history_session_report(session_id: str) -> dict[str, Any]:
        """Erzeugt ein menschenlesbares Chat-Fazit ohne Dateiinhalte aus der Hash-Kette."""
        return build_session_report(active_history, session_id)

    def history_verify() -> dict[str, Any]:
        """Prüft Hash-Kette und unabhängigen atomischen Endanker."""
        return active_history.verify()

    def history_capabilities() -> dict[str, Any]:
        """Liefert den verpflichtenden Werkzeugvertrag für die Client-Integration."""
        protocol = load_ui_visible_protocol()
        temporal_protocol = load_temporal_protocol()
        file_work_protocol = load_file_work_protocol()
        continuity_protocol = load_session_continuity_protocol()
        return {
            "actor": active_history.actor,
            "required_tools": list(REQUIRED_TOOLS),
            "history_path": str(active_history.path),
            "checkpoint_path": str(active_history.checkpoint_path),
            "rule": "Alle Dateiaktionen über tracked_*; alle übrigen Aktionen über history_record_action.",
            "startup_rule": "history_startup setzt standardmäßig die bekannte kanonische Session dieses UI- oder Arbeitsfadens fort. Ohne session_id entsteht keine neue Session.",
            "session_rule": "Jeder UI- oder Arbeitsfaden behält seine eigene kanonische session_id. Neue Sessions benötigen session_intent=new und einen dokumentierten Grund.",
            "closure_rule": "Laufende Aktionen und Sessionabschluss teilen denselben Verschluss; geschlossene Sessions nehmen keine Arbeit mehr an.",
            "report_rule": "history_end_session und history_session_report erzeugen das Fazit aus der Hash-Kette.",
            "integrity_rule": "history_verify prüft innere Hash-Kette und unabhängigen Endanker gegen Tail-Kürzung.",
            "session_continuity_protocol": {
                "protocol_id": continuity_protocol["protocol_id"],
                "protocol_version": continuity_protocol["protocol_version"],
                "status": continuity_protocol["status"],
                "protocol_path": continuity_protocol["protocol_path"],
                "protocol_sha256": continuity_protocol["protocol_sha256"],
                "default_intent": continuity_protocol["default_intent"],
                "hard_rules": continuity_protocol.get("hard_rules", []),
                "rule": "Resume ist Standard. Neu nur ausdrücklich mit Grund; geschlossene Sessions werden nicht still ersetzt.",
            },
            "ui_visible_protocol": {
                "protocol_id": protocol["protocol_id"],
                "protocol_version": protocol["protocol_version"],
                "status": protocol["status"],
                "protocol_path": protocol["protocol_path"],
                "protocol_sha256": protocol["protocol_sha256"],
                "rule": "Sichtbare UI-Nachrichten regelmäßig über ui_visible_record_message oder ui_visible_record_bundle speichern; vor Sessionende ui_visible_export_status prüfen.",
                "truth_boundary": "Technische History enthält keinen UI-Rohtext, sondern nur Hash, Umfang und Belegpfade. Ein vollständiger Browserexport bleibt unbestätigt, bis eine reale UI-Quelle eingelesen wurde.",
                "philosophy": protocol.get("philosophy", {}),
            },
            "file_work_constitution": {
                "protocol_id": file_work_protocol["protocol_id"],
                "protocol_version": file_work_protocol["protocol_version"],
                "status": file_work_protocol["status"],
                "protocol_path": file_work_protocol["protocol_path"],
                "protocol_sha256": file_work_protocol["protocol_sha256"],
                "purpose": file_work_protocol.get("purpose"),
                "philosophy": file_work_protocol.get("philosophy", {}),
                "mandatory_sequence": file_work_protocol.get("mandatory_sequence", []),
                "hard_rules": file_work_protocol.get("hard_rules", []),
                "rule": "Vor jedem Datei-Such-, Lese-, Schreib-, Erstell-, Verschiebe- oder Ordnungsauftrag file_work_context prüfen und die festgelegte Rücklese-, Watchdog-, Wahrheits- und Obsidian-Kette einhalten.",
            },
            "temporal_trace_protocol": {
                "protocol_id": temporal_protocol["protocol_id"],
                "protocol_version": temporal_protocol["protocol_version"],
                "status": temporal_protocol["status"],
                "protocol_path": temporal_protocol["protocol_path"],
                "protocol_sha256": temporal_protocol["protocol_sha256"],
                "canonical_timezone": temporal_protocol["canonical_timezone"],
                "display_timezone": temporal_protocol["display_timezone"],
                "rule": "Jede Action-History-Zeile ist ein Zeitereignis; bedeutende Aufploppmomente zusätzlich über timeline_record_marker markieren.",
                "parallelism": temporal_protocol.get("time_contract", {}).get("parallelism"),
                "tick_contract": temporal_protocol.get("tick_contract", {}),
            },
            "integration": "register_action_history_tools(existing_mcp) bindet den Körper in den bestehenden Server ein.",
        }

    def history_record_action(
        action: str,
        session_id: str,
        target: str | None = None,
        status: str = "success",
        completeness: str | None = None,
        details: dict[str, Any] | None = None,
        parent_event_id: str | None = None,
    ) -> dict[str, Any]:
        """Protokolliert eine Nicht-Dateiaktion eines anderen MCP-Werkzeugs."""
        with session_action(
            active_history,
            session_id,
            action=action,
            target=target,
        ) as active_session_id:
            return active_history.append(
                action=action,
                target=target,
                status=status,
                session_id=active_session_id,
                completeness=completeness,
                details=details,
                parent_event_id=parent_event_id,
            )

    def history_end_session(
        session_id: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Schließt die Session rennsicher und liefert sofort ihr protokollbasiertes Fazit."""
        ended = end_session_once(active_history, session_id, details=details)
        return {**ended, "report": build_session_report(active_history, session_id)}

    def ui_visible_record_message(
        session_id: str,
        ui_message_id: str,
        role: str,
        content: str,
        project_root: str | None = None,
        timestamp_utc: str | None = None,
        visibility_status: str = "UI_SICHTBAR_IM_AKTIVEN_KONTEXT_PROTOKOLLIERT",
        source_surface: str = "chatgpt.com",
        reply_to_message_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Speichert eine tatsächlich sichtbare UI-Nachricht getrennt von der technischen History und spiegelt sie in den Projektkörper."""
        with session_action(
            active_history,
            session_id,
            action="ui_visible.message_recorded",
            target=ui_message_id,
        ) as active_session_id:
            return record_ui_visible_message(
                active_history,
                session_id=active_session_id,
                ui_message_id=ui_message_id,
                role=role,
                content=content,
                project_root=project_root,
                timestamp_utc=timestamp_utc,
                visibility_status=visibility_status,
                source_surface=source_surface,
                reply_to_message_id=reply_to_message_id,
                metadata=metadata,
            )

    def ui_visible_record_bundle(
        session_id: str,
        messages: list[dict[str, Any]],
        project_root: str | None = None,
        source_surface: str = "chatgpt.com",
    ) -> dict[str, Any]:
        """Speichert mehrere sichtbare UI-Nachrichten idempotent als getrennten Gesprächskörper."""
        with session_action(
            active_history,
            session_id,
            action="ui_visible.bundle_recorded",
            target=f"bundle:{len(messages)}",
        ) as active_session_id:
            return record_ui_visible_bundle(
                active_history,
                session_id=active_session_id,
                messages=messages,
                project_root=project_root,
                source_surface=source_surface,
            )

    def ui_visible_export_status(
        session_id: str,
        project_root: str | None = None,
    ) -> dict[str, Any]:
        """Prüft UI-Gesprächskörper, Projektspiegel, Protokollbindung und weiterhin offene Browserexport-Lücken."""
        with session_action(
            active_history,
            session_id,
            action="ui_visible.export_status",
            target=session_id,
        ) as active_session_id:
            return build_ui_visible_export_status(
                active_history,
                session_id=active_session_id,
                project_root=project_root,
            )

    def browser_capture_list_chats(
        session_id: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Listet browserseitig aufgezeichnete ChatGPT-Gespräche mit Turn-, Lücken-, Import- und Snapshotstatus."""
        with session_action(active_history, session_id, action="browser_capture.list", target="ui_visible_conversations") as active_session_id:
            result = build_browser_chat_list(limit=limit)
            event = active_history.append(
                action="browser_capture.list",
                target="ui_visible_conversations",
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={"chat_count": result.get("count"), "returned": result.get("returned")},
            )
            return {**result, "history_event": event}

    def browser_capture_chat_status(
        session_id: str,
        identifier: str,
    ) -> dict[str, Any]:
        """Liest Manifest, Turns, Importstatus und erkannte Lücken eines Browser-Gesprächskörpers."""
        with session_action(active_history, session_id, action="browser_capture.status", target=identifier) as active_session_id:
            result = build_browser_chat_status(identifier)
            event = active_history.append(
                action="browser_capture.status",
                target=identifier,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "folder": result.get("folder"),
                    "last_complete_turn_id": result.get("manifest", {}).get("last_complete_turn_id"),
                    "gap_count": result.get("manifest", {}).get("gap_count"),
                    "last_import_status": result.get("manifest", {}).get("last_import_status"),
                },
            )
            return {**result, "history_event": event}

    def browser_capture_read_chat(
        session_id: str,
        identifier: str,
        visible_limit: int = 500,
        message_limit: int = 500,
    ) -> dict[str, Any]:
        """Liest sichtbare Ereignisse, fertige Nachrichten, Importe, Snapshots und Lücken eines Browser-Chats."""
        with session_action(active_history, session_id, action="browser_capture.read_chat", target=identifier) as active_session_id:
            result = build_browser_chat_read(identifier, visible_limit=visible_limit, message_limit=message_limit)
            event = active_history.append(
                action="browser_capture.read_chat",
                target=identifier,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "folder": result.get("folder"),
                    "message_count_returned": len(result.get("messages", [])),
                    "visible_events_returned": len(result.get("visible_stream", [])),
                    "gaps_returned": len(result.get("gaps", [])),
                    "raw_ui_text_stored_in_history": False,
                },
            )
            return {**result, "history_event": event}

    def browser_capture_read_turn(
        session_id: str,
        identifier: str,
        turn_id: str,
        limit: int = 1000,
    ) -> dict[str, Any]:
        """Liest alle sichtbaren Zwischenstände und fertigen Nachrichten eines einzelnen Browser-Turns."""
        with session_action(active_history, session_id, action="browser_capture.read_turn", target=turn_id) as active_session_id:
            result = build_browser_turn_read(identifier, turn_id, limit=limit)
            event = active_history.append(
                action="browser_capture.read_turn",
                target=turn_id,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "identifier": identifier,
                    "event_count_returned": len(result.get("events", [])),
                    "message_count_returned": len(result.get("messages", [])),
                    "raw_ui_text_stored_in_history": False,
                },
            )
            return {**result, "history_event": event}

    def browser_capture_read_timeline(
        session_id: str,
        identifier: str,
        provider_id: str | None = None,
        turn_id: str | None = None,
        mcp_session_id: str | None = None,
        event_type: str | None = None,
        binding_status: str | None = None,
        from_utc: str | None = None,
        to_utc: str | None = None,
        include_derived: bool = True,
        limit: int = 5000,
    ) -> dict[str, Any]:
        """Liest B als herkunftsgetrennte gemeinsame Browser-/MCP-Zeitspur mit expliziten Filtern."""
        with session_action(active_history, session_id, action="browser_capture.read_timeline", target=identifier) as active_session_id:
            result = build_browser_timeline_read(
                identifier,
                provider_id=provider_id,
                turn_id=turn_id,
                mcp_session_id=mcp_session_id,
                event_type=event_type,
                binding_status=binding_status,
                from_utc=from_utc,
                to_utc=to_utc,
                include_derived=include_derived,
                limit=limit,
                refresh_projection=True,
            )
            event = active_history.append(
                action="browser_capture.read_timeline",
                target=identifier,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "turn_id": turn_id,
                    "mcp_session_id": mcp_session_id,
                    "binding_status": binding_status,
                    "returned_events": result.get("counts", {}).get("returned_events"),
                    "confirmed_links": result.get("counts", {}).get("confirmed_links"),
                    "derived_links": result.get("counts", {}).get("derived_links"),
                    "primary_sources_modified": False,
                    "raw_ui_text_stored_in_history": False,
                },
            )
            return {**result, "history_event": event}

    def browser_capture_set_alias(
        session_id: str,
        identifier: str,
        alias: str,
    ) -> dict[str, Any]:
        """Setzt einen verständlichen Alias, ohne die Conversation-ID oder Ordneridentität zu ersetzen."""
        with session_action(active_history, session_id, action="browser_capture.set_alias", target=identifier) as active_session_id:
            result = build_browser_alias(identifier, alias)
            event = active_history.append(
                action="browser_capture.set_alias",
                target=result.get("folder_name"),
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={"identifier": identifier, "alias": result.get("alias")},
            )
            return {**result, "history_event": event}

    def browser_capture_link_turn_to_mcp(
        session_id: str,
        identifier: str,
        turn_id: str,
        mcp_session_id: str,
        action_history_event_ids: list[str] | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Bindet einen UI-Turn an MCP; bestätigt nur bei identischer expliziter correlation_id."""
        with session_action(active_history, session_id, action="browser_capture.link_mcp", target=turn_id) as active_session_id:
            result = build_browser_turn_link(
                identifier,
                turn_id,
                mcp_session_id,
                action_history_event_ids,
                correlation_id=correlation_id,
            )
            event = active_history.append(
                action="browser_capture.link_mcp",
                target=turn_id,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "identifier": identifier,
                    "mcp_session_id": mcp_session_id,
                    "correlation_id": correlation_id,
                    "binding_status": result.get("binding_status"),
                    "confirmed": result.get("confirmed"),
                    "action_history_event_ids": action_history_event_ids or [],
                },
            )
            refreshed = build_browser_timeline_read(identifier, limit=5000, refresh_projection=True)
            return {**result, "b_timeline_counts": refreshed.get("counts", {}), "history_event": event}

    def browser_capture_verify(
        session_id: str,
        identifier: str | None = None,
    ) -> dict[str, Any]:
        """Prüft Index, Manifeste, JSONL-Dateien, Turn-Dateien und Lückenablage des Browser-Recorders."""
        with session_action(active_history, session_id, action="browser_capture.verify", target=identifier or "all") as active_session_id:
            result = build_browser_verify(identifier)
            event = active_history.append(
                action="browser_capture.verify",
                target=identifier or "all",
                status="success" if result.get("ok") else "failed",
                session_id=active_session_id,
                completeness="complete",
                details={"checked_folders": result.get("checked_folders"), "finding_count": len(result.get("findings", []))},
            )
            return {**result, "history_event": event}

    def browser_experiment_list(
        session_id: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Listet ausschließlich manuell angelegte Mehrsitzungsversuche; startet keine Kommunikation."""
        with session_action(active_history, session_id, action="browser_experiment.list", target="_experiments") as active_session_id:
            result = build_browser_experiment_list(limit=limit)
            event = active_history.append(
                action="browser_experiment.list",
                target="_experiments",
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={"experiment_count": result.get("count"), "returned": result.get("returned")},
            )
            return {**result, "history_event": event}

    def browser_experiment_create(
        session_id: str,
        name: str,
        description: str | None = None,
        software_versions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Legt nach ausdrücklichem Aufruf einen vorbereiteten Versuch an; fügt keine Chats automatisch hinzu."""
        with session_action(active_history, session_id, action="browser_experiment.create", target=name) as active_session_id:
            result = build_browser_experiment_create(name, description, software_versions=software_versions)
            experiment_id = result.get("experiment", {}).get("experiment_id")
            event = active_history.append(
                action="browser_experiment.create",
                target=experiment_id or name,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "experiment_id": experiment_id,
                    "status": result.get("experiment", {}).get("status"),
                    "automatic_communication_started": False,
                    "participant_count": 0,
                },
            )
            return {**result, "history_event": event}

    def browser_experiment_status(
        session_id: str,
        experiment_id: str,
        refresh_participants: bool = True,
    ) -> dict[str, Any]:
        """Liest Versuchszustand und optional live abgeleitete Teilnehmerwerte, ohne Primärdaten zu verändern."""
        with session_action(active_history, session_id, action="browser_experiment.status", target=experiment_id) as active_session_id:
            result = build_browser_experiment_status(experiment_id, refresh_participants=refresh_participants)
            experiment = result.get("experiment", {})
            event = active_history.append(
                action="browser_experiment.status",
                target=experiment_id,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "experiment_status": experiment.get("status"),
                    "participant_count": sum(1 for item in experiment.get("participants", {}).values() if not item.get("removed_utc")),
                    "active_phase_id": experiment.get("active_phase_id"),
                    "primary_browser_events_modified": False,
                },
            )
            return {**result, "history_event": event}

    def browser_experiment_action(
        session_id: str,
        experiment_id: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Führt genau eine ausdrücklich benannte Versuchsaktion aus; sendet niemals automatisch Nachrichten."""
        with session_action(active_history, session_id, action="browser_experiment.action", target=experiment_id) as active_session_id:
            result = build_browser_experiment_action(
                experiment_id,
                action,
                payload,
                source="explicit_mcp_action",
            )
            event = active_history.append(
                action="browser_experiment.action",
                target=experiment_id,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "experiment_action": action,
                    "experiment_event_id": result.get("event", {}).get("event_id"),
                    "active_phase_id": result.get("experiment", {}).get("active_phase_id"),
                    "automatic_communication_started": False,
                    "raw_ui_text_stored_in_history": False,
                },
            )
            return {**result, "history_event": event}

    def browser_experiment_timeline(
        session_id: str,
        experiment_id: str,
        participant_id: str | None = None,
        phase_id: str | None = None,
        source: str | None = None,
        event_type: str | None = None,
        influence_class: str | None = None,
        include_derived: bool = True,
        limit: int = 20000,
    ) -> dict[str, Any]:
        """Liest die regenerierbare gemeinsame Versuchsspur mit erkennbarer Herkunft und unsicherer Parallelität."""
        with session_action(active_history, session_id, action="browser_experiment.timeline", target=experiment_id) as active_session_id:
            result = build_browser_experiment_timeline(
                experiment_id,
                participant_id=participant_id,
                phase_id=phase_id,
                source=source,
                event_type=event_type,
                influence_class=influence_class,
                include_derived=include_derived,
                limit=limit,
                write_projection=True,
            )
            event = active_history.append(
                action="browser_experiment.timeline",
                target=experiment_id,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "returned_events": result.get("counts", {}).get("returned_events"),
                    "confirmed_links": result.get("counts", {}).get("confirmed_links"),
                    "derived_links": result.get("counts", {}).get("derived_links"),
                    "exact_cross_source_order_claimed": False,
                    "primary_sources_modified": False,
                },
            )
            return {**result, "history_event": event}

    def browser_experiment_export(
        session_id: str,
        experiment_id: str,
    ) -> dict[str, Any]:
        """Erzeugt nach ausdrücklichem Aufruf einen vollständigen Versuchs-Export mit Rohereignissen, Hashliste, sieben menschenlesbaren Ansichten und getrennten 1:1-Gesprächsdokumenten."""
        with session_action(active_history, session_id, action="browser_experiment.export", target=experiment_id) as active_session_id:
            result = build_browser_experiment_export(experiment_id)
            event = active_history.append(
                action="browser_experiment.export",
                target=experiment_id,
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "archive": result.get("archive"),
                    "archive_sha256": result.get("archive_sha256"),
                    "file_count": len(result.get("manifest", {}).get("files", [])),
                    "primary_sources_modified": False,
                },
            )
            return {**result, "history_event": event}

    def file_work_context(
        session_id: str,
        target_path: str | None = None,
        operation: str | None = None,
        project_root: str | None = None,
    ) -> dict[str, Any]:
        """Liefert den globalen Datei-Arbeitsgrundsatz plus realen Watchdog-, Wahrheits-, Obsidian-, Zeitstrom- und Claim-Zustand."""
        with session_action(
            active_history,
            session_id,
            action="file_work.context",
            target=target_path or project_root or "default-project",
        ) as active_session_id:
            result = ensure_file_work_constitution(
                project_root=project_root,
                target_path=target_path,
                operation=operation,
            )
            event = active_history.append(
                action="file_work.context",
                target=target_path or result["state"]["project_root"],
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "summary": "Datei-Arbeitsgrundsatz und realer Projektzustand wurden vor der Dateioperation geprüft.",
                    "operation": operation,
                    "protocol_id": result["protocol"]["protocol_id"],
                    "protocol_sha256": result["protocol"]["protocol_sha256"],
                    "blocking_findings": result["state"]["blocking_findings"],
                    "target_is_generated_layer": result["state"]["target_is_generated_layer"],
                    "watchdog_active": result["state"]["watchdog"]["active"],
                    "truth_generation_id": result["state"]["current_truth"]["generation_id"],
                },
            )
            return {**result, "history_event": event}

    def timeline_now(
        session_id: str,
        project_root: str | None = None,
    ) -> dict[str, Any]:
        """Liefert UTC, Europe/Berlin und den aktuellen Zeitstromstatus."""
        with session_action(
            active_history,
            session_id,
            action="timeline.now",
            target="current-time",
        ) as active_session_id:
            now = utc_now_payload()
            event = active_history.append(
                action="timeline.now",
                target=now["parallel_second_key_utc"],
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={"summary": "Aktuelle UTC- und Berliner Zeit gelesen.", **now},
            )
            return {
                "ok": True,
                "session_id": active_session_id,
                "now": now,
                "history_event": event,
                "time_stream": ensure_temporal_trace(
                    active_history,
                    project_root=project_root,
                ),
            }

    def timeline_record_marker(
        session_id: str,
        title: str,
        summary: str,
        cause: str | None = None,
        locations: list[str] | None = None,
        source_paths: list[str] | None = None,
        related_event_ids: list[str] | None = None,
        related_message_ids: list[str] | None = None,
        tags: list[str] | None = None,
        truth_class: str = "BESTAETIGT_SESSION_MARKER",
        project_root: str | None = None,
    ) -> dict[str, Any]:
        """Markiert einen bedeutenden Aufploppmoment mit Ursache und Belegen."""
        with session_action(
            active_history,
            session_id,
            action="timeline.marker",
            target=title,
        ) as active_session_id:
            return record_timeline_marker(
                active_history,
                session_id=active_session_id,
                title=title,
                summary=summary,
                cause=cause,
                locations=locations,
                source_paths=source_paths,
                related_event_ids=related_event_ids,
                related_message_ids=related_message_ids,
                tags=tags,
                truth_class=truth_class,
                project_root=project_root,
            )

    def timeline_query(
        session_id: str,
        from_utc: str | None = None,
        to_utc: str | None = None,
        session_ids: list[str] | None = None,
        actions: list[str] | None = None,
        text: str | None = None,
        limit: int = 200,
        project_root: str | None = None,
    ) -> dict[str, Any]:
        """Durchsucht parallele Zeitfenster und liefert direkte Belegpfade."""
        with session_action(
            active_history,
            session_id,
            action="timeline.query",
            target=text or from_utc or "latest",
        ) as active_session_id:
            result = query_time_stream(
                active_history,
                from_utc=from_utc,
                to_utc=to_utc,
                session_ids=session_ids,
                actions=actions,
                text=text,
                limit=limit,
                project_root=project_root,
            )
            query_event = active_history.append(
                action="timeline.query",
                target=text or from_utc or "latest",
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "summary": f"Zeitstromabfrage lieferte {result['returned']} von {result['matched']} Treffern.",
                    "query": result["query"],
                    "matched": result["matched"],
                    "returned": result["returned"],
                },
            )
            return {**result, "query_history_event": query_event}

    def timeline_rebuild(
        session_id: str,
        project_root: str | None = None,
    ) -> dict[str, Any]:
        """Baut alle Zeitstromseiten aus der unveränderten Hash-History neu."""
        with session_action(
            active_history,
            session_id,
            action="timeline.rebuild",
            target=str(active_history.path),
        ) as active_session_id:
            result = rebuild_time_stream(
                active_history.path,
                project_root=project_root,
            )
            event = active_history.append(
                action="timeline.rebuild",
                target=result["root_entry"],
                status="success",
                session_id=active_session_id,
                completeness="complete",
                details={
                    "summary": "Zeitstrom vollständig aus der Action-History neu gebaut.",
                    "manifest": result["manifest"],
                    "root_entry": result["root_entry"],
                },
            )
            return {**result, "history_event": event}

    def tracked_read_file(
        path: str,
        session_id: str,
        start_line: int = 1,
        max_lines: int | None = None,
    ) -> dict[str, Any]:
        """Liest eine Werkraum-Datei und protokolliert Vollständigkeit, Hash und Umfang."""
        return active_files.read_text(
            path,
            session_id=session_id,
            start_line=start_line,
            max_lines=max_lines,
        )

    def tracked_write_file(
        path: str,
        content: str,
        session_id: str,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Schreibt atomar und protokolliert Pfad, Umfang und Hash."""
        return active_files.write_text(
            path,
            content,
            session_id=session_id,
            overwrite=overwrite,
        )

    def tracked_append_file(
        path: str,
        content: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Hängt Text an und protokolliert die resultierende Datei."""
        return active_files.append_text(path, content, session_id=session_id)

    def tracked_reread_own_file(
        path: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Liest eine gerade geschriebene Datei vollständig erneut und protokolliert dies separat."""
        return active_files.reread_text(path, session_id=session_id)

    for function in (
        history_begin_session,
        history_startup,
        history_recent,
        history_summary,
        history_session_report,
        history_verify,
        history_capabilities,
        history_record_action,
        history_end_session,
        ui_visible_record_message,
        ui_visible_record_bundle,
        ui_visible_export_status,
        browser_capture_list_chats,
        browser_capture_chat_status,
        browser_capture_read_chat,
        browser_capture_read_turn,
        browser_capture_read_timeline,
        browser_capture_set_alias,
        browser_capture_link_turn_to_mcp,
        browser_capture_verify,
        browser_experiment_list,
        browser_experiment_create,
        browser_experiment_status,
        browser_experiment_action,
        browser_experiment_timeline,
        browser_experiment_export,
        file_work_context,
        timeline_now,
        timeline_record_marker,
        timeline_query,
        timeline_rebuild,
        tracked_read_file,
        tracked_write_file,
        tracked_append_file,
        tracked_reread_own_file,
    ):
        register(function)

    actual = tuple(registered)
    if actual != REQUIRED_TOOLS:
        raise RuntimeError(
            f"Werkzeugvertrag beim Registrieren abweichend: erwartet={REQUIRED_TOOLS!r}, erhalten={actual!r}"
        )

    return registered
