from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_PROJECT_ROOT = Path("/root/werkraum/in_gpt/job-portfolio-try")
CONSTITUTION_DE = "00_ARCHAEOLOGIE_ARBEITSVERFASSUNG_DE.md"
CONSTITUTION_EN = "00_ARCHAEOLOGY_WORK_CONSTITUTION_EN.md"
CURRENT_STATE = "00_CURRENT_RESEARCH_STATE.json"
HARNESS_CONFIG = "00_PORTFOLIO_ARCHAEOLOGY_HARNESS.json"
SOURCE_CLASS_LEDGER = "00_SOURCE_CLASS_LEDGER.json"
CASE_STUDY_FRAMEWORK = "00_CASE_STUDY_FRAMEWORK.json"

HARD_CONSTRAINTS = [
    "Primärquellen außerhalb des Archiv-/Stagingbereichs nicht verändern.",
    "Große Quellen nur verlustfrei splitten; Rekonstruktion muss byteidentisch sein.",
    "Datierungen nicht erfinden; Datumsart bei Unsicherheit qualifizieren.",
    "Vision, Plan, Dokumentation, Code, Test, Laufzustand und Review getrennt halten.",
    "Nach einem Forschungsblock den Research State aktualisieren.",
]

SOFT_GUIDANCE = [
    "Chronologisch graben; thematische Forschungswege bleiben abgeleitete Browsing-Sichten.",
    "Die nächste Quelle aus dem bisher Gelesenen ableiten.",
    "Lesekomplexität wichtiger nehmen als Dateizahl.",
    "Sichtbare Packs sollen wie natürliche Uploadordner wirken: Quellen zuerst, Metaebene minimal.",
    "LESEN.md ist optional und pro Pack höchstens einmal erlaubt; keine neuen FOR_HUMANS/FOR_AGENTS/LESEN_DE/READ_EN anlegen.",
    "Eine einzige physische Quellenwahrheit behalten: Chronologie kanonisch, ENTDECKEN/NACHSCHLAGEN nur Navigation ohne neue Packkopien.",
    "Ordnernamen oben dürfen Entwicklung und Neugier tragen; Dateinamen unten bleiben präzise und sachlich.",
    "Dateinamen sollen Inhalt und Funktion tragen; Provenienzmechanik bleibt soweit möglich intern.",
    "LESEN.md nennt nur Kern, 2–4 Einstiegsdateien, Dateizweck und nötige Interpretationsgrenzen.",
    "Forschungslandschaften mit wenigen verständlichen Ober-/Unterordnern statt flacher Packwand bevorzugen.",
    "Navigation zeigt Wege, nicht Schlussfolgerungen.",
    "Neben Artefakten auch Entwicklung des eigenen Verständnisses sichtbar halten: Was wusste Daniel damals, was noch nicht, was änderte sich danach?",
    "Heutige technische Begriffe oder Fähigkeiten nicht rückwirkend in frühe Phasen hineinprojizieren.",
    "Portfolio-Claims gegen Primärbeleg, Eigenanteil, Gegenbeleg/Grenze und Aktualität halten; UNKNOWN bleibt erlaubt.",
    "Starke Entwicklungslinien lieber als abgeleitete Sicht zeigen als neue physische Kopien oder Pflichtdateien zu erzeugen.",
    "Markdown-Dateien nicht künstlich verknappen: getrennte Systemdokus, Spiegel, Ideen, Konzepte, Planungen, Reviews, Audits und Lösungsdokus dürfen getrennt bleiben, wenn ein Leser sie sinnvoll einzeln auswählen würde.",
    "Code, JSON, Diffs, Tests, SQL, Godot-Szenen, Logs und Konfigurationen nach Beweisdichte pro Kontext bewerten, nicht pauschal nach Dateizahl.",
    "Für Implementierungsbehauptungen kompakte Primärartefakte bevorzugen; Prosa dient vor allem Kontext, Anforderungen, Entscheidungen und Chronologie.",
]


class PortfolioHarnessError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_project_root(raw_root: str | None = None) -> Path:
    root = Path(raw_root).expanduser() if raw_root else DEFAULT_PROJECT_ROOT
    resolved = root.resolve()
    # Opt-in harness: only the agreed portfolio archaeology root or descendants.
    allowed = DEFAULT_PROJECT_ROOT.resolve()
    if resolved != allowed and allowed not in resolved.parents:
        raise PortfolioHarnessError(
            f"Arbeitsrahmen ist nur für {allowed} und Unterpfade aktiv, nicht für {resolved}"
        )
    if not resolved.exists() or not resolved.is_dir():
        raise PortfolioHarnessError(f"Projektwurzel fehlt: {resolved}")
    return resolved


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        raise PortfolioHarnessError(f"Pflichtdatei fehlt: {path}")
    return path.read_text(encoding="utf-8")


def _read_state(path: Path) -> dict[str, Any]:
    text = _read_text(path)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PortfolioHarnessError(f"Research State ist kein gültiges JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PortfolioHarnessError("Research State muss ein JSON-Objekt sein")
    return data


def _artifact_inventory(root: Path) -> dict[str, Any]:
    files = [path for path in root.rglob("*") if path.is_file()]
    suffix_counts = Counter((path.suffix.lower() or "<none>") for path in files)
    preferred = [".py", ".json", ".diff", ".sql", ".gd", ".tscn", ".godot", ".service", ".sh", ".log"]
    portfolio_root = root / "PORTFOLIO"
    return {
        "total_files": len(files),
        "markdown_files": suffix_counts.get(".md", 0),
        "visible_portfolio_markdown_files": len(list(portfolio_root.rglob("*.md"))) if portfolio_root.is_dir() else 0,
        "preferred_primary_evidence_formats": {
            suffix: suffix_counts.get(suffix, 0) for suffix in preferred if suffix_counts.get(suffix, 0)
        },
        "largest_format_counts": dict(suffix_counts.most_common(12)),
        "interpretation": "Markdown-Dateien nach Eigenständigkeit, Neugierwert und Dublettenfreiheit gegen das Dokumentbudget halten; kompakte Primärartefakte nach Beweisdichte und Einzigartigkeit bewerten.",
    }


def _navigation_health(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    nav = config.get("navigation_harness") or {}
    if nav.get("enabled") is not True:
        return {"enabled": False}

    promoted_rel = str(nav.get("promoted_portfolio_root") or "")
    promotion_status = str(nav.get("promotion_status") or "")
    if promoted_rel and promotion_status == "promoted":
        promoted = root / promoted_rel
        consolidation = nav.get("consolidation_policy") or {}
        systems = list(consolidation.get("primary_system_bodies") or [])
        contexts = list(consolidation.get("remaining_context_categories") or [])

        system_root = promoted / "01_WAS_ENTSTANDEN_IST"
        context_root = promoted / "02_WIE_ES_DAZU_KAM"
        missing_systems = [name for name in systems if not (system_root / name).is_dir()]
        missing_contexts = [name for name in contexts if not (context_root / name).is_dir()]
        lesen_files = sorted(promoted.rglob("LESEN.md")) if promoted.exists() else []
        missing_lesen = []
        for name in systems:
            if not (system_root / name / "LESEN.md").is_file():
                missing_lesen.append(f"01_WAS_ENTSTANDEN_IST/{name}/LESEN.md")
        for name in contexts:
            if not (context_root / name / "LESEN.md").is_file():
                missing_lesen.append(f"02_WIE_ES_DAZU_KAM/{name}/LESEN.md")

        nav_files = []
        if (promoted / "START.md").is_file():
            nav_files.append(promoted / "START.md")
        nav_files.extend(lesen_files)
        for relative in ("02_WIE_ES_DAZU_KAM/CHRONOLOGIE.md", "03_ENTWICKLUNGSLINIEN.md"):
            candidate = promoted / relative
            if candidate.is_file():
                nav_files.append(candidate)
        broken_links = []
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for doc in nav_files:
            text = doc.read_text(encoding="utf-8", errors="replace")
            for target in link_pattern.findall(text):
                if "://" in target or target.startswith("#"):
                    continue
                if not (doc.parent / target).resolve().exists():
                    broken_links.append({
                        "document": str(doc.relative_to(promoted)),
                        "target": target,
                    })

        visible_files = len([x for x in promoted.rglob("*") if x.is_file()]) if promoted.exists() else 0
        legacy_archive = root / str(nav.get("legacy_archive_root") or "")
        canonical = root / str(nav.get("canonical_physical_truth") or "")
        healthy = (
            promoted.is_dir()
            and (promoted / "START.md").is_file()
            and not missing_systems
            and not missing_contexts
            and not missing_lesen
            and not broken_links
            and legacy_archive.is_dir()
            and canonical.is_dir()
        )
        return {
            "enabled": True,
            "mode": "warn_only",
            "goal": "natural_research_landscape_with_internal_raw_truth",
            "promotion_status": "promoted",
            "promoted_portfolio_root": str(promoted),
            "promoted_root_available": promoted.is_dir(),
            "start_exists": (promoted / "START.md").is_file(),
            "visible_file_count": visible_files,
            "system_bodies": systems,
            "context_bodies": contexts,
            "missing_system_bodies": missing_systems,
            "missing_context_bodies": missing_contexts,
            "missing_lesen_files": missing_lesen,
            "broken_links": broken_links,
            "legacy_archived": legacy_archive.is_dir(),
            "legacy_archive_root": str(legacy_archive),
            "canonical_physical_truth": str(canonical),
            "canonical_truth_available": canonical.is_dir(),
            "derived_navigation_policy": nav.get("derived_navigation_policy", "reference_only_no_pack_copies"),
            "lesen_md_optional": True,
            "migration_in_progress": False,
            "healthy": healthy,
            "advice": [
                "Im sichtbaren PORTFOLIO weiterarbeiten; Rohchronologie nur intern als Belegkörper verwenden.",
                "Neue Entwicklungsschritte nicht wieder zu eigenen Packs aufblasen.",
                "Quellen verlustfrei in den passenden System- oder Kontextkörper einfügen.",
            ],
        }

    # Fallback for an unpromoted/legacy project state.
    chronology = root / str(nav.get("chronology_root") or "03_CHRONOLOGICAL_ARCHAEOLOGY")
    preferred = str(nav.get("preferred_pack_navigation") or "LESEN.md")
    legacy_names = set(
        nav.get("legacy_pack_navigation")
        or ["FOR_HUMANS_DE.md", "FOR_HUMANS_EN.md", "FOR_AGENTS_DE.md", "FOR_AGENTS_EN.md", "LESEN_DE.md", "READ_EN.md"]
    )
    if not chronology.exists() or not chronology.is_dir():
        return {
            "enabled": True,
            "mode": "warn_only",
            "chronology_root": str(chronology),
            "available": False,
            "migration_in_progress": True,
            "advice": ["Chronologieordner fehlt; Navigationsstatus kann nicht gemessen werden."],
        }

    packs = sorted(x for x in chronology.iterdir() if x.is_dir())
    legacy_files = 0
    legacy_packs = 0
    multi_nav_packs = 0
    preferred_packs = 0
    for pack in packs:
        present = {x.name for x in pack.iterdir() if x.is_file()}
        has_preferred = preferred in present
        legacy_here = present & legacy_names
        preferred_packs += int(has_preferred)
        legacy_files += len(legacy_here)
        legacy_packs += int(bool(legacy_here))
        multi_nav_packs += int(int(has_preferred) + len(legacy_here) > 1)

    return {
        "enabled": True,
        "mode": "warn_only",
        "goal": "natural_upload_folder_with_minimal_meta",
        "chronology_root": str(chronology),
        "available": True,
        "preferred_pack_navigation": preferred,
        "total_packs": len(packs),
        "packs_with_preferred_navigation": preferred_packs,
        "legacy_navigation_files": legacy_files,
        "legacy_navigation_packs": legacy_packs,
        "packs_with_multiple_navigation_files": multi_nav_packs,
        "migration_in_progress": legacy_files > 0 or multi_nav_packs > 0,
        "lesen_md_optional": True,
        "canonical_physical_truth": nav.get("canonical_physical_truth", "chronology"),
        "derived_navigation_policy": nav.get("derived_navigation_policy", "reference_only_no_pack_copies"),
    }

def build_context(project_root: str | None = None, include_full_rules: bool = False) -> dict[str, Any]:
    root = _safe_project_root(project_root)

    config_path = root / HARNESS_CONFIG
    config = _read_state(config_path)
    if config.get("activation") != "explicit_opt_in":
        raise PortfolioHarnessError("Arbeitsrahmen-Konfig muss activation=explicit_opt_in setzen")
    if config.get("startup_hook") is not False:
        raise PortfolioHarnessError("Arbeitsrahmen-Konfig darf keinen Startup-Hook aktivieren")
    if config.get("wrap_existing_tools") is not False:
        raise PortfolioHarnessError("Arbeitsrahmen-Konfig darf bestehende Werkzeuge nicht automatisch umhüllen")
    if config.get("read_only_context") is not True:
        raise PortfolioHarnessError("Arbeitsrahmen-Konfig muss read_only_context=true setzen")

    de_path = root / str(config.get("constitution_de") or CONSTITUTION_DE)
    en_path = root / str(config.get("constitution_en") or CONSTITUTION_EN)
    state_path = root / str(config.get("current_state") or CURRENT_STATE)

    de_text = _read_text(de_path)
    en_text = _read_text(en_path)
    state = _read_state(state_path)

    ledger_config = config.get("source_class_ledger") or {}
    ledger_enabled = ledger_config.get("enabled") is True
    ledger_path = root / str(ledger_config.get("path") or SOURCE_CLASS_LEDGER)
    ledger = _read_state(ledger_path) if ledger_enabled else {}
    ledger_compact = {
        "enabled": ledger_enabled,
        "mode": ledger_config.get("mode", "warn_only"),
        "path": str(ledger_path),
        "available": ledger_path.is_file() if ledger_enabled else False,
        "updated_date": ledger.get("updated_date") if ledger_enabled else None,
        "historical_metrics_snapshot": ledger.get("historical_metrics_snapshot") if ledger_enabled else None,
        "metrics_note": ledger.get("metrics_note") if ledger_enabled else None,
        "intentional_or_dynamic_groups": ledger.get("intentional_or_dynamic_groups", []) if ledger_enabled else [],
        "export_compaction": ledger.get("export_compaction") if ledger_enabled else None,
        "rule": ledger.get("rule") if ledger_enabled else None,
    }

    case_config = config.get("case_study_framework") or {}
    case_enabled = case_config.get("enabled") is True
    case_path = root / str(case_config.get("path") or CASE_STUDY_FRAMEWORK)
    case_data = _read_state(case_path) if case_enabled else {}
    case_compact = {
        "enabled": case_enabled,
        "mode": case_config.get("mode", "warn_only"),
        "path": str(case_path),
        "available": case_path.is_file() if case_enabled else False,
        "updated_date": case_data.get("updated_date") if case_enabled else None,
        "status": case_data.get("status") if case_enabled else None,
        "required_sequence": case_data.get("required_sequence", []) if case_enabled else [],
        "rules": case_data.get("rules", []) if case_enabled else [],
        "case_studies": case_data.get("case_studies", []) if case_enabled else [],
    }

    actual_hashes = {
        "de_sha256": _sha256(de_path),
        "en_sha256": _sha256(en_path),
        "state_sha256": _sha256(state_path),
        "harness_config_sha256": _sha256(config_path),
        "source_class_ledger_sha256": _sha256(ledger_path) if ledger_enabled else None,
        "case_study_framework_sha256": _sha256(case_path) if case_enabled else None,
    }
    expected_hashes = state.get("rules_hashes") or {}

    drift = {
        "de_matches_state": expected_hashes.get("de_sha256") == actual_hashes["de_sha256"],
        "en_matches_state": expected_hashes.get("en_sha256") == actual_hashes["en_sha256"],
    }
    drift["rules_in_sync"] = drift["de_matches_state"] and drift["en_matches_state"]

    next_action = state.get("next_action") or {}
    last_completed = state.get("last_completed") or {}
    navigation_health = _navigation_health(root, config)
    profile_development_lens = config.get("profile_development_lens") or {}
    artifact_inventory = _artifact_inventory(root)

    compact = {
        "active": True,
        "mode": state.get("mode", "chronological_archaeology"),
        "project_root": str(root),
        "harness_config": config,
        "current_period": state.get("current_period"),
        "last_completed": last_completed,
        "next_action": next_action,
        "hard_constraints": HARD_CONSTRAINTS,
        "soft_guidance": SOFT_GUIDANCE,
        "navigation_harness": navigation_health,
        "profile_development_lens": profile_development_lens,
        "artifact_inventory": artifact_inventory,
        "source_class_ledger": ledger_compact,
        "case_study_framework": case_compact,
        "rules_hashes": actual_hashes,
        "rules_hashes_expected_by_state": expected_hashes,
        "drift": drift,
        "truth_boundary": (
            "Dieser Arbeitsrahmen liefert Arbeitskontext und Drift-Hinweise. "
            "Er verändert keine Quellen, blockiert keine Leseaktionen und ersetzt keine Primärbelege."
        ),
    }

    if include_full_rules:
        compact["constitution_de"] = de_text
        compact["constitution_en"] = en_text
        compact["current_state"] = state

    return compact


def check(project_root: str | None = None) -> dict[str, Any]:
    context = build_context(project_root=project_root, include_full_rules=False)
    warnings: list[str] = []
    if not context["drift"]["rules_in_sync"]:
        warnings.append(
            "Verfassung und Research State sind nicht hash-synchron. "
            "Vor dem nächsten Schreib-/Kurationsblock State oder Verfassung bewusst abgleichen."
        )

    nav = context.get("navigation_harness") or {}
    if nav.get("promotion_status") == "promoted" and nav.get("healthy") is not True:
        warnings.append(
            "Promotetes PORTFOLIO hat Navigationsdrift: "
            f"fehlende Systeme={nav.get('missing_system_bodies', [])}, "
            f"fehlende Kontexte={nav.get('missing_context_bodies', [])}, "
            f"fehlende LESEN={nav.get('missing_lesen_files', [])}, "
            f"kaputte Links={nav.get('broken_links', [])}."
        )
    elif nav.get("enabled") and nav.get("migration_in_progress"):
        warnings.append(
            "Navigationsumbau läuft warn-only: "
            f"{nav.get('legacy_navigation_files', 0)} alte Meta-Navigationsdateien in "
            f"{nav.get('legacy_navigation_packs', 0)} Packs; "
            f"{nav.get('packs_with_multiple_navigation_files', 0)} Packs mit mehreren Begleitdateien."
        )
    context["warnings"] = warnings
    context["ok"] = True
    return context
