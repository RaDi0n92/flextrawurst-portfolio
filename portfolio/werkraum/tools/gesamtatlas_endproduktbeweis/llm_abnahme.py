#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

PROOF_ROOT = Path(os.environ.get('GA_PROOF_ROOT', '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis'))
INTEGRATION_ROOT = PROOF_ROOT / 'INTEGRATION'
RUNS_ROOT = INTEGRATION_ROOT / 'RUNS'
PROPOSALS_ROOT = INTEGRATION_ROOT / 'PROPOSALS'
CAPSULE = Path(os.environ.get('GA_CAPSULE', '/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_KAPSEL_AKTUELL.zip'))
TASKS = INTEGRATION_ROOT / 'LLM_ABNAHME_AUFGABEN.json'
STATUS = INTEGRATION_ROOT / 'STATUS.json'
LOCK = INTEGRATION_ROOT / '.workflow.lock'

ALLOWED_DECISIONS = {'approve', 'reject', 'revise'}
SAFE_ID = re.compile(r'^[A-Za-z0-9._:-]+$')


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, *parts: str, length: int = 20) -> str:
    raw = '\0'.join(parts).encode('utf-8', errors='replace')
    return f'{prefix}-' + hashlib.sha256(raw).hexdigest()[:length]


def load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text('utf-8'))
    except Exception:
        return default


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def workflow_lock() -> Iterator[None]:
    INTEGRATION_ROOT.mkdir(parents=True, exist_ok=True)
    with LOCK.open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def require_id(value: str, label: str) -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f'{label} enthält unzulässige Zeichen: {value!r}')
    return value


def tasks_payload() -> dict[str, Any]:
    value = load(TASKS)
    if not isinstance(value, dict) or not value.get('task_set_id'):
        raise RuntimeError(f'Aufgabensatz fehlt oder ist ungültig: {TASKS}')
    return value


def run_path(run_id: str) -> Path:
    require_id(run_id, 'run_id')
    path = RUNS_ROOT / run_id
    if not path.exists():
        raise FileNotFoundError(f'Run nicht gefunden: {run_id}')
    return path


def proposal_path(proposal_id: str) -> Path:
    require_id(proposal_id, 'proposal_id')
    path = PROPOSALS_ROOT / proposal_id
    if not path.exists():
        raise FileNotFoundError(f'Vorschlag nicht gefunden: {proposal_id}')
    return path


def update_global_status() -> dict[str, Any]:
    runs = [p for p in RUNS_ROOT.glob('*') if p.is_dir()] if RUNS_ROOT.exists() else []
    proposals = [p for p in PROPOSALS_ROOT.glob('*') if p.is_dir()] if PROPOSALS_ROOT.exists() else []
    response_count = 0
    approved = validated = canonical = 0
    for run in runs:
        response_count += len([p for p in (run / 'responses').glob('*') if p.is_dir()]) if (run / 'responses').exists() else 0
    for proposal in proposals:
        value = load(proposal / 'PROPOSAL.json', {}) or {}
        state = value.get('state')
        approved += int(state in {'DANIEL_APPROVED', 'IMPLEMENTED_UNVERIFIED', 'VALIDATED', 'CANONICAL'})
        validated += int(state in {'VALIDATED', 'CANONICAL'})
        canonical += int(state == 'CANONICAL')
    current = load(STATUS, {}) or {}
    current.update({
        'generated_utc': utcnow(),
        'state': 'WORKFLOW_READY',
        'capsule_path': str(CAPSULE),
        'capsule_sha256': sha256(CAPSULE) if CAPSULE.exists() else None,
        'run_count': len(runs),
        'raw_response_count': response_count,
        'proposal_count': len(proposals),
        'approved_count': approved,
        'validated_count': validated,
        'canonical_count': canonical,
        'canonical_integration_requires_daniel': True,
    })
    atomic_json(STATUS, current)
    return current


def prepare_run(args: argparse.Namespace) -> dict[str, Any]:
    if not CAPSULE.exists():
        raise FileNotFoundError(CAPSULE)
    tasks = tasks_payload()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_id = args.run_id or f'GA-RUN-{stamp}-{uuid.uuid4().hex[:8]}'
    require_id(run_id, 'run_id')
    path = RUNS_ROOT / run_id
    if path.exists():
        raise FileExistsError(path)
    (path / 'responses').mkdir(parents=True)
    payload = {
        'schema_version': 'gesamtatlas-clean-room-run-1.0',
        'run_id': run_id,
        'label': args.label,
        'state': 'PREPARED',
        'created_utc': utcnow(),
        'capsule_path': str(CAPSULE),
        'capsule_bytes': CAPSULE.stat().st_size,
        'capsule_sha256': sha256(CAPSULE),
        'task_set_path': str(TASKS),
        'task_set_id': tasks['task_set_id'],
        'task_set_sha256': sha256(TASKS),
        'distribution_count': 0,
        'response_count': 0,
        'truth_boundary': 'Dieser Run beweist nur Antworten auf exakt diese Kapsel und diesen Aufgabensatz.',
    }
    atomic_json(path / 'RUN.json', payload)
    append_jsonl(path / 'EVENTS.jsonl', {'event':'run_prepared','timestamp_utc':utcnow(),'run_id':run_id})
    update_global_status()
    return payload


def record_distribution(args: argparse.Namespace) -> dict[str, Any]:
    path = run_path(args.run_id)
    run = load(path / 'RUN.json')
    distribution_id = stable_id('DIST', args.run_id, args.provider, args.model, args.model_version, args.recipient_label, utcnow())
    row = {
        'distribution_id': distribution_id,
        'run_id': args.run_id,
        'provider': args.provider,
        'model': args.model,
        'model_version': args.model_version,
        'recipient_label': args.recipient_label,
        'distributed_by': 'Daniel',
        'distributed_utc': utcnow(),
        'capsule_sha256': run['capsule_sha256'],
        'task_set_id': run['task_set_id'],
        'state': 'DISTRIBUTED',
    }
    append_jsonl(path / 'DISTRIBUTIONS.jsonl', row)
    run['state'] = 'DISTRIBUTED'
    run['distribution_count'] = int(run.get('distribution_count', 0)) + 1
    atomic_json(path / 'RUN.json', run)
    append_jsonl(path / 'EVENTS.jsonl', {'event':'distribution_recorded','timestamp_utc':utcnow(),**row})
    return row


def validate_json_response(value: Any, run: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return False, ['JSON-Wurzel ist kein Objekt']
    for key in ('provider', 'model', 'model_version', 'task_set_id', 'capsule_sha256', 'answers'):
        if key not in value:
            errors.append(f'Pflichtfeld fehlt: {key}')
    if value.get('task_set_id') != run.get('task_set_id'):
        errors.append('task_set_id passt nicht zum Run')
    if value.get('capsule_sha256') != run.get('capsule_sha256'):
        errors.append('capsule_sha256 passt nicht zum Run')
    if not isinstance(value.get('answers'), list):
        errors.append('answers ist keine Liste')
    return not errors, errors


def ingest(args: argparse.Namespace) -> dict[str, Any]:
    path = run_path(args.run_id)
    run = load(path / 'RUN.json')
    source = Path(args.file).resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    response_id = stable_id('RESP', args.run_id, args.provider, args.model, args.model_version, sha256(source))
    target = path / 'responses' / response_id
    if target.exists():
        existing = load(target / 'METADATA.json')
        return {'ok': True, 'deduplicated': True, **existing}
    target.mkdir(parents=True)
    raw_name = 'RAW' + (source.suffix if source.suffix else '.txt')
    raw_target = target / raw_name
    shutil.copy2(source, raw_target)
    if sha256(source) != sha256(raw_target):
        raise RuntimeError('Rohantwort wurde beim Kopieren verändert')
    parsed = None
    parse_error = None
    if source.suffix.lower() == '.json':
        try:
            parsed = json.loads(source.read_text('utf-8'))
        except Exception as exc:
            parse_error = f'{type(exc).__name__}: {exc}'
    schema_ok = False
    validation_errors: list[str] = []
    if parsed is not None:
        schema_ok, validation_errors = validate_json_response(parsed, run)
    metadata = {
        'schema_version': 'gesamtatlas-raw-response-metadata-1.0',
        'response_id': response_id,
        'run_id': args.run_id,
        'provider': args.provider,
        'model': args.model,
        'model_version': args.model_version,
        'claimed_context': args.claimed_context,
        'received_utc': utcnow(),
        'source_path_at_ingest': str(source),
        'raw_path': str(raw_target),
        'raw_bytes': raw_target.stat().st_size,
        'raw_sha256': sha256(raw_target),
        'format': source.suffix.lower().lstrip('.') or 'text',
        'json_parsed': parsed is not None,
        'json_parse_error': parse_error,
        'schema_ok': schema_ok,
        'validation_errors': validation_errors,
        'capsule_sha256_expected': run['capsule_sha256'],
        'task_set_id_expected': run['task_set_id'],
        'state': 'READING_RESPONSE_RAW',
        'canonical': False,
        'truth_boundary': 'Rohantwort des angegebenen Prüfers; keine automatische Atlaswahrheit.',
    }
    atomic_json(target / 'METADATA.json', metadata)
    if parsed is not None:
        atomic_json(target / 'PARSED_COPY.json', parsed)
    run['state'] = 'RESPONSES_RECEIVED'
    run['response_count'] = int(run.get('response_count', 0)) + 1
    atomic_json(path / 'RUN.json', run)
    append_jsonl(path / 'EVENTS.jsonl', {'event':'raw_response_ingested','timestamp_utc':utcnow(),'response_id':response_id,'raw_sha256':metadata['raw_sha256']})
    update_global_status()
    return {'ok': True, 'deduplicated': False, **metadata}


def compare(args: argparse.Namespace) -> dict[str, Any]:
    path = run_path(args.run_id)
    rows = []
    task_ids = {item['id'] for item in tasks_payload().get('tasks', [])}
    for response_dir in sorted((path / 'responses').glob('*')):
        if not response_dir.is_dir():
            continue
        metadata = load(response_dir / 'METADATA.json', {}) or {}
        parsed = load(response_dir / 'PARSED_COPY.json')
        covered: set[str] = set()
        citation_count = uncertainty_count = claim_count = 0
        if isinstance(parsed, dict):
            for answer in parsed.get('answers', []) if isinstance(parsed.get('answers'), list) else []:
                if not isinstance(answer, dict):
                    continue
                if answer.get('task_id') in task_ids:
                    covered.add(answer['task_id'])
                citation_count += len(answer.get('citations', [])) if isinstance(answer.get('citations'), list) else 0
                uncertainty_count += len(answer.get('uncertainties', [])) if isinstance(answer.get('uncertainties'), list) else 0
                claim_count += len(answer.get('claims', [])) if isinstance(answer.get('claims'), list) else 0
        rows.append({
            'response_id': metadata.get('response_id'),
            'provider': metadata.get('provider'),
            'model': metadata.get('model'),
            'model_version': metadata.get('model_version'),
            'raw_sha256': metadata.get('raw_sha256'),
            'schema_ok': metadata.get('schema_ok'),
            'covered_tasks': sorted(covered),
            'missing_tasks': sorted(task_ids - covered),
            'citation_count': citation_count,
            'uncertainty_count': uncertainty_count,
            'claim_count': claim_count,
            'assessment_state': 'STRUCTURALLY_ASSESSED_NOT_TRUTH_VALIDATED',
        })
    result = {
        'schema_version': 'gesamtatlas-response-comparison-1.0',
        'run_id': args.run_id,
        'generated_utc': utcnow(),
        'response_count': len(rows),
        'responses': rows,
        'shared_capsule_hash': len({load(path/'responses'/r['response_id']/'METADATA.json',{}).get('capsule_sha256_expected') for r in rows}) <= 1 if rows else True,
        'truth_boundary': 'Strukturvergleich, kein automatischer Wahrheitsentscheid und kein Integrationsauftrag.',
    }
    atomic_json(path / 'VERGLEICH.json', result)
    md = ['# Fremd-LLM-Vergleich','',f'Run: `{args.run_id}`','',f'Antworten: {len(rows)}','',
          'Dieser Bericht bewertet zunächst nur Format, Aufgabenabdeckung und Herkunft. Inhaltliche Wahrheit benötigt Quellenprüfung.','',
          '| Antwort | Modell | Schema | Aufgaben | Zitate | Unsicherheiten |','|---|---|---:|---:|---:|---:|']
    for row in rows:
        md.append(f"| {row['response_id']} | {row['provider']} / {row['model']} {row['model_version']} | {'ja' if row['schema_ok'] else 'nein'} | {len(row['covered_tasks'])}/{len(task_ids)} | {row['citation_count']} | {row['uncertainty_count']} |")
    (path / 'VERGLEICH.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    run = load(path / 'RUN.json')
    run['state'] = 'ASSESSED'
    atomic_json(path / 'RUN.json', run)
    append_jsonl(path / 'EVENTS.jsonl', {'event':'responses_structurally_assessed','timestamp_utc':utcnow(),'response_count':len(rows)})
    return result


def propose(args: argparse.Namespace) -> dict[str, Any]:
    path = run_path(args.run_id)
    requirement_ids = sorted(set(args.requirement_id or []))
    response_ids = sorted(set(args.response_id or []))
    for response_id in response_ids:
        require_id(response_id, 'response_id')
        if not (path / 'responses' / response_id / 'METADATA.json').exists():
            raise FileNotFoundError(f'Response nicht im Run: {response_id}')
    proposal_id = stable_id('PROP', args.run_id, args.title, args.description, '|'.join(requirement_ids), '|'.join(response_ids), utcnow())
    target = PROPOSALS_ROOT / proposal_id
    target.mkdir(parents=True, exist_ok=False)
    value = {
        'schema_version': 'gesamtatlas-integration-proposal-1.0',
        'proposal_id': proposal_id,
        'run_id': args.run_id,
        'title': args.title,
        'description': args.description,
        'requirement_ids': requirement_ids,
        'source_response_ids': response_ids,
        'created_utc': utcnow(),
        'state': 'PROPOSED_NOT_CANONICAL',
        'canonical': False,
        'daniel_decision_required': True,
        'implementation_allowed': False,
    }
    atomic_json(target / 'PROPOSAL.json', value)
    append_jsonl(path / 'EVENTS.jsonl', {'event':'integration_proposed','timestamp_utc':utcnow(),'proposal_id':proposal_id})
    update_global_status()
    return value


def decide(args: argparse.Namespace) -> dict[str, Any]:
    if args.decided_by != 'Daniel':
        raise PermissionError('Nur decided_by=Daniel darf eine Integrationsentscheidung erzeugen')
    if args.decision not in ALLOWED_DECISIONS:
        raise ValueError(args.decision)
    path = proposal_path(args.proposal_id)
    proposal = load(path / 'PROPOSAL.json')
    if proposal.get('state') not in {'PROPOSED_NOT_CANONICAL', 'DANIEL_REVISE'}:
        raise RuntimeError(f'Vorschlag ist nicht entscheidbar: {proposal.get("state")}')
    mapping = {'approve':'DANIEL_APPROVED','reject':'DANIEL_REJECTED','revise':'DANIEL_REVISE'}
    decision = {
        'proposal_id': args.proposal_id,
        'decision': args.decision,
        'decided_by': 'Daniel',
        'decided_utc': utcnow(),
        'comment': args.comment,
        'allowed_scope': args.allowed_scope or [],
        'forbidden_scope': args.forbidden_scope or [],
    }
    atomic_json(path / f'DECISION_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}.json', decision)
    proposal['state'] = mapping[args.decision]
    proposal['implementation_allowed'] = args.decision == 'approve'
    proposal['canonical'] = False
    proposal['latest_decision'] = decision
    atomic_json(path / 'PROPOSAL.json', proposal)
    update_global_status()
    return proposal


def transition(args: argparse.Namespace, target_state: str) -> dict[str, Any]:
    path = proposal_path(args.proposal_id)
    proposal = load(path / 'PROPOSAL.json')
    current = proposal.get('state')
    if target_state == 'IMPLEMENTED_UNVERIFIED':
        if current != 'DANIEL_APPROVED':
            raise PermissionError('Implementierung verlangt vorher DANIEL_APPROVED')
        proposal['implementation_paths'] = args.evidence_path or []
    elif target_state == 'VALIDATED':
        if current != 'IMPLEMENTED_UNVERIFIED':
            raise PermissionError('Validierung verlangt vorher IMPLEMENTED_UNVERIFIED')
        if not args.evidence_path:
            raise ValueError('VALIDATED verlangt mindestens einen evidence_path')
        proposal['validation_evidence_paths'] = args.evidence_path
    elif target_state == 'CANONICAL':
        if current != 'VALIDATED':
            raise PermissionError('CANONICAL verlangt vorher VALIDATED')
        if args.confirmed_by != 'Daniel':
            raise PermissionError('CANONICAL verlangt confirmed_by=Daniel')
        proposal['canonical'] = True
        proposal['canonical_confirmed_by'] = 'Daniel'
        proposal['canonical_utc'] = utcnow()
    proposal['state'] = target_state
    atomic_json(path / 'PROPOSAL.json', proposal)
    update_global_status()
    return proposal


def status_command(_: argparse.Namespace) -> dict[str, Any]:
    return update_global_status()


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='gesamtatlas-llm-abnahme')
    sub = p.add_subparsers(dest='command', required=True)
    q = sub.add_parser('prepare-run'); q.add_argument('--label', required=True); q.add_argument('--run-id'); q.set_defaults(fn=prepare_run)
    q = sub.add_parser('record-distribution'); q.add_argument('--run-id', required=True); q.add_argument('--provider', required=True); q.add_argument('--model', required=True); q.add_argument('--model-version', required=True); q.add_argument('--recipient-label', required=True); q.set_defaults(fn=record_distribution)
    q = sub.add_parser('ingest'); q.add_argument('--run-id', required=True); q.add_argument('--provider', required=True); q.add_argument('--model', required=True); q.add_argument('--model-version', required=True); q.add_argument('--file', required=True); q.add_argument('--claimed-context', default='capsule_only'); q.set_defaults(fn=ingest)
    q = sub.add_parser('compare'); q.add_argument('--run-id', required=True); q.set_defaults(fn=compare)
    q = sub.add_parser('propose'); q.add_argument('--run-id', required=True); q.add_argument('--title', required=True); q.add_argument('--description', required=True); q.add_argument('--requirement-id', action='append'); q.add_argument('--response-id', action='append'); q.set_defaults(fn=propose)
    q = sub.add_parser('decide'); q.add_argument('--proposal-id', required=True); q.add_argument('--decision', choices=sorted(ALLOWED_DECISIONS), required=True); q.add_argument('--decided-by', required=True); q.add_argument('--comment', required=True); q.add_argument('--allowed-scope', action='append'); q.add_argument('--forbidden-scope', action='append'); q.set_defaults(fn=decide)
    q = sub.add_parser('mark-implemented'); q.add_argument('--proposal-id', required=True); q.add_argument('--evidence-path', action='append'); q.set_defaults(fn=lambda a: transition(a, 'IMPLEMENTED_UNVERIFIED'))
    q = sub.add_parser('mark-validated'); q.add_argument('--proposal-id', required=True); q.add_argument('--evidence-path', action='append'); q.set_defaults(fn=lambda a: transition(a, 'VALIDATED'))
    q = sub.add_parser('mark-canonical'); q.add_argument('--proposal-id', required=True); q.add_argument('--confirmed-by', required=True); q.set_defaults(fn=lambda a: transition(a, 'CANONICAL'))
    q = sub.add_parser('status'); q.set_defaults(fn=status_command)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        with workflow_lock():
            value = args.fn(args)
        print(json.dumps({'ok': True, 'result': value}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': f'{type(exc).__name__}: {exc}'}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
