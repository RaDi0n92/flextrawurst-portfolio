#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-light}"
REASON="${2:-scheduled}"
case "$MODE" in light|full) ;; *) echo "invalid atlas mode: $MODE" >&2; exit 2 ;; esac
ROOT='/root/werkraum/_gpt/gesamtatlas'
LOCK="$ROOT/.scheduled-refresh.lock"
OUT="$ROOT/runtime/last_${MODE}_refresh.json"
mkdir -p "$ROOT/runtime"
exec 9>"$LOCK"
if ! flock -n 9; then
  printf '%s atlas refresh skipped: another refresh is active\n' "$(date -u +%FT%TZ)"
  exit 0
fi
export PYTHONPATH='/root/werkraum/tools/vps_mcp:/root/werkraum'
export FLEXTRAWURST_ATLAS_MAX_TEXT_DOCUMENTS="${FLEXTRAWURST_ATLAS_MAX_TEXT_DOCUMENTS:-200000}"
TMP="$OUT.$$.tmp"
trap 'rm -f "$TMP"' EXIT
/usr/bin/python3 /root/werkraum/tools/vps_mcp/mcp_atlas.py refresh \
  --mode "$MODE" \
  --reason "$REASON" \
  --session-id system-atlas-scheduler > "$TMP"
python3 - "$TMP" <<'PY'
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
s=d.get('status',{})
scan=s.get('scan',{})
print(json.dumps({
 'ok':d.get('ok'),
 'revision':s.get('revision'),
 'mode':s.get('mode'),
 'reason':s.get('reason'),
 'generated_utc':s.get('generated_utc'),
 'observed_paths':scan.get('observed_path_count'),
 'indexed_paths':scan.get('path_count'),
 'text_documents':scan.get('text_document_count'),
 'dirty':s.get('dirty'),
},ensure_ascii=False))
PY
mv -f "$TMP" "$OUT"
trap - EXIT

if [[ "$MODE" == "full" ]]; then
  VERIFY="$ROOT/runtime/last_full_verification.json"
  VERIFY_TMP="$VERIFY.$$.tmp"
  python3 - "$ROOT" "$OUT" > "$VERIFY_TMP" <<'PYVERIFY'
import hashlib,json,sqlite3,sys
from pathlib import Path
root=Path(sys.argv[1])
refresh_payload=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
snapshot_status=refresh_payload.get('status',{})
current_status=json.loads((root/'ATLAS_STATUS.json').read_text(encoding='utf-8'))
scan=snapshot_status.get('scan',{})
projects=json.loads((root/'PROJEKTREGISTER.json').read_text(encoding='utf-8'))
project_revisions=json.loads((root/'PROJEKTREVISIONEN.json').read_text(encoding='utf-8')).get('projects',{})
claims=json.loads((root/'CLAIMREGISTER.json').read_text(encoding='utf-8')).get('claims',[])
validations=json.loads((root/'VALIDIERUNGSREGISTER.json').read_text(encoding='utf-8')).get('validations',[])
handoffs=json.loads((root/'UEBERGABEREGISTER.json').read_text(encoding='utf-8')).get('handoffs',[])
streams=json.loads((root/'AI_STROEME.json').read_text(encoding='utf-8'))
bridges=json.loads((root/'AI_STROM_BRUECKEN.json').read_text(encoding='utf-8')).get('streams',{})
relation_summary=json.loads((root/'BEZIEHUNGSREGISTER.json').read_text(encoding='utf-8'))
urbewohner_register=json.loads((root/'urbewohner/URBEWOHNERREGISTER.json').read_text(encoding='utf-8'))
expected_urbewohner={
    'F3INSCHM3CK3R','R1ZZ1','Resonanzknoten','Schorschel',
    'jumpa','träumerlie','dak+gord-system','GENI',
}
p=sqlite3.connect(root/'PFADINDEX.sqlite')
c=sqlite3.connect(root/'BEGRIFFSINDEX.sqlite')
r=sqlite3.connect(root/'BEZIEHUNGSREGISTER.sqlite')
try:
    path_count=p.execute('select count(*) from paths').fetchone()[0]
    suffixes=('.md','.txt','.json','.jsonl','.yaml','.yml','.toml','.ini','.conf','.service','.timer','.py','.js','.ts','.tsx','.jsx','.html','.css','.sql','.sh')
    placeholders=','.join('?' for _ in suffixes)
    candidates={row[0] for row in p.execute(f"select path from paths where is_dir=0 and size>0 and size<=2097152 and suffix in ({placeholders}) and coalesce(excluded_reason,'')!='broken_symlink_target_missing'",suffixes)}
    broken_symlinks={row[0] for row in p.execute(f"select path from paths where is_dir=0 and size>0 and size<=2097152 and suffix in ({placeholders}) and excluded_reason='broken_symlink_target_missing'",suffixes)}
    fts_rows=c.execute('select count(*) from documents').fetchone()[0]
    fts_paths={row[0] for row in c.execute('select path from documents')}
    relationship_nodes=r.execute('select count(*) from nodes').fetchone()[0]
    relationship_edges=r.execute('select count(*) from edges').fetchone()[0]
    urbewohner_ids={row[0] for row in r.execute("select identity from nodes where node_type='wesen'")}
    gedanken_nodes=r.execute("select count(*) from nodes where node_type='gedanke'").fetchone()[0]
    geni_nodes=r.execute("select count(*) from nodes where node_type='geni_knoten'").fetchone()[0]
    schlaf_nodes=r.execute("select count(*) from nodes where node_type='schlafphase'").fetchone()[0]
    obsolete_parallel_nodes=r.execute("select count(*) from nodes where node_type in ('entity','entity_facet','entity_alias','entity_collective','data_source','habitat','origin_habitat')").fetchone()[0]
    produced_thought_edges=r.execute("select count(*) from edges where relation='PRODUCED_THOUGHT'").fetchone()[0]
    memory_edges=r.execute("select count(*) from edges where relation='HAS_MEMORY_NODE'").fetchone()[0]
    target_edges=r.execute("select count(*) from edges where relation='TARGETS'").fetchone()[0]
    alias_count=sum(len(row.get('aliases') or []) for row in urbewohner_register.get('entities') or [])
    urbewohner_dangling=r.execute("select count(*) from edges e left join nodes s on s.node_id=e.source_node_id left join nodes t on t.node_id=e.target_node_id where s.node_id is null or t.node_id is null").fetchone()[0]
    path_integrity=p.execute('pragma integrity_check').fetchone()[0]
    concept_integrity=c.execute('pragma integrity_check').fetchone()[0]
    relationship_integrity=r.execute('pragma integrity_check').fetchone()[0]
finally:
    p.close();c.close();r.close()
missing=sorted(candidates-fts_paths)
extra=sorted(fts_paths-candidates)
project_ids={str(row.get('project_id') or '') for row in projects if row.get('project_id')}
revision_ids=set(project_revisions)
required_project_fields=('project_class','project_revision','relationship_counts','bridge_eligible','navigational_priority')
projects_missing_fields={
    str(row.get('project_id') or row.get('path')):[field for field in required_project_fields if field not in row]
    for row in projects
    if any(field not in row for field in required_project_fields)
}
bridge_ids=set(bridges)
stream_ids={str(row.get('id') or '') for row in streams if row.get('id')}
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()
checks={
    'status_path_count_equals_sqlite':scan.get('path_count')==path_count,
    'status_text_count_equals_fts_rows':scan.get('text_document_count')==fts_rows,
    'no_missing_nonempty_text_candidates':not missing,
    'no_unclassified_extra_fts_paths':not extra,
    'broken_symlinks_explicitly_classified':scan.get('broken_text_symlink_count')==len(broken_symlinks),
    'path_index_integrity':path_integrity=='ok',
    'concept_index_integrity':concept_integrity=='ok',
    'relationship_index_integrity':relationship_integrity=='ok',
    'relationship_summary_matches_database':relation_summary.get('node_count')==relationship_nodes and relation_summary.get('edge_count')==relationship_edges,
    'relationship_graph_nonempty':relationship_nodes>0 and relationship_edges>0,
    'exactly_eight_urbewohner_present':urbewohner_ids==expected_urbewohner,
    'documented_identity_aliases_present':alias_count==12,
    'no_obsolete_parallel_entity_nodes':obsolete_parallel_nodes==0,
    'thought_nodes_present':gedanken_nodes>0 and produced_thought_edges==gedanken_nodes,
    'geni_nodes_present':geni_nodes>0 and memory_edges==geni_nodes,
    'target_edges_present':target_edges>0,
    'sleep_nodes_present':schlaf_nodes>0,
    'urbewohner_edges_not_dangling':urbewohner_dangling==0,
    'urbewohner_register_complete':urbewohner_register.get('canonical_count')==8 and bool((urbewohner_register.get('completeness') or {}).get('complete')),
    'urbewohner_summary_matches_database':(
        int((relation_summary.get('urbewohner') or {}).get('canonical_entities') or 0)==len(urbewohner_ids)
        and int((relation_summary.get('urbewohner') or {}).get('thought_nodes') or 0)==gedanken_nodes
        and int((relation_summary.get('urbewohner') or {}).get('geni_nodes') or 0)==geni_nodes
        and int((relation_summary.get('urbewohner') or {}).get('sleep_nodes') or 0)==schlaf_nodes
        and int((relation_summary.get('urbewohner') or {}).get('target_edges') or 0)==target_edges
    ),
    'project_revisions_cover_projects':project_ids==revision_ids,
    'all_projects_have_relational_fields':not projects_missing_fields,
    'handoff_register_nonempty':len(handoffs)>0,
    'claims_register_nonempty':len(claims)>0,
    'validation_register_nonempty':len(validations)>0,
    'ai_bridges_cover_registered_streams':bridge_ids==stream_ids,
    'path_limit_not_reached':not bool(scan.get('path_limit_reached')),
    'text_limit_not_reached':not bool(scan.get('text_document_limit_reached')),
    'snapshot_marked_clean':not bool(snapshot_status.get('dirty')),
}
hash_names=(
    'ATLAS_STATUS.json','GESAMTKARTE.md','PFADINDEX.sqlite','BEGRIFFSINDEX.sqlite',
    'BEZIEHUNGSREGISTER.sqlite','BEZIEHUNGSREGISTER.json','PROJEKTREGISTER.json',
    'PROJEKTREVISIONEN.json','CLAIMREGISTER.json','VALIDIERUNGSREGISTER.json',
    'UEBERGABEREGISTER.json','AI_STROEME.json','AI_STROM_BRUECKEN.json','WURZELBRIEFE.json',
    'urbewohner/URBEWOHNERREGISTER.json','urbewohner/URBEWOHNERREGISTER.md'
)
result={
    'schema_version':'2.0',
    'ok':all(checks.values()),
    'verified_revision':snapshot_status.get('revision'),
    'verified_generated_utc':snapshot_status.get('generated_utc'),
    'truth_class':snapshot_status.get('truth_class'),
    'current_revision_after_snapshot':current_status.get('revision'),
    'current_dirty_after_snapshot':bool(current_status.get('dirty')),
    'post_snapshot_changes_present':bool(current_status.get('revision') != snapshot_status.get('revision') or current_status.get('dirty')),
    'truth_boundary':'Die Verifikation bindet den erzeugten Vollsnapshot samt Pfad-, Volltext-, Beziehungs-, Lease-, Übergabe- und AI-Strom-Schichten. Spätere Mutationen werden als Nachlauf gemeldet und machen den Snapshot nicht rückwirkend falsch.',
    'checks':checks,
    'counts':{
        'observed_paths':scan.get('observed_path_count'),
        'status_indexed_paths':scan.get('path_count'),
        'sqlite_indexed_paths':path_count,
        'status_text_documents':scan.get('text_document_count'),
        'sqlite_fts_rows':fts_rows,
        'nonempty_text_candidates':len(candidates),
        'unique_fts_paths':len(fts_paths),
        'missing_nonempty':len(missing),
        'extra_fts_paths':len(extra),
        'empty_text_paths':scan.get('empty_text_path_count'),
        'broken_text_symlinks':scan.get('broken_text_symlink_count'),
        'sqlite_broken_symlink_paths':len(broken_symlinks),
        'projects':len(projects),
        'project_revisions':len(project_revisions),
        'claims':len(claims),
        'validations':len(validations),
        'handoffs':len(handoffs),
        'ai_streams':len(streams),
        'ai_bridges':len(bridges),
        'relationship_nodes':relationship_nodes,
        'relationship_edges':relationship_edges,
        'urbewohner':len(urbewohner_ids),
        'urbewohner_source_facets':int((relation_summary.get('urbewohner') or {}).get('source_facets') or 0),
        'urbewohner_aliases':alias_count,
        'gedanken_nodes':gedanken_nodes,
        'geni_nodes':geni_nodes,
        'schlaf_nodes':schlaf_nodes,
        'target_edges':target_edges,
        'obsolete_parallel_nodes':obsolete_parallel_nodes,
        'urbewohner_dangling_edges':urbewohner_dangling,
    },
    'project_field_failures':projects_missing_fields,
    'project_revision_only_ids':sorted(revision_ids-project_ids),
    'project_without_revision_ids':sorted(project_ids-revision_ids),
    'stream_without_bridge_ids':sorted(stream_ids-bridge_ids),
    'bridge_without_stream_ids':sorted(bridge_ids-stream_ids),
    'missing_sample':missing[:25],
    'extra_sample':extra[:25],
    'hashes':{name:sha(root/name) for name in hash_names},
}
print(json.dumps(result,ensure_ascii=False,indent=2))
if not result['ok']:
    raise SystemExit(7)
PYVERIFY
  mv -f "$VERIFY_TMP" "$VERIFY"
fi
/usr/bin/python3 /root/werkraum/tools/vps_mcp/publish_omega_lean_binding.py \
  --mode "$MODE" \
  --reason "$REASON" \
  --refresh-json "$OUT"
