#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, '/root/werkraum/tools/vps_mcp')
import mcp_atlas_omega as omega

RUNTIME=Path('/root/werkraum/_gpt/gesamtatlas/omega/runtime')

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->dict:
    with tempfile.TemporaryDirectory(prefix='content-identity-',dir=RUNTIME) as td:
        root=Path(td);fixture=root/'fixture';fixture.mkdir();db=root/'content.sqlite'
        zip_payload=(b'PK\x03\x04OMEGA_BINARY_SAME_CONTENT\x00\xff'*4096)
        plain_payload=(b'EXTENSIONLESS_EQUAL_CONTENT\x00\x01\xff'*1024)
        files={
            'binary_a':fixture/'capsule-a.zip','binary_b':fixture/'capsule-b.zip',
            'extensionless':fixture/'body_without_suffix','listed':fixture/'body.log',
        }
        files['binary_a'].write_bytes(zip_payload);files['binary_b'].write_bytes(zip_payload)
        files['extensionless'].write_bytes(plain_payload);files['listed'].write_bytes(plain_payload)
        scan=omega.sync_roots([fixture],db_path=db,root_names=['section-2-content'],chunk_bytes=16384,force=True)
        con=sqlite3.connect(db);con.row_factory=sqlite3.Row
        try:
            rows={r['path']:dict(r) for r in con.execute('select path,object_id from paths where path in (?,?,?,?)',tuple(str(x) for x in files.values()))}
            objects={}
            for p,row in rows.items():
                obj=con.execute('select object_id,current_version_id,current_primary_path from objects where object_id=?',(row['object_id'],)).fetchone()
                objects[p]=dict(obj) if obj else None
            edges=[dict(r) for r in con.execute("select src_object_id,dst_object_id,edge_type,evidence_class,evidence_json from edges where active=1 and edge_type='SAME_CONTENT'")]
            versions=[dict(r) for r in con.execute('select version_id,object_id,file_sha256,size,complete from versions')]
            integrity=con.execute('pragma integrity_check').fetchone()[0]
        finally:con.close()

        def pair(a:Path,b:Path)->dict:
            oa,ob=objects.get(str(a)),objects.get(str(b));ids={oa['object_id'],ob['object_id']} if oa and ob else set()
            directed=[e for e in edges if e['src_object_id'] in ids and e['dst_object_id'] in ids and e['src_object_id']!=e['dst_object_id']]
            state={
                'paths':[str(a),str(b)],'sha256':[sha(a),sha(b)],'same_sha256':sha(a)==sha(b),
                'objects':[oa,ob],'objects_exist':bool(oa and ob),
                'distinct_object_ids':bool(oa and ob and oa['object_id']!=ob['object_id']),
                'current_versions_present':bool(oa and ob and oa['current_version_id'] and ob['current_version_id']),
                'same_content_edge_count':len(directed),'directed_edges':directed,
            }
            state['ok']=all([state['same_sha256'],state['objects_exist'],state['distinct_object_ids'],state['current_versions_present'],state['same_content_edge_count']>=2])
            return state
        binary=pair(files['binary_a'],files['binary_b']);extensionless=pair(files['extensionless'],files['listed'])
        all_ids=[o['object_id'] for o in objects.values() if o]
        result={
            'schema_version':'1.0','ok':binary['ok'] and extensionless['ok'] and len(set(all_ids))==4 and integrity=='ok',
            'scan':scan,'binary_pair':binary,'extensionless_pair':extensionless,
            'all_object_ids':all_ids,'all_object_ids_distinct':len(set(all_ids))==4,
            'version_count':len(versions),'versions':versions,'sqlite_integrity':integrity,
            'expected':'Identical bodies keep distinct path objects and current versions while SAME_CONTENT is explicit in both directions, including an extensionless binary body.'
        }
        print(json.dumps(result,ensure_ascii=False));return result
if __name__=='__main__':main()
