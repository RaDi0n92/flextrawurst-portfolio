from pathlib import Path
import json

import pytest

from portfolio_archaeology_harness import (
    DEFAULT_PROJECT_ROOT,
    PortfolioHarnessError,
    build_context,
    check,
)


def test_real_project_context_loads():
    result = build_context()
    assert result["active"] is True
    assert result["project_root"] == str(DEFAULT_PROJECT_ROOT.resolve())
    assert result["mode"] == "chronological_archaeology"
    assert "hard_constraints" in result
    assert "next_action" in result
    assert "navigation_harness" in result
    assert result["navigation_harness"]["mode"] == "warn_only"
    assert result["navigation_harness"]["promotion_status"] == "promoted"
    assert result["navigation_harness"]["promoted_root_available"] is True
    assert result["navigation_harness"]["start_exists"] is True
    assert result["navigation_harness"]["healthy"] is True
    assert result["navigation_harness"]["broken_links"] == []
    assert result["navigation_harness"]["lesen_md_optional"] is True
    assert result["navigation_harness"]["derived_navigation_policy"] == "reference_only_no_pack_copies"


def test_real_project_hashes_are_synchronized():
    result = check()
    assert result["ok"] is True
    assert result["drift"]["rules_in_sync"] is True
    assert not any("hash-synchron" in warning for warning in result["warnings"])


def test_navigation_harness_is_warn_only():
    result = check()
    nav = result["navigation_harness"]
    assert nav["enabled"] is True
    assert nav["mode"] == "warn_only"
    assert nav["goal"] == "natural_research_landscape_with_internal_raw_truth"
    assert nav["promotion_status"] == "promoted"
    assert nav["healthy"] is True
    assert nav["legacy_archived"] is True
    assert nav["canonical_truth_available"] is True
    minimum_structural_files = len(nav["system_bodies"]) + len(nav["context_bodies"]) + 1
    assert nav["visible_file_count"] >= minimum_structural_files
    assert nav["missing_system_bodies"] == []
    assert nav["missing_context_bodies"] == []
    assert nav["missing_lesen_files"] == []
    assert nav["broken_links"] == []
    assert result["ok"] is True


def test_full_rules_are_opt_in():
    compact = build_context(include_full_rules=False)
    full = build_context(include_full_rules=True)
    assert "constitution_de" not in compact
    assert "constitution_de" in full
    assert "constitution_en" in full
    assert isinstance(full["current_state"], dict)


def test_harness_refuses_unrelated_root(tmp_path):
    with pytest.raises(PortfolioHarnessError):
        build_context(project_root=str(tmp_path))


def test_harness_is_read_only_for_project_files():
    watched = [
        DEFAULT_PROJECT_ROOT / "00_ARCHAEOLOGIE_ARBEITSVERFASSUNG_DE.md",
        DEFAULT_PROJECT_ROOT / "00_ARCHAEOLOGY_WORK_CONSTITUTION_EN.md",
        DEFAULT_PROJECT_ROOT / "00_CURRENT_RESEARCH_STATE.json",
        DEFAULT_PROJECT_ROOT / "00_SOURCE_CLASS_LEDGER.json",
        DEFAULT_PROJECT_ROOT / "00_CASE_STUDY_FRAMEWORK.json",
    ]
    before = {str(p): (p.stat().st_mtime_ns, p.read_bytes()) for p in watched}
    build_context(include_full_rules=True)
    after = {str(p): (p.stat().st_mtime_ns, p.read_bytes()) for p in watched}
    assert before == after


def test_profile_development_lens_is_exposed():
    result = build_context()
    lens = result["profile_development_lens"]
    assert lens["enabled"] is True
    assert lens["mode"] == "warn_only"
    assert lens["claim_checks"]["overclaim_warning"] is True
    assert lens["claim_checks"]["stale_or_provenance_warning"] is True
    assert lens["physical_policy"]["do_not_create_per_system_meta_files"] is True


def test_portfolio_arbeitsrahmen_exposes_file_budget_and_case_study_contract():
    result = build_context()
    config = result["harness_config"]
    assert config["preferred_term_de"] == "Portfolio-Arbeitsrahmen"
    assert config["document_budget"]["hard_max"] == 444
    assert config["document_budget"]["working_ceiling"] == 444
    assert config["document_budget"]["expected_range"] == [222, 444]
    assert config["document_budget"]["quota"] is False
    assert config["document_budget"]["may_exceed_when_unique_reader_value_justifies_it"] is False
    assert config["evidence_artifact_policy"]["count_cap"] is None
    assert config["publication_model"]["principle"] == "one_evidence_base_many_traceable_views"
    assert "stages_not_export_layers" in config["publication_model"]
    assert "was_nicht_funktionierte_oder_begrenzt_war" in config["case_study_contract"]["preferred_sequence"]
    assert "invent_causality" in config["case_study_contract"]["must_not"]
    inventory = result["artifact_inventory"]
    assert inventory["markdown_files"] >= inventory["visible_portfolio_markdown_files"]
    assert inventory["preferred_primary_evidence_formats"][".py"] > 0
    assert inventory["preferred_primary_evidence_formats"][".json"] > 0

def test_source_class_ledger_is_exposed_and_warn_only():
    result = build_context()
    ledger = result["source_class_ledger"]
    assert ledger["enabled"] is True
    assert ledger["mode"] == "warn_only"
    assert ledger["available"] is True
    assert ledger["updated_date"] == "2026-10-02"
    assert ledger["historical_metrics_snapshot"]["unrepresented_live_markdown_at_snapshot"]["files"] >= 1
    assert "keine Live-Inventur" in ledger["metrics_note"]
    assert len(ledger["intentional_or_dynamic_groups"]) >= 1
    assert ledger["export_compaction"]["markdown_working_ceiling"] == 444


def test_case_study_framework_is_exposed():
    result = build_context()
    cases = result["case_study_framework"]
    assert cases["enabled"] is True
    assert cases["mode"] == "warn_only"
    assert cases["available"] is True
    assert cases["status"] == "editorial_v1_written"
    assert len(cases["case_studies"]) == 7
    assert "Was nicht funktionierte" in cases["required_sequence"]
    assert all(case.get("evidence_anchors") for case in cases["case_studies"])
