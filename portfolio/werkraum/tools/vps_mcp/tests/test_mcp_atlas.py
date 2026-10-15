from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path

import mcp_atlas as atlas


class MCPAtlasTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "START_HIER.md").write_text("# Projekt\n\nAtlas und Provenienz.\n", encoding="utf-8")
        (self.source / "coordination").mkdir()
        (self.source / "Verweise").mkdir()
        (self.source / "tools").mkdir()
        (self.source / "tools" / "build_obsidian_vault.py").write_text("print('vault')\n", encoding="utf-8")
        self.history = self.root / "history.jsonl"
        self.protocol = self.root / "protocol.json"
        self.protocol.write_text(json.dumps({"protocol_id": "test"}), encoding="utf-8")
        self.saved = {
            name: getattr(atlas, name)
            for name in (
                "ATLAS_ROOT",
                "HISTORY_PATH",
                "PROTOCOL_PATH",
                "STATUS_PATH",
                "PATH_DB",
                "CONCEPT_DB",
                "CHANGE_LOG",
                "CONSENSUS_LOG",
                "CONFLICT_LOG",
                "IDEA_LOG",
                "PROJECT_REVISION_PATH",
                "CLAIM_REGISTER_PATH",
                "VALIDATION_REGISTER_PATH",
                "HANDOFF_REGISTER_PATH",
                "HANDOFF_ROOT",
                "AI_BRIDGE_PATH",
                "RELATION_DB",
                "RELATION_JSON",
                "CURSOR_ROOT",
                "LOCK_PATH",
                "SCAN_ROOTS",
                "ROOT_LETTERS",
                "AI_STREAMS",
            )
        }
        atlas.ATLAS_ROOT = self.root / "atlas"
        atlas.HISTORY_PATH = self.history
        atlas.PROTOCOL_PATH = self.protocol
        atlas.STATUS_PATH = atlas.ATLAS_ROOT / "ATLAS_STATUS.json"
        atlas.PATH_DB = atlas.ATLAS_ROOT / "PFADINDEX.sqlite"
        atlas.CONCEPT_DB = atlas.ATLAS_ROOT / "BEGRIFFSINDEX.sqlite"
        atlas.CHANGE_LOG = atlas.ATLAS_ROOT / "AENDERUNGSSTROM.jsonl"
        atlas.CONSENSUS_LOG = atlas.ATLAS_ROOT / "KONSENSREGISTER.jsonl"
        atlas.CONFLICT_LOG = atlas.ATLAS_ROOT / "KONFLIKTREGISTER.jsonl"
        atlas.IDEA_LOG = atlas.ATLAS_ROOT / "EINGEBUNGSPROVENIENZ.jsonl"
        atlas.PROJECT_REVISION_PATH = atlas.ATLAS_ROOT / "PROJEKTREVISIONEN.json"
        atlas.CLAIM_REGISTER_PATH = atlas.ATLAS_ROOT / "CLAIMREGISTER.json"
        atlas.VALIDATION_REGISTER_PATH = atlas.ATLAS_ROOT / "VALIDIERUNGSREGISTER.json"
        atlas.HANDOFF_REGISTER_PATH = atlas.ATLAS_ROOT / "UEBERGABEREGISTER.json"
        atlas.HANDOFF_ROOT = atlas.ATLAS_ROOT / "uebergaben"
        atlas.AI_BRIDGE_PATH = atlas.ATLAS_ROOT / "AI_STROM_BRUECKEN.json"
        atlas.RELATION_DB = atlas.ATLAS_ROOT / "BEZIEHUNGSREGISTER.sqlite"
        atlas.RELATION_JSON = atlas.ATLAS_ROOT / "BEZIEHUNGSREGISTER.json"
        atlas.CURSOR_ROOT = atlas.ATLAS_ROOT / "session_cursors"
        atlas.LOCK_PATH = atlas.ATLAS_ROOT / ".atlas.lock"
        atlas.SCAN_ROOTS = ({"name": "test", "path": str(self.source), "kind": "test"},)
        self.root_letter = self.root / "grok.md"
        self.root_letter.write_text("du bist GLM, frisch in der Session", encoding="utf-8")
        atlas.ROOT_LETTERS = (
            {
                "path": str(self.root_letter),
                "filename_label": "grok",
                "declared_author": "test",
                "declared_targets": ["glm"],
                "excluded_targets": [],
                "identity_status": "filename_content_identity_mismatch",
            },
        )
        atlas.AI_STREAMS = ()

    def tearDown(self) -> None:
        for name, value in self.saved.items():
            setattr(atlas, name, value)
        self.tempdir.cleanup()

    def append_history(self, **values) -> None:
        event = {
            "event_id": values.get("event_id", f"e-{self.history.stat().st_size if self.history.exists() else 0}"),
            "event_hash": values.get("event_hash", "hash"),
            "timestamp_utc": values.get("timestamp_utc", "2026-07-26T18:00:00+00:00"),
            "session_id": values.get("session_id", "s1"),
            "actor": values.get("actor", "GPT"),
            "action": values.get("action", "session.begin"),
            "status": values.get("status", "success"),
            "target": values.get("target"),
            "details": values.get("details", {}),
        }
        with self.history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

    def test_full_refresh_builds_indexes_and_map(self) -> None:
        self.append_history(session_id="s1", action="session.begin")
        result = atlas.refresh_atlas(mode="full", reason="test", session_id="s1", max_paths=1000, max_text_documents=100)
        self.assertTrue(result["ok"])
        self.assertTrue(atlas.PATH_DB.exists())
        self.assertTrue(atlas.CONCEPT_DB.exists())
        self.assertTrue((atlas.ATLAS_ROOT / "GESAMTKARTE.md").exists())
        self.assertTrue((atlas.ATLAS_ROOT / "GROESSENWAHRHEIT.json").exists())
        map_text = (atlas.ATLAS_ROOT / "GESAMTKARTE.md").read_text(encoding="utf-8")
        self.assertIn("nicht Atlasgröße", map_text)
        self.assertIn("Kuratierter manueller Eingang", map_text)
        self.assertEqual(result["status"]["scan"]["byte_count_semantics"], "source_landscape_logical_bytes_referenced_not_copied")
        self.assertIn("atlas_workspace_logical_bytes_excluding_self_reports", result["status"]["sizes"])
        found = atlas.find(query="START_HIER", limit=10)
        self.assertTrue(found["path_matches"])
        projects = atlas.map_view(section="projects")["data"]
        self.assertTrue(any(row["path"] == str(self.source) for row in projects))
        letters = atlas.map_view(section="root_letters")["data"]
        self.assertEqual(letters[0]["path"], str(self.root_letter))
        self.assertEqual(letters[0]["identity_status"], "filename_content_identity_mismatch")
        letter_hit = atlas.where_is(name_or_path="grok.md")
        self.assertTrue(letter_hit["exact_matches"])

    def test_pulse_returns_only_foreign_delta_and_advances_cursor(self) -> None:
        self.append_history(session_id="current", action="session.begin", event_id="a")
        self.append_history(session_id="foreign", action="vps.write_file", target="/tmp/x", event_id="b")
        first = atlas.pulse(session_id="current", consume=True)
        self.assertTrue(first["changed"])
        self.assertEqual(first["foreign_sessions"][0]["session_id"], "foreign")
        second = atlas.pulse(session_id="current", consume=True)
        self.assertFalse(second["changed"])

    def test_parallel_pulses_do_not_deliver_same_delta_twice(self) -> None:
        self.append_history(session_id="current", action="session.begin", event_id="a")
        self.append_history(session_id="foreign", action="vps.write_file", target="/tmp/x", event_id="b")
        barrier = threading.Barrier(3)
        results = []
        failures = []

        def run() -> None:
            try:
                barrier.wait(2)
                results.append(atlas.pulse(session_id="current", consume=True))
            except BaseException as exc:
                failures.append(exc)

        threads = [threading.Thread(target=run, daemon=True) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait(2)
        for thread in threads:
            thread.join(3)
        self.assertFalse(failures, failures)
        self.assertEqual(len(results), 2)
        self.assertEqual(sum(1 for result in results if result["changed"]), 1)

    def test_light_refresh_does_not_launder_dirty_path_state(self) -> None:
        self.append_history(session_id="s1", action="session.begin")
        atlas.refresh_atlas(
            mode="full", reason="base", session_id="s1", max_paths=1000, max_text_documents=100
        )
        status = json.loads(atlas.STATUS_PATH.read_text(encoding="utf-8"))
        status["dirty"] = True
        status["full_refresh_recommended"] = True
        atlas._atomic_write_json(atlas.STATUS_PATH, status)
        light = atlas.refresh_atlas(mode="light", reason="light", session_id="s1")
        self.assertTrue(light["status"]["dirty"])
        self.assertTrue(light["status"]["full_refresh_recommended"])
        self.assertEqual(light["status"]["datenstand"], "STALE_METADATA_PROVISIONAL")
        full = atlas.refresh_atlas(
            mode="full", reason="healed", session_id="s1", max_paths=1000, max_text_documents=100
        )
        self.assertFalse(full["status"]["dirty"])
        self.assertFalse(full["status"]["full_refresh_recommended"])
        self.assertEqual(full["status"]["datenstand"], "LIVE_VALIDATED_PROVISIONAL")

    def test_nested_explicit_root_is_visible_without_double_counting(self) -> None:
        nested = self.source / "nested"
        nested.mkdir()
        (nested / "a.md").write_text("A", encoding="utf-8")
        (nested / "b.md").write_text("B", encoding="utf-8")
        atlas.SCAN_ROOTS = (
            {"name": "parent", "path": str(self.source), "kind": "test"},
            {"name": "nested", "path": str(nested), "kind": "ai_stream_home"},
        )
        result = atlas.refresh_atlas(
            mode="full", reason="overlap-test", session_id="s1", max_paths=1000, max_text_documents=100
        )
        scan = result["status"]["scan"]
        nested_row = next(row for row in scan["roots"] if row["name"] == "nested")
        self.assertEqual(nested_row["coverage_class"], "covered_by_parent_root")
        self.assertEqual(nested_row["covered_by_root_name"], "parent")
        import sqlite3
        paths = sqlite3.connect(atlas.PATH_DB)
        concepts = sqlite3.connect(atlas.CONCEPT_DB)
        try:
            unique_paths = paths.execute("SELECT count(*) FROM paths").fetchone()[0]
            raw_documents = concepts.execute("SELECT count(*) FROM documents").fetchone()[0]
        finally:
            paths.close(); concepts.close()
        self.assertEqual(scan["path_count"], unique_paths)
        self.assertEqual(scan["text_document_count"], raw_documents)

    def test_federated_root_counts_all_but_indexes_structure(self) -> None:
        large = self.root / "large"
        large.mkdir()
        for index in range(20):
            directory = large / f"d{index}"
            directory.mkdir()
            for file_index in range(10):
                (directory / f"f{file_index}.txt").write_text("content", encoding="utf-8")
        atlas.SCAN_ROOTS = (
            {"name": "test", "path": str(self.source), "kind": "test"},
            {
                "name": "large",
                "path": str(large),
                "kind": "large",
                "scan_mode": "federated",
                "federated_search_tool": "large.search",
                "federated_tree_tool": "large.tree",
            },
        )
        result = atlas.refresh_atlas(
            mode="full",
            reason="federated-test",
            session_id="s1",
            max_paths=1000,
            max_text_documents=100,
        )
        scan = result["status"]["scan"]
        root = next(row for row in scan["roots"] if row["name"] == "large")
        self.assertEqual(root["observed_path_count"], 220)
        self.assertLess(root["indexed_path_count"], root["observed_path_count"])
        self.assertEqual(root["coverage_class"], "federated_complete")
        self.assertEqual(root["scope_role"], "federated_external")
        self.assertEqual(root["federated_search_tool"], "large.search")
        self.assertEqual(scan["federated_source_bytes"], root["byte_count"])
        self.assertGreater(scan["direct_source_bytes"], 0)
        self.assertEqual(
            scan["source_landscape_bytes"],
            scan["direct_source_bytes"] + scan["federated_source_bytes"],
        )
        self.assertEqual(scan["byte_count"], scan["source_landscape_bytes"])

    def test_curated_manual_intake_is_fully_indexed_and_searchable(self) -> None:
        intake = self.root / "gesamtatlas_eingang"
        intake.mkdir()
        (intake / "START_HIER.md").write_text("# Eingang\n\nEinzigartige Kuratierungsspur Omega.", encoding="utf-8")
        (intake / "IDEEN").mkdir()
        (intake / "IDEEN" / "idee.md").write_text("Omega-Handeingabe für den Gesamtatlas.", encoding="utf-8")
        atlas.SCAN_ROOTS = (
            {"name": "test", "path": str(self.source), "kind": "test"},
            {
                "name": "gesamtatlas-eingang",
                "path": str(intake),
                "kind": "curated_manual_intake",
                "scope_role": "curated_manual",
            },
        )
        result = atlas.refresh_atlas(
            mode="full", reason="manual-intake-test", session_id="s1", max_paths=1000, max_text_documents=100
        )
        scan = result["status"]["scan"]
        row = next(item for item in scan["roots"] if item["name"] == "gesamtatlas-eingang")
        self.assertEqual(row["scope_role"], "curated_manual")
        self.assertEqual(row["coverage_class"], "full_metadata")
        self.assertEqual(row["indexed_path_count"], row["observed_path_count"])
        self.assertEqual(scan["curated_intake_bytes"], row["byte_count"])
        found = atlas.find(query="Omega-Handeingabe", include_content=True)
        self.assertTrue(any(item["path"].endswith("idee.md") for item in found["content_matches"]))

    def test_handoff_sort_accepts_mixed_legacy_timestamps(self) -> None:
        self.append_history(
            session_id="foreign", action="session.begin", event_id="mixed-1", timestamp_utc="2026-07-26T18:00:00+00:00"
        )
        with self.history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "event_id": "mixed-2",
                "event_hash": "hash-2",
                "timestamp_unix_ns": 1785088861000000000,
                "timestamp_utc": "2026-07-26T18:01:01+00:00",
                "session_id": "foreign",
                "actor": "GPT",
                "action": "vps.write_file",
                "status": "success",
                "target": str(self.source / "mixed.md"),
                "details": {},
            }) + "\n")
        self.append_history(
            session_id="foreign", action="session.end", event_id="mixed-3", timestamp_utc="2026-07-26T18:02:00+00:00", details={"summary": "mixed done"}
        )
        result = atlas.refresh_atlas(
            mode="full", reason="mixed-history", session_id="owner", max_paths=1000, max_text_documents=100
        )
        self.assertTrue(result["ok"])
        handoff = atlas.handoffs(session_id="foreign")
        self.assertEqual(handoff["count"], 1)
        self.assertEqual(handoff["handoffs"][0]["end_event_id"], "mixed-3")

    def test_relational_layer_builds_revisions_handoff_and_project_edges(self) -> None:
        changed = self.source / "changed.md"
        changed.write_text("changed", encoding="utf-8")
        self.append_history(session_id="foreign", action="session.begin", event_id="h1")
        self.append_history(
            session_id="foreign",
            action="vps.write_file",
            target=str(changed),
            event_id="h2",
        )
        self.append_history(
            session_id="foreign",
            action="session.end",
            event_id="h3",
            details={"summary": "Projektänderung abgeschlossen und geprüft."},
        )
        result = atlas.refresh_atlas(
            mode="full", reason="relations-test", session_id="owner", max_paths=1000, max_text_documents=100
        )
        self.assertTrue(result["ok"])
        self.assertTrue(atlas.RELATION_DB.exists())
        self.assertTrue(atlas.PROJECT_REVISION_PATH.exists())
        self.assertTrue(atlas.HANDOFF_REGISTER_PATH.exists())
        projects = atlas.map_view(section="projects")["data"]
        project = next(row for row in projects if row["path"] == str(self.source))
        self.assertGreaterEqual(project["project_revision"], 1)
        self.assertTrue(project["related_sessions"])
        handoff = atlas.handoffs(session_id="foreign")
        self.assertEqual(handoff["count"], 1)
        self.assertEqual(handoff["handoffs"][0]["datenstand"], "DERIVED_FROM_ACTION_HISTORY")
        relations = atlas.relationships(query=project["project_id"], node_type="project")
        self.assertTrue(relations["ok"])
        self.assertTrue(any(edge["relation"] == "TOUCHED_PROJECT" for edge in relations["edges"]))

    def test_observed_mutation_increments_matching_project_revision(self) -> None:
        atlas.refresh_atlas(
            mode="full", reason="base", session_id="owner", max_paths=1000, max_text_documents=100
        )
        project = next(row for row in atlas.map_view(section="projects")["data"] if row["path"] == str(self.source))
        before = project["project_revision"]
        event = {
            "event_id": "mutation-event",
            "event_hash": "mutation-hash",
            "timestamp_utc": "2026-07-26T20:00:00+00:00",
            "session_id": "foreign",
            "action": "vps.write_file",
            "status": "success",
        }
        observed = atlas.observe_tool_event(
            tool_name="vps.write_file",
            session_id="foreign",
            event=event,
            result={"ok": True},
            target=str(self.source / "new.md"),
            context_paths=[str(self.source)],
        )
        self.assertEqual(observed["project_id"], project["project_id"])
        self.assertEqual(observed["project_revision"], before + 1)
        state = json.loads(atlas.PROJECT_REVISION_PATH.read_text(encoding="utf-8"))["projects"][project["project_id"]]
        self.assertEqual(state["revision"], before + 1)
        self.assertIn("mutation-event", state["pending_event_ids"])

    def test_pulse_lease_tracks_project_revisions_and_handoffs(self) -> None:
        self.append_history(session_id="foreign", action="session.begin", event_id="l1")
        self.append_history(
            session_id="foreign", action="vps.write_file", target=str(self.source / "x.md"), event_id="l2"
        )
        self.append_history(
            session_id="foreign", action="session.end", event_id="l3", details={"summary": "done"}
        )
        atlas.refresh_atlas(
            mode="full", reason="lease", session_id="owner", max_paths=1000, max_text_documents=100
        )
        first = atlas.pulse(
            session_id="current", current_project=str(self.source), level="project", consume=True
        )
        self.assertTrue(first["new_handoffs"])
        self.assertTrue(first["project_revision_deltas"])
        self.assertNotIn("source_event_ids", first["new_handoffs"][0])
        self.assertNotIn("source_event_hashes", first["new_handoffs"][0])
        self.assertIn("markdown_path", first["new_handoffs"][0])
        cursor = json.loads(atlas._cursor_path("current").read_text(encoding="utf-8"))
        self.assertEqual(cursor["schema_version"], "2.0")
        self.assertIn("foreign", cursor["known_completed_sessions"])
        self.assertTrue(cursor["project_revisions_seen"])
        second = atlas.pulse(
            session_id="current", current_project=str(self.source), level="project", consume=True
        )
        self.assertFalse(second["new_handoffs"])
        self.assertFalse(second["project_revision_deltas"])

    def test_validation_register_separates_reports_from_raw_evidence(self) -> None:
        validation = self.source / "validation" / "run"
        validation.mkdir(parents=True)
        (validation / "RESULT.json").write_text('{"ok": true}', encoding="utf-8")
        (validation / "screen.png").write_bytes(b"not-a-real-png-but-a-path-artifact")
        atlas.refresh_atlas(
            mode="full", reason="validation-layers", session_id="owner", max_paths=1000, max_text_documents=100
        )
        project = next(
            row for row in atlas.map_view(section="projects")["data"]
            if row["path"] == str(self.source)
        )
        self.assertEqual(len(project["validation_artifacts"]), 2)
        self.assertEqual(len(project["validation_reports"]), 1)
        self.assertEqual(project["validation_reports"][0]["label"], "RESULT.json")
        register = atlas.map_view(section="validations")["data"]["validations"]
        classes = {row["artifact_class"] for row in register}
        self.assertEqual(classes, {"machine_result", "visual_evidence"})

    def test_claudeweb_stream_keeps_nested_entries_and_separate_identity(self) -> None:
        home = self.source / "_claudeweb"
        sessions = home / "verlauf"
        protocol = home / "protokoll"
        sessions.mkdir(parents=True)
        protocol.mkdir(parents=True)
        zuhause = home / "ZUHAUSE.md"
        manifest = home / "MANIFEST.json"
        protocol_file = protocol / "claudeweb_zuhause_v1.json"
        zuhause.write_text("Claude Web ist nicht Claude Code und nicht ChatGPT.\n", encoding="utf-8")
        manifest.write_text('{"sections":{"home":"ZUHAUSE.md"}}', encoding="utf-8")
        protocol_file.write_text('{"identity_boundary":"separate browser chat"}', encoding="utf-8")
        (sessions / "2026-07-29.md").write_text(f"Arbeit am Projektpfad {self.source}\n", encoding="utf-8")
        boundary = "Eigener Browserchatstrom; keine gemeinsame Erinnerung."
        atlas.AI_STREAMS = (
            {
                "id": "claudeweb",
                "home": str(home),
                "workspace": str(home),
                "sessions": str(sessions),
                "root_letter_paths": [],
                "entry_paths": [str(zuhause), str(manifest), str(protocol_file)],
                "identity_boundary": boundary,
            },
        )
        result = atlas.refresh_atlas(
            mode="full", reason="claudeweb-stream", session_id="owner", max_paths=2000, max_text_documents=200
        )
        self.assertTrue(result["ok"])
        streams = json.loads((atlas.ATLAS_ROOT / "AI_STROEME.json").read_text(encoding="utf-8"))
        self.assertEqual([row["id"] for row in streams], ["claudeweb"])
        stream = streams[0]
        self.assertEqual(stream["identity_boundary"], boundary)
        self.assertEqual(stream["session_source_stats"]["classification"], "directory_session_store")
        self.assertEqual(stream["session_source_stats"]["file_count"], 1)
        self.assertEqual(set(stream["entry_files"]), {str(zuhause), str(manifest), str(protocol_file)})
        bridge = json.loads(atlas.AI_BRIDGE_PATH.read_text(encoding="utf-8"))["streams"]["claudeweb"]
        self.assertEqual(bridge["stream_id"], "claudeweb")
        self.assertEqual(bridge["session_source"], str(sessions))
        self.assertEqual(bridge["session_source_stats"]["file_count"], 1)
        self.assertEqual(bridge["indexed_session_document_count"], 1)
        self.assertNotEqual(bridge["fingerprint"], "")

    def test_project_classes_keep_structural_views_out_of_ai_bridges(self) -> None:
        view = self.source / "Verweise"
        view.mkdir(exist_ok=True)
        (view / "MANIFEST.json").write_text("{}", encoding="utf-8")
        sessions = self.source / "agent_sessions"
        sessions.mkdir()
        (sessions / "session.md").write_text(
            f"Arbeit an {view} und {self.source}", encoding="utf-8"
        )
        atlas.AI_STREAMS = (
            {
                "id": "claude",
                "home": str(self.source),
                "workspace": str(self.source),
                "sessions": str(sessions),
                "root_letter_paths": [],
            },
        )
        atlas.refresh_atlas(
            mode="full", reason="classes", session_id="owner", max_paths=1000, max_text_documents=100
        )
        projects = atlas.map_view(section="projects")["data"]
        structural = next(row for row in projects if row["path"] == str(view))
        canonical = next(row for row in projects if row["path"] == str(self.source))
        self.assertEqual(structural["project_class"], "structural_view")
        self.assertFalse(structural["bridge_eligible"])
        self.assertEqual(structural["canonical_parent_project_id"], canonical["project_id"])
        bridge = json.loads(atlas.AI_BRIDGE_PATH.read_text(encoding="utf-8"))["streams"]["claude"]
        names = {row["name"] for row in bridge["related_projects"]}
        self.assertIn(self.source.name, names)
        self.assertNotIn("Verweise", names)

    def test_ai_stream_bridge_uses_exact_document_mentions(self) -> None:
        sessions = self.source / "agent_sessions"
        sessions.mkdir()
        (sessions / "session.md").write_text(
            f"Arbeit am Projektpfad {self.source}", encoding="utf-8"
        )
        atlas.AI_STREAMS = (
            {
                "id": "claude",
                "home": str(self.source),
                "workspace": str(self.source),
                "sessions": str(sessions),
                "root_letter_paths": [],
            },
        )
        atlas.refresh_atlas(
            mode="full", reason="bridge", session_id="owner", max_paths=1000, max_text_documents=100
        )
        bridge = json.loads(atlas.AI_BRIDGE_PATH.read_text(encoding="utf-8"))["streams"]["claude"]
        self.assertEqual(bridge["indexed_session_document_count"], 1)
        self.assertTrue(bridge["related_projects"])
        self.assertEqual(bridge["related_projects"][0]["datenstand"], "FULLTEXT_EXACT_MENTION_DERIVED")

    def test_idea_marker_marks_convergence_without_claiming_copy(self) -> None:
        atlas.record_idea(
            text="Wir bauen einen revisionsfähigen Gesamtatlas für Sitzungen.",
            session_id="alpha",
            prior_awareness="none",
        )
        result = atlas.record_idea(
            text="Ein revisionsfähiger Atlas soll alle Sessions verbinden.",
            session_id="beta",
            prior_awareness="none",
        )
        self.assertIn(result["record"]["classification"], {"KONVERGENT_MIT_AUFFINDBARER_VORSPUR", "OHNE_GEFUNDENE_VORSPUR"})
        self.assertIn("EINGEBUNGSPROVENIENZ", result["display_marker"])

    def test_broken_text_symlink_is_indexed_as_path_not_document(self) -> None:
        broken = self.source / "broken.md"
        broken.symlink_to(self.source / "missing-target.md")
        result = atlas.refresh_atlas(
            mode="full", reason="broken-link-test", session_id="s1", max_paths=1000, max_text_documents=100
        )
        scan = result["status"]["scan"]
        self.assertEqual(scan["broken_text_symlink_count"], 1)
        self.assertEqual(scan["text_read_error_count"], 0)
        found = atlas.where_is(name_or_path="broken.md")
        self.assertTrue(found["exact_matches"])
        self.assertEqual(found["exact_matches"][0]["excluded_reason"], "broken_symlink_target_missing")
        self.assertIn("broken_symlink", found["exact_matches"][0]["markers"])
        concept = atlas.find(query="broken.md", include_content=True)
        self.assertFalse(any(row["path"].endswith("broken.md") for row in concept["content_matches"]))

    def test_empty_text_paths_are_counted_but_not_claimed_as_documents(self) -> None:
        (self.source / "empty.md").write_bytes(b"")
        result = atlas.refresh_atlas(
            mode="full", reason="empty-test", session_id="s1", max_paths=1000, max_text_documents=100
        )
        scan = result["status"]["scan"]
        self.assertEqual(scan["empty_text_path_count"], 1)
        self.assertEqual(scan["text_read_error_count"], 0)
        self.assertFalse(scan["text_document_limit_reached"])
        found = atlas.where_is(name_or_path="empty.md")
        self.assertTrue(found["exact_matches"])
        concept = atlas.find(query="empty.md", include_content=True)
        self.assertFalse(any(row["path"].endswith("empty.md") for row in concept["content_matches"]))

    def test_cross_session_authorization_class_can_be_explicitly_bound(self) -> None:
        result = atlas.record_idea(
            text="Gesamtatlas und Eingebungsprovenienz bauen.",
            session_id="owner",
            prior_awareness="unknown",
            classification_override="CROSS_SESSION_EINGEBUNG_MIT_NACHGELAGERTER_LOKALER_FREIGABE",
            explicit_source_refs=["inbox.json", "session:foreign"],
        )
        self.assertEqual(
            result["record"]["classification"],
            "CROSS_SESSION_EINGEBUNG_MIT_NACHGELAGERTER_LOKALER_FREIGABE",
        )
        self.assertIn("CROSS_SESSION", result["display_marker"])
        self.assertIn("ExpliziteQuelle=inbox.json", result["display_marker"])

    def test_consensus_and_conflict_stay_separate(self) -> None:
        atlas.record_consensus(
            statement="Daniel hat den Atlasbau gesetzt.",
            consensus_class="DANIEL_EXPLIZIT_GESETZT",
            session_id="s1",
        )
        atlas.record_conflict(
            statement_a="A gilt.",
            statement_b="B gilt.",
            session_id="s2",
        )
        self.assertEqual(atlas.list_consensus()["count"], 1)
        self.assertEqual(atlas.list_conflicts()["count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
