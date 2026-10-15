from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import ATLAS_ROOT, CONTRIBUTION_ROOT, load_json, read_jsonl, stable_id, utcnow, write_jsonl

IDEAS = ATLAS_ROOT / 'IDEENREGISTER.jsonl'
CONFLICTS = ATLAS_ROOT / 'KONFLIKTREGISTER.jsonl'
CONSENSUS = ATLAS_ROOT / 'KONSENSREGISTER.jsonl'
CLAIMS = ATLAS_ROOT / 'CLAIMREGISTER.json'
HANDOFFS = ATLAS_ROOT / 'UEBERGABEREGISTER.json'

SUCCESS_WORDS = re.compile(r'(?i)\b(fertig|abgeschlossen|funktioniert|erfolgreich|implemented|done|endprodukt|vollständig umgesetzt)\b')
UNCERTAINTY_WORDS = re.compile(r'(?i)\b(ungetestet|nicht getestet|offen|todo|noch nicht|unklar|unsicher|fehlt)\b')
TEST_WORDS = re.compile(r'(?i)\b(test|playwright|pytest|unittest|beweis|validation|evidence|abnahme)\b')


def _read_registry(path: Path) -> list[dict[str, Any]]:
    if path.suffix == '.jsonl':
        return list(read_jsonl(path)) if path.exists() else []
    value = load_json(path, []) or []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ('items', 'claims', 'handoffs', 'register'):
            if isinstance(value.get(key), list):
                return [item for item in value[key] if isinstance(item, dict)]
        return [value]
    return []


def _finding(kind: str, subject: str, summary: str, evidence: list[dict[str, Any]], *, severity: str = 'medium', truth_class: str = 'DERIVED_CANDIDATE', action: str = '') -> dict[str, Any]:
    fingerprint = json.dumps({'kind': kind, 'subject': subject, 'evidence': evidence}, ensure_ascii=False, sort_keys=True, default=str)
    return {
        'finding_id': stable_id('atlas-finding', fingerprint),
        'kind': kind,
        'subject': subject,
        'summary': summary,
        'severity': severity,
        'truth_class': truth_class,
        'evidence': evidence,
        'suggested_action': action,
        'generated_utc': utcnow(),
        'status': 'open',
    }


def build_reactive(output: Path, core_db: Path, browser_status: dict[str, Any], terminal_status: dict[str, Any]) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    findings: list[dict[str, Any]] = []
    impulses: list[dict[str, Any]] = []
    connection = sqlite3.connect(f'file:{core_db}?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row

    # Verwaiste oder schwach zugeordnete Körper: nur relevante, nicht jeder Cache-Krümel.
    relation_paths = {str(row['path']) for row in connection.execute("select path from relation_nodes where path is not null and path != ''")}
    project_paths = [str(row['path']) for row in connection.execute("select path from projects where path is not null and path != ''")]
    orphan_candidates = []
    for row in connection.execute("select path,root_name,size,mtime_ns,suffix,basename,parent from paths where is_dir=0 and depth<=5 and excluded_reason is null order by mtime_ns desc limit 10000"):
        path = str(row['path'])
        if path in relation_paths:
            continue
        if any(path == project or path.startswith(project.rstrip('/') + '/') for project in project_paths):
            continue
        suffix = str(row['suffix'] or '').lower()
        if suffix not in {'.md', '.txt', '.json', '.jsonl', '.py', '.sh'}:
            continue
        orphan_candidates.append(dict(row))
        if len(orphan_candidates) >= 600:
            break
    for row in orphan_candidates:
        findings.append(_finding(
            'orphan_candidate', row['path'], 'Der Körper ist im schmalen Pfadindex sichtbar, aber keinem kanonischen Projekt- oder Beziehungsknoten direkt zugeordnet.',
            [{'path': row['path'], 'root_name': row['root_name'], 'size': row['size'], 'mtime_ns': row['mtime_ns']}],
            severity='low', action='Herkunft prüfen und bei Bedarf nur verlinken, nicht automatisch verschieben.',
        ))

    # Behauptete Fertigstellung ohne im selben Text sichtbaren Testbezug.
    try:
        rows = connection.execute("select path,title,headings,preview from previews where previews match 'fertig OR abgeschlossen OR Endprodukt OR erfolgreich' limit 1000")
    except sqlite3.OperationalError:
        rows = []
    for row in rows:
        text = ' '.join(str(row[key] or '') for key in ('title', 'headings', 'preview'))
        if not SUCCESS_WORDS.search(text) or TEST_WORDS.search(text) or UNCERTAINTY_WORDS.search(text):
            continue
        findings.append(_finding(
            'completion_claim_without_visible_test_evidence', row['path'], 'Im Vorschauausschnitt steht eine Fertigstellungsbehauptung, ohne dass dort ein Test- oder Beweisbezug sichtbar ist.',
            [{'path': row['path'], 'excerpt': text[:1200]}],
            severity='medium', action='Nicht automatisch widerlegen. Zugehörige Test- und Laufzeitbelege suchen.',
        ))

    # Fehlende native Terminalquellen bleiben explizit.
    for provider, state in terminal_status.get('providers', {}).items():
        if state.get('sessions', 0) > 0:
            continue
        findings.append(_finding(
            'missing_terminal_source', provider, f'Für {provider} wurde keine unterstützte native Terminalsitzung gefunden.',
            [{'source_root': state.get('source_root'), 'exists': state.get('exists'), 'format': state.get('format'), 'status': state.get('status')}],
            severity='medium', truth_class='OBSERVED_ABSENCE_AT_BUILD_TIME', action='Adapter ergänzen, sobald ein natives Logformat real vorhanden ist.',
        ))

    # Browserlücken aus realer Recorderzählung.
    gaps = int(browser_status.get('totals', {}).get('gaps', 0))
    if gaps:
        findings.append(_finding(
            'browser_capture_gaps', 'browser_recorder', f'Der Browserbestand enthält {gaps} protokollierte Aufnahmelücken.',
            [{'gap_count': gaps, 'source_root': browser_status.get('source_root')}],
            severity='high', truth_class='SOURCE_REPORTED', action='Betroffene Gespräche gezielt erneut importieren oder als dauerhaft unvollständig belassen.',
        ))

    # Bestehende Konflikt- und Konsensregister werden nicht neu gedeutet, nur gespiegelt.
    for row in _read_registry(CONFLICTS):
        findings.append(_finding(
            'existing_conflict', str(row.get('conflict_id') or row.get('id') or row.get('subject') or 'conflict'),
            str(row.get('summary') or row.get('description') or row.get('statement') or 'Vorhandener Konfliktregistereintrag.'),
            [{'source_path': str(CONFLICTS), 'entry': row}], severity='high', truth_class='REGISTERED_SOURCE', action='Quellen beider Seiten prüfen.',
        ))
    consensus_rows = _read_registry(CONSENSUS)
    repeated_sources = Counter()
    for row in consensus_rows:
        source = str(row.get('source_path') or row.get('source') or row.get('origin') or '')
        if source:
            repeated_sources[source] += 1
    for source, count in repeated_sources.items():
        if count > 1:
            findings.append(_finding(
                'possible_circular_confirmation', source, f'Dieselbe Herkunft erscheint in {count} Konsensregistereinträgen. Mehrfache Einträge sind nicht automatisch unabhängige Bestätigung.',
                [{'source': source, 'count': count}], severity='medium', action='Abstammung der Bestätigungen prüfen.',
            ))

    # Alte Ideen als Wiederentdeckungsimpulse.
    idea_rows = _read_registry(IDEAS)
    for row in idea_rows[:5000]:
        title = str(row.get('title') or row.get('name') or row.get('idea') or row.get('summary') or '')
        if not title:
            continue
        status = str(row.get('status') or row.get('state') or '').lower()
        if status in {'done', 'completed', 'closed', 'verworfen'}:
            continue
        timestamp = str(row.get('timestamp_utc') or row.get('created_utc') or row.get('date') or '')
        impulses.append({
            'impulse_id': stable_id('atlas-impulse', json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)),
            'kind': 'rediscovery',
            'title': title[:300],
            'source_path': str(IDEAS),
            'source_entry': row,
            'why_now': 'Offene oder nicht abgeschlossene Idee aus dem vorhandenen Ideenregister.',
            'truth_class': 'REGISTERED_IDEA_NOT_CURRENT_PRIORITY_PROOF',
            'generated_utc': utcnow(),
            'status': 'available_not_assigned',
            'timestamp': timestamp,
        })

    # Beiträge aller AI-Ströme werden als eigene, nicht kanonisierte Stimmen gespiegelt.
    contribution_count = 0
    if CONTRIBUTION_ROOT.exists():
        for path in sorted(CONTRIBUTION_ROOT.rglob('*.jsonl')):
            for row in read_jsonl(path):
                contribution_count += 1
                if row.get('kind') == 'challenge':
                    findings.append(_finding(
                        'ai_stream_challenge', str(row.get('subject') or row.get('contribution_id') or path),
                        str(row.get('text') or row.get('summary') or 'AI-Strom hat einen Widerspruch hinterlassen.'),
                        [{'source_path': str(path), 'entry': row}], severity='medium', truth_class='ATTRIBUTED_CONTRIBUTION', action='Nicht automatisch übernehmen; Herkunft und Gegenquellen prüfen.',
                    ))
                else:
                    impulses.append({
                        'impulse_id': stable_id('atlas-contribution-impulse', json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)),
                        'kind': 'ai_stream_contribution',
                        'title': str(row.get('subject') or row.get('text') or '')[:300],
                        'source_path': str(path),
                        'source_entry': row,
                        'why_now': 'Explizit zugeschriebener Beitrag eines AI-Stroms.',
                        'truth_class': 'ATTRIBUTED_CONTRIBUTION',
                        'generated_utc': utcnow(),
                        'status': 'available_not_canonical',
                    })

    connection.close()
    # Deduplizieren nach ID.
    findings_by_id = {row['finding_id']: row for row in findings}
    impulses_by_id = {row['impulse_id']: row for row in impulses}
    findings = sorted(findings_by_id.values(), key=lambda row: (row['severity'], row['kind'], row['subject']))
    impulses = sorted(impulses_by_id.values(), key=lambda row: (row['kind'], row.get('title', '')))
    if not impulses and findings:
        impulses = [{
            'impulse_id': stable_id('atlas-impulse', finding['finding_id']),
            'kind': 'finding_followup',
            'title': finding['summary'][:300],
            'source_path': str(output / 'REAKTIONSREGISTER.jsonl.gz'),
            'source_finding_id': finding['finding_id'],
            'why_now': finding.get('suggested_action') or 'Der Atlas hat einen offenen, prüfbaren Befund gefunden.',
            'truth_class': 'DERIVED_WORK_INVITATION',
            'generated_utc': utcnow(),
            'status': 'available_not_assigned',
        } for finding in findings[:80]]
    write_jsonl(output / 'REAKTIONSREGISTER.jsonl.gz', findings, gzip_output=True)
    write_jsonl(output / 'ARBEITSIMPULSE.jsonl.gz', impulses, gzip_output=True)
    kinds = Counter(row['kind'] for row in findings)
    impulse_kinds = Counter(row['kind'] for row in impulses)
    status = {
        'ok': True,
        'generated_utc': utcnow(),
        'finding_count': len(findings),
        'finding_kinds': dict(kinds),
        'impulse_count': len(impulses),
        'impulse_kinds': dict(impulse_kinds),
        'contribution_count': contribution_count,
        'mutation_policy': 'suggest_only_no_source_moves_no_original_changes',
        'truth_boundary': 'Reactive outputs are attributed observations or marked derivations. They are not automatic truth or commands.',
    }
    (output / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return status
